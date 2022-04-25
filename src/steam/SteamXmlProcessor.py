import os
from simplehttp.SimpleHttpClient import SimpleHttpClient
import pandas as pd
import xml.etree.ElementTree as ET


class SteamXmlProcessor:

    def __init__(self, data):
        self.data = data

    @classmethod
    def from_file(cls, filename: str):
        if os.path.exists(filename):
            with open(filename, "r", encoding = "utf-8") as games_file:
                return cls(games_file.read())
        else:
            raise Exception(f"{filename} does not exist")

    @classmethod
    def from_username(cls, username: str, cache_file: str = ""):
        xml_url = f'http://steamcommunity.com/id/{username}/games?tab=all&xml=1'
        httpClient = SimpleHttpClient()
        xml_contents = httpClient.get_request(xml_url, timeout = 5)

        if cache_file:
            with open(cache_file, "w", encoding = "utf-8") as games_file:
                games_file.write(xml_contents.text)

        return cls(xml_contents.text)

    # Reads the games XML returned from get_steam_xml() and outputs a pandas dataframe
    def get_game_infos(self):

        tree = ET.ElementTree(ET.fromstring(self.data))
        root = tree.getroot()

        if root.find('error') is not None:
            raise Exception("Root not found")

        game_infos = []

        for game in root.iter('game'):
            app_id_node = game.find('appID')
            if app_id_node is None:
                raise Exception("Missing AppId Node for game")
            app_id = app_id_node.text

            name_node = game.find('name')
            if name_node is None:
                raise Exception("Missing Name Node for game")
            name = name_node.text

            def propertyOrDefault(name, default: str) -> str:
                name_node = game.find(name)
                if name_node is None:
                    return default

                result = name_node.text
                if result is None:
                    return ""
                return result

            # Rest of these are optional
            logo_link = propertyOrDefault('logo', '')
            store_link = propertyOrDefault('storeLink', '')
            hours_last_2_weeks = float(
                propertyOrDefault('hoursLast2Weeks', '0.0'))
            hours_on_record = float(propertyOrDefault('hoursOnRecord', '0.0'))
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
