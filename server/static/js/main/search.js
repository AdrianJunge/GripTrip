document.addEventListener("DOMContentLoaded", () => {
    const searchBar = document.getElementById("search-bar");
    const results = document.getElementById("search-results");
    console.log("Search bar:", searchBar);
    console.log("Results:", results);
    
    const header = document.querySelector(".header");
    const tripIds = header ? JSON.parse(header.dataset.trips || '[]') : [];
    const tripTitles = header ? JSON.parse(header.dataset.tripTitles || '[]') : [];

    const trips = tripIds.map((id, index) => ({
        id: id,
        title: tripTitles[index]
    }));
    
    searchBar.addEventListener("input", () => {
        const q = searchBar.value.trim().toLowerCase();
        if (!q) {
            results.style.display = "none";
            results.innerHTML = "";
            return;
        }

        const filteredTrips = trips.filter(t => 
            t.title.toLowerCase().includes(q)
        );
        results.innerHTML = filteredTrips
            .map(t => `<li data-id="${t.id}">${t.title}</li>`)
            .join("");
        results.style.display = filteredTrips.length ? "block" : "none";
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