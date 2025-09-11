from __future__ import annotations

# Standard library imports
# import math

# Third-party imports
import numpy as np
import pandas as pd
import peek  # noqa: F401

from PySide6.QtWidgets import QDialog, QTableWidget
from sklearn import manifold

from constants import (
	MINIMUM_ALLOWABLE_CUT_OFF,
	MAXIMUM_ALLOWABLE_CUT_OFF,
	DEFAULT_ALLOWABLE_CUT_OFF,
	IS_CUTOFF_AN_INTEGER,
)

from dialogs import ChoseOptionDialog, SetValueDialog

from exceptions import (
	SelectionError,
	SpacesError,
	# UnderDevelopmentError,
)
from table_builder import StatisticalTableWidget
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
		self._director.cut_point = 0
		self._title: str = "Set cutoff level"
		self._label: str = (
			"If similarities, minimum similarity  points alike"
			"\nIf dis/similarities, maximum dis/similarity"
		)
		self._min_allowed: float = MINIMUM_ALLOWABLE_CUT_OFF
		self._max_allowed: float = MAXIMUM_ALLOWABLE_CUT_OFF
		self._default: float = DEFAULT_ALLOWABLE_CUT_OFF
		self._an_integer: bool = IS_CUTOFF_AN_INTEGER

		return

	# ------------------------------------------------------------------------

	def execute(self, common: Spaces) -> None:  # noqa: ARG002
		self._director.record_command_as_selected_and_in_process()
		self._director.optionally_explain_what_command_does()
		self._director.dependency_checker.detect_dependency_problems()
		# self._director.detect_limitations_violations()
		self._director.common.create_plot_for_plot_and_gallery_tabs("cutoff")
		self._get_cutoff_from_user()
		self._determine_alike_pairs()
		self._print_alike_pairs()
		self._create_alike_table()
		cut_point = self._director.cut_point
		self._director.title_for_table_widget = (
			f"Pairs with similarity using cutoff: {cut_point}"
		)
		self._director.common.create_plot_for_plot_and_gallery_tabs("alike")
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
		# peek("At start of determine_alike_pairs")
		self._determine_alike_pairs_initialize_variables()
		cut_point = self._director.cut_point
		value_type = self._director.similarities_active.value_type
		sorted_pairs = (
			self._director.similarities_active.sorted_similarities_w_pairs
		)
		# peek("In determine_alike_pairs"
		# 	f"\nsorted pairs: \n{sorted_pairs}")
		# Use the filter_pairs_by_cutoff method to get qualifying pairs
		filtered_pairs = self._filter_pairs_by_cutoff(
			sorted_pairs, cut_point, value_type
		)
		n_similar_pairs = len(filtered_pairs)

		# peek("In determine_alike_pairs"
		# 	f"\nfiltered pairs: \n{filtered_pairs}")

		if n_similar_pairs == 0:
			raise SelectionError(
				self.bad_cutoff_value_title, self.bad_cutoff_value_message
			)

		# Store filtered pairs and update coordinate lists for plotting
		self._director.similarities_active.filtered_pairs = filtered_pairs
		# peek("In determine_alike_pairs about to update coordinates")
		self._update_coordinates_for_similar_pairs(filtered_pairs)
		self._director.n_similar_pairs = n_similar_pairs

		# peek("At end of determine_alike_pairs"
		# 	f"Number of similar pairs: {n_similar_pairs}")
		return

	# ------------------------------------------------------------------------

	def _filter_pairs_by_cutoff(
		self, sorted_pairs: list[list], cut_point: float, value_type: str
	) -> list[list]:
		"""Filter pairs based on cutoff criteria and return qualifying
		pairs."""
		filtered_pairs = []
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
		lists in the similarities_active object for plotting.
		"""
		# peek("At top of _update_coordinates_for_similar_pairs"
		# 	f"\nfiltered pairs: \n{filtered_pairs}")
		# Get necessary objects
		similarities_active = self._director.similarities_active
		point_coords = self._director.configuration_active.point_coords
		hor_dim = self._director.common.hor_dim
		vert_dim = self._director.common.vert_dim

		# Clear existing coordinate lists
		similarities_active.a_x_alike = []
		similarities_active.a_y_alike = []
		similarities_active.b_x_alike = []
		similarities_active.b_y_alike = []

		# Get item labels and coordinates
		for pair in filtered_pairs:
			# Each pair contains: [similarity_value, item_a_label,
			# item_b_label, item_a_name, item_b_name]
			item_a_label = pair[1]
			item_b_label = pair[2]

			# Find indices of these items in point_coords
			item_a_index = (
				self._director.configuration_active.point_labels.index(
					item_a_label
				)
			)
			item_b_index = (
				self._director.configuration_active.point_labels.index(
					item_b_label
				)
			)

			# Add coordinates to the lists
			similarities_active.a_x_alike.append(
				point_coords.iloc[item_a_index, hor_dim]
			)
			similarities_active.a_y_alike.append(
				point_coords.iloc[item_a_index, vert_dim]
			)
			similarities_active.b_x_alike.append(
				point_coords.iloc[item_b_index, hor_dim]
			)
			similarities_active.b_y_alike.append(
				point_coords.iloc[item_b_index, vert_dim]
			)
		# peek("At end of _update_coordinates_for_similar_pairs")
		# Coordinates updated for plotting

		return

	# ------------------------------------------------------------------------

	def _print_alike_pairs(self) -> None:
		"""Print information about the cutoff and similar pairs."""
		most_alike_pairs = self._director.similarities_active.filtered_pairs
		cut_point = self._director.cut_point
		print("\tCut point: ", cut_point)
		print(f"\tNumber of similar pairs: {self._director.n_similar_pairs}")

		print(f"\n\t {'Item':<15} {'Paired With':<15} {'Similarity'}")
		print("\t" + "-" * 43)
		for each_pair in range(len(most_alike_pairs)):
			print(
				f"\t {most_alike_pairs[each_pair][3]:<15}"
				f"{most_alike_pairs[each_pair][4]:<15}"
				f"{most_alike_pairs[each_pair][0]:>8.3f}"
			)

		return

	# ------------------------------------------------------------------------

	def _get_cutoff_from_user_initialize_variables(self) -> None:
		self.cutoff_value_needed_title = self._director.command
		self.cutoff_value_needed_message = "Value for cutoff needed"

	# ------------------------------------------------------------------------

	def _get_cutoff_from_user(self) -> None:
		self._get_cutoff_from_user_initialize_variables()
		# command = self._director.command
		title = self._title
		label = self._label
		min_allowed = self._min_allowed
		max_allowed = self._max_allowed
		an_integer = self._an_integer
		default = self._default
		# cut_point = self._director.cut_point

		cutoff_dialog = SetValueDialog(
			title, label, min_allowed, max_allowed, an_integer, default
		)
		result = cutoff_dialog.exec()
		if result == QDialog.Accepted:
			cut_point = cutoff_dialog.getValue()
		else:
			raise SelectionError(
				self.cutoff_value_needed_title,
				self.cutoff_value_needed_message,
			)
		if cut_point == 0:
			raise SelectionError(
				self.cutoff_value_needed_title,
				self.cutoff_value_needed_message,
			)

		self._director.cut_point = cut_point

		# peek(f"\nAt end of _get_cutoff_from_user:"
		# 	f"\n{self._director.cut_point=}")

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
		sorted_similarities_w_pairs = (
			similarities_active.sorted_similarities_w_pairs
		)
		value_type = similarities_active.value_type
		# print(f"\nDEBUG -- in _create_alike_table:"
		# 	f"\n{value_type=}")
		cut_point = self._director.cut_point
		# print(f"\nDEBUG -- also in _create_alike_table:"
		# 	f"\n{sorted_similarities_w_pairs=}")
		# Filter pairs that meet the cutoff criteria
		alike_pairs = []
		for pair in sorted_similarities_w_pairs:
			similarity = pair[0]
			item_a = pair[1]
			item_b = pair[2]

			# Add pairs that meet cutoff criteria based on value_type
			if (value_type == "similarities" and similarity > cut_point) or (
				value_type == "dissimilarities" and similarity < cut_point
			):
				alike_pairs.append((item_a, item_b, similarity))

		# Create the DataFrame with appropriate column name based on value_type
		similarity_column_name = (
			"Similarity" if value_type == "similarities" else "Dis/similarity"
		)
		alike_df = pd.DataFrame(
			alike_pairs,
			columns=["Item", "Paired with", similarity_column_name],
		)

		# Store in the director for later use
		self._director.similarities_active.alike_df = alike_df

		return alike_df

	# ------------------------------------------------------------------------


class ClusterCommand:
	"""The Cluster command - is not yet implemented"""

	def __init__(self, director: Status, common: Spaces) -> None:
		self._director = director
		self.common = common
		self._director.command = "Cluster"

		return

	# ------------------------------------------------------------------------

	def execute(self, common: Spaces) -> None:  # noqa: ARG002
		self._director.record_command_as_selected_and_in_process()
		self._director.optionally_explain_what_command_does()
		self._director.dependency_checker.detect_dependency_problems()
		self._director.title_for_table_widget = (
			"Cluster is under construction - stay tuned, please"
		)
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.record_command_as_successfully_completed()
		return

	# ------------------------------------------------------------------------


class DistancesCommand:
	def __init__(self, director: Status, common: Spaces) -> None:
		"""Distances command - displays a matrix of inter-point distances."""
		self._director = director
		self.common = common
		self._director.command = "Distances"
		self._width = 8
		self._decimals = 2
		self.title_for_table_widget = "Inter-point distances"
		return

	# ------------------------------------------------------------------------

	def execute(self, common: Spaces) -> None:
		self._director.record_command_as_selected_and_in_process()
		self._director.optionally_explain_what_command_does()
		self._director.dependency_checker.detect_dependency_problems()
		self._director.configuration_active.print_the_distances(
			self._width, self._decimals, common
		)
		self._director.common.create_plot_for_plot_and_gallery_tabs(
			"heatmap_dist"
		)
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
		self._width = 8
		self._decimals = 1

		return

	# ------------------------------------------------------------------------

	def execute(self, common: Spaces) -> None:
		# Ensure similarities_candidate is properly set
		# 	self._director.similarities_candidate =
		# self.los(self._director.evaluations_active)
		#
		#
		# self._director.similarities_active =
		# self._director.similarities_candidate
		# if not hasattr(self._director, 'similarities_candidate') or
		# self._director.similarities_candidate is None:

		self._director.record_command_as_selected_and_in_process()
		self._director.optionally_explain_what_command_does()
		self._director.dependency_checker.detect_dependency_problems()
		self._director.similarities_candidate = self.common.los(
			self._director.evaluations_active
		)
		self._duplicate_similarities(common)
		self._director.similarities_candidate.rank_similarities()
		self._director.similarities_candidate.duplicate_ranked_similarities(
			common
		)
		self._director.similarities_active = (
			self._director.similarities_candidate
		)
		self._director.similarities_original = (
			self._director.similarities_candidate
		)
		self._director.similarities_last = (
			self._director.similarities_candidate
		)
		self._director.similarities_active.print_the_similarities(
			self._width, self._decimals, common
		)
		self._director.title_for_table_widget = (
			f"Line of sight:\n"
			f"The {self._director.similarities_active.value_type}"
			f"matrix has {self._director.similarities_active.nreferent}"
			f" items"
		)
		self._director.common.create_plot_for_plot_and_gallery_tabs(
			"similarities"
		)
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.set_focus_on_tab("Plot")
		self._director.record_command_as_successfully_completed()
		return

	# ------------------------------------------------------------------------

	def _duplicate_similarities(self, common: Spaces) -> None:
		(
			self._director.similarities_candidate.similarities_as_dataframe,
			self._director.similarities_candidate.similarities_as_dict,
			self._director.similarities_candidate.similarities_as_list,
			self._director.similarities_candidate.similarities_as_square,
			self._director.similarities_candidate.sorted_similarities_w_pairs,
			self._director.similarities_candidate.ndyad,
			self._director.similarities_candidate.range_dyads,
			self._director.similarities_candidate.range_items,
		) = common.duplicate_in_different_structures(
			self._director.similarities_candidate.similarities,
			self._director.similarities_candidate.item_names,
			self._director.similarities_candidate.item_labels,
			self._director.similarities_candidate.nreferent,
			self._director.similarities_candidate.value_type,
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
		# self._get_pair_from_user(self._paired_title, self._paired_items)
		focal_index = common.get_focal_item_from_user(
			self._paired_title,
			"Select point to view relationships with others",
			self._paired_items,
		)

		self._focal_item_index = focal_index
		self._create_paired_dataframe()
		self._print_paired()
		point_names = self._director.configuration_active.point_names
		self._director.title_for_table_widget = (
			f"Relationships between {point_names[focal_index]} "
			f"and other points"
		)

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
		similarities_as_dataframe = (
			self._director.similarities_active.similarities_as_dataframe
		)
		value_type = self._director.similarities_active.value_type
		distances_as_dataframe = (
			self._director.configuration_active.distances_as_dataframe
		)

		# Create a list to store data for the DataFrame
		paired_data = []

		# Loop through all points
		for i, name in enumerate(point_names):
			if i != focal_index:  # Skip the focal point itself
				# Get similarity between focal point and this point
				similarity = similarities_as_dataframe.iloc[focal_index, i]

				# Get distance between focal point and this point
				distance = distances_as_dataframe.iloc[focal_index, i]

				# Add to data list
				paired_data.append(
					{
						"Name": name,
						"Similarity": similarity,
						"Distance": distance,
					}
				)

		# Create DataFrame
		paired_df = pd.DataFrame(paired_data)

		# Sort by similarity (ascending or descending based on value_type)
		if value_type == "similarities":
			paired_df = paired_df.sort_values(by="Similarity", ascending=False)
		else:  # "dissimilarities"
			paired_df = paired_df.sort_values(by="Similarity", ascending=True)

		# Store the DataFrame for display
		self._paired_df = paired_df

		return paired_df

	# ------------------------------------------------------------------------

	def _print_paired(self) -> None:
		"""Print the DataFrame showing relationships between the focal
		point and all other points."""

		focal_index = self._focal_item_index
		point_names = self._director.configuration_active.point_names
		value_type = self._director.similarities_active.value_type

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
		display_df = self._paired_df[["Name", "Similarity", "Distance"]]

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

		table_widget = StatisticalTableWidget(self._director)
		gui_output_as_widget = table_widget.display_table("paired")

		self._director.output_widget_type = "Table"
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

	def execute(self, common: Spaces) -> None:  # noqa: ARG002
		self._director.record_command_as_selected_and_in_process()
		self._director.optionally_explain_what_command_does()
		self._director.dependency_checker.detect_dependency_problems()
		# self._create_rank_plot_for_plot_and_gallery_tabs()
		# columns_to_print = \
		# 	self._director.similarities_active.columns_for_ranks[self._columns]
		# print(columns_to_print)
		self._director.common.create_plot_for_plot_and_gallery_tabs(
			"heatmap_rank_diff"
		)
		# "differences")
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

	def execute(self, common: Spaces) -> None:  # noqa: ARG002
		self._director.record_command_as_selected_and_in_process()
		self._director.optionally_explain_what_command_does()
		self._director.dependency_checker.detect_dependency_problems()
		self._director.common.print_lower_triangle(
			self._director.common.decimals,
			self._director.configuration_active.point_labels,
			self._director.configuration_active.point_names,
			self._director.configuration_active.npoint,
			self._director.configuration_active.ranked_distances,
			self._director.common.width,
		)
		self._director.common.create_plot_for_plot_and_gallery_tabs(
			"heatmap_ranked_dist"
		)
		# "ranked_distances")
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

	def execute(self, common: Spaces) -> None:  # noqa: ARG002
		self._director.record_command_as_selected_and_in_process()
		self._director.optionally_explain_what_command_does()
		self._director.dependency_checker.detect_dependency_problems()
		self._director.common.print_lower_triangle(
			self._director.common.decimals,
			self._director.similarities_active.item_labels,
			self._director.similarities_active.item_names,
			self._director.similarities_active.nitem,
			self._director.similarities_active.ranked_similarities,
			self._director.common.width,
		)
		self._director.common.create_plot_for_plot_and_gallery_tabs(
			"heatmap_ranked_simi"
		)
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
			columns=["Dimensionality", "Best Stress"]
		)
		self._dim_names: list[str] = []
		self._dim_labels: list[str] = []
		self._use_metric: bool = False
		self._min_stress: pd.DataFrame = (
			self._director.configuration_active.min_stress
		)
		self._scree_title: str = "MDS model"
		self._scree_options_title: str = "Model to use"
		self._scree_options: list[str] = ["Non-metric", "Metric"]

		return

	# ------------------------------------------------------------------------

	def execute(self, common: Spaces) -> None:  # noqa: ARG002
		self._director.record_command_as_selected_and_in_process()
		self._director.optionally_explain_what_command_does()
		self._director.dependency_checker.detect_dependency_problems()
		self._get_model_for_scree_diagram(
			self._scree_title, self._scree_options_title, self._scree_options
		)
		self._scree()
		self._director.common.create_plot_for_plot_and_gallery_tabs("scree")
		self._director.title_for_table_widget = "Best stress by dimensionality"
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.record_command_as_successfully_completed()
		return

	# ------------------------------------------------------------------------

	def _get_model_for_scree_diagram_initialize_variables(self) -> None:
		self.need_model_for_scree_error_title = self._director.command
		self.need_model_for_scree_error_message = (
			"A model is needed to use in creating scree diagram."
		)

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
		if result == QDialog.Accepted:
			selected_option = dialog.selected_option  # + 1
			match selected_option:
				case 0:
					use_metric = False
				case 1:
					use_metric = True
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

		self._use_metric = use_metric
		self._director.common._use_metric = use_metric

		return

	# -------------------------------------------------------------------------

	def _scree(self) -> None:
		similarities_as_square = (
			self._director.similarities_active.similarities_as_square
		)
		min_stress = self._min_stress

		dim_names = []
		dim_labels = []

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

		self.point_coords = point_coords
		self._dim_names = dim_names
		self._dim_labels = dim_labels
		self.best_stress = best_stress
		self._min_stress = min_stress
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
			"Y-axis (vertical)",
		]

		self.shepard_axis: str = ""
		return

	# ------------------------------------------------------------------------

	def execute(
		self,
		common: Spaces,  # noqa: ARG002
		axis: str,
	) -> None:
		self._director.record_command_as_selected_and_in_process()
		self._director.optionally_explain_what_command_does()
		self._director.dependency_checker.detect_dependency_problems()
		self.shepard_axis = axis
		self._director.common.shepard_axis = axis
		self._director.common.create_plot_for_plot_and_gallery_tabs("shepard")
		self._director.title_for_table_widget = (
			"Rank of similarity above diagonal, "
			"rank of distance below diagonal"
		)
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
		self._contributions_title: str = "Contribution to stress"
		self._contributions_label: str = (
			"Select point to see stress contribution"
		)
		self._contributions_items: list[str] = (
			self._director.configuration_active.point_names
		)
		self._worst_fit = pd.DataFrame()

		return

	# ------------------------------------------------------------------------

	def execute(self, common: Spaces) -> None:  # noqa: ARG002
		self._director.record_command_as_selected_and_in_process()
		self._director.optionally_explain_what_command_does()
		self._director.dependency_checker.detect_dependency_problems()
		worst_fit = self._calculate_and_sort_stress_contributions()
		self._print_highest_stress_contributions(worst_fit)
		self._director.configuration_active.print_the_configuration()

		# Get the item using the common get_focal_item_from_user method
		index = self.common.get_focal_item_from_user(
			self._contributions_title,
			self._contributions_label,
			self._contributions_items,
		)

		stress_contribution_df = self._create_stress_contribution_df(
			index, worst_fit
		)
		self._director.similarities_active.stress_contribution_df = (
			stress_contribution_df
		)

		# Get the label based on the returned index
		point_labels = self._director.configuration_active.point_labels
		point_to_plot_label = point_labels[index]

		# Store the values with original names
		self._point_to_plot_label = point_to_plot_label
		self._point_to_plot_index = index

		self._director.common.create_plot_for_plot_and_gallery_tabs(
			"stress_contribution"
		)
		point_names = self._director.configuration_active.point_names
		self._director.title_for_table_widget = (
			f"Stress contribution of {point_names[index]}"
		)

		self._director.create_widgets_for_output_and_log_tabs()
		self._director.record_command_as_successfully_completed()

		self._worst_fit = worst_fit
		self._director.current_command._point_to_plot_label = (
			point_to_plot_label
		)
		self._director.current_command._point_to_plot_index = index
		self._director.common.point_to_plot_label = point_to_plot_label
		return

	# ------------------------------------------------------------------------

	def _calculate_and_sort_stress_contributions(self) -> list[float]:
		ranks_df = self._director.similarities_active.ranks_df

		worst_fit: list[float] = []
		ranks_df["Absolute_Difference"] = abs(ranks_df["AB_Rank_Difference"])
		ranks_df["Pct_of_Stress"] = ranks_df["Absolute_Difference"]
		total_differences = np.sum(ranks_df["Pct_of_Stress"])
		print(
			f"\nDEBUG -- in middle of _calculate_and_sort..."
			f"\n{total_differences=}"
		)
		ranks_df["Pct_of_Stress"] = (
			ranks_df["Pct_of_Stress"] / total_differences
		) * 100
		print(f"\n\nDEBUG -- nxt...\n{ranks_df['Pct_of_Stress'].sum()=}")
		sorted_dyads = ranks_df.sort_values(
			by="Absolute_Difference", ascending=False
		)
		worst_fit = sorted_dyads[
			[
				"A_label",
				"B_label",
				"Similarity_Rank",
				"Distance_Rank",
				"Pct_of_Stress",
			]
		]

		self._director.similarities_active.ranks_df = ranks_df

		print(
			"\nDEBUG -- at bottom of _calculate_and_sort_stress_contributions"
		)
		print(f"\nDEBUG -- worst_fit:\n{worst_fit}")

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
		# focal_name = point_names[index]
		focal_label = point_labels[index]

		# Filter worst_fit to only include rows where the selected point
		#  is involved
		contributions = []

		for _, row in worst_fit.iterrows():
			# Check if focal point is involved in this pair as A
			if row["A_label"] == focal_label:
				other_label = row["B_label"]
				# Find the name corresponding to this label
				other_name = None
				for i, label in enumerate(point_labels):
					if label == other_label:
						other_name = point_names[i]
						break

				if other_name:
					contributions.append(
						{
							"Item": other_name,
							"Stress Contribution": row["Pct_of_Stress"],
						}
					)

			# Check if focal point is involved in this pair as B
			if row["B_label"] == focal_label:
				other_label = row["A_label"]
				# Find the name corresponding to this label
				other_name = None
				for i, label in enumerate(point_labels):
					if label == other_label:
						other_name = point_names[i]
						break

				if other_name:
					contributions.append(
						{
							"Item": other_name,
							"Stress Contribution": row["Pct_of_Stress"],
						}
					)

		# Create DataFrame and sort by stress contribution (descending)
		result_df = pd.DataFrame(contributions)
		if not result_df.empty:
			result_df = result_df.sort_values(
				by="Stress Contribution", ascending=False
			)

		self.stress_contribution_df = result_df
		return result_df

	# ------------------------------------------------------------------------

	def _print_highest_stress_contributions(
		self, worst_fit: pd.DataFrame
	) -> None:
		print("\n\tThe following pairs contribute the most to Stress: \n")
		print(worst_fit.head(n=20))
		return
