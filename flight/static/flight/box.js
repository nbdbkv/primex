let weights = document.querySelectorAll("td.field-weight input");
let costs = document.querySelectorAll("td.field-cost input");
let totalCost = document.getElementById('total_cost')
let consumption = document.getElementById('id_consumption')

window.addEventListener('DOMContentLoaded', () =>  {
    getTotalWeight();
    getTotalCost();
    getTotalPrice();
});

function getCostPerParcel (weight) {
    let costPerParcel = 0
    const id = weight.id
    let number = id.replace(/[^0-9]/g,"");
    const price = document.getElementById(`id_base_parcel-${number}-price`);
    costPerParcel = price.value * weight.value
    document.getElementById(`id_base_parcel-${number}-cost`).value = costPerParcel.toFixed(2)
}

function getTotalWeight () {
    let totalWeight = 0
    weights.forEach(weight => {
        if (weight.value) {
            totalWeight += parseFloat(weight.value);
            document.getElementById('total_weight').value = totalWeight.toFixed(3);
        }
    });
}

function getTotalCost () {
    let totalCost = 0
    costs.forEach(cost => {
        if (cost.value) {
            totalCost += parseFloat(cost.value);
            document.getElementById('total_cost').value = totalCost.toFixed(2);
            getTotalPrice();
        }
    });
}

function getTotalPrice () {
    let totalPrice= 0
    if (!consumption.value) {
        totalPrice = parseFloat(totalCost.value)
    } else {
        totalPrice = parseFloat(totalCost.value) - parseFloat(consumption.value)
    }
    document.getElementById('id_sum').value = totalPrice.toFixed(2);
}

weights.forEach(weight => {
    weight.addEventListener('input', () => {
        getCostPerParcel(weight);
        getTotalWeight();
        getTotalCost();
    })
});

costs.forEach(cost => {
    cost.addEventListener('input', () => {
        getTotalCost();
    })
});

consumption.addEventListener('input', () => {
    getTotalPrice();
})
