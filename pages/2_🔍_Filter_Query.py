import pandas as pd
import streamlit as st
import numpy as np
from datetime import date
from Config import Database_Connection
from Config import df_print_noindex
from login import password_manager

# programming aid variables
degree_sign = u'\N{DEGREE SIGN}'

# define connection variables
st.set_page_config(layout="wide")

# instantiative the database connection and creating necessary object to interact with the database
cursor,cnxn = Database_Connection()

def main():

    # create datasource for dropdowns in the filter form (THIS CAN BE DONE WITHOUT DB QUERYING VIA DATAFRAME... TO FIX)

    #order of dropdown menus in filter query
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
    
    #different SQL queries required for filter query
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
            'selectype': 'multi'
        },
        'site_conditions': {
            'table': '[Project]',
            'column': '[SiteConditions]',
            'label': 'Site Conditions',
            'selectype': 'single'
        },
        'POX_type': {
            'table': '[Autoclave]',
            'column': '[Acid/Alkaline]',
            'label': 'POX Type',
            'selectype': 'single'
        }
    }

    #looping through dropdowm menus and creating their respective DF's
    for dropdown_menu_name in dropdown_order.keys():
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
    st.write('### Filter Criteria')

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

    # creating dropdowns for each input type
    for input_type in form_inputs.keys():
        if dropdown_queries[input_type]['selectype'] == 'multi':
            form_inputs[input_type] = st.multiselect(label=dropdown_queries[input_type]['label'], options=dropdown_order[input_type])
        if dropdown_queries[input_type]['selectype'] == 'single':
            form_inputs[input_type] = st.selectbox(label=dropdown_queries[input_type]['label'], options=dropdown_order[input_type], index=0)

    # initializing input lists for manipulation: ensuring all form inputs are of same type and initiallizing lists
    # if no input it provided
    for input_type in form_inputs.keys():
        if isinstance(form_inputs[input_type], str):
            form_inputs[input_type] = [form_inputs[input_type]]
        if not form_inputs[input_type]:
            form_inputs[input_type].append('')

    # Create sliders with specified slider properties and store them in a dictionary of slider user inputs
    slider_inputs = {
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
            'range': [0,8000000],
            'default': [200000,1000000],
            'step': 100000,
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
    }

    # displaying sliders and their associated checkboxes
    for slider in slider_inputs.keys():
        checkbox = st.checkbox(label=slider_properties[slider]['description'], help=slider_properties[slider]['help'], key=slider)
        if checkbox:
            slider_properties[slider]['disabled'] = False
        slider_inputs[slider]['data'] = st.slider('', min_value=slider_properties[slider]['range'][0],\
        max_value=slider_properties[slider]['range'][1],value=slider_properties[slider]['default'], step=slider_properties[slider]['step'],\
        disabled=slider_properties[slider]['disabled'], key=slider_inputs[slider]['data'])
        if slider_properties[slider]['disabled']:
            slider_inputs[slider]['data'] = (None, None)

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
                st.write(input)

    # append slider data to callable parameters list for querying

    for slider in slider_inputs:
        if slider_properties[slider]['disabled'] is False:
            rangeparams.append(slider_inputs[slider]['data'][0])
            rangeparams.append(slider_inputs[slider]['data'][1])

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
        }
    }

    for slider in slider_inputs:
        if slider_properties[slider]['disabled']:
            slider_inputs[slider]['sql'] = """"""
        else:
            slider_inputs[slider]['sql'] = slider_queries['genericrangequery'].format(slider_queries[slider]['table'], \
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
        if type == 'POX_type':
            if form_inputs[type][0] == '':
                sql_input[type] = """"""
            else:
                sql_input[type] = "AND" + dropdown_queries['sqlgeneral'].format(dropdown_queries[type]['table'], dropdown_queries[type]['column'],  
                dropdown_queries[type]['table'], dropdown_queries[type]['column'])
        elif type == 'study_types':
            if form_inputs[type][0] == '':
                sql_input[type] = """"""
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
    for type in sql_input:
        sql_filterquery += sql_input[type]

    for slider in slider_inputs:
        sql_filterquery += slider_inputs[slider]['sql']

    # Execute query to records with called variables
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
        'Initial Capex': None
    }

    for type in decimal_removal:
        project_dump = project_dump.fillna({type: 0})
        if type != 'Initial Capex':
            project_dump = project_dump.astype({type: int})

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
    project_dump = project_dump.round({'TotalReserves': 0})
    project_dump = project_dump.fillna('')
    project_dump = project_dump.astype(str)

    # aggregating payalbe metals column with ',' seperator
    project_dump = project_dump.groupby(['ID']).agg(lambda x: ' , '.join(list(set(list(x)))))
    project_dump = project_dump.sort_values(['ID'])

    # if metals criteria is used, filter for metal, along with rest of payable metals for that project. metal 1 OR metal 2 up to a maximum of 
    # 5 metals

    if form_inputs['payable_metals'][0] != '':
        if len(form_inputs['payable_metals']) == 1:
            project_dump = project_dump[project_dump['Payable Metal'].str.contains(form_inputs['payable_metals'][0])]

        elif len(form_inputs['payable_metals']) == 2:
            project_dump = project_dump[project_dump['Payable Metal'].str.contains(form_inputs['payable_metals'][0]) |
            project_dump['Payable Metal'].str.contains(form_inputs['payable_metals'][1])]

        elif len(form_inputs['payable_metals']) == 3:
            project_dump = project_dump[project_dump['Payable Metal'].str.contains(form_inputs['payable_metals'][0]) |
            project_dump['Payable Metal'].str.contains(form_inputs['payable_metals'][1]) | project_dump['Payable Metal'].str.contains(form_inputs['payable_metals'][2])]

        elif len(form_inputs['payable_metals']) == 4:
            project_dump = project_dump[project_dump['Payable Metal'].str.contains(form_inputs['payable_metals'][0]) |
            project_dump['Payable Metal'].str.contains(form_inputs['payable_metals'][1]) | project_dump['Payable Metal'].str.contains(form_inputs['payable_metals'][2]) |
            project_dump['Payable Metal'].str.contains(form_inputs['payable_metals'][3])]    

        elif len(form_inputs['payable_metals']) == 5:
            project_dump = project_dump[project_dump['Payable Metal'].str.contains(form_inputs['payable_metals'][0]) |
            project_dump['Payable Metal'].str.contains(form_inputs['payable_metals'][1]) | project_dump['Payable Metal'].str.contains(form_inputs['payable_metals'][2]) |
            project_dump['Payable Metal'].str.contains(form_inputs['payable_metals'][3]) | project_dump['Payable Metal'].str.contains(form_inputs['payable_metals'][4])]   

    # display query results
    st.write("""
        ## Filter Query
        ##### Based on above selections:
    """)

    #Column select for query
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

    for slider in slider_inputs.keys():
        if slider_inputs[slider]['data'] != (None,None):
            criteria_display_type.append(slider_properties[slider]['description'])
            criteria_display_value.append('{0:,}'.format(slider_inputs[slider]['data'][0]) + ' - ' + '{0:,}'.format(slider_inputs[slider]['data'][1]))
        
    criteria_display = pd.DataFrame(list(zip(criteria_display_type, criteria_display_value)), columns= ['Criteria', 'Value']).style.hide_index()

    # function to display table with formatting
    if criteria_display_value:
        df_print_noindex(criteria_display, type='Table')

    # Display Filter Query
    st._legacy_dataframe(project_dump, width=50000, height=700)

    # download csv of results
    def convert_df(df):
        """
        Author: Ali Kufaishi
        Date: 7/20/2022
        Revision: 0.0.1
        Reviewer: Liam Coleman
        Review Date: 7/20/2022
        Intent: Convert dataframes to csv and return csv as object
        Inputs: 
            df - Pandas Dataframe - output dataframe
        Returns:
            output_csv - csv object - output dataframe converted to csv
        Exceptions:
            N/A
        """
    
        output_csv = df.to_csv().encode('utf-8')
        return output_csv

    csv = convert_df(project_dump)

    st.download_button(
    "Download",
    csv,
    "ProjectFilter"+str(date.today())+".csv",
    "text/csv",
    key='download-csv'
    )

    # close cursor
    cursor.close()

if "user" not in st.session_state:
    st.session_state.user = False

if "dev" not in st.session_state:
    st.session_state.dev = False

# Authentication
if st.session_state.user or st.session_state.dev:
    main()
else:
    password_manager(cursor)