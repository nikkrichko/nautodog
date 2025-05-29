# Naurodog CLI Command Examples

This document provides examples for each command available in the Naurodog CLI application.

## Group: `ddsnmpconfig`

Commands for SNMP configuration.

### `addsnmpv3`
*   **Description:** (Mock) Adds a new SNMPv3 device configuration.
*   **Usage:**
    ```bash
    python src/naurodog.py ddsnmpconfig addsnmpv3 --name "device_snmpv3_profile_name"
    ```

### `addsnmpv2`
*   **Description:** (Mock) Adds a new SNMPv2 device configuration.
*   **Usage:**
    ```bash
    python src/naurodog.py ddsnmpconfig addsnmpv2 --name "device_snmpv2_community_string"
    ```

### `uploadcustopprofile`
*   **Description:** (Mock) Uploads a custom SNMP profile.
*   **Usage:**
    ```bash
    python src/naurodog.py ddsnmpconfig uploadcustopprofile --name "custom_profile_file_path"
    ```

### `createlocalconfig`
*   **Description:** (Mock) Creates a local SNMP configuration file.
*   **Usage:**
    ```bash
    python src/naurodog.py ddsnmpconfig createlocalconfig --name "local_config_name"
    ```

### `verifydevices`
*   **Description:** (Mock) Verifies connectivity or configuration of SNMP devices.
*   **Usage:**
    ```bash
    python src/naurodog.py ddsnmpconfig verifydevices --name "device_group_to_verify"
    ```

### `autodiscoveryv2`
*   **Description:** (Mock) Runs autodiscovery for SNMPv2 devices.
*   **Usage:**
    ```bash
    python src/naurodog.py ddsnmpconfig autodiscoveryv2 --name "ip_range_or_subnet"
    ```

### `autodiscoveryv3`
*   **Description:** (Mock) Runs autodiscovery for SNMPv3 devices.
*   **Usage:**
    ```bash
    python src/naurodog.py ddsnmpconfig autodiscoveryv3 --name "ip_range_or_subnet_v3"
    ```

### `rollbackconfig`
*   **Description:** (Mock) Rolls back SNMP configuration to a previous state.
*   **Usage:**
    ```bash
    python src/naurodog.py ddsnmpconfig rollbackconfig --name "backup_id_or_timestamp"
    ```

### `revokedevice`
*   **Description:** (Mock) Revokes access or removes an SNMP device.
*   **Usage:**
    ```bash
    python src/naurodog.py ddsnmpconfig revokedevice --name "device_id_to_revoke"
    ```

## Group: `ddmonitor`

Commands for managing Datadog monitors.

### `addreachablemonitor`
*   **Description:** (Mock) Adds a reachability monitor for a host or IP.
*   **Usage:**
    ```bash
    python src/naurodog.py ddmonitor addreachablemonitor --name "host_or_ip_to_monitor"
    ```

### `addinterfacemonitor`
*   **Description:** (Mock) Adds an interface monitor for a device.
*   **Usage:**
    ```bash
    python src/naurodog.py ddmonitor addinterfacemonitor --name "device_and_interface_specifier"
    ```

### `addmonitorsbyrules`
*   **Description:** (Mock) Adds multiple monitors based on predefined rules.
*   **Usage:**
    ```bash
    python src/naurodog.py ddmonitor addmonitorsbyrules --name "rule_set_name"
    ```

## Group: `ddmainconfig`

Commands for main Datadog configurations.

### `addtag`
*   **Description:** (Mock) Adds a tag to a specified resource or configuration.
*   **Usage:**
    ```bash
    python src/naurodog.py ddmainconfig addtag --name "tag_key_value_pair"
    ```

### `apikey`
*   **Description:** (Mock) Manages or sets the Datadog API key.
*   **Usage:**
    ```bash
    python src/naurodog.py ddmainconfig apikey --name "api_key_value_or_action"
    ```

## Group: `ddagent`

Commands related to the Datadog agent.

### `ddastatus`
*   **Description:** (Mock) Gets the status of the Datadog agent.
*   **Usage:**
    ```bash
    python src/naurodog.py ddagent ddastatus --name "agent_instance_name_or_all"
    ```

### `ddaerrors`
*   **Description:** (Mock) Retrieves errors from the Datadog agent logs.
*   **Usage:**
    ```bash
    python src/naurodog.py ddagent ddaerrors --name "error_filter_or_timeframe"
    ```

### `ddalogs`
*   **Description:** (Mock) Fetches logs from the Datadog agent.
*   **Usage:**
    ```bash
    python src/naurodog.py ddagent ddalogs --name "log_query_parameters"
    ```

### `dduploadconfigs`
*   **Description:** (Mock) Uploads agent configuration files.
*   **Usage:**
    ```bash
    python src/naurodog.py ddagent dduploadconfigs --name "config_file_path_to_upload"
    ```

### `dddownloadconfigs`
*   **Description:** (Mock) Downloads agent configuration files.
*   **Usage:**
    ```bash
    python src/naurodog.py ddagent dddownloadconfigs --name "config_file_to_download"
    ```

### `configconsistency`
*   **Description:** (Mock) Checks for configuration consistency across agents or instances.
*   **Usage:**
    ```bash
    python src/naurodog.py ddagent configconsistency --name "scope_of_check"
    ```

### `downloadconfigs`
*   **Description:** (Mock) Generic command to download configurations (potentially broader than agent configs).
*   **Usage:**
    ```bash
    python src/naurodog.py ddagent downloadconfigs --name "configuration_type_to_download"
    ```

### `uploadconfigs`
*   **Description:** (Mock) Generic command to upload configurations.
*   **Usage:**
    ```bash
    python src/naurodog.py ddagent uploadconfigs --name "configuration_file_to_upload"
    ```

## Group: `report`

Commands for generating various reports.

### `ndreport_devices`
*   **Description:** (Mock) Generates a report on Naurodog managed devices.
*   **Usage:**
    ```bash
    python src/naurodog.py report ndreport_devices --name "report_parameters_devices"
    ```

### `sldreport_devices`
*   **Description:** (Mock) Generates an SLD report for devices.
*   **Usage:**
    ```bash
    python src/naurodog.py report sldreport_devices --name "report_parameters_sld"
    ```

### `ddreportmonitorcoverage`
*   **Description:** (Mock) Generates a report on Datadog monitor coverage.
*   **Usage:**
    ```bash
    python src/naurodog.py report ddreportmonitorcoverage --name "coverage_report_scope"
    ```
