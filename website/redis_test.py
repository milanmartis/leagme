import redis

try:
    r = redis.Redis(
        host='leagme-redis-wb2hf0.serverless.eun1.cache.amazonaws.com',
        port=6378
    )
    response = r.ping()
    print(f"Connected to Redis: {response}")
except Exception as e:
    print(f"Error: {e}")