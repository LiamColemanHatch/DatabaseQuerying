
from asyncio.windows_events import NULL
from matplotlib.pyplot import axis
import sqlalchemy
import pandas as pd
import streamlit as st
import numpy as np
from datetime import date
from Config import Database_Connection
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
        'projects': {
            'table': '[Project]',
            'column': '[Name]'
        },
        'countries': {
            'table': '[Project]',
            'column': '[Country]'
        },
        'continents': {
            'table': '[Project]',
            'column': '[Continent]'
        },
        'study_types': {
            'table': '[Project]',
            'column': '[StudyType]'
        },
        'process_types': {
            'table': '[Project]',
            'column': '[HPM Type]'
        },
        'payable_metals': {
            'table': '[PayableMetals]',
            'column': '[name]'
        },
        'site_conditions': {
            'table': '[Project]',
            'column': '[SiteConditions]'
        },
        'POX_type': {
            'table': '[Autoclave]',
            'column': '[Acid/Alkaline]'
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
        if dropdown_menu_name == 'study_types':
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

    with st.form(key='filter_form'):
        project_input = form_inputs['projects'] =  st.multiselect('Project Name', dropdown_order['projects'], help="""To clear field, select empty element in the dropdown menu. Press
        submit and scroll down for filter results.""")
        country_input = form_inputs['countries'] = st.multiselect('Country', dropdown_order['countries'])
        continent_input = form_inputs['continents'] = st.multiselect('Continent', dropdown_order['continents'])
        studytype_input = form_inputs['study_types'] = st.multiselect('Study Type', dropdown_order['study_types'])
        hpmtype_input = form_inputs['process_types'] = st.multiselect('Process Type', dropdown_order['process_types'])
        payablemetal_input = form_inputs['payable_metals'] = st.multiselect('Payable Metal', dropdown_order['payable_metals'])
        greenbrownfield_input = form_inputs['site_conditions'] = st.selectbox('Greenfield/Brownfield', dropdown_order['site_conditions'], index=0)
        acidalkaline_input = form_inputs['POX_type'] = st.selectbox('POX Type', dropdown_order['POX_type'], index=0)
        submit_button = st.form_submit_button(label='submit')

    # initializing input lists for manipulation

    if not project_input:
        project_input.append('')
    
    if not country_input:
        country_input.append('')
    
    if not continent_input:
        continent_input.append('')

    if not studytype_input:
        studytype_input.append('')

    if not payablemetal_input:
        payablemetal_input.append('')

    if not hpmtype_input:
        hpmtype_input.append('')

    if not acidalkaline_input:
        acidalkaline_input = ''

    if not greenbrownfield_input:
        greenbrownfield_input = ''

    # temperature slider

    temp_check = st.checkbox("Operating Temperature ("+degree_sign+"C)")

    if temp_check:
        temp_checkinput = False
    else:
        temp_checkinput = True

    temp_slider = st.slider('', min_value=0, max_value=500, value=(150, 400), step=5, disabled=temp_checkinput)

    if temp_checkinput is False:
        temp_range = temp_slider
    else:
        temp_range = (NULL, NULL)

    # pressure slider

    press_check = st.checkbox('Operating Pressure (kPa)', help='Absolute')

    if press_check:
        press_checkinput = False
    else:
        press_checkinput = True

    press_slider = st.slider('', min_value=0, max_value=4000, value=(1500, 2500), step=5, disabled=press_checkinput)

    if press_checkinput is False:
        press_range = press_slider
    else:
        press_range = (NULL, NULL)

    # ore throughput slider

    ore_check = st.checkbox('Ore Throughput Rate (t/a)', help='Total circuit throughput')

    if ore_check:
        ore_checkinput = False
    else:
        ore_checkinput = True

    ore_slider = st.slider('', min_value=0, max_value=8000000, value=(750000, 1000000), step=100000, disabled=ore_checkinput)

    if ore_checkinput is False:
        ore_range = ore_slider
    else:
        ore_range = (NULL, NULL)

    # feed sulphur slider

    sulph_check = st.checkbox('Feed Sulphur (%)')

    if sulph_check:
        sulph_checkinput = False
    else:
        sulph_checkinput = True

    sulph_slider = st.slider('', min_value=0, max_value=50, value=(5, 10), step=1, disabled=sulph_checkinput)

    if sulph_checkinput is False:
        sulph_range = sulph_slider
    else:
        sulph_range = (NULL, NULL)

    # total reserves slider

    resrv_check = st.checkbox('Total Reserves (Mt)', help='Mt is million metric tonnes')

    if resrv_check:
        resrv_checkinput = False
    else:
        resrv_checkinput = True

    resrv_slider = st.slider('', min_value=0, max_value=1500, value=(200, 300), step=10, disabled=resrv_checkinput)

    if resrv_checkinput is False:
        resrv_range = resrv_slider
    else:
        resrv_range = (NULL, NULL)

    # define like variables for inprecise field inputs for each element of input list

    projectparam = []

    for i in range(len(project_input)):
        projectparam.append(project_input[i])
        projectparam.append(f'%{project_input[i]}%')

    countryparam = []

    for i in range(len(country_input)):
        countryparam.append(country_input[i])
        countryparam.append(f'%{country_input[i]}%')

    continentparam = []

    for i in range(len(continent_input)):
        continentparam.append(continent_input[i])
        continentparam.append(f'%{continent_input[i]}%')

    studytypeparam = []

    for i in range(len(studytype_input)):
        studytypeparam.append(studytype_input[i])  

    hpmtypeparam = []

    for i in range(len(hpmtype_input)):
        hpmtypeparam.append(hpmtype_input[i])
        hpmtypeparam.append(f'%{hpmtype_input[i]}%')  

    greenbrownfieldparam = f'%{greenbrownfield_input}%'
    acidalkalineparam = f'%{acidalkaline_input}%'

    # defining range criteria for sql input, to be added on to sql select query if checkbox is checked

    ## temp range criteria

            # pulling low and high variables from range tuple

    temprangelow = temp_range[0]
    temprangehigh = temp_range[1]

        # check if checkbox is checked, if not, no sql input

    if temp_checkinput is True:
        tempset_sql = """
        
        """
    else:
        tempset_sql = """
        AND

        [Autoclave].OperatingTemp Between ? And ?

        """

    ## pressure range criteria

            # pulling low and high variables from range tuple

    pressrangelow = press_range[0]
    pressrangehigh = press_range[1]

            # check if checkbox is checked if not, no sql input

    if press_checkinput is True:
        pressset_sql = """
        
        """
    else:
        pressset_sql = """
        AND

        [Autoclave].OperatingPressure Between ? And ?

        """

    ## ore throughput range criteria

            # pulling low and high variables from range tuple

    orerangelow = ore_range[0]
    orerangehigh = ore_range[1]

            # check if checkbox is checked if not, no sql input

    if ore_checkinput is True:
        oreset_sql = """
        
        """
    else:
        oreset_sql = """
        AND

        [Project].OreTreatmentRate Between ? And ?

        """

    ## feed sulphur range criteria

            # pulling low and high variables from range tuple

    sulphrangelow = sulph_range[0]
    sulphrangehigh = sulph_range[1]

            # check if checkbox is checked if not, no sql input

    if sulph_checkinput is True:
        sulphset_sql = """
        
        """
    else:
        sulphset_sql = """
        AND

        [Autoclave].FeedSulphurConcentration Between ? And ?

        """

    ## total reserves range criteria

            # pulling low and high variables from range tuple

    resrvrangelow = resrv_range[0]
    resrvrangehigh = resrv_range[1]

            # check if checkbox is checked if not, no sql input

    if resrv_checkinput is True:
        resrvset_sql = """
        
        """
    else:
        resrvset_sql = """
        AND

        [Project].TotalReserves Between ? And ?

        """


    # define query strings

    # select query, not in use

    sql_select = """
    SELECT *
    FROM [ProjectDetailDatabase].[dbo].[Project]

    WHERE [Project].[Name] LIKE IIF(? IS NULL, [Project].[Name], ?)

    AND

    [Project].[Country] LIKE IIF(? IS NULL, [Project].[Country], ?)

    AND

    [Project].[Continent] LIKE IIF(? IS NULL, [Project].[Continent], ?)

    AND

    [Project].[StudyType] LIKE IIF(? IS NULL, [Project].[StudyType], ?)

    AND

    [Project].[HPM Type] LIKE IIF(? IS NULL, [Project].[HPM Type], ?)

    --AND

    --WHERE [Project].[Country] LIKE IIF(? IS NULL, [Project].[Country], ?)

    --AND

    --WHERE [Project].[Country] LIKE IIF(? IS NULL, [Project].[Country], ?)



    """

    # additions to sql query for field inputs, depending on number of inputs

    projectinput_sql = """
    WHERE
    ([Project].[Name] LIKE IIF(? IS NULL, [Project].[Name], ?)

    """
    for i in range(len(project_input)-1):
        projectinput_sql += """
        OR
        [Project].[Name] LIKE IIF(? IS NULL, [Project].[Name], ?)        

        """

    projectinput_sql += ')'

    countryinput_sql = """
    AND
    ([Project].[Country] LIKE IIF(? IS NULL, [Project].[Country], ?)

    """

    for i in range(len(country_input)-1):
        countryinput_sql +="""
        OR
        [Project].[Country] LIKE IIF(? IS NULL, [Project].[Country], ?)     

        """

    countryinput_sql += ')'

    continentinput_sql = """
    AND
    ([Project].[Continent] LIKE IIF(? IS NULL, [Project].[Continent], ?)    
    """

    for i in range(len(continent_input)-1):
        continentinput_sql +="""
        OR
        [Project].[Continent] LIKE IIF(? IS NULL, [Project].[Continent], ?)     

        """

    continentinput_sql += ')'    

    if studytype_input[0] == '':
        studytypeinput_sql = """
        """
    else:
        studytypeinput_sql = """
        AND
        ([Project].[StudyType] = ?    
        """

        for i in range(len(studytype_input)-1):
            studytypeinput_sql += """
            OR
            [Project].[StudyType] = ?     

            """
        studytypeinput_sql += ')' 

    hpmtypeinput_sql = """
    AND
    ([Project].[HPM Type] LIKE IIF(? IS NULL, [Project].[HPM Type], ?)    
    """

    for i in range(len(hpmtype_input)-1):
        hpmtypeinput_sql += """
        OR
        [Project].[HPM Type] LIKE IIF(? IS NULL, [Project].[HPM Type], ?)     

        """
    hpmtypeinput_sql += ')'    

    otherinputs_sql = """

    AND
    [Project].[HPM Type] LIKE IIF(? IS NULL, [Project].[HPM Type], ?)

    """

    if greenbrownfield_input == '':
        gbtypeinput_sql = """
        """
    else:
        gbtypeinput_sql = """
    
        AND
        [Project].[SiteConditions] LIKE IIF(? IS NULL, [Project].[SiteConditions], ?)
        """

    if acidalkaline_input == '':
        phtypeinput_sql = """
        """
    
    else:
        phtypeinput_sql = """
    
        AND
        [Autoclave].[Acid/Alkaline] LIKE IIF(? IS NULL, [Autoclave].[Acid/Alkaline], ?)
        """

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



    """ + projectinput_sql + countryinput_sql + continentinput_sql + studytypeinput_sql + hpmtypeinput_sql + phtypeinput_sql + gbtypeinput_sql + tempset_sql + pressset_sql + oreset_sql + sulphset_sql + resrvset_sql

    # Execute query to records with called variables

    # define default range params

    rangeparams = []

    for i in range(len(projectparam)):
        rangeparams.append(projectparam[i])

    for i in range(len(countryparam)):
        rangeparams.append(countryparam[i])

    for i in range(len(continentparam)):
        rangeparams.append(continentparam[i])  

    if studytype_input[0] != '':

        for i in range (len(studytypeparam)):
            rangeparams.append(studytypeparam[i])  

    for i in range (len(hpmtypeparam)):
        rangeparams.append(hpmtypeparam[i]) 

    # acid and gbfield do not require 

    if greenbrownfield_input:
        rangeparams.append(greenbrownfield_input)
        rangeparams.append(greenbrownfieldparam)  
  
    if acidalkaline_input:
        rangeparams.append(acidalkaline_input)
        rangeparams.append(acidalkalineparam)

    # if statements: adding range inputs onto the params variable if applicable

    ## temperature range called variable appending to rangeparams list

    if temp_checkinput is True:
        rangeparams = rangeparams
    else:
        rangeparams.append(temprangelow)
        rangeparams.append(temprangehigh)

    ## pressure range called variable appending to rangeparams list

    if press_checkinput is True:
        rangeparams = rangeparams
    else:
        rangeparams.append(pressrangelow)
        rangeparams.append(pressrangehigh)

    ## ore throughput range called variable appending to rangeparams list

    if ore_checkinput is True:
        rangeparams = rangeparams
    else:
        rangeparams.append(orerangelow)
        rangeparams.append(orerangehigh)

    ## feed sulphur range called variable appending to rangeparams list

    if sulph_checkinput is True:
        rangeparams = rangeparams
    else:
        rangeparams.append(sulphrangelow)
        rangeparams.append(sulphrangehigh)

    ## total reserves range called variable appending to rangeparams list

    if resrv_checkinput is True:
        rangeparams = rangeparams
    else:
        rangeparams.append(resrvrangelow)
        rangeparams.append(resrvrangehigh)

    # execute query to records with called variables

    records = cursor.execute(sql_filterquery,rangeparams).fetchall()

    st.write(rangeparams)
    # define record column names

    columns = [column[0] for column in cursor.description]

    filterparam_data = {
        "Project": project_input,
        "Country": country_input,
        "Continent": continent_input,
        "Study Type": studytype_input,
        "Process Type": hpmtype_input,
        "Payable Metal": NULL
    }

    filterparam_df = pd.DataFrame([])

    # dump records into a dataframe

    project_dump = pd.DataFrame.from_records(
        data=records,
        columns=columns,
    )

    # setting database index as dataframe index

    project_dump.set_index(['ID'], inplace=True)

    # addressing unnecessary decimals

    project_dump = project_dump.fillna({'Date of information':0})
    project_dump = project_dump.astype({'Date of information': int})

    project_dump = project_dump.fillna({'No of Processing Years':0})
    project_dump = project_dump.astype({'No of Processing Years': int})

    project_dump = project_dump.fillna({'OperatingPressure':0})
    project_dump = project_dump.astype({'OperatingPressure': int})

    project_dump = project_dump.fillna({'OperatingTemp':0})
    project_dump = project_dump.astype({'OperatingTemp': int})

    project_dump = project_dump.fillna({'OreTreatmentRate':0})
    project_dump = project_dump.astype({'OreTreatmentRate': int})

    project_dump = project_dump.fillna({'Initial Capex':0})

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


    if payablemetal_input[0] != '':
        if len(payablemetal_input) == 1:
            project_dump = project_dump[project_dump['Payable Metal'].str.contains(payablemetal_input[0])]

        elif len(payablemetal_input) == 2:
            project_dump = project_dump[project_dump['Payable Metal'].str.contains(payablemetal_input[0]) |
            project_dump['Payable Metal'].str.contains(payablemetal_input[1])]

        elif len(payablemetal_input) == 3:
            project_dump = project_dump[project_dump['Payable Metal'].str.contains(payablemetal_input[0]) |
            project_dump['Payable Metal'].str.contains(payablemetal_input[1]) | project_dump['Payable Metal'].str.contains(payablemetal_input[2])]

        elif len(payablemetal_input) == 4:
            project_dump = project_dump[project_dump['Payable Metal'].str.contains(payablemetal_input[0]) |
            project_dump['Payable Metal'].str.contains(payablemetal_input[1]) | project_dump['Payable Metal'].str.contains(payablemetal_input[2]) |
            project_dump['Payable Metal'].str.contains(payablemetal_input[3])]    

        elif len(payablemetal_input) == 5:
            project_dump = project_dump[project_dump['Payable Metal'].str.contains(payablemetal_input[0]) |
            project_dump['Payable Metal'].str.contains(payablemetal_input[1]) | project_dump['Payable Metal'].str.contains(payablemetal_input[2]) |
            project_dump['Payable Metal'].str.contains(payablemetal_input[3]) | project_dump['Payable Metal'].str.contains(payablemetal_input[4])]   

    # display query results

    st.write('Temperature ('+degree_sign+'C) between' ,temp_range,'Pressure (kPa) between', press_range,'Throughput (t/a) between', ore_range,
    'Sulphur Feed (%) between', sulph_range,'Total Reserves (Mt) between', resrv_range)

    st.write("""
        ## Filter Query

        ##### Based on above selections:


    """)

    #Column select for query

    selectall_toggle = st.checkbox(label='Select all', value=False)

    col1, col2, col3, col4, col5, col6, col7 = st.columns(7)

    with col1:
        studytype_column = st.checkbox(label='Study Type', value=selectall_toggle)
        pressure_column = st.checkbox(label='Operating Pressure', value=selectall_toggle)
    with col2:
        country_column = st.checkbox(label='Country', value=selectall_toggle)
        temp_column = st.checkbox(label='Operating Temperature', value=selectall_toggle)
    with col3:
        continent_column =st.checkbox(label='Continent', value=selectall_toggle)
        sulphur_column = st.checkbox(label='Feed Sulphur %', value=selectall_toggle)
    with col4:
        metal_column = st.checkbox(label='Payable Metal', value=selectall_toggle)
        acid_column = st.checkbox(label='Acid/Alkaline', value=selectall_toggle)
    with col5:
        gbfield_column = st.checkbox(label='Site Conditions', value=selectall_toggle)
        orerate_column = st.checkbox(label='Treatment Rate', value=selectall_toggle)
    with col6:
        process_column = st.checkbox(label='Process Type', value=selectall_toggle)
        reserves_column = st.checkbox(label='Total Reserves', value=selectall_toggle)
    with col7:
        yearsop_column = st.checkbox(label='Process Years', value=selectall_toggle)
        capex_column = st.checkbox(label='Initial CAPEX', value=selectall_toggle)

    if studytype_column == False:
        project_dump = project_dump.drop(columns='Study Type')
    if pressure_column == False:
        project_dump = project_dump.drop(columns='Operating Pressure (kPa)')
    if country_column == False:
        project_dump = project_dump.drop(columns='Country')
    if temp_column == False:
        project_dump = project_dump.drop(columns='Operating Temperature ('+degree_sign+'C)')
    if continent_column == False:
        project_dump = project_dump.drop(columns='Continent')
    if sulphur_column == False:
        project_dump = project_dump.drop(columns='Feed Sulphur (%)')
    if metal_column == False:
        project_dump = project_dump.drop(columns='Payable Metal')
    if acid_column == False:
        project_dump = project_dump.drop(columns='Acid/Alkaline')
    if gbfield_column == False:
        project_dump = project_dump.drop(columns='Site Conditions')
    if orerate_column == False:
        project_dump = project_dump.drop(columns='Ore Treatment Rate (t/a)')
    if process_column == False:
        project_dump = project_dump.drop(columns='Process Type')
    if yearsop_column == False:
        project_dump = project_dump.drop(columns='No of Processing Years')
    if reserves_column == False:
        project_dump = project_dump.drop(columns='Total Reserves (Mt)')
    if capex_column == False:
        project_dump = project_dump.drop(columns='Initial Capital Cost (USD$)')

    st._legacy_dataframe(project_dump, width=50000, height=700)

    # download csv of results

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
    def convert_df(df):
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


# Authentication
if st.session_state.user or st.session_state.dev:
    main()
else:
    st.write("Please enter a valid password")
    password_manager(cursor)
