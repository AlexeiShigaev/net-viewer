from typing import Optional, List, Dict

from bson.objectid import ObjectId
from pydantic import BaseModel, Field


class NewDevice(BaseModel):
    """
    Описывает новое устройство.
    По этой же модели вынимается документ из базы.
     pydantic.errors.PydanticInvalidForJsonSchema:
     Cannot generate a JsonSchema for core_schema.IsInstanceSchema (<class 'bson.objectid.ObjectId'>)
    """
    # id: Optional[ObjectId] = Field(alias="_id", default=ObjectId())
    host: str = Field(description="Host IP-addr")
    port: int = Field(deefault=161, description="Port for SNMP query to host. Default: 161")
    community: str
    snmp_ver: int = 1  # 0 - for SNMP v1, 1 - for SNMP v2c (default)
    info_oid_start: str
    info_oid_stop: str
    ports_oid_start: str
    ports_oid_stop: str
    internal_ip_oid_start: str
    internal_ip_oid_stop: str
    macs_oid_start: str
    macs_oid_stop: str
    arp_oid_start: str
    arp_oid_stop: str

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "host": "10.20.30.10",
                    "port": 161,
                    "community": "public",
                    "snmp_ver": 1,
                    "info_oid_start": ".1.3.6.1.2.1.1.1",
                    "info_oid_stop": ".1.3.6.1.2.1.1.7",
                    "ports_oid_start": ".1.3.6.1.2.1.2.2.1.2",
                    "ports_oid_stop": ".1.3.6.1.2.1.2.2.1.3",
                    "internal_ip_oid_start": ".1.3.6.1.2.1.4.20.1",
                    "internal_ip_oid_stop": ".1.3.6.1.2.1.4.20.2",
                    "macs_oid_start": ".1.3.6.1.2.1.17.7.1.2.2.1.2",
                    "macs_oid_stop": ".1.3.6.1.2.1.17.7.1.2.2.1.3",
                    "arp_oid_start": ".1.3.6.1.2.1.4.22.1.2",
                    "arp_oid_stop": ".1.3.6.1.2.1.4.22.1.3",
                }
            ]
        }
    }


##############################################################
# Секция описывает структуру данных состояния устройства онлайн
##############################################################
class PortInfo(BaseModel):
    name: str = Field(description="Наименование порта устройства в его внутренних терминах.", default="")
    macs: Dict[str, str] = Field(description="Пара {key: value}, где key - mac-addr, value - VLAN", default={})


class InternalIP(BaseModel):
    ipAdEntAddr: str = Field(description="IP-addr")
    ipAdEntIfIndex: str = Field(description="Номер интерфейса (это может быть localhost или VLAN-iFace).")
    ipAdEntNetMask: str = Field(description="Маска субсети для данного IP-адреса")
    ipAdEntBcastAddr: str = Field(description="Значение младшего бита широковещательного адреса (обычно 1)")
    ipAdEntReasmMaxSize: str = Field(description="Размер наибольшей IP-дейтаграммы")
    ifPhyAddress: str = Field(description="MAC адрес на этом интерфейсе.", default="")


class DeviceInfo(BaseModel):
    host: str = Field(description="Host IP-addr")
    info: str = Field(description="Строка с именованием, комментарием, производителем.", default="")
    internal_ip: Dict[str, InternalIP] = Field(description="Список внутренних IP адресов", default={})
    ports: Dict[str, PortInfo] = Field(description="Данные о портах, маках за ними.", default={})
    device_macs_counter: int = Field(description="Общее количество маков на устройстве.", default=0)


