import pandas as pd
from pathlib import Path

# Configuração de caminhos (Windows Friendly)
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"

def clean_string(text):
    return str(text).strip().lower() if pd.notna(text) else ""

def run_transformation():
    print("--- Iniciando Transformação (Camada Silver) ---")
    
    file_lastfm = DATA_DIR / "raw_lastfm_djs.csv"
    file_billboard = DATA_DIR / "raw_billboard.csv"

    if not file_lastfm.exists():
        print(f"❌ Erro: Arquivo {file_lastfm} não encontrado!")
        return

    # 1. Leitura
    df_lfm = pd.read_csv(file_lastfm, encoding='utf-8-sig')
    
    # 2. Garantir que colunas críticas existam para o Streamlit não quebrar
    # Se a API não mandou, nós criamos com 0
    for col in ['playcount', 'listeners', 'name']:
        if col not in df_lfm.columns:
            df_lfm[col] = 0 if col != 'name' else "Unknown"
            print(f"⚠️ Coluna '{col}' estava faltando e foi criada com valor padrão.")

    # 3. Limpeza de tipos
    df_lfm['playcount'] = pd.to_numeric(df_lfm['playcount'], errors='coerce').fillna(0)
    df_lfm['listeners'] = pd.to_numeric(df_lfm['listeners'], errors='coerce').fillna(0)
    df_lfm['name_clean'] = df_lfm['name'].apply(clean_string)

    # 4. Processar Billboard se o arquivo existir
    if file_billboard.exists():
        df_bb = pd.read_csv(file_billboard, encoding='utf-8-sig')
        df_bb['artist_clean'] = df_bb['artist'].apply(clean_string)
        bb_counts = df_bb.groupby('artist_clean').size().reset_index(name='billboard_appearances')
        
        # Merge
        df_final = pd.merge(df_lfm, bb_counts, left_on='name_clean', right_on='artist_clean', how='left').fillna(0)
    else:
        df_final = df_lfm.copy()
        df_final['billboard_appearances'] = 0
        print("⚠️ Arquivo Billboard não encontrado. Seguindo apenas com Last.fm.")

    # 5. Criar colunas finais
    df_final['is_legend'] = df_final['billboard_appearances'] >= 3

    # Salvar resultado final
    output_path = DATA_DIR / "silver_dj_insights.csv"
    df_final.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f"✅ Sucesso! Arquivo '{output_path.name}' gerado com {len(df_final)} linhas.")

if __name__ == "__main__":
    run_transformation()