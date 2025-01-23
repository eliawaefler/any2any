import os
import uuid

import streamlit as st
import pandas as pd

import neon
import login
import data_handling
import json

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
    quell, map, ziel = st.columns(3)
    with quell:
        for q in neon.read_db(CONN, f"{sst.username}_Quelle"):
            st.write(q[3])
    with map:
        for m in neon.read_db(CONN, f"{sst.username}_Mapper"):
            st.write(m)
    with ziel:
        for z in neon.read_db(CONN, f"{sst.username}_Ziel"):
            st.write(z[3])
def display_user_new_file():
    new_file = st.file_uploader("upload new file")
    if new_file:
        new_file_type = st.selectbox("select file type", options=["Quelle", "Ziel", "Transferdaten", "Mapper"])
        st.write(new_file_type)
        if new_file_type == "mapper":
            if st.button("add to my mappers"):
                if neon.write_to_db(CONN, f"{sst.username}_mappers",
                                    {new_file.name: {new_file.read()}}) == "success":
                    st.success("mapper added")
                    st.rerun()
                else:
                    st.error("could not add mapper")
        elif new_file_type in ["Quelle", "Ziel"]:
            if st.button("add to my FDM"):
                with st.spinner("Processing file..."):
                    entities = data_handling.extract_entity_attributes(new_file)
                    if not entities:
                        st.error(f"could not add {new_file_type}")
                        st.rerun()
                    else:
                        for entity, attributes in entities.items():
                            json_attributes = json.dumps(attributes)
                            data = { 'guid': str(uuid.uuid4()),
                                    "api": "na",
                                    "file_name": new_file.name,
                                    "entity_name": str(entity),
                                    "entity_attributes": json_attributes
                                    }
                            if neon.write_to_db(CONN, f"{sst.username}_{new_file_type}", data) != "success":
                                st.error(f"could not add {new_file_type}")
                                st.rerun()
                        st.success(f"{new_file_type} hinzugefügt")
                        st.rerun()

        elif new_file_type == "Transferdaten":
            # add logic to select
            this_mapper = st.selectbox("MAPPER: ", options=[])  # get my MAPPERs
            this_ziel = st.selectbox("ZIEL: ", options=[])  # get my ZIELs
            if st.button("EXECUTE"):
                # add transfer logic
                pass


def display_user_home():
    a, b = st.columns(2)
    with a:
        display_user_fdm()
    with b:
        if st.button("Create new Mapper"):
            sst.page = "user_create_mapper"
            st.rerun()
        st.write()
        st.write("or")
        st.write()
        display_user_new_file()

def display_user_new_mapper():

    if "mapping_table" not in sst:
        sst.mapping_table = []
    if "mapper_name" not in sst:
        sst.mapper_name = str(uuid.uuid4())
    if "quell_cols" not in sst:
        sst.quell_cols = []
    if "ziel_cols" not in sst:
        sst.ziel_cols = []

    st.subheader("NEW MAPPER")
    rules = neon.read_db(CONN, "rules")
    rule_names = [r[1] for r in rules]
    rule_infos = [r[2] for r in rules]

    quellen = neon.read_db(CONN, f"{sst.username}_Quelle")
    quell_namen = [q[3] for q in quellen]
    ziele = neon.read_db(CONN, f"{sst.username}_Ziel")
    ziel_namen = [z[3] for z in ziele]

    if st.toggle("show rule information"):
        st.subheader("Rule Information")
        for rule_n in range(len(rules)):
            l, r = st.columns(2)
            with l:
                st.write(rules[rule_n])
            with r:
                st.write(rule_infos[rule_n])

    add_c1, add_c2, add_c3 = st.columns(3)
    with add_c1:
        quell_entity = st.selectbox("Quelle", quell_namen)

    with add_c2:
        a, l, r = st.columns([1, 1, 2])
        with l:
            st.subheader("")
            st.subheader(":twisted_rightwards_arrows:")
        with r:
            sst.mapper_name = st.text_input("mapper name: ")
    with add_c3:
        ziel_entity = st.selectbox("Ziel", ziel_namen)


    if st.button("create mapper table"):
        sst.mapping_table = []
        sst.quell_cols = quellen[quell_namen.index(quell_entity)][4]
        sst.ziel_cols = ziele[ziel_namen.index(ziel_entity)][4]
        sst.new_mapper = True

    if sst.new_mapper:
        for column in sst.quell_cols:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.text("")
                st.subheader(f"QUELLE: {column}")
            with col2:
                l, r = st.columns(2)
                with l:
                    my_rule = st.selectbox(
                        f"Select Rule",
                        rule_names,
                        key=f"rule_{quell_entity}_{column}"
                    )
                with r:
                    my_rule_param = st.text_input(
                        f"Rule Param",
                        key=f"rule_param_{quell_entity}_{column}"
                    )
            with col3:
                my_ziel_column = st.selectbox(
                    f"Select ZIEL Column",
                    sst.ziel_cols,
                    key=f"ziel_column_{ziel_entity}_{column}"
                )
            sst.mapping_table.append({
                "Quelle_Sheet": quell_entity,
                "Quelle_Column": column,
                "Transformation_Rule": my_rule,
                "Transformation_Rule_param": my_rule_param,
                "Ziel_Sheet": ziel_entity,
                "Ziel_Column": my_ziel_column,
            })

        # Display the mapping table
        if st.button("save Mapper"):
            data = {"guid": str(uuid.uuid4()),
                    "name": sst.mapper_name,
                    "data": sst.mapping_table}
            if neon.write_to_db(CONN, f"{sst.username}_mapper", data) == "success":
                st.success("mapper saved")
            else:
                st.error("couldn't save mapper")


def display_user_execute():
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
        layout="centered"  # 'centered' or 'wide'
    )
    if "user_logged_in" not in sst:
        sst.user_logged_in = False
    if "username" not in sst:
        sst.username = False
    if "page" not in sst:
        sst.page = "welcome"
    if "new_mapper" not in sst:
        sst.new_mapper = False

    st.write(f"login: {sst.user_logged_in}")
    st.write(f"username: {sst.username}")
    st.write(f"page: {sst.page}")

    hauptbereich, rechts, ganz_rechts = st.columns([12, 2, 2])
    if sst.user_logged_in:
        with hauptbereich:
            st.title(f"hello {sst.username}")
            st.title(f"")
        with rechts:
            if st.button("home"):
                sst.page = "user_home"
                st.rerun()
        with ganz_rechts:
            if st.button("logout"):
                sst.user_logged_in = False
                sst.page = "home"
                st.rerun()
        if sst.page == "user_home":
            display_user_home()
        elif sst.page == "user_fdm":
            display_user_fdm()
        elif sst.page == "user_create_mapper":
            display_user_new_mapper()
        elif sst.page == "user_execute":
            display_user_execute()
    else: # not LOGGED IN
        with hauptbereich:
            st.title(f"any2any")
            st.title(f"")
        with rechts:
            if st.button("home"):
                sst.page = "user_home"
                st.rerun()
        if sst.page == "login":
            with ganz_rechts:
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
            with ganz_rechts:
                if st.button("login"):
                    sst.page = "login"
                    st.rerun()
            login.display_forgot_pw()
        elif sst.page == "sign-up":
            with ganz_rechts:
                if st.button("login"):
                    sst.page = "login"
                    st.rerun()
            login.display_signup()
        else:
            with ganz_rechts:
                if st.button("login"):
                    sst.page = "login"
                    st.rerun()
            display_welcome()

if __name__ == "__main__":
    #CONN = os.environ["NEON_KEY"]
    CONN = os.environ["NEON_URL_any"]
    sst = st.session_state
    main()
