import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO
import datetime as dt

# Configuração da página
st.set_page_config(
    page_title="Comunity Finance",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado
st.markdown("""
<style>
    .main {
        background-color: #F8F9FA;
    }
    .metric-card {
        background-color: white;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    .header {
        color: #2C3E50;
        border-bottom: 3px solid #3498DB;
        padding-bottom: 10px;
        margin-bottom: 30px;
    }
    .stPlotlyChart {
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# Funções de processamento (moved outside the if/else block)
def generate_template():
    data = {'Coluna1': [1, 2], 'Coluna2': ['A', 'B']}
    buffer = BytesIO()
    df = pd.DataFrame(data)
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='Sheet1', index=False)
    return buffer.getvalue()

def process_data(df, date_col, value_col, type_col, category_col, desc_col):
    df_processed = df.copy()
    df_processed['Data'] = pd.to_datetime(df_processed[date_col])
    df_processed = df_processed.rename(columns={
        value_col: 'Valor',
        type_col: 'Tipo',
        category_col: 'Categoria',
        desc_col: 'Descrição'
    })
    return df_processed

def create_safe_chart(fig_func, *args, **kwargs):
    try:
        fig = fig_func(*args, **kwargs)
        return fig
    except Exception as e:
        st.error(f"Erro ao criar o gráfico: {e}")
        return None

# Interface principal
st.title("Comunity Finance ")
st.markdown("### Sua visão financeira ")

# Sidebar modernizada
with st.sidebar:
    st.markdown("## ⚙️ Controle")
    uploaded_file = st.file_uploader("Carregar dados financeiros", type=["xlsx"])

    if uploaded_file:
        try:
            df_preview = pd.read_excel(uploaded_file, nrows=5)
            cols = df_preview.columns.tolist()

            with st.expander("🔍 Mapeamento de Colunas", expanded=True):
                date_col = st.selectbox("Data", cols, index=0)
                value_col = st.selectbox("Valor Monetário", cols)
                type_col = st.selectbox("Tipo de Transação", cols)
                category_col = st.selectbox("Categoria", cols)
                desc_col = st.selectbox("Descrição", cols)

            with st.expander("⏳ Controle Temporal"):
                min_date = pd.to_datetime(df_preview[date_col]).min().date()
                max_date = pd.to_datetime(df_preview[date_col]).max().date()
                date_range = st.date_input("Selecione o período",
                                            value=(min_date, max_date),
                                            min_value=min_date,
                                            max_value=max_date)
        except Exception as e:
            st.error("Erro na leitura do arquivo")
    else:
        st.markdown("### 📁 Primeiros Passos")
        st.download_button(
            label="Baixar Modelo",
            data=generate_template(),
            file_name="modelo_finflow_pro.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        st.markdown("""
        ### 📌 Dicas:
        - Mantenha datas consistentes
        - Use categorias específicas
        - Revise valores antes de importar
        """)

# Conteúdo principal
if not uploaded_file:
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("""
       
        # Community Finance
        ### Recursos:
        ✅ Análise preditiva de fluxo de caixa \n
        ✅ Detecção automática de padrões \n
        ✅ Relatórios personalizáveis\n
        ✅ Integração multicontas\n
        ✅ Alertas inteligentes\n

        ### Como Começar:
        1. Baixe nosso modelo de planilha
        2. Preencha com seus dados financeiros
        3. Faça upload usando o menu lateral
        """)
    with col2:
        st.image("https://cdn-icons-png.flaticon.com/512/3144/3144456.png", width=400)

else:
    df = process_data(pd.read_excel(uploaded_file), date_col, value_col,
                        type_col, category_col, desc_col)

    if df is not None:
        df_filtered = df[(df['Data'].dt.date >= date_range[0]) &
                            (df['Data'].dt.date <= date_range[1])]

        if df_filtered.empty:
            st.warning("⚠️ Nenhuma transação encontrada no período selecionado")
            st.stop()

        # Seção de métricas
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("📈 Receita Total", f"R${df_filtered[df_filtered['Tipo'] == 'Receita']['Valor'].sum():,.2f}")
            st.markdown('</div>', unsafe_allow_html=True)

        with col2:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("📉 Despesa Total", f"R${df_filtered[df_filtered['Tipo'] == 'Despesa']['Valor'].sum():,.2f}")
            st.markdown('</div>', unsafe_allow_html=True)

        with col3:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            saldo = df_filtered['Valor'].sum()
            st.metric("💹 Saldo Financeiro", f"R${saldo:,.2f}",
                        delta=f"{saldo/df_filtered[df_filtered['Tipo'] == 'Receita']['Valor'].sum()*100:.1f}%" if saldo > 0 else None)
            st.markdown('</div>', unsafe_allow_html=True)

        # Análises principais
        tab1, tab2, tab3 = st.tabs(["📅 Análise Temporal", "📊 Composição Financeira", "🔍 Detalhamento"])

        with tab1:
            st.markdown("### Tendências Temporais")
            c1, c2 = st.columns([3, 1])
            with c1:
                freq = st.selectbox("Frequência", ["Diária", "Semanal", "Mensal"], index=2)
                freq_map = {"Diária": "D", "Semanal": "W", "Mensal": "M"}
                df_temp = df_filtered.groupby(pd.Grouper(key='Data', freq=freq_map[freq]))['Valor'].sum().reset_index()
                fig = create_safe_chart(px.area, df_temp, x='Data', y='Valor',
                                            title=f"Evolução {freq.lower()} do Fluxo")
                st.plotly_chart(fig, use_container_width=True)

            with c2:
                st.markdown("#### 📌 Insights")
                ultimo_mes = df_temp.iloc[-1]['Valor']
                penultimo_mes = df_temp.iloc[-2]['Valor'] if len(df_temp) > 1 else 0
                variacao = ((ultimo_mes - penultimo_mes)/penultimo_mes*100) if penultimo_mes != 0 else 0
                st.metric(f"Variação {freq.lower()}", f"{variacao:.1f}%")
                st.write("---")
                st.write("**Top Categorias**")
                st.dataframe(df_filtered.groupby('Categoria')['Valor'].sum().nlargest(3),
                             hide_index=True, use_container_width=True)

        with tab2:
            st.markdown("### Composição Financeira")
            col4, col5 = st.columns(2)

            with col4:
                fig = create_safe_chart(px.sunburst, df_filtered,
                                            path=['Tipo', 'Categoria'],
                                            values='Valor',
                                            color='Tipo',
                                            title="Distribuição Hierárquica")
                st.plotly_chart(fig, use_container_width=True)

            with col5:
                categoria = st.selectbox("Selecionar Categoria", df_filtered['Categoria'].unique())
                df_cat = df_filtered[df_filtered['Categoria'] == categoria]

                fig = create_safe_chart(px.bar, df_cat,
                                            x='Data', y='Valor',
                                            color='Tipo',
                                            title=f"Detalhes da Categoria: {categoria}")
                st.plotly_chart(fig, use_container_width=True)

        with tab3:
            st.markdown("### Detalhamento de Transações")
            with st.expander("🔎 Filtros Avançados"):
                col6, col7, col8 = st.columns(3)
                with col6:
                    categorias = st.multiselect("Categorias", df_filtered['Categoria'].unique())
                with col7:
                    tipos = st.multiselect("Tipos", df_filtered['Tipo'].unique(), default=df_filtered['Tipo'].unique())
                with col8:
                    valor_min, valor_max = st.slider("Faixa de Valores",
                                                        float(df_filtered['Valor'].min()),
                                                        float(df_filtered['Valor'].max()),
                                                        (float(df_filtered['Valor'].min()),
                                                         float(df_filtered['Valor'].max())))

            df_filtered_tab3 = df_filtered[
                (df_filtered['Categoria'].isin(categorias) if categorias else True) &
                (df_filtered['Tipo'].isin(tipos)) &
                (df_filtered['Valor'] >= valor_min) &
                (df_filtered['Valor'] <= valor_max)
            ]

            st.dataframe(
                df_filtered_tab3.sort_values('Data', ascending=False),
                column_config={
                    "Data": st.column_config.DateColumn(format="DD/MM/YYYY"),
                    "Valor": st.column_config.NumberColumn(
                        format="R$ %.2f",
                        help="Valor da transação"
                    )
                },
                hide_index=True,
                use_container_width=True,
                height=400
            )

# Rodapé
st.markdown("---")
st.markdown("FinFlow Pro © 2025 | Sistema de Comunitario de Gestão Financeira")