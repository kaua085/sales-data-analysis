from pathlib import Path

import pandas as pd
import streamlit as st
import plotly.express as px


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

    df["date"] = pd.to_datetime(
        df["date"]
    )

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

    df["ano_mes"] = (
        df["date"]
        .dt.to_period("M")
        .astype(str)
    )

    return df


df = carregar_dados()


# =========================================================
# CABEÇALHO
# =========================================================

st.title("📊 Painel de Análise de Vendas")

st.caption(
    "Dashboard interativo para análise de desempenho "
    "comercial, produtos, mercados e comportamento das vendas."
)


# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.header("🔎 Filtros")


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
    "Canal de venda",
    sorted(df["channel"].unique()),
    default=sorted(df["channel"].unique()),
)


pagamentos = st.sidebar.multiselect(
    "Forma de pagamento",
    sorted(df["payment_method"].unique()),
    default=sorted(
        df["payment_method"].unique()
    ),
)


data_min = df["date"].min().date()
data_max = df["date"].max().date()


periodo = st.sidebar.date_input(
    "Período",
    value=(data_min, data_max),
    min_value=data_min,
    max_value=data_max,
)


# =========================================================
# FILTRAGEM
# =========================================================

df_filtrado = df[
    df["category"].isin(categorias)
    & df["city"].isin(cidades)
    & df["product"].isin(produtos)
    & df["channel"].isin(canais)
    & df["payment_method"].isin(pagamentos)
].copy()


if len(periodo) == 2:

    inicio = pd.Timestamp(periodo[0])
    fim = pd.Timestamp(periodo[1])

    df_filtrado = df_filtrado[
        (df_filtrado["date"] >= inicio)
        & (df_filtrado["date"] <= fim)
    ]


if df_filtrado.empty:

    st.warning(
        "Nenhum registro encontrado para os filtros selecionados."
    )

    st.stop()


# =========================================================
# KPIs
# =========================================================

faturamento = df_filtrado["receita"].sum()

pedidos = df_filtrado["order_id"].nunique()

itens = df_filtrado["quantity"].sum()

ticket = (
    faturamento / pedidos
    if pedidos > 0
    else 0
)

produto_lider = (
    df_filtrado
    .groupby("product")["receita"]
    .sum()
    .idxmax()
)


k1, k2, k3, k4, k5 = st.columns(5)


k1.metric(
    "💰 Faturamento",
    f"R$ {faturamento:,.2f}"
)


k2.metric(
    "🎫 Ticket médio",
    f"R$ {ticket:,.2f}"
)


k3.metric(
    "🧾 Pedidos",
    f"{pedidos:,}"
)


k4.metric(
    "📦 Itens vendidos",
    f"{itens:,}"
)


k5.metric(
    "🏆 Produto líder",
    produto_lider
)


st.divider()


# =========================================================
# INSIGHTS AUTOMÁTICOS
# =========================================================

categoria_lider = (
    df_filtrado
    .groupby("category")["receita"]
    .sum()
    .idxmax()
)


cidade_lider = (
    df_filtrado
    .groupby("city")["receita"]
    .sum()
    .idxmax()
)


receita_produto = (
    df_filtrado
    .groupby("product")["receita"]
    .sum()
)


participacao_lider = (
    receita_produto.max()
    / faturamento
    * 100
)


i1, i2, i3 = st.columns(3)

i1.info(
    f"🏷️ Categoria com maior receita: "
    f"**{categoria_lider}**"
)

i2.info(
    f"🌎 Cidade com maior receita: "
    f"**{cidade_lider}**"
)

i3.info(
    f"📊 {produto_lider} representa "
    f"**{participacao_lider:.1f}%** da receita."
)


# =========================================================
# EVOLUÇÃO MENSAL
# =========================================================

st.subheader(
    "📈 Evolução do faturamento"
)


mensal = (
    df_filtrado
    .groupby("ano_mes", as_index=False)["receita"]
    .sum()
)


mensal["crescimento_pct"] = (
    mensal["receita"]
    .pct_change()
    * 100
)


fig_mensal = px.line(
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
    fig_mensal,
    use_container_width=True,
)


# =========================================================
# PRODUTOS + CATEGORIAS
# =========================================================

col1, col2 = st.columns(2)


with col1:

    st.subheader(
        "🏆 Produtos por faturamento"
    )

    ranking_produtos = (
        df_filtrado
        .groupby(
            "product",
            as_index=False
        )["receita"]
        .sum()
        .sort_values(
            "receita",
            ascending=False
        )
    )

    fig_produtos = px.bar(
        ranking_produtos,
        x="receita",
        y="product",
        orientation="h",
        labels={
            "product": "Produto",
            "receita": "Faturamento (R$)",
        },
    )

    fig_produtos.update_layout(
        yaxis={
            "categoryorder": "total ascending"
        }
    )

    st.plotly_chart(
        fig_produtos,
        use_container_width=True,
    )


with col2:

    st.subheader(
        "🏷️ Receita por categoria"
    )

    ranking_categoria = (
        df_filtrado
        .groupby(
            "category",
            as_index=False
        )["receita"]
        .sum()
    )

    fig_categoria = px.pie(
        ranking_categoria,
        names="category",
        values="receita",
        hole=0.45,
    )

    st.plotly_chart(
        fig_categoria,
        use_container_width=True,
    )


# =========================================================
# CIDADE + CANAL
# =========================================================

col3, col4 = st.columns(2)


with col3:

    st.subheader(
        "🌎 Faturamento por cidade"
    )

    ranking_cidades = (
        df_filtrado
        .groupby(
            "city",
            as_index=False
        )["receita"]
        .sum()
        .sort_values(
            "receita",
            ascending=False
        )
    )

    fig_cidade = px.bar(
        ranking_cidades,
        x="city",
        y="receita",
        labels={
            "city": "Cidade",
            "receita": "Faturamento (R$)",
        },
    )

    st.plotly_chart(
        fig_cidade,
        use_container_width=True,
    )


with col4:

    st.subheader(
        "🛒 Receita por canal"
    )

    ranking_canais = (
        df_filtrado
        .groupby(
            "channel",
            as_index=False
        )["receita"]
        .sum()
    )

    fig_canais = px.bar(
        ranking_canais,
        x="channel",
        y="receita",
        labels={
            "channel": "Canal",
            "receita": "Faturamento (R$)",
        },
    )

    st.plotly_chart(
        fig_canais,
        use_container_width=True,
    )


# =========================================================
# PAGAMENTOS
# =========================================================

st.subheader(
    "💳 Distribuição por forma de pagamento"
)


ranking_pagamentos = (
    df_filtrado
    .groupby(
        "payment_method",
        as_index=False
    )["receita"]
    .sum()
)


fig_pagamentos = px.pie(
    ranking_pagamentos,
    names="payment_method",
    values="receita",
    hole=0.45,
)


st.plotly_chart(
    fig_pagamentos,
    use_container_width=True,
)


# =========================================================
# CRESCIMENTO
# =========================================================

st.subheader(
    "📊 Crescimento mensal"
)


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


# =========================================================
# TABELA
# =========================================================

st.subheader(
    "📋 Dados filtrados"
)


st.dataframe(
    df_filtrado,
    use_container_width=True,
    hide_index=True,
)


# =========================================================
# DOWNLOAD
# =========================================================

csv = df_filtrado.to_csv(
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