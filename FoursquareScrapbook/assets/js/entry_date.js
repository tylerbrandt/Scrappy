$(document).ready(function() {
	$('.entry_date').on('click', '.all', function() {
		$('.book_entry').each(function() {
			$(this).show();
		});
	});

	$('.entry_date').on('click', 'li a', function() {
		var type = $(this).attr('class'),
			target = $(this).text();
		if (type) {
			$('.book_entry').each(function() {
				var timestamp = '' + $(this).data('date')[type];
				if(timestamp !== target) {
					$(this).hide();
				} else {
					$(this).show();
				}
			});
		}
		
	});
});