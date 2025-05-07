import streamlit as st
import pandas as pd
import numpy as np


# Set up session state
session_state_var_defaults = {
    'game_started': False,
    'current_index': 0,
    'n_guess': 0,
    'n_correct': 0,
    'n_streak': 0,
    'percent_correct': 0,
    'df': None,
    'random_state': 0,
    'page_icon': 'cn',
    'submitted_guess': False,

    'button_clicked_start_game': False,
    'button_clicked_restart_game': False,
    'button_clicked_submit': False,
    'button_clicked_next_word': False,

    'combo_word_guess': '',
    'current_english_guess': '',
    'problem_row': None,
}

# Populate session state with defaults
for var_name, var_default in session_state_var_defaults.items():
    if var_name not in st.session_state:
        st.session_state[var_name] = var_default

# Set basic page config
page_configs = {
    # https://gist.github.com/rxaviers/7360908 - contains list of possible icons
    'page_icon': f":{st.session_state['page_icon']}:",
    'page_title': "Mandarin Chinese Combo Word Game",
}


def load_data():
    if st.session_state['df'] is None:
        sheet_url = 'https://docs.google.com/spreadsheets/d/1pw9EAIvtiWenPDBFBIf7pwTh0FvIbIR0c3mY5gJwlDk/edit#gid=0'
        sheet_url = sheet_url.replace('/edit#gid=', '/export?format=csv&gid=')
        df = pd.read_csv(sheet_url)
        df = df.dropna(subset=['chinese', 'pinyin', 'english', 'word1', 'word2'])
        st.session_state['df'] = df

    st.session_state['df'] = st.session_state['df'].sample(frac=1.0, random_state=st.session_state['random_state']).reset_index(drop=True)
    st.session_state['game_started'] = True
    st.session_state['current_index'] = 0
    st.session_state['n_guess'] = 0
    st.session_state['n_correct'] = 0
    st.session_state['percent_correct'] = 0
    st.session_state['n_streak'] = 0
    st.session_state['problem_row'] = st.session_state['df'].loc[st.session_state['current_index']]
    st.session_state['page_icon'] = 'panda_face'


def restart_game():
    # print('restart 1', session_state_var_defaults['game_started'])
    st.session_state['random_state'] = np.random.randint(0, 1000)
    st.session_state['game_started'] = False
    st.session_state['submitted_guess'] = False
    st.session_state['page_icon'] = 'chicken'
    # load_data()


def evaluate_english_guess(guess, correct_options):
    correct_options_list = correct_options.split(';')

    # Still mark as true if it's a substring of one of multiple guesses and shares more than 50% of characters
    for correct_option in correct_options_list:
        if (guess in correct_option) and (len(guess) > (0.5 * len(correct_option))):
            return True
    
    # Still mark as true if the guess is a substring of any of the options
    for correct_option in correct_options_list:
        if (correct_option in guess) and (len(correct_option) > (0.5 * len(guess))):
            return True
        
    return False


def evaluate_guess():
    st.session_state['submitted_guess'] = True
    st.session_state['n_guess'] += 1
    if (st.session_state['combo_word_guess'] == st.session_state['problem_row']['chinese']) and evaluate_english_guess(st.session_state['current_english_guess'], st.session_state['problem_row']['english']):
        st.session_state['n_correct'] += 1
        st.session_state['n_streak'] += 1
    else:
        st.session_state['n_streak'] = 0
        
    st.session_state['percent_correct'] = 100 * st.session_state['n_correct'] / st.session_state['n_guess']


def go_to_next_word():
    st.session_state['current_index'] += 1
    st.session_state['problem_row'] = st.session_state['df'].loc[st.session_state['current_index']]
    st.session_state['current_english_guess'] = ''
    st.session_state['submitted_guess'] = False


# Button clicks
def fn_button_clicked(button_name=''):
    st.session_state[f'button_clicked_{button_name}'] = True

if st.session_state['button_clicked_start_game']:
    st.session_state['button_clicked_start_game'] = False
    load_data()

if st.session_state['button_clicked_restart_game']:
    st.session_state['button_clicked_restart_game'] = False
    restart_game()

if st.session_state['button_clicked_submit']:
    st.session_state['button_clicked_submit'] = False
    evaluate_guess()

if st.session_state['button_clicked_next_word']:
    st.session_state['button_clicked_next_word'] = False
    go_to_next_word()


# Displays
def display_header():
    st.title("Mandarin Chinese Combo Word Game")
    st.write("Instructions: using the 2-4 words provided, enter a compound vocabulary word and its English definition")

def display_footer():
    st.write("Github repo: https://github.com/srcole/streamlit_mandarin_chinese_combo_word_game")
    st.write("Blog post: https://srcole.github.io/datablog/")

def display_not_in_game():
    st.button(label = 'Start game', on_click=fn_button_clicked, kwargs={'button_name': 'start_game'})

def display_feedback():
    if st.session_state['n_streak'] > 0:
        correct_feedback = 'CORRECT! :rabbit:'
    else:
        correct_feedback = 'WRONG! :us:'

    st.write(f"{correct_feedback} Answer: ")
    st.write(f"{st.session_state['problem_row']['chinese']} ({st.session_state['problem_row']['pinyin']}) - {st.session_state['problem_row']['english']}")
        

def display_prompt():
    st.header("Component words")
    if not pd.isna(st.session_state['problem_row']['word4']):
        # 4 words
        col1_prompt_word, col2_prompt_word, col3_prompt_word, col4_prompt_word = st.columns(4)
        col1_prompt_word.write(f"Word 1: {st.session_state['problem_row']['word1']}")
        col2_prompt_word.write(f"Word 2: {st.session_state['problem_row']['word2']}")
        col3_prompt_word.write(f"Word 3: {st.session_state['problem_row']['word3']}")
        col4_prompt_word.write(f"Word 4: {st.session_state['problem_row']['word4']}")
        default_value = f'{st.session_state['problem_row']['word1']}{st.session_state['problem_row']['word2']}{st.session_state['problem_row']['word3']}{st.session_state['problem_row']['word4']}'
    elif not pd.isna(st.session_state['problem_row']['word3']):
        # 3 words
        col1_prompt_word, col2_prompt_word, col3_prompt_word = st.columns(3)
        col1_prompt_word.write(f"Word 1: {st.session_state['problem_row']['word1']}")
        col2_prompt_word.write(f"Word 2: {st.session_state['problem_row']['word2']}")
        col3_prompt_word.write(f"Word 3: {st.session_state['problem_row']['word3']}")
        default_value = f'{st.session_state['problem_row']['word1']}{st.session_state['problem_row']['word2']}{st.session_state['problem_row']['word3']}'
    else:
        # 2 words
        col1_prompt_word, col2_prompt_word = st.columns(2)
        col1_prompt_word.write(f"Word 1: {st.session_state['problem_row']['word1']}")
        col2_prompt_word.write(f"Word 2: {st.session_state['problem_row']['word2']}")
        default_value = f'{st.session_state['problem_row']['word1']}{st.session_state['problem_row']['word2']}'
    
    # st.code(f'''subset of {default_value}''', language="python")
    col1_guess, col2_guess = st.columns([0.4, 0.6])
    st.session_state['combo_word_guess'] = col1_guess.text_input(label=f'Combo word (subset of {default_value})', max_chars=8)
    col2_guess.text_input(label='Definition', max_chars=20, value='', key='current_english_guess')

    if not st.session_state['submitted_guess']:
        st.button(label = 'Submit', on_click=fn_button_clicked, kwargs={'button_name': 'submit'})

    else:
        display_feedback()
        st.button(label = 'Next word', on_click=fn_button_clicked, kwargs={'button_name': 'next_word'})


def display_score():
    st.header("Score")
    col1_score, col2_score, col3_score = st.columns([0.6, 0.2, 0.2])
    col1_score.write(f"% correct: {st.session_state['percent_correct']:.1f}% ({st.session_state['n_correct']}/{st.session_state['n_guess']})")
    col2_score.write(f"Streak: {st.session_state['n_streak']}")
    col3_score.button(label = 'Restart game', on_click=fn_button_clicked, kwargs={'button_name': 'restart_game'})


# Set up the page
st.set_page_config(**page_configs)
display_header()
if not st.session_state['game_started']:
    display_not_in_game()
else:
    display_prompt()
    display_score()
display_footer()
