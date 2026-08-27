import streamlit as st

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
    # Cria uma matriz 10x10 vazia
    board = [["⬜" for _ in range(10)] for _ in range(10)]
    
    # Adicionando os Lagos Centrais (Típico do Combate)
    for r in [4, 5]:
        for c in [2, 3, 6, 7]:
            board[r][c] = "🌊"
            
    # Adicionando algumas peças de exemplo
    board[0][0] = "🟩" # Peça Jogador 1
    board[9][9] = "🟥" # Peça Jogador 2
    
    st.session_state.board = board
    st.session_state.selected_pos = None # Guarda a coordenada do primeiro clique

def is_valid_move(orig_r, orig_c, target_r, target_c):
    # 1. Distância de Manhattan
    # abs() retorna o valor absoluto (positivo) da diferença matemática
    distance = abs(orig_r - target_r) + abs(orig_c - target_c)
    
    # Se a distância for diferente de 1, significa que o jogador tentou 
    # pular casas (distância > 1), andar na diagonal (distância = 2) 
    # ou não saiu do lugar (distância = 0)
    if distance != 1:
        return False
        
    # 2. Bloqueio dos Lagos
    # Garante que a peça não caia na água
    target_cell = st.session_state.board[target_r][target_c]
    if target_cell == "🌊":
        return False
        
    # Se passou pelas regras, o movimento é válido
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
                # Executa o movimento
                piece = st.session_state.board[orig_r][orig_c]
                st.session_state.board[row][col] = piece
                st.session_state.board[orig_r][orig_c] = "⬜" 
            else:
                # Avisa o jogador
                st.toast("Movimento inválido! Ande apenas uma casa ortogonal.", icon="🚨")
                
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
           
