let destination  = document.getElementById('id_destination');
let track_codes = document.querySelectorAll("td.field-track_code input");
let prices = document.querySelectorAll("td.field-price input");
let weights = document.querySelectorAll("td.field-weight input");
let costsUSD = document.querySelectorAll("td.field-cost_usd input");

window.addEventListener('DOMContentLoaded', () =>  {
    getTotalWeight();
    getTotalCost();
});

function setAllPrice () {
    for (let i = 0; i < track_codes.length; i++) {
        const track_code = document.getElementById(`id_base_parcel-${i}-track_code`);
        if (track_code?.value) {
            let regex = /[+-]?\d+(\.\d+)?/g;
            let price = destination.options[destination.selectedIndex].text;
            price = price.match(regex).map(function(p) { return parseFloat(p); });
            document.getElementById(`id_base_parcel-${i}-price`).value = price[0].toFixed(2);
            let weight = document.getElementById(`id_base_parcel-${i}-weight`).value;
            document.getElementById(`id_base_parcel-${i}-cost_usd`).value = (price * weight).toFixed(2);
        }
    }
    getTotalCost();
}

function setCodes () {
    const track_code = document.getElementById(`id_track_code`);
    if (track_code.value) {
        setCode(track_code.value);
    } else {
        getTrackCode();
    }
}

function setCode (track_code) {
    const a= {
        "Ё":"YO","Й":"I","Ц":"TS","У":"U","К":"K","Е":"E","Н":"N","Г":"G","Ш":"SH","Щ":"SCH","З":"Z","Х":"H","Ъ":"",
        "ё":"yo","й":"i","ц":"ts","у":"u","к":"k","е":"e","н":"n","г":"g","ш":"sh","щ":"sch","з":"z","х":"h","ъ":"",
        "Ф":"F","Ы":"I","В":"V","А":"a","П":"P","Р":"R","О":"O","Л":"L","Д":"D","Ж":"ZH","Э":"E","ф":"f","ы":"i",
        "в":"v","а":"a","п":"p","р":"r","о":"o","л":"l","д":"d","ж":"zh","э":"e","Я":"Ya","Ч":"CH","С":"S","М":"M",
        "И":"I","Т":"T","Ь":"","Б":"B","Ю":"YU","я":"ya","ч":"ch","с":"s","м":"m","и":"i","т":"t","ь":"","б":"b","ю":"yu"
    };
    let point = destination.options[destination.selectedIndex].text;
    point = point.split('').map(function (char) { return a[char] || char; }).join("");
    document.getElementById(`id_code`).value = point.slice(0, 3).toUpperCase() + track_code;
}

function getTrackCode () {
    fetch(window.location.origin + '/flight/' + 'track_code/', {
        method: 'GET',
        headers: {
            'Accept': 'application/json',
        },
    })
        .then(response => response.json())
        .then(response => {
            document.getElementById('id_track_code').value = response['code'];
            setCode(response['code']);
        });
}

function setPrice (track_code) {
    const id = track_code.id;
    let number = id.replace(/[^0-9]/g,"");
    let regex = /[+-]?\d+(\.\d+)?/g;
    let price = destination.options[destination.selectedIndex].text;
    price = price.match(regex).map(function(p) { return parseFloat(p); });
    document.getElementById(`id_base_parcel-${number}-price`).value = price[0].toFixed(2);
}

function getCostPerParcel (weight) {
    let costPerParcel = 0
    const id = weight.id
    let number = id.replace(/[^0-9]/g,"");
    const price = document.getElementById(`id_base_parcel-${number}-price`);
    costPerParcel = price.value * weight.value
    document.getElementById(`id_base_parcel-${number}-cost_usd`).value = costPerParcel.toFixed(2)
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
    costsUSD.forEach(cost_usd => {
        if (cost_usd.value) {
            totalCost += parseFloat(cost_usd.value);
            document.getElementById('total_cost').value = totalCost.toFixed(2);
        }
    });
}

destination.addEventListener('change', () => {
    setAllPrice();
    setCodes();
})

track_codes.forEach(track_code => {
    track_code.addEventListener('input', (event) => {
        document.getElementById('save').disabled = true;
        timeoutId = setTimeout(function() {
            const id = track_code.id
            let number = id.replace(/[^0-9]/g,"");
            const clientCode = document.getElementById(`id_base_parcel-${number}-client_code`);
            clientCode.focus()
        }, 400);
        setPrice(track_code);
    })
});

weights.forEach(weight => {
    weight.addEventListener('input', () => {
        getCostPerParcel(weight);
        getTotalWeight();
        getTotalCost();
    })
});

costsUSD.forEach(cost_usd => {
    cost_usd.addEventListener('input', () => {
        getTotalCost();
    })
});
