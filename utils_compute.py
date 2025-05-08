import streamlit as st
import pandas as pd


def compute_number_of_component_words():
    if not pd.isna(st.session_state['problem_row']['word4']):
        return 4
    elif not pd.isna(st.session_state['problem_row']['word3']):
        return 3
    else:
        return 2


def compute_component_printing_based_on_gameplay(component_word_idx):
    if st.session_state['gameplay_option'] == 'component_chinese':
        return f"Word {component_word_idx+1}: {st.session_state['problem_row'][f'word{component_word_idx+1}']}"
    elif st.session_state['gameplay_option'] == 'component_english':
        return f"Word {component_word_idx+1}: {st.session_state['problem_row'][f'word{component_word_idx+1}_english']}"
    else:
        return f"Word {component_word_idx+1}: {st.session_state['problem_row'][f'word{component_word_idx+1}']} ({st.session_state['problem_row'][f'word{component_word_idx+1}_english']})"


def compute_chinese_guess_field_str(all_component_char_concat_str):
    if st.session_state['gameplay_option'] == 'component_english':
        return 'Chinese combo word'
    else:
        return f'Chinese combo word (subset of {all_component_char_concat_str})'
    

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
    

def compute_guess_result():
    chinese_correct = (st.session_state['combo_word_guess'] == st.session_state['problem_row']['chinese'])
    english_correct = evaluate_english_guess(st.session_state['current_english_guess'], st.session_state['problem_row']['english'])
    if st.session_state['gameplay_option'] in ['component_both', 'component_chinese', 'component_english']:
        return chinese_correct and english_correct
    elif st.session_state['gameplay_option'] in ['chinese_prompt', 'pinyin_prompt']:
        return english_correct
    elif st.session_state['gameplay_option'] == 'english_prompt':
        return chinese_correct
    else:
        raise ValueError(f"Gameplay option '{st.session_state['gameplay_option']}' not yet supported")
