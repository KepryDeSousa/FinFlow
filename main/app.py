import streamlit as st
import pandas as pd
import plotly.express as px
import datetime as dt
from io import BytesIO




# === CONFIG VISUAL === #
PRIMARY_COLOR = "#2F80ED"
SECONDARY_COLOR = "#BBDEFB"
ACCENT_COLOR = "#27AE60"
BACKGROUND_COLOR = "#FAFAFA"
TEXT_COLOR = "#212121"
CARD_COLOR = "#FFFFFF"

st.set_page_config(page_title="Comunity Finance", layout="wide")

st.markdown(f"""
    <style>
        body {{ background-color: {BACKGROUND_COLOR}; color: {TEXT_COLOR}; }}
        .main .block-container {{ padding-top: 2rem; }}
    </style>
""", unsafe_allow_html=True)

# === FUNÇÃO TEMPLATE === #
def generate_template():
    data = {
        "Data": [dt.date.today()],
        "Valor": [1500.00],
        "Tipo": ["Receita"],
        "Categoria": ["Serviços"],
        "Descrição": ["Venda de produto"],
        "Conta": ["Corrente"],
        "Forma de Pagamento": ["Pix"]
    }
    return pd.DataFrame(data)


# === FUNÇÃO: DETECÇÃO DE COLUNAS === #
def detectar_colunas(df):
    return {
        "Data": next((c for c in df.columns if "data" in c.lower()), None),
        "Valor": next((c for c in df.columns if "valor" in c.lower() or "total" in c.lower()), None),
        "Tipo": next((c for c in df.columns if "tipo" in c.lower()), None),
        "Categoria": next((c for c in df.columns if "categ" in c.lower()), None),
        "Descrição": next((c for c in df.columns if "descri" in c.lower()), None)
    }

# === SEÇÃO PRINCIPAL === #
st.title("💸 Comunity Finance")

uploaded_file = st.file_uploader("📁 Faça o upload do seu Excel financeiro", type=[".xlsx"])
if uploaded_file:
    df = pd.read_excel(uploaded_file)
    colunas = detectar_colunas(df)
    df[colunas["Data"]] = pd.to_datetime(df[colunas["Data"]])
    st.success("✔️ Arquivo carregado com sucesso! Colunas detectadas:")
    st.json(colunas)

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Visão Geral",
        "📈 Análises Temporais",
        "📉 Despesas",
        "📋 Detalhamento",
        "📥 Template"
    ])

    with tab1:
        st.header("📊 Visão Geral")
        receita = df[df[colunas['Tipo']] == "Receita"][colunas['Valor']].sum()
        despesa = df[df[colunas['Tipo']] == "Despesa"][colunas['Valor']].sum()
        saldo = receita - despesa

        col1, col2, col3 = st.columns(3)
        col1.metric("Receita Total", f"R$ {receita:,.2f}")
        col2.metric("Despesa Total", f"R$ {despesa:,.2f}")
        col3.metric("Saldo", f"R$ {saldo:,.2f}")

        fig_linha = px.line(df, x=colunas['Data'], y=colunas['Valor'], color=colunas['Tipo'],
                            title="Evolução Financeira", markers=True)
        st.plotly_chart(fig_linha, use_container_width=True)

    with tab2:
        st.header("📈 Análise Temporal")
        df['AnoMes'] = df[colunas['Data']].dt.to_period('M').astype(str)
        resumo = df.groupby(['AnoMes', colunas['Tipo']])[colunas['Valor']].sum().reset_index()
        fig_bar = px.bar(resumo, x='AnoMes', y=colunas['Valor'], color=colunas['Tipo'],
                         title="Receitas vs Despesas por Mês", barmode='group')
        st.plotly_chart(fig_bar, use_container_width=True)

    with tab3:
        st.header("📉 Despesas por Categoria")
        despesas = df[df[colunas['Tipo']] == "Despesa"]
        resumo_cat = despesas.groupby(colunas['Categoria'])[colunas['Valor']].sum().reset_index()
        fig_pie = px.pie(resumo_cat, names=colunas['Categoria'], values=colunas['Valor'],
                         title="Distribuição de Despesas")
        st.plotly_chart(fig_pie, use_container_width=True)

    with tab4:
        st.header("📋 Detalhamento de Transações")
        with st.expander("🔍 Filtros"):
            tipo_select = st.multiselect("Tipo:", options=df[colunas['Tipo']].unique(), default=df[colunas['Tipo']].unique())
            categoria_select = st.multiselect("Categoria:", options=df[colunas['Categoria']].unique(), default=df[colunas['Categoria']].unique())

        filtrado = df[
            (df[colunas['Tipo']].isin(tipo_select)) &
            (df[colunas['Categoria']].isin(categoria_select))
        ]
        st.dataframe(filtrado)
        st.info(f"Total Filtrado: R$ {filtrado[colunas['Valor']].sum():,.2f}")

    with tab5:
        st.header("📥 Baixar Template")
        template = generate_template()
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            template.to_excel(writer, index=False)
        st.download_button("Download do Template", data=output.getvalue(), file_name="template_financeiro.xlsx")

else:
    st.info("📝 Nenhum arquivo carregado ainda. Você também pode começar baixando um template.")
    with st.expander("ℹ️ Instruções para o arquivo de dados", expanded=True):
        st.markdown("""
    # Nosso objetivo 
    > é ajudar você a organizar suas finanças de forma simples e prática!
    >
    > Este é um projeto voltado para a comunidade,  
    >
    >promovendo o acesso e educação financeira para todos! 
    
    > O objetivo é simplificar o controle financeiro, 
    #### Através da Analise de dados simplificada,
                    


    Nenhum arquivo carregado ainda. Você também pode começar baixando um template.
    Para garantir a leitura correta da planilha, siga este formato:
    
    - **Data**: Campo obrigatório com datas no formato `dd/mm/aaaa` ou `aaaa-mm-dd`
    - **Valor**: Valor numérico (positivo para receita, negativo ou separado como despesa)
    - **Tipo**: 'Receita' ou 'Despesa'
    - **Categoria**: Categoria do lançamento (ex: Alimentação, Transporte, Serviços etc.)
    - **Descrição**: Breve descrição da transação
    - **Conta**: Nome da conta ou banco utilizado (opcional)
    - **Forma de Pagamento**: Cartão, Pix, Dinheiro etc. (opcional)

    ⚠️ Certifique-se que os nomes das colunas estejam claros ou próximos ao esperado. O sistema tentará detectar automaticamente, mas você poderá editar no futuro.
    
    👉 Use o botão abaixo para baixar um modelo base.
    """, unsafe_allow_html=True)
    if st.button("📥 Baixar Template"):
        template = generate_template()
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            template.to_excel(writer, index=False)
        st.download_button("Download do Template", data=output.getvalue(), file_name="template_financeiro.xlsx")
        