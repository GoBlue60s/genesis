from __future__ import annotations

from typing import TYPE_CHECKING, Any
import pandas as pd

if TYPE_CHECKING:
	from director import Status

from geometry import Point

# ----------------------------------------------------------------------------


class CommandState:
	"""Captures application state before command execution for undo support.

	This class stores both the command metadata (name, type, parameters)
	and the application state snapshot (data, configuration, plot
	parameters) needed to support undo functionality.

	The class distinguishes between three types of commands:
	- active: Modify state and need full snapshots for undo
	- passive: Only query/display, need minimal tracking
	- script: Meta-commands for script operations, excluded from script generation

	Attributes:
		command_name: Name of the command (e.g., "Rotate", "Center")
		command_type: One of "active", "passive", or "script" (from command_dict)
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
				"correlations_as_dataframe": DataFrame,
				"item_names": list[str],
				"item_labels": list[str],
				"nitem": int,
				# ... other correlation attributes
			},
			"similarities": {
				"similarities_as_dataframe": DataFrame,
				"item_names": list[str],
				"item_labels": list[str],
				"value_type": str,
				"nitem": int,
				# ... other similarity attributes
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

		Args:
			director: The director instance containing configuration_active
		"""
		config = director.configuration_active

		self.state_snapshot["configuration"] = {
			# Core data
			"point_coords": config.point_coords.copy(),
			"point_names": config.point_names.copy(),
			"point_labels": config.point_labels.copy(),
			"dim_names": config.dim_names.copy(),
			"dim_labels": config.dim_labels.copy(),
			# Dimensions
			"ndim": config.ndim,
			"npoint": config.npoint,
			"range_dims": config.range_dims,
			"range_points": config.range_points,
			# Axis names
			"hor_axis_name": config.hor_axis_name,
			"vert_axis_name": config.vert_axis_name,
			# Computed data (distances, ranks, etc.)
			"distances_as_dataframe": config.distances_as_dataframe.copy()
			if not config.distances_as_dataframe.empty
			else pd.DataFrame(),
			"ranked_distances_as_dataframe": (
				config.ranked_distances_as_dataframe.copy()
				if not config.ranked_distances_as_dataframe.empty
				else pd.DataFrame()
			),
		}

	# ------------------------------------------------------------------------

	def capture_correlations_state(self, director: Status) -> None:
		"""Capture the current correlations feature state.

		Args:
			director: The director instance containing correlations_active
		"""
		corr = director.correlations_active

		self.state_snapshot["correlations"] = {
			"correlations_as_dataframe": corr.correlations_as_dataframe.copy()
			if not corr.correlations_as_dataframe.empty
			else pd.DataFrame(),
			"item_names": corr.item_names.copy(),
			"item_labels": corr.item_labels.copy(),
			"nitem": corr.nitem,
			"ncorrelations": corr.ncorrelations,
		}

	# ------------------------------------------------------------------------

	def capture_similarities_state(self, director: Status) -> None:
		"""Capture the current similarities feature state.

		Captures similarities_active, similarities_original, and
		similarities_last to ensure complete restoration on undo.

		Args:
			director: The director instance containing similarities_active
		"""
		sims = director.similarities_active
		sims_orig = director.similarities_original
		sims_last = director.similarities_last

		self.state_snapshot["similarities"] = {
			"active": {
				"similarities": [row.copy() for row in sims.similarities]
				if sims.similarities
				else [],
				"similarities_as_dataframe": (
					sims.similarities_as_dataframe.copy()
					if not sims.similarities_as_dataframe.empty
					else pd.DataFrame()
				),
				"item_names": sims.item_names.copy(),
				"item_labels": sims.item_labels.copy(),
				"value_type": sims.value_type,
				"nitem": sims.nitem,
				"nsimilarities": sims.nsimilarities,
			},
			"original": {
				"similarities": [
					row.copy() for row in sims_orig.similarities
				] if sims_orig.similarities else [],
				"similarities_as_dataframe": (
					sims_orig.similarities_as_dataframe.copy()
					if not sims_orig.similarities_as_dataframe.empty
					else pd.DataFrame()
				),
				"item_names": sims_orig.item_names.copy(),
				"item_labels": sims_orig.item_labels.copy(),
				"value_type": sims_orig.value_type,
				"nitem": sims_orig.nitem,
				"nsimilarities": sims_orig.nsimilarities,
			},
			"last": {
				"similarities": [
					row.copy() for row in sims_last.similarities
				] if sims_last.similarities else [],
				"similarities_as_dataframe": (
					sims_last.similarities_as_dataframe.copy()
					if not sims_last.similarities_as_dataframe.empty
					else pd.DataFrame()
				),
				"item_names": sims_last.item_names.copy(),
				"item_labels": sims_last.item_labels.copy(),
				"value_type": sims_last.value_type,
				"nitem": sims_last.nitem,
				"nsimilarities": sims_last.nsimilarities,
			}
		}

	# ------------------------------------------------------------------------

	def capture_evaluations_state(self, director: Status) -> None:
		"""Capture the current evaluations feature state.

		Args:
			director: The director instance containing evaluations_active
		"""
		evals = director.evaluations_active

		self.state_snapshot["evaluations"] = {
			"evaluations": evals.evaluations.copy()
			if not evals.evaluations.empty
			else pd.DataFrame(),
			"item_names": evals.item_names.copy(),
			"item_labels": evals.item_labels.copy(),
			"nitem": evals.nitem,
			"nevaluators": evals.nevaluators,
		}

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

		Args:
			director: The director instance containing scores_active
		"""
		scores = director.scores_active

		self.state_snapshot["scores"] = {
			"scores": scores.scores.copy()
			if not scores.scores.empty
			else pd.DataFrame(),
			"dim_names": scores.dim_names.copy(),
			"dim_labels": scores.dim_labels.copy(),
			"nscored_individ": scores.nscored_individ,
			"ndim": scores.ndim,
			"score_1_name": scores.score_1_name,
			"score_2_name": scores.score_2_name,
		}

	# ------------------------------------------------------------------------

	def capture_grouped_data_state(self, director: Status) -> None:
		"""Capture the current grouped data feature state.

		Args:
			director: The director instance containing grouped_data_active
		"""
		grouped = director.grouped_data_active

		self.state_snapshot["grouped_data"] = {
			"group_coords": grouped.group_coords.copy()
			if not grouped.group_coords.empty
			else pd.DataFrame(),
			"group_names": grouped.group_names.copy(),
			"group_labels": grouped.group_labels.copy(),
			"dim_names": grouped.dim_names.copy(),
			"dim_labels": grouped.dim_labels.copy(),
			"grouping_var": grouped.grouping_var,
			"ngroups": grouped.ngroups,
			"ndim": grouped.ndim,
		}

	# ------------------------------------------------------------------------

	def capture_target_state(self, director: Status) -> None:
		"""Capture the current target feature state.

		Args:
			director: The director instance containing target_active
		"""
		target = director.target_active

		self.state_snapshot["target"] = {
			"point_coords": target.point_coords.copy()
			if not target.point_coords.empty
			else pd.DataFrame(),
			"point_names": target.point_names.copy(),
			"point_labels": target.point_labels.copy(),
			"dim_names": target.dim_names.copy(),
			"dim_labels": target.dim_labels.copy(),
			"ndim": target.ndim,
			"npoint": target.npoint,
		}

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

		Args:
			director: The director instance containing rivalry
		"""
		rivalry = director.rivalry

		# Helper function to capture LineInPlot attributes
		def capture_line(line: object) -> dict[str, object] | None:
			if line is None:
				return None
			return {
				"x": line._x,
				"y": line._y,
				"cross_x": line._cross_x,
				"cross_y": line._cross_y,
				"slope": line._slope,
				"color": line._color,
				"thickness": line._thickness,
				"style": line._style,
				"direction": line._direction,
				"intercept": line._intercept,
				"case": line._case,
				"start_x": line._start.x if line._start else None,
				"start_y": line._start.y if line._start else None,
				"end_x": line._end.x if line._end else None,
				"end_y": line._end.y if line._end else None,
			}

		# Capture connector (includes length attribute)
		connector_data: dict[str, object] | None = None
		if rivalry.connector is not None:
			connector_data = capture_line(rivalry.connector)
			connector_data["length"] = rivalry.connector.length

		self.state_snapshot["rivalry"] = {
			"rival_a_index": rivalry.rival_a.index,
			"rival_a_name": rivalry.rival_a.name,
			"rival_a_label": rivalry.rival_a.label,
			"rival_a_x": rivalry.rival_a.x,
			"rival_a_y": rivalry.rival_a.y,
			"rival_b_index": rivalry.rival_b.index,
			"rival_b_name": rivalry.rival_b.name,
			"rival_b_label": rivalry.rival_b.label,
			"rival_b_x": rivalry.rival_b.x,
			"rival_b_y": rivalry.rival_b.y,
			"seg": rivalry.seg.copy()
			if not rivalry.seg.empty
			else pd.DataFrame(),
			"base_pcts": rivalry.base_pcts.copy() if rivalry.base_pcts else [],
			"battleground_pcts": (
				rivalry.battleground_pcts.copy()
				if rivalry.battleground_pcts
				else []
			),
			"conv_pcts": rivalry.conv_pcts.copy() if rivalry.conv_pcts else [],
			"core_pcts": rivalry.core_pcts.copy() if rivalry.core_pcts else [],
			"first_pcts": (
				rivalry.first_pcts.copy() if rivalry.first_pcts else []
			),
			"likely_pcts": (
				rivalry.likely_pcts.copy() if rivalry.likely_pcts else []
			),
			"second_pcts": (
				rivalry.second_pcts.copy() if rivalry.second_pcts else []
			),
			"core_radius": rivalry.core_radius,
			"bisector": capture_line(rivalry.bisector),
			"east": capture_line(rivalry.east),
			"west": capture_line(rivalry.west),
			"connector": connector_data,
			"first": capture_line(rivalry.first),
			"second": capture_line(rivalry.second),
		}

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

		Args:
			director: The director instance to restore state into
		"""
		if "configuration" not in self.state_snapshot:
			return

		config_snapshot = self.state_snapshot["configuration"]
		config = director.configuration_active

		# Restore core data
		config.point_coords = config_snapshot["point_coords"].copy()
		config.point_names = config_snapshot["point_names"].copy()
		config.point_labels = config_snapshot["point_labels"].copy()
		config.dim_names = config_snapshot["dim_names"].copy()
		config.dim_labels = config_snapshot["dim_labels"].copy()

		# Restore dimensions
		config.ndim = config_snapshot["ndim"]
		config.npoint = config_snapshot["npoint"]
		config.range_dims = config_snapshot["range_dims"]
		config.range_points = config_snapshot["range_points"]

		# Restore axis names
		config.hor_axis_name = config_snapshot["hor_axis_name"]
		config.vert_axis_name = config_snapshot["vert_axis_name"]

		# Restore computed data
		config.distances_as_dataframe = config_snapshot[
			"distances_as_dataframe"
		].copy()
		config.ranked_distances_as_dataframe = config_snapshot[
			"ranked_distances_as_dataframe"
		].copy()

	# ------------------------------------------------------------------------

	def restore_correlations_state(self, director: Status) -> None:
		"""Restore correlations feature state from snapshot.

		Args:
			director: The director instance to restore state into
		"""
		if "correlations" not in self.state_snapshot:
			return

		corr_snapshot = self.state_snapshot["correlations"]
		corr = director.correlations_active

		corr.correlations_as_dataframe = corr_snapshot[
			"correlations_as_dataframe"
		].copy()
		corr.item_names = corr_snapshot["item_names"].copy()
		corr.item_labels = corr_snapshot["item_labels"].copy()
		corr.nitem = corr_snapshot["nitem"]
		corr.ncorrelations = corr_snapshot["ncorrelations"]

	# ------------------------------------------------------------------------

	def restore_similarities_state(self, director: Status) -> None:
		"""Restore similarities feature state from snapshot.

		Restores similarities_active, similarities_original, and
		similarities_last to ensure complete restoration on undo.

		Args:
			director: The director instance to restore state into
		"""
		if "similarities" not in self.state_snapshot:
			return

		sims_snapshot = self.state_snapshot["similarities"]

		# Restore similarities_active
		sims = director.similarities_active
		sims_active_data: dict[str, Any] = sims_snapshot["active"]
		sims.similarities = [
			row.copy() for row in sims_active_data["similarities"]
		]
		sims.similarities_as_dataframe: pd.DataFrame = sims_active_data[
			"similarities_as_dataframe"
		].copy()
		sims.item_names = sims_active_data["item_names"].copy()
		sims.item_labels = sims_active_data["item_labels"].copy()
		sims.value_type = sims_active_data["value_type"]
		sims.nitem = sims_active_data["nitem"]
		sims.nsimilarities = sims_active_data["nsimilarities"]

		# Restore similarities_original
		sims_orig = director.similarities_original
		sims_orig_data = sims_snapshot["original"]
		sims_orig.similarities = [
			row.copy() for row in sims_orig_data["similarities"]
		]
		sims_orig.similarities_as_dataframe = sims_orig_data[
			"similarities_as_dataframe"
		].copy()
		sims_orig.item_names = sims_orig_data["item_names"].copy()
		sims_orig.item_labels = sims_orig_data["item_labels"].copy()
		sims_orig.value_type = sims_orig_data["value_type"]
		sims_orig.nitem = sims_orig_data["nitem"]
		sims_orig.nsimilarities = sims_orig_data["nsimilarities"]

		# Restore similarities_last
		sims_last = director.similarities_last
		sims_last_data = sims_snapshot["last"]
		sims_last.similarities = [
			row.copy() for row in sims_last_data["similarities"]
		]
		sims_last.similarities_as_dataframe = sims_last_data[
			"similarities_as_dataframe"
		].copy()
		sims_last.item_names = sims_last_data["item_names"].copy()
		sims_last.item_labels = sims_last_data["item_labels"].copy()
		sims_last.value_type = sims_last_data["value_type"]
		sims_last.nitem = sims_last_data["nitem"]
		sims_last.nsimilarities = sims_last_data["nsimilarities"]

	# ------------------------------------------------------------------------

	def restore_evaluations_state(self, director: Status) -> None:
		"""Restore evaluations feature state from snapshot.

		Args:
			director: The director instance to restore state into
		"""
		if "evaluations" not in self.state_snapshot:
			return

		evals_snapshot = self.state_snapshot["evaluations"]
		evals = director.evaluations_active

		evals.evaluations = evals_snapshot["evaluations"].copy()
		evals.item_names = evals_snapshot["item_names"].copy()
		evals.item_labels = evals_snapshot["item_labels"].copy()
		evals.nitem = evals_snapshot["nitem"]
		evals.nevaluators = evals_snapshot["nevaluators"]

	# ------------------------------------------------------------------------

	def restore_individuals_state(self, director: Status) -> None:
		"""Restore individuals feature state from snapshot.

		Args:
			director: The director instance to restore state into
		"""
		if "individuals" not in self.state_snapshot:
			return

		inds_snapshot: dict[str, Any] = self.state_snapshot["individuals"]
		inds = director.individuals_active

		inds.ind_vars = inds_snapshot["ind_vars"].copy()
		inds.var_names = inds_snapshot["var_names"].copy()
		inds.n_individ = inds_snapshot["n_individ"]
		inds.nvar = inds_snapshot["nvar"]

	# ------------------------------------------------------------------------

	def restore_scores_state(self, director: Status) -> None:
		"""Restore scores feature state from snapshot.

		Args:
			director: The director instance to restore state into
		"""
		if "scores" not in self.state_snapshot:
			return

		scores_snapshot: dict[str, Any] = self.state_snapshot["scores"]
		scores = director.scores_active

		scores.scores = scores_snapshot["scores"].copy()
		scores.dim_names = scores_snapshot["dim_names"].copy()
		scores.dim_labels = scores_snapshot["dim_labels"].copy()
		scores.nscored_individ = scores_snapshot["nscored_individ"]
		scores.ndim = scores_snapshot["ndim"]
		scores.score_1_name = scores_snapshot["score_1_name"]
		scores.score_2_name = scores_snapshot["score_2_name"]

	# ------------------------------------------------------------------------

	def restore_grouped_data_state(self, director: Status) -> None:
		"""Restore grouped data feature state from snapshot.

		Args:
			director: The director instance to restore state into
		"""
		if "grouped_data" not in self.state_snapshot:
			return

		grouped_snapshot = self.state_snapshot["grouped_data"]
		grouped = director.grouped_data_active

		grouped.group_coords = grouped_snapshot["group_coords"].copy()
		grouped.group_names = grouped_snapshot["group_names"].copy()
		grouped.group_labels = grouped_snapshot["group_labels"].copy()
		grouped.dim_names = grouped_snapshot["dim_names"].copy()
		grouped.dim_labels = grouped_snapshot["dim_labels"].copy()
		grouped.grouping_var = grouped_snapshot["grouping_var"]
		grouped.ngroups = grouped_snapshot["ngroups"]
		grouped.ndim = grouped_snapshot["ndim"]

	# ------------------------------------------------------------------------

	def restore_target_state(self, director: Status) -> None:
		"""Restore target feature state from snapshot.

		Args:
			director: The director instance to restore state into
		"""
		if "target" not in self.state_snapshot:
			return

		target_snapshot: dict[str, Any] = self.state_snapshot["target"]
		target = director.target_active

		target.point_coords = target_snapshot["point_coords"].copy()
		target.point_names = target_snapshot["point_names"].copy()
		target.point_labels = target_snapshot["point_labels"].copy()
		target.dim_names = target_snapshot["dim_names"].copy()
		target.dim_labels = target_snapshot["dim_labels"].copy()
		target.ndim = target_snapshot["ndim"]
		target.npoint = target_snapshot["npoint"]

	# ------------------------------------------------------------------------

	def restore_uncertainty_state(self, director: Status) -> None:
		"""Restore uncertainty feature state from snapshot.

		Args:
			director: The director instance to restore state into
		"""
		if "uncertainty" not in self.state_snapshot:
			return

		uncertainty_snapshot = self.state_snapshot["uncertainty"]
		uncertainty = director.uncertainty_active

		uncertainty.universe_size = uncertainty_snapshot["universe_size"]
		uncertainty.nrepetitions = uncertainty_snapshot["nrepetitions"]
		uncertainty.probability_of_inclusion = uncertainty_snapshot[
			"probability_of_inclusion"
		]
		uncertainty.sample_design = (
			uncertainty_snapshot["sample_design"].copy()
		)
		uncertainty.sample_design_frequencies = uncertainty_snapshot[
			"sample_design_frequencies"
		].copy()
		uncertainty.sample_repetitions = uncertainty_snapshot[
			"sample_repetitions"
		].copy()
		uncertainty.solutions_stress_df = uncertainty_snapshot[
			"solutions_stress_df"
		].copy()
		uncertainty.sample_solutions = uncertainty_snapshot[
			"sample_solutions"
		].copy()
		uncertainty.ndim = uncertainty_snapshot["ndim"]
		uncertainty.npoint = uncertainty_snapshot["npoint"]
		uncertainty.npoints = uncertainty_snapshot["npoints"]
		uncertainty.nsolutions = uncertainty_snapshot["nsolutions"]
		uncertainty.dim_names = uncertainty_snapshot["dim_names"].copy()
		uncertainty.dim_labels = uncertainty_snapshot["dim_labels"].copy()
		uncertainty.point_names = uncertainty_snapshot["point_names"].copy()
		uncertainty.point_labels = uncertainty_snapshot["point_labels"].copy()

	# ------------------------------------------------------------------------

	def restore_rivalry_state(self, director: Status) -> None:
		"""Restore rivalry state from snapshot.

		Args:
			director: The director instance to restore state into
		"""
		if "rivalry" not in self.state_snapshot:
			return

		rivalry_snapshot: dict[str, Any] = self.state_snapshot["rivalry"]
		rivalry = director.rivalry

		rivalry.rival_a.index = rivalry_snapshot["rival_a_index"]
		rivalry.rival_a.name = rivalry_snapshot["rival_a_name"]
		rivalry.rival_a.label = rivalry_snapshot["rival_a_label"]
		rivalry.rival_a.x = rivalry_snapshot["rival_a_x"]
		rivalry.rival_a.y = rivalry_snapshot["rival_a_y"]
		rivalry.rival_b.index = rivalry_snapshot["rival_b_index"]
		rivalry.rival_b.name = rivalry_snapshot["rival_b_name"]
		rivalry.rival_b.label = rivalry_snapshot["rival_b_label"]
		rivalry.rival_b.x = rivalry_snapshot["rival_b_x"]
		rivalry.rival_b.y = rivalry_snapshot["rival_b_y"]
		rivalry.seg = rivalry_snapshot["seg"].copy()
		rivalry.base_pcts = rivalry_snapshot["base_pcts"].copy()
		rivalry.battleground_pcts = (
			rivalry_snapshot["battleground_pcts"].copy()
		)
		rivalry.conv_pcts = rivalry_snapshot["conv_pcts"].copy()
		rivalry.core_pcts = rivalry_snapshot["core_pcts"].copy()
		rivalry.first_pcts = rivalry_snapshot["first_pcts"].copy()
		rivalry.likely_pcts = rivalry_snapshot["likely_pcts"].copy()
		rivalry.second_pcts = rivalry_snapshot["second_pcts"].copy()
		rivalry.core_radius = rivalry_snapshot["core_radius"]

		# Restore LineInPlot objects
		bisector_data = rivalry_snapshot.get("bisector")
		east_data = rivalry_snapshot.get("east")
		west_data = rivalry_snapshot.get("west")
		connector_data = rivalry_snapshot.get("connector")
		first_data = rivalry_snapshot.get("first")
		second_data = rivalry_snapshot.get("second")
		self._restore_line(rivalry, "bisector", bisector_data)
		self._restore_line(rivalry, "east", east_data)
		self._restore_line(rivalry, "west", west_data)
		self._restore_line(rivalry, "connector", connector_data)
		self._restore_line(rivalry, "first", first_data)
		self._restore_line(rivalry, "second", second_data)

	# ------------------------------------------------------------------------

	def _restore_line(
		self,
		rivalry: object,
		line_attr_name: str,
		line_data: dict[str, object] | None
	) -> None:
		"""Restore a LineInPlot object from captured data.

		Creates a new line object if needed to restore the saved state.

		Args:
			rivalry: The rivalry instance to restore the line into
			line_attr_name: Name of the line attribute to restore
			line_data: Dictionary containing the line's captured state
		"""
		if line_data is None:
			# If captured state was None, set the line to None
			setattr(rivalry, line_attr_name, None)
			return

		line = getattr(rivalry, line_attr_name)
		if line is None:
			# Need to create a new line object to restore into
			line = self._create_line_object(
				rivalry._director, line_attr_name, line_data
			)
			setattr(rivalry, line_attr_name, line)

		# Restore basic attributes
		line._x = line_data["x"]
		line._y = line_data["y"]
		line._cross_x = line_data["cross_x"]
		line._cross_y = line_data["cross_y"]
		line._slope = line_data["slope"]
		line._color = line_data["color"]
		line._thickness = line_data["thickness"]
		line._style = line_data["style"]
		line._direction = line_data["direction"]
		line._intercept = line_data["intercept"]
		line._case = line_data["case"]

		# Restore start and end points
		start_x = line_data["start_x"]
		start_y = line_data["start_y"]
		if start_x is not None and start_y is not None:
			line._start = Point(start_x, start_y)
		end_x = line_data["end_x"]
		end_y = line_data["end_y"]
		if end_x is not None and end_y is not None:
			line._end = Point(end_x, end_y)

		# Connector has additional length attribute
		if line_attr_name == "connector":
			line.length = line_data["length"]

	# ------------------------------------------------------------------------

	def _create_line_object(
		self,
		director: Status,
		line_attr_name: str,
		line_data: dict[str, object]
	) -> object:
		"""Create a line object for restoration.

		Creates a minimal line object using dummy values. The actual
		state will be overwritten immediately after creation.

		Args:
			director: The director instance
			line_attr_name: Name of the line type (bisector, east, etc.)
			line_data: The saved line data (used to get correct class)

		Returns:
			A new line object of the appropriate type
		"""
		# Import line classes locally to avoid circular imports
		from rivalry import (  # noqa: PLC0415
			Bisector,
			East,
			West,
			Connector,
			First,
			Second,
		)

		# Map line attribute names to their classes
		line_classes = {
			"bisector": Bisector,
			"east": East,
			"west": West,
			"connector": Connector,
			"first": First,
			"second": Second,
		}

		# Get the appropriate class
		line_class = line_classes[line_attr_name]

		# Create a dummy point and use saved slope for construction
		dummy_point: Point = Point(0.0, 0.0)
		slope = line_data["slope"]

		# Connector requires additional rival_a and rival_b parameters
		if line_attr_name == "connector":
			# Use dummy rival points for construction
			rival_a: Point = Point(0.0, 0.0)
			rival_b: Point = Point(0.0, 0.0)
			return line_class(
				director, dummy_point, slope, rival_a, rival_b
			)

		# All other line types just need director, point, slope
		return line_class(director, dummy_point, slope)

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
