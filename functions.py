import numpy as np
import pandas as pd
import streamlit as st
import gspread
from google.oauth2 import service_account
import matplotlib.pyplot as plt


# function to create api connection to google sheets
@st.cache_resource(
    max_entries=1,
)
def connect_to_gs(_service_account_key):
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    credentials = service_account.Credentials.from_service_account_info(
        _service_account_key, scopes=scopes
    )
    gs_connection = gspread.authorize(credentials)
    return gs_connection


def write_google_sheets_data(_gc, df, sheet_name, sheet_key):
    try:
        # Open specific sheet
        gs = _gc.open_by_key(sheet_key)

        # Open specific tab within the sheet
        tab = gs.worksheet(sheet_name)

        df_values = df.values.tolist()
        gs.values_append(sheet_name, {"valueInputOption": "RAW"}, {"values": df_values})

        return None

    except gspread.exceptions.APIError as e:
        print("Error accessing Google Sheets API:", e)
        return None
    except gspread.exceptions.WorksheetNotFound as e:
        print(f"Error: Worksheet not found, please create a new tab named:", e)
        return None
    except Exception as e:
        print("An error occurred:", e)
        return None
