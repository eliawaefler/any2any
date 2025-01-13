
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



def standard_tabelle():

    # A     B       C       D       E           F               G           H           ...
    # ID    GUID    name    wert    Einheit     dim1            dim1        dim3        ...
    # 01    fokfj   p1      5       h           G2              19.01.2025  projekt A   ...

    # Zeiterfassung
    # 01    jdskl   Elia    5       h           zeiterf         09.01.2025  Projekt1

    # energiedashboard
    # 01    sdflkj          5       h           Strom           01.2025

    # tabellenname

    pass



def finde_tabelle():
    pass
