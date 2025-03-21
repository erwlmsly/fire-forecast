# fire-forecast
A python program to create wildfire forecast summary maps for the US and Australia

## What does this repo do?

This repository contains a script that scrapes fire danger ratings from the Australian Bureau of Meteorology (BOM) and the Storm Prediction Center (SPC) Fire Weather Outlooks. It then generates summary maps for the next 4 days, highlighting areas with significant fire weather concerns.

## Features

- Scrapes fire danger ratings from the Australian BOM website.
- Retrieves fire weather outlooks from the SPC.
- Generates summary maps for the next 4 days.
- Highlights areas with significant fire weather concerns.
- Saves the generated maps to the `outputs` folder.

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/yourusername/fire-forecast.git
    cd fire-forecast
    ```

2. Install the dependencies using Poetry:
    ```sh
    poetry install
    ```

## Usage

1. Run the main script:
    ```sh
    poetry run python main.py
    ```

2. The generated maps will be saved in the `outputs` folder.

## Project Structure

## Acknowledgements

All spatial data is generated from the following agencies:

- [Bureau of Meteorology (BOM)](http://www.bom.gov.au/)
- [Storm Prediction Center (SPC)](https://www.spc.noaa.gov/)
