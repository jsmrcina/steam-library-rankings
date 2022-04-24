import os
from SimpleRequest import HttpClient
import pandas as pd
import xml.etree.ElementTree as ET


class SteamXmlProcessor:

    def __init__(self, data):
        self.data = data
        self.init = True

    @classmethod
    def from_file(cls, filename: str):
        if os.path.exists(filename):
            with open(filename, "r", encoding = "utf-8") as games_file:
                return cls(games_file.read())
        else:
            raise Exception(f"{filename} does not exist")

    @classmethod
    def from_username(cls, username: str, cache_file: str = None):
        xml_url = 'http://steamcommunity.com/id/{0}/games?tab=all&xml=1'.format(
            username)
        httpClient = HttpClient()
        xml_contents = httpClient.get_request(xml_url, timeout = 5)

        if cache_file:
            with open(cache_file, "w", encoding = "utf-8") as games_file:
                games_file.write(xml_contents.text)

        return cls(xml_contents.text)

    # Reads the games XML returned from get_steam_xml() and outputs a pandas dataframe
    def get_game_infos(cls):

        tree = ET.ElementTree(ET.fromstring(cls.data))
        root = tree.getroot()

        if root.find('error') is not None:
            raise Exception("Root not found")

        game_infos = []

        for game in root.iter('game'):
            app_id = game.find('appID').text
            name = game.find('name').text

            propertyOrDefault = lambda name, default: (game.find(
                name).text) if (game.find(name) is not None) else default

            # Rest of these are optional
            logo_link = propertyOrDefault('logo', '')
            store_link = propertyOrDefault('storeLink', '')
            hours_last_2_weeks = float(propertyOrDefault('hoursLast2Weeks', 0))
            hours_on_record = float(propertyOrDefault('hoursOnRecord', 0))
            stats_link = propertyOrDefault('statsLink', '')
            global_stats_link = propertyOrDefault('globalStatsLink', '')

            game_infos.append(
                (app_id, name, logo_link, store_link, hours_last_2_weeks,
                 hours_on_record, stats_link, global_stats_link))

        df = pd.DataFrame.from_records(game_infos,
                                       columns = [
                                           'AppId', 'Name', 'LogoLink',
                                           'StoreLink', 'HoursLast2Weeks',
                                           'HoursOnRecord', 'StatsLink',
                                           'GlobalStatsLink'
                                       ])
        df = df.astype(
            dtype = {
                'AppId': "int64",
                'Name': "object",
                'LogoLink': "object",
                'StoreLink': "object",
                'HoursLast2Weeks': "int64",
                'HoursOnRecord': "int64",
                'StatsLink': "object",
                'GlobalStatsLink': "object"
            })
        df.set_index('AppId', inplace = True)

        return df
