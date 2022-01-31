SELECT 
    exp_group,
    user_id,
    CountIf(user_id, action='like') as likes,
    CountIf(user_id, action='view') as views,
    round(likes / views, 4) AS ctr
FROM 
    {db}.feed_actions
WHERE
    toDate(time) >= '2021-12-08' 
    AND toDate(time) <= '2021-12-14'
    AND exp_group IN (2, 3)
GROUP BY
    exp_group,
    user_id;