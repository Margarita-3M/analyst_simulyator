SELECT 
    toString(start_day) AS start_day,
    toString(day) AS day,
    count(user_id) AS users
FROM
  (SELECT *
   FROM
        (SELECT user_id, min(toDate(time)) AS start_day
        FROM simulator_20211220.feed_actions
        WHERE source = 'organic'
        GROUP BY user_id
        ) AS t1
        
        INNER JOIN
        
        (SELECT DISTINCT user_id, toDate(time) AS day
        FROM simulator_20211220.feed_actions
        WHERE source = 'organic'
        ) AS t2
        
        USING user_id
        
        WHERE start_day >= today() - 20 AND start_day < today())
        
GROUP BY start_day, day