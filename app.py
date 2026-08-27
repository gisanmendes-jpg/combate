import streamlit as st

st.set_page_config(layout="centered")
st.markdown("""
    <style>
        /* Remove o espaço entre as colunas horizontais */
        [data-testid="column"] {
            padding: 0 !important;
            gap: 0 !important;
        }
        /* Remove o espaço vertical entre os botões */
        div.row-widget.stButton {
            margin-bottom: -15px !important;
        }
        /* Deixa os botões quadrados e maiores */
        button {
            height: 50px !important;
            font-size: 20px !important;
            border-radius: 0px !important;
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
        # Segundo clique: move a peça para o novo local
        orig_r, orig_c = st.session_state.selected_pos
        
        # Se clicou no mesmo lugar, apenas cancela a seleção
        if (orig_r, orig_c) != (row, col):
            # Move a peça
            piece = st.session_state.board[orig_r][orig_c]
            st.session_state.board[row][col] = piece
            st.session_state.board[orig_r][orig_c] = "⬜" # Esvazia origem
            
        # Limpa a seleção para o próximo turno
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
