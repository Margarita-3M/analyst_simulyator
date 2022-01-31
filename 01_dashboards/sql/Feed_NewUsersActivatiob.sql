-- Находим количество новых пользователей в ленте по дате
SELECT 
	os, 
	gender, 
	country, 
	activation_date as time, 
	COUNT (DISTINCT user_id) as new_users_num

FROM  (
  -- Находим первую активность пользователей по дате
  SELECT os, user_id, gender, country, min(toDate(time)) as activation_date
  FROM simulator_20211220.feed_actions
  GROUP BY user_id, gender, country, os
  ORDER BY activation_date DESC
  )

GROUP BY activation_date, gender, country, os
ORDER BY activation_date DESC