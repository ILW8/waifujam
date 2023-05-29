// paste your api v1 token into data/apiv1token.txt, NOT HERE
let apiV1Token = ""
const playersDataJson = 'data/players.json'
const corsProxyBaseUrl = `http://localhost:8010/proxy`

fetch("data/apiv1token.txt").then(async response => {
    apiV1Token = await response.text();
    if (apiV1Token.length < 5) {
        console.error("osu API token is invalid, please paste a valid api v1 token in data/apiv1token.txt")
        return;
    }
    populatePlayers();
})


const playersContainer = document.getElementById("player-container-left");
const playerTemplate = document.getElementById("player-template");


function playerClickHandler(event) {
    console.log(`Clicked ${event.target.parentElement.id}`)
}


function populatePlayers() {
    fetch(playersDataJson).then(response => response.json()).then(async data => {
    for (const index in data) {
        const playerId = data[index];
        // console.log(playerId);
        const newNode = playerTemplate.content.cloneNode(true);
        newNode.querySelector("div").id = `${index}-${playerId}`
        newNode.querySelector("img").addEventListener('click', playerClickHandler);

        try {
            let response = await fetch(
                `${corsProxyBaseUrl}/api/get_user?k=${apiV1Token}&u=${playerId}&type=id`
            )
            let playerData = await response.json();
            // console.log(playerData);
            newNode.querySelectorAll("span")[0].innerText = playerData[0].username;
            newNode.querySelectorAll("span")[1].innerText = `Rank #${playerData[0].pp_rank}`;

        } catch (e) {
            console.log(`Failed getting data for user ${playerId}`)
            console.log(e);
        }
        newNode.querySelectorAll("img")[0].src = `https://s.ppy.sh/a/${playerId}`;
        playersContainer.appendChild(newNode);
    }
})
}
