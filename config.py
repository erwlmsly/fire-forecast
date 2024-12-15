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

    # Australia fire danger rating tables
    AUSTRALIA_NEW_SOUTH_WALES_FIRE_DANGER_RATING_TABLE: str = (
        "http://www.bom.gov.au/nsw/forecasts/fire-danger-ratings.shtml"
    )
    AUSTRALIA_VICTORIA_FIRE_DANGER_RATING_TABLE: str = (
        "http://www.bom.gov.au/vic/forecasts/fire-danger-ratings.shtml"
    )
    AUSTRALIA_QUEENSLAND_FIRE_DANGER_RATING_TABLE: str = (
        "http://www.bom.gov.au/qld/forecasts/fire-danger-ratings.shtml"
    )
    AUSTRALIA_WESTERN_AUSTRALIA_FIRE_DANGER_RATING_TABLE: str = (
        "http://www.bom.gov.au/wa/forecasts/fire-danger-ratings.shtml"
    )
    AUSTRALIA_SOUTH_AUSTRALIA_FIRE_DANGER_RATING_TABLE: str = (
        "http://www.bom.gov.au/sa/forecasts/fire-danger-ratings.shtml"
    )
    AUSTRALIA_TASMANIA_FIRE_DANGER_RATING_TABLE: str = (
        "http://www.bom.gov.au/tas/forecasts/fire-danger-ratings.shtml"
    )
    AUSTRALIA_NORTHERN_TERRITORY_FIRE_DANGER_RATING_TABLE: str = (
        "http://www.bom.gov.au/nt/forecasts/fire-danger-ratings.shtml"
    )
