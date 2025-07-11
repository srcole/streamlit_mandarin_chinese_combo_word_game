import streamlit as st
import numpy as np
import pandas as pd
from collections import defaultdict

def compute_shared_character_df(df):
    # Create a DataFrame to hold the shared characters and their associated words
    shared_character_cols = [
        ('chinese', 'english', 'pinyin', 'type'),
        ('word1', 'word1_english'),
        ('word2', 'word2_english'),
        ('word3', 'word3_english'),
        ('word4', 'word4_english'),
    ]
    all_words_list = defaultdict(list)
    
    for _, row in df.iterrows():
        for col_tuple in shared_character_cols:
            all_words_list['chinese'].append(row[col_tuple[0]])
            all_words_list['english'].append(row[col_tuple[1]])
            if len(col_tuple) > 2:
                all_words_list['pinyin'].append(row[col_tuple[2]])
                all_words_list['type'].append(row[col_tuple[3]])
            else:
                all_words_list['pinyin'].append('')
                all_words_list['type'].append('component_word')

    # de-dup all words list
    df_all_words = pd.DataFrame(all_words_list).drop_duplicates(subset=['chinese']).reset_index(drop=True).dropna()
    
    # Compute new df, which is all characters in each word
    dict_all_shared_characters = defaultdict(list)
    for _, row in df_all_words.iterrows():
        for char in row['chinese']:
            dict_all_shared_characters['shared_char'].append(char)
            dict_all_shared_characters['chinese'].append(row['chinese'])
            dict_all_shared_characters['english'].append(row['english'])
            dict_all_shared_characters['pinyin'].append(row['pinyin'])
            dict_all_shared_characters['type'].append(row['type'])
    return pd.DataFrame(dict_all_shared_characters).drop_duplicates(subset=['shared_char', 'chinese']).reset_index(drop=True)


def compute_shared_character_options(df_shared_char):
    df_by_char = df_shared_char.groupby('shared_char').agg({
        'chinese': lambda x: ';'.join(x),
        'english': lambda x: ';'.join(x),
        'pinyin': lambda x: ';'.join(x)
    }).reset_index()
    df_by_char['n_words'] = df_by_char['chinese'].apply(lambda x: len(x.split(';')))
    return df_by_char.sort_values('n_words', ascending=False)

def load_google_sheet():
    cols_keep = [
        'id', 'chinese', 'pinyin', 'english', 'type', 'priority', 'quality', 
        'known', 'known_pinyin_prompt', 'known_english_prompt', 'phonetic', 'category1', 'category2',
        'word1', 'word1_english', 'word2', 'word2_english', 'word3', 'word3_english', 'word4', 'word4_english',
        'reverse chinese', 'date',
        ]
    types_keep = [
        'combo', 'no combo', 'two word', 'suffix', 'single char', 'abbreviation', 'prefix', 'phrase', 'phrase_save'
    ]
    sheet_url = 'https://docs.google.com/spreadsheets/d/1pw9EAIvtiWenPDBFBIf7pwTh0FvIbIR0c3mY5gJwlDk/edit#gid=0'
    sheet_url = sheet_url.replace('/edit#gid=', '/export?format=csv&gid=')
    df = pd.read_csv(sheet_url)[cols_keep]
    df = df[df['type'].isin(types_keep)].reset_index(drop=True)
    df = df.dropna(subset=['chinese', 'pinyin', 'english', 'id'])
    df['priority'] = df['priority'].fillna(5)
    df['known'] = df['known'].fillna(5)
    df['quality'] = df['quality'].fillna(5)
    return df


def filter_raw_data(df_raw):
    df = df_raw[df_raw['priority'] <= st.session_state['max_priority_rating']].reset_index(drop=True)
    df = df[df['known'] >= st.session_state['min_known_rating']].reset_index(drop=True)
    df = df[df['quality'] <= st.session_state['max_quality_rating']].reset_index(drop=True)
    df = df.sort_values('id').sample(frac=1.0, random_state=st.session_state['random_state']).reset_index(drop=True)
    df = df.loc[np.roll(df.index, -st.session_state['starting_index'])].reset_index(drop=True)
    return df
