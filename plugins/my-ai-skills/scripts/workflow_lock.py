"""Exclusão local cooperativa por estado/issue/run; não é CAS entre máquinas."""
import fcntl
import hashlib
import json
import os
from pathlib import Path


def domain(repository, issue, run_id):
    return hashlib.sha256(json.dumps([repository, issue, run_id], separators=(",", ":")).encode()).hexdigest()


class PublicationLock:
    def __init__(self, directory, repository, issue, run_id):
        self.path = Path(directory) / ("workflow-" + domain(repository, issue, run_id) + ".lock")
        self.fd = None

    def __enter__(self):
        self.path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        self.fd = os.open(self.path, os.O_CREAT | os.O_RDWR | os.O_CLOEXEC, 0o600)
        try:
            fcntl.flock(self.fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            os.close(self.fd)
            self.fd = None
            raise RuntimeError("publicação concorrente no mesmo domínio") from None
        return self

    def __exit__(self, *args):
        if self.fd is not None:
            os.close(self.fd)
            self.fd = None
