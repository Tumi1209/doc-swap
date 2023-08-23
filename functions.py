import numpy as np
import pandas as pd
import altair as alt
import streamlit as st
from datetime import datetime, timedelta
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


@st.cache_resource(
    ttl="1h",
    max_entries=1,
)
def fetch_swap_data(_gc, sheet_name, sheet_key, columns_list):
    try:
        # Open specific sheet
        gs = _gc.open_by_key(sheet_key)

        # Open specific tab within the sheet
        tab = gs.worksheet(sheet_name)

        data = tab.get_all_values()
        headers = data.pop(0)
        df = pd.DataFrame(data, columns=headers)

        # to handle numeric columns that are imported as strings
        for column in columns_list:
            df[column] = pd.to_numeric(df[column])

        return df

    except gspread.exceptions.APIError as e:
        print("Error accessing Google Sheets API:", e)
        return None
    except gspread.exceptions.WorksheetNotFound as e:
        print("Error: Worksheet not found:", e)
        return None
    except Exception as e:
        print("An error occurred:", e)
        return None


def count_unique_values(df, column_name):
    if column_name not in df.columns:
        raise ValueError(f"Column '{column_name}' not found in the DataFrame.")

    unique_values = df[column_name].nunique()
    return unique_values


def pivot_and_rename_choices(df):
    if not all(
        col in df.columns for col in ["first_choice", "second_choice", "third_choice"]
    ):
        raise ValueError("Required columns not found in the DataFrame.")

    # Reshape the data to long format
    choices_df = pd.melt(
        df,
        value_vars=["first_choice", "second_choice", "third_choice"],
        var_name="choice",
        value_name="hospital",
    )

    # Rename the values in the "choice" column
    choices_df["choice"] = choices_df["choice"].map(
        {
            "first_choice": "First Choice",
            "second_choice": "Second Choice",
            "third_choice": "Third Choice",
        }
    )

    return choices_df


@st.cache_data(ttl="1h", max_entries=1)
def time_since_last_update():
    time_plus_1_hours = datetime.now() + timedelta(hours=1)
    return time_plus_1_hours


def time_until_specified_time(target_time):
    current_time = datetime.now()
    time_difference = target_time - current_time
    time_difference = target_time - current_time
    hours, remainder = divmod(time_difference.seconds, 3600)
    minutes = remainder // 60
    time_format = f"{minutes:02d}min"
    return time_format