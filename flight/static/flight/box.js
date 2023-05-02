let weights = document.querySelectorAll("td.field-weight input");
let consumptions = document.querySelectorAll("td.field-consumption input");
let totalConsumption = document.getElementById('total_consumption')
let totalBoxWeight = document.getElementById('id_weight')
let pricePerKg = document.getElementById('id_price')
let consumption = document.getElementById('id_consumption')

window.addEventListener('DOMContentLoaded', () =>  {
    getTotalWeight();
    getTotalConsumption();
    getTotalPrice();
});

function getTotalWeight () {
    let total_weight = 0
    weights.forEach(weight => {
        if (weight.value) {
            total_weight += parseFloat(weight.value);
            document.getElementById('total_weight').value = total_weight;
        }
    });
}

function getTotalConsumption () {
    let total_consumption = 0
    consumptions.forEach(consumption => {
        if (consumption.value) {
            total_consumption += parseFloat(consumption.value);
            document.getElementById('total_consumption').value = total_consumption;
            getTotalPrice();
        }
    });
}

function getTotalPrice () {
    let total = 0
    if (!consumption.value) {
        total = parseFloat(totalBoxWeight.value) * parseFloat(pricePerKg.value) - parseFloat(totalConsumption.value)
    } else {
        total = parseFloat(totalBoxWeight.value) * parseFloat(pricePerKg.value) - parseFloat(consumption.value) - parseFloat(totalConsumption.value)
    }
    document.getElementById('id_sum').value = total;
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

totalBoxWeight.addEventListener('input', () => {
    getTotalPrice();
})

pricePerKg.addEventListener('input', () => {
    getTotalPrice();
})

consumption.addEventListener('input', () => {
    getTotalPrice();
})
