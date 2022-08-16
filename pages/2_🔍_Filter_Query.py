from logging import Filter
from click import style
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
import json
from streamlit_tags import st_tags
from st_aggrid import AgGrid


# programming aid variables
degree_sign = u'\N{DEGREE SIGN}'

# configure streamlit page to wide layout, must be first streamlit call
st.set_page_config(layout="wide")

# instantiative the database connection and creating necessary object to interact with the database
cursor,cnxn = Database_Connection()

def filter_query():

    # create datasource for dropdowns in the filter form

    # order of dropdown menus in filter query
    dropdown_order = {
        'projects': None,
        'countries': None,
        'continents': None,
        'study_types': None,
        'process_types': None,
        'payable_metals': None,
        'site_conditions': None,
        'POX_type': None,
    }

    # different SQL queries required for filter query dropdowns and sql_filterquery. selecttypes must be either 'single', 'multi', or 'exclusive'.
    # exclusive tag on select type will generate an "exclusive" button and query the as an exclusive criteria (CURRENTLY ONLY FOR PAYABLE METAL)
    dropdown_queries = {
        'singleTableLookup': """
            SELECT DISTINCT [ProjectDetailDatabase].[dbo].{}.{}
            FROM [ProjectDetailDatabase].[dbo].{}
            """,
        'sqlgeneral':"""
            {}.{} LIKE IIF(? IS NULL, {}.{}, ?)
        """,
        'sqlexact': """
            {}.{} = ?
        """,
        'projects': {
            'table': '[Project]',
            'column': '[Name]',
            'label': 'Project Name',
            'selectype': 'multi'
        },
        'countries': {
            'table': '[Project]',
            'column': '[Country]',
            'label': 'Country',
            'selectype': 'multi'
        },
        'continents': {
            'table': '[Project]',
            'column': '[Continent]',
            'label': 'Continent',
            'selectype': 'multi'
        },
        'study_types': {
            'table': '[Project]',
            'column': '[StudyType]',
            'label': 'Study Type',
            'selectype': 'multi'
        },
        'process_types': {
            'table': '[Project]',
            'column': '[HPM Type]',
            'label': 'Process Type',
            'selectype': 'multi'
        },
        'payable_metals': {
            'table': '[PayableMetals]',
            'column': '[name]',
            'label': 'Payable Metal',
            'selectype': 'exclusive'
        },
        'site_conditions': {
            'table': '[Project]',
            'column': '[SiteConditions]',
            'label': 'Site Conditions',
            'selectype': 'multi'
        },
        'POX_type': {
            'table': '[Autoclave]',
            'column': '[Acid/Alkaline]',
            'label': 'POX Type',
            'selectype': 'multi'
        }
    }

    # looping through dropdowm menus and creating their respective data sources
    for dropdown_menu_name in dropdown_order:
        query_string = dropdown_queries['singleTableLookup'].format(dropdown_queries[dropdown_menu_name]['table'],
        dropdown_queries[dropdown_menu_name]['column'],
        dropdown_queries[dropdown_menu_name]['table'])

        query_results = cursor.execute(query_string)

        dropdown_order[dropdown_menu_name] = pd.DataFrame.from_records(data=query_results)
        dropdown_order[dropdown_menu_name].loc[-1] = ''
        dropdown_order[dropdown_menu_name] = dropdown_order[dropdown_menu_name].sort_index().reset_index(drop=True)
        if dropdown_menu_name == 'study_types' or 'POX_type' :
            dropdown_order[dropdown_menu_name] = dropdown_order[dropdown_menu_name].replace('NULL', np.nan).dropna(axis=0)

    # create webpage layout
    st.write('# Project Filtering')
    st.write('')
    st.write('')
    st.write('### Filter Query')

    # creating form
    form_inputs = {
        'projects': None,
        'countries': None,
        'continents': None,
        'study_types': None,
        'process_types': None,
        'payable_metals': None,
        'site_conditions': None,
        'POX_type': None,
    }

    exclusive_inputs_toggle = {
        'projects': None,
        'countries': None,
        'continents': None,
        'study_types': None,
        'process_types': None,
        'payable_metals': None,
        'site_conditions': None,
        'POX_type': None,
    }

    # creating dropdowns for each input type, multi vs. single is determine by the given dropdown and it's tag in dropdown queries
    for input_type in form_inputs:
        if dropdown_queries[input_type]['selectype'] == 'multi':
            form_inputs[input_type] = st.multiselect(label=dropdown_queries[input_type]['label'], options=dropdown_order[input_type])
        elif dropdown_queries[input_type]['selectype'] == 'exclusive':
            col1, col2 = st.columns((13, 1))
            with col1:
                form_inputs[input_type] = st.multiselect(label=dropdown_queries[input_type]['label'], options=dropdown_order[input_type])
            with col2:
                st.write('')
                st.write('')
                st.write('')
                exclusive_inputs_toggle[input_type] = st.checkbox(label='Exclusive')
        elif dropdown_queries[input_type]['selectype'] == 'single':
            form_inputs[input_type] = st.selectbox(label=dropdown_queries[input_type]['label'], options=dropdown_order[input_type], index=0)

    # initializing input lists for manipulation: ensuring all form inputs are of same type and initiallizing lists
    # if no input it provided
    for input_type in form_inputs:
        if isinstance(form_inputs[input_type], str):
            form_inputs[input_type] = [form_inputs[input_type]]
        if not form_inputs[input_type]:
            form_inputs[input_type].append('')

    # Create sliders with specified slider properties and store them in a dictionary of slider user inputs
    slider_data = {
        'temperature':{
            'data':None,
            'sql': None
        },
        'pressure':{
            'data':None,
            'sql': None
        },
        'throughput':{
            'data':None,
            'sql': None
        },
        'sulphur':{
            'data':None,
            'sql': None
        },
        'reserves':{
            'data':None,
            'sql': None
        },
        'capex':{
            'data':None,
            'sql': None
        }
    }

    slider_properties = {
        'temperature': {
            'description': 'Operating Temperature ('+degree_sign+'C)',
            'help': None,
            'range': [0,500],
            'default': [150,400],
            'step': 5,
            'units': degree_sign+'C',
            'disabled': True
        },
        'pressure': {
            'description': 'Operating Pressure (kPa)',
            'help': 'Absolute',
            'range': [0,4000],
            'default': [1500,2500],
            'step': 10,
            'units': 'kPa',
            'disabled': True
        },
        'throughput': {
            'description': 'Ore Throughput Rate (t/a)',
            'help': 'Total circuit throughput',
            'range': [0,80000000],
            'default': [200000,10000000],
            'step': 1000000,
            'units': 't/a',
            'disabled': True
        },
        'sulphur': {
            'description': 'Feed Sulphur (%)',
            'help': None,
            'range': [0,50],
            'default': [5,10],
            'step': 1,
            'units': '%',
            'disabled': True
        },
        'reserves': {
            'description': 'Total Reserves (Mt)',
            'help': 'Million metric tonnes',
            'range': [0,1500],
            'default': [200,300],
            'step': 10,
            'units': 'Mt',
            'disabled': True
        },
        'capex': {
            'description': 'Initial Capital Cost ($USD)',
            'help': None,
            'range': [0,10000000000],
            'default': [500000000,2000000000],
            'step': 200000000,
            'units': '$USD',
            'disabled': True
        }
    }

    # displaying sliders and their associated checkboxes
    for slider in slider_data:
        checkbox = st.checkbox(label=slider_properties[slider]['description'], help=slider_properties[slider]['help'], key=slider)
        if checkbox:
            slider_properties[slider]['disabled'] = False
        slider_data[slider]['data'] = st.slider('', min_value=slider_properties[slider]['range'][0],\
        max_value=slider_properties[slider]['range'][1],value=slider_properties[slider]['default'], step=slider_properties[slider]['step'],\
        disabled=slider_properties[slider]['disabled'], key=slider_data[slider]['data'])
        if slider_properties[slider]['disabled']:
            slider_data[slider]['data'] = (None, None)

    # append dropdown data to callable parameters list for querying. study_types and POX_type are outliers requiring special forms of input. payable metal criteria is done further below
    rangeparams = []

    for input in form_inputs:
        if input == 'study_types':
            if form_inputs[input][0] != '':
                for i in range(len(form_inputs[input])):
                    rangeparams.append(form_inputs[input][i])
        elif input == 'POX_type':
            if form_inputs[input][0] != '':
                for i in range(len(form_inputs[input])):
                    rangeparams.append(form_inputs[input][i])
                    rangeparams.append(f"%{form_inputs[input][i]}%")
        elif input != 'payable_metals':
            for i in range(len(form_inputs[input])):
                rangeparams.append(form_inputs[input][i])
                rangeparams.append(f"%{form_inputs[input][i]}%")

    # append slider data to callable parameters list for querying
    for slider in slider_data:
        if slider_properties[slider]['disabled'] is False:
            rangeparams.append(slider_data[slider]['data'][0])
            rangeparams.append(slider_data[slider]['data'][1])

    slider_queries = {
        'genericrangequery': """
        AND
        {}.{} Between ? And ?
        """,
        'temperature': {
            'table': '[Autoclave]',
            'column': '[OperatingTemp]',
            'label': 'Operating Temperature ('+degree_sign+'C)'
        },
        'pressure': {
            'table': '[Autoclave]',
            'column': '[OperatingPressure]',
            'label': 'Operating Pressure (kPa)'
        },
        'throughput': {
            'table': '[Project]',
            'column': '[OreTreatmentRate]',
            'label': 'Ore Throughput Rate (t/a)'
        },
        'sulphur': {
            'table': '[Autoclave]',
            'column': '[FeedSulphurConcentration]',
            'label': 'Feed Sulphur (%)'
        },
        'reserves': {
            'table': '[Project]',
            'column': '[TotalReserves]',
            'label': 'Total Reserves (Mt)'
        },
        'capex': {
            'table': '[ProjectFinancials]',
            'column': '[Initial Capex]',
            'label': 'Initial Capital Cost ($USD)'
        }
    }

    for slider in slider_data:
        if slider_properties[slider]['disabled']:
            slider_data[slider]['sql'] = ""
        else:
            slider_data[slider]['sql'] = slider_queries['genericrangequery'].format(slider_queries[slider]['table'], \
            slider_queries[slider]['column'])

    # additions to sql query for field inputs, depending on number of inputs
    sql_input = {
        'projects': None,
        'countries': None,
        'continents': None,
        'study_types': None,
        'process_types': None,
        'site_conditions': None,
        'POX_type': None,
    }

    # generates sql code to add to base query. Based on entries to the form, will adjust for number of inputs by adding more sql criteria. sql stored in sql input
    for type in sql_input:

        if type == 'study_types':
            if form_inputs[type][0] == '':
                sql_input[type] = ""
            else:
                sql_input[type] = "AND" + "(" + dropdown_queries['sqlexact'].format(dropdown_queries[type]['table'], dropdown_queries[type]['column'])

                for i in range(len(form_inputs[type])-1):
                    sql_input[type] += "OR" + dropdown_queries['sqlexact'].format(dropdown_queries[type]['table'], dropdown_queries[type]['column'])
                sql_input[type] += ")"
        else:
            if type == 'projects':
                sql_input[type] = "WHERE"
            else:
                sql_input[type] = "AND"
            if type == 'POX_type':
                if form_inputs[type][0] == '':
                    sql_input[type] = ""
                    break

            sql_input[type] += "(" + dropdown_queries['sqlgeneral'].format(dropdown_queries[type]['table'], dropdown_queries[type]['column'],
            dropdown_queries[type]['table'], dropdown_queries[type]['column'])

            for i in range(len(form_inputs[type])-1):
                sql_input[type] += "OR" + dropdown_queries['sqlgeneral'].format(dropdown_queries[type]['table'], dropdown_queries[type]['column'],
                dropdown_queries[type]['table'], dropdown_queries[type]['column'])
            sql_input[type] += ")"

    sql_filterquery = """
    SELECT DISTINCT [Project].[ID],
        [Project].Name,
        [Project].StudyType,
        [Project].Country,
        [Project].Continent,
        [PayableMetals].Name AS [Payable Metal],
        [Project].SiteConditions,
        [Project].[HPM Type] AS [Process Type],
        [Project].[No of Processing Years],
        [Autoclave].OperatingPressure,
        [Autoclave].OperatingTemp,
        [Autoclave].FeedSulphurConcentration,
        [Autoclave].[Acid/Alkaline],
        [Project].OreTreatmentRate,
        [Project].TotalReserves,
        [ProjectFinancials].[Initial Capex],
        [Project].[Date of information]

    FROM (((([ProjectDetailDatabase].[dbo].[Project]
        LEFT JOIN [ProjectDetailDatabase].[dbo].[ProjectPayableMetals] ON [Project].[ID] = [ProjectPayableMetals].[ID(Projects)])
        LEFT JOIN [ProjectDetailDatabase].[dbo].[PayableMetals] ON [ProjectPayableMetals].[ID(Products)] = [PayableMetals].[ID])
        LEFT JOIN [ProjectDetailDatabase].[dbo].[Autoclave] ON [Project].[ID] = [Autoclave].[ID(Project)])
        LEFT JOIN [ProjectDetailDatabase].[dbo].[ProjectFinancials] ON [Project].[ID] = [ProjectFinancials].[ID(Projects)])
        LEFT JOIN [ProjectDetailDatabase].[dbo].[PayingMetal] ON Project.ID = [PayingMetal].[ID(Proj)]

    """

    # SQL addition for form inputs
    for type in sql_input:
        sql_filterquery += sql_input[type]
  
    # SQL addition for slider inputs
    for slider in slider_data:
        sql_filterquery += slider_data[slider]['sql']

    # execute query to records with called variables
    records = cursor.execute(sql_filterquery,rangeparams).fetchall()

    # define record column names
    columns = [column[0] for column in cursor.description]

    # dump records into a dataframe
    project_dump = pd.DataFrame.from_records(
        data=records,
        columns=columns,
    )

    # setting database index as dataframe index
    project_dump.set_index(['ID'], inplace=True)

    # addressing unnecessary decimals
    decimal_removal = {
        'Date of information': None,
        'No of Processing Years': None,
        'OperatingPressure': None,
        'OperatingTemp': None,
        'OreTreatmentRate': None,
        'TotalReserves': None,
        'Initial Capex': None
    }

    for type in decimal_removal:
        project_dump = project_dump.fillna({type: 0})
        project_dump = project_dump.astype({type: np.int64})

    # adding thousands seperators to columns
    project_dump.loc[:, "OreTreatmentRate"] = project_dump["OreTreatmentRate"].map('{:,.0f}'.format)
    project_dump.loc[:, "Initial Capex"] = project_dump["Initial Capex"].map('${:,.0f}'.format)

    # renaming columns
    project_dump = project_dump.rename(columns={'OperatingTemp': 'Operating Temperature ('+degree_sign+'C)'})
    project_dump = project_dump.rename(columns={'Name': 'Project Name'})
    project_dump = project_dump.rename(columns={'StudyType': 'Study Type'})
    project_dump = project_dump.rename(columns={'SiteConditions': 'Site Conditions'})
    project_dump = project_dump.rename(columns={'OperatingPressure': 'Operating Pressure (kPa)'})
    project_dump = project_dump.rename(columns={'FeedSulphurConcentration': 'Feed Sulphur (%)'})
    project_dump = project_dump.rename(columns={'OreTreatmentRate': 'Ore Treatment Rate (t/a)'})
    project_dump = project_dump.rename(columns={'TotalReserves': 'Total Reserves (Mt)'})
    project_dump = project_dump.rename(columns={'Initial Capex': 'Initial Capital Cost (USD$)'})

    # data rounding, removing nans, and prepping df for streamlit write
    project_dump = project_dump.replace(0,  '')
    project_dump = project_dump.replace('$0',  '')
    project_dump = project_dump.replace('$nan',  '')
    project_dump = project_dump.fillna('')
    project_dump = project_dump.astype(str)

    # aggregating payalbe metals column with ',' seperator
    project_dump = project_dump.groupby(['ID']).agg(lambda x: ' , '.join(list(set(list(x)))))
    project_dump = project_dump.sort_values(['ID'])

    # if metals criteria is used, filter for metal, along with rest of payable metals for that project.

    # if exclusive button is toggled, exclusive metal criteria used, else inclusive metal search
    for input in exclusive_inputs_toggle:
        if exclusive_inputs_toggle[input]:
            dropped_metals = dropdown_order['payable_metals'][0].values.tolist()
            dropped_metals.remove('')
            if form_inputs['payable_metals'][0] != '':
                project_dump = project_dump[project_dump['Payable Metal'] != '']  
                for metal in form_inputs['payable_metals']:
                    dropped_metals.remove(metal)
                for metal in dropped_metals:
                    project_dump = project_dump[project_dump['Payable Metal'].str.contains(metal)==False]    
        else:
            if form_inputs['payable_metals'][0] != '':
                for x, metal in enumerate(form_inputs['payable_metals']):
                    if x == 0:
                        query = project_dump['Payable Metal'].str.contains(metal)
                    else:
                        query = query | project_dump['Payable Metal'].str.contains(metal)
                project_dump = project_dump[query]

    # display query results
    st.write("""
        ## Filter Results
        ##### Based on above selections:
    """)

    # column select for query. checkboxes on by default, for each column that's toggled off, column will be dropped from df
    selectall_toggle = st.checkbox(label='Select all', value=True)

    column_toggle = {
        'Study Type':None,
        'Operating Pressure (kPa)': None,
        'Country': None,
        'Operating Temperature ('+degree_sign+'C)':None,
        'Continent': None,
        'Feed Sulphur (%)': None,
        'Payable Metal': None,
        'Acid/Alkaline': None,
        'Site Conditions': None,
        'Ore Treatment Rate (t/a)': None,
        'Process Type': None,
        'Total Reserves (Mt)': None,
        'No of Processing Years': None,
        'Initial Capital Cost (USD$)': None,
    }

    col1, col2, col3, col4, col5, col6, col7 = st.columns(7)

    with col1:
        column_toggle['Study Type'] = st.checkbox(label='Study Type', value=selectall_toggle)
        column_toggle['Operating Pressure (kPa)'] = st.checkbox(label='Operating Pressure', value=selectall_toggle)
    with col2:
        column_toggle['Country'] = st.checkbox(label='Country', value=selectall_toggle)
        column_toggle['Operating Temperature ('+degree_sign+'C)'] = st.checkbox(label='Operating Temperature', value=selectall_toggle)
    with col3:
        column_toggle['Continent'] = st.checkbox(label='Continent', value=selectall_toggle)
        column_toggle['Feed Sulphur (%)'] = st.checkbox(label='Feed Sulphur %', value=selectall_toggle)
    with col4:
        column_toggle['Payable Metal'] = st.checkbox(label='Payable Metal', value=selectall_toggle)
        column_toggle['Acid/Alkaline'] = st.checkbox(label='Acid/Alkaline', value=selectall_toggle)
    with col5:
        column_toggle['Site Conditions'] = st.checkbox(label='Site Conditions', value=selectall_toggle)
        column_toggle['Ore Treatment Rate (t/a)'] = st.checkbox(label='Treatment Rate', value=selectall_toggle)
    with col6:
        column_toggle['Process Type'] = st.checkbox(label='Process Type', value=selectall_toggle)
        column_toggle['Total Reserves (Mt)'] = st.checkbox(label='Total Reserves', value=selectall_toggle)
    with col7:
        column_toggle['No of Processing Years'] = st.checkbox(label='Process Years', value=selectall_toggle)
        column_toggle['Initial Capital Cost (USD$)'] = st.checkbox(label='Initial CAPEX', value=selectall_toggle)

    # drop columns toggle
    for toggle in column_toggle:
        if column_toggle[toggle] == False:
            project_dump = project_dump.drop(columns=toggle)

    # criteria display table creation
    criteria_display_type = []
    criteria_display_value = []

    for type in form_inputs:
        if form_inputs[type] != ['']:
            criteria_display_type.append(dropdown_queries[type]['label'])
            value_list = ''
            for i in range(len(form_inputs[type])):
                if i == 0:
                    value_list += ''
                else:
                    value_list += ' or '
                value_list += str(form_inputs[type][i])
            criteria_display_value.append(value_list)

    for slider in slider_data:
        if slider_data[slider]['data'] != (None,None):
            criteria_display_type.append(slider_properties[slider]['description'])
            criteria_display_value.append('{0:,}'.format(slider_data[slider]['data'][0]) + ' - ' + '{0:,}'.format(slider_data[slider]['data'][1]))

    criteria_display = pd.DataFrame(list(zip(criteria_display_type, criteria_display_value)), columns= ['Criteria', 'Value'])

    # function to display table with formatting
    if criteria_display_value:
        df_print_noindex(criteria_display, type='Table')

    # display Filter Query
    st._legacy_dataframe(project_dump, width=50000, height=700)

    # Potential new integration of AgGrid for displaying data, contains integrating filtering functions
    # AgGrid(project_dump, height=800, theme='streamlit')

    if 'dfs' not in st.session_state:
        st.session_state.dfs = {}
    
    with st.sidebar:
        tlabel = st.text_input(label="Enter Query Name")
        cache_trigger = st.button(label='Cache Query', help='Use this button to store multiple queries for later download.')

    # button to cache current filter-query pair
    if cache_trigger:
        if tlabel == '':
            with st.sidebar:
                st.warning("Please Enter Query Name")
        elif tlabel in st.session_state.dfs:
            with st.sidebar:
                st.warning("You entered a name that is currently used within the cache.\n Please enter another.")
        else:
            st.session_state.dfs[tlabel] = {}
            st.session_state.dfs[tlabel]['Filter'] = criteria_display
            st.session_state.dfs[tlabel]['Query'] = project_dump
       
    # display of cached queries. removing elements from the list will remove the query-filter pair from the df_dict
    with st.sidebar:
        list_of_queries = list(st.session_state.dfs.keys())
        cache_update = st.multiselect(label='Cached Queries:', default=list_of_queries, options=list_of_queries, help='Press on the x of the queries to \
            clear them from cache.')

    # checking whether element has been removed from the list. Then removing from list.
    if cache_update != list_of_queries:
        set(list_of_queries)
        set(cache_update)
        dropped_queries = list(set(list_of_queries).difference(cache_update))
        for query in dropped_queries:
            if query in st.session_state.dfs:
                st.session_state.dfs.pop(query)
        st.experimental_rerun()

    # check to see if cache is empty, if so block download from occuring

    if st.session_state.dfs == {}:
        download_toggle = True
        with st.sidebar:
            st.info('Give your query a name and cache it to download it.')
    else:
        download_toggle = False
    # download button for query output

    with st.sidebar:
        st.download_button(
        label="Export Query Results",
        data= output_excel(st.session_state.dfs, project_dump, criteria_display),
        file_name= 'FilteredDatabaseQuery.xlsx',
        key='download-excel',
        disabled=download_toggle
        )

    # close cursor
    cursor.close()

def output_excel(df_dict, current_query_df, current_filter_df):
    """
    Author: Ali Kufaishi
    Date: 7/27/2022
    Revision: 0.0.1
    Reviewer: N/A
    Review Date: N/A
    Intent: Convert dataframes to xlsx with proper formatting and return xlsx as object
    Inputs:
        df_dict - Dictionary - cached filter and query dataframes stored in a dictionary
    Returns:
        processed_data - xlsx object - output dataframes converted to xlsx
    Exceptions:
        N/A
    """
    # creating and preparing excel object for download

    # creating excel pointers
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    workbook = writer.book

    # writing dfs to excel
    for entry in df_dict:
        if entry:
            filter_df = df_dict[entry]['Filter']
            query_df = df_dict[entry]['Query']
            filter_label = entry + ' Filter'
            query_label = entry + ' Results'
            sheet_label = str(entry)

        worksheet = workbook.add_worksheet(sheet_label)
        writer.sheets[sheet_label] = worksheet

        worksheet.write_string(0, 0, filter_label)
        filter_df.to_excel(writer, sheet_name=sheet_label, startrow=1, startcol=0)
        worksheet.write_string(filter_df.shape[0] + 4, 0, query_label)
        query_df.to_excel(writer, sheet_name=sheet_label, startrow= filter_df.shape[0] + 5, startcol=0)
        auto_adjust_xlsx_column_width(query_df, writer, sheet_name=sheet_label, margin=0)

    writer.save()
    processed_data = output.getvalue()        
    return processed_data

if "user" not in st.session_state:
    st.session_state.user = False

if "dev" not in st.session_state:
    st.session_state.dev = False

# authentication
if st.session_state.user or st.session_state.dev:
    filter_query()
else:
    password_manager(cursor)