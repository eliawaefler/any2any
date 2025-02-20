
"""
Streamlit frontend für any2any
"""

import os
import time
import uuid
import streamlit as st
import pandas as pd
from streamlit.file_util import file_in_pythonpath

from utils import neon
from backend import any2any_backend
from backend import neon_login
import json


def get_headers(uploaded_file):
    if uploaded_file:
        excel_data = pd.ExcelFile(uploaded_file)
        sheet_names = excel_data.sheet_names

        tf_detected_headers = {}
        og_detected_headers = {}
        detected_header_vals = {}
        transformations = {}

        tabs = st.tabs(sheet_names)


        for i, sheet_name in enumerate(sheet_names):
            with tabs[i]:
                sst["no_headers"] = False
                st.subheader(f"Sheet: {sheet_name}")  #
                original_sheet_df = pd.read_excel(excel_data, sheet_name=sheet_name, header=None)
                s_inputs, abstand1, og_df, abstand2, t_df = st.columns([4, 1, 3, 1, 3])
                with s_inputs:

                    use_this = st.toggle(f"use this sheet: {sheet_name}",
                                         key=f"use_entity_{sheet_name}", value=True)
                    if use_this:

                        tab_left, tab_right = st.columns(2)
                        with tab_left:
                            headers_in_row = st.toggle(f"{sheet_name} \n\ncontains headers in a row",
                                                       key=f"headers_in_row_{sheet_name}", value=True)
                            headers_in_col = st.toggle(f"{sheet_name}  \ncontains headers in a column",
                                                       key=f"headers_in_col_{sheet_name}")
                        with tab_right:
                            more_dimensions = st.toggle(f"{sheet_name}  \nhas more than two dimensions",
                                                        key=f"more_dimensions_in_{sheet_name}")
                            more_entities = st.toggle(f"{sheet_name}  \nhas more than one entity",
                                                        key=f"more_ENTITIES_in_{sheet_name}")
                        if more_entities:
                            st.warning("this feature is not yet implemented, please clean your excel files")
                        if more_dimensions:
                            st.warning("this feature is not yet implemented, please clean your excel files")
                        header_locations = []
                        header_vals = []
                        #colors = ["yellow", "lightblue", "light green", "light coral"]
                        transformations[sheet_name] = {}
                        # 2d case
                        if headers_in_col and headers_in_row:
                            st.warning("work in progress")
                            dimensions = {}

                            n_dim = 2
                            if more_dimensions:
                                n_dim = int(st.slider(f"Number of dimensions for {sheet_name}", 3, 10))
                            transformations[sheet_name]["case"] = "2d"
                            transformations[sheet_name]["dimensions"] = {}

                            #highlights = [("blue", (int(data_x-1), int(data_y-1)))]
                            for n in range(n_dim):
                                dim_start = [0, 0]
                                dim_end = [0, 1]
                                a, b, c, d, e = st.columns([2, 1, 1, 1, 1])
                                with a:
                                    st.write(" ")
                                    dim_name = st.text_input(f"Name of Dimension {n}", key=f"dim_name_{n}_{sheet_name}", value="DimensionX")
                                with b:
                                    dim_start[0] = int(st.number_input(f"Start row for Dimension {n}", key=f"start_row_{n}_{sheet_name}", step=1, value=0))
                                with c:
                                    dim_start[1] = int(st.number_input(f"Start col for Dimension {n}", key=f"start_col_{n}_{sheet_name}", step=1, value=1))
                                with d:
                                    dim_end[0] = int(st.number_input(f"End row for Dimension {n}", key=f"end_row_{n}_{sheet_name}", step=1, value=0))
                                with e:
                                    dim_end[1] = int(st.number_input(f"End col for Dimension {n}", key=f"end_col_{n}_{sheet_name}", step=1, value=len(original_sheet_df.columns)-1))

                                list_of_cells = any2any_backend.get_cells_in_range(dim_start, dim_end)
                                #highlights.append((colors[n % len(colors)], list_of_cells))

                                dimensions[dim_name] = list_of_cells
                                transformations[sheet_name]["dimensions"][dim_name] = list_of_cells
                                for e in list_of_cells:
                                    header_locations.append(e)
                            header_locations = list(set(header_locations))

                            #tf_detected_headers[sheet_name] = [(0, 0), (0, 1)] + [(0, _) for _ in range(2, n_dim+2)]
                            tf_detected_headers[sheet_name] = header_locations
                            og_detected_headers[sheet_name] = tf_detected_headers[sheet_name]
                            detected_header_vals[sheet_name] = [original_sheet_df.iloc[h_loc] for h_loc in header_locations]
                            #transformed_df = any2any_backend.standardize_dataframe(original_sheet_df, dimensions)

                        # transpose
                        elif headers_in_col and not headers_in_row:
                            transformations[sheet_name]["case"] = "transpose"
                            with tab_left:
                                header_col = st.selectbox(f"Select header column for {sheet_name}",
                                                          options=list(range(len(original_sheet_df.columns))),
                                                          index=0, key=f"header_col_{sheet_name}")
                            with tab_right:
                                header_offset = st.selectbox(f"Offset for headers in {sheet_name}",
                                                             options=list(range(10)), index=0,
                                                             key=f"header_offset_{sheet_name}")
                            for row in range(header_offset, len(original_sheet_df)):
                                header_locations.append((row, header_col))
                                header_vals.append(original_sheet_df.iloc[row, header_col])
                            transformations[sheet_name]["h_col"] = header_col
                            transformations[sheet_name]["h_off"] = header_offset
                            #transformed_df = original_sheet_df.T.iloc[transformations[sheet_name]["h_col"]:].iloc[:, transformations[sheet_name]["h_off"]:]
                            tf_detected_headers[sheet_name] = [(b, a) for a, b in header_locations]
                            detected_header_vals[sheet_name] = header_vals
                            og_detected_headers[sheet_name] = header_locations


                        # basic case
                        elif headers_in_row and not headers_in_col:
                            transformations[sheet_name]["case"] = "basic"
                            with tab_left:
                                header_row = st.selectbox(f"Select header row for {sheet_name}",
                                                          options=list(range(len(original_sheet_df))),
                                                          index=0, key=f"header_row_{sheet_name}")
                            with tab_right:
                                header_offset = st.selectbox(f"Offset for headers in {sheet_name}",
                                                             options=list(range(10)), index=0,
                                                             key=f"header_offset_{sheet_name}")

                            for col in range(header_offset, len(original_sheet_df.columns)):
                                header_locations.append((header_row, col))
                                header_vals.append(original_sheet_df.iloc[header_row, col])
                            transformations[sheet_name]["h_row"] = header_row
                            transformations[sheet_name]["h_off"] = header_offset
                            tf_detected_headers[sheet_name] = header_locations
                            detected_header_vals[sheet_name] = header_vals
                            #transformed_df = original_sheet_df.iloc[transformations[sheet_name]["h_row"]:].iloc[:, transformations[sheet_name]["h_off"]:]
                            og_detected_headers[sheet_name] = tf_detected_headers[sheet_name]


                        # no headers case
                        else:
                            st.error("No headers detected. Please upload another file.")
                            sst.no_headers = True
                            detected_header_vals[sheet_name] = []
                            transformations[sheet_name] = {"case": "basic", "h_row": 0, "h_off": 0}


                    if not sst.no_headers:
                        with og_df:
                            st.write("uploaded DataFrame:")
                            st.dataframe(any2any_backend.highlight_multiple_cells(original_sheet_df, og_detected_headers[sheet_name]))
                        with t_df:
                            st.write("Dataframe with detected headers:")
                            transformed_data = any2any_backend.transform_file(uploaded_file, transformations)
                            for sheet, transformed_df in transformed_data.items():
                                if sheet == sheet_name:
                                    try:
                                        st.dataframe(transformed_df)
                                    except ValueError as e:
                                        st.error(e)
                                    #st.dataframe(any2any_backend.highlight_multiple_cells(transformed_df, tf_detected_headers[sheet_name]))

        if st.button("Confirm Headers for all sheets"):
            re_list = [True, detected_header_vals, transformations]
            return re_list

def display_welcome():

    st.write("transforming data since 2025")
    left, right = st.columns([3, 2])

    with left:
        st.markdown("""
                            ###   Das Problem
                            Die Welt ist voller Daten, aber oft sind diese unstrukturiert, schwer zugänglich oder in Formaten, die nicht kompatibel sind. Unternehmen kämpfen mit ineffizienten Prozessen, Daten-Silos und der mangelnden Fähigkeit, Informationen effektiv zu nutzen.    
                    """)
        st.markdown("""
                            ###   Unsere Lösung
                            any2any werden Daten einfach transformiert und visualisiert. Unsere Plattform vereinfacht komplexe Datenumwandlungen, ermöglicht nahtlose Integration und schafft ein Ökosystem, in dem Datenflüsse effizienter und transparenter werden.
                    """)
        st.markdown("""
                            ###   Jetzt starten
                            Gewinnen Sie die Kontrolle über Ihre Daten zurück!
                   
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


def display_new_api():
    """
    WORK IN PROGRESS
    todo

    :return:
    """


    st.subheader("new API connection")
    systems = list(neon.read_db(CONN, "systems"))
    st.write(f"currently supportet Systems: {[sys[1] for sys in systems]}")
    api_link = st.text_input("link to the API (baseURL)")
    m_name = str(st.text_input("Model name")).replace("%20", " ")
    sys_username = st.text_input("System user name")
    sys_pw = st.text_input("System PW")

    if m_name:
        if sys_username:
            if sys_pw:
                if api_link:
                    if st.button("execute"):
                        st.warning("this is not yet implemented")
                        pass


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
        #if st.button("wizard_go"):
        #    wizard_go() #todo
        st.subheader("erstelle Deinen ersten MAPPER  :twisted_rightwards_arrows:          -->>")
    else:
        st.write("to execute a transformation, upload Transferdaten")
        st.write("")

        st.subheader("MY FDM")
        quell, mapping_route, ziel = st.columns(3)

        with quell:
            st.subheader(":potable_water:")
            quellfiles = list(set([q[2] for q in quellen]))
            for qf in quellfiles:
                st.subheader(qf[:-5])
                if st.toggle(f"show attributes", key=f"{qf}_show"):
                    for q in quellen:
                        if q[2] == qf:
                            st.write(f"{q[3]}")
                    if st.toggle(f"show delete button"):
                        if st.button("delete this QUELLE"):
                            table_name = f"{sst.username}_quelle"
                            if table_name in neon.delete_record(CONN, table_name, "file_name", qf):
                                neon.write_to_db(CONN, "log", {
                                    'guid': str(uuid.uuid4()),
                                    'activity_type': "delete rec",
                                    'activity_desc': f"deleted {qf} FROM {table_name}",
                                    'user_name': sst.username,
                                    'sst': ""})
                                st.success(f"deleted: {qf}")
                                time.sleep(2)
                                st.rerun()
                            else:
                                st.error("something went wrong")

        with mapping_route:
            st.subheader(":twisted_rightwards_arrows:")
            for m in mappers:
                st.write(m[1])
        with ziel:
            st.subheader(":dart:")
            for z in ziele:
                st.write(f"{z[2]}_{z[3]}")


def display_user_new_file(my_file):
    new_file_type = st.selectbox("select file type", options=["quelle", "ziel", "Transferdaten", "mapper"],
                                 index=1) # after a quelle auto ziel
    if new_file_type == "mapper":
        if st.button("add to my mappers"):
            if neon.write_to_db(CONN, f"{sst.username}_{new_file_type}",
                                {my_file.name: {my_file.read()}}) == "success":
                if neon.write_to_db(CONN, "log", {
                    'guid': str(uuid.uuid4()),
                    'activity_type': "safe file",
                    'activity_desc': f"saved {new_file_type} named {my_file.name} TO {sst.username}_{new_file_type}",
                    'user_name': sst.username,
                    'sst': ""}) == "success":
                    st.success("mapper added")
                st.rerun()
            else:
                st.error("could not add mapper")

    elif new_file_type in ["quelle", "ziel"]:
        file_info = get_headers(my_file)
        if file_info and file_info[0]:

            bo, file_structure, transformations = file_info
            data = {"guid": str(uuid.uuid4()),
                    "api": "na",
                    "file_name": my_file.name,
                    "transformations": json.dumps(transformations),
                    "structure": json.dumps(file_structure)
                    }
            if neon.write_to_db(CONN, f"{sst.username}_{new_file_type}", data) == "success":
                if neon.write_to_db(CONN, "log", {
                    'guid': str(uuid.uuid4()),
                    'activity_type': "safe file",
                    'activity_desc': f"saved {new_file_type} named {my_file.name} TO {sst.username}_{new_file_type}",
                    'user_name': sst.username,
                    'sst': ""}) == "success":
                    st.success(f"saved  {my_file.name}")
                else:
                    st.warning("log failed")
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
                if neon.write_to_db(CONN, "log", {
                    'guid': str(uuid.uuid4()),
                    'activity_type': "start transformation",
                    'activity_desc': f"started m={selected_mapper} with z={selected_ziel} with d={my_file.name}",
                    'user_name': sst.username,
                    'sst': ""}) == "success":
                    pass
                transformation, new_df = any2any_backend.execute_mapper_transformation(my_file, this_mapper)

                if transformation:
                    neon.write_to_db(CONN, "log", {
                        'guid': str(uuid.uuid4()),
                        'activity_type': "end transformation",
                        'activity_desc': f"success",
                        'user_name': sst.username,
                        'sst': ""})
                    st.subheader("ZIEL Preview")
                    st.dataframe(new_df)
                    # Provide a download option for the transformed ZIEL
                    ziel_csv = new_df.to_csv(index=False)
                    st.download_button(
                        "Download Transformed ZIEL",
                        ziel_csv,
                        "transformed_ziel.csv",
                        "text/csv",
                        key="download_ziel_csv"
                    )
                else:
                    st.error(new_df)
                    neon.write_to_db(CONN, "log", {
                        'guid': str(uuid.uuid4()),
                        'activity_type': "error",
                        'activity_desc': f"transformation raised {new_df}",
                        'user_name': sst.username,
                        'sst': ""})

        elif selected_ziel == "GTO (read everything)":
            #add logic
            this_ziel = [] #pull FDM
            if st.button("EXECUTE"):
                any2any_backend.execute_gto_transformation(my_file, this_mapper, this_ziel)
        else:
            this_ziel =  next(item[4] for item in all_ziele if item[3] == selected_ziel)
            if st.button("EXECUTE"):
                any2any_backend.execute_ziel_transformation(my_file, this_mapper, this_ziel)


def display_user_home():
    a, b = st.columns(2)
    with a:
        display_user_fdm()
    with b:
        if st.button("Create new Mapper"):
            sst.page = "user_create_mapper"
            sst.quell_ziel_names = ["", ""]
            st.rerun()
        st.write()
        st.write()
        new_file = st.file_uploader("upload new file")
        st.write()
        st.write()
        if st.button("Create connection via API"):
            sst.page = "user_api"
            st.rerun()

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
        st.write("Use Cases")
        st.write(sst.quell_cols["Transformationen"])
        # TODO Fix bug
        st.write("Use Cases")
        for n in range(sst.rows):
            col1, col2, col3, col4, col5, col6 = st.columns(6)

            with col1:
                no_sst_quell_name[n] = st.selectbox(
                    f"Quelle Entity",
                    sst.quell_cols.keys(),
                    key=f"quel_entity_{quelle}_{n}"
                )
            with col2:
                st.write(no_sst_quell_name[n])
                st.write(sst.quell_cols[no_sst_quell_name[n]])

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
                st.write(sst.ziel_cols[no_sst_ziel_name[n]])
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
                    if neon.write_to_db(CONN, "log", {
                        'guid': str(uuid.uuid4()),
                        'activity_type': "safe mapper",
                        'activity_desc': f"saved {sst.mapper_name} TO {sst.username}_mapper",
                        'user_name': sst.username,
                        'sst': ""}) == "success":
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
        sst.quell_ziel_names = ["", ""]

    if "square" not in sst:
        sst.square = [500, 300, 100, "0.3"]

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
    #display_square()
    hauptbereich, login, fgt_pw, register, home = st.columns([12, 2, 2, 2, 2])
    if sst.user_logged_in:
        with hauptbereich:
            st.title(f"hello {sst.username}")
            st.title(f"")
        with home:
            if st.button("home"):
                reset_sst()
                sst.page = "user_home"
                st.rerun()
        with login:
            if st.button("logout"):
                reset_sst()
                sst.user_logged_in = False
                sst.page = "home"
                st.rerun()
        if sst.page == "user_home":
            display_user_home()
        elif sst.page == "user_fdm":
            display_user_fdm()
        elif sst.page == "user_create_mapper":
            display_user_new_mapper()
        elif sst.page == "user_api":
            display_new_api()

    else: # not LOGGED IN
        with hauptbereich:
            st.title(f"any2any")
            st.title(f"")
        with home:
            if st.button("home"):
                sst.page = "user_home"
                st.rerun()
        with fgt_pw:
            if st.button("forgot pw"):
                sst.page = "pw-reset"
                st.rerun()
        with login:
            if st.button("log in"):
                sst.page = "login"
                st.rerun()
        with register:
            if st.button("register"):
                sst.page = "sign-up"
                st.rerun()
        if sst.page == "login":
            reset_sst()
            user = neon_login.display_login()
            if user:
                sst.username = user
                sst.user_logged_in = True
                sst.page = "user_home"
                st.rerun()
        elif sst.page == "pw-reset":
            if neon_login.display_forgot_pw():
                st.success("password changed")
                st.rerun()

        elif sst.page == "sign-up":
            user = neon_login.display_signup()
            if user:
                st.success(f"Konto für {user} wurde erfolgreich erstellt!")
                sst.username = user
                sst.user_logged_in = True
                if any2any_backend.create_user_tables(user):
                    sst.page = "user_home"
                    st.rerun()
        else:
            display_welcome()

sst = st.session_state

if __name__ == "__main__":
    #CONN = os.environ["NEON_KEY"]
    CONN = os.environ["NEON_URL_any"]
    main()
