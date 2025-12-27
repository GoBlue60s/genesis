from __future__ import annotations

# Standard library imports
import math
import random

# Third party imports
import numpy as np
import pandas as pd
import peek # noqa: F401

# Typing imports
from typing import NamedTuple

from constants import (
	BATTLEGROUND_ASSIGNMENT,
	MINIMAL_DIFFERENCE_FROM_ZERO,
	SETTLED_ASSIGNMENT,
)
from exceptions import SpacesError

from geometry import (
	Circle,
	CoordinateLists,
	LineInPlot,
	PeoplePoints,
	Point,
	Polygon,
	Region,
	TheoreticalExtremes,
)

# from supporters import AbstractCommand, ASupporterGrouping
from typing import TYPE_CHECKING

if TYPE_CHECKING:
	from director import Status
	from common import Spaces


# -------------------------------------------------------------------------


class Bisector(LineInPlot):
	def __init__(
		self,
		director: Status | None = None,
		point_on_line: Point | None = None,
		slope: float | None = None,
		color: str = "black",
		thickness: int = 1,
		style: str = "solid",
	) -> None:
		super().__init__(
			director, point_on_line, slope, color, thickness, style
		)

		if director is not None:
			self._director = director

		return


# -------------------------------------------------------------------------


class East(LineInPlot):
	def __init__(
		self,
		director: Status | None = None,
		point_on_line: Point | None = None,
		slope: float | None = None,
		color: str = "black",
		thickness: int = 1,
		style: str = "solid",
	) -> None:
		super().__init__(
			director, point_on_line, slope, color, thickness, style
		)

		if director is not None:
			self._director = director


# --------------------------------------------------------------------------


class Rivalry:
	def __init__(self, director: Status) -> None:
		self._director = director
		self._initialized: bool = False

		self.EPSILON = MINIMAL_DIFFERENCE_FROM_ZERO

		self.seg: pd.DataFrame = pd.DataFrame()

		self.segment_names: list[str] = [
			"Base",
			"Convertible",
			"Core",
			"Likely",
			"Battle_ground",
			"First",
			"Second",
		]

		self._create_instances_based_on_rivalry()
		self.rival_a: Point = Point()
		self.rival_b: Point = Point()

		self.base_pcts: list[float] = []
		self.battleground_pcts: list = []
		self.conv_pcts: list[float] = []
		self.core_pcts: list[float] = []
		self.first_pcts: list[float] = []
		self.likely_pcts: list = []
		self.second_pcts: list[float] = []
		self.base_pcts_df: pd.DataFrame = pd.DataFrame()

		self.core_radius: float = 0.0

		# Line objects (empty instances until reference points are set)
		self.connector: Connector = Connector()
		self.bisector: Bisector = Bisector()
		self.east: East = East()
		self.west: West = West()
		self.first: First = First()
		self.second: Second = Second()

		self.n_individ: int = 0
		self.nscored_individ: int = 0
		self.first_div: float = 0.0
		self.second_div: float = 0.0
		self.point_coords: pd.DataFrame = pd.DataFrame()
		self.hor_dim: int = 0
		self.vert_dim: int = 0

	# ------------------------------------------------------------------------

	def is_initialized(self) -> bool:
		"""Check if reference points have been established.

		Returns:
			bool: True if reference points are set, False otherwise
		"""
		return self._initialized

	# ------------------------------------------------------------------------

	def get_bisector(self) -> Bisector:
		"""Get bisector, raising if not initialized."""
		if not self._initialized:
			error_title = "Bisector Not Initialized"
			error_message = (
				"Cannot access bisector before reference points set"
			)
			raise SpacesError(error_title, error_message)
		return self.bisector

	# ------------------------------------------------------------------------

	def get_east(self) -> East:
		"""Get east line, raising if not initialized."""
		if not self._initialized:
			error_title = "East Not Initialized"
			error_message = "Cannot access east before reference points set"
			raise SpacesError(error_title, error_message)
		return self.east

	# ------------------------------------------------------------------------

	def get_west(self) -> West:
		"""Get west line, raising if not initialized."""
		if not self._initialized:
			error_title = "West Not Initialized"
			error_message = "Cannot access west before reference points set"
			raise SpacesError(error_title, error_message)
		return self.west

	# ------------------------------------------------------------------------

	def get_connector(self) -> Connector:
		"""Get connector line, raising if not initialized."""
		if not self._initialized:
			error_title = "Connector Not Initialized"
			error_message = (
				"Cannot access connector before reference points set"
			)
			raise SpacesError(error_title, error_message)
		return self.connector

	# ------------------------------------------------------------------------

	def get_first(self) -> First:
		"""Get first dimension divider, raising if not initialized."""
		if not self._initialized:
			error_title = "First Divider Not Initialized"
			error_message = "Cannot access first before reference points set"
			raise SpacesError(error_title, error_message)
		return self.first

	# ------------------------------------------------------------------------

	def get_second(self) -> Second:
		"""Get second dimension divider, raising if not initialized."""
		if not self._initialized:
			error_title = "Second Divider Not Initialized"
			error_message = "Cannot access second before reference points set"
			raise SpacesError(error_title, error_message)
		return self.second

	# ------------------------------------------------------------------------

	def _create_instances_based_on_rivalry(self) -> None:
		self.rival_a = Point()
		self.rival_b = Point()
		self.mid_point = Point()
		self.point_1 = Point()
		self.point_2 = Point()
		self.east_cross = Point()
		self.west_cross = Point()
		self.first_cross = Point()
		self.second_cross = Point()

		self.core_left = Circle(fill="blue")
		self.core_right = Circle(fill="red")
		self.core_neither = Polygon(fill="white")
		self.base_left = Polygon(fill="blue")
		self.base_right = Polygon(fill="red")
		self.base_neither = Polygon(fill="white")
		self.likely_left = Polygon(fill="blue")
		self.likely_right = Polygon(fill="red")
		self.battleground_segment = Polygon(fill="purple")
		self.battleground_settled = Polygon(fill="white")
		self.convertible_to_left = Polygon(fill="blue")
		self.convertible_to_right = Polygon(fill="red")
		self.convertible_settled = Polygon(fill="white")
		self.first_left = Polygon(fill="blue")
		self.first_right = Polygon(fill="red")
		self.second_up = Polygon(fill="blue")
		self.second_down = Polygon(fill="red")

		return

	# ------------------------------------------------------------------------

	def assign_to_segments(self) -> None:
		#
		# Every case is assigned to all (each) types of segments
		# Segment types are not mutually exclusive
		# Within segment type segments are mutually exclusive
		# The total for each type of segment should be the same
		#
		if not self._director.common.have_scores():
			return

		rivalry = self._director.rivalry
		nscored = self._director.scores_active.nscored_individ
		score_1_name = self._director.scores_active.score_1_name
		score_1 = self._director.scores_active.score_1
		score_2_name = self._director.scores_active.score_2_name
		score_2 = self._director.scores_active.score_2
		bisector = rivalry.bisector
		point_coords = self._director.configuration_active.point_coords
		hor_dim = self._director.common.hor_dim
		vert_dim = self._director.common.vert_dim
		rival_a = rivalry.rival_a  # had been self.rival_a_index
		rival_b = rivalry.rival_b
		west = rivalry.west
		east = rivalry.east
		first_dim_divider = rivalry.first_div
		second_dim_divider = rivalry.second_div

		self.seg = pd.DataFrame(
			columns=[
				score_1_name,
				score_2_name,
				"Base",
				"Convertible",
				"Core",
				"Likely",
				"Battle_ground",
				"First",
				"Second",
			]
		)
		segments = self.seg
		segments[score_1_name] = score_1
		segments[score_2_name] = score_2
		#
		# Determine base left and base right  segments -----------------------
		#
		(segments, base_segment_names) = self.assign_to_base_segments(
			segments,
			score_1_name,
			score_2_name,
			rival_a,
			rival_b,
			bisector,
			west,
			east,
			nscored,
		)
		#
		# Determine convertible_to_left and convertible_to_right  segments ---
		#
		(segments, convertible_segment_names) = (
			self.assign_to_convertible_segments(
				segments,
				score_1_name,
				score_2_name,
				rival_a,
				rival_b,
				bisector,
				west,
				east,
				nscored,
			)
		)
		#
		# Determine Core left and core right  segments -----------------------
		#
		(segments, core_segment_names) = self.assign_to_core_segments(
			segments,
			score_1_name,
			score_2_name,
			rival_a,
			rival_b,
			bisector,
			point_coords,
			hor_dim,
			vert_dim,
			nscored,
		)
		#
		# Determine battleground and settled segments ------------------------
		#
		(segments, battleground_segment_names) = (
			self.assign_to_battleground_segments(
				segments,
				score_1_name,
				score_2_name,
				bisector,
				west,
				east,
				nscored,
			)
		)

		#
		# Determine Only first and second segments ----------------------
		#
		(segments, first_segment_names, second_segment_names) = (
			self.assign_to_first_and_second_dimension_segments(
				segments,
				score_1_name,
				score_2_name,
				rival_a,
				rival_b,
				bisector,
				first_dim_divider,
				second_dim_divider,
				nscored,
			)
		)
		#
		# Determine Likely  segments ----------------------------------------
		#
		(segments, likely_segment_names) = self.assign_to_likely_segments(
			segments, nscored, score_1_name, score_2_name, bisector
		)

		self.segment_percentages = self.calculate_segment_percentages(segments)
		self.assemble_segment_percentages(
			likely_segment_names,
			base_segment_names,
			core_segment_names,
			first_segment_names,
			second_segment_names,
			battleground_segment_names,
			convertible_segment_names,
		)

		return

	# ------------------------------------------------------------------------

	def assemble_segment_percentages(
		self,
		likely_segment_names: list[str],
		base_segment_names: list[str],
		core_segment_names: list[str],
		first_segment_names: list[str],
		second_segment_names: list[str],
		battleground_segment_names: list[str],
		convertible_segment_names: list[str],
	) -> None:
		self.base_pcts = self.segment_percentages.base_pcts
		self.battleground_pcts = self.segment_percentages.battleground_pcts
		self.conv_pcts = self.segment_percentages.conv_pcts
		self.core_pcts = self.segment_percentages.core_pcts
		self.first_pcts = self.segment_percentages.first_pcts
		self.likely_pcts = self.segment_percentages.likely_pcts
		self.second_pcts = self.segment_percentages.second_pcts

		base_pcts_df = pd.DataFrame(
			{
				"Core Supporter Segment": base_segment_names,
				"Percent": self.base_pcts,
			}
		)
		battleground_pcts_df = pd.DataFrame(
			{
				"Battleground Segment": battleground_segment_names,
				"Percent": self.battleground_pcts,
			}
		)
		conv_pcts_df = pd.DataFrame(
			{
				"Convertible Segment": convertible_segment_names,
				"Percent": self.conv_pcts,
			}
		)
		core_pcts_df = pd.DataFrame(
			{
				"Core Supporter Segment": core_segment_names,
				"Percent": self.core_pcts,
			}
		)
		first_pcts_df = pd.DataFrame(
			{"First Segment": first_segment_names, "Percent": self.first_pcts}
		)
		likely_pcts_df = pd.DataFrame(
			{
				"Core Supporter Segment": likely_segment_names,
				"Percent": self.likely_pcts,
			}
		)
		second_pcts_df = pd.DataFrame(
			{
				"Second Segment": second_segment_names,
				"Percent": self.second_pcts,
			}
		)

		self.base_pcts_df = base_pcts_df
		self.battleground_pcts_df = battleground_pcts_df
		self.conv_pcts_df = conv_pcts_df
		self.core_pcts_df = core_pcts_df
		self.first_pcts_df = first_pcts_df
		self.likely_pcts_df = likely_pcts_df
		self.second_pcts_df = second_pcts_df

		self.segments_pcts_df = pd.DataFrame(columns=["Segment", "Percent"])

		segments_list = []

		segments_list.append(likely_pcts_df.copy())
		segments_list.append(base_pcts_df.copy())
		segments_list.append(core_pcts_df.copy())
		segments_list.append(first_pcts_df.copy())
		segments_list.append(second_pcts_df.copy())
		segments_list.append(battleground_pcts_df.copy())
		segments_list.append(conv_pcts_df.copy().copy())

		for each_df in segments_list:
			each_df.columns = ["Segment", "Percent"]

		self.segments_pcts_df = pd.concat(segments_list, ignore_index=True)

		return

	# ------------------------------------------------------------------------

	def assign_to_likely_segments(
		self,
		segments: pd.DataFrame,
		nscored: int,
		score_1_name: str,
		score_2_name: str,
		bisector: Bisector,
	) -> tuple[pd.DataFrame, list[str]]:
		rivalry = self._director.rivalry
		in_group = self._director.common.in_group
		rival_a = self._director.rivalry.rival_a
		rival_b = self._director.rivalry.rival_b
		point_coords = self._director.configuration_active.point_coords
		hor_dim = self._director.common.hor_dim
		# vert_dim = self._director.common.vert_dim
		if bisector._direction == "Flat":
			for each_indiv in range(nscored):
				if (
					segments.loc[each_indiv, score_2_name]
					< bisector._intercept
				):
					segments.loc[each_indiv, "Likely"] = 1
				else:
					segments.loc[each_indiv, "Likely"] = 2
		else:
			for each_indiv in range(nscored):
				if (
					segments.loc[each_indiv, score_1_name]
					< (
						segments.loc[each_indiv, score_2_name]
						- bisector._intercept
					)
					/ bisector._slope
				):
					segments.loc[each_indiv, "Likely"] = 1
				else:
					segments.loc[each_indiv, "Likely"] = 2

		rivalry.likely_left._points.x = in_group(
			segments, nscored, score_1_name, "Likely", {1}
		)
		rivalry.likely_left._points.y = in_group(
			segments, nscored, score_2_name, "Likely", {1}
		)
		rivalry.likely_right._points.x = in_group(
			segments, nscored, score_1_name, "Likely", {2}
		)
		rivalry.likely_right._points.y = in_group(
			segments, nscored, score_2_name, "Likely", {2}
		)

		if (
			point_coords.iloc[rival_a.index, hor_dim]
			< point_coords.iloc[rival_b.index, hor_dim]
		):
			likely_segment_names = [rival_a.name, rival_b.name]
		else:
			likely_segment_names = [rival_b.name, rival_a.name]

		return segments, likely_segment_names

	# ------------------------------------------------------------------------

	def assign_to_base_segments(
		self,
		segments: pd.DataFrame,
		score_1_name: str,
		score_2_name: str,
		rival_a: Point,
		rival_b: Point,
		bisector: Bisector,
		west: West,
		east: East,
		nscored: int,
	) -> tuple[pd.DataFrame, list[str]]:
		rivalry = self._director.rivalry
		in_group = self._director.common.in_group
		for each_indiv in segments.index:
			west_at_x_coord = (
				segments.loc[each_indiv, score_2_name] - west._intercept
			) / west._slope

			east_at_x_coord = (
				segments.loc[each_indiv, score_2_name] - east._intercept
			) / east._slope

			if bisector._direction == "Flat":
				segments = self._base_group_when_bisector_is_flat(
					segments, each_indiv, score_2_name, west, east
				)
			elif bisector._direction == "Vertical":
				segments = self._base_group_when_bisector_is_vertical(
					segments, each_indiv, score_1_name, west, east
				)
			elif bisector._direction == "Upward slope":
				segments = self._base_group_when_bisector_slopes_upward(
					segments,
					each_indiv,
					score_1_name,
					west_at_x_coord,
					east_at_x_coord,
				)
			elif bisector._direction == "Downward slope":
				segments = self._base_group_when_bisector_slopes_downward(
					segments,
					each_indiv,
					score_1_name,
					west_at_x_coord,
					east_at_x_coord,
				)

		rivalry.base_left._points.x = in_group(
			segments, nscored, score_1_name, "Base", {1}
		)
		rivalry.base_left._points.y = in_group(
			segments, nscored, score_2_name, "Base", {1}
		)
		rivalry.base_neither._points.x = in_group(
			segments, nscored, score_1_name, "Base", {2}
		)
		rivalry.base_neither._points.y = in_group(
			segments, nscored, score_2_name, "Base", {2}
		)
		rivalry.base_right._points.x = in_group(
			segments, nscored, score_1_name, "Base", {3}
		)
		rivalry.base_right._points.y = in_group(
			segments, nscored, score_2_name, "Base", {3}
		)

		if bisector._direction == "Flat":
			if rival_a.y > rival_b.y:
				base_segment_names = [rival_a.name, "Neither", rival_b.name]
			else:
				base_segment_names = [rival_b.name, "Neither", rival_a.name]
		elif rival_a.x < rival_b.x:
			base_segment_names = [rival_a.name, "Neither", rival_b.name]
		else:
			base_segment_names = [rival_b.name, "Neither", rival_a.name]

		return (segments, base_segment_names)

	# ------------------------------------------------------------------------

	def _base_group_when_bisector_is_flat(
		self,
		segments: pd.DataFrame,
		each_indiv: int,
		score_2_name: str,
		west: West,
		east: East,
	) -> pd.DataFrame:
		if segments.loc[each_indiv, score_2_name] < west._start.y:
			segments.loc[each_indiv, "Base"] = 1
		elif (
			east._start.y
			> segments.loc[each_indiv, score_2_name]
			> west._start.y
		):
			segments.loc[each_indiv, "Base"] = 2
		else:
			segments.loc[each_indiv, "Base"] = 3
		return segments

	# ------------------------------------------------------------------------

	def _base_group_when_bisector_is_vertical(
		self,
		segments: pd.DataFrame,
		each_indiv: int,
		score_1_name: str,
		west: West,
		east: East,
	) -> pd.DataFrame:
		if segments.loc[each_indiv, score_1_name] < west._start.x:
			segments.loc[each_indiv, "Base"] = 1
		elif segments.loc[each_indiv, score_1_name] > east._start.x:
			segments.loc[each_indiv, "Base"] = 3
		else:
			segments.loc[each_indiv, "Base"] = 2
		return segments

	# ------------------------------------------------------------------------

	def _base_group_when_bisector_slopes_upward(
		self,
		segments: pd.DataFrame,
		each_indiv: int,
		score_1_name: str,
		west_at_x_coord: float,
		east_at_x_coord: float,
	) -> pd.DataFrame:
		if segments.loc[each_indiv, score_1_name] < west_at_x_coord:
			segments.loc[each_indiv, "Base"] = 1
		elif (
			east_at_x_coord
			> segments.loc[each_indiv, score_1_name]
			> west_at_x_coord
		):
			segments.loc[each_indiv, "Base"] = 2
		else:
			segments.loc[each_indiv, "Base"] = 3

		return segments

	# ------------------------------------------------------------------------

	def _base_group_when_bisector_slopes_downward(
		self,
		segments: pd.DataFrame,
		each_indiv: int,
		score_1_name: str,
		west_at_x_coord: float,
		east_at_x_coord: float,
	) -> pd.DataFrame:
		if (
			segments.loc[each_indiv, score_1_name] < west_at_x_coord
		):  # switched side
			segments.loc[each_indiv, "Base"] = 1
		elif (
			east_at_x_coord
			> segments.loc[each_indiv, score_1_name]
			> west_at_x_coord
		):  # switched side twice
			segments.loc[each_indiv, "Base"] = 2
		else:
			segments.loc[each_indiv, "Base"] = 3

		return segments

	# ------------------------------------------------------------------------

	def assign_to_convertible_segments(
		self,
		segments: pd.DataFrame,
		score_1_name: str,
		score_2_name: str,
		rival_a: Point,
		rival_b: Point,
		bisector: Bisector,
		west: West,
		east: East,
		nscored: int,
	) -> pd.DataFrame:
		rivalry = self._director.rivalry
		in_group = self._director.common.in_group
		not_in_group = self._director.common.not_in_group
		for each_indiv in range(nscored):
			bisector_x = (
				segments.loc[each_indiv, score_2_name] - bisector._intercept
			) / bisector._slope
			west_at_x_coord = (
				segments.loc[each_indiv, score_2_name] - west._intercept
			) / west._slope
			east_at_x_coord = (
				segments.loc[each_indiv, score_2_name] - east._intercept
			) / east._slope
			#
			if bisector._direction == "Flat":
				segments = self._convertible_group_when_bisector_is_flat(
					segments,
					each_indiv,
					bisector._start.y,
					score_2_name,
					west._start.y,
					east._start.y,
				)
			elif bisector._direction == "Vertical":
				segments = self._convertible_group_when_bisector_is_vertical(
					segments, each_indiv, score_1_name, bisector, west, east
				)
			elif bisector._direction == "Upward slope":
				segments = self._convertible_group_when_bisector_slopes_upward(
					segments,
					each_indiv,
					score_1_name,
					bisector_x,
					west_at_x_coord,
					east_at_x_coord,
				)
			elif bisector._direction == "Downward slope":
				segments = (
					self._convertible_group_when_bisector_slopes_downward(
						segments,
						each_indiv,
						score_1_name,
						bisector_x,
						west_at_x_coord,
						east_at_x_coord,
					)
				)

		rivalry.convertible_to_left._points.x = in_group(
			segments, nscored, score_1_name, "Convertible", {1}
		)
		rivalry.convertible_to_left._points.y = in_group(
			segments, nscored, score_2_name, "Convertible", {1}
		)
		rivalry.convertible_to_right._points.x = in_group(
			segments, nscored, score_1_name, "Convertible", {2}
		)
		rivalry.convertible_to_right._points.y = in_group(
			segments, nscored, score_2_name, "Convertible", {2}
		)

		rivalry.convertible_settled._points.x = not_in_group(
			segments, nscored, score_1_name, "Convertible", {1, 2}
		)
		rivalry.convertible_settled._points.y = not_in_group(
			segments, nscored, score_2_name, "Convertible", {1, 2}
		)

		if bisector._direction == "Flat":
			if rival_a.y > rival_b.y:
				convertible_segment_names = [
					rival_a.name,
					rival_b.name,
					"Settled",
				]
			else:
				convertible_segment_names = [
					rival_b.name,
					rival_a.name,
					"Settled",
				]
		elif rival_a.x < rival_b.x:
			convertible_segment_names = [rival_a.name, rival_b.name, "Settled"]
		else:
			convertible_segment_names = [rival_b.name, rival_a.name, "Settled"]

		return segments, convertible_segment_names

	# ------------------------------------------------------------------------

	def _convertible_group_when_bisector_is_flat(
		self,
		segments: pd.DataFrame,
		each_indiv: int,
		bisector_start_y: float,
		score_2_name: str,
		west: West,
		east: East,
	) -> pd.DataFrame:
		# west_start_y: float,
		# east_start_y: float) -> pd.DataFrame:

		if (
			bisector_start_y
			< segments.loc[each_indiv, score_2_name]
			< east._start.y
		):
			segments.loc[each_indiv, "Convertible"] = 1
		elif (
			bisector_start_y
			> segments.loc[each_indiv, score_2_name]
			> west._start.y
		):
			segments.loc[each_indiv, "Convertible"] = 2
		else:
			segments.loc[each_indiv, "Convertible"] = 3

		return segments

	# ------------------------------------------------------------------------

	def _convertible_group_when_bisector_is_vertical(
		self,
		segments: pd.DataFrame,
		each_indiv: int,
		score_1_name: str,
		bisector: Bisector,
		west: West,
		east: East,
	) -> pd.DataFrame:
		if (
			bisector._start.x
			< segments.loc[each_indiv, score_1_name]
			< east._start.x
		):
			segments.loc[each_indiv, "Convertible"] = 1
		elif (
			bisector._start.x
			> segments.loc[each_indiv, score_1_name]
			> west._start.x
		):
			segments.loc[each_indiv, "Convertible"] = 2
		else:
			segments.loc[each_indiv, "Convertible"] = 3

		return segments

	# ------------------------------------------------------------------------

	def _convertible_group_when_bisector_slopes_upward(
		self,
		segments: pd.DataFrame,
		each_indiv: int,
		score_1_name: str,
		bisector_x: float,
		west_at_x_coord: float,
		east_at_x_coord: float,
	) -> pd.DataFrame:
		if (
			bisector_x
			< segments.loc[each_indiv, score_1_name]
			< east_at_x_coord
		):
			segments.loc[each_indiv, "Convertible"] = 1
		elif (
			bisector_x
			> segments.loc[each_indiv, score_1_name]
			> west_at_x_coord
		):
			segments.loc[each_indiv, "Convertible"] = 2
		else:
			segments.loc[each_indiv, "Convertible"] = 3

		return segments

	# ------------------------------------------------------------------------

	def _convertible_group_when_bisector_slopes_downward(
		self,
		segments: pd.DataFrame,
		each_indiv: int,
		score_1_name: str,
		bisector_x: float,
		west_at_x_coord: float,
		east_at_x_coord: float,
	) -> pd.DataFrame:
		if (
			bisector_x
			< segments.loc[each_indiv, score_1_name]
			< east_at_x_coord
		):
			segments.loc[each_indiv, "Convertible"] = 1
		elif (
			bisector_x
			> segments.loc[each_indiv, score_1_name]
			> west_at_x_coord
		):
			segments.loc[each_indiv, "Convertible"] = 2
		else:
			segments.loc[each_indiv, "Convertible"] = 3

		return segments

	# -----------------------------------------------------------------------

	def assign_to_core_segments(
		self,
		segments: pd.DataFrame,
		score_1_name: str,
		score_2_name: str,
		rival_a: Point,
		rival_b: Point,
		bisector: Bisector,
		point_coords: pd.DataFrame,
		hor_dim: str,
		vert_dim: str,
		nscored: int,
	) -> tuple[pd.DataFrame, list[str]]:
		# point_names = self._director.configuration_active.point_names

		core_radius = self._director.rivalry.core_radius

		if bisector._direction == "Flat":
			if rival_a.y > rival_b.y:
				# here if rival a is higher vertically than rival b
				left_x = point_coords.iloc[rival_a.index, hor_dim]
				left_y = point_coords.iloc[rival_a.index, vert_dim]
				right_x = point_coords.iloc[rival_b.index, hor_dim]
				right_y = point_coords.iloc[rival_b.index, vert_dim]
				core_segment_names = [rival_a.name, "Neither", rival_b.name]
			else:
				# here if rival a is NOT higher vertically than rival b
				left_x = point_coords.iloc[rival_b.index, hor_dim]
				left_y = point_coords.iloc[rival_b.index, vert_dim]
				right_x = point_coords.iloc[rival_a.index, hor_dim]
				right_y = point_coords.iloc[rival_a.index, vert_dim]
				core_segment_names = [rival_b.name, "Neither", rival_a.name]
		# here if bisector is NOT Flat
		elif rival_a.x < rival_b.x:
			# here if rival a is more westward than rival b
			left_x = point_coords.iloc[rival_a.index, hor_dim]
			left_y = point_coords.iloc[rival_a.index, vert_dim]
			right_x = point_coords.iloc[rival_b.index, hor_dim]
			right_y = point_coords.iloc[rival_b.index, vert_dim]
			core_segment_names = [rival_a.name, "Neither", rival_b.name]
		else:
			# here is rival a is NOT more westward than rival b
			left_x = point_coords.iloc[rival_b.index, hor_dim]
			left_y = point_coords.iloc[rival_b.index, vert_dim]
			right_x = point_coords.iloc[rival_a.index, hor_dim]
			right_y = point_coords.iloc[rival_a.index, vert_dim]
			core_segment_names = [rival_b.name, "Neither", rival_a.name]
		#
		for each_indiv in range(nscored):
			target_x = segments.loc[each_indiv, score_1_name]
			target_y = segments.loc[each_indiv, score_2_name]
			dist_to_left = self.calculate_distance_between_points(
				Point(left_x, left_y), Point(target_x, target_y)
			)
			dist_to_right = self.calculate_distance_between_points(
				Point(right_x, right_y), Point(target_x, target_y)
			)
			#
			if dist_to_left < core_radius:
				segments.loc[each_indiv, "Core"] = 1
			# n_core_1 += 1
			elif dist_to_right < core_radius:
				segments.loc[each_indiv, "Core"] = 3
			# n_core_3 += 1
			else:
				segments.loc[each_indiv, "Core"] = 2
			# n_core_2 += 1

		return segments, core_segment_names

	# ------------------------------------------------------------------------

	def assign_to_battleground_segments(
		self,
		segments: pd.DataFrame,
		score_1_name: str,
		score_2_name: str,
		bisector: Bisector,
		west: West,
		east: East,
		nscored: int,
	) -> pd.DataFrame:
		if self._director.common.have_scores():
			self.battleground_segment_people_points = PeoplePoints(
				self.battleground_segment._x, self.battleground_segment._y
			)
			self.battleground_settled_people_points = PeoplePoints([], [])

		for each_indiv in range(nscored):
			battleground_assignment = self._assign_individual_to_battleground(
				segments, each_indiv, score_1_name, score_2_name,
				bisector, west, east
			)
			segments.loc[each_indiv, "Battle_ground"] = battleground_assignment

		self._update_battleground_points(
			segments, nscored, score_1_name, score_2_name
		)

		battleground_segment_names = ["Battleground", "Settled"]
		return segments, battleground_segment_names

	def _assign_individual_to_battleground(
		self,
		segments: pd.DataFrame,
		each_indiv: int,
		score_1_name: str,
		score_2_name: str,
		bisector: Bisector,
		west: West,
		east: East,
	) -> int:
		west_at_x_coord = (
			segments.loc[each_indiv, score_2_name] - west._intercept
		) / west._slope
		east_at_x_coord = (
			segments.loc[each_indiv, score_2_name] - east._intercept
		) / east._slope

		if bisector._direction == "Flat":
			return self._assign_flat_direction(
				segments, each_indiv, score_2_name, east, west
			)
		if bisector._direction == "Vertical":
			return self._assign_vertical_direction(
				segments, each_indiv, score_1_name, east, west
			)
		if bisector._direction in ("Upward slope", "Downward slope"):
			return self._assign_slope_direction(
				segments, each_indiv, score_1_name,
				east_at_x_coord, west_at_x_coord
			)
		return SETTLED_ASSIGNMENT

	def _assign_flat_direction(
		self,
		segments: pd.DataFrame,
		each_indiv: int,
		score_2_name: str,
		east: East,
		west: West,
	) -> int:
		if (
			east._intercept
			< segments.loc[each_indiv, score_2_name]
			< west._intercept
		):
			return BATTLEGROUND_ASSIGNMENT
		return SETTLED_ASSIGNMENT

	def _assign_vertical_direction(
		self,
		segments: pd.DataFrame,
		each_indiv: int,
		score_1_name: str,
		east: East,
		west: West,
	) -> int:
		if (
			east._start.x
			> segments.loc[each_indiv, score_1_name]
			> west._start.x
		):
			return BATTLEGROUND_ASSIGNMENT
		return SETTLED_ASSIGNMENT

	def _assign_slope_direction(
		self,
		segments: pd.DataFrame,
		each_indiv: int,
		score_1_name: str,
		east_at_x_coord: float,
		west_at_x_coord: float,
	) -> int:
		if (
			east_at_x_coord
			> segments.loc[each_indiv, score_1_name]
			> west_at_x_coord
		):
			return BATTLEGROUND_ASSIGNMENT
		return SETTLED_ASSIGNMENT

	def _update_battleground_points(
		self,
		segments: pd.DataFrame,
		nscored: int,
		score_1_name: str,
		score_2_name: str,
	) -> None:
		rivalry = self._director.rivalry
		in_group = self._director.common.in_group

		rivalry.battleground_segment._points.x = in_group(
			segments, nscored, score_1_name, "Battle_ground",
			{BATTLEGROUND_ASSIGNMENT}
		)
		rivalry.battleground_segment._points.y = in_group(
			segments, nscored, score_2_name, "Battle_ground",
			{BATTLEGROUND_ASSIGNMENT}
		)
		rivalry.battleground_settled._points.x = in_group(
			segments, nscored, score_1_name, "Battle_ground",
			{SETTLED_ASSIGNMENT}
		)
		rivalry.battleground_settled._points.y = in_group(
			segments, nscored, score_2_name, "Battle_ground",
			{SETTLED_ASSIGNMENT}
		)

	# ------------------------------------------------------------------------

	def assign_to_first_and_second_dimension_segments(
		self,
		segments: pd.DataFrame,
		score_1_name: str,
		score_2_name: str,
		rival_a: Point,
		rival_b: Point,
		bisector: Bisector,
		first_div: float,
		second_div: float,
		nscored: int,
	) -> tuple[pd.DataFrame, list[str], list[str]]:
		rivalry = self._director.rivalry
		in_group = self._director.common.in_group
		for each_indiv in range(nscored):
			# first
			if segments.loc[each_indiv, score_1_name] < first_div:
				segments.loc[each_indiv, "First"] = 1
			else:
				segments.loc[each_indiv, "First"] = 2
			# second
			# if self.second.loc[each_indiv] > self.second_div:
			if segments.loc[each_indiv, score_2_name] > second_div:
				segments.loc[each_indiv, "Second"] = 1
			else:
				segments.loc[each_indiv, "Second"] = 2

		rivalry.first_left._points.x = in_group(
			segments, nscored, score_1_name, "First", {1}
		)
		rivalry.first_left._points.y = in_group(
			segments, nscored, score_2_name, "First", {1}
		)
		rivalry.first_right._points.x = in_group(
			segments, nscored, score_1_name, "First", {2}
		)
		rivalry.first_right._points.y = in_group(
			segments, nscored, score_2_name, "First", {2}
		)

		rivalry.second_up._points.x = in_group(
			segments, nscored, score_1_name, "Second", {1}
		)
		rivalry.second_up._points.y = in_group(
			segments, nscored, score_2_name, "Second", {1}
		)
		rivalry.second_down._points.x = in_group(
			segments, nscored, score_1_name, "Second", {2}
		)
		rivalry.second_down._points.y = in_group(
			segments, nscored, score_2_name, "Second", {2}
		)

		if bisector._direction == "Flat":
			if rival_a.y > rival_b.y:
				first_segment_names = [rival_a.name, rival_b.name]
				second_segment_names = [rival_a.name, rival_b.name]
			else:
				first_segment_names = [rival_b.name, rival_a.name]
				second_segment_names = [rival_b.name, rival_a.name]
		elif rival_a.x < rival_b.x:
			first_segment_names = [rival_a.name, rival_b.name]
			second_segment_names = [rival_a.name, rival_b.name]
		else:
			first_segment_names = [rival_b.name, rival_a.name]
			second_segment_names = [rival_b.name, rival_a.name]

		return segments, first_segment_names, second_segment_names

	# ------------------------------------------------------------------------

	def calculate_segment_percentages(
		self, segments: pd.DataFrame
	) -> SegmentPercentages:
		# tuple[float, float, float, float, float, float, float]:

		#
		# gets percent for codes appearing in series
		# will not return 0.0 if code does not appear in series
		#
		base_pcts = (
			segments.value_counts("Base", normalize=True, sort=False) * 100
		)
		conv_pcts = (
			segments.value_counts("Convertible", normalize=True, sort=False)
			* 100
		)
		core_pcts = (
			segments.value_counts("Core", normalize=True, sort=False) * 100
		)
		likely_pcts = (
			segments.value_counts("Likely", normalize=True, sort=False) * 100
		)
		battleground_pcts = (
			segments.value_counts("Battle_ground", normalize=True, sort=False)
			* 100
		)
		first_pcts = (
			segments.value_counts("First", normalize=True, sort=False) * 100
		)
		second_pcts = (
			segments.value_counts("Second", normalize=True, sort=False) * 100
		)
		#
		# Needed to capture any code that does not appear in pcts
		# ensures percent is 0.0 for any missing code
		#
		for i in range(1, 4):
			base_pcts = base_pcts.reindex(
				base_pcts.index.union([i]), fill_value=0.0
			)
			conv_pcts = conv_pcts.reindex(
				conv_pcts.index.union([i]), fill_value=0.0
			)
			core_pcts = core_pcts.reindex(
				core_pcts.index.union([i]), fill_value=0.0
			)
		for i in range(1, 3):
			likely_pcts = likely_pcts.reindex(
				likely_pcts.index.union([i]), fill_value=0.0
			)
		for i in range(1, 3):
			first_pcts = first_pcts.reindex(
				first_pcts.index.union([i]), fill_value=0.0
			)
			second_pcts = second_pcts.reindex(
				second_pcts.index.union([i]), fill_value=0.0
			)
		for i in range(1, 3):
			battleground_pcts = battleground_pcts.reindex(
				battleground_pcts.index.union([i]), fill_value=0.0
			)
		#
		# Ensures order of pcts
		#
		base_pcts.sort_index(inplace=True)
		conv_pcts.sort_index(inplace=True)
		core_pcts.sort_index(inplace=True)
		likely_pcts.sort_index(inplace=True)
		battleground_pcts.sort_index(inplace=True)
		first_pcts.sort_index(inplace=True)
		second_pcts.sort_index(inplace=True)

		return SegmentPercentages(
			base_pcts,
			conv_pcts,
			core_pcts,
			likely_pcts,
			battleground_pcts,
			first_pcts,
			second_pcts,
		)

	# ------------------------------------------------------------------------

	def calculate_distance_between_points(
		self, a_point: Point, b_point: Point
	) -> float:
		"""Distance between points function - calculates distance between
		two points.
		"""
		#
		# Calculate the distance between pair of points
		#
		sq_x: float = (a_point.x - b_point.x) * (a_point.x - b_point.x)
		sq_y: float = (a_point.y - b_point.y) * (a_point.y - b_point.y)
		sumofsqs: float = sq_x + sq_y
		# Take the sq root of the sum of squares
		dist_pts: float = math.sqrt(sumofsqs)
		return dist_pts

	# ------------------------------------------------------------------------

	@staticmethod
	def choose_a_side_function() -> tuple[bool, bool]:
		"""The choose a side function - randomly chooses a side.
		\nIf a line goes through a corner this randomly assigns it as going
		through one side.
		\nArguments -
		\nNone
		\nReturned variables -
		\nside_1:  True or False indicating the line will be considered
		as going through side_1
		\nside_2: True or False indicating whether the line will be
		considered as going through side_2
		"""
		#
		# randomly set first to be true or false
		#
		first = random.choice([True, False])
		#
		if first:
			side_1 = True
			side_2 = False
		else:
			side_1 = False
			side_2 = True
		return side_1, side_2

		# --------------------------------------------------------------------

	def dividers(
		self, source: PeoplePoints, rival_a: Point, rival_b: Point
	) -> None:
		"""Determines the point on each dimension that separates rivals
		on that dimension
		"""

		point_coords = source.point_coords

		diff_first = (
			point_coords.iloc[rival_b.index, 0]
			- point_coords.iloc[rival_a.index, 0]
		)
		diff_second = (
			point_coords.iloc[rival_b.index, 1]
			- point_coords.iloc[rival_a.index, 1]
		)
		sq_first = diff_first**2
		sq_second = diff_second**2
		half_first = math.sqrt(sq_first) / 2
		half_second = math.sqrt(sq_second) / 2
		min_first = min(
			point_coords.iloc[rival_a.index, 0],
			point_coords.iloc[rival_b.index, 0],
		)
		min_second = min(
			point_coords.iloc[rival_a.index, 1],
			point_coords.iloc[rival_b.index, 1],
		)
		first_div = min_first + half_first
		second_div = min_second + half_second

		self.first_div = first_div
		self.second_div = second_div

		return

	# ------------------------------------------------------------------------

	def _establish_slope_and_cross_points(
		self,
		rival_a: Point,
		rival_b: Point,
		battleground_percent: float,
		point_coords: pd.DataFrame,
	) -> tuple[float, float]:
		mid_point = self.mid_point
		point_1 = self.point_1
		point_2 = self.point_2
		east_cross = self.east_cross
		west_cross = self.west_cross
		first_cross = self.first_cross
		second_cross = self.second_cross

		self._determine_connector_mid_point(rival_a, rival_b)

		slope = self._determine_connector_slope(rival_a, rival_b)

		connector_threshold = battleground_percent / 2.0

		self._director.common.set_axis_extremes_based_on_coordinates(
			point_coords
		)

		if abs(slope) < self.EPSILON:
			bisector_slope = float("inf")
		else:
			bisector_slope = -1 / slope

		(diff_x, diff_y, east_cross, west_cross) = (
			self._determine_east_and_west_cross_points(
				rival_a,
				rival_b,
				mid_point,
				connector_threshold,
				point_1,
				point_2,
				east_cross,
				west_cross,
			)
		)

		(first_cross, second_cross) = (
			self._determine_first_and_second_cross_points(
				diff_x, diff_y, first_cross, second_cross
			)
		)

		self.east_cross = east_cross
		self.west_cross = west_cross
		self.first_cross = first_cross
		self.second_cross = second_cross

		return (slope, bisector_slope)

	# ------------------------------------------------------------------------

	def _determine_connector_mid_point(
		self, rival_a: Point, rival_b: Point
	) -> None:
		self.mid_point.x = (rival_b.x + rival_a.x) / 2.0
		self.mid_point.y = (rival_b.y + rival_a.y) / 2.0

		return

	# ------------------------------------------------------------------------

	def _determine_connector_slope(
		self, rival_a: Point, rival_b: Point
	) -> float:
		dx = rival_b.x - rival_a.x
		if abs(dx) < self.EPSILON:
			slope = float("inf")
		else:
			slope = (rival_b.y - rival_a.y) / (rival_b.x - rival_a.x)

		return slope

	# ------------------------------------------------------------------------

	def _determine_east_and_west_cross_points(
		self,
		rival_a: Point,
		rival_b: Point,
		mid_point: Point,
		connector_threshold: float,
		point_1: Point,
		point_2: Point,
		east_cross: Point,
		west_cross: Point,
	) -> tuple[float, float, Point, Point]:
		diff_x = rival_b.x - rival_a.x
		diff_y = rival_b.y - rival_a.y

		point_1.x = mid_point.x - (connector_threshold * diff_x)
		point_1.y = mid_point.y - (connector_threshold * diff_y)
		point_2.x = mid_point.x + (connector_threshold * diff_x)
		point_2.y = mid_point.y + (connector_threshold * diff_y)

		if point_1.x < point_2.x:
			west_cross.x = point_1.x
			west_cross.y = point_1.y
			east_cross.x = point_2.x
			east_cross.y = point_2.y
		else:
			west_cross.x = point_2.x
			west_cross.y = point_2.y
			east_cross.x = point_1.x
			east_cross.y = point_1.y

		return (diff_x, diff_y, east_cross, west_cross)

	# ------------------------------------------------------------------------

	def _determine_first_and_second_cross_points(
		self,
		diff_x: float,
		diff_y: float,
		first_cross: Point,
		second_cross: Point,
	) -> tuple[Point, Point]:
		first_cross.x = diff_x
		first_cross.y = 0.0
		second_cross.x = 0.0
		second_cross.y = diff_y

		return (first_cross, second_cross)

	# ------------------------------------------------------------------------

	def create_or_revise_rivalry_attributes(
		self,
		director: Status,  # noqa: ARG002
		common: Spaces,
	) -> None:
		if not common.have_reference_points():
			return

		self.set_line_attributes_based_on_location_of_rivals(
			self._director
		)

		self.set_region_attributes_based_on_location_of_rivals(
			self._director
		)
		self.use_reference_points_to_define_segments(self._director)
		return

	# ------------------------------------------------------------------------

	def _establish_lines_defining_contest_and_segments(
		self,
		rival_a: Point,
		rival_b: Point,
		point_coords: pd.DataFrame,
		battleground_percent: float,
	) -> None:
		mid_point = self.mid_point
		east_cross = self.east_cross
		west_cross = self.west_cross
		first_cross = self.first_cross
		second_cross = self.second_cross

		# calculation of slope , extremes, and connector_threshold need to
		# precede use of
		# classes sub classed fromLineInPlot()
		(slope, bisector_slope) = self._establish_slope_and_cross_points(
			rival_a, rival_b, battleground_percent, point_coords
		)

		self.connector = Connector(
			self._director,
			mid_point,
			slope,
			rival_a,
			rival_b,
			style="solid",
			color="black",
			thickness=1,
		)
		self.bisector = Bisector(
			self._director,
			mid_point,
			bisector_slope,
			style="solid",
			color="black",
			thickness=1,
		)
		self.west = West(
			self._director,
			west_cross,
			bisector_slope,
			style="solid",
			color="black",
			thickness=1,
		)
		self.east = East(
			self._director,
			east_cross,
			bisector_slope,
			style="solid",
			color="black",
			thickness=1,
		)
		self.first = First(
			self._director,
			first_cross,
			self.EPSILON,
			style="solid",
			color="black",
			thickness=1,
		)
		self.second = Second(
			self._director,
			second_cross,
			1,
			style="solid",
			color="black",
			thickness=1,
		)

		self.west_cross = west_cross
		self.east_cross = east_cross

		# Mark rivalry as initialized now that all line objects are created
		self._initialized = True

		return

	# ------------------------------------------------------------------------

	def set_line_attributes_based_on_location_of_rivals(
		self, director: Status
	) -> None:
		"""
		This function establishes the attributes of the connector,
		the bisector,
		and the two lines that are parallel to the bisector which are the
		boundaries of the battleground, east and west. In a sense it
		establishes
		the current bisector information based on the reference points.

		It consists of the following -

		set_axis_extremes_based_on_coordinates - sets the maximum and minimum
		values for the x and y axes based on the coordinates. This is needed
		as coordinates
		may not be the same as when the previous bisector had been established.

		# set_direction_flags_based_on_connector - sets the direction flags
		# of connector,
		# bisector, and the two lines parallel to the bisector called east
		# and west

		set_bisector_based_on_connector - Determines the slope and length
		of connector.
		Also determines the slope and intercept of the perpendicular bisector.
		Also determines coordinates of the midpoint of the connector.

		set_core_radius - Determines the core radius based on the length
		of the connector.

		set_bisector_ends - Determines the ends of the bisector based on the
		coordinates .

		set_attributes_for_east_and_west_boundaries - Should be broken into
		smaller functions
		Determines the attributes of east and west edges of battleground.
		Relies on maximums being set which was done when configuration
		and/or scores
		were established. Uses copies (self._) of max and min values.

		dividers - Determines the attributes of the two lines parallel to
		the bisector.

		set flags to show bisector and connector
		"""

		point_coords = director.configuration_active.point_coords
		rival_a = self.rival_a
		rival_b = self.rival_b

		rival_a.x = point_coords.iloc[rival_a.index, 0]
		rival_a.y = point_coords.iloc[rival_a.index, 1]
		rival_b.x = point_coords.iloc[rival_b.index, 0]
		rival_b.y = self._director.configuration_active.point_coords.iloc[
			rival_b.index, 1
		]

		battleground_percent = self._director.common.battleground_size

		self._establish_lines_defining_contest_and_segments(
			rival_a, rival_b, point_coords, battleground_percent
		)

		(_, _) = self._establish_slope_and_cross_points(
			rival_a, rival_b, battleground_percent, point_coords
		)

		show_bisector = self._director.common.show_bisector
		show_connector = self._director.common.show_connector

		self.dividers(director.configuration_active, rival_a, rival_b)
		if self._director.common.have_reference_points():
			show_bisector = True
			show_connector = True

		# self.connector.length = connector_attributes.length

		core_radius = self.set_core_radius()

		self._director.common.show_bisector = show_bisector
		self._director.common.show_connector = show_connector

		self.core_radius = core_radius
		# self.first_div = dimension_dividers.first_div
		# self.second_div = dimension_dividers.second_div

		return

	# ------------------------------------------------------------------------

	def set_region_attributes_based_on_location_of_rivals(
		self, director: Status
	) -> None:
		point_coords = director.configuration_active.point_coords
		rival_a = self.rival_a
		rival_b = self.rival_b

		rival_a.x = point_coords.iloc[rival_a.index, 0]
		rival_a.y = point_coords.iloc[rival_a.index, 1]
		rival_b.x = point_coords.iloc[rival_b.index, 0]
		rival_b.y = point_coords.iloc[rival_b.index, 1]

		# battleground_percent = self._director.common.battleground_size

		self._establish_regions_defining_contest_and_segments()
		# 	battleground_percent)

		return

	# -----------------------------------------------------------------------

	def _create_core_regions(self) -> None:
		hor_dim = self._director.common.hor_dim
		vert_dim = self._director.common.vert_dim

		point_coords = self._director.configuration_active.point_coords
		rivalry = self._director.rivalry
		rival_a = rivalry.rival_a
		rival_b = rivalry.rival_b
		core_left = Point()
		core_right = Point()
		if self.bisector._direction == "Flat":
			if (
				point_coords.iloc[rival_a.index, vert_dim]
				> point_coords.iloc[rival_b.index, vert_dim]
			):
				core_left.x = point_coords.iloc[rival_a.index, hor_dim]
				core_left.y = point_coords.iloc[rival_a.index, vert_dim]
				core_right.x = point_coords.iloc[rival_b.index, hor_dim]
				core_right.y = point_coords.iloc[rival_b.index, vert_dim]
			else:
				core_left.x = point_coords.iloc[rival_b.index, hor_dim]
				core_left.y = point_coords.iloc[rival_b.index, vert_dim]
				core_right.x = point_coords.iloc[rival_a.index, hor_dim]
				core_right.y = point_coords.iloc[rival_a.index, vert_dim]
		elif (
			point_coords.iloc[rival_a.index, hor_dim]
			> point_coords.iloc[rival_b.index, hor_dim]
		):
			core_left.x = point_coords.iloc[rival_b.index, hor_dim]
			core_left.y = point_coords.iloc[rival_b.index, vert_dim]
			core_right.x = point_coords.iloc[rival_a.index, hor_dim]
			core_right.y = point_coords.iloc[rival_a.index, vert_dim]
		else:
			core_left.x = point_coords.iloc[rival_a.index, hor_dim]
			core_left.y = point_coords.iloc[rival_a.index, vert_dim]
			core_right.x = point_coords.iloc[rival_b.index, hor_dim]
			core_right.y = point_coords.iloc[rival_b.index, vert_dim]

		core_left_center = Point(core_left.x, core_left.y)
		core_right_center = Point(core_right.x, core_right.y)
		core_radius = self.core_radius

		self.core_left._center = core_left_center
		self.core_right._center = core_right_center
		self.core_left._radius = core_radius
		self.core_right._radius = core_radius

		return

	# ------------------------------------------------------------------------

	def _create_base_regions(self) -> None:
		self._determine_vertices_of_base_regions(self.west, self.east)

		self.base_left.vertices = CoordinateLists(
			x=self.base_left._x, y=self.base_left._y
		)
		self.base_right.vertices = CoordinateLists(
			x=self.base_right._x, y=self.base_right._y
		)
		self.base_neither.vertices = CoordinateLists(x=[], y=[])

		if self._director.common.have_scores():
			self.base_left_people_points = PeoplePoints(
				self.base_left._x, self.base_left._y
			)
			self.base_right_people_points = PeoplePoints(
				self.base_right._x, self.base_right._y
			)
			self.base_neither_people_points = PeoplePoints([], [])

		return

	# ------------------------------------------------------------------------

	def _determine_vertices_of_base_regions(
		self, west: West, east: East
	) -> None:
		base_left = self.base_left
		base_right = self.base_right

		base_left.outline = self._west_base(west)
		base_right.outline = self._east_base(east)

		self.base_left.outline = base_left.outline
		self.base_right.outline = base_right.outline

		# Taking transpose
		# x, y = data.T
		self.base_left._x, self.base_left._y = self.base_left.outline.T
		self.base_right._x, self.base_right._y = self.base_right.outline.T

		return

	# -----------------------------------------------------------------------

	def _west_base(self, west: West) -> np.array:
		(hor_max, hor_min, vert_max, vert_min) = (
			self._director.common.use_plot_ranges()
		)
		# WEST
		#
		west_dict = {
			"0a": np.array(
				[
					[west._start.x, west._start.y],
					[west._end.x, west._end.y],
					[hor_max, vert_min],
					[hor_min, vert_min],
				]
			),
			"0b": np.array(
				[
					[west._start.x, west._start.y],
					[west._end.x, west._end.y],
					[hor_min, vert_min],
					[hor_min, vert_max],
				]
			),
			"Ia": np.array(
				[
					[west._start.x, west._start.y],
					[west._end.x, west._end.y],
					[hor_max, vert_max],
					[hor_min, vert_max],
				]
			),
			"IIa": np.array(
				[
					[west._start.x, west._start.y],
					[west._end.x, west._end.y],
					[hor_min, vert_max],
				]
			),
			"IIIa": np.array(
				[
					[west._start.x, west._start.y],
					[west._end.x, west._end.y],
					[hor_max, vert_max],
					[hor_min, vert_max],
					[hor_min, vert_min],
				]
			),
			"IVa": np.array(
				[
					[west._start.x, west._start.y],
					[west._end.x, west._end.y],
					[hor_min, vert_max],
					[hor_min, vert_min],
				]
			),
			"Ib": np.array(
				[
					[west._start.x, west._start.y],
					[west._end.x, west._end.y],
					[hor_max, vert_min],
					[hor_min, vert_min],
				]
			),
			"IIb": np.array(
				[
					[west._start.x, west._start.y],
					[west._end.x, west._end.y],
					[hor_min, vert_min],
				]
			),
			"IIIb": np.array(
				[
					[west._start.x, west._start.y],
					[west._end.x, west._end.y],
					[hor_max, vert_min],
					[hor_min, vert_min],
					[hor_min, vert_max],
				]
			),
			"IVb": np.array(
				[
					[west._start.x, west._start.y],
					[west._end.x, west._end.y],
					[hor_min, vert_min],
					[hor_min, vert_max],
				]
			),
		}
		base_left_vertices = west_dict[west._case]
		#
		return base_left_vertices

	# -----------------------------------------------------------------------

	def _east_base(self, east: East) -> np.array:
		(hor_max, hor_min, vert_max, vert_min) = (
			self._director.common.use_plot_ranges()
		)

		# EAST
		#
		east_dict = {
			"0a": np.array(
				[
					[east._start.x, east._start.y],
					[east._end.x, east._end.y],
					[hor_max, vert_max],
					[hor_min, vert_max],
				]
			),
			"0b": np.array(
				[
					[east._start.x, east._start.y],
					[east._end.x, east._end.y],
					[hor_max, vert_min],
					[hor_max, vert_max],
				]
			),
			"Ia": np.array(
				[
					[east._start.x, east._start.y],
					[east._end.x, east._end.y],
					[hor_max, vert_min],
					[hor_min, vert_min],
				]
			),
			"IIa": np.array(
				[
					[east._start.x, east._start.y],
					[east._end.x, east._end.y],
					[hor_max, vert_max],
					[hor_max, vert_min],
					[hor_min, vert_min],
				]
			),
			"IIIa": np.array(
				[
					[east._start.x, east._start.y],
					[east._end.x, east._end.y],
					[hor_max, vert_min],
				]
			),
			"IVa": np.array(
				[
					[east._start.x, east._start.y],
					[east._end.x, east._end.y],
					[hor_max, vert_max],
					[hor_max, vert_min],
				]
			),
			"Ib": np.array(
				[
					[east._start.x, east._start.y],
					[east._end.x, east._end.y],
					[hor_max, vert_max],
					[hor_min, vert_max],
				]
			),
			"IIb": np.array(
				[
					[east._start.x, east._start.y],
					[east._end.x, east._end.y],
					[hor_min, vert_min],
				]
			),
			"IIIb": np.array(
				[
					[east._start.x, east._start.y],
					[east._end.x, east._end.y],
					[hor_max, vert_max],
				]
			),
			"IVb": np.array(
				[
					[east._start.x, east._start.y],
					[east._end.x, east._end.y],
					[hor_max, vert_min],
					[hor_max, vert_max],
				]
			),
		}
		base_right_vertices = east_dict[east._case]
		#
		return base_right_vertices

	# ------------------------------------------------------------------------

	def _create_likely_regions(self) -> None:
		self._determine_vertices_of_likely_regions()

		self.likely_left.vertices = CoordinateLists(
			x=self.likely_left._x, y=self.likely_left._y
		)
		self.likely_right.vertices = CoordinateLists(
			x=self.likely_right._x, y=self.likely_right._y
		)

		if self._director.common.have_scores():
			self.likely_left_people_points = PeoplePoints(
				self.likely_left._x, self.likely_left._y
			)
			self.likely_right_people_points = PeoplePoints(
				self.likely_right._x, self.likely_right._y
			)

		return

	# ------------------------------------------------------------------------

	def _determine_vertices_of_likely_regions(self) -> None:
		bisector = self.bisector

		(hor_max, hor_min, vert_max, vert_min) = (
			self._director.common.use_plot_ranges()
		)

		likely_left = self.likely_left
		likely_right = self.likely_right

		# Group cases by bisector direction for better readability and reduced
		# complexity
		if bisector._direction == "Flat":
			# Cases 0a - flat bisector
			self._likely_set_case_0a_vertices(
				likely_left, likely_right, bisector,
				hor_max, hor_min, vert_max, vert_min
			)
		elif bisector._direction == "Vertical":
			# Cases 0b - vertical bisector
			self._likely_set_case_0b_vertices(
				likely_left, likely_right, bisector,
				hor_max, hor_min, vert_max, vert_min
			)
		elif bisector._direction == "Upward slope":
			# Positive slope cases: Ia, IIa, IIIa, IVa
			self._likely_handle_upward_slope_cases(
				likely_left, likely_right, bisector,
				hor_max, hor_min, vert_max, vert_min
			)
		elif bisector._direction == "Downward slope":
			# Negative slope cases: Ib, IIb, IIIb, IVb
			self._likely_handle_downward_slope_cases(
				likely_left, likely_right, bisector,
				hor_max, hor_min, vert_max, vert_min
			)

		# Taking transpose
		#
		self.likely_left.outline = likely_left.outline
		self.likely_right.outline = likely_right.outline
		self.likely_left._x, self.likely_left._y = likely_left.outline.T
		self.likely_right._x, self.likely_right._y = likely_right.outline.T

		return

	# Helper functions for _determine_vertices_of_likely_regions

	def _likely_set_case_0a_vertices(
		self, likely_left: Polygon, likely_right: Polygon,
		bisector: LineInPlot, hor_max: float, hor_min: float,
		vert_max: float, vert_min: float
	) -> None:
		likely_right.outline = np.array(
			[
				[bisector._start.x, bisector._start.y],
				[bisector._end.x, bisector._end.y],
				[hor_max, vert_max],
				[hor_min, vert_max],
			]
		)
		likely_left.outline = np.array(
			[
				[bisector._start.x, bisector._start.y],
				[bisector._end.x, bisector._end.y],
				[hor_max, vert_min],
				[hor_min, vert_min],
			]
		)

	def _likely_set_case_0b_vertices(
		self, likely_left: Polygon, likely_right: Polygon,
		bisector: LineInPlot, hor_max: float, hor_min: float,
		vert_max: float, vert_min: float
	) -> None:
		likely_right.outline = np.array(
			[
				[bisector._start.x, bisector._start.y],
				[bisector._end.x, bisector._end.y],
				[hor_max, vert_min],
				[hor_max, vert_max],
			]
		)
		likely_left.outline = np.array(
			[
				[bisector._start.x, bisector._start.y],
				[bisector._end.x, bisector._end.y],
				[hor_min, vert_min],
				[hor_min, vert_max],
			]
		)

	def _likely_set_case_ia_vertices(
		self, likely_left: Polygon, likely_right: Polygon,
		bisector: LineInPlot, hor_max: float, hor_min: float,
		vert_max: float, vert_min: float
	) -> None:
		likely_right.outline = np.array(
			[
				[bisector._start.x, bisector._start.y],
				[bisector._end.x, bisector._end.y],
				[hor_max, vert_min],
				[hor_min, vert_min],
			]
		)
		likely_left.outline = np.array(
			[
				[bisector._start.x, bisector._start.y],
				[bisector._end.x, bisector._end.y],
				[hor_max, vert_max],
				[hor_min, vert_max],
			]
		)

	def _likely_set_case_iia_vertices(
		self, likely_left: Polygon, likely_right: Polygon,
		bisector: LineInPlot, hor_max: float, hor_min: float,
		vert_max: float, vert_min: float
	) -> None:
		likely_right.outline = np.array(
			[
				[bisector._start.x, bisector._start.y],
				[bisector._end.x, bisector._end.y],
				[hor_max, vert_max],
				[hor_max, vert_min],
				[hor_min, vert_min],
			]
		)
		likely_left.outline = np.array(
			[
				[bisector._start.x, bisector._start.y],
				[bisector._end.x, bisector._end.y],
				[hor_min, vert_max],
			]
		)

	def _likely_set_case_iiia_vertices(
		self, likely_left: Polygon, likely_right: Polygon,
		bisector: LineInPlot, hor_max: float, hor_min: float,
		vert_max: float, vert_min: float
	) -> None:
		likely_right.outline = np.array(
			[
				[bisector._start.x, bisector._start.y],
				[bisector._end.x, bisector._end.y],
				[hor_max, vert_max],
				[hor_max, vert_min],
				[hor_min, vert_min],
			]
		)
		likely_left.outline = np.array(
			[
				[bisector._start.x, bisector._start.y],
				[bisector._end.x, bisector._end.y],
				[hor_max, vert_max],
				[hor_min, vert_max],
				[hor_min, vert_min],
			]
		)

	def _likely_set_case_iva_vertices(
		self, likely_left: Polygon, likely_right: Polygon,
		bisector: LineInPlot, hor_max: float, hor_min: float,
		vert_max: float, vert_min: float
	) -> None:
		likely_right.outline = np.array(
			[
				[bisector._start.x, bisector._start.y],
				[bisector._end.x, bisector._end.y],
				[hor_max, vert_max],
				[hor_max, vert_min],
			]
		)
		likely_left.outline = np.array(
			[
				[bisector._start.x, bisector._start.y],
				[bisector._end.x, bisector._end.y],
				[hor_min, vert_max],
				[hor_min, vert_min],
			]
		)

	def _likely_set_case_ib_vertices(
		self, likely_left: Polygon, likely_right: Polygon,
		bisector: LineInPlot, hor_max: float, hor_min: float,
		vert_max: float, vert_min: float
	) -> None:
		likely_right.outline = np.array(
			[
				[bisector._start.x, bisector._start.y],
				[bisector._end.x, bisector._end.y],
				[hor_max, vert_max],
				[hor_min, vert_max],
			]
		)
		likely_left.outline = np.array(
			[
				[bisector._start.x, bisector._start.y],
				[bisector._end.x, bisector._end.y],
				[hor_max, vert_min],
				[hor_min, vert_min],
			]
		)

	def _likely_set_case_iib_vertices(
		self, likely_left: Polygon, likely_right: Polygon,
		bisector: LineInPlot, hor_max: float, hor_min: float,
		vert_max: float, vert_min: float
	) -> None:
		likely_right.outline = np.array(
			[
				[bisector._start.x, bisector._start.y],
				[bisector._end.x, bisector._end.y],
				[hor_max, vert_min],
				[hor_max, vert_max],
				[hor_min, vert_max],
			]
		)
		likely_left.outline = np.array(
			[
				[bisector._start.x, bisector._start.y],
				[bisector._end.x, bisector._end.y],
				[hor_min, vert_min],
			]
		)

	def _likely_set_case_iiib_vertices(
		self, likely_left: Polygon, likely_right: Polygon,
		bisector: LineInPlot, hor_max: float, hor_min: float,
		vert_max: float, vert_min: float
	) -> None:
		likely_right.outline = np.array(
			[
				[bisector._start.x, bisector._start.y],
				[bisector._end.x, bisector._end.y],
				[hor_max, vert_max],
			]
		)
		likely_left.outline = np.array(
			[
				[bisector._start.x, bisector._start.y],
				[bisector._end.x, bisector._end.y],
				[hor_max, vert_min],
				[hor_min, vert_min],
				[hor_min, vert_max],
			]
		)

	def _likely_set_case_ivb_vertices(
		self, likely_left: Polygon, likely_right: Polygon,
		bisector: LineInPlot, hor_max: float, hor_min: float,
		vert_max: float, vert_min: float
	) -> None:
		likely_right.outline = np.array(
			[
				[bisector._start.x, bisector._start.y],
				[bisector._end.x, bisector._end.y],
				[hor_max, vert_min],
				[hor_max, vert_max],
			]
		)
		likely_left.outline = np.array(
			[
				[bisector._start.x, bisector._start.y],
				[bisector._end.x, bisector._end.y],
				[hor_min, vert_min],
				[hor_min, vert_max],
			]
		)

	def _likely_handle_upward_slope_cases(
		self, likely_left: Polygon, likely_right: Polygon,
		bisector: LineInPlot, hor_max: float, hor_min: float,
		vert_max: float, vert_min: float
	) -> None:
		# Positive slope cases: Ia, IIa, IIIa, IVa
		match bisector._case:
			case "Ia":
				self._likely_set_case_ia_vertices(
					likely_left, likely_right, bisector,
					hor_max, hor_min, vert_max, vert_min
				)
			case "IIa":
				self._likely_set_case_iia_vertices(
					likely_left, likely_right, bisector,
					hor_max, hor_min, vert_max, vert_min
				)
			case "IIIa":
				self._likely_set_case_iiia_vertices(
					likely_left, likely_right, bisector,
					hor_max, hor_min, vert_max, vert_min
				)
			case "IVa":
				self._likely_set_case_iva_vertices(
					likely_left, likely_right, bisector,
					hor_max, hor_min, vert_max, vert_min
				)

	def _likely_handle_downward_slope_cases(
		self, likely_left: Polygon, likely_right: Polygon,
		bisector: LineInPlot, hor_max: float, hor_min: float,
		vert_max: float, vert_min: float
	) -> None:
		# Negative slope cases: Ib, IIb, IIIb, IVb
		match bisector._case:
			case "Ib":
				self._likely_set_case_ib_vertices(
					likely_left, likely_right, bisector,
					hor_max, hor_min, vert_max, vert_min
				)
			case "IIb":
				self._likely_set_case_iib_vertices(
					likely_left, likely_right, bisector,
					hor_max, hor_min, vert_max, vert_min
				)
			case "IIIb":
				self._likely_set_case_iiib_vertices(
					likely_left, likely_right, bisector,
					hor_max, hor_min, vert_max, vert_min
				)
			case "IVb":
				self._likely_set_case_ivb_vertices(
					likely_left, likely_right, bisector,
					hor_max, hor_min, vert_max, vert_min
				)

	# -----------------------------------------------------------------------

	def _create_battleground_regions(self) -> None:
		self._determine_vertices_of_battleground_regions(self.west, self.east)

		self.battleground_segment.vertices = CoordinateLists(
			x=self.battleground_segment._x, y=self.battleground_segment._y
		)
		self.battleground_settled.vertices = CoordinateLists(x=[], y=[])

		if self._director.common.have_scores():
			self.battleground_segment_people_points = PeoplePoints(
				self.battleground_segment._x, self.battleground_segment._y
			)
			self.battleground_settled_people_points = PeoplePoints([], [])

		return

	# -----------------------------------------------------------------------

	def _determine_vertices_of_battleground_regions(
		self, west: West, east: East
	) -> None:
		(hor_max, hor_min, vert_max, vert_min) = (
			self._director.common.use_plot_ranges()
		)

		battleground_segment = self.battleground_segment
		# battleground_settled = self.battleground_settled

		if (
			(west._right_side == east._right_side)
			and (west._left_side == east._left_side)
			and (west._top == east._top)
			and (west._bottom == east._bottom)
		):
			battleground_segment.outline = np.array(
				[
					[west._start.x, west._start.y],
					[west._end.x, west._end.y],
					[east._end.x, east._end.y],
					[east._start.x, east._start.y],
				]
			)

		#
		# Top Left only
		elif (
			east._top and east._bottom and west._left_side and west._right_side
		) or (
			east._top
			and east._right_side
			and west._left_side
			and west._right_side
		):
			#
			battleground_segment.outline = np.array(
				[
					[east._start.x, east._start.y],
					[east._end.x, east._end.y],
					[west._end.x, west._end.y],
					[west._start.x, west._start.y],
					[hor_min, vert_max],
				]
			)
		#
		# Top right only
		elif (
			west._top and west._bottom and east._right_side and east._bottom
		) or (
			west._top
			and west._left_side
			and east._right_side
			and east._left_side
		):
			#
			battleground_segment.outline = np.array(
				[
					[west._start.x, west._start.y],
					[west._end.x, west._end.y],
					[hor_max, vert_max],
					[east._end.x, east._end.y],
					[east._start.x, east._start.y],
				]
			)
		#
		# Bottom right only
		elif (
			east._top and east._right_side and west._top and west._bottom
		) or (
			east._left_side
			and east._right_side
			and west._left_side
			and west._bottom
		):
			#
			battleground_segment.outline = np.array(
				[
					[west._start.x, west._start.y],
					[west._end.x, west._end.y],
					[hor_max, vert_min],
					[east._end.x, east._end.y],
					[east._start.x, east._start.y],
				]
			)
		#
		# Bottom left only
		elif (
			west._top and west._left_side and east._top and east._bottom
		) or (
			west._right_side
			and west._left_side
			and east._right_side
			and east._bottom
		):
			#
			battleground_segment.outline = np.array(
				[
					[west._start.x, west._start.y],
					[west._end.x, west._end.y],
					[east._end.x, east._end.y],
					[east._start.x, east._start.y],
					[hor_min, vert_min],
				]
			)
			#
		# Both top right and bottom left ------ need reverse of 1 and 2 ????
		elif (
			west._top and west._left_side and east._right_side and east._bottom
		):
			#
			battleground_segment.outline = np.array(
				[
					[west._start.x, west._start.y],
					[west._end.x, west._end.y],
					[hor_max, vert_max],
					[east._end.x, east._end.y],
					[east._start.x, east._start.y],
					[hor_min, vert_min],
				]
			)
		#
		# Both top left and bottom right ------ need reverse of 1 and 2 ????
		elif (
			east._top and east._right_side and west._bottom and west._left_side
		):
			#
			battleground_segment.outline = np.array(
				[
					[west._start.x, west._start.y],
					[west._end.x, west._end.y],
					[hor_max, vert_min],
					[east._end.x, east._end.y],
					[east._start.x, east._start.y],
					[hor_min, vert_max],
				]
			)
		#
		# Taking transpose
		#
		self.battleground_segment.outline = battleground_segment.outline
		self.battleground_segment._x, self.battleground_segment._y = (
			battleground_segment.outline.T
		)

		return

	# ------------------------------------------------------------------------

	def _create_convertible_regions(self) -> None:
		self._determine_vertices_of_convertible_regions(
			self.bisector, self.west, self.east
		)
		self.convertible_to_left.vertices = CoordinateLists(
			x=self.convertible_to_left._x, y=self.convertible_to_left._y
		)
		self.convertible_to_right.vertices = CoordinateLists(
			x=self.convertible_to_right._x, y=self.convertible_to_right._y
		)
		self.convertible_settled.vertices = CoordinateLists(x=[], y=[])

		if self._director.common.have_scores():
			self.convertible_to_left_people_points = PeoplePoints(
				self.convertible_to_left._x, self.convertible_to_left._y
			)
			self.convertible_to_right_people_points = PeoplePoints(
				self.convertible_to_right._x, self.convertible_to_right._y
			)
			self.convertible_settled_people_points = PeoplePoints([], [])

		return

	# -----------------------------------------------------------------------

	def _determine_vertices_of_convertible_regions(
		self, bisector: object, west: West, east: East
	) -> None:
		(
			right_includes_upper_right_as_pairs,
			right_includes_lower_right_as_pairs,
			right_includes_upper_left_as_pairs,
			right_includes_lower_left_as_pairs,
			left_includes_lower_left_as_pairs,
			left_includes_upper_left_as_pairs,
			left_includes_lower_right_as_pairs,
			left_includes_upper_right_as_pairs,
			left_includes_lower_right_and_upper_left_as_pairs,
			left_includes_upper_right_and_lower_left_as_pairs,
			right_includes_upper_left_and_lower_right_as_pairs,
			right_includes_upper_right_and_lower_left_as_pairs
		) = self._define_convertible_regions(bisector, west, east)

		params = {
			"right_includes_upper_right_as_pairs":
				right_includes_upper_right_as_pairs,
			"right_includes_lower_right_as_pairs":
				right_includes_lower_right_as_pairs,
			"right_includes_upper_left_as_pairs":
				right_includes_upper_left_as_pairs,
			"right_includes_lower_left_as_pairs":
				right_includes_lower_left_as_pairs,
			"left_includes_lower_left_as_pairs":
				left_includes_lower_left_as_pairs,
			"left_includes_upper_left_as_pairs":
				left_includes_upper_left_as_pairs,
			"left_includes_lower_right_as_pairs":
				left_includes_lower_right_as_pairs,
			"left_includes_upper_right_as_pairs":
				left_includes_upper_right_as_pairs,
			"left_includes_lower_right_and_upper_left_as_pairs":
				left_includes_lower_right_and_upper_left_as_pairs,
			"left_includes_upper_right_and_lower_left_as_pairs":
				left_includes_upper_right_and_lower_left_as_pairs,
			"right_includes_upper_left_and_lower_right_as_pairs":
				right_includes_upper_left_and_lower_right_as_pairs,
			"right_includes_upper_right_and_lower_left_as_pairs":
				right_includes_upper_right_and_lower_left_as_pairs
		}

		(
			self.convertible_to_left.outline,
			self.convertible_to_right.outline,
		) = self._define_convertible_vertices(params)

		# convertible_to_left.outline and convertible_to_right.outline
		# assigned above
		#
		# # Taking transpose
		# x, y = data.T
		self.convertible_to_left._x, self.convertible_to_left._y = (
			self.convertible_to_left.outline.T
		)
		self.convertible_to_right._x, self.convertible_to_right._y = (
			self.convertible_to_right.outline.T
		)

		return

	# -----------------------------------------------------------------------

	def _define_convertible_regions(
		self, bisector: Bisector, west: West, east: East
	) -> tuple:
		(hor_max, hor_min, vert_max, vert_min) = (
			self._director.common.use_plot_ranges()
		)
		#
		# Create convertible regions
		#
		right_includes_upper_right_as_pairs = np.array(
			[
				[bisector._start.x, bisector._start.y],
				[bisector._end.x, bisector._end.y],
				[hor_max, vert_max],
				[west._end.x, west._end.y],
				[west._start.x, west._start.y],
			]
		)
		right_includes_lower_right_as_pairs = np.array(
			[
				[bisector._start.x, bisector._start.y],
				[bisector._end.x, bisector._end.y],
				[hor_max, vert_min],
				[west._end.x, west._end.y],
				[west._start.x, west._start.y],
			]
		)
		right_includes_upper_left_as_pairs = np.array(
			[
				[bisector._start.x, bisector._start.y],
				[bisector._end.x, bisector._end.y],
				[west._end.x, west._end.y],
				[west._start.x, west._start.y],
				[hor_min, vert_max],
			]
		)
		right_includes_lower_left_as_pairs = np.array(
			[
				[bisector._start.x, bisector._start.y],
				[bisector._end.x, bisector._end.y],
				[west._end.x, west._end.y],
				[west._start.x, west._start.y],
				[hor_min, vert_min],
			]
		)
		left_includes_lower_left_as_pairs = np.array(
			[
				[bisector._start.x, bisector._start.y],
				[bisector._end.x, bisector._end.y],
				# [hor_min, vert_min],
				[east._end.x, east._end.y],
				[east._start.x, east._start.y],
				[hor_min, vert_min],
			]
		)
		left_includes_upper_left_as_pairs = np.array(
			[
				[bisector._start.x, bisector._start.y],
				[bisector._end.x, bisector._end.y],
				[east._end.x, east._end.y],
				[east._start.x, east._start.y],
				[hor_min, vert_max],
			]
		)
		left_includes_lower_right_as_pairs = np.array(
			[
				[bisector._start.x, bisector._start.y],
				[bisector._end.x, bisector._end.y],
				[hor_max, vert_min],
				[east._end.x, east._end.y],
				[east._start.x, east._start.y],
			]
		)
		left_includes_upper_right_as_pairs = np.array(
			[
				[bisector._start.x, bisector._start.y],
				[bisector._end.x, bisector._end.y],
				[hor_max, vert_max],
				[east._end.x, east._end.y],
				[east._start.x, east._start.y],
			]
		)
		left_includes_lower_right_and_upper_left_as_pairs = np.array(
			[
				[bisector._start.x, bisector._start.y],
				[bisector._end.x, bisector._end.y],
				[hor_max, vert_min],
				[east._end.x, east._end.y],
				[east._start.x, east._start.y],
				[hor_min, vert_max],
			]
		)
		left_includes_upper_right_and_lower_left_as_pairs = np.array(
			[
				[bisector._start.x, bisector._start.y],
				[bisector._end.x, bisector._end.y],
				[hor_max, vert_max],
				[east._end.x, east._end.y],
				[east._start.x, east._start.y],
				[hor_min, vert_min],
			]
		)
		right_includes_upper_left_and_lower_right_as_pairs = np.array(
			[
				[bisector._start.x, bisector._start.y],
				[bisector._end.x, bisector._end.y],
				[hor_max, vert_max],
				[west._end.x, west._end.y],
				[west._start.x, west._start.y],
				[hor_min, vert_min],
			]
		)
		right_includes_upper_right_and_lower_left_as_pairs = np.array(
			[
				[bisector._start.x, bisector._start.y],
				[bisector._end.x, bisector._end.y],
				[hor_max, vert_min],
				[west._end.x, west._end.y],
				[west._start.x, west._start.y],
				[hor_min, vert_max],
			]
		)
		#
		# Bisector Case 0a Bisector slope is zero from Left side to Right side
		# Bisector Case 0b Connector slope is zero - from top to bottom
		# Bisector Case Ia Positive slope from Left side to Right side
		# bisector test is redundant, case includes slope, but improves
		# efficiency
		#
		# self.bisector = bisector
		# self.west = west
		# self.east = east

		return (
			right_includes_upper_right_as_pairs,
			right_includes_lower_right_as_pairs,
			right_includes_upper_left_as_pairs,
			right_includes_lower_left_as_pairs,
			left_includes_lower_left_as_pairs,
			left_includes_upper_left_as_pairs,
			left_includes_lower_right_as_pairs,
			left_includes_upper_right_as_pairs,
			left_includes_lower_right_and_upper_left_as_pairs,
			left_includes_upper_right_and_lower_left_as_pairs,
			right_includes_upper_left_and_lower_right_as_pairs,
			right_includes_upper_right_and_lower_left_as_pairs
		)

	# -----------------------------------------------------------------------

	def _define_convertible_vertices(
		self,
		params: dict
	) -> tuple:


		#
		# Establish default areas
		#
		rivalry = self._director.rivalry
		bisector = rivalry.bisector
		west = rivalry.west
		east = rivalry.east

		# (hor_max, hor_min, vert_max, vert_min) = (
		# 	self._director.common.use_plot_ranges()
		# )

		(
			convertible_to_left_vertices_as_pairs,
			convertible_to_right_vertices_as_pairs,
		) = self._convertible_default_vertices()
		#
		# Bisector Case 0a Bisector slope is zero from Left side to Right side
		# Bisector Case 0b Connector slope is zero - from top to bottom
		# Bisector Case Ia Positive slope from Left side to Right side
		# bisector test is redundant, case includes slope, but improves
		# efficiency
		#
		(
			convertible_to_left_vertices_as_pairs,
			convertible_to_right_vertices_as_pairs,
		) = self._handle_convertible_slope_cases(
			bisector,
			west,
			east,
			convertible_to_left_vertices_as_pairs,
			convertible_to_right_vertices_as_pairs,
			params
		)

		return (
			convertible_to_left_vertices_as_pairs,
			convertible_to_right_vertices_as_pairs,
		)

# -----------------------------------------------------------------------

	def _convertible_default_vertices(self) -> tuple[np.array, np.array]:
		"""
		Create default convertible vertices for left and right regions.

		The default case establishes the basic rectangular regions defined by
		the bisector and east/west lines before any case-specific
		modifications.

		Returns:
			tuple: (convertible_to_left_vertices_as_pairs,
					convertible_to_right_vertices_as_pairs)
		"""
		rivalry = self._director.rivalry
		bisector = rivalry.bisector
		west = rivalry.west
		east = rivalry.east

		convertible_to_left_vertices_as_pairs = np.array(
			[
				[bisector._start.x, bisector._start.y],
				[bisector._end.x, bisector._end.y],
				[east._end.x, east._end.y],
				[east._start.x, east._start.y],
			]
		)
		convertible_to_right_vertices_as_pairs = np.array(
			[
				[bisector._start.x, bisector._start.y],
				[bisector._end.x, bisector._end.y],
				[west._end.x, west._end.y],
				[west._start.x, west._start.y],
			]
		)

		return (
			convertible_to_left_vertices_as_pairs,
			convertible_to_right_vertices_as_pairs,
		)
# -----------------------------------------------------------------------

	def _handle_convertible_slope_cases(
		self,
		bisector: Bisector,
		west: West,
		east: East,
		convertible_to_left_vertices_as_pairs: np.array,
		convertible_to_right_vertices_as_pairs: np.array,
		params: dict
	) -> tuple[np.array, np.array]:
		right_includes_upper_right_as_pairs = params[
			"right_includes_upper_right_as_pairs"]
		left_includes_lower_left_as_pairs = params[
			"left_includes_lower_left_as_pairs"]
		left_includes_upper_right_as_pairs = params[
			"left_includes_upper_right_as_pairs"]
		right_includes_lower_left_as_pairs = params[
			"right_includes_lower_left_as_pairs"]
		right_includes_lower_right_as_pairs = params[
			"right_includes_lower_right_as_pairs"]
		left_includes_upper_left_as_pairs = params[
			"left_includes_upper_left_as_pairs"]
		right_includes_upper_left_as_pairs = params[
			"right_includes_upper_left_as_pairs"]
		left_includes_lower_right_as_pairs = params[
			"left_includes_lower_right_as_pairs"]
		left_includes_lower_right_and_upper_left_as_pairs = params[
			"left_includes_lower_right_and_upper_left_as_pairs"]
		# left_includes_upper_right_and_lower_left_as_pairs = params[
		# 	"left_includes_upper_right_and_lower_left_as_pairs"]
		right_includes_upper_left_and_lower_right_as_pairs = params[
			"right_includes_upper_left_and_lower_right_as_pairs"]
		right_includes_upper_right_and_lower_left_as_pairs = params[
			"right_includes_upper_right_and_lower_left_as_pairs"]
		"""Establish convertible region vertices for all slope cases."""

		# Establish keys for case combinations with their respective
		# vertices pairs
		case_combination = {
			# Active upward slope cases
			"Ia_IIa_Ia": lambda: (
				convertible_to_left_vertices_as_pairs,
				right_includes_upper_right_as_pairs
			),  # test with ------EV, TC
			"IIa_IIa_Ia": lambda: (
				left_includes_upper_right_as_pairs,
				convertible_to_right_vertices_as_pairs
			),  # test with ------BK
			"IIa_IIa_IVa": lambda: (
				left_includes_lower_left_as_pairs,
				convertible_to_right_vertices_as_pairs
			),  # test with -----TS,BL
			"IIIa_Ia_IIIa": lambda: (
				convertible_to_left_vertices_as_pairs,
				right_includes_lower_left_as_pairs
			),  # test with GP
			"IIIa_IIa_IIIa": lambda: (
				convertible_to_left_vertices_as_pairs,
				right_includes_upper_left_and_lower_right_as_pairs
			),  # test with BC
			"IIIa_IVa_IIIa": lambda: (
				convertible_to_left_vertices_as_pairs,
				right_includes_upper_right_as_pairs
			),  # test with -----CG
			"IVa_IIa_IVa": lambda: (
				convertible_to_left_vertices_as_pairs,
				right_includes_lower_left_as_pairs
			),  # test with -----TN
			"IVa_IVa_IIIa": lambda: (
				left_includes_upper_right_as_pairs,
				convertible_to_right_vertices_as_pairs
			),  # test with ----BR
			# Active downward slope cases
			"Ib_Ib_IIIb": lambda: (
				left_includes_upper_left_as_pairs,
				convertible_to_right_vertices_as_pairs,
			),  # test with ----AO
			"Ib_IIb_Ib": lambda: (
				convertible_to_left_vertices_as_pairs,
				right_includes_lower_right_as_pairs
			),  # test with EP
			"IIb_IIb_Ib": lambda: (
				left_includes_lower_right_as_pairs,
				convertible_to_right_vertices_as_pairs
			),  # test with IY, HI
			"IIb_IIb_IIIb": lambda: (
				left_includes_lower_right_and_upper_left_as_pairs,
				convertible_to_right_vertices_as_pairs
			),  # test with ?????????
			"IIIb_IIb_IIIb": lambda: (
				convertible_to_left_vertices_as_pairs,
				right_includes_upper_right_and_lower_left_as_pairs
			),  # test with  AI
			"IIIb_IVb_IIIb": lambda: (
				convertible_to_left_vertices_as_pairs,
				right_includes_lower_right_as_pairs
			),  # test with -----AG
			"IVb_IIb_IVb": lambda: (
				convertible_to_left_vertices_as_pairs,
				right_includes_upper_left_as_pairs
			),  # test with -----EI
			"IVb_IVb_IIIb": lambda: (
				left_includes_lower_right_as_pairs,
				convertible_to_right_vertices_as_pairs
			),  # test with ----AF
		}

		# Add all default cases explicitly
		def default_result() -> tuple[np.array, np.array]:
			return (
				convertible_to_left_vertices_as_pairs,
				convertible_to_right_vertices_as_pairs
			)
		bisector_cases = [
			"0a", "0b", "Ia", "Ib", "IIa", "IIb", "IIIa", "IIIb", "IVa",
			"IVb"
		]
		west_cases = [
			"", "0a", "0b", "Ia", "Ib", "IIa", "IIb", "IIIa", "IIIb",
			"IVa", "IVb"
		]
		east_cases = [
			"", "0a", "0b", "Ia", "Ib", "IIa", "IIb", "IIIa", "IIIb",
			"IVa", "IVb"
		]

		for bisector_case in bisector_cases:
			for west_case in west_cases:
				for east_case in east_cases:
					key = f"{bisector_case}_{west_case}_{east_case}"
					if key not in case_combination:
						case_combination[key] = default_result

		case_key = f"{bisector._case}_{west._case}_{east._case}"
		result = case_combination[case_key]()

		return result


	# ------------------------------------------------------------------------

	def _create_first_dimension_regions(self) -> None:
		self._determine_vertices_of_first_dim_regions()

		self.first_left.vertices = CoordinateLists(
			x=self.first_left._x, y=self.first_left._y
		)
		self.first_right_vertices_as_lists = CoordinateLists(
			x=self.first_right._x, y=self.first_right._y
		)

		if self._director.common.have_scores():
			self.first_left_people_points = PeoplePoints(
				self.first_left._x, self.first_left._y
			)
			self.first_right_people_points = PeoplePoints(
				self.first_right._x, self.first_right._y
			)

		return

	# -----------------------------------------------------------------------

	def _determine_vertices_of_first_dim_regions(self) -> None:
		(hor_max, hor_min, vert_max, vert_min) = (
			self._director.common.use_plot_ranges()
		)

		rivalry = self._director.rivalry
		first_div = rivalry.first_div

		first_left = rivalry.first_left
		first_right = rivalry.first_right

		self.first_right.outline = np.array(
			[
				[hor_max, vert_max],
				[first_div, vert_max],
				[first_div, vert_min],
				[hor_max, vert_min],
			]
		)
		self.first_left.outline = np.array(
			[
				[hor_min, vert_max],
				[first_div, vert_max],
				[first_div, vert_min],
				[hor_min, vert_min],
			]
		)
		# # Taking transpose
		self.first_left.outline = first_left.outline
		self.first_right.outline = first_right.outline
		self.first_left._x, self.first_left._y = self.first_left.outline.T
		self.first_right._x, self.first_right._y = self.first_right.outline.T

		return

	# -------------------------------------------------------------------------

	def _determine_vertices_of_second_dim_regions(self) -> None:
		(hor_max, hor_min, vert_max, vert_min) = (
			self._director.common.use_plot_ranges()
		)

		rivalry = self._director.rivalry
		second_div = rivalry.second_div

		second_up = rivalry.second_up
		second_down = rivalry.second_down

		self.second_up.outline = np.array(
			[
				[hor_min, second_div],
				[hor_min, vert_max],
				[hor_max, vert_max],
				[hor_max, second_div],
			]
		)
		self.second_down.outline = np.array(
			[
				[hor_max, second_div],
				[hor_max, vert_min],
				[hor_min, vert_min],
				[hor_min, second_div],
			]
		)
		#
		# Taking transpose
		#
		self.second_up.outline = second_up.outline
		self.second_down.outline = second_down.outline
		second_up._x, second_up._y = self.second_up.outline.T
		second_down._x, second_down._y = self.second_down.outline.T

		return

	# -----------------------------------------------------------------------

	def _create_second_dimension_regions(self) -> None:
		self._determine_vertices_of_second_dim_regions()

		self.second_up.vertices = CoordinateLists(
			x=self.second_up._x, y=self.second_up._y
		)
		self.second_down.vertices = CoordinateLists(
			x=self.second_down._x, y=self.second_down._y
		)

		if self._director.common.have_scores():
			self.second_up_people_points = PeoplePoints(
				self.second_up._x, self.second_up._y
			)
			self.second_down_people_points = PeoplePoints(
				self.second_down._x, self.second_down._y
			)

		return

	# ------------------------------------------------------------------------

	def set_connector_direction(
		self,
		point_coords: pd.DataFrame,
		rival_a: Point,
		rival_b: Point,
		hor_dim: int,
		vert_dim: int,
	) -> str:
		if (
			point_coords.iloc[rival_a.index, hor_dim]
			== point_coords.iloc[rival_b.index, hor_dim]
		):
			connector_direction = "Vertical"
		if (
			point_coords.iloc[rival_a.index, vert_dim]
			== point_coords.iloc[rival_b.index, vert_dim]
		):
			connector_direction = "Flat"
		#
		if (
			(
				point_coords.iloc[rival_a.index, hor_dim]
				< point_coords.iloc[rival_b.index, hor_dim]
			)
			and (
				point_coords.iloc[rival_a.index, vert_dim]
				> point_coords.iloc[rival_b.index, vert_dim]
			)
		) or (
			(
				point_coords.iloc[rival_a.index, hor_dim]
				> point_coords.iloc[rival_b.index, hor_dim]
			)
			and (
				point_coords.iloc[rival_a.index, vert_dim]
				< point_coords.iloc[rival_b.index, vert_dim]
			)
		):
			connector_direction = "Downward slope"
		#
		if (
			(
				point_coords.iloc[rival_a.index, hor_dim]
				< point_coords.iloc[rival_b.index, hor_dim]
			)
			and (
				point_coords.iloc[rival_a.index, vert_dim]
				< point_coords.iloc[rival_b.index, vert_dim]
			)
		) or (
			(
				point_coords.iloc[rival_a.index, hor_dim]
				> point_coords.iloc[rival_b.index, hor_dim]
			)
			and (
				point_coords.iloc[rival_a.index, vert_dim]
				> point_coords.iloc[rival_b.index, vert_dim]
			)
		):
			connector_direction = "Upward slope"

		return connector_direction

	# ------------------------------------------------------------------------

	def set_connector_length(
		self,
		point_coords: pd.DataFrame,
		rival_a: Point,
		rival_b: Point,
		hor_dim: int,
		vert_dim: int,
	) -> tuple[float]:
		sumofsqs = (
			point_coords.iloc[rival_a.index, hor_dim]
			- point_coords.iloc[rival_b.index, hor_dim]
		) ** 2 + (
			point_coords.iloc[rival_a.index, vert_dim]
			- point_coords.iloc[rival_b.index, vert_dim]
		) ** 2
		connector_length = math.sqrt(sumofsqs)

		return connector_length

	# ------------------------------------------------------------------------

	def set_core_radius(self) -> float:
		"""
		Determines the radius of the core region based on connector length
		and core tolerance.
		#"""

		connector_length = self._director.rivalry.connector.length
		core_tolerance = self._director.common.core_tolerance

		core_radius = connector_length * core_tolerance

		return core_radius

	# ------------------------------------------------------------------------

	def theoretical_extremes(
		self, slope: float, intercept: float
	) -> TheoreticalExtremes:
		# the return has been modified to return a named tuple

		(hor_max, hor_min, vert_max, vert_min) = (
			self._director.common.use_plot_ranges()
		)

		# self.bisector passes through top or bottom
		y_at_hor_max = (slope * hor_max) + intercept
		y_at_hor_min = (slope * hor_min) + intercept
		x_at_vert_max = (vert_max - intercept) / slope
		x_at_vert_min = (vert_min - intercept) / slope

		return TheoreticalExtremes(
			y_at_hor_max, y_at_hor_min, x_at_vert_max, x_at_vert_min
		)

	# ------------------------------------------------------------------------

	def set_sides_line_goes_through(
		self,
		bisector_direction: str,
		connector_direction: str,
		y_at_hor_max: float,
		y_at_hor_min: float,
		x_at_vert_max: float,
		x_at_vert_min: float,
	) -> tuple[bool, bool, bool, bool]:
		(hor_max, hor_min, vert_max, vert_min) = (
			self._director.common.use_plot_ranges()
		)

		right_side = False
		left_side = False
		top = False
		bottom = False

		if bisector_direction == "Flat":
			right_side = True
			left_side = True
			top = False
			bottom = False
		if connector_direction == "Flat":
			right_side = False
			left_side = False
			top = True
			bottom = True
		if bisector_direction != ("Flat" and connector_direction != "Flat"):
			if vert_min <= y_at_hor_max <= vert_max:
				right_side = True
			if vert_min <= y_at_hor_min <= vert_max:
				left_side = True
			if hor_min <= x_at_vert_max <= hor_max:
				top = True
			if hor_min <= x_at_vert_min <= hor_max:
				bottom = True

		return left_side, right_side, top, bottom

	# ------------------------------------------------------------------------

	def handle_corners(
		self,
		left_side: bool,  # noqa: FBT001
		right_side: bool,  # noqa: FBT001
		top: bool,  # noqa: FBT001
		bottom: bool,  # noqa: FBT001
		y_at_hor_max: float,
		y_at_hor_min: float,
		x_at_vert_max: float,
		x_at_vert_min: float,
	) -> tuple[bool, bool, bool, bool]:
		(hor_max, hor_min, vert_max, vert_min) = (
			self._director.common.use_plot_ranges()
		)

		# Handle lines going through corners
		#
		# upper right
		if x_at_vert_max == hor_max and y_at_hor_max == vert_max:
			(top, right_side) = self.choose_a_side_function()
		# upper left
		if x_at_vert_max == hor_min and y_at_hor_min == vert_max:
			(top, left_side) = self.choose_a_side_function()
		# lower right
		if x_at_vert_min == hor_max and y_at_hor_max == vert_min:
			(bottom, right_side) = self.choose_a_side_function()
		# lower left
		if x_at_vert_min == hor_min and y_at_hor_min == vert_min:
			(bottom, left_side) = self.choose_a_side_function()

		return left_side, right_side, top, bottom

	# ------------------------------------------------------------------------

	def handle_bisector_corners(
		self,
		right_side: bool,  # noqa: FBT001
		left_side: bool,  # noqa: FBT001
		top: bool,  # noqa: FBT001
		bottom: bool,  # noqa: FBT001
		bisector_y_at_hor_max: float,
		bisector_y_at_hor_min: float,
		bisector_x_at_vert_max: float,
		bisector_x_at_vert_min: float,
	) -> tuple[bool, bool, bool, bool]:
		(hor_max, hor_min, vert_max, vert_min) = (
			self._director.common.use_plot_ranges()
		)

		# Handle lines going through corners
		#
		# upper right
		if (
			bisector_x_at_vert_max == hor_max
			and bisector_y_at_hor_max == vert_max
		):
			(top, right_side) = self.choose_a_side_function()
		# upper left
		if (
			bisector_x_at_vert_max == hor_min
			and bisector_y_at_hor_min == vert_max
		):
			(top, left_side) = self.choose_a_side_function()
		# lower right
		if (
			bisector_x_at_vert_min == hor_max
			and bisector_y_at_hor_max == vert_min
		):
			(bottom, right_side) = self.choose_a_side_function()
		# lower left
		if (
			bisector_x_at_vert_min == hor_min
			and bisector_y_at_hor_min == vert_min
		):
			(bottom, left_side) = self.choose_a_side_function()

		return right_side, left_side, top, bottom

	# ------------------------------------------------------------------------

	def handle_east_corners(
		self,
		right_side: float,
		left_side: float,
		top: float,
		bottom: float,
		east_y_at_hor_max: float,
		east_y_at_hor_min: float,
		east_x_at_vert_max: float,
		east_x_at_vert_min: float,
	) -> tuple[float, float, float, float]:
		(hor_max, hor_min, vert_max, vert_min) = (
			self._director.common.use_plot_ranges()
		)

		#
		# upper right
		if east_x_at_vert_max == hor_max and east_y_at_hor_max == vert_max:
			(top, right_side) = self.choose_a_side_function()
		# upper left
		if east_x_at_vert_max == hor_min and east_y_at_hor_min == vert_max:
			(top, left_side) = self.choose_a_side_function()
		# lower right
		if east_x_at_vert_min == hor_max and east_y_at_hor_max == vert_min:
			(bottom, right_side) = self.choose_a_side_function()
		# lower left
		if east_x_at_vert_min == hor_min and east_y_at_hor_min == vert_min:
			(bottom, left_side) = self.choose_a_side_function()

		return right_side, left_side, top, bottom

	# -----------------------------------------------------------------------

	def establish_each_contributions_to_connector_length(
		self,
	) -> tuple[float, float]:
		point_coords = self._director.configuration_active.point_coords
		rival_a = self.rival_a
		rival_b = self.rival_b
		battleground_size = self._director.common.battleground_size

		# Determine distance and each dimension's contribution to distance
		#
		differ_x = (
			point_coords.iloc[rival_a.index, 0]
			/ -point_coords.iloc[rival_b.index, 0]
		)
		differ_y = (
			point_coords.iloc[rival_a.index, 1]
			/ -point_coords.iloc[rival_b.index, 1]
		)
		sq_diff_x = differ_x * differ_x
		sq_diff_y = differ_y * differ_y
		x_dist = math.sqrt(sq_diff_x)
		y_dist = math.sqrt(sq_diff_y)
		#
		# Determine width of battleground based on portion of distance
		# between reference point
		# tolerance is set in main  - default is.1
		#
		half_battleground_x = battleground_size * x_dist
		half_battleground_y = battleground_size * y_dist

		return half_battleground_x, half_battleground_y

	# ------------------------------------------------------------------------

	def use_reference_points_to_define_segments(
		self,
		director: Status  # noqa: ARG002
	) -> None:
		if not self._director.common.have_scores() \
			or not self._director.common.have_reference_points():
			return
		score_1_name = self._director.scores_active.score_1_name
		score_2_name = self._director.scores_active.score_2_name
		segment_names = self.segment_names

		segments = pd.DataFrame(
			columns=[score_1_name, score_2_name, segment_names]
		)
		self.seg = segments

		return

	# ------------------------------------------------------------------------

	def _establish_regions_defining_contest_and_segments(self) -> None:
		# rival_a: Point,
		# rival_b: Point,
		# point_coords: pd.DataFrame,
		# battleground_percent: float) -> None:

		self._create_core_regions()
		self._create_base_regions()
		self._create_likely_regions()
		self._create_battleground_regions()
		self._create_convertible_regions()
		self._create_first_dimension_regions()
		self._create_second_dimension_regions()

		return


# -------------------------------------------------------------------------


class Connector(LineInPlot):
	def __init__(
		self,
		director: Status | None = None,
		point_on_line: Point | None = None,
		slope: float | None = None,
		rival_a: Point | None = None,
		rival_b: Point | None = None,
		color: str = "black",
		thickness: int = 1,
		style: str = "solid",
	) -> None:
		super().__init__(
			director, point_on_line, slope, color, thickness, style
		)

		if director is not None:
			self._director = director

		# Only calculate length if both rivals are provided
		if rival_a is not None and rival_b is not None:
			self.length = self._calculate_connector_length(rival_a, rival_b)
		else:
			self.length = 0.0

	# -------------------------------------------------------------------------

	def _calculate_connector_length(
		self, rival_a: Point, rival_b: Point
	) -> float:
		"""Calculates the length of a line between points rival_a and
		rival_b."""
		length = math.sqrt(
			(rival_b.x - rival_a.x) ** 2 + (rival_b.y - rival_a.y) ** 2
		)
		return length


# -------------------------------------------------------------------------


class First(LineInPlot):
	def __init__(
		self,
		director: Status | None = None,
		point_on_line: Point | None = None,
		slope: float | None = None,
		color: str = "black",
		thickness: int = 1,
		style: str = "solid",
	) -> None:
		super().__init__(
			director, point_on_line, slope, color, thickness, style
		)


# -------------------------------------------------------------------------


class Second(LineInPlot):
	def __init__(
		self,
		director: Status | None = None,
		point_on_line: Point | None = None,
		slope: float | None = None,
		color: str = "black",
		thickness: int = 1,
		style: str = "solid",
	) -> None:
		super().__init__(
			director, point_on_line, slope, color, thickness, style
		)


# --------------------------------------------------------------------------


class Segmentation:
	def __init__(
		self,
		name: str,
		n_categories: int,
		pcts: pd.Series,
		regions: list[Region],
		tribes: list[str],
	) -> None:
		self._name = name
		self._n_categories = n_categories
		self._pcts = pcts
		self._regions = regions
		self._tribes = tribes


# -------------------------------------------------------------------------


class SegmentPercentages(NamedTuple):
	# to be phased out

	base_pcts: pd.Series
	conv_pcts: pd.Series
	core_pcts: pd.Series
	likely_pcts: pd.Series
	battleground_pcts: pd.Series
	first_pcts: pd.Series
	second_pcts: pd.Series


# -------------------------------------------------------------------------


class West(LineInPlot):
	def __init__(
		self,
		director: Status | None = None,
		point_on_line: Point | None = None,
		slope: float | None = None,
		color: str = "black",
		thickness: int = 1,
		style: str = "solid",
	) -> None:
		super().__init__(
			director, point_on_line, slope, color, thickness, style
		)

		if director is not None:
			self._director = director
