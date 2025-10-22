from utils.file_mgmt import create_outputs_folder
from utils.plotting import plot_bom_fire_danger_ratings, plot_fire_weather_outlooks
from utils.processing import (
    convert_fire_danger_gdf_to_dict_for_plotting,
    is_extreme_or_catastrophic_in_bom_fire_danger_ratings,
)
from utils.web_scraping import (
    get_storm_prediction_center_fire_weather_outlooks,
    get_australia_fire_danger_ratings,
)

# from pickle import dump, load


def main():

    # Create an outputs folder if it does not exist
    create_outputs_folder()

    # Get the Storm Prediction Center Fire Weather Outlooks
    # spc_fire_weather_days_1_to_4 = get_storm_prediction_center_fire_weather_outlooks()

    # Create the summary maps for the next 4 days
    # plot_fire_weather_outlooks(spc_fire_weather_days_1_to_4)

    # get the australian fire weather districts directly
    bom_fire_danger_gdf = get_australia_fire_danger_ratings()

    # convert to a format for plotting similar to SPC outlooks
    bom_fire_danger_dict = convert_fire_danger_gdf_to_dict_for_plotting(
        bom_fire_danger_gdf
    )

    # Create the summary map for the next 4 days
    plot_bom_fire_danger_ratings(bom_fire_danger_dict)

    # print("checking for extreme or catastrophic ratings")

    # if is_extreme_or_catastrophic_in_bom_fire_danger_ratings(bom_fire_danger_dict):

    #     # plot the extreme or catastrophic fire danger ratings


if __name__ == "__main__":
    main()
