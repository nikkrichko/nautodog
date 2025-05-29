# tests/unit/snmp_validator/regression_snmp_validator.py
"""
Regression tests for SnmpValidator.

These tests require a 'test_config.yaml' file in the same directory,
based on 'test_config.yaml.template'. This file must be configured
with details of a live SNMP agent to test against.

If 'test_config.yaml' is not found, is invalid, or specific test
configurations are missing, the relevant tests will be skipped.
"""

import os
import pytest
from ruamel.yaml import YAML
from src.snmp_validator import SnmpValidator

# Mark all tests in this module as 'regression'
pytestmark = pytest.mark.regression

CONFIG_FILE = os.path.join(os.path.dirname(__file__), 'test_config.yaml')

def load_test_config():
    """Loads test configuration from test_config.yaml."""
    if not os.path.exists(CONFIG_FILE):
        print(f"Test config file not found: {CONFIG_FILE}")
        return None
    yaml = YAML(typ='safe') # typ='safe' is important for security
    with open(CONFIG_FILE, 'r') as f:
        try:
            return yaml.load(f)
        except Exception as e: # Catching generic Exception as ruamel.yaml can raise various errors
            print(f"Error loading or parsing YAML from {CONFIG_FILE}: {e}")
            return None

config = load_test_config()

# Fallback global values from config if available
GLOBAL_HOST = None
GLOBAL_PORT = 161 # Default SNMP port
SNMP_V2_TEST_CONFIG = None
SNMP_V3_TEST_CONFIG = None

if config:
    GLOBAL_HOST = config.get('global_test_host')
    GLOBAL_PORT = config.get('global_test_port', 161)
    SNMP_V2_TEST_CONFIG = config.get('snmp_v2_tests')
    SNMP_V3_TEST_CONFIG = config.get('snmp_v3_tests')


@pytest.mark.skipif(not config or not SNMP_V2_TEST_CONFIG,
                    reason="SNMP v2 test config not found or test_config.yaml missing/invalid.")
class TestSnmpV2Regression:
    """Regression tests for SNMPv2c validation."""

    validator = SnmpValidator()

    @pytest.mark.skipif(not SNMP_V2_TEST_CONFIG or 'valid_v2_creds' not in SNMP_V2_TEST_CONFIG,
                        reason="Config for 'valid_v2_creds' missing in snmp_v2_tests.")
    def test_valid_v2_creds(self):
        """Tests validation with correct SNMPv2c credentials."""
        test_params = SNMP_V2_TEST_CONFIG['valid_v2_creds']
        host = test_params.get('host', GLOBAL_HOST)
        port = test_params.get('port', GLOBAL_PORT)
        community = test_params.get('community_string')

        if not host or not community:
            pytest.skip("Host or community string not configured for valid_v2_creds.")

        result = self.validator.validate_snmpv2_credentials(
            host=host,
            community_string=community,
            port=port
        )
        assert result is True, "SNMPv2 validation failed for valid credentials."

    @pytest.mark.skipif(not SNMP_V2_TEST_CONFIG or 'invalid_v2_creds' not in SNMP_V2_TEST_CONFIG,
                        reason="Config for 'invalid_v2_creds' missing in snmp_v2_tests.")
    def test_invalid_v2_creds(self):
        """Tests validation with incorrect SNMPv2c credentials."""
        test_params = SNMP_V2_TEST_CONFIG['invalid_v2_creds']
        host = test_params.get('host', GLOBAL_HOST)
        port = test_params.get('port', GLOBAL_PORT)
        community = test_params.get('community_string')

        if not host or not community:
            pytest.skip("Host or community string not configured for invalid_v2_creds.")

        result = self.validator.validate_snmpv2_credentials(
            host=host,
            community_string=community,
            port=port
        )
        assert result is False, "SNMPv2 validation succeeded for invalid credentials (expected failure)."


@pytest.mark.skipif(not config or not SNMP_V3_TEST_CONFIG,
                    reason="SNMP v3 test config not found or test_config.yaml missing/invalid.")
class TestSnmpV3Regression:
    """Regression tests for SNMPv3 validation."""

    validator = SnmpValidator()

    def _run_v3_test(self, test_case_name, expected_result):
        if test_case_name not in SNMP_V3_TEST_CONFIG:
            pytest.skip(f"Config for '{test_case_name}' missing in snmp_v3_tests.")

        test_params = SNMP_V3_TEST_CONFIG[test_case_name]
        host = test_params.get('host', GLOBAL_HOST)
        port = test_params.get('port', GLOBAL_PORT)
        user = test_params.get('user')
        auth_protocol = test_params.get('auth_protocol', 'usmNoAuthProtocol')
        priv_protocol = test_params.get('priv_protocol', 'usmNoPrivProtocol')
        auth_key = test_params.get('auth_key')
        priv_key = test_params.get('priv_key')

        if not host or not user:
            pytest.skip(f"Host or user not configured for {test_case_name}.")
        
        # Handle cases where keys might be empty strings in YAML but should be None for pysnmp
        auth_key = auth_key if auth_key else None
        priv_key = priv_key if priv_key else None
        
        # Ensure auth/priv protocols are correctly set to NoAuth/NoPriv if keys are not provided
        if auth_key is None:
            auth_protocol = 'usmNoAuthProtocol'
        if priv_key is None:
            priv_protocol = 'usmNoPrivProtocol'


        result = self.validator.validate_snmpv3_credentials(
            host=host,
            user=user,
            auth_key=auth_key,
            priv_key=priv_key,
            auth_protocol=auth_protocol,
            priv_protocol=priv_protocol,
            port=port
        )
        assert result is expected_result, \
            f"SNMPv3 validation for {test_case_name} returned {result}, expected {expected_result}."

    # Test methods for each SNMPv3 scenario
    def test_v3_no_auth_no_priv(self):
        """Tests SNMPv3 noAuthNoPriv."""
        self._run_v3_test('no_auth_no_priv', True)

    def test_v3_auth_no_priv(self):
        """Tests SNMPv3 authNoPriv."""
        self._run_v3_test('auth_no_priv', True)

    def test_v3_auth_priv(self):
        """Tests SNMPv3 authPriv."""
        self._run_v3_test('auth_priv', True)

    def test_v3_invalid_auth_key(self):
        """Tests SNMPv3 with an invalid authentication key."""
        self._run_v3_test('invalid_auth_key', False)

    def test_v3_invalid_priv_key(self):
        """Tests SNMPv3 with an invalid privacy key."""
        self._run_v3_test('invalid_priv_key', False)

# Example of how to run these tests (informational):
# 1. Copy tests/unit/snmp_validator/test_config.yaml.template to
#    tests/unit/snmp_validator/test_config.yaml
# 2. Edit test_config.yaml with your SNMP device details.
# 3. Run pytest:
#    pytest tests/unit/snmp_validator/regression_snmp_validator.py
#
# Note: If the config file or specific sections are missing, tests will be skipped.
# Ensure your SNMP agent is configured to respond to the credentials in test_config.yaml.
# For tests expected to fail (e.g., invalid_auth_key), ensure that the "failure"
# is due to the specific invalid parameter and not other misconfigurations.
# For example, for invalid_auth_key, the user, host, and priv_key (if used) should be valid.
