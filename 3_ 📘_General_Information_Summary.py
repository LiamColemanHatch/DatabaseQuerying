from asyncio.windows_events import NULL
from jmespath import search
from matplotlib.ft2font import HORIZONTAL
import streamlit as st
from streamlit_option_menu import option_menu
import streamlit.components.v1 as html
from  PIL import Image
import numpy as np
import cv2
import pandas as pd
from st_aggrid import AgGrid
import plotly.express as px
import io 
from flask import Blueprint
import pyodbc
import sqlalchemy
import pandas as pd
from streamlit import plotly_chart
from datetime import date

st.set_page_config(page_title="General Information Summary", page_icon="📘", layout='wide')

st.markdown("# General Information")
st.sidebar.header("General Information")

# define connection variables

## to run the localhost: directory -> python -m streamlit run "your_program".py 

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

sql_geninfoquery = """
SELECT DISTINCT Project.ID
    ,Project.Name AS Project
	,Project.[HPM Type] AS [Process Type]
	,Project.Country
	,Project.OreTreatmentRate AS [Ore Treatment Rate (t/a)]
	,Project.[No of Processing Years] AS [Years Operating]
	,[PayableMetals].Name AS [Payable Metal]
	,Project.StudyType
	,Autoclave.NumberofAutoclaveTrainsofThisType AS [# of Autoclave Trains]
	,Company.CompanyName AS [Company]
FROM (ProjectDetailDatabase.dbo.Company
	INNER JOIN ((((ProjectDetailDatabase.dbo.Project
	LEFT JOIN ProjectDetailDatabase.dbo.Autoclave ON Project.ID = Autoclave.[ID(Project)])
	LEFT JOIN ProjectDetailDatabase.dbo.MetalRecovery ON Project.ID = MetalRecovery.[ID(Projects)])
	INNER JOIN (ProjectDetailDatabase.dbo.PayableMetals
	INNER JOIN ProjectDetailDatabase.dbo.ProjectPayableMetals ON PayableMetals.ID = ProjectPayableMetals.[ID(Products)]) ON Project.ID = ProjectPayableMetals.[ID(Projects)])
	INNER JOIN ProjectDetailDatabase.dbo.ProjectCompany ON Project.ID = ProjectCompany.[ID(Project)]) ON Company.ID = ProjectCompany.[ID(Company)])

"""

geninforecords = cursor.execute(sql_geninfoquery).fetchall()
# define record column names

geninfocolumns = [column[0] for column in cursor.description]

# dump records into a dataframe

project_dump = pd.DataFrame.from_records(
    data=geninforecords,
    columns=geninfocolumns,
)

# set df index to project index

#project_dump.set_index(['ID'], inplace=True)

# removing decimals

project_dump = project_dump.fillna({'Years Operating':0})
project_dump = project_dump.astype({'Years Operating': int})

project_dump = project_dump.fillna({'Ore Treatment Rate (t/a)':0})
project_dump = project_dump.astype({'Ore Treatment Rate (t/a)': int})

project_dump = project_dump.fillna({'# of Autoclave Trains':0})
project_dump = project_dump.astype({'# of Autoclave Trains': int})

# adding comma separators for thousands

project_dump.loc[:, "Ore Treatment Rate (t/a)"] = project_dump["Ore Treatment Rate (t/a)"].map('{:,.0f}'.format)

# final formatting

project_dump = project_dump.replace(0,  '')
project_dump = project_dump.fillna('')
project_dump = project_dump.astype(str)

# record aggregation

project_dump = project_dump.groupby(['ID']).agg(lambda x: ' , '.join(list(set(list(x)))))
project_dump = project_dump.sort_values(['ID'], ascending=True, ignore_index=True)
project_dump = project_dump.sort_index()


# defining functions for cycling through records. uses session state values to track current current

if "row" not in st.session_state:
    st.session_state.row = 0

def next_row():
    st.session_state.row += 1

def prev_row():
    st.session_state.row -= 1

def reset_ss():
	st.session_state.row = 0

def gensearch(searchitem, source):	
	record = source.loc[source['Project'] == searchitem]
	
	return record

# selection of record from dataset

searchproj = st.selectbox('Select Project:', project_dump['Project'].unique())

searchrecord = gensearch(searchproj, project_dump)

col1, col2, col3, col4, col5 = st.columns([1, 1, 1, 1, 1])

# navigation buttons

if st.session_state.row > len(searchrecord.index)-1:
	st.session_state.row=0

if st.session_state.row < len(searchrecord.index)-1:
    col5.button("Next Record", on_click=next_row)
else:
    col5.write("") 

if st.session_state.row > 0:
    col1.button("Previous Record", on_click=prev_row)
else:
    col1.write("") 

with col3:
	st.write(str(st.session_state.row)+'/'+str(searchrecord.index-1))

# if session_state value is greater than the length of the record, reset to 0

st.write(st.session_state.row)
st.write(len(searchrecord.index)-1)

st.write('check')

if st.session_state.row > len(searchrecord.index)-1:
	st.session_state.row=0
	st.write(st.session_state.row,len(searchrecord.index)-1 )
else:
	
	st.write(st.session_state.row,len(searchrecord.index)-1 )

st.write(searchrecord)


if st.session_state.row > len(searchrecord.index)-1:
	st.session_state.row=0
	searchrecord = searchrecord.iloc[st.session_state.row]
else:
	
	searchrecord = searchrecord.iloc[st.session_state.row]

# displaying data

with col2:
	st.write('')
	st.write('')
	st.write('')
	st.markdown('#### Project Name:')
	st.write('')
	st.markdown('#### Process Type:')
	st.write('')
	st.markdown('#### Country:')
	st.write('')
	st.markdown('#### Ore Treatment Rate (t/a):')
	st.write('')
	st.markdown('#### Years Operating:')
	st.write('')
	st.markdown('#### Payable Metal:')
	st.write('')
	st.markdown('#### Study Type:')
	st.write('')
	st.markdown('#### Company:')
	st.write('')
	st.markdown('#### # of Autoclave Trains:')

with col4:
	st.write('')
	st.write('')
	st.write('')
	st.markdown(str( '####' + ' ' +searchrecord['Project']))
	st.write('')
	st.markdown(str( '####' + ' ' +searchrecord['Process Type']))
	st.write('')
	st.markdown(str( '####' + ' ' +searchrecord['Country']))
	st.write('')
	st.markdown(str( '####' + ' ' +searchrecord['Ore Treatment Rate (t/a)']))
	st.write('')
	st.markdown(str( '####' + ' ' +searchrecord['Years Operating']))	
	st.write('')
	st.markdown(str( '####' + ' ' +searchrecord['Payable Metal']))		
	st.write('')
	st.markdown(str( '####' + ' ' +searchrecord['StudyType']))	
	st.write('')
	st.markdown(str( '####' + ' ' +searchrecord['Company']))	
	st.write('')
	st.markdown(str( '####' + ' ' +searchrecord['# of Autoclave Trains']))	


# return full dataset

st._legacy_dataframe(project_dump)

# download button

def convert_df(df):
   return df.to_csv().encode('utf-8')

csv = convert_df(project_dump)

st.download_button(
   "Download",
   csv,
   "ProjectFilter"+str(date.today())+".csv",
   "text/csv",
   key='download-csv'
)
