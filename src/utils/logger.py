import os
import sys
import datetime

from loguru import logger

# --- OpenTelemetry Imports ---
from opentelemetry import _logs as otel_logs # Adjusted import
from opentelemetry.sdk._logs import LoggerProvider # Adjusted import
from opentelemetry.sdk._logs.export import SimpleLogRecordProcessor, ConsoleLogExporter # Adjusted import
from opentelemetry.sdk.resources import Resource
# SeverityNumber will be accessed via otel_logs.SeverityNumber
# from opentelemetry.logs import SeverityNumber # Original

# --- Loguru Configuration ---

# Remove the default handler to prevent duplicate logs if the module is reloaded.
logger.remove()

# Determine log level from environment variable or default to INFO
log_level = os.environ.get("LOG_LEVEL", "INFO").upper()
valid_log_levels = ["TRACE", "DEBUG", "INFO", "SUCCESS", "WARNING", "ERROR", "CRITICAL"]
if log_level not in valid_log_levels:
    log_level = "INFO"

# Standard stderr logger configuration
log_format = "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} - {message}"
logger.add(
    sys.stderr,
    level=log_level,
    format=log_format,
    colorize=True,
    backtrace=True,
    diagnose=True
)

# --- OpenTelemetry Logging Setup ---

# 1. Create a Resource for your application
resource = Resource(attributes={
    "service.name": os.environ.get("OTEL_SERVICE_NAME", "your-application-name"),
    # Add other resource attributes as needed
})

# 2. Create a LoggerProvider
logger_provider = LoggerProvider(resource=resource)

# 3. Create a ConsoleLogExporter (for now, to see logs in console)
#    Default formatter `lambda record: record.to_json()` fails because the API LogRecord doesn't have to_json.
#    The exporter receives SDK's LogData, and its `log_record` attribute is the API LogRecord.
#    We need to format the LogData object itself, or manually format the API LogRecord.
import json

def custom_otel_formatter(api_record) -> str: # Parameter is the API LogRecord itself
    output = {
        "timestamp": api_record.timestamp,
        "observed_timestamp": api_record.observed_timestamp,
        "trace_id": api_record.trace_id, # Will be None if not set
        "span_id": api_record.span_id, # Will be None if not set
        "trace_flags": api_record.trace_flags, # Will be None if not set
        "severity_text": api_record.severity_text,
        "severity_number": api_record.severity_number.value if api_record.severity_number else None,
        "body": api_record.body,
        "attributes": api_record.attributes,
        # Resource attributes are part of the SDK's LogData envelope.
        # The ConsoleLogExporter passes only the api_record to the formatter,
        # so we can't easily access the LoggerProvider's resource here.
        # A real OTLP exporter would correctly include the resource.
        "resource_attributes_note": "Resource attributes from LoggerProvider are not included by this custom console formatter."
    }
    return json.dumps(output) + os.linesep

console_exporter = ConsoleLogExporter(formatter=custom_otel_formatter)

# 4. Create a SimpleLogRecordProcessor and add the exporter
log_processor = SimpleLogRecordProcessor(console_exporter)
logger_provider.add_log_record_processor(log_processor)

# 5. Set the global LoggerProvider
otel_logs.set_logger_provider(logger_provider)

# --- Loguru to OpenTelemetry Sink ---

# Mapping Loguru levels to OpenTelemetry SeverityNumber
LOGURU_TO_OTEL_SEVERITY = {
    "TRACE": otel_logs.SeverityNumber.TRACE,
    "DEBUG": otel_logs.SeverityNumber.DEBUG,
    "INFO": otel_logs.SeverityNumber.INFO,
    "SUCCESS": otel_logs.SeverityNumber.INFO2, # OTel doesn't have SUCCESS, mapping to INFO2 or INFO3
    "WARNING": otel_logs.SeverityNumber.WARN,
    "ERROR": otel_logs.SeverityNumber.ERROR,
    "CRITICAL": otel_logs.SeverityNumber.FATAL,
}

class OpenTelemetrySink:
    def __init__(self):
        # Get an OTel logger. The name can be module-specific or app-specific.
        self.otel_logger = otel_logs.get_logger("loguru", logger_provider=logger_provider)

    def write(self, message):
        record = message.record

        # Transform Loguru record to OpenTelemetry LogRecord fields
        otel_severity_number = LOGURU_TO_OTEL_SEVERITY.get(record["level"].name, otel_logs.SeverityNumber.UNSPECIFIED)

        # Timestamp: Loguru time is datetime, OTel needs nanoseconds since epoch
        otel_timestamp = int(record["time"].timestamp() * 1_000_000_000)

        otel_body = record["message"]

        otel_attributes = {
            "loguru.level": record["level"].name,
            "loguru.module": record["module"],
            "loguru.function": record["function"],
            "loguru.file.path": record["file"].path,
            "loguru.file.name": record["file"].name,
            "loguru.line": record["line"],
            "loguru.thread.id": record["thread"].id,
            "loguru.process.id": record["process"].id,
        }
        # Add any 'extra' fields from Loguru
        if record["extra"]:
            for k, v in record["extra"].items():
                otel_attributes[f"loguru.extra.{k}"] = str(v) # Ensure attributes are simple types

        log_record = otel_logs.LogRecord(
            timestamp=otel_timestamp,
            observed_timestamp=otel_timestamp, # Can be different if the log was delayed
            severity_text=record["level"].name,
            severity_number=otel_severity_number,
            body=otel_body,
            attributes=otel_attributes,
        )
        self.otel_logger.emit(log_record)

# Add the OpenTelemetry sink to Loguru
# The level for this sink should also be controlled by log_level or set to a minimum (e.g., DEBUG)
# if OTel is expected to handle all severities sent by Loguru.
# For now, let's use the same log_level as the stderr sink.
try:
    otel_sink = OpenTelemetrySink()
    logger.add(otel_sink.write, level=log_level, format="{message}") # Format not really used by sink
    logger.info("Successfully initialized OpenTelemetry sink for Loguru.")
except Exception as e:
    logger.error(f"Failed to initialize OpenTelemetry sink: {e}", exception=True)


# Export the configured logger instance
__all__ = ["logger"]

# --- Example Usage ---
if __name__ == "__main__":
    logger.info("This is an info message from Loguru (via stderr).")
    logger.bind(user="test_user", transaction_id="12345").warning(
        "This is a warning with extra parameters, also sent to OTel."
    )
    logger.debug("This debug message should appear if LOG_LEVEL is DEBUG or TRACE (via stderr).")

    # Test exception logging
    try:
        x = 1 / 0
    except ZeroDivisionError:
        logger.exception("A wild ZeroDivisionError appeared!")

    logger.info("Testing complete. Check console for both Loguru formatted logs and OTel JSON logs.")
