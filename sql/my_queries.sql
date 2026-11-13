-- Lab 5 Part F: write your queries for the assistant database here.
-- Q1 requests per intent
SELECT intent, COUNT(*) AS requests
FROM interaction
GROUP BY intent
ORDER BY requests DESC, intent;

-- Q2 average latency per intent
SELECT intent, ROUND(AVG(latency_ms), 1) AS avg_latency_ms
FROM interaction
GROUP BY intent
ORDER BY COUNT(*) DESC, intent;

-- Q3 topics with the most thumbs-down (JOIN feedback with interaction)
SELECT i.topic, COUNT(*) AS thumbs_down
FROM feedback AS f
JOIN interaction AS i ON i.request_id = f.request_id
WHERE f.rating = -1
GROUP BY i.topic
ORDER BY thumbs_down DESC, i.topic;

-- Q4 H2: requests per UTC hour of day, busiest first (see docs/lab5/README.md)
SELECT strftime('%H', created_at) AS hour, COUNT(*) AS requests
FROM interaction
GROUP BY hour
ORDER BY requests DESC, hour;
