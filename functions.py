import pandas as pd
def get_favorite_genre(df,user_df):

    # a) Favorite Genre
    # Each film has a list of genres, what we are doing is splitting the list of genres and calculate the duration of the most watched one
    df['genres'] = df['genres'].str.split(", ") 
    stacked_genres_df = df.explode('genres') # we transform a column with lists into multiple rows
    genre_duration_df = stacked_genres_df.groupby(['user_id', 'genres'])['duration'].sum().reset_index() # sum the duration of each genre for each user
    favorite_genre_df = genre_duration_df.loc[genre_duration_df.groupby('user_id')['duration'].idxmax()] # get most favorite genre for each user
    favorite_genre_df = favorite_genre_df.rename(columns={'genres': 'favorite_genre'}) # change column name

    # Merge to user_df, without 'duration' column
    user_df = user_df.merge(favorite_genre_df[['user_id', 'favorite_genre']], on='user_id', how='left').drop(columns=[0])

    return(user_df)


def get_average_click_duration(df,user_df):

    # Calculate average click duration for each user, round it to 2 decimal places
    average_duration_df = df.groupby(['user_id'])['duration'].mean().round(2).reset_index(name='average_click_duration')

    # Merge with user_df
    user_df = user_df.merge(average_duration_df[['user_id', 'average_click_duration']], on='user_id', how='left')

    return(user_df)


# Define function to get time of day
def getTimeOfDay(row):
    hour = row.hour

    if 5 < hour < 12:  
        return "Morning"
    elif 12 <= hour < 21:
        return "Afternoon"
    else:
        return "Night"
    
def get_timeday_df(df,user_df):
    # We create a new df in order to better work with it
    df_1 = pd.DataFrame()
    df_1['datetime'] = pd.to_datetime(df['datetime'])
    df_1['user_id'] = df['user_id']
    df_1['duration'] = df['duration']

    # Get time of day by adding duration to datetime
    df_1['time_of_day'] = df_1['datetime'] + pd.to_timedelta(df_1['duration'],unit='s')
    # Apply function and get day  
    df_1['time_of_day'] = df_1['datetime'].apply(getTimeOfDay)


    # Now count how many occurences for each time of day for each user and get the highest one
    most_active_timeday= df_1.groupby(['user_id', 'time_of_day'])['duration'].sum().reset_index(name='most_active_timeday') # must reset index, because it's a Series object
    index_most_active_timeday = most_active_timeday.groupby(['user_id'])['most_active_timeday'].idxmax() # find index
    most_active_timeday_for_each_user = most_active_timeday.loc[index_most_active_timeday][['user_id', 'time_of_day']]
    most_active_timeday_for_each_user.rename(columns={'time_of_day': 'most_active_timeday'}, inplace=True) # rename the column

    # Merge with user_df
    user_df = user_df.merge(most_active_timeday_for_each_user[['user_id', 'most_active_timeday']], on='user_id', how='left')
    return(user_df)


def get_movies_liked(df,user_df):
    # Filter out rows where the release date is not available, creat df with user_id and datetime
    df_with_available_release_date = df[df['release_date'] != "NOT AVAILABLE"]
    df_with_available_release_date['release_date'] = pd.to_datetime(df_with_available_release_date['release_date'])
    df_with_available_release_date = df_with_available_release_date.iloc[:,[5,-1]]

    # Assign a label (Old or Recent) to movies 
    df_with_available_release_date['label'] = df_with_available_release_date['release_date'].apply(lambda x: 'Old' if x.year < 2010 else 'Recent')

    # Count occurrences of each label for each user and create a DataFrame, replace NaN with 0
    user_preference_counts_df = df_with_available_release_date.groupby('user_id')['label'].value_counts().unstack(fill_value=0)

    # Determine if the user is an Old lover or a Recent Lover based on the highest value
    user_preference_counts_df['movies_liked'] = user_preference_counts_df[['Old', 'Recent']].idxmax(axis=1)

    # Reset the index to make 'user_id' a regular column
    user_preference_counts_df.reset_index(inplace=True)

    # Drop the individual columns (Old and Recent)
    user_preference_counts_df.drop(columns=['Old', 'Recent'], inplace=True)

    # Merge with user_df
    user_df = user_df.merge(user_preference_counts_df, on='user_id', how='left')
    return(user_df)

def get_average_time_per_day(df,user_df):
    # Create new DataFrame with columns datetime, user_id and duration
    user_activity_df = pd.DataFrame()
    user_activity_df['datetime'] = pd.to_datetime(df['datetime'])
    user_activity_df['user_id'] = df['user_id']
    user_activity_df['duration'] = df['duration']

    # Group by user_id and date, and sum the duration for each day
    user_daily_duration_df = user_activity_df.groupby(['user_id', user_activity_df['datetime'].dt.date])['duration'].sum().reset_index() # with dt.date we take only the day without time

    # Group by user_id and calculate the average time spent per day
    average_time_per_day = user_daily_duration_df.groupby('user_id')['duration'].mean().round(2).reset_index(name='Average_time_per_day')

    # Merge with user_df
    user_df = user_df.merge(average_time_per_day, on='user_id', how='left')
    return(user_df)

def get_longest_viewing_time(df,user_df):
    # Group by and get longest time they have watched a movie
    longest_viewing_time = df.groupby('user_id')['duration'].idxmax()

    # Replace nan values with value 0
    longest_viewing_time.fillna(0, inplace=True)

    # Get df with user_id and longest viewing time (change name)
    viewing_time_df = df.loc[longest_viewing_time, ['user_id','duration']]
    viewing_time_df.rename(columns={'duration': 'longest_viewing_time'}, inplace=True)

    # Merge with user_df
    user_df = user_df.merge(viewing_time_df, on='user_id', how='left')
    # Drop duplicated rows based on the 'user_id' column, because of nan values
    user_df = user_df.drop_duplicates(subset='user_id', keep='first')

    return(user_df)

def get_movies_watched(df,user_df):
    # Group by 'user_id' and get the unique movies watched for each user
    movies_watched = df.groupby('user_id')['title'].unique()

    # Create a new column 'movies_watched' in user_df with the count of unique movies for each user
    user_df['movies_watched'] = user_df['user_id'].apply(lambda x: len(movies_watched.get(x, [])))
    return(user_df)

# Define function to get day
def getDay(row):
    day = row.strftime('%A')
    return day

def get_most_common_day(df,user_df):
    # Create temp dataframe so it's easier to calculate
    df_temp = pd.DataFrame()
    df_temp['datetime'] = pd.to_datetime(df['datetime'])
    df_temp['user_id'] = df['user_id']

    df_temp['day'] = df_temp['datetime'].apply(getDay)

    # Now count how many occurences for day for each user and get the highest one
    df_grouped = df_temp.groupby('user_id')['day'].value_counts()
    df_max_day = df_grouped.groupby('user_id').idxmax()
    df_max_day = df_max_day.apply(lambda x: x[1]).reset_index(name='most_common_day') # get day

    # Merge with user_df
    user_df = user_df.merge(df_max_day, on='user_id', how='left')
    return(user_df)


def get_num_session(df,user_df):
    # Group by 'user_id' and count sessions with duration > 0
    user_session_counts = df[df['duration'] > 0].groupby('user_id')['duration'].nunique().reset_index(name='num_sessions')

    # Merge with user_df to include users without sessions and set their count to 0
    user_df = user_df.merge(user_session_counts, on='user_id', how='left').fillna(0)
    return(user_df)

def get_most_watched_title(df,user_df):
    # Group by 'user_id' and 'title', sum the durations to get total watch time for each user-title combination
    user_most_watched_title = df.groupby(['user_id', 'title'])['duration'].sum().reset_index()

    # Find the index of the row with the highest total watch time for each user
    index_most_watched_title = user_most_watched_title.groupby('user_id')['duration'].idxmax()

    # Get the most watched title for each user
    most_watched_titles_for_each_user = user_most_watched_title.loc[index_most_watched_title]
    most_watched_titles_for_each_user.rename(columns={'title': 'most_watched_title'}, inplace=True)

    # merge to user_df, without duration column
    user_df = user_df.merge(most_watched_titles_for_each_user[['user_id', 'most_watched_title']], on='user_id', how='left')
    return(user_df)

def get_total_watch_time(df,user_df):
    # Get total watch time for each user
    total_watch_time = df.groupby('user_id')['duration'].sum().reset_index()

    # merge to user_df
    user_df = user_df.merge(total_watch_time, on='user_id', how='left')
    return(user_df)

def get_season_preference(df,user_df):
    # Create a dictionary that will help us map the season given the month number
    season_mapping = {1: 'Winter', 2: 'Winter', 3: 'Spring', 4: 'Spring', 5: 'Spring', 6: 'Summer', 7: 'Summer', 8: 'Summer', 9: 'Fall', 10: 'Fall', 11: 'Fall', 12: 'Winter'}

    # Create a temp df, with a month column
    df_season = pd.DataFrame()
    df_season['user_id'] = df['user_id']
    df_season['datetime'] = pd.to_datetime(df['datetime'])
    df_season['month'] = df_season['datetime'].dt.month
    df_season['season'] = df_season['month'].map(season_mapping)

    # Now group by user_id and get highest occurence of each user
    season_preference = df_season.groupby('user_id')['season'].value_counts()
    index_season_preference = season_preference.groupby('user_id').idxmax()
    season_preference = index_season_preference.apply(lambda x: x[1]).reset_index(name='season_preference') # get season

    # Merge with user_df
    user_df = user_df.merge(season_preference, on='user_id', how='left')
    return(user_df)

def get_average_release_date_year(df,user_df):
    # Filter out rows where the release date is not available, creat df with user_id and datetime
    df_with_available_release_date = df[df['release_date'] != "NOT AVAILABLE"]
    df_with_available_release_date['release_date'] = pd.to_datetime(df_with_available_release_date['release_date']).dt.year
    df_with_available_release_date = df_with_available_release_date.iloc[:,[5,-1]]

    # Calculate the average release date for each user
    average_release_date = df_with_available_release_date.groupby('user_id')['release_date'].mean().round().reset_index(name='average_release_date_year')

    # Merge with user_df
    user_df = user_df.merge(average_release_date, on='user_id', how='left')
    return(user_df)

def get_average_shows_per_month(df,user_df):
    # Convert 'datetime' column to datetime object
    temp_df = pd.DataFrame()
    temp_df['datetime'] = pd.to_datetime(df['datetime'])
    temp_df['user_id'] = df['user_id']
    temp_df['movie_id'] = df['movie_id']

    # Extract month and year
    temp_df['month'] = temp_df['datetime'].dt.month

    # Count the number of unique movies watched for each combination
    movies_per_month = temp_df.groupby(['user_id', 'month'])['movie_id'].size().reset_index(name='movies_watched_per_month')
    average_movies_per_month = movies_per_month.groupby('user_id')['movies_watched_per_month'].mean().reset_index(name='average_shows_per_month')

    # Merge with user_df
    user_df = user_df.merge(average_movies_per_month, on='user_id', how='left')
    return(user_df)

def get_percentage_watched_at_least_20_minutes(df,user_df):
    # Create a df where we have only shows with a watchtime of 20 minutes from the user
    watched_20_minutes = df[df['duration'] >= 1200]

    # Count the total number of shows watched for at least 20 minutes for each user, including rewatches
    watched_at_least_20_minutes_count = watched_20_minutes.groupby('user_id')['movie_id'].size().reset_index(name='watched_at_least_20_minutes_count')

    # Count the total number of shows watched from users
    number_shows_watched = df.groupby('user_id')['title'].size().reset_index(name='total_movies_watched')

    # Merge the two dataframes on 'user_id'
    merged_df = watched_at_least_20_minutes_count.merge(number_shows_watched, on='user_id', how='left')
    # Get percentage
    merged_df['percentage_watched_at_least_20_minutes'] = merged_df['watched_at_least_20_minutes_count'] / merged_df['total_movies_watched']

    # Merge with user_df and replace NaN with 0 
    # This means that they have not watched a single show for at least 20 minutes
    user_df = user_df.merge(merged_df[['user_id','percentage_watched_at_least_20_minutes']], on='user_id', how='left')
    user_df['percentage_watched_at_least_20_minutes'] = user_df['percentage_watched_at_least_20_minutes'].fillna(0) 
    return(user_df)




