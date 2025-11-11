from __future__ import annotations

from typing import TYPE_CHECKING, Any
import copy
import pandas as pd

if TYPE_CHECKING:
	from director import Status

# ----------------------------------------------------------------------------


def _handle_basic_types_and_memo(
	obj: object, memo: dict
) -> tuple[bool, object] | None:
	"""Handle basic types and check memo for circular references.

	Returns:
		Tuple of (found, value) if handled, None otherwise
	"""
	# Handle None and immutable basic types
	if obj is None or isinstance(obj, (int, float, str, bool)):
		return (True, obj)

	# Check memo to avoid infinite recursion
	obj_id = id(obj)
	if obj_id in memo:
		return (True, memo[obj_id])

	return None


# ----------------------------------------------------------------------------


def _handle_pandas_objects(obj: object, memo: dict) -> object | None:
	"""Handle pandas DataFrames and Series.

	Returns:
		Copied pandas object if handled, None otherwise
	"""
	if isinstance(obj, pd.DataFrame):
		result = obj.copy()
		memo[id(obj)] = result
		return result

	if isinstance(obj, pd.Series):
		result = obj.copy()
		memo[id(obj)] = result
		return result

	return None


# ----------------------------------------------------------------------------


def _handle_container_types(
	obj: object, memo: dict, copier_func: object
) -> object | None:
	"""Handle list, dict, and tuple container types.

	Returns:
		Copied container if handled, None otherwise
	"""
	obj_id = id(obj)

	# Handle lists
	if isinstance(obj, list):
		result = []
		memo[obj_id] = result
		result.extend(copier_func(item, memo) for item in obj)
		return result

	# Handle dicts
	if isinstance(obj, dict):
		result = {}
		memo[obj_id] = result
		for key, value in obj.items():
			result[key] = copier_func(value, memo)
		return result

	# Handle tuples
	if isinstance(obj, tuple):
		return tuple(copier_func(item, memo) for item in obj)

	return None


# ----------------------------------------------------------------------------


def _handle_custom_objects(
	obj: object, memo: dict, copier_func: object
) -> object:
	"""Handle custom objects with __dict__.

	Returns:
		Copied custom object, or standard deepcopy if special handling fails
	"""
	# Handle objects with __dict__ (custom classes)
	if not hasattr(obj, "__dict__"):
		return copy.deepcopy(obj, memo)

	# Create new instance without calling __init__
	try:
		new_obj = object.__new__(type(obj))
	except TypeError:
		# If object.__new__() doesn't work, use standard deepcopy
		return copy.deepcopy(obj, memo)

	memo[id(obj)] = new_obj

	# Copy all attributes, handling _director specially
	for attr_name, attr_value in obj.__dict__.items():
		if attr_name == "_director":
			# Set _director to None instead of copying
			setattr(new_obj, attr_name, None)
		else:
			# Recursively copy other attributes
			copied_value = copier_func(attr_value, memo)
			setattr(new_obj, attr_name, copied_value)

	return new_obj


# ----------------------------------------------------------------------------


def _copy_feature_state[T](feature_obj: T) -> T:
	"""Create a deep copy of a feature object, excluding _director.

	Feature objects contain a _director reference to the Status (QMainWindow)
	instance, which cannot be pickled/deepcopied. This function recursively
	handles _director references at all nesting levels.

	Args:
		feature_obj: The feature object to copy

	Returns:
		A new instance with all attributes copied except _director
	"""

	def _deepcopy_with_director_handling(obj: object, memo: dict) -> object:
		"""Custom deepcopy that handles _director at any nesting level."""

		# Handle basic types and memo check
		basic_result = _handle_basic_types_and_memo(obj, memo)
		if basic_result is not None:
			return basic_result[1] if basic_result[0] else None

		# Handle pandas objects
		pandas_result = _handle_pandas_objects(obj, memo)
		if pandas_result is not None:
			return pandas_result

		# Handle container types
		container_result = _handle_container_types(
			obj, memo, _deepcopy_with_director_handling
		)
		if container_result is not None:
			return container_result

		# Handle custom objects
		return _handle_custom_objects(
			obj, memo, _deepcopy_with_director_handling
		)

	# Start the recursive copy with empty memo
	return _deepcopy_with_director_handling(feature_obj, {})

# ----------------------------------------------------------------------------


class CommandState:
	"""Captures application state before command execution for undo support.

	This class stores both the command metadata (name, type, parameters)
	and the application state snapshot (data, configuration, plot
	parameters) needed to support undo functionality.

	The class distinguishes between three types of commands:
	- active: Modify state and need full snapshots for undo
	- passive: Only query/display, need minimal tracking
	- script: Meta-commands for script operations, excluded from
		script generation

	Attributes:
		command_name: Name of the command (e.g., "Rotate", "Center")
		command_type: One of "active", "passive", or "script"
			(from command_dict)
		command_params: Parameters used when command was executed
		timestamp: When the command was executed
		state_snapshot: Dictionary containing all captured state data

	State Snapshot Structure (for active commands):
		{
			"configuration": {
				"point_coords": DataFrame,
				"point_names": list[str],
				"point_labels": list[str],
				"dim_names": list[str],
				"dim_labels": list[str],
				"ndim": int,
				"npoint": int,
				# ... other configuration attributes
			},
			"correlations": {
				"correlations": list[list[float]],  # Raw lower triangular
				"item_names": list[str],
				"item_labels": list[str],
				"nitem": int,
				"nreferent": int,
				"ncorrelations": int,
				# Derived structures regenerated via duplicate_correlations()
			},
			"similarities": {
				"similarities": list[list[float]],  # Raw lower triangular
				"item_names": list[str],
				"item_labels": list[str],
				"value_type": str,
				"nitem": int,
				"nsimilarities": int,
				# Derived structures regenerated via duplicate_similarities()
			},
			"evaluations": {
				"evaluations": DataFrame,
				"item_names": list[str],
				"item_labels": list[str],
				# ... other evaluation attributes
			},
			"individuals": {
				"ind_vars": DataFrame,
				"var_names": list[str],
				"n_individ": int,
				# ... other individual attributes
			},
			"scores": {
				"scores": DataFrame,
				"dim_names": list[str],
				"dim_labels": list[str],
				"nscored_individ": int,
				# ... other score attributes
			},
			"grouped_data": {
				"group_coords": DataFrame,
				"group_names": list[str],
				"group_labels": list[str],
				"grouping_var": str,
				# ... other grouped data attributes
			},
			"target": {
				"point_coords": DataFrame,
				"point_names": list[str],
				"point_labels": list[str],
				"ndim": int,
				"npoint": int,
				# ... other target attributes
			},
			"uncertainty": {
				"universe_size": int,
				"nrepetitions": int,
				"probability_of_inclusion": float,
				"sample_design": DataFrame,
				"sample_design_frequencies": DataFrame,
				"sample_repetitions": DataFrame,
				"solutions_stress_df": DataFrame,
				"sample_solutions": DataFrame,
				"ndim": int,
				"npoint": int,
				"npoints": int,
				"nsolutions": int,
				"dim_names": list[str],
				"dim_labels": list[str],
				"point_names": list[str],
				"point_labels": list[str],
			},
			"settings": {
				"hor_dim": int,
				"vert_dim": int,
				"presentation_layer": str,
				# ... other settings
			},
			"plot_params": {
				# Plot configuration parameters
			}
		}
	"""

	def __init__(
		self,
		command_name: str,
		command_type: str,
		command_params: dict[str, Any] | None = None,
	) -> None:
		"""Initialize a CommandState instance.

		Args:
			command_name: Name of the command being executed
			command_type: One of "active", "passive", or "script"
			command_params: Parameters passed to the command (optional)
		"""
		self.command_name: str = command_name
		self.command_type: str = command_type
		self.command_params: dict[str, Any] = command_params or {}
		self.timestamp: str = ""  # Will be set when state is captured
		self.state_snapshot: dict[str, Any] = {}

	# ------------------------------------------------------------------------

	def capture_configuration_state(self, director: Status) -> None:
		"""Capture the current configuration feature state.

		Stores a deep copy of the entire configuration_active object to
		prevent mutations from affecting the captured state.

		Args:
			director: The director instance containing configuration_active
		"""
		# Use special copy that excludes unpickleable _director reference
		self.state_snapshot["configuration"] = _copy_feature_state(
			director.configuration_active
		)

	# ------------------------------------------------------------------------

	def capture_correlations_state(self, director: Status) -> None:
		"""Capture the current correlations feature state.

		Stores a deep copy of the entire correlations_active object to
		prevent mutations from affecting the captured state.

		Args:
			director: The director instance containing correlations_active
		"""
		# Use special copy that excludes unpickleable _director reference
		self.state_snapshot["correlations"] = _copy_feature_state(
			director.correlations_active
		)

	# ------------------------------------------------------------------------

	def capture_similarities_state(self, director: Status) -> None:
		"""Capture the current similarities feature state.

		Stores a deep copy of the entire similarities_active object to
		prevent mutations from affecting the captured state.

		Args:
			director: The director instance containing similarities_active
		"""
		# Use special copy that excludes unpickleable _director reference
		self.state_snapshot["similarities"] = _copy_feature_state(
			director.similarities_active
		)

	# ------------------------------------------------------------------------

	def capture_evaluations_state(self, director: Status) -> None:
		"""Capture the current evaluations feature state.

		Stores a deep copy of the entire evaluations_active object to
		prevent mutations from affecting the captured state.

		Args:
			director: The director instance containing evaluations_active
		"""
		# Use special copy that excludes unpickleable _director reference
		self.state_snapshot["evaluations"] = _copy_feature_state(
			director.evaluations_active
		)

	# ------------------------------------------------------------------------

	def capture_individuals_state(self, director: Status) -> None:
		"""Capture the current individuals feature state.

		Args:
			director: The director instance containing individuals_active
		"""
		inds = director.individuals_active

		self.state_snapshot["individuals"] = {
			"ind_vars": inds.ind_vars.copy()
			if not inds.ind_vars.empty
			else pd.DataFrame(),
			"var_names": inds.var_names.copy(),
			"n_individ": inds.n_individ,
			"nvar": inds.nvar,
		}

	# ------------------------------------------------------------------------

	def capture_scores_state(self, director: Status) -> None:
		"""Capture the current scores feature state.

		Stores a deep copy of the entire scores_active object to prevent
		mutations from affecting the captured state.

		Args:
			director: The director instance containing scores_active
		"""
		# Use special copy that excludes unpickleable _director reference
		self.state_snapshot["scores"] = _copy_feature_state(
			director.scores_active
		)

	# ------------------------------------------------------------------------

	def capture_grouped_data_state(self, director: Status) -> None:
		"""Capture the current grouped data feature state.

		Stores a deep copy of the entire grouped_data_active object to
		prevent mutations from affecting the captured state.

		Args:
			director: The director instance containing grouped_data_active
		"""
		# Use special copy that excludes unpickleable _director reference
		self.state_snapshot["grouped_data"] = _copy_feature_state(
			director.grouped_data_active
		)

	# ------------------------------------------------------------------------

	def capture_target_state(self, director: Status) -> None:
		"""Capture the current target feature state.

		Stores a reference to the entire target_active object.
		When restored, the object reference is reassigned, eliminating
		the need for manual attribute lists.

		Args:
			director: The director instance containing target_active
		"""
		# Use special copy that excludes unpickleable _director reference
		self.state_snapshot["target"] = _copy_feature_state(
			director.target_active
		)

	# ------------------------------------------------------------------------

	def capture_uncertainty_state(self, director: Status) -> None:
		"""Capture the current uncertainty feature state.

		Args:
			director: The director instance containing uncertainty_active
		"""
		uncertainty = director.uncertainty_active

		self.state_snapshot["uncertainty"] = {
			"universe_size": uncertainty.universe_size,
			"nrepetitions": uncertainty.nrepetitions,
			"probability_of_inclusion": uncertainty.probability_of_inclusion,
			"sample_design": uncertainty.sample_design.copy()
			if not uncertainty.sample_design.empty
			else pd.DataFrame(),
			"sample_design_frequencies": (
				uncertainty.sample_design_frequencies.copy()
				if not uncertainty.sample_design_frequencies.empty
				else pd.DataFrame()
			),
			"sample_repetitions": uncertainty.sample_repetitions.copy()
			if not uncertainty.sample_repetitions.empty
			else pd.DataFrame(),
			"solutions_stress_df": uncertainty.solutions_stress_df.copy()
			if not uncertainty.solutions_stress_df.empty
			else pd.DataFrame(),
			"sample_solutions": uncertainty.sample_solutions.copy()
			if not uncertainty.sample_solutions.empty
			else pd.DataFrame(),
			"ndim": uncertainty.ndim,
			"npoint": uncertainty.npoint,
			"npoints": uncertainty.npoints,
			"nsolutions": uncertainty.nsolutions,
			"dim_names": uncertainty.dim_names.copy(),
			"dim_labels": uncertainty.dim_labels.copy(),
			"point_names": uncertainty.point_names.copy(),
			"point_labels": uncertainty.point_labels.copy(),
		}

	# ------------------------------------------------------------------------

	def capture_rivalry_state(self, director: Status) -> None:
		"""Capture the current rivalry state.

		Stores a deep copy of the entire rivalry object to prevent
		mutations from affecting the captured state.

		Args:
			director: The director instance containing rivalry
		"""
		# Use special copy that excludes unpickleable _director reference
		self.state_snapshot["rivalry"] = _copy_feature_state(
			director.rivalry
		)

	# ------------------------------------------------------------------------

	def capture_settings_state(self, director: Status) -> None:
		"""Capture current application settings.

		Args:
			director: The director instance containing settings
		"""
		common = director.common

		self.state_snapshot["settings"] = {
			"hor_dim": common.hor_dim,
			"vert_dim": common.vert_dim,
			"presentation_layer": common.presentation_layer,
			# Add other settings as needed
		}

	# ------------------------------------------------------------------------

	def restore_configuration_state(self, director: Status) -> None:
		"""Restore configuration feature state from snapshot.

		Restores by reassigning the entire configuration_active object.
		No attribute copying or regeneration needed.

		Args:
			director: The director instance to restore state into
		"""
		if "configuration" not in self.state_snapshot:
			return

		# Restore the entire object
		director.configuration_active = self.state_snapshot["configuration"]
		# Reconnect the director reference (was set to None during copy)
		director.configuration_active._director = director

	# ------------------------------------------------------------------------

	def restore_correlations_state(self, director: Status) -> None:
		"""Restore correlations feature state from snapshot.

		Restores by reassigning the entire correlations_active object.
		No attribute copying or regeneration needed.

		Args:
			director: The director instance to restore state into
		"""
		if "correlations" not in self.state_snapshot:
			return

		# Restore the entire object
		director.correlations_active = self.state_snapshot["correlations"]
		# Reconnect the director reference (was set to None during copy)
		director.correlations_active._director = director

	# ------------------------------------------------------------------------

	def restore_similarities_state(self, director: Status) -> None:
		"""Restore similarities feature state from snapshot.

		Restores by reassigning the entire similarities_active object.
		If similarities weren't captured (didn't exist in old state),
		explicitly clears current similarities.

		Args:
			director: The director instance to restore state into
		"""
		if "similarities" not in self.state_snapshot:
			# Similarities didn't exist in the old state, so clear current
			director.similarities_active = None
			return

		# Restore the entire object
		director.similarities_active = self.state_snapshot["similarities"]
		# Reconnect the director reference (was set to None during copy)
		director.similarities_active._director = director

	# ------------------------------------------------------------------------

	def restore_evaluations_state(self, director: Status) -> None:
		"""Restore evaluations feature state from snapshot.

		Restores by reassigning the captured object reference back to
		evaluations_active.

		Args:
			director: The director instance to restore state into
		"""
		if "evaluations" not in self.state_snapshot:
			return

		# Restore the entire object
		director.evaluations_active = self.state_snapshot["evaluations"]
		# Reconnect the director reference (was set to None during copy)
		director.evaluations_active._director = director

	# ------------------------------------------------------------------------

	def restore_individuals_state(self, director: Status) -> None:
		"""Restore individuals feature state from snapshot.

		Restores individuals data from the captured dictionary snapshot
		into the individuals_active object.

		Args:
			director: The director instance to restore state into
		"""
		if "individuals" not in self.state_snapshot:
			return

		inds_snapshot: dict[str, Any] = self.state_snapshot["individuals"]
		inds = director.individuals_active

		# Restore all attributes
		inds.ind_vars = inds_snapshot["ind_vars"].copy()
		inds.var_names = inds_snapshot["var_names"].copy()
		inds.n_individ = inds_snapshot["n_individ"]
		inds.nvar = inds_snapshot["nvar"]

	# ------------------------------------------------------------------------

	def restore_scores_state(self, director: Status) -> None:
		"""Restore scores feature state from snapshot.

		Restores by reassigning the entire scores_active object.

		Args:
			director: The director instance to restore state into
		"""
		if "scores" not in self.state_snapshot:
			return

		# Restore the entire object
		director.scores_active = self.state_snapshot["scores"]
		# Reconnect the director reference (was set to None during copy)
		director.scores_active._director = director

	# ------------------------------------------------------------------------

	def restore_grouped_data_state(self, director: Status) -> None:
		"""Restore grouped data feature state from snapshot.

		Restores by reassigning the entire grouped_data_active object.
		No attribute copying or regeneration needed.

		Args:
			director: The director instance to restore state into
		"""
		if "grouped_data" not in self.state_snapshot:
			return

		# Restore the entire object
		director.grouped_data_active = self.state_snapshot["grouped_data"]
		# Reconnect the director reference (was set to None during copy)
		director.grouped_data_active._director = director

	# ------------------------------------------------------------------------

	def restore_target_state(self, director: Status) -> None:
		"""Restore target feature state from snapshot.

		Restores by reassigning the entire target_active object.
		No attribute copying or regeneration needed.

		Args:
			director: The director instance to restore state into
		"""
		if "target" not in self.state_snapshot:
			return

		# Restore the entire object
		director.target_active = self.state_snapshot["target"]
		# Reconnect the director reference (was set to None during copy)
		director.target_active._director = director

	# ------------------------------------------------------------------------

	def restore_uncertainty_state(self, director: Status) -> None:
		"""Restore uncertainty feature state from snapshot.

		Restores uncertainty data from the captured dictionary snapshot
		into the uncertainty_active object.

		Args:
			director: The director instance to restore state into
		"""
		if "uncertainty" not in self.state_snapshot:
			return

		unc_snapshot: dict[str, Any] = self.state_snapshot["uncertainty"]
		uncertainty = director.uncertainty_active

		# Restore scalar attributes
		uncertainty.universe_size = unc_snapshot["universe_size"]
		uncertainty.nrepetitions = unc_snapshot["nrepetitions"]
		uncertainty.probability_of_inclusion = (
			unc_snapshot["probability_of_inclusion"]
		)
		uncertainty.ndim = unc_snapshot["ndim"]
		uncertainty.npoint = unc_snapshot["npoint"]
		uncertainty.npoints = unc_snapshot["npoints"]
		uncertainty.nsolutions = unc_snapshot["nsolutions"]

		# Restore dataframes
		uncertainty.sample_design = unc_snapshot["sample_design"].copy()
		uncertainty.sample_design_frequencies = (
			unc_snapshot["sample_design_frequencies"].copy()
		)
		uncertainty.sample_repetitions = (
			unc_snapshot["sample_repetitions"].copy()
		)
		uncertainty.solutions_stress_df = (
			unc_snapshot["solutions_stress_df"].copy()
		)
		uncertainty.sample_solutions = unc_snapshot["sample_solutions"].copy()

		# Restore arrays
		uncertainty.dim_names = unc_snapshot["dim_names"].copy()
		uncertainty.dim_labels = unc_snapshot["dim_labels"].copy()
		uncertainty.point_names = unc_snapshot["point_names"].copy()
		uncertainty.point_labels = unc_snapshot["point_labels"].copy()

	# ------------------------------------------------------------------------

	def restore_rivalry_state(self, director: Status) -> None:
		"""Restore rivalry state from snapshot.

		Restores by reassigning the entire rivalry object.
		No attribute copying or regeneration needed.

		Args:
			director: The director instance to restore state into
		"""
		if "rivalry" not in self.state_snapshot:
			return

		# Restore the entire object
		director.rivalry = self.state_snapshot["rivalry"]
		# Reconnect the director reference (was set to None during copy)
		director.rivalry._director = director

	# ------------------------------------------------------------------------

	def restore_settings_state(self, director: Status) -> None:
		"""Restore application settings from snapshot.

		Args:
			director: The director instance to restore settings into
		"""
		if "settings" not in self.state_snapshot:
			return

		settings_snapshot = self.state_snapshot["settings"]
		common = director.common

		common.hor_dim = settings_snapshot["hor_dim"]
		common.vert_dim = settings_snapshot["vert_dim"]
		common.presentation_layer = settings_snapshot["presentation_layer"]

	# ------------------------------------------------------------------------

	def restore_all_state(self, director: Status) -> None:
		"""Restore all captured state to the director.

		This is the main method called during undo. It restores all feature
		states that were captured in the snapshot.

		Args:
			director: The director instance to restore state into
		"""
		self.restore_configuration_state(director)
		self.restore_correlations_state(director)
		self.restore_similarities_state(director)
		self.restore_evaluations_state(director)
		self.restore_individuals_state(director)
		self.restore_scores_state(director)
		self.restore_grouped_data_state(director)
		self.restore_target_state(director)
		self.restore_uncertainty_state(director)
		self.restore_rivalry_state(director)
		self.restore_settings_state(director)


# ----------------------------------------------------------------------------
