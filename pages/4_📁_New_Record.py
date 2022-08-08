from openpyxl import Workbook
import pandas as pd
import streamlit as st
from streamlit_option_menu import option_menu
import numpy as np
from datetime import date
import xlsxwriter
from io import BytesIO
from Config import Database_Connection
from Config import df_print_noindex
from login import password_manager
from UliPlot.XLSX import auto_adjust_xlsx_column_width

# programming aid variables
degree_sign = u'\N{DEGREE SIGN}'

# configure streamlit page to wide layout, must be first streamlit call
st.set_page_config(layout="wide")

# instantiative the database connection and creating necessary object to interact with the database
cursor,cnxn = Database_Connection()

def new_record():
    choose = option_menu("Data Class", ["Project", "Company", "Financials", "Metals", "Autoclave", "Other Circuits", "Tailings", "Oxygen Plant", "Submit Record"],
                            menu_icon="grid-fill", default_index=0, orientation='horizontal',
                            styles={
            "container": {"padding": "5!important", "color": "grey"},
            "icon": {"font-size": "12px", "color": "orange"}, 
            "nav-link": {"font-size": "13px", "text-align": "left", "margin":"0px", "--hover-color": "#000000", "color": "orange"},
            "nav-link-selected": {"background-color": "#ffffff"},
                            }
    )

    # Project Data Input
    if choose == "Project":

        proj_columns = ['Project Name', 'Continent', 'Country', 'Study Type', 'Mine Type', 'Total Reserves', 'Ore Treatment Rate (t/a)', 'Main Process Type', 'No of HPM Vessels'
            'No of Processing Years', 'No of Pre-Production Years', 'No of Closure Years', 'Date of Information']

        proj_data = [None, None, None, None, None, None, None, None, None, None, None, None, None]

        project_table = pd.DataFrame.from_records(columns=proj_columns, data=proj_data)

        # initiating data storing variable
        if "project_data" not in st.session_state:
            st.session_state.project_data = {}

        col1, col2, col3 = st.columns((3, 1, 1))

        with col1:
            proj_name = st.text_input(label='Project Name')
        
        if proj_name:
            st.session_state.project_data['Project_Name'] = proj_name

        st.markdown(st.session_state.project_data['Project_Name'])
        st._legacy_dataframe(project_table)


    if choose == "Company":

        st.write(st.session_state.project_data['Project_Name'])
        

if "user" not in st.session_state:
    st.session_state.user = False

if "dev" not in st.session_state:
    st.session_state.dev = False

# authentication
if st.session_state.user or st.session_state.dev:
    new_record()
else:
    password_manager(cursor)