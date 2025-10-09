from __future__ import annotations


import peek  # noqa: F401
from pyqtgraph.Qt import QtCore
from PySide6.QtWidgets import (
	QLabel,
	QTableWidget,
	QTableWidgetItem,
	QVBoxLayout,
	QWidget,
)
from typing import TYPE_CHECKING

if TYPE_CHECKING:
	from director import Status
	import pandas as pd

from dictionaries import (
	basic_table_dict,
	square_table_dict,
	statistical_table_dict,
	rivalry_table_dict,
)
from exceptions import SpacesError
# ----------------------------------------------------------------------------


class BuildOutputForGUI(QWidget):
	def __init__(self, director: Status) -> None:  # xxxxxxxxxx
		super().__init__()

		director.output_widget_type = "To be determined"
		director.setGeometry(
			1500, 300, director.tab_width, director.tab_height
		)
		gui_output_layout = QVBoxLayout(self)
		if director.include_explanation_when_verbosity_last_set_to_verbose():
			explain = QLabel(director.optionally_explain_what_command_does())
			gui_output_layout.addWidget(explain)
		title_label = QLabel(director.title_for_table_widget)
		gui_output_layout.addWidget(title_label)
		if director.command in director.widget_dict:
			gui_output_as_widget = director.widget_control(director.command)
		else:
			print(
				f"Key: {director.command=} not found in the widget dictionary"
			)
			gui_output_as_widget = None
		if gui_output_as_widget is None:
			return
		gui_output_layout.addWidget(gui_output_as_widget)
		gui_output_layout.addStretch()
		self.setLayout(gui_output_layout)


# --------------------------------------------------------------------------


class BasicTableWidget:
	def __init__(self, director: Status) -> None:
		self._director = director

		# Dictionary for standard (non-square) tables
		self.display_tables_dict = dict(basic_table_dict)

	# ------------------------------------------------------------------------

	def display_table(self, table_name: str) -> QTableWidget:
		"""Create and return a basic table widget"""
		result = None

		if table_name in self.display_tables_dict:
			table_config = self.display_tables_dict[table_name]
			source_name = table_config["source"]
			source = getattr(self._director, source_name)

			data = getattr(source, table_config["data"])

			# Handle row headers
			if isinstance(table_config["row_headers"], list):
				row_headers = table_config["row_headers"]
			else:
				row_headers = getattr(source, table_config["row_headers"])

			# Handle column headers
			if isinstance(table_config["column_headers"], list):
				column_headers = table_config["column_headers"]
			else:
				column_headers = getattr(
					source, table_config["column_headers"]
				)

			row_height = table_config["row_height"]
			format_str = table_config["format"]

			result = self._build_basic_table(
				data, row_headers, column_headers, row_height, format_str
			)
		else:
			print(f"Unknown basic table: {table_name}")
			result = QTableWidget()

		return result

	# ------------------------------------------------------------------------

	def _build_basic_table(
		self,
		data: pd.DataFrame,
		row_headers: list[str],
		column_headers: list[str],
		row_height: int,
		format_str: str,
	) -> QTableWidget:
		"""Build a basic table with the given data and formatting"""
		try:
			# Create the table widget
			table_widget = QTableWidget(data.shape[0], data.shape[1])

			# Use the shared function to fill and format the table data
			self._director.common.fill_table_with_formatted_data(
				table_widget, data, format_str
			)

			# Set headers and visual properties
			self._director.set_column_and_row_headers(
				table_widget, column_headers, row_headers
			)
			self._director.resize_and_set_table_size(table_widget, row_height)
			self._director.output_widget_type = "Table"

		except AttributeError as e:
			print(
				f"Cannot display basic table: Required data not available.\n"
				f"Error: {e!s}"
			)
			return QTableWidget()
		else:
			return table_widget


# --------------------------------------------------------------------------


class SquareTableWidget:
	def __init__(self, director: Status) -> None:
		self._director = director

		# Dictionary-driven configuration for square tables
		self.square_tables_config = dict(square_table_dict)

	def display_table(self, table_name: str) -> QTableWidget:
		"""Create and return a square table widget"""
		if table_name not in self.square_tables_config:
			print(f"Unknown square table: {table_name}")
			return QTableWidget()

		config = self.square_tables_config[table_name]
		source = getattr(self._director, config["source_attr"])
		data = getattr(source, config["data_attr"])
		item_names = getattr(source, config["item_names_attr"])
		row_height = config["row_height"]
		format_str = config["format_str"]
		diagonal = config["diagonal"]

		result = self._build_square_table(
			data, item_names, item_names, row_height, format_str, diagonal
		)

		return result

	# ------------------------------------------------------------------------

	def _build_square_table(
		self,
		data: pd.DataFrame,
		row_headers: list[str],
		column_headers: list[str],
		row_height: int,
		format_str: str,
		diagonal: str,
	) -> QTableWidget:
		"""Build a square table with the given data and formatting"""
		try:
			# Create the table widget
			table_widget = QTableWidget(data.shape[0], data.shape[1])

			# Fill table with data, handling diagonal elements specially
			for row in range(data.shape[0]):
				for col in range(data.shape[1]):
					value = data.iloc[row, col]

					# Format the value, using the diagonal string for diagonal
					if row == col:
						formatted_value = diagonal
					else:
						formatted_value = f"{value:{format_str}}"

					item = QTableWidgetItem(formatted_value)
					item.setTextAlignment(
						QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter
					)
					table_widget.setItem(row, col, item)

			# Set headers and visual properties
			self._director.set_column_and_row_headers(
				table_widget, column_headers, row_headers
			)
			self._director.resize_and_set_table_size(table_widget, row_height)
			self._director.output_widget_type = "Table"

		except AttributeError as e:
			print(
				f"Cannot display square table:"
				f"Required data not available.\nError: {e!s}"
			)
			return QTableWidget()
		else:
			return table_widget


# --------------------------------------------------------------------------


class GeneralStatisticalTableWidget:
	"""Handles score-independent statistical tables"""

	def __init__(self, director: Status) -> None:
		self._director = director
		self.unknown_statistical_table_error_title = (
			"General Statistical Table Widget"
		)
		self.unknown_statistical_table_error_message = (
			"Unknown general statistical table requested. "
		)

		# Dictionary-driven configuration for general statistical tables
		self.statistics_config = dict(statistical_table_dict)

	def display_table(self, table_name: str) -> QTableWidget:
		"""Create and return a general statistical table widget"""

		# Check if table_name exists in configuration
		if table_name not in self.statistics_config:
			raise SpacesError(
				self.unknown_statistical_table_error_title,
				self.unknown_statistical_table_error_message,
			)

		config = self.statistics_config[table_name]

		# Handle special cases first
		if table_name == "cluster_results":
			data = self._director.cluster_results
			row_headers = []
			column_headers = list(data.columns)
			row_height = 4
			# Format: Cluster (str), Color (str), Percent (str), coords (float)
			format_spec = ["s", "s", "s"] + ["8.3f"] * (len(data.columns) - 3)
		elif table_name == "paired":
			# Special handling for paired table
			source = getattr(self._director, config["source_attr"])
			data = getattr(source, config["data_attr"])
			row_headers = config["row_headers"]
			value_type = self._director.similarities_active.value_type
			column_headers = (
				["Name", "Similarity", "Distance"]
				if value_type == "similarities"
				else ["Name", "Dis/similarity", "Distance"]
			)
			row_height = 4
			format_spec = config["format_spec"]
		else:
			# Standard configuration-driven handling
			source = getattr(self._director, config["source_attr"])
			data = getattr(source, config["data_attr"])

			# Handle row headers - config structure guarantees these exist
			row_headers_attr = config.get("row_headers_attr")
			if row_headers_attr:
				# Dynamic row headers (e.g., "source.point_names")
				attr_path = row_headers_attr.split(".")
				row_headers = source
				for attr in attr_path[1:]:  # Skip "source"
					if attr.endswith("]"):  # Handle like "var_names[1:]"
						base_attr = attr.split("[")[0]
						index_expr = attr.split("[")[1].rstrip("]")
						row_headers = getattr(row_headers, base_attr)
						if index_expr == "1:":
							row_headers = row_headers[1:]
					else:
						row_headers = getattr(row_headers, attr)
			else:
				row_headers = config["row_headers"]

			# Handle column headers - config structure guarantees these exist
			column_headers_attr = config.get("column_headers_attr")
			if column_headers_attr == "data.columns":
				column_headers = data.columns
			else:
				column_headers = config["column_headers"]

			row_height = config.get("row_height", 4)
			format_spec = config["format_spec"]

		result = self._build_statistical_table(
			data,
			row_headers,
			column_headers,
			row_height,
			format_spec,
		)

		return result

	# -----------------------------------------------------------------------
	# ...existing code...
	def _build_statistical_table(
		self,
		data: pd.DataFrame,
		row_headers: list[str],
		column_headers: list[str],
		row_height: int,
		format_spec: str | list[str],
	) -> QTableWidget:
		"""Build a statistical table with the given data and formatting

		Parameters:
		-----------
		format_spec : str or list
			If str, the same format is used for all columns
			If list, each element is the format for a specific column
		"""
		# Create the table widget
		table_widget = QTableWidget(data.shape[0], data.shape[1])

		# Use the shared function to fill and format the table data
		self._director.common.fill_table_with_formatted_data(
			table_widget, data, format_spec
		)

		# Set headers and visual properties
		self._director.set_column_and_row_headers(
			table_widget, column_headers, row_headers
		)
		self._director.resize_and_set_table_size(table_widget, row_height)
		self._director.output_widget_type = "Table"

		return table_widget


# --------------------------------------------------------------------------


class RivalryTableWidget:
	"""Handles score-dependent rivalry segment tables"""

	def __init__(self, director: Status) -> None:
		self._director = director
		self.unknown_rivalry_table_error_title = "Rivalry Table Widget"
		self.unknown_rivalry_table_error_message = (
			"Unknown rivalry table requested. "
		)

		# Dictionary-driven configuration for rivalry tables
		self.rivalry_config = dict(rivalry_table_dict)

	def display_table(self, table_name: str) -> QTableWidget:
		"""Create and return a rivalry table widget"""

		# Check if table_name exists in configuration
		if table_name not in self.rivalry_config:
			raise SpacesError(
				self.unknown_rivalry_table_error_title,
				self.unknown_rivalry_table_error_message,
			)

		config = self.rivalry_config[table_name]
		source = self._director.rivalry

		# Handle score dependency (all except segments require scores)
		requires_scores = config.get("requires_scores", True)
		noscores = False

		if requires_scores:
			if self._director.common.have_scores():
				data = getattr(source, config["data_attr"])
				noscores = False
			else:
				data = None
				noscores = True
		else:
			# segments case - doesn't check scores
			data = getattr(source, config["data_attr"])
			noscores = False

		# Get configuration values
		row_headers = config.get("row_headers", [])  # Default to empty
		column_headers = config["column_headers"]
		row_height = 4  # All rivalry tables use height 4
		format_spec = config["format_spec"]

		result = self._build_rivalry_table(
			data,
			row_headers,
			column_headers,
			row_height,
			format_spec,
			noscores=noscores,
		)

		return result

	# -----------------------------------------------------------------------

	def _build_rivalry_table(
		self,
		data: pd.DataFrame,
		row_headers: list[str],
		column_headers: list[str],
		row_height: int,
		format_spec: str | list[str],
		*,
		noscores: bool = False,
	) -> QTableWidget:
		"""Build a rivalry table with the given data and formatting

		Parameters:
		-----------
		format_spec : str or list
			If str, the same format is used for all columns
			If list, each element is the format for a specific column
		"""

		if noscores:
			table_widget = QTableWidget(1, 1)
			table_widget.setItem(
				0,
				0,
				QTableWidgetItem(
					"Segment sizes will be available once scores are "
					"established"
				),
			)
			self._director.set_column_and_row_headers(table_widget, [], [])
			self._director.resize_and_set_table_size(table_widget, 4)
			self._director.output_widget_type = "Table"

			return table_widget

		# Create the table widget
		table_widget = QTableWidget(data.shape[0], data.shape[1])

		# Use the shared function to fill and format the table data
		self._director.common.fill_table_with_formatted_data(
			table_widget, data, format_spec
		)

		# Set headers and visual properties
		self._director.set_column_and_row_headers(
			table_widget, column_headers, row_headers
		)
		self._director.resize_and_set_table_size(table_widget, row_height)
		self._director.output_widget_type = "Table"

		return table_widget
