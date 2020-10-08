import sys
import utils.playlist as playlist
from flask import Flask, render_template

app = Flask( __name__ )

@app.route( '/' )
def index():
	pl = playlist.Playlist( 'osu_maps', 'feiri_tech_maps' )
	pl_rows = pl.get_rows()
	pl_cols = pl.get_columns()
	pl_size = len( pl_rows )
	pl_duration = pl.get_duration()
	pl_title = """Feiri's tech pack"""
	pl_desc = """Please note that the definition of \\"tech\\" is not well-defined. It may range from person-to-person."""
	pl_creator = "Feiri"
	
	return render_template( 
		"playlist.html",
		data = pl_rows,
		columns = pl_cols,
		pl_size = pl_size,
		pl_title = pl_title,
		pl_desc = pl_desc,
		pl_duration = pl_duration,
		pl_creator = pl_creator
	)

if __name__ == '__main__':
	app.run(debug=True)