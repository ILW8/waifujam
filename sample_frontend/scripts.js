let socket = new ReconnectingWebSocket('ws://localhost:8000/ws');


const labelTagLeft = document.getElementById('vid-left-tag')
const videoTagLeft = document.getElementById('vid-left');
videoTagLeft.crossOrigin = "anonymous";
videoTagLeft.onloadstart = () => {
    labelTagLeft.innerText = videoTagLeft.src;
}

socket.onopen = () => {
    console.log('Successfully Connected');
};

socket.onclose = event => {
	console.log('Socket Closed Connection: ', event);
	socket.send('Client Closed!');
};

socket.onerror = error => { console.log('Socket Error: ', error); };

// PUBLISH waifujam updatevideo|left|https://btmc.ams3.cdn.digitaloceanspaces.com/video2.mp4
socket.onmessage = event => {
    let data = event.data;
    console.log(data);
    let splitData = data.split("|")  // opType | <rest of payload>
    if (splitData.length === 0) {
        return;
    }

    let opType = splitData[0];
    if (opType === 'updatevideo' && splitData.length === 3) {
        updateVideo(splitData[1], splitData[2])
    }
};


function updateVideo(side, url){
    switch (side) {
        case "left":
            videoTagLeft.src = url;
            break;
        default:
            return;
    }
}
