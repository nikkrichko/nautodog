# SNMPv3 Credential Checker

This repository includes `snmpv3_check.py`, a small asynchronous script that
verifies credentials against an SNMPv3-enabled device by issuing a `sysDescr`
query. It uses the [`pysnmp-lextudio`](https://pypi.org/project/pysnmp-lextudio/)
package (pysnmp v7).

## Installation

Create a virtual environment and install the required library:

```bash
python -m venv venv
source venv/bin/activate
pip install pysnmp-lextudio
```

## Usage

```bash
python snmpv3_check.py --host 192.0.2.1 --user myUser --auth-key myAuthPass \
    --auth-proto sha --priv-key myPrivPass --priv-proto aes
```

Options:

- `--host` – target IP or hostname (required)
- `--port` – SNMP port (default: 161)
- `--user` – SNMPv3 security name (required)
- `--auth-key` – authentication passphrase (required if auth protocol is not `none`)
- `--auth-proto` – authentication protocol (`sha`, `sha224`, `sha256`, `sha384`, `sha512`, `md5`, `none`)
- `--priv-key` – privacy passphrase (required if privacy protocol is not `none`)
- `--priv-proto` – privacy protocol (`aes`, `aes192`, `aes256`, `3des`, `des`, `none`)
- `--oid` – OID to query (default: `1.3.6.1.2.1.1.1.0`)

The script exits with code `0` when the credentials are accepted and a response is
returned, otherwise it returns code `1` and prints the error.
