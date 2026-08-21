from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

# ============================================================
# CAMINHOS
# ============================================================

BASE = Path(__file__).parent
DATA = BASE / "data" / "sales.csv"
OUTPUT = BASE / "saida"
GRAFICOS = BASE / "graficos"

OUTPUT.mkdir(exist_ok=True)
GRAFICOS.mkdir(exist_ok=True)

# ============================================================
# CARREGAMENTO E TRATAMENTO
# ============================================================

df = pd.read_csv(DATA)

# Compatibilidade com nomes de colunas
df.columns = df.columns.str.strip().str.lower()

if "date" in df.columns:
    df["date"] = pd.to_datetime(df["date"])
elif "data" in df.columns:
    df.rename(columns={"data": "date"}, inplace=True)
    df["date"] = pd.to_datetime(df["date"])

# Receita
df["receita"] = df["quantity"] * df["unit_price"]

# ============================================================
# KPIs
# ============================================================

faturamento_total = df["receita"].sum()
pedidos = len(df)
ticket_medio = faturamento_total / pedidos if pedidos else 0

quantidade_total = df["quantity"].sum()

produto_receita = (
    df.groupby("product", as_index=False)
    .agg(
        quantidade=("quantity", "sum"),
        receita=("receita", "sum")
    )
    .sort_values("receita", ascending=False)
)

produto_lider = produto_receita.iloc[0]["product"]
receita_produto_lider = produto_receita.iloc[0]["receita"]

participacao_lider = (
    receita_produto_lider / faturamento_total * 100
    if faturamento_total else 0
)

categoria_receita = (
    df.groupby("category", as_index=False)["receita"]
    .sum()
    .sort_values("receita", ascending=False)
)

cidade_receita = (
    df.groupby("city", as_index=False)["receita"]
    .sum()
    .sort_values("receita", ascending=False)
)

categoria_lider = categoria_receita.iloc[0]["category"]
cidade_lider = cidade_receita.iloc[0]["city"]

# ============================================================
# ANÁLISE TEMPORAL
# ============================================================

df["mes"] = df["date"].dt.to_period("M").astype(str)

receita_mensal = (
    df.groupby("mes", as_index=False)["receita"]
    .sum()
    .sort_values("mes")
)

if len(receita_mensal) > 1:
    receita_mensal["crescimento_pct"] = (
        receita_mensal["receita"].pct_change() * 100
    )
else:
    receita_mensal["crescimento_pct"] = 0

melhor_mes = receita_mensal.loc[
    receita_mensal["receita"].idxmax(), "mes"
]

# ============================================================
# SALVAR TABELAS
# ============================================================

produto_receita.to_csv(
    OUTPUT / "ranking_produtos.csv",
    index=False
)

categoria_receita.to_csv(
    OUTPUT / "receita_categorias.csv",
    index=False
)

cidade_receita.to_csv(
    OUTPUT / "receita_cidades.csv",
    index=False
)

receita_mensal.to_csv(
    OUTPUT / "receita_mensal.csv",
    index=False
)

resumo_kpis = pd.DataFrame({
    "indicador": [
        "Faturamento total",
        "Ticket médio",
        "Pedidos",
        "Itens vendidos",
        "Produto líder",
        "Categoria líder",
        "Cidade líder",
        "Melhor mês"
    ],
    "resultado": [
        round(faturamento_total, 2),
        round(ticket_medio, 2),
        pedidos,
        quantidade_total,
        produto_lider,
        categoria_lider,
        cidade_lider,
        melhor_mes
    ]
})

resumo_kpis.to_csv(
    OUTPUT / "resumo_kpis.csv",
    index=False
)

# ============================================================
# GRÁFICO 1 — TOP PRODUTOS
# ============================================================

top10 = produto_receita.head(10).sort_values("receita")

plt.figure(figsize=(10, 6))
plt.barh(top10["product"], top10["receita"])
plt.title("Top 10 Produtos por Faturamento")
plt.xlabel("Receita (R$)")
plt.ylabel("Produto")
plt.tight_layout()
plt.savefig(
    GRAFICOS / "top_produtos.png",
    dpi=160,
    bbox_inches="tight"
)
plt.close()

# ============================================================
# GRÁFICO 2 — RECEITA POR CATEGORIA
# ============================================================

plt.figure(figsize=(9, 5))
plt.bar(
    categoria_receita["category"],
    categoria_receita["receita"]
)
plt.title("Receita por Categoria")
plt.xlabel("Categoria")
plt.ylabel("Receita (R$)")
plt.xticks(rotation=30)
plt.tight_layout()
plt.savefig(
    GRAFICOS / "receita_por_categoria.png",
    dpi=160,
    bbox_inches="tight"
)
plt.close()

# ============================================================
# GRÁFICO 3 — RECEITA POR CIDADE
# ============================================================

plt.figure(figsize=(9, 5))
plt.bar(
    cidade_receita["city"],
    cidade_receita["receita"]
)
plt.title("Receita por Cidade")
plt.xlabel("Cidade")
plt.ylabel("Receita (R$)")
plt.xticks(rotation=30)
plt.tight_layout()
plt.savefig(
    GRAFICOS / "receita_por_cidade.png",
    dpi=160,
    bbox_inches="tight"
)
plt.close()

# ============================================================
# GRÁFICO 4 — EVOLUÇÃO MENSAL
# ============================================================

plt.figure(figsize=(10, 5))
plt.plot(
    receita_mensal["mes"],
    receita_mensal["receita"],
    marker="o"
)
plt.title("Evolução Mensal do Faturamento")
plt.xlabel("Mês")
plt.ylabel("Receita (R$)")
plt.xticks(rotation=45)
plt.grid(alpha=0.25)
plt.tight_layout()
plt.savefig(
    GRAFICOS / "evolucao_mensal.png",
    dpi=160,
    bbox_inches="tight"
)
plt.close()

# ============================================================
# GRÁFICO 5 — QUANTIDADE POR PRODUTO
# ============================================================

top_quantidade = (
    produto_receita
    .sort_values("quantidade", ascending=False)
    .head(10)
    .sort_values("quantidade")
)

plt.figure(figsize=(10, 6))
plt.barh(
    top_quantidade["product"],
    top_quantidade["quantidade"]
)
plt.title("Produtos Mais Vendidos por Quantidade")
plt.xlabel("Quantidade")
plt.ylabel("Produto")
plt.tight_layout()
plt.savefig(
    GRAFICOS / "quantidade_por_produto.png",
    dpi=160,
    bbox_inches="tight"
)
plt.close()

# ============================================================
# GRÁFICO 6 — PARTICIPAÇÃO DOS PRODUTOS
# ============================================================

participacao = produto_receita.head(6).copy()

outros = produto_receita.iloc[6:]["receita"].sum()

if outros > 0:
    participacao.loc[len(participacao)] = [
        "Outros",
        produto_receita.iloc[6:]["quantidade"].sum(),
        outros
    ]

plt.figure(figsize=(8, 8))
plt.pie(
    participacao["receita"],
    labels=participacao["product"],
    autopct="%1.1f%%",
    startangle=90
)
plt.title("Participação dos Produtos no Faturamento")
plt.tight_layout()
plt.savefig(
    GRAFICOS / "participacao_produtos.png",
    dpi=160,
    bbox_inches="tight"
)
plt.close()

# ============================================================
# RELATÓRIO TXT
# ============================================================

relatorio = f"""
============================================
SALES DATA ANALYSIS
============================================

KPIs

Faturamento total: R$ {faturamento_total:,.2f}
Ticket médio: R$ {ticket_medio:,.2f}
Pedidos analisados: {pedidos}
Itens vendidos: {quantidade_total}

Produto líder: {produto_lider}
Receita do produto líder: R$ {receita_produto_lider:,.2f}
Participação no faturamento: {participacao_lider:.2f}%

Categoria líder: {categoria_lider}
Cidade líder: {cidade_lider}
Melhor mês: {melhor_mes}

============================================
TOP 5 PRODUTOS
============================================

{produto_receita.head(5).to_string(index=False)}

============================================
INSIGHTS
============================================

O produto {produto_lider} possui a maior participação
no faturamento da base analisada.

A categoria com maior faturamento é {categoria_lider}.

A cidade com melhor desempenho é {cidade_lider}.

O período com maior faturamento foi {melhor_mes}.

A concentração de receita nos principais produtos
deve ser considerada no planejamento comercial,
estoque e estratégia de vendas.
"""

with open(
    OUTPUT / "resultado.txt",
    "w",
    encoding="utf-8"
) as arquivo:
    arquivo.write(relatorio)

# ============================================================
# TERMINAL
# ============================================================

print("\n======================================")
print("📊 SALES DATA ANALYSIS")
print("======================================")

print(f"\n💰 Faturamento: R$ {faturamento_total:,.2f}")
print(f"🎫 Ticket médio: R$ {ticket_medio:,.2f}")
print(f"🧾 Pedidos: {pedidos}")
print(f"📦 Itens vendidos: {quantidade_total}")

print(f"\n🏆 Produto líder: {produto_lider}")
print(f"📊 Participação: {participacao_lider:.2f}%")
print(f"🏷️ Categoria líder: {categoria_lider}")
print(f"🌎 Cidade líder: {cidade_lider}")
print(f"📅 Melhor mês: {melhor_mes}")

print("\n✅ Análise concluída com sucesso.")
print(f"📁 Relatórios: {OUTPUT}")
print(f"📈 Gráficos: {GRAFICOS}")