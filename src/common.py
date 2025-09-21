from __future__ import annotations

# Standard library imports
# import copy
# import itertools
import math
from pathlib import Path

# Third-party imports
import numpy as np
import pandas as pd
import peek  # noqa: F401

from PySide6.QtWidgets import (
	QDialog,
	QInputDialog,
	QMessageBox,
	QTableWidget,
)
from scipy.stats import spearmanr
from sklearn import manifold

# Local application imports


from constants import (
	EXHAUSTED_EVALUATIONS,
	MAXIMUM_NUMBER_OF_EVALUATORS,
	MINIMUM_SIZE_FOR_PLOT,
	MUST_HAVE_TWO_FIELDS,
	REQUIRED_NUMBER_OF_FIELDS_IN_CONFIGURATION_FILE_LINE,
)
from exceptions import (
	DependencyError,
	InconsistentInformationError,
	MissingInformationError,
	# SelectionError,
	SpacesError,
	# UnderDevelopmentError,
	UnknownTypeError,
)

from geometry import PlotExtremes

from typing import TextIO, TYPE_CHECKING

if TYPE_CHECKING:
	# from collections.abc import Callable
	from spaces import Status
	from features import (
		ConfigurationFeature,
		CorrelationsFeature,
		SimilaritiesFeature,
		TargetFeature,
	)
# from experimental import RepresentationOfPoints

# ---------------------------------------------------------------------------


class Spaces:
	def __init__(self, parent: Status, director: Status) -> None:
		self.parent = parent
		self._director = director
		self._plot_type_dict = None  # ???????????????? is this needed
		self.plot_ranges = PlotExtremes()
		self.presentation_layer: str = "Matplotlib"

		self.item_names: list[str] = []
		self.item_labels: list[str] = []
		self.range_items: range = range(0)

		self.values: list = [float]

		#
		self.hor_dim: int = 0
		self.vert_dim: int = 1
		self.show_bisector: bool = False
		self.show_connector: bool = False
		self.show_just_reference_points: bool = False
		self.show_reference_points: bool = False
		# Not clear if this is ever used
		self.show_respondent_points: bool = False
		self.point_size: int = 3  # the size of the dots representing
		self.axis_extra: float = 0.1  # to keep points from falling on the edge
		self.displacement: float = 0.04  # to improve visibility

		self.vector_head_width: float = 0.05
		self.vector_width: float = 0.01
		self.battleground_size: float = 0.25
		# self.battleground_size defines a battleground sector as a percent
		# of connector on each side of bisector
		self.core_tolerance: float = 0.2
		self.plot_presentation_layer: list[str] = []
		#
		self.max_cols: int = 10
		self.width: int = 8  # had been 8 in other class
		self.decimals: int = 2  # had been 2 in other class

		self._use_metric = None
		self._min_stress: pd.DataFrame = pd.DataFrame()
		self.shepard_axis: str = ""
		self.point_to_plot_index: int = 0

		self.plot_dict: dict = {}  # ?????????? is this needed
		return

	# ------------------------------------------------------------------------

	def create_sample_design_analysis_table(self) -> pd.DataFrame:
		"""Create a DataFrame containing sample design analysis data.

		This function processes the sample design frequencies data and creates
		a structured DataFrame with counts and percentages for selected and
		not selected cases across repetitions.

		Returns:
			pd.DataFrame: Analysis table with columns for repetition number,
			selected counts and percentages, and not selected counts and
			percentages.
		"""
		# Get the number of repetitions
		nrepetitions = self._director.uncertainty_active.nrepetitions

		# Initialize our results DataFrame
		sample_design_analysis_df = pd.DataFrame(
			columns=[
				"Repetition",
				"Selected Count",
				"Selected Percent",
				"Not Selected Count",
				"Not Selected Percent",
			]
		)

		# Get the frequencies data
		frequencies_df = (
			self._director.uncertainty_active.sample_design_frequencies
		)

		# Process each repetition
		for repetition in range(1, nrepetitions + 1):
			# Filter data for this repetition
			rep_data = frequencies_df[
				frequencies_df["Repetition"] == repetition
			]

			# Get selected row (True) and not selected row (False)
			selected_row = rep_data[rep_data["Selected"] == True]  # noqa: E712
			not_selected_row = rep_data[rep_data["Selected"] == False]  # noqa: E712

			# Extract counts
			selected_count = (
				selected_row["Count"].to_numpy()[0]
				if not selected_row.empty
				else 0
			)
			not_selected_count = (
				not_selected_row["Count"].to_numpy()[0]
				if not not_selected_row.empty
				else 0
			)

			# Calculate total and percentages
			total = selected_count + not_selected_count
			selected_percent = (
				(selected_count / total * 100) if total > 0 else 0
			)
			not_selected_percent = (
				(not_selected_count / total * 100) if total > 0 else 0
			)

			# Add row to results DataFrame
			sample_design_analysis_df.loc[len(sample_design_analysis_df)] = [
				repetition,
				selected_count,
				selected_percent,
				not_selected_count,
				not_selected_percent,
			]
		self._director.uncertainty_active.sample_design_analysis_df = (
			sample_design_analysis_df
		)
		return sample_design_analysis_df

	# ------------------------------------------------------------------------

	def create_solutions_table(self) -> pd.DataFrame:
		# Use the solutions_stress_df DataFrame directly
		uncertainty_analysis_df = (
			self._director.uncertainty_active.solutions_stress_df
		)

		return uncertainty_analysis_df

	# ------------------------------------------------------------------------

	def get_focal_item_from_user_initialize_variables(self) -> None:
		self.no_selection_error_title = "Selection required"
		self.no_selection_error_message = "Nothing has been selected"

	# ------------------------------------------------------------------------

	def get_focal_item_from_user(
		self, title: str, label: str, items: list[str]
	) -> int:
		# director: Status) -> int:
		"""
		Displays a dialog for the user to select a focal item from a list of
		items.

		Args:
			title (str): The title for the dialog box
			label (str): The instructional text to display in the dialog
			items (list): List of item names to choose from

		Returns:
			int: The index of the selected item, or -1 if no item was selected

		"""

		self.get_focal_item_from_user_initialize_variables()

		dialog = QInputDialog()
		dialog.setWindowTitle(title)
		dialog.setLabelText(label)
		dialog.setComboBoxItems(items)
		dialog.setComboBoxEditable(False)

		# Select the first item as default if items exist
		if items:
			dialog.setTextValue(items[0])

		if dialog.exec() == QDialog.Accepted:
			selected_item = dialog.textValue()
			if selected_item in items:
				index_selected_item = items.index(selected_item)
		else:
			raise SpacesError(
				self.no_selection_error_title, self.no_selection_error_message
			)

		return index_selected_item

	# ------------------------------------------------------------------------

	def use_plot_ranges(self) -> tuple[float, float, float, float]:
		hor_max = self._director.common.plot_ranges.hor_max
		hor_min = self._director.common.plot_ranges.hor_min
		vert_max = self._director.common.plot_ranges.vert_max
		vert_min = self._director.common.plot_ranges.vert_min

		return hor_max, hor_min, vert_max, vert_min

	# ------------------------------------------------------------------------

	def in_group(
		self,
		segments: pd.DataFrame,
		nscored: int,
		score: str,
		group_name: str,
		group_code: set,
	) -> list:
		in_group_list = [
			segments.loc[ind, score]
			for ind in range(nscored)
			if segments.loc[ind, group_name] in group_code
		]
		return in_group_list

	# ------------------------------------------------------------------------

	def not_in_group(
		self,
		segments: pd.DataFrame,
		nscored: int,
		score: str,
		group_name: str,
		group_code: set,
	) -> list:
		not_in_group_list = [
			segments.loc[ind, score]
			for ind in range(nscored)
			if segments.loc[ind, group_name] not in group_code
		]
		return not_in_group_list

	# -----------------------------------------------------------------------

	def set_axis_extremes_based_on_coordinates(
		self, coordinates: pd.DataFrame
	) -> None:
		"""Set the maximum and minimum values for the x and y axes.

		This function calculates appropriate axis limits based on the
		coordinates.
		Needed when coordinates may not match the previously established
		extremes.
		"""
		if (
			self._director.common.have_scores()
			and self._director.scores_active.hor_max == 0.0
			and self._director.scores_active.hor_min == 0.0
		):
			numpy_scores = self._director.scores_active.scores.iloc[
				:, 1:3
			].to_numpy()

			score_max = np.amax(numpy_scores)
			score_min = np.amin(numpy_scores)

			score_max = max(score_max, abs(score_min))

			score_int_max = math.ceil(score_max)
			self._director.scores_active.hor_max = score_int_max
			self._director.scores_active.hor_min = -score_int_max
			self._director.scores_active.vert_max = score_int_max
			self._director.scores_active.vert_min = -score_int_max
			self._director.scores_active.offset = 0.03 * score_int_max

		scores_hor_max = self._director.scores_active.hor_max
		scores_hor_min = self._director.scores_active.hor_min
		scores_vert_max = self._director.scores_active.vert_max
		scores_vert_min = self._director.scores_active.vert_min
		scores_offset = self._director.scores_active.offset

		score_int_max: float = 0.0
		# coordinates = pd.DataFrame(coordinates)
		num_conf = np.array(coordinates)

		conf_max = np.amax(num_conf)
		conf_min = np.amin(num_conf)

		conf_max = max(conf_max, abs(conf_min))
		vals = [conf_max, score_int_max]
		the_max = max(vals)
		if the_max < MINIMUM_SIZE_FOR_PLOT:
			plot_max = MINIMUM_SIZE_FOR_PLOT
		else:
			plot_max = math.ceil(the_max)

		if self._director.common.have_scores() and scores_hor_max > plot_max:
			hor_max = scores_hor_max
			hor_min = scores_hor_min
			vert_max = scores_vert_max
			vert_min = scores_vert_min
			offset = scores_offset
		else:
			hor_max = plot_max
			hor_min = -plot_max
			vert_max = plot_max
			vert_min = -plot_max
			offset = 0.03 * plot_max

		self._director.common.plot_ranges = PlotExtremes(
			hor_max, hor_min, vert_max, vert_min, offset
		)

		return

	# ------------------------------------------------------------------------

	def read_configuration_type_file_initialize_variables(
		self, file_name: str, configuration_type: str
	) -> None:
		self.conf_file_not_found_title = configuration_type
		self.conf_file_not_found_message = f"File not found: \n{file_name}"

	# ------------------------------------------------------------------------

	def read_configuration_type_file(
		self, file_name: str, configuration_type: str
	) -> ConfigurationFeature | TargetFeature:
		"""This is used by commands needing to	read a configuration file."""

		from features import ConfigurationFeature, TargetFeature  # noqa: PLC0415

		_director = self._director

		self.read_configuration_type_file_initialize_variables(
			file_name, configuration_type
		)

		try:
			with Path(file_name).open() as file_handle:
				ndim, npoint = self.read_configuration_type_file_sizes(
					file_handle, configuration_type
				)
				dim_labels, dim_names, point_labels, point_names = (
					self.read_configuration_type_file_dictionary(
						file_handle, ndim, npoint
					)
				)
				point_coords = self.read_configuration_type_file_coordinates(
					file_handle, npoint, point_names, ndim, dim_labels
				)
		except FileNotFoundError:
			raise SpacesError(
				self.conf_file_not_found_title,
				self.conf_file_not_found_message,
			) from None

		if configuration_type == "Configuration":
			destination: ConfigurationFeature = ConfigurationFeature(_director)
		elif configuration_type == "Target":
			destination: TargetFeature = TargetFeature(_director)
		destination.ndim = ndim
		destination.npoint = npoint
		destination.range_dims = range(ndim)
		destination.range_points = range(npoint)
		destination.dim_labels = dim_labels
		destination.dim_names = dim_names
		destination.point_labels = point_labels
		destination.point_names = point_names
		destination.point_coords = point_coords
		# peek("Was Meghan right - did it get here?"
		# 	" This is ok when no problem"
		# 	" This is not ok when bad file name or file not found")
		return destination

	# ------------------------------------------------------------------------

	def read_configuration_type_file_sizes_initialize_variables(
		self, file_handle: TextIO, configuration_type: str
	) -> None:
		self.empty_header_error_title = configuration_type
		self.empty_header_error_message = (
			"The header line is empty in file:."
			f"\n{getattr(file_handle, 'name', '<unknown file>')}"
		)
		self.not_configuration_file_error_title = configuration_type
		self.not_configuration_file_error_message = (
			"File is not a configuration file:"
			f"\n{getattr(file_handle, 'name', '<unknown file>')}"
		)
		self.not_found_error_title = configuration_type
		self.not_found_error_message = f"File not found: \n{file_handle}"

	# ------------------------------------------------------------------------

	def read_configuration_type_file_sizes(
		self, file_handle: TextIO, configuration_type: str
	) -> tuple[int, int]:
		self.read_configuration_type_file_sizes_initialize_variables(
			file_handle, configuration_type
		)

		try:
			header = file_handle.readline()
			if len(header) == 0:
				raise SpacesError(
					self.empty_header_error_title,
					self.empty_header_error_message,
				) from None
			if header.lower().strip() != "configuration":
				raise SpacesError(
					self.not_configuration_file_error_title,
					self.not_configuration_file_error_message,
				) from None
			dim = file_handle.readline()
			dim_list = dim.strip().split()
			expected_dim = int(dim_list[0])
			expected_points = int(dim_list[1])
			ndim = expected_dim
			npoint = expected_points
		except FileNotFoundError as err:
			raise SpacesError(
				self.not_found_error_title, self.not_found_error_message
			) from err

		return (ndim, npoint)

	# ------------------------------------------------------------------------

	def read_configuration_type_file_dictionary_initialize_variables(
		self, npoint: int
	) -> None:
		self.shape_error_title = "Configuration"
		self.shape_error_message = (
			"Line two of the configuration file is not valid.\n"
			"Expected number of dimensions and number of points."
		)
		self.inconsistency_error_title = "Configuration"
		self.inconsistency_error_message = f"Expected {npoint} point lines"
		self.needs_two_fields_error_title = "Configuration"
		self.needs_two_fields_error_message = (
			"Invalid point format, expected 'label;name' format"
		)
		self.unexpected_line_error_title = "Configuration"
		self.unexpected_line_error_message = (
			"Unexpected content after point definitions but"
			"  before coordinates"
		)

	# -- ---------------------------------------------------------------------

	def read_configuration_type_file_dictionary(
		self, file_handle: TextIO, ndim: int, npoint: int
	) -> tuple[list[str], list[str], list[str], list[str]]:
		dim_labels = []
		dim_names = []
		point_labels = []
		point_names = []

		self.read_configuration_type_file_dictionary_initialize_variables(
			npoint
		)

		# Read dimension lines
		for i in range(ndim):  # noqa: B007
			line = file_handle.readline().rstrip("\n")
			if not line:
				raise SpacesError(
					self.shape_error_title, self.shape_error_message
				)
			parts = line.split(";")
			if (
				len(parts)
				!= REQUIRED_NUMBER_OF_FIELDS_IN_CONFIGURATION_FILE_LINE
			):
				raise SpacesError(
					self.shape_error_title, self.shape_error_message
				)
			dim_label, dim_name = parts
			dim_labels.append(dim_label)
			dim_names.append(dim_name)

		# Read point lines
		for i in range(npoint):  # noqa: B007
			line = file_handle.readline().rstrip("\n")
			if not line:
				raise InconsistentInformationError(
					self.inconsistency_error_title,
					self.inconsistency_error_message,
				)
			parts = line.split(";")
			if len(parts) != MUST_HAVE_TWO_FIELDS:
				raise InconsistentInformationError(
					self.needs_two_fields_error_title,
					self.needs_two_fields_error_message,
				)
			point_label, point_name = parts
			point_labels.append(point_label)
			point_names.append(point_name.strip())

		# Check if there are unexpected additional lines before coordinates
		pos_before_extra = file_handle.tell()
		extra = file_handle.readline().strip()
		if extra and not any(c.isdigit() for c in extra):
			raise SpacesError(
				self.unexpected_line_error_title,
				self.unexpected_line_error_message,
			)

		# Seek back to the position before reading the extra line
		file_handle.seek(pos_before_extra)

		return dim_labels, dim_names, point_labels, point_names

	# ------------------------------------------------------------------------

	def read_configuration_type_file_coordinates_initialize_variables(
		self,
	) -> None:
		self.unexpected_number_of_lines_error_title = "Configuration"
		self.unexpected_number_of_lines_error_message = (
			"Unexpected number of coordinate lines in the configuration file\n"
			"Expected {npoint} coordinate lines"
		)
		self.unexpected_number_of_coordinates_error_title = "Configuration"
		self.unexpected_number_of_coordinates_error_message = (
			"Number of coordinates does not match number of dimensions"
		)
		self.invalid_coordinate_error_title = "Configuration"
		self.invalid_coordinate_error_message = (
			"Invalid numeric value in coordinates"
		)
		self.unexpected_extra_error_title = "Configuration"
		self.unexpected_extra_error_message = (
			"Unexpected content after coordinates section"
		)
		self.unable_to_read_coordinates_error_title = "Configuration"
		self.unable_to_read_coordinates_error_message = (
			"File is not readable as a configuration file"
		)

	# ------------------------------------------------------------------------

	def read_configuration_type_file_coordinates(
		self,
		file_handle: TextIO,
		npoint: int,
		point_names: list[str],
		ndim: int,
		dim_labels: list[str],
	) -> pd.DataFrame:
		self.read_configuration_type_file_coordinates_initialize_variables()

		try:
			# Read coordinates data from file
			coords_data = []
			for i in range(npoint):  # noqa: B007
				line = file_handle.readline().strip()
				if not line:
					raise InconsistentInformationError(  # noqa: TRY301
						self.unexpected_number_of_lines_error_title,
						self.unexpected_number_of_lines_error_message,
					)

				values = [val for val in line.split() if val]

				# Verify we have the expected number of values
				if len(values) != ndim:
					raise InconsistentInformationError(  # noqa: TRY301
						self.unexpected_number_of_coordinates_error_title,
						self.unexpected_number_of_coordinates_error_message,
					)

				# Convert values to floats
				try:
					coords = [float(val) for val in values]
				except ValueError as err:
					raise SpacesError(
						self.invalid_coordinate_error_title,
						self.invalid_coordinate_error_message,
					) from err
				coords_data.append(coords)

			# Check if there's unexpected content after coordinates
			extra = file_handle.readline().strip()
			if extra:
				raise SpacesError(  # noqa: TRY301
					self.unexpected_extra_error_title,
					self.unexpected_extra_error_message,
				)

			# Handle ndim=1 case specially
			if ndim == 1:
				# For one-dimensional data, create DataFrame with single
				#  column properly
				# Extract the scalar values from each single-element list
				simple_values = [coord[0] for coord in coords_data]
				point_coords = pd.DataFrame(
					simple_values,  # Use the extracted values directly
					index=point_names,
					columns=dim_labels,
				)
			else:
				# For multi-dimensional data, use standard approach
				point_coords = pd.DataFrame(
					coords_data, index=point_names, columns=dim_labels
				)
		except Exception as e:
			raise SpacesError(
				self.unable_to_read_coordinates_error_title,
				self.unable_to_read_coordinates_error_message,
			) from e

		return point_coords

	# ----------------------------------------------------------------------

	def create_plot_for_plot_and_gallery_tabs_initialize_variables(
		self, plot_type: str
	) -> None:
		self.unknown_plot_type_error_title = "Unknown plot type"
		self.unknown_plot_type_error_message = (
			f"Plot type '{plot_type}' is not recognized."
			" Please check the plot type and try again."
		)

	# ----------------------------------------------------------------------

	def create_plot_for_plot_and_gallery_tabs(self, plot_type: str) -> None:
		if self._director.common.presentation_layer == "PyQtGraph":
			try:
				getattr(
					self._director.pyqtgraph_plotter,
					f"request_{plot_type}_plot_for_plot_and_gallery_tabs_using_pyqtgraph",
				)()
			except UnknownTypeError:
				getattr(
					self._director.matplotlib_plotter,
					f"request_{plot_type}_plot_for_plot_and_gallery_tabs_using_matplotlib",
				)()
		elif self._director.common.presentation_layer == "Matplotlib":
			getattr(
				self._director.matplotlib_plotter,
				f"request_{plot_type}_plot_for_plot_and_gallery_tabs_using_matplotlib",
			)()

	# ------------------------------------------------------------------------

	def duplicate_in_different_structures(
		self,
		values: list[list[float]],
		item_names: list[str],
		item_labels: list[str],
		nreferent: int,
		value_type: str | None,
	) -> (tuple)[
		pd.DataFrame, dict, list, list[list[float]], list, int, range, range
	]:
		values_as_dict: dict = {}
		values_as_list: list = []
		values_as_square: list[list[float]] = []

		a_item_name: list[str] = []  # the name of the first item
		b_item_name: list[str] = []  # the name of the second item
		a_item_label: list[str] = []  # the label of the first item
		b_item_label: list[str] = []  # the label of the second item
		from_points = range(1, nreferent)
		for an_item in from_points:
			to_points = range(an_item)
			for another_item in to_points:
				values_as_list.append(values[an_item - 1][another_item])
				new_key = str(
					item_labels[another_item] + "_" + item_labels[an_item]
				)
				a_item_label.append(item_labels[another_item])
				b_item_label.append(item_labels[an_item])
				a_item_name.append(item_names[another_item])
				b_item_name.append(item_names[an_item])

				values_as_dict[new_key] = values[an_item - 1][another_item]

		ndyad = nreferent * (nreferent - 1) / 2
		ndyad = int(ndyad)
		range_dyads = range(ndyad)

		# Sort the pairs based on value_type
		if value_type == "similarities":
			# For similarities, sort in descending order (highest first)
			sorted_values_w_pairs = sorted(
				zip(
					values_as_list,
					a_item_label,
					b_item_label,
					a_item_name,
					b_item_name,
					strict=True,
				),
				reverse=True,
			)
		else:
			# For dissimilarities or other types, sort in ascending\
			#  order (lowest first)
			sorted_values_w_pairs = sorted(
				zip(
					values_as_list,
					a_item_label,
					b_item_label,
					a_item_name,
					b_item_name,
					strict=True,
				)
			)

		range_items = range(len(item_labels))
		for each_item in range_items:
			values_as_square.append([])
			for other_item in range_items:
				if each_item == other_item:
					values_as_square[other_item].append(0.0)
				elif each_item < other_item:
					index = str(
						item_labels[each_item] + "_" + item_labels[other_item]
					)

					values_as_square[each_item].append(values_as_dict[index])
				else:
					index = str(
						item_labels[other_item] + "_" + item_labels[each_item]
					)
					values_as_square[each_item].append(values_as_dict[index])
		values_as_dataframe = pd.DataFrame(
			values_as_square, columns=item_names, index=item_names
		)

		return (
			values_as_dataframe,
			values_as_dict,
			values_as_list,
			values_as_square,
			sorted_values_w_pairs,
			ndyad,
			range_dyads,
			range_items,
		)

	# ------------------------------------------------------------------------
	@staticmethod
	def error(title: str, message: str) -> None:
		# positional arguments had been message and feedback
		# these are now title and message

		if title is not None:
			QMessageBox.warning(QMessageBox(), title, message)
		return

	# ------------------------------------------------------------------------

	def have_active_configuration(self) -> bool:
		return not self._director.configuration_active.point_coords.empty

	# ------------------------------------------------------------------------

	def have_alike_coords(self) -> bool:
		return len(self._director.similarities_active.a_x_alike) != 0

	# ------------------------------------------------------------------------

	def have_clusters(self) -> bool:
		return (
			hasattr(self._director.scores_active, 'cluster_labels')
			and hasattr(self._director.scores_active, 'cluster_centers')
			and self._director.scores_active.cluster_labels is not None
			and self._director.scores_active.cluster_centers is not None
		)

	# ------------------------------------------------------------------------

	def have_correlations(self) -> bool:
		#
		# Checks if correlations data is empty
		#
		return len(self._director.correlations_active.correlations) != 0

	# ------------------------------------------------------------------------

	def have_distances(self) -> bool:
		#
		# Checks if self.distances is empty
		#
		return len(self._director.configuration_active.distances) != 0

	# ------------------------------------------------------------------------

	def have_evaluations(self) -> bool:
		#
		# Checks if evaluations data is empty
		#
		return not self._director.evaluations_active.evaluations.empty

	# ------------------------------------------------------------------------

	def have_factors(self) -> bool:
		if len(self._director.configuration_active.dim_names) == 0:
			return False
		return self._director.configuration_active.dim_names[0] == "Factor 1"

	# ------------------------------------------------------------------------

	def have_grouped_data(self) -> bool:
		return not self._director.grouped_data_active.group_coords.empty

	# ------------------------------------------------------------------------

	def have_individual_data(self) -> bool:
		#
		# Checks if individual data is empty
		#
		return not self._director.individuals_active.ind_vars.empty

	# ------------------------------------------------------------------------

	def have_mds_results(self) -> bool:
		#
		# Check if best_stress is reasonable
		#
		return self._director.configuration_active.best_stress != -1

	# ------------------------------------------------------------------------

	def have_previous_active(self) -> bool:
		#
		return len(self._director.undo_stack) != 1

	# ------------------------------------------------------------------------

	def have_ranks_of_similarities(self) -> bool:
		#
		# Checks if ranks dataframe is empty
		#
		return not self._director.similarities_active.ranks_df.empty

	# ------------------------------------------------------------------------

	def have_reference_points(self) -> bool:
		rivalry = self._director.rivalry
		return not (
			rivalry.rival_a.index is None or rivalry.rival_b.index is None
		)

	# ------------------------------------------------------------------------

	def have_sample_design(self) -> bool:
		return not self._director.uncertainty_active.sample_design.empty

	# ------------------------------------------------------------------------

	def have_sample_design_frequencies(self) -> bool:
		return not self._director.uncertainty_active.\
			sample_design_frequencies.empty

	# ------------------------------------------------------------------------

	def have_sample_repetitions(self) -> bool:
		return not self._director.uncertainty_active.\
			sample_repetitions.empty

	# ------------------------------------------------------------------------

	def have_sample_solutions(self) -> bool:
		return not self._director.uncertainty_active.sample_solutions.empty

	# ------------------------------------------------------------------------

	def have_scores(self) -> bool:
		return not self._director.scores_active.scores.empty

	# ------------------------------------------------------------------------

	def have_segments(self) -> bool:
		return bool(not self._director.rivalry.seg.empty)

	# ------------------------------------------------------------------------

	def have_similarities(self) -> bool:
		#
		# Checks if similarities data is empty
		#
		return len(self._director.similarities_active.similarities) != 0

	# ------------------------------------------------------------------------

	def have_target_configuration(self) -> bool:
		#
		# Checks if dataframe is empty ?????????????untested
		#
		return not self._director.target_active.point_coords.empty

	# ------------------------------------------------------------------------

	def declare_file_type_and_size(
		self, file_handle: TextIO, file_type: str, nreferent: int
	) -> None:
		"""Writes file type and size information to a file.

		Args:
			file_handle: An open file handle with write permission
			file_type: The type of file (e.g., "Configuration",
				"Lower Triangular")
			nreferent: Number of reference points/items
		"""

		file_handle.write(file_type + "\n")
		file_handle.write(file_type + "\n")

		match file_type:
			case "Configuration":
				file_handle.write(
					" " + str(self.ndim) + " " + str(self.npoint) + "\n"
				)
			case "Lower Triangular":
				file_handle.write(str(nreferent) + "\n")
		return

	# ------------------------------------------------------------------------

	def los(self, evaluations: pd.DataFrame) -> SimilaritiesFeature:
		"""Line of sight analysis to extract similarities from evaluations."""
		line_of_sight = self._initialize_similarities_feature(evaluations)
		df = self._apply_reflection_if_needed(evaluations.evaluations)
		sums_s_star, diffs_d_star = self._calculate_sums_and_diffs(
			df, line_of_sight.nreferent
		)
		ordered = self._create_ranked_data(
			sums_s_star, diffs_d_star, line_of_sight
		)
		best_ranking = self._find_best_ranking(ordered, evaluations)
		self._build_final_similarities(line_of_sight, best_ranking)

		return line_of_sight

	def _initialize_similarities_feature(
		self, evaluations: pd.DataFrame
	) -> SimilaritiesFeature:
		"""Initialize and configure a SimilaritiesFeature object."""
		from features import SimilaritiesFeature  # noqa: PLC0415

		line_of_sight = SimilaritiesFeature(self._director)
		line_of_sight.nreferent = 0
		line_of_sight.value_type = "dissimilarities"

		# Initialize empty data structures
		line_of_sight.item_names = []
		line_of_sight.item_labels = []
		line_of_sight.similarities = []
		line_of_sight.similarities_as_dict = {}
		line_of_sight.similarities_as_list = []
		line_of_sight.similarities_as_square = []
		line_of_sight.similarities_as_dataframe = pd.DataFrame()
		line_of_sight.sorted_similarities = {}
		line_of_sight.a_item_label = []
		line_of_sight.b_item_label = []
		line_of_sight.a_item_name = []
		line_of_sight.b_item_name = []

		# Set up dimensions and item data
		df_orig = evaluations.evaluations
		(line_of_sight.n_individ, line_of_sight.nreferent) = df_orig.shape
		line_of_sight.nitem = line_of_sight.nreferent
		line_of_sight.npoints = line_of_sight.nreferent
		line_of_sight.range_items = range(line_of_sight.nreferent)
		line_of_sight.item_names = df_orig.columns.tolist()
		line_of_sight.range_similarities = range(len(line_of_sight.item_names))

		# Create item labels (first 4 characters)
		for each_item in line_of_sight.range_similarities:
			line_of_sight.item_labels.append(
				line_of_sight.item_names[each_item][0:4]
			)

		return line_of_sight

	def _apply_reflection_if_needed(
		self, df_orig: pd.DataFrame
	) -> pd.DataFrame:
		"""Apply reflection transformation to the data if needed."""
		reflect = "Yes"
		if reflect == "Yes":
			return df_orig.apply(lambda x: x.max() - x)
		return df_orig

	def _calculate_sums_and_diffs(
		self, df: pd.DataFrame, nreferent: int
	) -> tuple[pd.DataFrame, pd.DataFrame]:
		"""Calculate sum and difference matrices for all item pairs."""
		sums_s_star = pd.DataFrame()
		diffs_d_star = pd.DataFrame()
		n_items_less_one = nreferent - 1

		for an_item in range(n_items_less_one):
			to_pts = range(an_item + 1, nreferent)
			for another_item in to_pts:
				new_name = str(
					df.columns[an_item] + "_" + df.columns[another_item]
				)
				sums_s_star[new_name] = (
					df[str(df.columns[an_item])]
					+ df[str(df.columns[another_item])]
				)
				diffs_d_star[new_name] = abs(
					df[str(df.columns[an_item])]
					- df[str(df.columns[another_item])]
				)

		return sums_s_star, diffs_d_star

	def _create_ranked_data(
		self,
		sums_s_star: pd.DataFrame,
		diffs_d_star: pd.DataFrame,
		line_of_sight: SimilaritiesFeature,
	) -> pd.DataFrame:
		"""Create ranked data from sums and differences."""
		n_items_less_one = line_of_sight.nreferent - 1
		line_of_sight.n_pairs = int(
			line_of_sight.nreferent * n_items_less_one / 2
		)
		line_of_sight.range_similarities = range(line_of_sight.n_pairs)

		sumsort_s = sums_s_star.copy()
		diffsort_d = diffs_d_star.copy()

		# Sort columns in each dataframe
		for each_row in line_of_sight.range_similarities:
			a_col = list(sums_s_star[str(sums_s_star.columns[each_row])])
			a_col.sort()
			sumsort_s[str(sums_s_star.columns[each_row])] = a_col

			a_col = list(diffs_d_star[str(diffs_d_star.columns[each_row])])
			a_col.sort(reverse=True)
			diffsort_d[str(diffs_d_star.columns[each_row])] = a_col

		# Combine and create cumulative sums
		combo_b = sumsort_s + diffsort_d
		cum_b_hat = pd.DataFrame()
		for each_pair in line_of_sight.range_similarities:
			cum_b_hat[str(diffs_d_star.columns[each_pair])] = combo_b[
				str(diffs_d_star.columns[each_pair])
			].cumsum(axis=0)

		return cum_b_hat.rank(axis=1, method="average")

	def _find_best_ranking(
		self, ordered: pd.DataFrame, evaluations: pd.DataFrame
	) -> pd.Series:
		"""Find the best ranking through optimization."""
		# Calculate iteration control parameter (unused but preserved)
		if evaluations.nevaluators < MAXIMUM_NUMBER_OF_EVALUATORS:
			_itcon = 4
		else:
			_itcon = int(evaluations.nevaluators / 150)

		maxadeq = 0
		best_ranking = pd.Series()
		loc_best = 0
		range_rows = range(1, evaluations.nevaluators)

		for each_row in range_rows:
			rho = spearmanr(
				ordered.iloc[each_row], ordered.iloc[each_row - 1]
			)[0]
			unique_vals = ordered.iloc[each_row].nunique()
			n_pairs = len(ordered.columns)
			discrim = (unique_vals - 1) / n_pairs
			dense = (
				evaluations.nevaluators - each_row
			) / evaluations.nevaluators
			adeq = rho * discrim * dense

			if adeq > maxadeq:
				maxadeq = adeq
				best_ranking = ordered.iloc[each_row]
				loc_best = each_row
			elif maxadeq >= dense:
				print("\nMaxadeq value greater than dense value")
			elif (each_row - loc_best) == EXHAUSTED_EVALUATIONS:
				break

		return best_ranking

	def _build_final_similarities(
		self, line_of_sight: SimilaritiesFeature, best_ranking: pd.Series
	) -> None:
		"""Build the final similarities structure from the best ranking."""
		line_of_sight.similarities_as_list = list(best_ranking)

		# Create rows and columns from similarities_as_list
		for each_row in range(line_of_sight.nreferent - 1):
			row = []
			row.append(line_of_sight.similarities_as_list[each_row])
			last_index = each_row
			cols = range(each_row)
			for each_col in cols:
				indexer = last_index + line_of_sight.nreferent - each_col - 2
				last_index = indexer
				row.append(line_of_sight.similarities_as_list[indexer])

			line_of_sight.similarities.append(row)

	# ------------------------------------------------------------------------

	def mds(
		self,
		extract_ndim: int,
		use_metric: bool,  # noqa: FBT001
		similarities: SimilaritiesFeature,
	) -> ConfigurationFeature:
		from features import ConfigurationFeature  # noqa: PLC0415

		configuration = ConfigurationFeature(self._director)
		configuration.dim_names = []
		configuration.dim_labels = []
		nmds = manifold.MDS(
			n_components=extract_ndim,
			metric=use_metric,
			dissimilarity="precomputed",
			n_init=10,
			verbose=0,
			normalized_stress="auto",
		)
		npos = nmds.fit_transform(X=similarities.similarities_as_square)
		configuration.ndim = extract_ndim
		configuration.point_coords = pd.DataFrame(npos.tolist())
		configuration.point_coords.set_index(
			[similarities.item_labels], inplace=True
		)
		configuration.range_dims = range(extract_ndim)
		for each_dim in configuration.range_dims:
			dim_num = str(each_dim + 1)
			configuration.dim_names.append("Dimension " + dim_num)
			configuration.dim_labels.append("Dim" + dim_num)
		configuration.point_coords.columns = configuration.dim_names
		configuration.best_stress = nmds.stress_
		configuration.n_comp = extract_ndim

		return configuration

	# ------------------------------------------------------------------------

	def needs_configuration(self, command: str) -> bool:
		if not self.have_active_configuration():
			title = "No Active configuration has been established."
			message = (
				"Open a configuration file or use Models such as MDS, "
				"Factor analysis or "
				"\nPrincipal components to establish one before using "
				f"{command}."
			)
			raise DependencyError(title, message)

		return False

	# -------------------------------------------------------------------------

	def needs_correlations(self, command: str) -> bool:
		if not self.have_correlations():
			title = "No Correlations have been established."
			message = (
				"Open file of Correlations or Evaluations before using "
				f"{command}."
			)
			raise DependencyError(title, message)

		return False

	# ------------------------------------------------------------------------

	def needs_distances(self, command: str) -> bool:
		if not self.have_distances():
			title = "No Distances have been established."
			message = (
				"Use Associations Distances or Open Configuration file "
				"or use Principal components, Factor analysis, "
				"or Multi-dimensional scaling before using "
				f"{command}."
			)
			raise DependencyError(title, message)

		return False

	# ------------------------------------------------------------------------

	def needs_evaluations(self, command: str) -> bool:
		if not self.have_evaluations():
			title = "No Evaluations have been established."
			message = (
				"Open Evaluations file or use Associations Evaluations "
				"before using "
				f"{command}."
			)
			raise DependencyError(title, message)

		return False

	# ------------------------------------------------------------------------

	def needs_grouped_data(self, command: str) -> bool:
		if not self.have_grouped_data():
			title = "No Grouped data has been established."
			message = (
				"Open Grouped data file or use Associations Grouped data "
				"before using "
				f"{command}."
			)
			raise DependencyError(title, message)

		return False

	# ------------------------------------------------------------------------

	def needs_individual_data(self, command: str) -> bool:
		if not self.have_individual_data():
			title = "No Individual data has been established."
			message = (
				"Open Individual data file or use Associations Individual "
				"data before using "
				f"{command}."
			)
			raise DependencyError(title, message)

		return False

	# ------------------------------------------------------------------------

	def needs_ranks(self, command: str) -> bool:
		if not self.have_ranks_of_similarities():
			title = "No ranks have been established."
			message = f"Use Associations Ranks before using {command}."
			raise DependencyError(title, message)

		return False

	# ------------------------------------------------------------------------

	def needs_reference_points(self, command: str) -> bool:
		if not self.have_reference_points():
			title = "No reference points have been established."
			message = f"Establish Reference points before {command}."
			raise DependencyError(title, message)

		return False

	# ------------------------------------------------------------------------

	def needs_sample_design(self, command: str) -> bool:
		if not self.have_sample_design():
			title = "No Sample design has been established."
			message = (
				"Open a Sample design file or use Respondents Sample "
				"designer to establish one before using "
				f"{command}."
			)
			raise DependencyError(title, message)

		return False

	# ------------------------------------------------------------------------

	def needs_sample_design_frequencies(self, command: str) -> bool:
		if not self.have_sample_design_frequencies():
			title = "No Sample design frequencies have been established."
			message = (
				"Open a Sample design frequencies file or use "
				"Respondents Sample "
				f"designer to establish one before using {command}."
			)
			raise DependencyError(title, message)

		return False

	# ------------------------------------------------------------------------

	def needs_sample_repetitions(self, command: str) -> bool:
		if not self.have_sample_repetitions():
			title = "No Sample repetitions have been established."
			message = (
				"Open a Sample repetitions file or use Respondents "
				"Generate repetitions to establish one before using "
				f"{command}."
			)
			raise DependencyError(title, message)

		return False

	# ------------------------------------------------------------------------

	def needs_sample_solutions(self, command: str) -> bool:
		if not self.have_sample_solutions():
			title = "No Sample solutions have been established."
			message = (
				"Open a Sample solutions file or use Model Uncertainty"
				" to establish one before using "
				f"{command}."
			)
			raise DependencyError(title, message)

		return False

	# ------------------------------------------------------------------------

	def needs_scores(self, command: str) -> bool:
		if not self.have_scores():
			title = "No scores have been established."
			message = (
				"Open scores or use Models such as MDS, Factor analysis or "
				"\nPrincipal components to establish scores before using "
				f"{command}."
			)
			raise DependencyError(title, message)

		return False

	# ------------------------------------------------------------------------

	def needs_similarities(self, command: str) -> bool:
		if not self.have_similarities():
			title = "No similarities have been established."
			message = (
				"Open Similarities or use Line of Sight before"
				f" using {command}."
			)
			raise DependencyError(title, message)

		return False

	# ------------------------------------------------------------------------

	def needs_target(self, command: str) -> bool:
		if not self.have_target_configuration():
			title = "No Target configuration has been established."
			message = (
				f"Open a target file to establish one before using {command}."
			)
			raise DependencyError(title, message)

		return False

		# --------------------------------------------------------------------

	def print_display_settings(self) -> None:
		print("   Display settings:")
		print(
			"\tPercent of axis maxima added to keep points from "
			f"falling on edge of plots: "
			f"{self._director.common.axis_extra * 100: 3.0f}"
		)
		print(
			"\tPercent of axis maxima used to displace labelling "
			"off point to improve visibility: "
			f"{self._director.common.displacement * 100: 3.0f}"
		)
		print(
			f"\tSize in points of the dots representing people in plots: "
			f"{self._director.common.point_size}"
		)
		print(" ")
		return

		# --------------------------------------------------------------------

	def print_established_elements(self) -> None:
		print("   Established elements:")
		print(
			"\t Alike coordinates: ", self._director.common.have_alike_coords()
		)
		print(
			"\t Configuration: ",
			self._director.common.have_active_configuration(),
		)
		# print("\t Bisector: ", self._director.common.have_bisector_info())
		print("\t Clusters: ", self._director.common.have_clusters())
		print("\t Correlations: ", self._director.common.have_correlations())
		print("\t Distances: ", self._director.common.have_distances())
		print("\t Evaluations: ", self._director.common.have_evaluations())
		print("\t Factors: ", self._director.common.have_factors())
		print("\t Grouped data: ", self._director.common.have_grouped_data())
		print(
			"\t Individual data: ",
			self._director.common.have_individual_data(),
		)
		print("\t MDS results: ", self._director.common.have_mds_results())
		print(
			"\t Previous active configuration: ",
			self._director.common.have_previous_active(),
		)
		print("\t Ranks: ", self._director.common.have_ranks_of_similarities())
		print(
			"\t Reference_points: ",
			self._director.common.have_reference_points(),
		)
		print("\t Scores: ", self._director.common.have_scores())
		print("\t Segments: ", self._director.common.have_segments())
		print("\t Similarities: ", self._director.common.have_similarities())
		print(
			"\t Target configuration: ",
			self._director.common.have_target_configuration(),
		)
		print(
			"\t Verbosity setting: ",
			self._director.include_explanation_when_verbosity_last_set_to_verbose(),
		)
		print(" ")
		return

		# --------------------------------------------------------------------

	def print_layout_options_settings(self) -> None:
		print("   Layout options settings:")
		print(
			"\tMaximum number of columns per page: "
			f"{self._director.common.max_cols}"
		)
		print(
			"\tField width used to display numbers: "
			f"{self._director.common.width}"
		)
		print(
			"\tNumber of decimal places used to display numbers: "
			f"{self._director.common.decimals}"
		)
		print(" ")
		return

	# ------------------------------------------------------------------------

	@staticmethod
	def print_lower_triangle(
		decimals: int,
		labels: list[str],
		names: list[str],
		nelements: int,
		values: list[float],
		width: int,
	) -> None:
		"""Print values in lower triangular matrix format.

		This method prints a lower triangular matrix with row/column labels
		and item names. Used by commands to display correlations, similarities,
		dissimilarities, and distances.

		Args:
			decimals: Number of decimal places for values
			labels: Short labels (up to 4 chars) for items
			names: Full names for items
			nelements: Number of items/points in the matrix
			values: Lower triangular matrix values as list of lists
			width: Field width for formatting numbers
		"""
		if not labels or not names or not values or nelements <= 0:
			return

		label_indent = "  "
		name_separator = "\t"

		# Print items with their labels and names
		for label, name in zip(labels, names, strict=True):
			print(f"\t\t{label}{name_separator}{name}")

		# Calculate spacing to align headers with data columns
		# Account for label_indent (2 spaces) + max label width + 1 space
		max_label_width = max(len(label) for label in labels)
		header_spacing = len(label_indent) + max_label_width + 1

		# Format and print column headers
		header_line = "".join(f"{label:>{width}}" for label in labels)
		print(f"\n{' ' * header_spacing}{header_line}")

		# Print first row (just the label with diagonal "----")
		diagonal_placeholder = "----".rjust(width)
		first_row = (
			f"{label_indent}{labels[0]:<{max_label_width + 1}}"
			f"{diagonal_placeholder}"
		)
		print(first_row)

		# Print remaining rows with values and diagonal "----"
		for row_idx in range(1, nelements):
			row_values = values[row_idx - 1]
			formatted_values = "".join(
				f"{value:{width}.{decimals}f}" for value in row_values
			)
			diagonal_placeholder = "----".rjust(width)
			row_output = (
				f"{label_indent}{labels[row_idx]:<{max_label_width + 1}}"
				f"{formatted_values}{diagonal_placeholder}"
			)
			print(row_output)

		return

		# --------------------------------------------------------------------

	def print_plane_settings(self) -> None:
		print("    Plane settings:")
		print(
			f"\tHorizontal axis will be defined by: "
			f"{self._director.configuration_active.hor_axis_name}"
		)
		print(
			f"\tVertical axis will be defined by: "
			f"{self._director.configuration_active.vert_axis_name}"
		)
		print(" ")
		return

		# --------------------------------------------------------------------

	def print_plot_settings(self) -> None:
		print("    Plot settings:")
		print(
			"\tShow bisector if available:  "
			f"{self._director.common.show_bisector}"
		)
		print(
			"\tShow connector if available: "
			f"{self._director.common.show_connector}"
		)
		print(
			"\tShow reference points if available: "
			f"{self._director.common.show_reference_points}"
		)
		print(
			"\t In Joint plots show just reference points: "
			f"{self._director.common.show_just_reference_points}"
		)
		print(" ")
		return

	# ------------------------------------------------------------------------

	def print_segment_sizing_settings(self) -> None:
		print("    Segment sizing settings:")
		print(
			f"\tPercent of connector used to define size of"
			" battleground sector: "
			f"{self._director.common.battleground_size * 100: 3.0f}"
		)
		print(
			f"\tPercent of connector used to define size of"
			f" core sector: "
			f"{self._director.common.core_tolerance * 100: 3.0f}"
		)
		print(" ")
		return

	#  ------------------------------------------------------------------------

	def print_sample_solutions(self) -> None:
		uncertainty_active = self._director.uncertainty_active
		point_labels = uncertainty_active.point_labels
		point_names = uncertainty_active.point_names
		npoint = uncertainty_active.npoints

		points = range(npoint)
		print("\nSample solutions points\n")
		for each_point in points:
			print(f"\t{point_labels[each_point]}, {point_names[each_point]}")
		print("\nStress for each solution\n")
		print(uncertainty_active.solutions_stress_df.to_string(index=False))
		print("\nCoordinates for all points for all solutions\n")
		print(uncertainty_active.sample_solutions)
		return

	# ------------------------------------------------------------------------

	def print_vector_sizing_settings(self) -> None:
		print("    Vector sizing settings:")
		print(
			f"\tVector head size in inches: "
			f"{self._director.common.vector_head_width}"
		)
		print(
			f"\tVector thickness in inches: "
			f"{self._director.common.vector_width}"
		)
		print(" ")
		return

	# ------------------------------------------------------------------------

	def read_lower_triangular_matrix_initialize_variables(self) -> None:
		self.unexpected_eof_lower_triangular_error_title = (
			"Unexpected End of File"
		)
		self.unexpected_eof_lower_triangular_error_message = (
			"Review file name and contents"
		)
		self.problem_reading_lower_triangular_error_title = (
			"Problem reading lower triangular file."
		)
		self.problem_reading_lower_triangular_error_message = (
			"Review file name and contents"
		)
		self.unexpected_input_lower_triangular_error_title = (
			"Unexpected input in lower triangular file."
		)
		self.unexpected_input_lower_triangular_error_message = (
			"Review file name and contents"
		)

	# ------------------------------------------------------------------------

	def read_lower_triangular_matrix(
		self, file_name: str, data_type: str
	) -> SimilaritiesFeature | CorrelationsFeature:
		"""read lower triangular function - this function is used
		to read information stored in lower triangular form such
		as similarities, distances and correlations.
		"""
		from features import SimilaritiesFeature, CorrelationsFeature  # noqa: PLC0415

		# Note:
		# Within read_lower_triangular the elements of the matrix are
		#  considered
		# values regardless of whether the calling routine called them
		# correlations, similarities or even dissimilarities.
		# Analogously within this function it refers to labels and names
		# rather than item_labels and item_names.
		# And lastly it uses nelements??????? rather than self.range_points.
		# self.range_points refers specifically
		# to the active configuration.
		# peek("At top of read_lower_triangular_matrix", data_type)
		self.read_lower_triangular_matrix_initialize_variables()
		try:
			with Path(file_name).open() as file_handle:
				nreferent = self.read_lower_triangle_size(file_handle)
				item_labels, item_names = self.read_lower_triangle_dictionary(
					file_handle, nreferent
				)
				if data_type in {"similarities", "dissimilarities"}:
					similarities = self.read_lower_triangle_values(
						file_handle, nreferent
					)
				elif data_type == "correlations":
					correlations = self.read_lower_triangle_values(
						file_handle, nreferent
					)

		except EOFError:
			raise SpacesError(
				self.unexpected_eof_lower_triangular_error_title,
				self.unexpected_eof_lower_triangular_error_message,
			) from None
		except OSError:
			raise SpacesError(
				self.problem_reading_lower_triangular_error_title,
				self.problem_reading_lower_triangular_error_message,
			) from None
		except ValueError:
			raise SpacesError(
				self.unexpected_input_lower_triangular_error_title,
				self.unexpected_input_lower_triangular_error_message,
			) from None

		if data_type == "similarities":
			destination: SimilaritiesFeature = SimilaritiesFeature(
				self._director
			)
			destination.similarities = similarities
			destination.value_type = "similarities"
		elif data_type == "dissimilarities":
			destination: SimilaritiesFeature = SimilaritiesFeature(
				self._director
			)
			destination.similarities = similarities
			destination.value_type = "dissimilarities"
		elif data_type == "correlations":
			# peek("At elif data_type == 'correlations'")
			destination: CorrelationsFeature = CorrelationsFeature(
				self._director
			)
			destination.correlations = correlations
			# peek("After elif data_type == 'correlations'", destination)

		destination.nreferent = nreferent
		destination.nitem = destination.nreferent
		destination.npoint = destination.nreferent
		destination.item_labels = item_labels
		destination.item_names = item_names
		# peek("At bottom of read_lower_triangular_matrix",
		# 	destination,
		# 	destination.item_labels, destination.item_names,
		# 	destination.nreferent, destination.nitem, destination.npoint)
		return destination

	# ------------------------------------------------------------------------

	def read_lower_triangle_size_initialize_variables(self) -> None:
		self.missing_info_lower_triangle_error_title = "Empty file"
		self.missing_info_lower_triangle_error_message = (
			"Review file name and contents"
		)
		self.not_lower_triangular_error_title = "File is not lower triangular"
		self.not_lower_triangular_error_message = (
			"Review file name and contents. Should be lower triangular"
		)
		self.size_info_lower_triangular_error_title = (
			"Problem reading size of lower triangular matrix."
		)
		self.size_info_lower_triangular_error_message = (
			"Should contain the number of stimuli."
		)
		self.unreasonable_number_of_stimuli_error_title = (
			"Problem reading number of stimuli."
		)
		self.unreasonable_number_of_stimuli_error_message = (
			"Should be greater than 0."
		)

	# ------------------------------------------------------------------------

	def read_lower_triangle_size(self, file_handle: TextIO) -> int:
		self.read_lower_triangle_size_initialize_variables()

		line = file_handle.readline()
		flower = line.lower()
		file_type = flower.strip()
		if len(file_type) == 0:
			raise MissingInformationError(
				self.missing_info_lower_triangle_error_title,
				self.missing_info_lower_triangle_error_message,
			)

		if file_type.lower().strip() != "lower triangular":
			raise SpacesError(
				self.not_lower_triangular_error_title,
				self.not_lower_triangular_error_message,
			)

		nite = file_handle.readline().strip("\n")
		if len(nite) == 0:
			raise SpacesError(
				self.size_info_lower_triangular_error_title,
				self.size_info_lower_triangular_error_message,
			)

		nreferent = int(nite)
		if nreferent < 1:
			raise SpacesError(
				self.unreasonable_number_of_stimuli_error_title,
				self.unreasonable_number_of_stimuli_error_message,
			)

		return nreferent

	# ------------------------------------------------------------------------

	def read_lower_triangle_dictionary_initialize_variables(self) -> None:
		self.dict_problem_lower_triangle_error_title = (
			"Problem reading labels and names of stimuli"
		)
		self.dict_problem_lower_triangle_error_message = (
			"Review file name and contents"
		)

	# ------------------------------------------------------------------------

	def read_lower_triangle_dictionary(
		self, file_handle: TextIO, nreferent: int
	) -> tuple[list[str], list[str]]:
		item_labels: list = []
		item_names: list = []
		docs: list = []
		range_items = range(nreferent)
		for each_item in range_items:
			it = file_handle.readline()
			if len(it) == 0:
				raise SpacesError(
					self.dict_problem_lower_triangle_error_title,
					self.dict_problem_lower_triangle_error_message,
				)

			it = it.rstrip()
			docs.append(it)
			its = docs[each_item].split(";")
			item_labels.append(its[0])
			item_names.append(its[1])

		# labs =[item_labels[each_item] for each_item in range_items]

		return item_labels, item_names

	# ------------------------------------------------------------------------

	def read_lower_triangle_values_initialize_variables(self) -> None:
		self.problematic_values_in_lower_triangle_error_title = (
			"Problem reading values in lower triangular matrix."
		)
		self.problematic_values_in_lower_triangle_error_message = (
			"Review file name and contents"
		)

	# ------------------------------------------------------------------------

	def read_lower_triangle_values(
		self, file_handle: TextIO, nreferent: int
	) -> list[list[float]]:
		self.read_lower_triangle_values_initialize_variables()

		values: list[list[float]] = []
		one_less = nreferent - 1
		nitems = range(one_less)
		#
		for each_item in nitems:
			aitem = file_handle.readline()
			aitem = aitem.rstrip()
			if len(aitem) == 0:
				raise SpacesError(
					self.problematic_values_in_lower_triangle_error_title,
					self.problematic_values_in_lower_triangle_error_message,
				)

			item = aitem.split()
			values.append(item)
			#
			range_ites = range(each_item + 1)
			for ites in range_ites:
				values[each_item][ites] = float(values[each_item][ites])
		return values

	# ------------------------------------------------------------------------

	@staticmethod
	def resize_and_set_table_size(
		gui_output_as_widget: QTableWidget, fudge: int
	) -> None:
		n_rows = gui_output_as_widget.rowCount()
		#
		gui_output_as_widget.resizeColumnsToContents()
		gui_output_as_widget.resizeRowsToContents()
		#
		height_of_rows = sum(
			[gui_output_as_widget.rowHeight(row) for row in range(n_rows)]
		)
		height_of_header = gui_output_as_widget.horizontalHeader().height()
		gui_output_as_widget.setFixedHeight(
			height_of_rows + height_of_header + fudge
		)
		return

	# ------------------------------------------------------------------------

	def set_column_and_row_headers(
		self,
		table_widget: QTableWidget,
		column_header: list[str],
		row_header: list[str],
	) -> None:
		#
		if len(column_header) == 0:
			table_widget.horizontalHeader().hide()
		else:
			table_widget.setHorizontalHeaderLabels(column_header)
			table_widget.horizontalHeader().setStyleSheet(
				f"QHeaderView::section"
				f"{{ background-color: {self._director.column_header_color} }}"
			)
		if len(row_header) == 0:
			table_widget.verticalHeader().hide()
		else:
			table_widget.setVerticalHeaderLabels(row_header)
			table_widget.verticalHeader().setStyleSheet(
				f"QHeaderView::section"
				f"{{ background-color: {self._director.row_header_color} }}"
			)
		return

	# ------------------------------------------------------------------------

	def write_a_label_for_each_point(
		self,
		file_handle: TextIO,
		nreferent: int,
		item_labels: list[str],
		item_names: list[str],
	) -> None:
		for each_item in range(nreferent):
			file_handle.write(
				f"{item_labels[each_item]};{item_names[each_item]}"
			)
			if each_item != nreferent - 1:
				file_handle.write("\n")
		return

	# ------------------------------------------------------------------------

	def write_data_as_lower_triangle(
		self,
		file_handle: TextIO,
		data_as_list: list[float],
		nreferent: int,
		width: int,
		decimals: int,
	) -> None:
		start: int = 0
		for each_item in range(nreferent):
			for each_datum_in_row in range(each_item):
				value = f"{data_as_list[start]:{width}.{decimals}f}"
				file_handle.write(value)
				if each_datum_in_row != each_item - 1:
					file_handle.write(" ")
				start = start + 1
			file_handle.write("\n")
		return

	# ------------------------------------------------------------------------

	def point_solutions_extrema(
		self, focal_point: int
	) -> tuple[float, float, float, float]:
		"""Return extrema for x and y coordinates of a focal point.

		Args:
			focal_point: The index of a point in the solutions

		Returns:
			tuple[float, float, float, float]: x_max, x_min, y_max, y_min
		"""
		uncertainty_active = self._director.uncertainty_active
		sample_solutions = uncertainty_active.sample_solutions
		npoint = uncertainty_active.npoints

		# Get all coordinates for the focal point across all solutions
		# The solutions data is organized where each row is one point's
		# coordinates in one solution, so we need every npoint-th row starting
		# from focal_point
		focal_point_data = sample_solutions.iloc[focal_point::npoint]

		# Extract x and y coordinates
		x_coords = focal_point_data.iloc[:, 0]  # First dimension (x)
		y_coords = focal_point_data.iloc[:, 1]  # Second dimension (y)

		# Calculate extrema, preserving floating point precision
		x_max = float(x_coords.max())
		x_min = float(x_coords.min())
		y_max = float(y_coords.max())
		y_min = float(y_coords.min())

		return x_max, x_min, y_max, y_min

	# ------------------------------------------------------------------------

	def solutions_means(self, focal_point: int) -> tuple[float, float]:
		"""Return means of each coordinate for focal point across solutions.

		Args:
			focal_point: The index of a focal point in the solutions

		Returns:
			tuple[float, float]: Mean x coordinate, mean y coordinate as floats
		"""
		uncertainty_active = self._director.uncertainty_active
		sample_solutions = uncertainty_active.sample_solutions
		npoint = uncertainty_active.npoints

		# Get all coordinates for the focal point across all solutions
		# The solutions data is organized where each row is one point's
		# coordinates in one solution, so we need every npoint-th row starting
		# from focal_point
		focal_point_data = sample_solutions.iloc[focal_point::npoint]

		# Extract x and y coordinates
		x_coords = focal_point_data.iloc[:, 0]  # First dimension (x)
		y_coords = focal_point_data.iloc[:, 1]  # Second dimension (y)

		# Calculate means, preserving floating point precision
		x_mean = float(x_coords.mean())
		y_mean = float(y_coords.mean())

		return x_mean, y_mean

	# ------------------------------------------------------------------------

	def largest_uncertainty(self, focal_point: int) -> float:
		"""Return largest difference between extrema and mean for focal point.

		Args:
			focal_point: The index of a focal point in the solutions

		Returns:
			float: The largest difference between any extremum and its mean
		"""
		# Get extrema and means for the focal point
		x_max, x_min, y_max, y_min = self.point_solutions_extrema(focal_point)
		x_mean, y_mean = self.solutions_means(focal_point)

		# Return the single largest difference among all four possibilities
		return max(
			abs(x_max - x_mean),
			abs(x_min - x_mean),
			abs(y_max - y_mean),
			abs(y_min - y_mean),
		)

	# ------------------------------------------------------------------------

	def write_lower_triangle_initialize_variables(self) -> None:
		self.file_exists_lower_triangle_error_title = "File exists"
		self.file_exists_lower_triangle_error_message = (
			"File already exists\n"
			"Choose a different file name or delete the existing file."
		)

	# ------------------------------------------------------------------------

	def write_lower_triangle(
		self,
		file_name: str,
		data_as_list: list[float],
		nreferent: int,
		item_labels: list[str],
		item_names: list[str],
		width: int,
		decimals: int,
	) -> None:
		# last two positional arguments had been message and feedback

		self.write_lower_triangle_initialize_variables()

		file_type: str = "Lower Triangular"
		try:
			with Path(file_name).open("w") as file_handle:
				self.declare_file_type_and_size(
					file_handle, file_type, nreferent
				)
				self.write_a_label_for_each_point(
					file_handle, nreferent, item_labels, item_names
				)
				self.write_data_as_lower_triangle(
					file_handle, data_as_list, nreferent, width, decimals
				)
		except SpacesError as exc:
			raise SpacesError(
				self.file_exists_lower_triangle_error_title,
				self.file_exists_lower_triangle_error_message,
			) from exc
		return

	# ------------------------------------------------------------------------

	def get_components_to_extract_from_user_initialize_variables(
		self, title: str
	) -> tuple[str, str]:
		"""Initialize variables for the component extraction dialog."""
		zero_components_error_title = title
		zero_components_error_message = "Need number of components."
		return zero_components_error_title, zero_components_error_message

	# ------------------------------------------------------------------------

	def get_components_to_extract_from_user(
		self,
		title: str,
		label: str,
		min_allowed: int,
		max_allowed: int,
		an_integer: bool,  # noqa: FBT001
		default: int,
	) -> int:
		"""Get number of components to extract from user via dialog."""
		from dialogs import SetValueDialog

		(
			zero_components_error_title,
			zero_components_error_message,
		) = self.\
			get_components_to_extract_from_user_initialize_variables(title)

		ext_comp_dialog = SetValueDialog(
			title, label, min_allowed, max_allowed, an_integer, default
		)
		result = ext_comp_dialog.exec()
		if result == QDialog.Accepted:
			ext_comp = ext_comp_dialog.getValue()
		else:
			raise SpacesError(
				zero_components_error_title, zero_components_error_message
			)

		if ext_comp == 0:
			raise SpacesError(
				zero_components_error_title, zero_components_error_message
			)

		return ext_comp
