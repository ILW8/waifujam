let stages;
let socket;
let state;

fetch("http://127.0.0.1:8000/stages")
    .then(resp => resp.json())
    .then(data => {
        stages = data
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
            if (data.split("|").length <= 1) {
                return
            }
            let op = data.split("|")[0];
            console.log(data.split("|"))
            switch (op) {
                case "newstate":
                    state = parseInt(data.split("|")[1]);
                    updateState(state);
                    break;
            }
        };
    })


const voteLeftButton = document.getElementById("vote-left");
const voteRightButton = document.getElementById("vote-right");
const votesCountRight = document.getElementById("votes-right");

voteLeftButton.addEventListener('click', () => {
    console.log("left")
})
voteRightButton.addEventListener('click', () => {
    console.log("right");
    votesCountRight.dataset.newval = (parseInt(votesCountRight.innerText) + 10).toString()
    animateCountUp(votesCountRight)
    sendVote(voteRightButton, 1)
})

function sendVote(vote) {
    voteLeftButton.disabled = true
    voteRightButton.disabled = true
    fetch("http://127.0.0.1:8000/vote", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            "stage": ""
        })
    }).then(resp => {
        if (resp.ok) {
            return resp.json()
        }
        return resp.text().then(text => {
            throw new Error(text)
        })
    }).then(data => {
        console.log(data);
    }).catch(err => {
        console.log(err)
        voteLeftButton.disabled = false
        voteRightButton.disabled = false
    })
}

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
    doSetState(stageInput.value);
}


function updateState(newState) {
    if (newState === -1) {
        voteLeftButton.disabled = true;
        voteRightButton.disabled = true;
        return;
    }
    voteLeftButton.disabled = false;
    voteRightButton.disabled = false;
}


fetch("http://127.0.0.1:8000/state")
    .then(resp => {
        if (resp.ok) {
            return resp.json()
        }
        return resp.text().then(text => {
            throw new Error(text)
        })
    })
    .then(data => {
        console.log("data from GET /state:");
        console.log(data)
        state = data["state"];
        updateState(state);
    }).catch(error => {
    console.log("something wrong: " + error)
})

