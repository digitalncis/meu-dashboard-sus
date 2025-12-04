import streamlit as st
import pandas as pd
import unicodedata

# --- CONFIGURAÇÃO DA PÁGINA (WIDE) ---
st.set_page_config(
    page_title="Cadastro SUS",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CSS PERSONALIZADO (ESTILO) ---
st.markdown("""
    <style>
    /* Fundo do cabeçalho */
    .main-header {
        background-color: #0068c9;
        padding: 20px;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 20px;
    }
    .main-header h1 {
        color: white;
        font-family: 'Arial', sans-serif;
    }
    
    /* Cards de métricas */
    div[data-testid="stMetric"] {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #d6d6d6;
    }
    
    /* Botão de Download mais bonito */
    .stDownloadButton button {
        background-color: #28a745;
        color: white;
        border-radius: 8px;
        font-weight: bold;
        width: 100%;
    }
    .stDownloadButton button:hover {
        background-color: #218838;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

# --- FUNÇÕES DE LÓGICA (MANTIDAS) ---
def normalizar_texto(texto):
    if not isinstance(texto, str): return str(texto)
    return unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode('utf-8').upper()

def classificar_unidade(nome):
    nome = nome.upper()
    if 'UPA' in nome: return '🚨 UPA'
    if 'HOSP' in nome or 'SANTA CASA' in nome: return '🏥 HOSPITAL'
    if 'UMS' in nome: return '🩺 UMS'
    if 'UBS' in nome: return '💉 UBS'
    if 'ESF' in nome: return '👩‍⚕️ ESF'
    if 'CENTRO' in nome: return '🏢 CENTRO DE SAUDE'
    return '📍 OUTROS'

# --- TÍTULO COM VISUAL NOVO ---
st.markdown('<div class="main-header"><h1>🏥 Cadastro Nacional de Unidades (SIA/SUS)</h1><p>Visualização e Exportação de Unidades Cadastradas</p></div>', unsafe_allow_html=True)

# --- BARRA LATERAL ---
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/6/68/SUS_Logo.svg/1200px-SUS_Logo.svg.png", width=100)
    st.header("📂 Área de Dados")
    arquivo = st.file_uploader("Solte o arquivo 'espelhoUnidades.csv' aqui", type="csv")
    st.info("💡 Dica: Use o menu de filtros ao lado após carregar os dados para refinar sua busca.")

# --- CORPO PRINCIPAL ---
if arquivo:
    try:
        # Leitura Inteligente
        try:
            df = pd.read_csv(arquivo, sep=',', encoding='latin1', dtype=str)
        except:
            df = pd.read_csv(arquivo, sep=';', encoding='latin1', dtype=str)
        
        # Normalização
        cols_norm = [normalizar_texto(c) for c in df.columns]
        df.columns = cols_norm
        
        col_cnes = next((c for c in df.columns if 'NUM_CNES' in c), df.columns[11] if len(df.columns) > 11 else None)
        col_nome = next((c for c in df.columns if 'NOME' in c), df.columns[12] if len(df.columns) > 12 else None)

        if col_cnes and col_nome:
            df_unidades = df[[col_cnes, col_nome]].drop_duplicates().copy()
            df_unidades.columns = ['CNES', 'Nome da Unidade']
            df_unidades['CNES'] = df_unidades['CNES'].str.strip().str.zfill(7)
            df_unidades['Nome da Unidade'] = df_unidades['Nome da Unidade'].str.strip().str.upper()
            
            # Classificação com Ícones
            df_unidades['Categoria'] = df_unidades['Nome da Unidade'].apply(classificar_unidade)
            df_unidades = df_unidades.sort_values(['Categoria', 'Nome da Unidade'])
            
            # --- DASHBOARD VISUAL ---
            
            # 1. Métricas no topo
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total de Unidades", len(df_unidades))
            with col2:
                top_cat = df_unidades['Categoria'].mode()[0]
                st.metric("Categoria Principal", top_cat)
            with col3:
                hospitais = len(df_unidades[df_unidades['Categoria'] == '🏥 HOSPITAL'])
                st.metric("Total de Hospitais", hospitais)
            
            st.divider()

            # 2. Área de Filtros e Tabela
            col_filtros, col_tabela = st.columns([1, 3])
            
            with col_filtros:
                st.subheader("🔍 Filtros")
                with st.container(border=True):
                    filtro_tipo = st.multiselect("Selecione o Tipo:", df_unidades['Categoria'].unique())
                    
                    search = st.text_input("Buscar por nome:", placeholder="Ex: GUAMA")
            
            # Aplicar filtros
            df_view = df_unidades.copy()
            if filtro_tipo:
                df_view = df_view[df_view['Categoria'].isin(filtro_tipo)]
            if search:
                df_view = df_view[df_view['Nome da Unidade'].str.contains(search.upper())]

            with col_tabela:
                st.subheader(f"📋 Lista de Unidades ({len(df_view)})")
                
                # Tabela Interativa (Data Editor) - Muito mais bonita que dataframe normal
                st.data_editor(
                    df_view,
                    column_config={
                        "CNES": st.column_config.TextColumn("Código CNES", help="Código nacional do estabelecimento", width="small"),
                        "Nome da Unidade": st.column_config.TextColumn("Nome do Estabelecimento", width="large"),
                        "Categoria": st.column_config.TextColumn("Tipo", width="medium"),
                    },
                    hide_index=True,
                    use_container_width=True,
                    disabled=True # Apenas leitura
                )

            # 3. Botão de Download em destaque
            st.divider()
            col_d1, col_d2, col_d3 = st.columns([1, 2, 1])
            with col_d2:
                csv = df_view.to_csv(index=False, sep=';', encoding='utf-8-sig')
                st.download_button(
                    label="📥 BAIXAR LISTA FILTRADA AGORA",
                    data=csv,
                    file_name="lista_unidades_sus_v2.csv",
                    mime="text/csv",
                    use_container_width=True
                )

        else:
            st.error("Não foi possível identificar as colunas CNES e NOME no arquivo.")
            
    except Exception as e:
        st.error(f"Erro ao ler o arquivo: {e}")

else:
    # Tela de boas-vindas vazia
    st.markdown("""
    <div style="text-align: center; padding: 50px; color: #666;">
        <h2>Aguardando arquivo...</h2>
        <p>Faça o upload do arquivo <b>espelhoUnidades.csv</b> na barra lateral para começar.</p>
    </div>
    """, unsafe_allow_html=True)