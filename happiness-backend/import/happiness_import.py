import datetime
import pickle
from datetime import timedelta
from io import BytesIO

import gspread
import openpyxl
from gspread.urls import SPREADSHEET_URL
from gspread.utils import column_letter_to_index, ExportFormat

# import data config:
# format is (app_user_id, (2022_data_sheet_row, 2023_data_sheet_row))
# -------------------------------------------------------
import_config = [(1, (4, 4)), (2, (10, 10)), (3, (8, 8))]
since = datetime.date(2022, 8, 15) # date of earliest happiness entry
# -------------------------------------------------------

gc = gspread.oauth()
sh = gc.open_by_key('1CC6_64uz1kWNhL1U5T6bq2zGytuP6IsBduibciriK7E')

# for now only 2022-23 data from cornell sheet is supported
data_2022 = sh.worksheet('2022 Full Data')
data_2023 = sh.worksheet('2023 Full Data')
cornell_data = sh.worksheet('Input [CORNELL]')
cornell_data_cells = cornell_data.get_all_cells()
print('worksheets fetched')

def parse_notes():
    url = SPREADSHEET_URL % (cornell_data.spreadsheet.id)
    params = {"ranges": "'Input [CORNELL]'!A1:V146", "fields": "sheets/data/rowData/values/note"}
    response = cornell_data.client.request("get", url, params=params)
    response_data = response.json()['sheets'][0]['data'][0]['rowData']

    notes_data = {}

    row_count = 1
    for row in response_data:
        if len(row.keys()) != 0:
            column_count = 1
            for column in row['values']:
                if len(column.keys()) != 0:
                    notes_data[(row_count, column_count)] = column['note']
                column_count += 1
        row_count += 1

    return notes_data

def parse_comments():
    sh_bytes = sh.export(ExportFormat.EXCEL)
    workbook = openpyxl.load_workbook(filename=BytesIO(sh_bytes), data_only=False)
    worksheet = workbook['Input CORNELL']

    comment_data = {}

    for i, row in enumerate(worksheet.iter_rows(), 1):
        for j, cell in enumerate(row, 1):
            if cell.comment:
                # causes weekend comments to be lost but ok for now
                comment_data[(i, j)] = cell.comment.text.split('\n')[0]

    return comment_data

def get_cell(rc):
    r, c = rc
    for cell in cornell_data_cells:
        if cell.row == r and cell.col == c:
            return cell.value # returns string

all_notes = parse_notes()
print('notes fetched')
all_comments = parse_comments()
print('comments fetched')

all_user_data = []

def parse_sheet_user_data(app_user_id, start_date, data_sheet, data_sheet_row):
    user_data = []
    user_raw_data_row = data_sheet.row_values(data_sheet_row, value_render_option='FORMULA')[2:]

    date_counter = start_date
    count = 0
    for raw_cell in user_raw_data_row:
        loc_info = raw_cell.split("'")
        sheet, cell = loc_info[1], loc_info[2][1:]
        cell_rc = (int(cell[1:]), column_letter_to_index(cell[0]))

        happiness_value = get_cell(cell_rc)
        if len(happiness_value) > 0:
            happiness_entry = {
                # 'cell': cell,
                'user_id': app_user_id,
                'timestamp': date_counter.strftime("%Y-%m-%d"),
                'value': float(happiness_value),
            }

            user_comment = all_comments.get(cell_rc, '')
            if len(user_comment) == 0: user_comment = all_notes.get(cell_rc, '')
            if len(user_comment) != 0: happiness_entry['comment'] = user_comment

            if date_counter >= since:
                user_data.append(happiness_entry)

        count += 1
        date_counter = date_counter + timedelta(days=1 if count % 5 != 0 else 3)

    return user_data

def parse_user_data(app_user_id, sheet_rows):

    data_sheet_row_2022, data_sheet_row_2023 = sheet_rows
    user_data_2022 = parse_sheet_user_data(app_user_id, datetime.date(2022, 8, 15),
                                           data_2022, data_sheet_row_2022)
    user_data_2023 = parse_sheet_user_data(app_user_id, datetime.date(2023, 1, 2),
                                           data_2023, data_sheet_row_2023)
    user_data = [user_data_2022, user_data_2023]

    return [element for sublist in user_data for element in sublist]

for user_id, sheet_rows in import_config:
    data = parse_user_data(user_id, sheet_rows)
    all_user_data.extend(data)
    print(f'user {user_id} @ row {sheet_rows}: {len(data)} data entries parsed')

with open('happiness_import.pick', 'wb') as f:
    pickle.dump(all_user_data, f)

print(all_user_data)
