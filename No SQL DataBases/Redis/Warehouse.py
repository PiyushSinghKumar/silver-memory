import redis

redis = redis.Redis(
    host='localhost',
    port='6379')

redis.geoadd("Warehouse", (9.1776059, 49.1376432, 'Freiburg im Breisgau'))
redis.geoadd("Warehouse", (9.2415192, 48.8096645, 'Karlsruhe'))
redis.geoadd("Warehouse", (9.1776059, 49.1376432, 'Stuttgart'))
redis.geoadd("Warehouse", (8.560081, 49.4637092, 'Mannheim'))
redis.geoadd("Warehouse", (9.1584836, 48.7226206, 'Reutlingen'))
redis.geoadd("Warehouse", (9.2004305, 48.5373555, 'Stuttgart Stuttgart-Mitte'))
redis.geoadd("Warehouse", (9.1776059, 49.1376432, 'Heilbronn'))
