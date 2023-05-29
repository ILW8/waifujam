const playersDataJson = '/players.json'

// noinspection HttpUrlsUsage
const baseUrl = `http://${window.location.host}`
const url = `${baseUrl}${playersDataJson}`
const corsProxyBaseUrl = `http://localhost:8010/proxy`

// paste your api v1 token here, DO NOT SHARE THIS TOKEN WITH ANYONE ELSE AND REMOVE FROM CODE BEFORE SHARING CODE
const apiV1Token = "***REMOVED***"

const playersContainer = document.getElementById("player-container-left");
const playerTemplate = document.getElementById("player-template");

console.log(playersContainer);


fetch(url).then(response => response.json()).then(async data => {
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
