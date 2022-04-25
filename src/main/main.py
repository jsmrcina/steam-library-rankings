import os
import logging

import pandas as pd

from steam.SteamXmlProcessor import SteamXmlProcessor
from utils.MathUtils import MathUtils
from steam.SteamSpyQuery import SteamSpyQuery
from graphing.SteamDataBokehGraphGenerator import SteamDataBokehGraphGenerator


def query_steam_data_for_user(log, directory = ""):
    # Note, your 'Game details' must be set to 'Public' for this to work.
    # This is done in your profile -> Edit Profile -> Privacy Settings -> Game details
    # To find your username, check your profile under General -> Custom URL
    print(directory)
    username = ''
    if username == '':
        if os.path.exists(f"{directory}\steam_id.dat"):
            log.info('Reading steam ID from file')
            with open(f"{directory}\steam_id.dat", "r",
                      encoding = "utf-8") as id_file:
                username = id_file.read()
        else:
            log.critical('Need steam user ID')
            raise Exception("Missing steam id")

    cache_file = f"{directory}\{username}_steam_games.xml"
    if os.path.exists(cache_file):
        xmlProcessor = SteamXmlProcessor.from_file(cache_file)
    else:
        xmlProcessor = SteamXmlProcessor.from_username(username, cache_file)

    return xmlProcessor.get_game_infos()


def main():
    log = logging.getLogger()
    fhandler = logging.FileHandler(filename = 'mylog.log', mode = 'a')
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fhandler.setFormatter(formatter)
    log.addHandler(fhandler)
    log.setLevel(logging.CRITICAL)

    # Work from pwd
    pwd = os.getcwd()
    data_directory = f"{pwd}\data"

    # Decorate our steam library info with ranking info from SteamSpy
    game_infos = query_steam_data_for_user(log, data_directory)
    decorated_game_infos = pd.DataFrame.copy(game_infos)

    steam_spy_query = SteamSpyQuery(log, data_directory)
    decorated_game_infos = steam_spy_query.get_data_for_games(
        decorated_game_infos)
    decorated_game_infos = MathUtils.add_bayesian_average_to_gamespy_dataframe(
        decorated_game_infos)

    # Do any filtering or re-arranging you want to here
    decorated_game_infos = decorated_game_infos.sort_values(
        by = ['BayesianAverage'], ascending = False)

    # DLCs have no ratings, drop them from the list
    decorated_game_infos.drop(
        decorated_game_infos[decorated_game_infos["RatingsRatio"] == 0].index,
        inplace = True)

    # Write to file for easy access
    decorated_game_infos.to_csv(f"{data_directory}\decorated_game_infos.csv")

    graph_generator = SteamDataBokehGraphGenerator(decorated_game_infos,
                                                   data_directory)
    graph_generator.generate_most_played_games_graph()
    graph_generator.generate_most_played_games_2weeks_graph()
    graph_generator.generate_most_played_games_versus_rating_graph()
    graph_generator.generate_best_unplayed_games_average()
    graph_generator.generate_best_unplayed_games_bayesian_average()


if __name__ == "__main__":
    main()
