SELECT tUniqViews.gender, tUniqViews.os, tUniqViews.country, tUniqViews.time, tUniqViews.uniq_views_date, tLikes.likes

FROM
    (SELECT gender, os, country, time, SUM(uniq_views_post) as uniq_views_date
    FROM (
        SELECT gender, os, country, post_id, toDate(time) as time, COUNT(DISTINCT user_id) as uniq_views_post
        FROM simulator_20211220.feed_actions
        WHERE action='view'
        GROUP BY gender, os, country, post_id, time
        )
    GROUP BY gender, os, country, time) as tUniqViews
INNER JOIN
    (SELECT gender, os, country, toDate(time) as time, COUNT(user_id) as likes
    FROM simulator_20211220.feed_actions
    WHERE action='like'
    GROUP BY gender, os, country, time) as tLikes
ON tUniqViews.time = tLikes.time
AND tUniqViews.gender = tLikes.gender
AND tUniqViews.os = tLikes.os
AND tUniqViews.country = tLikes.country