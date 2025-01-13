"""
hier soll so übersichtlich wie möglich das Projekt
 abgehandelt werden,
 möglichst ohne funktionen klassen usw.
 alles komplizierte soll in functionality.py
 teständerung

#TODO: neon connection, RULES


"""

import streamlit as st
import pandas as pd
from functionality import *

# Streamlit app
def main():
    rules = ["1:1", "ignore", "split", "concat", "divide", "multiply", "add"]
    rule_infos = ["schreibt das attribut genau so von Quelle ins Ziel",
                   "das Attribut wird nicht bearbeitet",
                   "das Attribut der Quelle wird aufgeteilt, parameter ist das trennzeichen(in anführungszeichen), oder der trenn-index(zahl). das attribut muss zweimal aus der quelle importiert werden (zwei zeilen) um es in zwei verschiedene ziel attribute zu mappen.",
                   "das Quellattribut wird mit anderen quellattributen in ein Ziel übertragen.",
                   "mathematisch durch parameter Dividieren, Ergebniss ist eine KOMMAZAHL",
                   "mathematisch mit param Multiplizieren",
                   "mathematisch mit param addieren, param kann negativ sein."]
    st.set_page_config(layout="wide")
    if "mapper" not in st.session_state:
        st.session_state.counter = False
    if "create_mapper" not in st.session_state:
        st.session_state.create_mapper = False


    st.write("Excel File Mapper")

    st.write("")
    st.write("")
    st.write("")
    # Step 1: Upload QUELLE and ZIEL files
    st.write("Step 1: Upload Excel Files")
    c1, c2, c3 = st.columns(3)
    with c1:
        uploaded_quelle = st.file_uploader("Upload QUELLE Excel File", type="xlsx", key="quelle")
    with c2:
        uploaded_mapping_table = st.file_uploader("upload mapper table", type="csv", key="mapping_table")
    with c3:
        uploaded_ziel = st.file_uploader("Upload ZIEL Excel File", type="xlsx", key="ziel")

    st.write("")
    st.write("")
    st.write("")
    # create Mapping
    st.write("Step 2: Mapping")
    if st.button("New Mapping Table"):
        if uploaded_quelle and uploaded_ziel:
            st.session_state.create_mapper = True
        else:
            st.warning("upload a QUELLE and a ZIEL")
    if st.session_state.create_mapper:
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
            st.session_state.my_columns = []

            add_c1, add_c2, add_c3, _ = st.columns(4)
            with add_c1:
                if st.button("Add Column"):
                    st.session_state.my_columns.append(f"{st.session_state.add_col}_{len(st.session_state.my_columns)}")
            with add_c2:
                st.session_state.add_col = st.selectbox(
                    f"Additional Quelle Column",
                    columns,
                    key=f"add_quelle_{len(st.session_state.my_columns)}"
                )
            for column in list(columns + st.session_state.my_columns):
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
            st.session_state.mapper = True
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

    st.write("")
    st.write("")
    st.write("")
    st.write("Step 3: execute")
    # Execute transformation
    if st.button("Execute Transformation") and uploaded_mapping_table:
        if not st.session_state.mapper:
            st.error("select or create mapping table")
        else:
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

if __name__ == "__main__":
    main()
