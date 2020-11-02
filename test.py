import redis

r = redis.StrictRedis(host='10.176.48.180', port=27490, db=0, password='letMEin26379+1111')

r.set("name", "runoob")
print(r['name'])