import streamlit as st
import pandas as pd
from openpyxl import load_workbook


# Function to extract entity names and attribute names
def extract_entity_attributes(file, structure="other"):
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

            headers = False
            if structure == "other":
                # Check if there's a clear header (row 1)
                headers = sheet_data.iloc[0].dropna().tolist()
            elif structure == "row0":
                headers = sheet_data.iloc[0].dropna().tolist()
            elif structure == "row1":
                headers = sheet_data.iloc[1].dropna().tolist()
            if headers:
                entity_details[sheet] = headers
            else:
                # Fallback for undefined headers (use indexes)
                headers = [f"Column {i + 1}" for i in range(sheet_data.shape[1])]
                entity_details[sheet] = headers

    else:
        st.warning("Uploaded file format is not supported. Please upload a CSV or Excel file.")

    return entity_details

def execute_gto_transformation(data, mapper, gto):
    pass

def execute_ziel_transformation(data, mapper, ziel):
    pass

def execute_mapper_transformation(data, mapper):
    unique_quell_sheets = []
    for n in range(len(mapper)):
        sheetname = mapper[n]["Quelle_Sheet"]
        if sheetname not in unique_quell_sheets:
            unique_quell_sheets.append(sheetname)
    quelle_df = pd.read_excel(data, sheet_name=unique_quell_sheets)

    ziel_df = pd.DataFrame()

    for entry in mapper:
        quelle_sheet = entry['Quelle_Sheet']
        quelle_column = entry['Quelle_Column']
        transformation_rule = entry['Transformation_Rule']
        transformation_param = entry['Transformation_Rule_param']
        ziel_sheet = entry['Ziel_Sheet']
        ziel_column = entry['Ziel_Column']

        # Get the relevant source DataFrame
        source_df = quelle_df[quelle_sheet]

        # Perform the transformation based on the rule
        if transformation_rule == '1:1':
            ziel_df[ziel_column] = source_df[quelle_column]
        elif transformation_rule == 'multiply':
            ziel_df[ziel_column] = source_df[quelle_column] * float(transformation_param)
        elif transformation_rule == "cut_left":
            ziel_df[ziel_column] = source_df[quelle_column].str.split(transformation_param, expand=True)
        elif transformation_rule == "cut_sep_right":
            # LINKS RECHTS LOGIK FEHLT
            ziel_df[ziel_column] = source_df[quelle_column].str.split(transformation_param, expand=True)
        elif transformation_rule == "cut_sep_left":
            ziel_df[ziel_column] = source_df[quelle_column].str.split(transformation_param, expand=True)
        elif transformation_rule == "cut_right":
            ziel_df[ziel_column] = source_df[quelle_column].str.split(transformation_param, expand=True)
        elif transformation_rule == "concat":
            order = [int(i) for i in transformation_param.split(",")]
            ziel_df[ziel_column] = source_df.iloc[:, order].apply(lambda x: "".join(x.astype(str)), axis=1)
        elif transformation_rule == "add":
            ziel_df[ziel_column] = source_df[quelle_column] + float(transformation_param)

    st.subheader("ZIEL Preview")
    st.dataframe(ziel_df)
    # Provide a download option for the transformed ZIEL
    ziel_csv = ziel_df.to_csv(index=False)
    st.download_button(
        "Download Transformed ZIEL",
        ziel_csv,
        "transformed_ziel.csv",
        "text/csv",
        key="download_ziel_csv"
    )


def execute_transformation_old(data, mapper, ziel):
    ziel_preview = []
    ziel_df = pd.DataFrame(columns=ziel)



    unique_quell_sheets = []
    for n in range(len(mapper)):
        sheetname = mapper[n]["Quelle_Sheet"]
        if sheetname not in unique_quell_sheets:
            unique_quell_sheets.append(sheetname)

    quelle_df = pd.read_excel(data, sheet_name=unique_quell_sheets)
    for entity in quelle_df:
        for record in entity:
            st.write(record)
    """
        quelle = pd.read_excel(data, sheet_name=mapper[row]["Quelle_Sheet"])
        #quelle_df = pd.read_excel(data, sheet_name=mapper)

    st.write(ziel_df)

    mapping = []
    quelle_column = mapping["Quelle_Column"]
    ziel_column = mapping["Ziel_Column"]
    rule = mapping["Transformation_Rule"]
    rule_param = mapping["Transformation_Rule_param"]

    if rule == "1:1":
        ziel_df[ziel_column] = quelle_df[quelle_column]

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
    #main()
    my_mapper = [{'Quelle_Sheet': 'meine_räume', 'Quelle_Column': None, 'Transformation_Rule': None,
                  'Transformation_Rule_param': None, 'Ziel_Sheet': 'ROOMS', 'Ziel_Column': None},
                 {'Quelle_Sheet': 'meine_räume', 'Quelle_Column': 'Fläche', 'Transformation_Rule':
                     'multiply', 'Transformation_Rule_param': '100', 'Ziel_Sheet': 'ROOMS', 'Ziel_Column': 'Bodenfläche'}]
    print(len(my_mapper))



def other_rules():
   


"""