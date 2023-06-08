let searchTerm = document.getElementById('id_search_term')

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

searchTerm.addEventListener('input', () => {
    document.getElementsByClassName('default')[0].disabled = true;
    timeoutId = setTimeout(function() {
        document.getElementsByClassName('default')[0].disabled = false;
        document.getElementById("id_search_btn").click();
    }, 400);
})
