from datetime import timedelta

from fastapi import FastAPI
from pysnmp.proto.rfc1902 import TimeTicks

from oid_query import QueryOID, get_oid_from_to, extract_mac_vlan_port, ResultQueryOID

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}


@app.post("/query")
async def query_oid_range(query: QueryOID) -> ResultQueryOID:
    """
    Запрос нескольких oid из промежутка начиная от **oid_start** включительно и до **oid_stop**, исключая последний.

    Версию SNMP можно указать через snmp_ver: **0 - for SNMP v1, 1 - for SNMP v2c (default)**

    Эквивалент `c:\SnmpWalk -v:2c -c:public -r:host -os:1.3.6.1.2.1.1.1 -op:1.3.6.1.2.1.1.7`

    **Необходимо передать минимум три параметра:**
    - **host**: IP-addr - хост опроса.
    - **oid_start**: с какого oid начинаем, например 1.3.6.1.2.1.1.1
    - **oid_stop**: до какого oid, например 1.3.6.1.2.1.1.7

    !!! Обязательно проверять значение ключа error. Если оно не null - результатам верить нельзя !!!

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


@app.post("/query/info")
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
    !!! Обязательно проверять значение ключа error. Если оно не null - результатам верить нельзя !!!
    """

    # Запрашиваем сырые данные от хоста
    ret_data = await get_oid_from_to(query)
    if ret_data["error"] is not None:
        return ret_data

    results = ResultQueryOID()
    try:
        # убираю пустые значения, перевожу аптайм в строку, на выходе список строк
        results.results_list = [
            str(timedelta(milliseconds=10 * int(el[1]))) if isinstance(el[1], TimeTicks) else str(el[1])
            for el in ret_data["result_list"] if not (str(el[1]).startswith("1.3.6.1.") or str(el[1]) == "")
        ]
        results.count = len(results.results_list)
    except Exception as ex:
        results.error = "Error was occurred: {}".format(ex)
    return results


@app.post("/query/macs")
async def query_mac_vlan_port(query: QueryOID) -> ResultQueryOID:
    """
    Запрос: на каких портах коммутатора какие маки светятся, в каких VLan-ах.

    Для примера, работает запрос в котором:

    - **host**: IP-addr - хост опроса.
    - **oid_start**: значение 1.3.6.1.2.1.17.7.1.2.2.1.2
    - **oid_stop**: значение 1.3.6.1.2.1.17.7.1.2.2.1.3

    Возвращает словарь вида
    ```
    {
        "results_list": [{"mac": str, "vlan": str, "port": str},],
        "count": int,
        "error": str,
    }
    ```
    !!! Обязательно проверять значение ключа error. Если оно не null - результатам верить нельзя !!!
    """
    # Запрашиваем  сырые данные от хоста
    ret_data = await get_oid_from_to(query)
    if ret_data["error"] is not None:
        return ret_data

    # Вынимаем маки, вланы, порты
    # return json.dumps(extract_mac_vlan_port(ret_list))
    return extract_mac_vlan_port(ret_data)


# порты коммутатора

@app.post("/query/ports")
async def query_ports(query: QueryOID):
    """
    Запрос портов коммутатора, в его внутреннем именовании портов.

    Аналог запросов:
    * `SnmpWalk -csv -v:2c -c:public -r:host -os:1.3.6.1.2.1.31.1.1.1.1 -op:1.3.6.1.2.1.31.1.1.1.2`
    * `SnmpWalk -csv -v:2c -c:public -r:host -os:.1.3.6.1.2.1.2.2.1.2 -op:.1.3.6.1.2.1.2.2.1.3`
    """
    # Запрашиваем  сырые данные от хоста
    ret_data = await get_oid_from_to(query)
    if ret_data["error"] is not None:
        return ret_data



