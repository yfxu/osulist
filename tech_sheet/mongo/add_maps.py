import pymongo
import os

from osuapi import osuapi
from dotenv import load_dotenv, find_dotenv
from utils import map_url_parse

load_dotenv( find_dotenv() )
OSU_TOKEN = os.getenv( 'OSU_TOKEN' )
PASSWORD = os.getenv( 'MONGO_PASSWORD' )

maps_file_name = 'map_urls.txt'
db_name = 'osu_maps'
coll_name = 'feiri_tech_maps'

client = pymongo.MongoClient("mongodb+srv://Yifei:{}@cluster0.7n1ib.mongodb.net/{}?retryWrites=true&w=majority".format( PASSWORD, db_name ) )
collection = client[db_name][coll_name]

api = osuapi( OSU_TOKEN )

maps_file = open( maps_file_name, 'r' )
maps_lines = maps_file.readlines()

for line in maps_lines:
	beatmap_id = map_url_parse.get_beatmap_id( line )
	x = api.get_beatmap( beatmap_id )

	upsert_status = collection.replace_one( { 'beatmap_id': beatmap_id }, x, upsert = True )
	print( "updated {} [{}] ({})".format( x['title'], x['version'], x['creator'] ) )