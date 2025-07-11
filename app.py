import streamlit as st
import numpy as np
from utils_compute import (
    compute_number_of_component_words,
    compute_guess_result
)
from utils_load_data import (
    load_google_sheet,
    compute_shared_character_df,
    compute_shared_character_options,
    filter_raw_data
)


# Set up session state
session_state_var_defaults = {
    'game_started': False,
    'gameplay_option': 'easy',
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
    'max_quality_rating': 1,
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
    'problem_row': None,
}

gameplay_options = {
    'easy': ('EASY', 'Guess the English translation given component definitions', ':cn:'),
    'medium': ('MEDIUM', 'Guess the English translation without hints', ':ram:'),
    'hard': ('HARD', 'Guess the Chinese translation', ':cow:'),
    'review_mode': ('REVIEW', 'See vocabulary translation and component words, without guessing', ':hatched_chick:'),
    'review_shared': ('REVIEW SHARED CHARACTERS', 'See lists of words that all share a single character', ':hatched_chick:'),
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


def game_start_reset_session_state_vars():
    # Reset variables to indicate the start of a new game
    st.session_state['game_started'] = True
    st.session_state['current_index'] = 0
    st.session_state['n_guess'] = 0
    st.session_state['n_correct'] = 0
    st.session_state['percent_correct'] = 0
    st.session_state['n_streak'] = 0
    st.session_state['problem_row'] = st.session_state['df'].loc[st.session_state['current_index']]
    st.session_state['page_icon'] = 'panda_face'


def load_data():
    if st.session_state['df'] is None:
        st.session_state['df_raw'] = load_google_sheet()
        st.session_state['df_shared_char'] = compute_shared_character_df(st.session_state['df_raw'])
        st.session_state['df_shared_char_options'] = compute_shared_character_options(st.session_state['df_shared_char'])
    st.session_state['df'] = filter_raw_data(st.session_state['df_raw'])
    game_start_reset_session_state_vars()


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
    st.write("-- Example #1: 黄油 (butter) = 黄 (yellow) + 油 (oil)")
    st.write("-- Example #2: 保险 (insurance) = 保安 (protect) + 危险 (danger)")
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
    col1_advopt, col2_advopt, col3_advopt = st.columns([0.33, 0.33, 0.34])
    col1_advorder, col2_advorder = st.columns([0.5, 0.5])
    st.session_state['max_priority_rating'] = col1_advopt.number_input('Max. priority rating', min_value=1, max_value=4, value=st.session_state['max_priority_rating'])
    st.session_state['min_known_rating'] = col2_advopt.number_input('Min. known rating', min_value=1, max_value=4, value=st.session_state['min_known_rating'])
    st.session_state['max_quality_rating'] = col3_advopt.number_input('Max. quality rating', min_value=1, max_value=4, value=st.session_state['max_quality_rating'])
    st.session_state['random_state'] = col1_advorder.number_input('Random state', min_value=0, max_value=100000, value=st.session_state['random_state'])
    st.session_state['starting_index'] = col2_advorder.number_input('Starting index', min_value=0, max_value=100000, value=st.session_state['starting_index'])
    st.write('See full vocabulary list at [in this Google Sheet](https://docs.google.com/spreadsheets/d/1pw9EAIvtiWenPDBFBIf7pwTh0FvIbIR0c3mY5gJwlDk/edit?usp=sharing)')

    st.divider()
    st.header('Why build yet another vocab app?')
    st.write('Despite hundreds of great resources for learning Chinese vocabulary, I think this new one takes more advantage of how I best memorize vocabulary: Re-constructing the English translation by combining the semantic meanings of the individual component characters.')
    st.write("-- Example #1: 半岛 (peninsula) = 半 (half) + 岛 (island)")
    st.write("-- Example #2: 房贷 (mortgage) = 房子 (house) + 贷款 (loan)")
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
    n_examples_show = 5
    n_component_words = compute_number_of_component_words()
    st.write(f"Combo-word: [{st.session_state['problem_row']['chinese']}](https://www.dong-chinese.com/dictionary/search/{st.session_state['problem_row']['chinese']}) ({st.session_state['problem_row']['pinyin']}) - {st.session_state['problem_row']['english']}")
    cols_prompt_words = st.columns(n_component_words)
    for component_word_idx in range(n_component_words):
        component_prompt_str = f"Word {component_word_idx+1}: [{st.session_state['problem_row'][f'word{component_word_idx+1}']}](https://www.dong-chinese.com/dictionary/search/{st.session_state['problem_row'][f'word{component_word_idx+1}']}) ({st.session_state['problem_row'][f'word{component_word_idx+1}_english']})"
        cols_prompt_words[component_word_idx].write(component_prompt_str)

    cols_example_words = st.columns(n_component_words)
    for component_word_idx in range(n_component_words):
        # get first character of overlap between component word and combo word
        shared_char = st.session_state['problem_row'][f'word{component_word_idx+1}']
        if len(shared_char) > 1:
            not_found_shared_char, combo_word_idx, component_word_char_idx = True, 0, 0
            while not_found_shared_char:
                if st.session_state['problem_row']['chinese'][combo_word_idx] == shared_char[component_word_char_idx]:
                    shared_char = shared_char[component_word_char_idx]
                    not_found_shared_char = False
                else:
                    combo_word_idx += 1
                    if combo_word_idx >= len(st.session_state['problem_row']['chinese']):
                        combo_word_idx = 0
                        component_word_char_idx += 1

        df_this_char_other_words = st.session_state['df_shared_char'][st.session_state['df_shared_char']['shared_char'] == shared_char].reset_index(drop=True)
        df_this_char_other_words = df_this_char_other_words[~df_this_char_other_words['chinese'].isin([shared_char, st.session_state['problem_row'][f'word{component_word_idx+1}'], st.session_state['problem_row']['chinese']])].reset_index(drop=True)
        df_this_char_other_words = df_this_char_other_words[df_this_char_other_words['pinyin'] != ''].reset_index(drop=True)
        component_prompt_str = f"{df_this_char_other_words.shape[0]} other words with '{shared_char}':"
        for i_row, row in df_this_char_other_words.iterrows():
            if i_row >= n_examples_show:
                break
            component_prompt_str += f"\n\n{row['chinese']} ({row['pinyin']}) - {row['english']}"
        cols_example_words[component_word_idx].write(component_prompt_str)


def display_review_mode():
    st.write(f"Vocabulary # {st.session_state['current_index'] + 1} / {len(st.session_state['df'])}")
    display_full_vocab()
    st.button(label = 'Next word', on_click=fn_button_clicked, kwargs={'button_name': 'next_word'})
    st.button(label = 'Back to home', on_click=fn_button_clicked, kwargs={'button_name': 'restart_game'})
    st.session_state['submitted_guess'] = True


def display_review_shared():
    # How to select character?
    st.session_state['shared_char_select_type'] = st.radio("How to select character?",
        options=['Select character from list', 'Enter character'],
        index=0,
    )

    # Include phrases?
    st.session_state['shared_char_select_phrase_inclusion'] = st.radio("What should be included?",
        options=['Words only', 'Include phrases'],
        index=0,
    )
    if st.session_state['shared_char_select_phrase_inclusion'] == 'Words only':
        st.session_state['df_shared_char_use'] = st.session_state['df_shared_char'][st.session_state['df_shared_char']['type'].isin(['phrase', 'phrase_save']) == False].reset_index(drop=True)
    else:
        st.session_state['df_shared_char_use'] = st.session_state['df_shared_char'].copy()

    # Select the character
    if st.session_state['shared_char_select_type'] == 'Select character from list':
        selection_options = st.session_state['df_shared_char_options'][st.session_state['df_shared_char_options']['n_words'] >= 10]
        st.session_state['shared_char_selected'] = st.selectbox(
            label='Select character',
            options=selection_options,
            # format_func=lambda x: gameplay_options[x][0],
            index=0
        )
    else:
        st.session_state['shared_char_selected'] = st.text_input(
            label='Enter character',
            value='牛'
        )

    # Compute words with that character and display them
    st.session_state['shared_char_selected_words'] = st.session_state['df_shared_char_use'][st.session_state['df_shared_char_use']['shared_char'] == st.session_state['shared_char_selected']]
    st.write(f'{len(st.session_state['shared_char_selected_words'])} words contain {st.session_state['shared_char_selected']}')
    for _, row in st.session_state['shared_char_selected_words'].iterrows():
        st.write(f"{row['chinese']}: {row['english']}")

    # Return to home and housekeeping
    st.button(label = 'Back to home', on_click=fn_button_clicked, kwargs={'button_name': 'restart_game'})
    st.session_state['submitted_guess'] = True


def display_prompt():
    # Compute the components
    n_component_words = compute_number_of_component_words()
    all_components_english = []
    all_components_chinese = []
    for component_word_idx in range(n_component_words):
        all_components_english.append(st.session_state['problem_row'][f'word{component_word_idx+1}_english'])
        all_components_chinese.append(st.session_state['problem_row'][f'word{component_word_idx+1}'])

    # Prompt for the guess
    if st.session_state['gameplay_option'] in ['easy', 'medium']:
        st.text_input(label=f"English translation of {st.session_state['problem_row'][f'chinese']} ({st.session_state['problem_row'][f'pinyin']})", max_chars=20, value='', key='current_english_guess', autocomplete='off')
    else:
        st.text_input(label=f"Chinese translation of '{st.session_state['problem_row'][f'english']}'", max_chars=20, value='', key='combo_word_guess', autocomplete='off')

    # If in component mode, give each component
    if st.session_state['gameplay_option'] == 'easy':
        cols_prompt_words = st.columns(n_component_words)
        for component_word_idx in range(n_component_words):
            component_prompt_str = f"Word {component_word_idx+1}: {st.session_state['problem_row'][f'word{component_word_idx+1}']} ({st.session_state['problem_row'][f'word{component_word_idx+1}_english']})"
            cols_prompt_words[component_word_idx].write(component_prompt_str)

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
elif st.session_state['gameplay_option'] == 'review_shared':
    display_review_shared()
else:
    st.write(f"Vocabulary # {st.session_state['current_index'] + 1} / {len(st.session_state['df'])}")
    if st.session_state['submitted_guess']:
        display_feedback_and_continue()
    else:
        display_prompt()
    display_score_and_restart()
