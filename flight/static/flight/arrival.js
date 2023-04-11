window.addEventListener('DOMContentLoaded', function() {
    let selects = document.querySelectorAll('select')
    selects.forEach(function (select) {
        let index = select.selectedIndex;
        Array.from(select.options).forEach(function (opt, i) {
            if (i < index) {
                opt.disabled = true;
            }
        });
    });
});
