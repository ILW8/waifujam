let stages;
let socket;
let state;

fetch("https://waifujam.btmc.live/stages")
    .then(resp => resp.json())
    .then(data => {
        stages = data
        console.log(stages)
        socket = new ReconnectingWebSocket('wss://waifujam.btmc.live/ws')
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
            let args = data.split("|").slice(1)
            console.log(data.split("|"))
            switch (op) {
                case "newstate":
                    state = parseInt(data.split("|")[1]);
                    updateState(state);
                    getVotes();
                    break;
                case "updatevotes":
                    if (args.length !== 2) return;

                    votesCountRight.dataset.newval = args[1].toString();
                    animateCountUp(votesCountRight);
                    votesCountLeft.dataset.newval = args[0].toString();
                    animateCountUp(votesCountLeft);

            }
        };
    })


const voteLeftButton = document.getElementById("vote-left");
const voteRightButton = document.getElementById("vote-right");
const votesCountRight = document.getElementById("votes-right");
const votesCountLeft = document.getElementById("votes-left");
const currentStageDisplay = document.getElementById("stage-number");

voteLeftButton.addEventListener('click', () => {
    sendVote(0)
})
voteRightButton.addEventListener('click', () => {
    sendVote(1)
})

function sendVote(vote) {
    // todo: uncomment these
    // voteLeftButton.disabled = true
    // voteRightButton.disabled = true
    fetch("https://waifujam.btmc.live/vote?" + new URLSearchParams({gusdigfsduaioagguweriuveurg: 'true'}), {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            "stage": 3,
            "vote": vote,
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


function updateState(newState) {
    if (newState === -1) {
        voteLeftButton.disabled = true;
        voteRightButton.disabled = true;
        return;
    }
    voteLeftButton.disabled = false;
    voteRightButton.disabled = false;
    currentStageDisplay.innerText = newState;
}


fetch("https://waifujam.btmc.live/state")
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


function getVotes() {
    fetch("https://waifujam.btmc.live/votes?stage=" + state)
        .then(resp => resp.json())
        .then(data => {
            votesCountLeft.dataset.newval = data["" + state + ":0"];
            votesCountRight.dataset.newval = data["" + state + ":1"];
            animateCountUp(votesCountLeft);
            animateCountUp(votesCountRight);
        });
}
