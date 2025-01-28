import os
import time
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
        st.write("to execute a transformation, upload Transferdaten")
        st.write("")

        st.subheader("MY FDM")
        quell, map, ziel = st.columns(3)

        with quell:
            st.subheader(":potable_water:")
            for q in quellen:
                st.write(f"{q[2]}_{q[3]}")
        with map:
            st.subheader(":twisted_rightwards_arrows:")
            for m in mappers:
                st.write(m[1])
        with ziel:
            st.subheader(":dart:")
            for z in ziele:
                st.write(f"{z[2]}_{z[3]}")
def display_user_new_file(my_file):
    new_file_type = st.selectbox("select file type", options=["quelle", "ziel", "Transferdaten", "mapper"])
    if new_file_type == "mapper":
        if st.button("add to my mappers"):
            if neon.write_to_db(CONN, f"{sst.username}_mapper",
                                {my_file.name: {my_file.read()}}) == "success":
                st.success("mapper added")
                st.rerun()
            else:
                st.error("could not add mapper")
    elif new_file_type in ["quelle", "ziel"]:
        file_entities = data_handling.get_headers(my_file)
        if file_entities:
            for entity, attributes in file_entities.items():
                json_attributes = json.dumps(attributes)
                data = {"guid": str(uuid.uuid4()),
                        "api": "na",
                        "file_name": my_file.name,
                        "entity_name": str(entity),
                        "entity_attributes": json_attributes
                        }
                if neon.write_to_db(CONN, f"{sst.username}_{new_file_type}", data) == "success":
                    st.success(f"saved  {my_file.name} // {entity}")
                else:
                    st.error(f"could not add {new_file_type}")
                    time.sleep(3)
                    st.rerun()
            time.sleep(3)
            sst.page = "user_home"
            st.rerun()

    elif new_file_type == "Transferdaten":
        # add logic to select
        all_mappers = neon.read_db(CONN, f"{sst.username}_mapper")
        all_ziele = neon.read_db(CONN, f"{sst.username}_ziel")
        selected_mapper = st.selectbox("MAPPER: ", options=[m[1] for m in all_mappers])
        selected_ziel = st.selectbox("ZIEL: ", options=["mapper-defined", "GTO (read only)"]+[z[3] for z in all_ziele])
        this_mapper = json.loads(next(item[2] for item in all_mappers if item[1] == selected_mapper).replace("'", '"'))
        if selected_ziel == "mapper-defined":
            if st.button("EXECUTE"):
                data_handling.execute_mapper_transformation(my_file, this_mapper)
        elif selected_ziel == "GTO (read everything)":
            #add logic
            this_ziel = [] #pull FDM
            if st.button("EXECUTE"):
                data_handling.execute_gto_transformation(my_file, this_mapper, this_ziel)
        else:
            this_ziel =  next(item[4] for item in all_ziele if item[3] == selected_ziel)
            if st.button("EXECUTE"):
                data_handling.execute_ziel_transformation(my_file, this_mapper, this_ziel)
def display_user_home():
    a, b = st.columns(2)
    new_file = False
    with a:
        display_user_fdm()
    with b:
        if st.button("Create new Mapper"):
            sst.page = "user_create_mapper"
            st.rerun()
        st.write()
        st.write("or")
        st.write()
        new_file = st.file_uploader("upload new file")
    if new_file:
        display_user_new_file(new_file)
def display_user_new_mapper():
    st.subheader("NEW MAPPER")
    rules = neon.read_db(CONN, "rules")
    rule_names = ["1:1"] + [s for s in [r[1] for r in rules] if s != "1:1"]
    rule_infos = ["direkter übertrag ohne aktion"] + [s for s in [r[2] for r in rules] if "direkter übertrag" not in s]
    rule_param_type = [r[3] for r in rules]

    quellen = neon.read_db(CONN, f"{sst.username}_quelle")
    quell_file_namen = list(set([q[2] for q in quellen]))
    quell_entity_namen = []
    ziele = neon.read_db(CONN, f"{sst.username}_ziel")
    ziel_file_namen =  list(set([z[2] for z in ziele]))
    ziel_entity_namen = []

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

    quelle = st.selectbox(":potable_water: Quelle", quell_file_namen)
    mapper_name = st.text_input(":twisted_rightwards_arrows: mapper name: ")
    ziel = st.selectbox(":dart: Ziel ", ziel_file_namen)

    if st.button("create new mapper table"):
        sst.quell_ziel_names[0] = quelle
        sst.quell_ziel_names[1] = ziel
        sst.mapper_name = mapper_name
        for q in quellen:
            if q[2] == quelle:
                quell_entity_namen.append(q[3])
        for entity in quell_entity_namen:
            sst.quell_cols[entity] = quellen[quell_entity_namen.index(entity)][4]
        for z in ziele:
            if z[2] == ziel:
                ziel_entity_namen.append(z[3])
        for entity in ziel_entity_namen:
            sst.ziel_cols[entity] = ziele[ziel_entity_namen.index(entity)][4]
        sst.rows = 6
        sst.new_mapper = True

    if sst.new_mapper:
        add_c1, add_c2, add_c3 = st.columns(3)
        quelle, ziel = sst.quell_ziel_names
        with add_c1:
            st.subheader(f":potable_water: {quelle}")
        with add_c2:
            st.subheader(f":twisted_rightwards_arrows: {sst.mapper_name}")
        with add_c3:
            st.subheader(f":dart: {ziel}")
        no_sst_quell_name = [None for _ in range(sst.rows)]
        no_sst_quell_col = [None for _ in range(sst.rows)]
        no_sst_rule = [None for _ in range(sst.rows)]
        no_sst_rule_p = [None for _ in range(sst.rows)]
        no_sst_ziel_name = [None for _ in range(sst.rows)]
        no_sst_ziel_col = [None for _ in range(sst.rows)]
        for n in range(sst.rows):
            col1, col2, col3, col4, col5, col6 = st.columns(6)
            with col1:
                no_sst_quell_name[n] = st.selectbox(
                    f"Quelle Entity",
                    sst.quell_cols.keys(),
                    key=f"quel_entity_{quelle}_{n}"
                )
            with col2:
                no_sst_quell_col[n] = st.selectbox(
                    f"Quelle Column",
                    sst.quell_cols[no_sst_quell_name[n]],
                    key=f"quel_column_{quelle}_{n}"
                )
            with col3:
                no_sst_rule[n] = st.selectbox(
                    f"Rule",
                    rule_names,
                    key=f"rule_{quelle}_{n}"
                )
            with col4:
                no_sst_rule_p[n] = st.text_input(
                    f"Rule Param",
                    key=f"rule_param_{quelle}_{n}"
                )
            with col5:
                no_sst_ziel_name[n] = st.selectbox(
                    f"ZIEL Entity",
                    sst.ziel_cols.keys(),
                    key=f"ziel_entity_{quelle}_{n}"
                )
            with col6:
                no_sst_ziel_col[n] = st.selectbox(
                    f"ZIEL Column",
                    sst.ziel_cols[no_sst_ziel_name[n]],
                    key=f"ziel_column_{quelle}_{n}"
                )
        a, b, c, d = st.columns([2, 1, 1, 8])
        with a:
            # Display the mapping table
            if st.button("save Mapper"):
                sst.mapping_table = []
                for n in range(sst.rows):
                    sst.mapping_table.append({
                        "Quelle_Sheet": no_sst_quell_name[n],
                        "Quelle_Column": no_sst_quell_col[n],
                        "Transformation_Rule": no_sst_rule[n],
                        "Transformation_Rule_param": no_sst_rule_p[n],
                        "Ziel_Sheet": no_sst_ziel_name[n],
                        "Ziel_Column": no_sst_ziel_col[n],
                    })
                data = {"guid": str(uuid.uuid4()),
                        "name": sst.mapper_name,
                        "data": str(sst.mapping_table)}
                if neon.write_to_db(CONN, f"{sst.username}_mapper", data) == "success":
                    st.success("mapper saved")
                else:
                    st.error("couldn't save mapper")
        with b:
            if st.button("add row"):
                sst.rows += 1
                st.rerun()
        with c:
            if st.button("remove row"):
                sst.rows += -1
                st.rerun()

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
    sst.m_name = ""
    sst.quell_ziel_names = ["", ""]
    sst.quell_cols = {}
    sst.ziel_cols = {}
    sst.rows = 0
def innit_st_page(debug=False):
    st.set_page_config(
        page_title="any2any",  #:cyclone::hammer_and_pick::recycle:
        page_icon=":twisted_rightwards_arrows:",  # quelle: :potable_water:, ziel: :dart:
        # You can use emojis or path to an image file :repeat: oder :cyclone: :radio_button: :recycle: :hammer_and_pick:
        layout="wide" # "centered"  # 'centered' or 'wide' :scissors: :arrow_left: :arrow_right:
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
    if "quell_ziel_names" not in sst:
        sst.quell_ziel_names = []

    if debug:
        debug1, debug2, debug3, debug4, debug5 = st.columns(5)
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
        with debug5:
            st.write(f"quell_ziel_names: {str(sst.quell_ziel_names)[:20]}")
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
