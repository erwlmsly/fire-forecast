from io import StringIO
from datetime import datetime, timedelta

import pandas as pd
from bs4 import BeautifulSoup
from geopandas import GeoDataFrame
from httpx import Client, get

from config import Environment


def _get_arcgis_web_feature_service_geojson_dict(
    url: str, url_params: dict | None
) -> dict:
    """
    Returns a GeoJSON dictionary from a web feature service URL.

    Parameters
    ----------
    url : str
        The URL of the web feature service.

    url_params : dict
        A dictionary of parameters to pass to the URL. Default returns all features and geometries in a geojson format.
        {"f": "geojson", "where": "1=1", "outFields": "*", "returnGeometry": "true"}
    """
    if url_params is None:
        url_params = {
            "f": "geojson",
            "where": "1=1",
            "outFields": "*",
            "returnGeometry": "true",
        }

    try:
        # create the url to query the web feature service
        query_url = f"{url}/query"

        # make the request, timeout after 60 seconds
        response = get(query_url, params=url_params, timeout=60)

        # raise an exception if the request was unsuccessful
        response.raise_for_status()

        # return the GeoJSON dictionary
        return response.json()
    except Exception as e:
        print(
            f"get_arcgis_web_feature_service_geojson_dict failed due to this error: {e}"
        )
        raise


def get_storm_prediction_center_fire_weather_outlooks() -> dict:
    """
    Returns a dictionary of GeoJSON data from the Storm Prediction Center (SPC)
    Fire Weather Outlooks. The output dictionary is in this format

    {
        0: {
            'fire_wx_outlook_json': Geojson Data for day 1
            'dry_lightning_json': Geojson Data for day 1 dry lightning
        }
        ...
        3 : {
        ...
        }
    }
    """
    try:
        # create an instance of the Environment class
        env = Environment()

        # create a list of environment variables with "SPC_FIRE_WX_OUTLOOK_DAY" in the name
        spc_fire_wx_outlook_dicts = [
            var for var in dir(env) if "SPC_FIRE_WX_DAY" in var
        ]

        # initiate a dictionary to store the GeoJSON data and counter variable for forecast day
        out_dict = {}

        print("Getting Storm Prediction Center Fire Weather Outlooks")

        # loop through the SPC fire weather outlook url dictionaries
        for counter, spc_url_dict in enumerate(spc_fire_wx_outlook_dicts):

            # get the day URL
            day_dict = getattr(env, spc_url_dict)

            # get the fire weather outlook GeoJSON
            fire_wx_outlook_geojson = _get_arcgis_web_feature_service_geojson_dict(
                day_dict["fire_wx_outlook_url"], url_params=None
            )

            # get the dry lightning GeoJSON
            dry_lightning_geojson = _get_arcgis_web_feature_service_geojson_dict(
                day_dict["dry_lightning_url"], url_params=None
            )

            # add the GeoJSON data to the dictionary
            out_dict[counter] = {
                "fire_wx_outlook_geojson": fire_wx_outlook_geojson,
                "dry_lightning_geojson": dry_lightning_geojson,
            }

        # return the dictionary
        return out_dict

    except Exception as e:
        print(
            f"get_storm_prediction_center_fire_weather_outlooks_geojsons failed due to this error: {e}"
        )
        raise


def scrape_bureau_of_meteorology_fire_danger_ratings() -> pd.DataFrame:
    """
    Scrapes the Bureau of Meteorology's (BOM) fire danger rating ratings, retuns a dataframe with
    days of the week as the columns, and the fire weather districts as the rows.

    Parameters
    ----------
    url : str
        The URL of the BOM fire danger ratings page.
    """
    try:
        # create an instance of the Environment class
        env = Environment()

        # create a list of environment variables with "SPC_FIRE_WX_OUTLOOK_DAY" in the name
        bureau_of_meteorology_fire_danger_rating_urls = [
            var for var in dir(env) if "_FIRE_DANGER_RATING_TABLE" in var
        ]

        # Create a session
        client = Client()
        client.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
            }
        )

        fire_danger_australia = pd.DataFrame()

        print("Scraping Bureau of Meteorology Fire Danger Ratings")

        for fire_danger_url_config in bureau_of_meteorology_fire_danger_rating_urls:
            # get the URL from the environment variable
            fire_danger_url = getattr(env, fire_danger_url_config)

            # get the webpage content
            df = _get_fire_danger_data(client, fire_danger_url)

            # Identify day of the week columns dynamically
            day_columns = _identify_day_columns(df)

            # Separate the fire danger rating and the fire behavior index into their own columns
            df = _separate_fire_danger_rating_and_index(df, day_columns)

            # re identify new columns with the day names for conversion
            new_day_columns = _identify_day_columns(df)

            # convert the days of the week to a date plus day name
            df = _convert_days_of_week_to_date_plus_day(df, new_day_columns)

            # Add a column for the state
            df = _add_state_column(df, fire_danger_url_config)

            # add the DataFrame to the fire_danger_australia
            fire_danger_australia = pd.concat(
                [fire_danger_australia, df], ignore_index=True
            )

        # reset the index and drop the unwanted row
        fire_danger_australia.reset_index(drop=True, inplace=True)

        print("Scraping complete!")

        return fire_danger_australia

    except Exception as e:
        print(
            f"scrape_bureau_of_meteorology_fire_danger_ratings failed due to this error: {e}"
        )
        raise


def _get_fire_danger_data(client: Client, fire_danger_url: str) -> pd.DataFrame:
    """
    Returns a DataFrame of fire danger ratings from the Bureau of Meteorology's
    fire danger ratings page.

    Parameters
    ----------
    session : httpx.Client
        An HTTPX requests session object.

    fire_danger_url : str
        The URL of the BOM fire danger ratings page (there's a separate url for each)
    """
    try:
        # create a session
        page = client.get(fire_danger_url, timeout=300)

        # if status is not 200 raise an error
        page.raise_for_status()

        # store the page content
        html_content = page.content

        # parse the html content
        soup = BeautifulSoup(html_content, "html.parser")

        # find the table
        table = soup.find("table")

        # return the table as a DataFrame
        return pd.read_html(StringIO(str(table)))[0]

    except Exception as e:
        print(f"_get_fire_danger_data failed due to this error: {e}")
        raise


def _identify_day_columns(df: pd.DataFrame) -> list:
    """
    Returns a list of columns that contain the days of the week.

    Parameters
    ----------
    df : pd.DataFrame
        A DataFrame of fire danger ratings.
    """

    # return a list of columns that contain any days of the week
    return [
        col
        for col in df.columns
        if any(
            day in str(col).lower()
            for day in [
                "monday",
                "tuesday",
                "wednesday",
                "thursday",
                "friday",
                "saturday",
                "sunday",
            ]
        )
    ]


def _separate_fire_danger_rating_and_index(
    df: pd.DataFrame, day_columns: list
) -> pd.DataFrame:
    """
    Returns a DataFrame with the fire danger rating and fire behavior index separated
    into their own columns. They are stored in the same column on BOM's website
    """
    try:
        # on each day of the day colums
        for day in day_columns:
            # extract the rating and index
            df[[f"{day}_rating", f"{day}_index"]] = df[day].str.extract(
                r"(\D+)\s+(\d+)"
            )

        # drop the original columns which contain both the rating and index
        df.drop(columns=day_columns, inplace=True)

        # return the dataframe
        return df

    except Exception as e:
        print(f"_separate_fire_danger_rating_and_index failed due to this error: {e}")
        raise


def _add_state_column(df: pd.DataFrame, fire_danger_url_config: str) -> pd.DataFrame:
    """
    Adds a column to the DataFrame with the state abbreviation.

    Parameters
    ----------
    df : pd.DataFrame
        A DataFrame of fire danger ratings.

    fire_danger_url_config : str
        The name of the environment variable that contains the fire danger URL
    """
    try:
        if "NEW_SOUTH_WALES" in str(fire_danger_url_config):
            df["state"] = "NSW"
        if "VICTORIA" in str(fire_danger_url_config):
            df["state"] = "VIC"
        if "QUEENSLAND" in str(fire_danger_url_config):
            df["state"] = "QLD"
        if "WESTERN_AUSTRALIA" in str(fire_danger_url_config):
            df["state"] = "WA"
        if "SOUTH_AUSTRALIA" in str(fire_danger_url_config):
            df["state"] = "SA"
        if "TASMANIA" in str(fire_danger_url_config):
            df["state"] = "TAS"
        if "NORTHERN_TERRITORY" in str(fire_danger_url_config):
            df["state"] = "NT"
        return df
    except Exception as e:
        print(f"_add_state_column failed due to this error: {e}")
        raise


def _convert_days_of_week_to_date_plus_day(
    df: pd.DataFrame, day_columns: list
) -> pd.DataFrame:
    """
    Returns a DataFrame where columns are renamed from Monday_index to
    YYYY-MM-DD_dayName_index.

    Parameters
    ----------
    df : pd.DataFrame
        A DataFrame of fire danger ratings.

    day_columns : list
        A list of columns that contain the days of the week.
    """
    try:
        # get the current date
        now = datetime.today()

        # yesterday's date
        yesterday = now - timedelta(days=1)

        day_name_to_date = {}

        # create a dictionary of days of the week {monday: '2025-03-10', ...}
        for i in range(6):
            day_name_to_date[(yesterday + timedelta(days=i)).strftime("%A").lower()] = (
                yesterday + timedelta(days=i)
            )

        renaming_dict = {}
        # loop through the day columns
        for day in day_columns:

            # extract and lower all text before the underscore (monday, tuesday, etc)
            day_name = day.split("_")[0].lower()

            # extract and lower all text after the underscore (rating, index)
            column_suffix = day.split("_")[1].lower()

            # create a dict to rename the columns {old_column_name: "YYYYMMDD_dayName_rating"}
            renaming_dict[day] = day_name_to_date[day_name].strftime(
                f"%Y-%m-%d_%A_{column_suffix}"
            )

        # rename the columns
        df.rename(columns=renaming_dict, inplace=True)

        return df

    except Exception as e:
        print(f"_convert_days_of_week_to_date_plus_day failed due to this error: {e}")
        raise
