import os
import json
import utils.playlist as playlist
import utils.playlist_finder as playlist_finder
import utils.osuapi as osuapi
import utils.osuauth as osuauth
import requests
import pymongo
from werkzeug.exceptions import HTTPException
from flask import Flask, url_for, session, request, abort
from flask import render_template, redirect
from functools import wraps
from random import randrange
from dotenv import load_dotenv, find_dotenv


# import env variables
load_dotenv( find_dotenv() )
APP_SECRET_KEY = os.getenv( 'APP_SECRET_KEY' )

OSU_TOKEN = os.getenv( 'OSU_TOKEN' )
OSU_CLIENT_ID = os.getenv( 'OSU_CLIENT_ID' )
OSU_CLIENT_SECRET = os.getenv( 'OSU_CLIENT_SECRET' )
OAUTH_STATE = os.getenv( 'OAUTH_STATE' )

mongo_uri = os.getenv("MONGO_URI")

# constants
playlists_db_name = 'playlists'
playlist_details_db_name = 'playlist_details'
playlist_details_collection_name = 'details'
osu_base_url = 'https://osu.ppy.sh'


# app setup
app = Flask( __name__ )
app.secret_key = APP_SECRET_KEY


# connect to MongoDB
client = pymongo.MongoClient(mongo_uri)

# login_required decorator
def login_required(f):
	@wraps(f)
	def decorated_function(*args, **kwargs):
		try:
			if session['user_name'] is None:
				return redirect( url_for( 'page_unauthorized' ) )
		except Exception as e:
			return redirect( url_for( 'page_unauthorized' ) )
		return f(*args, **kwargs)
	return decorated_function


# check if user is owner of playlist
def is_owner( playlist_id ):
	pl_details = playlist.Playlist( client, playlists_db_name, playlist_id ).get_details()
	
	try:
		if str( session['user_id'] ) == str( pl_details['playlist_creator_id'] ):
			return True
	except Exception as e:
		print( e )

	return False


def get_login_info():
	try:
		return {
			'user_name': session['user_name'],
			'user_id': session['user_id'],
			'logged_in': True
		}
	except:
		pass

	return {
		'user_name': "",
		'user_id': "",
		'logged_in': False
	}


""" error handler """
@app.errorhandler( HTTPException )
def handle_exception( e ):
	login = get_login_info()

	return render_template(
		"error_template.html",
		login = login,
		error = {
			'code': e.code,
			'name': e.name
		}
	)


""" authorize osu! apiv2 using OAuth2 """
@app.route( '/login/', methods = ['GET'] )
def login():
	auth = osuauth.Auth()
	return redirect( auth.request_auth() )
	

""" oauth2 callback for successful authentication """
@app.route( '/callback/' )
def callback():
	#user = oauth.osu.parse_id_token( token )
	#print( user )
	state = request.args.get( 'state' )

	if state == OAUTH_STATE:
		auth = osuauth.Auth()
		code = request.args.get( 'code' )
		user = auth.authorize( code )
		api = osuapi.OsuapiV2( user )

		me = api.get_me()
		session['user_name'] = str( me['username'] )
		session['user_id'] = str( me['id'] )

	return redirect('/')


""" logout user """
@app.route( '/logout/' )
@login_required
def logout():
	session.pop( 'user_name', None )
	session.pop( 'user_id', None )
	return redirect( '/' )


""" unauthorized action page """
@app.route( '/unauthorized/' )
def page_unauthorized():
	login = get_login_info()

	return render_template(
		"unauthorized_template.html",
		login = login
	)

""" home page """
@app.route( '/' )
def page_index():
	login = get_login_info()

	pls = playlist_finder.Playlist_Finder( client, playlist_details_db_name, playlist_details_collection_name )
	pls_rows = pls.get_non_empty_playlists()

	return render_template(
		"index_template.html",
		data = pls_rows,
		login = login
	)


""" about page """
@app.route( '/about/' )
def page_about():
	login = get_login_info()

	return render_template(
		"about_template.html",
		login = login
	)


""" delete song from playlist """
@app.route( '/delete_map/', methods = ['POST'] )
@login_required
def delete_map():
	playlist_id = request.form.get( 'playlist_id' )
	
	if is_owner( playlist_id ):
		user_id = request.form.get( 'user_id' )
		beatmap_id = request.form.get( 'beatmap_id' )

		pl = playlist.Playlist( client, playlists_db_name, playlist_id )
		pl.delete_map( user_id, beatmap_id )
		return redirect( '/p/' + playlist_id )
	
	else:
		redirect( '/unauthorized/' )

""" route user to playlist add maps page or submit map add form """
@app.route( '/p/<pl_id>/add/', methods = ['GET', 'POST'] )
@login_required
def add_map( pl_id ):
	login = get_login_info()

	if is_owner( pl_id ):
		pl = playlist.Playlist( client, playlists_db_name, pl_id )
		
		# POST method handler
		if request.method == 'POST':
			beatmap_str = request.form.get( 'beatmap_str' )
			status_msg = pl.add_map( beatmap_str )

		# GET method handler
		elif request.method == 'GET':
			status_msg = ""
		
		pl_data = pl.get_details()

		return render_template(
			"playlist_add_map_template.html",
			pl = pl_data,
			status_msg = status_msg,
			login = login
		)

	else:
		return redirect( '/unauthorized/' )


""" route user to playlist edit page or submit edit form """
@app.route( '/p/<pl_id>/edit/', methods = ['GET', 'POST'] )
@login_required
def edit_playlist( pl_id ):
	login = get_login_info()

	if is_owner( pl_id ):
		# POST method handler
		if request.method == 'POST':
			title = request.form.get( 'title' ).strip()[:75]
			desc = request.form.get( 'desc' ).strip()[:500]

			if title == '':
				title = "untitled playlist"

			pl = playlist.Playlist( client, playlists_db_name, pl_id )
			pl.edit_details( title, desc )

			return redirect( f'/p/{ pl_id }/' )

		# GET method handler
		elif request.method == 'GET':
			pl = playlist.Playlist( client, playlists_db_name, pl_id )
			pl_details = pl.get_details()

			pl_data = {
				'id': pl_id,
				'title': pl_details['playlist_title'],
				'desc': pl_details['playlist_desc']			
			}

			return render_template(
				"playlist_edit_template.html",
				pl = pl_data,
				user_name = session['user_name'],
				user_id = session['user_id'],
				login = login
			)

	else:
		return redirect( '/unauthorized/' )


""" delete a playlist """
@app.route( '/p/<pl_id>/delete/', methods = ['POST'] )
@login_required
def delete_playlist( pl_id ):
	if is_owner( pl_id ):
		if request.method == 'POST':
			pl = playlist.Playlist( client, playlists_db_name, pl_id )
			pl.delete()

		return redirect( '/' )

	else:
		return redirect( '/unauthorized/' )


@app.route( '/new_playlist/', methods = ['GET', 'POST'] )
@login_required
def new_playlist():
	pls = playlist_finder.Playlist_Finder( client, playlist_details_db_name, playlist_details_collection_name )
	playlist_id = pls.new_playlist( session['user_id'] )

	return redirect( f'/p/{ playlist_id }/edit/' )

""" route user to playlist page """
@app.route( '/p/<pl_id>/' )
def page_playlist( pl_id ):
	login = get_login_info()
	try:
		owner = is_owner( pl_id )

		pl = playlist.Playlist( client, playlists_db_name, pl_id, owner )
		pl_details = pl.get_details()
		pl_rows = pl.get_rows()
		pl_cols = pl.get_columns()
	except IndexError:
		return abort(404)

	pl_data = {
		'id': pl_id,
		'duration': pl.get_duration(),
		'size': pl.get_size(),
		'title': pl_details['playlist_title'],
		'creator': pl_details['playlist_creator_name'],
		'creator_id': pl_details['playlist_creator_id'],
		'desc': pl_details['playlist_desc']
	}

	return render_template( 
		"playlist_template.html",
		data = pl_rows,
		columns = pl_cols,
		pl = pl_data,
		login = login,
		owner = owner
	)


""" route user to userpage """
@app.route( '/u/<u_id>/' )
def page_profile( u_id ):
	login = get_login_info()

	pls = playlist_finder.Playlist_Finder( client, playlist_details_db_name, playlist_details_collection_name )
	api = osuapi.Osuapi( OSU_TOKEN )

	pl_data = pls.get_user_playlists( u_id )
	num_playlists = len( pl_data )
	display_name = api.get_user( u_id )['username']

	return render_template(
		"profile_template.html",
		data = pl_data,
		display_name = display_name,
		user_id = u_id,
		num_playlists = num_playlists,
		login = login
	)


""" route user to beatmap page """
@app.route( '/b/<map_id>/' )
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


if __name__ == '__main__':
	app.run( host='0.0.0.0', port=5000, debug=False )
