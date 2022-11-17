def sanitize( s ):
	return s.replace( "<", "&lt;" ).replace( ">", "&gt;" )

def html_a_format( url, text ):
	return "<a href='{}'>{}</a>".format( url, sanitize( text ) )

def html_a_blank_format( url, text ):
	return "<a href='{}' target='_blank'>{}</a>".format( url, sanitize( text ) )

# modify to have randon auth hash to verify owner
# target="dummyframe"
def html_delete_format( url, playlist_id, user_id, beatmap_id, text ):
	return f"""<form action="{ url }/" method="POST" id="del-{ playlist_id }-{ beatmap_id }">
	<input name="playlist_id" type="hidden" value="{ playlist_id }"/>
	<input name="user_id" type="hidden" value="{ user_id }"/>
	<input name="beatmap_id" type="hidden" value="{ beatmap_id }"/>
	<button class="remove">{ sanitize( text ) }</button>
</form>"""