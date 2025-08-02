import streamlit as st
import pandas as pd
import re


def compute_number_of_component_words():
    if not pd.isna(st.session_state['problem_row']['word4']):
        return 4
    elif not pd.isna(st.session_state['problem_row']['word3']):
        return 3
    elif not pd.isna(st.session_state['problem_row']['word2']):
        return 2
    else:
        return 0


def _longest_common_substring(s1, s2):
    longest = ""
    for i in range(len(s1)):
        for j in range(len(s2)):
            lcs_temp = 0
            match = ""
            while (i + lcs_temp < len(s1)) and (j + lcs_temp < len(s2)) and (s1[i + lcs_temp] == s2[j + lcs_temp]):
                match += s1[i + lcs_temp]
                lcs_temp += 1
            if len(match) > len(longest):
                longest = match
    return longest
    

def evaluate_english_guess(guess, correct_options):
    # Force lowercase and parse multiple english translation options
    guess = guess.lower()
    correct_options = correct_options.lower()
    correct_options_list = correct_options.split(';')

    # Ignore anything in parentheses in english translation and trim
    guess = re.sub(r'\s*\([^)]*\)', '', guess).strip()
    
    # Mark as correct if the longest shared substring between the guess and any correct option is:
    # > 50% in length for both guess and answer
    # > 75% in length for either guess and answer
    for correct_option in correct_options_list:
        longest_substr = _longest_common_substring(correct_option, guess)
        if len(longest_substr) > (0.75 * len(guess)) or len(longest_substr) > (0.75 * len(correct_option)):
            return True
        if len(longest_substr) > (0.5 * len(guess)) and len(longest_substr) > (0.5 * len(correct_option)):
            return True
        
    return False
    

def compute_guess_result():
    if st.session_state['gameplay_option'] == 'english':
        if st.session_state['prompt_show_chinese'] == 'Yes':
            return evaluate_english_guess(st.session_state['current_english_guess'], st.session_state['problem_row']['english'])
        else:
            return (st.session_state['combo_word_guess'] == st.session_state['problem_row']['chinese'])
    if st.session_state['gameplay_option'] == 'vocab':
        if st.session_state['prompt_show_chinese'] == 'Yes':
            return evaluate_english_guess(st.session_state['current_english_guess'], st.session_state['problem_row']['english'])
        else:
            return (st.session_state['combo_word_guess'] == st.session_state['problem_row']['chinese'])
    else:
        raise ValueError(f"Gameplay option '{st.session_state['gameplay_option']}' not yet supported")
