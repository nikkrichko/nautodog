# SNMPv3 Credential Checker

This script, `snmp_check.py`, is a simple tool to check SNMPv3 credentials against a target host. It uses the `pysnmp` library to perform an asynchronous SNMP GET operation.

## Installation

To use this script, you need to have Python 3.7+ and the following libraries installed:

* `pysnmp`: A pure-Python SNMP library.
* `pycryptodomex`: A low-level cryptographic library required for SNMPv3 encryption.

You can install these libraries using pip:

```bash
pip install pysnmp pycryptodomex
```

## Usage

To use the script, run it from the command line with the following arguments:

```bash
python snmp_check.py <host> <user> <auth_key> <priv_key>
```

* `<host>`: The IP address or hostname of the SNMP agent.
* `<user>`: The SNMPv3 username.
* `<auth_key>`: The SNMPv3 authentication key.
* `<priv_key>`: The SNMPv3 privacy key.

### Example

```bash
python snmp_check.py 192.168.1.1 myuser myauthkey myprivkey
```

If the credentials are correct, the script will print a success message and the result of the SNMP GET operation. Otherwise, it will print an error message.
