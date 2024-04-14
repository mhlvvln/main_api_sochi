import asyncio

from fastapi import FastAPI, HTTPException, Depends
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from applications.router import shops_router, application_router, users_router, recommendations_router
from database.database import init_models, get_session
from examples.router import examples_router

# from applications.router import user_dispatcher_router


app = FastAPI(title="Main API Server", description="API\n"
                                                   "Client id - 8: <span>eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6OCwicm9sZSI6ImNsaWVudCIsImV4cCI6NDMwNDk2Mzc2NH0.HN8m6BYHnVxYLrJsQO12zaPy_NAUY1ToU1hrLzk03uQ</span>"
                                                   "Controller id - 99: <span>eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6OTksInJvbGUiOiJjb250cm9sbGVyIiwiZXhwIjo0MzA0OTY3Mzg2fQ.RtClKup6ev3qkx5Fx_Hw4hgsmrIlFCJP_K1AXGqeBLw</span>")
app.include_router(examples_router, prefix="/example", tags=["Распарсенный ПДФ"])
app.include_router(shops_router, prefix="/shops", tags=["Магазины"])
app.include_router(application_router, prefix="/applications", tags=["Заявки"])
app.include_router(users_router, prefix="/users", tags=["Пользователи"])
app.include_router(recommendations_router, prefix="/recommendations", tags=["Рекомендации"])

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(HTTPException)
async def unicorn_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"status": False, "error": exc.detail},
    )


@app.on_event("startup")
async def startup():
    await init_models()