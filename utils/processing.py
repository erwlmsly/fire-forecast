from datetime import datetime
from json import loads

from geopandas import GeoDataFrame
from pandas import DataFrame

from config import Environment

from utils.web_scraping import _get_arcgis_web_feature_service_geojson_dict


def merge_fire_weather_districts_and_fire_danger_table(
    fire_danger_table: DataFrame,
) -> GeoDataFrame:
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
        fire_weather_districts = _get_arcgis_web_feature_service_geojson_dict(
            url=env.AUSTRALIA_FIRE_DANGER_RATINGS, url_params=None
        )

        # Convert the GeoJSON to a GeoDataFrame
        fire_weather_districts_gdf = GeoDataFrame.from_features(
            fire_weather_districts["features"]
        )

        # Filter for unique DIST_NAMES
        fire_weather_districts_gdf = fire_weather_districts_gdf.drop_duplicates(
            subset="AAC"
        )

        # isolate "The Australian Capitla Territory row" and assign its "state" to "ACT"
        # this allows for a merge with the fire danger table
        fire_danger_table.loc[
            fire_danger_table["District"] == "The Australian Capital Territory",
            "state",
        ] = "ACT"

        # isolate row where DIST_NAME is "Australian Capital Territory" and assign it "The Australian Capital Territory"
        # this allows for a merge with the fire danger table
        fire_weather_districts_gdf.loc[
            fire_weather_districts_gdf["DIST_NAME"] == "Australian Capital Territory",
            "DIST_NAME",
        ] = "The Australian Capital Territory"

        # isolate the row where DIST_NAME is "Northern Fire Protection Area" and assign it "Northern Fire Protection Zone"
        fire_weather_districts_gdf.loc[
            fire_weather_districts_gdf["DIST_NAME"] == "Northern Fire Protection Area",
            "DIST_NAME",
        ] = "Northern Fire Protection Zone"

        # Merge the fire danger table with the fire weather districts GeoDataFrame
        fire_weather_districts_with_fire_danger = fire_weather_districts_gdf.merge(
            fire_danger_table,
            left_on=["DIST_NAME", "STATE_CODE"],
            right_on=["District", "state"],
            how="left",
        )

        # drop the uneeded columns
        fire_weather_districts_with_fire_danger = fire_weather_districts_with_fire_danger.drop(
            columns=[
                "OBJECTID",
                "AAC",
                "DIST_NO",
                "SOURCE",
                "FireBehavIndex",  # More timely, updated index is in the fire_danger_table
                "FireDanger",  # More timely, updated rating is in the fire_danger_table
                "Forecast_Period",
                "Start_Time",
                "End_Time",
                "Start_Time_UTC_str",
                "End_Time_UTC_str",
                "STATE_CODE",
                "DIST_NAME",
            ]
        )

        # assign a crs to the GeoDataFrame
        fire_weather_districts_with_fire_danger.crs = 4326

        # return the fire_weather_districts_gdf
        return fire_weather_districts_with_fire_danger

    except Exception as e:
        print(
            f"convert_fire_danger_rating_table_to_geodataframe failed due to this error: {e}"
        )
        raise


def convert_fire_danger_gdf_to_dict_for_plotting(
    fire_danger_gdf: GeoDataFrame,
) -> dict:
    """
    Converts a GeoDataFrame of fire danger ratings to a dictionary for plotting.
    Groups features by Forecast_Period and uses Start_Time_UTC_str attribute to
    determine dates.

    Parameters
    ----------
    fire_danger_gdf : GeoDataFrame
        A GeoDataFrame of fire weather districts with their geometries and attributes
    """
    try:
        # Create dictionary to store forecast data by date
        fire_danger_dict = {}
        
        # Get unique forecast periods
        if 'Forecast_Period' in fire_danger_gdf.columns:

            #isolate the unique forecast periods
            unique_forecast_periods = sorted(fire_danger_gdf['Forecast_Period'].unique())

            print(f"  Found forecast periods: {unique_forecast_periods}")
            
            for period in unique_forecast_periods:
                # Filter for this forecast period
                period_gdf = fire_danger_gdf[fire_danger_gdf['Forecast_Period'] == period]
                
                # if the period_gdf is not empty
                if len(period_gdf) > 0:
                    # Get the Start_Time_UTC_str from the first feature
                    start_time_str = period_gdf.iloc[0]['Start_Time_UTC_str']
                    
                    # Extract date from Start_Time_UTC_str (format: 2025-10-22T13:00:00Z)
                    if start_time_str:
                        # Extract just the date part (before the 'T')
                        date_str = start_time_str.split('T')[0]
                        
                        # Add this period's data to the dictionary
                        fire_danger_dict[date_str] = period_gdf.to_json()
                    else:
                        print(f"  Warning: No Start_Time_UTC_str found for period {period}")
        else:
            print("  Warning: No Forecast_Period column found, using current date")
            # Fallback to current date if no Forecast_Period column
            current_date = datetime.now().strftime("%Y-%m-%d")
            fire_danger_dict[current_date] = fire_danger_gdf.to_json()

        print(f"  Created dictionary with {len(fire_danger_dict)} date entries")
        return fire_danger_dict

    except Exception as e:
        print(
            f"convert_fire_danger_gdf_to_dict_for_plotting failed due to this error: {e}"
        )
        raise


def is_extreme_or_catastrophic_in_bom_fire_danger_ratings(
    fire_danger_dict: dict,
) -> bool:
    """
    Returns a bool if extreme or catastrophic ratings are found in the BOM fire
    danger ratings dictionary to see if any of the days contain an extreme or
    catastrophic fire danger rating.

    Parameters
    ----------
    fire_danger_dict : dict
        A dictionary of fire danger ratings for each day.
    """
    try:
        # initialize the assumption that there are no extreme or catastrophic fire danger ratings
        extreme_or_catastrophic = False

        # loop through all the days in the fire danger dict and see if any of them contain an extreme or catastrophic rating
        for day in fire_danger_dict.values():
            # conver the json string to a dictionary
            day = loads(day)

            # convert the json string to a DataFrame
            day_gdf = GeoDataFrame.from_features(day["features"], crs=4326)

            # identify the dataframe column which contains "_rating"
            rating_col = [col for col in day_gdf.columns if "_rating" in col]

            # filter the rating column for any values which are "Extreme" or "Catastrophic"
            day_extreme_or_catastrophic_ratings = day_gdf[
                day_gdf[rating_col].isin(["Extreme", "Catastrophic"])
            ]

            # if the day_extreme_or_catastrophic_rating is not empty, then there is an extreme or catastrophic rating
            if not day_extreme_or_catastrophic_ratings.empty:
                extreme_or_catastrophic = True
                break

        return extreme_or_catastrophic

    except Exception as e:
        print(
            f"does_forecast_contain_extreme_or_catastrophic_fire_danger failed due to this error: {e}"
        )
        raise


# def merge_geometries_by_attribute(
#     gdf: GeoDataFrame, attribute: str, attribute_values: list
# ) -> GeoDataFrame:
#     """
#     Merges geometries in a GeoDataFrame by a specified attribute.

#     Parameters
#     ----------
#     gdf : GeoDataFrame
#         A GeoDataFrame with the geometries to merge.

#     attribute : str
#         The attribute to merge the geometries by.

#     attribute_values : list
#         The attribute values to merge the geometries by.
#     """
#     try:
       

#     except Exception as e:
#         print(f"merge_geometries_by_attribute failed due to this error: {e}")
#         raise