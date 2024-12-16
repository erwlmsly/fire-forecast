from utils.file_mgmt_utils import create_outputs_folder
from utils.plotting_utils import plot_fire_weather_outlooks
from utils.web_scraping_utils import (
    get_storm_prediction_center_fire_weather_outlooks,
    scrape_bureau_of_meteorology_fire_danger_ratings,
    convert_fire_danger_rating_table_to_geodataframe,
    convert_fire_danger_geodataframe_to_dict
)

import json

def main():

    # Create an outputs folder if it does not exist
    create_outputs_folder()

    # Get the Storm Prediction Center Fire Weather Outlooks
    spc_fire_weather_days_1_to_4 = get_storm_prediction_center_fire_weather_outlooks()

    # Create the summary maps for the next 4 days
    plot_fire_weather_outlooks(spc_fire_weather_days_1_to_4)

    # get the australian fire danger ratings
    bom_fire_danger_ratings = scrape_bureau_of_meteorology_fire_danger_ratings()

    # convert the fire danger ratings to a geodataframe
    bom_fire_danger_gdf = convert_fire_danger_rating_table_to_geodataframe(
        bom_fire_danger_ratings
    )

    # convert the fire danger geodataframe to a dictionary3
    bom_fire_danger_forecast_dict = convert_fire_danger_geodataframe_to_dict(
        fire_danger_gdf = bom_fire_danger_gdf
    )

    # print the fire danger forecast dictionary using json.dumps with indent = 3
    print(json.dumps(bom_fire_danger_forecast_dict, indent=3))



if __name__ == "__main__":
    main()
