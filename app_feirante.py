import streamlit as st
import pandas as pd
from datetime import datetime
from io import BytesIO
import plotly.express as px
import uuid
import os

# =====================================
# CONFIGURAÇÃO
# =====================================

st.set_page_config(
    page_title="Gestão de Vendas da Feira",
    page_icon="🛒",
    layout="wide"
)

ARQUIVO_DADOS = "vendas_feira.xlsx"

# =====================================
# FUNÇÕES
# =====================================

def carregar_dados():

    if os.path.exists(ARQUIVO_DADOS):

        return pd.read_excel(
            ARQUIVO_DADOS,
            engine="openpyxl"
        )

    return pd.DataFrame(
        columns=[
            "ID",
            "Data",
            "Produto",
            "Peso (kg)",
            "Preço Total (R$)"
        ]
    )

def salvar_dados(df):

    df.to_excel(
        ARQUIVO_DADOS,
        index=False,
        engine="openpyxl"
    )

# =====================================
# CARREGAMENTO INICIAL
# =====================================

if "vendas" not in st.session_state:

    st.session_state.vendas = carregar_dados()

# =====================================
# TÍTULO
# =====================================

st.title("🛒 Gestão de Vendas da Feira")

# =====================================
# MENU LATERAL
# =====================================

st.sidebar.header("Nova Venda")

data_venda = st.sidebar.date_input(
    "Data da Venda",
    value=datetime.today().date()
)

produto = st.sidebar.text_input(
    "Produto"
)

peso = st.sidebar.number_input(
    "Peso (kg)",
    min_value=0.0,
    value=1.0,
    step=0.1
)

preco_total = st.sidebar.number_input(
    "Preço Total (R$)",
    min_value=0.0,
    value=0.0,
    step=0.50
)

if st.sidebar.button("Salvar Venda"):

    if produto.strip() == "":

        st.sidebar.error(
            "Informe o nome do produto."
        )

    else:

        nova_venda = pd.DataFrame({
            "ID": [str(uuid.uuid4())[:8].upper()],
            "Data": [data_venda],
            "Produto": [produto],
            "Peso (kg)": [peso],
            "Preço Total (R$)": [preco_total]
        })

        st.session_state.vendas = pd.concat(
            [st.session_state.vendas, nova_venda],
            ignore_index=True
        )

        salvar_dados(
            st.session_state.vendas
        )

        st.sidebar.success(
            "Venda cadastrada com sucesso!"
        )

        st.rerun()

# =====================================
# HISTÓRICO
# =====================================

st.subheader("📋 Histórico de Vendas")

if not st.session_state.vendas.empty:

    vendas = st.session_state.vendas.copy()

    vendas["Data"] = pd.to_datetime(
        vendas["Data"]
    )

    vendas = vendas.sort_values(
        by="Data",
        ascending=False
    )

    vendas_exibicao = vendas.copy()

    vendas_exibicao["Data"] = (
        vendas_exibicao["Data"]
        .dt.strftime("%d/%m/%Y")
    )

    st.dataframe(
        vendas_exibicao,
        use_container_width=True
    )

    # =====================================
    # EXCLUSÃO
    # =====================================

    st.subheader("🗑️ Excluir Venda")

    opcoes_vendas = {}

    for _, linha in vendas.iterrows():

        descricao = (
            f"ID {linha['ID']} | "
            f"{linha['Produto']} | "
            f"{linha['Peso (kg)']} kg | "
            f"R$ {linha['Preço Total (R$)']:.2f}"
        )

        opcoes_vendas[descricao] = linha["ID"]

    venda_selecionada = st.selectbox(
        "Selecione a venda",
        list(opcoes_vendas.keys())
    )

    if "confirmar_exclusao" not in st.session_state:

        st.session_state.confirmar_exclusao = False

    if st.button("Excluir Venda"):

        st.session_state.confirmar_exclusao = True

    if st.session_state.confirmar_exclusao:

        st.warning(
            "⚠️ Tem certeza que deseja excluir esta venda?"
        )

        col1, col2 = st.columns(2)

        with col1:

            if st.button("✅ Confirmar Exclusão"):

                id_venda = opcoes_vendas[
                    venda_selecionada
                ]

                st.session_state.vendas = (
                    st.session_state.vendas[
                        st.session_state.vendas["ID"]
                        != id_venda
                    ]
                    .reset_index(drop=True)
                )

                salvar_dados(
                    st.session_state.vendas
                )

                st.session_state.confirmar_exclusao = False

                st.success(
                    "Venda excluída com sucesso."
                )

                st.rerun()

        with col2:

            if st.button("❌ Cancelar"):

                st.session_state.confirmar_exclusao = False

                st.info(
                    "Exclusão cancelada."
                )

    # =====================================
    # MÉTRICAS
    # =====================================

    faturamento = vendas[
        "Preço Total (R$)"
    ].sum()

    peso_total = vendas[
        "Peso (kg)"
    ].sum()

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Quantidade de Vendas",
        len(vendas)
    )

    col2.metric(
        "Peso Vendido",
        f"{peso_total:.2f} kg"
    )

    col3.metric(
        "Faturamento",
        f"R$ {faturamento:,.2f}"
    )

    # =====================================
    # FATURAMENTO POR PRODUTO
    # =====================================

    st.subheader(
        "📊 Faturamento por Produto"
    )

    vendas_produto = (
        vendas.groupby("Produto")
        ["Preço Total (R$)"]
        .sum()
        .reset_index()
    )

    fig_produto = px.bar(
        vendas_produto,
        x="Produto",
        y="Preço Total (R$)",
        color="Produto",
        text_auto=".2f"
    )

    st.plotly_chart(
        fig_produto,
        use_container_width=True
    )

    # =====================================
    # EVOLUÇÃO DAS VENDAS
    # =====================================

    st.subheader(
        "📈 Evolução das Vendas"
    )

    vendas_dia = (
        vendas.groupby("Data")
        ["Preço Total (R$)"]
        .sum()
        .reset_index()
    )

    fig_tempo = px.line(
        vendas_dia,
        x="Data",
        y="Preço Total (R$)",
        markers=True
    )

    st.plotly_chart(
        fig_tempo,
        use_container_width=True
    )

    # =====================================
    # DOWNLOAD EXCEL
    # =====================================

    st.subheader("📥 Exportação")

    output = BytesIO()

    with pd.ExcelWriter(
        output,
        engine="openpyxl"
    ) as writer:

        vendas.to_excel(
            writer,
            index=False,
            sheet_name="Vendas"
        )

    st.download_button(
        label="📥 Baixar Excel",
        data=output.getvalue(),
        file_name="vendas_feira.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

else:

    st.info(
        "Nenhuma venda cadastrada."
    )

#Deploy: https://www.youtube.com/watch?v=vw0I8i7QJRk