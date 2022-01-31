SELECT 
  toString(start_day) AS start_day,
  toString(day) AS day,
  count(user_id) AS users
FROM
  (SELECT user_id, min(time) AS start_day
  FROM (
      SELECT user_id, toDate(time) as time
      FROM simulator_20211220.message_actions
      WHERE source = 'ads'
          
      UNION ALL
          
      SELECT user_id, toDate(time) as time
      FROM simulator_20211220.feed_actions
      WHERE source = 'ads'
        )
  GROUP BY user_id
  ) AS t1
        
INNER JOIN
        
  (SELECT DISTINCT user_id, day
  FROM (
  SELECT DISTINCT user_id, toDate(time) AS day
  FROM simulator_20211220.message_actions
  WHERE source = 'ads'
          
  UNION ALL
          
  SELECT DISTINCT user_id, toDate(time) AS day
  FROM simulator_20211220.feed_actions 
  WHERE source = 'ads'
  )
          ) AS t2
        
USING user_id

WHERE toDate(start_day) >= today() - 27  AND toDate(start_day) <= today() - 19
GROUP BY start_day, day
ORDER BY start_day, day