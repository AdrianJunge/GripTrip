//creates map object disables default leaflet zoom lock
const map = L.map('map', {
    zoomSnap: 0,
    zoomDelta: 0.25,
});

//sets tile layer
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
    }).addTo(map);

    //creates custom icons
    var TravelIcon = L.Icon.extend({
        options: {
            iconSize: [40, 50],
            iconAnchor: [20, 40],
            popupAnchor: [0, -35],            
        }
    });
    var greenIcon = new TravelIcon({iconUrl: '/static/trip_icons/Map_pin_icon_green.png'}),
    redIcon = new TravelIcon({iconUrl: '/static/trip_icons/Map_pin_icon_red.png'});

    //set all coordinates array and add markers for each trip
    let allCoords = [];
    const tripsData = document.getElementById("map").dataset.trips;
    let mapTrips = [];
    if (tripsData){
        mapTrips = JSON.parse(tripsData);
    }

    //shows green markers for available trips and red for unavailable trips (only allow link for user's trips)
    if (mapTrips.length > 0) {
        mapTrips.forEach(function (trip) {
            if (trip.lat && trip.lon) {
                const curr_icon = trip.available_to_user ? greenIcon : redIcon;
                if (curr_icon === greenIcon){
                    L.marker([trip.lat, trip.lon], { icon: curr_icon }).addTo(map)
                    .bindPopup(`<a href="/trip/${trip.id}">
                    <strong>${trip.title}</strong> </a>`);
                }
                else{
                    L.marker([trip.lat, trip.lon], { icon: curr_icon }).addTo(map)
                    .bindPopup(`<strong>${trip.title}</strong>`);
                }
            }
            allCoords.push([trip.lat, trip.lon]);
        });
    }

    //set coordinates and map view relative to trips
    if (allCoords.length === 0) {
        map.setView([54, 15], 4);
    } else if (allCoords.length === 1) {
        map.setView(allCoords[0], 6);
    } else {
        const bounds = L.latLngBounds(allCoords);
        map.fitBounds(bounds, { padding: [20, 20] });
        setTimeout(function () {
            map.setZoom(map.getZoom() + 0.25);
        }, 200);
    }