# Requires: `starlette`, `uvicorn`, `jinja2`
# Run with `uvicorn example:app`
import asyncio
import datetime
import signal
from functools import partial

from broadcaster import Broadcast
from fastapi import FastAPI, WebSocket, Response
from contextlib import asynccontextmanager
from pydantic import BaseModel
from uvicorn.server import HANDLED_SIGNALS
from fastapi.websockets import WebSocketDisconnect


class Vote(BaseModel):
    twitch_session_token: str
    vote: int  # 0 or 1 (left or right
    stage: int  # to index into the predefined mapping


STAGE_MAPPINGS = {
    0: {"section": 0, "maps": [0, 1]},
    1: {"section": 0, "maps": [2, 3]},
    2: {"section": 1, "maps": [0, 1]},
    3: {"section": 1, "maps": [2, 3]},
    4: {"section": 2, "maps": [0, 1]},
    5: {"section": 2, "maps": [2, 3]},
    6: {"section": 3, "maps": [0, 1]},
    7: {"section": 3, "maps": [2, 3]},
}

@asynccontextmanager
async def lifespan(_: FastAPI):
    # add signal handler for shutdown

    # loop = asyncio.get_running_loop()
    # # disclaimer 1: this is a private attribute: might change without notice.
    # # Also: unix only, won't work on windows
    # signal_handlers = getattr(loop, "_signal_handlers", {})
    #
    # for sig in HANDLED_SIGNALS:
    #     loop.add_signal_handler(sig, partial(handle_exit, signal_handlers.get(sig, None)), sig, None)

    signal.signal(signal.SIGINT, stop_server)

    # add broadcaster connect/disconnect
    print(f"[{datetime.datetime.now().isoformat()}] Connecting to broadcast backend...")
    await broadcast.connect()
    print(f"[{datetime.datetime.now().isoformat()}] Connected.")
    yield

    print(f"[{datetime.datetime.now().isoformat()}] Disconnecting...")
    await broadcast.disconnect()
    print(f"[{datetime.datetime.now().isoformat()}] Disconnected.")


# app = FastAPI()
app = FastAPI(lifespan=lifespan)
running = True
broadcast = Broadcast("redis://127.0.0.1:6379")


def stop_server(*_):
    global running
    running = False


# def handle_exit(original_handler, sig, _):
#     global running
#     running = False
#     print("running = False", sig)
#     if original_handler:
#         # disclaimer 2: this should be opaque and performed only by the running loop.
#         # not so bad: this is not changing, and is safe to do.
#         return original_handler._run()


@app.get("/")
async def get():
    return Response({"message": "hi, this is probably not what you're looking for"}, status_code=404)


@app.post("/vote")
async def vote_endpoint(vote: Vote):
    print(vote)
    return vote


@app.get("/stages")
async def get_stages():
    return {}


@app.get("/state")
async def get_current_state():
    return {}


@app.websocket("/ws")
async def ws_connect_handler(websocket: WebSocket):
    await websocket.accept()
    await ws_sender(websocket)


async def ws_sender(websocket):
    async with broadcast.subscribe(channel="waifujam") as subscriber:
        # async for event in subscriber:
        #     await websocket.send_text(event.message)
        while running:
            try:
                event = await asyncio.wait_for(subscriber.get(), timeout=1)
                await websocket.send_text(event.message)
            except asyncio.TimeoutError:
                # streaming is completed
                pass
