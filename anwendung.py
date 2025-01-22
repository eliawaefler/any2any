import json
import os
import time
import streamlit as st
import pandas as pd
from PIL import Image
from sqlalchemy import create_engine, text
# im terminal: streamlit run app.py
import neon
import login

def display_welcome():

    st.write("transforming data since 2025")
    left, right = st.columns([3, 2])

    with left:
        st.markdown("""
                            ###   Das Problem
                            bla bla     
                    """)
        st.markdown("""
                            ###   Unsere Lösung
                            bla bla
                    """)
        st.markdown("""
                            ###   Treten Sie unserer Bewegung bei
                            bla bla                        
                            """)
        if st.button("Registrieren"):
            sst.page = "sign-up"
            st.rerun()

    with right:
        st.markdown("""
                            ###   Wie es funktioniert
                            bla bla
                            """)


def display_user_fdm():
    st.subheader("MY FDM")

def extract_file_structure(file):
    return []

def display_new_mapper():
    st.subheader("NEW MAPPER")
    rules = [] # TEMP
    rule_infos = [] # TEMP
    uploaded_quelle = [] # TEMP
    uploaded_ziel = [] # TEMP
    st.write("Mapping")
    if "create_mapper" not in sst:
        sst["create_mapper"] = False
    if "map_q" not in sst:
        sst["map_q"] = False
    if "map_z" not in sst:
        sst["map_z"] = False
    if "uploaded_quelle" not in sst:
        sst["uploaded_quelle"] = False
    if "uploaded_ziel" not in sst:
        sst["uploaded_ziel"] = False
    if st.button("New Mapping Table"):
        if sst.uploaded_quelle and sst.uploaded_ziel:
            sst.create_mapper = True
        else:
            st.warning("upload a QUELLE and a ZIEL")
    if sst.create_mapper:
        if st.toggle("show rule information"):
            st.subheader("Rule Information")
            for rule_n in range(len(rules)):
                l, r = st.columns(2)
                with l:
                    st.write(rules[rule_n])
                with r:
                    st.write(rule_infos[rule_n])

        st.write("CREATE Mappings")
        quelle_structure = extract_file_structure(uploaded_quelle)
        ziel_structure = extract_file_structure(uploaded_ziel)

        # Display QUELLE structure on the left and ZIEL mapping options on the right
        mapping_table = []
        for sheet, columns in quelle_structure.items():
            st.write(f"Mapping for Sheet: {sheet}")
            sst.my_columns = []

            add_c1, add_c2, add_c3, _ = st.columns(4)
            with add_c1:
                if st.button("Add Column"):
                    sst.my_columns.append(
                        f"{sst.add_col}_{len(sst.my_columns)}")
            with add_c2:
                sst.add_col = st.selectbox(
                    f"Additional Quelle Column",
                    columns,
                    key=f"add_quelle_{len(sst.my_columns)}"
                )
            for column in list(columns + sst.my_columns):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.text(f"QUELLE Column: {column}")
                with col2:
                    l, r = st.columns(2)
                    with l:
                        my_rule = st.selectbox(
                            f"Select Rule",
                            rules,
                            key=f"rule_{sheet}_{column}"
                        )
                    with r:
                        my_rule_param = st.text_input(
                            f"Rule Param",
                            key=f"rule_param_{sheet}_{column}"
                        )
                with col3:
                    l, r = st.columns(2)
                    with l:
                        ziel_sheet = st.selectbox(
                            f"Select ZIEL Sheet",
                            list(ziel_structure.keys()),
                            key=f"Transformation_Rule_{sheet}_{column}"
                        )
                    with r:
                        my_ziel_column = st.selectbox(
                            f"Select ZIEL Column",
                            ziel_structure[ziel_sheet],
                            key=f"ziel_column_{sheet}_{column}"
                        )
                mapping_table.append({
                    "Quelle_File": uploaded_quelle.name,
                    "Quelle_Sheet": sheet,
                    "Quelle_Column": column,
                    "Transformation_Rule": my_rule,
                    "Transformation_Rule_param": my_rule_param,
                    "Ziel_File": uploaded_ziel.name,
                    "Ziel_Sheet": ziel_sheet,
                    "Ziel_Column": my_ziel_column,
                })

        # Display the mapping table
        if st.button("Generate Mapping Table"):
            sst.mapper = True
            mapping_df = pd.DataFrame(mapping_table)
            st.subheader("Mapping Table")
            st.dataframe(mapping_df)

            # Provide a download option for the mapping table
            csv = mapping_df.to_csv(index=False)
            st.download_button(
                "Download Mapping Table",
                csv,
                "mapping_table.csv",
                "text/csv",
                key="download_csv"
            )

def display_execute():
    st.subheader("EXECUTE")
    uploaded_mapping_table = []  # TEMP
    uploaded_quelle = []  # TEMP
    uploaded_ziel = []  # TEMP

    ziel_preview = []

    for mapping in uploaded_mapping_table:
        quelle_df = pd.read_excel(uploaded_quelle, sheet_name=mapping[0])
    ziel_df = pd.read_excel(uploaded_ziel, sheet_name=mapping[6])

    quelle_column = mapping["Quelle_Column"]
    ziel_column = mapping["Ziel_Column"]
    rule = mapping["Transformation_Rule"]
    rule_param = mapping["Transformation_Rule_param"]

    if rule == "1:1":
        ziel_df[ziel_column] = quelle_df[quelle_column]
    elif rule == "split":
        sep = rule_param
        ziel_df[[ziel_column, f"{ziel_column}_extra"]] = quelle_df[quelle_column].str.split(sep, expand=True)
    elif rule == "concat":
        order = [int(i) for i in rule_param.split(",")]
        ziel_df[ziel_column] = quelle_df.iloc[:, order].apply(lambda x: "".join(x.astype(str)), axis=1)
    elif rule == "divide":
        ziel_df[ziel_column] = quelle_df[quelle_column] / float(rule_param)
    elif rule == "multiply":
        ziel_df[ziel_column] = quelle_df[quelle_column] * float(rule_param)
    elif rule == "add":
        ziel_df[ziel_column] = quelle_df[quelle_column] + float(rule_param)

    ziel_preview.append(ziel_df)

    # Combine and display the preview of ZIEL
    combined_preview = pd.concat(ziel_preview)
    st.subheader("ZIEL Preview")
    st.dataframe(combined_preview)

    # Provide a download option for the transformed ZIEL
    ziel_csv = combined_preview.to_csv(index=False)
    st.download_button(
        "Download Transformed ZIEL",
        ziel_csv,
        "transformed_ziel.csv",
        "text/csv",
        key="download_ziel_csv"
    )

def main():
    st.set_page_config(
        page_title="any2any",  #:cyclone::hammer_and_pick::recycle:
        page_icon=":twisted_rightwards_arrows:",
        # You can use emojis or path to an image file :repeat: oder :cyclone: :radio_button: :recycle: :hammer_and_pick:
        layout="wide"  # 'centered' or 'wide'
    )
    if "user_logged_in" not in sst:
        sst.user_logged_in = False
    if "username" not in sst:
        sst.username = False
    if "page" not in sst:
        sst.page = "welcome"

    st.write(f"login: {sst.user_logged_in}")
    st.write(f"username: {sst.username}")
    st.write(f"page: {sst.page}")

    a, b, c = st.columns([15, 1, 1])
    if sst.user_logged_in:
        with a:
            st.title(f"hello {sst.username}")
            st.title(f"")
        with b:
            if st.button("home"):
                sst.page = "user_home"
                st.rerun()
        with c:
            if st.button("logout"):
                sst.user_logged_in = False
                sst.page = "home"
                st.rerun()
        if sst.page == "user_home":
            a, b, c, d = st.columns(4)
            with a:
                if st.button("My FDM"):
                    sst.page = "user_fdm"
                    st.rerun()
            with b:
                if st.button("Create Mapper"):
                    sst.page = "user_create_mapper"
                    st.rerun()
            with c:
                if st.button("execute transformation"):
                    sst.page = "user_execute"
                    st.rerun()
            with d:
                new_file = st.file_uploader("upload new file")
                if new_file:
                    new_file_type = st.selectbox(["mapper", "Quelle Ziel", "Transferdaten"])
                    st.write(new_file_type)
                    if new_file_type:
                        if st.button("add to my FDM"):
                            neon.create_table(CONN, f"{sst.username}_{new_file}")
        elif sst.page == "user_fdm":
            display_user_fdm()
        elif sst.page == "user_create_mapper":
            display_new_mapper()
        elif sst.page == "user_execute":
            display_execute()
    else:
        with a:
            st.title(f"any2any")
            st.title(f"")
        with b:
            if st.button("home"):
                sst.page = "user_home"
                st.rerun()
        if sst.page == "login":
            with c:
                if st.button("forgot pw"):
                    sst.page = "pw-reset"
                    st.rerun()
            user = login.display_login()
            if user:
                sst.username = user
                sst.user_logged_in = True
                sst.page = "user_home"
                st.rerun()
        elif sst.page == "pw-reset":
            with c:
                if st.button("login"):
                    sst.page = "login"
                    st.rerun()
            login.display_forgot_pw()
        elif sst.page == "sign-up":
            with c:
                if st.button("login"):
                    sst.page = "login"
                    st.rerun()
            login.display_signup()
        else:
            with c:
                if st.button("login"):
                    sst.page = "login"
                    st.rerun()
            display_welcome()

if __name__ == "__main__":
    #CONN = os.environ["NEON_KEY"]
    CONN = os.environ["NEON_URL_any"]
    sst = st.session_state
    main()
