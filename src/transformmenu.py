from __future__ import annotations

import math
import numpy as np
from numpy.linalg import svd
from numpy import asarray
import peek  # noqa: RUF100,F401
import pandas as pd
from typing import TYPE_CHECKING

from PySide6.QtWidgets import QDialog # noqa: F401
# from dialogs import MoveDialog, SelectItemsDialog, SetValueDialog

from scipy.spatial import procrustes
# from rivalry import Rivalry

if TYPE_CHECKING:
	from common import Spaces
	from director import Status
	# from exceptions import SpacesError

# ------------------------------------------------------------------------


class CompareCommand:
	"""The compare command performs a Procrustes rotation of the
	active configuration to match the target configuration. This is useful
	when the target configuration is a reference configuration and the
	active configuration needs to be rotated to match it.
	The Procrustes rotation is a least squares rotation of the
	active configuration to match the target configuration.
	It requires the target has the same number of points and dimensions
	as the active configuration.
	"""

	def __init__(self, director: Status, common: Spaces) -> None:  # noqa: ARG002
		self._director = director
		self._director.command = "Compare"
		return

	# ------------------------------------------------------------------------

	def execute(self, common: Spaces) -> None:
		self._director.record_command_as_selected_and_in_process()
		self._director.optionally_explain_what_command_does()
		self._director.dependency_checker.detect_dependency_problems()
		self._director.dependency_checker.detect_limitations_violations()
		common.capture_and_push_undo_state("Compare", "active", {})

		self._director.target_active.disparity = self._compare()

		self._create_compare_table()
		self._director.scores_active.scores = pd.DataFrame()
		self._director.rivalry.create_or_revise_rivalry_attributes(
			self._director, common)

		self._print_comparison()
		self._director.common.create_plot_for_tabs("compare")
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.record_command_as_successfully_completed()
		return

	# ------------------------------------------------------------------------

	def _compare(self) -> float:
		dim_labels = self._director.configuration_active.dim_labels
		point_names = self._director.configuration_active.point_names
		point_coords = self._director.configuration_active.point_coords
		target_coords = self._director.target_active.point_coords

		active_in = np.array(point_coords)
		target_in = np.array(target_coords)
		active_out, target_out, disparity = procrustes(active_in, target_in)

		point_coords = pd.DataFrame(
			active_out, columns=dim_labels, index=point_names
		)
		target_coords = pd.DataFrame(
			target_out, columns=dim_labels, index=point_names
		)
		compared = point_coords.merge(
			target_coords, how="inner", left_index=True, right_index=True
		)
		self._director.configuration_active.point_coords = point_coords
		self._director.target_active.point_coords = target_coords
		self._director.configuration_active.compared = compared

		return disparity

	# -----------------------------------------------------------------------

	def _create_compare_table(self) -> pd.DataFrame:
		"""Create a DataFrame comparing active configuration with
		target configuration.

		Returns:
			pd.DataFrame: DataFrame with the active and target coordinates
		"""
		# Get configuration objects
		active_config = self._director.configuration_active
		target_config = self._director.target_active

		# Get the dimensions we're using
		common = self._director.common
		hor_dim = common.hor_dim
		vert_dim = common.vert_dim

		# Create an empty DataFrame with point names as index
		compare_df = pd.DataFrame(index=active_config.point_names)

		# Add the coordinates in an object-oriented way
		# Use a loop to iterate over dimensions and set X/Y coordinates
		for index, dim in [(hor_dim, "X"), (vert_dim, "Y")]:
			compare_df[f"Active_{dim}"] = active_config.point_coords.iloc[
				:, index
			].apply(lambda x: f"{x:.2f}")
			compare_df[f"Target_{dim}"] = target_config.point_coords.iloc[
				:, index
			].apply(lambda x: f"{x:.2f}")

		self._director.target_active.compare_df = compare_df

		return compare_df

	# ------------------------------------------------------------------------

	def _print_comparison(self) -> None:
		point_coords = self._director.configuration_active.point_coords
		target_coords = self._director.target_active.point_coords

		print(f"Disparity = {self._director.target_active.disparity:8.4f}")
		print("\nActive configuration:")
		print(point_coords.to_string(float_format="{:.2f}".format))
		print("\nTarget configuration:")
		print(target_coords.to_string(float_format="{:.2f}".format))
		return


# ---------------------------------------------------------------------------


class CenterCommand:
	"""The Center command shifts points to be centered around the origin.
	This is useful when coordinates are Lat long degrees.
	"""

	def __init__(self, director: Status, common: Spaces) -> None:  # noqa: ARG002
		self._director = director
		director.command = "Center"
		return

	# ------------------------------------------------------------------------

	def execute(self, common: Spaces) -> None:
		self._director.record_command_as_selected_and_in_process()
		self._director.optionally_explain_what_command_does()
		self._director.dependency_checker.detect_dependency_problems()
		common.capture_and_push_undo_state("Center", "active", {})
		self._center_by_subtracting_mean_from_coordinates()
		self._director.scores_active.scores = pd.DataFrame()
		self._director.rivalry.create_or_revise_rivalry_attributes(
			self._director, common)
		self._director.configuration_active.print_active_function()
		self._director.common.create_plot_for_tabs("configuration")
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.record_command_as_successfully_completed()
		return

	# ------------------------------------------------------------------------

	def _center_by_subtracting_mean_from_coordinates(self) -> None:
		point_coords = self._director.configuration_active.point_coords
		point_labels = self._director.configuration_active.point_labels

		dim_avg = point_coords.mean()
		for index_dim in range(len(dim_avg)):
			for index_point, _ in enumerate(point_labels):
				point_coords.iloc[index_point, index_dim] = (
					point_coords.iloc[index_point, index_dim]
					- dim_avg.iloc[index_dim]
				)

		self._director.configuration_active.point_coords = point_coords

		return

	# ------------------------------------------------------------------------


class InvertCommand:
	"""The Invert command is used to invert dimensions"""

	def __init__(self, director: Status, common: Spaces) -> None:  # noqa: ARG002
		self._director = director
		self._director.command = "Invert"
		self._dimensions_to_invert_title = "Select dimensions to invert"
		self._dimensions = self._director.configuration_active.dim_names
		return

	# ------------------------------------------------------------------------

	def execute(self, common: Spaces) -> None:
		rivalry = self._director.rivalry
		self._director.record_command_as_selected_and_in_process()
		self._director.optionally_explain_what_command_does()
		self._director.dependency_checker.detect_dependency_problems()
		params = common.get_command_parameters("Invert")
		selected_items: list = params["dimensions"]
		dim_names = self._director.configuration_active.dim_names
		dims_indexes = [dim_names.index(dim) for dim in selected_items]
		common.capture_and_push_undo_state("Invert", "active", params)
		# Now perform the invert
		self._invert(dims_indexes)
		rivalry.create_or_revise_rivalry_attributes(
			self._director, common)
		self._director.configuration_active.print_active_function()
		self._director.common.create_plot_for_tabs("configuration")
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.record_command_as_successfully_completed()
		return

	# ------------------------------------------------------------------------

	def _invert(self, dims_indexes: list[int]) -> None:
		range_dims = self._director.configuration_active.range_dims
		range_scores = self._director.scores_active.range_scores

		_scores = self._director.scores_active.scores
		# scores = []
		#
		# Multiply all points on selected dimensions to be inverted by -1
		#
		for each_dim in range_dims:
			for checked_dim in dims_indexes:
				if each_dim == checked_dim:
					self._inverter(checked_dim)
		if self._director.common.have_scores():
			# peek("Scores exist, inverting scores on selected dimensions") # ty: ignore[call-non-callable]
			cols = []
			cols.extend(
				[
					_scores.columns[each_dim + 1]
					for each_dim in range_scores
					for checked_dim in dims_indexes
					if each_dim == checked_dim
				]
			)
			_scores[cols] = _scores[cols].mul(-1)
			self._director.scores_active.scores = _scores
			self._update_score_attributes_for_plotting()
			self._director.scores_active.print_scores()

		return

	# ------------------------------------------------------------------------

	def _inverter(self, which_dim: int) -> None:
		point_coords = self._director.configuration_active.point_coords
		range_points = self._director.configuration_active.range_points

		for each_point in range_points:
			point_coords.iloc[each_point, which_dim] = (
				point_coords.iloc[each_point, which_dim] * -1
			)

	# ------------------------------------------------------------------------

	def _update_score_attributes_for_plotting(self) -> None:
		"""Update score_1 and score_2 attributes after inversion."""
		if not self._director.common.have_scores():
			return

		scores_active = self._director.scores_active
		scores = scores_active.scores
		dim_names = scores_active.dim_names
		min_dims_for_first_score = 1
		min_dims_for_second_score = 2

		# Update score_1 if it exists
		if len(dim_names) >= min_dims_for_first_score:
			hor_axis_name = scores_active.hor_axis_name
			scores_active.score_1 = scores[hor_axis_name]
			scores_active.score_1_name = dim_names[0]

		# Update score_2 if it exists
		if len(dim_names) >= min_dims_for_second_score:
			vert_axis_name = scores_active.vert_axis_name
			scores_active.score_2 = scores[vert_axis_name]
			scores_active.score_2_name = dim_names[1]

		return

	# ------------------------------------------------------------------------


class MoveCommand:
	"""The Move command allows the used to add
	or subtract a constant form all points on one or more dimensions.
	"""

	def __init__(self, director: Status, common: Spaces) -> None:
		self._director = director
		self.common = common
		self._director.command = "Move"
		# self._director.rivalry.bisector.case = "Unknown"
		self._move_title = "Select dimension and value for move"
		self._move_value_title = "Value to add to all points on this dimension"
		self._move_options = self._director.configuration_active.dim_names

		return

	# ------------------------------------------------------------------------

	def execute(self, common: Spaces) -> None: # noqa: ARG002
		rivalry = self._director.rivalry
		self._director.record_command_as_selected_and_in_process()
		self._director.optionally_explain_what_command_does()
		self._director.dependency_checker.detect_dependency_problems()
		params = self.common.get_command_parameters("Move")
		dimension_name: str = params["dimension"]
		decimal_value: float = params["distance"]
		dim_names = self._director.configuration_active.dim_names
		selected_option = dim_names.index(dimension_name)
		self.common.capture_and_push_undo_state("Move", "active", params)
		# Now perform the move
		self._move(selected_option, decimal_value)
		self._director.scores_active.scores = pd.DataFrame()
		rivalry.create_or_revise_rivalry_attributes(
			self._director, self.common)
		self._director.configuration_active.inter_point_distances()
		self.common.rank_when_similarities_match_configuration()
		self._director.configuration_active.print_active_function()
		self._director.common.create_plot_for_tabs("configuration")
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.record_command_as_successfully_completed()
		return

	# ------------------------------------------------------------------------

	def _move(self, which_dim: int, value: float) -> None:
		point_coords = self._director.configuration_active.point_coords
		range_points = self._director.configuration_active.range_points

		for each_point in range_points:
			point_coords.iloc[each_point, which_dim] = (
				(point_coords.iloc[each_point, which_dim]) + value
			)
		return

# ------------------------------------------------------------------------


class RescaleCommand:
	"""The Rescale command is used to rescale one or more dimensions."""

	def __init__(self, director: Status, common: Spaces) -> None: # noqa: ARG002
		self._director = director
		self._director.command = "Rescale"
		self._rescale_title = "Select dimension to rescale"
		self._rescale_dims = self._director.configuration_active.dim_names
		self._rescale_by_title = "Rescale configuration"
		self._rescale_by_label = (
			"Amount by which to multiple every point \non selected dimensions"
		)
		self._rescale_by_min_val = -9999.9
		self._rescale_by_max_val = 9999.9
		self._rescale_by_an_integer = False
		self._rescale_by_default = 0.0
		_ndim = director.configuration_active.ndim
		_npoint = director.configuration_active.npoint
		return

	# ------------------------------------------------------------------------

	def execute(self, common: Spaces) -> None:  # noqa: ARG002
		self._director.record_command_as_selected_and_in_process()
		self._director.optionally_explain_what_command_does()
		self._director.dependency_checker.detect_dependency_problems()
		params = self.common.get_command_parameters("Rescale")
		selected_items: list = params["dimensions"]
		value: float = params["scale_factor"]
		self.common.capture_and_push_undo_state(
			"Rescale",
			"active",
			params
		)
		#
		# Now perform the rescale
		#
		self._rescale_selected_dimensions(selected_items, value)
		self._director.scores_active.scores = pd.DataFrame()
		self._director.configuration_active.inter_point_distances()
		self.common.rank_when_similarities_match_configuration()
		self._director.rivalry.create_or_revise_rivalry_attributes(
			self._director, self.common
		)
		self._director.configuration_active.print_active_function()
		self._director.common.create_plot_for_tabs("configuration")
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.record_command_as_successfully_completed()
		return

	# ------------------------------------------------------------------------

	# ------------------------------------------------------------------------

	def _rescale_selected_dimensions(
		self, selected_items: list[str], value: float
	) -> None:
		dim_names = self._director.configuration_active.dim_names
		range_dims = self._director.configuration_active.range_dims
		point_coords = self._director.configuration_active.point_coords

		for each_dim in range_dims:
			if dim_names[each_dim] in selected_items:
				point_coords.iloc[:, each_dim] *= value

		return

	# ------------------------------------------------------------------------


class RotateCommand:
	"""The Rotate command is used to rotate the active configuration."""

	def __init__(self, director: Status, common: Spaces) -> None:
		self._director = director
		self.common = common
		self._director.command = "Rotate"

		return

	# ------------------------------------------------------------------------

	def execute(self, common: Spaces) -> None: # noqa: ARG002
		rivalry = self._director.rivalry
		self._director.record_command_as_selected_and_in_process()
		self._director.optionally_explain_what_command_does()
		self._director.dependency_checker.detect_dependency_problems()
		params = self.common.get_command_parameters("Rotate")
		deg: int = params["degrees"]
		self.common.capture_and_push_undo_state(
			"Rotate",
			"active",
			params)
		# Now perform the rotation
		radians = math.radians(float(deg))
		self._rotate(radians)
		self._director.scores_active.scores = pd.DataFrame()
		rivalry.create_or_revise_rivalry_attributes(
			self._director, self.common)
		self._director.configuration_active.print_active_function()
		self._director.common.create_plot_for_tabs("configuration")
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.record_command_as_successfully_completed()
		return

	# ------------------------------------------------------------------------

	def _rotate(self, radians: float) -> None:
		hor_dim = self._director.common.hor_dim
		vert_dim = self._director.common.vert_dim
		point_coords = self._director.configuration_active.point_coords
		range_points = self._director.configuration_active.range_points

		for each_point in range_points:
			new_x = (
				math.cos(radians) * point_coords.iloc[each_point, hor_dim]
			) - (math.sin(radians) * point_coords.iloc[each_point, vert_dim])
			new_y = (
				math.sin(radians) * point_coords.iloc[each_point, hor_dim]
			) + (math.cos(radians) * point_coords.iloc[each_point, vert_dim])
			point_coords.iloc[each_point, hor_dim] = new_x
			point_coords.iloc[each_point, vert_dim] = new_y

		return

	# ------------------------------------------------------------------------


class VarimaxCommand:
	"""The Varimax command performs a varimax rotation on the
	active configuration.
	"""

	def __init__(self, director: Status, common: Spaces) -> None:
		self._director = director
		self.common = common
		self._director.command = "Varimax"
		return

	# ------------------------------------------------------------------------

	def execute(self, common: Spaces) -> None:
		ndim = self._director.configuration_active.ndim
		point_coords = self._director.configuration_active.point_coords
		point_names = self._director.configuration_active.point_names
		npoint = self._director.configuration_active.npoint
		item_names = self._director.configuration_active.item_names
		nreferent = self._director.configuration_active.nreferent

		self._director.record_command_as_selected_and_in_process()
		self._director.optionally_explain_what_command_does()
		self._director.dependency_checker.detect_dependency_problems()
		if len(item_names) == 0:
			item_names = point_names
		#
		# Capture state before making changes (for undo)
		#
		self.common.capture_and_push_undo_state(
			"Varimax", "active", {}
		)
		#
		# Now perform the varimax rotation
		#
		print(
			"DEBUG --in varimax command before rotation-- "
			f"{point_coords=}"
			f"{ndim=} {npoint=}"
			f"{nreferent=}"
		)
		self._perform_varimax_rotation()
		self._director.scores_active.scores = pd.DataFrame()
		self._director.rivalry.create_or_revise_rivalry_attributes(
			self._director, common
		)
		print(
			f"DEBUG -- after -- {point_coords=}{ndim=} {npoint=}{nreferent=}"
		)
		self._director.configuration_active.print_active_function()
		self._director.common.create_plot_for_tabs("configuration")
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.record_command_as_successfully_completed()
		return

	# ------------------------------------------------------------------------

	def _perform_varimax_rotation(self) -> None:
		dim_labels = self._director.configuration_active.dim_labels
		point_names = self._director.configuration_active.point_names
		point_coords = self._director.configuration_active.point_coords
		item_names = self._director.configuration_active.item_names

		to_be_rotated = np.array(point_coords)
		print(f"\nDEBUG -- in _perform_varimax_rotation {to_be_rotated=}")
		rotated = self._varimax_function(
			to_be_rotated, gamma=1.0, q=20, tol=1e-6
		)
		print(f"\nDEBUG -- in process {rotated=}")
		print(f"\nDEBUG -- {dim_labels=}{point_names=}{item_names=}")
		point_coords = pd.DataFrame(
			rotated, columns=dim_labels, index=item_names
		)

		self._director.configuration_active.point_coords = point_coords
		return

	# ------------------------------------------------------------------------

	@staticmethod
	def _varimax_function(
		Phi: np.ndarray,  # noqa: N803
		gamma: float = 1.0,
		q: int = 20,
		tol: float = 1e-6,
	) -> np.array:
		p, k = np.shape(Phi)
		# R = eye(k)
		R = np.zeros(k)  # noqa: N806
		d = 0
		xrange = range(q)
		for i in xrange:  # noqa: B007
			d_old = d
			# Lambda = dot(Phi, R)
			Lambda = Phi @ R  # noqa: N806
			# u, s, vh = svd(
			# 	dot(Phi.T, asarray(Lambda) ** 3 - (gamma / p) * dot(
			# 	 	Lambda, diag(diag(dot(Lambda.T, Lambda))))))
			# u, s, vh = svd(
			# 	dot(Phi.T, asarray(Lambda) ** 3 - (gamma / p) * dot(
			# 	 	Lambda, np.diagonal(np.diagonal(dot(Lambda.T, Lambda))))))
			u, s, vh = svd(
				Phi.T
				@ (
					asarray(Lambda) ** 3
					- (gamma / p)
					* (Lambda @ np.diagonal(np.diagonal(Lambda.T @ Lambda)))
				)
			)
			# R = dot(u, vh)
			R = u @ vh  # noqa: N806
			d = sum(s)
			if d_old != 0 and d / d_old < 1 + tol:
				break

		# return dot(Phi, R)
		return Phi @ R
