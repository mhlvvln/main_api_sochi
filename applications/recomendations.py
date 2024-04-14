import openpyxl


def read_recommendation_data(file_path="applications/recomendations.xlsx"):
    wb = openpyxl.load_workbook(file_path)
    ws = wb.active

    data = []

    for row in ws.iter_rows(min_row=3, max_row=31, min_col=2, max_col=4):
        row_data = [cell.value.lower() if isinstance(cell.value, str) else cell.value for cell in row]
        data.append(row_data)

    return data


print(read_recommendation_data())
