import numpy as np
import random
from datetime import datetime
from sklearn.linear_model import LinearRegression
import multiprocessing
import time
import pandas as pd
from functools import partial

random.seed(42)
np.random.seed(42)

# Реальные средние температуры (примерные данные) для городов по сезонам
seasonal_temperatures = {
    "New York": {"winter": 0, "spring": 10, "summer": 25, "autumn": 15},
    "London": {"winter": 5, "spring": 11, "summer": 18, "autumn": 12},
    "Paris": {"winter": 4, "spring": 12, "summer": 20, "autumn": 13},
    "Tokyo": {"winter": 6, "spring": 15, "summer": 27, "autumn": 18},
    "Moscow": {"winter": -10, "spring": 5, "summer": 18, "autumn": 8},
    "Sydney": {"winter": 12, "spring": 18, "summer": 25, "autumn": 20},
    "Berlin": {"winter": 0, "spring": 10, "summer": 20, "autumn": 11},
    "Beijing": {"winter": -2, "spring": 13, "summer": 27, "autumn": 16},
    "Rio de Janeiro": {"winter": 20, "spring": 25, "summer": 30, "autumn": 25},
    "Dubai": {"winter": 20, "spring": 30, "summer": 40, "autumn": 30},
    "Los Angeles": {"winter": 15, "spring": 18, "summer": 25, "autumn": 20},
    "Singapore": {"winter": 27, "spring": 28, "summer": 28, "autumn": 27},
    "Mumbai": {"winter": 25, "spring": 30, "summer": 35, "autumn": 30},
    "Cairo": {"winter": 15, "spring": 25, "summer": 35, "autumn": 25},
    "Mexico City": {"winter": 12, "spring": 18, "summer": 20, "autumn": 15},
}

# Сопоставление месяцев с сезонами
month_to_season = {12: "winter", 1: "winter", 2: "winter",
                   3: "spring", 4: "spring", 5: "spring",
                   6: "summer", 7: "summer", 8: "summer",
                   9: "autumn", 10: "autumn", 11: "autumn"}

# Генерация данных о температуре
def generate_realistic_temperature_data(cities, num_years=10):
    dates = pd.date_range(start="2010-01-01", periods=365 * num_years, freq="D")
    data = []

    for city in cities:
        for date in dates:
            season = month_to_season[date.month]
            mean_temp = seasonal_temperatures[city][season]
            # Добавляем случайное отклонение
            temperature = np.random.normal(loc=mean_temp, scale=5)
            data.append({"city": city, "timestamp": date, "temperature": temperature})

    df = pd.DataFrame(data)
    df['season'] = df['timestamp'].dt.month.map(lambda x: month_to_season[x])
    return df

# Генерация данных
data = generate_realistic_temperature_data(list(seasonal_temperatures.keys()))
data.to_csv('temperature_data.csv', index=False)

def main_analysis(city, df):

    new_df = df.copy()
    new_df = new_df.loc[df['city'] == city] # оставляем данные по городу
    # вычисляем скользящее среднее и скользящее отклонение
    new_df['moving_average'] = new_df['temperature'].transform(lambda x: x.rolling(30).median()) # считаем скользящее среднее
    new_df['moving_std'] = new_df['temperature'].transform(lambda x: x.rolling(30).std()) # считаем скользящее std

    # Находим аномалии
    new_df['hot_anomaly'] = (new_df['temperature'] > (new_df['moving_average'] + 2 * new_df['moving_std']))
    new_df['cold_anomaly'] = (new_df['temperature'] < (new_df['moving_average'] - 2 * new_df['moving_std']))
    anomaly_list = pd.concat([new_df.loc[(new_df['cold_anomaly'] == True)] , new_df.loc[(new_df['hot_anomaly'] == True)]], axis = 0)

    # профиль сезона по оригинальным температурам
    profile_season = new_df.groupby(['season'])['temperature'].agg(['mean', 'std']).reset_index()
    # профиль сезона по скользящим
    profile_season_with_moving_m = new_df.groupby(['season'])['moving_average'].agg(['mean', 'std']).reset_index()
    profile_season_with_moving_a = new_df.groupby(['season'])['moving_std'].agg(['mean', 'std']).reset_index()
    #
    # # определение тренда
    new_df['numeric_date'] = new_df['timestamp'].apply(lambda x: (pd.to_datetime(x) - datetime(2010, 1, 1)).days)
    X = new_df['numeric_date'].values.reshape(-1, 1)
    y = new_df['temperature'].values
    model = LinearRegression()
    model.fit(X, y)
    slope = model.coef_[0]
    if slope > 0:
        trend = 'positive'
    else: trend = 'negative'

    # статистики
    max_t = df['temperature'].max()
    min_t = df['temperature'].min()
    mean_t = df['temperature'].mean()

    return city, new_df, max_t, min_t, mean_t, profile_season,  profile_season_with_moving_m, profile_season_with_moving_a, anomaly_list, trend

cities = data.city.unique()
df = data.copy()
# city, new_df, max_t, min_t, mean_t, profile_season, profile_season_with_moving_m, profile_season_with_moving_a, anomaly_list, trend = main_analysis('Berlin', df)
def process_city(city, df):
    return main_analysis(city, df)

if __name__ == '__main__':

    start = time.time()
    for city in cities:
        city, new_df, max_t, min_t, mean_t, profile_season, profile_season_with_moving_m, profile_season_with_moving_a, anomaly_list, trend = main_analysis(city, df)
        print(city, trend)
    end = time.time()
    print(f"Время выполнения для всех городов: {end - start:.2f} секунд")

    partial_process = partial(process_city, df=df)
    num_processes = multiprocessing.cpu_count()
    start = time.time()
    with multiprocessing.Pool(processes=num_processes) as pool:
        results = pool.map(partial_process, cities)
    end = time.time()
    print(f"Время выполнения для всех городов с мультипроцессингом {end - start:.2f} секунд")


# Выводы: С использованием multiprocessing Pool время применения функции более длительное
# 0.24 без мультипроцессинга
# 1.95 с мультипроцессингом
