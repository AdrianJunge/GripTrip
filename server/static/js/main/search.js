document.addEventListener("DOMContentLoaded", () => {
    const searchBar = document.getElementById("search-bar");
    const results = document.getElementById("search-results");
    
    searchBar.addEventListener("input", () => {
        const filteredTrips = [];
        const q = searchBar.value.trim().toLowerCase();
        if (!q) {
            results.style.display = "none";
            results.innerHTML = "";
        }

        const searchTerm = searchBar.value.toLowerCase();
        const trip_cards = document.querySelectorAll('.trip-card');

        trip_cards.forEach(function (trip) {
            const searchTerms = JSON.parse(trip.getAttribute('search-terms')).map(term => term.toLowerCase());

            if (searchTerms.some(term => term.includes(searchTerm))) {
                trip.style.display = 'block';

                filteredTrips.push({
                    id: trip.getAttribute('trip-id'),
                    title: trip.getAttribute('trip-name'),
                });
                results.innerHTML = filteredTrips
                    .map(t => `<li data-id="${t.id}">${t.title}</li>`)
                    .join("");
                results.style.display = filteredTrips.length ? "block" : "none";
            } else {
                trip.style.display = 'none';
            }
        });
        
        const target = document.getElementById("dashboard-handle");
        target.scrollIntoView({ behavior: "smooth" });
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
