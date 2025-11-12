const map = L.map('map').setView([54, 15], 3);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
    }).addTo(map);

    const lat = document.getElementById('map').dataset.lat;
    const lon = document.getElementById('map').dataset.lon;
    const country_name = document.getElementById('map').dataset.country;

    if(lat && lon){
            L.marker([lat, lon]).addTo(map)
                .bindPopup("Home: " + country_name)
                .openPopup();

            map.setView([lat, lon], 5);
    }