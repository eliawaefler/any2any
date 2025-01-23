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
                            Die Welt ist voller Daten, aber oft sind diese unstrukturiert, schwer zugänglich oder in Formaten, die nicht kompatibel sind. Unternehmen kämpfen mit ineffizienten Prozessen, Daten-Silos und der mangelnden Fähigkeit, Informationen effektiv zu nutzen. Dies führt zu verpassten Chancen, unnötigen Kosten und langsamer Entscheidungsfindung.    
                    """)
        st.markdown("""
                            ###   Unsere Lösung
                            Mit any2any revolutionieren wir die Art und Weise, wie Daten transformiert und genutzt werden. Unsere Plattform vereinfacht komplexe Datenumwandlungen, ermöglicht nahtlose Integration und schafft ein Ökosystem, in dem Datenflüsse effizienter und transparenter werden. Ob Excel zu JSON, BIM-Daten zu FM-Systemen oder benutzerdefinierte Transformationen – any2any bietet die Werkzeuge, die Sie brauchen, um Daten sinnvoll und gewinnbringend einzusetzen.
                    """)
        st.markdown("""
                            ###   Treten Sie unserer Bewegung bei
                            Schließen Sie sich der any2any-Community an und werden Sie Teil einer Datenrevolution. Gemeinsam gestalten wir eine Zukunft, in der Daten nicht mehr im Weg stehen, sondern den Weg ebnen – für Innovation, Wachstum und Erfolg. Starten Sie heute und erleben Sie die Power von grenzenloser Datenflexibilität.
                   
                            """)
        if st.button("Registrieren"):
            sst.page = "sign-up"
            st.rerun()

    with right:
        st.markdown("""
                            ###   Wie es funktioniert
                            1. Datenquelle hochladen
                            Laden Sie Ihre Daten in jedem beliebigen Format hoch – von CSVs und Tabellen bis hin zu komplexen BIM-Modellen oder APIs.

                            2. Transformation definieren
                            Nutzen Sie unsere benutzerfreundliche Oberfläche, um Regeln und Transformationen festzulegen, oder lassen Sie unsere KI den besten Ansatz für Sie finden.

                            3. Nahtlose Ausgabe
                            Exportieren Sie Ihre Daten in das gewünschte Format, bereit für den nächsten Schritt – ob Integration, Analyse oder direkte Anwendung.

                            4. Wiederholbar und skalierbar
                            Speichern Sie Ihre Workflows, um Datenprozesse zu automatisieren und skalierbar zu machen.
                            """)

def display_user_fdm():
    st.subheader("MY FDM")
    quell, map, ziel = st.columns(3)
    quellen = neon.read_db(CONN, f"{sst.username}_quelle")
    mappers = neon.read_db(CONN, f"{sst.username}_mapper")
    ziele = neon.read_db(CONN, f"{sst.username}_ziel")
    if len(quellen) == 0:
        st.subheader("")
        st.subheader("starte mit dem Upload einer QUELLDATEI. :potable_water:  -->>")
    elif len(ziele) == 0:
        st.subheader("")
        st.subheader("lade eine ZIELDATEI hoch    :dart:              -->>")
    elif len(mappers) == 0:
        st.subheader("erstelle Deinen ersten MAPPER  :twisted_rightwards_arrows:          -->>")
    else:
        with quell:
            st.subheader(":potable_water:")
            for q in quellen:
                st.write(q[3])
        with map:
            st.subheader(":twisted_rightwards_arrows:")
            for m in mappers:
                st.write(m[1])
        with ziel:
            st.subheader(":dart:")
            for z in ziele:
                st.write(z[3])
def display_user_new_file():
    new_file = st.file_uploader("upload new file")
    if new_file:
        new_file_type = st.selectbox("select file type", options=["quelle", "ziel", "Transferdaten", "mapper"])
        st.write(new_file_type)
        if new_file_type == "mapper":
            if st.button("add to my mappers"):
                if neon.write_to_db(CONN, f"{sst.username}_mapper",
                                    {new_file.name: {new_file.read()}}) == "success":
                    st.success("mapper added")
                    st.rerun()
                else:
                    st.error("could not add mapper")
        elif new_file_type in ["quelle", "ziel"]:
            data_stucture = st.selectbox("data structure", ["row0", "row1", "A and row0", "A and row1", "other"])
            if st.button("add to my FDM"):
                with st.spinner("Processing file..."):
                    entities = data_handling.extract_entity_attributes(new_file, data_stucture)
                    if not entities:
                        st.error(f"could not add {new_file_type}")
                        st.rerun()
                    else:
                        for entity, attributes in entities.items():
                            json_attributes = json.dumps(attributes)
                            data = {"guid": str(uuid.uuid4()),
                                    "api": "na",
                                    "file_name": new_file.name,
                                    "entity_name": str(entity),
                                    "entity_attributes": json_attributes
                                    }
                            if neon.write_to_db(CONN, f"{sst.username}_{new_file_type}", data) != "success":
                                st.error(f"could not add {new_file_type}")
                                st.rerun()
                st.rerun()

        elif new_file_type == "Transferdaten":
            # add logic to select
            all_mappers = neon.read_db(CONN, f"{sst.username}_mapper")
            all_ziele = neon.read_db(CONN, f"{sst.username}_ziel")
            selected_mapper = st.selectbox("MAPPER: ", options=[m[1] for m in all_mappers])
            selected_ziel = st.selectbox("ZIEL: ", options=[z[3] for z in all_ziele]+["mapper-defined", "GTO (read only)"])
            this_mapper = json.loads(next(item[2] for item in all_mappers if item[1] == selected_mapper).replace("'", '"'))
            if selected_ziel == "mapper-defined":
                if st.button("EXECUTE"):
                    data_handling.execute_mapper_transformation(new_file, this_mapper)
            elif selected_ziel == "GTO (read everything)":
                #add logic
                this_ziel = [] #pull FDM
                if st.button("EXECUTE"):
                    data_handling.execute_gto_transformation(new_file, this_mapper, this_ziel)
            else:
                this_ziel =  next(item[4] for item in all_ziele if item[3] == selected_ziel)
                if st.button("EXECUTE"):
                    data_handling.execute_ziel_transformation(new_file, this_mapper, this_ziel)

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

    st.subheader("NEW MAPPER")
    rules = neon.read_db(CONN, "rules")
    rule_names = [r[1] for r in rules]
    rule_infos = [r[2] for r in rules]
    rule_param_type = [r[3] for r in rules]

    quellen = neon.read_db(CONN, f"{sst.username}_quelle")
    quell_namen = [q[3] for q in quellen]
    ziele = neon.read_db(CONN, f"{sst.username}_ziel")
    ziel_namen = [z[3] for z in ziele]

    if st.toggle("show rule information"):
        st.subheader("Rule Information")
        for rule_n in range(len(rules)):
            l, r, gr = st.columns([1, 4, 2])
            with l:
                st.write(rule_names[rule_n])
            with r:
                st.write(rule_infos[rule_n])
            with gr:
                st.write(f"Type HINT: {rule_param_type[rule_n]}")

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

    if st.button("create new mapper table"):
        reset_sst()
        sst.mapping_table = []
        sst.quell_cols = quellen[quell_namen.index(quell_entity)][4]
        sst.ziel_cols = ziele[ziel_namen.index(ziel_entity)][4]
        sst.rows = len(sst.quell_cols)

        #sst.sel_quell_col = [None for _ in range(sst.rows)]
        #sst.sel_ziel_col = [None for _ in range(sst.rows)]
        #sst.sel_rule = [None for _ in range(sst.rows)]
        #sst.sel_rule_p = [None for _ in range(sst.rows)]
        sst.new_mapper = True

    if st.button("add row"):
        sst.rows += 1
        #sst.sel_quell_col.append(None)
        #sst.sel_ziel_col.append(None)
        #sst.sel_rule.append(None)
        #sst.sel_rule_p.append(None)

    if sst.new_mapper:
        no_sst_quell_col = [None for _ in range(sst.rows)]
        no_sst_rule = [None for _ in range(sst.rows)]
        no_sst_rule_p = [None for _ in range(sst.rows)]
        no_sst_ziel_col = [None for _ in range(sst.rows)]
        for n in range(sst.rows):
            col1, col2, col3 = st.columns(3)
            with col1:
                no_sst_quell_col[n] = st.selectbox(
                    f"Select Quelle Column",
                    sst.quell_cols,
                    key=f"quel_column_{quell_entity}_{n}"
                )
            with col2:
                l, r = st.columns(2)
                with l:
                    no_sst_rule[n] = st.selectbox(
                        f"Select Rule",
                        rule_names,
                        key=f"rule_{quell_entity}_{n}"
                    )
                with r:
                    no_sst_rule_p[n] = st.text_input(
                        f"Rule Param",
                        key=f"rule_param_{quell_entity}_{n}"
                    )
            with col3:
                no_sst_ziel_col[n] = st.selectbox(
                    f"Select ZIEL Column",
                    sst.ziel_cols,
                    key=f"ziel_column_{ziel_entity}_{n}"
                )

        # Display the mapping table
        if st.button("save Mapper"):
            sst.mapping_table = []
            for n in range(sst.rows):
                sst.mapping_table.append({
                    "Quelle_Sheet": quell_entity,
                    "Quelle_Column": no_sst_quell_col[n],
                    "Transformation_Rule": no_sst_rule[n],
                    "Transformation_Rule_param": no_sst_rule_p[n],
                    "Ziel_Sheet": ziel_entity,
                    "Ziel_Column": no_sst_ziel_col[n],
                })
            data = {"guid": str(uuid.uuid4()),
                    "name": sst.mapper_name,
                    "data": str(sst.mapping_table)}
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
def reset_sst():
    sst.sel_rule_p = []
    sst.sel_rule = []
    sst.sel_quell_col = []
    sst.sel_ziel_col = []
    sst.new_mapper = False
    sst.mapping_table = []
    sst.mapper_name = str(uuid.uuid4())
    sst.quell_cols = []
    sst.ziel_cols = []
    sst.rows = 0
def innit_st_page(debug=False):
    st.set_page_config(
        page_title="any2any",  #:cyclone::hammer_and_pick::recycle:
        page_icon=":twisted_rightwards_arrows:",  # quelle: :potable_water:, ziel: :dart:
        # You can use emojis or path to an image file :repeat: oder :cyclone: :radio_button: :recycle: :hammer_and_pick:
        layout="centered"  # 'centered' or 'wide' :scissors: :arrow_left: :arrow_right:
    )

    if "user_logged_in" not in sst:
        sst.user_logged_in = False
    if "username" not in sst:
        sst.username = False
    if "page" not in sst:
        sst.page = "welcome"

    if "new_mapper" not in sst:
        sst.new_mapper = False
    if "mapping_table" not in sst:
        sst.mapping_table = []
    if "mapper_name" not in sst:
        sst.mapper_name = str(uuid.uuid4())

    if "quell_cols" not in sst:
        sst.quell_cols = []
    if "ziel_cols" not in sst:
        sst.ziel_cols = []
    if "rows" not in sst:
        sst.rows = 0

    if "sel_quell_col" not in sst:
        sst.sel_quell_col = []
    if "sel_ziel_col" not in sst:
        sst.sel_ziel_col = []
    if "sel_rule" not in sst:
        sst.sel_rule = []
    if "sel_rule_p" not in sst:
        sst.sel_rule_p = []

    if debug:
        debug1, debug2, debug3, debug4 = st.columns(4)
        with debug1:
            st.write(f"login: {str(sst.user_logged_in)[:20]}")
            st.write(f"username: {str(sst.username)[:20]}")
            st.write(f"page: {str(sst.page)[:20]}")
        with debug2:
            st.write(f"new_mapper: {str(sst.new_mapper)[:20]}")
            st.write(f"m_table: {str(sst.mapping_table)[:20]}")
            st.write(f"m_name: {str(sst.mapper_name)[:20]}")
        with debug3:
            st.write(f"quell_cols: {str(sst.quell_cols)[:20]}")
            st.write(f"ziel_cols: {str(sst.ziel_cols)[:20]}")
            st.write(f"rows: {str(sst.rows)[:20]}")
        with debug4:
            st.write(f"sel_quel: {str(sst.sel_quell_col)[:20]}")
            st.write(f"sel_ziel: {str(sst.sel_ziel_col)[:20]}")
            st.write(f"sel_rule: {str(sst.sel_rule)[:20]}")
            st.write(f"sel_rule_p: {str(sst.sel_rule_p)[:20]}")
def main():
    innit_st_page(debug=False)
    hauptbereich, rechts, ganz_rechts = st.columns([12, 2, 2])
    if sst.user_logged_in:
        with hauptbereich:
            st.title(f"hello {sst.username}")
            st.title(f"")
        with rechts:
            if st.button("home"):
                reset_sst()
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
