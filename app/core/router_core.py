"""
Добавление нового устройства:
Записали структуру NewDevice и вернули что ОК. Перед выходом,
инициировать обновление данных по этому новому устройству, отпустив его БЕЗ ОЖИДАНИЯ, в отдельный поток.

Обращение связанное с маками:
1. маки фигурируют в результатах /snmp/query/macs
    {
        "mac": str,
        "vlan": str,
        "logical_interface_id": str
    }
2. маки фигурируют в запросах /snmp/query/arp
    {
      "logical_interface_id": "100004",
      "ip_addr": "10.0.1.4",
      "mac": "62:13:a2:97:84:00"
    }

Оба эти результата синтезируют одну матрицу.
Дополнительная информация: Порты, устройства, должно быть добавлены.

Второй момент.
Есть внутренние IP-адреса. Надо как-то понять их связку с маками.
При этом, какими портами соединены устройства, как понять?
Факт, что если на порту больше одного мака - то там свитч. Обратно, если на порту 1 мак, то очевидно, это прибор
Не факт, что там нет ветки. Может быть роутер, может быть точка WiFi.

К размышлению: взять внутренние IP адреса и маски сети
(могут быть вланы, тот еще вопрос, будет ли маршрут к этим хостам для пинга),
опросить пингом ВСЕ адресное пространство, слать максимум два пакета,
а потом снять результат `arp -a`, добудем связки IP - MAC-addr.
И делать это каждые 10 минут, например.
(Пинги не быстрые, масштаб времени... нужно подумать. Смотря сколько хостов/устройств в сети.)

"""
import asyncio

from fastapi import APIRouter, Depends, HTTPException, status

from app.auth.auth import get_current_user
from app.auth.models import UserData4Auth
from app.core.core import Core, generate_mac_ip_pair, CoreManager
from app.core.models import NewDevice
from app.database import motorchik

router = APIRouter(prefix="/core", tags=["Core functionality API"])


@router.post("/add_device", summary="Добавление нового устройства")
async def add_new_device(device: NewDevice, user: UserData4Auth = Depends(get_current_user)):
    print("New device: {}".format(device))

    dev = await motorchik.find_one(
        "devices", {"host": device.host}
    )
    if dev is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Host already exists')

    dev = await motorchik.insert_one("devices", device)

    Core.update()
    return {"status": "ok", "inserted_id": str(dev.inserted_id)}


@router.get("/get_place", summary="Отдает карту устройств, портов, маков на портах.")
async def get_place(user: UserData4Auth = Depends(get_current_user)):
    # Core.update()
    while Core.is_in_progress():
        await asyncio.sleep(1)

    return {
        "macs": CoreManager.mac_ip_dict,
        "devices": CoreManager.device_dict,
        "tree": CoreManager.device_tree
    }


@router.post("/search/", summary="Поиск по MAC-ам или по IP")
async def search_mac_or_ip(param: dict, user: UserData4Auth = Depends(get_current_user)):
    """
    Искать можно или MAC или IP адрес
    mac_ip: {"query": "68:13:e2:85:c2:80" OR "10.20.30.41"}
    На выходе: на каких портах каких устройств светится MAC
    """
    print("search_mac_or_ip: {}".format(param))

    ret = generate_mac_ip_pair(param["query"], CoreManager.mac_ip_dict, CoreManager.device_dict)
    print("search_mac_or_ip: {}".format(ret))
    if ret is None:
        print("\tdata unrecognized.")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Bad or unknown data')

    return ret


