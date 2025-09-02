#!/usr/bin/env python3
"""Asynchronous SNMPv3 credential checker.

This script performs a simple SNMP GET request against a target host
using SNMPv3 security parameters. A successful response indicates that
provided credentials are valid.
"""

import argparse
import asyncio
from typing import Tuple

from pysnmp.hlapi.asyncio import (
    SnmpEngine,
    UdpTransportTarget,
    ContextData,
    UsmUserData,
    ObjectType,
    ObjectIdentity,
    getCmd,
)
from pysnmp.hlapi import (
    usmHMACSHAAuthProtocol,
    usmHMACSHA224AuthProtocol,
    usmHMACSHA256AuthProtocol,
    usmHMACSHA384AuthProtocol,
    usmHMACSHA512AuthProtocol,
    usmHMACMD5AuthProtocol,
    usmNoAuthProtocol,
    usmDESPrivProtocol,
    usm3DESEDEPrivProtocol,
    usmAesCfb128Protocol,
    usmAesCfb192Protocol,
    usmAesCfb256Protocol,
    usmNoPrivProtocol,
)

AUTH_PROTOCOLS = {
    "sha": usmHMACSHAAuthProtocol,
    "sha224": usmHMACSHA224AuthProtocol,
    "sha256": usmHMACSHA256AuthProtocol,
    "sha384": usmHMACSHA384AuthProtocol,
    "sha512": usmHMACSHA512AuthProtocol,
    "md5": usmHMACMD5AuthProtocol,
    "none": usmNoAuthProtocol,
}

PRIV_PROTOCOLS = {
    "des": usmDESPrivProtocol,
    "3des": usm3DESEDEPrivProtocol,
    "aes": usmAesCfb128Protocol,
    "aes192": usmAesCfb192Protocol,
    "aes256": usmAesCfb256Protocol,
    "none": usmNoPrivProtocol,
}


async def check_snmpv3(
    host: str,
    port: int,
    user: str,
    auth_key: str,
    auth_proto: str,
    priv_key: str,
    priv_proto: str,
    oid: str,
) -> Tuple[bool, str]:
    """Attempt an SNMP GET request and return success flag and details."""
    engine = SnmpEngine()
    user_data = UsmUserData(
        user,
        authKey=auth_key,
        privKey=priv_key,
        authProtocol=AUTH_PROTOCOLS[auth_proto],
        privProtocol=PRIV_PROTOCOLS[priv_proto],
    )

    error_indication, error_status, error_index, var_binds = await getCmd(
        engine,
        user_data,
        UdpTransportTarget((host, port)),
        ContextData(),
        ObjectType(ObjectIdentity(oid)),
    )

    await engine.shutdown()

    if error_indication:
        return False, str(error_indication)
    if error_status:
        msg = f"{error_status.prettyPrint()} at {error_index and var_binds[int(error_index) - 1][0] or '?'}"
        return False, msg
    result = ", ".join(f"{name.prettyPrint()} = {val.prettyPrint()}" for name, val in var_binds)
    return True, result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check SNMPv3 credentials against a host")
    parser.add_argument("--host", required=True, help="Target host or IP address")
    parser.add_argument("--port", type=int, default=161, help="SNMP port")
    parser.add_argument("--user", required=True, help="SNMPv3 security user")
    parser.add_argument("--auth-key", dest="auth_key", help="Authentication passphrase")
    parser.add_argument(
        "--auth-proto",
        dest="auth_proto",
        default="sha",
        choices=sorted(AUTH_PROTOCOLS.keys()),
        help="Authentication protocol",
    )
    parser.add_argument("--priv-key", dest="priv_key", help="Privacy passphrase")
    parser.add_argument(
        "--priv-proto",
        dest="priv_proto",
        default="none",
        choices=sorted(PRIV_PROTOCOLS.keys()),
        help="Privacy protocol",
    )
    parser.add_argument(
        "--oid",
        default="1.3.6.1.2.1.1.1.0",
        help="OID to query (default: sysDescr.0)",
    )
    return parser.parse_args()


async def main() -> int:
    args = parse_args()

    if args.auth_proto != "none" and not args.auth_key:
        raise SystemExit("--auth-key required for auth protocol")
    if args.priv_proto != "none" and not args.priv_key:
        raise SystemExit("--priv-key required for priv protocol")

    success, info = await check_snmpv3(
        args.host,
        args.port,
        args.user,
        args.auth_key,
        args.auth_proto,
        args.priv_key,
        args.priv_proto,
        args.oid,
    )

    if success:
        print(f"Success: {info}")
        return 0
    print(f"Failure: {info}")
    return 1


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
