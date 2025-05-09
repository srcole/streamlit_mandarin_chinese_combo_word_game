import streamlit as st
import pandas as pd
import numpy as np
from utils_compute import (
    compute_number_of_component_words,
    compute_chinese_guess_field_str,
    compute_guess_result
)


# Set up session state
session_state_var_defaults = {
    'game_started': False,
    'gameplay_option': 'component_both',
    'current_index': 0,
    'n_guess': 0,
    'n_correct': 0,
    'n_streak': 0,
    'n_streak_previous': 0,
    'percent_correct': 0,
    'df': None,
    'random_state': np.random.randint(0, 100000),
    'starting_index': 0,
    'max_priority_rating': 4,
    'min_known_rating': 1,
    'page_icon': 'cn',
    'submitted_guess': False,

    'button_clicked_start_game': False,
    'button_clicked_restart_game': False,
    'button_clicked_submit': False,
    'button_clicked_next_word': False,
    'button_clicked_skip': False,
    'button_clicked_wrongly_incorrect': False,

    'combo_word_guess': '',
    'current_english_guess': '',
    'all_component_english_concat_str': '',
    'problem_row': None,
}

gameplay_options = {
    'component_both': ('[EASY] Components prompt: Chinese + English', 'Guess the Chinese word and its translation based on 2+ component words', ':cn:'),
    'component_chinese': ('[MEDIUM] Components prompt: Chinese only', 'Guess the Chinese word and its translation based on 2+ component words', ':rat:'),
    'component_english': ('[HARD] Components prompt: English only', 'Guess the Chinese word and its translation based on 2+ component words', ':cow:'),
    'chinese_prompt': ('Chinese prompt', 'Guess the English translation', ':dog2:'),
    'pinyin_prompt': ('Chinese+pinyin prompt', 'Guess the English translation', ':ram:'),
    'english_prompt': ('English prompt', 'Guess the Chinese translation', ':tiger2:'),
    'review_mode': ('Review mode', 'See vocabulary translation and root words, without guessing', ':hatched_chick:'),
}

# Populate session state with defaults
for var_name, var_default in session_state_var_defaults.items():
    if var_name not in st.session_state:
        st.session_state[var_name] = var_default

# Set basic page config
page_configs = {
    # https://gist.github.com/rxaviers/7360908 - contains list of possible icons
    'page_icon': gameplay_options[st.session_state['gameplay_option']][2],
    'page_title': "Chinese Combo-Word Game",
}


def load_data():
    if st.session_state['df'] is None:
        sheet_url = 'https://docs.google.com/spreadsheets/d/1pw9EAIvtiWenPDBFBIf7pwTh0FvIbIR0c3mY5gJwlDk/edit#gid=0'
        sheet_url = sheet_url.replace('/edit#gid=', '/export?format=csv&gid=')
        df = pd.read_csv(sheet_url)
        df = df.dropna(subset=['chinese', 'pinyin', 'english', 'word1', 'word2', 'id'])
        df['priority'] = df['priority'].fillna(4)
        df['known'] = df['known'].fillna(4)
        st.session_state['df_raw'] = df

    st.session_state['df'] = st.session_state['df_raw'][st.session_state['df_raw']['priority'] <= st.session_state['max_priority_rating']].reset_index(drop=True)
    st.session_state['df'] = st.session_state['df'][st.session_state['df']['known'] >= st.session_state['min_known_rating']].reset_index(drop=True)
    st.session_state['df'] = st.session_state['df'].sort_values('id').sample(frac=1.0, random_state=st.session_state['random_state']).reset_index(drop=True)
    st.session_state['df'] = st.session_state['df'].loc[np.roll(st.session_state['df'].index, -st.session_state['starting_index'])].reset_index(drop=True)
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
    st.session_state['random_state'] = np.random.randint(0, 100000)
    st.session_state['game_started'] = False
    st.session_state['submitted_guess'] = False
    st.session_state['page_icon'] = 'chicken'


def evaluate_guess():
    if not st.session_state['submitted_guess']:
        st.session_state['submitted_guess'] = True
        st.session_state['n_guess'] += 1
        if compute_guess_result():
            st.session_state['n_correct'] += 1
            st.session_state['n_streak'] += 1
        else:
            st.session_state['n_streak_previous'] = st.session_state['n_streak']
            st.session_state['n_streak'] = 0
            
        st.session_state['percent_correct'] = 100 * st.session_state['n_correct'] / st.session_state['n_guess']


def fix_wrongly_incorrect():
    if st.session_state['n_streak'] == 0:
        st.session_state['n_correct'] += 1
        st.session_state['percent_correct'] = 100 * st.session_state['n_correct'] / st.session_state['n_guess']
        st.session_state['n_streak'] = st.session_state['n_streak_previous'] + 1


def go_to_next_word():
    if st.session_state['submitted_guess']:
        st.session_state['current_index'] += 1
        if st.session_state['current_index'] < len(st.session_state['df']):
            st.session_state['problem_row'] = st.session_state['df'].loc[st.session_state['current_index']]
        st.session_state['current_english_guess'] = ''
        st.session_state['combo_word_guess'] = ''
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

if st.session_state['button_clicked_skip']:
    st.session_state['button_clicked_skip'] = False
    st.session_state['submitted_guess'] = True
    go_to_next_word()

if st.session_state['button_clicked_wrongly_incorrect']:
    st.session_state['button_clicked_wrongly_incorrect'] = False
    fix_wrongly_incorrect()


# Displays
def display_header():
    st.title("Chinese Combo-Word Game")

def display_not_in_game():
    st.write("Study vocabulary building upon simpler words!")
    st.write("-- Example #1: 黄 (yellow) + 油 (oil) = 黄油 (butter)")
    st.write("-- Example #2: 保安 (protect) + 危险 (danger) = 保险 (insurance)")
    st.divider()
    st.session_state['gameplay_option'] = st.radio("Select gameplay option",
        options=gameplay_options.keys(),
        format_func=lambda x: gameplay_options[x][0],
        index=0,
        captions=[g[1] for g in gameplay_options.values()],
    )
    st.button(label = 'Start game', on_click=fn_button_clicked, kwargs={'button_name': 'start_game'})

    st.divider()
    st.header('Advanced options')
    col1_advopt, col2_advopt = st.columns([0.5, 0.5])
    col1_advorder, col2_advorder = st.columns([0.5, 0.5])
    st.session_state['max_priority_rating'] = col1_advopt.number_input('Max. priority rating', min_value=1, max_value=4, value=st.session_state['max_priority_rating'])
    st.session_state['min_known_rating'] = col1_advopt.number_input('Min. known rating', min_value=1, max_value=4, value=st.session_state['min_known_rating'])
    st.session_state['random_state'] = col1_advorder.number_input('Random state', min_value=0, max_value=100000, value=st.session_state['random_state'])
    st.session_state['starting_index'] = col2_advorder.number_input('Starting index', min_value=0, max_value=100000, value=st.session_state['starting_index'])
    st.write('See full vocabulary list at [in this Google Sheet](https://docs.google.com/spreadsheets/d/1pw9EAIvtiWenPDBFBIf7pwTh0FvIbIR0c3mY5gJwlDk/edit?usp=sharing)')

    st.divider()
    st.header('Why build yet another vocab app?')
    st.write('Despite hundreds of great resources for learning Chinese vocabulary, I think this new one takes more advantage of how I best memorize vocabulary: Re-constructing the English translation by combining the semantic meanings of the individual component characters.')
    st.write("-- Example #1: 半 (half) + 岛 (island) = 半岛 (peninsula)")
    st.write("-- Example #2: 房子 (house) + 贷款 (loan) = 房贷 (mortgage)")
    st.write('If you have any questions or suggestions, or if you are willing to contribute to creating or improving vocabulary, please feel free to contact me at scott.cole0@gmail.com')
	

def display_feedback():
    if st.session_state['n_streak'] > 0:
        correctness_feedback = 'CORRECT! :cow2:'
    else:
        correctness_feedback = 'WRONG! :bomb:'
    st.write(f"{correctness_feedback}")


def display_game_over():
    st.write("No words remaining")
    if st.session_state['gameplay_option'] != 'review_mode':
        st.write(f"Final score: {st.session_state['percent_correct']:.1f}% ({st.session_state['n_correct']}/{st.session_state['n_guess']})")
        st.write(f"Final streak: {st.session_state['n_streak']}")
    st.button(label = 'Back to home', on_click=fn_button_clicked, kwargs={'button_name': 'restart_game'})


def display_full_vocab():
    n_component_words = compute_number_of_component_words()
    st.write(f"Combo-word: {st.session_state['problem_row']['chinese']} ({st.session_state['problem_row']['pinyin']}) - {st.session_state['problem_row']['english']}")
    cols_prompt_words = st.columns(n_component_words)
    for component_word_idx in range(n_component_words):
        component_prompt_str = f"Word {component_word_idx+1}: {st.session_state['problem_row'][f'word{component_word_idx+1}']} ({st.session_state['problem_row'][f'word{component_word_idx+1}_english']})"
        cols_prompt_words[component_word_idx].write(component_prompt_str)


def display_review_mode():
    st.write(f"Vocabulary # {st.session_state['current_index'] + 1} / {len(st.session_state['df'])}")
    display_full_vocab()
    st.button(label = 'Next word', on_click=fn_button_clicked, kwargs={'button_name': 'next_word'})
    st.button(label = 'Back to home', on_click=fn_button_clicked, kwargs={'button_name': 'restart_game'})
    st.session_state['submitted_guess'] = True


def display_prompt():
    # Compute the components
    n_component_words = compute_number_of_component_words()
    cols_prompt_words = st.columns(n_component_words)
    all_components_english = []
    all_components_chinese = []
    for component_word_idx in range(n_component_words):
        all_components_english.append(st.session_state['problem_row'][f'word{component_word_idx+1}_english'])
        all_components_chinese.append(st.session_state['problem_row'][f'word{component_word_idx+1}'])
    st.session_state['all_component_english_concat_str'] = '(' + ' + '.join(all_components_english) + ')'
    
    if st.session_state['gameplay_option'] in ['component_both', 'component_chinese', 'component_english']:
        # If in component mode, give each component and prompt for a definition guess
        for component_word_idx in range(n_component_words):
            component_prompt_str = f"Word {component_word_idx+1}: {st.session_state['problem_row'][f'word{component_word_idx+1}']} ({st.session_state['problem_row'][f'word{component_word_idx+1}_english']})"
            cols_prompt_words[component_word_idx].write(component_prompt_str)
        st.session_state['all_component_english_concat_str'] = '(' + ' + '.join(all_components_english) + ')'

        col1_guess, col2_guess = st.columns([0.5, 0.5])
        col1_guess.text_input(label=compute_chinese_guess_field_str(''.join(all_components_chinese)), max_chars=20, value='', key='combo_word_guess', autocomplete='off')
        col2_guess.text_input(label='English definition', max_chars=20, value='', key='current_english_guess', autocomplete='off')

    elif st.session_state['gameplay_option'] in ['chinese_prompt', 'pinyin_prompt', 'english_prompt']:
        # If not in component mode, just prompt for a direct translation
        if st.session_state['gameplay_option'] == 'chinese_prompt':
            st.text_input(label=f"English translation of {st.session_state['problem_row'][f'chinese']}", max_chars=20, value='', key='current_english_guess', autocomplete='off')
        elif st.session_state['gameplay_option'] == 'pinyin_prompt':
            st.text_input(label=f"English translation of {st.session_state['problem_row'][f'chinese']} ({st.session_state['problem_row'][f'pinyin']})", max_chars=20, value='', key='current_english_guess', autocomplete='off')
        else:
            st.text_input(label=f"Chinese translation of '{st.session_state['problem_row'][f'english']}'", max_chars=20, value='', key='combo_word_guess', autocomplete='off')
        st.session_state['all_component_english_concat_str'] = '(' + ' + '.join(all_components_english) + ')'

    # Prompt to submit or skip
    col1_submit, col2_submit = st.columns([0.5, 0.5])
    col1_submit.button(label = 'Submit', on_click=fn_button_clicked, kwargs={'button_name': 'submit'})
    col2_submit.button(label = 'Skip', on_click=fn_button_clicked, kwargs={'button_name': 'skip'})


def display_feedback_and_continue():
    display_feedback()
    display_full_vocab()
    col1_feedback, col2_feedback = st.columns([0.5, 0.5])
    col1_feedback.button(label = 'Next word', on_click=fn_button_clicked, kwargs={'button_name': 'next_word'})
    col2_feedback.button(label = "Wrongly marked as 'incorrect'", on_click=fn_button_clicked, kwargs={'button_name': 'wrongly_incorrect'})


def display_score_and_restart():
    st.header("Score")
    col1_score, col2_score, col3_score = st.columns([0.6, 0.2, 0.2])
    col1_score.write(f"% correct: {st.session_state['percent_correct']:.1f}% ({st.session_state['n_correct']}/{st.session_state['n_guess']})")
    col2_score.write(f"Streak: {st.session_state['n_streak']}")
    col3_score.button(label = 'Restart game', on_click=fn_button_clicked, kwargs={'button_name': 'restart_game'})

# Set up the page depending on gameplay state
st.set_page_config(**page_configs)
display_header()
if not st.session_state['game_started']:
    display_not_in_game()
elif st.session_state['current_index'] >= len(st.session_state['df']):
    display_game_over()
elif st.session_state['gameplay_option'] == 'review_mode':
    display_review_mode()
else:
    st.write(f"Vocabulary # {st.session_state['current_index'] + 1} / {len(st.session_state['df'])}")
    if st.session_state['submitted_guess']:
        display_feedback_and_continue()
    else:
        display_prompt()
    display_score_and_restart()
