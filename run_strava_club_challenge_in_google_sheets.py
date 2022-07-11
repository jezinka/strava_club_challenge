# code built off script from the following blog post
# https://medium.com/swlh/using-python-to-connect-to-stravas-api-and-analyse-your-activities-dummies-guide-5f49727aac86

from datetime import datetime, timedelta, date

import gspread

from const import TRAINING_DATE_COLUMN, DISTANCE_COLUMN, DATE_FORMAT, DATE, GOOGLE_SHEET_KEY, GOOGLE_SHEET_NAME
from strava_service import get_user_activities_from_strava


# connect to google spreadsheet
# input
# key: key to google sheet
# worksheet: name of worksheet
# output
# sheet: google sheet object

def connect_to_spreadsheet():
    # connect to google sheet
    gc = gspread.service_account()

    # open spreadsheet
    sheet = gc.open_by_key(GOOGLE_SHEET_KEY).worksheet(GOOGLE_SHEET_NAME)
    return sheet


# get first date of challenge
# input
# sheet: google sheet
# output
# start_date: last date in spreadsheet
def get_begin_date(sheet):
    column_values = list(filter(None, sheet.col_values(TRAINING_DATE_COLUMN)))
    if column_values and column_values[-1] != DATE:
        last_date_cell_value = column_values[-1]
        if date.today().strftime(DATE_FORMAT) == last_date_cell_value:
            hour = datetime.now().hour
            return datetime.strptime(last_date_cell_value, DATE_FORMAT) + timedelta(hours=hour - 1)
        return datetime.strptime(last_date_cell_value, DATE_FORMAT) + timedelta(days=1)
    return None


# input
# sheet: google sheet where user information is stored
# activites: list of all activites
def write_to_sheet(sheet, activites):
    row_index = get_first_empty_row(sheet)
    for a in activites:
        sheet.update_cell(row_index, TRAINING_DATE_COLUMN, a.training_date)
        sheet.update_cell(row_index, DISTANCE_COLUMN, a.distance)
        row_index += 1


def get_first_empty_row(sheet):
    values = sheet.col_values(TRAINING_DATE_COLUMN)
    return len(values) + 1


def get_date_filter_range(sheet):
    begin_date = get_begin_date(sheet)
    if not begin_date:
        begin_date = datetime(int(sheet.title), 1, 1)  # first day of year
    begin_date_epoch = begin_date.timestamp()

    end_year_epoch = datetime(begin_date.year, 12, 31).timestamp()

    return begin_date_epoch, end_year_epoch


def main():
    # connect to google sheet
    sheet = connect_to_spreadsheet()

    begin_date_epoch, end_year_epoch = get_date_filter_range(sheet)

    # get user activity from strava
    activities = get_user_activities_from_strava(begin_date_epoch, end_year_epoch)

    # update google sheet with date and distance values
    write_to_sheet(sheet, activities)


if __name__ == "__main__":
    main()
