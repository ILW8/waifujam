# Requires: `starlette`, `uvicorn`, `jinja2`
# Run with `uvicorn example:app`
import datetime
import json
import signal
from typing import Annotated

from redis import asyncio as aioredis
from broadcaster import Broadcast
from fastapi import FastAPI, WebSocket, Depends
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from pydantic import BaseModel, BaseSettings
import asyncio
from uvicorn.main import Server
from fastapi.middleware.cors import CORSMiddleware


class Keys:
    """Methods to generate key names for Redis data structures."""

    @staticmethod
    def prefixed_key(f):
        def prefixed_method(*args, **kwargs):
            self = args[0]
            key = f(*args, **kwargs)
            return f'{self.prefix}:{key}'

        return prefixed_method

    def __init__(self, prefix: str = "DEFAULT_KEY_PREFIX"):
        self.prefix = prefix

    @prefixed_key
    def twitch_session_token_key_prefix(self) -> str:
        """Users who log in using twitch will have their account information stored in keys prefixed with this"""
        return f'twitch:session:token'

    @prefixed_key
    def state_key(self) -> str:
        """
        The current state of voting.
        A value of -1 means voting isn't enabled at the moment.
        """
        return f'state'

    @prefixed_key
    def live_votes_key(self) -> str:
        """An eventually consistent count of live votes"""
        return f'votes:live'

    @prefixed_key
    def votes_key_prefix(self) -> str:
        """prefix which should be followed by a stage id"""
        return f'votes:'


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


def waifu_jam_keys():
    return Keys("waifujam")


WaifuJamKeysDep = Annotated[Keys, Depends(waifu_jam_keys)]

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


async def check_identity(twitch_token: str, keys: WaifuJamKeysDep) -> dict | None:
    twitch_token = f"{keys.twitch_session_token_key_prefix()}:{twitch_token}"

    try:
        token_data = json.loads(await redis.get(twitch_token))
    except TypeError:  # redis.get -> None
        return None

    print(token_data['username'])
    return token_data


@app.post("/vote")
async def vote_endpoint(vote: Vote, keys: WaifuJamKeysDep):
    voter = await check_identity(vote.twitch_session_token)
    if voter is None:
        return JSONResponse({"error": "Could not find valid Twitch session"}, status_code=401)
    state = await redis.get(keys.state_key())
    if await redis.sismember(f"{keys.votes_key_prefix()}{state}", voter["username"]):
        return JSONResponse({"error": f"You have already voted for stage {state}"}, status_code=409)
    return vote


@app.get("/stages")
async def get_stages():
    return STAGE_MAPPINGS


@app.get("/state")
async def get_current_state(keys: WaifuJamKeysDep):
    state = await redis.get(keys.state_key())
    if state is None:
        return JSONResponse({"error": "server does not have an active state, please try again later"}, status_code=503)

    return state


@app.websocket("/ws")
async def ws_connect_handler(websocket: WebSocket):
    await websocket.accept()
    await ws_sender(websocket)


async def ws_sender(websocket):
    async with broadcast.subscribe(channel="waifujam") as subscriber:
        while running:  # to allow for clean shutdown
            try:
                event = await asyncio.wait_for(subscriber.get(), timeout=2)
                await websocket.send_text(event.message)
            except asyncio.TimeoutError:
                pass
