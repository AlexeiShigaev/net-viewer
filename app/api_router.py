from datetime import timedelta

from fastapi import APIRouter
from pysnmp.proto.rfc1902 import TimeTicks

from oid_query import QueryOID, get_oid_from_to, extract_mac_vlan_port, ResultQueryOID, extract_port_and_port_name, \
    extract_info_ip, extract_arp_table


router = APIRouter(tags=["api"])


@router.get("/")
async def root():
    return {"message": "Hello World"}


@router.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}


@router.post("/query")
async def query_oid_range(query: QueryOID) -> ResultQueryOID:
    """
    Запрос нескольких oid из промежутка начиная от **oid_start** включительно и до **oid_stop**, исключая последний.

    Версию SNMP можно указать через snmp_ver: **0 - for SNMP v1, 1 - for SNMP v2c (default)**

    Эквивалент `c:\SnmpWalk -v:2c -c:public -r:host -os:1.3.6.1.2.1.1.1 -op:1.3.6.1.2.1.1.7`

    **Необходимо передать минимум три параметра:**
    - **host**: IP-addr - хост опроса.
    - **oid_start**: с какого oid начинаем, например 1.3.6.1.2.1.1.1
    - **oid_stop**: до какого oid, например 1.3.6.1.2.1.1.7

    Обязательно проверять значение ключа error. Если оно не null - результатам верить нельзя.

    Возвращает словарь вида
    ```
    {
        "results_list": [
        {
            "oid": "1.3.6.1.2.1.1.6.0",
            "value": "comment"
        },
        ],
        "count": int,
        "error": str,
    }
    ```

    """
    results = ResultQueryOID()

    # Делаеам SNMP запрос к хосту
    ret_data = await get_oid_from_to(query)

    results.results_list = [{"oid": str(elem[0]), "value": str(elem[1])} for elem in ret_data["result_list"]]
    results.count, results.error = (ret_data["count"], ret_data["error"])

    return results


@router.post("/query/info")
async def query_info(query: QueryOID) -> ResultQueryOID:
    """
    Запрос наименования прибора, его время аптайм. Так же комментарии, расположение (если заполнено).

    аналог `SnmpWalk -csv -v:2c -r:host -os:.1.3.6.1.2.1.1.1 -op:.1.3.6.1.2.1.1.7`

    Возвращает словарь вида
    ```
    {
        "results_list": [
            "HPE OfficeConnect Switch 1920S 48G 4SFP JL382A.....",
            "59 days, 21:28:43",
            "where is",
            "comment"
        ],
        "count": int,
        "error": str,
    }
    ```
    Обязательно проверять значение ключа error. Если оно не null - результатам верить нельзя.
    """

    # Запрашиваем сырые данные от хоста
    ret_data = await get_oid_from_to(query)
    if ret_data["error"] is not None:
        return ret_data

    # распаковываем данные
    results = ResultQueryOID()
    try:
        # убираю пустые строки, перевожу аптайм в строку, на выходе список строк
        results.results_list = [
            str(timedelta(milliseconds=10 * int(el[1]))) if isinstance(el[1], TimeTicks) else str(el[1])
            for el in ret_data["result_list"] if not (str(el[1]).startswith("1.3.6.1.") or str(el[1]) == "")
        ]
        results.count = len(results.results_list)
    except Exception as ex:
        results.error = "Error was occurred: {}".format(ex)
    return results


@router.post("/query/info_ip")
async def query_info_ip(query: QueryOID) -> ResultQueryOID:
    """
    Запрос локальных IP адресов устройства.

    Аналог запросов:
    * `SnmpWalk -csv -v:2c -c:public -r:host -os:.1.3.6.1.2.1.4.20.1 -op:.1.3.6.1.2.1.4.20.2`

    На выходе словарь вида:
    ```
    {
        "results_list": [
            {
                "10.0.0.1": {
                    "ipAdEntAddr": "10.0.0.1",
                    "ipAdEntIfIndex": "53",
                    "ipAdEntNetMask": "255.255.252.0",
                    "ipAdEntBcastAddr": "1",
                    "ipAdEntReasmMaxSize": "65535"
                }
            }
        ],
        "count": 1,
        "error": null
    }
    ```
    """
    # Запрашиваем сырые данные от хоста
    ret_data = await get_oid_from_to(query)
    if ret_data["error"] is not None:
        return ret_data
    # разворачиваем данные в словарь
    return extract_info_ip(ret_data)


@router.post("/query/macs")
async def query_mac_vlan_port(query: QueryOID) -> ResultQueryOID:
    """
    Запрос: на каких портах коммутатора какие маки светятся, в каких VLan-ах.

    Аналог запросов:
    * `SnmpWalk -csv -v:2c -c:public -r:host -os:1.3.6.1.2.1.17.7.1.2.2.1.2 -op:1.3.6.1.2.1.17.7.1.2.2.1.3`

    Возвращает словарь вида
    ```
    {
        "results_list": [{"mac": str, "vlan": str, "logical_interface_id": str},],
        "count": int,
        "error": str,
    }
    ```
    Обязательно проверять значение ключа error. Если оно не null - результатам верить нельзя.
    """
    # Запрашиваем сырые данные от хоста
    ret_data = await get_oid_from_to(query)
    if ret_data["error"] is not None:
        return ret_data

    # Вынимаем маки, вланы, порты
    return extract_mac_vlan_port(ret_data)


@router.post("/query/ports")
async def query_ports(query: QueryOID):
    """
    Запрос портов/интерфейсов коммутатора, в его внутренних нумерации и именовании портов/интерфейсов.

    Аналог запросов:
    * `SnmpWalk -csv -v:2c -c:public -r:host -os:1.3.6.1.2.1.31.1.1.1.1 -op:1.3.6.1.2.1.31.1.1.1.2`
    * `SnmpWalk -csv -v:2c -c:public -r:host -os:.1.3.6.1.2.1.2.2.1.2 -op:.1.3.6.1.2.1.2.2.1.3`

    На выходе словарь вида:
    ```
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
    ```
    """
    # Запрашиваем сырые данные от хоста
    ret_data = await get_oid_from_to(query)
    if ret_data["error"] is not None:
        return ret_data

    return extract_port_and_port_name(ret_data)


@router.post("/query/arp")
async def query_arp_table(query: QueryOID) -> ResultQueryOID:
    """
    Запрос соответствий мак-адресов и IP-адресов. По портам.

    Аналог запросов:
    * `SnmpWalk -csv -v:2c -c:public -r:host -os:1.3.6.1.2.1.4.22.1.2 -op:1.3.6.1.2.1.4.22.1.3`

    На выходе словарь вида:
    ```

    ```
    """
    # Запрашиваем сырые данные от хоста
    ret_data = await get_oid_from_to(query)
    if ret_data["error"] is not None:
        return ret_data

    return extract_arp_table(ret_data)
