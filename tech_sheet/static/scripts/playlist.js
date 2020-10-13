function init_playlist( data, columns, pl_size, pl_desc, pl_title, pl_duration, pl_creator, pl_osu_beatmap_url ) {
	$( window ).on( 'load', function() {
		$(function() {
			$('#table').bootstrapTable({ 
				data: data,
				columns: columns,
				searchSelector: "#custom_search" /*,
				showColumns: true */
			});
		});
		$(function() {
			$('#text_size').text( pl_size );
		});
		$(function() {
			$('#text_duration').text( pl_duration );
		});
		$(function() {
			$('#text_title').text( pl_title );
		});
		$(function() {
			$('#text_desc').text( pl_desc );
		});
		$(function() {
			$('#text_creator').text( pl_creator );
		});
		$(function() {
			$('#tab_title').text( pl_title );
		});
	});

	function sortTable() {
		//get the parent table for convenience
		let table = document.getElementById("table");

		//1. get all rows
		let rowsCollection = table.querySelectorAll("tr");

		//2. convert to array
		let rows = Array.from(rowsCollection)
		.slice(1); //skip the header row

		//3. shuffle
		shuffleArray(rows);

		//4. add back to the DOM
		for (const row of rows) {
			table.appendChild(row);
		}
	}

	function shuffleArray( array ) {
		for (var i = array.length - 1; i > 0; i--) {
			var j = Math.floor(Math.random() * (i + 1));
			var temp = array[i];
			array[i] = array[j];
			array[j] = temp;
		}
	}

	$(document).ready(function(){
		$("#search_filter").on("keyup", function() {
			var value = $(this).val().toLowerCase();
			$("#table tr").filter(function() {
				$(this).toggle($(this).text().toLowerCase().indexOf(value) > -1)
			});
		});
	});

	var $search = $('.fixed-table-toolbar .search input');
	$search.attr('placeholder', 'New placeholder');
	$search.css('border', '1px solid red');
}