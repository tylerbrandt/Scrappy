$(document).ready(function() {
	$("#show_sidebar").on('click', function() {
		var left, content_pos = $(".main_content").css("left");

		if(parseInt(content_pos, 10) === 0) {
			left = $(".sidebar").css('width');
			$(".main_content").css({ 'left': left });
		} else {
			$(".main_content").css({ 'left': '0' });
		}
		
	});
});