# Application Logging with Loguru and OpenTelemetry Integration

## Overview
This document explains how to use the application's Loguru-based logging system and how to integrate it with an OpenTelemetry collector for centralized log management.

## Using the Application Logger (`src/utils/logger.py`)

### Initialization
The logger is initialized automatically when `src/utils/logger.py` is first imported. No explicit initialization is typically needed in your application modules.

### Getting a Logger Instance
To use the logger in your Python modules:
```python
from src.utils.logger import logger

# Now you can use the logger instance
logger.info("This is an informational message.")
logger.error("This is an error message.", extra={"custom_field": "custom_value"})
```

### Log Levels
The log level can be configured via the `LOG_LEVEL` environment variable. Supported levels are TRACE, DEBUG, INFO, SUCCESS, WARNING, ERROR, CRITICAL. The default level is INFO.

Loguru messages are automatically sent to:
1. Standard Error (console).
2. An OpenTelemetry pipeline (if configured, see below).

### Structured Logging & Custom Attributes
When logging, you can include extra information as keyword arguments to the logging methods. These will be included in the `extra` field of the Loguru record and automatically passed as attributes in the OpenTelemetry LogRecord.
```python
logger.info("User logged in.", extra={"username": "john.doe", "ip_address": "192.168.1.100"})
```

## Integrating with OpenTelemetry Collector

The logger in `src/utils/logger.py` is pre-configured to send logs to an OpenTelemetry logging pipeline. Currently, it uses a `ConsoleLogExporter` which prints OpenTelemetry logs to standard output in JSON format. To send logs to an OpenTelemetry collector, you would typically modify `src/utils/logger.py` to use an `OTLPLogExporter`.

### Step 1: Modify `logger.py` to use OTLP Exporter (Conceptual)
*(This step is for when you're ready to send to a collector. For now, the `ConsoleLogExporter` is active).*

To send logs to an OTLP endpoint (the collector), you would typically change the exporter in `src/utils/logger.py`.

Locate the section where `ConsoleLogExporter` is set up:
```python
# In src/utils/logger.py (current setup)
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor, ConsoleLogExporter
# ...
log_exporter = ConsoleLogExporter() # <--- CURRENT
# ...
```

You would replace `ConsoleLogExporter` with `OTLPLogExporter` and configure its endpoint:
```python
# Conceptual change for OTLP
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter # Or http
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
# ...
# Configure the OTLP exporter to send to your collector
# Ensure opentelemetry-exporter-otlp-proto-grpc (or http) is in requirements.txt
log_exporter = OTLPLogExporter(
    endpoint="http://localhost:4317",  # Default OTLP gRPC endpoint
    # insecure=True # Use if your collector is not using TLS
)
# ...
```
**Note:** You'd also need to add `opentelemetry-exporter-otlp-proto-grpc` or `opentelemetry-exporter-otlp-proto-http` to `requirements.txt`.

### Step 2: Set up an OpenTelemetry Collector
You need an OpenTelemetry Collector instance running. You can download it from the [OpenTelemetry releases page](https://github.com/open-telemetry/opentelemetry-collector-releases/releases).

Create a configuration file for the collector (e.g., `otel-collector-config.yaml`):

```yaml
receivers:
  otlp:
    protocols:
      grpc:
        endpoint: 0.0.0.0:4317 # Listens for OTLP gRPC logs from the application
      http:
        endpoint: 0.0.0.0:4318 # Optional: listens for OTLP HTTP logs

exporters:
  # Exporter 1: Logging to the collector's console (for debugging)
  logging:
    loglevel: debug

  # Exporter 2: (Example) Sending to a backend like Jaeger, Zipkin, or other OTLP-compatible system
  # otlphttp/jaeger:
  #   endpoint: "http://jaeger-collector:14268/api/traces" # Adjust for your backend

processors:
  batch:
  # Optional: Filter logs (see Filtering section below)
  # filter/include_errors:
  #   logs:
  #     include:
  #       match_type: strict
  #       severity_number:
  #         min: 17 # ERROR severity number in OpenTelemetry (ERROR:17, WARN:13, INFO:9, DEBUG:5)

service:
  pipelines:
    logs: # Pipeline for logs
      receivers: [otlp]
      processors: [batch] # Add 'filter/include_errors' here if using the example filter
      exporters: [logging] # Change to your desired backend exporter(s), e.g., [logging, otlphttp/jaeger]
```

### Step 3: Run the Collector
Run the collector with your configuration file:
```bash
./otelcol-contrib --config ./otel-collector-config.yaml
```
(Use `otelcol` if you downloaded the core version, `otelcol-contrib` for the version with more components).

### Step 4: Configure Application to Target Collector
If you modified `src/utils/logger.py` to use `OTLPLogExporter` (Step 1), ensure the `endpoint` matches where your collector is accessible. Environment variables like `OTEL_EXPORTER_OTLP_ENDPOINT` can also often be used to configure the exporter's target.

## Filtering Logs in the OpenTelemetry Collector
OpenTelemetry Collector offers powerful filtering capabilities using the [Filter Processor](https://github.com/open-telemetry/opentelemetry-collector-contrib/tree/main/processor/filterprocessor).

**Example: Filtering for ERROR level logs or higher**

1.  **Define the filter processor** in your `otel-collector-config.yaml` under `processors`:
    ```yaml
    processors:
      batch:
      filter/error_logs_only:
        logs:
          # Include logs with severity number greater than or equal to ERROR (17)
          # See OpenTelemetry Semantic Conventions for severity numbers
          include:
            match_type: expr
            expressions:
              - 'IsMatch(body, ".*ERROR.*")' # Example: If Loguru sends level name in body
              - 'severity_number >= 17'
          # Alternatively, to exclude certain logs:
          # exclude:
          #   match_type: strict
          #   attributes:
          #     http.status_code: 200
    ```

2.  **Add the filter processor to your logs pipeline** in `otel-collector-config.yaml` under `service.pipelines.logs.processors`:
    ```yaml
    service:
      pipelines:
        logs:
          receivers: [otlp]
          processors: [batch, filter/error_logs_only] # Add your filter here
          exporters: [logging]
    ```
This example `filter/error_logs_only` would only allow logs with a severity number corresponding to ERROR or higher to pass through to the exporters. You can use `expr` for more complex conditions based on log body or attributes. Refer to the Filter Processor documentation for more details on `match_type` and expression syntax.

## Further Reading
- [Loguru Documentation](https://loguru.readthedocs.io/en/stable/)
- [OpenTelemetry Python Logging SDK](https://opentelemetry-python.readthedocs.io/en/latest/sdk/logs.html)
- [OpenTelemetry Collector Configuration](https://opentelemetry.io/docs/collector/configuration/)
- [OpenTelemetry Semantic Conventions for Logs](https://opentelemetry.io/docs/specs/semconv/general/logs/)
- [OTLP Exporter Configuration](https://opentelemetry.io/docs/languages/python/exporters/#otlp)
- [Filter Processor](https://github.com/open-telemetry/opentelemetry-collector-contrib/tree/main/processor/filterprocessor)
