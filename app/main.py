from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# from fastapi_utils.tasks import repeat_every
from fastapi.staticfiles import StaticFiles
from app.routers.admin import api as admin
from fastapi.staticfiles import StaticFiles
import os
app = FastAPI(
    title="DailyVeg API Portal",
    description="APIs for DailyVeg",
    version="1.0.0",
    # docs_url=None,
    redoc_url=None,
)

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



app.include_router(admin.router)


app.mount(
    "/app/uploads/images/vegetables",
    StaticFiles(directory=os.path.join("app", "uploads", "images", "vegetables")),
    name="vegetable_images"
)

app.mount(
    "/static/info",
    StaticFiles(directory=os.path.join("app", "static", "info")),
    name="info_static"
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    error = exc.errors()[0]
    loc = error.get("loc", [])
    
    # Safe extraction of the field name
    if len(loc) >= 2:
        field = str(loc[1])
    elif len(loc) == 1:
        field = str(loc[0])
    else:
        field = "unknown"

    message = error.get("msg", "Invalid input")
    detail = f"{field} - {message.capitalize()}"

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder({"detail": detail}),
    )
