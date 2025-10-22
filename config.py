from pydantic_settings import BaseSettings


class Environment(BaseSettings):
    # Fire weather outlook sources

    # Storm Prediction Center (SPC) Fire Weather Outlooks
    # Day 1
    # Storm Prediction Center (SPC) Fire Weather Outlooks and dry lightning forecast
    SPC_FIRE_WX_DAY1: dict = {
        "fire_wx_outlook_url": "https://mapservices.weather.noaa.gov/vector/rest/services/fire_weather/SPC_firewx/MapServer/1",
        "dry_lightning_url": "https://mapservices.weather.noaa.gov/vector/rest/services/fire_weather/SPC_firewx/MapServer/2",
    }
    SPC_FIRE_WX_DAY2: dict = {
        "fire_wx_outlook_url": "https://mapservices.weather.noaa.gov/vector/rest/services/fire_weather/SPC_firewx/MapServer/4",
        "dry_lightning_url": "https://mapservices.weather.noaa.gov/vector/rest/services/fire_weather/SPC_firewx/MapServer/5",
    }
    SPC_FIRE_WX_DAY3: dict = {
        "fire_wx_outlook_url": "https://mapservices.weather.noaa.gov/vector/rest/services/fire_weather/SPC_firewx/MapServer/7",
        "dry_lightning_url": "https://mapservices.weather.noaa.gov/vector/rest/services/fire_weather/SPC_firewx/MapServer/8",
    }
    SPC_FIRE_WX_DAY4: dict = {
        "fire_wx_outlook_url": "https://mapservices.weather.noaa.gov/vector/rest/services/fire_weather/SPC_firewx/MapServer/10",
        "dry_lightning_url": "https://mapservices.weather.noaa.gov/vector/rest/services/fire_weather/SPC_firewx/MapServer/11",
    }

    # Australia fire danger ratings
    AUSTRALIA_FIRE_DANGER_RATINGS: str = (
        "https://services1.arcgis.com/vHnIGBHHqDR6y0CR/arcgis/rest/services/Fire_Districts_-_4_Day_Forecast/FeatureServer/5"
    )
