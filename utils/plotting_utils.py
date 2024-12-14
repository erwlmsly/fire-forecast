# plotting utilities

import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt
from geopandas import GeoDataFrame
from shapely.geometry import shape


def plot_fire_weather_outlooks(storm_prediction_center_fire_weather_outlooks: dict):

    # Create a figure with 4 subplots
    _fig, axs = plt.subplots(
        2, 2, figsize=(15, 10), subplot_kw={"projection": ccrs.LambertConformal()}
    )

    for day in range(len(storm_prediction_center_fire_weather_outlooks)):

        # store the geojson data for  the day in different objects
        fire_wx_outlook_geojson = storm_prediction_center_fire_weather_outlooks[day][
            "fire_wx_outlook_geojson"
        ]
        dry_lightning_geojson = storm_prediction_center_fire_weather_outlooks[day][
            "dry_lightning_geojson"
        ]

        # Create a GeoDataFrames from the GeoJSON data
        if len(fire_wx_outlook_geojson["features"]) > 0:
            fire_wx_outlook_gdf = GeoDataFrame.from_features(fire_wx_outlook_geojson)
        else:
            fire_wx_outlook_gdf = None
        if len(dry_lightning_geojson["features"]) > 0:
            dry_lightning_gdf = GeoDataFrame.from_features(dry_lightning_geojson)
        else:
            dry_lightning_gdf = None

        # specify the row and column where the data will be plotted
        row = day // 2
        col = day % 2
        ax = axs[row, col]

        # Plot the fire weather outlooks
        if not fire_wx_outlook_gdf.empty:
            fire_wx_outlook_gdf.plot(ax=ax, color="red", alpha=0.5)
        if not dry_lightning_gdf.empty:
            dry_lightning_gdf.plot(ax=ax, color="yellow", alpha=0.5)

        # Add map features

    plt.tight_layout()
    plt.show()
