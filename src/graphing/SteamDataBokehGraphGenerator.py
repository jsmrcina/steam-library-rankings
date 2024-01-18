import logging
import pandas as pd

from bokeh.plotting import figure, save, output_file
from bokeh.models import ColumnDataSource, HoverTool, LabelSet
from bokeh.palettes import Turbo256 as palette
from bokeh.transform import linear_cmap
from bokeh.util import logconfig


class SteamDataBokehGraphGenerator:

    def __init__(self, decorated_game_infos, output_directory = "."):
        self.decorated_game_infos = decorated_game_infos
        self.output_directory = output_directory

        # Make bokeh log to file
        logconfig.basicConfig(level = logging.DEBUG, filename = "output.log")

    def generate_most_played_games_graph(self):
        # Plot most played games (ignore non played games)
        colName = "HoursOnRecord"
        output_file(f"{self.output_directory}/MostPlayed.html")

        most_played_games = pd.DataFrame.copy(self.decorated_game_infos)
        most_played_games.drop(
            most_played_games[most_played_games[colName] == 0].index,
            inplace = True)

        # Take just top 30
        most_played_games = most_played_games.nlargest(50, colName)
        most_played_games = most_played_games.sort_values(by = [colName],
                                                          ascending = True)

        tooltips = [('Game', '@Name'), ('Hours Played', '@HoursOnRecord'),
                    ('Rating', '@BayesianAverage')]

        select_tools = [
            'box_select', 'lasso_select', 'poly_select', 'tap', 'reset'
        ]

        color_mapper = linear_cmap(field_name = colName,
                                   palette = palette,
                                   low = min(most_played_games[colName]),
                                   high = max(most_played_games[colName]))

        # Weird issue here where the text in LabelSet must be a string or it won't work, so decorate the data with strings
        most_played_games[f"{colName}Text"] = most_played_games[colName].apply(
            lambda x: str(x))
        data_source = ColumnDataSource(most_played_games)

        p = figure(
            y_range = most_played_games["Name"],
            width = 2000,
            height = 1250,
            title = "Most Played Games of All Time",
            tools = select_tools,
            x_range = (0, max(most_played_games[colName] + 20)),
        )

        p.title.text_font_size = '32pt'
        p.yaxis.major_label_text_font_size = "12pt"
        p.xaxis.major_label_text_font_size = "12pt"
        p.xaxis[0].axis_label = 'Hours Played'

        p.hbar(y = "Name",
               left = 0,
               right = colName,
               height = 0.5,
               source = data_source,
               color = color_mapper)
        p.add_tools(HoverTool(tooltips = tooltips))

        labels = LabelSet(x = colName,
                          y = "Name",
                          level = 'annotation',
                          text_color = 'black',
                          x_offset = 5,
                          y_offset = -6,
                          text = f"{colName}Text",
                          source = data_source)

        p.add_layout(labels)
        save(p)

    def generate_most_played_games_2weeks_graph(self):
        # Plot most played games in last 2 weeks
        colName = "HoursLast2Weeks"
        output_file(f"{self.output_directory}/MostPlayedLast2Weeks.html")

        most_played_games_2w = pd.DataFrame.copy(self.decorated_game_infos)
        most_played_games_2w.drop(
            most_played_games_2w[most_played_games_2w[colName] == 0].index,
            inplace = True)
        most_played_games_2w = most_played_games_2w.sort_values(
            by = [colName], ascending = False)

        # Weird issue here where the text in LabelSet must be a string or it won't work, so decorate the data with strings
        most_played_games_2w[f"{colName}Text"] = most_played_games_2w[
            colName].apply(lambda x: "{:.2f}".format(x))
        data_source = ColumnDataSource(most_played_games_2w)

        p = figure(x_range = most_played_games_2w["Name"],
                   y_range = (0, max(most_played_games_2w[colName] + 20)),
                   width = 2000,
                   title = "Most Played Games in Last 2 Weeks")

        p.vbar(x = "Name", top = colName, source = data_source, width = 0.5)
        p.xaxis.major_label_orientation = "vertical"
        p.xgrid.grid_line_color = None
        p.xaxis.major_label_text_font_size = "12pt"
        p.y_range.start = 0
        p.yaxis[0].axis_label = 'Hours Played'

        labels = LabelSet(x = "Name",
                          y = colName,
                          level = 'annotation',
                          text_color = 'black',
                          x_offset = -15,
                          y_offset = 10,
                          text = f"{colName}Text",
                          source = data_source)

        p.add_layout(labels)
        save(p)

    def generate_most_played_games_versus_rating_graph(self):
        # Plot most played games versus their rating
        colName = "HoursOnRecord"
        output_file(f"{self.output_directory}/MostPlayedVsRating.html")

        most_played_games = pd.DataFrame.copy(self.decorated_game_infos)
        most_played_games = most_played_games.sort_values(by = [colName],
                                                          ascending = False)

        tooltips = [('Game', '@Name'), ('Hours Played', '@HoursOnRecord'),
                    ('Rating', '@BayesianAverage')]

        color_mapper = linear_cmap(field_name = colName,
                                   palette = palette,
                                   low = min(most_played_games[colName]),
                                   high = max(most_played_games[colName]))

        select_tools = ['tap', 'reset', 'box_zoom']

        # For the most played and highest rated games, add names as labels.
        most_played_games["DisplayName"] = most_played_games.apply(
            axis = 1, func = lambda x: x["Name"] if x[colName] > 75 else "")
        data_source = ColumnDataSource(most_played_games)

        labels = LabelSet(x = colName,
                          y = "BayesianAverage",
                          level = 'annotation',
                          text_color = 'black',
                          x_offset = 10,
                          y_offset = -5,
                          text = "DisplayName",
                          source = data_source,
                          text_font_size = "8pt")

        p = figure(height = 1000,
                   width = 2000,
                   title = "Most played vs ranking",
                   tools = select_tools,
                   x_range = (0, max(most_played_games[colName]) + 50))

        p.circle(x = colName,
                 y = "BayesianAverage",
                 color = color_mapper,
                 source = data_source,
                 size = 10)

        p.xaxis[0].axis_label = 'Hours Played'
        p.yaxis[
            0].axis_label = 'Positive vs Negative Rating % Adjusted Using a Bayesian average'

        p.add_tools(HoverTool(tooltips = tooltips))
        p.add_layout(labels)
        save(p)

    def generate_best_unplayed_games_average(self):
        # Plot best ranked unplayed games
        colName = "RatingsRatio"
        output_file(f"{self.output_directory}/UnplayedPlainRating.html")

        tooltips = [('Game', '@Name'), ('Rating', '@RatingsRatio')]

        select_tools = [
            'box_select', 'lasso_select', 'poly_select', 'tap', 'reset'
        ]

        best_unplayed_games = pd.DataFrame.copy(self.decorated_game_infos)
        best_unplayed_games.drop(best_unplayed_games[
            best_unplayed_games["HoursOnRecord"] != 0].index,
                                 inplace = True)

        # Remove DLC and tools (0% and 100% rated)
        best_unplayed_games.drop(
            best_unplayed_games[best_unplayed_games[colName] == 0].index,
            inplace = True)
        best_unplayed_games.drop(
            best_unplayed_games[best_unplayed_games[colName] == 100].index,
            inplace = True)

        # Take just top 30
        best_unplayed_games = best_unplayed_games.nlargest(50, colName)
        best_unplayed_games = best_unplayed_games.sort_values(by = [colName],
                                                              ascending = True)

        color_mapper = linear_cmap(field_name = colName,
                                   palette = palette,
                                   low = min(best_unplayed_games[colName]),
                                   high = max(best_unplayed_games[colName]))

        # Weird issue here where the text in LabelSet must be a string or it won't work, so decorate the data with strings
        best_unplayed_games[f"{colName}Text"] = best_unplayed_games[
            colName].apply(lambda x: "{:.2f}".format(x))

        data_source = ColumnDataSource(best_unplayed_games)

        min_range = int(min(best_unplayed_games[colName]) - 1)
        max_range = int(max(best_unplayed_games[colName]) + 2)
        p = figure(y_range = best_unplayed_games["Name"],
                   x_range = (min_range, max_range),
                   width = 2000,
                   height = 1250,
                   title = "Best unplayed games",
                   tools = select_tools)

        p.title.text_font_size = '32pt'
        p.yaxis.major_label_text_font_size = "12pt"
        p.xaxis.major_label_text_font_size = "12pt"
        p.xaxis[0].axis_label = 'Positive vs. Negative Ratings %'

        p.hbar(y = "Name",
               left = 0,
               right = colName,
               height = 0.5,
               source = data_source,
               color = color_mapper)

        labels = LabelSet(x = colName,
                          y = "Name",
                          level = 'annotation',
                          text_color = 'black',
                          x_offset = 5,
                          y_offset = -6,
                          text = f"{colName}Text",
                          source = data_source)

        p.add_layout(labels)

        p.add_tools(HoverTool(tooltips = tooltips))
        save(p)

    def generate_best_unplayed_games_bayesian_average(self):
        # Plot best ranked unplayed games
        colName = "BayesianAverage"
        output_file(f"{self.output_directory}/UnplayedBayesian.html")

        tooltips = [('Game', '@Name'), ('Rating', '@BayesianAverage')]

        select_tools = [
            'box_select', 'lasso_select', 'poly_select', 'tap', 'reset'
        ]

        best_unplayed_games = pd.DataFrame.copy(self.decorated_game_infos)
        best_unplayed_games.drop(best_unplayed_games[
            best_unplayed_games["HoursOnRecord"] != 0].index,
                                 inplace = True)

        # Remove DLC and tools (0% and 100% rated)
        best_unplayed_games.drop(
            best_unplayed_games[best_unplayed_games[colName] == 0].index,
            inplace = True)
        best_unplayed_games.drop(
            best_unplayed_games[best_unplayed_games[colName] == 100].index,
            inplace = True)

        # Take just top 30
        best_unplayed_games = best_unplayed_games.nlargest(50, colName)
        best_unplayed_games = best_unplayed_games.sort_values(by = [colName],
                                                              ascending = True)

        color_mapper = linear_cmap(field_name = colName,
                                   palette = palette,
                                   low = min(best_unplayed_games[colName]),
                                   high = max(best_unplayed_games[colName]))

        # Weird issue here where the text in LabelSet must be a string or it won't work, so decorate the data with strings
        best_unplayed_games[f"{colName}Text"] = best_unplayed_games[
            colName].apply(lambda x: "{:.2f}".format(x))

        data_source = ColumnDataSource(best_unplayed_games)

        min_range = int(min(best_unplayed_games[colName]) - 1)
        max_range = int(max(best_unplayed_games[colName]) + 2)
        p = figure(y_range = best_unplayed_games["Name"],
                   x_range = (min_range, max_range),
                   width = 2000,
                   height = 1250,
                   title = "Best unplayed games",
                   tools = select_tools)

        p.title.text_font_size = '32pt'
        p.yaxis.major_label_text_font_size = "12pt"
        p.xaxis.major_label_text_font_size = "12pt"
        p.xaxis[
            0].axis_label = 'Positive vs. Negative Ratings % Adjusted Using a Bayesian Average'

        p.hbar(y = "Name",
               left = 0,
               right = colName,
               height = 0.5,
               source = data_source,
               color = color_mapper)

        labels = LabelSet(x = colName,
                          y = "Name",
                          level = 'annotation',
                          text_color = 'black',
                          x_offset = 5,
                          y_offset = -6,
                          text = f"{colName}Text",
                          source = data_source)

        p.add_layout(labels)

        p.add_tools(HoverTool(tooltips = tooltips))
        save(p)
