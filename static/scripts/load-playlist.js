let beatmap_ids = [];
function init_playlist( data, columns ) {
	$( window ).on( 'load', function() {
		$(function() {
			data.forEach(map => beatmap_ids.push([map.mirror.match(/(?<=<a.*href='https?:\/\/beatconnect.io\/b\/)([0-9]+)(?='.*>.*<\/a>)/)[0], map.title.match(/(?<=<a.*>).*(?= \[.*]<\/a>)/)[0].replaceAll(/[\\/:"*?<>|]+/g, "_")]));
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