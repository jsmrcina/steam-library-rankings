import os
import json
from typing import Any

from simplehttp.SimpleHttpClient import SimpleHttpClient
import pandas as pd


class SteamXmlProcessor:

    def __init__(self, data: dict[str, Any]):
        self.data = data

    @classmethod
    def from_file(cls, filename: str):
        if os.path.exists(filename):
            with open(filename, "r", encoding="utf-8") as f:
                return cls(json.load(f))
        else:
            raise Exception(f"{filename} does not exist")

    @classmethod
    def from_username(cls, api_key: str, username: str, cache_file: str = ""):
        http_client = SimpleHttpClient()

        resolve_url = (
            "https://api.steampowered.com/ISteamUser/"
            "ResolveVanityURL/v0001/")
        resolve_response = http_client.get_request(
            resolve_url,
            parameters={"key": api_key, "vanityurl": username},
            timeout=10
        )
        resolve_data = resolve_response.json()

        if resolve_data["response"]["success"] != 1:
            raise Exception(f"Could not resolve Steam username: {username}")

        steam_id = resolve_data["response"]["steamid"]

        games_url = (
            "https://api.steampowered.com/IPlayerService/"
            "GetOwnedGames/v0001/")
        games_response = http_client.get_request(
            games_url,
            parameters={
                "key": api_key,
                "steamid": steam_id,
                "include_appinfo": 1,
                "include_played_free_games": 1,
                "format": "json",
            },
            timeout=10
        )
        games_data = games_response.json()

        if cache_file:
            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump(games_data, f)

        return cls(games_data)

    def get_game_infos(self):
        games = self.data.get("response", {}).get("games", [])

        game_infos = []
        for game in games:
            app_id = game["appid"]
            name = game.get("name", "Unknown")

            img_hash = game.get("img_icon_url", "")
            logo_link = (
                "https://media.steampowered.com/steamcommunity/public/"
                f"images/apps/{app_id}/{img_hash}.jpg"
                if img_hash else ""
            )
            store_link = f"https://store.steampowered.com/app/{app_id}"

            # API returns playtime in minutes; convert to integer hours.
            # playtime_forever is online-only; playtime_disconnected holds
            # time played in Steam offline mode and must be added separately.
            hours_last_2_weeks = int(game.get("playtime_2weeks", 0) / 60)
            hours_on_record_online = int(game.get("playtime_forever", 0) / 60)
            hours_on_record = int(
                (game.get("playtime_forever", 0) +
                 game.get("playtime_disconnected", 0)) / 60
            )
            hours_on_record_deck = int(
                game.get("playtime_deck_forever", 0) / 60
            )

            game_infos.append((
                app_id, name, logo_link, store_link,
                hours_last_2_weeks, hours_on_record_online, hours_on_record,
                hours_on_record_deck, "", ""
            ))

        df = pd.DataFrame.from_records(
            game_infos,
            columns=[
                "AppId", "Name", "LogoLink", "StoreLink",
                "HoursLast2Weeks", "HoursOnRecordOnline", "HoursOnRecord",
                "HoursOnRecordDeck", "StatsLink", "GlobalStatsLink"
            ]
        )
        df = df.astype(dtype={
            "AppId": "int64",
            "Name": "object",
            "LogoLink": "object",
            "StoreLink": "object",
            "HoursLast2Weeks": "int64",
            "HoursOnRecordOnline": "int64",
            "HoursOnRecord": "int64",
            "HoursOnRecordDeck": "int64",
            "StatsLink": "object",
            "GlobalStatsLink": "object",
        })
        df.set_index("AppId", inplace=True)

        return df
