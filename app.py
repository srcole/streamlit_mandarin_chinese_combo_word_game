import streamlit as st
import pandas as pd
import numpy as np
from utils_compute import (
    compute_number_of_component_words,
    compute_component_printing_based_on_gameplay,
    compute_chinese_guess_field_str,
    compute_guess_result
)


# Set up session state
session_state_var_defaults = {
    'game_started': False,
    'current_index': 0,
    'n_guess': 0,
    'n_correct': 0,
    'n_streak': 0,
    'percent_correct': 0,
    'df': None,
    'random_state': np.random.randint(0, 1000),
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

gameplay_options = {
    'component_both': ('[EASY] Components prompt: Both', 'Guess the Chinese word and its translation based on 2+ component words'),
    'component_chinese': ('[MEDIUM] Components prompt: Chinese only', 'Guess the Chinese word and its translation based on 2+ component words'),
    'component_english': ('[HARD] Components prompt: English only', 'Guess the Chinese word and its translation based on 2+ component words'),
    'chinese_prompt': ('Chinese prompt', 'Guess the English translation'),
    'pinyin_prompt': ('Chinese+pinyin prompt', 'Guess the English translation'),
    'english_prompt': ('English prompt', 'Guess the Chinese translation'),
    'review_mode': ('Review mode', 'See vocabulary translation and root words, without guessing'),
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


def evaluate_guess():
    st.session_state['submitted_guess'] = True
    st.session_state['n_guess'] += 1
    if compute_guess_result():
        st.session_state['n_correct'] += 1
        st.session_state['n_streak'] += 1
    else:
        st.session_state['n_streak'] = 0
        
    st.session_state['percent_correct'] = 100 * st.session_state['n_correct'] / st.session_state['n_guess']


def go_to_next_word():
    st.session_state['current_index'] += 1
    if st.session_state['current_index'] < len(st.session_state['df']):
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
    st.title("Chinese Combo Word Game")

def display_footer():
    st.write("Github repo: https://github.com/srcole/streamlit_mandarin_chinese_combo_word_game")
    st.write("Blog post: https://srcole.github.io/datablog/")

def display_not_in_game():
    st.session_state['gameplay_option'] = st.radio("Select gameplay option",
        options=gameplay_options.keys(),
        format_func=lambda x: gameplay_options[x][0],
        index=0,
        captions=[g[1] for g in gameplay_options.values()],
    )
    st.button(label = 'Start game', on_click=fn_button_clicked, kwargs={'button_name': 'start_game'})

def display_feedback():
    if st.session_state['n_streak'] > 0:
        correct_feedback = 'CORRECT! :rabbit:'
    else:
        correct_feedback = 'WRONG! :us:'

    st.write(f"{correct_feedback} Answer: ")
    st.write(f"{st.session_state['problem_row']['chinese']} ({st.session_state['problem_row']['pinyin']}) - {st.session_state['problem_row']['english']}")


def display_prompt():
    if st.session_state['current_index'] >= len(st.session_state['df']):
        st.write("No words remaining")
        if st.session_state['gameplay_option'] != 'review_mode':
            st.write(f"Final score: {st.session_state['percent_correct']:.1f}% ({st.session_state['n_correct']}/{st.session_state['n_guess']})")
            st.write(f"Final streak: {st.session_state['n_streak']}")
        st.button(label = 'Back to home', on_click=fn_button_clicked, kwargs={'button_name': 'restart_game'})
    else:
        st.write(f"Vocabulary # {st.session_state['current_index'] + 1} / {len(st.session_state['df'])}")
        if st.session_state['gameplay_option'] in ['component_both', 'component_chinese', 'component_english']:
            n_component_words = compute_number_of_component_words()
            cols_prompt_words = st.columns(n_component_words)
            all_component_char_concat_str = ''
            for component_word_idx in range(n_component_words):
                component_prompt_str = compute_component_printing_based_on_gameplay(component_word_idx)
                cols_prompt_words[component_word_idx].write(component_prompt_str)
                all_component_char_concat_str += st.session_state['problem_row'][f'word{component_word_idx+1}']

            col1_guess, col2_guess = st.columns([0.5, 0.5])
            col1_guess.text_input(label=compute_chinese_guess_field_str(all_component_char_concat_str), max_chars=20, value='', key='combo_word_guess', autocomplete='off')
            col2_guess.text_input(label='English definition', max_chars=20, value='', key='current_english_guess', autocomplete='off')

        elif st.session_state['gameplay_option'] in ['chinese_prompt', 'pinyin_prompt', 'english_prompt']:
            if st.session_state['gameplay_option'] == 'chinese_prompt':
                st.text_input(label=f"English translation of {st.session_state['problem_row'][f'chinese']}", max_chars=20, value='', key='current_english_guess', autocomplete='off')
            elif st.session_state['gameplay_option'] == 'pinyin_prompt':
                st.text_input(label=f"English translation of {st.session_state['problem_row'][f'chinese']} ({st.session_state['problem_row'][f'pinyin']})", max_chars=20, value='', key='current_english_guess', autocomplete='off')
            else:
                st.text_input(label=f"Chinese translation of '{st.session_state['problem_row'][f'english']}'", max_chars=20, value='', key='combo_word_guess', autocomplete='off')

        if st.session_state['gameplay_option'] != 'review_mode':
            if not st.session_state['submitted_guess']:
                st.button(label = 'Submit', on_click=fn_button_clicked, kwargs={'button_name': 'submit'})

            else:
                display_feedback()
                st.button(label = 'Next word', on_click=fn_button_clicked, kwargs={'button_name': 'next_word'})

            st.header("Score")
            col1_score, col2_score, col3_score = st.columns([0.6, 0.2, 0.2])
            col1_score.write(f"% correct: {st.session_state['percent_correct']:.1f}% ({st.session_state['n_correct']}/{st.session_state['n_guess']})")
            col2_score.write(f"Streak: {st.session_state['n_streak']}")
            col3_score.button(label = 'Restart game', on_click=fn_button_clicked, kwargs={'button_name': 'restart_game'})

        if st.session_state['gameplay_option'] == 'review_mode':
            n_component_words = compute_number_of_component_words()
            cols_prompt_words = st.columns(n_component_words)
            all_component_char_concat_str = ''
            for component_word_idx in range(n_component_words):
                component_prompt_str = compute_component_printing_based_on_gameplay(component_word_idx)
                cols_prompt_words[component_word_idx].write(component_prompt_str)

            st.write(f"Combo word: {st.session_state['problem_row']['chinese']} ({st.session_state['problem_row']['pinyin']}) - {st.session_state['problem_row']['english']}")
            st.button(label = 'Next word', on_click=fn_button_clicked, kwargs={'button_name': 'next_word'})
            st.button(label = 'Back to home', on_click=fn_button_clicked, kwargs={'button_name': 'restart_game'})


# Set up the page
st.set_page_config(**page_configs)
display_header()
if not st.session_state['game_started']:
    display_not_in_game()
else:
    display_prompt()
display_footer()
