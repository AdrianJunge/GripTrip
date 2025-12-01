//creates map object
const map = L.map('map');

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
    const tripsData = document.getElementById("map").dataset.trips;
    let mapTrips = [];
    if (tripsData){
        mapTrips = JSON.parse(tripsData);
    }

    if (mapTrips.length > 0) {
        mapTrips.forEach(function (trip) {
            if (trip.lat && trip.lon) {
                L.marker([trip.lat, trip.lon], { icon: greenIcon }).addTo(map)
                    .bindPopup(`<a href="/trip/${trip.id}">
                    <strong>${trip.title}</strong> </a>`);
            }
        });
    }

    //set coordinates and map view
    if (allCoords.length === 0) {
        map.setView([54, 15], 3);
    } else if (allCoords.length === 1) {
        map.setView(allCoords[0], 5);
    } else {
        const bounds = L.latLngBounds(allCoords);
        map.fitBounds(bounds, { padding: [50, 50] });
    }