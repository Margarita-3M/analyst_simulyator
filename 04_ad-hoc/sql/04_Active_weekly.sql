SELECT this_week, previous_week, -uniq(user_id) as num_users, status FROM

(SELECT user_id, 
groupUniqArray(toMonday(toDate(time))) as weeks_visited, 
addWeeks(arrayJoin(weeks_visited), +1) this_week, 
if(has(weeks_visited, this_week) = 1, 'retained', 'gone') as status, 
addWeeks(this_week, -1) as previous_week
FROM simulator_20211220.feed_actions
GROUP BY user_id)

WHERE status = 'gone'
GROUP BY this_week, previous_week, status
HAVING this_week != addWeeks(toMonday(today()), +1)

UNION ALL

SELECT this_week, previous_week, toInt64(uniq(user_id)) as num_users, status FROM

(SELECT user_id, 
groupUniqArray(toMonday(toDate(time))) as weeks_visited, 
arrayJoin(weeks_visited) this_week, 
if(has(weeks_visited, addWeeks(this_week, -1)) = 1, 'retained', 'new') as status, 
addWeeks(this_week, -1) as previous_week
FROM simulator_20211220.feed_actions
GROUP BY user_id)

GROUP BY this_week, previous_week, status