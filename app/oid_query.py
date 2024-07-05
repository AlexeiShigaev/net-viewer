import re
from typing import List, Dict

from pydantic import BaseModel
from pysnmp.hlapi import varbinds
from pysnmp.hlapi.asyncio import *


class QueryOID(BaseModel):
    host: str
    port: int = 161
    community: str = "public"
    snmp_ver: int = 1  # 0 - for SNMP v1, 1 - for SNMP v2c (default)
    oid_start: str
    oid_stop: str

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "1. short query": {
                        "host": "IP addr, кого опрашиваем",
                        "oid_start": "oid.1",
                        "oid_stop": "oid.2",
                    },
                    "2. full query": {
                        "host": "IP addr, кого опрашиваем",
                        "port": 161,
                        "community": "public",
                        "snmp_ver": 1,
                        "oid_start": "oid.1",
                        "oid_stop": "oid.2",
                    }
                }
            ]
        }
    }


class ResultQueryOID(BaseModel):
    results_list: List = []
    count: int = 0
    error: str = None


snmp_engine = SnmpEngine()
mibViewController = varbinds.AbstractVarBinds.getMibViewController(snmp_engine)


async def get_oid_from_to(query: QueryOID):
    """
    Запрашивает список oid начиная с query.oid_start до query.oid_stop (исключая последний).
    Возвращает словарь, в котором в ключе result_list список объектов
    [ObjectIdentity, Integer/OctetString]
    """
    print("New query: {}:{} ({}) {} - {}".format(
        query.host, query.port, query.community, query.oid_start, query.oid_stop
    ))

    oid_start = ObjectIdentity(query.oid_start).resolveWithMib(mibViewController)
    oid_stop = ObjectIdentity(query.oid_stop).resolveWithMib(mibViewController)

    results = {
        "oid_start": oid_start,
        "oid_stop": oid_stop,
        "result_list": [],
        "count": 0,
        "error": None,
    }
    oid_current = oid_start

    while True:

        error_indication, error_status, error_index, var_binds = await nextCmd(
            snmp_engine,
            CommunityData(query.community, mpModel=query.snmp_ver),
            UdpTransportTarget((query.host, query.port)),
            ContextData(),
            ObjectType(oid_current)
        )

        if error_indication:
            print("ERROR:: ", error_indication)
            results["error"] = str(error_indication)
            break
        elif error_status:
            print("ERROR_STATUS: {} at {}".format(
                error_status.prettyPrint(),
                error_index and var_binds[int(error_index) - 1][0] or '?'
            ))
            results["error"] = "ERROR_STATUS: {} at {}".format(
                error_status.prettyPrint(),
                error_index and var_binds[int(error_index) - 1][0] or '?'
            )
            break
        else:
            oid_current, value = var_binds[0][0]
            if oid_current >= oid_stop:
                break
            else:
                print("value: {}, type: {}".format(str(value), type(value)))
                results["result_list"].append([oid_current, value])
                results["count"] += 1

    return results


def extract_mac_vlan_port(data):
    """
    Структура OID-шек с маками такова:
    1.3.6.1.2.1.17.7.1.2.2.1.2.VLAN.M.A.C.A.D.R = PORT
    Отсекаем головную часть равную 1.3.6.1.2.1.17.7.1.2.2.1.2, вычленяем октет с VLANом,
    все остальное мак.
    PORT представляет из себя значение в oid 1.3.6.1.2.1.31.1.1.1.1.PORT
    смотри SnmpWalk -v:2c -c:public -r:host -os:1.3.6.1.2.1.31.1.1.1.1 -op:1.3.6.1.2.1.31.1.1.1.2
    А комментарий/описание порта можно вынуть из 1.3.6.1.2.1.31.1.1.1.18.PORT
    !!! Обязательно проверять значение ключа error. Если оно не null - результатам верить нельзя.
    """
    oid_root = str(data["oid_start"])
    results = ResultQueryOID()

    reg_exp = re.compile(oid_root + '.')    # для всех в этом запросе будет одинаковый
    for elem in data["result_list"]:
        try:
            cut_oid = reg_exp.split(str(elem[0]))
            # print("elem: {} = {}".format(str(elem[0]), str(elem[1])))
            if len(cut_oid):
                # vlan указан в позиции между OID и MAC
                vlan_and_mac = cut_oid[1].split('.')
                vlan = vlan_and_mac[0]
                # mac представлен в десятичных числах, переводим в hex
                mac = ":".join(['{0:x}'.format(int(el)) for el in vlan_and_mac[1:]])
                port = str(elem[1])
                print("\tmac: {},\tvlan: {},\tport: {}".format(mac, vlan, port))
                results.results_list.append({"mac": mac, "vlan": vlan, "port": port})
                results.count += 1
        except Exception as ex:
            print("\n{}\nПри разборе элемента произошла ошибка\n{}".format(
                str(elem), ex
            ))
            results.error = "Exception: {}".format(ex)
            break

    return results
