document.getElementById('search-bar').addEventListener('input', function (event) {
    const searchTerm = event.target.value.toLowerCase();
    const trips = document.querySelectorAll('.trip-card');

    trips.forEach(function (trip) {
        const searchTerms = JSON.parse(trip.getAttribute('search-terms')).map(term => term.toLowerCase());
        console.log(searchTerms);
        console.log(searchTerms.includes('test'));

        if (searchTerms.some(term => term.includes(searchTerm))) {
            trip.style.display = 'block';
        } else {
            trip.style.display = 'none';
        }
    });
});
