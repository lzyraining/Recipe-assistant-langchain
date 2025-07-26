# Recipe LangChain

Add your project description here.

## Setup

### Installation

```bash
# Install dependencies
uv pip install -e .

# Install development dependencies
uv pip install -e ".[dev]"
```

## Development

### Code Quality Tools

This project uses several code quality tools to maintain consistent code style and catch potential issues:

#### Formatting

- **Black**: Code formatter
  ```bash
  # Format all Python files
  black .
  
  # Check formatting without making changes
  black --check .
  ```

- **isort**: Import sorter
  ```bash
  # Sort imports in all Python files
  isort .
  
  # Check import sorting without making changes
  isort --check .
  ```

#### Linting

- **Flake8**: Style guide enforcement
  ```bash
  # Run flake8 on all Python files
  flake8 .
  ```

- **Ruff**: Fast Python linter
  ```bash
  # Run ruff on all Python files
  ruff check .
  
  # Automatically fix issues where possible
  ruff check --fix .
  ```

### Running All Checks

You can run all code quality checks with:

```bash
# Format code
black .
isort .

# Run linters
flake8 .
ruff check .
```

## Usage

Add usage instructions here.
