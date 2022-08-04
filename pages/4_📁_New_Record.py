from openpyxl import Workbook
import pandas as pd
import streamlit as st
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
    return

if "user" not in st.session_state:
    st.session_state.user = False

if "dev" not in st.session_state:
    st.session_state.dev = False

# authentication
if st.session_state.user or st.session_state.dev:
    new_record()
else:
    password_manager(cursor)