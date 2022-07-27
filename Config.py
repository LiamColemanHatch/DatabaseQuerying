import pyodbc
import streamlit as st
import pandas as pd

def Database_Connection():
    """
        Author: Ali Kufaishi
        Date: 7/20/2022
        Revision: 0.0.1
        Reviewer: Liam Coleman
        Review Date: 7/20/2022
        Intent: Establish connection with database and create database interacting objects
        Inputs: 
            N/A TOADD
        Returns:
            output_csv - csv object - output dataframe converted to csv
        Exceptions:
            N/A
    """
    # to run the localhost: directory -> python -m streamlit run "your_program".py 
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

    # connect to DB and create cursor
    cnxn: pyodbc.Connection = pyodbc.connect(CONNECTION_STRING)
    cursor: pyodbc.Cursor = cnxn.cursor()
    return cursor,cnxn

def df_print_noindex(df, type):
    """
        Author: Ali Kufaishi
        Date: 7/25/2022
        Revision: 0.0.1
        Reviewer: N/A
        Review Date: N/A
        Intent: Display dataframe in streamlit in form of table or streamlit dataframe
        Inputs: 
            df - Pandas Dataframe - output dataframe,
            type - either 'Table' or 'Dataframe'
        Returns:
            N/A
        Exceptions:
            N/A
    """
    hide_table_row_index = """
            <style>
            .row_heading.level0 {display:none}
            .blank {display:none}
            </style>
            """
    st.markdown(hide_table_row_index, unsafe_allow_html=True)
    if type == 'Table':
        st.table(df)
    if type == 'Dataframe':
        st.markdown(hide_table_row_index, unsafe_allow_html=True)
        st._legacy_dataframe(df, width=50000, height=700)

    
