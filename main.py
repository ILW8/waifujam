# Requires: `starlette`, `uvicorn`, `jinja2`
# Run with `uvicorn example:app`
import datetime
import json
import signal

from redis import asyncio as aioredis
from broadcaster import Broadcast
from fastapi import FastAPI, WebSocket
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from pydantic import BaseModel, BaseSettings
import asyncio
from uvicorn.main import Server
from fastapi.middleware.cors import CORSMiddleware


def prefixed_key(f):
    """
    A method decorator that prefixes return values.

    Prefixes any string that the decorated method `f` returns with the value of
    the `prefix` attribute on the owner object `self`.
    """

    def prefixed_method(*args, **kwargs):
        self = args[0]
        key = f(*args, **kwargs)
        return f'{self.prefix}:{key}'

    return prefixed_method


class Keys:
    """Methods to generate key names for Redis data structures."""

    def __init__(self, prefix: str = "DEFAULT_KEY_PREFIX"):
        self.prefix = prefix

    @prefixed_key
    def twitch_session_token_key(self) -> str:
        """A time series containing 30-second snapshots of BTC price."""
        return f'twitch:session:token'

    @prefixed_key
    def state_key(self) -> str:
        """A time series containing 30-second snapshots of BTC price."""
        return f'state'


class Config(BaseSettings):
    # The default URL expects the app to run using Docker and docker-compose.
    redis_url: str = 'redis://localhost:6379'


config = Config()
redis = aioredis.from_url(config.redis_url, decode_responses=True)


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
    signal.signal(signal.SIGINT, stop_server)

    # add broadcaster connect/disconnect
    print(f"[{datetime.datetime.now().isoformat()}] Connecting to broadcast backend...")
    await broadcast.connect()
    print(f"[{datetime.datetime.now().isoformat()}] Connected.")
    yield

    print(f"[{datetime.datetime.now().isoformat()}] Disconnecting...")
    await broadcast.disconnect()
    print(f"[{datetime.datetime.now().isoformat()}] Disconnected.")


origins = [
    "http://localhost",
    "http://localhost:8080",
    "http://127.0.0.1:8080",
]

# app = FastAPI()
app = FastAPI(lifespan=lifespan)
app.add_middleware(CORSMiddleware,
                   allow_origins=origins,
                   allow_credentials=True,
                   allow_methods=["*"],
                   allow_headers=["*"], )
running = True
broadcast = Broadcast("redis://127.0.0.1:6379")

original_handler = Server.handle_exit


def handle_exit(*args, **kwargs):
    global running
    running = False
    original_handler(*args, **kwargs)


def stop_server(*_):
    global running
    running = False


Server.handle_exit = handle_exit


@app.get("/")
async def get():
    return JSONResponse({"message": "hi, this is probably not what you're looking for"}, status_code=404)


async def check_identity(twitch_token: str) -> str | None:
    keys = Keys("waifujam")
    twitch_token = f"{keys.twitch_session_token_key()}:{twitch_token}"

    try:
        token_data = json.loads(await redis.get(twitch_token))
    except TypeError:  # redis.get -> None
        return None

    print(token_data['username'])
    return ""


@app.post("/vote")
async def vote_endpoint(vote: Vote):
    print(vote)
    voter = await check_identity(vote.twitch_session_token)
    if voter is None:
        return JSONResponse({"error": "Could not find valid Twitch session"}, status_code=401)
    return vote


@app.get("/stages")
async def get_stages():
    return STAGE_MAPPINGS


@app.get("/state")
async def get_current_state():
    keys = Keys("waifujam")

    try:
        state = json.loads(await redis.get(keys.state_key()))
    except TypeError:  # redis.get -> None
        return JSONResponse({"error": "server does not have an active state, please try again later"}, status_code=503)

    return state


@app.websocket("/ws")
async def ws_connect_handler(websocket: WebSocket):
    await websocket.accept()
    await ws_sender(websocket)


async def ws_sender(websocket):
    async with broadcast.subscribe(channel="waifujam") as subscriber:
        # async for event in subscriber:
        #     await websocket.send_text(event.message)
        while running:  # to allow for clean shutdown
            try:
                event = await asyncio.wait_for(subscriber.get(), timeout=2)
                await websocket.send_text(event.message)
            except asyncio.TimeoutError:
                pass
