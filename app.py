import streamlit as st
import pandas as pd

def load_data():
    sheet_url = 'https://docs.google.com/spreadsheets/d/1pw9EAIvtiWenPDBFBIf7pwTh0FvIbIR0c3mY5gJwlDk/edit#gid=0'
    sheet_url = sheet_url.replace('/edit#gid=', '/export?format=csv&gid=')
    df_raw = pd.read_csv(sheet_url)
    return df_raw

df = load_data()

# https://gist.github.com/rxaviers/7360908 - contains list of possible icons
st.set_page_config(
    layout="wide",
    page_icon=':cn:',
    page_title="Mandarin Chinese Combo Word Game"
)

st.title("Mandarin Chinese Combo Word Game")
st.write(f"{df['english'].values[0]}_{df['english_combo'].values[0]}")
st.header("Part 1 - Define your culture & rank countries")
col1, col2, col3 = st.columns([1, 1, 3])
col1.text(df['english'].values[1])
col2.text(df['english'].values[3])
col3.text(df['english'].values[4])
# for dim_name, dim_name_full in DIM_NAMES.items():
#     dim_self[dim_name] = col1.slider(dim_name_full, 0, 100, DIM_SELF_DEFAULTS[dim_name], 5)

# # Define weights in 2nd column
# for dim_name, dim_name_full in DIM_NAMES.items():
#     dim_weights[dim_name] = col2.slider(f"{dim_name_full}, weight", 0.0, 1.0, 1.0, 0.1)

# # Bar plot
# barplot_hue_dim = col1.selectbox('Dimension for barplot color', DIM_NAMES.values(), index=0)
# df_loss = compute_similarity_score(df, dim_self, dim_weights)
# chart = col3.empty()
# fig_bar = create_bar_fig(df_loss, barplot_hue_dim)
# chart.plotly_chart(fig_bar, use_container_width=True)


# # Define 2 countries to compare in 3rd column
# st.header("Part 2 - Compare your ideal culture to 2 countries")
# col1b, col2b = st.columns([1,3])
# best_country_default = df_loss.sort_values('similarity_score', ascending=False).head(1)['country'].values[0]
# selected_country1 = col1b.selectbox('Country 1 in radar plot', all_countries, index=int(df[df['country']==best_country_default].index[0]))
# selected_country2 = col1b.selectbox('Country 2 in radar plot', all_countries, index=61)
# chart_radar = col2b.empty()