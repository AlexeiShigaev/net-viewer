import re

from pysnmp.hlapi import varbinds
from pysnmp.hlapi.asyncio import *

from app.snmp.models import QueryOID, ResultQueryOID

snmp_engine = SnmpEngine()
mibViewController = varbinds.AbstractVarBinds.getMibViewController(snmp_engine)

# Нет доверия к этой конструкции, а если некий новоявленный прибор даст свой вариант реализации?
info_key = {
    "1": "ipAdEntAddr",
    "2": "ipAdEntIfIndex",
    "3": "ipAdEntNetMask",
    "4": "ipAdEntBcastAddr",
    "5": "ipAdEntReasmMaxSize",
}


async def get_oid_from_to(query: QueryOID):
    """
    Запрашивает список oid начиная с query.oid_start до query.oid_stop (исключая последний).
    Возвращает словарь, в котором в ключе result_list список объектов
    [pysnmp.proto.rfc1902.ObjectIdentity, pysnmp.proto.rfc1902.Integer/OctetString/...]
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
                # print("value: {}, type: {}".format(str(value), type(value)))
                results["result_list"].append([oid_current, value])
                results["count"] += 1

    return results


def extract_info_ip(data) -> ResultQueryOID:
    """
    Принимает на входе результат опроса коммутатора - структуру данных которую отдает get_oid_from_to(),
    внутри списка result_list объекты времени выполнения:
    [pysnmp.proto.rfc1902.ObjectIdentity, pysnmp.proto.rfc1902.Integer/OctetString/...]
    Функциональность не работает с операциями ввода/вывода, поэтому не async
    *************************************************************************************************
    Эквивалент `SnmpWalk -csv -v:2c -c:public -r:host -os:.1.3.6.1.2.1.4.20.1 -op:.1.3.6.1.2.1.4.20.2`
    Струкрура OID-шек с инфо о наличии внутренних IP-addr такова:
    1.3.6.1.2.1.4.20.1.TYPE_INFO.IP.A.D.DR = INFO

    На выходе список словарей вида:
    {
        "results_list": [
            {
                "ipAdEntAddr": "10.0.0.1",
                "ipAdEntIfIndex": "53",
                "ipAdEntNetMask": "255.255.252.0",
                "ipAdEntBcastAddr": "1",
                "ipAdEntReasmMaxSize": "65535"
            },
        ],
        "count": 1,
        "error": null
    }
    """

    oid_root = str(data["oid_start"]) + '.'
    results = ResultQueryOID()
    ip_addr_entry = {}
    try:
        for elem in data["result_list"]:
            key, addr = str(elem[0]).split(oid_root)[1].split('.', maxsplit=1)
            ip_addr_entry.setdefault(addr, {})
            info_key.setdefault(key, "unknown")  # возможно это излишняя страховка
            ip_addr_entry[addr].update({info_key[key]: elem[1].prettyPrint()})

        results.results_list = [ip_addr_entry[el] for el in ip_addr_entry]
        results.count = len(results.results_list)
    except Exception as ex:
        results.error = "extract_info_ip: Error was occurred: {}".format(ex)

    return results


def extract_mac_vlan_port(data) -> ResultQueryOID:
    """
    Принимает на входе результат опроса коммутатора - структуру данных которую отдает get_oid_from_to(),
    внутри списка result_list объекты времени выполнения:
    [pysnmp.proto.rfc1902.ObjectIdentity, pysnmp.proto.rfc1902.Integer/OctetString/...]
    Функциональность не работает с операциями ввода/вывода, поэтому не async
    *************************************************************************************************
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
                mac = ":".join(['{0:02x}'.format(int(el)) for el in vlan_and_mac[1:]])
                logical_interface_id = str(elem[1])
                # print("\tmac: {},\tvlan: {},\tlogical_interface_id: {}".format(mac, vlan, logical_interface_id))
                results.results_list.append(
                    {
                        "mac": mac,
                        "vlan": vlan,
                        "logical_interface_id": logical_interface_id
                    }
                )
                results.count += 1
        except Exception as ex:
            print("\n{}\nПри разборе элемента произошла ошибка\n{}".format(
                str(elem), ex
            ))
            results.error = "extract_mac_vlan_port: Exception: {}".format(ex)
            break

    return results


def extract_port_and_port_name(data) -> ResultQueryOID:
    """
    Принимает на входе результат опроса коммутатора - структуру данных которую отдает get_oid_from_to(),
    внутри списка result_list объекты времени выполнения:
    [pysnmp.proto.rfc1902.ObjectIdentity, pysnmp.proto.rfc1902.Integer/OctetString/...]
    Функциональность не работает с операциями ввода/вывода, поэтому не async
    *************************************************************************************************
    Струкрура OID-шек с инфо по портам такова:
    1.3.6.1.2.1.31.1.1.1.1.PORT = PORT_NAME
    Не следует ожидать, что PORT будет 0 или 1 для первого порта. Все это внутренняя кухня коммутатора.
    На выходе словарь вида:
    {
    "results_list": [
        {
            "logical_interface_id": "49",
            "port_name": "gi1/0/1"
        },
        ],
        "count": int,
        "error": str
    }
    """
    results = ResultQueryOID()
    oid_root_str = str(data["oid_start"]) + '.'

    for elem in data["result_list"]:
        try:
            results.results_list.append(
                {
                    "logical_interface_id": str(elem[0]).split(oid_root_str)[1],
                    "port_name": str(elem[1])
                }
            )
            results.count += 1

        except Exception as ex:
            print("\n{}\nПри разборе элемента произошла ошибка\n{}".format(
                str(elem), ex
            ))
            results.error = "extract_port_and_port_name: Exception: {}".format(ex)
            break

    return results


def extract_arp_table(data) -> ResultQueryOID:
    """
    Принимает на входе результат опроса коммутатора - структуру данных которую отдает get_oid_from_to(),
    внутри списка result_list объекты времени выполнения:
    [pysnmp.proto.rfc1902.ObjectIdentity, pysnmp.proto.rfc1902.Integer/OctetString/...]
    Функциональность не работает с операциями ввода/вывода, поэтому не async
    *************************************************************************************************
    {
    "results_list": [
        {
            "logical_interface_id": "12",
            "ip_addr": "10.0.0.29",
            "mac": "63:13:a2:21:01:80",
        },
    ],
    "count": 1,
    "error": null
    }
    """
    results = ResultQueryOID()
    oid_root_str = str(data["oid_start"]) + '.'

    try:
        for elem in data["result_list"]:
            logical_interface_id, ip_addr = str(elem[0]).split(oid_root_str)[1].split(".", maxsplit=1)
            mac: OctetString = elem[1]
            results.results_list.append(
                {
                    "logical_interface_id": logical_interface_id,
                    "ip_addr": ip_addr,
                    "mac": ":".join(["{0:02x}".format(el) for el in mac.asNumbers()]),
                }
            )
        results.count = len(results.results_list)
    except Exception as ex:
        print("\nПри разборе элемента произошла ошибка\n{}".format(ex))
        results.error = "extract_arp_table: Exception: {}".format(ex)

    return results


def extract_mac_addr(data) -> ResultQueryOID:
    results = ResultQueryOID()
    oid_root_str = str(data["oid_start"]) + '.'
    try:
        tmp_dict = {"ports": {}}
        for elem in data["result_list"]:
            mac: OctetString = elem[1]
            tmp_dict["ports"].update(
                {
                    str(elem[0]).split(oid_root_str)[1]:
                    ":".join(["{0:02x}".format(el) for el in mac.asNumbers()]),
                }
            )
        results.results_list.append(tmp_dict)
        results.count = len(results.results_list)
    except Exception as ex:
        print("\nПри разборе элемента произошла ошибка\n{}".format(ex))
        results.error = "extract_arp_table: Exception: {}".format(ex)

    return results
