import pymongo
import os

from osuapi import osuapi
from dotenv import load_dotenv, find_dotenv
from utils import map_url_parse

load_dotenv( find_dotenv() )
OSU_TOKEN = os.getenv( 'OSU_TOKEN' )
PASSWORD = os.getenv( 'MONGO_PASSWORD_ADMIN' )
USERNAME = os.getenv( 'MONGO_USER_ADMIN' )
CLUSTER = os.getenv( 'MONGO_CLUSTER' )

maps_file_name = 'map_urls.txt'
db_name = 'playlists'
coll_name = '0'

client = pymongo.MongoClient("mongodb+srv://{}:{}@{}.mongodb.net/{}?retryWrites=true&w=majority".format( USERNAME, PASSWORD, CLUSTER, db_name ) )
collection = client[db_name][coll_name]

api = osuapi( OSU_TOKEN )

maps_file = open( maps_file_name, 'r' )
maps_lines = maps_file.readlines()

#print( collection.find_one( filter = { 'beatmap_id': '131564' } ) )

for line in maps_lines:
	beatmap_id = map_url_parse.get_beatmap_id( line )
	x = api.get_beatmap( beatmap_id )
	upsert_status = collection.replace_one( { 'beatmap_id': beatmap_id }, x, upsert=True )
	print( "updated {} [{}] ({})".format( x['title'], x['version'], x['creator'] ) )
