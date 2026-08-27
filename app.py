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
            height: 60px !important; /* Você pode aumentar aqui se quiser casas maiores */
            border-radius: 0px !important;
            margin: 0px !important;
            padding: 0px !important;
            border: 1px solid #d3d3d3 !important; /* Cria uma linha sutil imitando o quadriculado */
            font-size: 24px !important; /* Aumenta o tamanho dos emojis */
        }

        /* 4. Truque para colar as linhas verticais (puxa o botão de baixo para cima) */
        .stButton {
            margin-bottom: -16px !important; 
        }
    </style>
""", unsafe_allow_html=True)
st.title("⚔️ Combate - Prototipando o Tabuleiro")

# 1. Inicializa o estado do jogo na memória do Streamlit
if "board" not in st.session_state:
    # 1. Gera os exércitos e embaralha a ordem das listas
    pecas_verdes = gerar_exercito("verde", "🟩")
    pecas_vermelhas = gerar_exercito("vermelho", "🟥")
    
    random.shuffle(pecas_verdes)
    random.shuffle(pecas_vermelhas)
    
    # 2. Cria o tabuleiro vazio
    board = [["⬜" for _ in range(10)] for _ in range(10)]
    
    # 3. Adiciona os Lagos
    for r in [4, 5]:
        for c in [2, 3, 6, 7]:
            board[r][c] = "🌊"
            
    # 4. Distribui o exército Verde (Linhas 0 a 3)
    idx = 0
    for r in range(4):
        for c in range(10):
            board[r][c] = pecas_verdes[idx]
            idx += 1
            
    # 5. Distribui o exército Vermelho (Linhas 6 a 9)
    idx = 0
    for r in range(6, 10):
        for c in range(10):
            board[r][c] = pecas_vermelhas[idx]
            idx += 1
            
    st.session_state.board = board
    st.session_state.selected_pos = None

def get_team(cell_content):
    # Retorna vazio se for água ou espaço em branco
    if cell_content in ["⬜", "🌊"]:
        return None
    # Identifica o time pela cor do emoji base
    if "🟩" in cell_content:
        return "verde"
    if "🟥" in cell_content:
        return "vermelho"
    
    return None

def gerar_exercito(cor, emoji_cor):
    # Dicionário com a Patente e a Quantidade
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
    
    # Multiplica a patente pela quantidade e adiciona à lista
    for patente, quantidade in composicao.items():
        for _ in range(quantidade):
            # Formata a string para o botão, ex: "🟩 3-Cabo"
            peca = f"{emoji_cor} {patente}"
            exercito.append(peca)
            
    return exercito

# Gerando as listas de 40 peças para cada time
pecas_verdes = gerar_exercito("verde", "🟩")
pecas_vermelhas = gerar_exercito("vermelho", "🟥")

def resolver_combate(atacante, defensor):
    # Separa o emoji do nome da peça. Ex: "🟩 3-Cabo" vira "3-Cabo"
    nome_atk = atacante.split(" ", 1)[1]
    nome_def = defensor.split(" ", 1)[1]
    
    # 1. Condição de Vitória do Jogo
    if nome_def == "Prisioneiro":
        return "vitoria_jogo"
        
    # 2. Regra da Bomba
    if nome_def == "Bomba":
        if "3-Cabo" in nome_atk:
            return "vitoria" # O Cabo desarma e avança
        else:
            return "derrota" # Qualquer outro explode e morre
            
    # 3. Regra do Empate (Patentes iguais se destroem)
    if nome_atk == nome_def:
        return "empate"
        
    # 4. Regra Especial do Espião vs Marechal
    if "1-Espiao" in nome_atk and "10-Marechal" in nome_def:
        return "vitoria"
        
    # 5. Combate Padrão (Maior número vence)
    # Extrai só o número da string. Ex: "10-Marechal" -> "10" -> int(10)
    forca_atk = int(nome_atk.split("-")[0])
    forca_def = int(nome_def.split("-")[0])
    
    if forca_atk > forca_def:
        return "vitoria"
    else:
        return "derrota"


def is_valid_move(orig_r, orig_c, target_r, target_c):
    orig_cell = st.session_state.board[orig_r][orig_c]
    
    # 0. Impede que peças imóveis ataquem
    if "Bomba" in orig_cell or "Prisioneiro" in orig_cell:
        return False
        
   
    # 1. Distância de Manhattan (Andar apenas 1 casa ortogonal)
    distance = abs(orig_r - target_r) + abs(orig_c - target_c)
    
    if distance != 1:
        return False
        
    target_cell = st.session_state.board[target_r][target_c]
    orig_cell = st.session_state.board[orig_r][orig_c]
    
    # 2. Bloqueio dos Lagos
    if target_cell == "🌊":
        return False
        
    # 3. Trava de Fogo Amigo (Nova Regra)
    orig_team = get_team(orig_cell)
    target_team = get_team(target_cell)
    
    # Se a casa de destino tem um time, e é o MESMO time da sua peça, bloqueia
    if target_team is not None and orig_team == target_team:
        return False
        
    return True

# 2. Função que lida com o clique nos botões
def handle_click(row, col):
    clicked_item = st.session_state.board[row][col]
    
    # Impede clique nos lagos
    if clicked_item == "🌊":
        return
        
    # Lógica de Origem e Destino
    if st.session_state.selected_pos is None:
        # Primeiro clique: seleciona a peça (se não for espaço vazio)
        if clicked_item != "⬜":
            st.session_state.selected_pos = (row, col)
    else:
        # Segundo clique: tenta mover a peça
        orig_r, orig_c = st.session_state.selected_pos
        
        # Se clicou no mesmo lugar, apenas cancela a seleção
        if (orig_r, orig_c) != (row, col):
            
            # CHAMA A VALIDAÇÃO AQUI
            if is_valid_move(orig_r, orig_c, row, col):
                peca_atk = st.session_state.board[orig_r][orig_c]
                peca_def = st.session_state.board[row][col]
                
                # Movimento Normal (Destino Vazio)
                if peca_def == "⬜":
                    st.session_state.board[row][col] = peca_atk
                    st.session_state.board[orig_r][orig_c] = "⬜" 
                
                # Resolução de Combate (Destino Ocupado)
                else:
                    resultado = resolver_combate(peca_atk, peca_def)
                    
                    if resultado == "vitoria":
                        # Atacante ocupa a casa
                        st.session_state.board[row][col] = peca_atk
                        st.session_state.board[orig_r][orig_c] = "⬜"
                        st.toast("Você venceu o combate! Inimigo abatido.", icon="⚔️")
                        
                    elif resultado == "derrota":
                        # Atacante morre, defensor fica no lugar
                        st.session_state.board[orig_r][orig_c] = "⬜"
                        st.toast("Sua peça foi destruída!", icon="💥")
                        
                    elif resultado == "empate":
                        # Ambos morrem
                        st.session_state.board[row][col] = "⬜"
                        st.session_state.board[orig_r][orig_c] = "⬜"
                        st.toast("Combate empatado! Ambas peças destruídas.", icon="🤝")
                        
                    elif resultado == "vitoria_jogo":
                        st.session_state.board[row][col] = peca_atk
                        st.session_state.board[orig_r][orig_c] = "⬜"
                        st.balloons() 
                        st.success("🏆 Você capturou o Prisioneiro inimigo! FIM DE JOGO!")
                        
            else:
                # Movimento inválido (distância, água ou fogo amigo)
                st.toast("Movimento inválido!", icon="🚨")
                
        # Limpa a seleção para o próximo clique
        st.session_state.selected_pos = None


# 3. Desenhando o Grid de Interface
st.write("Selecione uma peça verde ou vermelha e depois clique em um quadrado branco para mover.")

# Loop para criar as 10 linhas
for row_idx in range(10):
    # Cria 10 colunas de tamanhos iguais para a linha atual
    cols = st.columns(10) 
    
    for col_idx in range(10):
        with cols[col_idx]:
            # Recupera o que tem nesta casa
            cell_content = st.session_state.board[row_idx][col_idx]
            
            # Destaca o botão se ele for a peça selecionada
            is_selected = st.session_state.selected_pos == (row_idx, col_idx)
            button_type = "primary" if is_selected else "secondary"
            
            # Cria o botão. A chave (key) deve ser única para cada casa!
            st.button(
                label=cell_content,
                key=f"btn_{row_idx}_{col_idx}",
                on_click=handle_click,
                args=(row_idx, col_idx), # Passa as coordenadas para a função
                type=button_type,
                use_container_width=True # Faz o botão preencher a coluna inteira
            )
           
