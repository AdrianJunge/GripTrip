document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('.role-select').forEach(function(sel){
        sel.addEventListener('change', function(e){
            const userId = sel.getAttribute('data-user-id');
            const newRole = sel.value;

            fetch(`/trip/${window.currentTripId}/participant/${userId}/role`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ role: newRole })
            }).then(r => r.json()).then(data => {
                if (data && data.success) {
                    const badge = document.getElementById(`role-badge-${userId}`);
                    if (badge) badge.textContent = data.new_role.charAt(0) + data.new_role.slice(1).toLowerCase();
                    if (data.messages && Array.isArray(data.messages)) showMessages(data.messages);
                } else {
                    const badge = document.getElementById(`role-badge-${userId}`);
                    if (badge) {
                        const current = badge.textContent.toUpperCase();
                        sel.value = current;
                    }
                    if (data && data.error) {
                        showMessages([{category: 'error', text: data.error}]);
                    }
                }
            }).catch(err => {
                console.error(err);
                alert('Failed to change role');
            });
        });
    });

    document.querySelectorAll('.promote-btn').forEach(function(btn){
        btn.addEventListener('click', function(e){
            const userId = btn.getAttribute('data-user-id');

            fetch(`/trip/${window.currentTripId}/participant/${userId}/role`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ role: 'EDITOR' })
            }).then(r => r.json()).then(data => {
                if (data && data.success) {
                    const badge = document.getElementById(`role-badge-${userId}`);
                    if (badge) badge.textContent = 'Editor';
                    btn.disabled = true;
                    btn.textContent = 'Editor';
                    if (data.messages && Array.isArray(data.messages)) showMessages(data.messages);
                } else {
                    if (data && data.error) showMessages([{category: 'error', text: data.error}]);
                    else showMessages([{category: 'error', text: 'Failed to promote'}]);
                }
            }).catch(err => {
                console.error(err);
                alert('Failed to promote');
            });
        });
    });

    function showMessages(messages) {
        if (!messages || !messages.length) return;
        messages.forEach(m => {
            window.pushNotification(m.category || 'info', m.text || m, 8000);
        });
    }
});
