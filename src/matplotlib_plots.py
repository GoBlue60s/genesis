from __future__ import annotations

import numpy as np

from matplotlib import pyplot as plt

# from archive import rivalry
from constants import MAXIMUM_NUMBER_OF_DIMENSIONS_FOR_PLOTTING
from exceptions import DependencyError

from typing import TYPE_CHECKING, cast

if TYPE_CHECKING:
	import pandas as pd
	from associationsmenu import AlikeCommand, StressContributionCommand
	from director import Status
	from respondentsmenu import (
		BaseCommand,
		BattlegroundCommand,
		ConvertibleCommand,
		CoreSupportersCommand,
		FirstDimensionCommand,
		LikelySupportersCommand,
		SecondDimensionCommand,
	)
	from rivalry import Bisector, East, West

	# from common import Spaces
	from geometry import PeoplePoints

# ------------------------------------------------------------------------


class MatplotlibMethods:
	def __init__(self, director: Status) -> None:
		from director import Status  # noqa: PLC0415, F401

		# from common import Spaces
		self._director = director

	# ------------------------------------------------------------------------

	def request_alike_plot_for_tabs_using_matplotlib(self) -> None:
		director = self._director
		common = director.common
		matplotlib_common = director.matplotlib_common
		point_coords = director.configuration_active.point_coords

		common.set_axis_extremes_based_on_coordinates(point_coords)
		fig = self._plot_alike_using_matplotlib()

		if fig is not None:
			matplotlib_common.plot_to_gui_using_matplotlib(fig)

		return

	# ------------------------------------------------------------------------

	def _plot_alike_using_matplotlib(self) -> plt.Figure | None:
		"""plot alike  -creates a plot with a line joining points with
		high similarity.
		A plot of the configuration will be created with a line joining pairs
		of points with
		a similarity above (or if dissimilarities, below) the cutoff.
		"""

		director = self._director
		common = director.common
		matplotlib_common = director.matplotlib_common
		configuration_active = director.configuration_active
		current_command = cast("AlikeCommand", director.current_command)

		if not common.have_alike_coords():
			title = "No alike points available for plotting"
			message = (
				"Open Similarities and establish configuration before"
				" using Alike."
			)
			raise DependencyError(title, message)

		a_x_alike = current_command.a_x_alike
		a_y_alike = current_command.a_y_alike
		b_x_alike = current_command.b_x_alike
		b_y_alike = current_command.b_y_alike

		ndim = configuration_active.ndim

		if ndim > MAXIMUM_NUMBER_OF_DIMENSIONS_FOR_PLOTTING:
			director.set_focus_on_tab("Output")
			return None

		fig, ax = matplotlib_common.begin_matplotlib_plot_with_title(None)
		ax = matplotlib_common.set_aspect_and_grid_in_matplotlib_plot(ax)

		matplotlib_common.add_axes_labels_to_matplotlib_plot(ax)
		matplotlib_common.set_ranges_for_matplotlib_plot(ax)
		matplotlib_common.add_configuration_to_matplotlib_plot(ax)

		nalike = range(len(a_x_alike))
		for each_alike in nalike:
			ax.plot(
				(a_x_alike[each_alike], b_x_alike[each_alike]),
				(a_y_alike[each_alike], b_y_alike[each_alike]),
				color="k",
			)

		director.set_focus_on_tab("Plot")

		return fig

	# ------------------------------------------------------------------------

	def request_base_plot_for_tabs_using_matplotlib(self) -> None:
		director = self._director
		common = director.common
		matplotlib_common = director.matplotlib_common
		configuration_active = director.configuration_active
		point_coords = configuration_active.point_coords
		current_command = cast("BaseCommand", director.current_command)

		base_groups_to_show = current_command._base_groups_to_show

		common.set_axis_extremes_based_on_coordinates(point_coords)
		fig = self._plot_base_using_matplotlib(base_groups_to_show)

		if fig is not None:
			matplotlib_common.plot_to_gui_using_matplotlib(fig)

		return

	# ------------------------------------------------------------------------

	def _plot_base_using_matplotlib(
		self, base_groups_to_show: str
	) -> plt.Figure | None:
		director = self._director
		matplotlib_common = director.matplotlib_common
		matplotlib_plotter = director.matplotlib_plotter
		configuration_active = director.configuration_active
		ndim = configuration_active.ndim

		if ndim > MAXIMUM_NUMBER_OF_DIMENSIONS_FOR_PLOTTING:
			director.set_focus_on_tab("Output")
			return None

		fig, ax = matplotlib_common.begin_matplotlib_plot_with_title(
			"Base Supporters"
		)
		ax = matplotlib_common.set_aspect_and_grid_in_matplotlib_plot(ax)

		matplotlib_common.add_axes_labels_to_matplotlib_plot(ax)
		matplotlib_common.set_ranges_for_matplotlib_plot(ax)
		matplotlib_common.add_reference_points_to_matplotlib_plot(ax)
		matplotlib_common.add_connector_to_matplotlib_plot(ax)
		matplotlib_common.add_east_to_matplotlib_plot(ax)
		matplotlib_common.add_west_to_matplotlib_plot(ax)

		base_people_points = (
			configuration_active._populate_base_groups_to_show(
				base_groups_to_show
			)
		)
		matplotlib_plotter._fill_base_regions_in_matplotlib_plot(
			ax, base_people_points
		)

		director.set_focus_on_tab("Plot")

		return fig

	# ------------------------------------------------------------------------

	def _fill_base_regions_in_matplotlib_plot(
		self, ax: plt.Axes, base_people_points: PeoplePoints
	) -> None:
		director = self._director
		common = director.common
		rivalry = director.rivalry
		scores_active = director.scores_active
		base_right = rivalry.base_right
		base_left = rivalry.base_left
		point_size = common.point_size
		score_color = scores_active.score_color

		ax.fill(base_right._x, base_right._y, base_right._fill)
		ax.fill(base_left._x, base_left._y, base_left._fill)

		ax.scatter(
			base_people_points.x,
			base_people_points.y,
			color=score_color,
			s=point_size,
		)

		return

	# ------------------------------------------------------------------------

	def request_battleground_plot_for_tabs_using_matplotlib(self) -> None:
		director = self._director
		matplotlib_common = director.matplotlib_common
		configuration_active = director.configuration_active
		point_coords = configuration_active.point_coords
		current_command = cast(
			"BattlegroundCommand", director.current_command
		)

		battleground_groups_to_show = (
			current_command._battleground_groups_to_show
		)

		director.common.set_axis_extremes_based_on_coordinates(point_coords)
		fig = self._plot_battleground_using_matplotlib(
			battleground_groups_to_show
		)

		if fig is not None:
			matplotlib_common.plot_to_gui_using_matplotlib(fig)

		return

	# ------------------------------------------------------------------------

	def _plot_battleground_using_matplotlib(
		self, battleground_groups_to_show: str
	) -> plt.Figure | None:
		"""show battleground function - creates a plot showing the reference
		points and an area where battleground supporters are most likely
		found.
		"""
		director = self._director
		common = director.common
		matplotlib_common = director.matplotlib_common
		matplotlib_plotter = director.matplotlib_plotter
		rivalry = director.rivalry
		configuration_active = director.configuration_active
		ndim = configuration_active.ndim

		if not common.have_reference_points():
			director.set_focus_on_tab("Output")
			return None

		bisector = cast("Bisector", rivalry.bisector)
		west = cast("West", rivalry.west)
		east = cast("East", rivalry.east)

		bisector_cross_x = bisector._cross_x
		bisector_cross_y = bisector._cross_y
		west_cross_x = west._cross_x
		west_cross_y = west._cross_y
		east_cross_x = east._cross_x
		east_cross_y = east._cross_y

		if ndim > MAXIMUM_NUMBER_OF_DIMENSIONS_FOR_PLOTTING:
			director.set_focus_on_tab("Output")
			return None

		fig, ax = matplotlib_common.begin_matplotlib_plot_with_title(
			"Battleground"
		)
		ax = matplotlib_common.set_aspect_and_grid_in_matplotlib_plot(ax)

		matplotlib_common.add_axes_labels_to_matplotlib_plot(ax)
		matplotlib_common.set_ranges_for_matplotlib_plot(ax)
		matplotlib_common.add_reference_points_to_matplotlib_plot(ax)
		matplotlib_common.add_connector_to_matplotlib_plot(ax)
		matplotlib_common.add_bisector_to_matplotlib_plot(ax)
		matplotlib_common.add_east_to_matplotlib_plot(ax)
		matplotlib_common.add_west_to_matplotlib_plot(ax)

		battleground_people_points = (
			configuration_active._populate_battleground_groups_to_show(
				battleground_groups_to_show
			)
		)
		matplotlib_plotter._fill_battleground_regions_in_matplotlib_plot(
			ax, battleground_people_points
		)

		ax.text(bisector_cross_x, bisector_cross_y, "M")  # type: ignore[arg-type]
		ax.text(west_cross_x, west_cross_y, "W")  # type: ignore[arg-type]
		ax.text(east_cross_x, east_cross_y, "E")  # type: ignore[arg-type]

		director.set_focus_on_tab("Plot")

		return fig

	# ------------------------------------------------------------------------

	def _fill_battleground_regions_in_matplotlib_plot(
		self, ax: plt.Axes, battleground_people_points: PeoplePoints
	) -> None:
		director = self._director
		rivalry = director.rivalry

		battleground_segment = rivalry.battleground_segment
		scores_active = director.scores_active
		score_color = scores_active.score_color
		point_size = director.common.point_size

		ax.fill(
			battleground_segment._x,
			battleground_segment._y,
			battleground_segment._fill,
		)
		if director.common.have_segments():
			ax.scatter(
				battleground_people_points.x,
				battleground_people_points.y,
				color=score_color,
				s=point_size,
			)

		return

	# --------------------------------------------------------------**--------

	def request_compare_plot_for_tabs_using_matplotlib(self) -> None:
		director = self._director
		common = director.common
		matplotlib_common = director.matplotlib_common
		target_active = director.target_active
		point_coords = target_active.point_coords

		common.set_axis_extremes_based_on_coordinates(point_coords)
		fig = self.plot_compare_using_matplotlib(point_coords)

		if fig is not None:
			matplotlib_common.plot_to_gui_using_matplotlib(fig)

		return

	# ----------------------------------------------------------------**------

	def plot_compare_using_matplotlib(
		self, target: pd.DataFrame
	) -> plt.Figure | None:
		director = self._director
		common = director.common
		matplotlib_common = director.matplotlib_common
		configuration_active = director.configuration_active
		point_coords = configuration_active.point_coords
		point_labels = configuration_active.point_labels
		offset = common.plot_ranges.offset
		range_points = configuration_active.range_points

		ndim = configuration_active.ndim

		if ndim > MAXIMUM_NUMBER_OF_DIMENSIONS_FOR_PLOTTING:
			director.set_focus_on_tab("Output")
			return None

		fig, ax = matplotlib_common.begin_matplotlib_plot_with_title(None)
		ax = matplotlib_common.set_aspect_and_grid_in_matplotlib_plot(ax)

		matplotlib_common.add_axes_labels_to_matplotlib_plot(ax)
		matplotlib_common.set_ranges_for_matplotlib_plot(ax)
		for each_point in range_points:
			mid_x = (
				point_coords.iloc[each_point, 0] + target.iloc[each_point, 0]
			) / 2
			mid_y = (
				point_coords.iloc[each_point, 1] + target.iloc[each_point, 1]
			) / 2
			ax.text((mid_x + offset), mid_y, point_labels[each_point])
			ax.text(
				point_coords.iloc[each_point, 0],
				point_coords.iloc[each_point, 1],
				"A",
			)
			ax.text(
				target.iloc[each_point, 0], target.iloc[each_point, 1], "T"
			)
			ax.plot(
				[point_coords.iloc[each_point, 0], target.iloc[each_point, 0]],
				[point_coords.iloc[each_point, 1], target.iloc[each_point, 1]],
				color="black",
			)

		director.set_focus_on_tab("Plot")

		return fig

	# ------------------------------------------------------------------------

	def request_configuration_plot_for_tabs_using_matplotlib(self) -> None:
		director = self._director
		matplotlib_common = director.matplotlib_common
		common = director.common
		configuration_active = director.configuration_active
		point_coords = configuration_active.point_coords

		common.set_axis_extremes_based_on_coordinates(point_coords)
		fig = self.plot_a_configuration_using_matplotlib()

		if fig is not None:
			matplotlib_common.plot_to_gui_using_matplotlib(fig)

		return

	# ------------------------------------------------------------------------

	def plot_a_configuration_using_matplotlib(self) -> plt.Figure | None:
		director = self._director
		matplotlib_common = director.matplotlib_common
		configuration_active = director.configuration_active
		ndim = configuration_active.ndim

		if ndim > MAXIMUM_NUMBER_OF_DIMENSIONS_FOR_PLOTTING:
			director.set_focus_on_tab("Output")
			return None

		fig, ax = matplotlib_common.begin_matplotlib_plot_with_title(None)
		ax = matplotlib_common.set_aspect_and_grid_in_matplotlib_plot(ax)

		matplotlib_common.add_axes_labels_to_matplotlib_plot(ax)
		matplotlib_common.set_ranges_for_matplotlib_plot(ax)
		matplotlib_common.add_connector_to_matplotlib_plot(ax)
		matplotlib_common.add_bisector_to_matplotlib_plot(ax)
		matplotlib_common.add_configuration_to_matplotlib_plot(ax)

		director.set_focus_on_tab("Plot")

		return fig

	# ------------------------------------------------------------------------

	def request_contest_plot_for_tabs_using_matplotlib(self) -> None:
		director = self._director
		common = director.common
		matplotlib_common = director.matplotlib_common
		configuration_active = director.configuration_active
		point_coords = configuration_active.point_coords

		matplotlib_common = director.matplotlib_common

		common.set_axis_extremes_based_on_coordinates(point_coords)
		fig = self._plot_contest_using_matplotlib()

		if fig is not None:
			matplotlib_common.plot_to_gui_using_matplotlib(fig)

		return

	# ------------------------------------------------------------------------

	def _plot_contest_using_matplotlib(self) -> plt.Figure | None:
		director = self._director
		common = director.common
		matplotlib_common = director.matplotlib_common
		configuration_active = director.configuration_active
		rivalry = director.rivalry
		hor_dim = common.hor_dim
		vert_dim = common.vert_dim
		point_coords = configuration_active.point_coords
		rival_a = rivalry.rival_a
		rival_b = rivalry.rival_b
		ndim = configuration_active.ndim

		if ndim > MAXIMUM_NUMBER_OF_DIMENSIONS_FOR_PLOTTING:
			director.set_focus_on_tab("Output")
			return None

		fig, ax = matplotlib_common.begin_matplotlib_plot_with_title("Contest")
		ax = matplotlib_common.set_aspect_and_grid_in_matplotlib_plot(ax)

		matplotlib_common.add_axes_labels_to_matplotlib_plot(ax)
		matplotlib_common.set_ranges_for_matplotlib_plot(ax)
		matplotlib_common.add_connector_to_matplotlib_plot(ax)
		matplotlib_common.add_reference_points_to_matplotlib_plot(ax)
		matplotlib_common.add_bisector_to_matplotlib_plot(ax)
		matplotlib_common.add_east_to_matplotlib_plot(ax)
		matplotlib_common.add_west_to_matplotlib_plot(ax)
		matplotlib_common.add_first_dim_divider_to_matplotlib_plot(ax)
		matplotlib_common.add_second_dim_divider_to_matplotlib_plot(ax)

		core_a = plt.Circle(
			(
				point_coords.iloc[rival_a.index, hor_dim],
				point_coords.iloc[rival_a.index, vert_dim],
			),
			radius=rivalry.core_radius,
			fill=False,
			hatch="X",
		)
		core_b = plt.Circle(
			(
				point_coords.iloc[rival_b.index, hor_dim],
				point_coords.iloc[rival_b.index, vert_dim],
			),
			radius=rivalry.core_radius,
			fill=False,
			hatch="O",
		)
		plt.gca().add_artist(core_a)
		plt.gca().add_artist(core_b)

		director.set_focus_on_tab("Plot")

		return fig

	# ------------------------------------------------------------------------

	def request_convertible_plot_for_tabs_using_matplotlib(self) -> None:
		director = self._director
		common = director.common
		matplotlib_common = director.matplotlib_common
		configuration_active = director.configuration_active
		point_coords = configuration_active.point_coords
		current_command = cast(
			"ConvertibleCommand", director.current_command
		)

		convertible_groups_to_show = (
			current_command._convertible_groups_to_show
		)

		common.set_axis_extremes_based_on_coordinates(point_coords)
		fig = self._plot_convertible_using_matplotlib(
			convertible_groups_to_show
		)

		if fig is not None:
			matplotlib_common.plot_to_gui_using_matplotlib(fig)

		return

	# ------------------------------------------------------------------------

	def _plot_convertible_using_matplotlib(
		self, convertible_groups_to_show: str
	) -> plt.Figure | None:
		director = self._director
		matplotlib_common = director.matplotlib_common
		matplotlib_plotter = director.matplotlib_plotter
		configuration_active = director.configuration_active
		ndim = configuration_active.ndim

		if ndim > MAXIMUM_NUMBER_OF_DIMENSIONS_FOR_PLOTTING:
			director.set_focus_on_tab("Output")
			return None

		fig, ax = matplotlib_common.begin_matplotlib_plot_with_title(
			"Convertible"
		)
		ax = matplotlib_common.set_aspect_and_grid_in_matplotlib_plot(ax)

		matplotlib_common.add_axes_labels_to_matplotlib_plot(ax)
		matplotlib_common.set_ranges_for_matplotlib_plot(ax)
		matplotlib_common.add_reference_points_to_matplotlib_plot(ax)
		matplotlib_common.add_connector_to_matplotlib_plot(ax)
		matplotlib_common.add_west_to_matplotlib_plot(ax)
		matplotlib_common.add_east_to_matplotlib_plot(ax)

		convertible_people_points = (
			configuration_active._populate_convertible_groups_to_show(
				convertible_groups_to_show
			)
		)
		matplotlib_plotter._fill_convertible_regions_in_matplotlib_plot(
			ax, convertible_people_points
		)

		director.set_focus_on_tab("Plot")

		return fig

	# ------------------------------------------------------------------------

	def _fill_convertible_regions_in_matplotlib_plot(
		self, ax: plt.Axes, convertible_people_points: PeoplePoints
	) -> None:
		director = self._director
		rivalry = director.rivalry
		convertible_to_left = rivalry.convertible_to_left
		convertible_to_right = rivalry.convertible_to_right
		convertible_settled = rivalry.convertible_settled
		scores_active = director.scores_active
		score_color = scores_active.score_color

		ax.fill(
			convertible_to_right.vertices.x,
			convertible_to_right.vertices.y,
			convertible_to_right._fill,
		)
		ax.fill(
			convertible_to_left.vertices.x,
			convertible_to_left.vertices.y,
			convertible_to_left._fill,
		)
		ax.fill(
			convertible_settled._x,
			convertible_settled._y,
			convertible_settled._fill,
		)

		ax.scatter(
			convertible_people_points.x,
			convertible_people_points.y,
			color=score_color,
			s=self._director.common.point_size,
		)

		return

	# ------------------------------------------------------------------------

	def request_core_plot_for_tabs_using_matplotlib(self) -> None:
		director = self._director
		common = director.common
		matplotlib_common = director.matplotlib_common
		configuration_active = director.configuration_active
		point_coords = configuration_active.point_coords
		current_command = cast(
			"CoreSupportersCommand", director.current_command
		)

		core_groups_to_show = current_command.core_groups_to_show

		common.set_axis_extremes_based_on_coordinates(point_coords)
		fig = self._plot_core_using_matplotlib(core_groups_to_show)

		if fig is not None:
			matplotlib_common.plot_to_gui_using_matplotlib(fig)

		return

	# ------------------------------------------------------------------------

	def _plot_core_using_matplotlib(
		self, core_groups_to_show: str
	) -> plt.Figure | None:
		director = self._director
		matplotlib_common = director.matplotlib_common
		matplotlib_plotter = director.matplotlib_plotter
		configuration_active = director.configuration_active
		ndim = configuration_active.ndim
		if ndim > MAXIMUM_NUMBER_OF_DIMENSIONS_FOR_PLOTTING:
			director.set_focus_on_tab("Output")
			return None

		fig, ax = matplotlib_common.begin_matplotlib_plot_with_title(
			"Core Supporters"
		)
		ax = matplotlib_common.set_aspect_and_grid_in_matplotlib_plot(ax)

		matplotlib_common.add_axes_labels_to_matplotlib_plot(ax)
		matplotlib_common.set_ranges_for_matplotlib_plot(ax)
		matplotlib_common.add_reference_points_to_matplotlib_plot(ax)
		matplotlib_common.add_connector_to_matplotlib_plot(ax)

		matplotlib_plotter._determine_circles_defining_core_regions_using_matplotlib()

		core_people_points = (
			configuration_active._populate_core_groups_to_show(
				core_groups_to_show
			)
		)
		matplotlib_plotter._fill_core_regions_in_matplotlib_plot(
			ax, core_people_points
		)

		director.set_focus_on_tab("Plot")

		return fig

	# ------------------------------------------------------------------------

	def _determine_circles_defining_core_regions_using_matplotlib(
		self,
	) -> None:
		director = self._director
		common = director.common
		configuration_active = director.configuration_active
		rivalry = director.rivalry

		if not common.have_reference_points():
			director.set_focus_on_tab("Output")
			return

		core_left = rivalry.core_left
		core_left_center = rivalry.core_left._center
		core_right = rivalry.core_right
		core_right_center = rivalry.core_right._center
		core_radius = rivalry.core_radius

		core_a = plt.Circle(
			(core_left_center.x, core_left_center.y),  # type: ignore[arg-type]
			radius=core_radius,  # type: ignore[arg-type]
			color=core_left._fill,  # type: ignore[arg-type]
		)
		core_b = plt.Circle(
			(core_right_center.x, core_right_center.y),  # type: ignore[arg-type]
			radius=core_radius,  # type: ignore[arg-type]
			color=core_right._fill,  # type: ignore[arg-type]
		)

		configuration_active._core_a = core_a  # type: ignore[assignment]
		configuration_active._core_b = core_b  # type: ignore[assignment]
		configuration_active._core_radius = core_radius  # type: ignore[assignment]

		director.set_focus_on_tab("Plot")

		return

	# ------------------------------------------------------------------------

	def _fill_core_regions_in_matplotlib_plot(
		self, ax: plt.Axes, core_people_points: PeoplePoints
	) -> None:
		director = self._director
		common = director.common
		configuration_active = director.configuration_active
		core_a = configuration_active._core_a
		core_b = configuration_active._core_b
		scores_active = director.scores_active
		score_color = scores_active.score_color
		point_size = common.point_size

		plt.gca().add_artist(core_a)
		plt.gca().add_artist(core_b)

		ax.scatter(
			core_people_points.x,
			core_people_points.y,
			color=score_color,
			s=point_size,
		)

		return

	# ------------------------------------------------------------------------

	def request_cutoff_plot_for_tabs_using_matplotlib(self) -> None:
		director = self._director
		# Skip plot if executing from script
		if director.executing_script:
			return
		matplotlib_common = director.matplotlib_common
		similarities_active = director.similarities_active

		fig = self._plot_cutoff_using_matplotlib(
			similarities_active.value_type
		)

		matplotlib_common.plot_to_gui_using_matplotlib(fig)

		return

	# ------------------------------------------------------------------------

	def _plot_cutoff_using_matplotlib(self, value_type: str) -> plt.Figure:
		director = self._director
		matplotlib_common = director.matplotlib_common
		similarities_active = director.similarities_active

		similarities_as_list = similarities_active.similarities_as_list
		range_similarities = similarities_active.range_similarities

		x_coords: list[float] = []
		y_coords: list[float] = []

		fig, ax = matplotlib_common.begin_matplotlib_plot_with_title(None)

		list_size = len(similarities_as_list)
		sorted_list = sorted(similarities_as_list)
		for each_pair in range_similarities:
			x_coords.append(sorted_list[each_pair])
			y_coords.append(each_pair * 100.0 / list_size)
		ax.plot(
			x_coords,
			y_coords,
			color="black",
			linewidth=2,
			linestyle="-",
			marker="o",
		)
		ax.set_xlabel("Cutoff")
		if value_type == "similarities":
			ax.set_ylabel("Percentage of Pairs Above Similarity")
		else:
			ax.set_ylabel("Percentage of Pairs Below Dissimilarity")

		director.set_focus_on_tab("Plot")

		return fig

	# ------------------------------------------------------------------------

	def request_directions_plot_for_tabs_using_matplotlib(self) -> None:
		director = self._director
		common = director.common
		matplotlib_common = director.matplotlib_common
		point_coords = director.configuration_active.point_coords

		common.set_axis_extremes_based_on_coordinates(point_coords)
		fig = self._plot_directions_using_matplotlib()

		if fig is not None:
			matplotlib_common.plot_to_gui_using_matplotlib(fig)

		return

	# ------------------------------------------------------------------------

	def _plot_directions_using_matplotlib(self) -> plt.Figure | None:
		director = self._director
		common = director.common
		matplotlib_common = director.matplotlib_common
		configuration_active = director.configuration_active

		hor_dim = common.hor_dim
		vert_dim = common.vert_dim
		vector_head_width = common.vector_head_width
		vector_width = common.vector_width
		offset = configuration_active.offset
		point_coords = configuration_active.point_coords
		point_labels = configuration_active.point_labels
		range_points = configuration_active.range_points

		ndim = configuration_active.ndim

		if ndim > MAXIMUM_NUMBER_OF_DIMENSIONS_FOR_PLOTTING:
			self._director.set_focus_on_tab("Output")
			return None

		fig, ax = matplotlib_common.begin_matplotlib_plot_with_title(None)
		ax = matplotlib_common.set_aspect_and_grid_in_matplotlib_plot(ax)

		matplotlib_common.add_axes_labels_to_matplotlib_plot(ax)
		matplotlib_common.set_ranges_for_matplotlib_plot(ax)

		for each_point in range_points:
			length = np.sqrt(
				point_coords.iloc[each_point, hor_dim] ** 2
				+ point_coords.iloc[each_point, vert_dim] ** 2
			)
			if length > 0.0:
				x_dir = point_coords.iloc[each_point, hor_dim] / length
				y_dir = point_coords.iloc[each_point, vert_dim] / length
			else:
				x_dir = point_coords.iloc[each_point, hor_dim]
				y_dir = point_coords.iloc[each_point, vert_dim]

			ax.arrow(
				0.0,
				0.0,
				x_dir,
				y_dir,
				color="black",
				head_width=vector_head_width,
				width=vector_width,
			)
			if x_dir >= 0.0:
				ax.text(x_dir + offset, y_dir, point_labels[each_point])
			else:
				ax.text(
					x_dir - (2 * (len(point_labels[each_point]) - 1) * offset),
					y_dir,
					point_labels[each_point],
				)
		#
		unit_circle = plt.Circle((0.0, 0.0), 1.0, fill=False)
		ax.add_artist(unit_circle)
		#
		ax.axis((-1.5, 1.5, -1.5, 1.5))

		director.set_focus_on_tab("Plot")

		return fig

	# --------------------------------------------------------------**--------

	def request_evaluations_plot_for_tabs_using_matplotlib(self) -> None:
		director = self._director
		matplotlib_common = director.matplotlib_common

		fig = self.plot_evaluation_means_using_matplotlib()

		matplotlib_common.plot_to_gui_using_matplotlib(fig)

		return

	# --------------------------------------------------------------**--------

	def plot_evaluation_means_using_matplotlib(self) -> plt.Figure:
		director = self._director
		matplotlib_common = director.matplotlib_common
		evaluations_active = director.evaluations_active
		avg_eval = evaluations_active.avg_eval

		fig, ax = matplotlib_common.\
			begin_matplotlib_plot_with_title( # noqa: RUF059
				"Average Evaluations"
			)
		x = avg_eval.index
		y = avg_eval
		plt.barh(x, y)

		director.set_focus_on_tab("Plot")

		return fig

	# ------------------------------------------------------------------------

	def request_first_plot_for_tabs_using_matplotlib(self) -> None:
		director = self._director
		common = director.common
		matplotlib_common = director.matplotlib_common
		configuration_active = director.configuration_active
		point_coords = configuration_active.point_coords
		current_command = cast(
			"FirstDimensionCommand", director.current_command
		)

		first_dim_groups_to_show = (
			current_command._first_dim_groups_to_show
		)

		common.set_axis_extremes_based_on_coordinates(point_coords)
		fig = self._plot_first_using_matplotlib(first_dim_groups_to_show)

		if fig is not None:
			matplotlib_common.plot_to_gui_using_matplotlib(fig)

		return

	# --------------------------------------------------------------------

	def _plot_first_using_matplotlib(
		self, first_dim_groups_to_show: str
	) -> plt.Figure | None:
		director = self._director
		matplotlib_common = director.matplotlib_common
		matplotlib_plotter = director.matplotlib_plotter
		configuration_active = director.configuration_active
		ndim = configuration_active.ndim

		if ndim > MAXIMUM_NUMBER_OF_DIMENSIONS_FOR_PLOTTING:
			director.set_focus_on_tab("Output")
			return None

		fig, ax = matplotlib_common.begin_matplotlib_plot_with_title(
			"First Dimension Supporters"
		)
		ax = matplotlib_common.set_aspect_and_grid_in_matplotlib_plot(ax)

		matplotlib_common.add_axes_labels_to_matplotlib_plot(ax)
		matplotlib_common.set_ranges_for_matplotlib_plot(ax)
		matplotlib_common.add_reference_points_to_matplotlib_plot(ax)
		matplotlib_common.add_connector_to_matplotlib_plot(ax)

		first_dim_people_points = (
			configuration_active._populate_first_dim_groups_to_show(
				first_dim_groups_to_show
			)
		)
		matplotlib_plotter._fill_first_dim_regions_in_matplotlib_plot(
			ax, first_dim_people_points
		)

		director.set_focus_on_tab("Plot")

		return fig

	# ---------------------------------------------------------------------

	def _fill_first_dim_regions_in_matplotlib_plot(
		self, ax: plt.Axes, first_dim_people_points: PeoplePoints
	) -> None:
		director = self._director
		common = director.common
		rivalry = director.rivalry
		first_left = rivalry.first_left
		first_right = rivalry.first_right
		scores_active = director.scores_active
		score_color = scores_active.score_color
		point_size = common.point_size

		ax.fill(first_left._x, first_left._y, first_left._fill)
		ax.fill(first_right._x, first_right._y, first_right._fill)

		ax.scatter(
			first_dim_people_points.x,
			first_dim_people_points.y,
			color=score_color,
			s=point_size,
		)

		return

	# ----------------------------------------------------------------**------

	def request_grouped_data_plot_for_tabs_using_matplotlib(self) -> None:
		director = self._director
		common = director.common
		matplotlib_common = director.matplotlib_common
		grouped_data_active = director.grouped_data_active
		group_coords = grouped_data_active.group_coords

		common.set_axis_extremes_based_on_coordinates(group_coords)
		fig = self.plot_grouped_using_matplotlib()

		if fig is not None:
			matplotlib_common.plot_to_gui_using_matplotlib(fig)

		return

	# ----------------------------------------------------------------**------

	def plot_grouped_using_matplotlib(self) -> plt.Figure | None:
		(hor_max, hor_min, vert_max, vert_min) = (
			self._director.common.use_plot_ranges()
		)

		director = self._director
		common = director.common
		matplotlib_common = director.matplotlib_common
		grouped_data_active = director.grouped_data_active

		hor_dim = grouped_data_active._hor_dim
		vert_dim = grouped_data_active._vert_dim
		group_coords = grouped_data_active.group_coords
		group_labels = grouped_data_active.group_labels
		range_groups = grouped_data_active.range_groups
		offset = common.plot_ranges.offset
		dim_names = grouped_data_active.dim_names
		x_coords = []
		y_coords = []
		ndim = grouped_data_active.ndim

		if ndim > MAXIMUM_NUMBER_OF_DIMENSIONS_FOR_PLOTTING:
			director.set_focus_on_tab("Output")
			return None

		fig, ax = matplotlib_common.begin_matplotlib_plot_with_title("Groups")
		ax = matplotlib_common.set_aspect_and_grid_in_matplotlib_plot(ax)

		ax.set_xlabel(dim_names[hor_dim])
		ax.set_ylabel(dim_names[vert_dim])
		x_coords.append(group_coords.iloc[:, hor_dim])
		y_coords.append(group_coords.iloc[:, vert_dim])
		for each_point in range_groups:
			ax.text(
				group_coords.iloc[each_point, hor_dim] + offset,
				group_coords.iloc[each_point, vert_dim],
				group_labels[each_point],
			)
		ax.scatter(x_coords, y_coords, color="black", marker="o")

		ax.axis((hor_min, hor_max, vert_min, vert_max))

		director.set_focus_on_tab("Plot")

		return fig

	# ------------------------------------------------------------------------

	def request_heatmap_corr_plot_for_tabs_using_matplotlib(self) -> None:
		director = self._director
		matplotlib_common = director.matplotlib_common

		fig = self.plot_a_heatmap_corr_using_matplotlib()

		matplotlib_common.plot_to_gui_using_matplotlib(fig)

		return

	# -----------------------------------------------------------------------

	def plot_a_heatmap_corr_using_matplotlib(self) -> plt.Figure:
		director = self._director
		matplotlib_common = director.matplotlib_common
		correlations_active = director.correlations_active
		item_labels = correlations_active.item_labels
		item_names = correlations_active.item_names

		correlations_as_square = correlations_active.correlations_as_square

		correlations_as_lower_triangle = np.tril(correlations_as_square, k=0)

		fig = matplotlib_common.create_heatmap_using_matplotlib(
			"Correlations",
			correlations_as_lower_triangle,
			"PiYG",
			item_names,
			item_labels,
			"Items",
		)

		director.set_focus_on_tab("Plot")

		return fig

	# ------------------------------------------------------------------------

	def request_heatmap_dist_plot_for_tabs_using_matplotlib(self) -> None:
		director = self._director
		matplotlib_common = director.matplotlib_common

		fig = self.plot_a_heatmap_dist_using_matplotlib()

		matplotlib_common.plot_to_gui_using_matplotlib(fig)

		return

	# -----------------------------------------------------------------------

	def plot_a_heatmap_dist_using_matplotlib(self) -> plt.Figure:
		director = self._director
		matplotlib_common = director.matplotlib_common
		configuration_active = director.configuration_active
		point_names = configuration_active.point_names
		point_labels = configuration_active.point_labels
		distances_as_square = configuration_active.distances_as_square

		title = "Inter-point Distances"
		distances_as_lower_triangle = np.tril(distances_as_square, k=0)

		fig = matplotlib_common.create_heatmap_using_matplotlib(
			title,
			distances_as_lower_triangle,
			"binary",
			point_names,
			point_labels,
			"Items",
		)

		director.set_focus_on_tab("Plot")

		return fig

	# ----------------------------------------------------------------------

	def request_heatmap_rank_diff_plot_for_tabs_using_matplotlib(self) -> None:
		director = self._director
		matplotlib_common = director.matplotlib_common

		fig = self.plot_a_heatmap_rank_diff_using_matplotlib()

		matplotlib_common.plot_to_gui_using_matplotlib(fig)

		return

	# ------------------------------------------------------------------------

	def plot_a_heatmap_rank_diff_using_matplotlib(self) -> plt.Figure:

		director = self._director
		matplotlib_common = director.matplotlib_common
		similarities_active = director.similarities_active
		item_labels = similarities_active.item_labels
		item_names = similarities_active.item_names
		differences_of_ranks_as_square = (
			similarities_active.differences_of_ranks_as_square
		)

		title = "Differences of Ranks"

		differences_as_lower_triangle = np.tril(
			differences_of_ranks_as_square, k=0
		)

		fig = matplotlib_common.create_heatmap_using_matplotlib(
			title,
			differences_as_lower_triangle,
			"PiYG",
			item_names,
			item_labels,
			"Items",
		)

		self._director.set_focus_on_tab("Plot")

		return fig

	# ------------------------------------------------------------------------

	def request_heatmap_ranked_dist_plot_for_tabs_using_matplotlib(self) \
		-> None:
		director = self._director
		matplotlib_common = director.matplotlib_common

		fig = self.plot_a_heatmap_ranked_dist_using_matplotlib()

		matplotlib_common.plot_to_gui_using_matplotlib(fig)

		return

	# ------------------------------------------------------------------------

	def plot_a_heatmap_ranked_dist_using_matplotlib(self) -> plt.Figure:
		director = self._director
		matplotlib_common = director.matplotlib_common
		configuration_active = director.configuration_active
		item_labels = configuration_active.item_labels
		item_names = configuration_active.item_names
		ranked_distances_as_square = (
			configuration_active.ranked_distances_as_square
		)

		title = "Ranked Distances"

		ranked_distances_as_lower_triangle = np.tril(
			ranked_distances_as_square, k=0
		)

		fig = matplotlib_common.create_heatmap_using_matplotlib(
			title,
			ranked_distances_as_lower_triangle,
			"binary",
			item_names,
			item_labels,
			"Items",
		)

		director.set_focus_on_tab("Plot")

		return fig

	# ------------------------------------------------------------------------

	def request_heatmap_ranked_simi_plot_for_tabs_using_matplotlib(self) \
		-> None:
		director = self._director
		matplotlib_common = director.matplotlib_common

		fig = self.plot_a_heatmap_ranked_simi_using_matplotlib()

		matplotlib_common.plot_to_gui_using_matplotlib(fig)

		return

	# ------------------------------------------------------------------------

	def plot_a_heatmap_ranked_simi_using_matplotlib(self) -> plt.Figure:
		director = self._director
		matplotlib_common = director.matplotlib_common
		similarities_active = director.similarities_active
		item_labels = similarities_active.item_labels
		item_names = similarities_active.item_names
		ranked_similarities_as_square = (
			similarities_active.ranked_similarities_as_square
		)

		ranked_similarities_as_lower_triangle = np.tril(
			ranked_similarities_as_square, k=0
		)

		fig = matplotlib_common.create_heatmap_using_matplotlib(
			"Ranked Similarities",
			ranked_similarities_as_lower_triangle,
			"binary",
			item_names,
			item_labels,
			"Items",
		)

		director.set_focus_on_tab("Plot")

		return fig

	# ------------------------------------------------------------------------

	def request_heatmap_simi_plot_for_tabs_using_matplotlib(self) -> None:
		director = self._director
		matplotlib_common = director.matplotlib_common

		fig = self.plot_a_heatmap_simi_using_matplotlib()

		matplotlib_common.plot_to_gui_using_matplotlib(fig)

		return

	# ---------------------------------------------------------------**-------

	def plot_a_heatmap_simi_using_matplotlib(self) -> plt.Figure:
		director = self._director
		matplotlib_common = director.matplotlib_common
		similarities_active = director.similarities_active
		item_names = similarities_active.item_names
		item_labels = similarities_active.item_labels
		value_type = similarities_active.value_type
		similarities_as_square = similarities_active.similarities_as_square

		similarities_as_lower_triangle = np.tril(similarities_as_square, k=0)

		if value_type == "similarities":
			title = "Similarities"
			shading = "gist_gray"
		else:
			title = "Dissimilarities"
			shading = "gist_yarg"

		fig = matplotlib_common.create_heatmap_using_matplotlib(
			title,
			similarities_as_lower_triangle,
			shading,
			item_names,
			item_labels,
			"Items",
		)

		director.set_focus_on_tab("Plot")

		return fig

	# ------------------------------------------------------------------------

	def request_individuals_plot_for_tabs_using_matplotlib(self) -> None:
		"""Create an individuals plot - plot and gallery tabs using matplotlib.

		This method generates a scatter plot of individual scores, displays it
		in the GUI, and sets the focus to the 'Plot' tab.
		"""
		director = self._director
		common = director.common
		matplotlib_common = director.matplotlib_common
		scores_active = director.scores_active
		hor_axis_name = scores_active.hor_axis_name
		vert_axis_name = scores_active.vert_axis_name
		scores = scores_active.scores
		dim_names = scores_active.dim_names

		score_1 = scores[hor_axis_name]
		score_2 = scores[vert_axis_name]
		score_1_name = dim_names[0]
		score_2_name = dim_names[1]

		common.set_axis_extremes_based_on_coordinates(scores.iloc[:, 1:3])

		fig = self.plot_individuals_using_matplotlib()
		if fig is not None:
			matplotlib_common.plot_to_gui_using_matplotlib(fig)

		self.score_1 = score_1
		self.score_1_name = score_1_name
		self.score_2 = score_2
		self.score_2_name = score_2_name

		return

	# ------------------------------------------------------------------------

	def plot_individuals_using_matplotlib(self) -> plt.Figure | None:
		"""Plot individual scores using matplotlib.

		Creates a scatter plot of individual score data with appropriate
		axis labels and ranges.
		"""
		director = self._director
		common = director.common
		matplotlib_common = director.matplotlib_common
		scores_active = director.scores_active
		score_1 = scores_active.score_1
		score_2 = scores_active.score_2
		ndim = scores_active.ndim
		score_color = scores_active.score_color
		point_size = common.point_size

		if ndim > MAXIMUM_NUMBER_OF_DIMENSIONS_FOR_PLOTTING:
			director.set_focus_on_tab("Output")
			return None

		fig, ax = matplotlib_common.begin_matplotlib_plot_with_title(
			"Individuals"
		)
		ax = matplotlib_common.set_aspect_and_grid_in_matplotlib_plot(ax)
		matplotlib_common.add_axes_labels_to_matplotlib_plot(ax)
		matplotlib_common.set_ranges_for_matplotlib_plot(ax)

		ax.scatter(score_1, score_2, color=score_color, s=point_size)

		self.score_1 = score_1
		self.score_2 = score_2

		director.set_focus_on_tab("Plot")

		return fig

	# ------------------------------------------------------------------------

	def request_joint_plot_for_tabs_using_matplotlib(self) -> None:
		director = self._director
		common = director.common
		matplotlib_common = director.matplotlib_common
		configuration_active = director.configuration_active
		point_coords = configuration_active.point_coords

		common.set_axis_extremes_based_on_coordinates(point_coords)
		fig = self._plot_joint_using_matplotlib()

		if fig is not None:
			matplotlib_common.plot_to_gui_using_matplotlib(fig)

		return

	# ------------------------------------------------------------------------

	def _plot_joint_using_matplotlib(self) -> plt.Figure | None:
		director = self._director
		matplotlib_common = director.matplotlib_common
		configuration_active = director.configuration_active
		scores_active = director.scores_active
		score_1 = scores_active.score_1
		score_2 = scores_active.score_2
		score_color = scores_active.score_color
		point_size = director.common.point_size
		ndim = configuration_active.ndim

		if ndim > MAXIMUM_NUMBER_OF_DIMENSIONS_FOR_PLOTTING:
			director.set_focus_on_tab("Output")
			return None

		fig, ax = matplotlib_common.begin_matplotlib_plot_with_title(
			"Candidates and Voters"
		)
		ax = matplotlib_common.set_aspect_and_grid_in_matplotlib_plot(ax)
		matplotlib_common.add_axes_labels_to_matplotlib_plot(ax)
		matplotlib_common.set_ranges_for_matplotlib_plot(ax)

		if self._director.common.have_reference_points():
			matplotlib_common.add_connector_to_matplotlib_plot(ax)
			matplotlib_common.add_bisector_to_matplotlib_plot(ax)
			if self._director.common.show_just_reference_points:
				matplotlib_common.add_reference_points_to_matplotlib_plot(ax)
			else:
				matplotlib_common.add_configuration_to_matplotlib_plot(ax)
		else:
			matplotlib_common.add_configuration_to_matplotlib_plot(ax)

		ax.scatter(score_1, score_2, c=score_color, s=point_size)

		director.set_focus_on_tab("Plot")

		return fig

	# ------------------------------------------------------------------------

	def request_likely_plot_for_tabs_using_matplotlib(self) -> None:
		director = self._director
		common = director.common
		matplotlib_common = director.matplotlib_common
		configuration_active = director.configuration_active
		point_coords = configuration_active.point_coords
		current_command = cast(
			"LikelySupportersCommand", director.current_command
		)

		common.set_axis_extremes_based_on_coordinates(point_coords)

		likely_groups_to_show = current_command.likely_groups_to_show

		fig = self._plot_likely_using_matplotlib(likely_groups_to_show)

		if fig is not None:
			matplotlib_common.plot_to_gui_using_matplotlib(fig)

		return

	# ------------------------------------------------------------------------

	def _plot_likely_using_matplotlib(
		self, likely_groups_to_show: str
	) -> plt.Figure | None:
		director = self._director
		matplotlib_common = director.matplotlib_common
		matplotlib_plotter = director.matplotlib_plotter
		configuration_active = director.configuration_active
		ndim = configuration_active.ndim

		if ndim > MAXIMUM_NUMBER_OF_DIMENSIONS_FOR_PLOTTING:
			director.set_focus_on_tab("Output")
			return None

		fig, ax = matplotlib_common.begin_matplotlib_plot_with_title(
			"Likely Supporters"
		)
		ax = matplotlib_common.set_aspect_and_grid_in_matplotlib_plot(ax)

		matplotlib_common.add_axes_labels_to_matplotlib_plot(ax)
		matplotlib_common.set_ranges_for_matplotlib_plot(ax)
		matplotlib_common.add_reference_points_to_matplotlib_plot(ax)
		matplotlib_common.add_connector_to_matplotlib_plot(ax)

		likely_people_points = (
			configuration_active._populate_likely_groups_to_show(
				likely_groups_to_show
			)
		)
		matplotlib_plotter._fill_likely_regions_in_matplotlib_plot(
			ax, likely_people_points
		)

		director.set_focus_on_tab("Plot")

		return fig

		# -------------------------------------------------------------------

	def _fill_likely_regions_in_matplotlib_plot(
		self, ax: plt.Axes, likely_people_points: PeoplePoints
	) -> None:
		director = self._director
		common = director.common
		rivalry = director.rivalry
		likely_right = rivalry.likely_right
		likely_left = rivalry.likely_left
		scores_active = director.scores_active
		score_color = scores_active.score_color
		point_size = common.point_size

		ax.fill(
			likely_right.vertices.x,
			likely_right.vertices.y,
			likely_right._fill,
		)
		ax.fill(
			likely_left.vertices.x, likely_left.vertices.y, likely_left._fill
		)

		ax.scatter(
			likely_people_points.x,
			likely_people_points.y,
			color=score_color,
			s=point_size,
		)

		return

	# ---------------------------------------------------------------**-------

	def request_scores_plot_for_tabs_using_matplotlib(self) -> None:
		"""Create a scores plot for the plot and gallery tabs using matplotlib.

		This method generates a scatter plot of the scores, displays it in the
		GUI, and sets the focus to the 'Plot' tab. It also updates internal
		attributes with the plotted score data.
		"""
		director = self._director
		common = director.common
		matplotlib_common = director.matplotlib_common
		scores_active = director.scores_active
		hor_axis_name = scores_active.hor_axis_name
		vert_axis_name = scores_active.vert_axis_name
		scores = scores_active.scores
		dim_names = scores_active.dim_names

		score_1 = scores[hor_axis_name]
		score_2 = scores[vert_axis_name]
		score_1_name = dim_names[0]
		score_2_name = dim_names[1]

		common.set_axis_extremes_based_on_coordinates(scores.iloc[:, 1:3])

		fig = self.plot_scores_using_matplotlib()
		if fig is not None:
			matplotlib_common.plot_to_gui_using_matplotlib(fig)

		self.score_1 = score_1
		self.score_1_name = score_1_name
		self.score_2 = score_2
		self.score_2_name = score_2_name

		return

	# -------------------------------------------------------------**---------

	def plot_scores_using_matplotlib(self) -> plt.Figure | None:

		director = self._director
		common = director.common
		matplotlib_common = director.matplotlib_common
		scores_active = director.scores_active
		score_1 = scores_active.score_1
		score_2 = scores_active.score_2
		ndim = scores_active.ndim
		score_color = scores_active.score_color
		point_size = common.point_size

		if ndim > MAXIMUM_NUMBER_OF_DIMENSIONS_FOR_PLOTTING:
			director.set_focus_on_tab("Output")
			return None

		fig, ax = matplotlib_common.begin_matplotlib_plot_with_title("Scores")
		ax = matplotlib_common.set_aspect_and_grid_in_matplotlib_plot(ax)
		matplotlib_common.add_axes_labels_to_matplotlib_plot(ax)
		matplotlib_common.set_ranges_for_matplotlib_plot(ax)

		ax.scatter(score_1, score_2, color=score_color, s=point_size)

		self.score_1 = score_1
		self.score_2 = score_2

		director.set_focus_on_tab("Plot")

		return fig

	# ------------------------------------------------------------------------

	def request_clusters_plot_for_tabs_using_matplotlib(self) -> None:
		"""Create a clusters plot for the plot and gallery tabs using
		matplotlib.

		This method generates a scatter plot of the scores with cluster
		centroids, displays it in the GUI, and sets the focus to the
		'Plot' tab. It also updates internal attributes with the plotted
		score data.
		"""

		director = self._director
		common = director.common
		matplotlib_common = director.matplotlib_common
		scores_active = director.scores_active
		hor_axis_name = scores_active.hor_axis_name
		vert_axis_name = scores_active.vert_axis_name
		scores = scores_active.scores
		dim_names = scores_active.dim_names

		score_1 = scores[hor_axis_name]
		score_2 = scores[vert_axis_name]
		score_1_name = dim_names[0]
		score_2_name = dim_names[1]

		# Set axis ranges based on appropriate data
		if scores_active.original_clustered_data is not None:
			# Use original data for range calculation when clustering scores
			original_data = scores_active.original_clustered_data
			common.set_axis_extremes_based_on_coordinates(
				original_data.iloc[:, :2])
		else:
			# Use cluster centers for range calculation
			common.set_axis_extremes_based_on_coordinates(scores.iloc[:, 1:3])

		fig = self.plot_clusters_using_matplotlib()
		matplotlib_common.plot_to_gui_using_matplotlib(fig)

		self.score_1 = score_1
		self.score_1_name = score_1_name
		self.score_2 = score_2
		self.score_2_name = score_2_name

		return

	# -------------------------------------------------------------**---------

	def plot_clusters_using_matplotlib(self) -> plt.Figure:
		director = self._director
		common = director.common
		matplotlib_common = director.matplotlib_common
		scores_active = director.scores_active
		hor_axis_name = scores_active.hor_axis_name
		vert_axis_name = scores_active.vert_axis_name
		scores = scores_active.scores
		point_size = common.point_size

		fig, ax = matplotlib_common.begin_matplotlib_plot_with_title(
			"Clusters")
		ax = matplotlib_common.set_aspect_and_grid_in_matplotlib_plot(ax)

		ax.set_xlabel(hor_axis_name)
		ax.set_ylabel(vert_axis_name)

		matplotlib_common.set_ranges_for_matplotlib_plot(ax)

		# Get the cluster labels
		cluster_labels: np.ndarray = scores_active.cluster_labels

		# Color points by cluster assignment
		colors = [
			'red', 'blue', 'green', 'orange', 'purple',
			'brown', 'pink', 'gray', 'olive', 'cyan'
		]

		# Check if we have original clustered data (from scores clustering)
		if scores_active.original_clustered_data is not None:
			# Plot original people points with cluster colors
			original_data = scores_active.original_clustered_data
			# Use first two dimensions for plotting
			score_1 = original_data.iloc[:, 0]
			score_2 = original_data.iloc[:, 1]
			n_total_points = len(score_1)

			# Create color array for original data points
			point_colors = [
				colors[cluster_labels[i] % len(colors)]
				for i in range(n_total_points)
			]

			ax.scatter(score_1, score_2, c=point_colors, s=point_size,
					alpha=0.7, label='Data Points')
		else:
			# Original behavior for distance/similarity clustering
			# Get coordinate data for ALL points
			score_1 = scores[hor_axis_name]
			score_2 = scores[vert_axis_name]
			n_total_points = len(score_1)

			# Create color array for ALL points (all should be clustered)
			point_colors = [
				colors[cluster_labels[i] % len(colors)]
				for i in range(n_total_points)
			]

			ax.scatter(score_1, score_2, c=point_colors, s=point_size)

		# Add cluster centroids as plus signs with different colors
		if common.have_clusters():
			cluster_centers = scores_active.cluster_centers
			# Extract centroid coordinates for the current axes
			centroid_1 = cluster_centers[:, 0]  # First dimension
			centroid_2 = cluster_centers[:, 1]  # Second dimension

			# Create different colors for each centroid
			colors = [
				'red', 'blue', 'green', 'orange', 'purple',
				'brown', 'pink', 'gray', 'olive', 'cyan'
			]
			n_centroids = len(centroid_1)

			for i in range(n_centroids):
				color = colors[i % len(colors)]
				ax.plot(
					centroid_1[i], centroid_2[i], marker='+', color=color,
					markersize=12,
					linestyle='None'
				)
		# markeredgewidth=3,
		# markersize=point_size // 2
		self.score_1 = score_1
		self.score_2 = score_2

		director.set_focus_on_tab("Plot")

		return fig

	# ------------------------------------------------------------------------

	def request_sorted_stress_contributions_plot_for_tabs_using_matplotlib(
		self,
	) -> None:
		matplotlib_common = self._director.matplotlib_common
		fig = self._plot_sorted_stress_contributions_using_matplotlib()
		matplotlib_common.plot_to_gui_using_matplotlib(fig)
		self._director.set_focus_on_tab("Plot")
		return

	# ------------------------------------------------------------------------

	def _plot_sorted_stress_contributions_using_matplotlib(self) -> plt.Figure:
		matplotlib_common = self._director.matplotlib_common
		current_command = cast(
			"StressContributionCommand", self._director.current_command
		)
		sorted_stress_df = current_command.sorted_stress_df

		fig, ax = matplotlib_common.begin_matplotlib_plot_with_title(
			"Stress Contribution by Point"
		)

		point_names = sorted_stress_df["Point"].tolist()[::-1]
		stress_values = sorted_stress_df["Stress_Contribution"].tolist()[::-1]

		ax.barh(point_names, stress_values)
		ax.set_xlabel("% of Total Stress")

		self._director.set_focus_on_tab("Plot")
		return fig

	# ------------------------------------------------------------------------

	def request_stress_contribution_plot_for_tabs_using_matplotlib(self) \
		-> None:
		matplotlib_common = self._director.matplotlib_common

		fig = self._plot_stress_contribution_by_point_using_matplotlib()
		matplotlib_common.plot_to_gui_using_matplotlib(fig)
		self._director.set_focus_on_tab("Plot")
		return

	# ------------------------------------------------------------------------

	def _plot_stress_contribution_by_point_using_matplotlib(
		self,
	) -> plt.Figure:
		# point = self._point_to_plot_label
		matplotlib_common = self._director.matplotlib_common
		current_command = cast(
			"StressContributionCommand", self._director.current_command
		)
		point_label = current_command._point_to_plot_label
		point_index = current_command._point_to_plot_index
		ranks_df = self._director.similarities_active.ranks_df
		item_names = self._director.similarities_active.item_names
		range_similarities = (
			self._director.similarities_active.range_similarities
		)
		ndyad = self._director.similarities_active.ndyad
		fig, ax = matplotlib_common.begin_matplotlib_plot_with_title(
			"Stress contribution of " + item_names[point_index]
		)
		ax = matplotlib_common.set_aspect_and_grid_in_matplotlib_plot(ax)
		plt.close()
		#
		x_others = []
		y_others = []
		label_others = []
		index_others = []
		column_a_label = ranks_df.columns.get_loc("A_label")
		column_a_name = ranks_df.columns.get_loc("A_name")
		column_b_label = ranks_df.columns.get_loc("B_label")
		column_b_name = ranks_df.columns.get_loc("B_name")
		column_sim_rank = ranks_df.columns.get_loc("Similarity_Rank")
		column_dist_rank = ranks_df.columns.get_loc("Distance_Rank")
		for each_dyad in range_similarities:
			if ranks_df.iloc[each_dyad, column_a_label] == point_label:
				x_others.append(ranks_df.iloc[each_dyad, column_sim_rank])
				y_others.append(ranks_df.iloc[each_dyad, column_dist_rank])
				label_others.append(ranks_df.iloc[each_dyad, column_b_name])
				index_others.append(each_dyad)
			if ranks_df.iloc[each_dyad, column_b_label] == point_label:
				x_others.append(ranks_df.iloc[each_dyad, column_sim_rank])
				y_others.append(ranks_df.iloc[each_dyad, column_dist_rank])
				label_others.append(ranks_df.iloc[each_dyad, column_a_name])
				index_others.append(each_dyad)
		#
		# Create plot for selected item

		ax.set_xlabel("Similarity Rank")
		ax.set_ylabel("Distance Rank")
		ax.scatter(x_others, y_others)
		other_range = range(len(x_others))
		for each_item in other_range:
			ax.text(
				x_others[each_item],
				y_others[each_item],
				label_others[each_item],
			)
			if index_others[each_item] + 1 == x_others[each_item]:
				ax.plot(
					[index_others[each_item] + 1, x_others[each_item]],
					[index_others[each_item] + 1, y_others[each_item]],
					"b",
				)
			else:
				difference = index_others[each_item] + 1 - x_others[each_item]
				if difference > 0:
					ax.plot(
						[x_others[each_item], x_others[each_item]],
						[
							index_others[each_item] + difference,
							y_others[each_item],
						],
						"b",
					)
				else:
					ax.plot(
						[x_others[each_item], x_others[each_item]],
						[
							index_others[each_item] + 1 - difference,
							y_others[each_item],
						],
						"b",
					)
		#
		# Add line to indicate what a perfect relationship, no stress, would be
		#
		ax.plot((1, ndyad + 1), (1, ndyad + 1), "r")

		self._director.similarities_active.ranks_df = ranks_df

		return fig

	# ------------------------------------------------------------------------

	def request_second_plot_for_tabs_using_matplotlib(self) -> None:
		director = self._director
		common = director.common
		matplotlib_common = director.matplotlib_common
		configuration_active = director.configuration_active
		point_coords = configuration_active.point_coords
		current_command = cast(
			"SecondDimensionCommand", director.current_command
		)

		second_dim_groups_to_show = (
			current_command._second_dim_groups_to_show
		)

		common.set_axis_extremes_based_on_coordinates(point_coords)
		fig = self._plot_second_using_matplotlib(second_dim_groups_to_show)

		if fig is not None:
			matplotlib_common.plot_to_gui_using_matplotlib(fig)

		return

	# ------------------------------------------------------------------------

	def _plot_second_using_matplotlib(
		self, second_dim_groups_to_show: str
	) -> plt.Figure | None:
		director = self._director
		matplotlib_common = director.matplotlib_common
		matplotlib_plotter = director.matplotlib_plotter
		configuration_active = director.configuration_active
		ndim = configuration_active.ndim

		if ndim > MAXIMUM_NUMBER_OF_DIMENSIONS_FOR_PLOTTING:
			director.set_focus_on_tab("Output")
			return None

		fig, ax = matplotlib_common.begin_matplotlib_plot_with_title(
			"Second Dimension Supporters"
		)
		ax = matplotlib_common.set_aspect_and_grid_in_matplotlib_plot(ax)

		matplotlib_common.add_axes_labels_to_matplotlib_plot(ax)
		matplotlib_common.set_ranges_for_matplotlib_plot(ax)
		matplotlib_common.add_reference_points_to_matplotlib_plot(ax)
		matplotlib_common.add_connector_to_matplotlib_plot(ax)

		second_dim_people_points = (
			configuration_active._populate_second_dim_groups_to_show(
				second_dim_groups_to_show
			)
		)
		matplotlib_plotter._fill_second_dim_regions_in_matplotlib_plot(
			ax, second_dim_people_points
		)

		director.set_focus_on_tab("Plot")

		return fig

	# ------------------------------------------------------------------------

	def _fill_second_dim_regions_in_matplotlib_plot(
		self, ax: plt.Axes, second_dim_people_points: PeoplePoints
	) -> None:
		director = self._director
		common = director.common
		rivalry = director.rivalry
		second_up = rivalry.second_up
		second_down = rivalry.second_down
		scores_active = director.scores_active
		score_color = scores_active.score_color
		point_size = common.point_size

		ax.fill(second_up._x, second_up._y, second_up._fill)
		ax.fill(second_down._x, second_down._y, second_down._fill)

		ax.scatter(
			second_dim_people_points.x,
			second_dim_people_points.y,
			color=score_color,
			s=point_size,
		)

		return

	# ----------------------------------------------------------------------

	def request_target_plot_for_tabs_using_matplotlib(self) -> None:
		director = self._director
		common = director.common
		matplotlib_common = director.matplotlib_common
		target_active = director.target_active
		point_coords = target_active.point_coords

		common.set_axis_extremes_based_on_coordinates(point_coords)
		fig = self.plot_target_using_matplotlib()

		if fig is not None:
			matplotlib_common.plot_to_gui_using_matplotlib(fig)

		return

	# ------------------------------------------------------------------------

	def plot_target_using_matplotlib(self) -> plt.Figure | None:
		director = self._director
		common = director.common
		matplotlib_common = director.matplotlib_common
		target_active = director.target_active
		hor_dim = target_active._hor_dim
		vert_dim = target_active._vert_dim
		dim_names = target_active.dim_names
		point_labels = target_active.point_labels
		point_coords = target_active.point_coords
		range_points = target_active.range_points
		offset = common.plot_ranges.offset
		point_size = common.point_size
		ndim = target_active.ndim

		if ndim > MAXIMUM_NUMBER_OF_DIMENSIONS_FOR_PLOTTING:
			director.set_focus_on_tab("Output")
			return None

		x_coords = []
		y_coords = []

		fig, ax = matplotlib_common.begin_matplotlib_plot_with_title(None)
		ax = matplotlib_common.set_aspect_and_grid_in_matplotlib_plot(ax)

		ax.set_xlabel(dim_names[hor_dim])
		ax.set_ylabel(dim_names[vert_dim])
		matplotlib_common.set_ranges_for_matplotlib_plot(ax)

		x_coords.append(point_coords.iloc[:, hor_dim])
		y_coords.append(point_coords.iloc[:, vert_dim])
		for each_point in range_points:
			ax.text(
				point_coords.iloc[each_point, hor_dim] + offset,
				point_coords.iloc[each_point, vert_dim],
				point_labels[each_point],
			)

		ax.scatter(x_coords, y_coords, color="black", s=point_size)

		director.set_focus_on_tab("Plot")

		return fig

	# ------------------------------------------------------------------------

	def request_uncertainty_plot_for_tabs_using_matplotlib(self) -> None:
		director = self._director
		matplotlib_common = director.matplotlib_common
		common = director.common
		uncertainty_active = director.uncertainty_active

		common.set_axis_extremes_based_on_coordinates(
			uncertainty_active.solutions
		)
		fig = self.plot_uncertainty_using_matplotlib()

		if fig is not None:
			matplotlib_common.plot_to_gui_using_matplotlib(fig)

		return

	# ------------------------------------------------------------------------

	def plot_uncertainty_using_matplotlib(self) -> plt.Figure | None:
		director = self._director
		common = director.common
		matplotlib_common = director.matplotlib_common
		uncertainty_active = director.uncertainty_active
		hor_dim = common.hor_dim
		vert_dim = common.vert_dim
		dim_names = uncertainty_active.dim_names
		point_labels = uncertainty_active.point_labels
		range_points = uncertainty_active.range_points
		npoint = uncertainty_active.npoints
		ndim = uncertainty_active.ndim

		if ndim > MAXIMUM_NUMBER_OF_DIMENSIONS_FOR_PLOTTING:
			director.set_focus_on_tab("Output")
			return None

		solutions = director.uncertainty_active.solutions

		fig, ax = matplotlib_common.begin_matplotlib_plot_with_title(
			"Uncertainty"
		)
		ax = matplotlib_common.set_aspect_and_grid_in_matplotlib_plot(ax)
		ax.set_xlabel(dim_names[hor_dim])
		ax.set_ylabel(dim_names[vert_dim])
		matplotlib_common.set_ranges_for_matplotlib_plot(ax)

		for each_point in range_points:
			point_coordinates_for_repetition = solutions.iloc[
				each_point::npoint
			]
			x_coords = point_coordinates_for_repetition.iloc[:, 0].to_numpy()
			y_coords = point_coordinates_for_repetition.iloc[:, 1].to_numpy()
			x_mean, y_mean = common.solutions_means(each_point)
			ax.text(x_mean, y_mean, point_labels[each_point])
			ax.scatter(x_coords, y_coords, color="r", s=0.5)
			matplotlib_common.confidence_ellipse_using_matplotlib(
				x_coords,
				y_coords,
				ax,
				n_std=2.0,
				facecolor="none",
				edgecolor="r",
			)

		director.set_focus_on_tab("Plot")

		return fig

	# ------------------------------------------------------------------------

	def request_spatial_uncertainty_plot_for_tabs_using_matplotlib(self) \
		-> None:
		director = self._director
		matplotlib_common = director.matplotlib_common
		common = director.common
		uncertainty_active = director.uncertainty_active

		common.set_axis_extremes_based_on_coordinates(
			uncertainty_active.solutions
		)
		fig = self.plot_spatial_uncertainty_using_matplotlib()

		if fig is not None:
			matplotlib_common.plot_to_gui_using_matplotlib(fig)

		return

	# ------------------------------------------------------------------------

	def plot_spatial_uncertainty_using_matplotlib(self) -> plt.Figure | None:
		director = self._director
		common = director.common
		matplotlib_common = director.matplotlib_common
		uncertainty_active = director.uncertainty_active
		hor_dim = common.hor_dim
		vert_dim = common.vert_dim
		dim_names = uncertainty_active.dim_names
		point_labels = uncertainty_active.point_labels
		range_points = uncertainty_active.range_points
		npoint = uncertainty_active.npoints
		ndim = uncertainty_active.ndim

		if ndim > MAXIMUM_NUMBER_OF_DIMENSIONS_FOR_PLOTTING:
			director.set_focus_on_tab("Output")
			return None

		# Get the visualization mode from the ViewSpatialUncertainty command
		plot_to_show = getattr(director, "plot_to_show", "ellipses")

		solutions = uncertainty_active.solutions

		title = "Uncertainty"
		fig, ax = matplotlib_common.begin_matplotlib_plot_with_title(title)
		ax = matplotlib_common.set_aspect_and_grid_in_matplotlib_plot(ax)
		ax.set_xlabel(dim_names[hor_dim])
		ax.set_ylabel(dim_names[vert_dim])
		matplotlib_common.set_ranges_for_matplotlib_plot(ax)

		for each_point in range_points:
			point_coordinates_for_repetition = solutions.iloc[
				each_point::npoint
			]
			x_coords = point_coordinates_for_repetition.iloc[:, 0].to_numpy()
			y_coords = point_coordinates_for_repetition.iloc[:, 1].to_numpy()
			x_mean, y_mean = common.solutions_means(each_point)
			ax.text(x_mean, y_mean, point_labels[each_point])
			ax.scatter(x_coords, y_coords, color="r", s=0.5)

			match plot_to_show:
				case "ellipses":
					matplotlib_common.add_ellipse_mode_matplotlib(
						ax, x_coords, y_coords
					)
				case "boxes":
					matplotlib_common.add_box_mode_matplotlib(ax, each_point)
				case "lines":
					matplotlib_common.add_lines_mode_matplotlib(
						ax, each_point, x_mean, y_mean
					)
				case "circles":
					matplotlib_common.add_circles_mode_matplotlib(
						ax, each_point, x_mean, y_mean
					)

		director.set_focus_on_tab("Plot")

		return fig

	# ------------------------------------------------------------------------

	def request_point_uncertainty_plot_for_tabs_using_matplotlib(self) -> None:
		director = self._director
		matplotlib_common = director.matplotlib_common
		common = director.common
		uncertainty_active = director.uncertainty_active

		common.set_axis_extremes_based_on_coordinates(
			uncertainty_active.solutions
		)
		fig = self.plot_point_uncertainty_using_matplotlib()

		if fig is not None:
			matplotlib_common.plot_to_gui_using_matplotlib(fig)

		return

	# ------------------------------------------------------------------------

	def plot_point_uncertainty_using_matplotlib(self) -> plt.Figure | None:
		director = self._director
		common = director.common
		matplotlib_common = director.matplotlib_common
		uncertainty_active = director.uncertainty_active
		hor_dim = common.hor_dim
		vert_dim = common.vert_dim
		dim_names = uncertainty_active.dim_names
		point_labels = uncertainty_active.point_labels
		range_points = uncertainty_active.range_points
		npoint = uncertainty_active.npoints
		ndim = uncertainty_active.ndim

		if ndim > MAXIMUM_NUMBER_OF_DIMENSIONS_FOR_PLOTTING:
			director.set_focus_on_tab("Output")
			return None

		plot_to_show = getattr(director, "plot_to_show", "ellipses")
		selected_point_indices = getattr(
			director, "selected_point_indices", range_points
		)
		solutions = uncertainty_active.solutions

		title = "Uncertainty"
		fig, ax = matplotlib_common.begin_matplotlib_plot_with_title(title)
		ax = matplotlib_common.set_aspect_and_grid_in_matplotlib_plot(ax)
		ax.set_xlabel(dim_names[hor_dim])
		ax.set_ylabel(dim_names[vert_dim])
		matplotlib_common.set_ranges_for_matplotlib_plot(ax)

		for each_point in range_points:
			x_mean, y_mean = common.solutions_means(each_point)
			ax.text(x_mean, y_mean, point_labels[each_point])

		for each_point in selected_point_indices:
			point_coordinates_for_repetition = solutions.iloc[
				each_point::npoint
			]
			x_coords = point_coordinates_for_repetition.iloc[:, 0].to_numpy()
			y_coords = point_coordinates_for_repetition.iloc[:, 1].to_numpy()
			x_mean, y_mean = common.solutions_means(each_point)
			ax.scatter(x_coords, y_coords, color="r", s=0.5)

			match plot_to_show:
				case "ellipses":
					matplotlib_common.add_ellipse_mode_matplotlib(
						ax, x_coords, y_coords
					)
				case "boxes":
					matplotlib_common.add_box_mode_matplotlib(ax, each_point)
				case "lines":
					matplotlib_common.add_lines_mode_matplotlib(
						ax, each_point, x_mean, y_mean
					)
				case "circles":
					matplotlib_common.add_circles_mode_matplotlib(
						ax, each_point, x_mean, y_mean
					)

		director.set_focus_on_tab("Plot")
		return fig


	# ------------------------------------------------------------------------

	def request_vectors_plot_for_tabs_using_matplotlib(self) -> None:
		director = self._director
		matplotlib_common = director.matplotlib_common
		common = director.common
		point_coords = director.configuration_active.point_coords

		common.set_axis_extremes_based_on_coordinates(point_coords)
		fig = self._plot_vectors_using_matplotlib()

		if fig is not None:
			matplotlib_common.plot_to_gui_using_matplotlib(fig)

		return

	# ------------------------------------------------------------------------

	def _plot_vectors_using_matplotlib(self) -> plt.Figure | None:
		director = self._director
		common = director.common
		matplotlib_common = director.matplotlib_common
		configuration_active = director.configuration_active
		hor_dim = common.hor_dim
		vert_dim = common.vert_dim
		vector_head_width = common.vector_head_width
		vector_width = common.vector_width
		point_coords = configuration_active.point_coords
		point_labels = configuration_active.point_labels
		offset = common.plot_ranges.offset
		ndim = director.configuration_active.ndim

		if ndim > MAXIMUM_NUMBER_OF_DIMENSIONS_FOR_PLOTTING:
			director.set_focus_on_tab("Output")
			return None

		fig, ax = matplotlib_common.begin_matplotlib_plot_with_title(None)
		ax = matplotlib_common.set_aspect_and_grid_in_matplotlib_plot(ax)
		matplotlib_common.add_axes_labels_to_matplotlib_plot(ax)
		matplotlib_common.set_ranges_for_matplotlib_plot(ax)
		for each_point in configuration_active.range_points:
			if point_coords.iloc[each_point, hor_dim] >= 0.0:
				ax.text(
					point_coords.iloc[each_point, hor_dim] + (2 * offset),
					point_coords.iloc[each_point, vert_dim],
					point_labels[each_point],
				)
			else:
				ax.text(
					point_coords.iloc[each_point, hor_dim]
					- (2 * len(point_labels[each_point]) * offset),
					point_coords.iloc[each_point, vert_dim],
					point_labels[each_point],
				)
			ax.arrow(
				0,
				0,
				point_coords.iloc[each_point, hor_dim],
				point_coords.iloc[each_point, vert_dim],
				color="black",
				head_width=vector_head_width,
				width=vector_width,
			)

		director.set_focus_on_tab("Plot")

		return fig

	# ------------------------------------------------------------------------

	def request_view_custom_plot_for_tabs_using_matplotlib(self) -> None:
		director = self._director
		matplotlib_plotter = director.matplotlib_plotter
		matplotlib_common = director.matplotlib_common
		common = director.common
		point_coords = director.configuration_active.point_coords

		common.set_axis_extremes_based_on_coordinates(point_coords)
		fig = matplotlib_plotter._plot_custom_using_matplotlib()

		if fig is not None:
			matplotlib_common.plot_to_gui_using_matplotlib(fig)

		return

	# ------------------------------------------------------------------------

	def _plot_custom_using_matplotlib(self) -> plt.Figure | None:
		#
		director = self._director
		common = director.common
		matplotlib_common = director.matplotlib_common
		configuration_active = director.configuration_active
		hor_dim = common.hor_dim
		vert_dim = common.vert_dim
		dim_names = configuration_active.dim_names
		point_coords = configuration_active.point_coords
		point_labels = configuration_active.point_labels
		offset = common.plot_ranges.offset
		rivalry = director.rivalry
		rival_a = rivalry.rival_a
		rival_b = rivalry.rival_b
		bisector = rivalry.bisector

		ndim = configuration_active.ndim

		if ndim > MAXIMUM_NUMBER_OF_DIMENSIONS_FOR_PLOTTING:
			director.set_focus_on_tab("Output")
			return None

		x_coords = []
		y_coords = []

		fig, ax = matplotlib_common.begin_matplotlib_plot_with_title("Custom")

		ax.set_xlabel(dim_names[hor_dim])
		ax.set_ylabel(dim_names[vert_dim])
		#
		x_coords.append(point_coords.iloc[:, hor_dim])
		y_coords.append(point_coords.iloc[:, vert_dim])

		for each_point in self._director.configuration_active.range_points:
			ax.text(
				point_coords.iloc[each_point, hor_dim] + offset,
				point_coords.iloc[each_point, vert_dim],
				point_labels[each_point],
			)
		ax.scatter(x_coords, y_coords, color="black", s=5)
		#
		custom_hor_min = 0.1
		custom_hor_max = 0.95
		custom_vert_min = -1.0
		custom_vert_max = 1.0
		ax.axis(
			(custom_hor_min, custom_hor_max, custom_vert_min, custom_vert_max)
		)

		if common.show_connector:
			ax.plot(
				[
					point_coords.iloc[rival_a.index, hor_dim],
					point_coords.iloc[rival_b.index, hor_dim],
				],
				[
					point_coords.iloc[rival_a.index, vert_dim],
					point_coords.iloc[rival_b.index, vert_dim],
				],
			)

		if common.have_reference_points() and common.show_bisector:
			bisector_cast = cast("Bisector", bisector)
			ax.text(bisector_cast._start.x, bisector_cast._start.y, "S")
			ax.text(bisector_cast._end.x, bisector_cast._end.y, "E")
			ax.text(bisector_cast._start.x, bisector_cast._start.y, "S")
			ax.text(bisector_cast._end.x, bisector_cast._end.y, "E")
			ax.plot(
				[bisector_cast._start.x, bisector_cast._end.x],
				[bisector_cast._start.y, bisector_cast._end.y],
			)

		director.set_focus_on_tab("Plot")

		return fig
