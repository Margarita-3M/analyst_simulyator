-- Подсчитываем количество дней активации во втором продукте после активации в первом продукте

SELECT toString(t3.FirstProductDate) as FirstProductDate, ProductDateDiff, t3.FirstProduct, COUNT(DISTINCT t3.user_id) as user_num
FROM   
    -- Выбираем только тех пользоваталей, которые пользуются обоими продуктами
    -- Для каждого их них выбираем даты активации для каждого продуктами
    -- Затем ищем дату и продукт, который был первым
    (SELECT 
        t1.user_id, t1.FeedTime, t2.MessageTime,
        if (FeedTime <= MessageTime, 'Feed', 'Message') AS FirstProduct,
        if (FeedTime <= MessageTime, toDate(FeedTime), toDate(MessageTime)) AS FirstProductDate,
        if (FeedTime <= MessageTime, 'Message', 'Feed') AS SecondProduct,
        if (FeedTime <= MessageTime, toDate(MessageTime), toDate(FeedTime)) AS SecondProductDate,
        dateDiff('day', FirstProductDate, SecondProductDate) as ProductDateDiff
    FROM 
        (SELECT tFeed.user_id, min(tFeed.time) as FeedTime
        FROM simulator_20211220.feed_actions as tFeed
        GROUP BY tFeed.user_id) as t1
    INNER JOIN
        (SELECT tMessage.user_id, min(tMessage.time) as MessageTime
        FROM simulator_20211220.message_actions as tMessage
        GROUP BY tMessage.user_id) as t2
    ON 
        t1.user_id = t2.user_id) as t3
GROUP BY FirstProductDate, ProductDateDiff, FirstProduct
ORDER BY FirstProductDate DESC, ProductDateDiff DESC, FirstProduct DESC