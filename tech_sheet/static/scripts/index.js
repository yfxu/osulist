function init_playlist( data, columns ) {
	$( window ).on( 'load', function() {
		$(function() {
			$('#table').bootstrapTable({ 
				data: data,
				columns: columns,
				searchSelector: "#custom_search"
			});
		});
	});
}