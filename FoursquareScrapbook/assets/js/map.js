$(document).ready(function() {
	// var lat,lng,


	function getCheckinsLocs() {
		var locs = [], bounds = new google.maps.LatLngBounds();

		$(".book_entries article").each(function() {
			var loc, lat, lng;
			if($(this).find(".checkin").length > 0) {
				
				loc = $(this).find(".checkin").data("geo");
				//loc = JSON.parse(locdata);
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
    	var i, len, latlng, latlngs = [];
    	for(i = 0, len=locs.length; i < locs.length; i++) {
    		var loc=locs[i],
    			latlng = new google.maps.LatLng(loc.lat, loc.lng),
    			marker = new google.maps.Marker({
					position: latlng,
					map: map,
					title: loc.title
				});

				google.maps.event.addListener(marker, 'click', jumpToArticle(loc));

				latlngs.push(latlng);
    	}

    	var path = new google.maps.Polyline({
    		path: latlngs,
    		strokeColor: "blue",
    		strokeOpacity: 0.5,
    		strokeWeight: 4.0
    	});

    	path.setMap(map);
    }

	function init() {
		var checkins = getCheckinsLocs(),
			map = new google.maps.Map(document.getElementById("map_canvas"), {
      			zoom: 15,
      			center: checkins.bounds.getCenter(),
      			mapTypeId: google.maps.MapTypeId.HYBRID            
    		});

    	map.fitBounds(checkins.bounds);

    	addPostMarkers(map,checkins.locs);	
	}
	
	init();
});