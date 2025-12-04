import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import unicodedata

# --- CONFIGURAÇÃO DA PÁGINA (WIDE & INITIAL SIDEBAR) ---
st.set_page_config(
    page_title="Gestão SUS | Executive Dashboard",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- ESTILO CSS AVANÇADO (MODERNO & CLEAN) ---
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* Fundo Principal */
    .stApp {
        background-color: #f4f7f6;
    }

    /* Container do Cabeçalho */
    .header-container {
        background: linear-gradient(90deg, #2c3e50 0%, #3498db 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        text-align: center;
    }
    .header-container h1 {
        font-weight: 600;
        margin: 0;
        font-size: 2.5rem;
        color: white !important;
    }
    .header-container p {
        font-weight: 300;
        font-size: 1.1rem;
        opacity: 0.9;
        margin-top: 5px;
    }

    /* Cards de Métricas (KPIs) - Uniformização */
    div[data-testid="stMetric"] {
        background-color: white;
        padding: 20px;
        border-radius: 12px;
        border: none;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        transition: transform 0.2s ease;
        height: 160px; /* Altura Fixa Maior para garantir alinhamento */
        display: flex;
        flex-direction: column;
        justify-content: space-between; /* Espalha o conteúdo */
    }
    div[data-testid="stMetric"]:hover {
        transform: translateY(-3px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    div[data-testid="stMetric"] label {
        font-size: 1rem;
        font-weight: 600;
        color: #7f8c8d;
    }
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
        font-size: 1.8rem;
        font-weight: 700;
        color: #2c3e50;
    }
    
    /* Cores das bordas superiores dos KPIs (ajustado para melhor semântica) */
    div[data-testid="column"]:nth-child(1) div[data-testid="stMetric"] { border-top: 5px solid #3498db; } /* Teto (Azul) */
    div[data-testid="column"]:nth-child(2) div[data-testid="stMetric"] { border-top: 5px solid #9b59b6; } /* Produção (Roxo) */
    div[data-testid="column"]:nth-child(3) div[data-testid="stMetric"] { border-top: 5px solid #e74c3c; } /* Saldo (Vermelho) */
    div[data-testid="column"]:nth-child(4) div[data-testid="stMetric"] { border-top: 5px solid #2ecc71; } /* Execução (Verde) */

    /* Abas */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        border-bottom: 1px solid #e0e0e0;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        background-color: white;
        border-radius: 8px 8px 0px 0px;
        padding: 0 20px;
        border: 1px solid transparent;
        font-weight: 600;
        transition: all 0.2s ease;
    }
    .stTabs [aria-selected="true"] {
        background-color: white;
        border-bottom: 3px solid #3498db;
        color: #3498db !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e0e0e0;
        padding-top: 2rem;
    }
    section[data-testid="stSidebar"] h3 {
        color: #2c3e50;
        font-size: 1.2rem;
        margin-top: 1.5rem;
    }
    
    /* Ajuste para que a coluna de barra de progresso em HTML fique melhor */
    div[data-testid="stHorizontalBlock"] > div:nth-child(5) {
        width: 100% !important;
        min-width: 150px; /* Ajuste para ter espaço para a barra */
    }
    .stMarkdown table {
        width: 100% !important;
        table-layout: fixed; /* Ajuda a distribuir colunas */
    }
    .stMarkdown td, .stMarkdown th {
        word-wrap: break-word; /* Previne estouro de texto */
        white-space: normal;
    }

</style>
""", unsafe_allow_html=True)

# --- FUNÇÃO DE CORES CONDICIONAIS PARA PROGRESS BAR ---
def get_color_hex(execucao_perc):
    """Retorna o código HEX da cor com base na porcentagem."""
    if execucao_perc >= 80:
        return '#2ecc71'  # Verde
    elif execucao_perc >= 50:
        return '#f39c12'  # Laranja
    else: 
        return '#e74c3c'  # Vermelho

def style_progress_bar_html(val):
    """Gera o HTML para a barra de progresso colorida."""
    
    # 1. O preenchimento visual é limitado a 100%
    val_clamped_visual = max(0, min(100, val)) 
    
    # 2. A cor é baseada no valor real
    color = get_color_hex(val)
    
    return f"""
    <div style="background-color: #f0f2f6; border-radius: 4px; overflow: hidden; height: 1.5rem; width: 100%;">
        <div style="
            background-color: {color}; 
            width: {val_clamped_visual}%; /* LIMITA VISUALMENTE A 100% */
            height: 100%; 
            display: flex;
            align-items: center;
            justify-content: center;
            color: white; 
            font-weight: 600;
        ">
        {val:.1f}% </div>
    </div>
    """

# --- FUNÇÕES DE LÓGICA (Não alteradas) ---
def normalizar_texto(texto):
    if not isinstance(texto, str): return str(texto)
    return unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode('utf-8').upper()

def apenas_digitos(texto):
    return ''.join(filter(str.isdigit, str(texto)))

def classificar_unidade(nome):
    nome = normalizar_texto(nome)
    if 'UPA' in nome: return '🚨 UPA'
    if 'HOSP' in nome or 'SANTA CASA' in nome: return '🏥 HOSPITAL'
    if 'UMS' in nome: return '🩺 UMS'
    if 'UBS' in nome: return '💉 UBS'
    if 'ESF' in nome: return '👩‍⚕️ ESF'
    if 'CENTRO' in nome: return '🏢 CENTRO'
    return '📍 OUTROS'

def identificar_mes_por_arquivo(nome_arquivo):
    nome_limpo = str(nome_arquivo).lower().replace('.csv', '').strip()
    if not nome_limpo: return "Desconhecido"
    ultimo_digito = nome_limpo[-1]
    mapa_meses = {
        '1': 'Janeiro', '2': 'Fevereiro', '3': 'Março', '4': 'Abril',
        '5': 'Maio', '6': 'Junho', '7': 'Julho', '8': 'Agosto',
        '9': 'Setembro', '0': 'Outubro', 'o': 'Outubro', 'n': 'Novembro', 'd': 'Dezembro'
    }
    return mapa_meses.get(ultimo_digito, f"Arquivo Final {ultimo_digito}")

def encontrar_coluna_valor(df_columns):
    cols_norm = [normalizar_texto(c) for c in df_columns]
    for i, col_norm in enumerate(cols_norm):
        # Procura genérica por coluna de orçamento/valor total
        if 'TOTAL' in col_norm and 'ORC' in col_norm: return df_columns[i]
        if 'ORCAMENT' in col_norm: return df_columns[i]
        if 'VLR TOTAL' in col_norm: return df_columns[i]
    # Fallback pela posição (colunas 8 ou 9 costumam ser valores no espelho padrão)
    if len(df_columns) > 8: return df_columns[8]
    return None

def extrair_dicionario_procedimentos(df, origem="Desconhecida"):
    dict_encontrado = {}
    headers_norm = [normalizar_texto(c) for c in df.columns]
    idx_cod, idx_desc = -1, -1
    
    for i, h in enumerate(headers_norm):
        if 'PROC_ID' in h or 'PROCEDIM' in h or ('COD' in h and 'PROC' in h): idx_cod = i; break
    for i, h in enumerate(headers_norm):
        if 'DESCR' in h or ('NOME' in h and 'PROC' in h) or 'DS_PROC' in h: idx_desc = i; break
            
    if idx_cod != -1 and idx_desc != -1:
        col_cod, col_desc = df.columns[idx_cod], df.columns[idx_desc]
        try:
            temp = df[[col_cod, col_desc]].dropna().drop_duplicates()
            for k, v in zip(temp[col_cod], temp[col_desc]):
                k_clean = apenas_digitos(str(k))
                if k_clean and isinstance(v, str):
                    v_limpo = v.strip().upper()
                    dict_encontrado[k_clean] = v_limpo
                    try: dict_encontrado[str(int(k_clean))] = v_limpo
                    except: pass
                    try: dict_encontrado[k_clean.zfill(10)] = v_limpo
                    except: pass
        except: pass
    return dict_encontrado

# Função para formatar moeda no padrão BR (ajustada para garantir o padrão)
def formatar_brl(valor):
    if pd.isna(valor): return "R$ 0,00"
    try:
        # Formatação com ponto como milhar e vírgula como decimal
        return "R$ {:,.2f}".format(valor).replace(",", "X").replace(".", ",").replace("X", ".")
    except ValueError:
        return "R$ 0,00"

@st.cache_data
def load_data_raw(files_papa, files_espelho):
    df_papa = pd.DataFrame()
    if files_papa:
        papa_dfs = []
        for file in files_papa:
            try: 
                file.seek(0); df_temp = pd.read_csv(file, sep=',', encoding='latin1', dtype=str)
            except: 
                file.seek(0); df_temp = pd.read_csv(file, sep=';', encoding='latin1', dtype=str)
            df_temp['MES_NOME'] = identificar_mes_por_arquivo(file.name)
            papa_dfs.append(df_temp)
        
        if papa_dfs:
            df_papa = pd.concat(papa_dfs, ignore_index=True)
            if 'PA_NAT_JUR' in df_papa.columns:
                df_papa['PA_NAT_JUR'] = df_papa['PA_NAT_JUR'].astype(str).str.strip()
                df_papa = df_papa[df_papa['PA_NAT_JUR'] == '1031']
            
            col_val = next((c for c in df_papa.columns if 'VALAPR' in c), 'PA_VALAPR')
            df_papa[col_val] = df_papa[col_val].astype(str).str.replace('.', '', regex=False).str.replace(',', '.', regex=False).fillna('0').astype(float)
            
            col_cnes = next((c for c in df_papa.columns if 'CODUNI' in c), 'PA_CODUNI')
            df_papa['CNES_KEY'] = df_papa[col_cnes].astype(str).str.strip().str.replace('"', '').str.zfill(7)

    df_espelho = pd.DataFrame()
    teto_agrupado = pd.DataFrame()
    if files_espelho:
        espelho_dfs = []
        target_files = files_espelho if isinstance(files_espelho, list) else [files_espelho]
        for file in target_files:
            try: file.seek(0); df_temp = pd.read_csv(file, sep=',', encoding='latin1', dtype=str)
            except: file.seek(0); df_temp = pd.read_csv(file, sep=';', encoding='latin1', dtype=str)
            espelho_dfs.append(df_temp)
        if espelho_dfs:
            df_espelho = pd.concat(espelho_dfs, ignore_index=True)
            col_teto = encontrar_coluna_valor(df_espelho.columns)
            
            if col_teto:
                df_espelho['Valor_Teto'] = df_espelho[col_teto].astype(str).str.replace('.', '', regex=False).str.replace(',', '.', regex=False).fillna('0').astype(float)
                
                headers_esp = [normalizar_texto(c) for c in df_espelho.columns]
                idx_cnes = next((i for i, h in enumerate(headers_esp) if 'CNES' in h), 11)
                col_cnes = df_espelho.columns[idx_cnes]
                
                idx_nome = next((i for i, h in enumerate(headers_esp) if ('NOME' in h and 'ESTAB' in h) or 'UNIDADE' in h), 12)
                col_nome = df_espelho.columns[idx_nome]
                
                df_espelho['CNES_KEY'] = df_espelho[col_cnes].astype(str).str.strip().str.replace('"', '').str.zfill(7)
                teto_agrupado = df_espelho.groupby(['CNES_KEY', col_nome])['Valor_Teto'].sum().reset_index()
                teto_agrupado.rename(columns={col_nome: 'Unidade'}, inplace=True)

    dict_proc = {}
    if not df_papa.empty: dict_proc.update(extrair_dicionario_procedimentos(df_papa, "PAPA"))
    if not df_espelho.empty: dict_proc.update(extrair_dicionario_procedimentos(df_espelho, "ESPELHO"))
    
    return df_papa, teto_agrupado, dict_proc

def processar_consolidado(df_papa_filtrado, df_teto):
    if df_papa_filtrado.empty:
        final = df_teto.copy(); final['Valor_Produzido'] = 0.0
    else:
        col_val = next((c for c in df_papa_filtrado.columns if 'VALAPR' in c), 'PA_VALAPR')
        prod = df_papa_filtrado.groupby('CNES_KEY')[col_val].sum().reset_index()
        prod.rename(columns={col_val: 'Valor_Produzido'}, inplace=True)
        final = pd.merge(df_teto, prod, on='CNES_KEY', how='outer').fillna(0)
    
    final['Unidade'] = final['Unidade'].replace(0, 'Unidade Desconhecida').replace('0', 'Unidade Desconhecida').astype(str)
    final['Saldo'] = final['Valor_Teto'] - final['Valor_Produzido']
    final['% Execucao'] = final.apply(lambda x: (x['Valor_Produzido'] / x['Valor_Teto'] * 100) if x['Valor_Teto'] > 0 else 0, axis=1)
    final['Categoria'] = final['Unidade'].apply(classificar_unidade)
    return final

# --- SIDEBAR ---
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/6/68/SUS_Logo.svg/1200px-SUS_Logo.svg.png", width=140)
    st.markdown("### 📥 Central de Dados")
    files_papa = st.file_uploader("📂 Produção (PAPA) - Múltiplos", type="csv", accept_multiple_files=True)
    files_espelho = st.file_uploader("💰 Teto (Espelho) - Múltiplos", type="csv", accept_multiple_files=True)
    st.markdown("---")
    st.caption("Filtro Automático: Natureza Jurídica **1031**")
    
    filtros_data_container = st.container()
    filtros_unidade_container = st.container()

# --- MAIN LAYOUT ---
st.markdown('<div class="header-container"><h1>Gestão Estratégica SIA/SUS</h1><p>Intelligence Dashboard • Teto vs Produção • Tendências</p></div>', unsafe_allow_html=True)

if files_papa and files_espelho:
    df_papa_raw, df_teto, dict_procedimentos = load_data_raw(files_papa, files_espelho)
    num_meses_papa = len(files_papa) if files_papa else 1
    
    if not df_teto.empty:
        # --- FILTROS NA SIDEBAR ---
        ordem_meses = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
        meses_disp = list(df_papa_raw['MES_NOME'].unique()) if not df_papa_raw.empty else []
        meses_ord = sorted(meses_disp, key=lambda x: ordem_meses.index(x) if x in ordem_meses else 99)
        
        # Filtro de Período
        if meses_ord:
            with filtros_data_container:
                st.subheader("📅 Período")
                sel_meses = st.multiselect("Selecione os Meses:", meses_ord, default=meses_ord)
        else: sel_meses = []

        df_papa_final = df_papa_raw[df_papa_raw['MES_NOME'].isin(sel_meses)] if not df_papa_raw.empty else pd.DataFrame()
        df = processar_consolidado(df_papa_final, df_teto)
        
        if not df_papa_raw.empty:
            valid_cnes = df_papa_raw['CNES_KEY'].unique()
            df = df[df['CNES_KEY'].isin(valid_cnes)]
        
        # ⚠️ NOVO BLOCO DE FILTROS NA PÁGINA PRINCIPAL
        st.markdown("---")
        
        c_f1, c_f2 = st.columns([1, 3])
        cats = sorted(df['Categoria'].unique())
        
        # Filtro de Categoria na página principal (c_f1)
        sel_cat = c_f1.multiselect("🏷️ Filtrar Categoria:", cats)
        df_filtered = df[df['Categoria'].isin(sel_cat)] if sel_cat else df
        
        # Filtro de Unidade na página principal (c_f2) - Mantido aqui para seguir o layout original, apesar de ser grande
        units = sorted(df_filtered['Unidade'].unique())
        sel_unit = c_f2.multiselect("🏥 Filtrar Unidade:", units)
        df_view = df_filtered[df_filtered['Unidade'].isin(sel_unit)] if sel_unit else df_filtered

        st.markdown("---")

        # --- KPIs ---
        teto_base = df_view['Valor_Teto'].sum()
        teto_total = teto_base * num_meses_papa 
        prod = df_view['Valor_Produzido'].sum()
        saldo = teto_total - prod
        perc = (prod / teto_total * 100) if teto_total > 0 else 0
        
        # CÁLCULO: Saldo em % do Teto (Diferença Percentual)
        saldo_perc = 100 - perc
        
        # Configuração de cor do Delta para os KPIs
        saldo_delta_color = "inverse" if saldo < 0 else "normal"
        prod_delta_color = "normal" if perc >= 100 else "off"

        c1, c2, c3, c4 = st.columns(4)
        
        # KPI 1: Teto Acumulado
        c1.metric("💰 Teto Global (Acumulado)", formatar_brl(teto_total), help=f"Base Mensal: {formatar_brl(teto_base)} x {num_meses_papa} meses")
        
        # KPI 2: Produção Acumulada (com Execução % como delta)
        c2.metric("📊 Produção Realizada", formatar_brl(prod), delta=f"{perc:.1f}% de Execução", delta_color=prod_delta_color)
        
        # KPI 3: Saldo Disponível (com Diferença % como delta)
        c3.metric("📉 Saldo Disponível", formatar_brl(saldo), delta=f"{saldo_perc:.1f}% do Teto", delta_color=saldo_delta_color)
        
        # KPI 4: Execução Média (Mantido para mostrar a taxa principal)
        c4.metric("📈 Execução Média", f"{perc:.1f}%", f"{len(df_view)} Unidades")
        
        st.markdown("---")

        # --- ABAS (Definição Correta) ---
        tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Visão Geral", "📈 Evolução", "🩺 Top Procedimentos", "📋 Dados Detalhados", "🏥 Mapeamento CNES"])
        
        # ABA 1: Visão Geral (Gráfico Teto vs Produção)
        with tab1:
            st.subheader("Performance por Unidade (Top 10 por Teto)")
            df_chart = df_view.sort_values('Valor_Teto', ascending=False).head(10).copy()
            df_chart['Valor_Teto_Acumulado'] = df_chart['Valor_Teto'] * num_meses_papa
            
            # Wrap de texto para o eixo X
            def quebrar_texto_unidade(texto, limite=15):
                if not isinstance(texto, str): return str(texto)
                palavras = texto.split()
                linhas = []
                linha_atual = []
                contagem = 0
                for p in palavras:
                    if contagem + len(p) > limite:
                        linhas.append(" ".join(linha_atual)); linha_atual = [p]; contagem = len(p)
                    else: linha_atual.append(p); contagem += len(p) + 1
                if linha_atual: linhas.append(" ".join(linha_atual))
                return "<br>".join(linhas)
            
            df_chart['Unidade_Wrap'] = df_chart['Unidade'].apply(lambda x: quebrar_texto_unidade(x, 15))
            
            fig = go.Figure()
            # Teto (Cinza/Fundo)
            fig.add_trace(go.Bar(x=df_chart['Unidade_Wrap'], y=df_chart['Valor_Teto_Acumulado'], name='Teto (Acumulado)', marker_color='#95a5a6', opacity=0.9, text=df_chart['Valor_Teto_Acumulado'].apply(formatar_brl), textposition='outside'))
            # Produção (Azul/Destaque)
            fig.add_trace(go.Bar(x=df_chart['Unidade_Wrap'], y=df_chart['Valor_Produzido'], name='Produção', marker_color='#3498db', text=df_chart['Valor_Produzido'].apply(formatar_brl), textposition='auto'))
            
            fig.update_layout(
                barmode='group', 
                xaxis_tickangle=0, 
                legend=dict(orientation="h", y=1.1, x=0.5, xanchor='center'), 
                margin=dict(t=40), 
                height=500, 
                plot_bgcolor='white',
                yaxis_title="Valor (R$)"
            )
            st.plotly_chart(fig, use_container_width=True)

        # ABA 2: Evolução (Timeline)
        with tab2:
            st.subheader("Evolução Mensal da Produção")
            if not df_papa_final.empty:
                col_val = next((c for c in df_papa_final.columns if 'VALAPR' in c), 'PA_VALAPR')
                cnese = df_view['CNES_KEY'].unique()
                timeline = df_papa_final[df_papa_final['CNES_KEY'].isin(cnese)].groupby('MES_NOME')[col_val].sum().reset_index()
                timeline['Ordem'] = timeline['MES_NOME'].apply(lambda x: ordem_meses.index(x) if x in ordem_meses else 99)
                timeline = timeline.sort_values('Ordem')
                if not timeline.empty:
                    fig_line = px.line(timeline, x='MES_NOME', y=col_val, markers=True, text=timeline[col_val].apply(formatar_brl))
                    fig_line.update_traces(line_color='#3498db', line_width=4, textposition='top center')
                    fig_line.update_layout(plot_bgcolor='white', yaxis_title='Valor Produzido (R$)', xaxis_title='Mês')
                    st.plotly_chart(fig_line, use_container_width=True)
                else: st.info("Sem dados temporais para a seleção atual.")


        # ABA 3: Top Procedimentos
        with tab3:
            st.subheader("Top 5 Procedimentos por Valor")
            if not df_papa_final.empty:
                col_val = next((c for c in df_papa_final.columns if 'VALAPR' in c), 'PA_VALAPR')
                col_proc_id = next((c for c in df_papa_final.columns if 'PROC_ID' in c), 'PA_PROC_ID')
                
                cnese = df_view['CNES_KEY'].unique()
                df_proc = df_papa_final[df_papa_final['CNES_KEY'].isin(cnese)]
                top_proc = df_proc.groupby(col_proc_id)[col_val].sum().reset_index().sort_values(col_val, ascending=False).head(5)
                
                # Mapeamento de Nomes
                def get_nome_proc(cod, wrap=True):
                    c = apenas_digitos(str(cod))
                    nome = dict_procedimentos.get(c, dict_procedimentos.get(str(int(c)) if c.isdigit() else c, f"Proc. {cod}"))
                    if wrap:
                        return "<br>".join([nome[i:i+25] for i in range(0, len(nome), 25)])
                    return nome

                top_proc['Nome_Grafico'] = top_proc[col_proc_id].apply(lambda x: get_nome_proc(x, True))
                top_proc['Nome_Tabela'] = top_proc[col_proc_id].apply(lambda x: get_nome_proc(x, False))
                
                fig_bar_v = px.bar(top_proc, x='Nome_Grafico', y=col_val, text=top_proc[col_val].apply(formatar_brl), title="")
                fig_bar_v.update_traces(marker_color='#1abc9c', textposition='auto')
                fig_bar_v.update_layout(xaxis={'title': None, 'tickangle': 0}, yaxis_title="Valor (R$)", height=600, plot_bgcolor='white')
                st.plotly_chart(fig_bar_v, use_container_width=True)
                
                st.divider()
                # Aplica a formatação BR no pandas Styler
                st.dataframe(top_proc[[col_proc_id, 'Nome_Tabela', col_val]].rename(columns={col_proc_id:'Código', 'Nome_Tabela':'Procedimento', col_val:'Valor Total'}).style.format({'Valor Total': formatar_brl}), use_container_width=True)

        # ABA 4: DADOS BRUTOS COM BARRA DE PROGRESSO (CORRIGIDA COM HTML)
        with tab4:
            st.subheader("Detalhes da Execução por Unidade")
            df_exibicao = df_view[['Unidade', 'Valor_Teto', 'Valor_Produzido', 'Saldo', '% Execucao']].copy()
            df_exibicao['Valor_Teto'] = df_exibicao['Valor_Teto'] * num_meses_papa
            df_exibicao['Saldo'] = df_exibicao['Valor_Teto'] - df_exibicao['Valor_Produzido']
            df_exibicao['% Execucao'] = df_exibicao['% Execucao'] 
            
            # Formatação do DataFrame usando a formatação BR
            df_styled = df_exibicao.copy()
            df_styled.rename(columns={'Valor_Teto': 'Teto Acumulado', 'Valor_Produzido': 'Produção Total', '% Execucao': 'Execução (%)'}, inplace=True)
            
            # Cria a coluna com o HTML da barra de progresso (incluindo a porcentagem dentro do HTML)
            df_styled['Barra de Execução'] = df_styled['Execução (%)'].apply(style_progress_bar_html)

            # Aplica formatação monetária nas colunas (Função de Styler)
            def format_monetary(df):
                return df.style.format({
                    'Teto Acumulado': formatar_brl,
                    'Produção Total': formatar_brl,
                    'Saldo': formatar_brl,
                })
            
            # O DataFrame a ser estilizado
            df_to_style = df_styled[['Unidade', 'Teto Acumulado', 'Produção Total', 'Saldo', 'Barra de Execução']].copy()
            
            # Aplica o estilo na coluna da barra de progresso e depois no restante
            # Necessário para que o HTML seja renderizado
            styled_df = format_monetary(df_to_style)
            
            # O to_html() do Pandas gera uma tabela que, por padrão, se ajusta bem a 100%
            st.markdown(styled_df.to_html(escape=False), unsafe_allow_html=True)
            
            st.caption("Nota: A coluna **Barra de Execução** exibe o percentual calculado como (**Produção Total** / **Teto Acumulado**) x 100%, com preenchimento visual limitado a 100%. As cores seguem as regras: Verde (>=80%), Laranja (50% a 79%), Vermelho (<50%).")


        # ABA 5: Mapeamento CNES
        with tab5:
            st.subheader("Mapeamento CNES e Classificação")
            st.dataframe(df_view[['CNES_KEY', 'Unidade', 'Categoria']].drop_duplicates(), use_container_width=True, height=600)
            
    else: 
        st.error("❌ Erro na leitura dos arquivos ou o arquivo 'Teto (Espelho)' está vazio. Verifique se os arquivos CSV estão corretos.")
else:
    st.markdown("""
    <div style='text-align: center; margin-top: 100px; padding: 30px; border: 2px dashed #3498db; border-radius: 15px; background-color: white; box-shadow: 0 4px 10px rgba(0,0,0,0.05);'>
        <h2><span style="color: #3498db;">Bem-vindo ao Dashboard SUS!</span></h2>
        <p style='font-size: 1.1rem; color: #7f8c8d;'>
            Para começar, por favor, faça o upload dos arquivos de **Produção (PAPA)** e **Teto (Espelho)** na **barra lateral** à esquerda.
        </p>
    </div>
    """, unsafe_allow_html=True)