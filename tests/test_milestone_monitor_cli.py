"""M1/M6/M10: launchers reais, distribuição e coleta fake multi-projeto."""
import copy
import json
import os
import py_compile
import subprocess
import sys
import tempfile
import unittest

from milestone_monitor_fixtures import *
from milestone_monitor.config import load
from milestone_monitor.common import MonitorError
from milestone_monitor.runtime import git_identity

FAKE_GH = '''#!/usr/bin/env python3
import json,sys,os
path=sys.argv[-1]
if os.environ.get('FAKE_OFFLINE'):
    print('HTTP 429 PRIVATE_TOKEN Retry-After: 60',file=sys.stderr);sys.exit(1)
if '/milestones/' in path: result={'number':int(path.rsplit('/',1)[1]),'title':'Real fixture'}
elif '/comments?' in path or '/timeline?' in path: result=[]
else:
    repo='/'.join(path.split('/')[1:3]);result=[{'number':7,'title':'No instrumentation','state':'open','milestone':{'number':1},'html_url':f'https://github.com/{repo}/issues/7'}]
print(json.dumps(result))
'''


class CLITests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name)
        self.env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1", "XDG_CONFIG_HOME": str(self.path/"config"), "XDG_STATE_HOME": str(self.path/"state")}

    def run_cli(self, *argv, executable=None, env=None):
        return subprocess.run([str(executable or ROOT / "scripts/aew"), *argv], capture_output=True, text=True,
                              cwd=self.path, env=env or self.env, timeout=20)

    def test_config_validation_empty_xdg_dedup_and_help(self):
        self.assertEqual(load(self.path/"missing")["targets"], [])
        config = self.path/"config.json"
        config.write_text(json.dumps({**CONFIG, "targets": CONFIG["targets"]*2}))
        self.assertEqual(len(load(config)["targets"]), 1)
        for override in ({"schema_version": 2}, {"targets": [{"repository": "evil;cmd", "milestones": [1]}]},
                         {"targets": [{"repository": REPO, "milestones": [True]}]}, {"timing": {"timeout": 0}},
                         {"runtime": {"enabled": True, "server": "http://user:secret@host"}},
                         {"runtime": {"enabled": True, "expected_version": "2.3"}}):
            config.write_text(json.dumps({**CONFIG, **override}))
            with self.assertRaises(MonitorError): load(config)
        result = self.run_cli("collect", "--once")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["milestones"], [])
        self.assertTrue((self.path/"state/aew/monitor.sqlite3").exists())
        self.assertEqual(self.run_cli("--help").returncode, 0)
        self.assertIn("TTY", self.run_cli("dashboard").stderr)

    def test_install_other_cwd_idempotent_and_conflicting_symlink(self):
        bin_dir = self.path/"bin"
        cmd = [str(ROOT/"scripts/install-aew"), "--bin-dir", str(bin_dir)]
        for _ in range(2):
            result = subprocess.run(cmd, capture_output=True, text=True, env=self.env)
            self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.run_cli("collect", "--once", executable=bin_dir/"aew").returncode, 0)
        (bin_dir/"aew").unlink()
        (bin_dir/"aew").symlink_to(self.path/"other")
        self.assertNotEqual(subprocess.run(cmd, capture_output=True).returncode, 0)
        self.assertTrue((bin_dir/"aew").is_symlink())

    def test_fake_collection_two_projects_restart_offline_and_distribution(self):
        fake = self.path/"gh"
        fake.write_text(FAKE_GH)
        fake.chmod(0o755)
        env = {**self.env, "PATH": f"{self.path}:{self.env['PATH']}"}
        config = copy.deepcopy(CONFIG)
        config["targets"].append({"repository": "other/repo", "milestones": [1]})
        cfg = self.path/"targets.json"
        cfg.write_text(json.dumps(config))
        args = ("collect", "--once", "--config", str(cfg))
        result = self.run_cli(*args, env=env)
        self.assertEqual(result.returncode, 0, result.stderr)
        values = json.loads(result.stdout)["milestones"]
        self.assertEqual(len(values), 2)
        self.assertEqual([g["totals"]["pending"] for g in values], [1, 1])
        second = self.run_cli(*args, env={**env, "FAKE_OFFLINE": "1"})
        self.assertEqual(second.returncode, 1)
        restored = json.loads(second.stdout)
        self.assertEqual([len(g["issues"]) for g in restored["milestones"]], [1, 1])
        self.assertNotIn("PRIVATE_TOKEN", second.stdout+second.stderr)
        db = self.path/"state/aew/monitor.sqlite3"
        self.assertNotIn(b"PRIVATE_TOKEN", db.read_bytes())
        packaged = ROOT/"plugins/my-ai-skills/scripts/aew"
        if packaged.exists():
            result = self.run_cli("--help", executable=packaged)
            self.assertEqual(result.returncode, 0, result.stderr)
            result = self.run_cli(*args, "--state-dir", str(self.path/"packaged-state"), executable=packaged, env=env)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(len(json.loads(result.stdout)["milestones"]), 2)

    def test_git_identity_real_checkout_and_branch_rejection(self):
        directory = self.path/"repo"
        subprocess.run(["git", "init", "-q", str(directory)], check=True)
        subprocess.run(["git", "-C", str(directory), "remote", "add", "origin", f"git@github.com:{REPO}.git"], check=True)
        self.assertTrue(git_identity(str(directory), REPO))
        with self.assertRaises(MonitorError): git_identity(str(directory), "wrong/repo")
        with self.assertRaises(MonitorError): git_identity(str(directory), REPO, "wrong-branch")

    def test_demo_preserved_and_compiles_without_credentials(self):
        demo = ROOT/"examples/milestone-monitor/dashboard.py"
        py_compile.compile(str(demo), cfile=str(self.path/"demo.pyc"), doraise=True)
        self.assertIn("DADOS SIMULADOS", demo.read_text().upper())
