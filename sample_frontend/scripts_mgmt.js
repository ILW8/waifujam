let rounds;
let maps;
let socket;
let state;

const ENDPOINT_BASE = "waifujam.btmc.live"
const API_ENDPOINT = `https://${ENDPOINT_BASE}/`
const WEBSOCKET_ENDPOINT = `wss://${ENDPOINT_BASE}/ws`

const setStageButton = document.getElementById('setStage');
const stageInput = document.getElementById('stage-input')
const matchInput = document.getElementById('match-input')
// const voteStatusInput = document.getElementById("match-state");
const voteStateWinner = document.getElementById("vote-state-has-winner");
const voteStateShowcaseLeft = document.getElementById("vote-state-showcase-left");
const voteStateShowcaseRight = document.getElementById("vote-state-showcase-right");
const voteStateActive = document.getElementById("vote-state-voting-active");
const stageVisibility = document.getElementById('currentVisibility')
const hideRoundButton = document.getElementById("hideRound");
const showRoundButton = document.getElementById("showRound");
const roundsEditorSelect = document.getElementById("rounds-select");
const roundsEditorContainer = document.getElementById("editor-container");
const roundsEditorSubmitBtn = document.getElementById("submit-round");

const pauseVideoButton = document.getElementById("pause-video-btn");
const startVideoButton = document.getElementById("start-video-btn");

const volumeInput = document.getElementById("volume-input");
const changeVolumeButton = document.getElementById("change-volume");

const voteOverrideLeft = document.getElementById("vote-override-left");
const voteOverrideRight = document.getElementById("vote-override-right");
const voteOverrideButton = document.getElementById("vote-override-button");
// const matchEditorMapLeft = document.getElementById("match-map-left");
// const matchEditorMapRight = document.getElementById("match-map-right");

// https://btmc.live/wjoverlays/pauseVideos
// https://btmc.live/wjoverlays/startVideos
// https://btmc.live/wjoverlays/changeVolume {volume: <0-1>}
// https://btmc.live/wjoverlays/setVoting {left: Number, right: Number}

// volumeInput.addEventListener('input', () => {
//     console.log(volumeInput.value);
// })

voteOverrideButton.addEventListener('click', () => {
    fetch("https://btmc.live/wjoverlays/setVoting", {
        method: "POST",
        mode: "cors",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({left: parseInt(voteOverrideLeft.value), right: parseInt(voteOverrideRight.value)})
    }).then(() => {
    })
})

pauseVideoButton.addEventListener('click', () => {
    fetch("https://btmc.live/wjoverlays/pauseVideos", {
        method: "POST",
        mode: "cors",
    }).then(() => {
    })
})

startVideoButton.addEventListener('click', () => {
    fetch("https://btmc.live/wjoverlays/startVideos", {
        method: "POST",
        mode: "cors",
    }).then(() => {
    })
})

changeVolumeButton.addEventListener('click', () => {
    const newValue = parseInt(volumeInput.value);
    console.log(`Changing volume to ${newValue}%`);
    fetch("https://btmc.live/wjoverlays/changeVolume", {
        method: "POST",
        mode: "cors",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({volume: newValue / 100})
    }).then(() => {
    })
})


function removeOptionsFromOthers(event) {
    // console.log(event.target);
    console.log(event.target.dataset.prev);
    let prevStillInUse = false;
    roundsEditorContainer.querySelectorAll("select")
        .forEach(selectElem => {
            // if (selectElem === event.target) return;
            //
            // const a = Array.prototype.filter.call(event.target.querySelectorAll("option"), node => {
            //     return node.value === event.target.dataset.prev;
            // })
            // console.log(a.length);
            //
            // // don't remove the ---- option
            // if (selectElem.value === "-1") return;

            // check if prev still in use
            if (selectElem.value === event.target.dataset.prev) {
                prevStillInUse = true;
            }

            // add * to new selected option
            for (let i = 0; i < selectElem.length; i++) {
                if (selectElem.options[i].value === event.target.value) {
                    // console.log(`removing ${selectElem.options[i].text}`)
                    // selectElem.remove(i);
                    selectElem.options[i].text = selectElem.options[i].text.replace(/ \*$/, '') + " *";
                    break;
                }
            }
        })

    if (!prevStillInUse) {
        roundsEditorContainer.querySelectorAll("select").forEach(selectElem => {
            for (let i = 0; i < selectElem.length; i++) {
                if (selectElem.options[i].value === event.target.dataset.prev) {
                    // console.log(`removing ${selectElem.options[i].text}`)
                    // selectElem.remove(i);
                    selectElem.options[i].text = selectElem.options[i].text.replace(/ \*$/, '');
                    return;
                }
            }
        })
    }

    event.target.dataset.prev = event.target.value;
}


// the order things are being loaded should guarantee that we have rounds information
roundsEditorSelect.addEventListener('change', () => {
    roundsEditorContainer.replaceChildren();

    if (roundsEditorSelect.value === "0") {
        return;
    }

    const matchesCount = 8 / Math.pow(2, roundsEditorSelect.value - 1)
    for (let matchIndex = 0; matchIndex < matchesCount; matchIndex++) {
        const roundEditorTemplate = document.getElementById("round-edit-template");

        // console.log(rounds);

        let mapLeft, mapRight;
        if (matchIndex < rounds[roundsEditorSelect.value].matches.length) {
            [mapLeft, mapRight] = rounds[roundsEditorSelect.value].matches[matchIndex];
        }
        // console.log(mapLeft, mapRight);

        const clone = roundEditorTemplate.content.cloneNode(true);
        clone.querySelectorAll("select").forEach(selectElem => {
            selectElem.addEventListener('change', removeOptionsFromOthers);
        })
        clone.querySelectorAll("span")[0].innerText = matchIndex
        let selectLeft, selectRight;
        [selectLeft, selectRight] = clone.querySelectorAll("select");

        selectLeft.id = selectLeft.id + matchIndex;
        selectRight.id = selectRight.id + matchIndex;
        roundsEditorContainer.appendChild(clone);


        Object.keys(maps).forEach(mapId => {
            mapId = parseInt(mapId);
            let opt = document.createElement('option');
            opt.value = mapId.toString();
            opt.innerHTML = `${mapId} - ${maps[mapId].title}`;
            selectLeft.appendChild(opt);
            if (mapId === mapLeft) {
                selectLeft.value = mapId;
            }

            opt = opt.cloneNode(true);
            selectRight.appendChild(opt);
            if (mapId === mapRight) {
                selectRight.value = mapId;
            }
        })
    }

    roundsEditorContainer.querySelectorAll("select").forEach(selectElem => {
        selectElem.dispatchEvent(new Event("change"));
    })
})

roundsEditorSubmitBtn.addEventListener('click', () => {
    // {
    // 	"matches": [[1,2], [2,2]]
    // }
    let roundsData = {
        "matches": []
    };
    let selects = roundsEditorContainer.querySelectorAll("select");
    for (let i = 0; i < selects.length; i += 2) {
        const leftSelect = selects[i];
        const rightSelect = selects[i + 1];
        roundsData.matches.push([leftSelect.value, rightSelect.value])
    }

    fetch(API_ENDPOINT + "round/" + roundsEditorSelect.value, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify(roundsData),
        mode: "cors",
        credentials: "include"
    }).then(resp => resp.json()).then(() => {
    });
})

hideRoundButton.addEventListener('click', () => {
    doSetState(`${state.split(":")[0]}:-1:${state.split(":")[2]}`)
})

stageInput.addEventListener('change', () => {
    const isValid = stageInput.checkValidity()
    stageInput.style.boxShadow = isValid ? "0px 0px 0px red" : "0px 0px 5px red";  // eh.
    stageInput.style.border = isValid ? '1px solid black' : '1px solid red';

    if (isValid) {
        matchInput.max = 8 / Math.pow(2, stageInput.value - 1) - 1
        if (matchInput.value > matchInput.max) {
            matchInput.value = 0;
        }
    }
})


function doSetState(newState) {
    fetch(API_ENDPOINT + "state", {
        method: "POST",
        body: JSON.stringify({new_state: newState}),
        headers: {
            "Content-Type": "application/json",
            // 'Content-Type': 'application/x-www-form-urlencoded',
        },
        mode: "cors",
        credentials: "include"
    }).then(resp => resp.json()).then(data => {
        console.log("Set new state: " + JSON.stringify(data))
        if (data["new_state"].split(":").length === 3) {  // is this really necessary...
            stageVisibility.innerText = data["new_state"].split(":")[1] === "-1" ? "hidden" : data["new_state"];
        }
        state = data["new_state"];
        roundsEditorSelect.value = data["new_state"].split(":")[0];
        roundsEditorSelect.dispatchEvent(new Event('change'));
    })
}

function setStage() {
    // console.log(stageInput.value);

    //voteStatusInput.value

    if (voteStateShowcaseLeft.checked && voteStateShowcaseRight.checked) {
        document.getElementById("vote-state-validation-error").style.display = 'block';
        document.getElementById("vote-state-validation-error").innerText = "Cannot have both left and right showcase active at the same time";
        return;
    }

    if (voteStateActive.checked && voteStateWinner.checked) {
        document.getElementById("vote-state-validation-error").style.display = 'block';
        document.getElementById("vote-state-validation-error").innerText = "cannot have winner decided and voting active at the same time";
        return;
    }

    let newVoteStatus = 0;
    newVoteStatus += voteStateActive.checked;
    newVoteStatus += voteStateShowcaseRight.checked << 1;
    newVoteStatus += voteStateShowcaseLeft.checked << 2;
    newVoteStatus += voteStateWinner.checked << 3;
    // console.log(newVoteStatus);
    document.getElementById("vote-state-validation-error").style.display = 'none';

    doSetState(`${stageInput.value}:${matchInput.value}:${newVoteStatus}`);
}

setStageButton.addEventListener('click', setStage)

function loadMeta() {
    return Promise.all([loadRounds(), loadMaps()]).then(() => {
        // console.log("all loaded: ");
        // console.log(maps);
        // console.log(rounds)
        //
        // console.log("loading state: ");
        return loadState();
    })
}


function loadRounds() {
    return fetch(API_ENDPOINT + "rounds")
        .then(resp => resp.json())
        .then(data => {
            rounds = data
            // console.log(Object.keys(rounds))
            stageInput.max = Math.max(...Object.keys(rounds).map(x => parseInt(x)))
            stageInput.min = Math.min(...Object.keys(rounds).map(x => parseInt(x)))
            // console.log(rounds)
        })
}


function loadState() {
    fetch(API_ENDPOINT + "state")
        .then(resp => {
            if (resp.ok) {
                return resp.json()
            }
            return resp.text().then(text => {
                throw new Error(text)
            })
        })
        .then(data => {

            // visibility
            if (data["state"].split(":").length !== 3) {
                console.log("expected `:`-separated numbers, got: " + data["state"]);
                return;
            }
            // console.log(`state: ${data["state"]}`)
            state = data["state"];
            let round, match, status;
            [round, match, status] = state.split(":")
            stageVisibility.innerText = match === "-1" ? "hidden" : state;

            // stage select
            stageInput.value = round;
            stageInput.dispatchEvent(new Event('change'));
            matchInput.value = match;
            matchInput.dispatchEvent(new Event('change'));

            // visibility select  ((deprecated))
            // voteStatusInput.value = status;
            // voteStatusInput.dispatchEvent(new Event("change"));

            // visibility status:
            status = parseInt(status);
            voteStateWinner.checked = (status & 0x8) > 0;
            voteStateShowcaseLeft.checked = (status & 0x4) > 0;
            voteStateShowcaseRight.checked = (status & 0x2) > 0;
            voteStateActive.checked = (status & 0x1) > 0;

            // rounds editor
            roundsEditorSelect.value = round;
            roundsEditorSelect.dispatchEvent(new Event('change'));
        }).catch(error => {
        console.log("something wrong: " + error)
    })
}


function loadMaps() {
    return fetch(API_ENDPOINT + "maps")
        .then(resp => resp.json())
        .then(data => {
            // console.log("maps:")
            // console.log(data);
            maps = data;
        })
}

function initSocket() {
    socket = new ReconnectingWebSocket(WEBSOCKET_ENDPOINT)
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
}

loadMeta().then(() => {
    initSocket();
})

