let stages;
let socket;

const setStageButton = document.getElementById('setStage');
const stageInput = document.getElementById('stage-input')
const matchInput = document.getElementById('match-input')
const stageVisibility = document.getElementById('currentVisibility')
const hideRoundButton = document.getElementById("hideRound");
const showRoundButton = document.getElementById("showRound");

hideRoundButton.addEventListener('click', () => { doSetState(-1) })

stageInput.addEventListener('change', () => {
    const isValid = stageInput.checkValidity()
    stageInput.style.boxShadow = isValid ? "0px 0px 0px red" : "0px 0px 5px red";
    stageInput.style.border    = isValid ? '1px solid black' : '1px solid red';
})



function doSetState(newState) {
    fetch("http://127.0.0.1:8000/state", {
        method: "POST",
        body: JSON.stringify({new_state: newState}),
            headers: {
      "Content-Type": "application/json",
      // 'Content-Type': 'application/x-www-form-urlencoded',
    },
    }).then(resp => resp.json()).then(data => {
        console.log("Set new state: " + JSON.stringify(data))
        stageVisibility.innerText = data["new_state"] === -1 ? "hidden" : data["new_state"];
    })
}

function setStage() {
    console.log(stageInput.value);
    doSetState(`${stageInput.value}:${matchInput.value}`);
}

setStageButton.addEventListener('click', setStage)

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

fetch("http://127.0.0.1:8000/state")
    .then(resp => {
        if (resp.ok) {
            return resp.json()
        }
        return resp.text().then(text => {throw new Error(text)})
    })
    .then(data => {
        stageVisibility.innerText = data["state"] === -1 ? "hidden" : "visible";
    }).catch(error => {
        console.log("something wrong: " + error)
})

