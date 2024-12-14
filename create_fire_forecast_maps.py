from utils.plotting_utils import plot_fire_weather_outlooks
from utils.web_scraping_utils import (
    get_storm_prediction_center_fire_weather_outlooks,
)


def main():

    spc_fire_weather_days_1_to_4 = get_storm_prediction_center_fire_weather_outlooks()

    plot_fire_weather_outlooks(spc_fire_weather_days_1_to_4)


if __name__ == "__main__":
    main()
