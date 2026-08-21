from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

BASE = Path(__file__).parent
DATA = BASE / "data" / "sales.csv"

st.set_page_config(
    page_title="Sales Analytics Dashboard",
    page_icon="📊",
    layout="wide",
)


@st.cache_data
def carregar_dados():
    df = pd.read_csv(DATA)

    df["date"] = pd.to_datetime(df["date"])

    df["receita_bruta"] = (
        df["quantity"] * df["unit_price"]
    )

    df["valor_desconto"] = (
        df["receita_bruta"] * df["discount"]
    )

    df["receita"] = (
        df["receita_bruta"] -
        df["valor_desconto"]
    )

    df["ano_mes"] = (
        df["date"]
        .dt.to_period("M")
        .astype(str)
    )

    return df


df = carregar_dados()

# ============================================================
# CABEÇALHO
# ============================================================

st.title("📊 Sales Analytics Dashboard")

st.caption(
    "Análise interativa de desempenho comercial, "
    "produtos, categorias, mercados e evolução das vendas."
)

# ============================================================
# FILTROS
# ============================================================

st.sidebar.title("🔎 Filtros")

categorias = st.sidebar.multiselect(
    "Categoria",
    sorted(df["category"].unique()),
    default=sorted(df["category"].unique()),
)

cidades = st.sidebar.multiselect(
    "Cidade",
    sorted(df["city"].unique()),
    default=sorted(df["city"].unique()),
)

produtos = st.sidebar.multiselect(
    "Produto",
    sorted(df["product"].unique()),
    default=sorted(df["product"].unique()),
)

canais = st.sidebar.multiselect(
    "Canal",
    sorted(df["channel"].unique()),
    default=sorted(df["channel"].unique()),
)

pagamentos = st.sidebar.multiselect(
    "Forma de pagamento",
    sorted(df["payment_method"].unique()),
    default=sorted(df["payment_method"].unique()),
)

data_min = df["date"].min().date()
data_max = df["date"].max().date()

periodo = st.sidebar.date_input(
    "Período",
    value=(data_min, data_max),
    min_value=data_min,
    max_value=data_max,
)

filtrado = df[
    df["category"].isin(categorias)
    & df["city"].isin(cidades)
    & df["product"].isin(produtos)
    & df["channel"].isin(canais)
    & df["payment_method"].isin(pagamentos)
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
        "Nenhum registro encontrado com esses filtros."
    )
    st.stop()

# ============================================================
# KPIs
# ============================================================

faturamento = filtrado["receita"].sum()
faturamento_bruto = filtrado["receita_bruta"].sum()
descontos = filtrado["valor_desconto"].sum()

pedidos = filtrado["order_id"].nunique()
itens = filtrado["quantity"].sum()

ticket = faturamento / pedidos if pedidos else 0

produto_lider = (
    filtrado
    .groupby("product")["receita"]
    .sum()
    .idxmax()
)

k1, k2, k3, k4, k5 = st.columns(5)

k1.metric(
    "💰 Faturamento",
    f"R$ {faturamento:,.2f}",
)

k2.metric(
    "🎫 Ticket médio",
    f"R$ {ticket:,.2f}",
)

k3.metric(
    "🧾 Pedidos",
    f"{pedidos:,}",
)

k4.metric(
    "📦 Itens vendidos",
    f"{int(itens):,}",
)

k5.metric(
    "🏆 Produto líder",
    produto_lider,
)

# ============================================================
# INSIGHTS
# ============================================================

categoria_lider = (
    filtrado.groupby("category")["receita"]
    .sum()
    .idxmax()
)

cidade_lider = (
    filtrado.groupby("city")["receita"]
    .sum()
    .idxmax()
)

canal_lider = (
    filtrado.groupby("channel")["receita"]
    .sum()
    .idxmax()
)

receita_produtos = (
    filtrado.groupby("product")["receita"]
    .sum()
)

participacao = (
    receita_produtos.max() /
    faturamento * 100
)

st.divider()

i1, i2, i3, i4 = st.columns(4)

i1.info(
    f"🏷️ Categoria líder\n\n**{categoria_lider}**"
)

i2.info(
    f"🌎 Cidade líder\n\n**{cidade_lider}**"
)

i3.info(
    f"🛒 Canal líder\n\n**{canal_lider}**"
)

i4.info(
    f"📊 Participação do líder\n\n"
    f"**{participacao:.1f}%**"
)

# ============================================================
# EVOLUÇÃO
# ============================================================

st.subheader("📈 Evolução mensal do faturamento")

mensal = (
    filtrado.groupby(
        "ano_mes",
        as_index=False,
    )["receita"]
    .sum()
    .sort_values("ano_mes")
)

mensal["crescimento_pct"] = (
    mensal["receita"]
    .pct_change() * 100
)

fig = px.line(
    mensal,
    x="ano_mes",
    y="receita",
    markers=True,
    labels={
        "ano_mes": "Mês",
        "receita": "Faturamento (R$)",
    },
)

st.plotly_chart(
    fig,
    use_container_width=True,
)

# ============================================================
# PRODUTOS / CATEGORIAS
# ============================================================

c1, c2 = st.columns(2)

ranking_produtos = (
    filtrado.groupby(
        "product",
        as_index=False,
    )
    .agg(
        receita=("receita", "sum"),
        quantidade=("quantity", "sum"),
    )
    .sort_values(
        "receita",
        ascending=False,
    )
)

fig_produtos = px.bar(
    ranking_produtos.head(10),
    x="receita",
    y="product",
    orientation="h",
    title="🏆 Top Produtos por Faturamento",
)

fig_produtos.update_layout(
    yaxis={
        "categoryorder": "total ascending"
    }
)

c1.plotly_chart(
    fig_produtos,
    use_container_width=True,
)

ranking_categoria = (
    filtrado.groupby(
        "category",
        as_index=False,
    )["receita"]
    .sum()
)

fig_categoria = px.pie(
    ranking_categoria,
    names="category",
    values="receita",
    hole=0.45,
    title="🏷️ Participação por Categoria",
)

c2.plotly_chart(
    fig_categoria,
    use_container_width=True,
)

# ============================================================
# CIDADE / CANAL
# ============================================================

c3, c4 = st.columns(2)

ranking_cidades = (
    filtrado.groupby(
        "city",
        as_index=False,
    )["receita"]
    .sum()
    .sort_values(
        "receita",
        ascending=False,
    )
)

fig_cidade = px.bar(
    ranking_cidades,
    x="city",
    y="receita",
    title="🌎 Faturamento por Cidade",
)

c3.plotly_chart(
    fig_cidade,
    use_container_width=True,
)

ranking_canais = (
    filtrado.groupby(
        "channel",
        as_index=False,
    )["receita"]
    .sum()
)

fig_canal = px.bar(
    ranking_canais,
    x="channel",
    y="receita",
    title="🛒 Receita por Canal",
)

c4.plotly_chart(
    fig_canal,
    use_container_width=True,
)

# ============================================================
# PAGAMENTO / QUANTIDADE
# ============================================================

c5, c6 = st.columns(2)

ranking_pagamentos = (
    filtrado.groupby(
        "payment_method",
        as_index=False,
    )["receita"]
    .sum()
)

fig_pagamentos = px.pie(
    ranking_pagamentos,
    names="payment_method",
    values="receita",
    hole=0.45,
    title="💳 Formas de Pagamento",
)

c5.plotly_chart(
    fig_pagamentos,
    use_container_width=True,
)

ranking_quantidade = (
    ranking_produtos
    .sort_values(
        "quantidade",
        ascending=False,
    )
    .head(10)
)

fig_quantidade = px.bar(
    ranking_quantidade,
    x="product",
    y="quantidade",
    title="📦 Produtos Mais Vendidos",
)

c6.plotly_chart(
    fig_quantidade,
    use_container_width=True,
)

# ============================================================
# CRESCIMENTO
# ============================================================

st.subheader("📊 Crescimento mensal")

crescimento = mensal.dropna().copy()

fig_crescimento = px.bar(
    crescimento,
    x="ano_mes",
    y="crescimento_pct",
    labels={
        "ano_mes": "Mês",
        "crescimento_pct": "Variação (%)",
    },
)

st.plotly_chart(
    fig_crescimento,
    use_container_width=True,
)

# ============================================================
# DESCONTOS
# ============================================================

st.subheader("💵 Visão financeira")

f1, f2, f3 = st.columns(3)

f1.metric(
    "Receita bruta",
    f"R$ {faturamento_bruto:,.2f}",
)

f2.metric(
    "Descontos concedidos",
    f"R$ {descontos:,.2f}",
)

f3.metric(
    "Receita líquida",
    f"R$ {faturamento:,.2f}",
)

# ============================================================
# RANKING
# ============================================================

st.subheader("🏅 Ranking de produtos")

ranking_tabela = ranking_produtos.copy()

ranking_tabela["participacao_pct"] = (
    ranking_tabela["receita"] /
    faturamento * 100
).round(2)

st.dataframe(
    ranking_tabela,
    use_container_width=True,
    hide_index=True,
)

# ============================================================
# DADOS + DOWNLOAD
# ============================================================

st.subheader("📋 Dados detalhados")

st.dataframe(
    filtrado.sort_values(
        "date",
        ascending=False,
    ),
    use_container_width=True,
    hide_index=True,
)

csv = filtrado.to_csv(
    index=False
).encode("utf-8")

st.download_button(
    "⬇️ Baixar dados filtrados em CSV",
    csv,
    "vendas_filtradas.csv",
    "text/csv",
)

st.caption(
    "Base sintética criada exclusivamente para "
    "estudo e demonstração de competências em Análise de Dados."
)