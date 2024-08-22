from typing import List

from pydantic import BaseModel


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

