import streamlit as st
import pandas as pd
from analysis import main_analysis
import matplotlib.pyplot as plt
from monitoring import get_current_temp
from monitoring import main as main_curr
def main():

    # загрузка заголовка приложения
    st.title("Анализ температурных данных")
    st.write("Это интерактивное приложение для анализа температурных данных и мониторинг текущей температуры через OpenWeatherMap API")
    st.header("Загрузка данных")
    uploaded_file = st.file_uploader("Выберите CSV-файл", type=["csv"])

    # вывод начала датафрейма
    if uploaded_file is not None:
        data = pd.read_csv(uploaded_file)
        st.write("Превью - первые 5 строк:")
        st.dataframe(data.head(5))
    else:
        st.write("укажите CSV-файл")

    # выбор города через выпадающий список
    if uploaded_file is not None:
        cities = data['city'].unique()
        cities_ = [' '] + list(cities)
        selected_city = st.selectbox("Выберите город:", cities_, index=0)
    # форма для ввода API ключа
    def show_form():
        with st.form("form_for_api"):
            st.write("Укажите API-ключ OpenWeatherMap")
            key = st.text_input("API-ключ")
            submitted = st.form_submit_button("Отправить")
            if submitted:
                return key
        return None

    if uploaded_file is not None:
        api_key = show_form()
        if api_key is not None:
            st.success("Ключ успешно сохранен")

    if uploaded_file is not None:
        # вывод информации о текущей температуре с openweathermap и есть ли отклонение от нормы
        if api_key is not None:
            if main_curr(selected_city, api_key):
                city, cur_temp_c, m, s, norma = main_curr(selected_city, api_key)
                cur_temp = get_current_temp(selected_city, api_key)
                if cur_temp:
                    res = { "город" : selected_city,
                            "сезон" : "winter",
                            "температура" : cur_temp,
                            "norma" : norma,
                            "среднее" : m,
                            "отклонение" : s
                            }
                    # проверка на нормальность текущей температуры
                    st.json(res)
            else:
                err = {
                "code": 401,
                "message": "Invalid API key. Please see https://openweathermap.org/faq#error401 for more info."
                }
                st.json(err)
    # функция для отрисовки графика температуры со скользящим
    def plot_moving(city_year, city):
        # 'seaborn-v0_8-bright'
        with plt.style.context('fivethirtyeight'):
            fig, ax = plt.subplots(figsize=(15, 8))
            plt.title(f"Распределение температуры города {city}", fontsize=12)
            plt.plot( pd.to_datetime(city_year['timestamp']), city_year["temperature"], label='оригинальное значение')
            plt.plot(pd.to_datetime(city_year['timestamp']), city_year['moving_average'], label='скользящее mean')
            plt.plot(pd.to_datetime(city_year['timestamp']), city_year['moving_std'], label='скользящее std')
            plt.legend(fontsize=10)
        st.pyplot(fig)
    # функция для отрисовки  графика температуры с аномальными точками
    def plot_anomaly(city, city_year):
        with plt.style.context('fivethirtyeight'):
            fig, ax = plt.subplots(figsize=(15, 8 ))
            plt.title(f"Аномальные температуры для города {city}", fontsize=12)
            plt.plot(pd.to_datetime(city_year['timestamp']), new_df["temperature"], label='распределение температуры')
            # Фильтрация для аномалий
            hot = city_year[new_df["hot_anomaly"] == 1]
            cold = city_year[new_df["cold_anomaly"] == 1]
            # Точки аномалий
            plt.scatter(pd.to_datetime(hot["timestamp"]), hot["temperature"], color='green', s=70, alpha=0.5, zorder=5,
                        label='аномально высокая температура')
            plt.scatter(pd.to_datetime(cold["timestamp"]), cold["temperature"], color='red', s=70, alpha=0.5, zorder=5,
                        label='аномально низкая температура')
            y_min = city_year["temperature"].min() - 5
            y_max = city_year["temperature"].max() + 5
            plt.ylim(y_min, y_max)
            plt.legend()
            plt.ylabel('Температура', fontsize=12)
            plt.tight_layout()
        st.pyplot(fig)

    if uploaded_file is not None:
        #  чекбоксы для отображения статистик и графика
        if selected_city != ' ':
            st.header(f"Основные статистики для города {selected_city}")
            city, new_df, max_t, min_t, mean_t, profile_season, profile_season_with_moving_m, profile_season_with_moving_a, anomaly_list, trend = main_analysis(selected_city, data)
            new = new_df.drop("numeric_date", axis=1 )
            if st.checkbox(f"Профиль сезона - {selected_city}"):
                st.write(profile_season)
            if st.checkbox(f"Описательные статистики - {selected_city}"):
                st.write(new.describe())
            if st.checkbox(f"Данные с дополненными статистиками - {selected_city}"):
                st.write(new)
            if st.checkbox(f"Тренд - {selected_city}"):
                st.write(trend)
            if st.checkbox(f"Показать график распеределения температуры - {selected_city}"):
                st.subheader(f"Распределение температуры со скользящими {selected_city}")
                plot_moving(new_df, selected_city)
            if st.checkbox("Показать график с аномальными точками"):
                st.subheader(f"График с аномальными точками {selected_city}")
                plot_anomaly(selected_city, new_df)


if __name__ == "__main__":
    main()