document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('input.tagify').forEach(function (input) {
        try {
            const tf = new Tagify(input, {
                dropdown: { enabled: 0 },
                originalInputValueFormat: valuesArr => JSON.stringify(valuesArr.map(v => v.value))
            });
        } catch (err) {
            console.warn('Tagify init failed for', input, err);
        }
    });

    document.querySelectorAll('.mv-dates-widget').forEach(function (widget) {
        const startInput = widget.querySelector('.mv-start');
        const endInput = widget.querySelector('.mv-end');
        const addBtn = widget.querySelector('.mv-add');
        const list = widget.querySelector('.mv-list');

        function renderRangeDisplay(s, e) {
            const disp = document.createElement('div');
            disp.className = 'd-inline-flex align-items-center me-2 mb-1 badge bg-primary text-white';
            disp.style.padding = '0.45rem 0.6rem';
            disp.textContent = s + ' → ' + e;

            const close = document.createElement('button');
            close.type = 'button';
            close.className = 'btn-close btn-close-white btn-sm ms-2';
            close.style.marginLeft = '6px';
            close.addEventListener('click', function () {
                const hs = list.querySelector('input[type="hidden"][name="start_date"][value="' + s + '"]');
                const he = list.querySelector('input[type="hidden"][name="end_date"][value="' + e + '"]');
                if (hs) hs.remove();
                if (he) he.remove();
                disp.remove();
            });

            disp.appendChild(close);
            list.appendChild(disp);
        }

        function addRange() {
            const s = startInput.value;
            const e = endInput.value;
            if (!s || !e) return;
            const hs = document.createElement('input'); hs.type = 'hidden'; hs.name = 'start_date'; hs.value = s;
            const he = document.createElement('input'); he.type = 'hidden'; he.name = 'end_date'; he.value = e;
            list.appendChild(hs);
            list.appendChild(he);
            renderRangeDisplay(s, e);

            startInput.value = '';
            endInput.value = '';
            startInput.focus();
        }

        if (addBtn) addBtn.addEventListener('click', addRange);

        const hiddenStarts = Array.from(list.querySelectorAll('input[type="hidden"][name="start_date"]'));
        hiddenStarts.forEach(function (hs) {
            const s = hs.value;
            let foundEnd = null;
            let node = hs.nextSibling;
            while (node) {
                if (node.nodeType === 1 && node.tagName.toLowerCase() === 'input' && node.getAttribute('name') === 'end_date') {
                    foundEnd = node; break; 
                }
                node = node.nextSibling;
            }
            const e = foundEnd ? foundEnd.value : null;
            if (e) {
                renderRangeDisplay(s, e);
            }
        });
    });
});
