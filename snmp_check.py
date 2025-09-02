import asyncio
import argparse
from pysnmp.hlapi.asyncio import *

async def check_snmp_credentials(host, user, auth_key, priv_key):
    """
    Checks SNMPv3 credentials by performing an asynchronous GET command.

    Args:
        host (str): The IP address or hostname of the SNMP agent.
        user (str): The SNMPv3 username.
        auth_key (str): The SNMPv3 authentication key.
        priv_key (str): The SNMPv3 privacy key.
    """
    snmp_engine = SnmpEngine()

    error_indication, error_status, error_index, var_binds = await getCmd(
        snmp_engine,
        UsmUserData(
            user,
            authKey=auth_key,
            privKey=priv_key,
            authProtocol=usmHMACSHAAuthProtocol,
            privProtocol=usmAesCfb128Protocol
        ),
        UdpTransportTarget((host, 161)),
        ContextData(),
        ObjectType(ObjectIdentity('SNMPv2-MIB', 'sysDescr', 0))
    )

    if error_indication:
        print(f"Authentication failed: {error_indication}")
    elif error_status:
        print(f"Authentication failed: {error_status.prettyPrint()} at {error_index and var_binds[int(error_index) - 1][0] or '?'}")
    else:
        print("Authentication successful!")
        for var_bind in var_binds:
            print(' = '.join([x.prettyPrint() for x in var_bind]))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Check SNMPv3 credentials.")
    parser.add_argument("host", help="The IP address or hostname of the SNMP agent.")
    parser.add_argument("user", help="The SNMPv3 username.")
    parser.add_argument("auth_key", help="The SNMPv3 authentication key.")
    parser.add_argument("priv_key", help="The SNMPv3 privacy key.")
    args = parser.parse_args()

    asyncio.run(check_snmp_credentials(args.host, args.user, args.auth_key, args.priv_key))
