let flightCode = document.getElementById('id_code');
let flights = document.querySelectorAll("td.field-swap select");

window.addEventListener('DOMContentLoaded', () =>  {
    setFlightCode();
});

function setFlightCode () {
    flights.forEach(flight => {
        for (let i = 0; i < flight.options.length; i++) {
            if (flight.options[i].text !== '---------' && (flight.options[i].text === flightCode.value)) {
                flight.options.selectedIndex = i;
            }
        }
    });
}
