import pymongo
import os
import time
from dotenv import load_dotenv, find_dotenv
from .html_utils import html_a_blank_format, html_a_format
from .osuapi import Osuapi

# load environment variables
load_dotenv( find_dotenv() )
MONGO_USER = os.getenv( 'MONGO_USER_PUBLIC' )
MONGO_PASSWORD = os.getenv( 'MONGO_PASSWORD_PUBLIC' )
MONGO_CLUSTER = os.getenv( 'MONGO_CLUSTER' )
OSU_TOKEN = os.getenv( 'OSU_TOKEN' )

# common URLs
osu_beatmap_url = "https://osu.ppy.sh/b/"
osu_mirror_url = "https://beatconnect.io/b/" # needs to be followed by beatmapset_id
osu_direct_url = "osu://b/" # needs to be followed by beatmap_id

class Playlist_Finder():
	""" class defintion for a single playlist object
		- one playlist is saved as a single collection within the 'osu_maps' database in MongoDB
		- provides methods to fetch data from MongoDB and format it into usable data for the website
		- requires database > collection to be initialized
	""" 
	def __init__( self, db, collection ):
		self.db = db
		self.collection = collection
		self.mongo_client_str = "mongodb+srv://{}:{}@{}.mongodb.net/{}?retryWrites=true&w=majority".format( MONGO_USER, MONGO_PASSWORD, MONGO_CLUSTER, self.db )
		self.playlist_details = self.fetch_playlist_details()
	
	def client( self ):
		return pymongo.MongoClient( self.mongo_client_str )[self.db][self.collection]

	def fetch_playlist_details( self ):
		client = self.client()
		data = client.find()
		return list( data )

	# get columns for display in home page
	def get_columns( self ):
		return [{
			'field': 'id',
			'title': 'ID',
			'align': 'right',
			'sortable': True
		}, {
			'field': 'playlist',
			'title': 'Playlist',
		}, {
			'field': 'creator',
			'title': 'Creator',
		}, {
			'field': 'size',
			'title': 'Size',
			'align': 'right'
		}]

	# format the data that will appear on homepage rows
	def get_rows( self ):
		table_data = []
		for pl in self.get_playlist_details():
			table_data.insert( 0, {
				'playlist_id': pl['playlist_id'],
				'playlist_title': pl['playlist_title'],
				'playlist_creator_name': pl['playlist_creator_name'],
				'playlist_creator_id': pl['playlist_creator_id'],
				'playlist_size': pl['playlist_size']
			})
		return table_data

	def get_playlist_details( self ):
		return self.playlist_details