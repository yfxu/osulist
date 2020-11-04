import requests
import json
import os
from dotenv import load_dotenv, find_dotenv

load_dotenv( find_dotenv() )
OSU_CLIENT_ID = os.getenv( 'OSU_CLIENT_ID' )
OSU_CLIENT_SECRET = os.getenv( 'OSU_CLIENT_SECRET' )
OAUTH_STATE = os.getenv( 'OAUTH_STATE' )


class Auth():
	""" class for osu authentication """
	def __init__( self ):
		self.client_id = OSU_CLIENT_ID
		self.client_secret = OSU_CLIENT_SECRET
		self.redirect_uri = 'http://localhost:5000/callback' #'http://localhost:5000/callback'
		self.response_type = 'code'
		self.scope = 'identify public'
		self.state = OAUTH_STATE
		self.grant_type = 'authorization_code'
		self.auth_url = 'https://osu.ppy.sh/oauth/authorize'
		self.token_url = 'https://osu.ppy.sh/oauth/token'
	
	def request_auth( self ):
		params = {
			'client_id': self.client_id,
			'redirect_uri': self.redirect_uri,
			'response_type': self.response_type,
			'scope': self.scope,
			'state': self.state
		}
		response = requests.get( self.auth_url, params = params )
		return response.url

	def authorize( self, oauth_code ):
		data = {
			'client_id': self.client_id,
			'client_secret': self.client_secret,
			'code': oauth_code,
			'grant_type': self.grant_type,
			'redirect_uri': self.redirect_uri
		}
		headers = { 'content_type': 'application/x-www-form-urlencoded' }
		response = requests.post( self.token_url, headers = headers, data = data )
		return response.json()