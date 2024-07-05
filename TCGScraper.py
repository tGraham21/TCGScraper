import os.path
import gspread
import datetime

from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from PriceScraper import PriceScraper, PriceData

# Path to your service account key file
SERVICE_ACCOUNT_FILE = 'service-key.json'

# Scopes required to access Google Sheets and Drive APIs
SCOPES = ["https://www.googleapis.com/auth/spreadsheets",
          "https://www.googleapis.com/auth/drive"]

# The ID and range of the spreadsheet
SPREADSHEET_ID = '1W13k9LgPpaf806bIOwjhnAhsi0QQ77sJ6IJZ0vgq5K0'
RANGE_NAME = 'Sheet1'  # Adjust range as needed

def col_index_to_letter(index):
    letter = ''
    while index > 0:
        index -= 1
        letter = chr(index % 26 + 65) + letter
        index //= 26
    return letter


def main():
    creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)

    try:
        # Build the service
        service = build("sheets", "v4", credentials=creds)

        # Call the Sheets API
        sheet = service.spreadsheets()
        
        result = (
            sheet.values()
            .get(spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME)
            .execute()
            )

        # Request data from the specified range
        values = result.get('values', [])

        urls = [url[0]  for url in values if url[0]]

        scraper = PriceScraper(urls)
        data = scraper.GetPriceData()
        scraper.Close()

        for d in data.values():
          print(d)

        client = gspread.authorize(creds)

        spreadsheet = client.open_by_key(SPREADSHEET_ID)
        worksheet = spreadsheet.sheet1

        writeData = []

        for d in data.values():
            writeData.append([d.MarketPrice])

        time = datetime.datetime.now()
        writeData.append([time.strftime("%Y-%m-%d %H:%M:%S")])

        if values and values[0]:
            next_empty_col_index = len(values[0]) + 1
        else:
            next_empty_col_index = 1

        next_empty_col_letter = col_index_to_letter(next_empty_col_index)
        # WRITE_RANGE = f'Sheet1!{next_empty_col_letter}1:{next_empty_col_letter}'
        start_index = next_empty_col_letter + '1'

        worksheet.update(writeData, start_index)

    except HttpError as err:
        print(err)

if __name__ == '__main__':
    main()

