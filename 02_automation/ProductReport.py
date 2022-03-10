# Соберите единый отчет по работе всего приложения. 
# В отчете должна быть информация и по ленте новостей, и по сервису отправки сообщений. 

# Выведем:
# - активные пользователи приложения, только ленты, только сообщений
# - лайки, просмотры, сообщения
# - активация пользоваталей в разрезе продуктов

# импортируем нужные бßиблиотекßи
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
bot_token = os.environ.get('BOT_TOKEN')
bot = telegram.Bot(token=bot_token)

# соединение к БД
connection = {
    'host': 'https://clickhouse.lab.karpov.courses',
    'password': 'dpo_python_2020',
    'user': 'student',
    'database': 'simulator_20211220'
}

# запросы к БД и сохранение в dataframes
## Действия в Приложении в Ленте и Сообщениях

q = '''
    --- Действия в Приложении в Ленте и Сообщениях
    --- Просмотры за последние 7 дней
    SELECT
        toDate(tFeed.time) as time,
        COUNT (tFeed.user_id) / 1000 as action_count,
        'Просмотры' as action_name
    FROM {db}.feed_actions as tFeed
    WHERE 
        time between (today() - 7) AND (today() - 1)
        AND tFeed.action = 'view'
    GROUP BY time, action_name

    UNION ALL

    --- Лайки за последние 7 дней
    SELECT 
        toDate(tFeed.time) as time,
        COUNT (tFeed.user_id) / 1000 as action_count,
        'Лайки' as action_name
    FROM {db}.feed_actions as tFeed
    WHERE 
        time between (today() - 7) AND (today() - 1)
        AND tFeed.action = 'like'
    GROUP BY time, action_name

    UNION ALL
    
    --- Сообщения за последние 7 дней    
    SELECT 
        toDate(tMessage.time) as time,
        COUNT (tMessage.user_id) / 1000 as action_count,
        'Сообщения' as action_name
    FROM {db}.message_actions as tMessage
    WHERE 
        time between (today() - 7) AND (today() - 1)
    GROUP BY time, action_name
        
    '''
week_actions = pandahouse.read_clickhouse(q, connection=connection)

## Активные уникальные пользователи в день в разрезе продукта
q = '''
    --- Активные уникальные пользователи в день в разрезе продукта
    --- Пользователи сообщений за день
    SELECT time, COUNT (DISTINCT user_id) as DAU, 'Сообщения' as product
    FROM (
        SELECT 
            toDate(tMessage.time) as time,
            tMessage.user_id,
            COUNT (tMessage.user_id)
        FROM {db}.message_actions as tMessage
        WHERE time between (today() - 7) AND (today() - 1)
        GROUP BY time, user_id)
    GROUP BY time, product
        
    UNION ALL
    
    --- Пользователи Ленты за день
    SELECT time, COUNT (DISTINCT user_id) as DAU, 'Лента' as product
    FROM (
        SELECT 
            toDate(tFeed.time) as time,
            tFeed.user_id,
            COUNT (tFeed.user_id)
        FROM {db}.feed_actions as tFeed
        WHERE time between (today() - 7) AND (today() - 1)
        GROUP BY time, user_id)
    GROUP BY time, product
    
    UNION ALL
    
    --- Пользователи, которые за текущий день пользовались и Лентой, и Сообщениями   
    SELECT time, COUNT (DISTINCT user_id) as DAU, 'и Лента, и Сообщения' as product
    
    -- t1 - таблица с уникальными пользователями Сообщений
    FROM (
        SELECT time, user_id, 'tMessages' as table
        FROM (
            SELECT 
                toDate(tMessage.time) as time,
                tMessage.user_id,
                COUNT (tMessage.user_id)
            FROM {db}.message_actions as tMessage
            WHERE time between (today() - 7) AND (today() - 1)
            GROUP BY
                time, user_id)) as t1
                
    -- t2 - таблица с уникальными пользователями Ленты    
    INNER JOIN
        (SELECT time, user_id, 'tFeed' as table
        FROM (
            SELECT 
                toDate(tFeed.time) as time,
                tFeed.user_id,
                COUNT (tFeed.user_id)
            FROM {db}.feed_actions as tFeed
            WHERE time between (today() - 7) AND (today() - 1)
            GROUP BY time, user_id)) as t2
            
    -- t2 и t1 соединяем по составному ключу user_id + time     
    ON t1.time = t2.time AND t1.user_id = t2.user_id    
    GROUP BY time, product 
    
    '''

week_DAU = pandahouse.read_clickhouse(q, connection=connection)

## Подсчет уникальных пользователей в разрезе даты активации и продукта
q = '''
    --- Подсчет уникальных пользователей в разрезе даты активации и продукта
    
    ---- Лента
    SELECT activation_date, product, COUNT(DISTINCT user_id) as users_num
    FROM (
        -- активация пользователя в Ленте
        SELECT toDate(min(tFeed.time)) as activation_date, tFeed.user_id, 'Лента' as product
        FROM {db}.feed_actions as tFeed
        GROUP BY tFeed.user_id, product
        )
    GROUP BY activation_date, product
    HAVING activation_date between toDate(today() - 7) AND toDate(today() - 1)
    ORDER BY activation_date
    
    UNION ALL

    --- Сообщения
    SELECT activation_date, product, COUNT(DISTINCT user_id) as users_num
    FROM (
        -- активация пользователя в Сообщениях
        SELECT toDate(min(tMessage.time)) as activation_date, tMessage.user_id, 'Сообщения' as product
        FROM {db}.message_actions as tMessage
        GROUP BY tMessage.user_id, product
        )       
    GROUP BY activation_date, product
    HAVING activation_date between toDate(today() - 7) AND toDate(today() - 1)
    ORDER BY activation_date
    
    UNION ALL
    
    --- Приложение в целом (все пользователи)
    SELECT activation_date, product, COUNT(DISTINCT user_id) as users_num
    FROM (    
        -- активация пользователя в Приложении
        SELECT min(tApplication.activation_date) as activation_date, tApplication.user_id, 'Приложение' as product
        FROM (
            --- Таблица с датами активаций в Ленте и Сообщениях в разрезе пользователя

            --- Находим дату активации в Ленте
            SELECT toDate(min(tFeed.time)) as activation_date, tFeed.user_id
            FROM {db}.feed_actions as tFeed
            GROUP BY tFeed.user_id

            UNION ALL

            --- Находим дату активации в Сообщениях
            SELECT toDate(min(tMessage.time)) as activation_date, tMessage.user_id
            FROM {db}.message_actions as tMessage
            GROUP BY tMessage.user_id
            ) as tApplication
        GROUP BY tApplication.user_id, product
        )
    GROUP BY activation_date, product
    HAVING activation_date between toDate(today() - 7) AND toDate(today() - 1)
    ORDER BY activation_date
'''

week_activation = pandahouse.read_clickhouse(q, connection=connection)

# подготовка данных для визуализации
week_actions['time_short'] = week_actions['time'].dt.strftime('%d-%m')
week_DAU['time_short'] = week_DAU['time'].dt.strftime('%d-%m')
week_activation['time_short'] = week_activation['activation_date'].dt.strftime('%d-%m')

# дата для заголовков
y_date = week_actions['time'].max()
from_date = week_actions['time'].min().strftime("%d-%m-%Y")
to_date = y_date.strftime("%d-%m-%Y")

# подзаголовок для графиков
f_suptitle = 'Отчет по работе Приложения за период с {} по {}'.format(from_date, to_date)

# настройки для визуализации
sns.set_style("darkgrid", {"axes.facecolor": "lavender", 'axes.grid': False})
sns.set_context("talk")

f, axes = plt.subplots(3, 3, figsize=(30, 12))
sns.despine(fig=f, left=True) # убираем угол
f.suptitle(f_suptitle, fontweight="bold")

## Действия
dataviz_elements = [(0, 'Сообщения'), (1, 'Просмотры'), (2, 'Лайки')]
for el in dataviz_elements:
    el_pos = el[0]
    el_name = el[1]
    sns.lineplot(ax=axes[0, el_pos], data=week_actions[week_actions['action_name'] == el_name], y='action_count', x='time_short', linewidth=3, marker='o')
    axes[0, el_pos].set(ylabel='тыс.действий', xlabel='')
    if el_pos == 0:
        title = 'Actions \n{}'.format(el_name)
    else:
        title = '\n{}'.format(el_name)
    axes[0, el_pos].set_title(title, fontweight="bold")

## DAU
dataviz_elements = [(0, 'Сообщения'), (1, 'Лента'), (2, 'и Лента, и Сообщения')]
for el in dataviz_elements:
    el_pos = el[0]
    el_name = el[1]
    sns.lineplot(ax=axes[1, el_pos], data=week_DAU[week_DAU['product'] == el_name], y='DAU', x='time_short', linewidth=3, marker='o')
    axes[1, el_pos].set(ylabel='Уник.польз.', xlabel='')
    if el_pos == 0:
        title = 'DAU \n{}'.format(el_name)
    else:
        title = '\n{}'.format(el_name)
    axes[1, el_pos].set_title(title, fontweight="bold")

## Активация
dataviz_elements = [(0, 'Сообщения'), (1, 'Лента'), (2, 'Приложение')]
for el in dataviz_elements:
    el_pos = el[0]
    el_name = el[1]
    sns.lineplot(ax=axes[2, el_pos], data=week_activation[week_activation['product'] == el_name], y='users_num', x='time_short', linewidth=3, marker='o')
    axes[2, el_pos].set(ylabel='Уник.польз.', xlabel='')
    if el_pos == 0:
        title = 'Активация пользователей \n{}'.format(el_name)
    else:
        title = '\n{}'.format(el_name)
    axes[2, el_pos].set_title(title, fontweight="bold")

plt.subplots_adjust(hspace = 0.55);

# сохранение графиков
plot_object = io.BytesIO()
f.savefig(plot_object)
plot_object.seek(0) # return to the beginning
plot_object.name = 'Application_{}'.format(to_date)
plt.close()

# текст сообщения
message = 'Отчет по работе Приложения за период с {} по {}'.format(from_date, to_date)

# отправка отчетов
bot.sendMessage(chat_id=-674009613, text=message, parse_mode='HTML')
bot.sendPhoto(chat_id=-674009613, photo=plot_object)
