from pydantic import BaseModel


class Device(BaseModel):
    host: str
    port: int = 161
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
                    "host": "10.30.1.1",
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