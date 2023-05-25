# Requires: `starlette`, `uvicorn`, `jinja2`
# Run with `uvicorn example:app`
import datetime
import json
import os
import random
import signal
import urllib.parse
from typing import Annotated, Optional

from redis import asyncio as aioredis
from broadcaster import Broadcast

from fastapi import FastAPI, WebSocket, Depends, BackgroundTasks, Cookie, Body
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import UniqueConstraint, Column
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql import expression
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.types import DateTime

from sqlmodel import Field, Session, SQLModel, create_engine, select

from contextlib import asynccontextmanager
from pydantic import BaseModel, BaseSettings
import asyncio
from uvicorn.main import Server

from dotenv import load_dotenv
from websockets.exceptions import ConnectionClosedOK

load_dotenv()

# ======== constants ========


REDIS_ADDR = 'redis://127.0.0.1:6379'
PUBSUB_CHANNEL = "waifujam"
PUB_MIN_INTERVAL = 2
SQLALCHEMY_DATABASE_URL = f'mysql+pymysql://{os.getenv("USERNAME")}:{os.getenv("PASSWORD")}' \
                          f'@{os.getenv("HOST")}/{os.getenv("DATABASE")}?charset=utf8mb4&ssl=true'
print(SQLALCHEMY_DATABASE_URL)
CORS_ORIGINS = [
    "http://localhost",
    "http://localhost:8080",
    "http://127.0.0.1:8080",
]
MAPS_META = {
    0: {
        "title": "soft whisper",
        "videos": {
            0: "https://example.com/v0s0",
            1: "https://example.com/v0s0",
            2: "https://example.com/v0s2"
        }
    },
    1: {
        "title": "somber rain",
        "videos": {
            0: "https://example.com/v1s0",
            1: "https://example.com/v1s1",
            2: "https://example.com/v1s2"
        }
    },
    2: {
        "title": "vibrant hill",
        "videos": {
            0: "https://example.com/v2s0",
            1: "https://example.com/v2s1",
            2: "https://example.com/v2s2"
        }
    },
}
STAGE_MAPPINGS = {
    0: {"section": 0, "maps": [0, 1]},
    1: {"section": 0, "maps": [2, 3]},
    2: {"section": 1, "maps": [0, 1]},
    3: {"section": 1, "maps": [2, 3]},
    4: {"section": 2, "maps": [0, 1]},
    5: {"section": 2, "maps": [2, 3]},
    6: {"section": 3, "maps": [0, 1]},
    7: {"section": 3, "maps": [2, 3]},
    8: {"section": 3, "maps": [2, 3]},
    9: {"section": 3, "maps": [2, 3]},
    10: {"section": 3, "maps": [2, 3]},
}


# noinspection PyPep8Naming
class utcnow(expression.FunctionElement):
    type = DateTime()


@compiles(utcnow, 'mysql')
def mysql_utcnow(element, compiler, **kw):
    return "GETUTCDATE()"


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
        """
        prefix which should be followed by a stage id
        used for storing set of twitch user_ids that have voted in a certain stage
        """
        return f'votes:'

    @prefixed_key
    def last_time_publish(self) -> str:
        return f'pub_ts'


class RedisConfig(BaseSettings):
    # The default URL expects the app to run using Docker and docker-compose.
    redis_url: str = REDIS_ADDR


class VoteRequest(BaseModel):  # comes in with a request
    vote: int = Field(ge=0, le=1)  # 0 or 1 (left or right)
    stage: int  # to index into the predefined mapping


class TwitchSessionData(BaseModel):
    sample = {
        'cookie': {
            'originalMaxAge': None,
            'expires': None,
            'httpOnly': True,
            'path': '/'
        },
        'passport': {  # dict['passport']['user']['data'][0]['id']
            'user': {
                'data': [
                    {
                        'id': '1234567890',
                        'login': 'abcdefgh',
                        'display_name': 'AbcdEfgh',
                        'type': '',
                        'broadcaster_type': '',
                        'description': "hello world",
                        'profile_image_url': 'https://static-cdn.jtvnw.net/jtv_user_pictures/'
                                             'xxxxxxxxxxxxxxxxx.png',
                        'offline_image_url': '',
                        'view_count': 0,
                        'email': 'xxxxxxxxxxxxxxxxx@example.com',
                        'created_at': '1970-01-01T07:27:27Z'
                    }
                ],
                'accessToken': 'xxxxxxxxxxxxxxxxx',
                'refreshToken': 'xxxxxxxxxxxxxxxxx'}
        }
    }


class Vote(SQLModel, table=True):  # model of data stored in db
    __table_args__ = (UniqueConstraint("twitch_user_id", "stage", name="one_vote_per_stage_per_user"),)

    id: Optional[int] = Field(default=None, primary_key=True)
    twitch_user_id: int = Field(index=True)
    stage: int = Field(index=True)
    vote: int
    datetime: 'Optional[datetime.datetime]' = Field(
        sa_column=Column(DateTime(timezone=False), server_default=utcnow())
    )


@asynccontextmanager
async def lifespan(_: FastAPI):
    # add signal handler for shutdown
    signal.signal(signal.SIGINT, stop_server)

    # create databases
    create_db_and_tables()

    # add broadcaster connect/disconnect
    print(f"[{datetime.datetime.now().isoformat()}] Connecting to broadcast backend...")
    await broadcast.connect()
    print(f"[{datetime.datetime.now().isoformat()}] Connected.")
    yield

    print(f"[{datetime.datetime.now().isoformat()}] Disconnecting...")
    await broadcast.disconnect()
    print(f"[{datetime.datetime.now().isoformat()}] Disconnected.")


running = True
broadcast = Broadcast(REDIS_ADDR)
config = RedisConfig()
redis = aioredis.from_url(config.redis_url, decode_responses=True)
engine = create_engine(SQLALCHEMY_DATABASE_URL,
                       echo=True,  # todo: remove this for prod
                       connect_args={
                           "ssl": {
                               "ca":
                                   "/etc/ssl/certs/ca-certificates.crt" if os.path.exists(
                                       "/etc/ssl/certs/ca-certificates.crt")
                                   else "/etc/ssl/cert.pem"
                           }
                       })


# ======= dependencies =========


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def waifu_jam_keys():
    return Keys("waifujam")


def get_session():
    with Session(engine) as session:
        yield session


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


# ======== utilities ========


async def update_redis_votes(vote: Vote, keys: Keys):
    await asyncio.gather(
        redis.sadd(f"{keys.live_votes_key()}:{vote.stage}", vote.twitch_user_id),
        redis.hincrby(keys.live_votes_key(), f"{vote.stage}:{vote.vote}", 1),
        # redis.publish(PUBSUB_CHANNEL, f'votes|{await redis.hget(keys.live_votes_key(), f"{vote.stage}:0")}'
        #                               f'|{await redis.hget(keys.live_votes_key(), f"{vote.stage}:1")}')
    )
    do_not_publish = await redis.get(keys.last_time_publish())
    if do_not_publish is not None:
        return
    votes = await redis.hgetall(keys.live_votes_key())
    left, right = votes.get(f"{vote.stage}:0", 0), votes.get(f"{vote.stage}:1", 0)
    # print("publishing")
    await broadcast.publish(PUBSUB_CHANNEL, f'updatevotes|{left}|{right}')
    await redis.set(keys.last_time_publish(), "", ex=PUB_MIN_INTERVAL)  # set empty value, only cares about expiry

    # print()


# ======== app ========

# app = FastAPI()
app = FastAPI(lifespan=lifespan)
app.add_middleware(CORSMiddleware,
                   allow_origins=CORS_ORIGINS,
                   allow_credentials=True,
                   allow_methods=["*"],
                   allow_headers=["*"], )


# ======== routes ========

@app.get("/")
async def get():
    return JSONResponse({"message": "hi, this is probably not what you're looking for"}, status_code=404)


# noinspection PyUnreachableCode
async def check_identity(session_string: str, keys: Keys) -> dict | None:
    # @app.post("/")
    # async def handle_post(request: Request):
    #     print(request.headers)
    #     print(await request.body())
    #     the_thing = request.cookies.get("_btmcache")
    #     if the_thing is not None:
    #         print(urllib.parse.unquote(the_thing))
    session_string = urllib.parse.unquote(session_string)
    print(session_string)
    try:
        print(f"{(session_string := session_string.split(':')[1].split('.')[0])=}")
    except IndexError:  # session_string invalid
        return None
    session_key_redis = f"sess:{session_string}"
    print(session_key_redis)

    # todo: for debug, remove this
    return {"username": "notreallyaJame", "userid": random.randint(0, 1024)}

    try:
        twitch_session_data = json.loads(await redis.get(twitch_token))
    except TypeError:  # redis.get -> None causes TypeError when calling json.loads
        return None

    try:
        print(twitch_session_data['passport']['user']['data'][0]['id'])
    except KeyError:
        return None
    return twitch_session_data


@app.post("/vote")
async def vote_endpoint(vote: VoteRequest,
                        keys: WaifuJamKeysDep,
                        background_tasks: BackgroundTasks,
                        session: Session = Depends(get_session),
                        session_string: Annotated[str | None, Cookie(alias="_btmcache")] = None,
                        gusdigfsduaioagguweriuveurg: bool = False):
    # bypass checks, TODO: REMOVE THIS!!!!!!!!!!!!!!!
    if gusdigfsduaioagguweriuveurg:
        await redis.hincrby(keys.live_votes_key(), f"{vote.stage}:{vote.vote}", 1),

        do_not_publish = await redis.get(keys.last_time_publish())
        if do_not_publish is not None:
            return vote
        votes = await redis.hgetall(keys.live_votes_key())
        left, right = votes.get(f"{vote.stage}:0", 0), votes.get(f"{vote.stage}:1", 0)
        # print("publishing")
        await broadcast.publish(PUBSUB_CHANNEL, f'updatevotes|{left}|{right}')
        await redis.set(keys.last_time_publish(), "", ex=PUB_MIN_INTERVAL)  # set empty value, only cares about expiry
        return vote

    if session_string is None:
        return JSONResponse({"error": "Missing session cookie"}, status_code=400)
    voter = await check_identity(session_string, keys)
    if voter is None:
        return JSONResponse({"error": "Could not find valid Twitch session"}, status_code=401)

    state = await redis.get(keys.state_key())
    if state is None:
        return JSONResponse({"error": "server does not have an active state, please try again later"}, status_code=503)
    if str(vote.stage) != state:  # str() because redis values are always strings
        return JSONResponse({"error": f"currently active stage is {state}, tried voting for {vote.stage}"},
                            status_code=400)

    already_voted_resp = JSONResponse({"error": f"You have already voted for stage {state}"}, status_code=409)
    if await redis.sismember(f"{keys.votes_key_prefix()}{state}", voter["username"]):
        return already_voted_resp

    # insert into db, fail if vote already exists
    db_vote = Vote(twitch_user_id=voter["userid"], stage=vote.stage, vote=vote.vote)
    session.add(db_vote)
    try:
        session.commit()
        session.refresh(db_vote)
    except IntegrityError as e:
        session.rollback()
        if "AlreadyExists" in str(e):  # dunno if ugly hack
            res = session.exec(select(Vote).where(Vote.twitch_user_id == db_vote.twitch_user_id,
                                                  Vote.stage == db_vote.stage)).first()
            if res is not None:  # vote on this stage by this user already exists
                return JSONResponse({"error": f"twitch user {res.twitch_user_id} has already voted "
                                              f"in stage {res.stage}"}, status_code=409)

        # otherwise, different integrity error
        return JSONResponse({"error": "IntegrityError"}, status_code=500)
    background_tasks.add_task(update_redis_votes, db_vote, keys)
    return vote


@app.get("/stages")
async def get_stages():
    return STAGE_MAPPINGS


@app.get("/state")
async def get_current_state(keys: WaifuJamKeysDep):
    state = await redis.get(keys.state_key())
    if state is None:
        return JSONResponse({"error": "server does not have an active state, please try again later"}, status_code=503)
    state = int(state)

    return JSONResponse({"state": state})


@app.post("/state")
async def get_current_state(new_state: Annotated[int, Body(embed=True)], keys: WaifuJamKeysDep):
    state = await update_state(new_state, keys)
    return JSONResponse({"new_state": state})


async def update_state(new_state: int, keys: Keys):
    await redis.set(keys.state_key(), new_state)
    await broadcast.publish(PUBSUB_CHANNEL, f'newstate|{new_state}')
    return int(await redis.get(keys.state_key()))


@app.get("/votes")
async def get_current_votes(keys: WaifuJamKeysDep, force: bool = False, stage: int = None):
    if not force:
        all_keys = await redis.hgetall(keys.live_votes_key())
        if stage is None:
            print(all_keys)
            return JSONResponse(all_keys)

        return JSONResponse({
            f"{stage}:0": all_keys.get(f"{stage}:0", "0"),
            f"{stage}:1": all_keys.get(f"{stage}:1", "0")
        })


@app.get("/maps")
async def get_maps():
    return JSONResponse(MAPS_META)


@app.websocket("/ws")
async def ws_connect_handler(websocket: WebSocket):
    await websocket.accept()
    await ws_sender(websocket)


async def ws_sender(websocket):
    async with broadcast.subscribe(channel=PUBSUB_CHANNEL) as subscriber:
        while running:  # to allow for clean shutdown
            try:
                event = await asyncio.wait_for(subscriber.get(), timeout=2)
                await websocket.send_text(event.message)
            except asyncio.TimeoutError:
                pass
            except ConnectionClosedOK:
                pass
