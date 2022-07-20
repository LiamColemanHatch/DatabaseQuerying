from ast import If
from asyncio.windows_events import NULL
from pickle import TRUE
from turtle import color
from click import pass_context
from flask import Blueprint
import pyodbc
import sqlalchemy
import pandas as pd
import streamlit as st
import numpy as np
from streamlit import plotly_chart
from login import password_manager

st.set_page_config(
        page_title="Settings",
        layout='wide'
)

DRIVER = '{ODBC Driver 17 for SQL Server}'
SERVER_NAME = 'CACSQLDEV03'
DATABASE_NAME = 'ProjectDetailDatabase'

# DEFINE CONNECTION 

CONNECTION_STRING = """
 Driver={driver};
Server={server};
Database={database};
Trusted_Connection=yes;
    """.format(
        driver=DRIVER,
        server=SERVER_NAME,
        database=DATABASE_NAME
    )

    # misc variables
degree_sign = u'\N{DEGREE SIGN}'

hide_dataframe_row_index = """
                <style>
                .row_heading.level0 {display:none}
                .blank {display:none}
                </style>
                """

# connect to DB and create cursor

cnxn: pyodbc.Connection = pyodbc.connect(CONNECTION_STRING)

cursor: pyodbc.Cursor = cnxn.cursor()


sql_pullpass = """
SELECT [Location], [Password]
  FROM [ProjectDetailDatabase].[dbo].[Passbook]

"""

sql_newuserpass = """
USE [ProjectDetailDatabase]

UPDATE [dbo].[Passbook]
   SET
   [Password] = ?
 WHERE [Location] = 'HPM Process Database Viewer'

"""

rdevpass = cursor.execute(sql_pullpass)

columns = ['Location', 'Pass']

passdf = pd.DataFrame.from_records(
    data=rdevpass,
    columns=columns
)

devpass = passdf.loc[passdf['Location'] == 'HPM Process Database Viewer Developer']['Pass'].item()
userpass = passdf.loc[passdf['Location'] == 'HPM Process Database Viewer']['Pass'].item()

def main2():

    st.write('### New Password')

    if 'submit_button' not in st.session_state:
        st.session_state.submit_button = False

    if 'newpass' not in st.session_state:
        st.session_state.newpass = False

    if 'confirmpass' not in st.session_state:
        st.session_state.confirmpass = True  

    st.session_state.newpass = st.text_input("New Password")
    st.session_state.confirmpass = st.text_input("Confirm Password")  

    if st.button('Submit'):
        if st.session_state.newpass == st.session_state.confirmpass and  len(st.session_state.newpass) >= 8: 
            cursor.execute(sql_newuserpass, st.session_state.newpass)
            cnxn.commit()
            st.success('Password Succesfully Changed!')
        elif st.session_state.newpass != st.session_state.confirmpass:
            st.info('Passwords do not match.')
        elif len(st.session_state.newpass) < 8:
            st.info('Password must be greater than 8 characters long.')
        

    cursor.close()
    cnxn.close()

# Authentication
if st.session_state.dev:
    main2()
else:
    st.write("#### Please enter the Dev Password to access the settings page")
    password_manager(cursor)
