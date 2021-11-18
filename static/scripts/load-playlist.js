let beatmap_ids = [];
function init_playlist( data, columns ) {
	$( window ).on( 'load', function() {
		$(function() {
			data.forEach(map => beatmap_ids.push(map.mirror.split("https://beatconnect.io/b/")[1].split('\'')[0]));
			let table = $('#playlist-table').DataTable( {
				data: data,
				columns: columns,
				paging: false,
				info: false,
				responsive: true
			});

		});
	});
	
	/*$('#playlist-table tbody').on( 'click', '.remove', function () {
	   	$(this).parents('form')[0].submit();
	    $('#playlist-table').DataTable().row( $(this).parents('tr') ).remove().draw();
	});*/
}