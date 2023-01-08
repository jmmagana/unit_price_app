import streamlit as st
import pandas as pd
import base64
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os

st.set_page_config(layout="wide")  # this needs to be the first Streamlit command
st.title('Precios Unitarios del Bajío')

st.markdown("""
#### **¡Bienvenido!** 
#### Base de datos de Precios Unitarios de materiales de construcción del Bajío Mexicano
""")

def get_root_dir():
    script_path = os.path.dirname(os.path.realpath(__file__))
    root_dir = os.path.dirname(script_path)
    return root_dir
root_dir_path = get_root_dir()

# Carga de datos
@st.cache
def load_csv(filepath):
    df = pd.read_csv(filepath, sep=';')
    return df
source_df = load_csv(root_dir_path+'\data\data.csv')

# Sidebar
st.sidebar.header('Selección de datos')

# Sidebar - State selection
# selected_year = st.sidebar.selectbox('Año', list(reversed(range(2020,2023))))

# Sidebar - State selection
sorted_unique_state = sorted(source_df.Estado.unique())
selected_state = st.sidebar.multiselect('Estado', sorted_unique_state, sorted_unique_state)

# Sidebar - Supplier selection
sorted_unique_supplier = sorted(source_df.Proveedor.unique())
selected_supplier = st.sidebar.multiselect('Proveedor', sorted_unique_supplier, sorted_unique_supplier)

# Sidebar - Category selection
unique_category = ['Acero y Metal','Cementos y Pegazulejo','Block y Ladrillo','Maquinaria y Equipo']
selected_category = st.sidebar.multiselect('Materiales', unique_category, unique_category)

# Filtering data
df_selected = source_df[
    (source_df.Estado.isin(selected_state)) &
    (source_df.Proveedor.isin(selected_supplier)) &
    (source_df.Categoria.isin(selected_category))
    ]

st.header('Tabla de precios, materiales y proveedores')
st.write('Productos seleccionados: ' + str(df_selected.shape[0]))
st.dataframe(df_selected)

# Download selected data
# https://discuss.streamlit.io/t/how-to-download-file-in-streamlit/1806
def filedownload(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # strings <-> bytes conversions
    href = f'<a href="data:file/csv;base64,{b64}" download="unit_prices_download.csv">Descargar datos</a>'
    return href

st.markdown(filedownload(df_selected), unsafe_allow_html=True)