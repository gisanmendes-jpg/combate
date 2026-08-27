import streamlit as st
import random
import time

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

        /* Estilo visual das Cartas de Combate */
        .arena-container {
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 30px;
            margin: 40px 0;
        }
        .combat-card {
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            border: 3px solid #4a5568;
            border-radius: 15px;
            padding: 30px 20px;
            width: 220px;
            text-align: center;
            box-shadow: 0 10px 20px rgba(0,0,0,0.2);
            font-family: sans-serif;
        }
        .card-title {
            font-size: 14px;
            font-weight: bold;
            color: #4a5568;
            text-transform: uppercase;
            margin-bottom: 10px;
        }
        .card-body {
            font-size: 26px;
            font-weight: bold;
            color: #1a202c;
            margin: 15px 0;
        }
        .card-winner {
            border-color: #48bb78 !important;
            background: linear-gradient(135deg, #f0fff4 0%, #c6f6d5 100%) !important;
            transform: scale(1.05);
            box-shadow: 0 0 25px rgba(72, 187, 120, 0.6);
        }
        .card-loser {
            border-color: #f56565 !important;
            background: linear-gradient(135deg, #fff5f5 0%, #fed7d7 100%) !important;
            opacity: 0.5;
            text-decoration: line-through;
            filter: grayscale(40%);
        }
        .vs-text {
            font-size: 32px;
            font-weight: 900;
            color: #e53e3e;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
        }
    </style>
""", unsafe_allow_html=True)

st.title("⚔️ Combate - Jogador vs Máquina")

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

def obter_caminho(orig_r, orig_c, target_r, target_c):
    caminho = [(orig_r, orig_c)]
    step_r = 1 if target_r > orig_r else (-1 if target_r < orig_r else 0)
    step_c = 1 if target_c > orig_c else (-1 if target_c < orig_c else 0)
    
    curr_r, curr_c = orig_r + step_r, orig_c + step_c
    while (curr_r, curr_c) != (target_r, target_c):
        caminho.append((curr_r, curr_c))
        curr_r += step_r
        curr_c += step_c
    caminho.append((target_r, target_c))
    return caminho

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
# 2. MOTOR DA INTELIGÊNCIA ARTIFICIAL (COM CAMINHADA LENTA)
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
        st.toast("A Máquina não encontrou movimentos válidos.", icon="⚠️")
        return
        
    max_score = max(movimentos_possiveis, key=lambda x: x["score"])["score"]
    melhores_jogadas = [m for m in movimentos_possiveis if m["score"] == max_score]
    jogada_escolhida = random.choice(melhores_jogadas)
    
    orig_r, orig_c = jogada_escolhida["orig"]
    target_r, target_c = jogada_escolhida["target"]
    
    # Prepara a animação de caminhada no tabuleiro
    path = obter_caminho(orig_r, orig_c, target_r, target_c)
    st.session_state.anim_path = path
    st.session_state.anim_peca = st.session_state.board[orig_r][orig_c]
    st.session_state.anim_index = 0
    st.session_state.em_animacao = True

# ==========================================
# 3. CONTROLE DE CLIQUES DO JOGADOR
# ==========================================

def handle_click(row, col):
    if st.session_state.get("game_over") or st.session_state.get("em_animacao"): return
        
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
                    st.session_state.dados_combate = {
                        "orig": (orig_r, orig_c),
                        "target": (row, col),
                        "atacante": peca_atk,
                        "defensor": peca_def,
                        "resultado": resultado,
                        "quem_iniciou": "jogador"
                    }
                    st.session_state.fase_combate = True
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
    st.session_state.historico_combates = []
    st.session_state.fase_combate = False
    st.session_state.dados_combate = None
    st.session_state.em_animacao = False

# ==========================================
# 5. EXECUÇÃO DA ANIMAÇÃO DE CAMINHADA DA MÁQUINA
# ==========================================

if st.session_state.get("em_animacao"):
    path = st.session_state.anim_path
    idx = st.session_state.anim_index
    peca = st.session_state.anim_peca
    
    if idx < len(path):
        r, c = path[idx]
        
        # Remove da origem no primeiro passo
        if idx == 0:
            st.session_state.board[path[0][0]][path[0][1]] = "⬜"
        
        # Se for o último passo
        if idx == len(path) - 1:
            target_cell = st.session_state.board[r][c]
            if target_cell != "⬜":
                # Bateu em uma peça verde! Para a animação e abre a Arena de Cartas
                st.session_state.em_animacao = False
                resultado = resolver_combate(peca, target_cell)
                st.session_state.dados_combate = {
                    "orig": path[0],
                    "target": (r, c),
                    "atacante": peca,
                    "defensor": target_cell,
                    "resultado": resultado,
                    "quem_iniciou": "maquina"
                }
                st.session_state.fase_combate = True
                st.rerun()
            else:
                # Casa vazia, termina a caminhada aqui
                st.session_state.board[r][c] = peca
                st.session_state.em_animacao = False
                st.rerun()
        else:
            # Passo intermediário (casa vazia)
            st.session_state.board[r][c] = peca
            if idx > 0:
                prev_r, prev_c = path[idx - 1]
                st.session_state.board[prev_r][prev_c] = "⬜"
            
            st.session_state.anim_index += 1
            time.sleep(0.4) # Velocidade de passo a passo no tabuleiro
            st.rerun()

# ==========================================
# 6. TELA DE COMBATE CINEMATOGRÁFICA (CARTAS)
# ==========================================

if st.session_state.get("fase_combate"):
    st.markdown("---")
    st.markdown("<h2 style='text-align: center;'>⚔️ CONFRONTO NA ARENA ⚔️</h2>", unsafe_allow_html=True)
    
    dados = st.session_state.dados_combate
    atk = dados["atacante"]
    def_ = dados["defensor"]
    res = dados["resultado"]
    
    class_atk = "combat-card"
    class_def = "combat-card"
    status_msg = ""
    
    if res == "vitoria":
        class_atk += " card-winner"
        class_def += " card-loser"
        status_msg = f"🏆 O **{atk}** venceu o confronto e eliminou o inimigo!"
    elif res == "derrota":
        class_atk += " card-loser"
        class_def += " card-winner"
        status_msg = f"💀 O **{atk}** foi destruído pela defesa inimiga!"
    elif res == "empate":
        class_atk += " card-loser"
        class_def += " card-loser"
        status_msg = f"🤝 Empate total! Ambas as peças se destruíram mutuamente."
    elif res == "vitoria_jogo":
        class_atk += " card-winner"
        class_def += " card-loser"
        status_msg = f"🎉 **PRISIONEIRO CAPTURADO!**"

    st.markdown(f"""
        <div class="arena-container">
            <div class="{class_atk}">
                <div class="card-title">Atacante</div>
                <div class="card-body">{atk}</div>
            </div>
            <div class="vs-text">X</div>
            <div class="{class_def}">
                <div class="card-title">Defensor</div>
                <div class="card-body">{def_}</div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"<h3 style='text-align: center; color: #2d3748;'>{status_msg}</h3>", unsafe_allow_html=True)
    st.markdown("---")
    
    col_centro = st.columns([1, 2, 1])
    with col_centro[1]:
        if st.button("🎯 Continuar para o Tabuleiro", use_container_width=True):
            orig_r, orig_c = dados["orig"]
            target_r, target_c = dados["target"]
            
            if res == "vitoria":
                st.session_state.board[target_r][target_c] = atk
                st.session_state.board[orig_r][orig_c] = "⬜"
                st.session_state.historico_combates.insert(0, f"⚔️ {atk} derrotou {def_}")
            elif res == "derrota":
                st.session_state.board[orig_r][orig_c] = "⬜"
                st.session_state.historico_combates.insert(0, f"💥 {atk} foi destruído por {def_}")
            elif res == "empate":
                st.session_state.board[target_r][target_c] = "⬜"
                st.session_state.board[orig_r][orig_c] = "⬜"
                st.session_state.historico_combates.insert(0, f"🤝 Empate entre {atk} e {def_}")
            elif res == "vitoria_jogo":
                st.session_state.board[target_r][target_c] = atk
                st.session_state.board[orig_r][orig_c] = "⬜"
                st.session_state.game_over = True
                venc = "Verde (Você)" if "🟩" in atk else "Vermelho (Máquina)"
                st.session_state.vencedor = venc
                st.session_state.historico_combates.insert(0, f"🏆 Prisioneiro capturado!")
            
            st.session_state.fase_combate = False
            st.session_state.dados_combate = None
            st.session_state.selected_pos = None
            st.rerun()

# ==========================================
# 7. BARRA LATERAL (SIDEBAR) - PAINEL DE CONTROLE
# ==========================================

else:
    st.sidebar.title("📊 Painel de Controle")

    if st.sidebar.button("🔄 Reiniciar Partida"):
        st.session_state.clear()
        st.rerun()

    if st.sidebar.button("🤖 Passar a vez para a Máquina"):
        if not st.session_state.get("game_over") and not st.session_state.get("em_animacao"):
            jogada_da_maquina()
            st.rerun()

    st.sidebar.divider()

    vivas_verdes = 0
    vivas_vermelhas = 0
    for r in range(10):
        for c in range(10):
            celula = st.session_state.board[r][c]
            if "🟩" in celula: vivas_verdes += 1
            elif "🟥" in celula: vivas_vermelhas += 1

    st.sidebar.subheader("🛡️ Status dos Exércitos")
    st.sidebar.markdown(f"* 🟩 Suas Peças Vivas: **{vivas_verdes} / 40***")
    st.sidebar.markdown(f"* 🟥 Peças Inimigas: **{vivas_vermelhas} / 40***")

    st.sidebar.divider()

    st.sidebar.subheader("📜 Diário de Guerra")
    if st.session_state.get("historico_combates"):
        for evento in st.session_state.historico_combates[:6]:
            st.sidebar.markdown(f"- {evento}")
    else:
        st.sidebar.info("Ainda não ocorreram combates.")

    # ==========================================
    # 8. INTERFACE DO TABULEIRO
    # ==========================================

    if st.session_state.get("game_over"):
        st.success(f"🎉 JOGO ENCERRADO! A vitória é do exército {st.session_state.vencedor}!", icon="🏆")
    elif st.session_state.get("em_animacao"):
        st.info("🤖 A Máquina está se movimentando pelo tabuleiro...", icon="🚶‍♂️")
    else:
        st.write("Você é o **Verde**. Faça sua jogada e depois clique em **'Passar a vez para a Máquina'** na barra lateral.")

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
