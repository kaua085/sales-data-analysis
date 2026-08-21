from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt


BASE = Path(__file__).parent
DATA = BASE / "data" / "sales.csv"
OUTPUT = BASE / "saida"
GRAFICOS = BASE / "graficos"

OUTPUT.mkdir(exist_ok=True)
GRAFICOS.mkdir(exist_ok=True)


# =========================================================
# CARREGAMENTO
# =========================================================

df = pd.read_csv(
    DATA,
    parse_dates=["date"]
)


# =========================================================
# TRATAMENTO
# =========================================================

df.columns = (
    df.columns
    .str.strip()
    .str.lower()
)

df = df.drop_duplicates()

df["quantity"] = pd.to_numeric(
    df["quantity"],
    errors="coerce"
)

df["unit_price"] = pd.to_numeric(
    df["unit_price"],
    errors="coerce"
)

df["discount"] = pd.to_numeric(
    df["discount"],
    errors="coerce"
).fillna(0)

df = df.dropna(
    subset=[
        "date",
        "product",
        "quantity",
        "unit_price"
    ]
)


# =========================================================
# ENGENHARIA DE ATRIBUTOS
# =========================================================

df["receita_bruta"] = (
    df["quantity"] *
    df["unit_price"]
)

df["valor_desconto"] = (
    df["receita_bruta"] *
    df["discount"]
)

df["receita"] = (
    df["receita_bruta"] -
    df["valor_desconto"]
)

df["ano"] = df["date"].dt.year
df["mes"] = df["date"].dt.month

df["ano_mes"] = (
    df["date"]
    .dt.to_period("M")
    .astype(str)
)


# =========================================================
# KPIs
# =========================================================

faturamento_total = df["receita"].sum()

faturamento_bruto = df["receita_bruta"].sum()

descontos_total = df["valor_desconto"].sum()

pedidos_unicos = df["order_id"].nunique()

itens_vendidos = df["quantity"].sum()

ticket_medio = (
    faturamento_total / pedidos_unicos
    if pedidos_unicos > 0
    else 0
)


# =========================================================
# PRODUTOS
# =========================================================

produtos = (
    df.groupby("product")
    .agg(
        quantidade=("quantity", "sum"),
        receita=("receita", "sum"),
    )
    .sort_values(
        "receita",
        ascending=False
    )
)

produto_lider = produtos.index[0]


# =========================================================
# CATEGORIAS
# =========================================================

categorias = (
    df.groupby("category")["receita"]
    .sum()
    .sort_values(ascending=False)
)


# =========================================================
# CIDADES
# =========================================================

cidades = (
    df.groupby("city")["receita"]
    .sum()
    .sort_values(ascending=False)
)


# =========================================================
# CANAIS
# =========================================================

canais = (
    df.groupby("channel")["receita"]
    .sum()
    .sort_values(ascending=False)
)


# =========================================================
# PAGAMENTOS
# =========================================================

pagamentos = (
    df.groupby("payment_method")["receita"]
    .sum()
    .sort_values(ascending=False)
)


# =========================================================
# ANÁLISE MENSAL
# =========================================================

mensal = (
    df.groupby("ano_mes")["receita"]
    .sum()
    .reset_index()
)

mensal["crescimento_pct"] = (
    mensal["receita"]
    .pct_change() *
    100
)

melhor_mes = mensal.loc[
    mensal["receita"].idxmax()
]


# =========================================================
# SALVAR RELATÓRIOS
# =========================================================

produtos.to_csv(
    OUTPUT / "produtos.csv"
)

categorias.to_csv(
    OUTPUT / "categorias.csv"
)

cidades.to_csv(
    OUTPUT / "cidades.csv"
)

canais.to_csv(
    OUTPUT / "canais.csv"
)

pagamentos.to_csv(
    OUTPUT / "pagamentos.csv"
)

mensal.to_csv(
    OUTPUT / "evolucao_mensal.csv",
    index=False
)


# =========================================================
# GRÁFICO - PRODUTOS
# =========================================================

plt.figure(figsize=(10, 6))

produtos.head(10)["receita"].plot(
    kind="bar"
)

plt.title(
    "Top 10 Produtos por Receita"
)

plt.xlabel("Produto")
plt.ylabel("Receita (R$)")

plt.xticks(
    rotation=45,
    ha="right"
)

plt.tight_layout()

plt.savefig(
    GRAFICOS / "top_produtos.png",
    dpi=150
)

plt.close()


# =========================================================
# GRÁFICO - CATEGORIAS
# =========================================================

plt.figure(figsize=(8, 5))

categorias.plot(
    kind="bar"
)

plt.title(
    "Receita por Categoria"
)

plt.xlabel("Categoria")
plt.ylabel("Receita (R$)")

plt.xticks(
    rotation=45,
    ha="right"
)

plt.tight_layout()

plt.savefig(
    GRAFICOS / "receita_por_categoria.png",
    dpi=150
)

plt.close()


# =========================================================
# GRÁFICO - CIDADES
# =========================================================

plt.figure(figsize=(9, 5))

cidades.plot(
    kind="bar"
)

plt.title(
    "Receita por Cidade"
)

plt.xlabel("Cidade")
plt.ylabel("Receita (R$)")

plt.xticks(
    rotation=45,
    ha="right"
)

plt.tight_layout()

plt.savefig(
    GRAFICOS / "receita_por_cidade.png",
    dpi=150
)

plt.close()


# =========================================================
# GRÁFICO - EVOLUÇÃO MENSAL
# =========================================================

plt.figure(figsize=(12, 6))

plt.plot(
    mensal["ano_mes"],
    mensal["receita"],
    marker="o"
)

plt.title(
    "Evolução Mensal do Faturamento"
)

plt.xlabel("Mês")
plt.ylabel("Receita (R$)")

plt.xticks(
    rotation=45,
    ha="right"
)

plt.tight_layout()

plt.savefig(
    GRAFICOS / "evolucao_mensal.png",
    dpi=150
)

plt.close()


# =========================================================
# RESULTADO TXT
# =========================================================

resultado = f"""
=== SALES DATA ANALYSIS ===

Registros analisados: {len(df):,}

=== KPIs ===

Faturamento bruto:
R$ {faturamento_bruto:,.2f}

Descontos concedidos:
R$ {descontos_total:,.2f}

Faturamento líquido:
R$ {faturamento_total:,.2f}

Ticket médio:
R$ {ticket_medio:,.2f}

Pedidos únicos:
{pedidos_unicos:,}

Itens vendidos:
{itens_vendidos:,}

Produto líder:
{produto_lider}

Melhor mês:
{melhor_mes["ano_mes"]}

Receita do melhor mês:
R$ {melhor_mes["receita"]:,.2f}


=== TOP 5 PRODUTOS ===

{produtos.head(5).to_string()}


=== TOP CATEGORIAS ===

{categorias.to_string()}


=== RECEITA POR CIDADE ===

{cidades.to_string()}


=== RECEITA POR CANAL ===

{canais.to_string()}


=== FORMAS DE PAGAMENTO ===

{pagamentos.to_string()}
"""

with open(
    BASE / "resultado.txt",
    "w",
    encoding="utf-8"
) as arquivo:

    arquivo.write(resultado)


print(resultado)

print("\n✅ Análise concluída com sucesso.")
print(f"📁 Relatórios: {OUTPUT}")
print(f"📈 Gráficos: {GRAFICOS}")