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
from websockets.exceptions import ConnectionClosedOK, ConnectionClosedError

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

MAPS_META = {
    0: {'title': 'appropriate especially',
        'videos': {0: '1f918f3beb0fb97f9f8c48f5b722430b30ba9395',
                   1: '9c9f99cfd39ae53f695f5df4383606a4bed8cc03',
                   2: '0107843954c3fd26864613f878040678bfa88acd',
                   3: 'b7cd58cdb366cd2775fa660a6984c9efd0452114',
                   4: 'fb07d3bc5f535c13f0559de4731e75c6e31d7b91'}},
    1: {'title': 'regular flower',
        'videos': {0: '2dff360641e775651e9551be6a84fc3215715bab',
                   1: '6ef39985086984df6cc10d9af369f7037d704f59',
                   2: '7b93b40b46d4716dbee36ff54784e3d6c771f4a4',
                   3: '1c7a96aafc6e9556ef91e013245c92e0d5c619a3',
                   4: '0de65aab8af75def98c63ac873e6278458a87341'}},
    2: {'title': 'distance fellow',
        'videos': {0: '35675e246a1751cbe8994c6b13128872765636e1',
                   1: 'a8bcab0682e3b051e840764c4c388fa7fb7f33de',
                   2: 'ba70f39ccd947c82b0d93265f4b1889f64f90d34',
                   3: '3b7752695c51d07db3156f312941f74789ecd0dc',
                   4: '9b35bac2e03025fd5be72de10ae8384a4232ef4a'}},
    3: {'title': 'busy continued',
        'videos': {0: 'cafd5f3535a5f99925841e516f0fb0cf80127f78',
                   1: '4c2f7138b6db303d6f1be9097b1d6b169682772d',
                   2: '94b8d0603b4ea1eeaeb7d9d27379781238f08cfb',
                   3: 'b39c15d09989392c9feab9c432dee6b4fb22b2b9',
                   4: 'fe42685e6bb3f34173865884447a29240c0e2361'}},
    4: {'title': 'tear rainbow',
        'videos': {0: 'a631a4bd26cfe454e7318ccadbf32d4c3ff6123e',
                   1: '4f00444098ac1e7d5a1d571c64af8a5b1e90e28e',
                   2: '9daf3ec8be9f5b471e1febc406466d17bf0ba39c',
                   3: 'cfc2828d90cfabb9e53a25b222d9b6ab6e87c68f',
                   4: 'a694a20bc098c07d07741ba77dba78722eb36cb5'}},
    5: {'title': 'under balloon',
        'videos': {0: '2c52dd973baff430c09ae1d054d84eec8bbce0b5',
                   1: '4385f37ceeff0dcf172068fc3255021424f93274',
                   2: '689e1a3c7c947e3c4873109b7cea99998546bc3c',
                   3: 'b439ec1de54228d985ec8399cf0a7a6fd15bfa73',
                   4: '444cfc0cab7aaa53cc3cbcc34a7bd272bef62ada'}},
    6: {'title': 'round cloud',
        'videos': {0: 'd7b6c905d7871801413a2e1d2be7ddb3d8aea6f0',
                   1: 'a61fcac9cd603e92eeeb261ea4a05af7b5b145a4',
                   2: '5a259dc671e1688f689dd447f1a3b538383034be',
                   3: 'a8f50345c62cee37328562042f7e6df0058864de',
                   4: '3e1d9025c3903cc63dcac72389bef05f4709ef3c'}},
    7: {'title': 'summer fifteen',
        'videos': {0: '2bd274e66108107c5ad121f188715be6dd9bbacd',
                   1: '408b897163d38822c2019b07a14b6560c7efa3ac',
                   2: 'd7bfc319d00ef9045bf9a968056a8919f41a3f28',
                   3: '860b4bab4960322c11a67a2e392c1e633dd15c46',
                   4: 'abb933553c0a3c2e0556b2f438c6b8616ad080e3'}},
    8: {'title': 'star hamster',
        'videos': {0: '754f173d0aa4b59af9cfef03c77327b609bf1f40',
                   1: '69319e99dc0817beb64b3d531f8f81486d500338',
                   2: '89c34027ae8a84a14679f70027209956e83d49b8',
                   3: 'ed0e3ba93db96af2ed9437709bb7e7b582bdc4fe',
                   4: 'af3b24fd4a641302e7a125534e4beadb5c5f0d33'}},
    9: {'title': 'bent does',
        'videos': {0: 'eb8d6f34385cb75174e2edfae8b238d188975d26',
                   1: '30f6009f9c2c05741e42ef94d9d41fc8ba0e5756',
                   2: 'a190860598b29836edfd2fbeb610841a5ff384c3',
                   3: '3239566b9fbb64ff11eef69638f6101471142812',
                   4: '720497f930d8f597d64bd74239d8cb248454d1a7'}},
    10: {'title': 'grandmother fighting',
         'videos': {0: '579bd91db493f1153bb6742743d860c1eb318bb7',
                    1: 'a35b10b8d6e6b44cb7fa706b7fa90c98eb1e0b83',
                    2: '32f6f755795d00dcc6332b019a13fcd52f9d340c',
                    3: 'f903210e483b3d0f5d1f5afcdc52764d4cd50145',
                    4: 'b116235c0a079ca57b4b0da149531ad66b108307'}},
    11: {'title': 'quiet forest',
         'videos': {0: '6ed4fba46cb89fbaf141932fd03f1460279b310c',
                    1: '0090499bc2768512fa9aab5016e56999fb094a73',
                    2: 'b2e6b4cc8174cac4b7147a803d93f5394e306a37',
                    3: 'a1ae6cda163d972bcaca25cc60457381609e7db4',
                    4: 'e535e0099260abe7c87add91ef02231ddc91b219'}},
    12: {'title': 'clear watercress',
         'videos': {0: '2ed288b1c739693b4f8c10ef261af15a1e7bc8ad',
                    1: 'edddadd8e006c37bb5d33d4f169473b2f0c17f52',
                    2: 'f39b78cf0bb26c3aa956c236d796c6db7611b915',
                    3: 'f3620871fc17b157370181342317c30f2fd21e35',
                    4: '443f9c85b862d18dff5165880f2f081490ac8ae2'}},
    13: {'title': 'pine touch',
         'videos': {0: '6121d64cc81dc6f6df809032b26febd696b15521',
                    1: 'c3706313903e2b6667687dacdc015bbc35616afd',
                    2: '6860141f96545e204d1124c0d6deaf192306c642',
                    3: 'a49a6aa1fedd8eabd81ddb72dbff22d6fc59236c',
                    4: '01fe6f5dc8d94474f78c3e9686e123e784d216ac'}},
    14: {'title': 'time article',
         'videos': {0: 'e542ad38dfd073f4f024c2dacc8d982545743a3a',
                    1: 'f046a07b65f84605967e33b1e9e3d5b0ad7857d7',
                    2: 'a111d7a76055af4aaf47e4b1d1db1dba99ffff1f',
                    3: '3af3b5cbb8e38d4bddaf270e0bd7d622b4573657',
                    4: '389dfc4e9e342682fa503888a3beef1e36742f1f'}},
    15: {'title': 'pressure hurt',
         'videos': {0: '0bf781112b0326a997116a3aba2f06ffece7b4fe',
                    1: '2908ab90f1a9e04ae1b7b6b49c8d680e7fe39294',
                    2: '25e2aed6811ec9f21a4a5e87d094bc9e4116c266',
                    3: '51531e6728ebceedb3842c8b80a76e0c9e8cdb1a',
                    4: '2cc26bfbee46568c99c3ce0b5d2c0644010c84bd'}}
}

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
    state_round, state_match, _ = tuple(map(int, state.split(":")))
    if vote.round != state_round or vote.match != state_match:
        return JSONResponse({"error": f"currently active round:stage is {state_round}:{state_match}, "
                                      f"tried voting for {vote.round}:{vote.match}"},
                            status_code=400)

    already_voted_resp = JSONResponse({"error": f"You have already voted for stage {state}"}, status_code=409)
    if await redis.sismember(f"{keys.votes_key_prefix()}:{vote.round}:{vote.match}", voter["id"]):
        return already_voted_resp

    # insert into db, fail if vote already exists
    db_vote = Vote(twitch_user_id=voter["id"], round=vote.round, match=vote.match, vote=vote.vote)
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
                return JSONResponse({"error": f"twitch user {res.twitch_user_id} ({voter.get('display_name', 'N/A')}) "
                                              f"has already voted in stage {res.round}:{res.match}"}, status_code=409)

        # otherwise, different integrity error
        return JSONResponse({"error": "Unexpected IntegrityError"}, status_code=500)
    background_tasks.add_task(update_redis_votes, db_vote, keys)
    return vote


# @app.get("/stages")
# async def get_stages():
#     return STAGE_MAPPINGS


@app.get("/state")
async def get_current_state(keys: WaifuJamKeysDep,
                            session_string: Annotated[str | None, Cookie(alias="_btmcache")] = None):

    state = await redis.get(keys.state_key())
    if state is None:
        return JSONResponse({"error": "server does not have an active state, please try again later"}, status_code=503)

    has_voted = False
    if session_string is not None:
        voter = await check_identity(session_string)
        if await redis.sismember(f"{keys.votes_key_prefix()}:{state.split(':')[0]}:{state.split(':')[1]}", voter["id"]):
            has_voted = True

    resp_obj = {
        "state": state,
        "aux_data": await get_aux_state_data(state, keys),
        "hasProbablyVoted": has_voted
    }
    return JSONResponse(resp_obj)


@app.post("/state")
async def set_current_state(new_state: Annotated[str, Body(embed=True, regex=r"^\d+:-?\d+:\d+$")],
                            keys: WaifuJamKeysDep,
                            background_tasks: BackgroundTasks,
                            _: Annotated[str, Depends(get_current_username)]):
    state = await update_state(new_state, keys, background_tasks)
    return JSONResponse({"new_state": state})


async def get_aux_state_data(state: str, keys: Keys):
    if int(state_round := state.split(":")[0]) == 0:
        return
    state_match_id = int(state.split(":")[1])
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
            "currentVideo": MAPS_META[meta_index_left]["videos"][int(state_round) - 1],
            "votes": votes.get(f"{state_round}:{state_match_id}:0", 0)
        }
        state_aux_data["right"] = {
            "title": MAPS_META[meta_index_right]["title"],
            "currentVideo": MAPS_META[meta_index_right]["videos"][int(state_round) - 1],
            "votes": votes.get(f"{state_round}:{state_match_id}:1", 0)
        }
    except IndexError:
        pass

    return state_aux_data


async def send_new_state_with_data(new_state: str, keys: Keys):
    state_aux_data = await get_aux_state_data(new_state, keys)
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


@app.post("/reload_cached_votes")
async def reload_cached_votes(keys: WaifuJamKeysDep, _: Annotated[str, Depends(get_current_username)]):
    # delete all keys starting with keys.votes_key_prefix()
    count = 0
    async for key in redis.scan_iter(f"{keys.votes_key_prefix()}*"):
        await redis.delete(key)
        count += 1

    return JSONResponse({"deleted": count})


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
            except ConnectionClosedError:
                pass
