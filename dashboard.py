from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

# ============================================================
# CONFIGURAÇÃO
# ============================================================

BASE = Path(__file__).parent
DATA = BASE / "data" / "sales.csv"

st.set_page_config(
    page_title="Sales Analytics Dashboard",
    page_icon="📊",
    layout="wide",
)

# ============================================================
# DADOS
# ============================================================

@st.cache_data
def carregar_dados():
    df = pd.read_csv(DATA)

    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
    )

    df["date"] = pd.to_datetime(df["date"])

    df["receita"] = (
        df["quantity"] *
        df["unit_price"]
    )

    df["mes"] = (
        df["date"]
        .dt.to_period("M")
        .astype(str)
    )

    return df


df = carregar_dados()

# ============================================================
# CABEÇALHO
# ============================================================

st.title("📊 Painel de Análise de Vendas")

st.caption(
    "Dashboard interativo para acompanhamento de "
    "indicadores comerciais e análise de desempenho."
)

# ============================================================
# FILTROS
# ============================================================

st.sidebar.header("🔎 Filtros")

categorias = sorted(df["category"].dropna().unique())
cidades = sorted(df["city"].dropna().unique())
produtos = sorted(df["product"].dropna().unique())

categorias_selecionadas = st.sidebar.multiselect(
    "Categoria",
    categorias,
    default=categorias,
)

cidades_selecionadas = st.sidebar.multiselect(
    "Cidade",
    cidades,
    default=cidades,
)

produtos_selecionados = st.sidebar.multiselect(
    "Produto",
    produtos,
    default=produtos,
)

data_minima = df["date"].min().date()
data_maxima = df["date"].max().date()

periodo = st.sidebar.date_input(
    "Período",
    value=(data_minima, data_maxima),
    min_value=data_minima,
    max_value=data_maxima,
)

filtrado = df[
    df["category"].isin(categorias_selecionadas)
    & df["city"].isin(cidades_selecionadas)
    & df["product"].isin(produtos_selecionados)
].copy()

if len(periodo) == 2:
    inicio = pd.Timestamp(periodo[0])
    fim = pd.Timestamp(periodo[1])

    filtrado = filtrado[
        (filtrado["date"] >= inicio)
        & (filtrado["date"] <= fim)
    ]

if filtrado.empty:
    st.warning(
        "Nenhum registro encontrado com os filtros selecionados."
    )
    st.stop()

# ============================================================
# KPIs
# ============================================================

faturamento = filtrado["receita"].sum()
pedidos = filtrado["order_id"].nunique()
itens = filtrado["quantity"].sum()

ticket_medio = (
    faturamento / pedidos
    if pedidos
    else 0
)

ranking_produtos = (
    filtrado
    .groupby("product", as_index=False)
    .agg(
        quantidade=("quantity", "sum"),
        receita=("receita", "sum"),
    )
    .sort_values("receita", ascending=False)
)

produto_lider = ranking_produtos.iloc[0]["product"]

categoria_lider = (
    filtrado
    .groupby("category")["receita"]
    .sum()
    .idxmax()
)

cidade_lider = (
    filtrado
    .groupby("city")["receita"]
    .sum()
    .idxmax()
)

# ============================================================
# CARDS
# ============================================================

c1, c2, c3, c4, c5 = st.columns(5)

c1.metric(
    "💰 Faturamento",
    f"R$ {faturamento:,.2f}",
)

c2.metric(
    "🎫 Ticket médio",
    f"R$ {ticket_medio:,.2f}",
)

c3.metric(
    "🧾 Pedidos",
    f"{pedidos}",
)

c4.metric(
    "📦 Itens vendidos",
    f"{int(itens)}",
)

c5.metric(
    "🏆 Produto líder",
    produto_lider,
)

st.divider()

# ============================================================
# INSIGHTS RÁPIDOS
# ============================================================

i1, i2, i3 = st.columns(3)

i1.info(
    f"🏷️ Categoria com maior receita: **{categoria_lider}**"
)

i2.info(
    f"🌎 Cidade com maior receita: **{cidade_lider}**"
)

participacao_lider = (
    ranking_produtos.iloc[0]["receita"] /
    faturamento *
    100
)

i3.info(
    f"📊 {produto_lider} representa "
    f"**{participacao_lider:.1f}%** da receita"
)

# ============================================================
# EVOLUÇÃO DO FATURAMENTO
# ============================================================

st.subheader("📈 Evolução do faturamento")

receita_mensal = (
    filtrado
    .groupby("mes", as_index=False)["receita"]
    .sum()
    .sort_values("mes")
)

fig_evolucao = px.line(
    receita_mensal,
    x="mes",
    y="receita",
    markers=True,
)

fig_evolucao.update_layout(
    xaxis_title="Mês",
    yaxis_title="Receita (R$)",
)

st.plotly_chart(
    fig_evolucao,
    use_container_width=True,
)

# ============================================================
# TOP PRODUTOS + CATEGORIAS
# ============================================================

col1, col2 = st.columns(2)

top_produtos = (
    ranking_produtos
    .head(10)
    .sort_values("receita")
)

fig_produtos = px.bar(
    top_produtos,
    x="receita",
    y="product",
    orientation="h",
    title="🏆 Top 10 Produtos por Faturamento",
)

fig_produtos.update_layout(
    xaxis_title="Receita (R$)",
    yaxis_title="Produto",
)

col1.plotly_chart(
    fig_produtos,
    use_container_width=True,
)

receita_categoria = (
    filtrado
    .groupby("category", as_index=False)["receita"]
    .sum()
    .sort_values("receita", ascending=False)
)

fig_categoria = px.bar(
    receita_categoria,
    x="category",
    y="receita",
    title="🏷️ Receita por Categoria",
)

fig_categoria.update_layout(
    xaxis_title="Categoria",
    yaxis_title="Receita (R$)",
)

col2.plotly_chart(
    fig_categoria,
    use_container_width=True,
)

# ============================================================
# CIDADES + PARTICIPAÇÃO
# ============================================================

col3, col4 = st.columns(2)

receita_cidade = (
    filtrado
    .groupby("city", as_index=False)["receita"]
    .sum()
    .sort_values("receita", ascending=False)
)

fig_cidade = px.bar(
    receita_cidade,
    x="city",
    y="receita",
    title="🌎 Receita por Cidade",
)

fig_cidade.update_layout(
    xaxis_title="Cidade",
    yaxis_title="Receita (R$)",
)

col3.plotly_chart(
    fig_cidade,
    use_container_width=True,
)

fig_participacao = px.pie(
    ranking_produtos.head(8),
    names="product",
    values="receita",
    title="📊 Participação dos Produtos na Receita",
    hole=0.45,
)

col4.plotly_chart(
    fig_participacao,
    use_container_width=True,
)

# ============================================================
# QUANTIDADE VENDIDA
# ============================================================

st.subheader("📦 Produtos mais vendidos")

ranking_quantidade = (
    ranking_produtos
    .sort_values("quantidade", ascending=False)
    .head(10)
)

fig_quantidade = px.bar(
    ranking_quantidade,
    x="product",
    y="quantidade",
)

fig_quantidade.update_layout(
    xaxis_title="Produto",
    yaxis_title="Quantidade vendida",
)

st.plotly_chart(
    fig_quantidade,
    use_container_width=True,
)

# ============================================================
# RANKING
# ============================================================

st.subheader("🏅 Ranking de produtos")

ranking_exibicao = ranking_produtos.copy()

ranking_exibicao["participacao_pct"] = (
    ranking_exibicao["receita"] /
    faturamento *
    100
).round(2)

ranking_exibicao.columns = [
    "Produto",
    "Quantidade",
    "Receita",
    "Participação (%)",
]

st.dataframe(
    ranking_exibicao,
    use_container_width=True,
    hide_index=True,
)

# ============================================================
# DADOS DETALHADOS
# ============================================================

st.subheader("📋 Dados detalhados")

dados_exibicao = filtrado[
    [
        "order_id",
        "date",
        "product",
        "category",
        "quantity",
        "unit_price",
        "city",
        "receita",
    ]
].copy()

dados_exibicao = dados_exibicao.sort_values(
    "date",
    ascending=False,
)

st.dataframe(
    dados_exibicao,
    use_container_width=True,
    hide_index=True,
)

# ============================================================
# DOWNLOAD
# ============================================================

csv = dados_exibicao.to_csv(
    index=False
).encode("utf-8")

st.download_button(
    label="⬇️ Baixar dados filtrados em CSV",
    data=csv,
    file_name="vendas_filtradas.csv",
    mime="text/csv",
)

st.divider()

st.caption(
    "Projeto desenvolvido para portfólio em Análise de Dados."
)
