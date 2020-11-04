import requests
import os
import json

API_BASE_URL = 'https://osu.ppy.sh/api'

class Osuapi():
	"""docstring for api"""
	def __init__( self, key ):
		self.key = key
		self.url = API_BASE_URL
		
	def get_beatmap( self, beatmap_id, mode='0' ):
		params = { 'k': self.key, 'b': beatmap_id }
		data = requests.get( self.url + '/get_beatmaps', params = params )
		return data.json()[0]

	def get_user( self, user_id ):
		params = { 'k': self.key, 'u': user_id, 'type': 'id' }
		data = requests.get( self.url + '/get_user', params = params )
		return data.json()[0]


class OsuapiV2():
	"""docstring for api"""
	def __init__( self, user ):
		self.user = dict( user )
		self.ver = 'v2'
		self.url = f'{API_BASE_URL}/{self.ver}'

	def get_me( self ):
		headers = { 'Authorization': 'Bearer ' + self.user['access_token'] }
		response = requests.get( self.url + '/me', headers = headers )
		return response.json()
