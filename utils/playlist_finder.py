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

	def global_counters_client( self ):
		return self.client_con[self.db]['global_counters']

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
				'playlist_size': pl['playlist_size'],
				'playlist_timestamp': pl['_id'].generation_time.date()
			})
		return table_data

	def get_user_playlists( self, user_id ):
		table_data = []
		for pl in self.get_playlist_details():
			if pl['playlist_creator_id'] == user_id:
				table_data.insert( 0, {
					'playlist_id': pl['playlist_id'],
					'playlist_title': pl['playlist_title'],
					'playlist_creator_name': pl['playlist_creator_name'],
					'playlist_creator_id': pl['playlist_creator_id'],
					'playlist_size': pl['playlist_size'],
					'playlist_timestamp': pl['_id'].generation_time.date()
				})
		return table_data

	def get_non_empty_playlists( self ):
		table_data = []
		for pl in self.get_playlist_details():
			if pl['playlist_size'] != 0:
				table_data.insert( 0, {
					'playlist_id': pl['playlist_id'],
					'playlist_title': pl['playlist_title'],
					'playlist_creator_name': pl['playlist_creator_name'],
					'playlist_creator_id': pl['playlist_creator_id'],
					'playlist_size': pl['playlist_size'],
					'playlist_timestamp': pl['_id'].generation_time.date()
				})
		return table_data

	def get_search_playlists( self, search_string ):

		def match_kw( str1 ):
			str1 = str1.lower().split()
			str2 = search_string.replace( "%20", " " ).lower().split()

			for word in str1:
				if word in str2:
					return True

			return False

		table_data = []
		for pl in self.get_playlist_details():
			if match_kw( pl['playlist_title'] ) or match_kw( pl['playlist_creator_name'] ) or match_kw( pl['playlist_desc'] ):
				table_data.insert( 0, {
					'playlist_id': pl['playlist_id'],
					'playlist_title': pl['playlist_title'],
					'playlist_creator_name': pl['playlist_creator_name'],
					'playlist_creator_id': pl['playlist_creator_id'],
					'playlist_size': pl['playlist_size'],
					'playlist_timestamp': pl['_id'].generation_time.date()
				})
		return table_data


	# insert new playlist
	def new_playlist( self, creator_id ):
		api = Osuapi( OSU_TOKEN )
		playlist_id = ""

		with self.client_con.start_session() as sess:
			with sess.start_transaction():
				client = self.client()
				client2 = self.global_counters_client()

				client2.update_one( {}, { '$inc': { 'global_id': 1 } }, session = sess )
				playlist_id = str( client2.find_one( session = sess )['global_id'] )
				client.insert_one( {
					'playlist_id': playlist_id,
					'playlist_title': "untitled_playlist",
					'playlist_desc': "",
					'playlist_creator_id': str( creator_id ),
					'playlist_creator_name': api.get_user( creator_id )['username'],
					'playlist_size': 0
				}, session = sess )
		
		return playlist_id


	def get_playlist_details( self ):
		return self.playlist_details