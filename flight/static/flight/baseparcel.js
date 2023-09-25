// const socket = new ReconnectingWebSocket("ws://" + window.location.host + "/ws/create_baseparcel/");
//
// socket.onmessage = (event) => {
//     console.log('1'.repeat(10), event)
//     const data = JSON.parse(event.data);
//     console.log('2'.repeat(10), data)
//     location.reload();
// };

let clientCodes = document.querySelectorAll("td.field-client_code input");
let phones = document.querySelectorAll("td.field-phone input");

clientCodes.forEach((clientCode, index) => {
    clientCode.addEventListener('input', () => {
        let clientCodeValue = clientCode.value
        if (clientCodeValue.length === 8 && clientCodeValue.slice(0, 3) === 'OSH') {
            fetch(window.location.origin + `/flight/phone/?search=${clientCodeValue}`, {
                method: 'GET',
                headers: {
                    'Accept': 'application/json',
                },
            })
                .then(response => response.json())
                .then(response => {
                    document.getElementById(`id_form-${index}-phone`).value = response['phone'];
                })
                .catch(error => {
                    alert(`${clientCodeValue} 缺少电话号码`)
                });
        } else if (clientCodeValue.length === 9 && clientCodeValue.slice(0, 4) === 'BISH') {
            fetch(window.location.origin + `/flight/phone/?search=${clientCodeValue}`, {
                method: 'GET',
                headers: {
                    'Accept': 'application/json',
                },
            })
                .then(response => response.json())
                .then(response => {
                    document.getElementById(`id_form-${index}-phone`).value = response['phone'];
                }).catch(error => {
                alert(`${clientCodeValue} 缺少电话号码`)
            });
        }
    })
});

phones.forEach((phone, index) => {
    phone.addEventListener('input', () => {
        let value = phone.value
        if (value.length === 1) {
            phone.value = "996" + value
        } else if (value === '996') {
            phone.value = ''
        }
        if (value.length === 12) {
            fetch(window.location.origin + `/flight/client_code/?search=${phone.value}`, {
                method: 'GET',
                headers: {
                    'Accept': 'application/json',
                },
            })
                .then(response => response.json())
                .then(response => {
                    document.getElementById(`id_form-${index}-client_code`).value = response['client_code'];
                }).catch(error => {
                alert(`${value} 缺少客户端代码`)
            });
        }
    })
});
