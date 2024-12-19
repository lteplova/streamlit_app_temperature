# Приложение для анализа температурных данных и мониторинг текущей температуры через OpenWeatherMap API


Готовое приложение доступно по ссылке: [приложение](https://appapptemperature-mqrlpxlrud8lc86dclvz7z.streamlit.app/)

Данные сгенерированы случайным образом, содержат 4 колонки и 54750 строк.  
Колонки: город, дата, температура, сезон.  

<img width="396" alt="image" src="https://github.com/user-attachments/assets/553b0541-497b-4ded-bea4-b1ca5b0d6a0c" />

**Анализ исторических данных**:
   - Вычислить **скользящее среднее** температуры с окном в 30 дней для сглаживания краткосрочных колебаний.
   - Рассчитать среднюю температуру и стандартное отклонение для каждого сезона в каждом городе.
   - Выявить аномалии, где температура выходит за пределы $ \text{среднее} \pm 2\sigma $.
   - Попробуйте распараллелить проведение этого анализа. Сравните скорость выполнения анализа с распараллеливанием и без него.
  
  В файле `analysis.py` с помощью функции `main_analysis` расчитываются скользящие, максимум, минимум, среднее, профиль по температурам,  профили по скользящим, список аномальных точек, тренд.  
  Функция запускается в 2-х режимах с распараллеливанием расчетов по городами без.

С использованием multiprocessing Pool время применения функции более длительное:
0.24 без мультипроцессинга
1.68 с мультипроцессингом

![image](https://github.com/user-attachments/assets/22c62feb-c82d-4c92-8974-ee39c05f51c8)



2. **Мониторинг текущей температуры**:
   - Подключить OpenWeatherMap API для получения текущей температуры города. Для получения API Key (бесплатно) надо зарегистрироваться на сайте. Обратите внимание, что API Key может активироваться только через 2-3 часа, это нормально. Посему получите ключ заранее.
   - Получить текущую температуру для выбранного города через OpenWeatherMap API.
   - Определить, является ли текущая температура нормальной, исходя из исторических данных для текущего сезона.
   - Данные на самом деле не совсем реальные (сюрпрайз). Поэтому на момент эксперимента погода в Берлине, Каире и Дубае была в рамках нормы, а в Пекине и Москве аномальная. Протестируйте свое решение для разных городов.
   - Попробуйте для получения текущей температуры использовать синхронные и асинхронные методы. Что здесь лучше использовать?

3. **Создание приложения на Streamlit**:
   - Добавить интерфейс для загрузки файла с историческими данными.
   - Добавить интерфейс для выбора города (из выпадающего списка).
   - Добавить форму для ввода API-ключа OpenWeatherMap. Когда он не введен, данные для текущей погоды не показываются. Если ключ некорректный, выведите на экран ошибку (должно приходить `{"cod":401, "message": "Invalid API key. Please see https://openweathermap.org/faq#error401 for more info."}`).
   - Отобразить:
     - Описательную статистику по историческим данным для города, можно добавить визуализации.
     - Временной ряд температур с выделением аномалий (например, точками другого цвета).
     - Сезонные профили с указанием среднего и стандартного отклонения.
   - Вывести текущую температуру через API и указать, нормальна ли она для сезона.
