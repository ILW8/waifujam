# Requires: `starlette`, `uvicorn`, `jinja2`
# Run with `uvicorn example:app`
import datetime
import json
import os
import secrets
import signal
import urllib.parse
import uuid
from typing import Annotated, Optional

from fastapi.params import Path
from redis import asyncio as aioredis
from broadcaster import Broadcast

from fastapi import FastAPI, WebSocket, Depends, BackgroundTasks, Cookie, Body, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from sqlalchemy import UniqueConstraint, Column, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql import expression
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.types import DateTime

from sqlmodel import Field, Session, SQLModel, create_engine, select

from contextlib import asynccontextmanager
from pydantic import BaseModel, BaseSettings
import asyncio

from starlette import status
from starlette.requests import Request
from uvicorn.main import Server

from dotenv import load_dotenv
from websockets.exceptions import ConnectionClosedOK

load_dotenv()

# ======== constants ========


REDIS_ADDR = os.getenv("REDISCONNSTRING")
PUBSUB_CHANNEL = "waifujam"
PUB_MIN_INTERVAL = 1
SQLALCHEMY_DATABASE_URL = f'mysql+pymysql://{os.getenv("USERNAME")}:{os.getenv("PASSWORD")}' \
                          f'@{os.getenv("HOST")}/{os.getenv("DATABASE")}?charset=utf8mb4&ssl=true'
# print(SQLALCHEMY_DATABASE_URL)
CORS_ORIGINS = [
    "http://localhost",
    "http://localhost:8080",
    "http://127.0.0.1:8080",
    "https://btmc.live",
    "https://btmc.ams3.digitaloceanspaces.com",
    "https://btmc.ams3.cdn.digitaloceanspaces.com",
]

MAPS_META = {0: {'title': 'appropriate especially',
                 'videos': {0: 'https://example.com/v0s0',
                            1: 'https://example.com/v0s0',
                            2: 'https://example.com/v0s2'}},
             1: {'title': 'regular flower',
                 'videos': {0: 'https://example.com/v1s0',
                            1: 'https://example.com/v1s0',
                            2: 'https://example.com/v1s2'}},
             2: {'title': 'distance fellow',
                 'videos': {0: 'https://example.com/v2s0',
                            1: 'https://example.com/v2s0',
                            2: 'https://example.com/v2s2'}},
             3: {'title': 'busy continued',
                 'videos': {0: 'https://example.com/v3s0',
                            1: 'https://example.com/v3s0',
                            2: 'https://example.com/v3s2'}},
             4: {'title': 'tear rainbow',
                 'videos': {0: 'https://example.com/v4s0',
                            1: 'https://example.com/v4s0',
                            2: 'https://example.com/v4s2'}},
             5: {'title': 'under balloon',
                 'videos': {0: 'https://example.com/v5s0',
                            1: 'https://example.com/v5s0',
                            2: 'https://example.com/v5s2'}},
             6: {'title': 'round cloud',
                 'videos': {0: 'https://example.com/v6s0',
                            1: 'https://example.com/v6s0',
                            2: 'https://example.com/v6s2'}},
             7: {'title': 'summer fifteen',
                 'videos': {0: 'https://example.com/v7s0',
                            1: 'https://example.com/v7s0',
                            2: 'https://example.com/v7s2'}},
             8: {'title': 'star hamster',
                 'videos': {0: 'https://example.com/v8s0',
                            1: 'https://example.com/v8s0',
                            2: 'https://example.com/v8s2'}},
             9: {'title': 'bent does',
                 'videos': {0: 'https://example.com/v9s0',
                            1: 'https://example.com/v9s0',
                            2: 'https://example.com/v9s2'}},
             10: {'title': 'grandmother fighting',
                  'videos': {0: 'https://example.com/v10s0',
                             1: 'https://example.com/v10s0',
                             2: 'https://example.com/v10s2'}},
             11: {'title': 'quiet forest',
                  'videos': {0: 'https://example.com/v11s0',
                             1: 'https://example.com/v11s0',
                             2: 'https://example.com/v11s2'}},
             12: {'title': 'clear watercress',
                  'videos': {0: 'https://example.com/v12s0',
                             1: 'https://example.com/v12s0',
                             2: 'https://example.com/v12s2'}},
             13: {'title': 'pine touch',
                  'videos': {0: 'https://example.com/v13s0',
                             1: 'https://example.com/v13s0',
                             2: 'https://example.com/v13s2'}},
             14: {'title': 'time article',
                  'videos': {0: 'https://example.com/v14s0',
                             1: 'https://example.com/v14s0',
                             2: 'https://example.com/v14s2'}},
             15: {'title': 'pressure hurt',
                  'videos': {0: 'https://example.com/v15s0',
                             1: 'https://example.com/v15s0',
                             2: 'https://example.com/v15s2'}}}

ROUNDS_MAPPING_TEMPLATE = {
    0: {},  # intro
    1: {"matches": []},  # QF
    2: {"matches": []},  # SM
    3: {"matches": []},  # F
    4: {"matches": []},  # GF
}


# noinspection PyPep8Naming
class utcnow(expression.FunctionElement):
    type = DateTime()


@compiles(utcnow,
          'mysql')
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

    @prefixed_key
    def rounds(self) -> str:
        return f"rounds"


class RedisConfig(BaseSettings):
    # The default URL expects the app to run using Docker and docker-compose.
    redis_url: str = REDIS_ADDR


class VoteRequest(BaseModel):  # comes in with a request
    vote: int = Field(ge=0, le=1)  # 0 or 1 (left or right)
    round: int = Field(ge=1, le=4)
    match: int


class Vote(SQLModel, table=True):  # model of data stored in db
    __table_args__ = (UniqueConstraint("twitch_user_id", "round", "match", name="one_vote_per_stage_per_user"),)

    id: Optional[int] = Field(default=None, primary_key=True)
    twitch_user_id: int = Field(index=True)
    round: int = Field(index=True)
    match: int
    vote: int
    vote_time: 'Optional[datetime.datetime]' = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
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
    await broadcast.publish(str(uuid.uuid4()), "connectivity check")  # raises exception if no auth
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
                       # echo=True,
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
        redis.sadd(f"{keys.votes_key_prefix()}:{vote.round}:{vote.match}", vote.twitch_user_id),
        redis.hincrby(keys.live_votes_key(), f"{vote.round}:{vote.match}:{vote.vote}", 1),
        # redis.publish(PUBSUB_CHANNEL, f'votes|{await redis.hget(keys.live_votes_key(), f"{vote.stage}:0")}'
        #                               f'|{await redis.hget(keys.live_votes_key(), f"{vote.stage}:1")}')
    )
    do_not_publish = await redis.get(keys.last_time_publish())
    if do_not_publish is not None:
        return
    votes = await redis.hgetall(keys.live_votes_key())
    left, right = votes.get(f"{vote.round}:{vote.match}:0", 0), votes.get(f"{vote.round}:{vote.match}:1", 0)
    # print("publishing")
    await broadcast.publish(PUBSUB_CHANNEL, f'updatevotes|{left}|{right}')
    await redis.set(keys.last_time_publish(), "", ex=PUB_MIN_INTERVAL)  # set empty value, only cares about expiry

    # print()


# ======== app ========

# app = FastAPI()
app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBasic()


def get_current_username(
        credentials: Annotated[HTTPBasicCredentials, Depends(security)]
):
    current_username_bytes = credentials.username.encode("utf8")
    correct_username_bytes = b"British Toastmasters Club Jakarta"
    is_correct_username = secrets.compare_digest(
        current_username_bytes, correct_username_bytes
    )
    current_password_bytes = credentials.password.encode("utf8")
    correct_password_bytes = os.getenv("MANAGEMENT_PASSWORD", "wysi727").encode("utf8")
    is_correct_password = secrets.compare_digest(
        current_password_bytes, correct_password_bytes
    )
    if not (is_correct_username and is_correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


# ======== routes ========

@app.get("/")
async def get():
    return JSONResponse({"message": "hi, this is probably not what you're looking for"}, status_code=404)


# noinspection PyUnreachableCode
async def check_identity(session_string: str) -> dict | None:
    # @app.post("/")
    # async def handle_post(request: Request):
    #     print(request.headers)
    #     print(await request.body())
    #     the_thing = request.cookies.get("_btmcache")
    #     if the_thing is not None:
    #         print(urllib.parse.unquote(the_thing))
    session_string = urllib.parse.unquote(session_string)

    try:
        session_key_redis = f"sess:{session_string.split(':')[1].split('.')[0]}"
        twitch_session_data = json.loads(await redis.get(session_key_redis))
        return twitch_session_data['passport']['user']['data'][0]
    # IndexError: session_string invalid or twitch_session_data.passport.user.data is of length 0
    # TypeError:  redis.get -> None causes TypeError when calling json.loads
    # KeyError:   twitch_session_data doesn't contain .passport.user.data
    except (IndexError, TypeError, KeyError):
        return None


@app.get("/test")
async def test_endpoint(req: Request):
    print(req.cookies)
    print(req.headers)
    return JSONResponse({"c": req.cookies, "headers": req.headers})


@app.post("/vote")
async def vote_endpoint(vote: VoteRequest,
                        keys: WaifuJamKeysDep,
                        request: Request,
                        background_tasks: BackgroundTasks,
                        session: Session = Depends(get_session),
                        session_string: Annotated[str | None, Cookie(alias="_btmcache")] = None):
    # TODO: !!!!!!!!!!!!!!!!!!!!!!!!!! UPDATE THIS TO USE NEW STATE :-SEPARATED TRIPLET !!!!!!!!!!!!!!!!!!!!!!!!!!!!
    if session_string is None:
        return JSONResponse({"error": "Missing session cookie"}, status_code=400)
    voter = await check_identity(session_string)
    if voter is None:
        return JSONResponse({"error": "Could not find valid Twitch session"}, status_code=401)

    # return JSONResponse(voter)
    # return JSONResponse({"username": voter.get("display_name")})

    state = await redis.get(keys.state_key())
    if state is None:
        return JSONResponse({"error": "server does not have an active state, please try again later"}, status_code=503)
    state_round, state_match, _ = state.split(":")
    if vote.round != state_round or vote.match != state_match:
        return JSONResponse({"error": f"currently active round:stage is {state_round}:{state_match}, "
                                      f"tried voting for {vote.round}:{vote.match}"},
                            status_code=400)

    already_voted_resp = JSONResponse({"error": f"You have already voted for stage {state}"}, status_code=409)
    if await redis.sismember(f"{keys.votes_key_prefix()}{state}", voter["username"]):
        return already_voted_resp

    # insert into db, fail if vote already exists
    db_vote = Vote(twitch_user_id=voter["userid"], round=vote.round, vote=vote.vote)
    session.add(db_vote)
    try:
        session.commit()
        session.refresh(db_vote)
    except IntegrityError as e:
        session.rollback()
        if "AlreadyExists" in str(e):  # dunno if ugly hack
            res = session.exec(select(Vote).where(Vote.twitch_user_id == db_vote.twitch_user_id,
                                                  Vote.round == db_vote.round,
                                                  Vote.match == db_vote.match)).first()
            if res is not None:  # vote on this stage by this user already exists
                return JSONResponse({"error": f"twitch user {res.twitch_user_id} has already voted "
                                              f"in stage {res.round}:{res.match}"}, status_code=409)

        # otherwise, different integrity error
        return JSONResponse({"error": "IntegrityError"}, status_code=500)
    background_tasks.add_task(update_redis_votes, db_vote, keys)
    return vote


# @app.get("/stages")
# async def get_stages():
#     return STAGE_MAPPINGS


@app.get("/state")
async def get_current_state(keys: WaifuJamKeysDep):
    state = await redis.get(keys.state_key())
    if state is None:
        return JSONResponse({"error": "server does not have an active state, please try again later"}, status_code=503)

    return JSONResponse({"state": state})


@app.post("/state")
async def set_current_state(new_state: Annotated[str, Body(embed=True, regex=r"^\d+:-?\d+:\d+$")],
                            keys: WaifuJamKeysDep,
                            background_tasks: BackgroundTasks,
                            _: Annotated[str, Depends(get_current_username)]):
    state = await update_state(new_state, keys, background_tasks)
    return JSONResponse({"new_state": state})


async def send_new_state_with_data(new_state: str, keys: Keys):
    if int(state_round := new_state.split(":")[0]) == 0:
        return
    state_match_id = int(new_state.split(":")[1])
    try:
        round_matches = json.loads(await redis.hget(keys.rounds(), state_round))
    except TypeError:
        round_matches = []
    state_aux_data = {
        "left": None,
        "right": None,
    }

    try:
        meta_index_left = round_matches[state_match_id][0]
        meta_index_right = round_matches[state_match_id][1]

        votes = await redis.hgetall(keys.live_votes_key())

        # first set essential data
        state_aux_data["left"] = {
            "title": MAPS_META[meta_index_left]["title"],
            "currentVideo": MAPS_META[meta_index_left]["videos"][state_match_id],
            "votes": votes.get(f"{state_round}:{state_match_id}:0", 0)
        }
        state_aux_data["right"] = {
            "title": MAPS_META[meta_index_right]["title"],
            "currentVideo": MAPS_META[meta_index_right]["videos"][state_match_id],
            "votes": votes.get(f"{state_round}:{state_match_id}:1", 0)
        }
    except IndexError:
        pass

    await broadcast.publish(PUBSUB_CHANNEL, f'newstatewithdata|{new_state}|{json.dumps(state_aux_data)}')


async def update_state(new_state: str, keys: Keys, background_tasks: BackgroundTasks):
    await redis.set(keys.state_key(), new_state)
    await broadcast.publish(PUBSUB_CHANNEL, f'newstate|{new_state}')
    background_tasks.add_task(send_new_state_with_data, new_state, keys)
    return await redis.get(keys.state_key())


# @app.get("/votes")
# async def get_current_votes(keys: WaifuJamKeysDep, force: bool = False, stage: int = None):
#     if not force:
#         all_keys = await redis.hgetall(keys.live_votes_key())
#         if stage is None:
#             print(all_keys)
#             return JSONResponse(all_keys)
#
#         return JSONResponse({
#             f"{stage}:0": all_keys.get(f"{stage}:0", "0"),
#             f"{stage}:1": all_keys.get(f"{stage}:1", "0")
#         })


@app.get("/rounds")
async def get_rounds(keys: WaifuJamKeysDep):
    rounds = ROUNDS_MAPPING_TEMPLATE.copy()
    rounds_redis = await redis.hgetall(keys.rounds())
    for key, json_str in rounds_redis.items():
        rounds[int(key)] = {"matches": json.loads(json_str)}
    print(rounds)
    return JSONResponse(rounds)


@app.get("/round/{round_id}")
async def get_round(round_id: Annotated[int, Path(ge=0, le=len(ROUNDS_MAPPING_TEMPLATE))], keys: WaifuJamKeysDep):
    return JSONResponse(json.loads(await redis.hget(keys.rounds(), round_id)))


async def set_round(round_id: int, matches: list[tuple], keys: Keys):
    await redis.hset(keys.rounds(), round_id, json.dumps(matches))
    return await redis.hget(keys.rounds(), round_id)


@app.post("/round/{round_id}")
async def update_round(
        round_id: Annotated[int, Path(ge=1, le=len(ROUNDS_MAPPING_TEMPLATE))],
        matches: Annotated[list[tuple[int, int]], Body(embed=True)],
        keys: WaifuJamKeysDep,
        _: Annotated[str, Depends(get_current_username)]
):
    if len(matches) != 8 // (2 ** (round_id - 1)):
        # raise RequestValidationError()
        return JSONResponse(
            {"error": f"unexpected number of matches: {len(matches)}, expected: {8 // (2 ** (round_id - 1))}"},
            status_code=400)
    for match_id, match in enumerate(matches):
        if match[0] == match[1]:
            return JSONResponse(
                {"error": f"Cannot have a map face against itself (match {match_id}: {match[0]} vs {match[1]})"},
                status_code=400)
    # print(round_id)
    # print(matches)
    return JSONResponse(await set_round(round_id, matches, keys))


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
