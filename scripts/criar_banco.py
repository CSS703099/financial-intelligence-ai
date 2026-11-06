"""Gera banco SQLite local a partir de dados sinteticos. Usa apenas Python padrao."""

# GUIA PARA INICIANTES — Preparação do banco
# Leia a explicação completa em docs/guia_para_iniciantes.md.
# Comentários são apenas explicações: não mudam o comportamento do programa.
import csv
import sqlite3
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
CSV = RAIZ / "dados" / "pedidos_sinteticos.csv"
DB = RAIZ / "financial_intelligence.db"

with sqlite3.connect(DB) as conexao:
    conexao.execute("DROP TABLE IF EXISTS pedidos")
    conexao.execute("""
        CREATE TABLE pedidos (
            pedido_id TEXT PRIMARY KEY,
            data_pedido TEXT NOT NULL,
            restaurante TEXT NOT NULL,
            status TEXT NOT NULL CHECK(status IN ('concluido', 'cancelado')),
            valor_bruto REAL NOT NULL,
            taxa_plataforma REAL NOT NULL,
            taxa_logistica REAL NOT NULL,
            repasse_real REAL NOT NULL
        )
    """)
    with CSV.open(encoding="utf-8", newline="") as arquivo:
        for linha in csv.DictReader(arquivo):
            conexao.execute("""
                INSERT INTO pedidos
                (pedido_id, data_pedido, restaurante, status, valor_bruto,
                 taxa_plataforma, taxa_logistica, repasse_real)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                linha["pedido_id"], linha["data_pedido"], linha["restaurante"], linha["status"],
                float(linha["valor_bruto"]), float(linha["taxa_plataforma"]),
                float(linha["taxa_logistica"]), float(linha["repasse_real"])
            ))
    conexao.commit()
    total = conexao.execute("SELECT COUNT(*) FROM pedidos").fetchone()[0]
print(f"Banco criado: {DB.name} | Registros: {total}")
print("AVISO: dataset inteiramente ficticio, para estudo. Nao inclui dados do iFood.")
