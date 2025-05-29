# Tests for SnmpValidator

This directory contains unit tests for the `SnmpValidator` class located in `src/snmp_validator.py`.

## Overview

The `SnmpValidator` class provides methods to validate SNMPv2 and SNMPv3 credentials against a target device. These tests aim to ensure the reliability and correctness of these validation methods.

## Test Files

-   **`smoke_snmp_validator.py`**: Contains smoke tests. These are basic checks to ensure that the validation methods are callable, accept parameters correctly, and return boolean values as expected. They typically use dummy data and are not intended for live credential validation but rather for a quick sanity check of the class's interface and basic error handling.
-   **`regression_snmp_validator.py`**: Contains regression tests. These are more comprehensive tests designed to validate various scenarios with actual SNMP credentials against a live SNMP-enabled device. These tests rely on a configuration file that you must create.

## Configuration (`test_config.yaml`)

To run the regression tests, you need to provide SNMP credentials and target device information.

1.  **Copy the template**:
    Copy the `test_config.yaml.template` file located in this directory to a new file named `test_config.yaml` in the same directory (`tests/unit/snmp_validator/`).

2.  **Edit `test_config.yaml`**:
    Open `test_config.yaml` and fill in the required details:
    *   `global_test_host`: The IP address or hostname of your SNMP test device. This will be used if a specific test case does not override the host.
    *   `global_test_port`: The SNMP port of your test device (default is 161).
    *   **`snmp_v2_tests`**:
        *   `valid_v2_creds`: Provide a valid SNMPv2 community string for your test device.
            For initial SNMPv2 testing, you can use publicly available SNMP agents. For example:
            -   `demo.snmplabs.com` with community string `public`
            -   `snmp.live.gambitcommunications.com` with community string `public`
            You can use these details in the `valid_v2_creds` section of your `test_config.yaml`.
        *   `invalid_v2_creds`: Provide an invalid SNMPv2 community string.
    *   **`snmp_v3_tests`**:
        *   `no_auth_no_priv`: Configure an SNMPv3 user with NoAuthNoPriv security level on your device and provide the username.
        *   `auth_no_priv`: Configure an SNMPv3 user with AuthNoPriv security level. Provide the username, authentication protocol (e.g., `usmHMACMD5AuthProtocol`, `usmHMACSHAAuthProtocol`), and the authentication key.
        *   `auth_priv`: Configure an SNMPv3 user with AuthPriv security level. Provide the username, authentication protocol, authentication key, privacy protocol (e.g., `usmDESPrivProtocol`, `usmAesCfb128Protocol`), and the privacy key.
        *   `invalid_auth_key`: Use details for a valid AuthPriv user but provide an incorrect `auth_key`.
        *   `invalid_priv_key`: Use details for a valid AuthPriv user but provide an incorrect `priv_key`.

    Refer to the comments within `test_config.yaml.template` for more details on each parameter.

    **Important**: Ensure the SNMP agent on your test device is configured to accept queries from the machine where you are running these tests, and that the provided credentials match the device's configuration for each test case.

## Running the Tests

These tests are designed to be run with `pytest`. From the root of the repository:

```bash
pytest tests/unit/snmp_validator/
```

Or to run specific files:

```bash
pytest tests/unit/snmp_validator/smoke_snmp_validator.py
pytest tests/unit/snmp_validator/regression_snmp_validator.py
```

Regression tests for specific configurations will be skipped if `test_config.yaml` is not found or if the relevant sections within it are not filled out.
