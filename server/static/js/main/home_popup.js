const map = L.map('map');

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
    }).addTo(map);

    var TravelIcon = L.Icon.extend({
        options: {
            iconSize: [40, 50],
            iconAnchor: [20, 40],
            popupAnchor: [0, -35],            
        }
    });

    var greenIcon = new TravelIcon({iconUrl: '/static/trip_icons/Map_pin_icon_green.png'}),
    redIcon = new TravelIcon({iconUrl: '/static/trip_icons/Map_pin_icon_red.png'});
    
    var allCoords = [];


    const h_lat = document.getElementById('map').dataset.lat;
    const h_lon = document.getElementById('map').dataset.lon;
    const h_country_name = document.getElementById('map').dataset.country;

    if(h_lat && h_lon){
        allCoords.push([h_lat, h_lon]);
            L.marker([h_lat, h_lon], { icon: redIcon }).addTo(map)
                .bindPopup("Home: <strong>" + h_country_name + "</strong>")
                .openPopup();

            map.setView([h_lat, h_lon], 5);
    }

    //need a better way of doing this
    const tripsData = document.getElementById("map").dataset.trips;
    let mapTrips = [];
    if (tripsData){
        mapTrips = JSON.parse(tripsData);
    }

    const pin_points = {};
    mapTrips.forEach(function (trip) {
        if (trip.lat && trip.lon) {
            allCoords.push([trip.lat, trip.lon]);
            const key = trip.lat + ',' + trip.lon;
            if (pin_points[key]) {
                pin_points[key].push(trip);
            } else {
                pin_points[key] = [trip];
            }
        }
    });
    //warning trips with same location will not be displayed correctly
    if (mapTrips.length > 0) {
        mapTrips.forEach(function (trip) {
            if (trip.lat && trip.lon) {
                L.marker([trip.lat, trip.lon], { icon: greenIcon }).addTo(map)
                    .bindPopup(`<a href="/trip/${trip.id}">
                    <strong>${trip.title}</strong> </a>`);
            }
        });
    }

    if (allCoords.length === 0) {
        map.setView([54, 15], 3);
    } else if (allCoords.length === 1) {
        map.setView(allCoords[0], 5);
    } else {
        const bounds = L.latLngBounds(allCoords);
        map.fitBounds(bounds, { padding: [50, 50] });
    }