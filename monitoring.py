import requests
import pandas as pd
import time

def profile(city, df):
    new_df = df.copy()
    new_df = new_df.loc[df['city'] == city]
    profile_season = new_df.groupby(['season'])['temperature'].agg(['mean', 'std']).reset_index()
    season_dict = {}
    for _, row in profile_season.iterrows():
        season_dict[row['season']] = [row['mean'], row['std']]
    return season_dict


data = pd.read_csv("temperature_data.csv")
cities = data["city"].unique()
api_key = '00eea6919572f8bb24bb8ae8cd05e33c'
def get_current_temp(city, api_key):
    base_url = "http://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": city,
        "appid": api_key,
        "units": "metric"
    }
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        data = response.json()
        temperature = data["main"]["temp"]
        return temperature
    except requests.exceptions.RequestException as e:
        print(f"Ошибка запроса к API: {e}")
        return None

def main(city):
    API_KEY = api_key
    cur_temp_cities = {}
    pp = {}
    temperature = get_current_temp(city, API_KEY)
    if temperature is not None:
        cur_temp_cities[city] = temperature
    else:
        print("Не удалось получить температуру.")
    pp[city] = profile(city, data)
    for k, v in pp.items():
        low = round(v['winter'][0], 2) - round(v['winter'][1], 2)
        high = round(v['winter'][0], 2) + round(v['winter'][1], 2)
        if cur_temp_cities[k] < high and cur_temp_cities[k] > low:
            norma = "is normal"
        else:
            norma = "out of normal"
        return  k, cur_temp_cities[k], round(v['winter'][0], 2),  round(v['winter'][1], 2), norma



if __name__ == "__main__":
    start = time.time()
    for city in cities:
        city, cur_temp_c, m, s, norma = main(city)
        print(city, "Текущая:", cur_temp_c, "Средняя:", m, "Отклонение:", s, norma)
    end = time.time()
    print(f"Время выполнения без асинхронности {end - start:.2f} секунд")


# Вывод без асинхронности выполнение сбора инфомации с сайта openweathermap выполняется быстрее
# в данном случае нет большой необходимости использовать асинхронные соединения, так как HTTP запросов к сайту довольно мало
# а также запросы методом request выполняются довольно быстро


