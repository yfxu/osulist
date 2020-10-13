import sys
import utils.playlist as playlist
import utils.playlist_finder as playlist_finder
import utils.osuapi as osuapi
from flask import Flask, render_template
from random import randrange
from dotenv import load_dotenv, find_dotenv

app = Flask( __name__ )

# import env variables
load_dotenv( find_dotenv() )
OSU_TOKEN = load_dotenv( 'OSU_TOKEN' )

# constants
playlists_db_name = 'playlists'
playlist_details_db_name = "playlist_details"
playlist_details_collection_name = "details"
osu_base_url = "https://osu.ppy.sh"

@app.route( '/' )
def page_index():
	pls = playlist_finder.Playlist_Finder( playlist_details_db_name, playlist_details_collection_name )

	pls_rows = pls.get_rows()
	pls_cols = pls.get_columns()
	
	return render_template(
		"index_template.html",
		data = pls_rows,
		columns = pls_cols
	)


""" authorize osu! apiv2 using OAuth2 """
@app.route( '/osuauth/login' )
def auth():
	return


""" route user to beatmap page """
@app.route( '/b/<map_id>' )
def page_beatmap( map_id ):
	api = osuapi.Osuapi( OSU_TOKEN )
	b = api.get_beatmap( map_id )

	b_url = f"{ osu_base_url }/b/{ map_id }"
	b_img = f"https://b.ppy.sh/thumb/{ b['beatmapset_id'] }.jpg"
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


""" route user to playlist page """
@app.route( '/p/<pl_id>' )
def page_playlist( pl_id ):
	pl = playlist.Playlist( playlists_db_name, pl_id )
	pl_details = pl.get_details()
	
	pl_rows = pl.get_rows()
	pl_cols = pl.get_columns()
	pl_duration = pl.get_duration()

	pl_title = pl_details['playlist_title']
	pl_creator = pl_details['playlist_creator_name']
	pl_desc = pl_details['playlist_desc']
	pl_size = pl_details['playlist_size']

	random_num = randrange( 10000000, 99999999 )
	return render_template( 
		"playlist_template.html",
		data = pl_rows,
		columns = pl_cols,
		pl_size = pl_size,
		pl_title = pl_title,
		pl_desc = pl_desc,
		pl_duration = pl_duration,
		pl_creator = pl_creator,
		random_num = random_num
	)

if __name__ == '__main__':
	app.run(debug=True, host='0.0.0.0')