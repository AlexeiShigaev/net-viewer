import uvicorn
from fastapi import FastAPI
from starlette.staticfiles import StaticFiles
from app.snmp.router_snmp import router as router_snmp
from app.settings import STATIC_DIR
from app.client.router_web_client import router as router_web_client
from app.auth.router_auth import router as router_auth
from app.core.router_core import router as router_core


def app_loader():
    app = FastAPI()

    app.mount("/static/", StaticFiles(directory=STATIC_DIR), name="static")

    app.include_router(router_auth)
    app.include_router(router_snmp)
    app.include_router(router_web_client)
    app.include_router(router_core)

    return app


if __name__ == "__main__":
    uvicorn.run(
        "app.__main__:app_loader",
        host="0.0.0.0", port=8008,
        reload=True, factory=True
    )
