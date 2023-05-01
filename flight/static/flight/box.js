let weights = document.querySelectorAll("td.field-weight input");
let consumptions = document.querySelectorAll("td.field-consumption input");

window.addEventListener('DOMContentLoaded', () =>  {
    getTotalWeight();
    getTotalConsumption();
});

function getTotalWeight () {
    let total_weight = 0
    weights.forEach(weight => {
        if (weight.value) {
            total_weight += parseFloat(weight.value);
            document.getElementById('total_weight').value= total_weight;
        }
    });
}

function getTotalConsumption () {
    let total_consumption = 0
    consumptions.forEach(consumption => {
        if (consumption.value) {
            total_consumption += parseFloat(consumption.value);
            document.getElementById('total_consumption').value= total_consumption;
        }
    });
}

weights.forEach(weight => {
    weight.addEventListener('input', () => {
        getTotalWeight();
    })
});

consumptions.forEach(consumption => {
    consumption.addEventListener('input', () => {
        getTotalConsumption();
    })
});
