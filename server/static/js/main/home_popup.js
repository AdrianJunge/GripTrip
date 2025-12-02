//creates map object disables default leaflet zoom lock
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
            className: 'travel-icon'            
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
                    .bindPopup(`<div class="map-popup-row">
                    <strong class="map-popup-title">${trip.title}</strong>
                    <a href="/trip/${trip.id}" class="map-view-button">View</a>
                    </div>
                </div>`);
                }
                else{ //not a member of trip can join from map
                    if(!trip.is_full){
                        L.marker([trip.lat, trip.lon], { icon: curr_icon }).addTo(map)
                        .bindPopup(`
                        <div class="map-popup-row">
                            <strong class="map-popup-title">${trip.title}</strong>
                            <form action="/trip/join/${trip.id}" method="POST">
                                <button type="submit" class="map-join-button">Join?</button>
                            </form>
                        </div>
                    `);
                    }                        
                }
                allCoords.push([trip.lat, trip.lon]);
            }
        }
    )};

    //set coordinates and map view relative to trips
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