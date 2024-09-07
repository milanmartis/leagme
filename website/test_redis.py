import redis

# Nastavenie pripojenia k Redis serveru
redis_host = 'elasticacheleagme-wb2hf0.serverless.eun1.cache.amazonaws.com'
redis_port = 6379

try:
    # Vytvorenie pripojenia
    r = redis.StrictRedis(host=redis_host, port=redis_port, decode_responses=True)
    
    # Otestujte pripojenie pomocou ping
    response = r.ping()
    
    if response:
        print("Pripojenie k Redis serveru je úspešné!")
    else:
        print("Pripojenie zlyhalo.")
except Exception as e:
    print(f"Došlo k chybe pri pripojení: {e}")