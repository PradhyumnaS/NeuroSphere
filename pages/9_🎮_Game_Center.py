import streamlit as st
import time 
import random 

tab1, tab2 = st.tabs(["Memory Matcher", "Rock Paper Scissors"])

with tab1:
    st.title("🧠 Memory Matcher")
    
    if 'game_state' not in st.session_state:
        emojis = ['🍎', '🍌', '🍇', '🍊', '🍉', '🍓', 
                    '🚗', '🚀', '🎈', '🏀', '🐶', '🐱']
        board = emojis * 2
        random.shuffle(board)
        
        st.session_state.game_state = {
            'board': board,
            'flipped': [],
            'matched': [],
            'attempts': 0,
            'game_over': False
        }
    
    game = st.session_state.game_state
    
    cols = st.columns(4)
    for i in range(12):
        with cols[i % 4]:
            if i not in game['matched']:
                if i in game['flipped']:
                    st.button(game['board'][i], disabled=True, key=f"flipped_{i}")
                else:
                    if st.button(f"Card {i+1}", key=f"card_{i}"):
                        game['flipped'].append(i)
                        
                        if len(game['flipped']) == 2:
                            game['attempts'] += 1
                            first, second = game['flipped']
                            if game['board'][first] == game['board'][second]:
                                game['matched'].extend(game['flipped'])
                            else:
                                time.sleep(1)
                            
                            game['flipped'] = []
            else:
                st.button(game['board'][i], disabled=True, key=f"matched_{i}")
    
    st.write(f"Attempts: {game['attempts']}")
    
    if len(game['matched']) == 12:
        st.balloons()
        st.success("Congratulations! You found all pairs! 🎉")
        game['game_over'] = True
    
    if game.get('game_over'):
        if st.button("New Game", key="new_game"):
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
            st.balloons()
            st.info("### It's a tie! 🤝")
        elif (
            (player_choice == 'Rock ✊' and computer_choice == 'Scissors ✌️') or
            (player_choice == 'Paper ✋' and computer_choice == 'Rock ✊') or
            (player_choice == 'Scissors ✌️' and computer_choice == 'Paper ✋')
        ):
            st.snow()
            st.success("### You win! 🎉🏆")
        else:
            st.error("### Computer wins! That's always OK, TRY AGAIN! 😢🤖")