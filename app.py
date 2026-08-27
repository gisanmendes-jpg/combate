import streamlit as st
import random

st.set_page_config(layout="centered")
st.markdown("""
    <style>
        [data-testid="stHorizontalBlock"] { gap: 0rem !important; }
        [data-testid="column"] { padding: 0 !important; }
        .stButton > button {
            width: 100% !important; height: 60px !important;
            border-radius: 0px !important; margin: 0px !important;
            padding: 0px !important; border: 1px solid #d3d3d3 !important;
            font-size: 24px !important;
        }
        .stButton { margin-bottom: -16px !important; }
    </style>
""", unsafe_allow_html=True)

st.title("⚔️ Combate - Jogador vs Máquina")

col_btn1, col_btn2 = st.columns([1, 1])
with col_btn1:
    if st.button("🔄 Reiniciar Partida"):
        st.session_state.clear()
        st.rerun()
with col_btn2:
    # Botão manual para a máquina jogar quando você quiser ver o movimento dela
    if st.button("🤖 Passar a vez para a Máquina"):
        if st.session_state.get("turno_atual") == "vermelho" and not st.session_state.get("game_over"):
            jogada_da_maquina()
            st.session_state.turno_atual = "verde"
            st.rerun()

# ==========================================
# 1. FUNÇÕES DO JOGO
# ==========================================

def get_team(cell_content):
    if cell_content in ["⬜", "🌊"]: return None
    if "🟩" in cell_content: return "verde"
    if "🟥" in cell_content: return "vermelho"
    return None

def gerar_exercito(cor, emoji_cor):
    composicao = {
        "Prisioneiro": 1, "Bomba": 6, "10-Marechal": 1, "9-General": 1,
        "8-Coronel": 2, "7-Major": 3, "6-Capitao": 4, "5-Tenente": 4,
        "4-Sargento": 4, "3-Cabo": 5, "2-Soldado": 8, "1-Espiao": 1
    }
    exercito = []
    for patente, quantidade in composicao.items():
        for _ in range(quantidade):
            exercito.append(f"{emoji_cor} {patente}")
    return exercito

def resolver_combate(atacante, defensor):
    if " " not in atacante or " " not in defensor:
        return "empate"
        
    nome_atk = atacante.split(" ", 1)[1]
    nome_def = defensor.split(" ", 1)[1]
    
    if nome_def == "Prisioneiro": return "vitoria_jogo"
    if nome_def == "Bomba":
        return "vitoria" if "3-Cabo" in nome_atk else "derrota"
    if nome_atk == nome_def: return "empate"
    if "1-Espiao" in nome_atk and "10-Marechal" in nome_def: return "vitoria"
        
    forca_atk = int(nome_atk.split("-")[0])
    forca_def = int(nome_def.split("-")[0])
    
    return "vitoria" if forca_atk > forca_def else "derrota"

def is_valid_move(orig_r, orig_c, target_r, target_c):
    if not (0 <= target_r < 10 and 0 <= target_c < 10): return False
        
    orig_cell = st.session_state.board[orig_r][orig_c]
    if "Bomba" in orig_cell or "Prisioneiro" in orig_cell: return False
        
    if "2-Soldado" in orig_cell:
        if orig_r != target_r and orig_c != target_c: return False
        step_r = 1 if target_r > orig_r else (-1 if target_r < orig_r else 0)
        step_c = 1 if target_c > orig_c else (-1 if target_c < orig_c else 0)
        
        curr_r, curr_c = orig_r + step_r, orig_c + step_c
        while (curr_r, curr_c) != (target_r, target_c):
            if st.session_state.board[curr_r][curr_c] != "⬜": return False
            curr_r += step_r
            curr_c += step_c
    else:
        if abs(orig_r - target_r) + abs(orig_c - target_c) != 1: return False
            
    target_cell = st.session_state.board[target_r][target_c]
    if target_cell == "🌊": return False
    if get_team(orig_cell) == get_team(target_cell): return False
        
    return True

def avaliar_movimento(orig_r, orig_c, target_r, target_c):
    score = 0
    peca_atk = st.session_state.board[orig_r][orig_c]
    peca_def = st.session_state.board[target_r][target_c]
    
    if target_r < orig_r: score += 10 
        
    if peca_def != "⬜" and "🟩" in peca_def:
        score += 50
        if "Prisioneiro" in peca_def:
            score += 1000
            
    if "2-Soldado" in peca_atk:
        distancia = abs(orig_r - target_r) + abs(orig_c - target_c)
        if distancia > 1:
            score += (distancia * 3)
            
    return score

# ==========================================
# 2. MOTOR DA INTELIGÊNCIA ARTIFICIAL
# ==========================================

def jogada_da_maquina():
    if st.session_state.get("game_over"): return
    
    movimentos_possiveis = []
    
    for r in range(10):
        for c in range(10):
            cell = st.session_state.board[r][c]
            
            if "🟥" in cell and "Bomba" not in cell and "Prisioneiro" not in cell:
                direcoes = [(0, 1), (0, -1), (1, 0), (-1, 0)]
                alcance = 9 if "2-Soldado" in cell else 1
                
                for dr, dc in direcoes:
                    for passo in range(1, alcance + 1):
                        target_r = r + (dr * passo)
                        target_c = c + (dc * passo)
                        
                        if not (0 <= target_r < 10 and 0 <= target_c < 10):
                            break
                            
                        if is_valid_move(r, c, target_r, target_c):
                            score = avaliar_movimento(r, c, target_r, target_c)
                            movimentos_possiveis.append({
                                "orig": (r, c), "target": (target_r, target_c), "score": score
                            })
                            if st.session_state.board[target_r][target_c] != "⬜":
                                break
                        else:
                            break
                            
    if not movimentos_possiveis:
        return
        
    max_score = max(movimentos_possiveis, key=lambda x: x["score"])["score"]
    melhores_jogadas = [m for m in movimentos_possiveis if m["score"] == max_score]
    jogada_escolhida = random.choice(melhores_jogadas)
    
    orig_r, orig_c = jogada_escolhida["orig"]
    target_r, target_c = jogada_escolhida["target"]
    
    peca_atk = st.session_state.board[orig_r][orig_c]
    peca_def = st.session_state.board[target_r][target_c]
    
    if peca_def == "⬜":
        st.session_state.board[target_r][target_c] = peca_atk
        st.session_state.board[orig_r][orig_c] = "⬜"
    else:
        resultado = resolver_combate(peca_atk, peca_def)
        if resultado == "vitoria":
            st.session_state.board[target_r][target_c] = peca_atk
            st.session_state.board[orig_r][orig_c] = "⬜"
        elif resultado == "derrota":
            st.session_state.board[orig_r][orig_c] = "⬜"
        elif resultado == "empate":
            st.session_state.board[target_r][target_c] = "⬜"
            st.session_state.board[orig_r][orig_c] = "⬜"
        elif resultado == "vitoria_jogo":
            st.session_state.board[target_r][target_c] = peca_atk
            st.session_state.board[orig_r][orig_c] = "⬜"
            st.session_state.game_over = True
            st.session_state.vencedor = "Vermelho (Máquina)"
            
    st.toast("A Máquina executou a jogada dela!", icon="🤖")

# ==========================================
# 3. CONTROLE DE CLIQUES DO JOGADOR
# ==========================================

def handle_click(row, col):
    if st.session_state.get("game_over"): return
        
    clicked_item = st.session_state.board[row][col]
    if clicked_item == "🌊": return
        
    if st.session_state.selected_pos is None:
        if "🟩" in clicked_item:
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
                        st.toast("Você venceu o combate!", icon="⚔️")
                    elif resultado == "derrota":
                        st.session_state.board[orig_r][orig_c] = "⬜"
                        st.toast("Sua peça foi destruída!", icon="💥")
                    elif resultado == "empate":
                        st.session_state.board[row][col] = "⬜"
                        st.session_state.board[orig_r][orig_c] = "⬜"
                        st.toast("Combate empatado!", icon="🤝")
                    elif resultado == "vitoria_jogo":
                        st.session_state.board[row][col] = peca_atk
                        st.session_state.board[orig_r][orig_c] = "⬜"
                        st.session_state.game_over = True
                        st.session_state.vencedor = "Verde (Você)"
                        st.balloons() 
                        st.session_state.selected_pos = None
                        return
                
                # Terminou seu turno, agora é a vez da máquina responder
                st.session_state.turno_atual = "vermelho"
            else:
                st.toast("Movimento inválido!", icon="🚨")
                
        st.session_state.selected_pos = None

# ==========================================
# 4. INICIALIZAÇÃO DO ESTADO
# ==========================================

if "board" not in st.session_state:
    pecas_verdes = gerar_exercito("verde", "🟩")
    pecas_vermelhas = gerar_exercito("vermelho", "🟥")
    random.shuffle(pecas_verdes)
    random.shuffle(pecas_vermelhas)
    
    board = [["⬜" for _ in range(10)] for _ in range(10)]
    for r in [4, 5]:
        for c in [2, 3, 6, 7]: board[r][c] = "🌊"
            
    idx = 0
    for r in range(4):
        for c in range(10): board[r][c] = pecas_verdes[idx]; idx += 1
            
    idx = 0
    for r in range(6, 10):
        for c in range(10): board[r][c] = pecas_vermelhas[idx]; idx += 1
            
    st.session_state.board = board
    st.session_state.selected_pos = None
    st.session_state.game_over = False
    st.session_state.vencedor = None
    st.session_state.turno_atual = "vermelho"

# ==========================================
# 5. INTERFACE DO TABULEIRO
# ==========================================

if st.session_state.get("game_over"):
    st.success(f"🎉 JOGO ENCERRADO! A vitória é do exército {st.session_state.vencedor}!", icon="🏆")
else:
    st.write("Você é o **Verde**. Faça sua jogada e depois clique em **'Passar a vez para a Máquina'** para ver a resposta dela no seu próprio tempo.")

nevoa_ativada = st.toggle("🌫️ Ocultar patentes inimigas", value=True)

for row_idx in range(10):
    cols = st.columns(10) 
    for col_idx in range(10):
        with cols[col_idx]:
            cell_content = st.session_state.board[row_idx][col_idx]
            texto_exibicao = cell_content
            
            if nevoa_ativada and not st.session_state.get("game_over") and "🟥" in cell_content:
                texto_exibicao = "🟥"
            
            is_selected = st.session_state.selected_pos == (row_idx, col_idx)
            btn_type = "primary" if is_selected else "secondary"
            
            st.button(
                label=texto_exibicao,
                key=f"btn_{row_idx}_{col_idx}",
                on_click=handle_click,
                args=(row_idx, col_idx), 
                type=btn_type,
                use_container_width=True 
            )
