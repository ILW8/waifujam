// paste your api v1 token into data/apiv1token.txt
let apiV1Token = ""

fetch("data/apiv1token.txt").then(async response => {
    apiV1Token = await response.text();
    console.log(apiV1Token);

    populatePlayers();
})



const playersDataJson = 'data/players.json'

// noinspection HttpUrlsUsage
const baseUrl = `http://${window.location.host}`
const corsProxyBaseUrl = `http://localhost:8010/proxy`



const playersContainer = document.getElementById("player-container-left");
const playerTemplate = document.getElementById("player-template");

console.log(playersContainer);


function populatePlayers() {
    fetch(playersDataJson).then(response => response.json()).then(async data => {
    // console.log(data);
    for (const playerId of data) {
        console.log(playerId);
        const newNode = playerTemplate.content.cloneNode(true);

        try {
            let response = await fetch(
                `${corsProxyBaseUrl}/api/get_user?k=${apiV1Token}&u=${playerId}&type=id`
            )
            let playerData = await response.json();
            console.log(playerData);
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
