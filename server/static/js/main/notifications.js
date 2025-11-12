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

window.pushNotification = function(category, message, duration) {
    const wrapper = document.getElementById('notification-wrapper');
    if (!wrapper) return;

    const node = document.createElement('div');
    node.className = `notification ${category || ''}`.trim();
    node.setAttribute('data-duration', duration || 8000);

    const content = document.createElement('div');
    content.className = 'notification-content';
    content.textContent = message || '';
    node.appendChild(content);

    const btn = document.createElement('button');
    btn.className = 'close-btn';
    btn.setAttribute('aria-label', 'Close');
    btn.innerHTML = '&times;';
    node.appendChild(btn);

    wrapper.appendChild(node);

    setTimeout(() => node.classList.add('show'), 20);

    const timeoutId = setTimeout(() => hide(node), parseInt(node.getAttribute('data-duration')) || 8000);

    btn.addEventListener('click', () => {
        clearTimeout(timeoutId);
        hide(node);
    });

    function hide(n) {
        n.classList.remove('show');
        n.classList.add('hide');
        setTimeout(() => {
            if (n && n.parentNode) n.parentNode.removeChild(n);
        }, 350);
    }
};
