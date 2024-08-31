from fastapi import APIRouter, Depends

from app.auth.auth import get_current_user
from app.auth.schemas import UserData4Auth
from app.core.models import Device

router = APIRouter(prefix="/core", tags=["Core functionality API"])


@router.post("/add_device", summary="Добавление нового устройства")
async def add_new_device(device: Device, user: UserData4Auth = Depends(get_current_user)):
    print("New device: {}".format(device))
    return {"status": "OK"}


@router.get("/get_place", summary="Отдает карту устройств, портов, маков на портах.")
async def get_place():
    return {
        "device": "ip/hostname",
        "ports": {
            "port1": {
                "mac1": "mac1",
                "mac2": "mac2",
            },
            "port2": ""
        }
    }

