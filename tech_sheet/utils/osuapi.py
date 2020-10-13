import requests
import os
import json

class Osuapi():
	"""docstring for api"""
	def __init__( self, key ):
		self.key = key
		self.url = 'https://osu.ppy.sh/api'
		
	def get_beatmap( self, beatmap_id ):
		params = { 'k': self.key, 'b': beatmap_id }
		data = requests.get( self.url + '/get_beatmaps', params = params )
		return data.json()[0]

	def get_user( self, user_id ):
		params = { 'k': self.key, 'u': user_id, 'type': 'id' }
		data = requests.get( self.url + '/get_user', params = params )
		return data.json()[0]