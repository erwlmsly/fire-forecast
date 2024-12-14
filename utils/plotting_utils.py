# plotting utilities

from datetime import datetime, timedelta

import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt
from geopandas import GeoDataFrame
from matplotlib.patches import Patch
from shapely.geometry import shape


def country_extent_coordinates(name:str) -> tuple:
    '''
    Returns a tuple of floats representing a country's extent (x0, x1, y0, y1) in wgs 84

    Parameters
    ----------
    name: str
        The name of the country for who's country extent coordinates you want
    '''
    try:
        coords = {
            'Australia': (113.338953078, -43.6345972634, 153.569469029, -10.6681857235),
            'United States': (-122.47601061058944, -68.73406869478453, 21.727238911948035, 49.479472253540195), #continental
        }

        return coords[name]
    except Exception as e:
        print(f"country_extent_coordinates failed due to this error:\n{e}")
        raise


def plot_fire_weather_outlooks(storm_prediction_center_fire_weather_outlooks: dict):
    '''
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
    '''
    # Create a figure with 4 subplots
    fig, axs = plt.subplots(
        2, 2, figsize=(10, 7), subplot_kw={"projection": ccrs.LambertConformal()}
    )

    #each the four maps {row, col}
    plot_sections = [
        axs[0,0],
        axs[0,1],
        axs[1,0],
        axs[1,1]
    ]

    for day, plot_section in zip(storm_prediction_center_fire_weather_outlooks, plot_sections, strict=False):

        fire_wx_outlook_geojson = storm_prediction_center_fire_weather_outlooks[day]['fire_wx_outlook_geojson']
        dry_lightning_geojson = storm_prediction_center_fire_weather_outlooks[day]['dry_lightning_geojson']

        #initalize an empty dict for plotting layers
        layers_to_plot = {
            'fire_wx_outlook_gdf': GeoDataFrame.from_features(fire_wx_outlook_geojson['features'], crs=4326) if fire_wx_outlook_geojson['features'] else None,
            'dry_lightning_gdf': GeoDataFrame.from_features(dry_lightning_geojson['features'], crs=4326) if dry_lightning_geojson['features'] else None
        }

        # plot coastlines
        plot_section.coastlines()

        # create a states object
        states_provinces = cfeature.NaturalEarthFeature(
            category='cultural',
            name='admin_1_states_provinces_lines',
            scale='50m',
            facecolor='none'
        )

        # add statelines o plot
        plot_section.add_feature(states_provinces, edgecolor='gray')

        # add country borders to plot
        plot_section.add_feature(cfeature.BORDERS, edgecolor='black')

        # asuuming all layers are nonne
        all_layers_none = True

        # plot the layers in layers_to_plot
        for layer_name, layer in layers_to_plot.items():
            if layer is not None:
                all_layers_none = False
                for feature in layer.iterfeatures():
                    geom = shape(feature['geometry'])
                    dn = feature['properties'].get('dn', None)
                    if dn == 5:
                        facecolor = 'orange'
                        edgecolor = 'darkorange'
                    elif dn == 8:
                        facecolor = 'red'
                        edgecolor = 'darkred'
                    elif dn == 10:
                        facecolor = 'purple'
                        edgecolor = 'darkpurple'
                    else:
                        facecolor = 'none'
                        edgecolor = 'black'
                    plot_section.add_geometries(
                        [geom],
                        ccrs.PlateCarree(),
                        facecolor=facecolor,
                        edgecolor=edgecolor,
                        alpha=0.5,
                        linewidth=2
                    )

        if all_layers_none:
            # add a text annotation if there is no data
            plot_section.text(
                0.5, 0.5, "Limited Fire Weather Concerns", ha='center', va='center', transform=plot_section.transAxes,
                color='green', fontweight='bold', fontsize=12
            )

        # set the extent
        plot_section.set_extent(country_extent_coordinates('United States'))

        # set the title
        # calculate the date for the current day
        current_date = datetime.utcnow() + timedelta(days=int(day))
        # format the date to include the day name and the date
        formatted_date = current_date.strftime('%A %b %d')

        # set the title
        plot_section.set_title(f"{formatted_date}")

    # Create custom legend handles
    legend_handles = [
        Patch(facecolor='orange', edgecolor='darkorange', label='Elevated'),
        Patch(facecolor='red', edgecolor='darkred', label='Critical'),
        Patch(facecolor='purple', edgecolor='#4B0082', label='Extreme')
    ]

    # Add legend to the plot
    fig.legend(handles=legend_handles, loc='lower center', ncol=3, bbox_to_anchor=(0.5, 0.45), frameon=False)

    # set the overall figure title
    fig.suptitle("Storm Prediction Center Fire Weather Outlooks", fontsize=16, fontweight='bold')

    # set a tight layout
    plt.tight_layout()

     # Adjust space between subplots
    plt.subplots_adjust(wspace=0.0001, hspace=0.1, top=0.9)

    fig.set_size_inches(12.8, 7.2)

    # create a datetime object for current utc ime and format it to YYYYMMDD_HHM format
    current_utc_time_str = datetime.utcnow().strftime('%Y%m%d_%H%M')

    # save the plot to the outputs folderS
    plt.savefig(f'outputs\\fire_wx_outlook_spc_{current_utc_time_str}.png', dpi=300)

    #plt.show()


