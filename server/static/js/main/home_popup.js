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

const csrfToken = document.querySelector('meta[name="csrf-token"]')?.content || '';

let tripGroups = {}
mapTrips.forEach(function (trip) {
    if(!trip.lat || !trip.lon) return;
    const key = `${trip.lat},${trip.lon}`;
    if(!tripGroups[key]) tripGroups[key] = [];
    if (!tripGroups[key].some(t => t.id === trip.id)) {
        tripGroups[key].push(trip);
    } 
});

Object.keys(tripGroups).forEach(function (key) {
    const group = tripGroups[key];
    const [lat, lon] = key.split(',').map(Number);
    const isGreen = group.some(t => t.available_to_user);
    const iconColor = isGreen ? greenIcon : redIcon;

    let popupContent = '';
    group.forEach(function (trip) {
        if(trip.available_to_user){
            popupContent += `<br><div class="map-popup-row">
                <strong class="map-popup-title">${trip.title}</strong>
                <a href="/trip/${trip.id}" class="map-view-button">View</a>
            </div><br>`;
        } else {
            if(!trip.is_full){
                popupContent += `<br><div class="map-popup-row">
                    <strong class="map-popup-title">${trip.title}</strong>
                    <form action="/trip/join/${trip.id}" method="POST">
                        <input type="hidden" name="csrf_token" value="${csrfToken}"/>
            
                        <button type="submit" class="map-join-button">Join?</button>
                    </form>
                </div><br>`;
            }
        }
    });
    popupContent += '';
    const marker = L.marker([lat, lon], { icon: iconColor });
    allCoords.push([lat, lon]);

    marker.bindPopup(popupContent);
    marker.addTo(map);
    group.forEach(function (trip) {
        window.mapMarkers[String(trip.id)] = { marker: marker, added: true };
    });
});

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
