# src/snmp_validator.py

from pysnmp.hlapi import (
    getCmd,
    SnmpEngine,
    CommunityData,
    UdpTransportTarget,
    ContextData,
    ObjectType,
    ObjectIdentity,
    UsmUserData,
    usmHMACMD5AuthProtocol,
    usmHMACSHAAuthProtocol,
    usmHMAC128SHA224AuthProtocol,
    usmHMAC192SHA256AuthProtocol,
    usmHMAC256SHA384AuthProtocol,
    usmHMAC384SHA512AuthProtocol,
    usmNoAuthProtocol,
    usmDESPrivProtocol,
    usm3DESEDEPrivProtocol,
    usmAesCfb128Protocol,
    usmAesCfb192Protocol,
    usmAesCfb256Protocol,
    usmNoPrivProtocol,
)
from pysnmp.error import PySnmpError


class SnmpValidator:
    """
    Validates SNMPv2 and SNMPv3 credentials by attempting an SNMP GET operation.
    """

    def __init__(self):
        """
        Initializes the SnmpValidator.
        """
        pass

    def validate_snmpv2_credentials(self, host, community_string, port=161, timeout=1, retries=2):
        """
        Validates SNMPv2c credentials by attempting an SNMP GET operation.

        Args:
            host (str): The IP address or hostname of the SNMP agent.
            community_string (str): The SNMP community string.
            port (int): The SNMP port number. Defaults to 161.
            timeout (int): The SNMP timeout in seconds. Defaults to 1.
            retries (int): The number of SNMP retries. Defaults to 2.

        Returns:
            bool: True if credentials are valid, False otherwise.
        """
        try:
            snmp_engine = SnmpEngine()
            iterator = getCmd(
                snmp_engine,
                CommunityData(community_string),
                UdpTransportTarget((host, port), timeout=timeout, retries=retries),
                ContextData(),
                ObjectType(ObjectIdentity('1.3.6.1.2.1.1.1.0'))  # sysDescr.0
            )

            error_indication, error_status, error_index, var_binds = next(iterator)

            if error_indication:
                # This covers network errors, timeouts, etc.
                print(f"SNMPv2 validation failed for {host}: {error_indication}")
                return False
            elif error_status:
                # This covers SNMP errors like noSuchName, readOnly, etc.
                # For credential validation, an error_status often means the community string is wrong
                # or the OID is not accessible with these credentials.
                print(
                    f"SNMPv2 validation failed for {host}: {error_status.prettyPrint()} at "
                    f"{error_index and var_binds[int(error_index) - 1][0] or '?'}"
                )
                return False
            else:
                # Successful GET operation
                # for var_bind in var_binds:
                #     print(f"SNMPv2 received: {' = '.join([x.prettyPrint() for x in var_bind])}")
                return True

        except PySnmpError as e:
            # Specific PySnmp library errors
            print(f"SNMPv2 PySnmpError for {host}: {e}")
            return False
        except Exception as e:
            # Other unexpected errors (e.g., socket errors not caught by PySnmpError)
            print(f"SNMPv2 general error for {host}: {e}")
            return False

    def validate_snmpv3_credentials(self, host, user, auth_key=None, priv_key=None,
                                   auth_protocol='usmHMACMD5AuthProtocol',
                                   priv_protocol='usmDESPrivProtocol',
                                   port=161, timeout=1, retries=2):
        """
        Validates SNMPv3 credentials by attempting an SNMP GET operation.

        Args:
            host (str): The IP address or hostname of the SNMP agent.
            user (str): The SNMPv3 username.
            auth_key (str, optional): The SNMPv3 authentication key. Defaults to None.
            priv_key (str, optional): The SNMPv3 privacy key. Defaults to None.
            auth_protocol (str, optional): The authentication protocol.
                                          Defaults to 'usmHMACMD5AuthProtocol'.
                                          Supported: 'usmHMACMD5AuthProtocol', 'usmHMACSHAAuthProtocol',
                                                     'usmHMAC128SHA224AuthProtocol', 'usmHMAC192SHA256AuthProtocol',
                                                     'usmHMAC256SHA384AuthProtocol', 'usmHMAC384SHA512AuthProtocol',
                                                     'usmNoAuthProtocol'.
            priv_protocol (str, optional): The privacy protocol.
                                          Defaults to 'usmDESPrivProtocol'.
                                          Supported: 'usmDESPrivProtocol', 'usm3DESEDEPrivProtocol',
                                                     'usmAesCfb128Protocol', 'usmAesCfb192Protocol',
                                                     'usmAesCfb256Protocol', 'usmNoPrivProtocol'.
            port (int): The SNMP port number. Defaults to 161.
            timeout (int): The SNMP timeout in seconds. Defaults to 1.
            retries (int): The number of SNMP retries. Defaults to 2.

        Returns:
            bool: True if credentials are valid, False otherwise.
        """
        # Map protocol strings to pysnmp objects
        auth_protocol_map = {
            'usmHMACMD5AuthProtocol': usmHMACMD5AuthProtocol,
            'usmHMACSHAAuthProtocol': usmHMACSHAAuthProtocol,
            'usmHMAC128SHA224AuthProtocol': usmHMAC128SHA224AuthProtocol,
            'usmHMAC192SHA256AuthProtocol': usmHMAC192SHA256AuthProtocol,
            'usmHMAC256SHA384AuthProtocol': usmHMAC256SHA384AuthProtocol,
            'usmHMAC384SHA512AuthProtocol': usmHMAC384SHA512AuthProtocol,
            'usmNoAuthProtocol': usmNoAuthProtocol,
        }
        priv_protocol_map = {
            'usmDESPrivProtocol': usmDESPrivProtocol,
            'usm3DESEDEPrivProtocol': usm3DESEDEPrivProtocol,
            'usmAesCfb128Protocol': usmAesCfb128Protocol,
            'usmAesCfb192Protocol': usmAesCfb192Protocol,
            'usmAesCfb256Protocol': usmAesCfb256Protocol,
            'usmNoPrivProtocol': usmNoPrivProtocol,
        }

        selected_auth_protocol = auth_protocol_map.get(auth_protocol, usmNoAuthProtocol)
        selected_priv_protocol = priv_protocol_map.get(priv_protocol, usmNoPrivProtocol)

        # Determine security level based on provided keys
        if not auth_key: # noAuthNoPriv
            selected_auth_protocol = usmNoAuthProtocol
            selected_priv_protocol = usmNoPrivProtocol
            auth_key_param = None
            priv_key_param = None
        elif not priv_key: # authNoPriv
            selected_priv_protocol = usmNoPrivProtocol
            auth_key_param = auth_key
            priv_key_param = None
        else: # authPriv
            auth_key_param = auth_key
            priv_key_param = priv_key
        
        # Ensure that if auth_key is None, auth_protocol is usmNoAuthProtocol
        # And if priv_key is None, priv_protocol is usmNoPrivProtocol
        if auth_key_param is None:
            selected_auth_protocol = usmNoAuthProtocol
        if priv_key_param is None:
            selected_priv_protocol = usmNoPrivProtocol


        try:
            snmp_engine = SnmpEngine()
            usm_user_data = UsmUserData(
                user,
                authKey=auth_key_param,
                privKey=priv_key_param,
                authProtocol=selected_auth_protocol,
                privProtocol=selected_priv_protocol
            )

            iterator = getCmd(
                snmp_engine,
                usm_user_data,
                UdpTransportTarget((host, port), timeout=timeout, retries=retries),
                ContextData(),
                ObjectType(ObjectIdentity('1.3.6.1.2.1.1.1.0'))  # sysDescr.0
            )

            error_indication, error_status, error_index, var_binds = next(iterator)

            if error_indication:
                print(f"SNMPv3 validation failed for {host} (user: {user}): {error_indication}")
                return False
            elif error_status:
                print(
                    f"SNMPv3 validation failed for {host} (user: {user}): {error_status.prettyPrint()} at "
                    f"{error_index and var_binds[int(error_index) - 1][0] or '?'}"
                )
                return False
            else:
                # Successful GET operation
                # for var_bind in var_binds:
                #     print(f"SNMPv3 received: {' = '.join([x.prettyPrint() for x in var_bind])}")
                return True

        except PySnmpError as e:
            print(f"SNMPv3 PySnmpError for {host} (user: {user}): {e}")
            return False
        except Exception as e:
            print(f"SNMPv3 general error for {host} (user: {user}): {e}")
            return False

if __name__ == '__main__':
    # Example Usage (for testing purposes)
    validator = SnmpValidator()

    # Test SNMPv2
    # Replace with your actual SNMPv2 details
    # v2_valid = validator.validate_snmpv2_credentials("your_snmp_host", "public")
    # print(f"SNMPv2 Validation: {'Success' if v2_valid else 'Failure'}")

    # Test SNMPv3
    # Replace with your actual SNMPv3 details
    # v3_valid = validator.validate_snmpv3_credentials(
    #     "your_snmp_host",
    #     "your_user",
    #     auth_key="your_auth_key", # Or None
    #     priv_key="your_priv_key", # Or None
    #     auth_protocol="usmHMACSHAAuthProtocol", # Or appropriate protocol
    #     priv_protocol="usmAesCfb128Protocol"  # Or appropriate protocol
    # )
    # print(f"SNMPv3 Validation: {'Success' if v3_valid else 'Failure'}")
    pass
