# Напишите скрипт для сборки отчета по ленте новостей. Отчет должен состоять из двух частей:
# - текст с информацией о значениях ключевых метрик за предыдущий день
# - график со значениями метрик за предыдущие 7 дней
# 
# Отобразите в отчете следующие ключевые метрики: 
# - DAU 
# - Просмотры
# - Лайки
# - CTR

# импортируем библиотеки
import pandahouse
import pandas as pd
import numpy as np
import seaborn as sns
sns.set() # Setting seaborn as default style even if use only matplotlib
import matplotlib.pyplot as plt
import io
import telegram # importing the library to work with tg bot
import os

# инициализация бота
# значение переменной tg_token хранится в переменных GitLab CI/CD
bot_token = os.environ.get('tg_token')
bot = telegram.Bot(token=bot_token)

# соединение к БД
connection = {
    'host': 'https://clickhouse.lab.karpov.courses',
    'password': 'dpo_python_2020',
    'user': 'student',
    'database': 'simulator_20211220'
}

# DAU, views, likes, CTR для прошлой недели
q_all = '''
    SELECT
          toDate(time) as date
        , uniqExact(user_id) /1000 as DAU
        , countIf(user_id, action='view') /1000 as views
        , countIf(user_id, action='like') /1000 as likes
        , 100 * likes / views as CTR
    FROM simulator_20211220.feed_actions
    WHERE toDate(time) between  today() - 7 and today() - 1
    GROUP BY date
    ORDER BY date
'''
# считывакм данные и переводим в датафрейм
week_df = pandahouse.read_clickhouse(q_all, connection=connection)
week_df['date_short'] = week_df['date'].dt.strftime('%d-%m')

# значение метрик за вчерашний день
# DAU, views, likes and CTR

y_date = week_df['date'].max()
y_DAU = week_df.loc[week_df['date'] == y_date, 'DAU'].item()
y_views = week_df.loc[week_df['date'] == y_date, 'views'].item()
y_likes = week_df.loc[week_df['date'] == y_date, 'likes'].item()
y_CTR = week_df.loc[week_df['date'] == y_date,'CTR'].item()

# дата для заголовков
from_date = week_df['date'].min().strftime("%d-%m-%Y")
to_date = y_date.strftime("%d-%m-%Y")

# текст сообщения с данными за вчера
message = 'Отчет по Ленте новостей за {}: \n - DAU: {}k, \n - Просмотры: {}k, \n - Лайки: {}k, \n - CTR: {}%'.format(
    to_date, round(y_DAU, 1), round(y_views, 1), round(y_likes, 1), round(y_CTR, 2))
message = message + '\n<a href="https://superset.lab.karpov.courses/superset/dashboard/212/"> Основные метрики </a>'
message = message + ' и <a href="https://superset.lab.karpov.courses/superset/dashboard/220/"> Оперативные данные </a>'

# подзаголовок для графиков
f_suptitle = 'Отчет по Ленте новостей за период с {} по {}'.format(from_date, to_date)

# настройки для визуализации данных за 7 дней
sns.set_style("darkgrid", {"axes.facecolor": "lavender", 'axes.grid': False})
sns.set_context("talk")

f, axes = plt.subplots(2, 2, figsize=(18, 10))
sns.despine(fig=f, left=True) # убираем угол
f.suptitle(f_suptitle, fontweight="bold")

## DAU
sns.lineplot(ax=axes[0, 0], data=week_df, y='DAU', x='date_short', linewidth=3, marker='o')
axes[0, 0].set(ylabel='тыс.пользователей',
               xlabel='')
axes[0, 0].set_title('DAU', fontweight="bold")

## CTR
sns.lineplot(ax=axes[0, 1], data=week_df, y='CTR', x='date_short', linewidth=3, marker='o')
axes[0, 1].set(ylabel='%',
               xlabel='')
axes[0, 1].set_title('CTR', fontweight="bold")

## views
sns.lineplot(ax=axes[1, 0], data=week_df, y='views', x='date_short', linewidth=3, marker='o')
axes[1, 0].set(ylabel='тыс.действий',
               xlabel='')
axes[1, 0].set_title('Просмотры', fontweight="bold")

## likes
sns.lineplot(ax=axes[1, 1], data=week_df, y='likes', x='date_short', linewidth=3, marker='o')
axes[1, 1].set(ylabel='тыс.действий',
               xlabel='')
axes[1, 1].set_title('Лайки', fontweight="bold")

plt.subplots_adjust(hspace = 0.4);

# сохранение графиков
plot_object = io.BytesIO()
f.savefig(plot_object)
plot_object.seek(0) # return to the beginning
plot_object.name = 'Lenta_{}'.format(to_date)
plt.close()

# отправка отчетов
bot.sendMessage(chat_id=-674009613, text=message, parse_mode='HTML')
bot.sendPhoto(chat_id=-674009613, photo=plot_object)
