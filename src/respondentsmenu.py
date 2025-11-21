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
		self._rival_a = rivalry.rival_a
		self._rival_b = rivalry.rival_b
		return

	# ------------------------------------------------------------------------

	def execute(self, common: Spaces, show: str) -> None:
		director = self._director
		common = director.common
		director.record_command_as_selected_and_in_process()
		director.optionally_explain_what_command_does()
		director.dependency_checker.detect_dependency_problems()
		director.current_command._base_groups_to_show = show

		# Track passive command with parameters for script generation
		common.push_passive_command_to_undo_stack(
			director.command,
			{"show": show})

		self._print_base()
		common.create_plot_for_tabs("base")
		director.create_widgets_for_output_and_log_tabs()
		director.record_command_as_successfully_completed()

		return

	# ------------------------------------------------------------------------

	def _print_base(self) -> None:
		"""Print base supporter counts for each rival."""
		director = self._director
		rivalry = director.rivalry

		# Get the title (same as table widget title)
		title = (
			f"Base supporters of {self._rival_a.name} and "
			f"{self._rival_b.name}"
		)
		print(f"\n\t{title}\n")

		# Calculate counts from percentages
		# Access base_pcts directly from rivalry (it's a pandas Series)
		# nscored comes from scores_active, not rivalry (rivalry.nscored_individ is 0)
		nscored = director.scores_active.nscored_individ
		base_pcts = rivalry.base_pcts
		base_left_count = int((base_pcts[1] / 100) * nscored)
		base_right_count = int((base_pcts[3] / 100) * nscored)

		# Print the counts
		print(
			f"\tThere are {base_left_count} base supporters of "
			f"{self._rival_a.name}"
		)
		print(
			f"\tThere are {base_right_count} base supporters of "
			f"{self._rival_b.name}"
		)

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

		return

	# ------------------------------------------------------------------------

	def execute(
		self,
		common: Spaces,  # noqa: ARG002
		show: str,
	) -> None:
		self._director.record_command_as_selected_and_in_process()
		self._director.optionally_explain_what_command_does()
		self._director.dependency_checker.detect_dependency_problems()
		self._director.current_command._battleground_groups_to_show = (show)

		# Track passive command with parameters for script generation
		self._director.common.push_passive_command_to_undo_stack(
			self._director.command,
			{"show": show})

		self._print_battleground()
		self._director.common.create_plot_for_tabs("battleground")
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.record_command_as_successfully_completed()
		return

	# ------------------------------------------------------------------------

	def _print_battleground(self) -> None:
		"""Print battleground and settled counts."""
		director = self._director
		rivalry = director.rivalry

		# Get the title (same as table widget title)
		title = "Size of battleground"
		print(f"\n\t{title}\n")

		# Calculate counts from percentages
		# Access battleground_pcts directly from rivalry (it's a pandas Series)
		# nscored comes from scores_active, not rivalry (rivalry.nscored_individ is 0)
		nscored = director.scores_active.nscored_individ
		battleground_pcts = rivalry.battleground_pcts
		battleground_count = int(
			(battleground_pcts[1] / 100) * nscored
		)
		settled_count = int((battleground_pcts[2] / 100) * nscored)

		# Print the counts
		print(
			f"\tThere are {battleground_count} in the battleground"
		)
		print(f"\tThere are {settled_count} settled")

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

		# Get command parameters and capture state
		params = common.get_command_parameters("Contest")
		common.capture_and_push_undo_state("Contest", "passive", params)

		self._director.dependency_checker.detect_dependency_problems()
		self._director.common.create_plot_for_tabs("contest")
		# self._rival_a = rivalry.rival_a
		# self._rival_b = rivalry.rival_b
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
		self._rival_a = rivalry.rival_a
		self._rival_b = rivalry.rival_b

		return

	# ------------------------------------------------------------------------

	def execute(
		self,
		common: Spaces,  # noqa: ARG002
		show: str,
	) -> None:
		self._director.record_command_as_selected_and_in_process()
		self._director.optionally_explain_what_command_does()
		self._director.dependency_checker.detect_dependency_problems()
		self._director.current_command._convertible_groups_to_show = (show)

		# Track passive command with parameters for script generation
		self._director.common.push_passive_command_to_undo_stack(
			self._director.command, {"show": show})

		self._print_convertible()
		self._director.common.create_plot_for_tabs("convertible")
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.record_command_as_successfully_completed()
		return

	# ------------------------------------------------------------------------

	def _print_convertible(self) -> None:
		"""Print convertible supporter counts for each rival."""
		director = self._director
		rivalry = director.rivalry

		# Get the title (same as table widget title)
		title = (
			f"Convertible supporters of {self._rival_a.name} and "
			f"{self._rival_b.name}"
		)
		print(f"\n\t{title}\n")

		# Calculate counts from percentages
		# nscored comes from scores_active, not rivalry
		nscored = director.scores_active.nscored_individ
		conv_pcts = rivalry.conv_pcts
		conv_left_count = int((conv_pcts[1] / 100) * nscored)
		conv_right_count = int((conv_pcts[2] / 100) * nscored)
		conv_settled_count = int((conv_pcts[3] / 100) * nscored)

		# Print the counts
		print(
			f"\tThere are {conv_left_count} convertible to "
			f"{self._rival_a.name}"
		)
		print(
			f"\tThere are {conv_right_count} convertible to "
			f"{self._rival_b.name}"
		)
		print(f"\tThere are {conv_settled_count} settled")

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
		self._core_radius = rivalry.core_radius
		self._rival_a = rivalry.rival_a
		self._rival_b = rivalry.rival_b
		return

	# ------------------------------------------------------------------------

	def execute(
		self,
		common: Spaces,  # noqa: ARG002
		show: str,
	) -> None:
		self._director.record_command_as_selected_and_in_process()
		self._director.optionally_explain_what_command_does()
		self._director.dependency_checker.detect_dependency_problems()
		self._director.current_command.core_groups_to_show = show

		# Track passive command with parameters for script generation
		self._director.common.push_passive_command_to_undo_stack(
			self._director.command, {"show": show})

		self._print_core()
		self._director.common.create_plot_for_tabs("core")
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.record_command_as_successfully_completed()
		return

	# ------------------------------------------------------------------------

	def _print_core(self) -> None:
		"""Print core supporter counts for each rival."""
		director = self._director
		rivalry = director.rivalry

		# Get the title (same as table widget title)
		title = (
			f"Core supporters of {self._rival_a.name} and "
			f"{self._rival_b.name}"
		)
		print(f"\n\t{title}\n")

		# Calculate counts from percentages
		# nscored comes from scores_active, not rivalry
		nscored = director.scores_active.nscored_individ
		core_pcts = rivalry.core_pcts
		core_left_count = int((core_pcts[1] / 100) * nscored)
		core_neither_count = int((core_pcts[2] / 100) * nscored)
		core_right_count = int((core_pcts[3] / 100) * nscored)

		# Print the counts
		print(
			f"\tThere are {core_left_count} core supporters of "
			f"{self._rival_a.name}"
		)
		print(
			f"\tThere are {core_right_count} core supporters of "
			f"{self._rival_b.name}"
		)
		print(f"\tThere are {core_neither_count} core supporters of neither")

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
		self._first_div = rivalry.first_div
		self._rival_a = rivalry.rival_a
		self._rival_b = rivalry.rival_b

		return

	# ------------------------------------------------------------------------

	def execute(self, common: Spaces, show: str) -> None:
		self._director.record_command_as_selected_and_in_process()
		self._director.optionally_explain_what_command_does()
		self._director.dependency_checker.detect_dependency_problems()
		self._director.current_command._first_dim_groups_to_show = (show)

		# Track passive command with parameters for script generation
		common.push_passive_command_to_undo_stack(
			self._director.command, {"show": show})

		self._print_first_dimension()
		common.create_plot_for_tabs("first")
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.record_command_as_successfully_completed()
		return

	# ------------------------------------------------------------------------

	def _print_first_dimension(self) -> None:
		"""Print first dimension supporter counts."""
		director = self._director
		rivalry = director.rivalry

		# Get the title (same as table widget title)
		title = "First dimension supporters"
		print(f"\n\t{title}\n")

		# Calculate counts from percentages
		# nscored comes from scores_active, not rivalry
		nscored = director.scores_active.nscored_individ
		first_pcts = rivalry.first_pcts
		first_left_count = int((first_pcts[1] / 100) * nscored)
		first_right_count = int((first_pcts[2] / 100) * nscored)

		# Print the counts
		print(
			f"\tThere are {first_left_count} on the {self._rival_a.name} side"
		)
		print(
			f"\tThere are {first_right_count} on the {self._rival_b.name} side"
		)

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

		# Get command parameters and capture state
		params = common.get_command_parameters("Joint")
		common.capture_and_push_undo_state("Joint", "passive", params)

		self._director.dependency_checker.detect_dependency_problems()
		self._director.common.create_plot_for_tabs("joint")
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
		self._rival_a = rivalry.rival_a
		self._rival_b = rivalry.rival_b
		return

	# ------------------------------------------------------------------------

	def execute(
		self,
		common: Spaces,  # noqa: ARG002
		show: str,
	) -> None:
		self._director.record_command_as_selected_and_in_process()
		self._director.optionally_explain_what_command_does()
		self._director.dependency_checker.detect_dependency_problems()
		self._director.current_command.likely_groups_to_show = show

		# Track passive command with parameters for script generation
		self._director.common.push_passive_command_to_undo_stack(
			self._director.command, {"show": show})

		self._print_likely()
		self._director.common.create_plot_for_tabs("likely")
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.record_command_as_successfully_completed()

		return

	# ------------------------------------------------------------------------

	def _print_likely(self) -> None:
		"""Print likely supporter counts for each rival."""
		director = self._director
		rivalry = director.rivalry

		# Get the title (same as table widget title)
		title = (
			f"Likely supporters of {self._rival_a.name} and "
			f"{self._rival_b.name}"
		)
		print(f"\n\t{title}\n")

		# Calculate counts from percentages
		# nscored comes from scores_active, not rivalry
		nscored = director.scores_active.nscored_individ
		likely_pcts = rivalry.likely_pcts
		likely_left_count = int((likely_pcts[1] / 100) * nscored)
		likely_right_count = int((likely_pcts[2] / 100) * nscored)

		# Print the counts
		print(
			f"\tThere are {likely_left_count} likely supporters of "
			f"{self._rival_a.name}"
		)
		print(
			f"\tThere are {likely_right_count} likely supporters of "
			f"{self._rival_b.name}"
		)

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
			self._director.configuration_active.point_names)
		return

	# ------------------------------------------------------------------------

	def execute(self, common: Spaces) -> None:

		rivalry = self._director.rivalry
		point_names = self._director.configuration_active.point_names
		point_labels = self._director.configuration_active.point_labels

		self._director.record_command_as_selected_and_in_process()
		self._director.optionally_explain_what_command_does()
		self._director.dependency_checker.detect_dependency_problems()
		self._director.configuration_active.print_the_configuration()
		params = self.common.get_command_parameters("Reference points")
		contest: list = params["contest"]
		new_rival_a_index = point_names.index(contest[0])
		new_rival_b_index = point_names.index(contest[1])
		self.common.capture_and_push_undo_state(
			"Reference points", "active", params)

		# NOW modify the rivalry state with the new reference points
		rivalry.rival_a.index = new_rival_a_index
		rivalry.rival_b.index = new_rival_b_index
		rivalry.rival_a.name = point_names[new_rival_a_index]
		rivalry.rival_b.name = point_names[new_rival_b_index]
		rivalry.rival_a.label = point_labels[new_rival_a_index]
		rivalry.rival_b.label = point_labels[new_rival_b_index]
		rivalry.create_or_revise_rivalry_attributes(self._director, common)
		rivalry.use_reference_points_to_define_segments(self._director)
		rivalry.assign_to_segments()

		self._print_reference_points()
		self._director.common.create_plot_for_tabs("configuration")
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.record_command_as_successfully_completed()
		return

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
		"""The Sample designer command is used to create a sample design.

		DEPRECATED: This command is deprecated and may be removed in a future
		version. The Uncertainty command now handles sample design internally.
		"""
		self._director = director
		self.common = common
		self._director.command = "Sample designer"
		self._director.uncertainty_active.universe_size = 0
		self._director.uncertainty_active.probability_of_inclusion = 0
		self._director.uncertainty_active.nrepetitions = 0
		self._director.uncertainty_active.sample_design = pd.DataFrame(
			columns=["RespId", "Repetition", "Selected"])
		self._director.uncertainty_active.sample_design_frequencies = (
			pd.DataFrame(columns=["Repetition", "Selected", "Count"]))
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
		params = self.common.get_command_parameters("Sample designer")
		probability_of_inclusion: int = params["probability_of_inclusion"]
		nrepetitions: int = params["nrepetitions"]
		universe_size = self._director.evaluations_active.nevaluators
		self._director.uncertainty_active.universe_size = universe_size
		self._director.uncertainty_active.probability_of_inclusion = probability_of_inclusion
		self._director.uncertainty_active.nrepetitions = nrepetitions
		self.common.capture_and_push_undo_state(
			"Sample designer", "active", params)

		self._create_sample_design()

		universe_size = self._director.uncertainty_active.universe_size
		probability_of_inclusion = (
			self._director.uncertainty_active.probability_of_inclusion)
		self.common.create_sample_design_analysis_table()
		self._print_sample_design_analysis_results()
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.set_focus_on_tab("Output")
		self._director.record_command_as_successfully_completed()
		return

	# ------------------------------------------------------------------------

	def _create_sample_design(self) -> None:
		universe_size = self._director.uncertainty_active.universe_size
		probability_of_inclusion = (
			self._director.uncertainty_active.probability_of_inclusion)
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
		sample repetitions.

		DEPRECATED: This command is deprecated and may be removed in a future
		version. The Uncertainty command now handles sample repetitions
		internally.
		"""
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
			"universe_size": self._director.uncertainty_active.universe_size}
		self.common.capture_and_push_undo_state(
			"Sample repetitions", "active", params)

		self._create_sample_repetitions()
		universe_size = self._director.uncertainty_active.universe_size
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
			"Score individuals", "active", params)

		self._calculate_scores()

		self._director.scores_active.summarize_scores()
		self._director.scores_active.print_scores()
		if self._director.common.have_reference_points():
			self._director.rivalry.assign_to_segments()
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
		self._second_div = rivalry.second_div
		self._rival_a = rivalry.rival_a
		self._rival_b = rivalry.rival_b

		return

	# ------------------------------------------------------------------------

	def execute(
		self,
		common: Spaces,  # noqa: ARG002
		show: str,
	) -> None:
		self._director.record_command_as_selected_and_in_process()
		self._director.optionally_explain_what_command_does()
		self._director.dependency_checker.detect_dependency_problems()
		self._director.current_command._second_dim_groups_to_show = (show)

		# Track passive command with parameters for script generation
		self._director.common.push_passive_command_to_undo_stack(
			self._director.command, {"show": show})

		self._print_second_dimension()
		self._director.common.create_plot_for_tabs("second")
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.record_command_as_successfully_completed()
		return

	# ------------------------------------------------------------------------

	def _print_second_dimension(self) -> None:
		"""Print second dimension supporter counts."""
		director = self._director
		rivalry = director.rivalry

		# Get the title (same as table widget title)
		title = "Second dimension supporters"
		print(f"\n\t{title}\n")

		# Calculate counts from percentages
		# nscored comes from scores_active, not rivalry
		nscored = director.scores_active.nscored_individ
		second_pcts = rivalry.second_pcts
		second_up_count = int((second_pcts[1] / 100) * nscored)
		second_down_count = int((second_pcts[2] / 100) * nscored)

		# Print the counts
		print(f"\tThere are {second_up_count} on the upper side")
		print(f"\tThere are {second_down_count} on the lower side")

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

		# Get command parameters and capture state
		params = common.get_command_parameters("Segments")
		common.capture_and_push_undo_state("Segments", "passive", params)

		self._director.dependency_checker.detect_dependency_problems()
		if not self._director.common.have_segments():
			self._director.rivalry.assign_to_segments()

		self._print_segments(width, decimals)
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
