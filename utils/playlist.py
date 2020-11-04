import pymongo
import os
import time
from dotenv import load_dotenv, find_dotenv
from .html_utils import html_a_blank_format, html_a_format, html_delete_format
from .time_utils import time_format_num, time_format_str
from .osuapi import Osuapi


# load environment variables
load_dotenv( find_dotenv() )
OSU_TOKEN = os.getenv( 'OSU_TOKEN' )

# common URLs
osu_beatmap_url = "https://osu.ppy.sh/b/"
osu_users_url = "https://osu.ppy.sh/u/"
osu_mirror_url = "https://beatconnect.io/b/" # needs to be followed by beatmapset_id
osu_direct_url = "osu://b/" # needs to be followed by beatmap_id
osu_preview_url = "https://b.ppy.sh/preview/"


class Playlist():
	""" class defintion for a single playlist object
		- one playlist is saved as a single collection within the 'osu_maps' database in MongoDB
		- provides methods to fetch data from MongoDB and format it into usable data for the website
		- requires database > collection to be initialized
	""" 
	def __init__( self, cli, db, collection, is_owner=False ):
		self.client_con = cli
		self.db = db
		self.collection = collection
		self.map_data = self.fetch_maps()
		self.playlist_details = self.fetch_details()
		self.is_owner = is_owner
		#print( "Playlist details:", self.playlist_details )

	def client( self ):
		return self.client_con[self.db][self.collection]

	def details_client( self ):
		return self.client_con['playlist_details']['details']

	# get map playlist data from mongodb
	def fetch_maps( self ):
		client = self.client()
		data = client.find( { 'beatmap_id': { '$exists': True } } )
		return list( data )

	# get map playlist data from mongodb
	def fetch_details( self ):
		client = self.details_client()
		data = client.find( { 'playlist_id': self.collection } )
		return list( data )

	# edit playlist details
	def edit_details( self, title, desc ):
		client = self.details_client()
		client.update_one( { 'playlist_id': self.collection }, { '$set': { 'playlist_title': str( title ) } } )
		client.update_one( { 'playlist_id': self.collection }, { '$set': { 'playlist_desc': str( desc ) } } )

	# add map to playlist
	# return:
	#	 0 > successfully added beatmap
	#	-1 > failed to add beatmap ( presumably due to bad input string )
	def add_map( self, beatmap_str ):
		modes = {
			'osu': '0',
			'taiko': '1',
			'fruits': '2',
			'mania': '3'
		}

		# attempt to parse beatmap_id from url
		try:
			beatmap_id = beatmap_str.split('/')[5].strip()
			mode = modes[beatmap_str.split('/')[4].split('#')[1].strip()]
		except:
			beatmap_id = beatmap_str
			mode = modes['osu']

		api = Osuapi( OSU_TOKEN )
		client = self.client()

		# try to add the beatmap given the best interpretation of the beatmap_id
		try:
			x = api.get_beatmap( beatmap_id, mode )
			response = client.replace_one( { 'beatmap_id': beatmap_id }, x, upsert=True )
			
			if response.upserted_id is not None:
				client = self.details_client()
				client.update_one( { 'playlist_id': self.collection }, { '$set': { 'playlist_size': self.get_size() + 1 } } )
				self.playlist_details = self.fetch_details()
				return f"successfully added { x['artist'] } - { x['title'] } [{ x['version'] }] ({ x['creator'] })"
			else:
				return f"{ x['artist'] } - { x['title'] } [{ x['version'] }] ({ x['creator'] }) already exists in the playlist"
		except Exception as e:
			print(e)
			return "could not find the specified beatmap"
		

	# delete map from playlist
	def delete_map( self, user_id, beatmap_id ):
		# remove map
		client = self.client()
		client.delete_one( { 'beatmap_id': beatmap_id } )

		# update playlist details
		client = self.details_client()
		client.update_one( { 'playlist_id': self.collection }, { '$set': { 'playlist_size': self.get_size() - 1 } } )

	# get columns for display in playlist pages
	def get_columns( self ):
		return [{
			'data': 'position',
			'title': '#'
		}, {
			'data': 'beatmap_id',
			'title': 'beatmap_id',
			'visible': False
		}, {
			'data': 'mode',
			'title': 'Mode'
		}, {
			'data': 'title',
			'title': 'Beatmap'
		}, {
			'data': 'creator',
			'title': 'Creator'
		}, {
			'data': 'bpm',
			'title': 'BPM'
		}, {
			'data': 'sr',
			'title': 'SR',
			'searchable': False
		}, {
			'data': 'length',
			'title': 'Length',
			'searchable': False
		}, {
			'data': 'tags',
			'title': 'Tags',
			'visible': False
		}, {
			'data': 'mirror',
			'title': '',
			'sortable': False,
			'searchable': False
		}, {
			'data': 'direct',
			'title': '',
			'sortable': False,
			'searchable': False
		}, {
			'data': 'delete',
			'title': '',
			'sortable': False,
			'searchable': False,
			'visible': self.is_owner
		}]

	# format mongodb map data into well-formatted dict for bootstrap-tables
	def get_rows( self ):
		modes = {
			'0': "std",
			'1': "taiko",
			'2': "catch",
			'3': "mania"
		}

		table_data = []
		position = 1
		playlist_creator_id = self.playlist_details[0]['playlist_creator_id']

		for x in self.get_raw_map_data():
			table_data.append({
				'position': position,
				'beatmap_id': x['beatmap_id'],
				'mode': modes[ x['mode'] ],
				'title': html_a_format( osu_beatmap_url + x['beatmap_id'] , f"{x['artist']} - {x['title']} [{x['version']}]" ),
				'creator': html_a_format( osu_users_url + x['creator_id'], x['creator'] ),
				'bpm': round( float( x['bpm'] ) ),
				'sr': f"{round( float(x['difficultyrating']), 2)}&nbsp;&#9733;",
				'length': f"{time_format_num( x['total_length'] )} ({time_format_num( x['hit_length'] )})",
				'tags': x['tags'],
				'mirror': html_a_format( osu_mirror_url + x['beatmapset_id'] , "mirror" ),
				'direct': html_a_format( osu_direct_url + x['beatmap_id'] , "direct" ),
				'delete': html_delete_format( '/delete_map', self.collection, playlist_creator_id, x['beatmap_id'], "delete" )
			})
			position += 1
		return table_data

	# get playlist details such as playlist title, description, creator, etc
	def get_details( self ):
		return self.playlist_details[0]

	# return total duration of all beatmaps in a playlist
	def get_duration( self ):
		pl_total_length = sum( [ int( x['total_length'] ) for x in self.get_raw_map_data() ] )
		pl_hit_length = sum( [ int( x['hit_length'] ) for x in self.get_raw_map_data() ] )
		return f"{time_format_str( pl_total_length )} ({time_format_str( pl_hit_length )})"

	# return number of maps in playlist
	def get_size( self ):
		return len( self.get_raw_map_data() )

	# drop a playlist from the database
	def delete( self ):
		client = self.client()
		client.drop()

		client = self.details_client()
		client.delete_one( { 'playlist_id': self.collection } )

	# return raw data from mongodb collection
	def get_raw_map_data( self ):
		return self.map_data