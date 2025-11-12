from __future__ import annotations

import copy
import math
from pathlib import Path

import numpy as np
import pandas as pd
import peek

import scipy.stats as ss

from experimental import ItemFrame
from geometry import PeoplePoints
from typing import TYPE_CHECKING

if TYPE_CHECKING:
	from common import Spaces
	from director import Status
# from constants import (
#     MAXIMUM_NUMBER_OF_DIMENSIONS_FOR_PLOTTING,
# )

from exceptions import DependencyError, SpacesError

# --------------------------------------------------------------------------


class ConfigurationFeature:
	def __init__(self, director: Status) -> None:  # xxxxxxxxxx
		self._director = director
		self._director.title_for_table_widget = ""
		self._hor_dim = director.common.hor_dim
		self._vert_dim = director.common.vert_dim

		self.nreferent: int = 0
		self.npoint: int = 0
		self.npoints: int = 0
		self.range_points: range = range(0)
		self.point_names: list[str] = []
		self.point_labels: list[str] = []
		self.point_coords: pd.DataFrame = pd.DataFrame()
		self.config_as_itemframe: ItemFrame = ItemFrame()
		self.ndim: int = 0
		self.dim_names: list[str] = []
		self.dim_labels: list[str] = []
		self.range_dims: range = range(0)

		# self.hor_axis_name: str = "Unknown"   # ???????????????????????
		# self.vert_axis_name: str = "Unknown"   # ??????????????????????
		self.hor_axis_name: str = ""
		self.vert_axis_name: str = ""

		_min: float = 0.0  # the vertical minimum for plot

		self.distances: list[float] = []
		self.range_distances: range = range(0)
		self.distances_as_dict: dict = {}
		self.distances_as_list: list[float] = []
		self.distances_as_square: list[list[float]] = []
		self.distances_as_dataframe: pd.DataFrame = pd.DataFrame()
		# self.sorted_distances_w_pairs: list = []
		self.sorted_distances = {}
		self.sorted_distances_in_numpy = []
		self.ranked_distances: list[int] = []
		self.ranked_distances_as_list: list = [int]
		self.ranked_distances_as_square: list[list[int]] = []
		self.ranked_distances_as_dict: dict = {}
		self.ranked_distances_as_dataframe = pd.DataFrame()
		self.ndyad: int = 0
		self.range_dyads: range = range(0)
		self.ranks_df: pd.DataFrame = pd.DataFrame()
		# Pandas data frame used for advanced computations on dyads
		self.ev: pd.DataFrame = pd.DataFrame()
		# Pandas data framer used for evaluations
		self.first: pd.DataFrame = pd.DataFrame()
		self.second: pd.DataFrame = pd.DataFrame()
		self.segments: pd.DataFrame = pd.DataFrame()
		self.score_1_name: str = ""
		self.score_2_name: str = ""
		# self.nscored_individ: int = 0
		self.best_stress: int = -1
		self.n_comp: int = 0
		self.use_metric: bool = False
		# self.min_stress: list = []
		self.offset: float = 0.0
		# self.sample_design: pd.DataFrame = pd.DataFrame()

		self.item_labels: list[str] = []
		self.item_names: list[str] = []
		self.eigen: pd.DataFrame = pd.DataFrame()

		return

	# ------------------------------------------------------------------------

	def _populate_base_groups_to_show(
		self, base_groups_to_show: list[str]
	) -> PeoplePoints:
		director = self._director
		common = director.common
		rivalry = director.rivalry

		if base_groups_to_show == "regions":
			return PeoplePoints([], [])
		if not common.have_scores():
			title = "No scores available for plotting"
			message = "Establish scores before plotting base groups"
			raise DependencyError(title, message)

		x = []
		y = []
		base_dict = {
			"left": (rivalry.base_left._points.x, rivalry.base_left._points.y),
			"right": (
				rivalry.base_right._points.x,
				rivalry.base_right._points.y,
			),
			"both": (
				rivalry.base_left._points.x + rivalry.base_right._points.x,
				rivalry.base_left._points.y + rivalry.base_right._points.y,
			),
			"neither": (
				rivalry.base_neither._points.x,
				rivalry.base_neither._points.y,
			),
		}
		x = base_dict[base_groups_to_show][0]
		y = base_dict[base_groups_to_show][1]

		return PeoplePoints(x, y)

	# ------------------------------------------------------------------------

	def _populate_battleground_groups_to_show(
		self, battleground_groups_to_show: str
	) -> PeoplePoints:
		director = self._director
		common = director.common
		rivalry = director.rivalry

		if battleground_groups_to_show == "regions":
			return PeoplePoints([], [])
		if not common.have_scores():
			title = "No scores available for plotting"
			message = "Establish scores before plotting battleground groups"
			raise DependencyError(title, message)

		x = []
		y = []
		battleground_dict = {
			"battleground": (
				rivalry.battleground_segment._points.x,
				rivalry.battleground_segment._points.y,
			),
			"settled": (
				rivalry.battleground_settled._points.x,
				rivalry.battleground_settled._points.y,
			),
		}
		x = battleground_dict[battleground_groups_to_show][0]
		y = battleground_dict[battleground_groups_to_show][1]

		return PeoplePoints(x, y)

	# ------------------------------------------------------------------------

	def _populate_convertible_groups_to_show(
		self, convertible_groups_to_show: str
	) -> PeoplePoints:
		director = self._director
		common = director.common
		rivalry = director.rivalry

		if convertible_groups_to_show == "regions":
			return PeoplePoints([], [])
		if not common.have_scores():
			title = "No scores available for plotting"
			message = "Establish scores before plotting convertible groups"
			raise DependencyError(title, message)

		x = []
		y = []
		convertible_dict = {
			"left": (
				rivalry.convertible_to_left._points.x,
				rivalry.convertible_to_left._points.y,
			),
			"right": (
				rivalry.convertible_to_right._points.x,
				rivalry.convertible_to_right._points.y,
			),
			"both": (
				rivalry.convertible_to_left._points.x
				+ rivalry.convertible_to_right._points.x,
				rivalry.convertible_to_left._points.y
				+ rivalry.convertible_to_right._points.y,
			),
			"settled": (
				rivalry.convertible_settled._points.x,
				rivalry.convertible_settled._points.y,
			),
		}
		x = convertible_dict[convertible_groups_to_show][0]
		y = convertible_dict[convertible_groups_to_show][1]

		# rivalry.segments = segments

		return PeoplePoints(x, y)

	# ------------------------------------------------------------------------

	def _populate_core_groups_to_show(
		self, core_groups_to_show: str
	) -> PeoplePoints:
		director = self._director
		common = director.common
		segments = director.rivalry.seg
		score_1_name = director.current_command._score_1_name
		score_2_name = director.current_command._score_2_name
		nscored = director.current_command._nscored_individ
		in_group = common.in_group

		if core_groups_to_show == "regions":
			return PeoplePoints([], [])
		if not common.have_scores():
			title = "No scores available for plotting"
			message = "Establish scores before plotting core groups"
			raise DependencyError(title, message)

		x = []
		y = []

		core_dict = {
			"left": (
				in_group(segments, nscored, score_1_name, "Core", {1}),
				in_group(segments, nscored, score_2_name, "Core", {1}),
			),
			"right": (
				in_group(segments, nscored, score_1_name, "Core", {3}),
				in_group(segments, nscored, score_2_name, "Core", {3}),
			),
			"both": (
				in_group(segments, nscored, score_1_name, "Core", {1, 3}),
				in_group(segments, nscored, score_2_name, "Core", {1, 3}),
			),
			"neither": (
				in_group(segments, nscored, score_1_name, "Core", {2}),
				in_group(segments, nscored, score_2_name, "Core", {2}),
			),
		}
		x = core_dict[core_groups_to_show][0]
		y = core_dict[core_groups_to_show][1]

		return PeoplePoints(x, y)

	# ---------------------------------------------------------------------

	def _populate_first_dim_groups_to_show(
		self, first_dim_groups_to_show: str
	) -> PeoplePoints:
		# segments = self._director.current_command._seg
		# score_1_name = self._director.current_command._score_1_name
		# score_2_name = self._director.current_command._score_2_name
		# nscored = self._director.current_command._nscored_individ

		director = self._director
		common = director.common
		rivalry = director.rivalry

		if first_dim_groups_to_show == "regions":
			return PeoplePoints([], [])
		if not common.have_scores():
			title = "No scores available for plotting"
			message = "Establish scores before plotting first dimension groups"
			raise DependencyError(title, message)
		x = []
		y = []
		first_dict = {
			"left": (
				rivalry.first_left._points.x,
				rivalry.first_left._points.y,
			),
			"right": (
				rivalry.first_right._points.x,
				rivalry.first_right._points.y,
			),
		}
		x = first_dict[first_dim_groups_to_show][0]
		y = first_dict[first_dim_groups_to_show][1]

		return PeoplePoints(x, y)

	# ------------------------------------------------------------------------

	def _populate_likely_groups_to_show(
		self, likely_groups_to_show: str
	) -> PeoplePoints:
		director = self._director
		common = director.common
		rivalry = director.rivalry
		# likely_groups_to_show = \
		# 	self._director.current_command.likely_groups_to_show
		likely_left = rivalry.likely_left
		likely_right = rivalry.likely_right

		if likely_groups_to_show == "regions":
			return PeoplePoints([], [])
		if not common.have_scores():
			title = "No scores available for plotting"
			message = "Establish scores before plotting likely groups"
			raise DependencyError(title, message)
		x = []
		y = []

		likely_dict = {
			"left": (likely_left._points.x, likely_left._points.y),
			"right": (likely_right._points.x, likely_right._points.y),
			"both": (
				likely_left._points.x + likely_right._points.x,
				likely_left._points.y + likely_right._points.y,
			),
		}
		x = likely_dict[likely_groups_to_show][0]
		y = likely_dict[likely_groups_to_show][1]

		return PeoplePoints(x, y)

	# -------------------------------------------------------------------------

	def _populate_second_dim_groups_to_show(
		self, second_dim_groups_to_show: str
	) -> PeoplePoints:
		director = self._director
		common = director.common
		rivalry = director.rivalry

		if second_dim_groups_to_show == "regions":
			return PeoplePoints([], [])
		if not common.have_scores():
			title = "No scores available for plotting"
			message = (
				"Establish scores before plotting second dimension groups"
			)
			raise DependencyError(title, message)

		x = []
		y = []
		second_dict = {
			"upper": (
				rivalry.second_up._points.x,
				rivalry.second_up._points.y,
			),
			"lower": (
				rivalry.second_down._points.x,
				rivalry.second_down._points.y,
			),
		}

		x = second_dict[second_dim_groups_to_show][0]
		y = second_dict[second_dim_groups_to_show][1]

		return PeoplePoints(x, y)

	# ------------------------------------------------------------------------

	def inter_point_distances_initialize_variables(
		self,
	) -> tuple[list[float], list[float], float]:
		self.distances.clear()
		self.distances_as_dict = {}
		self.distances_as_list.clear()
		self.distances_as_square.clear()
		self.distances_as_dataframe = pd.DataFrame()
		self.ranked_distances.clear()
		self.ranked_distances_as_list = []
		self.ranked_distances_as_square.clear()
		self.ranked_distances_as_dict = {}
		self.ranked_distances_as_dataframe = pd.DataFrame()
		diffs = []
		sqs = []
		sumofsqs = 0

		return diffs, sqs, sumofsqs

	# ------------------------------------------------------------------------

	def inter_point_distances(self) -> None:
		npoint = self.npoint
		point_names = self.point_names
		point_labels = self.point_labels
		point_coords = self.point_coords
		nreferent = self.nreferent
		range_points = self.range_points
		range_dims = self.range_dims
		distances = [] # self.distances
		distances_as_list = [] #self.distances_as_list
		distances_as_dict = {} # self.distances_as_dict
		distances_as_square = [] # self.distances_as_square
		# range_distances = self.range_distances
		# sorted_distances = self.sorted_distances

		# calculate the inter-point distances in separate function??

		if npoint == 0:
			npoint = nreferent

		distances_as_list, distances_as_dict, distances = (
			self.calculate_inter_point_distances(
				point_coords, point_labels, npoint, range_dims
			)
		)

		sorted_distances = dict(
			sorted(distances_as_dict.items(), key=lambda x: x[1])
		)

		nreferent = npoint

		# _item_labels = point_labels ????????
		item_names = point_names
		item_labels = point_labels
		ndyad = int(nreferent * (nreferent - 1) / 2)
		range_distances = range(ndyad)
		#
		# create distances-as-square a full, upper and lower, matrix,
		#
		# self.range_items = range(len(self.item_labels))
		# range_points = range(nreferent)

		for each_point in range_points:
			distances_as_square.append([])
			for other_point in range_points:
				if each_point == other_point:
					# self.distances_as_square[each_item][other_item] = 0.0
					distances_as_square[other_point].append(0.0)
				elif each_point < other_point:
					index = str(
						point_labels[each_point]
						+ "_"
						+ point_labels[other_point]
					)
					distances_as_square[each_point].append(
						distances_as_dict[index]
					)
				else:
					index = str(
						point_labels[other_point]
						+ "_"
						+ point_labels[each_point]
					)
					distances_as_square[each_point].append(
						distances_as_dict[index]
					)
		#
		self.distances_as_dataframe = pd.DataFrame(
			distances_as_square, columns=point_names, index=point_names
		)

		self.distances_as_list = distances_as_list  # this is the fix

		self.rank_distances()

		# self.range_points = range_points
		self.distances = distances
		self.distances_as_dict = distances_as_dict
		self.distances_as_list = distances_as_list
		self.distances_as_square = distances_as_square
		self.sorted_distances = sorted_distances
		self.range_distances = range_distances
		self.point_coords = point_coords
		self.npoints = npoint
		self.nreferent = nreferent
		self.item_names = item_names
		self.item_labels = item_labels
		self.ndyad = ndyad

		return

	# ------------------------------------------------------------------------

	def calculate_inter_point_distances(
		self,
		point_coords: pd.DataFrame,
		point_labels: list[str],
		npoint: int,
		range_dims: range,
	) -> tuple[list, dict, list[list[float]]]:

		distances_as_list: list[float] = []
		distances_as_dict: dict = {}
		distances: list[list[float]] = []

		diffs, sqs, sumofsqs = (
			self.inter_point_distances_initialize_variables()
		)
		from_pts_range = range(1, npoint)
		for from_pts in from_pts_range:
			a_row = []
			to_pts_range = range(from_pts)
			for to_pts in to_pts_range:
				for each_dim in range_dims:
					diffs.append(
						point_coords.iloc[from_pts, each_dim]
						- point_coords.iloc[to_pts, each_dim]
					)
					sqs.append(
						(
							point_coords.iloc[from_pts, each_dim]
							- point_coords.iloc[to_pts, each_dim]
						)
						* (
							point_coords.iloc[from_pts, each_dim]
							- point_coords.iloc[to_pts, each_dim]
						)
					)
					sumofsqs += sqs[each_dim]
				distpts = math.sqrt(sumofsqs)
				distances_as_list.append(distpts)
				a_row.append(distpts)
				dist_key = str(
					point_labels[to_pts] + "_" + point_labels[from_pts]
				)
				distances_as_dict[dist_key] = distpts
				diffs = []
				sqs = []
				sumofsqs = 0
			distances.append(a_row)

		return distances_as_list, distances_as_dict, distances

	# ------------------------------------------------------------------------
	def rank_distances(self) -> None:

		point_names = self.point_names
		point_labels = self.point_labels
		range_points = self.range_points
		npoint = self.npoint

		# ???????????????????????????
		# nreferent = self.nreferent
		distances = self.distances
		ranked_distances = self.ranked_distances
		ranked_distances_as_dict = self.ranked_distances_as_dict
		ranked_distances_as_square = self.ranked_distances_as_square

		ranked_distances_as_list = ss.rankdata(self.distances_as_list)

		next_pair = 0
		from_pts_range = range(1, npoint)
		for from_pts in from_pts_range:
			a_row = []
			to_pts_range = range(from_pts)
			for to_pts in to_pts_range:
				rank = ranked_distances_as_list[next_pair]
				next_pair += 1
				a_row.append(rank)
				key = str(point_labels[to_pts] + "_" + point_labels[from_pts])
				ranked_distances_as_dict[key] = rank
			ranked_distances.append(a_row)
		# self.range_points = range(nreferent)
		for each_point in range_points:
			ranked_distances_as_square.append([])
			for other_point in range_points:
				if each_point == other_point:
					# self.ranked_distances_as_square[
					# other_point].append("---")
					ranked_distances_as_square[other_point].append(0)
				elif each_point < other_point:
					index = str(
						point_labels[each_point]
						+ "_"
						+ point_labels[other_point]
					)
					ranked_distances_as_square[each_point].append(
						ranked_distances_as_dict[index]
					)
				else:
					index = str(
						point_labels[other_point]
						+ "_"
						+ point_labels[each_point]
					)
					ranked_distances_as_square[each_point].append(
						ranked_distances_as_dict[index]
					)

		ranked_distances_as_dataframe = pd.DataFrame(
			ranked_distances_as_square, columns=point_names, index=point_names
		)

		self.distances = distances
		self.ranked_distances = ranked_distances
		self.ranked_distances_as_dict = ranked_distances_as_dict
		self.ranked_distances_as_list = ranked_distances_as_list
		self.ranked_distances_as_square = ranked_distances_as_square
		self.ranked_distances_as_dataframe = ranked_distances_as_dataframe
		return

	# -------------------------------------------------------------------------

	def print_active_function(self) -> None:
		"""print active function - is used by many commands to print the
		active configuration.
		"""
		print(self.point_coords.to_string(float_format="{:.2f}".format))
		# print(self.point_coords.index.format())
		return

	# ------------------------------------------------------------------------

	def print_the_configuration(self) -> None:
		ndim = self.ndim
		npoint = self.npoint
		point_coords = self.point_coords
		print(f"\n\tConfiguration has {ndim} dimensions and {npoint} points\n")
		point_coords.style.format(precision=3, thousands=",", decimal=".")
		self.print_active_function()
		return

	# ------------------------------------------------------------------------

	def print_the_distances(
		self, width: int, decimals: int, common: Spaces
	) -> None:
		point_labels = self.point_labels
		point_names = self.point_names
		npoint = self.npoint
		distances = self.distances

		print("\n\tDistances between points in the active configuration\n")
		common.print_lower_triangle(
			decimals, point_labels, point_names,
			npoint, distances, width
		)
		return

	# -------------------------------------------------------------------------

	def write_a_configuration_type_file_initialize_variables(self) -> None:
		self.conf_file_exists_error_title = "File exists"
		self.conf_file_exists_error_message = (
			"File already exists\n"
			"Choose a different file name or delete the existing file."
		)

	# ------------------------------------------------------------------------

	def write_a_configuration_type_file(
		self, file_name: str, source: ConfigurationFeature
	) -> None:
		# dropped positional arguments message and feedback

		self.write_a_configuration_type_file_initialize_variables()

		file_type: str = "Configuration"
		try:
			with Path(file_name).open("w") as file_handle:
				file_handle.write(file_type + "\n")
				file_handle.write(
					" " + str(source.ndim) + \
					" " + str(source.npoint) + "\n"
				)
				lines = [
					f"{source.dim_labels[each_dim]};"
					f"{source.dim_names[each_dim].strip()}\n"
					for each_dim in source.range_dims
				]
				file_handle.write("".join(lines))
				lines = [
					f"{source.point_labels[each_point]};"
					f"{source.point_names[each_point]}\n"
					for each_point in source.range_points
				]
				file_handle.write("".join(lines))
				for each_point in source.range_points:
					for each_dim in source.range_dims:
						file_handle.write(
							str(
								source.point_coords.iloc[each_point].iloc[
									each_dim
								]
							)
							+ " "
						)
						continue
					file_handle.write("\n")
					continue

		except SpacesError as exc:
			# except SituationToBeNamedLaterError:
			# peek("Do we get past Qt")
			raise SpacesError(
				self.conf_file_exists_error_title,
				self.conf_file_exists_error_message,
			) from exc
		return

	# ------------------------------------------------------------------------


class CorrelationsFeature:
	def __init__(self, director: Status) -> None:
		self._director = director
		self.title_for_table_widget: str = ""
		self.file_handle: str = ""
		self.nreferent: int = 0
		self.npoints: int = 0
		self.nitem: int = 0  # replaces self.nitem_corr
		self.range_items: range = range(0)
		# replaces self.range_correlations & self.range_items_corr
		self.item_names: list[str] = []  # replaces self.item_names_corr
		self.item_labels: list[str] = []  # replaces self.item_labels_corr
		self.ncorrelations: int = 0  # replaces self.n_correlations
		self.correlations: list[list[float]] = []  # kept from previous
		self.correlations_as_list: list = []  # kept from previous
		self.correlations_as_dict: dict = {}  # kept from previous
		self.correlations_as_square: list[list[float]] = []
		# kept from previous
		self.correlations_as_dataframe: pd.DataFrame = pd.DataFrame()
		# kept from previous
		self.sorted_correlations: dict = {}  # kept from previous
		self.sorted_correlations_w_pairs: list = []

		self.ndyad: int = 0  # kept from previous
		self.range_dyads: range = range(0)
		self.n_pairs: int = 0  # kept from previous
		self.range_pairs: range = range(0)  # kept from previous
		self.a_item_names: list[str] = []  # replaces self.a_item_names_corr
		self.b_item_names: list[str] = []  # replaces self.b_item_names_corr
		self.a_item_labels: list[str] = []  # replaces self.a_item_labels_corr
		self.b_item_labels: list[str] = []  # replaces self.b_item_labels_corr
		self.a_item_name: str = ""  # the name of the first item
		self.b_item_name: str = ""  # the name of the second item
		self.a_item_label: str = ""  # the label of the first item
		self.b_item_label: str = ""  # the label of the second item

	# ------------------------------------------------------------------------

	def duplicate_correlations(self, common: Spaces) -> None:
		(
			self.correlations_as_dataframe,
			self.correlations_as_dict,
			self.correlations_as_list,
			self.correlations_as_square,
			self.sorted_correlations_w_pairs,
			self.ndyad,
			self.range_dyads,
			self.range_items,
		) = common.duplicate_in_different_structures(
			self.correlations,
			self.item_names,
			self.item_labels,
			self.nreferent,
			"dissimilarities",
		)

	# ------------------------------------------------------------------------

	def print_the_correlations(
		self, width: int, decimals: int, common: Spaces
	) -> None:
		item_labels = self.item_labels
		item_names = self.item_names
		nitem = self.nitem
		correlations = self.correlations

		print("\n\tThe correlation matrix has", self.nitem, "items")
		common.print_lower_triangle(
			decimals, item_labels, item_names, nitem, correlations, width
		)

		return

	# ------------------------------------------------------------------------


class EvaluationsFeature:
	def __init__(self, director: Status) -> None:
		self._director = director
		self.file_handle: str = ""
		self.nreferent: int = 0
		self.nitem: int = 0
		self.range_items: range = range(0)
		self.item_names: list[str] = []
		self.item_labels: list[str] = []
		self.nevaluators: int = 0
		self.universe_size: int = 0
		self.evaluations: pd.DataFrame = pd.DataFrame()
		self.stats_eval: pd.DataFrame = pd.DataFrame()
		self.avg_eval: pd.Series = pd.Series()
		# if not self._director.pyqtgraph_common.have_sample_design():
		# self.sample_design: pd.DataFrame = pd.DataFrame()
		# self.sample_repetitions: pd.DataFrame = pd.DataFrame()
		# self.sample_solutions: pd.DataFrame = pd.DataFrame()

	# ------------------------------------------------------------------------

	def print_the_evaluations(self) -> None:
		print("\nEvaluations: \n", self.evaluations)
		# self.evaluate()
		return

	# ------------------------------------------------------------------------

	def summarize_evaluations(self) -> None:
		evaluations = self.evaluations
		# stats_eval = self.stats_eval
		# avg_eval = self.avg_eval
		temp_stats_eval = evaluations.describe(
			percentiles=[0.25, 0.5, 0.75]
		).transpose()
		stats_eval = temp_stats_eval[
			["mean", "std", "min", "max", "25%", "50%", "75%"]
		]
		stats_eval.columns = [
			"Mean",
			"Standard\nDeviation",
			"Min",
			"Max",
			"First\nquartile",
			"Median",
			"Third\nquartile",
		]
		new_order = [
			"Mean",
			"Standard\nDeviation",
			"Min",
			"First\nquartile",
			"Median",
			"Third\nquartile",
			"Max",
		]
		stats_eval = stats_eval.reindex(columns=new_order)
		stats_eval_sorted = stats_eval.sort_values(by="Mean", ascending=False)
		# stats_eval_sorted = pd.DataFrame(stats_eval_sorted)
		names_eval_sorted = stats_eval_sorted.index.tolist()
		# columns = stats_eval_sorted.columns.tolist()

		avg_eval = evaluations.mean()
		avg_eval.sort_values(inplace=True)

		# self.stats_eval = stats_eval
		self.stats_eval_sorted = stats_eval_sorted
		self.names_eval_sorted = names_eval_sorted
		self.avg_eval = avg_eval

		return

	# ------------------------------------------------------------------------


class GroupedDataFeature:
	def __init__(self, director: Status) -> None:
		self._director = director
		self._hor_dim = director.common.hor_dim
		self._vert_dim = director.common.vert_dim
		self.file_handle: str = ""
		# the handle of the grouped configuration file
		self.grouping_var: str = ""
		self.ngroups: int = 0  # replaces npoint_grpd
		self.group_codes: list = []  # replaces point_codes_grpd
		self.range_groups: range = range(0)  # replaces range_points_grpd
		self.ndim: int = 0  # replaces ndim_points_grpd
		self.dim_names: list[str] = []  # replaces dim_names_points_grpd
		self.dim_labels: list[str] = []  # replaces dim_labels_points_grpd
		self.range_dims: range = range(0)  # replaces range_dims_points_grpd
		self.group_names: list[str] = []  # replaces point_names_grpd
		self.group_labels: list[str] = []  # replaces point_labels_grpd
		self.group_coords: pd.DataFrame = pd.DataFrame()

	# ------------------------------------------------------------------------

	def print_grouped_data(self) -> None:
		"""print grouped - is used to print the grouped data configuration."""
		grouping_var = self.grouping_var
		group_coords = self.group_coords
		print(f" Configuration is based on {grouping_var} \n")
		print(group_coords)
		return

	# ------------------------------------------------------------------------

	def write_a_grouped_data_file(
		self, file_name: str, source: GroupedDataFeature
	) -> None:
		"""Write grouped data to a file in configuration format."""
		file_type: str = "Grouped"
		try:
			with Path(file_name).open("w") as file_handle:
				# Line 1: File type
				file_handle.write(file_type + "\n")
				# Line 2: Grouping variable name
				file_handle.write(f"{source.grouping_var}\n")
				# Line 3: Dimensions (ndim ngroups)
				file_handle.write(
					f"   {source.ndim}  {source.ngroups}\n"
				)
				# Next lines: Dimension labels and names
				lines = [
					f"{source.dim_labels[each_dim]};"
					f"{source.dim_names[each_dim].strip()}\n"
					for each_dim in source.range_dims
				]
				file_handle.write("".join(lines))
				# Next lines: Group labels, codes, and names
				lines = [
					f"{source.group_labels[each_group]};"
					f"{source.group_codes[each_group]};"
					f"{source.group_names[each_group]}\n"
					for each_group in source.range_groups
				]
				file_handle.write("".join(lines))
				# Next lines: Coordinates
				for each_group in source.range_groups:
					for each_dim in source.range_dims:
						coord = source.group_coords.iloc[each_group].iloc[
							each_dim
						]
						file_handle.write(f"{coord:6.3f} ")
					file_handle.write("\n")

		except Exception as exc:
			raise SpacesError(
				"File write error",
				"Error writing grouped data file",
			) from exc
		return


# --------------------------------------------------------------------------


class IndividualsFeature:
	def __init__(self, director: Status) -> None:
		self._director = director
		self.file_handle: str = ""
		# the handle of the grouped configuration file
		self.hor_axis_name: str = "Unknown"
		self.vert_axis_name: str = "Unknown"
		self.n_individ: int = 0
		self.nitem: int = 0
		self.range_items: range = range(0)
		self.item_names: list[str] = []
		self.item_labels: list[str] = []
		self.nvar: int = 0
		# replaces self.nvar_ind?? # the number of variables about the people
		self.var_names: list[str] = []
		self.ind_vars: pd.DataFrame = pd.DataFrame()
		self.stats_inds: pd.DataFrame = pd.DataFrame()

	# ------------------------------------------------------------------------

	def print_individuals(self) -> None:
		n_individ = self._director.individuals_active.n_individ
		ind_vars = self._director.individuals_active.ind_vars

		print(f"The file contains {n_individ} individuals.\n")
		print(ind_vars)
		return

	# -----------------------------------------------------------------------


class ScoresFeature:
	def __init__(self, director: Status) -> None:
		self._director = director
		self._hor_dim = self._director.common.hor_dim
		self._vert_dim = self._director.common.vert_dim
		self.scores: pd.DataFrame = pd.DataFrame()
		self.nscores: int = 0
		self.range_scores: range = range(0)
		self.nscored_individ: int = 0
		self.ndim: int = 0
		self.dim_labels: list[str] = []
		self.dim_names: list[str] = []
		self.var_names: list = []
		self.var_labels: list = []
		self.score_1: pd.DataFrame = pd.DataFrame()
		self.score_2: pd.DataFrame = pd.DataFrame()
		self.score_1_name: str = ""
		self.score_2_name: str = ""
		self.score_color: str = "black" # had been "yellow"
		self.hor_axis_name: str = ""
		self.vert_axis_name: str = ""
		self.stats_scores: pd.DataFrame = pd.DataFrame()
		self.avg_scores: pd.DataFrame = pd.DataFrame()
		self.hor_max: float = 0.0
		self.hor_min: float = 0.0
		self.vert_max: float = 0.0
		self.vert_min: float = 0.0
		self.offset: float = 0.0

		self._hor_max: float = 0.0
		self._hor_min: float = 0.0
		self._vert_max: float = 0.0
		self._vert_min: float = 0.0
		self._offset: float = 0.0

		# Cluster-related attributes
		self.cluster_labels: np.ndarray | None = None
		self.cluster_centers: np.ndarray | None = None
		self.n_clusters: int = 0
		self.original_clustered_data: pd.DataFrame | None = None

	# ------------------------------------------------------------------------

	def print_scores(self) -> None:
		scores = self.scores
		columns = self.scores.columns

		print("\n\tFor each individual: ")
		cols = columns
		for i in range(len(cols) - 1):
			print("\t\t", cols[i + 1])
			self.var_names = [] if self.var_names is None else self.var_names
			self.var_names = self.var_names.append(pd.Index([cols[i + 1]]))
		print(scores.head(10).to_string(index=False))

		return

	# ------------------------------------------------------------------------

	def summarize_scores(self) -> None:
		scores = self.scores

		scores_vars = copy.deepcopy(scores)
		scores_vars.drop(scores_vars.columns[0], axis=1, inplace=True)
		floated_vars = scores_vars.astype(float)
		temp_stats_scores = floated_vars.describe(
			percentiles=[0.25, 0.5, 0.75]
		).transpose()

		stats_scores = temp_stats_scores[
			["mean", "std", "min", "max", "25%", "50%", "75%"]
		]

		stats_scores.columns = [
			"Mean",
			"Standard\nDeviation",
			"Min",
			"Max",
			"First\nquartile",
			"Median",
			"Third\nquartile",
		]

		new_order = [
			"Mean",
			"Standard\nDeviation",
			"Min",
			"First\nquartile",
			"Median",
			"Third\nquartile",
			"Max",
		]

		stats_scores = stats_scores.reindex(columns=new_order)
		avg_scores = scores.mean()

		self.stats_scores = stats_scores
		self.avg_scores = avg_scores
		return

	# ------------------------------------------------------------------------


class SimilaritiesFeature:
	def __init__(self, director: Status) -> None:
		# self.nreferent_sims: int = 0 no
		self._director = director
		# self.shepard_axis: str = ""
		self.file_handle: str = ""
		self.value_type: str = ""
		self.nitem: int = 0  # replaces self.nitem_sims
		self.range_items: range = range(0)
		# replaces self.range_similarities & self.range_items_sims
		self.nreferent: int = 0
		self.npoints: int = 0
		self.range_similarities: range = range(0)

		self.item_names: list[str] = []  # replaces self.item_names_sims
		self.item_labels: list[str] = []  # replaces self.item_labels_sims
		self.nsimilarities: int = 0  # replaces self.n_similarities
		self.similarities: list[list[float]] = []  # kept from previous
		self.similarities_as_list: list[int] = []  # kept from previous
		self.similarities_as_dict: dict = {}  # kept from previous
		self.similarities_as_square: list[list[float]] = []
		# kept from previous
		self.similarities_as_dataframe: pd.DataFrame = pd.DataFrame()
		# kept from previous
		self.sorted_similarities: dict = {}  # kept from previous
		self.sorted_similarities_w_pairs: list = []
		# the similarities sorted by value with a and b labels
		self.ranked_similarities: list[int] = []
		self.ranked_similarities_as_list: list[int] = []
		self.ranked_similarities_as_square: list[list[int]] = []
		self.ranked_similarities_as_dict: dict = {}
		self.ranked_similarities_as_dataframe: pd.DataFrame = pd.DataFrame()
		self.sorted_ranked_similarities_w_pairs: list = []
		self.differences_of_ranks_as_list: list[int] = []
		self.differences_of_ranks_as_square: list[list[int]] = []
		self.differences_of_ranks_as_dataframe = pd.DataFrame()
		# self.shepard_diagram_table_as_square
		self.shepard_diagram_table_as_dataframe = pd.DataFrame()
		self.ndyad: int = 0  # kept from previous
		self.range_dyads: range = range(0)  # kept from previous
		self.n_pairs: int = 0  # kept from previous
		self.range_pairs: range = range(0)  # kept from previous
		self.a_item_names: list[str] = []  # replaces self.a_item_names_sims
		self.b_item_names: list[str] = []  # replaces self.b_item_names_sims
		self.a_item_labels: list[str] = []  # replaces self.a_item_labels_sims
		self.b_item_labels: list[str] = []  # replaces self.b_item_labels_sims
		self.a_item_name: str = ""  # the name of the first item
		self.b_item_name: str = ""  # the name of the second item
		self.a_item_label: str = ""  # the label of the first item
		self.b_item_label: str = ""  # the label of the second item
		# self.a_item_label: list[int] = []  # replaces self.a_item_label_sims
		# self.b_item_label: list[int] = []  # replaces self.b_item_label_sims
		# Alike-related attributes moved to AlikeCommand (command instance)
		# self.point_size: int = 15		# the size of the dots representing
		self.ranks_df: pd.DataFrame = pd.DataFrame()
		# Pandas data frame used for advanced computations on dyads
		self.columns_for_ranks: pd.DataFrame = pd.DataFrame()
		# defines the columns in ranks_df to be displayed

		# self.name_item_selected_for_stress_contribution: str = ""
		# self.create_heatmap_plot_for_tabs_using_matplotlib:
		# object = None

	# ------------------------------------------------------------------------

	def compute_differences_in_ranks(self) -> None:

		nreferent = self._director.similarities_active.nreferent
		ranked_similarities_as_list = (
			self._director.similarities_active.ranked_similarities_as_list
		)
		ranked_distances_as_list = (
			self._director.configuration_active.ranked_distances_as_list
		)
		item_names = self._director.similarities_active.item_names

		square = np.empty((nreferent, nreferent))

		differences_of_ranks_as_list = (
			ranked_similarities_as_list - ranked_distances_as_list
		)
		np.set_printoptions(suppress=True)
		next_pair = 0
		from_pts_range = range(1, nreferent)
		for each_item in from_pts_range:
			to_pts_range = range(each_item)
			for that_item in to_pts_range:
				square[each_item][that_item] = differences_of_ranks_as_list[
					next_pair
				]
				square[that_item][each_item] = differences_of_ranks_as_list[
					next_pair
				]
				next_pair += 1

		differences_of_ranks_as_square = square
		differences_of_ranks_as_dataframe = pd.DataFrame(
			differences_of_ranks_as_square,
			columns=item_names,
			index=item_names,
		)

		self._director.similarities_active.differences_of_ranks_as_list = (
			differences_of_ranks_as_list
		)
		self._director.similarities_active.differences_of_ranks_as_square = (
			differences_of_ranks_as_square
		)
		self._director.similarities_active.\
			differences_of_ranks_as_dataframe = \
				differences_of_ranks_as_dataframe

		return

	# ------------------------------------------------------------------------

	def duplicate_similarities(self, common: Spaces) -> None:
		"""Duplicate similarities into various data structures.

		This method uses a utility function from the 'common' object to
		convert the primary similarities list into multiple formats,
		including a DataFrame, dictionary, list, and square matrix.
		These are stored as attributes of the instance.

		Parameters
		----------
		common : Spaces
			An object with utility functions, including
			'duplicate_in_different_structures'.
		"""
		(
			self.similarities_as_dataframe,
			self.similarities_as_dict,
			self.similarities_as_list,
			self.similarities_as_square,
			self.sorted_similarities_w_pairs,
			self.ndyad,
			self.range_dyads,
			self.range_items,
		) = common.duplicate_in_different_structures(
			self.similarities,
			self.item_names,
			self.item_labels,
			self.nitem,
			self.value_type,
		)
		self.range_similarities = self.range_dyads

	# ------------------------------------------------------------------------

	def prepare_for_shepard_diagram(self) -> None:
		nreferent = self._director.similarities_active.nreferent
		ranked_similarities_as_list = (
			self._director.similarities_active.ranked_similarities_as_list
		)
		ranked_distances_as_list = (
			self._director.configuration_active.ranked_distances_as_list
		)
		item_names = self._director.similarities_active.item_names

		pd.set_option("display.float_format", lambda x: f"{x:.2f}")
		shepard_square = np.empty((nreferent, nreferent))
		next_dist = 0
		next_simi = 0
		for each_item in range(nreferent):
			for that_item in range(nreferent):
				if each_item < that_item:
					shepard_square[each_item][that_item] = (
						ranked_similarities_as_list[next_simi]
					)
					next_simi += 1
				elif each_item > that_item:
					shepard_square[each_item][that_item] = (
						ranked_distances_as_list[next_dist]
					)
					next_dist += 1
		shepard_diagram_table_as_square = shepard_square
		shepard_diagram_table_as_dataframe = pd.DataFrame(
			shepard_diagram_table_as_square,
			columns=item_names,
			index=item_names,
		)

		self._director.similarities_active.shepard_diagram_table_as_square = (
			shepard_diagram_table_as_square
		)
		self._director.similarities_active.\
			shepard_diagram_table_as_dataframe = \
				shepard_diagram_table_as_dataframe

		return

	# ------------------------------------------------------------------------

	def print_the_similarities(
		self, width: int, decimals: int, common: Spaces
	) -> None:
		value_type = self.value_type
		nitem = self.nitem
		item_labels = self.item_labels
		item_names = self.item_names
		similarities = self.similarities

		print("\n\tThe", value_type, "matrix has", nitem, "items")
		common.print_lower_triangle(
			decimals, item_labels, item_names,
			nitem, similarities, width
		)
		return

	# ------------------------------------------------------------------------

	def create_ranked_similarities_dataframe(self) -> None:
		
		#
		# Create dataframe which is used for computing and displaying ranks
		# It will start with self.sorted_similarities_w_pairs which has
		# similarities sorted ascending and
		# labels of the items in each pair
		#

		# ranks_df = self._director.similarities_active.ranks_df
		distances_as_dict = (
			self._director.configuration_active.distances_as_dict
		)
		sorted_similarities_w_pairs = self.sorted_similarities_w_pairs
		range_similarities = self.range_similarities
		# columns_for_ranks = self.columns_for_ranks

		range_items = self.range_items
		item_labels = self.item_labels

		ranks_df = pd.DataFrame(
			sorted_similarities_w_pairs,
			columns=["Similarity", "A_label", "B_label", "A_name", "B_name"],
		)
		a_label_index = 1
		b_label_index = 2
		#
		# Rank the similarities
		#
		ranks_df["Similarity_Rank"] = ranks_df["Similarity"].rank(
			method="average"
		)
		#
		# Add and rank the distances
		#
		temp_list = [
			str(
				ranks_df.iloc[each_dyad, a_label_index]
				+ "_"
				+ ranks_df.iloc[each_dyad, b_label_index]
			)
			for each_dyad in range_similarities
		]
		ranks_df["Dyad"] = temp_list
		ranks_df["Distance_AB"] = 0.0
		#
		for each_dyad in range_similarities:
			ranks_df.loc[each_dyad, "Distance_AB"] = distances_as_dict[
				temp_list[each_dyad]
			]
		ranks_df["Distance_Rank"] = ranks_df["Distance_AB"].rank(
			method="average"
		)
		#
		# Compute the difference in ranks between the similarities
		# and the distances
		#
		ranks_df["AB_Rank_Difference"] = (
			ranks_df["Similarity_Rank"] - ranks_df["Distance_Rank"]
		)
		ranks_df["Absolute_AB_Rank_Difference"] = abs(
			ranks_df["AB_Rank_Difference"]
		)
		columns_for_ranks = ranks_df[
			[
				"A_label",
				"B_label",
				"Similarity_Rank",
				"Distance_Rank",
				"AB_Rank_Difference",
				"Absolute_AB_Rank_Difference",
				"A_name",
				"B_name",
			]
		]
		columns_for_ranks = columns_for_ranks.rename(
			columns={"A_name": "A", "B_name": "B"}
		)
		#
		# Create filter for each item  indicating when an item is part
		# of a dyad
		# and the other item they are paired with. Item can be either
		# the A or B item.
		#
		for each_item in range_items:
			ranks_df[item_labels[each_item]] = "INAP"
		for each_pair in range_similarities:
			for each_item in range_items:
				if (
					ranks_df.iloc[each_pair, a_label_index]
					== item_labels[each_item]
					or ranks_df.iloc[each_pair, b_label_index]
					== item_labels[each_item]
				):
					if (
						ranks_df.iloc[each_pair, a_label_index]
						== item_labels[each_item]
					):
						ranks_df.loc[each_pair, item_labels[each_item]] = (
							ranks_df.iloc[each_pair, b_label_index]
						)
					else:
						ranks_df.loc[each_pair, item_labels[each_item]] = (
							ranks_df.iloc[each_pair, a_label_index]
						)
				else:
					ranks_df.loc[each_pair, item_labels[each_item]] = "INAP"

		self._director.similarities_active.ranks_df = ranks_df
		self._director.similarities_active.columns_for_ranks = (
			columns_for_ranks
		)

		return

	# ------------------------------------------------------------------------

	def rank_similarities(self) -> None:

		nitem = self.nitem
		item_names = self.item_names
		item_labels = self.item_labels
		ranked_similarities = self.ranked_similarities
		nreferent = self.nreferent
		ranked_similarities_as_dict = self.ranked_similarities_as_dict
		ranked_similarities_as_square = self.ranked_similarities_as_square
		ranked_similarities_as_list = ss.rankdata(self.similarities_as_list)

		next_pair = 0
		from_pts_range = range(1, nitem)
		for from_pts in from_pts_range:
			a_row = []
			to_pts_range = range(from_pts)
			for to_pts in to_pts_range:
				rank = ranked_similarities_as_list[next_pair]
				next_pair += 1
				a_row.append(rank)
				key = str(item_labels[to_pts] + "_" + item_labels[from_pts])
				ranked_similarities_as_dict[key] = rank
			ranked_similarities.append(a_row)
		range_items = range(nreferent)
		for each_item in range_items:
			ranked_similarities_as_square.append([])
			for other_item in range_items:
				if each_item == other_item:
					# self.ranked_similarities_as_square[
					# other_item].append("---")
					ranked_similarities_as_square[other_item].append(0.0)
				elif each_item < other_item:
					index = str(
						item_labels[each_item] + "_" + item_labels[other_item]
					)
					ranked_similarities_as_square[each_item].append(
						ranked_similarities_as_dict[index]
					)
				else:
					index = str(
						item_labels[other_item] + "_" + item_labels[each_item]
					)
					ranked_similarities_as_square[each_item].append(
						ranked_similarities_as_dict[index]
					)

		ranked_similarities_as_dataframe = pd.DataFrame(
			ranked_similarities_as_square, columns=item_names, index=item_names
		)

		self.ranked_similarities = ranked_similarities
		self.range_items = range_items
		self.ranked_similarities_as_list = ranked_similarities_as_list
		self.ranked_similarities_as_dict = ranked_similarities_as_dict
		self.ranked_similarities_as_square = ranked_similarities_as_square
		self.ranked_similarities_as_dataframe = (
			ranked_similarities_as_dataframe
		)

		return

	# ------------------------------------------------------------------------

	def duplicate_ranked_similarities(self, common: Spaces) -> None:

		(
			self.ranked_similarities_as_dataframe,
			self.ranked_similarities_as_dict,
			self.ranked_similarities_as_list,
			self.ranked_similarities_as_square,
			self.sorted_ranked_similarities_w_pairs,
			self.ndyad,
			self.range_dyads,
			self.range_items,
		) = common.duplicate_in_different_structures(
			self.ranked_similarities,
			self.item_names,
			self.item_labels,
			self.nreferent,
			self.value_type,
		)

# --------------------------------------------------------------------------


class TargetFeature:
	def __init__(self, director: Status) -> None:
		self._director = director
		self._hor_dim = director.common.hor_dim
		self._vert_dim = director.common.vert_dim
		self.file_handle: str = ""
		self.npoint: int = 0
		self.npoints: int = 0
		self.range_points: range = range(0)
		self.ndim: int = 0
		self.dim_names: list[str] = []
		self.dim_labels: list[str] = []
		self.range_dims: range = range(0)
		self.point_names: list[str] = []
		self.point_labels: list[str] = []
		self.point_coords: pd.DataFrame = pd.DataFrame()

		self.distances: list[float] = []
		self.seg: pd.DataFrame = pd.DataFrame()

	# ------------------------------------------------------------------------

	def print_target(self) -> None:
		"""print target function -
		is used to print the target configuration."""
		print(self.point_coords)
		return


# --------------------------------------------------------------------------
