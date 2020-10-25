def html_a_format( url, text ):
	return "<a href='{}'>{}</a>".format( url, text )

def html_a_blank_format( url, text ):
	return "<a href='{}' target='_blank'>{}</a>".format( url, text )

# modify to have randon auth hash to verify owner
def html_delete_format( url, playlist_id, user_id, beatmap_id, text ):
	return f"""<form action="{ url }" method="POST">
	<input name="playlist_id" type="hidden" value="{ playlist_id }"/>
	<input name="user_id" type="hidden" value="{ user_id }"/>
	<input name="beatmap_id" type="hidden" value="{ beatmap_id }"/>
	<button id="del-{ playlist_id }-{ beatmap_id }">{ text }</button>
</form>"""