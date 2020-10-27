import os
import json
import utils.playlist as playlist
import utils.playlist_finder as playlist_finder
import utils.osuapi as osuapi
import utils.osuauth as osuauth
import requests
import pymongo
from werkzeug.exceptions import HTTPException
from flask import Flask, url_for, session, request
from flask import render_template, redirect
from random import randrange
from dotenv import load_dotenv, find_dotenv


# import env variables
load_dotenv( find_dotenv() )
APP_SECRET_KEY = os.getenv( 'APP_SECRET_KEY' )

OSU_TOKEN = os.getenv( 'OSU_TOKEN' )
OSU_CLIENT_ID = os.getenv( 'OSU_CLIENT_ID' )
OSU_CLIENT_SECRET = os.getenv( 'OSU_CLIENT_SECRET' )
OAUTH_STATE = os.getenv( 'OAUTH_STATE' )

MONGO_USER = os.getenv( 'MONGO_USER_PUBLIC' )
MONGO_PASSWORD = os.getenv( 'MONGO_PASSWORD_PUBLIC' )
MONGO_CLUSTER = os.getenv( 'MONGO_CLUSTER' )


# constants
playlists_db_name = 'playlists'
playlist_details_db_name = 'playlist_details'
playlist_details_collection_name = 'details'
osu_base_url = 'https://osu.ppy.sh'


# app setup
app = Flask( __name__ )
app.secret_key = APP_SECRET_KEY


# connect to MongoDB
client = pymongo.MongoClient( f"mongodb+srv://{ MONGO_USER }:{ MONGO_PASSWORD }@{ MONGO_CLUSTER }.mongodb.net/?retryWrites=true&w=majority" )


@app.errorhandler( HTTPException )
def handle_exception( e ):
	"""Return JSON instead of HTML for HTTP errors."""
	# start with the correct headers and status code from the error
	response = e.get_response()
	# replace the body with JSON
	response.data = json.dumps( {
		"code": e.code,
		"name": e.name,
		"description": e.description,
	} )
	response.content_type = "application/json"
	return response


""" authorize osu! apiv2 using OAuth2 """
@app.route( '/login', methods = ['GET'] )
def login():
	auth = osuauth.Auth()
	return redirect( auth.request_auth() )
	

@app.route( '/callback' )
def callback():
	#user = oauth.osu.parse_id_token( token )
	#print( user )
	state = request.args.get( 'state' )

	if state == OAUTH_STATE:
		auth = osuauth.Auth()
		code = request.args.get( 'code' )
		user = auth.authorize( code )
		api = osuapi.OsuapiV2( user )

	return redirect('/')


""" logout user """
"""
@app.route( '/logout' )
def logout():
	session.pop('user', None)
	return redirect('/')
"""

""" home page """
@app.route( '/' )
def page_index():
	pls = playlist_finder.Playlist_Finder( client, playlist_details_db_name, playlist_details_collection_name )

	pls_rows = pls.get_rows()
	pls_cols = pls.get_columns()

	return render_template(
		"index_template.html",
		data = pls_rows,
		columns = pls_cols
	)


""" route user to beatmap page """
@app.route( '/b/<map_id>' )
def page_beatmap( map_id ):
	user = session.get('user')

	api = osuapi.Osuapi( OSU_TOKEN )
	b = api.get_beatmap( map_id )

	b_url = f"{ osu_base_url }/b/{ map_id }"
	b_img = f"{ osu_thumbnail_url }{ b['beatmapset_id'] }.jpg"
	b_title = f"{ b['title'] } [{ b['version'] }]"
	b_creator = b['creator']
	b_creator_id = b['']
	b_length = b['total_length']
	b_cs = b['diff_size']
	b_od = b['diff_overall']
	b_ar = b['diff_approach']
	b_hp = b['diff_drain']
	b_sr = b['difficultyrating']
	b_bpm = b['bpm']
	b_mode = b['mode']

	return render_template(
		"beatmap_template.html",
		b_url = b_url,
		b_title = b_title,
		b_creator = b_creator,
		b_creator_id = b_creator_id,
		b_length = b_length,
		b_cs = b_cs,
		b_od = b_od,
		b_ar = b_ar,
		b_hp = b_hp,
		b_sr = b_sr,
		b_bpm = b_bpm,
		b_mode = b_mode
	)


""" delete song from playlist """
@app.route( '/delete_map', methods = ['POST'] )
def delete_map():
	playlist_id = request.form.get( 'playlist_id' )
	user_id = request.form.get( 'user_id' )
	beatmap_id = request.form.get( 'beatmap_id' )

	pl = playlist.Playlist( client, playlists_db_name, playlist_id )
	pl.delete_map( user_id, beatmap_id )
	return redirect( '/p/' + playlist_id )


""" route user to playlist add maps page or submit map add form """
@app.route( '/p/<pl_id>/add', methods = ['GET', 'POST'] )
def add_map( pl_id ):
	# POST method handler
	if request.method == 'POST':
		beatmap_str = request.form.get( 'beatmap_str' )
		user_id = "3214844"
		pl = playlist.Playlist( client, playlists_db_name, pl_id )

		status_msg = pl.add_map( user_id, beatmap_str )

	# GET method handler
	elif request.method == 'GET':
		status_msg = ""
	
	pl_data = { 'id': pl_id }

	return render_template(
		"playlist_add_map_template.html",
		pl = pl_data,
		status_msg = status_msg
	)


""" route user to playlist edit page or submit edit form """
@app.route( '/p/<pl_id>/edit', methods = ['GET', 'POST'] )
def edit_playlist( pl_id ):
	# POST method handler
	if request.method == 'POST':
		title = request.form.get( 'title' )
		desc = request.form.get( 'desc' )

		pl = playlist.Playlist( client, playlists_db_name, pl_id )
		pl.edit_details( title, desc )

		return redirect( f'/p/{ pl_id }' )

	# GET method handler
	elif request.method == 'GET':
		pl = playlist.Playlist( client, playlists_db_name, pl_id )
		pl_details = pl.get_details()

		pl_data = {}
		pl_data['id'] = pl_id
		pl_data['title'] = pl_details['playlist_title']
		pl_data['desc'] = pl_details['playlist_desc']

		return render_template(
			"playlist_edit_template.html",
			pl = pl_data 
		)

	else:
		return render_template(
			"error_template.html"
		)


""" route user to playlist page """
@app.route( '/p/<pl_id>' )
def page_playlist( pl_id ):
	pl = playlist.Playlist( client, playlists_db_name, pl_id )
	pl_details = pl.get_details()
	pl_rows = pl.get_rows()
	pl_cols = pl.get_columns()

	pl_data = {}
	pl_data['id'] = pl_id
	pl_data['duration'] = pl.get_duration()
	pl_data['size'] = pl.get_size()

	pl_data['title'] = pl_details['playlist_title']
	pl_data['creator'] = pl_details['playlist_creator_name']
	pl_data['creator_id'] = pl_details['playlist_creator_id']
	pl_data['desc'] = pl_details['playlist_desc']

	return render_template( 
		"playlist_template.html",
		data = pl_rows,
		columns = pl_cols,
		pl = pl_data
	)

if __name__ == '__main__':
	app.run(debug=True, host='0.0.0.0')
