# Tomli incorporado

Dependência de produção limitada à inspeção de `config.toml` do Codex:
**Tomli 2.5.0**, puro Python, zero dependências de runtime, Python upstream >=3.8
(instalador continua exigindo **3.10+**). O mesmo parser é usado em todos os
Pythons suportados, sem `tomllib`, pacote ambiente, pip, build ou download extra.
OpenCode-only não carrega esse parser.

- Origem: https://github.com/hukkin/tomli
- Commit da tag 2.5.0: `a2a578949199336ebc3884eeba4aede87da41ef2`
- Sdist: https://files.pythonhosted.org/packages/b0/78/9ad63712633ed3ab5cc1a648d863d7e7da371e9425e209555a0fe711b695/tomli-2.5.0.tar.gz
- Tamanho: 17.662 bytes
- SHA-256: `264507556cd8b8c8e7c6ee037cdf443a463f03f4c958e57195e3d369711b8ff6`

O literal `TOMLI_SDIST_B85` em `scripts/install-global` contém os bytes exatos
desse sdist. O loader autentica tamanho/hash **antes** da descompressão e lê
somente seis membros regulares. Não extrai paths do archive; escreve nomes
fixos em temporário privado, importa em namespace privado sem mudar `sys.path`,
evita bytecode e remove módulos/temporário também em falha. Os arquivos Python
upstream permanecem intactos. A licença completa está aqui e no standalone.

| Membro sob `tomli-2.5.0/` | SHA-256 |
|---|---|
| `src/tomli/__init__.py` | `7182927b251660b7d649eec79e0dcaf03a59973793400990a693d9f6f8b73eca` |
| `src/tomli/_parser.py` | `3e782f1bc85639ecef630ae686df3d849f2bedd2e9c987d8f5109a5a154df131` |
| `src/tomli/_re.py` | `a12359fe294523a72112e434d58452a14c9d050affa2417f9927474e4166bfdd` |
| `src/tomli/_types.py` | `f864c6d9552a929c7032ace654ee05ef26ca75d21b027b801d77e65907138b74` |
| `src/tomli/py.typed` | `f0f8f2675695a10a5156fb7bd66bafbaae6a13e8d315990af862c792175e6e67` |
| `LICENSE` | `b80816b0d530b8accb4c2211783790984a6e3b61922c2b5ee92f3372ab2742fe` |

## Inspeção offline

Sem importar/executar o instalador ou parser:

```sh
python3 - <<'PY'
import ast, base64, hashlib, io, tarfile
from pathlib import Path
tree = ast.parse(Path("scripts/install-global").read_text())
value = next(n.value for n in tree.body if isinstance(n, ast.Assign)
             and any(isinstance(t, ast.Name) and t.id == "TOMLI_SDIST_B85"
                     for t in n.targets))
payload = base64.b85decode(ast.literal_eval(value))
assert len(payload) == 17662
assert hashlib.sha256(payload).hexdigest() == "264507556cd8b8c8e7c6ee037cdf443a463f03f4c958e57195e3d369711b8ff6"
with tarfile.open(fileobj=io.BytesIO(payload)) as archive:
    for member in archive.getmembers():
        if member.isfile() and (member.name.startswith("tomli-2.5.0/src/tomli/")
                                or member.name == "tomli-2.5.0/LICENSE"):
            print(member.name, hashlib.sha256(archive.extractfile(member).read()).hexdigest())
PY
```

## Manutenção e confiança

Atualização é revisão explícita: conferir release/commit imutáveis, Python
mínimo, changelog e licença; comparar bytes dos seis membros com upstream;
substituir **todo** o sdist/literal e hashes, sem editar o parser. Rodar testes
offline e em Python 3.10 real. Criar novo instalador A e launcher B posterior,
pinando SHA completo e digest literal de **todos** os bytes de A. Nunca emendar
âncoras publicadas, resolver `latest` ou autoatualizar esta dependência em HOME.

O hash interno fixa proveniência, não autentica o próprio instalador: alterar
payload e hash ainda deve ser recusado pelo pin externo. O bootstrap obtido de
main não verifica a si próprio. Merge commit preserva âncoras; disponibilidade
pública após integração precisa ser verificada antes de declarar publicação.

## Licença upstream integral

MIT License

Copyright (c) 2021 Taneli Hukkinen

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
