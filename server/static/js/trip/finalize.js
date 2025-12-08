document.addEventListener('DOMContentLoaded', function () {
    const csrfToken = document.querySelector('meta[name="csrf-token"]')?.content || '';

    document.querySelectorAll('.toggle-final-btn').forEach(function(btn){
        btn.addEventListener('click', function(){
            const field = btn.getAttribute('data-field');
            const action = btn.getAttribute('data-action');
            btn.disabled = true;
            fetch(window.location.pathname, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': csrfToken,
                },
                body: new URLSearchParams({ toggle_final: field, toggle_action: action })
            }).then(function(resp){
                if (resp.ok) {
                    window.location.reload();
                } else {
                    return resp.text().then(function(t){ throw new Error(t || 'Request failed'); });
                }
            }).catch(function(err){
                console.error('Toggle finalize failed', err);
                alert('Unable to change final state.');
                btn.disabled = false;
            });
        });
    });
});