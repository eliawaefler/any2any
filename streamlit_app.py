"""
hier soll so übersichtlich wie mölgich das Projekt
 abgehandelt werden,
 möglichst ohne funktionen klassen usw.
 alles komplizierte soll in functionality.py
 teständerung


 TODO: requirements.txt
 neon connecten

"""


import streamlit as st
import pandas as pd
from functionality import *

# Streamlit app
def main():
    st.title("Excel File Mapper")

    # Step 1: Upload QUELLE and ZIEL files
    st.header("Step 1: Upload Excel Files")
    c1, c2 = st.columns(2)
    with c1:
        uploaded_quelle = st.file_uploader("Upload QUELLE Excel File", type="xlsx", key="quelle")
    with c2:
        uploaded_ziel = st.file_uploader("Upload ZIEL Excel File", type="xlsx", key="ziel")

    if uploaded_quelle and uploaded_ziel:
        # Extract sheet names and column headers
        st.header("Step 2: Select Mappings")
        quelle_structure = extract_file_structure(uploaded_quelle)
        ziel_structure = extract_file_structure(uploaded_ziel)

        # Display QUELLE structure on the left and ZIEL mapping options on the right
        mapping_table = []
        for sheet, columns in quelle_structure.items():
            st.subheader(f"Mapping for Sheet: {sheet}")
            for column in columns:
                col1, col2, col3 = st.columns(3)

                with col1:
                    st.text(f"QUELLE Column: {column}")

                with col2:
                    ziel_sheet = st.selectbox(
                        f"Select ZIEL Sheet for {sheet} -> {column}",
                        list(ziel_structure.keys()),
                        key=f"ziel_sheet_{sheet}_{column}"
                    )
                with col3:
                    ziel_column = st.selectbox(
                        f"Select ZIEL Column for {sheet} -> {column}",
                        ziel_structure[ziel_sheet],
                        key=f"ziel_column_{sheet}_{column}"
                    )
                    mapping_table.append({
                        "Quelle_File": uploaded_quelle.name,
                        "Quelle_Sheet": sheet,
                        "Quelle_Column": column,
                        "Transformation_Rule": "1:1",
                        "Ziel_File": uploaded_ziel.name,
                        "Ziel_Sheet": ziel_sheet,
                        "Ziel_Column": ziel_column,
                    })

        # Display the mapping table
        if st.button("Generate Mapping Table"):
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

if __name__ == "__main__":
    main()
