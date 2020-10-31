import pymongo
import os
import time
from dotenv import load_dotenv, find_dotenv
from .html_utils import html_a_blank_format, html_a_format
from .osuapi import Osuapi

# load environment variables
load_dotenv( find_dotenv() )
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
	def __init__( self, cli, db, collection ):
		self.client_con = cli
		self.db = db
		self.collection = collection
		self.playlist_details = self.fetch_playlist_details()
	
	def client( self ):
		return self.client_con[self.db][self.collection]

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

	# insert new playlist
	def new_playlist( self, creator_id ):
		client = self.client()
		api = Osuapi( OSU_TOKEN )

		playlist_id = str( int( max( [ x['playlist_id'] for x in self.get_playlist_details() ] ) ) + 1 )
		
		try:
			client.insert_one( {
				'playlist_id': playlist_id,
				'playlist_title': "untitled_playlist",
				'playlist_desc': "",
				'playlist_creator_id': creator_id,
				'playlist_creator_name': api.get_user( creator_id )['username'],
				'playlist_size': 0
			} )
		except Exception as e:
			print( "ERROR:", e )

		return playlist_id


	def get_playlist_details( self ):
		return self.playlist_details