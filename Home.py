from ast import If
from asyncio.windows_events import NULL
from pickle import TRUE
from turtle import color
from flask import Blueprint
import pyodbc
import sqlalchemy
import pandas as pd
import streamlit as st
import numpy as np
from streamlit import plotly_chart
from Config import Database_Connection
from login import password_manager

cursor,cnxn = Database_Connection()

st.set_page_config(
        page_title="Home",
        page_icon="📊",
        layout='wide'
)

def main():


    st.write("# Welcome to The HPM Process Database Viewer")

    st.sidebar.success("Select a tool above.")

    st.markdown(f'''
    <style>
        section[data-testid="stSidebar"] .css-ng1t4o {{width: 50rem;}}
        section[data-testid="stSidebar"] .css-1d391kg {{width: 50rem;}}
    </style>
    ''',unsafe_allow_html=True)

    st.write(
        """
        This web app uses data pulled from the access database which has been migrated to Hatch database servers for greater reliability
        and data security.

        For more querying tools, use the Access front end database executable found here:
        \\\idcdata07 ->Projects -> ATG -> Process -> 3 Project Reference -> 1. Plant Benchmarking Database -> ProjectDetailDatabase_fe_master.accdb
        """, unsafe_allow_html=True
    )

#instantiating the user and dev session states
if "user" not in st.session_state:
    st.session_state.user = False

if "dev" not in st.session_state:
    st.session_state.dev = False

# Authentication
if st.session_state.user or st.session_state.dev:
    main()
else:
    password_manager(cursor)

