# Project Title

This is a CLI Click application for integrating Nautobot data and executing API calls within Datadog.

## Installation and Setup

To get this project up and running on your local machine, follow these steps. It's highly recommended to use a Python virtual environment to manage dependencies and avoid conflicts with other projects or your system's Python installation.

### 1. Create and Activate a Virtual Environment

A virtual environment provides an isolated space for your Python packages.

**On Unix-like systems (Linux/macOS - bash/zsh):**
\`\`\`bash
# Create the virtual environment
python3 -m venv .venv

# Activate the virtual environment
source .venv/bin/activate
\`\`\`
After activation, your shell prompt will usually change to indicate that the virtual environment is active (e.g., `(.venv) your-prompt$`).

**On Windows (PowerShell/CMD):**
\`\`\`powershell
# Create the virtual environment (CMD or PowerShell)
python -m venv .venv

# Activate the virtual environment (CMD)
# .venv\Scripts\activate.bat

# Activate the virtual environment (PowerShell)
# .\.venv\Scripts\Activate.ps1
\`\`\`
If you encounter issues running `Activate.ps1` in PowerShell, you might need to adjust your execution policy. You can do this for the current process by running:
`Set-ExecutionPolicy RemoteSigned -Scope Process`

### 2. Install Dependencies

Once your virtual environment is activated, install the required Python packages using pip and the `requirements.txt` file:
\`\`\`bash
pip install -r requirements.txt
\`\`\`

### Automated Setup Scripts

To simplify the setup process, you can use the provided scripts which will create the virtual environment and install dependencies automatically.

**For Unix-like systems (bash/zsh):**
Make the script executable (if you haven't already):
\`\`\`bash
chmod +x scripts/setup_venv.sh
\`\`\`
Then run the script:
\`\`\`bash
./scripts/setup_venv.sh
\`\`\`
Or directly using bash:
\`\`\`bash
bash scripts/setup_venv.sh
\`\`\`
Follow the on-screen prompts. To activate the environment after the script completes, run `source .venv/bin/activate`.

**For Windows (PowerShell):**
Ensure your PowerShell execution policy allows script execution. Then run:
\`\`\`powershell
.\scripts\setup_venv.ps1
\`\`\`
Follow the on-screen prompts. To activate the environment after the script completes, run `.\.venv\Scripts\Activate.ps1`.

## Basic Usage

Here's how to run the basic `hello` command provided by the CLI.

**Example: Running the 'hello' command**

Ensure your virtual environment is activated and you are in the project's root directory.
\`\`\`bash
python src/main.py hello YourName
\`\`\`

**Expected output:**
\`\`\`
Hello, YourName!
\`\`\`

## Documentation

For more detailed information about the project, including guides and API references, please see our main documentation page:

[Project Documentation](docs/index.md)

## Running the tests

Explain how to run the automated tests for this system.

### Break down into end-to-end tests

Explain what these tests test and why.

\`\`\`
Give an example
\`\`\`

### And coding style tests

Explain what these tests test and why.

\`\`\`
Give an example
\`\`\`

## Built With

* [Dropwizard](http://www.dropwizard.io/1.0.2/docs/) - The web framework used
* [Maven](https://maven.apache.org/) - Dependency Management
* [ROME](https://rometools.github.io/rome/) - Used to generate RSS Feeds

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct, and the process for submitting pull requests to us.

## Versioning

We use [SemVer](http://semver.org/) for versioning. For the versions available, see the [tags on this repository](https://github.com/your/project/tags).

## Authors

* **Billie Thompson** - *Initial work* - [PurpleBooth](https://github.com/PurpleBooth)

See also the list of [contributors](https://github.com/your/project/contributors) who participated in this project.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* Hat tip to anyone whose code was used
* Inspiration
* etc
