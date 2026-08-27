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

if st.button("🔄 Reiniciar Partida"):
    st.session_state.clear()
    st.rerun()

# ==========================================
# 1. ÁREA DE FUNÇÕES BASE
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

def resolver_combate(atacante, defensor, silencioso=False):
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
    # Protege contra limites do tabuleiro (importante para a IA)
    if not (0 <= target_r < 10 and 0 <= target_c < 10): return False
        
    orig_cell = st.session_state.board[orig_r][orig_c]
    
    # Peças imóveis
    if "Bomba" in orig_cell or "Prisioneiro" in orig_cell: return False
        
    # --- REGRA ESPECIAL DO SOLDADO ---
    if "2-Soldado" in orig_cell:
        # O Soldado deve andar apenas em linha reta (não pode ser diagonal)
        if orig_r != target_r and orig_c != target_c:
            return False
            
        # Determina a direção do passo (+1, -1 ou 0)
        step_r = 1 if target_r > orig_r else (-1 if target_r < orig_r else 0)
        step_c = 1 if target_c > orig_c else (-1 if target_c < orig_c else 0)
        
        # Percorre o caminho verificando se há obstáculos ANTES do destino final
        curr_r, curr_c = orig_r + step_r, orig_c + step_c
        while (curr_r, curr_c) != (target_r, target_c):
            # Se bater em qualquer coisa no caminho (água, amigos ou inimigos), trava
            if st.session_state.board[curr_r][curr_c] != "⬜":
                return False
            curr_r += step_r
            curr_c += step_c
            
    # --- REGRA PADRÃO PARA OUTRAS PEÇAS ---
    else:
        # Demais peças andam apenas 1 casa
        if abs(orig_r - target_r) + abs(orig_c - target_c) != 1: 
            return False
            
    # Checagens finais no destino (Agua e Fogo Amigo)
    target_cell = st.session_state.board[target_r][target_c]
    
    if target_cell == "🌊": return False
    if get_team(orig_cell) == get_team(target_cell): return False
        
    return True


def avaliar_movimento(orig_r, orig_c, target_r, target_c):
    score = 0
    peca_atk = st.session_state.board[orig_r][orig_c]
    peca_def = st.session_state.board[target_r][target_c]
    
    # 1. Peso de Avanço: Recompensa por marchar para o norte (linha 0)
    # Como o vermelho começa embaixo (linhas 6 a 9), ir para uma linha menor é avanço.
    if target_r < orig_r:
        score += 10 
        
    # 2. Peso de Agressividade: Recompensa altíssima por atacar uma peça inimiga
    if peca_def != "⬜":
        score += 50
        
        # Faro assassino: Se a máquina "farejar" o prisioneiro (um pequeno cheat da IA), foco total
        if "Prisioneiro" in peca_def:
            score += 1000
            
    # 3. Peso Tático: Incentivo para o Soldado explorar seu super movimento
    if "2-Soldado" in peca_atk:
        distancia = abs(orig_r - target_r) + abs(orig_c - target_c)
        if distancia > 1:
            score += (distancia * 5) # Quanto mais longe ele for, melhor a nota
            
    return score
    
# ==========================================
# 2. MOTOR DA INTELIGÊNCIA ARTIFICIAL
# ==========================================

def jogada_da_maquina():
    movimentos_possiveis = []
    
    # 1. Varredura Tática: Analisa todas as peças vermelhas no tabuleiro
    for r in range(10):
        for c in range(10):
            cell = st.session_state.board[r][c]
            
            if "🟥" in cell and "Bomba" not in cell and "Prisioneiro" not in cell:
                
                # O Soldado pode tentar andar até 9 casas; as outras peças, apenas 1
                alcance = 9 if "2-Soldado" in cell else 1
                direcoes = [(0, 1), (0, -1), (1, 0), (-1, 0)]
                
                for dr, dc in direcoes:
                    for passo in range(1, alcance + 1):
                        target_r = r + (dr * passo)
                        target_c = c + (dc * passo)
                        
                        # Usa o motor físico do jogo para validar
                        if is_valid_move(r, c, target_r, target_c):
                            score = avaliar_movimento(r, c, target_r, target_c)
                            movimentos_possiveis.append({
                                "orig": (r, c),
                                "target": (target_r, target_c),
                                "score": score
                            })
                        else:
                            # Se esbarrou em obstáculo, o soldado para de olhar nessa direção
                            break
                            
    # Se a máquina ficar travada sem movimentos, passa a vez
    if not movimentos_possiveis:
        st.session_state.turno_atual = "verde"
        return
        
    # 2. Tomada de Decisão (Otimização)
    # Encontra a nota máxima entre todos os cenários projetados
    max_score = max(movimentos_possiveis, key=lambda x: x["score"])["score"]
    
    # Filtra as jogadas que empataram na nota máxima
    melhores_jogadas = [m for m in movimentos_possiveis if m["score"] == max_score]
    
    # Sorteia uma das melhores opções para manter a imprevisibilidade
    jogada_escolhida = random.choice(melhores_jogadas)
    
    orig_r, orig_c = jogada_escolhida["orig"]
    target_r, target_c = jogada_escolhida["target"]
    
    # 3. Execução do Movimento
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
            st.error("💀 A Máquina capturou seu Prisioneiro! Você perdeu.")
            
    st.toast("A Máquina executou uma jogada tática!", icon="🤖")
    st.session_state.turno_atual = "verde"

# ==========================================
# 3. LÓGICA DE CLIQUE DO JOGADOR
# ==========================================

def handle_click(row, col):
    # Se não for a vez do jogador, ignora cliques
    if st.session_state.turno_atual != "verde": return
        
    clicked_item = st.session_state.board[row][col]
    if clicked_item == "🌊": return
        
    if st.session_state.selected_pos is None:
        # Só deixa selecionar peças verdes
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
                        st.balloons() 
                        st.success("🏆 Você capturou o Prisioneiro inimigo! VITÓRIA!")
                
                # Passa a vez para a máquina
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
        for c in range(10):
            board[r][c] = pecas_verdes[idx]; idx += 1
            
    idx = 0
    for r in range(6, 10):
        for c in range(10):
            board[r][c] = pecas_vermelhas[idx]; idx += 1
            
    st.session_state.board = board
    st.session_state.selected_pos = None
    st.session_state.turno_atual = "verde"

# --- Gatilho da IA ---
# Se for a vez do vermelho, a máquina joga e recarrega a tela
if st.session_state.turno_atual == "vermelho":
    jogada_da_maquina()
    st.rerun()

# ==========================================
# 5. INTERFACE DO TABULEIRO
# ==========================================

st.write("Você é o **Verde**. Clique na sua peça e depois no destino.")
nevoa_ativada = st.toggle("🌫️ Ocultar patentes inimigas", value=True)

for row_idx in range(10):
    cols = st.columns(10) 
    for col_idx in range(10):
        with cols[col_idx]:
            cell_content = st.session_state.board[row_idx][col_idx]
            
            # Oculta APENAS as peças vermelhas se a névoa estiver ativa
            texto_exibicao = cell_content
            if nevoa_ativada and "🟥" in cell_content:
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
