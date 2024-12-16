from io import StringIO

import pandas as pd
from geopandas import GeoDataFrame
from bs4 import BeautifulSoup
from requests import Session, get

from config import Environment


def get_arcgis_web_feature_service_geojson_dict(url: str, url_params: dict | None) -> dict:
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
        url_params = {"f": "geojson", "where": "1=1", "outFields": "*", "returnGeometry": "true"}

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

        # loop through the SPC fire weather outlook url dictionaries
        for counter, spc_url_dict in enumerate(spc_fire_wx_outlook_dicts):

            # get the day URL
            day_dict = getattr(env, spc_url_dict)

            print(f"Requesting Storm Prediction Center Fire Weather Forecast data for day: {counter}")

            # get the fire weather outlook GeoJSON
            fire_wx_outlook_geojson = get_arcgis_web_feature_service_geojson_dict(
                day_dict["fire_wx_outlook_url"], url_params=None
            )

            # get the dry lightning GeoJSON
            dry_lightning_geojson = get_arcgis_web_feature_service_geojson_dict(
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
            var for var in dir(env) if "AUSTRALIA_" in var
        ]

         # Create a session
        session = Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        })

        fire_danger_australia = pd.DataFrame()

        for fire_danger_url_config in bureau_of_meteorology_fire_danger_rating_urls:
            # get the URL from the environment variable
            fire_danger_url = getattr(env, fire_danger_url_config)

            # get the webpage
            page = session.get(fire_danger_url, timeout=300)

            # show the status code of the page object
            print(f"URL: {fire_danger_url_config} - Status Code: {page.status_code}")

            # raise an exception if the request was unsuccessful
            page.raise_for_status()

            # read the html content
            html_content = page.content

            # parse the HTML content using BeautifulSoup
            soup = BeautifulSoup(html_content, 'html.parser')

            # find the table in the HTML content
            table = soup.find('table')

            # convert the table to a DataFrame
            df = pd.read_html(StringIO(str(table)))[0]

            # Identify day of the week columns dynamically
            day_columns = [col for col in df.columns if str(col).lower() in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']]

            # Separate the fire danger rating and the fire behavior index into their own columns
            for day in day_columns:
                df[[f'{day}_rating', f'{day}_index']] = df[day].str.extract(r'(\D+)\s+(\d+)')

            # Drop the original day columns
            df.drop(columns=day_columns, inplace=True)

            # add the DataFrame to the fire_danger_australia
            fire_danger_australia = pd.concat([fire_danger_australia, df])

        # return the fire_danger_australia DataFrame
        return fire_danger_australia

    except Exception as e:
        print(f"scrape_bureau_of_meteorology_fire_danger_ratings failed due to this error: {e}")
        raise

def convert_fire_danger_rating_table_to_geodataframe(fire_danger_table: pd.DataFrame) -> GeoDataFrame:
    """
    Converts a DataFrame of fire danger ratings to a GeoDataFrame by joining the fire danger ratings
    to the fire weather districts.

    Parameters
    ----------
    fire_danger_table : pd.DataFrame
        A DataFrame of fire danger ratings with the columns 'district', 'geometry', and 'rating'.

    fire_weather_districts_rest_service_url : str
        The URL of the fire weather districts REST service.
    """
    try:
        # create an instance of the Environment class
        env = Environment()

        # get the fire weather districts GeoJson
        fire_weather_districts = get_arcgis_web_feature_service_geojson_dict(
            url = env.AUSTRALIA_FIRE_WEATHER_DISTRICTS, url_params=None
        )

         # Convert the GeoJSON to a GeoDataFrame
        fire_weather_districts_gdf = GeoDataFrame.from_features(fire_weather_districts['features'])

        # Filter for unique DIST_NAMES
        fire_weather_districts_gdf = fire_weather_districts_gdf.drop_duplicates(subset='DIST_NAME')

        # Merge the fire danger table with the fire weather districts GeoDataFrame
        fire_weather_districts_gdf.merge(fire_danger_table, left_on='DIST_NAME', right_on='District')

        #drop the uneeded columsn
        return fire_weather_districts_gdf.drop(
            columns=['OBJECTID',
                     'AAC',
                     'DIST_NO',
                     'SOURCE',
                     'FireBehavIndex', # More timely, updated index is in the fire_danger_table
                     'FireDanger', # More timely, updated rating is in the fire_danger_table
                     'Forecast_Period',
                     'Start_Time',
                     'End_Time',
                     'Start_Time_UTC_str',
                     'End_Time_UTC_str',
                     ]
        )

    except Exception as e:
        print(f"convert_fire_danger_rating_table_to_geodataframe failed due to this error: {e}")
        raise

def convert_fire_danger_geodataframe_to_dict(fire_danger_gdf: GeoDataFrame) -> dict:
    """
    Returns a dictionary of GeoJSON data from the Bureau of Meteorology's (BOM)
    Fire danger ratings. The output dictionary is in this format

    {
        0: {
            'fire_danger_geojson': Geojson Data for day 1
        },
        1: {
            'fire_danger_geojson': Geojson Data for day 2
        },
        ...
    }

    Parameters
    ----------
    fire_danger_gdf : gpd.GeoDataFrame
        A GeoDataFrame of fire danger ratings with the columns 'geometry', 'DIST_NAME', 'STATE_CODE', '0', 'District', and day of the week columns.
    """
    try:
        # Identify day of the week columns dynamically
        day_columns = [col for col in fire_danger_gdf.columns if '_rating' in str(col)]

        # Initialize the output dictionary
        out_dict = {}

        # Iterate over the day columns
        for i, day in enumerate(day_columns):
            # Get the corresponding index column
            index_col = day.replace('_rating', '_index')

            # Create a new GeoDataFrame for the current day
            day_gdf = fire_danger_gdf[['geometry', 'DIST_NAME', 'STATE_CODE', '0', 'District', day, index_col]].copy()

            # Rename the columns to remove the day suffix
            day_gdf.rename(columns={day: 'rating', index_col: 'index'}, inplace=True)

            # Convert the GeoDataFrame to GeoJSON format
            day_geojson = day_gdf.to_json()

            # Add the GeoJSON data to the output dictionary
            out_dict[i] = {
                'fire_danger_geojson': day_geojson
            }

        # Return the output dictionary
        return out_dict

    except Exception as e:
        print(f"convert_fire_danger_geodataframe_to_dict failed due to this error: {e}")
        raise