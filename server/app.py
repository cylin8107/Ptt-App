import uvicorn
import time

from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from pytz import timezone

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

# from az_redis.utils import get_redis
from routers import authentication, user, board, post
# from watch_dog import watch

# SECRET_KEY = os.getenv('JWT-SECRET-KEY')
# ALGORITHM = "HS256"

app = FastAPI()

origins = [
    'https://ptt-app.azurewebsites.net',
    'https://ptt-app-stage.azurewebsites.net',
    'https://ptt-app-prod.azurewebsites.net',
    'http://localhost',
    'http://localhost:8080',
    '*'
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(authentication.router)
app.include_router(user.router)
app.include_router(board.router)
app.include_router(post.router)


# @app.on_event("startup")
# async def startup_event():
#     scheduler = BackgroundScheduler()
#     scheduler.add_job(watch, 'interval', seconds=10)
#     scheduler.start()

@app.middleware("http")
async def middlewareOpencensus(request: Request, call_next):
    start_time = time.time()
    
    response = await call_next(request)

    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(round(process_time, 4))

    return response

@app.get('/')
def hello_word():
    return 'hello_word'

def get_time():

    time_format = '%Y-%m-%d %H:%M:%S'
    cur_time = datetime.now(timezone('Asia/Taipei'))

    return cur_time.strftime(time_format)


if __name__ == '__main__':

    uvicorn.run("app:app", host="0.0.0.0", port=5000, reload=True)