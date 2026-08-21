from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

# Caminhos do projeto
BASE = Path(__file__).parent
DATA = BASE / "data" / "sales.csv"
OUTPUT = BASE / "saida"
GRAFICOS = BASE / "graficos"

OUTPUT.mkdir(exist_ok=True)
GRAFICOS.mkdir(exist_ok=True)

# Carregar dados
df = pd.read_csv(DATA, parse_dates=["date"])

# Calcular receita
df["receita"] = df["quantity"] * df["unit_price"]

# =========================
# KPIs
# =========================

faturamento_total = df["receita"].sum()

ticket_medio = (
    df.groupby("order_id")["receita"]
    .sum()
    .mean()
)

pedidos_unicos = df["order_id"].nunique()

print("=== KPIs ===")
print(f"Faturamento total: R$ {faturamento_total:,.2f}")
print(f"Ticket médio: R$ {ticket_medio:,.2f}")
print(f"Pedidos únicos: {pedidos_unicos}")

# =========================
# ANÁLISES
# =========================

por_produto = (
    df.groupby("product", as_index=False)
    .agg(
        quantidade=("quantity", "sum"),
        receita=("receita", "sum")
    )
    .sort_values("receita", ascending=False)
)

por_categoria = (
    df.groupby("category", as_index=False)["receita"]
    .sum()
    .sort_values("receita", ascending=False)
)

por_cidade = (
    df.groupby("city", as_index=False)["receita"]
    .sum()
    .sort_values("receita", ascending=False)
)

# =========================
# EXPORTAR RELATÓRIOS
# =========================

por_produto.to_csv(
    OUTPUT / "vendas_por_produto.csv",
    index=False
)

por_categoria.to_csv(
    OUTPUT / "vendas_por_categoria.csv",
    index=False
)

por_cidade.to_csv(
    OUTPUT / "vendas_por_cidade.csv",
    index=False
)

# =========================
# GRÁFICO 1
# Receita por categoria
# =========================

plt.figure(figsize=(10, 6))
plt.bar(
    por_categoria["category"],
    por_categoria["receita"]
)

plt.title("Receita por Categoria")
plt.xlabel("Categoria")
plt.ylabel("Receita (R$)")
plt.xticks(rotation=30)
plt.tight_layout()

plt.savefig(
    GRAFICOS / "receita_por_categoria.png",
    dpi=200
)

plt.close()

# =========================
# GRÁFICO 2
# Top produtos
# =========================

top_produtos = por_produto.head(10)

plt.figure(figsize=(10, 6))
plt.barh(
    top_produtos["product"],
    top_produtos["receita"]
)

plt.title("Top 10 Produtos por Faturamento")
plt.xlabel("Receita (R$)")
plt.ylabel("Produto")
plt.gca().invert_yaxis()
plt.tight_layout()

plt.savefig(
    GRAFICOS / "top_produtos.png",
    dpi=200
)

plt.close()

# =========================
# GRÁFICO 3
# Receita por cidade
# =========================

plt.figure(figsize=(10, 6))
plt.bar(
    por_cidade["city"],
    por_cidade["receita"]
)

plt.title("Receita por Cidade")
plt.xlabel("Cidade")
plt.ylabel("Receita (R$)")
plt.xticks(rotation=30)
plt.tight_layout()

plt.savefig(
    GRAFICOS / "receita_por_cidade.png",
    dpi=200
)

plt.close()

# =========================
# RESULTADO
# =========================

print("\nTop 5 produtos por receita:")
print(por_produto.head(5).to_string(index=False))

print("\nAnálise concluída com sucesso.")
print(f"Relatórios salvos em: {OUTPUT}")
print(f"Gráficos salvos em: {GRAFICOS}")