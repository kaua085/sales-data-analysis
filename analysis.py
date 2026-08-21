from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

BASE = Path(__file__).parent
DATA = BASE / "data" / "sales.csv"
OUTPUT = BASE / "saida"
GRAFICOS = BASE / "graficos"

OUTPUT.mkdir(exist_ok=True)
GRAFICOS.mkdir(exist_ok=True)

# ============================================================
# CARREGAMENTO
# ============================================================

df = pd.read_csv(DATA, parse_dates=["date"])

df.columns = (
    df.columns
    .str.strip()
    .str.lower()
)

# ============================================================
# TRATAMENTO
# ============================================================

df = df.drop_duplicates()

colunas_numericas = [
    "quantity",
    "unit_price",
    "discount",
]

for coluna in colunas_numericas:
    df[coluna] = pd.to_numeric(
        df[coluna],
        errors="coerce",
    )

df["discount"] = df["discount"].fillna(0)

df = df.dropna(
    subset=[
        "date",
        "product",
        "category",
        "city",
        "quantity",
        "unit_price",
    ]
)

# ============================================================
# ENGENHARIA DE ATRIBUTOS
# ============================================================

df["receita_bruta"] = (
    df["quantity"] * df["unit_price"]
)

df["valor_desconto"] = (
    df["receita_bruta"] * df["discount"]
)

df["receita"] = (
    df["receita_bruta"] - df["valor_desconto"]
)

df["ano"] = df["date"].dt.year
df["mes"] = df["date"].dt.month

df["ano_mes"] = (
    df["date"]
    .dt.to_period("M")
    .astype(str)
)

# ============================================================
# KPIs
# ============================================================

faturamento_bruto = df["receita_bruta"].sum()
descontos = df["valor_desconto"].sum()
faturamento = df["receita"].sum()

pedidos = df["order_id"].nunique()
itens = df["quantity"].sum()

ticket = faturamento / pedidos if pedidos else 0

desconto_medio = (
    descontos / faturamento_bruto * 100
    if faturamento_bruto
    else 0
)

# ============================================================
# RANKINGS
# ============================================================

produtos = (
    df.groupby("product")
    .agg(
        quantidade=("quantity", "sum"),
        receita=("receita", "sum"),
    )
    .sort_values("receita", ascending=False)
)

categorias = (
    df.groupby("category")["receita"]
    .sum()
    .sort_values(ascending=False)
)

cidades = (
    df.groupby("city")["receita"]
    .sum()
    .sort_values(ascending=False)
)

regioes = (
    df.groupby("region")["receita"]
    .sum()
    .sort_values(ascending=False)
)

canais = (
    df.groupby("channel")["receita"]
    .sum()
    .sort_values(ascending=False)
)

pagamentos = (
    df.groupby("payment_method")["receita"]
    .sum()
    .sort_values(ascending=False)
)

produto_lider = produtos.index[0]
categoria_lider = categorias.index[0]
cidade_lider = cidades.index[0]
canal_lider = canais.index[0]

participacao_produto = (
    produtos.iloc[0]["receita"] /
    faturamento * 100
)

# ============================================================
# ANÁLISE TEMPORAL
# ============================================================

mensal = (
    df.groupby("ano_mes", as_index=False)
    .agg(
        receita=("receita", "sum"),
        pedidos=("order_id", "nunique"),
        itens=("quantity", "sum"),
    )
    .sort_values("ano_mes")
)

mensal["crescimento_pct"] = (
    mensal["receita"]
    .pct_change() * 100
)

melhor_mes = mensal.loc[
    mensal["receita"].idxmax()
]

# ============================================================
# EXPORTAÇÃO
# ============================================================

produtos.to_csv(OUTPUT / "ranking_produtos.csv")
categorias.to_csv(OUTPUT / "receita_categorias.csv")
cidades.to_csv(OUTPUT / "receita_cidades.csv")
regioes.to_csv(OUTPUT / "receita_regioes.csv")
canais.to_csv(OUTPUT / "receita_canais.csv")
pagamentos.to_csv(OUTPUT / "formas_pagamento.csv")

mensal.to_csv(
    OUTPUT / "evolucao_mensal.csv",
    index=False,
)

resumo = pd.DataFrame(
    {
        "indicador": [
            "Faturamento bruto",
            "Descontos",
            "Faturamento líquido",
            "Ticket médio",
            "Pedidos",
            "Itens vendidos",
            "Produto líder",
            "Categoria líder",
            "Cidade líder",
            "Canal líder",
            "Melhor mês",
        ],
        "resultado": [
            round(faturamento_bruto, 2),
            round(descontos, 2),
            round(faturamento, 2),
            round(ticket, 2),
            pedidos,
            itens,
            produto_lider,
            categoria_lider,
            cidade_lider,
            canal_lider,
            melhor_mes["ano_mes"],
        ],
    }
)

resumo.to_csv(
    OUTPUT / "resumo_kpis.csv",
    index=False,
)

# ============================================================
# GRÁFICOS
# ============================================================

plt.figure(figsize=(10, 6))

produtos.head(10).sort_values("receita")[
    "receita"
].plot(kind="barh")

plt.title("Top 10 Produtos por Faturamento")
plt.xlabel("Receita (R$)")
plt.ylabel("Produto")
plt.tight_layout()

plt.savefig(
    GRAFICOS / "top_produtos.png",
    dpi=160,
)

plt.close()


plt.figure(figsize=(9, 5))

categorias.plot(kind="bar")

plt.title("Receita por Categoria")
plt.xlabel("Categoria")
plt.ylabel("Receita (R$)")
plt.xticks(rotation=30, ha="right")
plt.tight_layout()

plt.savefig(
    GRAFICOS / "receita_por_categoria.png",
    dpi=160,
)

plt.close()


plt.figure(figsize=(10, 5))

cidades.plot(kind="bar")

plt.title("Receita por Cidade")
plt.xlabel("Cidade")
plt.ylabel("Receita (R$)")
plt.xticks(rotation=30, ha="right")
plt.tight_layout()

plt.savefig(
    GRAFICOS / "receita_por_cidade.png",
    dpi=160,
)

plt.close()


plt.figure(figsize=(12, 6))

plt.plot(
    mensal["ano_mes"],
    mensal["receita"],
    marker="o",
)

plt.title("Evolução Mensal do Faturamento")
plt.xlabel("Mês")
plt.ylabel("Receita (R$)")
plt.xticks(rotation=45, ha="right")
plt.grid(alpha=0.25)
plt.tight_layout()

plt.savefig(
    GRAFICOS / "evolucao_mensal.png",
    dpi=160,
)

plt.close()


plt.figure(figsize=(10, 6))

produtos.head(10).sort_values("quantidade")[
    "quantidade"
].plot(kind="barh")

plt.title("Top Produtos por Quantidade Vendida")
plt.xlabel("Quantidade")
plt.ylabel("Produto")
plt.tight_layout()

plt.savefig(
    GRAFICOS / "quantidade_por_produto.png",
    dpi=160,
)

plt.close()

# ============================================================
# RELATÓRIO
# ============================================================

relatorio = f"""
==================================================
SALES DATA ANALYSIS
==================================================

REGISTROS ANALISADOS: {len(df):,}

KPIs

Faturamento bruto: R$ {faturamento_bruto:,.2f}
Descontos concedidos: R$ {descontos:,.2f}
Faturamento líquido: R$ {faturamento:,.2f}

Ticket médio: R$ {ticket:,.2f}
Pedidos: {pedidos:,}
Itens vendidos: {itens:,}
Desconto sobre faturamento bruto: {desconto_medio:.2f}%

Produto líder: {produto_lider}
Participação do produto líder: {participacao_produto:.2f}%

Categoria líder: {categoria_lider}
Cidade líder: {cidade_lider}
Canal líder: {canal_lider}

Melhor mês: {melhor_mes["ano_mes"]}
Receita do melhor mês: R$ {melhor_mes["receita"]:,.2f}

==================================================
TOP 10 PRODUTOS
==================================================

{produtos.head(10).to_string()}

==================================================
INSIGHTS
==================================================

O produto {produto_lider} apresentou a maior receita,
representando {participacao_produto:.2f}% do faturamento.

A categoria líder foi {categoria_lider}.

A cidade com maior faturamento foi {cidade_lider}.

O canal com maior receita foi {canal_lider}.

O melhor período da série foi {melhor_mes["ano_mes"]}.

Os indicadores permitem acompanhar concentração de receita,
desempenho comercial, comportamento temporal e distribuição
das vendas.
"""

with open(
    OUTPUT / "resultado.txt",
    "w",
    encoding="utf-8",
) as arquivo:
    arquivo.write(relatorio)

print(relatorio)
print("\n✅ Análise concluída com sucesso.")