function init_playlist( data, columns, pl_size, pl_desc, pl_title, pl_duration, pl_creator, pl_osu_beatmap_url ) {
	$( window ).on( 'load', function() {
		$(function() {
			$('#playlist_table').DataTable( { 
				data: data,
				columns: columns
			});
		});
	});
}