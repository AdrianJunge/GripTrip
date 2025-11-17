document.addEventListener('DOMContentLoaded', function () {
    const wrapper = document.getElementById('notification-wrapper');
    if (!wrapper) return;

    const notifications = Array.from(wrapper.querySelectorAll('.notification'));

    notifications.forEach((node, index) => {
        const showDelay = index * 150;
        const duration = parseInt(node.getAttribute('data-duration')) || 10000;

        setTimeout(() => {
            node.classList.add('show');
            const timeoutId = setTimeout(() => {
                hideNotification(node);
            }, duration);

            const btn = node.querySelector('.close-btn');
            if (btn) {
                btn.addEventListener('click', () => {
                    clearTimeout(timeoutId);
                    hideNotification(node);
                });
            }
        }, showDelay);
    });

    function hideNotification(node) {
        node.classList.remove('show');
        node.classList.add('hide');
        setTimeout(() => {
            if (node && node.parentNode) node.parentNode.removeChild(node);
        }, 350);
    }
});
