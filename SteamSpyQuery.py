# Small module for querying data from SteamSpy
import os
import time

import pandas as pd

from SimpleRequest import HttpClient


class SteamSpyQuery:

    def __init__(self, logger = None):
        self.logger = logger
        self.httpClient = HttpClient()

    def __get_data_for_game(self, appid: str, name: str):
        if self.logger:
            self.logger.info("Request {0} from SteamSpy".format(name))
            url = "http://steamspy.com/api.php"
            parameters = {"request": "appdetails", "appid": appid}
            json_data = self.httpClient.get_request(
                url, parameters = parameters).json()
            downloaded_info = pd.DataFrame.from_dict(json_data,
                                                     orient = 'index')

            # Only look at the first game that is returned as a result
            game = downloaded_info[0]
            if self.logger:
                self.logger.debug("Finished request for {0}".format(name))

            positive = int(json_data["positive"])
            negative = int(json_data["negative"])
            return (appid, name, positive, negative, positive + negative,
                    (positive / (positive + negative)) *
                    100 if positive + negative > 0 else 0,
                    int(json_data["userscore"]),
                    int(json_data["average_forever"]),
                    int(json_data["average_2weeks"]),
                    int(json_data["median_forever"]),
                    int(json_data["median_2weeks"]))

    # Get data from SteamSpy for each game
    # The structure of game_infos must be at least two columns named 'AppId' and 'Name', with AppId being the index.
    # Setting 'in_place' to true will modify the input game_infos preserving any other existing columns.
    # Otherwise, they are discarded.
    # pull_first_n allows limiting the number of queries to the first N found.
    def get_data_for_games(self,
                           game_infos_df,
                           pull_first_n = None,
                           use_cache = True):

        cache_columns = [
            'AppId', 'Name', 'Positive', 'Negative', 'TotalRatings',
            'RatingsRatio', 'UserScore', 'AvgForever', 'Avg2Weeks',
            'MedForever', 'Med2Weeks'
        ]

        cache = pd.DataFrame(columns = cache_columns)
        if use_cache is True:
            cache_file = "steam_spy_cache.csv"
            if os.path.exists(cache_file):
                cache = pd.read_csv(cache_file, index_col = "AppId")
        else:
            cache_file = ""

        new_cache_data = []
        pulled = 0
        for index, row in game_infos_df.iterrows():
            name = row['Name']
            appid = index

            cache_found = False
            if cache.empty == False:
                cache_row = cache.loc[cache['Name'] == name]
                if cache_row.empty == False:
                    if self.logger:
                        self.logger.info("Found {0} in cache".format(name))
                    cache_found = True

            if cache_found == False:
                new_cache_data.append(self.__get_data_for_game(appid, name))
                # Per documentation, don't make more than 1 request per second
                time.sleep(2)

            pulled = pulled + 1
            if pull_first_n is not None:
                if self.logger:
                    self.logger.debug("Pulled {0} of {1}".format(
                        pulled, pull_first_n))
                if pulled == pull_first_n:
                    break

        # Turn newly queried cache info into a data frame
        new_cache = pd.DataFrame.from_records(new_cache_data,
                                              columns = cache_columns)
        new_cache = new_cache.astype(
            dtype = {
                'AppId': "int64",
                'Name': "object",
                'Positive': "int64",
                'Negative': "int64",
                'TotalRatings': "int64",
                'RatingsRatio': "float64",
                'UserScore': "int64",
                'AvgForever': "int64",
                'Avg2Weeks': "int64",
                'MedForever': "int64",
                'Med2Weeks': "int64"
            })
        new_cache.set_index("AppId", inplace = True)

        # Merge new cache and existing cache data
        final_cache = pd.concat([cache, new_cache])
        if use_cache is True:
            final_cache.to_csv(cache_file)

        # Add the new columns to the existing game_infos, drop Names since they're duplicated otherwise
        game_infos_df.drop("Name", axis = 1, inplace = True)
        return game_infos_df.join(final_cache, on = "AppId", how = 'left')