import streamlit as st
import time 
import random 

st.markdown("<h1 style='text-align: center;'>🎮 Game Center</h1>", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["Memory Matcher", "Rock Paper Scissors"])

st.markdown("""
<style>
    /* Game card button styling */
    .stButton > button {
        width: 120px;
        height: 60px;
        font-size: 24px !important;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 5px auto;
        padding: 0 !important;
        background-color: #d9ae84 !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(230, 126, 34, 0.2);
        background-color: #D35400 !important;
    }
    
    .stButton > button:disabled {
        background-color: #FDF2E9 !important;
        color: #E67E22 !important;
        cursor: not-allowed;
        transform: none;
        font-size: 32px !important;
    }
</style>
""", unsafe_allow_html=True)

with tab1:
    st.title("🧠 Memory Matcher")
    
    if 'game_state' not in st.session_state:
        emojis = ['🍎', '🍌', '🍇', '🍊', '🍉', '🍓']
        
        board = []
        for emoji in emojis:
            board.extend([emoji, emoji])
        
        random.shuffle(board)
        
        st.session_state.game_state = {
            'board': board,
            'flipped': [],
            'matched': [],
            'attempts': 0,
            'game_over': False,
            'last_flip_time': None
        }
    
    game = st.session_state.game_state
    current_time = time.time()
    
    if len(game['flipped']) == 2 and game['last_flip_time'] and (current_time - game['last_flip_time']) > 1:
        if not any(card in game['matched'] for card in game['flipped']):
            game['flipped'] = []
    
    cols = st.columns(4)
    for i in range(12):
        with cols[i % 4]:
            if i not in game['matched']:
                if i in game['flipped']:
                    st.button(game['board'][i], disabled=True, key=f"flipped_{i}")
                else:
                    if st.button("🔄", key=f"card_{i}"):
                        if len(game['flipped']) < 2 and i not in game['flipped']:
                            game['flipped'].append(i)
                            
                            if len(game['flipped']) == 2:
                                game['attempts'] += 1
                                first, second = game['flipped']
                                if game['board'][first] == game['board'][second]:
                                    game['matched'].extend(game['flipped'])
                                    game['flipped'] = []
                                else:
                                    game['last_flip_time'] = current_time
            else:
                st.button(game['board'][i], disabled=True, key=f"matched_{i}")
    
    st.markdown("""
    <style>
    .stats-container {
        margin-top: 20px;
        padding: 10px;
        border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    with st.container():
        st.markdown(f"""
        <div class='stats-container'>
        <h3>Game Stats</h3>
        <p>Attempts: {game['attempts']}</p>
        <p>Pairs Found: {len(game['matched'])//2} / 6</p>
        </div>
        """, unsafe_allow_html=True)
    
    if len(game['matched']) == 12:
        st.balloons()
        st.success(f"🎉 Congratulations! You found all pairs in {game['attempts']} attempts!")
        if st.button("Play Again", key="new_game"):
            del st.session_state.game_state

with tab2:
    st.title("✊ Rock Paper Scissors Showdown!")

    st.markdown("""
    <style>
    .hand-container {
        display: flex;
        justify-content: space-between;
        font-size: 100px;
        margin: 20px 0;
        transition: transform 0.3s ease;
    }
    .hand-move {
        animation: shake 0.5s;
    }
    @keyframes shake {
        0% { transform: rotate(0deg); }
        25% { transform: rotate(15deg); }
        50% { transform: rotate(-15deg); }
        75% { transform: rotate(15deg); }
        100% { transform: rotate(0deg); }
    }
    </style>
    """, unsafe_allow_html=True)

    choices = ['Rock ✊', 'Paper ✋', 'Scissors ✌️']

    player_choice = st.radio(
    "Player selection",
    choices,
    label_visibility="collapsed"
)

    if st.button("Play"):
        computer_choice = random.choice(choices)

        with st.spinner('Battling it out...'):
            time.sleep(1)

        col1, col2 = st.columns(2)

        with col1:
            st.write("### Your Choice")
            st.markdown(f"## {player_choice}")

        with col2:
            st.write("### Computer's Choice")
            st.markdown(f"## {computer_choice}")

        if player_choice == computer_choice:
            st.snow()
            st.info("### It's a tie! 🤝")
        elif (
            (player_choice == 'Rock ✊' and computer_choice == 'Scissors ✌️') or
            (player_choice == 'Paper ✋' and computer_choice == 'Rock ✊') or
            (player_choice == 'Scissors ✌️' and computer_choice == 'Paper ✋')
        ):
            st.balloons()
            st.success("### You win! 🎉🏆")
        else:
            st.error("### Computer wins! That's always OK, TRY AGAIN! 😢🤖")