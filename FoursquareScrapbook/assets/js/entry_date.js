$(document).ready(function() {
	$('.entry_date').on('click', '.all', function() {
		$('.dated_entries').each(function() {
			$(this).show();
		});
	});

	$('.entry_date').on('click', 'li a', function() {
		var type = $(this).attr('class'),
			target = $(this).attr('href').replace('#nav_' + type + '_','');
		if (type) {
			$('.dated_entries').each(function() {
				var data = $(this).data('date'),
					timestamp = '' + data[type];
				if(timestamp !== target) {
					$(this).hide();
				} else {
					$(this).show();
				}
			});
		}
		
	});
});