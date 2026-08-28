import streamlit as st
import random

st.set_page_config(layout="centered", page_title="Combate Tático", page_icon="⚔️")

# ==========================================
# ESTILIZAÇÃO VISUAL TÁTICA (CONTRASTE CORRIGIDO)
# ==========================================
st.markdown("""
    <style>
        .stApp {
            background-color: #0f172a;
            color: #f8fafc;
        }
        
        [data-testid="stHorizontalBlock"] { gap: 0rem !important; }
        [data-testid="column"] { padding: 0 !important; }
        
        /* Ajuste do botão para comportar 2 linhas e FORÇAR COR CLARA */
        .stButton > button {
            width: 100% !important; height: 65px !important;
            border-radius: 6px !important; margin: 0px !important;
            padding: 2px !important; border: 1px solid #334155 !important;
            background-color: #1e293b !important;
            transition: all 0.2s ease-in-out;
        }
        
        /* Força o texto interno a ser branco/legível e quebrar linha */
        .stButton > button p {
            font-size: 10.5px !important; 
            font-weight: bold !important;
            line-height: 1.3 !important;
            white-space: pre-wrap !important; 
            margin: 0 !important;
            color: #f8fafc !important; /* TEXTO BRANCO */
            text-shadow: 1px 1px 2px rgba(0,0,0,0.8); /* Sombra para destacar */
        }
        
        /* Garante que botões bloqueados continuem legíveis */
        .stButton > button:disabled p {
            color: #94a3b8 !important; /* TEXTO CINZA CLARO NO BLOQUEIO */
        }

        .stButton > button:hover {
            border-color: #38bdf8 !important;
            transform: scale(1.02);
            z-index: 10;
        }
        .stButton { margin-bottom: -16px !important; }

        .main-title {
            text-align: center;
            font-family: 'Courier New', Courier, monospace;
            font-weight: 900;
            color: #f1f5f9;
            text-transform: uppercase;
            letter-spacing: 2px;
            margin-bottom: 20px;
            text-shadow: 0 0 10px rgba(56, 189, 248, 0.5);
        }

        .arena-container {
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 30px;
            margin: 40px 0;
        }
        .combat-card {
            background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
            border: 3px solid #475569;
            border-radius: 12px;
            padding: 30px 20px;
            width: 240px;
            text-align: center;
            box-shadow: 0 15px 30px rgba(0,0,0,0.5);
            font-family: 'Courier New', Courier, monospace;
        }
        .card-title {
            font-size: 13px;
            font-weight: bold;
            color: #94a3b8;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 15px;
        }
        .card-body {
            font-size: 22px;
            font-weight: bold;
            color: #f8fafc;
            margin: 15px 0;
            white-space: pre-wrap;
        }
        .card-winner {
            border-color: #22c55e !important;
            background: linear-gradient(135deg, #052e16 0%, #1e293b 100%) !important;
            transform: scale(1.06);
            box-shadow: 0 0 30px rgba(34, 197, 94, 0.4);
        }
        .card-loser {
            border-color: #ef4444 !important;
            background: linear-gradient(135deg, #450a0a 0%, #1e293b 100%) !important;
            opacity: 0.6;
            text-decoration: line-through;
            filter: grayscale(30%);
        }
        .vs-text {
            font-size: 36px;
            font-weight: 900;
            color: #ef4444;
            text-shadow: 0 0 15px rgba(239, 68, 68, 0.6);
        }
        
        ::-webkit-scrollbar { width: 8px; }
        ::-webkit-scrollbar-track { background: #0f172a; }
        ::-webkit-scrollbar-thumb { background: #475569; border-radius: 4px; }
        ::-webkit-scrollbar-thumb:hover { background: #64748b; }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 class='main-title'>⚔️ Centro de Comando: Combate Tático</h1>", unsafe_allow_html=True)

# ==========================================
# 1. FUNÇÕES DO JOGO E ÍCONES
# ==========================================

ICONES_PECAS = {
    "Prisioneiro": "🚩", "Bomba": "💣", "10-Marechal": "🎖️", "9-General": "🦅", 
    "8-Coronel": "🪖", "7-Major": "🛡️", "6-Capitao": "⚔️", "5-Tenente": "🔫", 
    "4-Sargento": "🎯", "3-Cabo": "🔧", "2-Soldado": "🏃", "1-Espiao": "🕵️"
}

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
        for _ in range(quantidade): exercito.append(f"{emoji_cor} {patente}")
    return exercito

def resolver_combate(atacante, defensor):
    if " " not in atacante or " " not in defensor: return "empate"
    nome_atk = atacante.split(" ", 1)[1]
    nome_def = defensor.split(" ", 1)[1]
    
    if nome_def == "Prisioneiro": return "vitoria_jogo"
    if nome_def == "Bomba": return "vitoria" if "3-Cabo" in nome_atk else "derrota"
    if nome_atk == nome_def: return "empate"
    if "1-Espiao" in nome_atk and "10-Marechal" in nome_def: return "vitoria"
        
    try:
        forca_atk = int(nome_atk.split("-")[0])
        forca_def = int(nome_def.split("-")[0])
        return "vitoria" if forca_atk > forca_def else "derrota"
    except: return "empate"

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
        if "Prisioneiro" in peca_def: score += 1000
    if "2-Soldado" in peca_atk:
        distancia = abs(orig_r - target_r) + abs(orig_c - target_c)
        if distancia > 1: score += (distancia * 3)
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
                        if not (0 <= target_r < 10 and 0 <= target_c < 10): break
                        if is_valid_move(r, c, target_r, target_c):
                            score = avaliar_movimento(r, c, target_r, target_c)
                            movimentos_possiveis.append({"orig": (r, c), "target": (target_r, target_c), "score": score})
                            if st.session_state.board[target_r][target_c] != "⬜": break
                        else: break
                            
    if not movimentos_possiveis:
        st.session_state.ultimo_movimento_maquina = "A Máquina tentou se mover, mas está sem jogadas válidas."
        st.session_state.turno_atual = "verde"
        return
        
    max_score = max(movimentos_possiveis, key=lambda x: x["score"])["score"]
    melhores_jogadas = [m for m in movimentos_possiveis if m["score"] == max_score]
    jogada_escolhida = random.choice(melhores_jogadas)
    
    orig_r, orig_c = jogada_escolhida["orig"]
    target_r, target_c = jogada_escolhida["target"]
    peca_atk = st.session_state.board[orig_r][orig_c]
    peca_def = st.session_state.board[target_r][target_c]
    
    st.session_state.ultima_origem_maquina = (orig_r, orig_c)
    st.session_state.ultimo_destino_maquina = (target_r, target_c)
    
    if peca_def == "⬜":
        st.session_state.board[target_r][target_c] = peca_atk
        st.session_state.board[orig_r][orig_c] = "⬜"
        st.session_state.ultimo_movimento_maquina = f"🤖 Inimigo avançou de ({orig_r+1}, {orig_c+1}) para ({target_r+1}, {target_c+1})."
        st.session_state.turno_atual = "verde"
    else:
        resultado = resolver_combate(peca_atk, peca_def)
        st.session_state.dados_combate = {
            "orig": (orig_r, orig_c), "target": (target_r, target_c),
            "atacante": peca_atk, "defensor": peca_def,
            "resultado": resultado, "quem_iniciou": "maquina"
        }
        st.session_state.fase_combate = True
        st.session_state.ultimo_movimento_maquina = f"⚔️ Inimigo atacou em ({target_r+1}, {target_c+1})!"

# ==========================================
# 3. CONTROLE DE CLIQUES DO JOGADOR
# ==========================================

def handle_click(row, col):
    if st.session_state.get("game_over") or st.session_state.get("fase_combate") or st.session_state.get("turno_atual") != "verde": return
    clicked_item = st.session_state.board[row][col]
    if clicked_item == "🌊": return
        
    if st.session_state.selected_pos is None:
        if "🟩" in clicked_item: st.session_state.selected_pos = (row, col)
    else:
        orig_r, orig_c = st.session_state.selected_pos
        if (orig_r, orig_c) != (row, col):
            if is_valid_move(orig_r, orig_c, row, col):
                peca_atk = st.session_state.board[orig_r][orig_c]
                peca_def = st.session_state.board[row][col]
                st.session_state.ultima_origem_maquina = None
                st.session_state.ultimo_destino_maquina = None
                
                if peca_def == "⬜":
                    st.session_state.board[row][col] = peca_atk
                    st.session_state.board[orig_r][orig_c] = "⬜" 
                    st.session_state.ultimo_movimento_maquina = f"Sua jogada: moveu de ({orig_r+1}, {orig_c+1}) para ({row+1}, {col+1})."
                    st.session_state.turno_atual = "vermelho"
                else:
                    resultado = resolver_combate(peca_atk, peca_def)
                    st.session_state.dados_combate = {
                        "orig": (orig_r, orig_c), "target": (row, col),
                        "atacante": peca_atk, "defensor": peca_def,
                        "resultado": resultado, "quem_iniciou": "jogador"
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
    st.session_state.turno_atual = "verde"
    st.session_state.historico_combates = []
    st.session_state.fase_combate = False
    st.session_state.dados_combate = None
    st.session_state.ultima_origem_maquina = None
    st.session_state.ultimo_destino_maquina = None
    st.session_state.ultimo_movimento_maquina = "Área segura. Aguardando ordens de marcha."

if st.session_state.get("turno_atual") == "vermelho" and not st.session_state.get("game_over") and not st.session_state.get("fase_combate"):
    jogada_da_maquina()
    st.rerun()

# ==========================================
# 5. TELA DE COMBATE CINEMATOGRÁFICA
# ==========================================

if st.session_state.get("fase_combate"):
    st.markdown("""<audio autoplay style="display:none;"><source src="https://actions.google.com/sounds/v1/alarms/beep_short.ogg" type="audio/ogg"></audio>""", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("<h2 style='text-align: center; color: #f8fafc; font-family: Courier New;'>⚡ CONFRONTO IMINENTE NA ARENA ⚡</h2>", unsafe_allow_html=True)
    
    dados = st.session_state.dados_combate
    atk = dados["atacante"]
    def_ = dados["defensor"]
    res = dados["resultado"]
    quem_iniciou = dados["quem_iniciou"]
    
    nome_atk = atk.split(" ", 1)[1] if " " in atk else atk
    nome_def = def_.split(" ", 1)[1] if " " in def_ else def_
    icone_atk = ICONES_PECAS.get(nome_atk, "♟️")
    icone_def = ICONES_PECAS.get(nome_def, "♟️")
    
    class_atk = "combat-card card-winner" if res in ["vitoria", "vitoria_jogo"] else "combat-card card-loser"
    class_def = "combat-card card-loser" if res in ["vitoria", "vitoria_jogo"] else "combat-card card-winner"
    if res == "empate":
        class_atk, class_def = "combat-card card-loser", "combat-card card-loser"
        
    status_msg = {
        "vitoria": f"🏆 Vitória da tropa **{nome_atk}**!",
        "derrota": f"💀 A tropa **{nome_atk}** foi neutralizada!",
        "empate": "🤝 Conflito anulado! Ambas as unidades destruídas.",
        "vitoria_jogo": "🎉 **ALVO ESTRATÉGICO CAPTURADO COM SUCESSO!**"
    }[res]

    st.markdown(f"""
        <div class="arena-container">
            <div class="{class_atk}">
                <div class="card-title">Atacante</div>
                <div class="card-body">{icone_atk}<br>{nome_atk}</div>
            </div>
            <div class="vs-text">VS</div>
            <div class="{class_def}">
                <div class="card-title">Defensor</div>
                <div class="card-body">{icone_def}<br>{nome_def}</div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    st.markdown(f"<h3 style='text-align: center; color: #cbd5e1; font-size: 18px;'>{status_msg}</h3>", unsafe_allow_html=True)
    st.markdown("---")
    
    col_centro = st.columns([1, 2, 1])
    with col_centro[1]:
        if st.button("🎯 Retornar ao Centro de Comando", use_container_width=True):
            orig_r, orig_c = dados["orig"]
            target_r, target_c = dados["target"]
            
            if quem_iniciou == "jogador":
                txt_atk = f"<span style='color:#4ade80; font-weight:bold;'>Seu {nome_atk}</span>"
                txt_def = f"<span style='color:#f87171; font-weight:bold;'>{nome_def} inimigo</span>"
            else:
                txt_atk = f"<span style='color:#f87171; font-weight:bold;'>{nome_atk} inimigo</span>"
                txt_def = f"<span style='color:#4ade80; font-weight:bold;'>Seu {nome_def}</span>"

            if res == "vitoria":
                st.session_state.board[target_r][target_c] = atk
                st.session_state.board[orig_r][orig_c] = "⬜"
                msg_log = f"🎯 {txt_atk} destruiu {txt_def}."
            elif res == "derrota":
                st.session_state.board[orig_r][orig_c] = "⬜"
                msg_log = f"💥 {txt_atk} foi eliminado por {txt_def}."
            elif res == "empate":
                st.session_state.board[target_r][target_c] = "⬜"
                st.session_state.board[orig_r][orig_c] = "⬜"
                msg_log = f"🤝 {txt_atk} e {txt_def} se destruíram."
            elif res == "vitoria_jogo":
                st.session_state.board[target_r][target_c] = atk
                st.session_state.board[orig_r][orig_c] = "⬜"
                st.session_state.game_over = True
                st.session_state.vencedor = "Verde (Você)" if "🟩" in atk else "Vermelho (Máquina)"
                msg_log = f"🏆 {txt_atk} capturou o Prisioneiro!"
                
            st.session_state.historico_combates.insert(0, msg_log)
            
            st.session_state.fase_combate = False
            st.session_state.dados_combate = None
            st.session_state.selected_pos = None
            st.session_state.turno_atual = "verde"
            st.rerun()

# ==========================================
# 6. BARRA LATERAL E TABULEIRO
# ==========================================
else:
    st.sidebar.title("📡 Painel Tático")
    if st.sidebar.button("🔄 Reiniciar Operação"):
        st.session_state.clear()
        st.rerun()
    st.sidebar.divider()

    vivas_verdes, vivas_vermelhas = 0, 0
    for r in range(10):
        for c in range(10):
            if "🟩" in st.session_state.board[r][c]: vivas_verdes += 1
            elif "🟥" in st.session_state.board[r][c]: vivas_vermelhas += 1

    st.sidebar.subheader("🛡️ Status das Tropas")
    st.sidebar.markdown(f"* 🟩 Suas Forças: **{vivas_verdes} / 40***")
    st.sidebar.markdown(f"* 🟥 Forças Inimigas: **{vivas_vermelhas} / 40***")
    st.sidebar.divider()

    st.sidebar.subheader("📜 Relatório de Inteligência")
    if st.session_state.get("historico_combates"):
        # FORÇA A COR BRANCA DENTRO DA DIV DO RELATÓRIO
        html_log = "<div style='background-color: #1e293b; color: #f8fafc; padding: 12px; border-radius: 8px; max-height: 350px; overflow-y: auto; border: 1px solid #334155;'>"
        for idx, evento in enumerate(st.session_state.historico_combates):
            borda = "border-bottom: 1px solid #334155;" if idx < len(st.session_state.historico_combates)-1 else ""
            html_log += f"<div style='font-size: 12.5px; line-height: 1.5; padding-bottom: 10px; margin-bottom: 10px; {borda}'>{evento}</div>"
        html_log += "</div>"
        st.sidebar.markdown(html_log, unsafe_allow_html=True)
    else: 
        st.sidebar.info("Nenhum conflito reportado.")

    if st.session_state.get("game_over"):
        st.success(f"🎉 OPERAÇÃO CONCLUÍDA! Vitória do exército {st.session_state.vencedor}!", icon="🏆")
    else:
        if st.session_state.get("turno_atual") == "verde":
            st.success("🟢 **Status: Turno do Jogador.** Selecione a unidade e ordene o avanço.", icon="🎯")
        else:
            st.warning("🔴 **Status: Inteligência Inimiga Agindo...**", icon="🛰️")
        st.info(st.session_state.get("ultimo_movimento_maquina", ""), icon="📢")

    nevoa_ativada = st.toggle("🌫️ Ativar Névoa de Guerra (Ocultar Patentes Inimigas)", value=True)

    header_cols = st.columns(11)
    with header_cols[0]: st.write("")
    for c_idx in range(10):
        with header_cols[c_idx + 1]:
            st.markdown(f"<div style='text-align: center; font-weight: bold; color: #94a3b8; font-size: 14px; margin-bottom: 5px;'>{c_idx + 1}</div>", unsafe_allow_html=True)

    destino_maquina = st.session_state.get("ultimo_destino_maquina")
    travar_botoes = (st.session_state.get("turno_atual") != "verde") or st.session_state.get("game_over")

    for row_idx in range(10):
        row_cols = st.columns(11)
        with row_cols[0]:
            st.markdown(f"<div style='display: flex; align-items: center; justify-content: center; height: 65px; font-weight: bold; color: #94a3b8; font-size: 14px;'>{row_idx + 1}</div>", unsafe_allow_html=True)
            
        for col_idx in range(10):
            with row_cols[col_idx + 1]:
                cell_content = st.session_state.board[row_idx][col_idx]
                
                if cell_content == "⬜":
                    texto_exibicao = " "
                elif cell_content == "🌊":
                    texto_exibicao = "🌊"
                else:
                    if nevoa_ativada and not st.session_state.get("game_over") and "🟥" in cell_content:
                        texto_exibicao = "❓\nInimigo"
                    else:
                        time_cor = "🟢" if "🟩" in cell_content else "🔴"
                        nome_peca = cell_content.split(" ", 1)[1]
                        icone_peca = ICONES_PECAS.get(nome_peca, "♟️")
                        texto_exibicao = f"{time_cor} {icone_peca}\n{nome_peca}"
                
                is_selected = st.session_state.selected_pos == (row_idx, col_idx)
                is_last_move = (destino_maquina == (row_idx, col_idx))
                
                if is_selected:
                    btn_type = "primary"
                elif is_last_move:
                    btn_type = "primary"
                    if texto_exibicao.strip(): 
                        texto_exibicao = f"📍 {texto_exibicao}"
                else:
                    btn_type = "secondary"
                
                st.button(
                    label=texto_exibicao,
                    key=f"btn_{row_idx}_{col_idx}",
                    on_click=handle_click,
                    args=(row_idx, col_idx), 
                    type=btn_type,
                    disabled=travar_botoes,
                    use_container_width=True 
                )
