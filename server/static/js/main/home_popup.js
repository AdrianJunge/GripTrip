const map = L.map('map');

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
}).addTo(map);

var TravelIcon = L.Icon.extend({
    options: {
        iconSize: [40, 50],
        iconAnchor: [20, 40],
        popupAnchor: [0, -35],
        className: 'travel-icon'            
    }
});
var greenIcon = new TravelIcon({iconUrl: '/static/trip_icons/Map_pin_icon_green.png'});
var redIcon = new TravelIcon({iconUrl: '/static/trip_icons/Map_pin_icon_red.png'});

window.mapMarkers = {};

let allCoords = [];
const tripsData = document.getElementById("map").dataset.trips;
let mapTrips = [];
if (tripsData){
    mapTrips = JSON.parse(tripsData);
}

if (mapTrips.length > 0) {
    mapTrips.forEach(function (trip) {
        if (trip.lat && trip.lon) {
            const curr_icon = trip.available_to_user ? greenIcon : redIcon;

            const marker = L.marker([trip.lat, trip.lon], { icon: curr_icon });

            if (curr_icon === greenIcon) {
                marker.bindPopup(`
                    <div class="map-popup-row">
                        <strong class="map-popup-title">${trip.title}</strong>
                        <a href="/trip/${trip.id}" class="map-view-button">View</a>
                    </div>
                `);
                marker.addTo(map);
                window.mapMarkers[String(trip.id)] = { marker: marker, added: true };
            } else {
                if (!trip.is_full) {
                    marker.bindPopup(`
                        <div class="map-popup-row">
                            <strong class="map-popup-title">${trip.title}</strong>
                            <form action="/trip/join/${trip.id}" method="POST">
                                <button type="submit" class="map-join-button">Join?</button>
                            </form>
                        </div>
                    `);
                    marker.addTo(map);
                    window.mapMarkers[String(trip.id)] = { marker: marker, added: true };
                }
            }
            allCoords.push([trip.lat, trip.lon]);
        }
    });
}

if (allCoords.length === 0) {
    map.setView([54, 15], 4);
} else if (allCoords.length === 1) {
    map.setView(allCoords[0], 6);
} else {
    const bounds = L.latLngBounds(allCoords);
    map.fitBounds(bounds, { padding: [20, 20] });
    setTimeout(function () {
        map.setZoom(map.getZoom() + 0.5);
    }, 200);
}

window.filterMapMarkers = function(visibleIds) {
    const visibleSet = new Set((visibleIds || []).map(id => String(id)));

    Object.keys(window.mapMarkers).forEach(key => {
        const entry = window.mapMarkers[key];
        const shouldShow = visibleSet.has(String(key));
        if (shouldShow && !entry.added) {
            entry.marker.addTo(map);
            entry.added = true;
        } else if (!shouldShow && entry.added) {
            map.removeLayer(entry.marker);
            entry.added = false;
        }
    });
};
