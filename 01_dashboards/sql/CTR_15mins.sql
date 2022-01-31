SELECT 
    tUniqViews.gender, tUniqViews.os, tUniqViews.country, tUniqViews.ts, tUniqViews.date, tUniqViews.hm, tLikes.likes as likes, tUniqViews.uniq_views_date as uniq_views
FROM
    (SELECT gender, os, country, ts, toDate(ts) as date, formatDateTime(ts, '%R') as hm, SUM(uniq_views_post) as uniq_views_date
    FROM (
        SELECT gender, os, country, post_id, toStartOfFifteenMinutes(time) as ts, COUNT(DISTINCT user_id) as uniq_views_post
        FROM simulator_20211220.feed_actions
        WHERE action='view'
        GROUP BY gender, os, country, post_id, ts
        )
    GROUP BY gender, os, country, ts, date, hm) as tUniqViews
INNER JOIN
    (SELECT gender, os, country,
        toStartOfFifteenMinutes(time) as ts, 
        toDate(ts) as date,
        formatDateTime(ts, '%R') as hm, 
        COUNT (user_id) as likes
    FROM simulator_20211220.feed_actions
    WHERE action='like'
    GROUP BY gender, os, country, ts, date, hm
    
    ) as tLikes
ON tUniqViews.ts = tLikes.ts
AND tUniqViews.gender = tLikes.gender
AND tUniqViews.os = tLikes.os
AND tUniqViews.country = tLikes.country
ORDER BY ts