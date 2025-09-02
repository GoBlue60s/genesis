# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is a Python GUI application called "Spaces" for multidimensional scaling (MDS) and statistical analysis. The application uses PySide6 for the GUI framework and provides various data visualization and analysis capabilities.

## Development Commands

### Linting and Code Quality

```bash
# Run ruff linter (configured in pyproject.toml)
ruff check .

# Format code with ruff
ruff format .
```

### Running the Application

```bash
# Run the main application
python src/spaces.py
```

### Python Environment

- This project uses a virtual environment (`venv/`)
- Target Python version: 3.13
- Activate the virtual environment before running commands

## Code Architecture

### Main Application Structure

- **Entry Point**: `src/spaces.py` - Contains `MyApplication` class and main execution
- **Core Logic**: `src/common.py` - Contains the main `Spaces` class with data processing logic
- **UI Director**: `src/director.py` - Manages GUI components, plotting, and user interactions
- **Menu System**: Organized into separate modules:
  - `src/filemenu.py` - File operations
  - `src/editmenu.py` - Edit operations
  - `src/viewmenu.py` - View controls
  - `src/modelmenu.py` - Model operations
  - `src/transformmenu.py` - Data transformations
  - `src/associationsmenu.py` - Association analysis
  - `src/respondentsmenu.py` - Respondent data handling
  - `src/helpmenu.py` - Help and about dialogs

### Key Components

- **Plotting**: Dual plotting system with matplotlib (`matplotlib_plots.py`) and pyqtgraph (`pyqtgraph_plots.py`)
- **Data Tables**: `table_builder.py` - Various table widgets for data display
- **Geometry**: `geometry.py` - Point and coordinate handling
- **Dependencies**: `dependencies.py` - Dependency checking utilities
- **Exceptions**: `exceptions.py` - Custom `SpacesError` exception class

### Data Handling

- Uses pandas for data manipulation
- Supports various statistical analyses including MDS, factor analysis, and correlations
- Works with CSV files and custom configuration formats
- Sample data located in `data/Elections/` with various election datasets

## Code Style Guidelines

This project follows specific coding standards defined in `.github/copilot-instructions.md`:

### Formatting (Enforced by Ruff)

- **Indentation**: Use tabs (not spaces)
- **Line length**: 79 characters maximum
- **Quotes**: Double quotes for string literals
- **Imports**: Standard library, third-party, then local imports

### Naming Conventions

- **Functions/variables**: snake_case
- **Classes**: PascalCase  
- **Constants**: UPPER_CASE (see `constants.py`)
- Avoid single-letter variable names

### Code Structure

- Functions should be 20-30 lines maximum
- Use type hints (imported from `__future__ import annotations`)
- Include docstrings for classes and functions
- Use specific exception handling with meaningful error messages

### Critical Code Quality Requirements

- **Type Annotations**: ALWAYS include proper type hints for all function parameters and return values
- **No Trailing Whitespace**: Ensure no trailing spaces at end of lines (ruff will flag W293)
- **Proper Parameter Types**: Use specific types like `pd.DataFrame` instead of generic `object` or missing annotations
- **Import Consistency**: Follow the existing import pattern with `from __future__ import annotations`

## Dependencies

Key external dependencies include:

- **PySide6**: GUI framework
- **matplotlib**: Primary plotting library
- **pyqtgraph**: Alternative plotting library
- **pandas**: Data manipulation
- **numpy**: Numerical operations
- **scipy**: Statistical functions
- **sklearn**: Machine learning utilities (manifold learning)

## Archive Structure

The `archive/` directory contains historical versions and development snapshots, organized chronologically with descriptive folder names indicating major refactoring milestones.
