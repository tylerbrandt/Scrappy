$(document).ready(function() {
	$("#show_sidebar").on('click', function() {
		var left;

		$(".sidebar").toggle("fast",function() {
			if($(".sidebar").is(":visible")) {
				left = $(".sidebar").width();
				$(".main_content").css('left',left);
			} else {
				$(".main_content").css('left','0');
			}
		});
		
	});
});