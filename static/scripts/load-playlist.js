function init_playlist( data, columns ) {
	$( window ).on( 'load', function() {
		$(function() {
			var table = $('#playlist-table').DataTable( { 
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