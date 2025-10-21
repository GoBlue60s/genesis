from __future__ import annotations

import random
import pandas as pd
import peek
from typing import TYPE_CHECKING

from PySide6.QtWidgets import QDialog, QTableWidget

from common import Spaces

from dialogs import ModifyValuesDialog, PairofPointsDialog
from exceptions import SpacesError

from supporters import ASupporterGrouping

if TYPE_CHECKING:
	from director import Status

# ---------------------------------------------------------------------------


class BaseCommand(ASupporterGrouping):
	def __init__(self, director: Status, common: Spaces) -> None:
		super().__init__(director, common)

		self._director = director
		self._common = common
		self._director.command = "Base"
		self._base_groups_to_show = ""
		rivalry = self._director.rivalry
		self._base_pcts = rivalry.base_pcts
		self._rival_a = rivalry.rival_a
		self._rival_b = rivalry.rival_b

		return

	# ------------------------------------------------------------------------

	def execute(self, common: Spaces, groups_to_show: str) -> None:
		director = self._director
		common = director.common
		director.record_command_as_selected_and_in_process()
		director.optionally_explain_what_command_does()
		director.dependency_checker.detect_dependency_problems()
		director.current_command._base_groups_to_show = groups_to_show

		# Track passive command with parameters for script generation
		common.push_passive_command_to_undo_stack(
			director.command,
			{"groups_to_show": groups_to_show}
		)

		common.create_plot_for_tabs("base")
		director.title_for_table_widget = (
			f"Base supporters of {self._rival_a.name} and {self._rival_b.name}"
		)
		director.create_widgets_for_output_and_log_tabs()
		director.record_command_as_successfully_completed()

		return


# --------------------------------------------------------------------------


class BattlegroundCommand(ASupporterGrouping):
	"""The Battleground command creates a plot with a lines
	delineating area with battleground individuals.
	"""

	def __init__(self, director: Status, command: str) -> None:
		super().__init__(director, director.common)

		self._director = director
		self.command = command
		self._director.command = "Battleground"
		self._battleground_groups_to_show = ""
		rivalry = self._director.rivalry
		self._battleground_pcts = rivalry.battleground_pcts

		return

	# ------------------------------------------------------------------------

	def execute(
		self,
		common: Spaces,  # noqa: ARG002
		groups_to_show: str,
	) -> None:
		self._director.record_command_as_selected_and_in_process()
		self._director.optionally_explain_what_command_does()
		self._director.dependency_checker.detect_dependency_problems()
		self._director.current_command._battleground_groups_to_show = (
			groups_to_show
		)

		# Track passive command with parameters for script generation
		self._director.common.push_passive_command_to_undo_stack(
			self._director.command,
			{"groups_to_show": groups_to_show}
		)

		self._director.common.create_plot_for_tabs("battleground")
		self._director.title_for_table_widget = "Size of battleground"
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.record_command_as_successfully_completed()
		return

	# ------------------------------------------------------------------------


class ContestCommand:
	"""contest command - identifies regions defined by reference points"""

	def __init__(self, director: Status, common: Spaces) -> None:
		self._director = director
		self.common = common
		self._director.command = "Contest"

		return

	# ------------------------------------------------------------------------

	def execute(self, common: Spaces) -> None:  # noqa: ARG002
		rivalry = self._director.rivalry
		self._director.record_command_as_selected_and_in_process()
		self._director.optionally_explain_what_command_does()
		self._director.dependency_checker.detect_dependency_problems()
		self._director.common.create_plot_for_tabs("contest")
		self._rival_a = rivalry.rival_a
		self._rival_b = rivalry.rival_b
		self._director.title_for_table_widget = (
			f"Segments are based on a contest between "
			f"{self._rival_a.name} and {self._rival_b.name}"
		)
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.record_command_as_successfully_completed()
		return

	# ------------------------------------------------------------------------


class ConvertibleCommand(ASupporterGrouping):
	"""The convertible supporters command identifies regions of opponent
	supporters that may be convertible
	"""

	def __init__(self, director: Status, common: Spaces) -> None:
		super().__init__(director, common)

		self._director.command = "Convertible"
		self._groups_to_show = ""
		rivalry = self._director.rivalry
		self._conv_pcts = rivalry.conv_pcts
		self._rival_a = rivalry.rival_a
		self._rival_b = rivalry.rival_b

		return

	# ------------------------------------------------------------------------

	def execute(
		self,
		common: Spaces,  # noqa: ARG002
		groups_to_show: str,
	) -> None:
		self._director.record_command_as_selected_and_in_process()
		self._director.optionally_explain_what_command_does()
		self._director.dependency_checker.detect_dependency_problems()
		self._director.current_command._convertible_groups_to_show = (
			groups_to_show
		)

		# Track passive command with parameters for script generation
		self._director.common.push_passive_command_to_undo_stack(
			self._director.command,
			{"groups_to_show": groups_to_show}
		)

		self._director.common.create_plot_for_tabs("convertible")
		self._director.title_for_table_widget = (
			f"Potential supporters convertible to "
			f"{self._rival_a.name} and {self._rival_b.name}"
		)
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.record_command_as_successfully_completed()
		return


# ------------------------------------------------------------------------


class CoreSupportersCommand(ASupporterGrouping):
	def __init__(self, director: Status, common: Spaces) -> None:
		super().__init__(director, common)
		self._director = director
		self.common = common
		self._director.command = "Core supporters"
		self._groups_to_show = ""
		rivalry = self._director.rivalry
		self._core_pcts = rivalry.core_pcts
		self._core_radius = rivalry.core_radius
		self._rival_a = rivalry.rival_a
		self._rival_b = rivalry.rival_b
		return

	# ------------------------------------------------------------------------

	def execute(
		self,
		common: Spaces,  # noqa: ARG002
		groups_to_show: str,
	) -> None:
		self._director.record_command_as_selected_and_in_process()
		self._director.optionally_explain_what_command_does()
		self._director.dependency_checker.detect_dependency_problems()
		self._director.current_command.core_groups_to_show = groups_to_show

		# Track passive command with parameters for script generation
		self._director.common.push_passive_command_to_undo_stack(
			self._director.command,
			{"groups_to_show": groups_to_show}
		)

		self._director.common.create_plot_for_tabs("core")
		self._director.title_for_table_widget = (
			f"Core supporters of {self._rival_a.name} and {self._rival_b.name}"
		)
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.record_command_as_successfully_completed()
		return

	# ------------------------------------------------------------------------


class FirstDimensionCommand(ASupporterGrouping):
	"""The first_dim command - identifies regions defined by the
	first dimension
	"""

	def __init__(self, director: Status, common: Spaces) -> None:
		super().__init__(director, common)

		self._director = director
		self._common = common
		self._director.command = "First dimension"
		self._groups_to_show = ""
		rivalry = self._director.rivalry
		self._first_pcts = rivalry.first_pcts
		self._first_div = rivalry.first_div
		self._rival_a = rivalry.rival_a
		self._rival_b = rivalry.rival_b

		return

	# ------------------------------------------------------------------------

	def execute(self, common: Spaces, groups_to_show: str) -> None:
		self._director.record_command_as_selected_and_in_process()
		self._director.optionally_explain_what_command_does()
		self._director.dependency_checker.detect_dependency_problems()
		self._director.current_command._first_dim_groups_to_show = (
			groups_to_show
		)

		# Track passive command with parameters for script generation
		common.push_passive_command_to_undo_stack(
			self._director.command,
			{"groups_to_show": groups_to_show}
		)

		common.create_plot_for_tabs("first")
		self._director.title_for_table_widget = "Party oriented segments"
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.record_command_as_successfully_completed()
		return


# ----------------------------------------------------------------------------


class JointCommand:
	"""The Joint command is used to create a plot with the reference
	points and individuals.
	"""

	def __init__(self, director: Status, common: Spaces) -> None:
		self._director = director
		self.common = common
		self._director.command = "Joint"

		return

	# ------------------------------------------------------------------------

	def execute(self, common: Spaces) -> None:  # noqa: ARG002
		self._director.record_command_as_selected_and_in_process()
		self._director.optionally_explain_what_command_does()
		self._director.dependency_checker.detect_dependency_problems()
		self._director.common.create_plot_for_tabs("joint")
		self._director.title_for_table_widget = (
			"Warning: Make sure the scores "
			"match the \ndimensions AND orientation of the active"
			"configuration."
		)
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.record_command_as_successfully_completed()
		return

	# ------------------------------------------------------------------------


class LikelySupportersCommand(ASupporterGrouping):
	def __init__(self, director: Status, common: Spaces) -> None:
		super().__init__(director, common)

		""" The Likely supporters command identifies regions defining
		likely supporters of both reference points
		"""
		self._director = director
		self.common = common
		rivalry = self._director.rivalry
		self._director.command = "Likely supporters"
		self._groups_to_show = ""
		self._likely_pcts = rivalry.likely_pcts
		self._rival_a = rivalry.rival_a
		self._rival_b = rivalry.rival_b

		return

	# ------------------------------------------------------------------------

	def execute(
		self,
		common: Spaces,  # noqa: ARG002
		groups_to_show: str,
	) -> None:
		self._director.record_command_as_selected_and_in_process()
		self._director.optionally_explain_what_command_does()
		self._director.dependency_checker.detect_dependency_problems()
		self._director.current_command.likely_groups_to_show = groups_to_show

		# Track passive command with parameters for script generation
		self._director.common.push_passive_command_to_undo_stack(
			self._director.command,
			{"groups_to_show": groups_to_show}
		)

		self._director.common.create_plot_for_tabs("likely")
		self._director.title_for_table_widget = (
			f"Likely supporters of {self._rival_a.name} "
			f"and {self._rival_b.name}"
		)
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.record_command_as_successfully_completed()

		return

	# ------------------------------------------------------------------------


class ReferencePointsCommand:
	"""The Reference command is used to establish a pair of
	points to be used as reference points.
	"""

	def __init__(self, director: Status, common: Spaces) -> None:
		self._director = director
		rivalry = self._director.rivalry
		self.common = common
		self._director.command = "Reference points"

		self.rival_a = rivalry.rival_a
		self.rival_b = rivalry.rival_b
		self._refs_title: str = "Select a pair of reference points"
		self._refs_items: list[str] = (
			self._director.configuration_active.point_names
		)

		return

	# ------------------------------------------------------------------------

	def execute(self, common: Spaces) -> None:

		rivalry = self._director.rivalry
		point_names = self._director.configuration_active.point_names
		point_labels = self._director.configuration_active.point_labels
		rival_a = rivalry.rival_a
		rival_b = rivalry.rival_b

		self._director.record_command_as_selected_and_in_process()
		self._director.optionally_explain_what_command_does()
		self._director.dependency_checker.detect_dependency_problems()
		self._director.configuration_active.print_the_configuration()

		# Get user's desired reference points WITHOUT modifying state
		new_rival_a_index, new_rival_b_index = (
			self._get_reference_points_from_user(
				self._refs_title, self._refs_items
			)
		)

		# Capture OLD state BEFORE modifications, save NEW names as params
		params = {
			"contest": [
				point_names[new_rival_a_index],
				point_names[new_rival_b_index]
			]
		}
		self.common.capture_and_push_undo_state(
			"Reference points", "active", params
		)

		# NOW modify the rivalry state with the new reference points
		rivalry.rival_a.index = new_rival_a_index
		rivalry.rival_b.index = new_rival_b_index
		rivalry.rival_a.name = point_names[new_rival_a_index]
		rivalry.rival_b.name = point_names[new_rival_b_index]
		rivalry.rival_a.label = point_labels[new_rival_a_index]
		rivalry.rival_b.label = point_labels[new_rival_b_index]

		self._print_reference_points()

		rivalry.create_or_revise_rivalry_attributes(self._director, common)

		rivalry.use_reference_points_to_define_segments(self._director)

		if (
			self._director.common.have_scores()
			and not self._director.common.have_segments()
		):
			rivalry.assign_to_segments()

		self._director.common.create_plot_for_tabs("configuration")

		self._director.title_for_table_widget = (
			f"Reference points will be {rival_a.name} and {rival_b.name}"
		)
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.set_focus_on_tab("Plot")
		self._director.record_command_as_successfully_completed()
		return

	# ------------------------------------------------------------------------

	def _get_reference_points_from_user_initialize_variables(self) -> None:
		self.need_reference_points_error_title = self._director.command
		self.need_reference_points_error_message = (
			"A pair of reference points needs to be established."
		)

	# ------------------------------------------------------------------------

	def _get_reference_points_from_user(
		self, refs_title: str, refs_items: list[str]
	) -> tuple[int, int]:
		self._get_reference_points_from_user_initialize_variables()
		range_points = self._director.configuration_active.range_points
		point_names = self._director.configuration_active.point_names

		# Check if executing from script with parameters
		if (
			self._director.executing_script
			and self._director.script_parameters
			and "contest" in self._director.script_parameters
		):
			selected_items = self._director.script_parameters["contest"]
			if not isinstance(selected_items, list) or len(selected_items) != 2:
				raise SpacesError(
					"Script parameter error",
					"contest parameter must be a list of 2 point names"
				)
		else:
			dialog = PairofPointsDialog(refs_title, refs_items)

			if dialog.exec() == QDialog.Accepted:
				selected_items = dialog.selected_items()
			else:
				del dialog
				raise SpacesError(
					self.need_reference_points_error_title,
					self.need_reference_points_error_message,
				)

			del dialog

		# Find the index for each selected item
		refs_indexes = []
		for selected_name in selected_items:
			found_index = None
			for j in range_points:
				if selected_name == point_names[j]:
					found_index = j
					break
			if found_index is None:
				raise SpacesError(
					"Invalid reference point",
					f"Point '{selected_name}' not found in configuration"
				)
			refs_indexes.append(found_index)

		refs_a = refs_indexes[0]
		refs_b = refs_indexes[1]

		return refs_a, refs_b

	# ------------------------------------------------------------------------

	def _print_reference_points(self) -> None:
		rivalry = self._director.rivalry
		rival_a = rivalry.rival_a
		rival_b = rivalry.rival_b

		print("\nReference points: ")
		print("\t", rival_a.label, rival_a.name)
		print("\t", rival_b.label, rival_b.name)
		return

	# ------------------------------------------------------------------------


class SampleDesignerCommand:
	def __init__(self, director: Status, common: Spaces) -> None:
		"""The Sample designer command is used to create a sample design."""
		self._director = director
		self.common = common
		self._director.command = "Sample designer"
		self._director.uncertainty_active.universe_size = 0
		self._director.uncertainty_active.probability_of_inclusion = 0
		self._director.uncertainty_active.nrepetitions = 0
		self._director.uncertainty_active.sample_design = pd.DataFrame(
			columns=["RespId", "Repetition", "Selected"]
		)
		self._director.uncertainty_active.sample_design_frequencies = (
			pd.DataFrame(columns=["Repetition", "Selected", "Count"])
		)
		self._designer_title = "Set sample parameters.."
		self._designer_items = [
			"Probability of inclusion",
			"Number of repetitions",
		]
		self._designer_integers = [True, True]
		self._designer_default_values = [50, 2]
		self._director.uncertainty_active.sample_design_frequencies_as_json = (
			""
		)
		return

	# ------------------------------------------------------------------------

	def execute(self, common: Spaces) -> QTableWidget:  # noqa: ARG002
		self._director.record_command_as_selected_and_in_process()
		self._director.optionally_explain_what_command_does()
		self._director.dependency_checker.detect_dependency_problems()
		self._establish_sample_designer_sizes(
			self._designer_title,
			self._designer_items,
			self._designer_integers,
			self._designer_default_values,
		)

		# Capture state for undo AFTER user input but BEFORE modifications
		params = {
			"universe_size": self._director.uncertainty_active.universe_size,
			"probability_of_inclusion": (
				self._director.uncertainty_active.probability_of_inclusion
			),
			"nrepetitions": self._director.uncertainty_active.nrepetitions
		}
		self.common.capture_and_push_undo_state(
			"Sample designer", "active", params
		)

		self._create_sample_design()

		universe_size = self._director.uncertainty_active.universe_size
		probability_of_inclusion = (
			self._director.uncertainty_active.probability_of_inclusion
		)
		self.common.create_sample_design_analysis_table()
		self._print_sample_design_analysis_results()
		self._director.title_for_table_widget = (
			f"Sample design - Size of universe: {universe_size}, "
			f"Probability of inclusion: {probability_of_inclusion}"
		)
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.set_focus_on_tab("Output")
		self._director.record_command_as_successfully_completed()
		return

	# ------------------------------------------------------------------------

	def _establish_sample_designer_sizes_initialize_variables(self) -> None:
		self._need_sample_sizes_error_title = "Sample parameters"
		self._need_sample_sizes_error_message = (
			"Need sample parameters to create a sample design."
		)

	# ------------------------------------------------------------------------

	def _establish_sample_designer_sizes(
		self,
		title: str,
		items: list[str],
		integers: list[bool],
		default_values: list[int],
	) -> None:
		self._establish_sample_designer_sizes_initialize_variables()

		# Get universe size automatically from evaluations_active
		universe_size = self._director.evaluations_active.nevaluators

		# Check if executing from script with parameters
		if (
			self._director.executing_script
			and self._director.script_parameters
		):
			# Get parameters from script
			if "probability_of_inclusion" in self._director.script_parameters:
				probability_of_inclusion = (
					self._director.script_parameters["probability_of_inclusion"]
				)
			else:
				raise SpacesError(
					"Missing script parameter",
					"probability_of_inclusion parameter required for Sample designer"
				)

			if "nrepetitions" in self._director.script_parameters:
				nrepetitions = self._director.script_parameters["nrepetitions"]
			else:
				raise SpacesError(
					"Missing script parameter",
					"nrepetitions parameter required for Sample designer"
				)
		else:
			# Show dialog to get user input
			dialog = ModifyValuesDialog(
				title, items, integers, default_values=default_values
			)
			dialog.selected_items()
			result = dialog.exec()
			if result == QDialog.Accepted:
				value = dialog.selected_items()
				probability_of_inclusion = value[0][1]
				nrepetitions = value[1][1]
			else:
				raise SpacesError(
					self._need_sample_sizes_error_title,
					self._need_sample_sizes_error_message,
				)

		self._director.uncertainty_active.universe_size = universe_size
		self._director.uncertainty_active.probability_of_inclusion = (
			probability_of_inclusion
		)
		self._director.uncertainty_active.nrepetitions = nrepetitions
		return

	# ------------------------------------------------------------------------

	def _create_sample_design(self) -> None:
		universe_size = self._director.uncertainty_active.universe_size
		probability_of_inclusion = (
			self._director.uncertainty_active.probability_of_inclusion
		)
		nrepetitions = self._director.uncertainty_active.nrepetitions
		sample_design = self._director.uncertainty_active.sample_design

		# sample_size = int(universe_size * probability_of_inclusion / 100)
		range_of_universe = range(universe_size)
		# range_of_sample = range(sample_size)
		range_of_repetitions = range(1, nrepetitions + 1)
		n_selected = 0
		next_out = 0
		for each_repetition in range_of_repetitions:
			for each_case in range_of_universe:
				probability: float = probability_of_inclusion
				if random.uniform(0.0, 100.0) <= probability:
					select = True
					n_selected += 1
				else:
					select = False
				sample_design.loc[next_out] = {
					"RespId": each_case,
					"Repetition": each_repetition,
					"Selected": select,
				}

				next_out += 1

		sample_design.sort_values(by=["Repetition", "RespId"], inplace=True)

		sample_design_frequencies = (
			sample_design.groupby(["Repetition", "Selected"])
			.size()
			.reset_index(name="Count")
		)
		sample_design_frequencies_as_json = sample_design_frequencies.to_json(
			orient="records"
		)

		self._director.uncertainty_active.sample_design = sample_design
		self._director.uncertainty_active.sample_design_nrepetitions = (
			nrepetitions
		)
		self._director.uncertainty_active.sample_design_frequencies = (
			sample_design_frequencies
		)
		self._director.uncertainty_active.sample_design_frequencies_as_json = (
			sample_design_frequencies_as_json
		)

		return

	# ------------------------------------------------------------------------

	def _display(self) -> QTableWidget:
		gui_output_as_widget = self._director.statistics.display_table(
			"sample_design"
		)

		self._director.output_widget_type = "Table"
		return gui_output_as_widget

	# ------------------------------------------------------------------------

	def _print_sample_design_analysis_results(self) -> None:
		"""Print sample design analysis results with fixed-width columns
		and proper alignment.
		"""

		df = self._director.uncertainty_active.sample_design_analysis_df

		# Fixed-width string constants
		header1 = "                Selected       Not Selected      "
		header2 = "Repetition      N      %        N      %      "
		separator = "-------------------------------------------"

		# Print headers and separator
		print("\n" + header1)
		print(header2)
		print(separator)

		# Print each row of data with fixed spacing
		for _, row in df.iterrows():
			print(
				f"{int(row['Repetition']):10d}  "
				f"{int(row['Selected Count']):6d}  "
				f"{row['Selected Percent']:5.2f}   "
				f"{int(row['Not Selected Count']):6d}  "
				f"{row['Not Selected Percent']:5.2f}"
			)

		return


# ------------------------------------------------------------------------


class SampleRepetitionsCommand:
	def __init__(self, director: Status, common: Spaces) -> None:
		"""The Sample repetitions command is used to create
		sample repetitions."""
		self._director = director
		self.common = common
		self._director.command = "Sample repetitions"

		self._director.uncertainty_active.sample_repetitions = pd.DataFrame()

		return

	# ------------------------------------------------------------------------

	def execute(self, common: Spaces) -> None:  # noqa: ARG002

		self._director.record_command_as_selected_and_in_process()
		self._director.optionally_explain_what_command_does()
		self._director.dependency_checker.detect_dependency_problems()
		self._check_that_sizes_match()

		# Capture state for undo BEFORE modifications
		params = {
			"universe_size": self._director.uncertainty_active.universe_size
		}
		self.common.capture_and_push_undo_state(
			"Sample repetitions", "active", params
		)

		self._create_sample_repetitions()
		universe_size = self._director.uncertainty_active.universe_size
		self._director.title_for_table_widget = (
			f"Sample repetitions - Size of universe: {universe_size}"
		)
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.set_focus_on_tab("Output")
		self._director.record_command_as_successfully_completed()
		return

	# ------------------------------------------------------------------------

	def _check_that_sizes_match_initialize_variables(self) -> None:
		universe_size = self._director.uncertainty_active.universe_size
		evaluations = self._director.evaluations_active.evaluations
		self._sample_size_mismatch_error_title = "Sample size mismatch"
		self._sample_size_mismatch_error_message = (
			f"Size in sample design: {universe_size} "
			f"does not match size of evaluations: {len(evaluations)}"
		)

	# ------------------------------------------------------------------------

	def _check_that_sizes_match(self) -> None:
		self._check_that_sizes_match_initialize_variables()
		universe_size = self._director.uncertainty_active.universe_size
		evaluations = self._director.evaluations_active.evaluations

		if universe_size == len(evaluations):
			pass
		else:
			raise SpacesError(
				self._sample_size_mismatch_error_title,
				self._sample_size_mismatch_error_message,
			)

		return

	# ------------------------------------------------------------------------

	def _create_sample_repetitions(self) -> None:
		evaluations = self._director.evaluations_active.evaluations
		universe_size = self._director.uncertainty_active.universe_size
		nrepetitions = self._director.uncertainty_active.nrepetitions
		sample_design = self._director.uncertainty_active.sample_design

		columns = evaluations.columns

		sample_repetitions = pd.DataFrame(columns=columns)
		range_of_repetitions = range(1, nrepetitions + 1)

		next_out = 0
		for each_repetition in range_of_repetitions:
			n_selected_for_repetition = 0
			repetition_start = 0 + (each_repetition - 1) * universe_size
			repetition_end = each_repetition * universe_size
			range_of_this_repetition = range(repetition_start, repetition_end)
			restart = (each_repetition - 1) * universe_size
			for each_case in range_of_this_repetition:
				if sample_design.loc[each_case]["Selected"]:
					n_selected_for_repetition += 1
					sample_repetitions.loc[next_out] = evaluations.loc[
						each_case - 0 - restart
					]
					next_out += 1
				else:
					pass

		self._director.uncertainty_active.sample_repetitions = (
			sample_repetitions
		)

		return

	# ------------------------------------------------------------------------

	def _display(self) -> QTableWidget:
		#
		gui_output_as_widget = self._director.uncertainty_active.\
			create_table_widget_for_sample_designer()
		#
		self._director.set_column_and_row_headers(
			gui_output_as_widget,
			[
				"Repetition",
				"Selected \n N",
				"Percent",
				"Not selected \n N",
				"Percent",
			],
			[],
		)
		#
		self._director.resize_and_set_table_size(gui_output_as_widget, 4)
		#
		self._director.output_widget_type = "Table"
		return gui_output_as_widget

	# ------------------------------------------------------------------------


class ScoreIndividualsCommand:
	def __init__(self, director: Status, common: Spaces) -> None:
		"""The Score individuals command computes scores."""

		self._director = director
		self.common = common
		self._director.command = "Score individuals"
		# file = ""
		self._director.scores_active.scores = pd.DataFrame()
		return

	# ------------------------------------------------------------------------

	def execute(self, common: Spaces) -> None:  # noqa: ARG002
		self._director.record_command_as_selected_and_in_process()
		self._director.optionally_explain_what_command_does()
		self._director.dependency_checker.detect_dependency_problems()

		# Capture state for undo BEFORE modifications
		params = {}
		self.common.capture_and_push_undo_state(
			"Score individuals", "active", params
		)

		self._calculate_scores()

		self._director.scores_active.summarize_scores()
		self._director.scores_active.print_scores()
		if self._director.common.have_reference_points():
			self._director.rivalry.assign_to_segments()
		nscores = self._director.scores_active.nscores
		nscored = self._director.scores_active.nscored_individ
		self._director.title_for_table_widget = (
			f"There are {nscores} active scores for {nscored} individuals."
		)
		# self._director.scores_active. \
		# create_scores_plot_for_tabs(self._director)
		self._director.common.create_plot_for_tabs("scores")
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.record_command_as_successfully_completed()
		return

	# ------------------------------------------------------------------------

	def _calculate_scores(self) -> None:
		dim_names = self._director.configuration_active.dim_names
		# dim_labels = self._director.configuration_active.dim_labels
		# ndim = self._director.configuration_active.ndim
		point_coords = self._director.configuration_active.point_coords
		evaluations = self._director.evaluations_active.evaluations
		nevaluators = self._director.evaluations_active.nevaluators

		score_1_name = dim_names[0]
		score_2_name = dim_names[1]

		scores_df = pd.DataFrame(
			columns=[score_1_name, score_2_name], index=evaluations.index
		)
		nscored = len(evaluations)

		range_nscored = range(nevaluators)
		for each_ind in range(len(evaluations)):
			score_1 = 0
			score_2 = 0
			for each_var in range(len(evaluations.columns)):
				score_1 += (
					evaluations.iloc[each_ind, each_var]
					* point_coords.iloc[each_var, 0]
				)
				score_2 += (
					evaluations.iloc[each_ind, each_var]
					* point_coords.iloc[each_var, 1]
				)
				# score_1 += evaluations.iloc[each_ind, each_var]
				# * point_coords.iloc[each_var, score_1_name]
				# score_2 += evaluations.iloc[each_ind, each_var]
				# * point_coords.iloc[each_var, score_2_name]
			# scores_df.loc[each_ind][0] = score_1
			# scores_df.loc[each_ind][1] = score_2
			scores_df.loc[each_ind, score_1_name] = score_1
			scores_df.loc[each_ind, score_2_name] = score_2
			# scores_df.loc[score_1_name][each_ind] = score_1
			# scores_df.loc[score_2_name][each_ind] = score_2
		scores_df = (scores_df - scores_df.mean()) / scores_df.std()
		scores = scores_df.copy()
		scores.reset_index(inplace=True)
		scores.rename(columns={"index": "Resp no"}, inplace=True)

		nscores = scores.shape[1] - 1
		nscored = scores.shape[0]
		# nscored = self._director.scores_active.scores.shape[0]
		# score_1_name = dim_names[0]
		# score_2_name = dim_names[1]

		self._director.scores_active.scores = scores
		self._director.scores_active.nscores = nscores
		self._director.scores_active.nscored_individ = nscored
		self._director.scores_active.range_nscored_individ = range_nscored
		self._director.scores_active.dim_names = dim_names
		self._director.scores_active.score_1_name = score_1_name
		self._director.scores_active.score_2_name = score_2_name
		self._director.scores_active.hor_axis_name = score_1_name
		self._director.scores_active.vert_axis_name = score_2_name
		self._director.scores_active.score_1 = scores[score_1_name]
		self._director.scores_active.score_2 = scores[score_2_name]
		self._director.scores_active.ndim = 2

		return

	# ------------------------------------------------------------------------


class SecondDimensionCommand(ASupporterGrouping):
	"""The Second dimension command identifies regions defined
	by the second dimension
	"""

	def __init__(self, director: Status, common: Spaces) -> None:
		super().__init__(director, common)

		self._director = director
		self.common = common
		self._director.command = "Second dimension"
		self._groups_to_show = ""
		rivalry = self._director.rivalry
		self._second_pcts = rivalry.second_pcts
		self._second_div = rivalry.second_div
		self._rival_a = rivalry.rival_a
		self._rival_b = rivalry.rival_b

		return

	# ------------------------------------------------------------------------

	def execute(
		self,
		common: Spaces,  # noqa: ARG002
		groups_to_show: str,
	) -> None:
		self._director.record_command_as_selected_and_in_process()
		self._director.optionally_explain_what_command_does()
		self._director.dependency_checker.detect_dependency_problems()
		self._director.current_command._second_dim_groups_to_show = (
			groups_to_show
		)

		# Track passive command with parameters for script generation
		self._director.common.push_passive_command_to_undo_stack(
			self._director.command,
			{"groups_to_show": groups_to_show}
		)

		self._director.common.create_plot_for_tabs("second")
		self._director.title_for_table_widget = "Social oriented segments"
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.record_command_as_successfully_completed()
		return

	# ------------------------------------------------------------------------


class SegmentsCommand:
	"""The Segments command identifies regions defined by the
	individual scores
	"""

	def __init__(self, director: Status, common: Spaces) -> None:
		self._director = director
		self.common = common
		self._director.command = "Segments"
		self._segs_width: int = 4
		self._segs_decimals: int = 1
		rivalry = self._director.rivalry
		self._rival_a = rivalry.rival_a
		self._rival_b = rivalry.rival_b
		return

	# ------------------------------------------------------------------------

	def execute(self, common: Spaces) -> None:  # noqa: ARG002
		width = self._segs_width
		decimals = self._segs_decimals

		self._director.record_command_as_selected_and_in_process()
		self._director.optionally_explain_what_command_does()
		self._director.dependency_checker.detect_dependency_problems()
		if not self._director.common.have_segments():
			self._director.rivalry.assign_to_segments()

		self._print_segments(width, decimals)
		self._director.title_for_table_widget = (
			f"Segments defined by contest between "
			f"{self._rival_a.name} and {self._rival_b.name}"
		)
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.set_focus_on_tab("Output")
		self._director.record_command_as_successfully_completed()
		return

	# ------------------------------------------------------------------------

	def _print_segments(self, width: int, decimals: int) -> None:
		rivalry = self._director.rivalry
		likely_pcts = rivalry.likely_pcts
		base_pcts = rivalry.base_pcts
		core_pcts = rivalry.core_pcts
		first_pcts = rivalry.first_pcts
		second_pcts = rivalry.second_pcts
		conv_pcts = rivalry.conv_pcts
		battleground_pcts = rivalry.battleground_pcts

		print("\tSegment and size")
		#
		print(
			f"Percent likely left:  {likely_pcts[1]:{width}.{decimals}f}"
			f"\tPercent likely right: {likely_pcts[2]:{width}.{decimals}f}"
		)
		print(
			f"Percent base left:    {base_pcts[1]:{width}.{decimals}f}"
			f"\tPercent base right:   {base_pcts[3]:{width}.{decimals}f}"
			f"\tPercent base neither:   {base_pcts[2]:{width}.{decimals}f}"
		)
		print(
			f"Percent core left:    {core_pcts[1]:{width}.{decimals}f}"
			f"\tPercent core right:   {core_pcts[3]:{width}.{decimals}f}"
			f"\tPercent core neither:   {core_pcts[2]:{width}.{decimals}f}"
		)
		print(
			f"Percent left only:    {first_pcts[1]:{width}.{decimals}f}"
			f"\tPercent right only:   {first_pcts[2]:{width}.{decimals}f}"
		)
		print(
			f"Percent up only:      {second_pcts[1]:{width}.{decimals}f}"
			f"\tPercent down only:    {second_pcts[2]:{width}.{decimals}f}"
		)
		print(
			f"Percent battleground:    "
			f"{battleground_pcts[1]:{width}.{decimals}f}"
			f"\tPercent settled:      "
			f"{battleground_pcts[2]:{width}.{decimals}f}"
		)
		print(
			f"Percent convertible to left:    "
			f"{conv_pcts[1]:{width}.{decimals}f}"
			f"\tPercent convertible to right:   "
			f"{conv_pcts[2]:{width}.{decimals}f}"
			f"\tPercent settled:    {conv_pcts[3]:{width}.{decimals}f}"
		)
		return
