import streamlit as st
import pandas as pd
import base64
import os

st.set_page_config(layout="wide")  # this needs to be the first Streamlit command

from streamlit_login_auth_ui.widgets import __login__

__login__obj = __login__(auth_token = "dk_prod_TX46GMNE9KM41JNDMJAQ5YB5S628", 
                    company_name = "BIDCSA",
                    width = 340, height = 300, 
                    logout_button_name = 'Cerrar sesión', 
                    hide_menu_bool = False, 
                    hide_footer_bool = True, 
                    lottie_url = 'https://assets9.lottiefiles.com/private_files/lf30_dzn8fp9a.json')

LOGGED_IN = __login__obj.build_login_ui()

if LOGGED_IN == True:
        
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

    # Load data
    @st.cache
    def load_csv(filepath):
        df = pd.read_csv(filepath, sep=';')
        return df
    source_df = load_csv(root_dir_path+'/data/data.csv')

    # Sidebar
    st.sidebar.header('Selección de datos')

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