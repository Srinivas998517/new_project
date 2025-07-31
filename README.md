# Research Paper Fetcher

This project is a Python program designed to fetch research papers from PubMed based on a user-specified query. It identifies papers with at least one author affiliated with a pharmaceutical or biotech company and returns the results as a CSV file or prints them to the console.

## Table of Contents
- [How the Code is Organized](#how-the-code-is-organized)
- [Installation Instructions](#installation-instructions)
- [Execution Instructions](#execution-instructions)
- [Tools and Libraries Used](#tools-and-libraries-used)
- [Identification of Non-Academic Authors](#identification-of-non-academic-authors)
- [Notes](#notes)

## How the Code is Organized
The project is structured into two main parts: a core module and a command-line interface (CLI) program. This modular approach ensures separation of concerns, making the code more maintainable and reusable.

- `research_paper_fetcher/`: This is the main package directory.
    - `__init__.py`: Makes `research_paper_fetcher` a Python package.
    - `pubmed_module.py`: Contains the core logic for interacting with the PubMed API, fetching paper details, parsing XML responses, identifying non-academic affiliations, and preparing data for output.
    - `cli.py`: This is the command-line interface script. It uses the `argparse` module to handle command-line arguments and orchestrates calls to functions within `pubmed_module.py`. It serves as the entry point for the `get-papers-list` command.

## Installation Instructions

This project uses [Poetry](https://python-poetry.org/) for dependency management and packaging.

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/your-username/research-paper-fetcher.git](https://github.com/your-username/research-paper-fetcher.git)
    cd research-paper-fetcher
    ```
    *(Replace `your-username` with your actual GitHub username and `research-paper-fetcher` with your repository name.)*

2.  **Install dependencies using Poetry:**
    ```bash
    poetry install
    ```
    This command will create a virtual environment and install all necessary dependencies (e.g., `requests`, `biopython`) as specified in `pyproject.toml`.

## Execution Instructions

The program can be run using the `get-papers-list` command provided by Poetry.

**Usage:**

```bash
poetry run get-papers-list <query> [options]