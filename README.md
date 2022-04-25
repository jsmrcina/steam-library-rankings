# Description

This Jupyter Notebook allows you to quickly query a public Steam XML for a given user and create some visualizations about their Steam game library.

# Usage

1. Make sure your game information on Steam is set to 'Public'
2. Clone the repo
3. Create a `data` folder in the root directory
4. From the root directory, run
```
python src/main/main.py
```
5. Go get a coffee, each game takes ~2 seconds to query due to query limits on SteamSpy API, so 500 games will take about 17 minutes. The script will create caches under the data folder to make subsequent queries almost instant.
6. Under the data folder, you can find the analyzed data: your steam XML, a CSV with all of the raw data, and a few Bokeh graphs summarizing that data

Any issues will be logged into the output.log file.