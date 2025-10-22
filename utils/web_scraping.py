from geopandas import GeoDataFrame
from httpx import get

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


def _has_valid_geometry_and_risk(geojson_data: dict) -> bool:
    """
    Check if GeoJSON data contains valid geometry features with actual risk (dn != 0).
    
    Parameters
    ----------
    geojson_data : dict
        GeoJSON data dictionary
        
    Returns
    -------
    bool
        True if there are features with valid geometry AND dn != 0, False otherwise
    """
    if not geojson_data or "features" not in geojson_data:
        return False
    
    for feature in geojson_data["features"]:
        # Check if feature has valid geometry
        if feature.get("geometry") is not None:
            # Check if feature has actual risk (dn != 0)
            dn = feature.get("properties", {}).get("dn", None)
            if dn is not None and dn != 0:
                return True
    
    return False


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

            # Check if we have valid geometry data with actual risk
            has_fire_wx_geometry = _has_valid_geometry_and_risk(fire_wx_outlook_geojson)
            has_dry_lightning_geometry = _has_valid_geometry_and_risk(dry_lightning_geojson)
            
            # Log the status for this day
            day_name = f"Day {counter + 1}"
            if has_fire_wx_geometry and has_dry_lightning_geometry:
                print(f"  {day_name}: Both fire weather outlooks and dry lightning risk areas found")
            elif has_fire_wx_geometry:
                print(f"  {day_name}: Fire weather outlooks found (no dry lightning risk)")
            elif has_dry_lightning_geometry:
                print(f"  {day_name}: Dry lightning risk areas found (no general fire weather outlooks)")
            else:
                print(f"  {day_name}: No active fire weather outlooks (no elevated fire weather conditions)")

            # add the GeoJSON data to the dictionary
            out_dict[counter] = {
                "fire_wx_outlook_geojson": fire_wx_outlook_geojson,
                "dry_lightning_geojson": dry_lightning_geojson,
                "has_fire_wx_geometry": has_fire_wx_geometry,
                "has_dry_lightning_geometry": has_dry_lightning_geometry,
            }

        # Check if any days have active outlooks
        has_any_outlooks = any(
            out_dict[day]["has_fire_wx_geometry"] or out_dict[day]["has_dry_lightning_geometry"]
            for day in out_dict
        )
        
        if not has_any_outlooks:
            print("  No active fire weather outlooks found for any forecast day.")
            print("  This is normal when there are no elevated fire weather conditions expected.")
        else:
            # Count the types of outlooks found
            fire_wx_days = sum(1 for day in out_dict if out_dict[day]["has_fire_wx_geometry"])
            dry_lightning_days = sum(1 for day in out_dict if out_dict[day]["has_dry_lightning_geometry"])
            
            if fire_wx_days > 0 and dry_lightning_days > 0:
                print(f"  Summary: {fire_wx_days} day(s) with fire weather outlooks, {dry_lightning_days} day(s) with dry lightning risk")
            elif fire_wx_days > 0:
                print(f"  Summary: {fire_wx_days} day(s) with fire weather outlooks found")
            elif dry_lightning_days > 0:
                print(f"  Summary: {dry_lightning_days} day(s) with dry lightning risk areas found")

        # return the dictionary
        return out_dict

    except Exception as e:
        print(
            f"get_storm_prediction_center_fire_weather_outlooks_geojsons failed due to this error: {e}"
        )
        raise


def get_australia_fire_danger_ratings() -> GeoDataFrame:
    """
    Gets the Australian fire danger ratings directly from the AUSTRALIA_FIRE_DANGER_RATINGS
    configuration and returns a GeoDataFrame.
    
    Returns
    -------
    GeoDataFrame
        A GeoDataFrame containing the fire weather districts with their geometries and attributes.
    """
    try:
        # create an instance of the Environment class
        env = Environment()

        print("Fetching Australian Fire Danger Ratings...")
        # get the fire weather districts GeoJson with parameters to get all forecast periods
        url_params = {
            "f": "geojson",
            "where": "1=1",  # Get all features
            "outFields": "*",  # Get all fields
            "returnGeometry": "true",
        }
        
        fire_weather_districts = _get_arcgis_web_feature_service_geojson_dict(
            url=env.AUSTRALIA_FIRE_DANGER_RATINGS, url_params=url_params
        )

        print("  Converting to GeoDataFrame...")
        # Convert the GeoJSON to a GeoDataFrame
        fire_weather_districts_gdf = GeoDataFrame.from_features(
            fire_weather_districts["features"]
        )

        print("  Setting CRS...")
        # assign a crs to the GeoDataFrame
        fire_weather_districts_gdf.crs = 4326

        print("  Fire weather districts data ready")
        
        # Debug: Check what forecast periods we actually got
        if 'Forecast_Period' in fire_weather_districts_gdf.columns:
            unique_periods = fire_weather_districts_gdf['Forecast_Period'].unique()
            print(f"  Available forecast periods: {unique_periods}")
            print(f"  Total features: {len(fire_weather_districts_gdf)}")
        
        # return the fire_weather_districts_gdf
        return fire_weather_districts_gdf

    except Exception as e:
        print(
            f"get_australia_fire_weather_districts failed due to this error: {e}"
        )
        raise