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
from streamlit_tags import st_tags

# programming aid variables
degree_sign = u'\N{DEGREE SIGN}'

# configure streamlit page to wide layout, must be first streamlit call
st.set_page_config(layout="wide")

# instantiative the database connection and creating necessary object to interact with the database
cursor,cnxn = Database_Connection()

# clear form button. dict and field name and key must be the same.
def clear_entry(data_field, data_dict):
    st.session_state[data_field] = ''
    data_dict[data_field] = [None]


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

        # initiating data storing dict
        if "project_data" not in st.session_state:
            st.session_state.project_data = {
            'Project Name': [None],
            'Continent': [None],
            'Country': [None],
            'Study Type': [None],
            'Mine Type': [None],
            'Total Reserves': [None],
            'Ore Treatment Rate (t/a)': [None],
            'Main Process Type': [None],
            'No of HPM Vessels': [None],
            'No of Processing Years': [None],
            'No of Pre-Production Years': [None],
            'No of Closure Years': [None]
            }

        col1, col2 = st.columns((1, 1))

        # for each text input, check if input is blank (textbox submits empty variable any time box is cleared)
        # if text input is not empty, store in dict
        with st.form('Project Data'):
            for data_type in st.session_state.project_data:
                with col1:
                    data_input = st.text_input(label=data_type, key=data_type)
                if data_input:
                    st.session_state.project_data[data_type] = [data_input]

        keywords = st_tags(
            label='# Enter Keywords:',
            text='Press enter to add more',
            value=['Zero', 'One', 'Two'],
            suggestions=['five', 'six', 'seven', 
                        'eight', 'nine', 'three', 
                        'eleven', 'ten', 'four'],
            maxtags = 4,
            key='1'
            )

        # generate df to display entered data
        project_table = pd.DataFrame.from_dict(st.session_state.project_data)
        project_table = project_table.transpose()
        project_table = project_table.replace(np.nan, '')

        with col2:
            st.table(project_table)
            if st.button('Clear'):
                for data_field in st.session_state.project_data:
                    clear_entry(data_field, st.session_state.project_data)
                

    if choose == "Company":

        st.write(st.session_state.project_data['Project Name'])
        

if "user" not in st.session_state:
    st.session_state.user = False

if "dev" not in st.session_state:
    st.session_state.dev = False

# authentication
if st.session_state.user or st.session_state.dev:
    new_record()
else:
    password_manager(cursor)

