"""Executa consultas SELECT escritas em arquivo .sql (sem bibliotecas extras)."""
import sqlite3
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
DB = RAIZ / "financial_intelligence.db"
if len(sys.argv) != 2:
    raise SystemExit("Uso: python scripts/executar_sql.py sql/00_exploracao.sql")
if not DB.exists():
    raise SystemExit("Banco inexistente. Execute: python scripts/criar_banco.py")
caminho_sql = Path(sys.argv[1])
if not caminho_sql.is_absolute():
    caminho_sql = RAIZ / caminho_sql
if not caminho_sql.resolve().is_relative_to(RAIZ.resolve()):
    raise SystemExit("O arquivo SQL deve estar dentro da pasta do projeto.")
sql = caminho_sql.read_text(encoding="utf-8").strip()
sql_sem_comentarios = re.sub(r"--.*$", "", sql, flags=re.MULTILINE).strip()
if not sql_sem_comentarios:
    raise SystemExit("Exercicio ainda nao preenchido.")
with sqlite3.connect(f"file:{DB}?mode=ro", uri=True) as conexao:
    cursor = conexao.execute(sql)
    cabecalhos = [d[0] for d in cursor.description or []]
    linhas = cursor.fetchmany(100)
if cabecalhos:
    print(" | ".join(cabecalhos))
    print("-" * max(30, len(" | ".join(cabecalhos))))
for linha in linhas:
    print(" | ".join(str(v) for v in linha))
print(f"({len(linhas)} linha(s) exibida(s); maximo 100)")
