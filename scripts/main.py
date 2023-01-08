import streamlit as st
import pandas as pd
import base64
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

st.title('Precios Unitarios del Bajio')

st.markdown("""
#### **¡Bienvenido!** 
#### Base de datos de Precios Unitarios de materiales de construcción del Bajio Mexicano
""")

st.sidebar.header('Selección de datos')
selected_year = st.sidebar.selectbox('Año', list(reversed(range(2020,2023))))

# Carga de datos
@st.cache
def load_data(year):
    url = "https://www.basketball-reference.com/leagues/NBA_" + str(year) + "_per_game.html"
    html = pd.read_html(url, header = 0)
    df = html[0]
    raw = df.drop(df[df.Age == 'Age'].index) # Deletes repeating headers in content
    raw = raw.fillna(0)
    playerstats = raw.drop(['Rk'], axis=1)
    return playerstats
playerstats = load_data(selected_year)

# Sidebar - State selection
sorted_unique_state = ['Guanajuato','Michoacan','Queretaro'] #sorted(playerstats.Tm.unique())
selected_state = st.sidebar.multiselect('Seleccione el Estado', sorted_unique_state, sorted_unique_state)

# Sidebar - Category selection
unique_category = ['Acero y Metal','Cementos y Pegazulejo','Block y Ladrillo','Plomería']
selected_category = st.sidebar.multiselect('Materiales', unique_category, unique_category)

# Filtering data
df_selected_team = playerstats[(playerstats.Tm.isin(selected_state)) & (playerstats.Pos.isin(selected_category))]

st.header('Tabla de precios y materiales')
st.write('Data Dimension: ' + str(df_selected_team.shape[0]) + ' rows and ' + str(df_selected_team.shape[1]) + ' columns.')
st.dataframe(df_selected_team)

# Download NBA player stats data
# https://discuss.streamlit.io/t/how-to-download-file-in-streamlit/1806
def filedownload(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # strings <-> bytes conversions
    href = f'<a href="data:file/csv;base64,{b64}" download="playerstats.csv">Descargar datos</a>'
    return href

st.markdown(filedownload(df_selected_team), unsafe_allow_html=True)