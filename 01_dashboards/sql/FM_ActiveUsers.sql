-- активная аудитория по группам пользования приложения:
-- т.е. пользователи, которые пользуются и лентой новостей, и сервисом сообщений
-- или пользователи, которые пользуются чем-то одним
-- аггрегация по дате без времени

-- пользователи, которые пользуются и лентой новостей, и сервисом сообщений
SELECT j1.gender, j1.source, j1.os, j1.country, j1.time, 'Feed and Messages' as status, COUNT (DISTINCT j1.user_id) as users_num
FROM  (
  SELECT tMessage.gender, tMessage.source, tMessage.os, tMessage.country, toDate(tMessage.time) as time, tMessage.user_id
  FROM simulator_20211220.message_actions as tMessage
  INNER JOIN simulator_20211220.feed_actions as tFeed
  ON tMessage.user_id = tFeed.user_id
  ) as j1

GROUP BY j1.gender, j1.source, j1.os, j1.country, j1.time, status
ORDER BY j1.time DESC

UNION ALL

-- пользователи, которые пользуются только сервисом сообщений
SELECT j2.gender, j2.source, j2.os, j2.country, j2.time, 'Messages only' as status, COUNT (DISTINCT j2.user_id) as users_num
FROM  (
  SELECT tMessage.gender, tMessage.source, tMessage.os, tMessage.country, toDate(tMessage.time) as time, tMessage.user_id
  FROM simulator_20211220.message_actions as tMessage
  LEFT JOIN simulator_20211220.feed_actions as tFeed
  ON tMessage.user_id = tFeed.user_id
  ) as j2

GROUP BY j2.gender, j2.source, j2.os, j2.country, j2.time, status
ORDER BY j2.time DESC

UNION ALL

-- пользователи, которые пользуются только лентой
SELECT j3.gender, j3.source, j3.os, j3.country, j3.time, 'Feed only' as status, COUNT (DISTINCT j3.user_id) as users_num
FROM  (
  SELECT tFeed.gender, tFeed.source, tFeed.os, tFeed.country, toDate(tFeed.time) as time, tFeed.user_id
  FROM simulator_20211220.feed_actions as tFeed
  LEFT JOIN simulator_20211220.message_actions as tMessage
  ON tMessage.user_id = tFeed.user_id
  ) as j3

GROUP BY j3.gender, j3.source, j3.os, j3.country, j3.time, status
ORDER BY j3.time DESC