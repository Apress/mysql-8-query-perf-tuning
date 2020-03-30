from pymemcache.client.base import Client
import mysql.connector

connect_args = {
    "user": "root",
    "password": "password",
    "host": "localhost",
    "port": 3306,
}
db = mysql.connector.connect(**connect_args)
cursor = db.cursor()
memcache = Client(("localhost", 11211))

sql = "SELECT CountryCode, Name FROM world.city WHERE ID = %s"
city_id = 130
city = memcache.get(str(city_id))
if city is not None:
    country_code, name = city.decode("utf-8").split("|")
    print("memcached: country: {0} - city: {1}".format(country_code, name))
else:
    cursor.execute(sql, (city_id,))
    country_code, name = cursor.fetchone()
    memcache.set(str(city_id), "|".join([country_code, name]), expire=60)
    print("MySQL: country: {0} - city: {1}".format(country_code, name))

memcache.close()
cursor.close()
db.close()