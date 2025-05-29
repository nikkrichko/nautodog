# tests/unit/snmp_validator/smoke_snmp_validator.py
"""
Smoke tests for SnmpValidator.

These tests are intended to verify basic method functionality and return types.
They do not perform actual credential validation against a live SNMP agent
and are expected to fail (return False) or confirm the return type is boolean,
as they use dummy data or attempt to connect to localhost where no SNMP agent
is expected to be listening with these parameters.
"""

import pytest
from src.snmp_validator import SnmpValidator

# Mark the entire module as 'smoke'
pytestmark = pytest.mark.smoke

def test_smoke_validate_snmpv2_call_and_return_type():
    """
    Smoke test for SnmpValidator.validate_snmpv2_credentials.
    Checks if the method can be called and returns a boolean value.
    Uses parameters that should lead to a quick local failure.
    """
    validator = SnmpValidator()
    # Using localhost, a non-standard port, very short timeout, and 0 retries
    # to encourage a quick failure without actual network dependency if possible.
    # The primary check is that the method executes and returns a boolean.
    result = validator.validate_snmpv2_credentials(
        host="127.0.0.1",
        community_string="smoke_test_community",
        port=16100,  # Non-standard port
        timeout=0.1, # Very short timeout
        retries=0    # No retries
    )
    assert isinstance(result, bool), "validate_snmpv2_credentials should return a boolean."
    # For a smoke test, we typically expect False as no real agent should respond.
    # However, the isinstance check is the crucial part for a smoke test.
    # Depending on how PySNMP handles immediate connection refusals vs timeouts,
    # it might return False quickly.
    print(f"SNMPv2 smoke test result: {result}")


def test_smoke_validate_snmpv3_call_and_return_type():
    """
    Smoke test for SnmpValidator.validate_snmpv3_credentials.
    Checks if the method can be called and returns a boolean value.
    Uses parameters that should lead to a quick local failure.
    """
    validator = SnmpValidator()
    # Using localhost, non-standard port, noAuthNoPriv for simplicity,
    # very short timeout, and 0 retries.
    result = validator.validate_snmpv3_credentials(
        host="127.0.0.1",
        user="smoke_test_user",
        auth_protocol="usmNoAuthProtocol", # Simplest case
        priv_protocol="usmNoPrivProtocol", # Simplest case
        port=16100,  # Non-standard port
        timeout=0.1, # Very short timeout
        retries=0    # No retries
    )
    assert isinstance(result, bool), "validate_snmpv3_credentials should return a boolean."
    # Similar to v2, expecting False, but the type check is key.
    print(f"SNMPv3 smoke test result: {result}")

def test_smoke_snmpv2_instantiation_and_call():
    """
    Ensures SnmpValidator can be instantiated and validate_snmpv2_credentials called.
    Focuses on basic call execution and expecting False due to invalid parameters.
    """
    validator = SnmpValidator()
    # These parameters are intentionally invalid for a real SNMP agent but ensure the method logic is traversed.
    result = validator.validate_snmpv2_credentials(host="localhost", community_string="invalid_community_for_smoke_test")
    assert result is False, "Expected False for invalid SNMPv2 parameters in smoke test."

def test_smoke_snmpv3_instantiation_and_call():
    """
    Ensures SnmpValidator can be instantiated and validate_snmpv3_credentials called.
    Focuses on basic call execution and expecting False due to invalid parameters.
    """
    validator = SnmpValidator()
    # Minimal parameters, expecting failure.
    result = validator.validate_snmpv3_credentials(host="localhost", user="smoke_test_user_v3")
    assert result is False, "Expected False for invalid SNMPv3 parameters in smoke test."
