from io import StringIO

import pandas as pd
from bs4 import BeautifulSoup
from requests import Session, get

from config import Environment


def get_arcgis_web_feature_service_geojson_dict(url: str) -> dict:
    """
    Returns a GeoJSON dictionary from a web feature service URL.

    Parameters
    ----------
    url : str
        The URL of the web feature service.
    """
    try:
        # create the url to query the web feature service
        query_url = f"{url}/query"

        # specify query parameters
        params = {
            "f": "geojson",  # format = geojson
            "where": "1=1",  # return all features
            "outFields": "*",  # return all attributes
            "returnGeometry": "true",  # return geometry
        }

        # make the request, timeout after 60 seconds
        response = get(query_url, params=params, timeout=60)

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
                day_dict["fire_wx_outlook_url"]
            )

            # get the dry lightning GeoJSON
            dry_lightning_geojson = get_arcgis_web_feature_service_geojson_dict(
                day_dict["dry_lightning_url"]
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

            # add the DataFrame to the fire_danger_australia
            fire_danger_australia = pd.concat([fire_danger_australia, df])

        # return the fire_danger_australia DataFrame
        return fire_danger_australia

    except Exception as e:
        print(f"scrape_bureau_of_meteorology_fire_danger_ratings failed due to this error: {e}")
        raise
