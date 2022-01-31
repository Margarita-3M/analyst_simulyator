SELECT
    exp_group,
    user_id,
    CountIf(user_id, action='like') as likes,
    CountIf(user_id, action='view') as views,
    round(likes / views, 4) AS ctr
FROM
    {db}.feed_actions    
WHERE
    toDate(time) <= '2022-01-04'
    AND toDate(time) >= '2021-12-29'
    AND exp_group IN (1, 0)
GROUP BY
    exp_group,
    user_id    
ORDER BY    
    exp_group,
    user_id;