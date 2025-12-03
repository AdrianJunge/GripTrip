document.addEventListener("DOMContentLoaded", () => {
    const searchBar = document.getElementById("search-bar");
    const results = document.getElementById("search-results");
    
    searchBar.addEventListener("input", () => {
        const filteredTrips = [];
        const q = searchBar.value.trim().toLowerCase();
        if (!q) {
            results.style.display = "none";
            results.innerHTML = "";
            document.querySelectorAll('.trip-card').forEach(t => t.style.display = 'block');

            if (window.filterMapMarkers) {
                const allIds = Array.from(document.querySelectorAll('.trip-card'))
                    .map(t => t.getAttribute('trip-id'));
                window.filterMapMarkers(allIds);
            }
            return;
        }

        const searchTerm = q;
        const trip_cards = document.querySelectorAll('.trip-card');

        trip_cards.forEach(function (trip) {
            const searchTerms = JSON.parse(trip.getAttribute('search-terms')).map(term => term.toLowerCase());

            if (searchTerms.some(term => term.includes(searchTerm))) {
                trip.style.display = 'block';

                if (!filteredTrips.find(t => t.id === trip.getAttribute('trip-id'))) {
                    filteredTrips.push({
                        id: trip.getAttribute('trip-id'),
                        title: trip.getAttribute('trip-name'),
                    });
                }
            } else {
                trip.style.display = 'none';
            }
        });

        results.innerHTML = filteredTrips
            .map(t => `<li data-id="${t.id}">${t.title}</li>`)
            .join("");
        results.style.display = filteredTrips.length ? "block" : "none";

        console.log("Filtered trips:", filteredTrips);

        if (window.filterMapMarkers) {
            const visibleIds = filteredTrips.map(t => String(t.id));
            window.filterMapMarkers(visibleIds);
        }
    });
    
    results.addEventListener("click", (e) => {
        const li = e.target.closest("li");
        if (!li) return;  
        const tripId = li.dataset.id;
        window.location.href = `/trip/${tripId}`;
    });
    
    searchBar.addEventListener("keydown", (e) => {
        if (e.key === "Enter") {
            e.preventDefault();
            const first = results.querySelector("li");
            if (!first) return;
            const tripId = first.dataset.id;
            window.location.href = `/trip/${tripId}`;
        }
    });

    document.addEventListener("click", (e) => {
        if (!searchBar.contains(e.target) && !results.contains(e.target)) {
            results.style.display = "none";
        }
    });
});
