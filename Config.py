import pyodbc

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

