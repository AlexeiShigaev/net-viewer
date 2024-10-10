import ipaddress
import re


def is_it_ipv4(ip: str) -> bool:
    try:
        ipaddress.IPv4Network(ip)
        return True
    except Exception:
        return False


def is_it_mac_addr(mac: str) -> bool:
    if re.match(r"^(?:[0-9A-Fa-f]{2}[:-]){5}(?:[0-9A-Fa-f]{2})$", mac):
        return True
    else:
        return False


if __name__ == "__main__":
    print("test IP")
    if is_it_ipv4("10.30.1.1111"):
        print("IP checked ok")
    else:
        print("it is not IPv4")

    print("test MAC")
    if is_it_mac_addr("08:f1:ea:54:3a:fg"):
        print("MAC. it is")
    else:
        print("it is not mac")
