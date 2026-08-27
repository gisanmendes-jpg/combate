import streamlit as st
import random

st.set_page_config(layout="centered")
st.markdown("""
    <style>
        /* 1. Zera o gap (espaço horizontal) entre as colunas nativas do Streamlit */
        [data-testid="stHorizontalBlock"] {
            gap: 0rem !important;
        }
        
        /* 2. Zera o padding interno de cada coluna */
        [data-testid="column"] {
            padding: 0 !important;
        }

        /* 3. Força o botão a ser perfeitamente quadrado e sem bordas arredondadas */
        .stButton > button {
            width: 100% !important;
            height: 60px !important;
            border-radius: 0px !important;
            margin: 0px !important;
            padding: 0px !important;
            border: 1px solid #d3d3d3 !important;
            font-size: 24px !important;
        }

        /* 4. Truque para colar as linhas verticais (puxa o botão de baixo para cima) */
        .stButton {
            margin-bottom: -16px !important; 
        }
    </style>
""", unsafe_allow_html=True)

st.title("⚔️ Combate - Prototipando o Tabuleiro")

if st.button("🔄 Reiniciar Partida (Limpar Memória)"):
    st.session_state.clear()
    st.rerun()

# ==========================================
# 1. ÁREA DE FUNÇÕES (Todas juntas no topo)
# ==========================================

def get_team(cell_content):
    if cell_content in ["⬜", "🌊"]:
        return None
    if "🟩" in cell_content:
        return "verde"
    if "🟥" in cell_content:
        return "vermelho"
    return None

def gerar_exercito(cor, emoji_cor):
    composicao = {
        "Prisioneiro": 1,
        "Bomba": 6,
        "10-Marechal": 1,
        "9-General": 1,
        "8-Coronel": 2,
        "7-Major": 3,
        "6-Capitao": 4,
        "5-Tenente": 4,
        "4-Sargento": 4,
        "3-Cabo": 5,
        "2-Soldado": 8,
        "1-Espiao": 1
    }
    exercito = []
    for patente, quantidade in composicao.items():
        for _ in range(quantidade):
            peca = f"{emoji_cor} {patente}"
            exercito.append(peca)
    return exercito

def resolver_combate(atacante, defensor):
    if " " not in atacante or " " not in defensor:
        st.toast("Erro de leitura na peça. Combate anulado.", icon="⚠️")
        return "empate"
        
    nome_atk = atacante.split(" ", 1)[1]
    nome_def = defensor.split(" ", 1)[1]
    
    if nome_def == "Prisioneiro":
        return "vitoria_jogo"
        
    if nome_def == "Bomba":
        if "3-Cabo" in nome_atk:
            return "vitoria"
        else:
            return "derrota"
            
    if nome_atk == nome_def:
        return "empate"
        
    if "1-Espiao" in nome_atk and "10-Marechal" in nome_def:
        return "vitoria"
        
    forca_atk = int(nome_atk.split("-")[0])
    forca_def = int(nome_def.split("-")[0])
    
    if forca_atk > forca_def:
        return "vitoria"
    else:
        return "derrota"

def is_valid_move(orig_r, orig_c, target_r, target_c):
    orig_cell = st.session_state.board[orig_r][orig_c]
    
    if "Bomba" in orig_cell or "Prisioneiro" in orig_cell:
        return False
        
    distance = abs(orig_r - target_r) + abs(orig_c - target_c)
    if distance != 1:
        return False
        
    target_cell = st.session_state.board[target_r][target_c]
    if target_cell == "🌊":
        return False
        
    orig_team = get_team(orig_cell)
    target_team = get_team(target_cell)
    if target_team is not None and orig_team == target_team:
        return False
        
    return True

def handle_click(row, col):
    clicked_item = st.session_state.board[row][col]
    
    if clicked_item == "🌊":
        return
        
    if st.session_state.selected_pos is None:
        if clicked_item != "⬜":
            st.session_state.selected_pos = (row, col)
    else:
        orig_r, orig_c = st.session_state.selected_pos
        
        if (orig_r, orig_c) != (row, col):
            if is_valid_move(orig_r, orig_c, row, col):
                peca_atk = st.session_state.board[orig_r][orig_c]
                peca_def = st.session_state.board[row][col]
                
                if peca_def == "⬜":
                    st.session_state.board[row][col] = peca_atk
                    st.session_state.board[orig_r][orig_c] = "⬜" 
                else:
                    resultado = resolver_combate(peca_atk, peca_def)
                    
                    if resultado == "vitoria":
                        st.session_state.board[row][col] = peca_atk
                        st.session_state.board[orig_r][orig_c] = "⬜"
                        st.toast("Você venceu o combate! Inimigo abatido.", icon="⚔️")
                    elif resultado == "derrota":
                        st.session_state.board[orig_r][orig_c] = "⬜"
                        st.toast("Sua peça foi destruída!", icon="💥")
                    elif resultado == "empate":
                        st.session_state.board[row][col] = "⬜"
                        st.session_state.board[orig_r][orig_c] = "⬜"
                        st.toast("Combate empatado! Ambas peças destruídas.", icon="🤝")
                    elif resultado == "vitoria_jogo":
                        st.session_state.board[row][col] = peca_atk
                        st.session_state.board[orig_r][orig_c] = "⬜"
                        st.balloons() 
                        st.success("🏆 Você capturou o Prisioneiro inimigo! FIM DE JOGO!")
            else:
                st.toast("Movimento inválido!", icon="🚨")
                
        st.session_state.selected_pos = None

# ==========================================
# 2. INICIALIZAÇÃO DO JOGO
# ==========================================

if "board" not in st.session_state:
    # Como gerar_exercito já foi lida no topo, agora funciona!
    pecas_verdes = gerar_exercito("verde", "🟩")
    pecas_vermelhas = gerar_exercito("vermelho", "🟥")
    
    random.shuffle(pecas_verdes)
    random.shuffle(pecas_vermelhas)
    
    board = [["⬜" for _ in range(10)] for _ in range(10)]
    
    for r in [4, 5]:
        for c in [2, 3, 6, 7]:
            board[r][c] = "🌊"
            
    idx = 0
    for r in range(4):
        for c in range(10):
            board[r][c] = pecas_verdes[idx]
            idx += 1
            
    idx = 0
    for r in range(6, 10):
        for c in range(10):
            board[r][c] = pecas_vermelhas[idx]
            idx += 1
            
    st.session_state.board = board
    st.session_state.selected_pos = None

# ==========================================
# 3. RENDERIZAÇÃO DA INTERFACE
# ==========================================

st.write("Selecione uma peça verde ou vermelha e depois clique em um quadrado branco para mover.")

for row_idx in range(10):
    cols = st.columns(10) 
    
    for col_idx in range(10):
        with cols[col_idx]:
            cell_content = st.session_state.board[row_idx][col_idx]
            
            is_selected = st.session_state.selected_pos == (row_idx, col_idx)
            button_type = "primary" if is_selected else "secondary"
            
            st.button(
                label=cell_content,
                key=f"btn_{row_idx}_{col_idx}",
                on_click=handle_click,
                args=(row_idx, col_idx), 
                type=button_type,
                use_container_width=True 
            )
