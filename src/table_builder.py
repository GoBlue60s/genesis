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
		self.display_tables_dict = {
			"configuration": {
				"source": "configuration_active",
				"data": "point_coords",
				"row_headers": "point_names",
				"column_headers": "dim_names",
				"row_height": 4,
				"format": "8.2f",
			},
			"grouped_data": {
				"source": "grouped_data_active",
				"data": "group_coords",
				"row_headers": "group_names",
				"column_headers": "dim_names",
				"row_height": 4,
				"format": "8.2f",
			},
			"target": {
				"source": "target_active",
				"data": "point_coords",
				"row_headers": "point_names",
				"column_headers": "dim_names",
				"row_height": 4,
				"format": "8.2f",
			},
		}

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

			# Fill table with data
			for row in range(data.shape[0]):
				for col in range(data.shape[1]):
					value = data.iloc[row, col]

					# Format the value
					if format_str == "d":
						formatted_value = f"{int(value)}"
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
				f"Cannot display basic table: Required data not available.\n"
				f"Error: {str(e)}"
			)
			return QTableWidget()
		else:
			return table_widget


# --------------------------------------------------------------------------


class SquareTableWidget:
	def __init__(self, director: Status) -> None:
		self._director = director

	def display_table(self, table_name: str) -> QTableWidget:
		"""Create and return a square table widget"""
		result = None

		match table_name:
			case "correlations":
				source = self._director.correlations_active
				data = source.correlations_as_dataframe
				item_names = source.item_names
				row_height = 4
				format_str = "8.2f"
				diagonal = "1.00"

			case "similarities":
				source = self._director.similarities_active
				data = source.similarities_as_dataframe
				item_names = source.item_names
				row_height = 4
				format_str = "8.2f"
				diagonal = "---"  # Changed from "1.00" to "---"

			case "distances":
				source = self._director.configuration_active
				data = source.distances_as_dataframe
				item_names = source.item_names
				row_height = 4
				format_str = "8.2f"
				diagonal = "0.00"

			case "ranked_distances":
				source = self._director.configuration_active
				data = source.ranked_distances_as_dataframe
				item_names = source.item_names
				row_height = 4
				format_str = "8.1f"  # Changed from "8.2f" to "8.1f"
				diagonal = "0.0"  # Changed from "-" to "0.0"

			case "ranked_similarities":
				source = self._director.similarities_active
				data = source.ranked_similarities_as_dataframe
				item_names = source.item_names
				row_height = 4
				format_str = "8.1f"  # Changed from "8.2f" to "8.1f"
				diagonal = "0.0"  # Changed from "-" to "0.0"

			case "ranked_differences":
				source = self._director.similarities_active
				data = source.differences_of_ranks_as_dataframe
				item_names = source.item_names
				row_height = 4
				format_str = "8.1f"  # Changed from "8.2f" to "8.1f"
				diagonal = "0.0"  # Changed from "0" to "0.0"

			case "shepard":
				source = self._director.similarities_active
				data = source.shepard_diagram_table_as_dataframe
				item_names = source.item_names
				row_height = 4
				format_str = "8.1f"  # Changed from "8.2f" to "8.1f"
				diagonal = "-"  # Changed from "-" to "0.0"

			case _:
				print(f"Unknown square table: {table_name}")
				result = QTableWidget()

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

			# Fill table with data
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


class StatisticalTableWidget:
	def __init__(self, director: Status) -> None:
		self._director = director
		self.unknown_statistical_table_error_title = "Statistical Table Widget"
		self.unknown_statistical_table_error_message = (
			"Unknown statistical table requested. "
		)

	def display_table(self, table_name: str) -> QTableWidget:
		"""Create and return a statistical table widget"""
		result = None

		noscores = False
		match table_name:
			case "alike":
				source = self._director.similarities_active
				data = source.alike_df
				row_headers = []
				column_headers = data.columns
				row_height = 4
				format_spec = ["s", "s", "8.4f"]
				# String for item and paired with, 4 dec places for similarity

			case "base":
				source = self._director.rivalry
				if self._director.common.have_scores():
					data = source.base_pcts_df
					noscores = False
				else:
					data = None
					noscores = True
				row_headers = []
				column_headers = [
					"Base\nSupporters of:",
					"Percent of\nPopulation",
				]
				row_height = 4
				format_spec = "8.1f"

			case "battleground":
				source = self._director.rivalry
				if self._director.common.have_scores():
					data = source.battleground_pcts_df
					noscores = False
				else:
					data = None
					noscores = True
				row_headers = []
				column_headers = ["Region", "Percent of\nPopulation"]
				row_height = 4
				format_spec = "8.2f"

			case "compare":
				source = self._director.target_active
				data = source.compare_df
				row_headers = source.point_names
				column_headers = [
					"Active\nX",
					"Active\nY",
					"Target\nX",
					"Target\nY",
				]
				row_height = 4
				# format_spec = "8.4f"  # Same format for all columns
				format_spec = ["8.4f", "8.4f", "8.4f", "8.4f"]  # Same all cols

			case "convertible":
				source = self._director.rivalry
				if self._director.common.have_scores():
					data = source.conv_pcts_df
					noscores = False
				else:
					data = None
					noscores = True
				row_headers = []
				column_headers = ["Convertible to:", "Percent of\nPopulation"]
				row_height = 4
				format_spec = "8.1f"

			case "core":
				source = self._director.rivalry
				if self._director.common.have_scores():
					data = source.core_pcts_df
					noscores = False
				else:
					data = None
					noscores = True
				row_headers = []
				column_headers = [
					"Core\nSupporters of:",
					"Percent of\nPopulation",
				]
				row_height = 4
				format_spec = "8.1f"

			case "directions":
				source = self._director.configuration_active
				data = source.directions_df
				row_headers = source.point_names
				column_headers = [
					"Slope",
					"Unit Circle\nX",
					"Unit Circle\nY",
					"Angle in\nDegrees",
					"Angle in\nRadians",
					"Quadrant",
				]
				row_height = 4
				format_spec = ["16.2f", "8.2f", "8.2f", "8.2f", "8.2f", "s"]

			case "evaluations":
				source = self._director.evaluations_active
				data = source.stats_eval_sorted
				# peek("In StatisticalTableWidget.evaluations")
				# peek(f"{source.stats_eval_sorted=}")
				# row_headers = source.item_names
				row_headers = source.names_eval_sorted
				column_headers = [
					"Mean",
					"Standard\nDeviation",
					"Min",
					"First\nquartile",
					"Median",
					"Third\nquartile",
					"Max",
				]
				row_height = 4
				format_spec = "8.2f"  # Same format for all columns
				# format_spec = ["8.2f", "8.2f", "8.2f", "8.2f",
				# 	"8.2f", "8.2f", "8.2f"]
				# Same format for all columns

			case "factor_analysis":
				source = self._director.configuration_active
				data = source.factor_analysis_df
				row_headers = []
				column_headers = [
					"Eigenvalues",
					"Common Factor\nEigenvalues",
					"Commonalities",
					"Uniquenesses",
					"Item",
					"Loadings\nFactor 1",
					"Loadings\nFactor 2",
				]
				row_height = 4
				format_spec = [
					"8.4f",
					"8.4f",
					"8.4f",
					"8.4f",
					"s",
					"8.4f",
					"8.4f",
				]

			case "first":
				source = self._director.rivalry
				if self._director.common.have_scores():
					data = source.first_pcts_df
					noscores = False
				else:
					data = None
					noscores = True
				row_headers = []
				column_headers = [
					"Party Oriented\nSupporters of:",
					"Percent of\nPopulation",
				]
				row_height = 4
				format_spec = "8.1f"

			case "individuals":
				source = self._director.individuals_active
				data = source.stats_inds
				row_headers = source.var_names[1:]
				column_headers = [
					"Mean",
					"Standard\nDeviation",
					"Min",
					"Max",
					"First\nquartile",
					"Median",
					"Third\nquartile",
				]
				row_height = 4
				format_spec = "8.2f"  # Same format for all columns

			case "likely":
				source = self._director.rivalry
				if self._director.common.have_scores():
					data = source.likely_pcts_df
					noscores = False
				else:
					data = None
					noscores = True
				row_headers = []
				column_headers = [
					"Likely\nSupporters of:",
					"Percent of\nPopulation",
				]
				row_height = 4
				format_spec = "8.1f"

			case "paired":
				source = self._director.current_command
				data = source._paired_df
				row_headers = []  # No row headers needed
				value_type = self._director.similarities_active.value_type
				# Set conditional column headers based on value_type
				if value_type == "similarities":
					column_headers = ["Name", "Similarity", "Distance"]
				else:
					column_headers = ["Name", "Dis/similarity", "Distance"]
				row_height = 4
				format_spec = ["s", ".4f", ".4f"]
				# Str for name, 4 dec for numbers

			case "sample_design":
				source = self._director.uncertainty_active
				data = source.sample_design_analysis_df
				row_headers = []
				column_headers = [
					"Repetition",
					"Selected \n N",
					"Percent",
					"Not selected \n N",
					"Percent",
				]
				row_height = 4
				format_spec = ["d", "d", ".1f", "d", ".1f"]

			case "sample_repetitions":
				source = self._director.uncertainty_active
				data = source.sample_design_analysis_df
				row_headers = []
				column_headers = [
					"Repetition",
					"Selected \n N",
					"Percent",
					"Not selected \n N",
					"Percent",
				]
				row_height = 4
				format_spec = ["d", "d", ".1f", "d", ".1f"]

			case "sample_solutions":
				source = self._director.uncertainty_active
				data = source.solutions_stress_df
				row_headers = []
				column_headers = ["Solution", "Stress"]
				row_height = 4
				format_spec = ["d", "8.4f"]

			case "scores":
				source = self._director.scores_active
				data = source.stats_scores
				row_headers = source.dim_names
				column_headers = [
					"Mean",
					"Standard\nDeviation",
					"Min",
					"Max",
					"First\nquartile",
					"Median",
					"Third\nquartile",
				]
				row_height = 4
				format_spec = "8.2f"  # Same format for all columns

			case "scree":
				source = self._director.configuration_active
				data = source.min_stress
				row_headers = []
				column_headers = ["Dimensionality", "Best Stress"]
				row_height = 8
				format_spec = ["4.0f", "8.2f"]

			case "second":
				source = self._director.rivalry
				if self._director.common.have_scores():
					data = source.second_pcts_df
					noscores = False
				else:
					data = None
					noscores = True
				row_headers = []
				column_headers = [
					"Social Oriented\nSupporters of:",
					"Percent of\nPopulation",
				]
				row_height = 4
				format_spec = "8.1f"

			case "segments":
				source = self._director.rivalry
				data = source.segments_pcts_df
				row_headers = [
					"Likely Supporters:",
					"",
					"Base supporters",
					"",
					"",
					"Core Supporters",
					"",
					"",
					"Party oriented",
					"",
					"Social oriented",
					"",
					"Battleground",
					"",
					"Convertible",
					"",
					"",
				]
				column_headers = ["Segment", "Percent of\nPopulation"]
				row_height = 4
				format_spec = "8.1f"

			case "stress_contribution":
				source = self._director.similarities_active
				data = source.stress_contribution_df
				row_headers = []
				column_headers = ["Item", "Stress Contribution"]
				row_height = 4
				format_spec = ["d", "8.2f"]

			case "uncertainty":
				source = self._director.uncertainty_active
				data = source.solutions_stress_df
				row_headers = []
				column_headers = ["Solution", "Stress"]
				row_height = 4
				format_spec = ["d", "8.4f"]

			case "spatial_uncertainty":
				source = self._director.uncertainty_active
				data = source.solutions_stress_df
				row_headers = []
				column_headers = ["Solution", "Stress"]
				row_height = 4
				format_spec = ["d", "8.4f"]

			case _:
				raise SpacesError(
					self.unknown_statistical_table_error_title,
					self.unknown_statistical_table_error_message,
				)

		result = self._build_statistical_table(
			data,
			row_headers,
			column_headers,
			row_height,
			format_spec,
			noscores,
		)

		# peek("\nAt the end of StatisticalTableWidget.display_table",
		# 	f"\ndata: \n{data}"
		# 	)

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
		noscores: bool = False,
	) -> QTableWidget:  # noqa: FBT001, FBT002
		"""Build a statistical table with the given data and formatting

		Parameters:
		-----------
		format_spec : str or list
			If str, the same format is used for all columns
			If list, each element is the format for a specific column
		"""
		# peek("At top of StatisticalTableWidget._build_statistical_table")
		# peek(format_spec)

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

		# Check if format_spec is a list or a single string
		use_column_specific_formats = isinstance(format_spec, list)

		# Fill table with data
		for row in range(data.shape[0]):
			for col in range(data.shape[1]):
				try:
					value = data.iloc[row, col]

					# Get the appropriate format for this column
					if use_column_specific_formats and col < len(format_spec):
						column_format = format_spec[col]
					else:
						column_format = format_spec

					# Format the value based on format type
					if column_format == "d":
						if isinstance(value, (int, float)):
							formatted_value = str(int(value))
						else:
							formatted_value = str(value)
					elif column_format == "s":
						formatted_value = str(value)
					elif isinstance(value, (int, float)):
						# Format numeric values
						formatted_value = f"{value:{column_format}}"
					else:
						formatted_value = str(value)

					item = QTableWidgetItem(formatted_value)

					# Set alignment based on column format
					if column_format == "s":
						item.setTextAlignment(
							QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter
						)
					else:
						item.setTextAlignment(
							QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter
						)

					table_widget.setItem(row, col, item)

				except (ValueError, TypeError) as e:
					# Handle formatting errors for cell values
					print(f"Error formatting cell ({row}, {col}): {e!s}")
					table_widget.setItem(row, col, QTableWidgetItem("Error"))

		# Set headers and visual properties
		self._director.set_column_and_row_headers(
			table_widget, column_headers, row_headers
		)
		self._director.resize_and_set_table_size(table_widget, row_height)
		self._director.output_widget_type = "Table"

		return table_widget
