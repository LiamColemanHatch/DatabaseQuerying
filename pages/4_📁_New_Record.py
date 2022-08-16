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
from st_aggrid import AgGrid, GridOptionsBuilder
from st_aggrid.shared import GridUpdateMode, DataReturnMode

# programming aid variables
degree_sign = u'\N{DEGREE SIGN}'

# configure streamlit page to wide layout, must be first streamlit call
st.set_page_config(layout="wide")

# instantiative the database connection and creating necessary object to interact with the database
cursor,cnxn = Database_Connection()

# clear form button. dict and field name and key must be the same.
def clear_entry(data_dict):
    
    for data_field in data_dict:
        data_dict[data_field] = [None]

    st.session_state.Project_Name = [None]


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

        store_meta = cursor.columns(table='dbo.Project', catalog=None, schema=None, column=None)

        # initiating data storing dict
        if "project_data" not in st.session_state:
            st.session_state.project_data = {
            'Project Name': [''],
            'Continent': [''],
            'Country': [''],
            'Study Type': [''],
            'Mine Type': [''],
            'Total Reserves': [''],
            'Ore Treatment Rate (t/a)': [''],
            'Main Process Type': [''],
            'No of HPM Vessels': [''],
            'No of Processing Years': [''],
            'No of Pre-Production Years': [''],
            'No of Closure Years': ['']
            }

        col1, col2, col3 = st.columns((10, 2, 1))

        # for each text input, check if input is blank (textbox submits empty variable any time box is cleared)
        # if text input is not empty, store in dict
        for data_type in st.session_state.project_data:
            with col2:
                new_toggle = st.radio(label='', options=['Existing', 'New'], key=data_type)
            if new_toggle == 'New':
                with col1:
                    st.write('')
                    st.write('')
                    st.write('')
                    data_input = st.text_input(label=data_type, key=data_type, value=st.session_state.project_data[data_type][0])
            else:
                with col1:
                    st.write('')
                    st.write('')
                    st.write('')
                    data_input = st.selectbox(label=data_type, options=['','sasa','dasd'], key=data_type)
            with col2:
                if st.button('Clear Field', key=data_type):
                    st.session_state.project_data[data_type] = [None]
                    del st.session_state[data_type]
                elif data_input:
                    st.session_state.project_data[data_type] = [data_input]

        # generate df to display entered data
        project_table = pd.DataFrame.from_dict(st.session_state.project_data)
        project_table = project_table.transpose()
        project_table.columns = project_table.columns.astype(str) 
        project_table = project_table.replace(np.nan, '')

        gb = GridOptionsBuilder.from_dataframe(project_table)
        for column in project_table:
            gb.configure_columns(column, header_name=column, editable=True, )

        gridOptions = gb.build()
        data = AgGrid(project_table, theme='streamlit', 
        gridOptions=gridOptions, 
        reload_data=False, 
        editable=True, 
        data_return_mode=DataReturnMode.AS_INPUT,
        update_mode=GridUpdateMode.MODEL_CHANGED)

        st.write(st.session_state)

        # AgGrid(project_table, theme='streamlit',)

        with st.sidebar:
            st.table(project_table)


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

