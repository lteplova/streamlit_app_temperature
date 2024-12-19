import asyncio
import aiohttp
import pandas as pd
import time
# функция для подсчета профиля по сезону, выдает словарь с профилем
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
# функция запроса текущей температуры через API с помощью aiohttp
async def get_current_temp_async(city, api_key):
    base_url = "http://api.openweathermap.org/data/2.5/weather"

    params = {
        "q": city,
        "appid": api_key,
        "units": "metric"
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(base_url, params=params) as response:
                response.raise_for_status()
                data = await response.json()
                temperature = data["main"]["temp"]
                return temperature
    except aiohttp.ClientError as e:
        print(f"Ошибка запроса к API: {e}")
        return None

async def main(city, temper):
    cur_temp_cities = {}
    pp = {}
    # запрос и сохранение текущей температуры
    if temper is not None:
        cur_temp_cities[city] = temper
    else:
        print("Не удалось получить температуру.")
    #     высчитывание профиля сезона для города
    pp[city] = profile(city, data)
    for k, v in pp.items():
        # высчитывание границ аномальности для текущего сезона
        low = round(v['winter'][0], 2) - round(v['winter'][1], 2)
        high = round(v['winter'][0], 2) + round(v['winter'][1], 2)
        if cur_temp_cities[k] < high and cur_temp_cities[k] > low:
            norma = "is normal"
        else:
            norma = "out of normal"
        return k, cur_temp_cities[k], round(v['winter'][0], 2), round(v['winter'][1], 2), norma

if __name__ == "__main__":
    start = time.time()
    for city in cities:
        temper = asyncio.run(get_current_temp_async(city, api_key))
        city, cur_temp_c, m, s, norma = asyncio.run(main(city, temper))
        print(city, "Текущая:", cur_temp_c, "Средняя:", m, "Отклонение:", s, norma)
    end = time.time()
    print(f"Время выполнения с асинхронностью {end - start:.2f} секунд")


# Вывод без асинхронности выполнение сбора инфомации с сайта openweathermap выполняется быстрее
# в данном случае нет большой необходимости использовать асинхронные соединения, так как HTTP запросов к сайту довольно мало
# а также запросы методом request выполняются довольно быстро