from __future__ import annotations
import peek  # noqa: F401
from PySide6.QtWidgets import QDialog

from typing import TYPE_CHECKING

if TYPE_CHECKING:
	from director import Status

from common import Spaces  # noqa: F401
from constants import MAXIMUM_NUMBER_OF_DIMENSIONS_FOR_PLOTTING
from dialogs import ChoseOptionDialog
from dictionaries import command_dependencies_dict
from exceptions import SpacesError

# --------------------------------------------------------------------------


class DependencyChecking:
	def __init__(self, director: Status) -> None:

		self._director = director
		self.features: list[str] = []
		self.new_feature_dict: dict[str, tuple] = {}
		self.existing_feature_dict: dict[str, tuple] = {}
		self._conflict_title: str = ""
		self._conflict_options_title: str = ""
		self._conflict_options: list[str] = []
		self.check_label_consistency: bool = False


	# ------------------------------------------------------------------------

	def detect_dependency_problems(self) -> None:
		"""Check if command's required dependencies are satisfied.

		Uses command_dependencies_dict to look up which dependencies
		a command requires, then tests each one.
		"""
		command = self._director.command
		deps = command_dependencies_dict.get(command, ())

		n_problems = 0
		for dep in deps:
			test_func = getattr(self._director.common, f"needs_{dep}")
			if test_func(command):
				n_problems += 1

		if n_problems > 0:
			raise SpacesError(None, None)


	def detect_consistency_issues_initialize_variables(self) -> None:
		"""Establishes what information is needed to determine
		whether new	data is consistent with existing data.
		"""
		# Enable label consistency checking to ensure dictionary keys match
		self.check_label_consistency = True

		configuration_active = self._director.configuration_active
		target_active = self._director.target_active
		grouped_data_active = self._director.grouped_data_active
		similarities_active = self._director.similarities_active
		evaluations_active = self._director.evaluations_active
		individuals_active = self._director.individuals_active
		correlations_active = self._director.correlations_active
		scores_active = self._director.scores_active
		have_configuration = self._director.common.have_active_configuration
		have_target = self._director.common.have_target_configuration
		have_grouped_data = self._director.common.have_grouped_data
		have_similarities = self._director.common.have_similarities
		have_correlations = self._director.common.have_correlations
		have_evaluations = self._director.common.have_evaluations
		have_individual_data = self._director.common.have_individual_data
		have_scores = self._director.common.have_scores

		self.features = [
			"Configuration",
			"Target",
			"Grouped data",
			"Similarities",
			"Evaluations",
			"Correlations",
			"Individuals",
			"Scores",
		]

		self.new_feature_dict = {
			"Configuration": (
				"Configuration",
				"Points",
				"Dimensions",
				configuration_active.npoint,
				configuration_active.point_names,
				configuration_active.point_labels,
				configuration_active.ndim,
				configuration_active.dim_names,
				configuration_active.dim_labels,
			),
			"Target": (
				"Target",
				"Points",
				"Dimensions",
				target_active.npoint,
				target_active.point_names,
				target_active.point_labels,
				target_active.ndim,
				target_active.dim_names,
				target_active.dim_labels,
			),
			"Grouped data": (
				"Grouped data",
				"Points",
				"Dimensions",
				grouped_data_active.ngroups,
				grouped_data_active.group_names,
				grouped_data_active.group_labels,
				grouped_data_active.ndim,
				grouped_data_active.dim_names,
				grouped_data_active.dim_labels,
			),
			# "Uncertainty":
			# 	("Uncertainty", None, None,
			# 	None, None, None,
			# 	None, None, None),
			"Similarities": (
				"Similarity",
				"Points",
				None,
				similarities_active.nitem if similarities_active else 0,
				similarities_active.item_names if similarities_active else [],
				similarities_active.item_labels if similarities_active else [],
				None,
				None,
				None,
			),
			"Correlations": (
				"Correlations",
				"Points",
				None,
				correlations_active.nitem if correlations_active else 0,
				correlations_active.item_names if correlations_active else [],
				correlations_active.item_labels if correlations_active else [],
				None,
				None,
				None,
			),
			"Evaluations": (
				"Evaluations",
				"Points",
				None,
				evaluations_active.nitem if evaluations_active else 0,
				evaluations_active.item_names if evaluations_active else [],
				evaluations_active.item_labels if evaluations_active else [],
				None,
				None,
				None,
			),
			"Individuals": (
				"Individuals",
				"Points",
				None,
				(individuals_active.nitem
					if individuals_active else 0),
				(individuals_active.item_names
					if individuals_active else []),
				(individuals_active.item_labels
					if individuals_active else []),
				None,
				None,
				None,
			),
			"Scores": (
				"Scores",
				None,
				"Dimensions",
				None,
				None,
				None,
				scores_active.nscores,
				scores_active.dim_names,
				scores_active.dim_labels,
			),
		}

		self.existing_feature_dict = {
			"Configuration": (
				"Configuration",
				have_configuration,
				"Points",
				"Dimensions",
				configuration_active.npoint,
				configuration_active.point_names,
				configuration_active.point_labels,
				configuration_active.ndim,
				configuration_active.dim_names,
				configuration_active.dim_labels,
				"Must match",
			),
			"Target": (
				"Target",
				have_target,
				"Points",
				"Dimensions",
				target_active.npoint,
				target_active.point_names,
				target_active.point_labels,
				target_active.ndim,
				target_active.dim_names,
				target_active.dim_labels,
				"Must match",
			),
			"Grouped data": (
				"Grouped data",
				have_grouped_data,
				"Points",
				"Dimensions",
				grouped_data_active.ngroups,
				grouped_data_active.group_names,
				grouped_data_active.group_labels,
				grouped_data_active.ndim,
				grouped_data_active.dim_names,
				grouped_data_active.dim_labels,
				"Must match",
			),
			"Similarities": (
				"Similarities",
				have_similarities,
				"Points",
				None,
				similarities_active.nitem if similarities_active else 0,
				similarities_active.item_names if similarities_active else [],
				similarities_active.item_labels if similarities_active else [],
				None,
				None,
				None,
				"No information in common",
			),
			"Evaluations": (
				"Evaluations",
				have_evaluations,
				"Points",
				None,
				evaluations_active.nitem if evaluations_active else 0,
				evaluations_active.item_names if evaluations_active else [],
				evaluations_active.item_labels if evaluations_active else [],
				None,
				None,
				None,
				"No information in common",
			),
			"Individuals": (
				"Individuals",
				have_individual_data,
				None,
				None,
				individuals_active.nitem if individuals_active else 0,
				individuals_active.item_names if individuals_active else [],
				individuals_active.item_labels if individuals_active else [],
				None,
				None,
				None,
				"No information in common",
			),
			"Correlations": (
				"Correlations",
				have_correlations,
				"Points",
				None,
				correlations_active.nitem if correlations_active else 0,
				correlations_active.item_names if correlations_active else [],
				correlations_active.item_labels if correlations_active else [],
				None,
				None,
				None,
				"No information in common",
			),
			"Scores": (
				"Scores",
				have_scores,
				None,
				"Dimensions",
				None,
				None,
				None,
				scores_active.nscores,
				scores_active.dim_names,
				scores_active.dim_labels,
				"No information in common",
			),
		}
		return

	# ------------------------------------------------------------------------

	def detect_consistency_issues(self) -> None:
		"""Determines whether new data is consistent with existing data."""

		features = self.features

		self.detect_consistency_issues_initialize_variables()
		# n_exist = self._check_if_any_features_exist()
		# if n_exist == 0:
		# 	return
		new: str = self._create_new_from_command_without_open()

		for each_feature in features:
			if self._skip_when_new_and_existing_are_same_type_of_feature(
				new, each_feature
			) and self._check_whether_feature_currently_exists(each_feature):
				new_abandoned = \
				self._when_no_information_in_common_get_user_to_resolve_conflict(
					new, each_feature
				)
				if new_abandoned:
					break  # Stop checking - new feature was abandoned

				# If existing was abandoned, skip to next feature
				if not self._check_whether_feature_currently_exists(
					each_feature):
					continue

				new_abandoned = (
					self._check_if_points_match_and_resolve_conflict(
						new, each_feature
					)
				)
				if new_abandoned:
					break  # Stop checking - new feature was abandoned

				# If existing was abandoned, skip to next feature
				if not self._check_whether_feature_currently_exists(
					each_feature):
					continue

				new_abandoned = \
					self._check_if_dimensions_match_and_resolve_conflict(
					new, each_feature
				)
				if new_abandoned:
					break  # Stop checking - new feature was abandoned
		return

	# ------------------------------------------------------------------------

	def _create_new_from_command_without_open(self) -> str:
		command = self._director.command

		if command[0:4] == "Open":
			new: str = command[5:]
			new: str = new.capitalize()
		elif command == "Create":
			new: str = "Configuration"
		elif command == "New grouped data":
			new: str = "Grouped data"
		elif command == "Line of sight":
			new: str = "Similarities"
		else:
			new: str = command
		return new

	# ------------------------------------------------------------------------

	def _check_if_any_features_exist(self) -> int:
		n_exist = 0
		for each_feature in self.features:
			if self.existing_feature_dict[each_feature][1]():
				n_exist += 1
		return n_exist

	# ------------------------------------------------------------------------

	def _check_if_dimensions_match_and_resolve_conflict(
		self, new: str, each_feature: str
	) -> bool:
		"""Check if dimensions match and resolve conflict if not.

		Returns:
			True if new feature was abandoned (stop checking),
			False otherwise (continue checking)
		"""
		existing_feature_dict: dict[str, tuple] = self.existing_feature_dict
		new_feature_dict: dict[str, tuple] = self.new_feature_dict

		new_abandoned: bool = False
		if (
			new_feature_dict[new][2] == "Dimensions"
			and existing_feature_dict[each_feature][3] == "Dimensions"
		):
			dimensions_match = self.do_dimensions_match(
				existing_feature_dict[each_feature][7],
				existing_feature_dict[each_feature][8],
				existing_feature_dict[each_feature][9],
				new_feature_dict[new][6],
				new_feature_dict[new][7],
				new_feature_dict[new][8],
			)
			if not dimensions_match:
				nothing_in_common: bool = False
				new_abandoned = self.resolve_conflict_w_existing_data(
					existing_feature_dict[each_feature][0],
					new_feature_dict[new][0],
					no_common_information=nothing_in_common,
				)
		return new_abandoned

	# ------------------------------------------------------------------------

	def _check_if_points_match_and_resolve_conflict(
		self, new: str, each_feature: str
	) -> bool:
		"""Check if points match and resolve conflict if not.

		Returns:
			True if new feature was abandoned (stop checking),
			False otherwise (continue checking)
		"""
		existing_feature_dict: dict[str, tuple] = self.existing_feature_dict
		new_feature_dict: dict[str, tuple] = self.new_feature_dict

		new_abandoned: bool = False
		if (
			new_feature_dict[new][1] == "Points"
			and existing_feature_dict[each_feature][2] == "Points"
		):
			points_match = self.do_points_match(
				existing_feature_dict[each_feature][4],
				existing_feature_dict[each_feature][5],
				existing_feature_dict[each_feature][6],
				new_feature_dict[new][3],
				new_feature_dict[new][4],
				new_feature_dict[new][5],
			)
			if not points_match:
				nothing_in_common = False
				new_abandoned = self.resolve_conflict_w_existing_data(
					existing_feature_dict[each_feature][0],
					new_feature_dict[new][0],
					no_common_information=nothing_in_common,
				)
		return new_abandoned

	# ------------------------------------------------------------------------

	def _check_that_both_features_have_both_points_and_dimensions(
		self, new: str, each_feature: str
	) -> bool:
		existing_feature_dict: dict[str, tuple] = self.existing_feature_dict
		new_feature_dict: dict[str, tuple] = self.new_feature_dict

		return (
			new_feature_dict[new][2] == "Dimensions"
			and existing_feature_dict[each_feature][3] == "Dimensions"
			and new_feature_dict[new][1] == "Points"
			and existing_feature_dict[each_feature][2] == "Points"
		)

	# ------------------------------------------------------------------------

	def _check_that_both_features_have_dimensions(
		self, new: str, each_feature: str
	) -> bool:
		existing_feature_dict: dict[str, tuple] = self.existing_feature_dict
		new_feature_dict: dict[str, tuple] = self.new_feature_dict

		return (
			new_feature_dict[new][2] == "Dimensions"
			and existing_feature_dict[each_feature][3] == "Dimensions"
		)

	# ------------------------------------------------------------------------

	def _check_that_both_features_have_points(
		self, new: str, each_feature: str
	) -> bool:
		existing_feature_dict: dict[str, tuple] = self.existing_feature_dict
		new_feature_dict: dict[str, tuple] = self.new_feature_dict

		return (
			new_feature_dict[new][1] == "Points"
			and existing_feature_dict[each_feature][2] == "Points"
		)

	# ------------------------------------------------------------------------

	def _check_whether_feature_currently_exists(
		self, each_feature: str
	) -> bool:
		return self.existing_feature_dict[each_feature][1]()

	# -------------------------------------------------------------------------

	def detect_limitations_violations_initialize_variables(self) -> None:
		self.compare_mismatch_error_title = (
			"Number of points in active configuration differs "
			"from number of stimuli in similarities."
		)
		self.compare_mismatch_error_message = (
			"Use Configuration or Similarities command to "
			"establish a configuration or similarities."
		)
		self.compare_too_many_dimensions_error_title = (
			"Number of dimensions is larger than two."
		)
		self.compare_too_many_dimensions_error_message = (
			"Current version of Compare command is "
			"\nlimited to two dimensions."
		)

	# ------------------------------------------------------------------------

	def detect_limitations_violations(self) -> None:
		self.detect_limitations_violations_initialize_variables()

		if self._director.command == "Alike":
			if (
				self._director.similarities_active.nreferent
				!= self._director.configuration_active.npoint
			):
				raise SpacesError(
					self.compare_mismatch_error_title,
					self.compare_mismatch_error_message,
				)

		elif self._director.command == "Compare":
			ndim = self._director.configuration_active.ndim
			if ndim > MAXIMUM_NUMBER_OF_DIMENSIONS_FOR_PLOTTING:
				raise SpacesError(
					self.compare_too_many_dimensions_error_title,
					self.compare_too_many_dimensions_error_message,
				)

		return

	# ------------------------------------------------------------------------

	def do_dimensions_match(
		self,
		existing_ndim: int,
		existing_dim_names: list[str],
		existing_dim_labels: list[str],
		new_ndim: int,
		new_dim_names: list[str],
		new_dim_labels: list[str],
	) -> bool:
		dimensions_match: bool = False

		if self.check_label_consistency:
			# Fall back to name matching if either label list is empty
			if not existing_dim_labels or not new_dim_labels:
				if existing_ndim == \
					new_ndim and existing_dim_names == new_dim_names:
					dimensions_match = True
				else:
					dimensions_match = False
				return dimensions_match

			if existing_dim_labels == new_dim_labels:
				dimensions_match = True
			else:
				dimensions_match = False
			return dimensions_match

		if existing_ndim == new_ndim and existing_dim_names == new_dim_names:
			dimensions_match = True
		return dimensions_match

	# ------------------------------------------------------------------------

	def do_points_match(
		self,
		existing_npoint: int,
		existing_point_names: list[str],
		existing_point_labels: list[str],
		new_npoint: int,
		new_point_names: list[str],
		new_point_labels: list[str],
	) -> bool:
		points_match: bool = False

		if self.check_label_consistency:
			# Fall back to name matching if either label list is empty
			if not existing_point_labels or not new_point_labels:
				if (
					existing_npoint == new_npoint
					and existing_point_names == new_point_names
				):
					points_match = True
				else:
					points_match = False
				return points_match

			if existing_point_labels == new_point_labels:
				points_match: bool = True
			else:
				points_match: bool = False
			return points_match

		if (
			existing_npoint == new_npoint
			and existing_point_names == new_point_names
		):
			points_match: bool = True
		return points_match

	# ------------------------------------------------------------------------

	def resolve_conflict_w_existing_data(
		self, existing: str, new: str, *, no_common_information: bool
	) -> bool:
		"""Resolve conflict between existing and new features.

		Returns:
			True if NEW feature was abandoned (stop checking),
			False if existing was abandoned or conflict ignored
				(continue checking)
		"""
		existing_abandoned: bool = False
		abandon_dict = {
			"Configuration": self._director.abandon_configuration,
			"Target": self._director.abandon_target,
			"Grouped data": self._director.abandon_grouped_data,
			"Similarities": self._director.abandon_similarities,
			"Correlations": self._director.abandon_correlations,
			"Evaluations": self._director.abandon_evaluations,
			"Individuals": self._director.abandon_individual_data,
			"Scores": self._director.abandon_scores,
		}
		feature_name_map = {
			"Configuration": "configuration",
			"Target": "target",
			"Grouped data": "grouped_data",
			"Similarities": "similarities",
			"Correlations": "correlations",
			"Evaluations": "evaluations",
			"Individuals": "individuals",
			"Scores": "scores",
		}
		if no_common_information:
			self._conflict_title: str = "Potential consistency problem"
			self._conflict_options_title: str = "How to proceed"
			self._conflict_options: list[str] = [
				f"Abandon active {existing.lower()}, \
				\ncontinue establishing {new.lower()}",
				f"Abandon opening {new.lower()}, \
				\nkeep active {existing.lower()}",
				"Ignore potential of inconsistency",
			]
		else:
			self._conflict_title: str = f"{existing} does not match"
			self._conflict_options_title: str = "How to proceed"
			self._conflict_options: list[str] = [
				f"Abandon active {existing.lower()}, \
				\ncontinue establishing {new.lower()}",
				f"Abandon opening {new.lower()}, \
				\nkeep active {existing.lower()}",
			]
		dialog = ChoseOptionDialog(
			self._conflict_title,
			self._conflict_options_title,
			self._conflict_options,
		)
		result = dialog.exec()
		if result == QDialog.Accepted:
			selected_option = dialog.selected_option  # + 1

			match selected_option:
				case 0:
					# Abandon existing - continue checking other features
					abandon_dict[existing]()
					existing_abandoned: bool = True
					return False  # Continue checking
				case 1:
					# Abandon new - stop checking
					feature_name = feature_name_map.get(
						new, new.lower().replace(" ", "_")
					)
					restored = (
						self._director.common.event_driven_optional_restoration(
							feature_name
						)
					)
					# Raise appropriate error based on what happened
					if restored:
						# Feature was restored - stop checking
						return True  # Stop checking
					# else:
					# Feature was cleared - inform user it's abandoned
					abandon_needed_error_title: str = (
						self._director.command
					)
					abandon_needed_error_message: str = \
						f"{new} has been abandoned"
					raise SpacesError(
						abandon_needed_error_title,
						abandon_needed_error_message,
					)
				case 2:
					# Ignore - continue checking
					return False  # Continue checking
				case _:
					# Unexpected case - ask user to restore or clear new
					feature_name = feature_name_map.get(
						new, new.lower().replace(" ", "_")
					)
					restored = (
						self._director.common.event_driven_optional_restoration(
							feature_name
						)
					)
					# Raise appropriate error based on what happened
					if restored:
						# Feature was restored - stop checking
						return True  # Stop checking
					#else:
					# Feature was cleared - inform user
					inconsistency_error_title: str = \
						f"{new} has been abandoned"
					inconsistency_error_message: str = (
						f"Inconsistency between {new.lower()} "
						f"and {existing.lower()} was not resolved"
					)
					raise SpacesError(
						inconsistency_error_title,
						inconsistency_error_message
					)
		else:
			# Dialog cancelled or failed - ask user to restore or clear new
			feature_name = feature_name_map.get(
				new, new.lower().replace(" ", "_")
			)
			restored = (
				self._director.common.event_driven_optional_restoration(
					feature_name
				)
			)
			# Raise appropriate error based on what happened
			if restored:
				# Feature was restored - don't say "abandoned"
				# Just stop command execution silently
				return existing_abandoned
			# else:
			# Feature was cleared - inform user
			inconsistency_unresolved_error_title: str = \
				f"{new} has been abandoned"
			inconsistency_unresolved_error_message: str = (
				f"Inconsistency between {new.lower()} "
				f"and {existing.lower()} was not resolved"
			)
			raise SpacesError(
				inconsistency_unresolved_error_title,
				inconsistency_unresolved_error_message,
			)

		return existing_abandoned

	# ------------------------------------------------------------------------

	def _skip_when_new_and_existing_are_same_type_of_feature(
		self, new: str, each_feature: str
	) -> bool:
		return new != self.existing_feature_dict[each_feature][0]

	# ------------------------------------------------------------------------

	def _when_no_information_in_common_get_user_to_resolve_conflict(
		self, new: str, each_feature: str
	) -> bool:
		"""Check if features have nothing in common and resolve conflict.

		Returns:
			True if new feature was abandoned (stop checking),
			False otherwise (continue checking)
		"""
		existing_feature_dict: dict[str, tuple] = self.existing_feature_dict
		new_feature_dict: dict[str, tuple] = self.new_feature_dict

		new_abandoned: bool = False
		feature_group_1: list[str] = \
			["Similarities", "Correlations", "Evaluations"]
		feature_group_2: list[str] = ["Grouped data", "Scores"]

		if existing_feature_dict[each_feature][
			10
		] == "No information in common" and (
			(
				new_feature_dict[new][0] in feature_group_1
				and existing_feature_dict[each_feature][0] in feature_group_2
			)
			or (
				new_feature_dict[new][0] in feature_group_2
				and existing_feature_dict[each_feature][0] in feature_group_1
			)
		):
			nothing_in_common: bool = True
			new_abandoned: bool = self.resolve_conflict_w_existing_data(
				existing_feature_dict[each_feature][0],
				new_feature_dict[new][0],
				no_common_information=nothing_in_common,
			)
		return new_abandoned

