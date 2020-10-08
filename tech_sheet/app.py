import sys
import utils.playlist as playlist
from flask import Flask, render_template

app = Flask( __name__ )

@app.route( '/' )
def index():
	pl = playlist.Playlist( 'osu_maps', 'feiri_tech_maps' )
	pl_rows = pl.get_rows()
	pl_cols = pl.get_columns()
	pl_len = len( pl_rows )

	return render_template( 
		"playlist.html",
		data = pl_rows,
		columns = pl_cols,
		length = pl_len,
		title = "Feiri's curated tech maps"
	)

if __name__ == '__main__':
	app.run(debug=True)