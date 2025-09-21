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
- **Formatting**: Never use Ruff to reformat.

### Naming Conventions

- **Functions/variables**: snake_case
- **Classes**: PascalCase  
- **Constants**: UPPER_CASE (see `constants.py`)
- **INDEXES**: Use decriptive names such as each_point, each_name,
normally derived from the range instead of i, or idx
- Avoid single-letter variable names

### Code Structure

- Functions should be 20-30 lines maximum
- Use type hints (imported from `__future__ import annotations`)
- Include docstrings for classes and functions
- Use specific exception handling with meaningful error messages
- Helper functions should be placed AFTER the functions they help

### Critical Code Quality Requirements

- **Type Annotations**: ALWAYS include proper type hints for all function parameters and return values
- **No Trailing Whitespace**: Ensure no trailing spaces at end of lines (ruff will flag W293)
- **Proper Parameter Types**: Use specific types like `pd.DataFrame` instead of generic `object` or missing annotations
- **Import Consistency**: Follow the existing import pattern with `from __future__ import annotations`

### Ruff Warnings and Code Quality

- **Address ALL ruff warnings**: Never ignore complexity warnings (C901, C902) but may ignore too many arguments warnings (PLR0913)
- **Function Complexity**: If ruff flags complexity issues, refactor by:
  - Breaking large functions into smaller helper functions
  - Extracting complex logic into separate methods
  - Reducing nested conditionals and loops
- **Statement Count**: Keep functions under the complexity threshold by splitting functionality
- **Refactoring Priority**: Always refactor code that triggers complexity warnings before considering the task complete

## Dependencies

Key external dependencies include:

- **PySide6**: GUI framework
- **matplotlib**: Primary plotting library
- **pyqtgraph**: Alternative plotting library
- **pandas**: Data manipulation
- **numpy**: Numerical operations
- **scipy**: Statistical functions
- **sklearn**: Machine learning utilities (manifold learning)

## Spaces Application Guidelines

When working with the Spaces application, follow these domain-specific patterns and conventions:

### GUI Architecture

- **Dictionary-driven GUI**: Spaces uses a large GUI (150+ menu items) built with PySide6 using a dictionary-based system to add items
- **Menu Organization**: GUI is split across separate files corresponding to menus (`filemenu.py`, `editmenu.py`, etc.) to manage the 100+ commands
- **Icons and Toolbar**: Most commands have icons and some are used in a toolbar for common operations

### Error Handling and User Experience

- **Exception-based Error Handling**: All error conditions are trapped and handled by custom exceptions (see `exceptions.py`) to inform users so they can resolve problems
- **Dependency Checking**: Many commands check for dependencies (see `dependencies.py`) that must be satisfied before execution since users may get ahead of themselves
- **User Dialogs**: Commands requiring additional user input use dialogs (see `dialogs.py`) to obtain information after command selection

### Application Flow and Interaction

- **Director Pattern**: The `director` instance handles user interaction and often relies on `common` for shared functions
- **Tab System**: GUI uses tabs to display:
  - **Plot**: For visualizations
  - **Output**: For recent command results
  - **Gallery**: For plot history
  - **Log**: For output history
  - **Record**: For print-oriented output
- **Focus Management**: Commands with plots set focus to Plot tab, otherwise to Output tab

### Plotting Architecture

- **Dual Presentation Layers**: Two plotting systems available:
  - `matplotlib_plots.py` for matplotlib-based plots
  - `pyqtgraph_plots.py` for pyqtgraph-based plots
  - Common functions in corresponding `_common` files

### Command Structure Standards

All new commands should follow this consistent structure:

- **Class Structure**: Most command classes have:
  - `__init__` method containing strings used in error messaging
  - `exec` method that should be kept flat (minimal nesting)
- **Exception Handling**: All exceptions should be raised below the `exec` method, not within it
- **Avoid hasattr**: Don't use `hasattr()` - there's likely a checking function in `director` instead
- **Follow Patterns**: Study existing commands to maintain consistency in structure and flow

### Data Presentation and Tables

- **Table Builder System**: The Output tab uses table widgets built with `table_builder` which supports different table types (square, statistical, etc.)
- **Widget Organization**: Spaces has 100+ widgets organized in a dictionary called `widget_dict`

### Plot Types and Consistency

- **Plot Type Concept**: Spaces uses a plot type system that allows for reuse of common plot types and ensures consistency of presentation across the application
- **Standardized Visualization**: Follow existing plot type patterns when creating new visualizations to maintain consistency

### Features and Data Validation

- **Feature System**: Spaces uses a feature concept to prevent inconsistent data requests from users
- **Data Type Handling**: Features handle data types and expect file formats to supply metadata for consistency testing
- **Metadata Integration**: File formats should provide metadata that feeds into the consistency testing process

### User Experience and Documentation

- **Command Explanations**: All commands have explanations available to users
- **Verbosity Toggle**: Default mode is Terse; users can toggle verbosity to include detailed explanations
- **Help Integration**: Ensure new commands include proper explanations that work with the verbosity toggle system

### Development Best Practices

- **Live User Focus**: Remember that Spaces is designed for interactive use by live users, so prioritize clear error messages and graceful degradation
- **Check Dependencies First**: Always validate dependencies before command execution
- **Use Director Functions**: Leverage existing checking functions in `director` rather than implementing custom attribute checking

## Archive Structure

The `archive/` directory contains historical versions and development snapshots, organized chronologically with descriptive folder names indicating major refactoring milestones.
