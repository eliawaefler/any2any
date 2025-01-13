import json
import time
import streamlit as st
from PIL import Image
from sqlalchemy import create_engine, text
# im terminal: streamlit run app.py
import neon



def main():
    st.set_page_config(
        page_title="any2any",  #:cyclone::hammer_and_pick::recycle:
        page_icon=":cyclone:",
        # You can use emojis or path to an image file :repeat: oder :cyclone: :radio_button: :recycle: :hammer_and_pick:
        layout="wide",  # 'centered' or 'wide'
        initial_sidebar_state='expanded'  # 'auto', 'expanded', or 'collapsed' "expanded"
    )
    st.sidebar.title("Navigation")
    # Apply custom CSS
    st.markdown("""
        <style>
        div.row-widget.stRadio > div {
            flex-direction: col;
            align-items: stretch;
        }

        div.row-widget.stRadio > div[role="radiogroup"] > label[data-baseweb="radio"] > div:first-child {
            display: none;
        }

        div.row-widget.stRadio > div[role="radiogroup"] > label[data-baseweb="radio"] {
            background: transparent;
            padding-right: 10px;
            padding-left: 4px;
            padding-bottom: 3px;
            margin: 4px;
            border: 1px solid #0F0F0F;
        }

        div.row-widget.stRadio > div[role="radiogroup"] > label[data-baseweb="radio"]:has(input[type="radio"]:checked) {
            background: white !important;
            border: 4px solid 000000 !important;
        }
        </style>
        """, unsafe_allow_html=True)

    # Sidebar radio button
    choice = st.sidebar.radio("Go to", (
    "Home", "My Files", "Create Mapper Table", "Execute", )) #"About", "test_db", "newDBtest",
    if "username" not in st.session_state:
        st.session_state.username = ""
    if "user_pw" not in st.session_state:
        st.session_state.user_pw = False
    if "create_mapper" not in st.session_state:
        st.session_state.create_mapper = False
    if "user_space" not in st.session_state:
        st.session_state.user_space = "menu"
    if "user_logged_in" not in st.session_state:
        st.session_state.user_logged_in = False
    if choice == "Home":
        st.title("any2any")
        st.write("transforming data since 2025")
        left, right = st.columns([3, 2])

        with left:
            st.markdown("""
                        ###   Das Problem
                        bla bla                        
                        ###   Unsere Lösung
                        bla bla
                        ###   Treten Sie unserer Bewegung bei
                        bla bla                        
                        """)

        with right:
            st.markdown("""
                        ###   Wie es funktioniert
                        bla bla
                        """)

        #st.image("images/circ.webp", caption="circular building industry")

    elif choice == "My Files":
        st.write("Step 1: Upload Excel Files")
        c1, c2, c3 = st.columns(3)
        with c1:
            uploaded_quelle = st.file_uploader("Upload QUELLE Excel File", type="xlsx", key="quelle")
        with c2:
            uploaded_mapping_table = st.file_uploader("upload mapper table", type="csv", key="mapping_table")
        with c3:
            uploaded_ziel = st.file_uploader("Upload ZIEL Excel File", type="xlsx", key="ziel")

    elif choice == "Create Mapper Table":
        st.write("Mapping")
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
                        st.session_state.my_columns.append(
                            f"{st.session_state.add_col}_{len(st.session_state.my_columns)}")
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

    elif choice == "test_db":
        # Connection URL for SQLAlchemy
        connection_url = st.secrets["NEON_NEW"]
        engine = create_engine(connection_url)

        def add_to_circdb_(my_id, my_name, my_pet):
            query = text("INSERT INTO home (id, name, pet) VALUES (:id, :name, :pet)")
            with engine.connect() as conn:
                try:
                    conn.execute(query, {"id": my_id, "name": my_name, "pet": my_pet})
                    st.success("Added to database successfully!")
                except Exception as e:
                    st.error(f"Failed to add to database: {str(e)}")

        def add_to_circdb(my_id, my_name, my_pet):
            # Define the query for insertion
            insert_query = text("INSERT INTO home (id, name, pet) VALUES (:id, :name, :pet)")
            # Define the query for checking the entry
            check_query = text("SELECT * FROM home WHERE id = :id AND name = :name AND pet = :pet")

            with engine.connect() as conn:
                try:
                    # Insert the entry into the database
                    conn.execute(insert_query, {"id": my_id, "name": my_name, "pet": my_pet})
                    st.warning("Insertion step completed for table 'home', branch 'dev_branch'.")

                    # Check if the entry was successfully added
                    result = conn.execute(check_query, {"id": my_id, "name": my_name, "pet": my_pet}).fetchone()
                    st.warning("Verification step completed for table 'home', branch 'dev_branch'.")

                    if result:
                        st.success("Added to database successfully!")
                    else:
                        st.error("Entry was not added to the database.")

                except Exception as e:
                    st.error(f"Failed to add to database: {str(e)}")

    elif choice == "Execute":
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
    elif choice == "UserSpace":
        st.title(f"welcome {st.session_state.username}")
        if st.session_state.user_logged_in:
            elia.user_space()
        else:
            if st.toggle("login/signup"):
                st.session_state.username = st.text_input("username")
                st.session_state.user_pw = str(hash(st.text_input("password", type="password")))
                if st.button("login"):
                    if checkpw():
                        # elia.user_space()
                        st.rerun()
                    else:
                        st.error("wrong pw / username")
            else:
                st.session_state.username = st.text_input("required: NEW username")
                st.session_state.user_pw = str(hash(st.text_input("required: NEW password", type="password")))
                st.session_state.email = st.text_input("required: EMAIL")
                st.session_state.corp = st.text_input("required: company")
                st.session_state.birthday = st.text_input("required: Birthday YYYY-MM-DD")
                if st.button("Create!"):
                    if createuser():
                        st.success("login")
                        st.session_state.user_logged_in = True
                        st.rerun()
                    else:
                        st.warning("didnt work")

    elif choice == "About":
        l, r = st.columns(2)
        with l:
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
            st.write("")


if __name__ == "__main__":
    main()