from __future__ import annotations

import numpy as np
import pyqtgraph as pg
from pyqtgraph import BarGraphItem, PlotWidget
from PySide6 import QtGui, QtWidgets

from constants import (
	CORE_SIZE_FULL,
	CORE_SIZE_HALF,
	MAXIMUM_NUMBER_OF_DIMENSIONS_FOR_PLOTTING,
)
from typing import TYPE_CHECKING

if TYPE_CHECKING:
	import pandas as pd
	from director import Status
	from features import TargetFeature
	from geometry import PeoplePoints

from exceptions import DependencyError, UnderDevelopmentError


class PyQtGraphMethods:
	def __init__(self, director: Status) -> None:
		from director import Status  # noqa: PLC0415, F401

		self._director = director

	# ------------------------------------------------------------------------

	def request_alike_plot_for_tabs_using_pyqtgraph(self) -> None:
		director = self._director
		common = director.common
		pyqtgraph_common = director.pyqtgraph_common
		configuration_active = director.configuration_active
		point_coords = configuration_active.point_coords

		common.set_axis_extremes_based_on_coordinates(point_coords)

		tab_plot_widget = self._plot_alike_using_pyqtgraph()
		tab_gallery_widget = self._plot_alike_using_pyqtgraph()

		pyqtgraph_common.plot_to_gui_using_pyqtgraph(
			tab_plot_widget, tab_gallery_widget
		)

		return

	# ------------------------------------------------------------------------

	def _plot_alike_using_pyqtgraph(self) -> pg.GraphicsLayoutWidget:
		"""plot alike  -creates a plot with a line joining points with
		high similarity.
		A plot of the configuration will be created with a line joining pairs
		of points with
		a similarity above (or if dissimilarities, below) the cutoff.
		"""

		director = self._director
		common = director.common
		pyqtgraph_common = director.pyqtgraph_common
		configuration_active = director.configuration_active
		similarities_active = director.similarities_active

		if not common.have_alike_coords():
			title = "No alike points available for plotting"
			message = (
				"Open Similarities and establish configuration before"
				" using Alike."
			)
			raise DependencyError(title, message)

		a_x_alike = similarities_active.a_x_alike
		a_y_alike = similarities_active.a_y_alike
		b_x_alike = similarities_active.b_x_alike
		b_y_alike = similarities_active.b_y_alike

		ndim = configuration_active.ndim

		if ndim > MAXIMUM_NUMBER_OF_DIMENSIONS_FOR_PLOTTING:
			director.set_focus_on_tab("Output")
			return None

		graphics_layout_widget, plot = (
			pyqtgraph_common.begin_pyqtgraph_plot_with_title(None)
		)
		plot = pyqtgraph_common.set_aspect_and_grid_in_pyqtgraph_plot(plot)

		pyqtgraph_common.add_axes_labels_to_pyqtgraph_plot(plot)
		pyqtgraph_common.set_ranges_for_pyqtgraph_plot(plot)
		pyqtgraph_common.add_configuration_to_pyqtgraph_plot(plot)

		nalike = range(len(a_x_alike))
		for each_alike in nalike:
			plot.plot(
				(a_x_alike[each_alike], b_x_alike[each_alike]),
				(a_y_alike[each_alike], b_y_alike[each_alike]),
				color="k",
			)

		director.set_focus_on_tab("Plot")

		return graphics_layout_widget

	# ------------------------------------------------------------------------

	def request_base_plot_for_tabs_using_pyqtgraph(self) -> None:
		director = self._director
		common = director.common
		pyqtgraph_common = director.pyqtgraph_common
		configuration_active = director.configuration_active
		point_coords = configuration_active.point_coords

		base_groups_to_show = director.current_command._base_groups_to_show

		common.set_axis_extremes_based_on_coordinates(point_coords)
		tab_plot_widget = self._plot_base_using_pyqtgraph(base_groups_to_show)
		tab_gallery_widget = self._plot_base_using_pyqtgraph(
			base_groups_to_show
		)

		pyqtgraph_common.plot_to_gui_using_pyqtgraph(
			tab_plot_widget, tab_gallery_widget
		)

		return

	# ------------------------------------------------------------------------

	def _plot_base_using_pyqtgraph(
		self, base_groups_to_show: str
	) -> pg.GraphicsLayoutWidget:
		director = self._director
		pyqtgraph_common = director.pyqtgraph_common
		pyqtgraph_plotter = director.pyqtgraph_plotter
		configuration_active = director.configuration_active
		ndim = configuration_active.ndim

		if ndim > MAXIMUM_NUMBER_OF_DIMENSIONS_FOR_PLOTTING:
			director.set_focus_on_tab("Output")
			return None

		graphics_layout_widget, plot = (
			pyqtgraph_common.begin_pyqtgraph_plot_with_title("Base Supporters")
		)
		plot = pyqtgraph_common.set_aspect_and_grid_in_pyqtgraph_plot(plot)

		pyqtgraph_common.add_axes_labels_to_pyqtgraph_plot(plot)
		pyqtgraph_common.set_ranges_for_pyqtgraph_plot(plot)
		pyqtgraph_common.add_reference_points_to_pyqtgraph_plot(plot)
		pyqtgraph_common.add_connector_to_pyqtgraph_plot(plot)
		pyqtgraph_common.add_east_to_pyqtgraph_plot(plot)
		pyqtgraph_common.add_west_to_pyqtgraph_plot(plot)

		base_people_points = (
			self._director.configuration_active._populate_base_groups_to_show(
				base_groups_to_show
			)
		)
		pyqtgraph_plotter._fill_base_regions_in_pyqtgraph_plot(
			plot, base_people_points
		)

		director.set_focus_on_tab("Plot")

		return graphics_layout_widget

	# ------------------------------------------------------------------------

	def _fill_base_regions_in_pyqtgraph_plot(
		self, plot: pg.PlotItem, base_people_points: PeoplePoints
	) -> None:
		director = self._director
		common = director.common
		rivalry = director.rivalry
		base_left = rivalry.base_left
		base_right = rivalry.base_right
		scores_active = director.scores_active
		score_color = scores_active.score_color
		point_size = common.point_size

		left_region = pg.QtGui.QPainterPath()
		left_region.moveTo(base_left._x[0], base_left._y[0])
		for x_, y_ in zip(base_left._x[1:], base_left._y[1:], strict=True):
			left_region.lineTo(x_, y_)
		left_region_item = pg.QtWidgets.QGraphicsPathItem(left_region)
		left_brush = pg.QtGui.QBrush(pg.QtGui.QColor(base_left._fill))
		left_region_item.setBrush(left_brush)
		left_region_item.setPen(pg.mkPen(color=(0, 0, 0), width=2))
		plot.addItem(left_region_item)

		right_region = pg.QtGui.QPainterPath()
		right_region.moveTo(base_right._x[0], base_right._y[0])
		for x_, y_ in zip(base_right._x[1:], base_right._y[1:], strict=True):
			right_region.lineTo(x_, y_)
		right_region_item = pg.QtWidgets.QGraphicsPathItem(right_region)
		right_brush = pg.QtGui.QBrush(pg.QtGui.QColor(base_right._fill))
		right_region_item.setBrush(right_brush)
		right_region_item.setPen(pg.mkPen(color=(0, 0, 0), width=2))
		plot.addItem(right_region_item)
		plot.scatterPlot(
			x=base_people_points.x,
			y=base_people_points.y,
			pen=score_color,
			size=point_size,
		)

		return

	# ------------------------------------------------------------------------

	def request_battleground_plot_for_tabs_using_pyqtgraph(self) -> None:
		director = self._director
		common = director.common
		pyqtgraph_common = director.pyqtgraph_common
		configuration_active = director.configuration_active
		point_coords = configuration_active.point_coords

		battleground_groups_to_show = (
			director.current_command._battleground_groups_to_show
		)

		common.set_axis_extremes_based_on_coordinates(point_coords)

		tab_plot_widget = self._plot_battleground_using_pyqtgraph(
			battleground_groups_to_show
		)
		tab_gallery_widget = self._plot_battleground_using_pyqtgraph(
			battleground_groups_to_show
		)
		pyqtgraph_common.plot_to_gui_using_pyqtgraph(
			tab_plot_widget, tab_gallery_widget
		)

		return

	# ------------------------------------------------------------------------

	def _plot_battleground_using_pyqtgraph(
		self, battleground_groups_to_show: str
	) -> pg.GraphicsLayoutWidget:
		"""show battleground function - creates a plot showing the reference
		points and an area where battleground supporters are most likely
		found.
		"""

		director = self._director
		pyqtgraph_common = director.pyqtgraph_common
		pyqtgraph_plotter = director.pyqtgraph_plotter
		configuration_active = director.configuration_active
		rivalry = director.rivalry
		bisector_cross_x = rivalry.bisector._cross_x
		bisector_cross_y = rivalry.bisector._cross_y

		graphics_layout_widget, plot = (
			pyqtgraph_common.begin_pyqtgraph_plot_with_title("Battleground")
		)
		plot = pyqtgraph_common.set_aspect_and_grid_in_pyqtgraph_plot(plot)

		pyqtgraph_common.add_axes_labels_to_pyqtgraph_plot(plot)
		pyqtgraph_common.set_ranges_for_pyqtgraph_plot(plot)
		pyqtgraph_common.add_west_to_pyqtgraph_plot(plot)
		pyqtgraph_common.add_east_to_pyqtgraph_plot(plot)
		pyqtgraph_common.add_connector_to_pyqtgraph_plot(plot)
		pyqtgraph_common.add_reference_points_to_pyqtgraph_plot(plot)
		pyqtgraph_common.add_bisector_to_pyqtgraph_plot(plot)
		bisector_middle_name = pg.TextItem(
			text="M", color=(0, 0, 0), anchor=(1.0, 0.0)
		)
		bisector_middle_name.setPos(bisector_cross_x, bisector_cross_y)
		plot.addItem(bisector_middle_name)

		battleground_people_points = (
			configuration_active._populate_battleground_groups_to_show(
				battleground_groups_to_show
			)
		)
		pyqtgraph_plotter._fill_battleground_regions_in_pyqtgraph_plot(
			plot, battleground_people_points
		)

		director.set_focus_on_tab("Plot")

		return graphics_layout_widget

	# ------------------------------------------------------------------------

	def _fill_battleground_regions_in_pyqtgraph_plot(
		self, plot: pg.PlotItem, battleground_people_points: PeoplePoints
	) -> None:
		director = self._director
		common = director.common
		rivalry = director.rivalry
		scores_active = director.scores_active
		battleground_segment = rivalry.battleground_segment
		# battleground_settled = self._battleground_settled
		point_size = common.point_size
		score_color = scores_active.score_color

		battleground_region = QtGui.QPainterPath()
		battleground_region.moveTo(
			battleground_segment._x[0], battleground_segment._y[0]
		)
		for x_, y_ in zip(
			battleground_segment._x[1:],
			battleground_segment._y[1:],
			strict=True,
		):
			battleground_region.lineTo(x_, y_)
		battleground_region_item = QtWidgets.QGraphicsPathItem(
			battleground_region
		)
		battleground_region_brush = QtGui.QBrush(
			QtGui.QColor(battleground_segment._fill)
		)
		battleground_region_item.setBrush(battleground_region_brush)
		battleground_region_item.setPen(pg.mkPen(color=(0, 0, 0), width=2))
		plot.addItem(battleground_region_item)
		if common.have_segments():
			points = pg.ScatterPlotItem(
				battleground_people_points.x,
				battleground_people_points.y,
				pen=score_color,
				symbol="o",
				size=point_size,
			)
			plot.addItem(points)

		return

	# ------------------------------------------------------------------------

	def request_clusters_plot_for_tabs_using_pyqtgraph(self) -> None:
		director = self._director
		common = director.common
		pyqtgraph_common = director.pyqtgraph_common
		scores_active = director.scores_active
		hor_axis_name = scores_active.hor_axis_name
		vert_axis_name = scores_active.vert_axis_name
		scores = scores_active.scores
		dim_names = scores_active.dim_names

		score_1 = scores[hor_axis_name]
		score_2 = scores[vert_axis_name]
		score_1_name = dim_names[0]
		score_2_name = dim_names[1]

		common.set_axis_extremes_based_on_coordinates(scores.iloc[:, 1:])

		tab_plot_widget = self.plot_clusters_using_pyqtgraph()
		tab_gallery_widget = self.plot_clusters_using_pyqtgraph()
		pyqtgraph_common.plot_to_gui_using_pyqtgraph(
			tab_plot_widget, tab_gallery_widget
		)

		self.score_1 = score_1
		self.score_1_name = score_1_name
		self.score_2 = score_2
		self.score_2_name = score_2_name

		return

	# -----------------------------------------------------------------**-----

	def plot_clusters_using_pyqtgraph(self) -> pg.GraphicsLayoutWidget:
		director = self._director
		common = director.common
		pyqtgraph_common = director.pyqtgraph_common
		scores_active = director.scores_active
		hor_axis_name = scores_active.hor_axis_name
		vert_axis_name = scores_active.vert_axis_name
		hor_dim = scores_active._hor_dim
		vert_dim = scores_active._vert_dim
		scores = scores_active.scores
		nscored = scores_active.nscored_individ
		point_size = common.point_size

		graphics_layout_widget, plot = (
			pyqtgraph_common.begin_pyqtgraph_plot_with_title("Clusters")
		)
		plot = pyqtgraph_common.set_aspect_and_grid_in_pyqtgraph_plot(plot)
		plot.setLabel("left", hor_axis_name, color="k", size=15)
		plot.setLabel("bottom", vert_axis_name, color="k", size=15)
		pyqtgraph_common.set_ranges_for_pyqtgraph_plot(plot)
		x_coords = [
			scores.iloc[each_point, hor_dim + 1]
			for each_point in range(nscored)
		]
		y_coords = [
			scores.iloc[each_point, vert_dim + 1]
			for each_point in range(nscored)
		]

		# Color points by cluster assignment
		cluster_labels = scores_active.cluster_labels
		colors = [
			'r', 'b', 'g', 'orange', 'purple',
			'brown', 'pink', 'gray', 'olive', 'cyan'
		]

		# Group points by cluster and plot each cluster with its color
		for cluster_id in set(cluster_labels):
			cluster_color = colors[cluster_id % len(colors)]
			# Get indices for this cluster
			cluster_indices = [
				i for i, label in enumerate(cluster_labels)
				if label == cluster_id
			]
			# Get coordinates for this cluster
			cluster_x = [x_coords[i] for i in cluster_indices]
			cluster_y = [y_coords[i] for i in cluster_indices]

			plot.scatterPlot(
				cluster_x,
				cluster_y,
				pen=cluster_color,
				symbol="o",
				symbolSize=point_size,
				symbolBrush=cluster_color,
			)

		# Add cluster centroids as plus signs with different colors
		if common.have_clusters():
			cluster_centers = scores_active.cluster_centers
			# Extract centroid coordinates for the current axes
			centroid_x = cluster_centers[:, 0].tolist()  # First dimension
			centroid_y = cluster_centers[:, 1].tolist()  # Second dimension

			# Create different colors for each centroid
			colors = [
				'r', 'b', 'g', 'orange', 'purple',
				'brown', 'pink', 'gray', 'olive', 'cyan'
			]
			n_centroids = len(centroid_x)

			for i in range(n_centroids):
				color = colors[i % len(colors)]
				plot.scatterPlot(
					[centroid_x[i]],
					[centroid_y[i]],
					pen=color,
					symbol="+",
					symbolSize=point_size * 3,
					symbolBrush=None,
				)

		director.set_focus_on_tab("Plot")

		return graphics_layout_widget

	# --------------------------------------------------------------**--------

	def request_compare_plot_for_tabs_using_pyqtgraph(self) -> None:
		director = self._director
		common = director.common
		pyqtgraph_common = director.pyqtgraph_common
		target = director.target_active
		point_coords = target.point_coords

		common.set_axis_extremes_based_on_coordinates(point_coords)
		tab_plot_widget = self.plot_compare_using_pyqtgraph(target)
		tab_gallery_widget = self.plot_compare_using_pyqtgraph(target)
		pyqtgraph_common.plot_to_gui_using_pyqtgraph(
			tab_plot_widget, tab_gallery_widget
		)

		director.set_focus_on_tab("Plot")

		return

	# ----------------------------------------------------------**------------

	def plot_compare_using_pyqtgraph(
		self, target: TargetFeature
	) -> pg.GraphicsLayoutWidget:
		director = self._director
		pyqtgraph_common = director.pyqtgraph_common
		configuration_active = director.configuration_active
		point_coords = configuration_active.point_coords
		point_labels = configuration_active.point_labels
		range_points = configuration_active.range_points

		ndim = target.ndim

		if ndim > MAXIMUM_NUMBER_OF_DIMENSIONS_FOR_PLOTTING:
			director.set_focus_on_tab("Output")
			return None

		mid_x_s: list[float] = []
		mid_y_s: list[float] = []

		graphics_layout_widget, plot = (
			pyqtgraph_common.begin_pyqtgraph_plot_with_title(None)
		)
		plot = pyqtgraph_common.set_aspect_and_grid_in_pyqtgraph_plot(plot)

		pyqtgraph_common.add_axes_labels_to_pyqtgraph_plot(plot)
		pyqtgraph_common.set_ranges_for_pyqtgraph_plot(plot)

		for each_label in range_points:
			mid_x = (
				point_coords.iloc[each_label, 0]
				+ target.point_coords.iloc[each_label, 0]
			) / 2
			mid_y = (
				point_coords.iloc[each_label, 1]
				+ target.point_coords.iloc[each_label, 1]
			) / 2
			mid_x_s.append(mid_x)
			mid_y_s.append(mid_y)
			point_label = pg.TextItem(text=point_labels[each_label], color="k")

			point_label.setPos(mid_x, mid_y + 0.04)
			plot.addItem(point_label)
			a_label = pg.TextItem(text="A", color="black")
			a_label.setPos(
				point_coords.iloc[each_label, 0],
				point_coords.iloc[each_label, 1] + 0.04,
			)
			plot.addItem(a_label)
			t_label = pg.TextItem(text="T", color="black")
			t_label.setPos(
				target.point_coords.iloc[each_label, 0],
				target.point_coords.iloc[each_label, 1] + 0.04,
			)
			plot.addItem(t_label)
			plot.plot(
				[
					point_coords.iloc[each_label, 0],
					target.point_coords.iloc[each_label, 0],
				],
				[
					point_coords.iloc[each_label, 1],
					target.point_coords.iloc[each_label, 1],
				],
				color="black",
				width=4,
			)

		director.set_focus_on_tab("Plot")

		return graphics_layout_widget

	# ------------------------------------------------------------------------

	def request_configuration_plot_for_tabs_using_pyqtgraph(self) -> None:
		director = self._director
		common = director.common
		pyqtgraph_common = director.pyqtgraph_common
		configuration_active = director.configuration_active
		point_coords = configuration_active.point_coords

		common.set_axis_extremes_based_on_coordinates(point_coords)

		tab_plot_widget = self.plot_a_configuration_using_pyqtgraph()
		tab_gallery_widget = self.plot_a_configuration_using_pyqtgraph()
		pyqtgraph_common.plot_to_gui_using_pyqtgraph(
			tab_plot_widget, tab_gallery_widget
		)

		return

	# ------------------------------------------------------------------------

	def plot_a_configuration_using_pyqtgraph(self) -> pg.GraphicsLayoutWidget:
		director = self._director
		pyqtgraph_common = director.pyqtgraph_common
		configuration_active = director.configuration_active
		ndim = configuration_active.ndim

		if ndim > MAXIMUM_NUMBER_OF_DIMENSIONS_FOR_PLOTTING:
			director.set_focus_on_tab("Output")
			return None

		graphics_layout_widget, plot = (
			pyqtgraph_common.begin_pyqtgraph_plot_with_title(None)
		)
		plot = pyqtgraph_common.set_aspect_and_grid_in_pyqtgraph_plot(plot)

		pyqtgraph_common.add_axes_labels_to_pyqtgraph_plot(plot)
		pyqtgraph_common.set_ranges_for_pyqtgraph_plot(plot)
		pyqtgraph_common.add_connector_to_pyqtgraph_plot(plot)
		pyqtgraph_common.add_bisector_to_pyqtgraph_plot(plot)
		pyqtgraph_common.add_configuration_to_pyqtgraph_plot(plot)

		director.set_focus_on_tab("Plot")

		return graphics_layout_widget

	# ------------------------------------------------------------------------

	def request_contest_plot_for_tabs_using_pyqtgraph(self) -> None:
		director = self._director
		common = director.common
		pyqtgraph_common = director.pyqtgraph_common
		configuration_active = director.configuration_active
		point_coords = configuration_active.point_coords

		common.set_axis_extremes_based_on_coordinates(point_coords)
		tab_plot_widget = self._plot_contest_using_pyqtgraph()
		tab_gallery_widget = self._plot_contest_using_pyqtgraph()

		pyqtgraph_common.plot_to_gui_using_pyqtgraph(
			tab_plot_widget, tab_gallery_widget
		)

		return

	# ------------------------------------------------------------------------

	def _plot_contest_using_pyqtgraph(self) -> pg.GraphicsLayoutWidget:
		director = self._director
		common = director.common
		pyqtgraph_common = director.pyqtgraph_common
		configuration_active = director.configuration_active
		rivalry = director.rivalry
		hor_dim = common.hor_dim
		vert_dim = common.vert_dim
		point_coords = configuration_active.point_coords
		point_labels = configuration_active.point_labels
		rival_a = rivalry.rival_a
		rival_b = rivalry.rival_b
		connector = rivalry.connector
		ndim = configuration_active.ndim

		if ndim > MAXIMUM_NUMBER_OF_DIMENSIONS_FOR_PLOTTING:
			director.set_focus_on_tab("Output")
			return None

		x_coords: list[int] = []
		y_coords: list[int] = []
		graphics_layout_widget, plot = (
			pyqtgraph_common.begin_pyqtgraph_plot_with_title("Contest")
		)
		plot = pyqtgraph_common.set_aspect_and_grid_in_pyqtgraph_plot(plot)
		pyqtgraph_common.add_axes_labels_to_pyqtgraph_plot(plot)
		pyqtgraph_common.set_ranges_for_pyqtgraph_plot(plot)
		pen = pg.mkPen(color=(255, 0, 0))
		rival_a_label = pg.TextItem(
			text=point_labels[rival_a.index], color="k", border="w", fill=None
		)
		rival_a_label.setPos(
			point_coords.iloc[rival_a.index, hor_dim],
			point_coords.iloc[rival_a.index, vert_dim] + 0.04,
		)
		plot.addItem(rival_a_label)
		rival_b_label = pg.TextItem(
			text=point_labels[rivalry.rival_b.index],
			color="k",
			border="w",
			fill=None,
		)
		rival_b_label.setPos(
			point_coords.iloc[rival_b.index, hor_dim],
			point_coords.iloc[rival_b.index, vert_dim] + 0.04,
		)
		plot.addItem(rival_b_label)
		x_coords.append(point_coords.iloc[rival_a.index, hor_dim])
		y_coords.append(point_coords.iloc[rival_a.index, vert_dim])
		x_coords.append(point_coords.iloc[rival_b.index, hor_dim])
		y_coords.append(point_coords.iloc[rival_b.index, vert_dim])
		plot.scatterPlot(x_coords, y_coords, symbolSize=5, symbol="o", pen=pen)
		core_a = pg.QtWidgets.QGraphicsEllipseItem(
			point_coords.iloc[rival_a.index, hor_dim] - connector.length * 0.2,
			point_coords.iloc[rival_a.index, vert_dim]
			- connector.length * 0.2,
			connector.length * 0.4,
			connector.length * 0.4,
		)
		core_a.setPen(pen)
		plot.addItem(core_a)
		core_b = pg.QtWidgets.QGraphicsEllipseItem(
			point_coords.iloc[rival_b.index, hor_dim] - connector.length * 0.2,
			point_coords.iloc[rival_b.index, vert_dim]
			- connector.length * 0.2,
			connector.length * 0.4,
			connector.length * 0.4,
		)
		core_b.setPen(pen)
		plot.addItem(core_b)
		pyqtgraph_common.add_bisector_to_pyqtgraph_plot(plot)
		pyqtgraph_common.add_connector_to_pyqtgraph_plot(plot)
		pyqtgraph_common.add_west_to_pyqtgraph_plot(plot)
		pyqtgraph_common.add_east_to_pyqtgraph_plot(plot)
		pyqtgraph_common.add_first_dim_divider_to_pyqtgraph_plot(plot)
		pyqtgraph_common.add_second_dim_divider_to_pyqtgraph_plot(plot)
		m_label = pg.TextItem(text="M", color="k", border="w", fill=None)
		m_label.setPos(
			rivalry.bisector._cross_x, rivalry.bisector._cross_y + 0.04
		)
		plot.addItem(m_label)

		director.set_focus_on_tab("Plot")

		return graphics_layout_widget

	# ------------------------------------------------------------------------

	def request_convertible_plot_for_tabs_using_pyqtgraph(self) -> None:
		director = self._director
		common = director.common
		pyqtgraph_common = director.pyqtgraph_common
		configuration_active = director.configuration_active
		point_coords = configuration_active.point_coords

		convertible_groups_to_show = (
			director.current_command._convertible_groups_to_show
		)

		common.set_axis_extremes_based_on_coordinates(point_coords)

		tab_plot_widget = self._plot_convertible_using_pyqtgraph(
			convertible_groups_to_show
		)
		tab_gallery_widget = self._plot_convertible_using_pyqtgraph(
			convertible_groups_to_show
		)
		pyqtgraph_common.plot_to_gui_using_pyqtgraph(
			tab_plot_widget, tab_gallery_widget
		)

		return

	# ------------------------------------------------------------------------

	def _plot_convertible_using_pyqtgraph(
		self, convertible_groups_to_show: str
	) -> pg.GraphicsLayoutWidget:
		director = self._director
		pyqtgraph_common = director.pyqtgraph_common
		pyqtgraph_plotter = director.pyqtgraph_plotter
		configuration_active = director.configuration_active
		ndim = configuration_active.ndim

		if ndim > MAXIMUM_NUMBER_OF_DIMENSIONS_FOR_PLOTTING:
			director.set_focus_on_tab("Output")
			return None

		graphics_layout_widget, plot = (
			pyqtgraph_common.begin_pyqtgraph_plot_with_title("Convertible")
		)
		plot = pyqtgraph_common.set_aspect_and_grid_in_pyqtgraph_plot(plot)

		pyqtgraph_common.add_axes_labels_to_pyqtgraph_plot(plot)
		pyqtgraph_common.set_ranges_for_pyqtgraph_plot(plot)
		pyqtgraph_common.add_reference_points_to_pyqtgraph_plot(plot)
		pyqtgraph_common.add_connector_to_pyqtgraph_plot(plot)
		pyqtgraph_common.add_west_to_pyqtgraph_plot(plot)
		pyqtgraph_common.add_east_to_pyqtgraph_plot(plot)

		convertible_people_points = (
			configuration_active._populate_convertible_groups_to_show(
				convertible_groups_to_show
			)
		)
		pyqtgraph_plotter._fill_convertible_regions_in_pyqtgraph_plot(
			plot, convertible_people_points
		)

		director.set_focus_on_tab("Plot")

		return graphics_layout_widget

	# ------------------------------------------------------------------------

	def _fill_convertible_regions_in_pyqtgraph_plot(
		self, plot: pg.PlotItem, convertible_people_points: PeoplePoints
	) -> None:
		director = self._director
		common = director.common
		rivalry = director.rivalry
		convertible_to_left = rivalry.convertible_to_left
		convertible_to_right = rivalry.convertible_to_right
		scores_active = director.scores_active
		score_color = scores_active.score_color
		point_size = common.point_size

		convertible_to_right_region = QtGui.QPainterPath()
		convertible_to_right_region.moveTo(
			convertible_to_right._x[0], convertible_to_right._y[0]
		)
		for x_, y_ in zip(
			convertible_to_right._x[1:],
			convertible_to_right._y[1:],
			strict=True,
		):
			convertible_to_right_region.lineTo(x_, y_)
		convertible_to_right_region_item = QtWidgets.QGraphicsPathItem(
			convertible_to_right_region
		)
		convertible_to_right_region_brush = QtGui.QBrush(
			QtGui.QColor(convertible_to_right._fill)
		)
		convertible_to_right_region_item.setBrush(
			convertible_to_right_region_brush
		)
		convertible_to_right_region_item.setPen(
			pg.mkPen(color=(0, 0, 0), width=2)
		)
		plot.addItem(convertible_to_right_region_item)

		convertible_to_left_region = QtGui.QPainterPath()
		convertible_to_left_region.moveTo(
			convertible_to_left._x[0], convertible_to_left._y[0]
		)
		for x_, y_ in zip(
			convertible_to_left._x[1:], convertible_to_left._y[1:], strict=True
		):
			convertible_to_left_region.lineTo(x_, y_)
		convertible_to_left_region_item = QtWidgets.QGraphicsPathItem(
			convertible_to_left_region
		)
		convertible_to_left_region_brush = QtGui.QBrush(
			QtGui.QColor(convertible_to_left._fill)
		)
		convertible_to_left_region_item.setBrush(
			convertible_to_left_region_brush
		)
		convertible_to_left_region_item.setPen(
			pg.mkPen(color=(0, 0, 0), width=2)
		)
		plot.addItem(convertible_to_left_region_item)

		plot.scatterPlot(
			convertible_people_points.x,
			convertible_people_points.y,
			pen=score_color,
			symbol="o",
			size=point_size,
		)

		return

	# ------------------------------------------------------------------------

	def request_core_plot_for_tabs_using_pyqtgraph(self) -> None:
		director = self._director
		common = director.common
		pyqtgraph_common = director.pyqtgraph_common
		configuration_active = director.configuration_active
		point_coords = configuration_active.point_coords

		core_groups_to_show = director.current_command.core_groups_to_show

		common.set_axis_extremes_based_on_coordinates(point_coords)
		tab_plot_widget = self._plot_core_using_pyqtgraph(core_groups_to_show)
		tab_gallery_widget = self._plot_core_using_pyqtgraph(
			core_groups_to_show
		)

		pyqtgraph_common.plot_to_gui_using_pyqtgraph(
			tab_plot_widget, tab_gallery_widget
		)

		return

	# ------------------------------------------------------------------------

	def _plot_core_using_pyqtgraph(
		self, core_groups_to_show: str
	) -> pg.GraphicsLayoutWidget:
		director = self._director
		pyqtgraph_common = director.pyqtgraph_common
		pyqtgraph_plotter = director.pyqtgraph_plotter
		configuration_active = director.configuration_active
		ndim = configuration_active.ndim
		if ndim > MAXIMUM_NUMBER_OF_DIMENSIONS_FOR_PLOTTING:
			director.set_focus_on_tab("Output")
			return None

		graphics_layout_widget, plot = (
			pyqtgraph_common.begin_pyqtgraph_plot_with_title("Core Supporters")
		)
		plot = pyqtgraph_common.set_aspect_and_grid_in_pyqtgraph_plot(plot)

		pyqtgraph_common.add_axes_labels_to_pyqtgraph_plot(plot)
		pyqtgraph_common.set_ranges_for_pyqtgraph_plot(plot)
		pyqtgraph_common.add_reference_points_to_pyqtgraph_plot(plot)
		pyqtgraph_common.add_connector_to_pyqtgraph_plot(plot)

		core_people_points = (
			configuration_active._populate_core_groups_to_show(
				core_groups_to_show
			)
		)

		pyqtgraph_plotter._fill_core_regions_in_pyqtgraph_plot(
			plot, core_people_points
		)

		director.set_focus_on_tab("Plot")

		return graphics_layout_widget

	# ------------------------------------------------------------------------

	# def _determine_circles_defining_core_regions_using_pyqtgraph(self)\
	#  -> None:

	# 	title: str = "Determine circles defining core regions using pyqtgraph"
	# 	message: str = "Must be created"

	# 	raise UnderDevelopmentError(title, message)

	# ------------------------------------------------------------------------

	def _fill_core_regions_in_pyqtgraph_plot(
		self, plot: pg.PlotItem, core_people_points: PeoplePoints
	) -> None:
		director = self._director
		common = director.common
		rivalry = director.rivalry
		connector = rivalry.connector
		core_left = rivalry.core_left
		core_left_center = rivalry.core_left._center
		core_right = rivalry.core_right
		core_right = rivalry.core_right
		core_right_center = rivalry.core_right._center
		scores_active = director.scores_active
		score_color = scores_active.score_color
		point_size = common.point_size

		core_a = pg.QtWidgets.QGraphicsEllipseItem(
			core_left_center.x - connector.length * CORE_SIZE_HALF,
			core_left_center.y - connector.length * CORE_SIZE_HALF,
			connector.length * CORE_SIZE_FULL,
			connector.length * CORE_SIZE_FULL,
		)
		core_a.setPen(pg.mkPen(color="b"))

		core_a.setBrush(pg.mkBrush(color=core_left._fill))
		plot.addItem(core_a)
		core_b = pg.QtWidgets.QGraphicsEllipseItem(
			core_right_center.x - connector.length * 0.2,
			core_right_center.y - connector.length * 0.2,
			connector.length * 0.4,
			connector.length * 0.4,
		)
		core_b.setPen(pg.mkPen(color="b"))
		core_b.setBrush(pg.mkBrush(color=core_right._fill))
		plot.addItem(core_b)
		plot.scatterPlot(
			core_people_points.x,
			core_people_points.y,
			pen=score_color,
			symbol="o",
			size=point_size,
		)

		return

	# ------------------------------------------------------------------------

	def request_cutoff_plot_for_tabs_using_pyqtgraph(self) -> None:
		director = self._director
		pyqtgraph_common = director.pyqtgraph_common
		similarities_active = director.similarities_active

		tab_plot_widget = self._plot_cutoff_using_pyqtgraph(
			similarities_active.value_type
		)
		gallery_plot_widget = self._plot_cutoff_using_pyqtgraph(
			similarities_active.value_type
		)

		pyqtgraph_common.plot_to_gui_using_pyqtgraph(
			tab_plot_widget, gallery_plot_widget
		)

		return

	# ------------------------------------------------------------------------

	def _plot_cutoff_using_pyqtgraph(
		self, value_type: str
	) -> pg.GraphicsLayoutWidget:
		director = self._director
		similarities_active = director.similarities_active

		similarities_as_list = similarities_active.similarities_as_list
		range_similarities = similarities_active.range_similarities

		x_coords: list[float] = []
		y_coords: list[float] = []
		# sorted_list: list[float] = []
		list_size = len(similarities_as_list)
		sorted_list = sorted(similarities_as_list)
		for each_pair in range_similarities:
			x_coords.append(sorted_list[each_pair])
			y_coords.append(each_pair * 100.0 / list_size)
		graphics_layout_widget, plot = (
			self._director.common.begin_pyqtgraph_plot_with_title(None)
		)
		plot.showGrid(x=True, y=True)
		pen = pg.mkPen(color=(255, 0, 0))
		line = pg.PlotDataItem(
			x_coords,
			y_coords,
			pen=pen,
			symbol="o",
			symbolPen="k",
			symbolBrush=(255, 0, 0),
		)
		plot.addItem(line)
		plot.setLabel("bottom", "Cutoff", color="k", size="15pt")
		if value_type == "similarities":
			plot.setLabel(
				"left",
				"Percentage of Pairs Above Similarity",
				color="k",
				size="15pt",
			)
		else:
			plot.setLabel(
				"left",
				"Percentage of Pairs Below Dissimilarity",
				color="k",
				size="15pt",
			)

		director.set_focus_on_tab("Plot")

		return graphics_layout_widget

	# ------------------------------------------------------------------------

	def request_directions_plot_for_tabs_using_pyqtgraph(self) -> None:
		director = self._director
		pyqtgraph_common = director.pyqtgraph_common
		configuration_active = director.configuration_active
		point_coords = configuration_active.point_coords

		pyqtgraph_common.set_axis_extremes_based_on_coordinates(point_coords)
		tab_plot_widget = self._plot_directions_using_pyqtgraph()
		tab_gallery_widget = self._plot_directions_using_pyqtgraph()

		pyqtgraph_common.plot_to_gui_using_pyqtgraph(
			tab_plot_widget, tab_gallery_widget
		)

		return

	# ------------------------------------------------------------------------

	def _plot_directions_using_pyqtgraph(self) -> pg.GraphicsLayoutWidget:
		director = self._director
		common = director.common
		pyqtgraph_common = director.pyqtgraph_common
		configuration_active = director.configuration_active
		point_coords = configuration_active.point_coords
		range_points = configuration_active.range_points

		hor_dim = common.hor_dim
		vert_dim = common.vert_dim

		ndim = configuration_active.ndim

		if ndim > MAXIMUM_NUMBER_OF_DIMENSIONS_FOR_PLOTTING:
			director.set_focus_on_tab("Output")
			return None

		graphics_layout_widget, plot = (
			pyqtgraph_common.begin_pyqtgraph_plot_with_title(None)
		)
		plot = pyqtgraph_common.set_aspect_and_grid_in_pyqtgraph_plot(plot)

		x = [
			point_coords.iloc[each_point, hor_dim]
			for each_point in range_points
		]
		y = [
			point_coords.iloc[each_point, vert_dim]
			for each_point in range_points
		]
		pyqtgraph_common.add_axes_labels_to_pyqtgraph_plot(plot)
		pyqtgraph_common.set_ranges_for_pyqtgraph_plot(plot)

		for each_point in range_points:
			# Calculate the distance of the point from the origin
			distance = np.sqrt(x[each_point] ** 2 + y[each_point] ** 2)
			# Normalize the point so that it lies on the unit circle
			unit_x, unit_y = x[each_point] / distance, y[each_point] / distance
			arrow_len = 0.1  # adjust the size of the arrow
			line_pen = pg.mkPen("r", width=3)
			# create line from origin to the (normalized) point
			line = pg.PlotDataItem([0, unit_x], [0, unit_y], pen=line_pen)
			plot.addItem(line)
			# calculate rotation angle
			# (in degrees) for the arrow. Add 180 degree for correction
			angle = np.degrees(np.arctan2(unit_y, unit_x)) + 180
			# Add an ArrowItem at each (normalized) point
			arrow = pg.ArrowItem(
				pos=(unit_x, unit_y),
				angle=angle,
				headLen=arrow_len,
				tipAngle=45,
				baseAngle=20,
				brush="y",
			)
			plot.addItem(arrow)
			a_label = pg.TextItem(
				text=self.point_labels[each_point],
				color="k",
				anchor=(0.5, 1),
				border="w",
				fill=None,
			)
			nudge_x = unit_x + 0.2 if unit_x >= 0.0 else unit_x - 0.2
			nudge_y = unit_y if unit_y >= 0.0 else unit_y - 0.2
			a_label.setPos(nudge_x, nudge_y)
			plot.addItem(a_label)
		# Add a unit circle
		x = np.linspace(-1, 1, 500)
		y1 = np.sqrt(1 - x**2)
		y2 = -np.sqrt(1 - x**2)
		plot.plot(x, y1, pen="b")
		plot.plot(x, y2, pen="b")

		director.set_focus_on_tab("Plot")

		return graphics_layout_widget

	# --------------------------------------------------------------**--------

	def request_evaluations_plot_for_tabs_using_pyqtgraph(self) -> None:
		# consider renaming

		director = self._director
		pyqtgraph_common = director.pyqtgraph_common

		tab_plot_widget = self.plot_evaluation_means_using_pyqtgraph()
		tab_gallery_widget = self.plot_evaluation_means_using_pyqtgraph()

		pyqtgraph_common.plot_to_gui_using_pyqtgraph(
			tab_plot_widget, tab_gallery_widget
		)

		return

	# ---------------------------------------------------------------**-------

	def plot_evaluation_means_using_pyqtgraph(self) -> pg.GraphicsLayoutWidget:
		director = self._director
		evaluations_active = director.evaluations_active
		avg_eval = evaluations_active.avg_eval
		names_eval_sorted = evaluations_active.names_eval_sorted

		graphics_layout_widget = PlotWidget()

		# Get the mean values in sorted order (highest to lowest)
		# Use names_eval_sorted to get the correct order
		mean_values = [avg_eval[name] for name in names_eval_sorted]
		mean_values.reverse()  # Reverse to match original order

		indices = range(len(mean_values))
		# the position on the y-axis of the bars
		# Adjust the centers and the widths of the bars
		centers = [val / 2 for val in mean_values]
		widths = mean_values
		bar_graph_item = BarGraphItem(
			x=centers, height=0.6, width=widths, y=indices, brush="b", pen="k"
		)
		graphics_layout_widget.addItem(bar_graph_item)

		# Custom ticks (labels) on the y-axis
		y_axis = graphics_layout_widget.getAxis("left")
		y_labels = names_eval_sorted[::-1]  # Reverse order-match mean_values

		y_axis.setTicks([[(i, label) for i, label in enumerate(y_labels)]])
		graphics_layout_widget.getAxis("bottom").setLabel("Average Evaluation")
		graphics_layout_widget.setBackground("w")

		director.set_focus_on_tab("Plot")

		return graphics_layout_widget

	# ------------------------------------------------------------------------

	def request_first_plot_for_tabs_using_pyqtgraph(self) -> None:
		director = self._director
		common = director.common
		pyqtgraph_common = director.pyqtgraph_common
		configuration_active = director.configuration_active
		point_coords = configuration_active.point_coords

		first_dim_groups_to_show = (
			director.current_command._first_dim_groups_to_show
		)

		common.set_axis_extremes_based_on_coordinates(point_coords)

		tab_plot_widget = self._plot_first_using_pyqtgraph(
			first_dim_groups_to_show
		)
		tab_gallery_widget = self._plot_first_using_pyqtgraph(
			first_dim_groups_to_show
		)

		pyqtgraph_common.plot_to_gui_using_pyqtgraph(
			tab_plot_widget, tab_gallery_widget
		)

		return

	# --------------------------------------------------------------------

	def _plot_first_using_pyqtgraph(
		self, first_dim_groups_to_show: str
	) -> pg.GraphicsLayoutWidget:
		director = self._director
		pyqtgraph_common = director.pyqtgraph_common
		pyqtgraph_plotter = director.pyqtgraph_plotter
		configuration_active = director.configuration_active
		ndim = configuration_active.ndim

		if ndim > MAXIMUM_NUMBER_OF_DIMENSIONS_FOR_PLOTTING:
			director.set_focus_on_tab("Output")
			return None

		graphics_layout_widget, plot = (
			pyqtgraph_common.begin_pyqtgraph_plot_with_title(
				"First Dimension Supporters"
			)
		)
		plot = pyqtgraph_common.set_aspect_and_grid_in_pyqtgraph_plot(plot)

		pyqtgraph_common.add_axes_labels_to_pyqtgraph_plot(plot)
		pyqtgraph_common.set_ranges_for_pyqtgraph_plot(plot)

		pyqtgraph_common.add_reference_points_to_pyqtgraph_plot(plot)
		pyqtgraph_common.add_connector_to_pyqtgraph_plot(plot)

		first_dim_people_points = (
			configuration_active._populate_first_dim_groups_to_show(
				first_dim_groups_to_show
			)
		)
		pyqtgraph_plotter._fill_first_dim_regions_in_pyqtgraph_plot(
			plot, first_dim_people_points
		)

		director.set_focus_on_tab("Plot")

		return graphics_layout_widget

	# ------------------------------------------------------------------------

	def _fill_first_dim_regions_in_pyqtgraph_plot(
		self, plot: pg.PlotItem, first_dim_people_points: PeoplePoints
	) -> None:
		director = self._director
		common = director.common
		rivalry = director.rivalry
		first_left = rivalry.first_left
		first_right = rivalry.first_right
		point_size = common.point_size
		scores_active = director.scores_active
		score_color = scores_active.score_color

		first_left_region = QtGui.QPainterPath()
		first_left_region.moveTo(first_left._x[0], first_left._y[0])
		for x_, y_ in zip(first_left._x[1:], first_left._y[1:], strict=True):
			first_left_region.lineTo(x_, y_)
		first_left_region_item = QtWidgets.QGraphicsPathItem(first_left_region)
		first_left_brush = QtGui.QBrush(QtGui.QColor(first_left._fill))
		first_left_region_item.setBrush(first_left_brush)
		first_left_region_item.setPen(pg.mkPen(color=(0, 0, 0), width=2))
		plot.addItem(first_left_region_item)
		first_right_region = QtGui.QPainterPath()
		first_right_region.moveTo(first_right._x[0], first_right._y[0])
		for x_, y_ in zip(first_right._x[1:], first_right._y[1:], strict=True):
			first_right_region.lineTo(x_, y_)
		first_right_region_item = QtWidgets.QGraphicsPathItem(
			first_right_region
		)
		first_right_brush = QtGui.QBrush(QtGui.QColor(first_right._fill))
		first_right_region_item.setBrush(first_right_brush)
		first_right_region_item.setPen(pg.mkPen(color=(0, 0, 0), width=2))
		plot.addItem(first_right_region_item)
		points = plot.scatterPlot(
			x=first_dim_people_points.x,
			y=first_dim_people_points.y,
			pen=score_color,
			symbol="o",
			size=point_size,
		)
		plot.addItem(points)

		return

	# ------------------------------------------------------------------------

	def request_grouped_data_plot_for_tabs_using_pyqtgraph(self) -> None:
		director = self._director
		common = director.common
		pyqtgraph_common = director.pyqtgraph_common
		grouped_data_active = director.grouped_data_active
		group_coords = grouped_data_active.group_coords

		common.set_axis_extremes_based_on_coordinates(group_coords)
		tab_plot_widget = self.plot_grouped_data_using_pyqtgraph()
		tab_gallery_widget = self.plot_grouped_data_using_pyqtgraph()

		pyqtgraph_common.plot_to_gui_using_pyqtgraph(
			tab_plot_widget, tab_gallery_widget
		)

		return

	# -----------------------------------------------------------------------

	def plot_grouped_data_using_pyqtgraph(self) -> pg.GraphicsLayoutWidget:
		director = self._director
		grouped_data_active = director.grouped_data_active
		hor_dim = grouped_data_active._hor_dim
		vert_dim = grouped_data_active._vert_dim
		group_coords = grouped_data_active.group_coords
		group_labels = grouped_data_active.group_labels
		range_groups = grouped_data_active.range_groups
		dim_names = grouped_data_active.dim_names

		ndim = grouped_data_active.ndim
		if ndim > MAXIMUM_NUMBER_OF_DIMENSIONS_FOR_PLOTTING:
			director.set_focus_on_tab("Output")
			return None

		graphics_layout_widget, plot = (
			self._director.pyqtgraph_common.begin_pyqtgraph_plot_with_title(
				"Groups"
			)
		)
		plot = self._director.pyqtgraph_common.\
			set_aspect_and_grid_in_pyqtgraph_plot(plot
		)
		x = [
			group_coords.iloc[each_point, hor_dim]
			for each_point in range_groups
		]
		y = [
			group_coords.iloc[each_point, vert_dim]
			for each_point in range_groups
		]
		# self._director.pyqtgraph_common.\
		# add_axes_labels_to_pyqtgraph_plot(plot)
		plot.setLabel("left", dim_names[vert_dim], color="k", size="15pt")
		plot.setLabel("bottom", dim_names[hor_dim], color="k", size="15pt")
		self._director.pyqtgraph_common.set_ranges_for_pyqtgraph_plot(plot)
		for each_label in range_groups:
			a_label = pg.TextItem(
				text=group_labels[each_label],
				color="k",
				anchor=(0.5, 1),
				border="w",
				fill=None,
			)
			a_label.setPos(x[each_label], y[each_label])
			plot.addItem(a_label)
		# pen = pg.mkPen(color=(255, 0, 0))
		plot.scatterPlot(
			x, y, pen="black", symbol="o", symbolSize=5, symbolBrush="k"
		)

		director.set_focus_on_tab("Plot")

		return graphics_layout_widget

	# ------------------------------------------------------------------------

	def request_heatmap_corr_plot_for_tabs_using_pyqtgraph(self) -> None:
		director = self._director
		pyqtgraph_common = director.pyqtgraph_common

		tab_plot_widget = self.plot_a_heatmap_corr_using_pyqtgraph()
		tab_gallery_widget = self.plot_a_heatmap_corr_using_pyqtgraph()

		pyqtgraph_common.plot_to_gui_using_pyqtgraph(
			tab_plot_widget, tab_gallery_widget
		)

		return

	# ------------------------------------------------------------------------

	def plot_a_heatmap_corr_using_pyqtgraph(self) -> pg.GraphicsLayoutWidget:
		director = self._director
		pyqtgraph_common = director.pyqtgraph_common
		correlations_active = director.correlations_active
		item_labels = correlations_active.item_labels
		item_names = correlations_active.item_names
		correlations_as_square = correlations_active.correlations_as_square

		correlations_as_lower_triangle = np.tril(correlations_as_square, k=0)

		layout_widget = pyqtgraph_common.create_heatmap_using_pyqtgraph(
			"Correlations",
			correlations_as_lower_triangle,
			"PiYG",
			item_names,
			item_labels,
			"Items",
		)

		director.set_focus_on_tab("Plot")

		return layout_widget

	# ------------------------------------------------------------------------

	def request_heatmap_dist_plot_for_tabs_using_pyqtgraph(self) -> None:
		director = self._director
		pyqtgraph_common = director.pyqtgraph_common

		tab_plot_widget = self.plot_a_heatmap_dist_using_pyqtgraph()
		tab_gallery_widget = self.plot_a_heatmap_dist_using_pyqtgraph()

		pyqtgraph_common.plot_to_gui_using_pyqtgraph(
			tab_plot_widget, tab_gallery_widget
		)

		return

	# ------------------------------------------------------------------------

	def plot_a_heatmap_dist_using_pyqtgraph(self) -> pg.GraphicsLayoutWidget:
		director = self._director
		pyqtgraph_common = director.pyqtgraph_common
		configuration_active = director.configuration_active
		point_names = configuration_active.point_names
		point_labels = configuration_active.point_labels
		distances_as_square = configuration_active.distances_as_square

		title = "Inter-point distances"
		distances_as_lower_triangle = np.tril(distances_as_square, k=0)
		layout_widget = pyqtgraph_common.create_heatmap_using_pyqtgraph(
			title,
			distances_as_lower_triangle,
			"binary",
			point_names,
			point_labels,
			"Items",
		)

		director.set_focus_on_tab("Plot")

		return layout_widget

	# ------------------------------------------------------------------------

	def request_heatmap_rank_diff_plot_for_tabs_using_pyqtgraph(self) -> None:
		director = self._director
		pyqtgraph_common = director.pyqtgraph_common

		tab_plot_widget = self.plot_a_heatmap_rank_diff_using_pyqtgraph()
		tab_gallery_widget = self.plot_a_heatmap_rank_diff_using_pyqtgraph()

		pyqtgraph_common.plot_to_gui_using_pyqtgraph(
			tab_plot_widget, tab_gallery_widget
		)

		return

	# ------------------------------------------------------------------------

	def plot_a_heatmap_rank_diff_using_pyqtgraph(
		self,
	) -> pg.GraphicsLayoutWidget:
		director = self._director
		pyqtgraph_common = director.pyqtgraph_common
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

		layout_widget = pyqtgraph_common.create_heatmap_using_pyqtgraph(
			title,
			differences_as_lower_triangle,
			"PiYG",
			item_names,
			item_labels,
			"Items",
		)

		director.set_focus_on_tab("Plot")

		return layout_widget

	# ------------------------------------------------------------------------

	def request_heatmap_ranked_dist_plot_for_tabs_using_pyqtgraph(self) \
		-> None:
		director = self._director
		pyqtgraph_common = director.pyqtgraph_common

		tab_plot_widget = self.plot_a_heatmap_ranked_dist_using_pyqtgraph()
		tab_gallery_widget = self.plot_a_heatmap_ranked_dist_using_pyqtgraph()

		pyqtgraph_common.plot_to_gui_using_pyqtgraph(
			tab_plot_widget, tab_gallery_widget
		)

		return

	# ------------------------------------------------------------------------

	def plot_a_heatmap_ranked_dist_using_pyqtgraph(
		self,
	) -> pg.GraphicsLayoutWidget:
		director = self._director
		pyqtgraph_common = director.pyqtgraph_common
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

		layout_widget = pyqtgraph_common.create_heatmap_using_pyqtgraph(
			title,
			ranked_distances_as_lower_triangle,
			"binary",
			item_names,
			item_labels,
			"Items",
		)

		director.set_focus_on_tab("Plot")

		return layout_widget

	# ------------------------------------------------------------------------

	def request_heatmap_ranked_simi_plot_for_tabs_using_pyqtgraph(self) \
		-> None:
		director = self._director
		pyqtgraph_common = director.pyqtgraph_common

		tab_plot_widget = self.plot_a_heatmap_ranked_simi_using_pyqtgraph()
		tab_gallery_widget = self.plot_a_heatmap_ranked_simi_using_pyqtgraph()

		pyqtgraph_common.plot_to_gui_using_pyqtgraph(
			tab_plot_widget, tab_gallery_widget
		)

		return

	# ------------------------------------------------------------------------

	def plot_a_heatmap_ranked_simi_using_pyqtgraph(
		self,
	) -> pg.GraphicsLayoutWidget:
		director = self._director
		pyqtgraph_common = director.pyqtgraph_common
		similarities_active = director.similarities_active
		item_labels = similarities_active.item_labels
		item_names = similarities_active.item_names
		ranked_similarities_as_square = (
			similarities_active.ranked_similarities_as_square
		)

		ranked_similarities_as_lower_triangle = np.tril(
			ranked_similarities_as_square, k=0
		)

		layout_widget = pyqtgraph_common.create_heatmap_using_pyqtgraph(
			"Ranked Similarities",
			ranked_similarities_as_lower_triangle,
			"binary",
			item_names,
			item_labels,
			"Items",
		)

		director.set_focus_on_tab("Plot")

		return layout_widget

	# ------------------------------------------------------------------------

	def request_heatmap_simi_plot_for_tabs_using_pyqtgraph(self) -> None:
		# Consider renaming
		director = self._director
		pyqtgraph_common = director.pyqtgraph_common

		tab_plot_widget = self.plot_a_heatmap_simi_using_pyqtgraph()
		tab_gallery_widget = self.plot_a_heatmap_simi_using_pyqtgraph()

		pyqtgraph_common.plot_to_gui_using_pyqtgraph(
			tab_plot_widget, tab_gallery_widget
		)

		return

	# ------------------------------------------------------------------------

	def plot_a_heatmap_simi_using_pyqtgraph(self) -> pg.GraphicsLayoutWidget:
		director = self._director
		pyqtgraph_common = director.pyqtgraph_common
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

		layout_widget = pyqtgraph_common.create_heatmap_using_pyqtgraph(
			title,
			similarities_as_lower_triangle,
			shading,
			item_names,
			item_labels,
			"Items",
		)

		director.set_focus_on_tab("Plot")

		return layout_widget

	# ------------------------------------------------------------------------

	def request_individuals_plot_for_tabs_using_pyqtgraph(self) -> None:
		title = "Request Individuals Plot for Plot and Gallery using PyQtGraph"
		message = "Must be created"
		raise UnderDevelopmentError(title, message)

		return

	# ------------------------------------------------------------------------

	def plot_individuals_using_pyqtgraph(self) -> None:
		title = "Plot Individuals using PyQtGraph"

		message = "Must be created"
		raise UnderDevelopmentError(title, message)

		return

	# ------------------------------------------------------------------------

	def request_joint_plot_for_tabs_using_pyqtgraph(self) -> None:
		director = self._director
		pyqtgraph_common = director.pyqtgraph_common

		tab_plot_widget = self._plot_joint_using_pyqtgraph()
		tab_gallery_widget = self._plot_joint_using_pyqtgraph()

		pyqtgraph_common.plot_to_gui_using_pyqtgraph(
			tab_plot_widget, tab_gallery_widget
		)

		return

	# ------------------------------------------------------------------------

	def _plot_joint_using_pyqtgraph(self) -> pg.GraphicsLayoutWidget:
		director = self._director
		common = director.common
		pyqtgraph_common = director.pyqtgraph_common
		configuration_active = director.configuration_active
		scores_active = director.scores_active
		score_1 = scores_active.score_1
		score_2 = scores_active.score_2
		score_color = scores_active.score_color
		ndim = configuration_active.ndim

		if ndim > MAXIMUM_NUMBER_OF_DIMENSIONS_FOR_PLOTTING:
			director.set_focus_on_tab("Output")
			return None

		graphics_layout_widget, plot = (
			pyqtgraph_common.begin_pyqtgraph_plot_with_title(
				"Candidates and Voters"
			)
		)
		plot = pyqtgraph_common.set_aspect_and_grid_in_pyqtgraph_plot(plot)
		pyqtgraph_common.add_axes_labels_to_pyqtgraph_plot(plot)
		pyqtgraph_common.set_ranges_for_pyqtgraph_plot(plot)
		# pen = pg.mkPen(color=(0, 255, 0))
		plot.scatterPlot(
			score_1,
			score_2,
			pen=score_color,
			symbol="o",
			symbolSize=5,
			symbolBrush=(0, 255, 0),
		)
		if common.have_reference_points():
			pyqtgraph_common.add_connector_to_pyqtgraph_plot(plot)
			pyqtgraph_common.add_bisector_to_pyqtgraph_plot(plot)
			if common.show_just_reference_points:
				pyqtgraph_common.add_reference_points_to_pyqtgraph_plot(plot)
				# pen)
			else:
				pyqtgraph_common.add_configuration_to_pyqtgraph_plot(plot)
		else:
			pyqtgraph_common.add_configuration_to_pyqtgraph_plot(plot)

		director.set_focus_on_tab("Plot")

		return graphics_layout_widget

	# ------------------------------------------------------------------------

	def request_likely_plot_for_tabs_using_pyqtgraph(self) -> None:
		director = self._director
		common = director.common
		pyqtgraph_common = director.pyqtgraph_common
		configuration_active = director.configuration_active
		point_coords = configuration_active.point_coords

		common.set_axis_extremes_based_on_coordinates(point_coords)

		# likely_groups_to_show = configuration_active.\
		# 	_populate_likely_groups_to_show
		likely_groups_to_show = director.current_command.likely_groups_to_show

		tab_plot_widget = self._plot_likely_using_pyqtgraph(
			likely_groups_to_show
		)
		tab_gallery_widget = self._plot_likely_using_pyqtgraph(
			likely_groups_to_show
		)

		pyqtgraph_common.plot_to_gui_using_pyqtgraph(
			tab_plot_widget, tab_gallery_widget
		)

		return

	# ------------------------------------------------------------------------

	def _plot_likely_using_pyqtgraph(
		self, likely_groups_to_show: str
	) -> pg.GraphicsLayoutWidget:
		director = self._director
		pyqtgraph_common = director.pyqtgraph_common
		pyqtgraph_plotter = director.pyqtgraph_plotter
		configuration_active = director.configuration_active
		ndim = configuration_active.ndim

		if ndim > MAXIMUM_NUMBER_OF_DIMENSIONS_FOR_PLOTTING:
			director.set_focus_on_tab("Output")
			return None

		graphics_layout_widget, plot = (
			pyqtgraph_common.begin_pyqtgraph_plot_with_title(
				"Likely Supporters"
			)
		)
		plot = pyqtgraph_common.set_aspect_and_grid_in_pyqtgraph_plot(plot)

		pyqtgraph_common.add_axes_labels_to_pyqtgraph_plot(plot)
		pyqtgraph_common.set_ranges_for_pyqtgraph_plot(plot)
		pyqtgraph_common.add_reference_points_to_pyqtgraph_plot(plot)
		pyqtgraph_common.add_connector_to_pyqtgraph_plot(plot)

		likely_people_points = (
			configuration_active._populate_likely_groups_to_show(
				likely_groups_to_show
			)
		)
		pyqtgraph_plotter._fill_likely_regions_in_pyqtgraph_plot(
			plot, likely_people_points
		)

		director.set_focus_on_tab("Plot")

		return graphics_layout_widget

	# ------------------------------------------------------------------------

	def _fill_likely_regions_in_pyqtgraph_plot(
		self, plot: pg.PlotItem, likely_people_points: PeoplePoints
	) -> None:
		director = self._director
		common = director.common
		rivalry = director.rivalry
		likely_left = rivalry.likely_left
		likely_right = rivalry.likely_right
		scores_active = director.scores_active
		score_color = scores_active.score_color
		point_size = common.point_size

		likely_left_region = QtGui.QPainterPath()
		likely_left_region.moveTo(likely_left._x[0], likely_left._y[0])
		for x_, y_ in zip(likely_left._x[1:], likely_left._y[1:], strict=True):
			likely_left_region.lineTo(x_, y_)
		likely_left_region_item = QtWidgets.QGraphicsPathItem(
			likely_left_region
		)
		likely_left_region_brush = QtGui.QBrush(
			QtGui.QColor(likely_left._fill)
		)
		likely_left_region_item.setBrush(likely_left_region_brush)
		likely_left_region_item.setPen(pg.mkPen(color=(0, 0, 0), width=2))
		plot.addItem(likely_left_region_item)
		likely_right_region = QtGui.QPainterPath()
		likely_right_region.moveTo(likely_right._x[0], likely_right._y[0])
		for x_, y_ in zip(
			likely_right._x[1:], likely_right._y[1:], strict=True
		):
			likely_right_region.lineTo(x_, y_)
		likely_right_region_item = QtWidgets.QGraphicsPathItem(
			likely_right_region
		)
		likely_right_region_brush = QtGui.QBrush(
			QtGui.QColor(likely_right._fill)
		)
		likely_right_region_item.setBrush(likely_right_region_brush)
		likely_right_region_item.setPen(pg.mkPen(color=(0, 0, 0), width=2))
		plot.addItem(likely_right_region_item)
		points = pg.ScatterPlotItem(
			x=likely_people_points.x,
			y=likely_people_points.y,
			pen=score_color,
			symbol="o",
			size=point_size,
		)
		plot.addItem(points)

		return

	# ------------------------------------------------------------------------

	def request_scores_plot_for_tabs_using_pyqtgraph(self) -> None:
		director = self._director
		common = director.common
		pyqtgraph_common = director.pyqtgraph_common
		scores_active = director.scores_active
		hor_axis_name = scores_active.hor_axis_name
		vert_axis_name = scores_active.vert_axis_name
		scores = scores_active.scores
		dim_names = scores_active.dim_names

		score_1 = scores[hor_axis_name]
		score_2 = scores[vert_axis_name]
		score_1_name = dim_names[0]
		score_2_name = dim_names[1]

		common.set_axis_extremes_based_on_coordinates(scores.iloc[:, 1:])

		tab_plot_widget = self.plot_scores_using_pyqtgraph()
		tab_gallery_widget = self.plot_scores_using_pyqtgraph()
		pyqtgraph_common.plot_to_gui_using_pyqtgraph(
			tab_plot_widget, tab_gallery_widget
		)

		self.score_1 = score_1
		self.score_1_name = score_1_name
		self.score_2 = score_2
		self.score_2_name = score_2_name

		return

	# -----------------------------------------------------------------**-----

	def plot_scores_using_pyqtgraph(self) -> pg.GraphicsLayoutWidget:
		director = self._director
		common = director.common
		pyqtgraph_common = director.pyqtgraph_common
		scores_active = director.scores_active
		hor_axis_name = scores_active.hor_axis_name
		vert_axis_name = scores_active.vert_axis_name
		hor_dim = scores_active._hor_dim
		vert_dim = scores_active._vert_dim
		scores = scores_active.scores
		nscored = scores_active.nscored_individ
		score_color = scores_active.score_color
		point_size = common.point_size

		graphics_layout_widget, plot = (
			pyqtgraph_common.begin_pyqtgraph_plot_with_title("Scores")
		)
		plot = pyqtgraph_common.set_aspect_and_grid_in_pyqtgraph_plot(plot)
		plot.setLabel("left", hor_axis_name, color="k", size=15)
		plot.setLabel("bottom", vert_axis_name, color="k", size=15)
		pyqtgraph_common.set_ranges_for_pyqtgraph_plot(plot)
		x_coords = [
			scores.iloc[each_point, hor_dim + 1]
			for each_point in range(nscored)
		]
		y_coords = [
			scores.iloc[each_point, vert_dim + 1]
			for each_point in range(nscored)
		]
		# pen = pg.mkPen(color=score_color)   # had been 255, 0, 0))
		plot.scatterPlot(
			x_coords,
			y_coords,
			pen=score_color,
			symbol="o",
			symbolSize=point_size,
			symbolBrush="k",
		)

		director.set_focus_on_tab("Plot")

		return graphics_layout_widget

	# ------------------------------------------------------------------------

	def request_stress_contribution_plot_for_tabs_using_pyqtgraph(self) \
		-> None:
		pyqtgraph_common = self._director.pyqtgraph_common
		tab_plot_widget = (
			self._plot_stress_contribution_by_point_using_pyqtgraph()
		)
		gallery_plot_widget = (
			self._plot_stress_contribution_by_point_using_pyqtgraph()
		)
		pyqtgraph_common.plot_to_gui_using_pyqtgraph(
			tab_plot_widget, gallery_plot_widget
		)
		self._director.set_focus_on_tab("Plot")
		return

	# ------------------------------------------------------------------------

	def _plot_stress_contribution_by_point_using_pyqtgraph(
		self,
	) -> pg.GraphicsLayoutWidget:
		point_label = self._director.current_command._point_to_plot_label
		ranks_df = self._director.similarities_active.ranks_df
		ndyad = self._director.similarities_active.ndyad
		item_names = self._director.similarities_active.item_names
		range_similarities = (
			self._director.similarities_active.range_similarities
		)
		point_size = self._director.common.point_size
		point_index = self._director.current_command._point_to_plot_index

		x_others, y_others, label_others, index_others = (
			self._extract_dyad_data_for_point(
				point_label, ranks_df, range_similarities
			)
		)

		title = "Stress contribution of " + item_names[point_index]
		graphics_layout_widget, plot = self._setup_stress_contribution_plot(
			title, ndyad
		)

		self._add_scatter_points_and_labels(
			plot, x_others, y_others, label_others, point_size
		)

		self._add_stress_contribution_lines(
			plot, x_others, y_others, index_others
		)

		self._director.similarities_active.ranks_df = ranks_df

		return graphics_layout_widget

# ------------------------------------------------------------------------

	def _extract_dyad_data_for_point(
		self, point_label: str, ranks_df: pd.DataFrame,
		range_similarities: range
	) -> tuple[list[int], list[int], list[str], list[int]]:
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

		return x_others, y_others, label_others, index_others

	# ------------------------------------------------------------------------

	def _setup_stress_contribution_plot(
		self, title: str, ndyad: int
	) -> tuple[pg.GraphicsLayoutWidget, pg.PlotItem]:
		pyqtgraph_common = self._director.pyqtgraph_common
		graphics_layout_widget, plot = (
			pyqtgraph_common.begin_pyqtgraph_plot_with_title(title)
		)
		plot.showGrid(x=True, y=True)
		plot.setLabel("bottom", "Similarity Rank", color="k", size="15pt")
		plot.setLabel("left", "Distance Rank", color="k", size="15pt")

		pen = pg.mkPen(color=(255, 0, 0))
		line = pg.PlotDataItem((1, ndyad + 1), (1, ndyad + 1), pen=pen)
		plot.addItem(line)

		return graphics_layout_widget, plot

# ------------------------------------------------------------------------

	def _add_scatter_points_and_labels(
		self, plot: pg.PlotItem, x_others: list[int], y_others: list[int],
		label_others: list[str], point_size: int
	) -> None:
		points = pg.ScatterPlotItem(
			x_others,
			y_others,
			size=point_size,
			pen=pg.mkPen(None),
			symnol="o",
			brush=pg.mkBrush(0, 0, 255, 120),
		)
		plot.addItem(points)

		for i, label in enumerate(label_others):
			a_name = pg.TextItem(
				text=label,
				color=(0, 0, 0),
				anchor=(1.0, 0.0),
			)
			a_name.setPos(x_others[i], y_others[i])
			plot.addItem(a_name)

# ------------------------------------------------------------------------

	def _add_stress_contribution_lines(
		self, plot: pg.PlotItem, x_others: list[int], y_others: list[int],
		index_others: list[int]
	) -> None:
		for i in range(len(x_others)):
			if index_others[i] + 1 == x_others[i]:
				other_line = pg.PlotDataItem(
					[index_others[i] + 1, x_others[i]],
					[index_others[i] + 1, y_others[i]],
					pen=pg.mkPen("b"),
				)
			else:
				difference = index_others[i] + 1 - x_others[i]
				if difference > 0:
					other_line = pg.PlotDataItem(
						[x_others[i], x_others[i]],
						[index_others[i] + difference, y_others[i]],
						pen=pg.mkPen("b"),
					)
				else:
					other_line = pg.PlotDataItem(
						[x_others[i], x_others[i]],
						[index_others[i] + 1 - difference, y_others[i]],
						pen=pg.mkPen("b"),
					)
			plot.addItem(other_line)

	# ------------------------------------------------------------------------

	def request_scree_plot_for_tabs_using_pyqtgraph(self) -> None:
		title = "Request Scree Plot for Plot and Gallery using PyQtGraph"
		message = "Must be created"
		raise UnderDevelopmentError(title, message)

		return

	# ------------------------------------------------------------------------

	def request_second_plot_for_tabs_using_pyqtgraph(self) -> None:
		director = self._director
		common = director.common
		pyqtgraph_common = director.pyqtgraph_common
		configuration_active = director.configuration_active
		point_coords = configuration_active.point_coords

		second_dim_groups_to_show = (
			director.current_command._second_dim_groups_to_show
		)

		common.set_axis_extremes_based_on_coordinates(point_coords)

		tab_plot_widget = self._plot_second_using_pyqtgraph(
			second_dim_groups_to_show
		)
		tab_gallery_widget = self._plot_second_using_pyqtgraph(
			second_dim_groups_to_show
		)

		pyqtgraph_common.plot_to_gui_using_pyqtgraph(
			tab_plot_widget, tab_gallery_widget
		)

		return

	# --------------------------------------------------------------------

	def _plot_second_using_pyqtgraph(
		self, second_dim_groups_to_show: str
	) -> pg.GraphicsLayoutWidget:
		director = self._director
		pyqtgraph_common = director.pyqtgraph_common
		pyqtgraph_plotter = director.pyqtgraph_plotter
		configuration_active = director.configuration_active

		graphics_layout_widget, plot = (
			pyqtgraph_common.begin_pyqtgraph_plot_with_title(
				"Second Dimension Supporters"
			)
		)
		plot = pyqtgraph_common.set_aspect_and_grid_in_pyqtgraph_plot(plot)

		pyqtgraph_common.add_axes_labels_to_pyqtgraph_plot(plot)
		pyqtgraph_common.set_ranges_for_pyqtgraph_plot(plot)
		pyqtgraph_common.add_reference_points_to_pyqtgraph_plot(plot)
		pyqtgraph_common.add_connector_to_pyqtgraph_plot(plot)

		second_dim_people_points = (
			configuration_active._populate_second_dim_groups_to_show(
				second_dim_groups_to_show
			)
		)
		pyqtgraph_plotter._fill_second_dim_regions_in_pyqtgraph_plot(
			plot, second_dim_people_points
		)

		director.set_focus_on_tab("Plot")

		return graphics_layout_widget

	# ------------------------------------------------------------------------

	def _fill_second_dim_regions_in_pyqtgraph_plot(
		self, plot: pg.PlotItem, second_dim_people_points: PeoplePoints
	) -> None:
		director = self._director
		common = director.common
		rivalry = director.rivalry
		second_up = rivalry.second_up
		second_down = rivalry.second_down
		scores_active = director.scores_active
		score_color = scores_active.score_color
		point_size = common.point_size

		second_up_region = QtGui.QPainterPath()
		second_up_region.moveTo(second_up._x[0], second_up._y[0])
		for x_, y_ in zip(second_up._x[1:], second_up._y[1:], strict=True):
			second_up_region.lineTo(x_, y_)
		second_up_region_item = QtWidgets.QGraphicsPathItem(second_up_region)
		second_up_brush = QtGui.QBrush(QtGui.QColor(second_up._fill))
		second_up_region_item.setBrush(second_up_brush)
		second_up_region_item.setPen(pg.mkPen(color=(0, 0, 0), width=2))
		plot.addItem(second_up_region_item)
		second_down_region = QtGui.QPainterPath()
		second_down_region.moveTo(second_down._x[0], second_down._y[0])
		for x_, y_ in zip(second_down._x[1:], second_down._y[1:], strict=True):
			second_down_region.lineTo(x_, y_)
		second_down_region_item = QtWidgets.QGraphicsPathItem(
			second_down_region
		)
		second_down_brush = QtGui.QBrush(QtGui.QColor(second_down._fill))
		second_down_region_item.setBrush(second_down_brush)
		second_down_region_item.setPen(pg.mkPen(color=(0, 0, 0), width=2))
		plot.addItem(second_down_region_item)
		points = plot.scatterPlot(
			x=second_dim_people_points.x,
			y=second_dim_people_points.y,
			pen=score_color,
			symbol="o",
			size=point_size,
		)
		plot.addItem(points)

		return

	# ---------------------------------------------------------------------**--

	def request_target_plot_for_tabs_using_pyqtgraph(self) -> None:
		director = self._director
		common = director.common
		pyqtgraph_common = director.pyqtgraph_common
		target_active = director.target_active
		point_coords = target_active.point_coords

		common.set_axis_extremes_based_on_coordinates(point_coords)
		tab_plot_widget = self.plot_target_using_pyqtgraph()
		tab_gallery_widget = self.plot_target_using_pyqtgraph()

		pyqtgraph_common.plot_to_gui_using_pyqtgraph(
			tab_plot_widget, tab_gallery_widget
		)

		return

	# ------------------------------------------------------------------------

	def plot_target_using_pyqtgraph(self) -> pg.GraphicsLayoutWidget:
		(hor_max, hor_min, vert_max, vert_min) = (
			self._director.common.use_plot_ranges()
		)

		director = self._director
		pyqtgraph_common = director.pyqtgraph_common
		target_active = director.target_active
		hor_dim = target_active._hor_dim
		vert_dim = target_active._vert_dim
		dim_names = target_active.dim_names
		point_labels = target_active.point_labels
		range_points = target_active.range_points
		point_coords = target_active.point_coords
		point_size = director.common.point_size
		ndim = target_active.ndim

		if ndim > MAXIMUM_NUMBER_OF_DIMENSIONS_FOR_PLOTTING:
			director.set_focus_on_tab("Output")
			return None

		graphics_layout_widget, plot = (
			pyqtgraph_common.begin_pyqtgraph_plot_with_title(None)
		)
		plot = pyqtgraph_common.set_aspect_and_grid_in_pyqtgraph_plot(plot)

		x = [
			point_coords.iloc[each_point, hor_dim]
			for each_point in range_points
		]
		y = [
			point_coords.iloc[each_point, vert_dim]
			for each_point in range_points
		]
		plot.setLabel("left", dim_names[vert_dim], color="k", size="15pt")
		plot.setLabel("bottom", dim_names[hor_dim], color="k", size="15pt")
		plot.setXRange(hor_max, hor_min, padding=None)
		plot.setYRange(vert_min, vert_max, padding=None)
		for each_label in range_points:
			a_label = pg.TextItem(
				text=point_labels[each_label],
				color="k",
				anchor=(0.5, 1),
				border="w",
				fill=None,
			)
			a_label.setPos(x[each_label], y[each_label])
			plot.addItem(a_label)
		pen = pg.mkPen(color=(255, 0, 0))
		plot.scatterPlot(
			x, y, pen=pen, symbol="o", symbolSize=point_size, symbolBrush="k"
		)

		director.set_focus_on_tab("Plot")

		return graphics_layout_widget

	# ------------------------------------------------------------------------

	def request_uncertainty_plot_for_tabs_using_pyqtgraph(self) -> None:
		director = self._director
		common = director.common
		pyqtgraph_common = director.pyqtgraph_common
		uncertainty_active = director.uncertainty_active

		common.set_axis_extremes_based_on_coordinates(
			uncertainty_active.solutions
		)
		tab_plot_widget = self.plot_uncertainty_using_pyqtgraph()
		tab_gallery_widget = self.plot_uncertainty_using_pyqtgraph()

		pyqtgraph_common.plot_to_gui_using_pyqtgraph(
			tab_plot_widget, tab_gallery_widget
		)

		return

	# ------------------------------------------------------------------------

	def plot_uncertainty_using_pyqtgraph(self) -> pg.GraphicsLayoutWidget:
		director = self._director
		common = director.common
		uncertainty_active = director.uncertainty_active
		range_points = uncertainty_active.range_points
		npoint = uncertainty_active.npoints
		solutions = uncertainty_active.solutions

		result = self._initialize_uncertainty_plot()
		if result is None:
			return None
		graphics_layout_widget, plot = result

		for each_point in range_points:
			x_coords, y_coords = self._extract_point_coordinates(
				solutions, each_point, npoint
			)
			x_mean, y_mean = common.solutions_means(each_point)

			self._add_point_scatter_and_label(
				plot, each_point, x_coords, y_coords, x_mean, y_mean
			)
			self._add_ellipse_mode_pyqtgraph(
				plot, x_coords, y_coords, x_mean, y_mean
			)

		director.set_focus_on_tab("Plot")

		return graphics_layout_widget

# ------------------------------------------------------------------------

	def _initialize_uncertainty_plot(
		self,
	) -> tuple[pg.GraphicsLayoutWidget, pg.PlotItem] | None:
		"""Initialize the uncertainty plot with title and labels."""
		director = self._director
		common = director.common
		pyqtgraph_common = director.pyqtgraph_common
		uncertainty_active = director.uncertainty_active
		hor_dim = common.hor_dim
		vert_dim = common.vert_dim
		dim_names = uncertainty_active.dim_names
		ndim = uncertainty_active.ndim

		if ndim > MAXIMUM_NUMBER_OF_DIMENSIONS_FOR_PLOTTING:
			director.set_focus_on_tab("Output")
			return None

		graphics_layout_widget, plot = (
			pyqtgraph_common.begin_pyqtgraph_plot_with_title("Uncertainty")
		)
		plot = pyqtgraph_common.set_aspect_and_grid_in_pyqtgraph_plot(plot)
		plot.setLabel("left", dim_names[vert_dim], color="k", size="15pt")
		plot.setLabel("bottom", dim_names[hor_dim], color="k", size="15pt")
		pyqtgraph_common.set_ranges_for_pyqtgraph_plot(plot)

		return graphics_layout_widget, plot

# ------------------------------------------------------------------------

	def _extract_point_coordinates(
		self, solutions: pd.DataFrame, each_point: int, npoint: int
	) -> tuple[np.ndarray, np.ndarray]:
		"""Extract x and y coordinates for a point across repetitions."""
		point_coordinates_for_repetition = solutions.iloc[each_point::npoint]
		x_coords = point_coordinates_for_repetition.iloc[:, 0].to_numpy()
		y_coords = point_coordinates_for_repetition.iloc[:, 1].to_numpy()
		return x_coords, y_coords

	# ------------------------------------------------------------------------

	def request_spatial_uncertainty_plot_for_tabs_using_pyqtgraph(self) \
		-> None:
		director = self._director
		common = director.common
		pyqtgraph_common = director.pyqtgraph_common
		uncertainty_active = director.uncertainty_active

		common.set_axis_extremes_based_on_coordinates(
			uncertainty_active.solutions
		)
		tab_plot_widget = self.plot_spatial_uncertainty_using_pyqtgraph()
		tab_gallery_widget = self.plot_spatial_uncertainty_using_pyqtgraph()

		pyqtgraph_common.plot_to_gui_using_pyqtgraph(
			tab_plot_widget, tab_gallery_widget
		)

		return

	# ------------------------------------------------------------------------

	def plot_spatial_uncertainty_using_pyqtgraph(
		self,
	) -> pg.GraphicsLayoutWidget:
		director = self._director
		common = director.common
		pyqtgraph_common = director.pyqtgraph_common
		uncertainty_active = director.uncertainty_active
		range_points = uncertainty_active.range_points
		npoint = uncertainty_active.npoints
		solutions = uncertainty_active.solutions

		result = self._initialize_spatial_uncertainty_plot()
		if result is None:
			return None
		graphics_layout_widget, plot = result

		plot_to_show = getattr(director, "plot_to_show", "ellipses")

		for each_point in range_points:
			point_coordinates_for_repetition = solutions.iloc[
				each_point::npoint
			]
			x_coords = point_coordinates_for_repetition.iloc[:, 0].to_numpy()
			y_coords = point_coordinates_for_repetition.iloc[:, 1].to_numpy()
			x_mean, y_mean = common.solutions_means(each_point)

			self._add_point_scatter_and_label(
				plot, each_point, x_coords, y_coords, x_mean, y_mean
			)

			match plot_to_show:
				case "ellipses":
					pyqtgraph_common.add_ellipse_mode_pyqtgraph(
						plot, x_coords, y_coords, x_mean, y_mean
					)
				case "boxes":
					pyqtgraph_common.add_box_mode_pyqtgraph(plot, each_point)
				case "lines":
					pyqtgraph_common.add_lines_mode_pyqtgraph(
						plot, each_point, x_mean, y_mean
					)
				case "circles":
					pyqtgraph_common.add_circles_mode_pyqtgraph(
						plot, each_point, x_mean, y_mean
					)

		director.set_focus_on_tab("Plot")

		return graphics_layout_widget
	
	# ------------------------------------------------------------------------

	def _initialize_spatial_uncertainty_plot(
		self,
	) -> tuple[pg.GraphicsLayoutWidget, pg.PlotItem] | None:
		"""Initialize the spatial uncertainty plot with title and labels."""
		director = self._director
		common = director.common
		pyqtgraph_common = director.pyqtgraph_common
		uncertainty_active = director.uncertainty_active
		hor_dim = common.hor_dim
		vert_dim = common.vert_dim
		dim_names = uncertainty_active.dim_names
		ndim = uncertainty_active.ndim

		if ndim > MAXIMUM_NUMBER_OF_DIMENSIONS_FOR_PLOTTING:
			director.set_focus_on_tab("Output")
			return None

		title = "Uncertainty"
		graphics_layout_widget, plot = (
			pyqtgraph_common.begin_pyqtgraph_plot_with_title(title)
		)
		plot = pyqtgraph_common.set_aspect_and_grid_in_pyqtgraph_plot(plot)
		plot.setLabel("left", dim_names[vert_dim], color="k", size="15pt")
		plot.setLabel("bottom", dim_names[hor_dim], color="k", size="15pt")
		pyqtgraph_common.set_ranges_for_pyqtgraph_plot(plot)

		return graphics_layout_widget, plot

# ------------------------------------------------------------------------

	def _add_point_scatter_and_label(
		self,
		plot: pg.PlotItem,
		each_point: int,
		x_coords: np.ndarray,
		y_coords: np.ndarray,
		x_mean: float,
		y_mean: float,
	) -> None:
		"""Add scatter plot and label for a single point."""
		director = self._director
		common = director.common
		uncertainty_active = director.uncertainty_active
		point_labels = uncertainty_active.point_labels
		point_size = common.point_size

		point_label = pg.TextItem(
			text=point_labels[each_point],
			color="k",
			anchor=(0.5, 0.5),
			border="w",
			fill=None,
		)
		point_label.setPos(x_mean, y_mean)
		plot.addItem(point_label)
		scatter = pg.ScatterPlotItem(
			x=x_coords,
			y=y_coords,
			pen="r",
			symbol="o",
			size=point_size,
			brush="r",
		)
		plot.addItem(scatter)


	# ------------------------------------------------------------------------

	def request_point_uncertainty_plot_for_tabs_using_pyqtgraph(self) -> None:
		director = self._director
		common = director.common
		pyqtgraph_common = director.pyqtgraph_common
		uncertainty_active = director.uncertainty_active

		common.set_axis_extremes_based_on_coordinates(
			uncertainty_active.solutions
		)
		tab_plot_widget = self.plot_point_uncertainty_using_pyqtgraph()
		tab_gallery_widget = self.plot_point_uncertainty_using_pyqtgraph()

		pyqtgraph_common.plot_to_gui_using_pyqtgraph(
			tab_plot_widget, tab_gallery_widget
		)

		return

	# ------------------------------------------------------------------------

	def plot_point_uncertainty_using_pyqtgraph(
		self,
	) -> pg.GraphicsLayoutWidget:
		director = self._director
		common = director.common
		pyqtgraph_common = director.pyqtgraph_common
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
		graphics_layout_widget, plot = (
			pyqtgraph_common.begin_pyqtgraph_plot_with_title(title)
		)
		plot = pyqtgraph_common.set_aspect_and_grid_in_pyqtgraph_plot(plot)
		plot.setLabel("left", dim_names[vert_dim])
		plot.setLabel("bottom", dim_names[hor_dim])
		pyqtgraph_common.set_ranges_for_pyqtgraph_plot(plot)

		for each_point in range_points:
			x_mean, y_mean = common.solutions_means(each_point)
			label_text = pg.TextItem(text=point_labels[each_point], color="k")
			label_text.setPos(x_mean, y_mean)
			plot.addItem(label_text)

		for each_point in selected_point_indices:
			point_coordinates_for_repetition = solutions.iloc[
				each_point::npoint
			]
			x_coords = point_coordinates_for_repetition.iloc[:, 0].to_numpy()
			y_coords = point_coordinates_for_repetition.iloc[:, 1].to_numpy()
			x_mean, y_mean = common.solutions_means(each_point)

			scatter = pg.ScatterPlotItem(
				x_coords, y_coords, size=0.5,
				pen=pg.mkPen("r"), brush=pg.mkBrush("r")
			)
			plot.addItem(scatter)

			match plot_to_show:
				case "ellipses":
					pyqtgraph_common.add_ellipse_mode_pyqtgraph(
						plot, x_coords, y_coords, x_mean, y_mean
					)
				case "boxes":
					pyqtgraph_common.add_box_mode_pyqtgraph(plot, each_point)
				case "lines":
					pyqtgraph_common.add_lines_mode_pyqtgraph(
						plot, each_point, x_mean, y_mean
					)
				case "circles":
					pyqtgraph_common.add_circles_mode_pyqtgraph(
						plot, each_point, x_mean, y_mean
					)

		director.set_focus_on_tab("Plot")
		return graphics_layout_widget


	# ------------------------------------------------------------------------

	def request_vectors_plot_for_tabs_using_pyqtgraph(self) -> None:
		director = self._director
		pyqtgraph_common = director.pyqtgraph_common
		configuration_active = director.configuration_active
		point_coords = configuration_active.point_coords

		pyqtgraph_common.set_axis_extremes_based_on_coordinates(point_coords)
		tab_plot_widget = self._plot_vectors_using_pyqtgraph()
		tab_gallery_widget = self._plot_vectors_using_pyqtgraph()

		pyqtgraph_common.plot_to_gui_using_pyqtgraph(
			tab_plot_widget, tab_gallery_widget
		)

		return

	# -------------------------------------------------------------------------

	def _plot_vectors_using_pyqtgraph(self) -> pg.GraphicsLayoutWidget:
		director = self._director
		pyqtgraph_common = director.pyqtgraph_common
		configuration_active = director.configuration_active
		point_coords = self.point_coords
		range_points = self.range_points
		ndim = configuration_active.ndim

		if ndim > MAXIMUM_NUMBER_OF_DIMENSIONS_FOR_PLOTTING:
			director.set_focus_on_tab("Output")
			return None

		graphics_layout_widget, plot = (
			pyqtgraph_common.begin_pyqtgraph_plot_with_title(None)
		)
		plot = pyqtgraph_common.set_aspect_and_grid_in_pyqtgraph_plot(plot)
		pyqtgraph_common.add_axes_labels_to_pyqtgraph_plot(plot)
		pyqtgraph_common.set_ranges_for_pyqtgraph_plot(plot)
		pyqtgraph_common.add_configuration_to_pyqtgraph_plot(plot)
		for each_point in range_points:
			x = point_coords.iloc[each_point][0]
			y = point_coords.iloc[each_point][1]
			arrow_len = 20  # adjust the size of the arrow (
			# to indicate relative vector magnitude if necessary)
			line_pen = pg.mkPen("r", width=3)
			line = pg.PlotDataItem([0, x], [0, y], pen=line_pen)
			plot.addItem(line)
			angle = -np.degrees(np.arctan2(y, x)) + 180
			arrow = pg.ArrowItem(
				pos=(x, y),
				angle=angle,
				headLen=arrow_len,
				tipAngle=30,
				baseAngle=0,
				brush="r",
			)
			plot.addItem(arrow)

		director.set_focus_on_tab("Plot")

		return graphics_layout_widget

	# ------------------------------------------------------------------------

	def request_view_custom_plot_for_tabs_using_pyqtgraph(self) -> None:
		title = "Request Custom Plot for Plot and Gallery using PyQtGraph"
		message = "Must be created"
		raise UnderDevelopmentError(title, message)

		return

	# ------------------------------------------------------------------------

	def _plot_custom_using_pyqtgraph(self) -> None:
		title: str = "Plot Custom using pyqtgraph"
		message: str = "Must be created"

		raise UnderDevelopmentError(title, message)
