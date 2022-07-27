import streamlit as st
import pandas as pd


def password_manager(cursor, clearance='user'):
    sql_pullpass = """
    SELECT [Location], [Password]
    FROM [ProjectDetailDatabase].[dbo].[Passbook]

    """

    rdevpass = cursor.execute(sql_pullpass)

    columns = ['Location', 'Pass']

    passdf = pd.DataFrame.from_records(
        data=rdevpass,
        columns=columns
    )

    devpass = passdf.loc[passdf['Location'] == 'HPM Process Database Viewer Developer']['Pass'].item()
    userpass = passdf.loc[passdf['Location'] == 'HPM Process Database Viewer']['Pass'].item()



    # Define empty page block when password not filled

    def generate_login_block():
        block1 = st.empty()
        block2 = st.empty()

        return block1, block2


    def clean_blocks(blocks):
        for block in blocks:
            block.empty()

    # defining login sequence

    def login(blocks):
        blocks[0].markdown("""
                <style>
                    input {
                        -webkit-text-security: disc;
                    }
                </style>
            """, unsafe_allow_html=True)

        return blocks[1].text_input('Password:')

    if "unlock" not in st.session_state:
        st.session_state.unlock = False

    login_blocks = generate_login_block()
    password = login(login_blocks)
    
    if password == devpass:
        st.session_state.dev = True
        st.experimental_rerun()
    elif password == userpass:
        if clearance == 'dev':
            st.error("You did not enter the dev password")
        elif clearance == 'user':
            st.session_state.user = True
            st.experimental_rerun()
        else:
            st.warning
        
    elif password == "":
        st.write("Please enter a password")    
    else:
        st.error("You did not enter a valid password")

    
