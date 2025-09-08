
# Standard library imports
import copy
import sys
from pathlib import Path

# Third-party imports
import numpy as np
import pandas as pd
import peek

from pyqtgraph.Qt import QtCore
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import (
	QDialog, QTableWidget, QTableWidgetItem
)
from dialogs import (
	ChoseOptionDialog, MatrixDialog, ModifyItemsDialog,
	ModifyValuesDialog, SelectItemsDialog,
	SetNamesDialog
)
from exceptions import (
	DependencyError, MissingInformationError,
	ProblemReadingFileError,
	SelectionError, SpacesError
)
from features import ConfigurationFeature
from geometry import (
    Point
)
from experimental import (Item, ItemFrame)
from common import Spaces
from director import Status

from typing import TextIO
from constants import (
	# MAXIMUM_NUMBER_OF_DIMENSIONS_FOR_PLOTTING,
	ITEM_LABEL_FIRST_COLUMN,
	ITEM_LABEL_LENGTH,
	MUST_HAVE_AT_LEAST_TWO_ITEMS_EVALUATED,
	MAXIMUM_NUMBER_OF_VAR_NAMES,

	N_ROWS_IN_SETTINGS_PLOT_TABLE,
	N_ROWS_IN_SETTINGS_PLANE_TABLE,
	N_ROWS_IN_SETTINGS_SEGMENTS_TABLE,
	N_ROWS_IN_SETTINGS_DISPLAY_TABLE,
	N_ROWS_IN_SETTINGS_VECTOR_TABLE,
	N_ROWS_IN_SETTINGS_LAYOUT_TABLE,
	N_COLS_IN_TABLE,
	TEST_IF_BISECTOR_SELECTED,
	TEST_IF_CONNECTOR_SELECTED,
	TEST_IF_REFERENCE_POINTS_SELECTED,
	TEST_IF_JUST_REFERENCE_POINTS_SELECTED
)

# --------------------------------------------------------------------------

class ConfigurationCommand:
	""" The Configuration command reads in a configuration to be used
	as the active configuration.
	"""
	def __init__(
			self,
			director: Status,
			common: Spaces) -> None:

		self._director = director
		self.common = common
		self._director.command = "Configuration"
		# self._director.abandon_configuration()
		configuration_candidate = self._director.configuration_candidate
		configuration_candidate.file_handle = ""

		configuration_candidate.ndim = 0
		configuration_candidate.npoint = 0
		configuration_candidate.dim_labels.clear()
		configuration_candidate.dim_names.clear()
		configuration_candidate.point_labels.clear()
		configuration_candidate.point_names.clear()
		configuration_candidate.point_coords = pd.DataFrame()
		# self._director.configuration_candidate.bisector.case = "Unknown"
		# self._director.configuration_candidate.bisector.direction = "Unknown"
		configuration_candidate.distances.clear()
		configuration_candidate.seg = pd.DataFrame()
		# rivalry = self._director.rivalry
		# rivalry.rival_a.index = -1
		# rivalry.rival_b.index = -1

		common.show_bisector = False
		self._dialog_caption: str = "Open configuration"
		self._dialog_filter: str = "*.txt"
		self._empty_response_title: str = "Empty response"
		self._empty_response_message: str = \
			"To establish configuration select file in dialog"
		self._bad_target_title: str = "Target configuration does not match"
		self._bad_target_message: str = (
			"Target configuration and dependent information "
			"have been abandoned")

		return

	# ------------------------------------------------------------------------

	def execute(
			self,
			common: Spaces) -> None:
		# peek("\nAt top of ConfigurationCommand.execute()")
		director = self._director
		common = director.common
		# configuration_candidate = director.configuration_candidate


		director.record_command_as_selected_and_in_process()
		director.optionally_explain_what_command_does()
		# peek("\nIn ConfigurationCommand.execute() about to get file name")
		file_name = director.\
			get_file_name_and_handle_nonexistent_file_names(
				self._dialog_caption, self._dialog_filter)
		director.configuration_candidate = (
			common.read_configuration_type_file(file_name, "Configuration"))
		# peek("Just after reading configuration file")
		# peek(director.configuration_candidate.dim_names)
		director.dependency_checker.detect_consistency_issues()
		director.configuration_candidate.inter_point_distances()
		director.configuration_active = director.configuration_candidate
		director.configuration_original = director.configuration_active
		director.configuration_last = director.configuration_active
		similarities_active = director.similarities_active
		ndim = director.configuration_active.ndim
		npoint = director.configuration_active.npoint


		# configuration_active = director.configuration_candidate
		# configuration_original = director.configuration_active
		# configuration_last = director.configuration_active
		# peek("Just before conversion")
		# peek(self._director.configuration_active.dim_names)
		self._convert_configuration_to_object()
		# peek("\nJust after creation of config_as_itemframe")
		# peek(self.config_as_itemframe)
		if common.have_similarities():
			similarities_active.create_ranked_similarities_dataframe()
		director.configuration_active.print_the_configuration()
		common.create_plot_for_plot_and_gallery_tabs("configuration")
		# ndim = self._director.configuration_active.ndim
		# npoint = self._director.configuration_active.npoint
		director.title_for_table_widget = (
			f"Configuration has {ndim} dimensions and {npoint} points")
		director.create_widgets_for_output_and_log_tabs()
		director.set_focus_on_tab('Plot')
		director.record_command_as_successfully_completed()
		return

# --------------------------------------------------------------------------

	def _print_the_configuration(self) -> None:
		ndim = self._director.configuration_active.ndim
		npoint = self._director.configuration_active.npoint
		print(
			f"\n\tConfiguration has {ndim} dimensions and {npoint} points\n")
		self._director.configuration_active.print_the_configuration()
		return

# # --------------------------------------------------------------------------

	def _convert_configuration_to_object(self) -> ItemFrame:
		"""Convert the configuration to an object structure."""
		data = {}
		
		# Get dimension names to use as coordinate keys
		dim_names = self._director.configuration_active.dim_names
		dim_labels = self._director.configuration_active.dim_labels
		
		# Create Item objects for each point in the configuration
		for each_item in range(
			len(self._director.configuration_active.point_names)):
			# Create a Point object with coordinates using dimension
			# names as keys
			coords = {}
			for i, dim_name in enumerate(dim_names):
				if i < \
					self._director.configuration_active.point_coords.shape[1]:
					coords[dim_name] = \
						self._director.configuration_active.point_coords.\
							iloc[each_item, i]
			
			location = Point(**coords, color="green")
			
			# Create Item with this location
			data[each_item] = Item(
				name=self._director.configuration_active.point_names[each_item],
				label=\
					self._director.configuration_active.point_labels[each_item],
				location=location
			)
		
		# Create ItemFrame with the data
		item_frame = ItemFrame(
			data=data,
			columns=["name", "label", "location"],
			index=list(range(len(
				self._director.configuration_active.point_names))),
			dim_names=dim_names,
			dim_labels=dim_labels
		)

		self._director.configuration_active.config_as_itemframe = item_frame
		
		print("\nDEBUG -- ItemFrame representation:")
		print(item_frame.full())

		print("\nDEBUG -- ItemFrame without labels:")
		print(item_frame)

		print("\nDEBUG -- Experimenting with ItemFrame:")

		print(f"{item_frame._index=}")
		print(f"{item_frame._columns=}")
		print(f"{item_frame._dim_names=}")
		print(f"{item_frame._data[0].location=}")
		print(f"{item_frame._data[0].location.x=}")
		print(f"{item_frame._data[0].location.y=}")
		print(f"{item_frame._data[0].location.z=}")
		print(f"{item_frame[0].location.x=}")
		print(f"{item_frame[0].location.y=}")
		print(f"{item_frame[0].location.z=}")
		print(f"{item_frame[0].location._coords=}")
		print(f"{item_frame[0].location['Social']=}")
		print(f"{item_frame[0].location['Third']=}")
		print(f"{item_frame[0].location['Fourth']=}")
		print(f"{item_frame[0].location[3]=}")
		print(f"{item_frame[0].location.color=}")
		print(f"{item_frame[0].location.size=}")
		print(f"{item_frame[0].location.style=}")
		print(f"{item_frame._data[0].location._coords=}")
		rival_a_index = 6
		rival_b_index = 7
		print(f"{item_frame._data[rival_a_index].location._coords=}")
		print(f"{item_frame._data[rival_b_index].location._coords=}")
		print(f"{item_frame._data[rival_a_index].location.x=}")
		print(f"{item_frame._data[rival_b_index].location.x=}")
		print(f"{item_frame._data[rival_a_index].location.y=}")
		print(f"{item_frame._data[rival_b_index].location.y=}")
		print(f"{item_frame[rival_b_index].location.y=}")

		# the following need specific congifurations
		# print(f"{item_frame[0].location._coords['Left-Right']=}")
		# print(f"{item_frame[0].location._coords['Fa1']=}")
		# print(f"{item_frame["Carter"].location._coords=}")
		# print(f"{item_frame["bclinton"].location._coords=}")
		# print(f"{item_frame._data[0].location.z=}")
		

		# the following do not produce useful information
		# print(f"{item_frame._data=}")

		# the following fail
		# print(f"{item_frame._data['Carter'].location=}")
		# print(f"{item_frame._data[0].x=}")
		# print(f"{item_frame._data[1].location._coords['x']=}")
		# print(f"{item_frame._data[1]._coords['x']=}")
		# print(f"{item_frame._data[rival_b].location._coords['x']=}")
		# print(f"{item_frame._data[rival_a].location._coords['x']=}")
		# print(f"{item_frame._data[rival_b].location._coords['y']=}")
		# print(f"{item_frame._data[rival_a].location._coords.x=}")

		return item_frame



	# ------------------------------------------------------------------------


class CorrelationsCommand:

	def __init__(
			self,
			director: Status,
			common: Spaces) -> None:

		self._director = director
		self.common = common
		self._director.command = "Open correlations"
		self._director.correlations_candidate.nreferent = 0
		self._director.correlations_candidate.item_names.clear()
		self._director.correlations_candidate.item_labels.clear()
		self._director.correlations_candidate.correlations.clear()
		self._director.correlations_candidate.correlations_as_dict = {}
		self._director.correlations_candidate.correlations_as_list.clear()
		self._director.correlations_candidate.correlations_as_square.clear()
		self._director.correlations_candidate.correlations_as_dataframe = \
			pd.DataFrame()
		self._director.correlations_candidate.sorted_correlations = {}
		# self._director.\
		# correlations_candidate.sorted_correlations_w_pairs.clear()

		self._director.correlations_candidate.ndyad = 0
		self._director.correlations_candidate.n_pairs = 0
		self._director.correlations_candidate.range_pairs = range(0)
		self._director.correlations_candidate.a_item_names.clear()
		self._director.correlations_candidate.b_item_names.clear()
		self._director.correlations_candidate.a_item_labels.clear()
		self._director.correlations_candidate.b_item_labels.clear()

		self._director.correlations_candidate.value_type = "Unknown"
		self._director.width = 8
		self._director.decimals = 2
		# file = ""
		self._file_caption = "Open correlations"
		self._file_filter = "*.txt"
		return

	# -----------------------------------------------------------------------

	def execute(
			self,
			common: Spaces) -> None:
		
		director = self._director
		common = self.common

		director.record_command_as_selected_and_in_process()
		director.optionally_explain_what_command_does()
		director.dependency_checker.detect_dependency_problems()
		file = director.get_file_name_and_handle_nonexistent_file_names(
			self._file_caption, self._file_filter)
		director.correlations_candidate = \
			common.read_lower_triangular_matrix(file, "correlations")
		director.dependency_checker.detect_consistency_issues()
		director.correlations_candidate.duplicate_correlations(common)
		director.correlations_active = director.correlations_candidate
		director.correlations_original = director.correlations_active
		director.correlations_last = director.correlations_active
		if common.have_active_configuration():
			director.correlations_active.rank()
		director.correlations_active.print_the_correlations(
			director.width, director.decimals, common)
		# director.correlations_active.print_the_correlations(
		# 	director.width, director.decimals, common)
		common.create_plot_for_plot_and_gallery_tabs("heatmap_corr")
		nitem = director.correlations_active.nitem
		director.title_for_table_widget = (
			f"Correlation matrix has {nitem} items")
		director.create_widgets_for_output_and_log_tabs()
		director.set_focus_on_tab('Plot')
		director.record_command_as_successfully_completed()
		return

# --------------------------------------------------------------------------


class CreateCommand:
	""" The Create command is used to build the active configuration.
	"""
	def __init__(
			self,
			director: Status,
			common: Spaces) -> None:

		self._director = director
		self.common = common
		director.command = "Create"
		director.configuration_candidate.ndim = 1
		director.configuration_candidate.npoint = 1
		director.configuration_candidate.dim_labels.clear()
		director.configuration_candidate.dim_names.clear()
		director.configuration_candidate.point_labels.clear()
		director.configuration_candidate.point_names.clear()
		director.configuration_candidate.point_coords = pd.DataFrame()
		# file = ""
		self._shape_title = "Set shape of new configuration"
		self._shape_items = [
			"Set number of dimensions",
			"Set number of points"]
		self._shape_default_values = [
			self._director.configuration_candidate.ndim,
			self._director.configuration_candidate.npoint]
		self._shape_integers = True
		self._dims_title = "Enter dimension names"
		self._dims_label = ("Type dimension name, "
			"use tab to advance to next dimension:")
		self._dims_max_chars = 32
		self._dims_labels_title = \
			"Enter dimension labels, maximum four characters"
		self._dims_labels_label = \
			"Type labels, use tab to advance to next label:"
		self._dims_labels_max_chars = 4
		self._pts_names_title = "Enter point names"
		self._pts_names_label = "Type names, use tab to advance to next name:"
		self._pts_names_max_chars = 32
		self._pts_labels_title = \
			"Enter points labels, maximum four characters"
		self._pts_labels_label = \
			"Type labels, use tab to advance to next label:"
		self._pts_labels_max_chars = 4
		self._methods_title = "Method to specify coordinates"
		self._methods_options_title = "Select method"
		self._methods_options = ["Random", "Ordered", "Enter values"]
		self._coords_title = "Set point coordinates"
		self._coords_label \
			= (
				"Enter coordinate for each point on each dimension\n"
				"Use tab to advance to next coordinate")
		return

	# ------------------------------------------------------------------------

	def execute(
			self,
			common: Spaces) -> None:
		
		director = self._director
		common = self.common

		director.record_command_as_selected_and_in_process()
		director.optionally_explain_what_command_does()
		self._establish_shape_for_new_configuration(
			self._shape_title, self._shape_items, self._shape_integers)
		# 	self._shape_default_values)
		director.configuration_candidate.range_dims = \
			range(director.configuration_candidate.ndim)
		director.configuration_candidate.range_points = \
			range(director.configuration_candidate.npoint)
		self._create_labeling_for_dimensions()
		self._create_labeling_for_points()
		method = self._create_method_to_create_coordinates()
		self._establish_coordinates(method)
		director.dependency_checker.detect_consistency_issues()
		director.configuration_candidate.inter_point_distances()
		director.configuration_active = director.configuration_candidate
		director.configuration_original = director.configuration_active
		director.configuration_last = director.configuration_active
		if common.have_similarities():
			director.similarities_active.rank_similarities()
		director.configuration_active.print_active_function()
		common.create_plot_for_plot_and_gallery_tabs(
			"configuration")
		ndim = director.configuration_active.ndim
		npoint = director.configuration_active.npoint
		director.title_for_table_widget = (
			f"Configuration has {ndim} dimensions and {npoint} points")
		director.create_widgets_for_output_and_log_tabs()
		director.record_command_as_successfully_completed()
		return

# ------------------------------------------------------------------------
	def _establish_shape_for_new_configuration_initialize_variables(
			self) -> None:

		self.create_needs_shape_title = "Create"
		self.create_needs_shape_message = (
			"Need number of dimensions and points for "
			"new configuration")

	# ------------------------------------------------------------------------

	def _establish_shape_for_new_configuration(
			self, title: str, items: list[str],
			integers: bool) -> None: # noqa: FBT001
			# default_values: list[int]) -> None:

		director = self._director
		self._establish_shape_for_new_configuration_initialize_variables()
		dialog = ModifyValuesDialog(
			title, items, integers,
			default_values=self._shape_default_values)
		dialog.selected_items()
		result = dialog.exec()
		if result == QDialog.Accepted:
			value = dialog.selected_items()
			ndim = value[0][1]
			npoint = value[1][1]
		else:
			raise SpacesError(
				self.create_needs_shape_title,
				self.create_needs_shape_message)

		director.configuration_candidate.ndim = ndim
		director.configuration_candidate.npoint = npoint

		return

# --------------------------------------------------------------------------

	def _create_labeling_for_dimensions_initialize_variables(self) -> None:

		self.create_needs_dimensions_title = self._director.command
		self.create_needs_dimensions_message = ("Needs dimensions")

# --------------------------------------------------------------------------

	def _create_labeling_for_dimensions(self) -> None:

		director = self._director
		
		self._create_labeling_for_dimensions_initialize_variables()
		range_dims = director.configuration_candidate.range_dims
		dims_title = self._dims_title
		dims_label = self._dims_label
		dims_max_chars = self._dims_max_chars
		# dim_names = director.configuration_candidate.dim_names

		dims_labels_title = self._dims_labels_title
		dims_labels_label = self._dims_labels_label
		dims_labels_max_chars = self._dims_labels_max_chars

		default_names = [f"Dimension {n + 1}" for n in range_dims]
		dialog = SetNamesDialog(
			dims_title, dims_label, default_names, dims_max_chars)
		if dialog.exec() == QDialog.Accepted:
			dim_names = dialog.getNames()
		else:
			raise SelectionError(
				self.create_needs_dimensions_title,
				self.create_needs_dimensions_message)

		default_labels = [dim_names[n][0:4] for n in range_dims]
		dialog = SetNamesDialog(
			dims_labels_title, dims_labels_label,
			default_labels, dims_labels_max_chars)
		if dialog.exec() == QDialog.Accepted:
			dim_labels = dialog.getNames()
		else:
			raise SelectionError(
				self.create_needs_dimensions_title,
				self.create_needs_dimensions_message)

		director.configuration_candidate.dim_names = dim_names
		director.configuration_candidate.dim_labels = dim_labels

		return

# --------------------------------------------------------------------------

	def _create_labeling_for_points_initialize_variables(self) -> None:

		self.create_needs_points_title = self._director.command
		self.create_needs_points_message = (
			"Needs points to create configuration")
		
# --------------------------------------------------------------------------

	def _create_labeling_for_points(self) -> None:

		director = self._director

		self._create_labeling_for_points_initialize_variables()

		range_points = director.configuration_candidate.range_points
		pts_names_title = self._pts_names_title
		pts_names_label = self._pts_names_label
		pts_names_max_chars = self._pts_names_max_chars
		pts_labels_title = self._pts_labels_title
		pts_labels_label = self._pts_labels_label
		pts_labels_max_chars = self._pts_labels_max_chars

		default_names = [f"Point {n + 1}" for n in range_points]
		dialog = SetNamesDialog(
			pts_names_title, pts_names_label,
			default_names, pts_names_max_chars)
		if dialog.exec() == QDialog.Accepted:
			point_names = dialog.getNames()
		else:
			raise SelectionError(
				self.create_needs_points_title,
				self.create_needs_points_message)

		default_labels = [point_names[n][0:4] for n in range_points]
		dialog = SetNamesDialog(
			pts_labels_title, pts_labels_label,
			default_labels, pts_labels_max_chars)
		if dialog.exec() == QDialog.Accepted:
			point_labels = dialog.getNames()
		else:
			raise SelectionError(
				self.create_needs_points_title,
				self.create_needs_points_message)

		director.configuration_candidate.point_names = point_names
		director.configuration_candidate.point_labels = point_labels

		return

# --------------------------------------------------------------------------

	def _create_method_to_create_coordinates_initialize_variables(self) \
		-> None:
		self.create_needs_method_title = self._director.command
		self.create_needs_method_message = (
			"Needs method to create configuration")

# --------------------------------------------------------------------------

	def _create_method_to_create_coordinates(self) -> str:

		self._create_method_to_create_coordinates_initialize_variables()

		methods_title = self._methods_title
		methods_title_options_title = self._methods_options_title
		methods_options = self._methods_options

		# reply = "unknown"
		dialog = ChoseOptionDialog(
			methods_title, methods_title_options_title, methods_options)
		result = dialog.exec()
		if result == QDialog.Accepted:
			selected_option = dialog.selected_option	# + 1
			match selected_option:
				case 0:
					reply = "random"
				case 1:
					reply = "ordered"
				case 2:
					reply = "enter values"
				case _:
					# reply = "unknown"
					raise SelectionError(
						self.create_needs_method_title,
						self.create_needs_method_message)

		else:
			raise SelectionError(
				self.create_needs_method_title,
				self.create_needs_method_message)

		return reply

# --------------------------------------------------------------------------

	def _establish_coordinates_initialize_variables(self) -> None:

		self.create_needs_coordinates_title = self._director.command
		self.create_needs_coordinates_message = (
			"Needs coordinates to create configuration")

# --------------------------------------------------------------------------

	def _establish_coordinates(
			self,
			method: str) -> None:

		self._establish_coordinates_initialize_variables()
		config = self._director.configuration_candidate
		
		point_coords = self._generate_coordinates_by_method(
			method, config)
		config.point_coords = point_coords

	def _generate_coordinates_by_method(
			self, method: str, config: ConfigurationFeature) -> pd.DataFrame:
		"""Generate coordinates based on the specified method."""
		method_handlers = {
			"random": self._generate_random_coordinates,
			"ordered": self._generate_ordered_coordinates,
			"enter values": self._generate_user_input_coordinates
		}
		
		handler = method_handlers.get(method)
		if handler is None:
			raise MissingInformationError(
				self.create_needs_coordinates_title,
				self.create_needs_coordinates_message)
				
		return handler(config)

	def _generate_random_coordinates(self, config: ConfigurationFeature) \
		-> pd.DataFrame:
		"""Generate random coordinates for points."""
		rng = np.random.default_rng()
		all_point_coords = [
			[rng.uniform(-1.5, 1.5) for _ in config.range_dims]
			for _ in config.range_points
		]
		return pd.DataFrame(
			all_point_coords,
			index=config.point_names,
			columns=config.dim_labels)

	def _generate_ordered_coordinates(self, config: ConfigurationFeature) \
		-> pd.DataFrame:
		"""Generate ordered coordinates for points."""
		all_point_coords = []
		my_next = 1
		
		for each_point in config.range_points:
			a_point_coords = []
			for each_dim in config.range_dims:
				if each_point % config.ndim == each_dim:
					coord = float(my_next)
					if each_dim == config.ndim - 1:
						my_next += 1
				else:
					coord = 0.0
				a_point_coords.append(coord)
			all_point_coords.append(a_point_coords)
			
		return pd.DataFrame(
			all_point_coords,
			columns=config.dim_names,
			index=config.point_names)

	def _generate_user_input_coordinates(self, config: ConfigurationFeature) \
		-> pd.DataFrame:
		"""Generate coordinates from user input via dialog."""
		matrix_dialog = MatrixDialog(
			self._coords_title, self._coords_label,
			config.dim_names, config.point_names)
			
		try:
			result = matrix_dialog.exec()
			if result == QDialog.Accepted:
				matrix = matrix_dialog.get_matrix()
				print("Matrix:")
				for row in matrix:
					print(row)
				return pd.DataFrame(
					matrix,
					columns=config.dim_names,
					index=config.point_names)
			
			raise MissingInformationError(
				self.create_needs_coordinates_title,
				self.create_needs_coordinates_message)
		finally:
			del matrix_dialog

# --------------------------------------------------------------------------


class DeactivateCommand:
	""" The Deactivate command is used to abandon the active
		configuration, or existing similarities or correlations.
	"""
	def __init__(
			self,
			director: Status,
			common: Spaces) -> None:

		self._director = director
		self.common = common
		self._director.command = "Deactivate"
		# selected_items = []
		self._items_to_deactivate_title = "Select items to deactivate"
		self._deac_config_txt = (
				"Active configuration and dependent information have "
				"been abandoned.")
		self._deac_targ_txt = (
				"Target configuration and dependent information "
				"have been abandoned.")
		self._deac_grpd_txt = "Grouped data have been abandoned."
		self._deac_simi_txt = "Similarities have been abandoned."
		self._deac_refs_txt = "Reference points have been abandoned."
		self._deac_corr_txt = "Correlations have been abandoned."
		self._deac_eval_txt = "Evaluations have been abandoned."
		self._deac_ind_txt = "Data for individuals have been abandoned."
		self._deac_scor_txt = "Scores have been abandoned."

	def execute(
			self,
			common: Spaces) -> None: # noqa: ARG002

		self._director.record_command_as_selected_and_in_process()
		self._director.optionally_explain_what_command_does()
		self._determine_whether_anything_can_be_deactivated()
		items_to_deactivate \
			= self._get_items_to_deactivate_from_user()
		self._deactivate_selected_items(items_to_deactivate)
		self._director.deactivated_items = items_to_deactivate
		self._print_items_deactivated(items_to_deactivate)
		self._director.title_for_table_widget = "Deactivated items:"
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.set_focus_on_tab('Output')
		self._director.record_command_as_successfully_completed()
		return

# --------------------------------------------------------------------------

	def _determine_whether_anything_can_be_deactivated_init_variables(
			self) -> None:
		
		self.deactivate_dependency_error_title = "Nothing has been established"
		self.deactivate_dependency_error_message = (
			"Something must be established before anything "
			"can be deactivated.")
		
# --------------------------------------------------------------------------

	def _determine_whether_anything_can_be_deactivated(self) -> None:

		self._determine_whether_anything_can_be_deactivated_init_variables()
		
		if (not self._director.common.have_active_configuration()) \
			and (not self._director.common.have_target_configuration()) \
			and (not self._director.common.have_grouped_data()) \
			and (not self._director.common.have_similarities()) \
			and (not self._director.common.have_reference_points()) \
			and (not self._director.common.have_correlations()) \
			and (not self._director.common.have_evaluations()) \
			and (not self._director.common.have_individual_data())\
			and (not self._director.common.have_scores()):
	
			raise DependencyError(
				self.deactivate_dependency_error_title,
				self.deactivate_dependency_error_message)

		return

# --------------------------------------------------------------------------

	def _get_items_to_deactivate_title_init_variables(self) -> None:

		self.deactivate_needs_items_title = self._director.command
		self.deactivate_needs_items_message = (
			"Need items to deactivate")
		
# --------------------------------------------------------------------------

	def _get_items_to_deactivate_from_user(self) -> list[str]:

		self._get_items_to_deactivate_title_init_variables()
		items_to_deactivate_title = self._items_to_deactivate_title

		items = self._collect_available_items_for_deactivation()
		items_to_deactivate = self._get_user_selection_from_dialog(
			items_to_deactivate_title, items)
		
		return items_to_deactivate

	def _collect_available_items_for_deactivation(self) -> list[str]:
		"""Collect all available items that can be deactivated."""
		items = []
		common = self._director.common

		item_checks = [
			(common.have_active_configuration, "Active configuration"),
			(common.have_target_configuration, "Target"),
			(common.have_grouped_data, "Grouped data"),
			(common.have_similarities, "Similarities"),
			(common.have_reference_points, "Reference points"),
			(common.have_correlations, "Correlations"),
			(common.have_evaluations, "Evaluations"),
			(common.have_individual_data, "Individual data"),
			(common.have_scores, "Scores"),
		]

		for check_method, item_name in item_checks:
			if check_method():
				items.append(item_name)

		return items

	def _get_user_selection_from_dialog(
			self, title: str, items: list[str]) -> list[str]:
		"""Get user selection from dialog and validate it."""
		dialog = SelectItemsDialog(title, items)
		
		try:
			if dialog.exec() == QDialog.Accepted:
				items_to_deactivate = dialog.selected_items()
			else:
				raise SelectionError(
					self.deactivate_needs_items_title,
					self.deactivate_needs_items_message)

			if len(items_to_deactivate) == 0:
				raise SelectionError(
					self.deactivate_needs_items_title,
					self.deactivate_needs_items_message)
			
			return items_to_deactivate
		finally:
			del dialog

	# ------------------------------------------------------------------------

	def _deactivate_selected_items(
			self,
			items_to_deactivate: list[str]) -> None:

		deac_config_txt = self._deac_config_txt
		deac_targ_txt = self._deac_targ_txt
		deac_grpd_txt = self._deac_grpd_txt
		deac_simi_txt = self._deac_simi_txt
		deac_refs_txt = self._deac_refs_txt
		deac_corr_txt = self._deac_corr_txt
		deac_eval_txt = self._deac_eval_txt
		deac_ind_txt = self._deac_ind_txt
		deac_scor_txt = self._deac_scor_txt

		deactivated_descriptions = []

		# consider using a dictionary to hold the items to deactivate

		if "Active configuration" in items_to_deactivate:
			self._director.abandon_configuration()
			deactivated_descriptions.append(deac_config_txt)
		if "Target" in items_to_deactivate:
			self._director.abandon_target()
			deactivated_descriptions.append(deac_targ_txt)
		if "Grouped data" in items_to_deactivate:
			self._director.abandon_grouped_data()
			deactivated_descriptions.append(deac_grpd_txt)
		if "Similarities" in items_to_deactivate:
			self._director.abandon_similarities()
			deactivated_descriptions.append(deac_simi_txt)
		if "Reference points" in items_to_deactivate:
			self._director.abandon_reference_points()
			deactivated_descriptions.append(deac_refs_txt)
		if "Correlations" in items_to_deactivate:
			self._director.abandon_correlations()
			deactivated_descriptions.append(deac_corr_txt)
		if "Evaluations" in items_to_deactivate:
			self._director.abandon_evaluations()
			deactivated_descriptions.append(deac_eval_txt)
		if "Individual data" in items_to_deactivate:
			self._director.abandon_individual_data()
			deactivated_descriptions.append(deac_ind_txt)
		if "Scores" in items_to_deactivate:
			self._director.abandon_scores()
			deactivated_descriptions.append(deac_scor_txt)

		self._director.deactivated_descriptions = deactivated_descriptions

		return

	# ------------------------------------------------------------------------

	def _print_items_deactivated(
			self,
			items_to_deactivate: list[str]) -> None:

		deac_config_txt = self._deac_config_txt
		deac_targ_txt = self._deac_targ_txt
		deac_grpd_txt = self._deac_grpd_txt
		deac_simi_txt = self._deac_simi_txt
		deac_refs_txt = self._deac_refs_txt
		deac_corr_txt = self._deac_corr_txt
		deac_eval_txt = self._deac_eval_txt
		deac_ind_txt = self._deac_ind_txt
		deac_scor_txt = self._deac_scor_txt

		if "Active configuration" in items_to_deactivate:
			print(deac_config_txt)
		if "Target" in items_to_deactivate:
			print(deac_targ_txt)
		if "Grouped data" in items_to_deactivate:
			print(deac_grpd_txt)
		if "Similarities" in items_to_deactivate:
			print(deac_simi_txt)
		if "Reference points" in items_to_deactivate:
			print(deac_refs_txt)
		if "Correlations" in items_to_deactivate:
			print(deac_corr_txt)
		if "Evaluations" in items_to_deactivate:
			print(deac_eval_txt)
		if "Individual data" in items_to_deactivate:
			print(deac_ind_txt)
		if "Scores" in items_to_deactivate:
			print(deac_scor_txt)
		return

	# ------------------------------------------------------------------------

	def _display(self) -> QTableWidget:
		#
		gui_output_as_widget = self._create_table_widget_for_deactivations()
		#
		self._director.set_column_and_row_headers(
			gui_output_as_widget,
			[], [])
		#
		self._director.resize_and_set_table_size(gui_output_as_widget, 4)
		#
		self._director.output_widget_type = "Table"
		return gui_output_as_widget

	# ------------------------------------------------------------------------

	def _create_table_widget_for_deactivations(self) -> QTableWidget:

		deactivated_items = self._director.deactivated_items
		deactivated_descriptions = self._director.deactivated_descriptions
		#
		table_widget = QTableWidget(len(deactivated_items), 1)
		#
		for each_item_deactivated in range(len(deactivated_items)):
			table_widget.setItem(
				each_item_deactivated, 0,
				QTableWidgetItem(deactivated_descriptions[
					each_item_deactivated]))
		return table_widget


# --------------------------------------------------------------------------


class EvaluationsCommand:
	""" The Evaluations command reads in feeling thermometer
	data from csv file
	"""
	def __init__(
			self,
			director: Status,
			common: Spaces) -> None:

		self._director = director
		self.common = common
		self._director.command = "Evaluations"
		# all_names = []
		self._director.range_items = range(0)
		self._director.item_names = []
		self._director.item_labels = []
		self._director.correlations_active.correlations = []
		self._director.file_caption = "Open evaluations"
		self._director.file_filter = "*.csv"

		return

	# ------------------------------------------------------------------------

	def execute(self, common: Spaces) -> None:

		command = self._director.command

		evaluations_candidate = self._director.evaluations_candidate
		file_caption = self._director.file_caption
		file_filter = self._director.file_filter

		self._director.record_command_as_selected_and_in_process()
		self._director.optionally_explain_what_command_does()
		self._director.dependency_checker.detect_dependency_problems()
		file = self._director.get_file_name_and_handle_nonexistent_file_names(
			file_caption, file_filter)
		self._read_evaluations(file)
		self._director.dependency_checker.detect_consistency_issues()
		self._director.evaluations_active = evaluations_candidate
		self._director.evaluations_original = self._director.evaluations_active
		self._director.evaluations_last = self._director.evaluations_active
		self._director.evaluations_active.print_the_evaluations()
		self._director.evaluations_active.summarize_evaluations()
		self._compute_correlations_from_evaluations(common)
		self._director.title_for_table_widget = command
		self._director.common.create_plot_for_plot_and_gallery_tabs(
			"evaluations")
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.record_command_as_successfully_completed()

		return

	# ------------------------------------------------------------------------

	def _compute_correlations_from_evaluations(
			self,
			common: Spaces) -> None:

		nreferent = self._director.evaluations_active.nreferent
		item_names = self._director.evaluations_active.item_names
		item_labels = self._director.evaluations_active.item_labels
		evaluations = self._director.evaluations_active.evaluations
		correlations = []

		correlations_as_dataframe = evaluations.corr(method='pearson')

		for each_col in range(1, nreferent):
			# Create a list comprehension instead of appending to a list
			a_row = [
				correlations_as_dataframe.iloc[each_row, each_col]
				for each_row in range(each_col)
			]
			correlations.append(a_row)
		self._director.correlations_active.nreferent = nreferent
		self._director.correlations_active.nitem = nreferent
		self._director.correlations_active.item_names = item_names
		self._director.correlations_active.item_labels = item_labels
		self._director.correlations_active.correlations = correlations
		self._director.correlations_active.correlations_as_dataframe = \
			correlations_as_dataframe
		self._director.correlations_active.duplicate_correlations(common)
		self._director.correlations_active.ndyad = \
			len(self._director.correlations_active.correlations_as_list)
		self._director.correlations_active.n_pairs = \
			len(self._director.correlations_active.correlations_as_list)
		self._director.correlations_active.range_dyads = \
			range(self._director.correlations_active.ndyad)


# ------------------------------------------------------------------------

	def _read_evaluations_initialize_variables(
			self) -> None:
		
		self._problem_reading_evaluations_title: str = \
			"Problem reading evaluations"
		self._problem_reading_evaluations_message: str = \
			"Review file name and contents"
		
	# ------------------------------------------------------------------------

	def _read_evaluations(
			self,
			file: str) -> None:

		self._read_evaluations_initialize_variables()

		# item_names = []
		item_labels = []

		try:
			evaluations = pd.read_csv(file)
			(nevaluators, nreferent) = evaluations.shape
			nitem = nreferent
			range_items = range(nreferent)
			item_names = \
				evaluations.columns.tolist()
			item_labels = [label[ITEM_LABEL_FIRST_COLUMN:ITEM_LABEL_LENGTH] \
				for label in item_names]
			if len(item_names) < MUST_HAVE_AT_LEAST_TWO_ITEMS_EVALUATED:
				raise SpacesError(
					self._problem_reading_evaluations_title,
					self._problem_reading_evaluations_message)
		except (
			FileNotFoundError, PermissionError,
			pd.errors.EmptyDataError, pd.errors.ParserError):
			raise SpacesError(
				self._problem_reading_evaluations_title,
				self._problem_reading_evaluations_message
			) from None

		self._director.evaluations_candidate.evaluations = evaluations
		self._director.evaluations_candidate.nevaluators = nevaluators
		self._director.evaluations_candidate.nreferent = nreferent
		self._director.evaluations_candidate.nitem = nitem
		self._director.evaluations_candidate.range_items = range_items
		self._director.evaluations_candidate.item_names = item_names
		self._director.evaluations_candidate.item_labels = item_labels
		return


	# ------------------------------------------------------------------------


class ExitCommand:

	def __init__(
			self,
			director: Status,
			common: Spaces) -> None:

		self._director = director
		self.common = common
		self.command = "Exit"
		return

	# ------------------------------------------------------------------------

	def execute(
			self,
			common: Spaces) -> None: # noqa: ARG002

		sys.exit()
		return



	# ------------------------------------------------------------------------


class GroupedDataCommand:
	""" The Grouped command reads a file with coordinates for a
	set of groups. The number of dimensions must be the same as
	the active configuration.
	"""
	def __init__(
			self,
			director: Status,
			common: Spaces) -> None:

		self._director = director
		self.common = common
		self._director.command = "Grouped data"
		self._director.grouped_data_candidate.file_handle = ""
		self._director.grouped_data_candidate.ndim = 0
		self._director.grouped_data_candidate.dim_labels.clear()
		self._director.grouped_data_candidate.dim_names.clear()
		self._director.grouped_data_candidate.group_labels.clear()
		self._director.grouped_data_candidate.group_codes.clear()
		self._director.grouped_data_candidate.group_names.clear()
		self._director.grouped_data_candidate.group_coords = pd.DataFrame()
		self._file_caption: str = "Open grouped data"
		self._file_filter: str = "*.txt"
		return

	# ------------------------------------------------------------------------

	def execute(
			self,
			common: Spaces) -> None: # noqa: ARG002

		self._director.record_command_as_selected_and_in_process()
		self._director.optionally_explain_what_command_does()
		self._director.dependency_checker.detect_dependency_problems()
		file = self._director.grouped_data_candidate.file_handle = \
			self._director.get_file_name_and_handle_nonexistent_file_names(
				self._file_caption, self._file_filter)
		self._read_grouped_data(file)
		self._director.dependency_checker.detect_consistency_issues()
		self._director.grouped_data_active = \
			self._director.grouped_data_candidate
		self._director.grouped_data_original = \
			self._director.grouped_data_active
		self._director.grouped_data_last = self._director.grouped_data_active
		self._director.grouped_data_active.print_grouped_function()
		self._director.common.create_plot_for_plot_and_gallery_tabs(
			"grouped_data")
		grouping_var = self._director.grouped_data_active.grouping_var
		ndim = self._director.grouped_data_active.ndim
		ngroups = self._director.grouped_data_active.ngroups
		self._director.title_for_table_widget = (
			f"Configuration is based on {grouping_var}"
			f" and has {ndim} dimensions and {ngroups} points")
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.set_focus_on_tab('Plot')
		self._director.record_command_as_successfully_completed()

		return
	
# ------------------------------------------------------------------------

	def _read_grouped_data_initialized_variables(
		self, file_name: str, file_handle: TextIO) -> None:

		self.grouped_data_file_not_found_error_title = "Grouped data"
		self.grouped_data_file_not_found_error_message = (
			"File not found: \n"
			f"{file_name}")
		self.grouped_data_file_not_found_error_title = "Grouped data"
		self.grouped_data_empty_header_error_message = (
			"The header line is empty in file:."
			f"\n{getattr(file_handle, 'name', '<unknown file>')}")
		self.grouped_data_file_not_grouped_error_title = "Grouped data"
		self.grouped_data_file_not_grouped_error_message = (
			"File is not a grouped data file:\n"
			f"{getattr(file_handle, 'name', '<unknown file>')}")
		self.missing_grouping_var_error_title = "Grouped data"
		self.missing_grouping_var_error_message = (
			"Line for grouping variable name is empty in file: "
			f"\n{file_handle}")
		self.group_data_file_not_found_error_title = "Grouped data"
		self.group_data_file_not_found_error_message = (
			"File not found: \n"
				f"{file_handle}")
	# ------------------------------------------------------------------------

	def _read_grouped_data(
			self,
			file_name: str) -> None:
		""" read_groups - is used by group command needing to read
		a group configuration from a file.
		"""
		# command = self._director.command
		file_handle = self._director.grouped_data_candidate.file_handle
		
		self._read_grouped_data_initialized_variables(
			file_name, file_handle)

		dim_names = []
		dim_labels = []
		group_names = []
		group_labels = []
		group_codes = []
		try:
			with Path(file_name).open() as file_handle:
				header = file_handle.readline()
				if len(header) == 0:
					raise SpacesError(
						self.grouped_data_file_not_found_error_title,
						self.grouped_data_file_not_found_error_message
					) from None

				if header.lower().strip() != "grouped":
					raise SpacesError(
						self.grouped_data_file_not_grouped_error_title,
						self.grouped_data_file_not_grouped_error_message
					) from None

				grouping_var = file_handle.readline()
				if len(grouping_var) == 0:
					raise SpacesError(
						self.missing_grouping_var_error_title,
						self.missing_grouping_var_error_message
					) from None
				grouping_var = grouping_var.strip("\n")
				dim = file_handle.readline()
				dim_list = dim.strip("\n").split()
				expected_dim = int(dim_list[0])
				expected_groups = int(dim_list[1])
				range_groups = range(expected_groups)
				range_dims = range(expected_dim)
				for _ in range(expected_dim):
					(dim_label, dim_name) = file_handle.readline().split(';')
					dim_labels.append(dim_label)
					dim_name = dim_name.strip("\n")
					dim_names.append(dim_name)
				for i in range(expected_groups):
					(group_label, group_code, group_name) \
						= file_handle.readline().split(';')
					group_names.append(group_name)
					group_labels.append(group_label)
					group_codes.append(group_code)

					group_names[i] = group_names[i].strip()
				group_coords = pd.DataFrame(
					[[float(g) for g in
						file_handle.readline().split()]
						for i in range(expected_groups)],
					index=group_names,
					columns=dim_labels
				)
		except FileNotFoundError:
			raise SpacesError(
				self.group_data_file_not_found_error_title,
				self.group_data_file_not_found_error_message) from None

		self._director.grouped_data_candidate.grouping_var = grouping_var
		self._director.grouped_data_candidate.ndim = expected_dim
		self._director.grouped_data_candidate.dim_names = dim_names
		self._director.grouped_data_candidate.group_labels = dim_labels
		self._director.grouped_data_candidate.npoint = expected_groups
		self._director.grouped_data_candidate.ngroups = expected_groups
		self._director.grouped_data_candidate.range_groups = range_groups
		self._director.grouped_data_candidate.group_names = group_names
		self._director.grouped_data_candidate.group_labels = group_labels
		self._director.grouped_data_candidate.group_codes = group_codes
		self._director.grouped_data_candidate.group_coords = group_coords
		self._director.grouped_data_candidate.range_dims = range_dims

		return



	# ------------------------------------------------------------------------


class IndividualsCommand:
	""" The Individuals command is used to establish filters for individuals.
	"""
	def __init__(
			self,
			director: Status,
			common: Spaces) -> None:

		self._director = director
		self.common = common
		self._director.command = "Individuals"
		self._director.individuals_candidate.hor_axis_name = "Unknown"
		self._director.individuals_candidate.n_individ = 0
		self._director.individuals_candidate.var_names = []
		self._director.individuals_candidate.vert_axis_name = "Unknown"
		self._director.individuals_candidate.ind_vars = pd.DataFrame()
		self._file_caption = "Open individual data"
		self._file_filter = "*.csv"

		return

	# ------------------------------------------------------------------------

	def execute(
			self,
			common: Spaces) -> None: # noqa: ARG002

		self._director.record_command_as_selected_and_in_process()
		self._director.optionally_explain_what_command_does()
		file = self._director.get_file_name_and_handle_nonexistent_file_names(
			self._file_caption, self._file_filter)
		self._read_individuals_function(file)
		self._director.dependency_checker.detect_consistency_issues()
		self._director.individuals_active = \
			self._director.individuals_candidate
		self._director.individuals_original = \
			self._director.individuals_candidate
		self._director.individuals_last = \
			self._director.individuals_candidate
		self._director.individuals_active.print_individuals()
		self._compute_summary_statistics()
		n_individ = self._director.individuals_active.n_individ
		self._director.title_for_table_widget = (
			f"The file contains {n_individ} individuals.")
		# self._director.common.create_plot_for_plot_and_gallery_tabs(
		# "individuals")
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.set_focus_on_tab('Output')
		self._director.record_command_as_successfully_completed()
		return


# ------------------------------------------------------------------------
	
	def _read_individuals_function_initialize_variables(self) -> None:

		self._problem_reading_individuals_title: str = \
			"Problem reading individuals"
		self._problem_reading_individuals_message: str = \
			"Review file name and contents"

	# ------------------------------------------------------------------------

	def _read_individuals_function(
			self,
			file: str) -> None:

		self._read_individuals_function_initialize_variables()
		try:
			ind_vars = pd.read_csv(file)
			n_individ = ind_vars.shape[0]
			var_names = ind_vars.columns
			if len(var_names) < MAXIMUM_NUMBER_OF_VAR_NAMES:
				raise SpacesError(
					self._problem_reading_individuals_title,
					self._problem_reading_individuals_message)
		except (
			FileNotFoundError, PermissionError,
			pd.errors.EmptyDataError, pd.errors.ParserError):
			raise SpacesError(
				self._problem_reading_individuals_title,
				self._problem_reading_individuals_message) from None

		self._director.individuals_candidate.ind_vars = ind_vars
		self._director.individuals_candidate.n_individ = n_individ
		self._director.individuals_candidate.var_names = var_names

		return

	# ------------------------------------------------------------------------

	def _compute_summary_statistics(self) -> None:

		ind_vars = self._director.individuals_active.ind_vars

		people_vars = copy.deepcopy(ind_vars)
		people_vars.drop(people_vars.columns[0], axis=1, inplace=True)
		temp_stats_inds = people_vars.describe(
			percentiles=[.25, .5, .75]).transpose()
		stats_inds = temp_stats_inds[
			['mean', 'std', 'min', 'max', '25%', '50%', '75%']]
		stats_inds.columns = [
			'Mean', 'Standard\nDeviation', 'Min', 'Max', 'First\nquartile',
			'Median', 'Third\nquartile']
		new_order = [
			'Mean', 'Standard\nDeviation', 'Min',
			'First\nquartile', 'Median', 'Third\nquartile', 'Max']
		stats_inds = stats_inds.reindex(columns=new_order)
		stats_inds = stats_inds.sort_values(by="Mean", ascending=False)
		avg = ind_vars.mean()
		avg.sort_values(inplace=True)

		self._director.individuals_active.stats_inds = stats_inds
		self._director.individuals_active.avg = avg

		return

# --------------------------------------------------------------------------


class NewGroupedDataCommand:
	""" The New grouped data command is used to build the active
	grouped data configuration.
	"""
	def __init__(
			self,
			director: Status,
			common: Spaces) -> None:

		self._director = director
		self.common = common
		self._director.command = "New grouped data"
		self._director.grouped_data_candidate.ndim = 0
		self._director.grouped_data_candidate.ngroups = 0
		self._director.grouped_data_candidate.group_codes.clear()
		self._director.grouped_data_candidate.dim_labels.clear()
		self._director.grouped_data_candidate.dim_names.clear()
		self._director.grouped_data_candidate.group_labels.clear()
		self._director.grouped_data_candidate.group_names.clear()
		self._director.grouped_data_candidate.group_coords = pd.DataFrame()
		# file = ""
		self._group_title = "Grouping variable"
		self._group_label = "Enter name of grouping variable"
		self._group_default = {"Grouping variable"}
		self._group_max_chars = 32
		self._shape_title = "Set shape of new grouped data configuration"
		self._shape_items = [
			"Set number of dimensions",
			"Set number of groups"]
		self._shape_default_values = [1, 1]
		self._shape_integers = True
		self._dims_title = "Enter dimension names"
		self._dims_label = \
			"Type dimension name, use tab to advance to next dimension:"
		self._dims_max_chars = 32
		self._dims_labels_title = \
			"Enter dimension labels, maximum four characters"
		self._dims_labels_label = \
			"Type labels, use tab to advance to next label:"
		self._dims_labels_max_chars = 4
		self._pts_names_title = "Enter group names"
		self._pts_names_label = "Type names, use tab to advance to next name:"
		self._pts_names_max_chars = 32
		self._pts_labels_title = "Enter group labels, maximum four characters"
		self._pts_labels_label = \
			"Type labels, use tab to advance to next label:"
		self._pts_labels_max_chars = 4
		self._coords_title = "Set group coordinates"
		self._coords_label \
			= (
				"Enter coordinate for each group on each dimension\n"
				"Use tab to advance to next coordinate")
		self._director.grouped_data_candidate.grouping_var = \
			"Grouping variable unknown"
		return

	# ------------------------------------------------------------------------

	def execute(
			self,
			common: Spaces) -> None: # noqa: ARG002

		self._director.record_command_as_selected_and_in_process()
		self._director.optionally_explain_what_command_does()
		self._get_grouping_var()
		self._get_shape_for_new_grouped_data_configuration(
			self._shape_title, self._shape_items, self._shape_integers,
			self._shape_default_values)
		self._director.grouped_data_candidate.range_dims \
			= range(self._director.grouped_data_candidate.ndim)
		self._director.grouped_data_candidate.range_groups \
			= range(self._director.grouped_data_candidate.ngroups)
		self._create_labeling_for_dimensions()
		self._create_labeling_for_groups()
		self._establish_coordinates()
		self._director.dependency_checker.detect_consistency_issues()
		self._director.grouped_data_active = \
			self._director.grouped_data_candidate
		self._director.grouped_data_original = \
			self._director.grouped_data_active
		self._director.grouped_data_last = self._director.grouped_data_active
		self._director.grouped_data_candidate.print_grouped_function()
		self._create_grouped_plot_for_plot_and_gallery_tabs()
		self._director.set_focus_on_tab('Plot')
		self._director.title_for_table_widget = (
			"Configuration is based on "
			f"{self._director.grouped_data_candidate.grouping_var}"
			f" and has {self._director.grouped_data_candidate.ndim} "
			f"dimensions and "
			f"{self._director.grouped_data_candidate.ngroups} groups")
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.record_command_as_successfully_completed()
		return

# ------------------------------------------------------------------------

	def _get_grouping_var_initialize_variables(self) -> None:

		self.missing_grouping_var_error_title = (
			"New grouped data configuration")
		self.missing_grouping_var_error_message = (
			"Need name of grouping variable for "
			"new grouped data configuration")

# --------------------------------------------------------------------------

	def _get_grouping_var(self) -> None:

		self._get_grouping_var_initialize_variables()
		group_title = self._group_title
		group_label = self._group_label
		group_default = self._group_default
		group_max_chars = self._group_max_chars

		# group_var_list = []
		dialog = SetNamesDialog(
			group_title, group_label, group_default, group_max_chars)
		if dialog.exec() == QDialog.Accepted:
			group_var_list = dialog.getNames()
			grouping_var = group_var_list[0]
		else:
			raise SpacesError(
				self.missing_grouping_var_error_title,
				self.missing_grouping_var_error_message)

		self._director.grouped_data_candidate.grouping_var = grouping_var

		return

# ------------------------------------------------------------------------

	def _get_shape_for_new_grouped_data_configuration_initialize_variables(
			self) -> None:
		self.missing_new_group_shape_error_title = \
			"New grouped data configuration"
		self.missing_new_group_shape_error_message = (
			"Need number of dimensions and groups for "
			"new grouped data configuration")
		
	# ------------------------------------------------------------------------

	def _get_shape_for_new_grouped_data_configuration(
			self,
			title: str,
			items: list[str],
			integers: bool, #noqa: FBT001
			default_values: list) -> None:

		self.\
			_get_shape_for_new_grouped_data_configuration_initialize_variables()
		ndim = self._director.grouped_data_candidate.ndim
		ngroups = self._director.grouped_data_candidate.ngroups

		if ndim == 0:
			ndim = 1
		if ngroups == 0:
			ngroups = 1
		dialog = ModifyValuesDialog(
			title, items, integers, default_values)
		dialog.selected_items()
		result = dialog.exec()
		if result == QDialog.Accepted:
			value = dialog.selected_items()
			ndim = value[0][1]
			ngroups = value[1][1]
		else:
			raise SpacesError(
				self.missing_new_group_shape_error_title,
				self.missing_new_group_shape_error_message)

		self._director.grouped_data_candidate.ndim = ndim
		self._director.grouped_data_candidate.ngroups = ngroups
		return

# ------------------------------------------------------------------------

	def _create_labeling_for_groups_and_dimensions_initialize_variables(
			self) -> None:
		self.missing_group_labeling_error_title = \
			"New grouped data configuration"
		self.missing_group_labeling_error_message = (
			"Need names of groups for new grouped data configuration")

	# ------------------------------------------------------------------------

	def _create_labeling_for_dimensions(self) -> None:

		self._create_labeling_for_groups_and_dimensions_initialize_variables()
		range_dims = self._director.grouped_data_candidate.range_dims
		dims_title = self._dims_title
		dims_label = self._dims_label
		dims_max_chars = self._dims_max_chars
		dims_labels_title = self._dims_labels_title
		dims_labels_label = self._dims_labels_label
		dims_labels_max_chars = self._dims_labels_max_chars

		default_names = [f"Dimension {n + 1}" for n in range_dims]
		dialog = SetNamesDialog(
			dims_title, dims_label, default_names, dims_max_chars)
		if dialog.exec() == QDialog.Accepted:
			dim_names = dialog.getNames()
		else:
			raise SpacesError(
				self.missing_group_labeling_error_title,
				self.missing_group_labeling_error_message)

		default_labels = [dim_names[n][0:4] for n in range_dims]
		dialog = SetNamesDialog(
			dims_labels_title, dims_labels_label,
			default_labels, dims_labels_max_chars)
		if dialog.exec() == QDialog.Accepted:
			dim_labels = dialog.getNames()
		else:
			raise SpacesError(
				self.missing_group_labeling_error_title,
				self.missing_group_labeling_error_message)

		self._director.grouped_data_candidate.dim_names = dim_names
		self._director.grouped_data_candidate.dim_labels = dim_labels

		return

# --------------------------------------------------------------------------

	def _create_labeling_for_groups_initialize_variables(self) -> None:

		self.missing_group_names_error_title = \
			"New grouped data configuration"
		self.missing_group_names_error_message = (
			"Need names of groups for new grouped data configuration")
		self.missing_group_labels_error_title = \
			"New grouped data configuration"
		self.missing_group_labels_error_message = (
			"Need labels of groups for new grouped data configuration")


# --------------------------------------------------------------------------

	def _create_labeling_for_groups(self) -> None:

		self._create_labeling_for_groups_initialize_variables()
		range_groups = self._director.grouped_data_candidate.range_groups
		pts_names_title = self._pts_names_title
		pts_names_label = self._pts_names_label
		pts_names_max_chars = self._pts_names_max_chars
		pts_labels_title = self._pts_labels_title
		pts_labels_label = self._pts_labels_label
		pts_labels_max_chars = self._pts_labels_max_chars

		default_names = [f"Group {n + 1}" for n in range_groups]
		dialog = SetNamesDialog(
			pts_names_title, pts_names_label,
			default_names, pts_names_max_chars)
		if dialog.exec() == QDialog.Accepted:
			group_names = dialog.getNames()
		else:
			raise SpacesError(
				self.missing_group_names_error_title,
				self.missing_group_names_error_message)

		default_labels = [group_names[n][0:4] for n in range_groups]
		dialog = SetNamesDialog(
			pts_labels_title, pts_labels_label,
			default_labels, pts_labels_max_chars)
		if dialog.exec() == QDialog.Accepted:
			group_labels = dialog.getNames()
		else:
			raise SpacesError(
				self.missing_group_labels_error_title,
				self.missing_group_labels_error_message)

		self._director.grouped_data_candidate.group_names = group_names
		self._director.grouped_data_candidate.group_labels = group_labels

		return
	
# --------------------------------------------------------------------------

	def _establish_coordinates_initialize_variables(self) -> None:

		self.missing_coordinates_error_title = \
			"New grouped data configuration"
		self.missing_coordinates_error_message = (
			"Need coordinates for new grouped data configuration")
		
# --------------------------------------------------------------------------

	def _establish_coordinates(self) -> None:

		self._establish_coordinates_initialize_variables()
		dim_names = self._director.grouped_data_candidate.dim_names
		group_names = self._director.grouped_data_candidate.group_names
		coords_title = self._coords_title
		coords_label = self._coords_label

		matrix_dialog = MatrixDialog(
			coords_title, coords_label,
			dim_names, group_names)
		result = matrix_dialog.exec()
		# Show the dialog to get values
		if result == QDialog.Accepted:
			matrix = matrix_dialog.get_matrix()
		else:
			raise SpacesError(
				self.missing_coordinates_error_title,
				self.missing_coordinates_error_message)
		group_coords = pd.DataFrame(
			matrix, columns=dim_names,
			index=group_names)

		self._director.grouped_data_candidate.dim_names = dim_names
		self._director.grouped_data_candidate.group_names = group_names
		self._director.grouped_data_candidate.group_coords = group_coords

		return

# --------------------------------------------------------------------------

	def _create_grouped_plot_for_plot_and_gallery_tabs(self) -> None:


		fig = self._director.grouped_data_candidate.\
			plot_grouped_using_matplotlib()
		self._director.plot_to_gui(fig)
		self._director.set_focus_on_tab('Plot')
		
		return


	# ------------------------------------------------------------------------


class OpenSampleDesignCommand:

	def __init__(
			self,
			director: Status,
			common: Spaces) -> None:
		"""The Sample designer command is used to open a sample design.
		"""
		self._director = director
		self.common = common
		self._director.command = "Open sample design"
		self._open_sample_design_caption = "Open sample design"
		self._open_sample_design_filter = "*.csv"
		self._open_sample_design_frequencies_caption = \
			"Open sample design frequencies"
		self._open_sample_design_frequencies_filter = "*.txt"
		return

	# ------------------------------------------------------------------------
	def execute(self, common: Spaces) -> None: # noqa: ARG002
		try:
			# peek("At top of OpenSampleDesignCommand.execute()"
			# 	" - self._director.uncertainty_active.sample_design: "
			# 	f"{self._director.uncertainty_active.sample_design}")
			self._director.record_command_as_selected_and_in_process()
			self._director.optionally_explain_what_command_does()
			self._director.dependency_checker.detect_dependency_problems()
			file = self._director.\
				get_file_name_and_handle_nonexistent_file_names(
				self._open_sample_design_caption,
				self._open_sample_design_filter)
			self._read_sample_design_from_file(file)
			freqs_file = \
				self._director.get_file_name_and_handle_nonexistent_file_names(
					self._open_sample_design_frequencies_caption,
					self._open_sample_design_frequencies_filter)
			self._read_sample_design_frequencies_from_file(freqs_file)
			self.common.create_sample_design_analysis_table()
			self._director.title_for_table_widget = (
					f"Sample design file has "
					f"{self.\
						_director.uncertainty_active.number_of_repetitions} "
					"repetitions for "
					f"{self._director.uncertainty_active.universe_size} "
					f"evaluators.")
			self._director.create_widgets_for_output_and_log_tabs()
			self._director.set_focus_on_tab('Output')
			self._director.record_command_as_successfully_completed()
		finally:
			# Ensure window is restored and activated
			# Use a timer to defer window activation slightly
			# This gives Qt event loop time to process events
			QTimer.singleShot(100, lambda: self._restore_window())
			
		return

# ------------------------------------------------------------------------

	def _restore_window(self) -> None:
		"""Restore and activate the main window."""
		if hasattr(self._director, 'isMinimized') \
			and self._director.isMinimized():
			self._director.showNormal()
		if hasattr(self._director, 'activateWindow'):
			self._director.activateWindow()
		if hasattr(self._director, 'raise_'):
			self._director.raise_()

# ------------------------------------------------------------------------

	def _read_sample_design_initialize_variables(self) -> None:

		self.missing_sample_design_error_title = "Open sample design"
		self.missing_sample_design_error_message = (
			"Need name of sample design file to open.")

	# ------------------------------------------------------------------------

	def _read_sample_design_from_file(
			self,
			file: str) -> None:

		self._read_sample_design_initialize_variables()
		try:
			sample_design = pd.read_csv(file)
			universe_size = (int(sample_design.columns[0]))
			number_of_repetitions = (int(sample_design.columns[1]))
			probability_of_inclusion = (
				float(sample_design.columns[2]))
			sample_design.columns = ["RespId", "Repetition", "Selected"]
		except (
			FileNotFoundError, PermissionError,
			pd.errors.EmptyDataError, pd.errors.ParserError):
			raise SpacesError(
				self.missing_sample_design_error_title,
				self.missing_sample_design_error_message) from None

		self._director.uncertainty_active.sample_design = sample_design
		self._director.uncertainty_active.universe_size = universe_size
		self._director.uncertainty_active.number_of_repetitions = \
			number_of_repetitions
		self._director.uncertainty_active.probability_of_inclusion = \
			probability_of_inclusion

		return

# ------------------------------------------------------------------------

	def _read_sample_design_frequencies_initialize_variables(self) -> None:

		self.missing_sample_design_frequencies_error_title = \
			"Open sample design frequencies"
		self.missing_sample_design_frequencies_error_message = (
			"Need name of sample design frequencies file to open.")

	# ------------------------------------------------------------------------

	def _read_sample_design_frequencies_from_file(
			self,
			file: str) -> None:

		self._read_sample_design_frequencies_initialize_variables()
		try:
			self._director.uncertainty_active.sample_design_frequencies = \
				pd.read_json(file)
			self._director.uncertainty_active.sample_design.columns = \
				["RespId", "Repetition", "Selected"]
		except (
			FileNotFoundError, PermissionError,
			pd.errors.EmptyDataError, pd.errors.ParserError):
			raise SpacesError(
				self.missing_sample_design_frequencies_error_title,
				self.missing_sample_design_frequencies_error_message) from None
		return
		
	# ------------------------------------------------------------------------


class OpenSampleRepetitionsCommand:

	def __init__(
			self,
			director: Status,
			common: Spaces) -> None:
		"""The Open Sample Repetitions command is used to open a sample
		repetitons file.
		"""
		self._director = director
		self.common = common
		self._director.command = "Open sample repetitions"
		self._open_sample_repetitions_caption = "Open sample repetitions"
		self._open_sample_repetitions_filter = "*.csv"
		self._problem_reading_sample_repetitions_title: str = \
			"Problem reading sample_repetitions"
		self._problem_reading_sample_repetitions_message: str = \
			"Review file name and contents"
		return
	
	# ------------------------------------------------------------------------

	def execute(
			self,
			common: Spaces) -> None: # noqa: ARG002

		peek("At top of OpenSampleRepetitionsCommand.execute()"
			" - self._director.uncertainty_active.sample_design: \n",
			f"{self._director.uncertainty_active.sample_design}"
			f" - self._director.uncertainty_active.sample_repetitions: \n"
			f"{self._director.uncertainty_active.sample_repetitions}")
		self._director.record_command_as_selected_and_in_process()
		self._director.optionally_explain_what_command_does()
		self._director.dependency_checker.detect_dependency_problems()
		file = self._director.get_file_name_and_handle_nonexistent_file_names(
			self._open_sample_repetitions_caption,
			self._open_sample_repetitions_filter)
		self._read_sample_repetitions_from_file(file)
		# self._director.common.create_plot_for_plot_and_gallery_tabs(
		# "sample_design")
		self._director.title_for_table_widget = (
				"Sample repetitions file has "
				f"{self._director.uncertainty_active.number_of_repetitions} "
				"repetitions.")
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.set_focus_on_tab('Output')
		self._director.record_command_as_successfully_completed()
		return

	# ------------------------------------------------------------------------

	def _read_sample_repetitions_from_file(self, file_name: str) -> None:
		"""Read sample repetitions from a CSV file and verify record count.
		
		Args:
			file_name: Path to the CSV file containing sample repetitions
			
		Raises:
			ProblemReadingFileError: If there's an issue reading the file
			InconsistentInformationError: If the number of records doesn't
			match expected
		"""
		try:
			sample_repetitions = pd.read_csv(file_name, index_col=0)
			self._director.uncertainty_active.sample_repetitions = \
				sample_repetitions
			
		except (FileNotFoundError, PermissionError,
				pd.errors.EmptyDataError, pd.errors.ParserError):
			raise ProblemReadingFileError(
				self._problem_reading_sample_repetitions_title,
				self._problem_reading_sample_repetitions_message) from None
		
		return
	# ------------------------------------------------------------------------


class OpenSampleSolutionsCommand:

	def __init__(
			self,
			director: Status,
			common: Spaces) -> None:
		"""The Open Sample Solutionss command is used to open a sample
		solutions file.
		"""
		self._director = director
		self.common = common
		self._director.command = "Open sample solutions"
		self._open_sample_solutions_caption = "Open sample solutions"
		self._open_sample_solutions_filter = "*.txt"
		self._problem_reading_sample_solutions_title: str = \
			"Problem reading sample_solutions"
		self._problem_reading_sample_solutions_message: str = \
			"Review file name and contents"

		return

	# ------------------------------------------------------------------------

	def execute(
			self,
			common: Spaces) -> None:

		self._director.record_command_as_selected_and_in_process()
		self._director.optionally_explain_what_command_does()
		self._director.dependency_checker.detect_dependency_problems()
		file = self._director.get_file_name_and_handle_nonexistent_file_names(
			self._open_sample_solutions_caption,
			self._open_sample_solutions_filter)
		# Use the new Solutions format reader
		self.read_a_solutions_type_file(file)
		# self._director.common.create_plot_for_plot_and_gallery_tabs(
		# "sample_design")
		common.print_sample_solutions()

		self._director.title_for_table_widget = (
				"Sample solutions file has "
				f"{self._director.uncertainty_active.ndim} "
				"dimensions, "
				f"{self._director.uncertainty_active.npoints} "
				"points and "
				f"{self._director.uncertainty_active.nsolutions} "
				"solutions.")
		common.create_uncertainty_table()
		common.create_plot_for_plot_and_gallery_tabs("uncertainty")
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.set_focus_on_tab('Plot')
		self._director.record_command_as_successfully_completed()
		return

	# ------------------------------------------------------------------------

	def read_a_solutions_type_file(self, file_name: str) -> None:
		"""Read solutions data from a custom Solutions format file.
		
		Args:
			file_name: Path to the input file
		"""
		uncertainty_active = self._director.uncertainty_active
		
		file_path = Path(file_name)
		with file_path.open(encoding='utf-8') as f:
			# Line 1: File type identifier
			file_type = f.readline().strip()
			if file_type != "Solutions":
				error_msg = (
					f"Invalid file type: expected 'Solutions', "
					f"got '{file_type}'"
				)
				raise ValueError(error_msg)
			
			# Line 2: Basic parameters (I4 format)
			parameters_line = f.readline()
			ndim = int(parameters_line[0:4])
			npoint = int(parameters_line[4:8])
			nsolutions = int(parameters_line[8:12])
			
			# Set basic parameters
			uncertainty_active.ndim = ndim
			uncertainty_active.npoints = npoint
			uncertainty_active.nsolutions = nsolutions
			uncertainty_active.number_of_repetitions = nsolutions
			
			# Section: Description of dimensions
			dim_labels = []
			dim_names = []
			for _i in range(ndim):
				dim_line = f.readline().strip()
				parts = dim_line.split(';')
				dim_labels.append(parts[0])
				dim_names.append(parts[1])
			
			uncertainty_active.dim_labels = dim_labels
			uncertainty_active.dim_names = dim_names
			uncertainty_active.range_dims = range(ndim)
			
			# Section: Description of points
			point_labels = []
			point_names = []
			for _i in range(npoint):
				point_line = f.readline().strip()
				parts = point_line.split(';')
				point_labels.append(parts[0])
				point_names.append(parts[1])
			
			uncertainty_active.point_labels = point_labels
			uncertainty_active.point_names = point_names
			uncertainty_active.range_points = range(npoint)
			
			# Section: Read stress information for each repetition
			stress_data = []
			for i in range(nsolutions):
				stress_line = f.readline()
				repetition = int(stress_line[0:4])
				stress = float(stress_line[4:12])
				stress_data.append([repetition, stress])
			
			# Create stress DataFrame and store it
			stress_df = pd.DataFrame(
				stress_data, columns=["Repetition", "Stress"])
			uncertainty_active.repetitions_stress_df = stress_df
			
			# Section: Coordinates for all points for all solutions
			# Prepare data structure
			total_rows = npoint * nsolutions
			solutions_data = np.zeros((total_rows, ndim))
			
			# Read coordinates
			for solution_idx in range(nsolutions):
				for point_idx in range(npoint):
					coord_line = f.readline().rstrip(
						'\n\r')  # Only strip newlines, preserve leading spaces
					row_idx = solution_idx * npoint + point_idx
					
					# Parse coordinates (8.4f format)
					coords = []
					for dim_idx in range(ndim):
						start_pos = dim_idx * 8
						end_pos = start_pos + 8
						coord_str = coord_line[start_pos:end_pos].strip()
						coords.append(float(coord_str))
					
					solutions_data[row_idx] = coords
			
			# Create DataFrame with proper column names
			solutions_df = pd.DataFrame(solutions_data, columns=dim_names)
			
			# Store the solutions data
			uncertainty_active.sample_solutions = solutions_df
			uncertainty_active.repetitions_rotated = solutions_df

	# ------------------------------------------------------------------------

	def _display(self) -> QTableWidget:
		#
		gui_output_as_widget = \
			self._create_table_widget_for_open_sample_solutions()
		
		# self._director.set_column_and_row_headers(
		# 	gui_output_as_widget,
		# 	["Factor", "Size"],
		# 	[])
		#
		self._director.resize_and_set_table_size(gui_output_as_widget, 4)
		#
		# self._director.output_widget_type = "Table"
		return gui_output_as_widget

	# ------------------------------------------------------------------------
	
	def _create_table_widget_for_open_sample_solutions(self) -> QTableWidget:

		peek("At top of _create_table_widget_for_open_sample_solutions()")
		max_cols = self._director.common.max_cols
		width = self._director.common.width
		decimals = self._director.common.decimals
		#
		nrows = N_ROWS_IN_SETTINGS_LAYOUT_TABLE
		table_widget = QTableWidget(nrows, 2)
		#
		table_widget.setItem(0, 0, QTableWidgetItem(
			"Maximum number of columns per page"))
		value = QTableWidgetItem(f"{max_cols}")
		value.setTextAlignment(QtCore.Qt.AlignCenter)
		table_widget.setItem(0, 1, QTableWidgetItem(value))

		table_widget.setItem(
			1, 0,
			QTableWidgetItem("Field width"))
		value = QTableWidgetItem(f"{width}")
		value.setTextAlignment(QtCore.Qt.AlignCenter)
		table_widget.setItem(1, 1, QTableWidgetItem(value))
		#
		table_widget.setItem(
			2, 0,
			QTableWidgetItem("Decimal points"))
		value = QTableWidgetItem(f"{decimals}")
		value.setTextAlignment(QtCore.Qt.AlignCenter)
		table_widget.setItem(2, 1, QTableWidgetItem(value))

		return table_widget
	
	# ------------------------------------------------------------------------


class OpenScoresCommand:
	""" The Open scores command reads a csv file containing scores.
	"""
	def __init__(
			self,
			director: Status,
			common: Spaces) -> None:

		self._director = director
		self.common = common
		self._director.command = "Open scores"
		self._open_scores_caption = "Open scores"
		self._open_scores_filter = "*.csv"
		return

	# ------------------------------------------------------------------------

	def execute(
			self,
			common: Spaces) -> None:

		self._director.record_command_as_selected_and_in_process()
		self._director.optionally_explain_what_command_does()
		self._director.dependency_checker.detect_dependency_problems()
		file = self._director.get_file_name_and_handle_nonexistent_file_names(
			self._open_scores_caption, self._open_scores_filter)
		self._read_scores_from_file(file)
		self._director.dependency_checker.detect_consistency_issues()
		self._director.scores_active = self._director.scores_candidate
		self._director.scores_original = self._director.scores_candidate
		self._director.scores_last = self._director.scores_candidate
		self._director.rivalry.create_or_revise_rivalry_attributes(
			self._director, common)
		self._director.scores_active.summarize_scores()
		self._director.scores_active.print_scores()
		self._director.common.create_plot_for_plot_and_gallery_tabs("scores")
		self._director.title_for_table_widget = (
				f"Scores file has {self._director.scores_active.nscores} "
				"scores for "
				f"{self._director.scores_active.nscored_individ} "
				f"individuals.")
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.record_command_as_successfully_completed()

		return

# ------------------------------------------------------------------------

	def _read_scores_initialize_variables(self) -> None:

		self.missing_scores_error_title = "Open scores"
		self.missing_scores_error_message = (
			"Need name of scores file to open.")
		
	# ------------------------------------------------------------------------

	def _read_scores_from_file(
			self,
			file: str) -> None:

		self._read_scores_initialize_variables()
		scores_candidate = self._director.scores_candidate
		try:
			scores_candidate.scores = pd.read_csv(file)
			scores_candidate.nscores = scores_candidate.scores.shape[1] - 1
			scores_candidate.nscored_individ = scores_candidate.scores.shape[0]
			scores_candidate.n_individ = scores_candidate.nscored_individ
			scores_candidate.range_scores = range(scores_candidate.nscores)
			scores_candidate.dim_names.\
				append(scores_candidate.scores.columns[1])
			scores_candidate.dim_names.\
				append(scores_candidate.scores.columns[2])
			scores_candidate.dim_labels.\
				append(scores_candidate.dim_names[0][:4])
			scores_candidate.dim_labels.\
				append(scores_candidate.dim_names[1][:4])
			if scores_candidate.dim_labels[0] == \
				scores_candidate.dim_labels[1]:
				match scores_candidate.dim_labels[0]:
					case "Fact":
						scores_candidate.dim_labels[0] = "Fa01"
						scores_candidate.dim_labels[1] = "Fa02"
					case "Dime":
						scores_candidate.dim_labels[0] = "Di01"
						scores_candidate.dim_labels[1] = "Di02"
			scores_candidate.hor_axis_name = scores_candidate.scores.columns[1]
			scores_candidate.vert_axis_name = \
			scores_candidate.scores.columns[2]
			scores_candidate.score_1_name = scores_candidate.scores.columns[1]
			scores_candidate.score_2_name = scores_candidate.scores.columns[2]
			scores_candidate.score_1 = scores_candidate.scores[
				scores_candidate.hor_axis_name]
			scores_candidate.score_2 = scores_candidate.scores[
				scores_candidate.vert_axis_name]

			self._director.scores_candidate = scores_candidate

		except (
			FileNotFoundError, PermissionError,
			pd.errors.EmptyDataError, pd.errors.ParserError):
			raise SpacesError(
				self.missing_scores_error_title,
				self.missing_scores_error_message) from None
		return

	# ------------------------------------------------------------------------


class PrintConfigurationCommand:
	"""The Print configuration command is used to print a copy of the active
		configuration.
	"""
	def __init__(
			self,
			director: Status,
			common: Spaces) -> None:

		self._director = director
		self.common = common
		self._director.command = "Print configuration"
		self._director.title_for_table_widget = "Active configuration."
		return

	# ------------------------------------------------------------------------

	def execute(
			self,
			common: Spaces) -> None: # noqa: ARG002

		self._director.record_command_as_selected_and_in_process()
		self._director.optionally_explain_what_command_does()
		self._director.dependency_checker.detect_dependency_problems()
		self._director.configuration_active.print_the_configuration()
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.set_focus_on_tab('Output')
		self._director.record_command_as_successfully_completed()
		return

	# ------------------------------------------------------------------------


class PrintCorrelationsCommand:
	"""The Print correlations command is used to print correlations.
	"""
	def __init__(
			self,
			director: Status,
			common: Spaces) -> None:

		self._director = director
		self.common = common
		self._director.command = "Print correlations"

		return

	# ------------------------------------------------------------------------

	def execute(
			self,
			common: Spaces) -> None:

		self._director.record_command_as_selected_and_in_process()
		self._director.optionally_explain_what_command_does()
		self._director.dependency_checker.detect_dependency_problems()
		self._director.correlations_active.print_the_correlations(
			self._director.width, self._director.decimals, common)
		self._director.title_for_table_widget = (
			"Correlation matrix has "
			f"{self._director.correlations_active.nreferent} items")
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.set_focus_on_tab('Output')
		self._director.record_command_as_successfully_completed()
		return

	# ------------------------------------------------------------------------


class PrintEvaluationsCommand:

	def __init__(
			self,
			director: Status,
			common: Spaces) -> None:
		"""The Print evaluations command is used to print evaluations.
		"""
		self._director = director
		self.common = common
		self._director.command = "Print evaluations"

		return

	# ------------------------------------------------------------------------

	def execute(
			self,
			common: Spaces) -> None: # noqa: ARG002

		self._director.record_command_as_selected_and_in_process()
		self._director.optionally_explain_what_command_does()
		self._director.dependency_checker.detect_dependency_problems()
		self._director.evaluations_active.print_the_evaluations()
		self._director.title_for_table_widget = "Evaluations"
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.set_focus_on_tab('Output')
		self._director.record_command_as_successfully_completed()
		return

	# ------------------------------------------------------------------------


class PrintGroupedDataCommand:
	"""The Print grouped data command is used to print grouped data.
	"""
	def __init__(
			self,
			director: Status,
			common: Spaces) -> None:

		self._director = director
		self.common = common
		self._director.command = "Print grouped data"
		return

	# ------------------------------------------------------------------------

	def execute(
			self,
			common: Spaces) -> None: # noqa: ARG002

		self._director.record_command_as_selected_and_in_process()
		self._director.optionally_explain_what_command_does()
		self._director.dependency_checker.detect_dependency_problems()
		self._director.grouped_data_active.print_grouped_function()
		self._director.title_for_table_widget = (
			f"Configuration is based on "
			f"{self._director.grouped_data_candidate.grouping_var}"
			f" and has {self._director.grouped_data_candidate.ndim}"
			f" dimensions and "
			f"{self._director.grouped_data_candidate.ngroups} points")
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.set_focus_on_tab('Output')
		self._director.record_command_as_successfully_completed()
		return


# --------------------------------------------------------------------------


class PrintIndividualsCommand:

	def __init__(
			self,
			director: Status,
			common: Spaces) -> None:
		"""The Print individuals command is used to print individuals.
		"""
		self._director = director
		self.common = common
		self._director.command = "Print individuals"

		return

	# ------------------------------------------------------------------------

	def execute(
			self,
			common: Spaces) -> None: # noqa: ARG002

		self._director.record_command_as_selected_and_in_process()
		self._director.optionally_explain_what_command_does()
		self._director.dependency_checker.detect_dependency_problems()
		self._director.individuals_active.print_individuals()
		self._director.title_for_table_widget = "Individuals"
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.set_focus_on_tab('Output')
		self._director.record_command_as_successfully_completed()
		return

	# ------------------------------------------------------------------------


class PrintSampleDesignCommand:

	def __init__(
			self,
			director: Status,
			common: Spaces) -> None:
		"""The Print Sample command is used to print a sample design.
		"""
		self._director = director
		self.common = common
		self._director.command = "Print sample design"
		return

# --------------------------------------------------------------------------

	def execute(
			self,
			common: Spaces) -> None:  # noqa: ARG002

		self._director.record_command_as_selected_and_in_process()
		self._director.optionally_explain_what_command_does()
		self._director.dependency_checker.detect_dependency_problems()
		self._print_sample_design()
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.set_focus_on_tab('Output')
		self._director.record_command_as_successfully_completed()
		return

	# ------------------------------------------------------------------------

	def _print_sample_design(self) -> None:

		""" print sample design function - is used to print the
		sample design.
		"""
		print(self._director.uncertainty_active.sample_design)
		return

# --------------------------------------------------------------------------


class PrintSampleRepetitionsCommand:

	def __init__(
			self,
			director: Status,
			common: Spaces) -> None:
		"""The Print Sample Repetitions command is used to print a sample
		repetitons file.
		"""
		self._director = director
		self.common = common
		self._director.command = "Print sample repetitions"
		self._print_sample_repetitions_caption = "Print sample repetitions"
		self._print_sample_repetitions_filter = "*.csv"
		self._problem_reading_sample_repetitions_title: str = \
			"Problem reading sample_repetitions"
		self._problem_reading_sample_repetitions_message: str = \
			"Review file name and contents"

		return

# --------------------------------------------------------------------------


class PrintSampleSolutionsCommand:

	def __init__(
			self,
			director: Status,
			common: Spaces) -> None:
		"""The Print Sample Solutions command is used to print a sample
		repetitons file.
		"""
		
		self._director = director
		self.common = common
		self._director.command = "Print sample solutions"
		self._print_sample_solutions_caption = "Print sample solutions"
		self._print_sample_solutions_filter = "*.csv"
		self._problem_reading_sample_solutions_title: str = \
			"Problem reading sample_solutions"
		self._problem_reading_sample_solutions_message: str = \
			"Review file name and contents"

		return
	
	# ------------------------------------------------------------------------


class PrintScoresCommand:
	"""The Print scores command is used to print scores.
	"""
	def __init__(
			self,
			director: Status,
			common: Spaces) -> None:

		self._director = director
		self.common = common
		self._director.command = "Print scores"
		self._director.title_for_table_widget = "Summary of scores"
		return

	# ------------------------------------------------------------------------

	def execute(
			self,
			common: Spaces) -> None: # noqa: ARG002

		peek("At top of PrintSampleRepetitionsCommand.execute()"
			" - self._director.uncertainty_active.sample_design: ",
			f"{self._director.uncertainty_active.sample_design}")
		self._director.record_command_as_selected_and_in_process()
		self._director.optionally_explain_what_command_does()
		self._director.dependency_checker.detect_dependency_problems()
		self._director.scores_active.print_scores()
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.set_focus_on_tab('Output')
		self._director.record_command_as_successfully_completed()

		return

	# ------------------------------------------------------------------------


class PrintSimilaritiesCommand:

	def __init__(
			self,
			director: Status,
			common: Spaces) -> None:
		"""The Print similarities command is used to print similarities.
		"""
		self._director = director
		self.common = common
		self._director.command = "Print similarities"
		self._director.title_for_table_widget = "Similarities"
		self._width = 8
		self._decimals = 2
		return

	# ------------------------------------------------------------------------

	def execute(
			self,
			common: Spaces) -> None:

		self._director.record_command_as_selected_and_in_process()
		self._director.optionally_explain_what_command_does()
		self._director.dependency_checker.detect_dependency_problems()
		self._director.similarities_active.print_the_similarities(
			self._width, self._decimals, common)
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.set_focus_on_tab('Output')
		self._director.record_command_as_successfully_completed()
		return

	# ------------------------------------------------------------------------


class PrintTargetCommand:
	"""The Print target command is used to print target .
	"""
	def __init__(
			self,
			director: Status,
			common: Spaces) -> None:

		self._director = director
		self.common = common
		self._director.command = "Print target"
		self._director.title_for_table_widget = "Target configuration"
		return

	# ------------------------------------------------------------------------

	def execute(
			self,
			common: Spaces) -> None: # noqa: ARG002

		self._director.record_command_as_selected_and_in_process()
		self._director.optionally_explain_what_command_does()
		self._director.dependency_checker.detect_dependency_problems()
		self._director.target_active.print_target()
		self._director.title_for_table_widget = (
			f"Target configuration has {self._director.target_active.ndim}"
			f" dimensions and {self._director.target_active.npoint} points")
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.set_focus_on_tab('Output')
		self._director.record_command_as_successfully_completed()
		return

	# ------------------------------------------------------------------------


class SaveConfigurationCommand:
	"""The Save configuration command is used to write a copy of the active
		configuration to a file.
	"""
	def __init__(
			self,
			director: Status,
			common: Spaces) -> None: # noqa: ARG002

		# _message and _feedback changed to _title and _message

		self._director = director
		self._director.command = "Save configuration"
		self._save_conf_caption = "Save active configuration"
		self._save_conf_filter = "*.txt"
		self._director.name_of_file_written_to = ""

		return

	# ------------------------------------------------------------------------

	def execute(
			self,
			common: Spaces) -> None: # noqa: ARG002

		# _message and _feedback changed to _title and _message

		self._director.record_command_as_selected_and_in_process()
		self._director.optionally_explain_what_command_does()
		self._director.dependency_checker.detect_dependency_problems()
		file_name = self._director.get_file_name_to_store_file(
			self._save_conf_caption, self._save_conf_filter)
		self._director.configuration_active.write_a_configuration_type_file(
			file_name, self._director.configuration_active)
		self._director.name_of_file_written_to = file_name
		self._print_active_configuration_confirmation(file_name)
		name_of_file_written_to = self._director.name_of_file_written_to
		self._director.title_for_table_widget = (
			f"The active configuration has been written to: "
			f"\n {name_of_file_written_to}\n")
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.set_focus_on_tab('Output')
		self._director.record_command_as_successfully_completed()
		return

	# ------------------------------------------------------------------------

	def _print_active_configuration_confirmation(
			self,
			file_name: str) -> None:

		print("\n\tThe active configuration has been written to: ", file_name)
		return

	# ------------------------------------------------------------------------


class SaveCorrelationsCommand:
	"""The Save correlations command is used to write a copy of the active
	configuration to a file.
	"""
	def __init__(
			self,
			director: Status,
			common: Spaces) -> None:

		# _message and _feedback changed to _title and _message

		self._director = director
		self.common = common
		self._director.command = "Save correlations"
		self._save_corr_caption = "Save active correlations"
		self._save_corr_filter = "*.txt"
		self._save_corr_title = "The response is empty."
		self._save_corr_message = (
			"A file name is needed to save the active correlations.")
		# self._saving_corr_message = "Check whether file already exists"
		self._width = 8
		self._decimals = 4
		self._director.name_of_file_written_to = ""
		self.item_labels = self._director.correlations_active.item_labels
		self.item_names = self._director.correlations_active.item_names
		return

		# --------------------------------------------------------------------

	def execute(
			self,
			common: Spaces) -> None:

		
		# dropped arguments_message and _feedback

		self._director.record_command_as_selected_and_in_process()
		self._director.optionally_explain_what_command_does()
		self._director.dependency_checker.detect_dependency_problems()
		file_name = self._director.get_file_name_to_store_file(
			self._save_corr_caption, self._save_corr_filter)
		common.write_lower_triangle(
			file_name, self._director.correlations_active.correlations_as_list,
			self._director.correlations_active.nreferent,
			self._director.correlations_active.item_labels,
			self._director.correlations_active.item_names,
			self._width, self._decimals)
			# self._saving_corr_title, self._saving_corr_message)
		self._director.name_of_file_written_to = file_name
		self._print_save_correlations_confirmation(file_name)
		self._director.correlations_active.print_the_correlations(
			self._width, self._decimals, common)
		nreferent = self._director.correlations_active.nreferent
		self._director.title_for_table_widget = (
			"The active correlations have been written to: "
			f"\n {file_name}\n\n"
			f"The correlation matrix has {nreferent} items")
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.set_focus_on_tab('Output')
		self._director.record_command_as_successfully_completed()
		return

	# ------------------------------------------------------------------------

	def _print_save_correlations_confirmation(
			self,
			file_name: str) -> None:

		print("\n\tThe active correlations has been written to: ", file_name)
		return

	# ------------------------------------------------------------------------


class SaveIndividualsCommand:
	"""The Save individuals command is used to write a copy of the active
	individuals to a file.
	"""
	def __init__(
			self,
			director: Status,
			common: Spaces) -> None:

		# _message and _feedback changed to _title and _message

		self._director = director
		self.common = common
		self._director.command = "Save individuals"
		self._save_individ_title = "The response is empty."
		self._save_individ_message = \
			"A file name is needed to save individuals."
		self._save_individ_filter = "*.csv"
		self._director.name_of_file_written_to = ""
		return

		# --------------------------------------------------------------------

	def execute(
			self,
			common: Spaces) -> None: # noqa: ARG002

		# _message and _feedback changed to _title and _message

		self._director.record_command_as_selected_and_in_process()
		self._director.optionally_explain_what_command_does()
		self._director.dependency_checker.detect_dependency_problems()
		file_name = self._director.get_file_name_to_store_file(
			self._save_individ_title, self._save_individ_message,
			self._save_individ_filter)
		self._director.individuals_active.ind_vars.to_csv(
			file_name,
			columns=self._director.individuals_active.var_names)
		self._director.name_of_file_written_to = file_name
		self._print_individuals_confirmation(file_name)
		name_of_file_written_to = self._director.name_of_file_written_to
		self._director.individuals_active.print_individuals()
		self._director.title_for_table_widget = (
			f"The active individuals have been written to:"
			f"\n {name_of_file_written_to}")
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.set_focus_on_tab('Output')
		self._director.record_command_as_successfully_completed()
		return

	# ------------------------------------------------------------------------

	def _print_individuals_confirmation(
			self,
			file_name: str) -> None:

		print("\nThe active individuals have been written to: ", file_name)
		return

	# ----------------------------------------------------------------------


class SaveSampleDesignCommand:

	"""The Save sample design command is used to write a copy of the active
		sample design to a file.
	"""
	def __init__(
			self,
			director: Status,
			common: Spaces) -> None: # noqa: ARG002

		# _message and _feedback changed to _title and _message
		self._director = director
		self._director.command = "Save sample design"
		self._saving_sample_design_caption = "Save sample design"
		self._saving_sample_design_filter = "*.csv"
	
		self._director.name_of_file_written_to = ""
		self._saving_sample_design_frequencies_caption = \
			"Save sample design frequencies"
		self._saving_sample_design_frequencies_filter = "*.txt"


		return

	# ------------------------------------------------------------------------

	def execute(
			self,
			common: Spaces) -> None: # noqa: ARG002

		# _message and _feedback changed to _title and _message

		self._director.record_command_as_selected_and_in_process()
		self._director.optionally_explain_what_command_does()
		self._director.dependency_checker.detect_dependency_problems()
		file_name = self._director.get_file_name_to_store_file(
			self._saving_sample_design_caption,
			self._saving_sample_design_filter)
		self._write_sample_design_type_file(
			file_name, self._director.uncertainty_active.sample_design)
		
		self._director.name_of_file_sample_design_written_to = file_name
		freqs_file_name = self._director.get_file_name_to_store_file(
			self._saving_sample_design_frequencies_caption,
			self._saving_sample_design_frequencies_filter)
		self._director.name_of_file_sample_design_frequencies_written_to = \
			freqs_file_name
		self._write_sample_design_frequencies_type_file(freqs_file_name)
		name_of_file_sample_design_written_to = (
			self._director.name_of_file_sample_design_written_to)
		name_of_file_sample_design_frequencies_written_to = (
			self._director.name_of_file_sample_design_frequencies_written_to)
		self._director.title_for_table_widget = (
			f"The active sample design has been written to: "
			f"\n {name_of_file_sample_design_written_to}"
			f"\nThe sample design frequencies have been written to: "
			f"\n {name_of_file_sample_design_frequencies_written_to}")
		print(self._director.uncertainty_active.sample_design)
		print(self._director.uncertainty_active.sample_design_frequencies)
		self._director.name_of_file_written_to = freqs_file_name
		# self._print_sample_design_confirmation(file_name)
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.set_focus_on_tab('Output')
		self._director.record_command_as_successfully_completed()
		return

# ------------------------------------------------------------------------

	def _write_sample_design_type_file_initialize_variables(self) -> None:

		self._saving_sample_design_problem_title = "Problem writing file."
		self._saving_sample_design_problem_message = \
			"Check whether file already exists"
		return

# --------------------------------------------------------------------------

	def _write_sample_design_type_file(
			self,
			file_name: str,
			sample_design: pd.DataFrame) -> None:

		# positional arguments title and message were dropped

		self._write_sample_design_type_file_initialize_variables()
		universe_size = self._director.uncertainty_active.universe_size
		number_of_repetitions = \
			self._director.uncertainty_active.number_of_repetitions
		probability_of_inclusion = self._director.uncertainty_active.\
			probability_of_inclusion

		# file_type: str = "Sample design"
		try:
			with Path(file_name).open('w') as file_handle:
				# file_handle.write(file_type + "\n")
				file_handle.write(
					str(universe_size) + ","
					+ str(number_of_repetitions) + ","
					+ str(probability_of_inclusion) + "\n")
				next_record = 0
				for each_repetition in range(1, number_of_repetitions + 1):
					for each_case in range(1, universe_size + 1):
						file_handle.write(
							f"{each_repetition},"
							f"{each_case},"
							f"{sample_design.iloc[next_record]['Selected']}"
							f"\n")
						next_record += 1
						continue
					continue
		except FileExistsError:
			raise SpacesError(
				self._saving_sample_design_problem_title,
				self._saving_sample_design_problem_message) from None

		return

	# ------------------------------------------------------------------------

	def _write_sample_design_frequencies_type_file_initialize_variables(
			self) -> None:
		self._saving_sample_design_frequencies_problem_title = \
			"Problem writing file."
		self._saving_sample_design_frequencies_problem_message = \
			"Check whether file already exists"
		
# --------------------------------------------------------------------------

	def _write_sample_design_frequencies_type_file(
			self,
			file_name: str) -> None:

		# positional arguments title and message have been dropped
		# file_type: str = "Sample design frequencies"
		self._write_sample_design_type_file_initialize_variables()
		try:
			with Path(file_name).open('w') as file_handle:
				file_handle.write(
					self._director.uncertainty_active.\
						sample_design_frequencies_as_json)
		except FileExistsError:
			raise SpacesError(
				self._saving_sample_design_frequencies_problem_title,
				self._saving_sample_design_frequencies_problem_message) \
					from None
		
		return

# --------------------------------------------------------------------------


class SaveSampleRepetitionsCommand:

	"""The Save sample repetitions command is used to write a copy of the
		active sample repetitions to a file.
	"""
	def __init__(
			self,
			director: Status,
			common: Spaces) -> None: # noqa: ARG002

		# _message and _feedback changed to _title and _message

		self._director = director
		self._director.command = "Save sample repetitions"
		self._save_sample_repetitions_caption = "Save sample repetitions"
		# self._save_sample_repetitions_message = \
		# 	"A file name is needed to save the active sample repetitions."
		self._save_sample_repetitions_filter = "*.csv"
		self._save_sample_repetitions_problem_title = "Problem writing file."
		self._save_sample_repetitions_problem_message = \
			"Check whether file already exists"
		self._director.name_of_file_written_to = ""
		return

	# ------------------------------------------------------------------------

	def execute(
			self,
			common: Spaces) -> None: # noqa: ARG002

		# _message and _feedback changed to _title and _message

		peek("At top of SaveSampleRepetitionsCommand.execute()"
			" - self._director.uncertainty_active.sample_design: ",
			f"{self._director.uncertainty_active.sample_design}")
		self._director.record_command_as_selected_and_in_process()
		self._director.optionally_explain_what_command_does()
		self._director.dependency_checker.detect_dependency_problems()
		file_name = self._director.get_file_name_to_store_file(
			self._save_sample_repetitions_caption,
			self._save_sample_repetitions_filter)
		self._director.uncertainty_active.sample_repetitions.to_csv(file_name)
		self._director.name_of_file_written_to = file_name
		self._director.title_for_table_widget = (
			f"The active sample repetitions has been written to: "
			f"\n {file_name}")
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.set_focus_on_tab('Output')
		self._director.record_command_as_successfully_completed()
		return

# --------------------------------------------------------------------------


class SaveSampleSolutionsCommand:

	"""The Save sample solutions command is used to write a copy of the active
		sample solutions to a file.
	"""
	def __init__(
			self,
			director: Status,
			common: Spaces) -> None: # noqa: ARG002

		# _message and _feedback changed to _title and _message

		self._director = director
		self._director.command = "Save sample solutions"
		self._save_sample_solutions_title = "The response is empty."
		self._save_sample_solutions_message = \
			"A file name is needed to save the active sample solutions."
		self._save_sample_solutions_caption = "Save sample solutions"
		self._save_sample_solutions_filter = "*.txt"
		self._save_sample_solutions_problem_title = "Problem writing file."
		self._save_sample_solutions_problem_message = \
			"Check whether file already exists"
		self._director.name_of_file_written_to = ""
		return

	# ------------------------------------------------------------------------

	def execute(
			self,
			common: Spaces) -> None: # noqa: ARG002

		# _message and _feedback changed to _title and _message
		peek("At top of SaveSampleSolutionsCommand.execute()"
			" - self._director.uncertainty_active: ",
			f"{self._director.uncertainty_active}",
			"ndim: ",
			f"{self._director.uncertainty_active.ndim}",
			"npoints: ",
			f"{self._director.uncertainty_active.npoints}",
			"nrepetitions: ",
			f"{self._director.uncertainty_active.number_of_repetitions}",
			"dim_labels:"
			f" {self._director.uncertainty_active.dim_labels}"
			"dim_names: "
			f"{self._director.uncertainty_active.dim_names}",
			"point_names: "
			f"{self._director.uncertainty_active.point_names}",
			"point_labels: "
			f"{self._director.uncertainty_active.point_labels}")
		self._director.record_command_as_selected_and_in_process()
		self._director.optionally_explain_what_command_does()
		self._director.dependency_checker.detect_dependency_problems()
		file_name = self._director.get_file_name_to_store_file(
			self._save_sample_solutions_caption,
			self._save_sample_solutions_filter)
		# Use the new Solutions format writer
		self.write_a_solutions_type_file(file_name)
		self._director.name_of_file_written_to = file_name
		self._director.title_for_table_widget = (
			f"The active sample solutions has been written to: "
			f"\n {file_name}")
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.set_focus_on_tab('Output')
		self._director.record_command_as_successfully_completed()
		return

	# ------------------------------------------------------------------------

	def write_a_solutions_type_file(self, file_name: str) -> None:
		"""Write solutions data to a custom Solutions format file.
		
		Args:
			file_name: Path to the output file
		"""
		
		uncertainty_active = self._director.uncertainty_active
		
		# Get basic dimensions
		ndim = uncertainty_active.ndim
		npoint = uncertainty_active.npoints
		nsolutions = uncertainty_active.number_of_repetitions
		
		# Get solutions data (repetitions_rotated DataFrame)
		solutions_df = uncertainty_active.sample_solutions
		
		file_path = Path(file_name)
		print(f"DEBUG write_a_solutions_type_file: Path object: '{file_path}'")
		with file_path.open('w', encoding='utf-8') as f:
			# Line 1: File type identifier
			f.write("Solutions\n")
			
			# Line 2: Basic dimensions (I4 format)
			f.write(f"{ndim:4d}{npoint:4d}{nsolutions:4d}\n")
			
			# Section: Description of dimensions
			for i in range(ndim):
				dim_label = uncertainty_active.dim_labels[i]
				dim_name = uncertainty_active.dim_names[i]
				f.write(f"{dim_label};{dim_name}\n")
			
			# Section: Description of points
			for i in range(npoint):
				point_label = uncertainty_active.point_labels[i]
				point_name = uncertainty_active.point_names[i]
				f.write(f"{point_label};{point_name}\n")
			
			# Section: Stress information for each repetition
			if hasattr(uncertainty_active, 'repetitions_stress_df'):
				stress_df = uncertainty_active.repetitions_stress_df
			else:
				# Create DataFrame from sample_repetitions_stress list
				stress_data = []
				for i, stress in enumerate(
					uncertainty_active.sample_repetitions_stress):
					stress_data.append(
						[i + 1, stress])  # Repetition starts from 1
				stress_df = pd.DataFrame(
					stress_data, columns=["Repetition", "Stress"])
			for i in range(nsolutions):
				repetition = stress_df.iloc[i, 0]  # Repetition number
				stress = stress_df.iloc[i, 1]      # Stress value
				f.write(f"{repetition:4d}{stress:8.4f}\n")
			
			# Section: Coordinates for all points for all solutions
			# solutions_df has columns for dimension, rows for points*solutions
			for solution_idx in range(nsolutions):
				for point_idx in range(npoint):
					# Calculate the row index in the DataFrame
					row_idx = solution_idx * npoint + point_idx
					
					# Write coordinates for this point (8.4f format)
					coords = []
					for dim_idx in range(ndim):
						coord_value = solutions_df.iloc[row_idx, dim_idx]
						coords.append(f"{coord_value:8.4f}")
					f.write("".join(coords) + "\n")

# --------------------------------------------------------------------------


class SaveScoresCommand:
	"""The Save scores command is used to write a copy of the active
	scores to a file.
	"""
	def __init__(
			self,
			director: Status,
			common: Spaces) -> None:

		# _message and _feedback changed to _title and _message

		self._director = director
		self.common = common
		self._director.command = "Save scores"
		self._save_scores_title = "The response is empty."
		self._save_scores_message = "A file name is needed to save scores."
		self._save_scores_filter = "*.csv"
		self._director.name_of_file_written_to = ""
		return

# --------------------------------------------------------------------------

	def execute(
			self,
			common: Spaces) -> None: # noqa: ARG002

		# _message and _feedback changed to _title and _message

		score_1_name = self._director.scores_active.score_1_name
		score_2_name = self._director.scores_active.score_2_name

		self._director.record_command_as_selected_and_in_process()
		self._director.optionally_explain_what_command_does()
		self._director.dependency_checker.detect_dependency_problems()
		file_name = self._director.get_file_name_to_store_file(
			self._save_scores_title,
			self._save_scores_filter)
		self._director.scores_active.scores.to_csv(
			file_name, columns=[score_1_name, score_2_name])
		self._director.name_of_file_written_to = file_name
		self._print_save_scores_confirmation(file_name)
		self._director.title_for_table_widget = (
			f"The active scores have been written to:"
			f"\n {file_name}")
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.set_focus_on_tab('Output')
		self._director.record_command_as_successfully_completed()
		return

	# ------------------------------------------------------------------------

	def _print_save_scores_confirmation(
			self,
			file_name: str) -> None:

		print("\nThe active scores have been written to: ", file_name)
		return

	# ----------------------------------------------------------------------


class SaveSimilaritiesCommand:

	def __init__(
			self,
			director: Status,
			common: Spaces) -> None:
		"""The Save similarities command is used to write a copy of the active
		similarities to a file.
		"""

		# _message and _feedback changed to _title and _message

		self._director = director
		self.common = common
		self._director.command = "Save similarities"
		self._save_simi_caption = "Save active similarities"
		self._save_simi_filter = "*.txt"
		self._save_simi_title = "The response is empty."
		self._save_simi_message = \
			"A file name is needed to save the active similarities."

		self._width = 8
		self._decimals = 2
		self._director.name_of_file_written_to = ""
		return

		# --------------------------------------------------------------------

	def execute(
			self,
			common: Spaces) -> None:

		# _message and _feedback changed to _title and _message

		similarities_as_list = \
			self._director.similarities_active.similarities_as_list
		save_simi_caption = self._save_simi_caption
		save_simi_filter = self._save_simi_filter
		nreferent = self._director.similarities_active.nreferent
		width = self._width
		decimals = self._decimals
		item_labels = self._director.similarities_active.item_labels
		item_names = self._director.similarities_active.item_names

		self._director.record_command_as_selected_and_in_process()
		self._director.optionally_explain_what_command_does()
		self._director.dependency_checker.detect_dependency_problems()
		file_name = self._director.get_file_name_to_store_file(
			save_simi_caption, save_simi_filter)
		common.write_lower_triangle(
			file_name, similarities_as_list,  nreferent,
			item_labels, item_names, width, decimals)
		self._director.name_of_file_written_to = file_name
		self._print_save_similarities_confirmation(file_name)
		self._director.similarities_active.print_the_similarities(
			width, decimals, common)
		nreferent = self._director.similarities_active.nreferent
		self._director.title_for_table_widget = (
			"The active similarities have been written to: "
			f"\n {file_name}\n\n"
			f"The similarities matrix has {nreferent} items")
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.set_focus_on_tab('Output')
		self._director.record_command_as_successfully_completed()
		return

	# ------------------------------------------------------------------------

	def _print_save_similarities_confirmation(
			self,
			file_name: str) -> None:

		print("\n\tThe active similarities has been written to: ", file_name)
		return

	# ------------------------------------------------------------------------


class SaveTargetCommand:
	"""The Save target command is used to write a copy of the target
		configuration to a file.
	"""
	def __init__(
			self,
			director: Status,
			common: Spaces) -> None:

		# _message and _feedback changed to _title and _message

		self._director = director
		self.common = common
		self._director.command = "Save target"
		self._save_target_caption = "Save target configuration"
		self._save_target_filter = "*.txt"
		self._save_target_title = "The response is empty."
		self._save_target_message = ("A file name is needed to save "
			"the target configuration.")

		self._director.name_of_file_written_to = ""
		return

	# ------------------------------------------------------------------------

	def execute(
			self, common: Spaces) -> None: # noqa: ARG002

		# dropped _message and _feedback positional arguments

		self._director.record_command_as_selected_and_in_process()
		self._director.optionally_explain_what_command_does()
		self._director.dependency_checker.detect_dependency_problems()
		file_name = self._director.get_file_name_to_store_file(
			self._save_target_caption, self._save_target_filter)
		self._director.configuration_active.write_a_configuration_type_file(
			file_name,
			self._director.target_active)
		self._director.name_of_file_written_to = file_name
		self._print_save_target_confirmation(file_name)
		self._director.target_active.print_target()
		self._director.name_of_file_written_to = file_name
		self._director.title_for_table_widget = (
			f"The active target has been written to: "
			f"\n {file_name}\n")
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.set_focus_on_tab('Output')
		self._director.record_command_as_successfully_completed()
		return

	# ------------------------------------------------------------------------

	def _print_save_target_confirmation(
			self,
			file_name: str) -> None:

		print("\n\tThe target configuration has been written to: ", file_name)
		return


# --------------------------------------------------------------------------


class SettingsDisplayCommand:
	""" The Settings display command is used to set various parameters used
	in the program.
	"""
	def __init__(
			self,
			director: Status,
			common: Spaces) -> None:

		self._director = director
		self.common = common
		self._director.command = "Settings - display sizing"

		self._display_title = "Display adjustments"
		self._display_items = [
			"Extend axis by adding percent of axis maxima "
			"\nto keep points from falling on the edge of plots",
			"Improve visibility by displacing labelling off "
			"\n point by percent of axis maxima                        ",
			"Size in points of the dots representing people "
			"\n in plots                                               "]
		self._display_default_values = [
			int(self._director.common.axis_extra * 100),
			int(self._director.common.displacement * 100),
			self._director.common.point_size]
		self._display_integers = True

	# ------------------------------------------------------------------------

	def execute(
			self,
			common: Spaces) -> None: # noqa: ARG002

		self._director.record_command_as_selected_and_in_process()
		self._director.optionally_explain_what_command_does()
		self._get_display_sizings_from_user(
			self._display_title, self._display_items,
			self._display_integers, self._display_default_values)
		self._director.common.print_display_settings()
		self._director.title_for_table_widget = "Display settings"
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.set_focus_on_tab('Output')
		self._director.record_command_as_successfully_completed()
		return

	# ------------------------------------------------------------------------

	def _get_display_sizings_from_user(
			self,
			title: str,
			items: list[str],
			integers: bool, # noqa: FBT001
			default_values: list[int]) -> None:

		dialog = ModifyValuesDialog(
			title, items, integers, default_values=default_values)
		dialog.selected_items()
		result = dialog.exec()
		if result == QDialog.Accepted:
			value = dialog.selected_items()
			axis_extra = value[0][1] / 100.0
			displacement = value[1][1] / 100.0
			point_size = value[2][1]
		else:
			axis_extra = self._director.common.axis_extra
			displacement = self._director.common.displacement
			point_size = self._director.common.point_size

		self._director.common.axis_extra = axis_extra
		self._director.common.displacement = displacement
		self._director.common.point_size = point_size
		return

	# ------------------------------------------------------------------------

	def _display(self) -> QTableWidget:

		gui_output_as_widget = \
			self._create_table_widget_for_settings_display()

		self._director.set_column_and_row_headers(
			gui_output_as_widget,
			["Factor", "Size"],
			[])
		#
		self._director.resize_and_set_table_size(gui_output_as_widget, 4)
		#
		self._director.output_widget_type = "Table"
		return gui_output_as_widget

	# ------------------------------------------------------------------------

	def _create_table_widget_for_settings_display(self) -> QTableWidget:

		axis_extra = self._director.common.axis_extra
		displacement = self._director.common.displacement
		point_size = self._director.common.point_size
		#
		nrows = N_ROWS_IN_SETTINGS_DISPLAY_TABLE
		#
		table_widget = QTableWidget(nrows, 2)
		#
		table_widget.setItem(
			0, 0,
			QTableWidgetItem(
				"Extend axis by adding percent of axis maxima "
				"\nto keep points from falling on the edge of plots"))
		value = QTableWidgetItem(f"{axis_extra * 100: 3.0f}")
		value.setTextAlignment(QtCore.Qt.AlignCenter)
		table_widget.setItem(0, 1, QTableWidgetItem(value))
		#
		table_widget.setItem(1, 0, QTableWidgetItem(
			"Improve visibility by displacing labelling off"
			"\n point by percent of axis maxima"))
		value = QTableWidgetItem(f"{displacement * 100: 3.0f}")
		value.setTextAlignment(QtCore.Qt.AlignCenter)
		table_widget.setItem(1, 1, QTableWidgetItem(value))
		#
		table_widget.setItem(2, 0, QTableWidgetItem(
			"Size in points of the dots representing people\n in plots"))
		value = QTableWidgetItem(f"{point_size: 3.0f}")
		value.setTextAlignment(QtCore.Qt.AlignCenter)
		table_widget.setItem(2, 1, QTableWidgetItem(value))
		return table_widget

# --------------------------------------------------------------------------


class SettingsLayoutCommand:
	""" The Settings layout command is used to set various parameters used
	in the program.
	"""
	def __init__(
			self,
			director: Status,
			common: Spaces) -> None:

		self._director = director
		self.common = common
		self._director.command = "Settings - layout options"
		self._layout_title = "Layout options"
		self._layout_items = [
			"Maximum number of columns per page",
			"Field width",
			"Decimal points                                               "]
		self._layout_default_values = [
			self._director.common.max_cols,
			self._director.common.width,
			self._director.common.decimals]
		self._layout_integers = True

		return

	# ------------------------------------------------------------------------

	def execute(
			self,
			common: Spaces) -> None: # noqa: ARG002

		self._director.record_command_as_selected_and_in_process()
		self._director.optionally_explain_what_command_does()
		self._get_layout_settings_from_user(
			self._layout_title, self._layout_items,
			self._layout_integers, self._layout_default_values)
		self._director.command = "Settings - layout options"
		self._director.common.print_layout_options_settings()
		self._director.title_for_table_widget = "Layout options"
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.set_focus_on_tab('Output')
		self._director.record_command_as_successfully_completed()
		return

	# ------------------------------------------------------------------------

	def _get_layout_settings_from_user(
			self,
			title: str,
			items: list[str],
			integers: bool, # noqa: FBT001
			default_values: list[str]) -> None:

		dialog = ModifyValuesDialog(
			title, items, integers, default_values=default_values)
		dialog.selected_items()
		result = dialog.exec()
		if result == QDialog.Accepted:
			value = dialog.selected_items()
			max_cols = value[0][1]
			width = value[1][1]
			decimals = value[2][1]
		else:
			max_cols = self._director.common.max_cols
			width = self._director.common.width
			decimals = self._director.common.decimals

		self._director.common.max_cols = max_cols
		self._director.common.width = width
		self._director.common.decimals = decimals

		return

	# ------------------------------------------------------------------------

	def _display(self) -> QTableWidget:
		#
		gui_output_as_widget = self._create_table_widget_for_settings_layout()
		#
		self._director.set_column_and_row_headers(
			gui_output_as_widget,
			["Factor", "Size"],
			[])
		#
		self._director.resize_and_set_table_size(gui_output_as_widget, 4)
		#
		self._director.output_widget_type = "Table"
		return gui_output_as_widget

	# ------------------------------------------------------------------------
	
	def _create_table_widget_for_settings_layout(self) -> QTableWidget:

		max_cols = self._director.common.max_cols
		width = self._director.common.width
		decimals = self._director.common.decimals
		#
		nrows = N_ROWS_IN_SETTINGS_LAYOUT_TABLE
		table_widget = QTableWidget(nrows, 2)
		#
		table_widget.setItem(0, 0, QTableWidgetItem(
			"Maximum number of columns per page"))
		value = QTableWidgetItem(f"{max_cols}")
		value.setTextAlignment(QtCore.Qt.AlignCenter)
		table_widget.setItem(0, 1, QTableWidgetItem(value))

		table_widget.setItem(
			1, 0,
			QTableWidgetItem("Field width"))
		value = QTableWidgetItem(f"{width}")
		value.setTextAlignment(QtCore.Qt.AlignCenter)
		table_widget.setItem(1, 1, QTableWidgetItem(value))
		#
		table_widget.setItem(
			2, 0,
			QTableWidgetItem("Decimal points"))
		value = QTableWidgetItem(f"{decimals}")
		value.setTextAlignment(QtCore.Qt.AlignCenter)
		table_widget.setItem(2, 1, QTableWidgetItem(value))

		return table_widget

# --------------------------------------------------------------------------


class SettingsPlaneCommand:
	""" The Settings plane command is used to establish the axes to be used
	in plots.
	"""

	def __init__(
			self,
			director: Status,
			common: Spaces) -> None:

		self._director = director
		self.common = common
		self._director.command = "Settings - plane"
		self._hor_axis_title = "Horizontal axis"
		self._hor_axis_options_title = "Dimension to use"
		self._hor_axis_options = self._director.configuration_active.dim_names
		self._vert_axis_title = "Vertical axis"
		self._vert_axis_options_title = "Dimension to use"

	# ------------------------------------------------------------------------

	def execute(
			self,
			common: Spaces) -> None: # noqa: ARG002

		self._director.record_command_as_selected_and_in_process()
		self._director.optionally_explain_what_command_does()
		self._director.dependency_checker.detect_dependency_problems()
		self._get_plane_from_user(
			self._hor_axis_title, self._hor_axis_options_title,
			self._hor_axis_options)
		self._director.common.print_plane_settings()
		self._director.common.create_plot_for_plot_and_gallery_tabs(
			"configuration")
		self._director.title_for_table_widget = "Plane settings"
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.set_focus_on_tab('Plot')
		self._director.record_command_as_successfully_completed()
		return

	# ------------------------------------------------------------------------

	def _get_plane_from_user(
			self,
			title: str,
			items: list[str],
			default_values: list[str]) -> None:

		dim_names = self._director.configuration_active.dim_names
		selected_option = None

		dialog = ChoseOptionDialog(title, items, default_values)
		result = dialog.exec()
		if result == QDialog.Accepted:
			selected_option = dialog.selected_option  # + 1
			match selected_option:
				case 0:
					hor_axis_name = dim_names[0]
					hor_dim = 0
					vert_axis_name = dim_names[1]
					vert_dim = 1
				case 1:
					hor_axis_name = dim_names[1]
					hor_dim = 1
					vert_axis_name = dim_names[0]
					vert_dim = 0
				case _:
					hor_axis_name = \
						self._director.configuration_active.hor_axis_name
					vert_axis_name = \
						self._director.configuration_active.vert_axis_name
					hor_dim = self._director.common.hor_dim
					vert_dim = self._director.common.vert_dim

		else:
			hor_axis_name = \
				self._director.configuration_active.hor_axis_name
			vert_axis_name = \
				self._director.configuration_active.vert_axis_name
			hor_dim = self._director.common.hor_dim
			vert_dim = self._director.common.vert_dim

		if selected_option is None:
			hor_axis_name = \
				self._director.configuration_active.hor_axis_name
			vert_axis_name = \
				self._director.configuration_active.vert_axis_name
			hor_dim = self._director.common.hor_dim
			vert_dim = self._director.common.vert_dim

		else:
			hor_axis_name = \
				self._director.configuration_active.hor_axis_name
			vert_axis_name = \
				self._director.configuration_active.vert_axis_name
			hor_dim = self._director.common.hor_dim
			vert_dim = self._director.common.vert_dim

		if selected_option is None:
			hor_axis_name = \
				self._director.configuration_active.hor_axis_name
			vert_axis_name = \
				self._director.configuration_active.vert_axis_name
			hor_dim = self._director.common.hor_dim
			vert_dim = self._director.common.vert_dim

		self._director.common.hor_dim = hor_dim
		self._director.common.vert_dim = vert_dim
		self._director.configuration_active.hor_axis_name = hor_axis_name
		self._director.configuration_active.vert_axis_name = vert_axis_name
		return

	# ------------------------------------------------------------------------

	def _display(self) -> QTableWidget:
		#
		gui_output_as_widget = self._create_table_widget_for_settings_plane()
		#
		self._director.set_column_and_row_headers(
			gui_output_as_widget,
			["Setting", "Status"],
			[])
		#
		self._director.resize_and_set_table_size(gui_output_as_widget, 4)
		#
		self._director.output_widget_type = "Table"
		return gui_output_as_widget

	# ------------------------------------------------------------------------

	def _create_table_widget_for_settings_plane(self) -> QTableWidget:

		_hor_axis_name = self._director.configuration_active.hor_axis_name
		_vert_axis_name = self._director.configuration_active.vert_axis_name

		nrows = N_ROWS_IN_SETTINGS_PLANE_TABLE
		table_widget = QTableWidget(nrows, 2)
		#
		table_widget.setItem(
			0, 0, QTableWidgetItem("Horizontal axis will be defined by:"))
		table_widget.setItem(
			0, 1, QTableWidgetItem(str(_hor_axis_name)))
		table_widget.setItem(
			1, 0, QTableWidgetItem("Vertical axis will be defined by:"))
		table_widget.setItem(
			1, 1, QTableWidgetItem(str(_vert_axis_name)))
		return table_widget

	# -------------------------------------------------------------------------


class SettingsPlotCommand:
	""" The Settings - plot command is used to set some plots settings used
	in the program.
	"""
	def __init__(
			self,
			director: Status,
			common: Spaces) -> None:
		self._director = director
		self.common = common
		self._director.command = "Settings - plot settings"
		self._plot_title = "Show if available"
		self._plot_items = [
			"Bisector",
			"Connector",
			"Reference points",
			"Only reference points in Joint plots"]
		self._plot_default_values = [
			self._director.common.show_bisector,
			self._director.common.show_connector,
			self._director.common.show_reference_points,
			self._director.common.show_just_reference_points]

	# ------------------------------------------------------------------------

	def execute(
			self,
			common: Spaces) -> None: # noqa: ARG002

		self._director.record_command_as_selected_and_in_process()
		self._director.optionally_explain_what_command_does()
		self._get_plot_settings_from_user(
			self._plot_title, self._plot_items,
			self._plot_default_values)
		self._director.common.print_plot_settings()
		self._director.title_for_table_widget = "Plot settings"
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.set_focus_on_tab('Output')
		self._director.record_command_as_successfully_completed()
		return

# --------------------------------------------------------------------------

	def _get_plot_settings_from_user(
			self,
			title: str,
			items: list[str],
			default_values: list[str]) -> None:
		
		# Save current state before showing dialog
		original_show_bisector = self._director.common.show_bisector
		original_show_connector = self._director.common.show_connector
		original_show_reference_points = \
			self._director.common.show_reference_points
		original_show_just_reference_points = \
			self._director.common.show_just_reference_points

		dialog = ModifyItemsDialog(title, items, default_values=default_values)
		
		if dialog.exec() == QDialog.Accepted:
			selected_items = dialog.selected_items()
			
			features_indexes = [
				j for i in range(len(selected_items))
				for j in range(len(items))
				if selected_items[i] == items[j]
			]
			
			show_bisector = TEST_IF_BISECTOR_SELECTED in features_indexes
			show_connector = TEST_IF_CONNECTOR_SELECTED in features_indexes
			show_reference_points = \
				TEST_IF_REFERENCE_POINTS_SELECTED in features_indexes
			show_just_reference_points = \
				TEST_IF_JUST_REFERENCE_POINTS_SELECTED in features_indexes

			self._director.common.show_bisector = show_bisector
			self._director.common.show_connector = show_connector
			self._director.common.show_reference_points = show_reference_points
			self._director.common.show_just_reference_points = \
				show_just_reference_points
		else:
			# User cancelled - restore original state
			self._director.common.show_bisector = original_show_bisector
			self._director.common.show_connector = original_show_connector
			self._director.common.show_reference_points = \
				original_show_reference_points
			self._director.common.show_just_reference_points = \
				original_show_just_reference_points

		del dialog
		return


	# ------------------------------------------------------------------------

	def _display(self) -> QTableWidget:
		#
		gui_output_as_widget = self._create_table_widget_for_settings_plot()
		#
		self._director.set_column_and_row_headers(
			gui_output_as_widget,
			["Setting", "Status"],
			[])
		#
		self._director.resize_and_set_table_size(gui_output_as_widget, 4)
		#
		self._director.output_widget_type = "Table"
		return gui_output_as_widget

	# ------------------------------------------------------------------------

	def _create_table_widget_for_settings_plot(self) -> QTableWidget:

		show_bisector = self._director.common.show_bisector
		show_connector = self._director.common.show_connector
		show_reference_points = self._director.common.show_reference_points
		show_just_reference_points = \
			self._director.common.show_just_reference_points
		#
		nrows = N_ROWS_IN_SETTINGS_PLOT_TABLE
		ncols = N_COLS_IN_TABLE
		table_widget = QTableWidget(nrows, ncols)
		#
		table_widget.setItem(
			0, 0, QTableWidgetItem("Show bisector"))
		table_widget.setItem(
			0, 1, QTableWidgetItem(str(show_bisector)))
		table_widget.setItem(
			1, 0, QTableWidgetItem("Show connector"))
		table_widget.setItem(
			1, 1, QTableWidgetItem(str(show_connector)))
		table_widget.setItem(
			2, 0, QTableWidgetItem("Show reference points"))
		table_widget.setItem(
			2, 1,
			QTableWidgetItem(str(show_reference_points)))
		table_widget.setItem(
			3, 0,
			QTableWidgetItem("Show just reference points"))
		table_widget.setItem(
			3, 1,
			QTableWidgetItem(str(show_just_reference_points)))
		return table_widget

# --------------------------------------------------------------------------


class SettingsPresentationLayerCommand:

	def __init__(
			self,
			director: Status,
			common: Spaces) -> None:

		self._director = director
		self.common = common
		self._director.command = "Settings - presentation layer"

# --------------------------------------------------------------------------

	def execute(
			self,
			common: Spaces, # noqa: ARG002
			layer_to_use: str) -> None:

		self._director.record_command_as_selected_and_in_process()
		self._director.optionally_explain_what_command_does()
		self._director.dependency_checker.detect_dependency_problems()
		self._director.common.presentation_layer = layer_to_use

		self._director.title_for_table_widget \
			= (f" Presentation layer will be created using "
				f"{self._director.common.presentation_layer} library")
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.set_focus_on_tab('Output')
		self._director.record_command_as_successfully_completed()
		return

# --------------------------------------------------------------------------


class SettingsSegmentCommand:
	""" The Settings segment command is used to set various parameters used
	in the program.
	"""
	def __init__(
			self,
			director: Status,
			common: Spaces) -> None:

		self._director = director
		self.common = common
		self._director.command = "Settings - segment sizing"
		self._segment_title = "Segment sizing"
		self._segment_items = [
			"Define battleground sector using percent "
			"\nof connector on each side of bisector ",
			"Define core sector around reference "
			"\npoint using percent of connector"]
		self._segment_default_values = [
			int(self._director.common.battleground_size * 100),
			int(self._director.common.core_tolerance * 100)]
		self._segment_integers = True

	# ------------------------------------------------------------------------

	def execute(
			self,
			common: Spaces) -> None: # noqa: ARG002

		self._director.record_command_as_selected_and_in_process()
		self._director.optionally_explain_what_command_does()
		self._get_segment_settings_from_user(
			self._segment_title, self._segment_items,
			self._segment_integers, self._segment_default_values)
		self._director.common.print_segment_sizing_settings()
		self._director.title_for_table_widget = "Segment settings"
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.set_focus_on_tab('Output')
		self._director.record_command_as_successfully_completed()
		return

	# ------------------------------------------------------------------------

	def _get_segment_settings_from_user(
			self,
			title: str,
			items: list[str],
			integers: bool, # noqa: FBT001
			default_values: list[int]) -> None:

		dialog = ModifyValuesDialog(
			title, items, integers, default_values=default_values)
		dialog.selected_items()
		result = dialog.exec()
		if result == QDialog.Accepted:
			value = dialog.selected_items()
			_tolerance = value[0][1] / 100.0
			_core_tolerance = value[1][1] / 100.0
		else:
			value = default_values[0]
			_tolerance = self._director.common.battleground_size
			_core_tolerance = self._director.common.core_tolerance

		self._director.common.battleground_size = _tolerance
		self._director.common.core_tolerance = _core_tolerance
		return

	# ------------------------------------------------------------------------

	def _display(self) -> QTableWidget:
		#
		gui_output_as_widget = \
			self._create_table_widget_for_settings_segment()
		#
		self._director.set_column_and_row_headers(
			gui_output_as_widget,
			["Segment sizing", "Percent"],
			[])
		#
		self._director.resize_and_set_table_size(gui_output_as_widget, 4)
		#
		self._director.output_widget_type = "Table"
		return gui_output_as_widget

	# ------------------------------------------------------------------------

	def _create_table_widget_for_settings_segment(self) -> QTableWidget:

		tolerance = self._director.common.battleground_size
		core_tolerance = self._director.common.core_tolerance
		#
		nrows = N_ROWS_IN_SETTINGS_SEGMENTS_TABLE
		table_widget = QTableWidget(nrows, 2)
		#
		table_widget.setItem(
			0, 0,
			QTableWidgetItem(
				"Define battleground sector using percent "
				"\nof connector on each side of bisector"))
		value = QTableWidgetItem(f"{tolerance * 100: 3.0f}")
		value.setTextAlignment(QtCore.Qt.AlignCenter)
		table_widget.setItem(
			0, 1, QTableWidgetItem(value))

		table_widget.setItem(
			1, 0,
			QTableWidgetItem(
				"Define core sector around reference "
				"\npoint using percent of connector"))
		value = QTableWidgetItem(f"{core_tolerance * 100: 3.0f}")
		value.setTextAlignment(QtCore.Qt.AlignCenter)
		table_widget.setItem(1, 1, QTableWidgetItem(value))
		return table_widget

# --------------------------------------------------------------------------


class SettingsVectorSizeCommand:
	""" The Settings vector command is used to set various parameters used
	in the program.
	"""
	def __init__(
			self,
			director: Status,
			common: Spaces) -> None:

		self._director = director
		self.common = common
		self._director.command = "Settings - vector sizing"
		self._vector_title = "Vector size"
		self._vector_items = [
			"Vector head size in inches",
			"Vector thickness in inches"]
		self._vector_default_values = [
			self._director.common.vector_head_width,
			self._director.common.vector_width]
		self._vector_integers = False

		return

	# ------------------------------------------------------------------------

	def execute(
			self,
			common: Spaces) -> None: # noqa: ARG002

		self._director.record_command_as_selected_and_in_process()
		self._director.optionally_explain_what_command_does()
		self._get_vector_settings_from_user(
			self._vector_title, self._vector_items,
			self._vector_integers, self._vector_default_values)
		self._director.common.print_vector_sizing_settings()
		self._director.title_for_table_widget = "Vector settings"
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.command = "Settings - vector sizing"
		self._director.set_focus_on_tab('Output')
		self._director.record_command_as_successfully_completed()
		return

	# ------------------------------------------------------------------------

	def _get_vector_settings_from_user(
			self,
			title: str,
			items: list[str],
			integers: bool, # noqa: FBT001
			default_values: list[float]) -> None:

		dialog = ModifyValuesDialog(
			title, items, integers, default_values=default_values)
		dialog.selected_items()
		result = dialog.exec()
		if result == QDialog.Accepted:
			value = dialog.selected_items()
			vector_head_width = value[0][1]
			vector_width = value[1][1]
		else:
			vector_head_width = self._director.common.vector_head_width
			vector_width = self._director.common.vector_width

		self._director.common.vector_head_width = vector_head_width
		self._director.common.vector_width = vector_width

		return

	# ------------------------------------------------------------------------

	def _display(self) -> QTableWidget:
		#
		gui_output_as_widget = \
			self._create_table_widget_for_settings_vectors()
		#
		self._director.set_column_and_row_headers(
			gui_output_as_widget,
			["Vector element", "Size in inches"],
			[])
		#
		self._director.resize_and_set_table_size(gui_output_as_widget, 4)
		#
		self._director.output_widget_type = "Table"
		return gui_output_as_widget

	# ------------------------------------------------------------------------

	def _create_table_widget_for_settings_vectors(self) -> QTableWidget:

		vector_head_width = self._director.common.vector_head_width
		vector_width = self._director.common.vector_width
		#
		nrows = N_ROWS_IN_SETTINGS_VECTOR_TABLE
		table_widget = QTableWidget(nrows, 2)
		#
		table_widget.setItem(
			0, 0, QTableWidgetItem("Head size"))
		value = QTableWidgetItem(f"{vector_head_width: 3.2f}")
		value.setTextAlignment(QtCore.Qt.AlignCenter)
		table_widget.setItem(
			0, 1, QTableWidgetItem(value))

		table_widget.setItem(
			1, 0, QTableWidgetItem("Thickness"))
		value = QTableWidgetItem(f"{vector_width: 3.2f}")
		value.setTextAlignment(QtCore.Qt.AlignCenter)
		table_widget.setItem(
			1, 1, QTableWidgetItem(value))
		return table_widget


# --------------------------------------------------------------------------


class SimilaritiesCommand:
	""" The Similarities command is used to establish similarities
		between the points by reading a file of similarities.
	"""
	def __init__(
			self,
			director: Status,
			common: Spaces) -> None:

		self._director = director
		self.common = common
		self._director.command = "Similarities"
		self._director.similarities_candidate.nreferent = 0
		self._director.similarities_candidate.nitem = 0
		self._director.similarities_candidate.item_names.clear()
		self._director.similarities_candidate.item_labels.clear()
		self._director.similarities_candidate.similarities.clear()
		self._director.similarities_candidate.similarities_as_dict = {}
		self._director.similarities_candidate.similarities_as_list.clear()
		self._director.similarities_candidate.similarities_as_square.clear()
		self._director.similarities_candidate.similarities_as_dataframe = \
			pd.DataFrame()
		self._director.similarities_active.similarities_as_dataframe = \
			pd.DataFrame()
		self._director.similarities_candidate.sorted_similarities = {}

		self._director.similarities_candidate.ndyad = 0
		self._director.similarities_candidate.n_pairs = 0
		self._director.similarities_candidate.range_pairs = range(0)
		self._director.similarities_candidate.a_item_names.clear()
		self._director.similarities_candidate.b_item_names.clear()
		self._director.similarities_candidate.a_item_labels.clear()
		self._director.similarities_candidate.b_item_labels.clear()
		self._director.similarities_candidate.a_item_labels_as_dict = {}
		self._director.similarities_candidate.b_item_labels_as_dict = {}
		self._director.similarities_candidate.a_item_labels_as_dataframe = \
			pd.DataFrame()
		self._director.similarities_candidate.b_item_labels_as_dataframe = \
			pd.DataFrame()
		self._director.similarities_active.ranked_similarities.clear()
		self._director.similarities_active.ranked_similarities_as_list = \
			np.array([])
		self._director.similarities_active.ranked_similarities_as_square.\
			clear()
		self._director.similarities_active.ranked_similarities_as_dataframe = \
			pd.DataFrame()

		# self._director.active.sorted_similarities_w_pairs.clear()
		self._director.similarities_candidate.value_type = "Unknown"
		self._width: int = 8
		self._decimals: int = 2
		self._similarities_caption: str = "Open similarities"
		self._similarities_filter: str = "*.txt"
		self._empty_similarities_title: str = "No file selected"
		self._empty_similarities_message: str = \
			"To establish similarities select file in dialog."
		self._mismatch_title = "Similarities do not match configuration"
		self._mismatch_options_title = "How to proceed"
		self._mismatch_options: list[str] = [
			"Abandon similarities", "Abandon active configuration"]
		return
	
	# ------------------------------------------------------------------------

	def execute(
			self,
			common: Spaces,
			value_type: str) -> None:
	
		width = self._width
		decimals = self._decimals

		self._director.record_command_as_selected_and_in_process()
		self._director.optionally_explain_what_command_does()
		self._director.dependency_checker.detect_dependency_problems()
		self._director.similarities_candidate.value_type = value_type

		file = self._director.get_file_name_and_handle_nonexistent_file_names(
			self._similarities_caption, self._similarities_filter)
		if value_type == "similarities":
			self._director.similarities_candidate = \
				self._director.common.read_lower_triangular_matrix(
					file, "similarities")
		else:
			self._director.similarities_candidate = \
				self._director.common.read_lower_triangular_matrix(
					file, "dissimilarities")

		self._director.similarities_candidate.duplicate_similarities(common)

		self._director.similarities_candidate.range_similarities = \
			range(len(
				self._director.similarities_candidate.similarities_as_list))
		self._director.similarities_candidate.rank_similarities()

		self._director.dependency_checker.detect_consistency_issues()
		self._director.similarities_active = \
			self._director.similarities_candidate
		self._director.similarities_original = \
			self._director.similarities_candidate
		self._director.similarities_last = \
			self._director.similarities_candidate

		if self._director.common.have_active_configuration():
			self._director.similarities_active. \
				create_ranked_similarities_dataframe()
				# self._director)
			self._director.similarities_active.compute_differences_in_ranks()
			self._director.similarities_active.prepare_for_shepard_diagram()
		self._director.similarities_active.print_the_similarities(
			width, decimals, common)
		self._director.common.create_plot_for_plot_and_gallery_tabs(
			"heatmap_simi")
		nreferent = self._director.similarities_active.nreferent

		self._director.title_for_table_widget = (
			f"The {value_type} matrix has {nreferent} items")
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.set_focus_on_tab('Plot')
		self._director.record_command_as_successfully_completed()
		
		return

# --------------------------------------------------------------------------


class TargetCommand:
	"""The Target command establishes a target configuration.
	"""
	def __init__(
			self,
			director: Status,
			common: Spaces) -> None:

		self._director = director
		self.common = common
		self._director.command = "Target"
		self._director.target_candidate.file_handle = ""
		self._director.target_candidate.ndim = 0
		self._director.target_candidate.npoint = 0
		self._director.target_candidate.dim_labels.clear()
		self._director.target_candidate.dim_names.clear()
		self._director.target_candidate.point_labels.clear()
		self._director.target_candidate.point_names.clear()
		self._director.target_candidate.point_coords = pd.DataFrame()
		self._director.target_candidate.distances.clear()
		self._director.target_candidate.seg = pd.DataFrame()
		self._target_caption: str = "Open target configuration"
		self._target_filter: str = "*.txt"
		return

	# ------------------------------------------------------------------------

	def execute(
			self,
			common: Spaces) -> None:  # noqa: ARG002

		self._director.record_command_as_selected_and_in_process()
		self._director.optionally_explain_what_command_does()
		file_name = \
			self._director.get_file_name_and_handle_nonexistent_file_names(
			self._target_caption, self._target_filter)
		self._director.target_candidate = \
			self._director.common.read_configuration_type_file(
				file_name, "Target")
		self._director.dependency_checker.detect_consistency_issues()
		self._director.target_active = self._director.target_candidate
		self._director.target_original = self._director.target_active
		self._director.target_last = self._director.target_active
		self._director.target_active.print_target()
		self._director.common.create_plot_for_plot_and_gallery_tabs("target")
		ndim = self._director.target_candidate.ndim
		npoint = self._director.target_candidate.npoint
		self._director.title_for_table_widget = (
			f"Target configuration has {ndim} dimensions and "
			f"{npoint} points")
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.record_command_as_successfully_completed()
		return




