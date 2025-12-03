
document.addEventListener("DOMContentLoaded", () => {
    const handle = document.getElementById("dashboard-handle");
    const target = document.getElementById("trips-grid");
    
    handle.addEventListener("click", () => {
        target.scrollIntoView({ behavior: "smooth" });

    })
});