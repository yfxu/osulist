import pymongo
import os
import time
from dotenv import load_dotenv, find_dotenv

load_dotenv( find_dotenv() )
MONGO_USER = os.getenv( 'MONGO_USER_PUBLIC' )
MONGO_PASSWORD = os.getenv( 'MONGO_PUBLIC_PASSWORD' )
MONGO_CLUSTER = os.getenv( 'MONGO_CLUSTER' )

osu_beatmap_url = "https://osu.ppy.sh/b/"

class Playlist():
	""" maps playlist class """ 
	def __init__( self, db, collection ):
		self.db = db
		self.collection = collection
		self.mongo_client_str = "mongodb+srv://{}:{}@{}.mongodb.net/{}?retryWrites=true&w=majority".format( MONGO_USER, MONGO_PASSWORD, MONGO_CLUSTER, self.db )
	
	def client( self ):
		return pymongo.MongoClient( self.mongo_client_str )[self.db][self.collection]

	# get map playlist data from mongodb
	def get_maps( self ):
		client = self.client()
		data = client.find()
		return data

	def get_columns( self ):
		return [{
			'field': 'beatmap_id',
			'title': 'id',
			'sortable': True
		}, {
			'field': 'title',
			'title': 'Beatmap'
		}, {
			'field': 'creator',
			'title': 'Creator',
			'sortable': True
		}, {
			'field': 'bpm',
			'title': 'BPM',
			'align': 'right',
			'sortable': True
		}, {
			'field': 'sr',
			'title': 'SR',
			'align': 'right',
			'sortable': True
		}, {
			'field': 'length',
			'title': 'Length',
			'align': 'right',
			'sortable': True
		}, {
			'field': 'cs',
			'title': 'CS',
			'align': 'right',
			'sortable': True
		}, {
			'field': 'ar',
			'title': 'AR',
			'align': 'right',
			'sortable': True
		}]

	# format mongodb map data into well-formatted dict for bootstrap-tables
	def get_rows( self ):
		data = self.get_maps()
		table_data = []

		for x in data:
			table_data.append({
				'beatmap_id': x['beatmap_id'],
				'title': '<a href="{}{}" target="_blank">{} - {} [{}]</a>'.format( osu_beatmap_url, x['beatmap_id'], x['artist'], x['title'], x['version'] ),
				'creator': x['creator'],
				'bpm': x['bpm'],
				'sr': round( float(x['difficultyrating']), 2),
				'length': time.strftime("%#M:%S", time.gmtime( int(x['total_length'] ))),
				'cs': x['diff_size'],
				'ar': x['diff_approach'],
			})
		return table_data

""" TESTING SHIT
test = Playlist( 'osu_maps', 'feiri_tech_maps' )

print( test.get_columns() )

for i in test.get_rows():
	print( i )
"""