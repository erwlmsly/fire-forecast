# plotting utilities

from datetime import datetime, timedelta, timezone
from json import loads
from tempfile import NamedTemporaryFile
from typing import Dict

import cartopy.crs as ccrs
import matplotlib.pyplot as plt
from cartopy.io.img_tiles import GoogleTiles
from geopandas import GeoDataFrame
from matplotlib import font_manager as fm
from matplotlib.patches import Patch
from requests import get
from shapely.geometry import shape


def _country_extent_coordinates(name: str) -> tuple:
    """
    Returns a tuple of floats representing a country's extent (x0, x1, y0, y1) in wgs 84

    Parameters
    ----------
    name: str
        The name of the country for who's country extent coordinates you want
    """
    try:
        coords = {
            "Australia": (105.338953078, 161.569469029, -42.0345972634, -8.5681857235),
            "United States": (
                -122.00601061058944,
                -71.73406869478453,
                21.727238911948035,
                49.879472253540195,
            ),  # continental
        }

        return coords[name]
    except Exception as e:
        print(f"country_extent_coordinates failed due to this error:\n{e}")
        raise


def _get_space_mono_font_from_github():
    """
    Downloads the Space Mono font from the google fonts GitHub repository and
    stores it within a temp file which is then loaded into a FontProperties
    object for use in plots

    Returns: a matblotlib.font_manager.FontProperties object with the Space Mono
        font
    """
    try:
        # google fonts url
        github_url = "https://github.com/google/fonts/blob/main/ofl/spacemono/SpaceMono-Regular.ttf"
        url = github_url + "?raw=true"  # You want the actual file, not some html

        # get the data from github
        response = get(url, timeout=120)

        # add the byte content into an object
        font_bytes = response.content

        # create a temporare file
        f = NamedTemporaryFile(delete=False, suffix=".ttf")

        # write the bytes to that file
        f.write(font_bytes)

        # close it so its deleted
        f.close()

        # create a font properties object for use in the plots
        return fm.FontProperties(fname=f.name)
    except Exception as e:
        print(f"_get_font_font_from_github failed due to this error: {e}")
        raise


def plot_fire_weather_outlooks(
    storm_prediction_center_fire_weather_outlooks: dict,
    font: fm.FontProperties = _get_space_mono_font_from_github(),
) -> None:
    """
    Plots the fire weather outlooks for the next 4 days. Returns a png file to the outputs folder.

    Parameters
    ----------
    storm_prediction_center_fire_weather_outlooks: dict
        A dictionary containing the fire weather outlooks for the next 4 days. The keys are the days and the values are dictionaries containing the fire weather outlooks and dry lightning outlooks for the day.

        Example:
        {
            '0': { # day of the forecast
                'fire_wx_outlook_geojson': {
                    'type': 'FeatureCollection',
                    'features': []
                },
                'dry_lightning_geojson': {
                    'type': 'FeatureCollection',
                    'features': []
                }
            },
        }
    """
    try:
        # print message to screen
        print("Plotting Storm Prediction Center Fire Weather Outlooks")

        # Create a figure with 4 subplots
        fig, axs = plt.subplots(
            2, 2, figsize=(10, 7), subplot_kw={"projection": ccrs.LambertConformal()}
        )

        # each the four maps {row, col}
        plot_sections = [axs[0, 0], axs[0, 1], axs[1, 0], axs[1, 1]]

        for day, plot_section in zip(
            storm_prediction_center_fire_weather_outlooks, plot_sections, strict=False
        ):

            fire_wx_outlook_geojson = storm_prediction_center_fire_weather_outlooks[
                day
            ]["fire_wx_outlook_geojson"]
            dry_lightning_geojson = storm_prediction_center_fire_weather_outlooks[day][
                "dry_lightning_geojson"
            ]

            # initalize a dict for plotting layers
            layers_to_plot = {
                "fire_wx_outlook_gdf": (
                    GeoDataFrame.from_features(
                        fire_wx_outlook_geojson["features"], crs=4326
                    )
                    if fire_wx_outlook_geojson["features"]
                    else None
                ),
                "dry_lightning_gdf": (
                    GeoDataFrame.from_features(
                        dry_lightning_geojson["features"], crs=4326
                    )
                    if dry_lightning_geojson["features"]
                    else None
                ),
            }

            # plot the stck images
            tiler = GoogleTiles(style="street")

            # add the tiles to the map
            plot_section.add_image(tiler, 4)

            # dn is what determines the color of the polygon, if they're all zero, then no fire weather concerns
            all_dn_zero = True

            # plot the layers in layers_to_plot
            for layer in layers_to_plot.values():
                if layer is not None:
                    for feature in layer.iterfeatures():
                        geom = shape(feature["geometry"])
                        dn = feature["properties"].get("dn", None)

                        if dn != 0:
                            all_dn_zero = False

                        # check for a fill value
                        fill = feature["properties"].get("fill", None)
                        if fill == " ":
                            fill = "none"

                        # conditional symbology based on dn value
                        if dn == 5:
                            facecolor = "orange"
                            edgecolor = "darkorange"
                        elif dn == 8:
                            facecolor = "red"
                            edgecolor = "darkred"
                        elif dn == 10:
                            facecolor = "purple"
                            edgecolor = "#4B0082"  # dark purple
                        else:
                            facecolor = "none"
                            edgecolor = fill

                        # add the geometry to the plot
                        plot_section.add_geometries(
                            [geom],
                            ccrs.PlateCarree(),
                            facecolor=facecolor,
                            edgecolor=edgecolor,
                            alpha=0.5,
                            linewidth=2,
                        )

            # if there's no layers
            if all_dn_zero:
                # add a text annotation
                plot_section.text(
                    0.5,
                    0.5,
                    "Limited Fire Weather Concerns",
                    ha="center",
                    va="center",
                    transform=plot_section.transAxes,
                    color="green",
                    fontproperties=font,
                    fontsize=12,
                    bbox={
                        "facecolor": "white",
                        "edgecolor": "green",
                        "boxstyle": "round,pad=0.5",
                    },
                )

            # set the extent
            plot_section.set_extent(_country_extent_coordinates("United States"))

            # set the title
            # calculate the date for the current day
            current_date_utc = datetime.now(timezone.utc) + timedelta(days=int(day))

            # format the date to include the day name and the date (e.g., Monday Jan 01)
            formatted_date = current_date_utc.strftime("%A %b %d")

            # set the title
            plot_section.set_title(f"{formatted_date}", fontproperties=font)

        # Create custom legend handles
        legend_handles = [
            Patch(facecolor="orange", edgecolor="darkorange", label="Elevated"),
            Patch(facecolor="red", edgecolor="darkred", label="Critical"),
            Patch(facecolor="purple", edgecolor="#4B0082", label="Extreme"),
        ]

        # Add legend to the plot
        fig.legend(
            title="Fire Weather Outlook",
            handles=legend_handles,
            loc="upper right",
            ncol=1,
            bbox_to_anchor=(1.0, 0.91),
            prop=font,
            # frameon=False,
        )

        # set the overall figure title
        fig.suptitle(
            "Storm Prediction Center Fire Weather Outlooks",
            fontsize=16,
            fontproperties=font,
        )

        # create a new current date variable
        current_date_utc = datetime.now(timezone.utc)

        # add an issued date time test to the lower left corner
        fig.text(
            0.01,
            0.01,
            f"Issued: {current_date_utc.strftime('%Y-%m-%d %H:%M')} UTC",
            fontsize=8,
            color="black",
            ha="left",
            va="bottom",
            fontproperties=font,
        )

        # set a tight layout
        plt.tight_layout()

        # Adjust space between subplots
        # Adjust space between subplots
        plt.subplots_adjust(
            wspace=0.0001, hspace=0.125, top=0.9, bottom=0.05, right=0.9, left=0
        )

        fig.set_size_inches(12.8, 7.2)

        # create a datetime object for current utc ime and format it to YYYYMMDD_HHM format
        current_date_utc_yyyymmdd_str = current_date_utc.strftime("%Y%m%d")

        # save the plot to the outputs folderS
        plt.savefig(
            f"outputs\\fire_wx_outlook_spc_{current_date_utc_yyyymmdd_str}.png",
            dpi=300,
        )

        # print message that the polt was saved
        print("Fire Weather Outlook maps completed and saved to outputs folder")

    except Exception as e:
        print(f"plot_fire_weather_outlooks failed due to this error:\n{e}")
        raise


def plot_bom_fire_danger_ratings(
    bom_fire_danger: Dict[str, GeoDataFrame],
    font: fm.FontProperties = _get_space_mono_font_from_github(),
) -> None:
    """
    Plots the next four days of the Australian Bureau of Meteorology fire danger
    ratings. Returns a png file to the outputs folder. Only rating areas with
    a fire danger index greater than or equal to 41 are plotted.

    Parameters
    ----------
    bom_fire_danger_gdf: GeoDataFrame
        A GeoDataFrame containing the fire danger ratings for the next 4 days.
    """
    try:
        # print message to screen
        print("Plotting Bureau of Meteorology Fire Danger Ratings")

        # Create a figure with 4 subplots
        fig, axs = plt.subplots(
            2,
            2,
            figsize=(7, 10),
            subplot_kw={
                "projection": ccrs.LambertConformal(
                    central_longitude=135,
                    # central_latitude=-25,
                    standard_parallels=(-50, 20),
                    cutoff=10,
                )
            },
        )

        # each the four maps {row, col}
        plot_sections = [axs[0, 0], axs[0, 1], axs[1, 0], axs[1, 1]]

        for date, plot_section in zip(bom_fire_danger, plot_sections, strict=False):
            # isolate the gdf for the current date
            bom_fire_danger_date = loads(bom_fire_danger[date])

            # convert the geojson to a geodataframe
            bom_fire_danger_gdf = GeoDataFrame.from_features(
                bom_fire_danger_date["features"], crs=4326
            )

            # identify the column with _index at the end
            for col in bom_fire_danger_gdf.columns:
                if col.endswith("_index"):
                    index_col = col
                if col.endswith("_rating"):
                    rating_col = col

            # convert the index column to an integer
            bom_fire_danger_gdf[index_col] = bom_fire_danger_gdf[index_col].astype(int)

            # filter the gdf to only include areas with a fire danger index greater than or equal to 41
            bom_fire_danger_gdf_high_extreme = bom_fire_danger_gdf[
                bom_fire_danger_gdf[index_col] >= 41
            ]

            # create a dictionary of layers to plot
            layers_to_plot = {
                "bom_fire_danger_above_40": (
                    bom_fire_danger_gdf_high_extreme
                    if len(bom_fire_danger_gdf_high_extreme)
                    else None
                )
            }

            # retrieve the google street tiles
            tiler = GoogleTiles(style="street")

            # add the tiles to the plot
            plot_section.add_image(tiler, 4)

            # asuming all layers are none
            all_layers_none = True

            # plot the layers in layers_to_plot
            for layer in layers_to_plot.values():
                if layer is not None:
                    all_layers_none = False
                    for feature in layer.iterfeatures():
                        geom = shape(feature["geometry"])
                        rating = feature["properties"].get(rating_col, None)

                        # conditional symbology based on den value
                        if rating == "High":
                            facecolor = "yellow"
                            edgecolor = "#CCCC00"  # dark yellow
                        elif rating == "Extreme":
                            facecolor = "orange"
                            edgecolor = "darkorange"
                        else:
                            facecolor = "red"
                            edgecolor = "darkred"

                        # add the geometry to the plot
                        plot_section.add_geometries(
                            [geom],
                            ccrs.PlateCarree(),
                            facecolor=facecolor,
                            edgecolor=edgecolor,
                            alpha=0.5,
                            linewidth=2,
                        )

            # if there's no layers
            if all_layers_none:
                # add a text annotation
                plot_section.text(
                    0.5,
                    0.5,
                    "Limited Fire Weather Concerns",
                    ha="center",
                    va="center",
                    transform=plot_section.transAxes,
                    color="green",
                    fontproperties=font,
                    fontsize=12,
                    bbox={
                        "facecolor": "white",
                        "edgecolor": "green",
                        "boxstyle": "round,pad=0.5",
                    },
                )

            # set the extent
            plot_section.set_extent(_country_extent_coordinates("Australia"))

            # set the title
            # calculate the date for the current day
            current_date_utc = datetime.now(timezone.utc)

            # format the date to include the day name and the date (e.g., Monday Jan 01)
            formatted_date = current_date_utc.strftime("%A %b %d")

            # date is a string, convert it to a datetime
            date_for_title = datetime.strptime(date, "%Y-%m-%d")

            # format the date to include the day name and the date (e.g., Monday Jan 01)
            title_date = date_for_title.strftime("%A %b %d")

            # set the title
            plot_section.set_title(f"{title_date}", fontproperties=font)

        # Create custom legend handles
        legend_handles = [
            Patch(facecolor="yellow", edgecolor="#CCCC00", label="High"),
            Patch(facecolor="orange", edgecolor="darkorange", label="Extreme"),
            Patch(facecolor="red", edgecolor="darkred", label="Catastrophic"),
        ]

        # Add legend to the plot
        fig.legend(
            title="Fire Danger",
            handles=legend_handles,
            loc="upper right",
            ncol=1,
            bbox_to_anchor=(0.99, 0.91),
            prop=font,
            # frameon=False,
        )

        # set the overall figure title
        fig.suptitle(
            "Bureau of Meteorology Fire Danger Ratings",
            fontsize=16,
            fontweight="bold",
            fontproperties=font,
        )

        # add an issued date time test to the lower left corner
        fig.text(
            0.01,
            0.01,
            f"Issued: {current_date_utc.strftime('%Y-%m-%d %H:%M')} UTC",
            fontsize=8,
            color="black",
            ha="left",
            va="bottom",
            fontproperties=font,
        )

        # set a tight layout
        plt.tight_layout()

        # Adjust space between subplots
        plt.subplots_adjust(
            wspace=-0.1, hspace=0.125, top=0.9, bottom=0.05, right=0.9, left=0
        )

        fig.set_size_inches(12.8, 7.2)

        # create a datetime object for current utc ime and format it to YYYYMMDD_HHM format
        current_date_utc_yyyymmdd_str = current_date_utc.strftime("%Y%m%d")

        # save the plot to the outputs folderS
        plt.savefig(
            f"outputs\\fire_wx_outlook_bom_{current_date_utc_yyyymmdd_str}.png",
            dpi=300,
        )

        # print message that the polt was saved
        print("Fire Weather Outlook maps completed and saved to outputs folder")

    except Exception as e:
        print(f"plot_bom_fire_danger_ratings failed due to this error:\n{e}")
        raise
