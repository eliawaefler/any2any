
"""
hier kommen funktionen, die von der ANWENUNG aufgerufen werden.
"""

# Function to extract sheet names and column headers from an uploaded Excel file
def extract_file_structure(uploaded_file):
    structure = {}
    excel_file = pd.ExcelFile(uploaded_file)
    for sheet in excel_file.sheet_names:
        df = excel_file.parse(sheet)
        structure[sheet] = list(df.columns)
    return structure
