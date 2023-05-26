# waifujam

## RUNNING (dev environment)
- run a redis instance locally on port 6379
- fill in the `.env` file with (use MySQL/MariaDB, otherwise datetimes might not be stored properly):
    ```yaml
    HOST=xxxxxxxxxxxxxxxxx
    USERNAME=yyyyyyyyyyyyy
    PASSWORD=zzzzzzzzzzzzz
    DATABASE=zxczxczcxzxcz
    ```
- install dependencies: `python3 -m pip install -r requirements.txt`
- install deps (part 2): you may need to install a SQL connector (i.e. `sudo apt update && sudo apt install python3-pymysql`)
- start api server using `python3 -m uvicorn main:app --reload` (development)
- when voting in a test environment, add query parameter `gusdigfsduaioagguweriuveurg=true` to bypass credentials check

## what
horizontally scalable backend for vote gathering and websocket publishing

## how
fastapi asgi + uvicorn workers across one or more nodes
redis for caching and pub/sub
