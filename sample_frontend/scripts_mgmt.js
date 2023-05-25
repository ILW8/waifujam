let stages;
let socket;

const setStageButton = document.getElementById('setStage');
const stageInput = document.getElementById('stage-input')

stageInput.addEventListener('change', () => {
    const isValid = stageInput.checkValidity()
    stageInput.style.boxShadow = isValid ? "0px 0px 0px red" : "0px 0px 5px red";
    stageInput.style.border    = isValid ? '1px solid black' : '1px solid red';
})

function a() {
    console.log(stageInput.value);
    fetch("http://127.0.0.1:8000/state", {
        method: "POST",
        body: JSON.stringify({new_state: stageInput.value}),
            headers: {
      "Content-Type": "application/json",
      // 'Content-Type': 'application/x-www-form-urlencoded',
    },
    }).then(resp => resp.json()).then(data => {
        console.log("Set new state: " + JSON.stringify(data))
    })
}

setStageButton.addEventListener('click', a)

fetch("http://127.0.0.1:8000/stages")
    .then(resp => resp.json())
    .then(data => {
        stages = data
        console.log(Object.keys(stages))
        stageInput.max = Math.max(...Object.keys(stages).map(x => parseInt(x)))
        stageInput.min = Math.min(...Object.keys(stages).map(x => parseInt(x)))
        console.log(stages)
        socket = new ReconnectingWebSocket('ws://localhost:8000/ws')
        socket.onopen = () => {
            console.log('Successfully Connected');
        };

        socket.onclose = event => {
            console.log('Socket Closed Connection: ', event);
            socket.send('Client Closed!');
        };

        socket.onerror = error => {
            console.log('Socket Error: ', error);
        };

        socket.onmessage = event => {
            let data = event.data;
            console.log(data);

        };
    })

