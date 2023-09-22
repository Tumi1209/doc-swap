import numpy as np
import pandas as pd
import altair as alt
import streamlit as st
from datetime import datetime, timedelta
import gspread
from google.oauth2 import service_account
import base64


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


@st.cache_data(
    ttl="15m",
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


@st.cache_data(
    ttl="15m",
    max_entries=1,
)
def fetch_status_data(_gc, sheet_name, sheet_key, columns_list):
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


def count_unique_values_swapped_yes(df, column_name):
    if column_name not in df.columns:
        raise ValueError(f"Column '{column_name}' not found in the DataFrame.")

    filtered_df = df[df["swapped"] == "yes"]
    unique_values = filtered_df[column_name].nunique()
    return unique_values


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


@st.cache_data(ttl="15m", max_entries=1)
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


# @st.cache_data(
#     ttl="15m",
#     max_entries=1,
# )
# def get_latest_record_per_email(df):
#     # Convert the timestamp column to datetime if not already
#     df["timestamp"] = pd.to_datetime(df["timestamp"])

#     # Sort the DataFrame by email and timestamp
#     df.sort_values(by=["email", "timestamp"], ascending=[True, False], inplace=True)

#     # Group by email and select the first record in each group (latest due to sorting)
#     latest_records = df.groupby("email").first().reset_index()

#     return latest_records


def get_latest_record_per_email(df, df_swapped):
    # Filter out records where swapped = 'yes' in the second DataFrame
    df_swapped_filtered = df_swapped[df_swapped["swapped"] != "yes"]

    # Convert the timestamp column to datetime if not already
    df["timestamp"] = pd.to_datetime(df["timestamp"])

    # Sort the DataFrame by email and timestamp
    df.sort_values(by=["email", "timestamp"], ascending=[True, False], inplace=True)

    # Group by email and select the first record in each group (latest due to sorting)
    latest_records = df.groupby("email").first().reset_index()

    # Filter the first DataFrame to include only emails present in the filtered second DataFrame
    latest_records_filtered = latest_records[
        latest_records["email"].isin(df_swapped_filtered["email"])
    ]

    return latest_records_filtered


def render_svg(path, width=None, height=None, caption=None):
    with open(path, "r") as f:
        svg_content = f.read()

    b64_svg = base64.b64encode(svg_content.encode("utf-8")).decode("utf-8")

    style = ""
    if width is not None:
        style += f"width: {width}%;"
    if height is not None:
        style += f"height: {height}%;"

    img_tag = f'<img src="data:image/svg+xml;base64,{b64_svg}" style="{style}"/>'

    st.write(img_tag, unsafe_allow_html=True)
    if caption is not None:
        st.caption(caption)
    st.write("""### """)


def render_svg_banner(path, width=None, height=None, swappers=None, emails=None):
    with open(path, "r") as f:
        svg_content = f.read()

    if swappers is not None:
        svg_content = svg_content.replace("@swappers", str(swappers))
    if emails is not None:
        svg_content = svg_content.replace("@emails", str(emails))

    b64_svg = base64.b64encode(svg_content.encode("utf-8")).decode("utf-8")

    style = ""
    if width is not None:
        style += f"width: {width}%;"
    if height is not None:
        style += f"height: {height}%;"

    img_tag = f'<img src="data:image/svg+xml;base64,{b64_svg}" style="{style}"/>'

    st.write(img_tag, unsafe_allow_html=True)
    st.write("""### """)
