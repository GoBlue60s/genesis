from __future__ import annotations

# Standard library imports
# import math

# Third-party imports
import numpy as np
import pandas as pd

from PySide6.QtWidgets import QTableWidget
from sklearn import manifold

from dialogs import ChoseOptionDialog

from exceptions import (
	SelectionError,
	SpacesError,
	# UnderDevelopmentError,
)
from typing import TYPE_CHECKING

if TYPE_CHECKING:
	from common import Spaces
	from director import Status


# --------------------------------------------------------------------------


class AlikeCommand:
	"""The Alike command - creates a plot with a line joining points
	with high similarity. The Alike command is used to identify pairs
	of points with high similarity. The user will be asked for a cutoff
	value. A plot of the configuration with be created with pairs of
	points with a similarity above (or if dissimilarities, below)
	the cutoff having a line joining the points.
	"""

	def __init__(self, director: Status, common: Spaces) -> None:
		self._director = director
		self._common = common
		self._director.command = "Alike"
		# Store alike-specific data in command instance, not in feature
		self.cutoff: float = 0.0
		self.filtered_pairs: list[list] = []
		self.a_x_alike: list[float] = []
		self.a_y_alike: list[float] = []
		self.b_x_alike: list[float] = []
		self.b_y_alike: list[float] = []
		self.alike_df: pd.DataFrame = pd.DataFrame()

		return

	# ------------------------------------------------------------------------

	def execute(self, common: Spaces) -> None:
		self._director.record_command_as_selected_and_in_process()
		self._director.optionally_explain_what_command_does()
		self._director.dependency_checker.detect_dependency_problems()
		self._director.common.create_plot_for_tabs("cutoff")
		params = common.get_command_parameters("Alike")
		common.capture_and_push_undo_state("Alike", "passive", params)
		self.cutoff = params["cutoff"]
		self._determine_alike_pairs()
		self._print_alike_pairs()
		self._create_alike_table()
		self._director.common.create_plot_for_tabs("alike")
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.record_command_as_successfully_completed()

		return

	# ------------------------------------------------------------------------

	def _determine_alike_pairs_initialize_variables(self) -> None:
		self.bad_cutoff_value_title = self._director.command
		self.bad_cutoff_value_message = (
			"No pairs meet the cutoff criteria\nChange cutoff criteria"
		)

	# ------------------------------------------------------------------------

	def _determine_alike_pairs(self) -> None:
		"""Determine which pairs meet the alike criteria based on cutoff.

		Raises:
			SelectionError: If no pairs satisfy the cutoff criteria
		"""
		self._determine_alike_pairs_initialize_variables()
		self._director.common.cutoff = self.cutoff
		value_type: str = self._director.similarities_active.value_type
		sorted_pairs: list[list] = (
			self._director.similarities_active.sorted_similarities_w_pairs
		)
		# Use the filter_pairs_by_cutoff method to get qualifying pairs
		self.filtered_pairs = self._filter_pairs_by_cutoff(
			sorted_pairs, self.cutoff, value_type
		)
		n_similar_pairs: int = len(self.filtered_pairs)

		if n_similar_pairs == 0:
			raise SelectionError(
				self.bad_cutoff_value_title, self.bad_cutoff_value_message
			)

		# Store filtered pairs and update coordinate lists for plotting
		self._update_coordinates_for_similar_pairs(self.filtered_pairs)
		self._director.n_similar_pairs = n_similar_pairs

		return

	# ------------------------------------------------------------------------

	def _filter_pairs_by_cutoff(
		self, sorted_pairs: list[list], cut_point: float, value_type: str
	) -> list[list]:
		"""Filter pairs based on cutoff criteria and return qualifying
		pairs."""
		filtered_pairs: list[list] = []
		for pair in sorted_pairs:
			similarity = pair[0]
			# Add pairs that meet cutoff criteria
			if (value_type == "similarities" and similarity > cut_point) or (
				value_type == "dissimilarities" and similarity < cut_point
			):
				filtered_pairs.append(pair)
		return filtered_pairs

	# ------------------------------------------------------------------------

	def _update_coordinates_for_similar_pairs(
		self, filtered_pairs: list[list]
	) -> None:
		"""Update coordinate lists for pairs that meet the similarity criteria.

		Args:
			filtered_pairs: List of pairs that meet the cutoff criteria

		This method updates the a_x_alike, a_y_alike, b_x_alike, and b_y_alike
		lists in the command instance for plotting.
		"""
		# Get necessary objects
		point_coords = self._director.configuration_active.point_coords
		hor_dim = self._director.common.hor_dim
		vert_dim = self._director.common.vert_dim

		# Clear existing coordinate lists
		self.a_x_alike = []
		self.a_y_alike = []
		self.b_x_alike = []
		self.b_y_alike = []

		# Get item labels and coordinates
		for pair in filtered_pairs:
			# Each pair contains: [similarity_value, item_a_label,
			# item_b_label, item_a_name, item_b_name]
			item_a_label: str = pair[1]
			item_b_label: str = pair[2]

			# Find indices of these items in point_coords
			item_a_index: int = (
				self._director.configuration_active.point_labels.index(
					item_a_label
				)
			)
			item_b_index: int = (
				self._director.configuration_active.point_labels.index(
					item_b_label
				)
			)

			# Add coordinates to the lists
			self.a_x_alike.append(
				point_coords.iloc[item_a_index, hor_dim]
			)
			self.a_y_alike.append(
				point_coords.iloc[item_a_index, vert_dim]
			)
			self.b_x_alike.append(
				point_coords.iloc[item_b_index, hor_dim]
			)
			self.b_y_alike.append(
				point_coords.iloc[item_b_index, vert_dim]
			)

		return

	# ------------------------------------------------------------------------

	def _print_alike_pairs(self) -> None:
		"""Print information about the cutoff and similar pairs."""
		print("\tCut point: ", self.cutoff)
		print(f"\tNumber of similar pairs: {self._director.n_similar_pairs}")

		print(f"\n\t {'Item':<15} {'Paired With':<15} {'Similarity'}")
		print("\t" + "-" * 43)
		for each_pair in range(len(self.filtered_pairs)):
			print(
				f"\t {self.filtered_pairs[each_pair][3]:<15}"
				f"{self.filtered_pairs[each_pair][4]:<15}"
				f"{self.filtered_pairs[each_pair][0]:>8.3f}"
			)

		return

	# ------------------------------------------------------------------------

	def _create_alike_table(self) -> pd.DataFrame:
		"""Create a DataFrame displaying pairs of items that meet the alike
		criteria.

		Returns:
			pd.DataFrame: DataFrame with items that are "alike" based on cutoff
		"""
		# Get similarity information
		similarities_active = self._director.similarities_active
		sorted_similarities_w_pairs: list[list] = (
			similarities_active.sorted_similarities_w_pairs
		)
		value_type: str = similarities_active.value_type
		# Filter pairs that meet the cutoff criteria
		alike_pairs: list[tuple] = []
		for pair in sorted_similarities_w_pairs:
			similarity: float = pair[0]
			item_a: str = pair[1]
			item_b: str = pair[2]
			# Add pairs that meet cutoff criteria based on value_type
			if (value_type == "similarities" and similarity > self.cutoff) or (
				value_type == "dissimilarities" and similarity < self.cutoff
			):
				alike_pairs.append((item_a, item_b, similarity))

		# Create the DataFrame with appropriate column name based on value_type
		similarity_column_name = (
			"Similarity" if value_type == "similarities" else "Dis/similarity"
		)
		self.alike_df = pd.DataFrame(
			alike_pairs,
			columns=["Item", "Paired with", similarity_column_name],
		)

		return self.alike_df

	# ------------------------------------------------------------------------


class DistancesCommand:
	def __init__(self, director: Status, common: Spaces) -> None:
		"""Distances command - displays a matrix of inter-point distances."""
		self._director = director
		self.common = common
		self._director.command = "Distances"
		self._width: int = 8
		self._decimals: int = 2
		self.title_for_table_widget: str = "Inter-point distances"
		return

	# ------------------------------------------------------------------------

	def execute(self, common: Spaces) -> None:
		self._director.record_command_as_selected_and_in_process()
		self._director.optionally_explain_what_command_does()

		# Get command parameters and capture state
		params = common.get_command_parameters("Distances")
		common.capture_and_push_undo_state("Distances", "passive", params)

		self._director.dependency_checker.detect_dependency_problems()
		self._director.configuration_active.print_the_distances(
			self._width, self._decimals, common)
		self._director.common.create_plot_for_tabs("heatmap_dist")
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.set_focus_on_tab("Plot")
		self._director.record_command_as_successfully_completed()
		return

	# ------------------------------------------------------------------------


class LineOfSightCommand:
	def __init__(self, director: Status, common: Spaces) -> None:
		"""The Line of Sight command computes the line of sight measure
		of association
		"""
		self._director = director
		self.common = common
		self._director.command = "Line of sight"
		self._width: int = 8
		self._decimals: int = 1

		return

	# ------------------------------------------------------------------------

	def execute(self, common: Spaces) -> None:


		self._director.record_command_as_selected_and_in_process()
		self._director.optionally_explain_what_command_does()
		self._director.dependency_checker.detect_dependency_problems()
		#
		# Capture state before making changes (for undo)
		#
		self.common.capture_and_push_undo_state(
			"Line of sight",
			"active",
			{})
		#
		# Now perform the line of sight calculation
		#
		self._director.similarities_active = self.common.los(
			self._director.evaluations_active)
		self._duplicate_similarities(common)
		self._director.similarities_active.rank_similarities()
		self._director.similarities_active.duplicate_ranked_similarities(
			common)
		self._director.similarities_active.print_the_similarities(
			self._width, self._decimals, common)
		self._director.title_for_table_widget = (
			f"Line of sight:\n"
			f"The {self._director.similarities_active.value_type}"
			f"matrix has {self._director.similarities_active.nreferent}"
			f" items")
		self._director.common.create_plot_for_tabs("heatmap_simi")
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.set_focus_on_tab("Plot")
		self._director.record_command_as_successfully_completed()
		return

	# ------------------------------------------------------------------------

	def _duplicate_similarities(self, common: Spaces) -> None:
		(
			self._director.similarities_active.similarities_as_dataframe,
			self._director.similarities_active.similarities_as_dict,
			self._director.similarities_active.similarities_as_list,
			self._director.similarities_active.similarities_as_square,
			self._director.similarities_active.sorted_similarities_w_pairs,
			self._director.similarities_active.ndyad,
			self._director.similarities_active.range_dyads,
			self._director.similarities_active.range_items,
		) = common.duplicate_in_different_structures(
			self._director.similarities_active.similarities,
			self._director.similarities_active.item_names,
			self._director.similarities_active.item_labels,
			self._director.similarities_active.nreferent,
			self._director.similarities_active.value_type,
		)

	# ------------------------------------------------------------------------


class PairedCommand:
	"""The paired command is used to get the
	interpoint distance and similarity for pairs of points.
	"""

	def __init__(self, director: Status, common: Spaces) -> None:
		self._director = director
		self.common = common
		self._director.command = "Paired"
		self._paired_title: str = "Point comparisons"
		self._paired_items: list[str] = (
			self._director.configuration_active.point_names
		)
		return

	# ------------------------------------------------------------------------

	def execute(self, common: Spaces) -> None:
		self._director.record_command_as_selected_and_in_process()
		self._director.optionally_explain_what_command_does()
		self._director.dependency_checker.detect_dependency_problems()
		params = common.get_command_parameters("Paired")
		common.capture_and_push_undo_state("Paired", "passive", params)
		point_names = self._director.configuration_active.point_names
		focal_index: int = params["focus"]
		self._focal_item_index: int = focal_index
		self._create_paired_dataframe()
		self._print_paired()
		point_names = self._director.configuration_active.point_names
		self._director.title_for_table_widget = (
			f"Relationships between {point_names[focal_index]} "
			f"and other points")

		self._director.create_widgets_for_output_and_log_tabs()
		self._director.set_focus_on_tab("Output")
		self._director.record_command_as_successfully_completed()
		return

	# ------------------------------------------------------------------------

	def _create_paired_dataframe(self) -> pd.DataFrame:
		"""Create a DataFrame of relationships between the focal
		point and all other points."""

		focal_index = self._focal_item_index
		point_names = self._director.configuration_active.point_names
		similarities_as_dataframe: pd.DataFrame = (
			self._director.similarities_active.similarities_as_dataframe)
		value_type: str = self._director.similarities_active.value_type
		distances_as_dataframe: pd.DataFrame = (
			self._director.configuration_active.distances_as_dataframe)

		# Create a list to store data for the DataFrame
		paired_data = []

		# Loop through all points
		for i, name in enumerate(point_names):
			if i != focal_index:  # Skip the focal point itself
				# Get similarity between focal point and this point
				similarity: float = \
					similarities_as_dataframe.iloc[focal_index, i]

				# Get distance between focal point and this point
				distance: float = distances_as_dataframe.iloc[focal_index, i]

				# Add to data list
				paired_data.append(
					{
						"Name": name,
						"Similarity": similarity,
						"Distance": distance,
					})

		# Create DataFrame
		paired_df: pd.DataFrame = pd.DataFrame(paired_data)

		# Sort by similarity (ascending or descending based on value_type)
		if value_type == "similarities":
			paired_df: pd.DataFrame = \
				paired_df.sort_values(by="Similarity", ascending=False)
		else:  # "dissimilarities"
			paired_df: pd.DataFrame = \
				paired_df.sort_values(by="Similarity", ascending=True)

		# Store the DataFrame for display
		self._paired_df: pd.DataFrame = paired_df

		return paired_df

	# ------------------------------------------------------------------------

	def _print_paired(self) -> None:
		"""Print the DataFrame showing relationships between the focal
		point and all other points."""

		focal_index: int = self._focal_item_index
		point_names: list[str] = \
			self._director.configuration_active.point_names
		value_type: str = self._director.similarities_active.value_type

		# Determine the similarity label based on value type
		sim_label = (
			"Similarity" if value_type == "similarities" else "Dis/similarity"
		)

		# Print title line
		print(
			f"\nRelationships between {point_names[focal_index]} "
			f"and other points:\n"
		)

		# Print just the three columns with appropriate headers
		display_df: pd.DataFrame = \
			self._paired_df[["Name", "Similarity", "Distance"]]

		print(
			f"  {display_df.columns[0]:<20} {sim_label:>12} "
			f"{display_df.columns[2]:>12}"
		)
		print("  " + "-" * 48)
		for _, row in display_df.iterrows():
			print(
				"  {:<20} {:>12.4f} {:>12.4f}".format(
					row["Name"], row["Similarity"], row["Distance"]
				)
			)

		return

	# ------------------------------------------------------------------------

	def _display(self) -> QTableWidget:
		"""Create a table widget showing relationships between the focal
		point and all other points."""

		gui_output_as_widget = self._director.statistics.display_table(
			"paired"
		)

		self._director.output_widget_type= "Table"
		return gui_output_as_widget

	# ------------------------------------------------------------------------


class RanksDifferencesCommand:
	def __init__(self, director: Status, common: Spaces) -> None:
		self._director = director
		self.common = common
		self._director.command = "Ranks differences"
		self._director.title_for_table_widget = "Difference of Ranks"
		return

	# ------------------------------------------------------------------------

	def execute(self, common: Spaces) -> None:
		self._director.record_command_as_selected_and_in_process()
		self._director.optionally_explain_what_command_does()

		# Get command parameters and capture state
		params = common.get_command_parameters("Ranks differences")
		common.capture_and_push_undo_state(
			"Ranks differences", "passive", params)

		self._director.dependency_checker.detect_dependency_problems()
		self._director.similarities_active.compute_differences_in_ranks()

		self._director.common.create_plot_for_tabs("heatmap_rank_diff")
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.record_command_as_successfully_completed()
		self._director.set_focus_on_tab("Plot")
		return

	# ------------------------------------------------------------------------


class RanksDistancesCommand:
	def __init__(self, director: Status, common: Spaces) -> None:
		self._director = director
		self.common = common
		self._director.command = "Ranks distances"
		self._director.title_for_table_widget = "Rank of Distances"
		return

	# ------------------------------------------------------------------------

	def execute(self, common: Spaces) -> None:
		self._director.record_command_as_selected_and_in_process()
		self._director.optionally_explain_what_command_does()

		# Get command parameters and capture state
		params = common.get_command_parameters("Ranks distances")
		common.capture_and_push_undo_state(
			"Ranks distances", "passive", params)

		self._director.dependency_checker.detect_dependency_problems()
		self._director.common.print_lower_triangle(
			self._director.common.decimals,
			self._director.configuration_active.point_labels,
			self._director.configuration_active.point_names,
			self._director.configuration_active.npoint,
			self._director.configuration_active.ranked_distances,
			self._director.common.width)
		self._director.common.create_plot_for_tabs("heatmap_ranked_dist")
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.record_command_as_successfully_completed()
		self._director.set_focus_on_tab("Plot")
		return

	# ------------------------------------------------------------------------


class RanksSimilaritiesCommand:
	def __init__(self, director: Status, common: Spaces) -> None:
		self._director = director
		self.common = common
		self._director.command = "Ranks similarities"
		self._director.title_for_table_widget = "Rank of Similarities"
		return

	# ------------------------------------------------------------------------

	def execute(self, common: Spaces) -> None:
		self._director.record_command_as_selected_and_in_process()
		self._director.optionally_explain_what_command_does()

		# Get command parameters and capture state
		params = common.get_command_parameters("Ranks similarities")
		common.capture_and_push_undo_state(
			"Ranks similarities", "passive", params)

		self._director.dependency_checker.detect_dependency_problems()
		self._director.common.print_lower_triangle(
			self._director.common.decimals,
			self._director.similarities_active.item_labels,
			self._director.similarities_active.item_names,
			self._director.similarities_active.nitem,
			self._director.similarities_active.ranked_similarities,
			self._director.common.width)
		self._director.common.create_plot_for_tabs("heatmap_ranked_simi")
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.record_command_as_successfully_completed()
		self._director.set_focus_on_tab("Plot")
		return

	# ------------------------------------------------------------------------


class ScreeCommand:
	"""The Scree command creates diagram showing stress vs. dimensionality."""

	def __init__(self, director: Status, common: Spaces) -> None:
		self._director = director
		self.common = common
		self._director.command = "Scree"
		self._director.configuration_active.min_stress = pd.DataFrame(
			columns=["Dimensionality", "Best Stress"])
		self._dim_names: list[str] = []
		self._dim_labels: list[str] = []
		self._use_metric: bool = False
		self._min_stress: pd.DataFrame = (
			self._director.configuration_active.min_stress)
		self._scree_title: str = "MDS model"
		self._scree_options_title: str = "Model to use"
		self._scree_options: list[str] = ["Non-metric", "Metric"]

		return

	# ------------------------------------------------------------------------

	def execute(
		self, common: Spaces, use_metric: bool = False  # noqa: FBT001, FBT002
	) -> None:
		self._director.record_command_as_selected_and_in_process()
		self._director.optionally_explain_what_command_does()

		# Get command parameters and capture state
		params = common.get_command_parameters("Scree", use_metric=use_metric)
		use_metric = params["use_metric"]
		common.capture_and_push_undo_state("Scree", "passive", params)

		self._director.dependency_checker.detect_dependency_problems()
		self._use_metric = use_metric
		self._scree()
		self._director.common.create_plot_for_tabs("scree")
		self._director.title_for_table_widget = "Best stress by dimensionality"
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.record_command_as_successfully_completed()
		return

	# ------------------------------------------------------------------------

	def _get_model_for_scree_diagram_initialize_variables(self) -> None:
		self.need_model_for_scree_error_title = self._director.command
		self.need_model_for_scree_error_message: str = (
			"A model is needed to use in creating scree diagram.")

	# ------------------------------------------------------------------------

	def _get_model_for_scree_diagram(
		self,
		scree_title: str,
		scree_options_title: str,
		scree_options: list[str],
	) -> None:
		self._get_model_for_scree_diagram_initialize_variables()

		# use_metric = self._use_metric

		dialog = ChoseOptionDialog(
			scree_title, scree_options_title, scree_options
		)
		result = dialog.exec()
		if result == QDialog.Accepted: # ty: ignore[unresolved-attribute]
			selected_option = dialog.selected_option  # + 1
			match selected_option:
				case 0:
					use_metric: bool = False
				case 1:
					use_metric: bool = True
				case _:
					raise SpacesError(
						self.need_model_for_scree_error_title,
						self.need_model_for_scree_error_message,
					)

		else:
			raise SpacesError(
				self.need_model_for_scree_error_title,
				self.need_model_for_scree_error_message,
			)

		self._use_metric: bool = use_metric
		self._director.common._use_metric = use_metric

		return

	# -------------------------------------------------------------------------

	def _scree(self) -> None:
		similarities_as_square = (
			self._director.similarities_active.similarities_as_square
		)
		min_stress: pd.DataFrame = self._min_stress

		dim_names: list[str] = []
		dim_labels: list[str] = []

		dim_names.append("Dimension 1")
		dim_labels.append("Dim1")
		#
		range_ncomps = range(1, 11)
		for each_n_comp in range_ncomps:
			nmds = manifold.MDS(
				n_components=each_n_comp,
				metric=self._use_metric,
				dissimilarity="precomputed",
				n_init=20,
				verbose=0,
				normalized_stress="auto",
			)
			npos = nmds.fit_transform(X=similarities_as_square)
			point_coords = pd.DataFrame(npos.tolist())
			dim_names.append("Dimension " + str(each_n_comp))
			dim_labels.append("Di" + str(each_n_comp))
			#
			best_stress = nmds.stress_
			min_stress.loc[len(min_stress)] = [each_n_comp, best_stress]

			print(
				f"\tBest stress in {each_n_comp} dimensions: {best_stress:.4f}"
			)

		self.point_coords: pd.DataFrame = point_coords
		self._dim_names: list[str] = dim_names
		self._dim_labels: list[str] = dim_labels
		self.best_stress: float = best_stress
		self._min_stress: pd.DataFrame = min_stress
		self._director.common._min_stress = min_stress

		return

	# ------------------------------------------------------------------------


class ShepardCommand:
	"""The Shepard command creates shepard diagram - rank of
	distance against rank or similarity
	"""

	def __init__(self, director: Status, common: Spaces) -> None:
		self._director = director
		self.common = common
		self._director.command = "Shepard"
		self._shepard_title: str = "Shepard diagram"
		self._shepard_options_title: str = "Show similarity on:"
		self._shepard_options: list[str] = [
			"X-axis (horizontal)",
			"Y-axis (vertical)"]

		self.shepard_axis: str = ""
		return

	# ------------------------------------------------------------------------

	def execute(
		self,
		common: Spaces,
		axis_for_similarities: str = "",
	) -> None:
		self._director.record_command_as_selected_and_in_process()
		self._director.optionally_explain_what_command_does()

		# Get command parameters and capture state
		params = common.get_command_parameters(
			"Shepard", axis=axis_for_similarities)
		axis_for_similarities = params["axis"]
		common.capture_and_push_undo_state("Shepard", "passive", params)

		self._director.dependency_checker.detect_dependency_problems()
		self.shepard_axis: str = axis_for_similarities
		self._director.common.shepard_axis = axis_for_similarities

		self._director.common.create_plot_for_tabs("shepard")
		self._director.title_for_table_widget = (
			"Rank of similarity above diagonal, "
			"rank of distance below diagonal")
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.record_command_as_successfully_completed()
		return


# --------------------------------------------------------------------------


class StressContributionCommand:
	"""The Stress contribution command assesses
	label_item_selected_for_stress_contribution to lack of fit.
	The Stress command is used to identify points with high
	contribution to the lack of fit. The user will be shown all the pairs
	that include a label_item_selected_for_stress_contribution in a plot
	showing rank of similarity and rank of distance between the points.
	"""

	def __init__(self, director: Status, common: Spaces) -> None:
		self._director = director
		self.common = common
		self._director.command = "Stress contribution"

		return

	# ------------------------------------------------------------------------

	def execute(self, common: Spaces) -> None:  # noqa: ARG002
		self._director.record_command_as_selected_and_in_process()
		self._director.optionally_explain_what_command_does()
		self._director.dependency_checker.detect_dependency_problems()
		worst_fit = self._calculate_and_sort_stress_contributions()
		self._print_highest_stress_contributions(worst_fit)
		params = common.get_command_parameters("Stress contribution")
		common.capture_and_push_undo_state(
			"Stress contribution", "passive", params)
		index = params["focal_item"]
		self.stress_contribution_df = (
			self._create_stress_contribution_df(index, worst_fit))
		point_labels = self._director.configuration_active.point_labels
		self._point_to_plot_label = point_labels[index]
		self._point_to_plot_index = index
		self._director.common.create_plot_for_tabs("stress_contribution")
		point_names = self._director.configuration_active.point_names
		self._director.title_for_table_widget = (
			f"Stress contribution of {point_names[index]}")
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.record_command_as_successfully_completed()
		return

	# ------------------------------------------------------------------------

	def _calculate_and_sort_stress_contributions(self) -> list[float]:
		ranks_df = self._director.similarities_active.ranks_df

		worst_fit: list[float] = []
		ranks_df["Absolute_Difference"] = abs(ranks_df["AB_Rank_Difference"])
		ranks_df["Pct_of_Stress"] = ranks_df["Absolute_Difference"]
		total_differences: float = np.sum(ranks_df["Pct_of_Stress"])
		ranks_df["Pct_of_Stress"] = (
			ranks_df["Pct_of_Stress"] / total_differences
		) * 100
		sorted_dyads: pd.DataFrame = ranks_df.sort_values(
			by="Absolute_Difference", ascending=False
		)
		worst_fit: pd.DataFrame = sorted_dyads[
			[
				"A_label",
				"B_label",
				"Similarity_Rank",
				"Distance_Rank",
				"Pct_of_Stress",
			]
		]

		self._director.similarities_active.ranks_df = ranks_df

		return worst_fit

	# ------------------------------------------------------------------------

	def _create_stress_contribution_df(
		self, index: int, worst_fit: pd.DataFrame
	) -> pd.DataFrame:
		"""
		Create a DataFrame showing stress contribution between selected point
		and all other points.

		Parameters:
		-----------
		index : int
			Index of the selected focal point
		worst_fit : DataFrame
			DataFrame containing stress contribution data

		Returns:
		--------
		pandas.DataFrame
			DataFrame with columns 'Item' and 'Stress Contribution',
			sorted by contribution
		"""
		point_names = self._director.configuration_active.point_names
		point_labels = self._director.configuration_active.point_labels
		focal_label = point_labels[index]

		contributions = []
		label_to_name_map = self._create_label_to_name_mapping(
			point_labels, point_names
		)

		for _, row in worst_fit.iterrows():
			other_label = self._get_other_label_if_focal_involved(
				row, focal_label
			)
			if other_label:
				other_name = label_to_name_map.get(other_label)
				if other_name:
					contributions.append(
						self._create_contribution_entry(
							other_name, row["Pct_of_Stress"]
						)
					)

		result_df = self._create_and_sort_dataframe(contributions)
		self.stress_contribution_df = result_df
		return result_df

	# ------------------------------------------------------------------------

	def _create_label_to_name_mapping(
		self, point_labels: list[str], point_names: list[str]
	) -> dict[str, str]:
		"""Create a mapping from point labels to point names."""
		return dict(zip(point_labels, point_names, strict=True))

	# ------------------------------------------------------------------------

	def _get_other_label_if_focal_involved(
		self, row: pd.Series, focal_label: str
	) -> str | None:
		"""Return the other label if focal point is involved in this pair."""
		if row["A_label"] == focal_label:
			return row["B_label"]
		if row["B_label"] == focal_label:
			return row["A_label"]
		return None

	# ------------------------------------------------------------------------

	def _create_contribution_entry(
		self, item_name: str, stress_contribution: float
	) -> dict[str, str | float]:
		"""Create a contribution entry dictionary."""
		return {
			"Item": item_name,
			"Stress Contribution": stress_contribution,
		}

	# ------------------------------------------------------------------------

	def _create_and_sort_dataframe(
		self, contributions: list[dict[str, str | float]]
	) -> pd.DataFrame:
		"""Create DataFrame from contributions and sort by stress
		contribution."""
		result_df: pd.DataFrame = pd.DataFrame(contributions)
		if not result_df.empty:
			result_df = result_df.sort_values(
				by="Stress Contribution", ascending=False
			)
		return result_df

	# ------------------------------------------------------------------------

	def _print_highest_stress_contributions(
		self, worst_fit: pd.DataFrame
	) -> None:
		print("\n\tThe following pairs contribute the most to Stress: \n")
		print(worst_fit.head(n=20).to_string(index=False))
		return
