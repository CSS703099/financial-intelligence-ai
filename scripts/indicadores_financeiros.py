
# GUIA PARA INICIANTES — Indicadores em SQL
# Leia a explicação completa em docs/guia_para_iniciantes.md.
# Comentários são apenas explicações: não mudam o comportamento do programa.
import sqlite3
from pathlib import Path
from contextlib import closing

# Caminhos padrão do projeto
RAIZ = Path(__file__).resolve().parents[1]
BANCO = RAIZ / "financial_intelligence.db"

def obter_indicadores():
    """
    Conecta ao banco SQLite em modo somente leitura (ro), 
    executa a consulta consolidada dos 11 indicadores financeiros 
    e retorna os resultados em formato de dicionário.
    """
    if not BANCO.exists():
        raise FileNotFoundError(
            "Banco não encontrado. Execute criar_banco.py."
        )
    
    consulta = """
        SELECT
            COUNT(*) AS total_pedidos,
            SUM(
                CASE
                    WHEN status = 'concluido' THEN 1
                    ELSE 0
                END
            ) AS pedidos_concluidos,
            SUM(
                CASE
                    WHEN status = 'cancelado' THEN 1
                    ELSE 0
                END
            ) AS pedidos_cancelados,
            ROUND(SUM(
                CASE
                    WHEN status = 'concluido' THEN valor_bruto
                    ELSE 0
                END
            ), 2) AS faturamento_bruto,
            ROUND(SUM(
                CASE
                    WHEN status = 'concluido' THEN taxa_plataforma
                    ELSE 0
                END
            ), 2) AS taxas_plataforma,
            ROUND(SUM(
                CASE
                    WHEN status = 'concluido' THEN taxa_logistica
                    ELSE 0
                END
            ), 2) AS taxas_logistica,
            ROUND(SUM(
                CASE
                    WHEN status = 'concluido' THEN repasse_real
                    ELSE 0
                END
            ), 2) AS repasses_realizados,
            SUM(
                CASE
                    WHEN status = 'concluido' 
                         AND ROUND((valor_bruto - taxa_plataforma - taxa_logistica) - repasse_real, 2) != 0 
                    THEN 1
                    ELSE 0
                END
            ) AS pedidos_divergentes,
            ROUND(SUM(
                CASE
                    WHEN status = 'concluido' 
                    THEN ROUND((valor_bruto - taxa_plataforma - taxa_logistica) - repasse_real, 2)
                    ELSE 0
                END
            ), 2) AS divergencia_liquida,
            ROUND(SUM(
                CASE
                    WHEN status = 'concluido' 
                    THEN ABS(ROUND((valor_bruto - taxa_plataforma - taxa_logistica) - repasse_real, 2))
                    ELSE 0
                END
            ), 2) AS divergencia_absoluta,
            ROUND(
                (
                    SUM(
                        CASE
                            WHEN status = 'concluido' 
                                 AND ROUND((valor_bruto - taxa_plataforma - taxa_logistica) - repasse_real, 2) != 0 
                            THEN 1
                            ELSE 0
                        END
                    ) * 100.0
                ) / NULLIF(SUM(CASE WHEN status = 'concluido' THEN 1 ELSE 0 END), 0),
                2
            ) AS taxa_divergencia_pct
        FROM pedidos
    """

    with closing(
        sqlite3.connect(
            f"file:{BANCO.as_posix()}?mode=ro",
            uri=True
        )
    ) as conexao:
        conexao.row_factory = sqlite3.Row
        resultado = conexao.execute(consulta).fetchone()
        return dict(resultado)

def main():
    try:
        indicadores = obter_indicadores()
        print("FINANCIAL INTELLIGENCE AI")
        print("Resumo financeiro consolidado")
        print("-" * 35)
        for nome, valor in indicadores.items():
            print(f"{nome}: {valor}")
    except Exception as e:
        print(f"Erro ao obter os indicadores: {e}")

if __name__ == "__main__":
    main()