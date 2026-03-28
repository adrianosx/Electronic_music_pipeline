import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# 1. Configuração da Página
st.set_page_config(
    page_title="EDM Data Explorer", 
    page_icon="🎧", 
    layout="wide"
)

# 2. Caminhos dos Arquivos (Compatível com Windows)
BASE_DIR = Path(__file__).parent
DATA_PATH = BASE_DIR / "data" / "silver_dj_insights.csv"
BILLBOARD_PATH = BASE_DIR / "data" / "raw_billboard.csv"
MARKET_PATH = BASE_DIR / "data" / "market_data.csv"

# 3. Função para carregar dados
@st.cache_data
def load_data():
    # Carrega dados principais
    df = pd.read_csv(DATA_PATH) if DATA_PATH.exists() else pd.DataFrame()
    # Carrega Billboard
    df_bb = pd.read_csv(BILLBOARD_PATH) if BILLBOARD_PATH.exists() else pd.DataFrame()
    # Carrega Mercado (Cachês)
    df_mkt = pd.read_csv(MARKET_PATH) if MARKET_PATH.exists() else pd.DataFrame()
    return df, df_bb, df_mkt

# --- TÍTULO E INTRODUÇÃO ---
st.title("🎧 Electronic Music Industry - Data Pipeline")
st.markdown("""
Este dashboard apresenta uma visão 360º da cena eletrônica, cruzando popularidade atual (Last.fm), 
histórico de hits (Billboard 2000-2026) e dados de mercado.
""")

try:
    df_djs, df_bb, df_mkt = load_data()

    if df_djs.empty:
        st.error("❌ O arquivo 'silver_dj_insights.csv' não foi encontrado. Rode o 'transform.py' primeiro!")
    else:
        # --- SIDEBAR (FILTROS) ---
        st.sidebar.header("⚙️ Filtros de Análise")
        
        # Ajuste: Começando em 0 para mostrar todos os dados por padrão
       # --- SIDEBAR (FILTROS) ---
        st.sidebar.header("⚙️ Filtros de Análise")
        
        # Pegamos o min e max reais da coluna
        v_min = int(df_djs['listeners'].min())
        v_max = int(df_djs['listeners'].max())

        # Se os dados estiverem zerados, criamos um slider padrão para não dar erro
        if v_min == v_max:
            st.sidebar.warning("⚠️ Dados de ouvintes não disponíveis (todos estão 0).")
            min_listeners = 0
        else:
            min_listeners = st.sidebar.slider(
                "Filtrar por Ouvintes Mínimos (Last.fm)", 
                v_min, 
                v_max, 
                v_min # Começa no valor mínimo encontrado
            )
        
        df_filtered = df_djs[df_djs['listeners'] >= min_listeners]

        # --- MÉTRICAS DE TOPO ---
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("DJs no Dataset", len(df_djs))
        m2.metric("DJs Filtrados", len(df_filtered))
        m3.metric("Lendas Billboard", len(df_djs[df_djs['billboard_appearances'] > 0]))
        m4.metric("Top Listeners", f"{int(df_djs['listeners'].max()):,}")

        st.divider()

        # --- ORGANIZAÇÃO EM ABAS ---
        tab1, tab2, tab3, tab4 = st.tabs([
            "📊 Popularidade Atual", 
            "📈 Histórico Billboard", 
            "💰 Mercado & Prêmios", 
            "📋 Dados Brutos"
        ])

        with tab1:
            st.subheader("Popularidade no Last.fm vs. Presença na Billboard")
            fig_scatter = px.scatter(
                df_filtered, 
                x="listeners", 
                y="playcount", 
                size="billboard_appearances", 
                color="name",
                hover_name="name", 
                log_x=True,
                title="Tamanho da bolha = Vezes no Top 10 Billboard (2000-2026)",
                labels={"listeners": "Ouvintes Únicos", "playcount": "Total de Reproduções"}
            )
            st.plotly_chart(fig_scatter, use_container_width=True)

        with tab2:
            st.subheader("DJs que dominaram os charts da Billboard por Ano")
            if not df_bb.empty:
                fig_bb = px.bar(
                    df_bb, 
                    x="year", 
                    color="artist", 
                    title="Hits no Top 10 Dance/Electronic Songs",
                    labels={"year": "Ano", "count": "Quantidade de Tracks"}
                )
                st.plotly_chart(fig_bb, use_container_width=True)
            else:
                st.warning("Dados da Billboard não encontrados.")

        with tab3:
            st.subheader("Cachês e Premiações (Dados de Mercado)")
            if not df_mkt.empty:
                c1, c2 = st.columns(2)
                with c1:
                    fig_cache = px.bar(
                        df_mkt, x="dj_name", y="average_cache", 
                        title="Cachê Estimado por Show (USD)",
                        color="average_cache",
                        labels={"average_cache": "Cachê ($)", "dj_name": "DJ"}
                    )
                    st.plotly_chart(fig_cache, use_container_width=True)
                with c2:
                    fig_awards = px.pie(
                        df_mkt, values="awards_count", names="dj_name", 
                        title="Distribuição de Prêmios (DJ Mag / Grammys)",
                        hole=0.4
                    )
                    st.plotly_chart(fig_awards, use_container_width=True)
            else:
                st.info("Dica: Crie o arquivo 'market_data.csv' na pasta 'data' para ver estes gráficos.")

        with tab4:
            st.subheader("Exploração da Camada Silver")
            st.dataframe(
                df_filtered.sort_values(by="listeners", ascending=False), 
                use_container_width=True
            )

except Exception as e:
    st.error(f"Ocorreu um erro ao carregar o dashboard: {e}")

# Rodapé lateral
st.sidebar.markdown("---")
st.sidebar.caption("🚀 Desenvolvido como projeto de Portfólio para Data Engineering.")