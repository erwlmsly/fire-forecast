from utils.file_mgmt import create_outputs_folder
from utils.plotting import plot_bom_fire_danger_ratings, plot_fire_weather_outlooks
from utils.processing import (
    convert_fire_danger_gdf_to_dict_for_plotting,
    merge_fire_weather_districts_and_fire_danger_table,
    is_extreme_or_catastrophic_in_bom_fire_danger_ratings,
)
from utils.web_scraping import (
    get_storm_prediction_center_fire_weather_outlooks,
    scrape_bureau_of_meteorology_fire_danger_ratings,
)

from pickle import dump, load


def main():

    # Create an outputs folder if it does not exist
    create_outputs_folder()

    # Get the Storm Prediction Center Fire Weather Outlooks
    spc_fire_weather_days_1_to_4 = get_storm_prediction_center_fire_weather_outlooks()

    # # save the bom fire danger ratings to a pickle file
    # with open("outputs/spc_fire_weather_days_1_to_4.pkl", "wb") as f:
    #     dump(spc_fire_weather_days_1_to_4, f)

    # # turn off the web scraping and just load the pickle file
    # with open("outputs/spc_fire_weather_days_1_to_4.pkl", "rb") as f:
    #     spc_fire_weather_days_1_to_4 = load(f)

    # Create the summary maps for the next 4 days
    plot_fire_weather_outlooks(spc_fire_weather_days_1_to_4)

    # get the australian fire danger ratings
    bom_fire_danger_ratings = scrape_bureau_of_meteorology_fire_danger_ratings()

    # convert the fire danger ratings to a geodataframe
    bom_fire_danger_gdf = merge_fire_weather_districts_and_fire_danger_table(
        fire_danger_table=bom_fire_danger_ratings
    )

    bom_fire_danger_dict = convert_fire_danger_gdf_to_dict_for_plotting(
        bom_fire_danger_gdf
    )

    # # save the bom fire danger ratings to a pickle file
    # with open("outputs/bom_fire_danger_ratings.pkl", "wb") as f:
    #     dump(bom_fire_danger_dict, f)

    # # turn off the web scraping and just load the pickle file
    # with open("outputs/bom_fire_danger_ratings.pkl", "rb") as f:
    #     bom_fire_danger_dict = load(f)

    plot_bom_fire_danger_ratings(bom_fire_danger_dict)

    # print("checking for extreme or catastrophic ratings")

    # if is_extreme_or_catastrophic_in_bom_fire_danger_ratings(bom_fire_danger_dict):

    #     # plot the extreme or catastrophic fire danger ratings


if __name__ == "__main__":
    main()
