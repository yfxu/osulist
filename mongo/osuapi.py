import requests
import os
import json
from dotenv import load_dotenv, find_dotenv

# import credentials
load_dotenv( find_dotenv() )
OSU_TOKEN = os.getenv( 'OSU_TOKEN' )

class osuapi():
	"""docstring for api"""
	def __init__( self, key ):
		self.key = key
		self.url = 'https://osu.ppy.sh/api'
		
	def get_beatmap( self, beatmap_id ):
		params = { 'k': self.key, 'b': beatmap_id }
		data = requests.get( self.url + '/get_beatmaps', params = params )
		return data.json()[0]