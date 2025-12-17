
# Spaces

A Python GUI application for multidimensional scaling (MDS) and statistical analysis, providing comprehensive data visualization and analysis capabilities for research and data exploration. Has extensive tools for one on one rivalry competitions such as political candidates, market leaders, etc.

## Overview

Spaces is a feature-rich desktop application built with PySide6 that enables users to perform various statistical analyses including multidimensional scaling, factor analysis, and correlation studies. The application provides an intuitive interface with multiple visualization options and extensive data manipulation tools. Includes segmentation tools for identifying core supporters, base supporters, likely supporters, battleground targets with convertible individuals. Also identifies dimesnions that maximally separate the population. Uses data for surveys of individual as voters, buyers, etc having preferences measuredwith thermometer questions where respondents rate candidates, products, groups on scales where 0 is least prefered and 100 are most prefered.  

## Features

### Core Functionality

- **Multidimensional Scaling (MDS)**: Advanced MDS algorithms for dimensionality reduction and data visualization
- **Statistical Analysis**: Comprehensive statistical tools including factor analysis, clustering and correlation analysis
- **Data Visualization**: Dual plotting system with both matplotlib and pyqtgraph backends
- **Data Import/Export**: Support for CSV files and custom configuration formats
- **Interactive GUI**: Over 150 menu items organized across multiple menu categories

### Analysis Capabilities

- Association analysis
- Respondent data handling
- Spatial data transformations
- Advanced modeling operations
- View controls and customization

### User Interface

- **Tabbed Interface**:
  - Plot tab for visualizations
  - Output tab for command results as tables
  - Gallery tab for plot history
  - Log tab for output history
  - Record tab for print-oriented output
- **Menu System**: Organized across separate modules for uasbility
- **Toolbar**: Quick access to common operations with icons
- **Error Handling**: Comprehensive exception handling with user-friendly error messages

## Installation

### Prerequisites

- Python 3.14 (recommended)
- Virtual environment (recommended)

### Dependencies

The application requires the following key packages:

- **PySide6**: GUI framework
- **matplotlib**: Primary plotting library
- **pyqtgraph**: Alternative plotting library
- **pandas**: Data manipulation
- **numpy**: Numerical operations
- **scipy**: Statistical functions
- **scikit-learn**: Machine learning utilities (manifold learning)

### Setup

1. Clone the repository
2. Create and activate a virtual environment:

   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate

3. Install dependencies (requirements file to be added)

- Tested with latest version of libraries
- Older version may work as well

4. Run the application: # noqa: MD029

   ```bash
   python src/spaces.py
   ```

## Usage

Launch the application by running:

```bash
python src/spaces.py
```

The application provides a comprehensive menu system organized into logical categories:

- **File**: Data import/export operations
- **Edit**: Command editing operations
- **View**: Display and visualization controls
- **Transform**: Spatial transformation tools
- **Associations**: Association analysis tools
- **Model**: Statistical modeling operations
- **Respondents**: Respondent data management and specialized visiualizations
- **Help**: Documentation and about information

## Development

### Code Quality

The project uses Ruff for linting:

```bash
# Run linter
ruff check .

### Code Structure

- **Entry Point**: `src/spaces.py`
- **Core Logic**: `src/common.py` (main Spaces class)
- **UI Management**: `src/director.py`
- **Menu Modules**: Separate files for each menu category
- **Plotting**: Dual system with matplotlib and pyqtgraph support
- **Output data Tables**: Custom table widgets in `table_builder.py`

### Testing

Testing framework setup is planned using PyTest (not yet implemented).

### Coding Standards

- **Indentation**:  2 spaces
- **Line length**: 79 characters maximum
- **Quotes**: Double quotes for string literals
- **Type hints**: Required for all function parameters and return values
- **Functions**: Maximum 20-30 lines
- **Variables**: Descriptive names using snake_case

## Sample Data

The application includes sample datasets in the `data/Elections/` directory with various election datasets spanning multiple years (1976-2020) for testing and demonstration purposes.

## Architecture

### GUI Design

- Dictionary-driven GUI system for managing 150+ menu items
- Tab-based interface for different output types
- Icon support with toolbar integration
- Exception-based error handling for user experience

### Data Processing

- Feature system for data validation and consistency
- Dependency checking to ensure proper command execution
- Metadata integration for file format consistency

### Plotting System

- Dual presentation layers (matplotlib and pyqtgraph)
- Standardized plot types for consistency
- Plot history and gallery management

## Contributing

This is not an open-source project, but there is a public GitHub repository available for reference and collaboration.

### Development Guidelines

- Follow the established coding standards in `.github/copilot-instructions.md`
- Use the existing command structure for new features
- Implement proper error handling with custom exceptions
- Follow the Director pattern for user interactions
- Maintain consistency with existing plot types and table widgets
- Use long descriptive variable names
- Avoid relying on comments in code
- For indices avoid simpliestic i, or idx
- Name indices based on range, such as each_point, each_dimension

## License

[License information to be added]

## Contact

Ed Schneider - [ejschnei@umich.edu](mailto:ejschnei@umich.edu)
