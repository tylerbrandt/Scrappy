$(document).ready(function() {
	// var lat,lng,


	function getCheckinsLocs() {
		var locs = [], bounds = new google.maps.LatLngBounds();

		$(".book_entries article").each(function() {
			var loc, lat, lng;
			if($(this).find(".checkin").length > 0) {
				
				loc = JSON.parse($(".geo", this).html());
				lat = parseFloat(loc.lat);
				lng = parseFloat(loc.lng);

				loc.title = $(".checkin .title", this).text();
				loc.id = $(this).attr("id");
				locs.push(loc);

				bounds.extend(new google.maps.LatLng(lat,lng));
			}
		});

		return {
			bounds: bounds,
			locs: locs
		};
	}

	function jumpToArticle(loc) {
		return function() {
			window.location.hash = loc.id;
		};
	}

	function addPostMarkers(map,locs) {
    	var i,len;
    	for(i = 0, len=locs.length; i < locs.length; i++) {
    		var loc=locs[i],
    			marker = new google.maps.Marker({
					position: new google.maps.LatLng(loc.lat, loc.lng),
					map: map,
					title: loc.title
				});

				google.maps.event.addListener(marker, 'click', jumpToArticle(loc));
    	}
    }

	var checkins = getCheckinsLocs(),
		map = new google.maps.Map(document.getElementById("map_canvas"), {
      		zoom: 15,
      		center: checkins.bounds.getCenter(),
      		mapTypeId: google.maps.MapTypeId.HYBRID            
    	});

    	map.fitBounds(checkins.bounds);

    addPostMarkers(map,checkins.locs);
});