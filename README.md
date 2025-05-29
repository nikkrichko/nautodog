# Naurodog CLI Application

Naurodog is a command-line interface (CLI) application built with Python and Click for managing various Datadog configurations and operations.

## Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository_url>
    cd <repository_directory>
    ```

2.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
    *(Note: `requirements.txt` will be updated in a subsequent step to include `click`)*

## Usage

The main entry point for the CLI is `src/naurodog.py`.

### General Help

To see the list of available command groups:
```bash
python src/naurodog.py --help
```

### Group Help

To see commands available within a specific group, use `--help` after the group name. For example, for the `ddsnmpconfig` group:
```bash
python src/naurodog.py ddsnmpconfig --help
```

### Command Usage

To run a specific command, follow this pattern:
`python src/naurodog.py <group_name> <command_name> --name <your_name_here>`

For example, to run the `addsnmpv3` command from the `ddsnmpconfig` group:
```bash
python src/naurodog.py ddsnmpconfig addsnmpv3 --name "my_device_01"
```
This will output:
```
Command: addsnmpv3, Name: my_device_01
```

## Command Structure

The application is organized into the following command groups:

*   **`ddsnmpconfig`**: Commands for SNMP configuration.
*   **`ddmonitor`**: Commands for managing Datadog monitors.
*   **`ddmainconfig`**: Commands for main Datadog configurations.
*   **`ddagent`**: Commands related to the Datadog agent.
*   **`report`**: Commands for generating various reports.

Detailed examples for each command can be found in `docs/examples.md`.
