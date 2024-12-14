from requests import get

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

            print(f"Getting storm prediction center GeoJSON data for day: {counter}")

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
