import streamlit as st
import pandas as pd
from openpyxl import load_workbook


# Function to extract entity names and attribute names
def extract_entity_attributes(file):
    entity_details = {}

    if file.name.endswith('.csv'):
        # Read CSV and use the filename as the entity name
        df = pd.read_csv(file)
        entity_name = file.name.split('.')[0]
        attributes = df.columns.tolist()
        entity_details[entity_name] = attributes

    elif file.name.endswith(('.xls', '.xlsx')):
        # Load Excel file
        workbook = load_workbook(file, data_only=True)
        for sheet in workbook.sheetnames:
            sheet_data = pd.DataFrame(workbook[sheet].values)

            if sheet_data.empty:
                continue

            # Check if there's a clear header (row 1)
            headers = sheet_data.iloc[0].dropna().tolist()
            if headers:
                entity_details[sheet] = headers
            else:
                # Fallback for undefined headers (use indexes)
                headers = [f"Column {i + 1}" for i in range(sheet_data.shape[1])]
                entity_details[sheet] = headers

    else:
        st.warning("Uploaded file format is not supported. Please upload a CSV or Excel file.")

    return entity_details



# Streamlit app
def main():
    st.title("Entity and Attribute Extractor")

    uploaded_file = st.file_uploader("Upload a CSV or Excel file", type=["csv", "xls", "xlsx"])

    if uploaded_file:
        with st.spinner("Processing file..."):
            entity_details = extract_entity_attributes(uploaded_file)

        if entity_details:
            st.success("Entities and attributes extracted successfully!")
            for entity, attributes in entity_details.items():
                st.subheader(f"Entity: {entity}")
                st.write("Attributes:")
                st.write(attributes)
        else:
            st.warning("No entities or attributes found in the uploaded file.")


if __name__ == "__main__":
    main()

"""
 AGBs

st.subheader("contact")
st.write("")
st.write("main office")
st.write("ABC str 123")
st.write("1234 Stadt")
st.write("")
st.subheader("AGBs")
st.write("")
st.write("by using our plattform you agree to our AGB.")
st.write("AGB")
st.write("we will sell your data.")
st.write("yes, also on the dark web")
st.write("")>

"""


"""
NOTIZEN

  
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
        quelle_structure = [] #extract_file_structure(uploaded_quelle)
        ziel_structure = [] #extract_file_structure(uploaded_ziel)

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

"""