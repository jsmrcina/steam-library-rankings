class MathUtils:

    # Add a Bayesian average to better rank the games
    @classmethod
    def __calculate_bayesian_average(cls, item_num_ratings, item_ratio_ratings,
                                     system_avg_num_ratings,
                                     system_ratio_ratings):
        b_avg = (((item_num_ratings) /
                  (item_num_ratings + system_avg_num_ratings)) *
                 item_ratio_ratings) + (
                     ((system_avg_num_ratings) /
                      (item_num_ratings + system_avg_num_ratings)) *
                     system_ratio_ratings)
        return b_avg

    @classmethod
    def add_bayesian_average_to_gamespy_dataframe(cls, to_decorate):
        # Calculate an overall average for the system
        system_ratings_avg = to_decorate["RatingsRatio"].mean()
        system_num_ratings_avg = to_decorate["TotalRatings"].mean()

        # Calculate Bayesian average
        b_averages = list(
            to_decorate.apply(lambda row: cls.__calculate_bayesian_average(
                row["TotalRatings"], row["RatingsRatio"],
                system_num_ratings_avg, system_ratings_avg),
                              axis = 1))

        # Add the new averages to the data frame
        to_decorate['BayesianAverage'] = b_averages
        return to_decorate
