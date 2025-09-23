from __future__ import annotations

import math
from matplotlib import pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib import transforms
from matplotlib.patches import Ellipse
import numpy as np
from PySide6.QtWidgets import QSizePolicy, QSpacerItem

from typing import TYPE_CHECKING

if TYPE_CHECKING:
	from director import Status

from exceptions import SelectionError

# ------------------------------------------------------------------------


class MatplotlibCommon:
	def __init__(self, director: Status) -> None:
		from director import Status  # noqa: PLC0415, F401

		self._director = director


	# ------------------------------------------------------------------------

	def begin_matplotlib_plot_with_title(
		self, title: str
	) -> tuple[plt.Figure, plt.Axes]:
		fig, ax = plt.subplots()
		ax.set_title(title)
		return fig, ax

	# ------------------------------------------------------------------------

	def begin_matplotlib_heatmap_with_title(
		self, title: str
	) -> tuple[plt.Figure, plt.Axes]:
		fig = plt.gcf()
		ax = fig.add_subplot(111)
		ax.set_title(title)

		return fig, ax

	# ------------------------------------------------------------------------

	def set_aspect_and_grid_in_matplotlib_plot(self, ax: plt.Axes) -> plt.Axes:
		ax.set_aspect("equal")
		ax.grid(False)  # noqa: FBT003

		return ax

	# ------------------------------------------------------------------------

	def add_axes_labels_to_matplotlib_plot(self, ax: plt.Axes) -> plt.Axes:
		director = self._director
		hor_dim = director.common.hor_dim
		vert_dim = director.common.vert_dim
		if self._director.common.have_active_configuration():
			dim_names = director.configuration_active.dim_names
		else:
			dim_names = director.scores_active.dim_names

		ax.set_xlabel(dim_names[hor_dim])
		ax.set_ylabel(dim_names[vert_dim])

		return ax

	# ------------------------------------------------------------------------

	def add_axes_names_to_matplotlib_heatmap(
		self, ax: plt.Axes, name: str
	) -> plt.Axes:
		ax.set_xlabel(name)
		ax.set_ylabel(name)

		return ax

	# ------------------------------------------------------------------------

	def add_tick_names_and_labels_to_matplotlib_heatmap(
		self, ax: plt.Axes, tick_names: list[str], tick_labels: list[str]
	) -> plt.Axes:
		tick_range = range(len(tick_names))
		ax.set_xticks(tick_range)
		ax.set_xticklabels(tick_labels, rotation=45)
		ax.set_yticks(tick_range)
		ax.set_yticklabels(tick_names)

		return ax

	# -----------------------------------------------------------------------

	def add_heatmap_to_matplotlib_heatmap(
		self, ax: plt.Axes, data: np.ndarray, shading: str
	) -> plt.Axes:
		im = ax.imshow(data, cmap=shading, interpolation="none")

		return im

	# -----------------------------------------------------------------------

	def add_colorbar_to_matplotlib_heatmap(
		self, fig: plt.Figure, ax: plt.Axes, im: plt.AxesImage
	) -> None:
		fig.colorbar(im, ax=ax)
		return

	# -----------------------------------------------------------------------

	def create_heatmap_using_matplotlib(
		self,
		title: str,
		data: np.ndarray,
		shading: str,
		names: list[str],
		labels: list[str],
		axes_names: str,
	) -> plt.Figure:
		fig, ax = self.begin_matplotlib_heatmap_with_title(title)
		im = self.add_heatmap_to_matplotlib_heatmap(ax, data, shading)
		self.add_colorbar_to_matplotlib_heatmap(fig, ax, im)
		self.add_tick_names_and_labels_to_matplotlib_heatmap(ax, names, labels)
		self.add_axes_names_to_matplotlib_heatmap(ax, axes_names)

		return fig

	# ------------------------------------------------------------------------

	def add_configuration_to_matplotlib_plot(self, ax: plt.Axes) -> None:
		hor_dim = self._director.common.hor_dim
		vert_dim = self._director.common.vert_dim
		point_coords = self._director.configuration_active.point_coords
		point_names = self._director.configuration_active.point_names
		offset = self._director.common.plot_ranges.offset
		range_points = self._director.configuration_active.range_points

		# conf = self._director.configuration_active.config_as_itemframe
		# conf = self._director.configuration_active.point_coords
		# peek("\nIn add_configuration_to_matplotlib_plot"
		# 	f"\n conf = {conf}")

		x_coords = []
		y_coords = []
		for each_point in range_points:
			x_coords.append(point_coords.iloc[each_point, hor_dim])
			y_coords.append(point_coords.iloc[each_point, vert_dim])
			ax.text(
				# conf.dim_1_coords[each_point] + offset,
				# conf.dim_2_coords[each_point],
				# conf.item(each_point).label)
				point_coords.iloc[each_point, hor_dim] + offset,
				point_coords.iloc[each_point, vert_dim],
				point_names[each_point],
			)

		# x_coords = conf.dim_1_coords
		# y_coords = conf.dim_2_coords
		# rep = RepresentationOfPoints(conf, color="black", marker='o')
		# ax.scatter(x_coords, y_coords, color=rep.color, marker=rep.marker)

		ax.scatter(x_coords, y_coords, color="black", marker="o", s=3)

		return

	# ------------------------------------------------------------------------

	def set_ranges_for_matplotlib_plot(self, ax: plt.Axes) -> None:
		"""Set axis limits for a matplotlib plot.

		Args:
			ax: The matplotlib Axes object to configure
		"""
		(hor_max, hor_min, vert_max, vert_min) = (
			self._director.common.use_plot_ranges()
		)

		ax.axis([hor_min, hor_max, vert_min, vert_max])

		return

	# ------------------------------------------------------------------------

	def _plot_scree_using_matplotlib(self) -> plt.Figure:
		use_metric = self._use_metric
		min_stress = self._min_stress

		fig, ax = self._director.common.begin_matplotlib_plot_with_title(
			"Scree Diagram"
		)
		if not use_metric:
			ax = self._director.common.set_aspect_and_grid_in_matplotlib_plot(
				ax
			)
		ax.set_xlabel("Number of Dimensions")
		ax.set_ylabel("Stress")
		x_coords = min_stress["Dimensionality"].tolist()
		y_coords = min_stress["Best Stress"].tolist()
		ax.plot(x_coords, y_coords)
		if use_metric:
			max_stress = max(y_coords)
			show_max_stress = math.ceil(max_stress)
			ax.axis([1, 10, 0, show_max_stress])
		else:
			show_min_stress = int(min_stress.iloc[0, 1] + 2)
			ax.axis([1, 10, 0, show_min_stress])
		return fig

	# --------------------------------------------------------------------

	def plot_shep_using_matplotlib(self) -> plt.Figure:
		shepard_axis = self.shepard_axis
		distances_as_list = (
			self._director.configuration_active.distances_as_list
		)
		similarities_as_list = (
			self._director.similarities_active.similarities_as_list
		)
		range_similarities = (
			self._director.similarities_active.range_similarities
		)
		ndyad = self._director.similarities_active.ndyad
		ranks_df = self._director.similarities_active.ranks_df
		command = self._director.command

		fig, ax = self._director.common.begin_matplotlib_plot_with_title(
			"Shepard Diagram"
		)
		if shepard_axis == "Y":
			# if self._director.current_command.shepard_axis == 'Y':
			hor_max = max(distances_as_list)
			hor_min = min(distances_as_list)
			vert_max = max(similarities_as_list)
			vert_min = min(similarities_as_list)
			#
			ax.set_xlabel("Distance")
			ax.set_ylabel("Similarity")
			#
			for each_dyad in range_similarities:
				if each_dyad != ndyad - 1:
					ax.plot(
						(
							ranks_df.loc[each_dyad, "Distance_AB"],
							ranks_df.loc[each_dyad + 1, "Distance_AB"],
						),
						(
							ranks_df.loc[each_dyad, "Similarity"],
							ranks_df.loc[each_dyad + 1, "Similarity"],
						),
						color="k",
					)
		elif shepard_axis == "X":
			# elif self._director.current_command.shepard_axis == "X":
			vert_max = max(distances_as_list)
			vert_min = min(distances_as_list)
			hor_max = max(similarities_as_list)
			hor_min = min(similarities_as_list)
			ax.set_ylabel("Distance")
			ax.set_xlabel("Similarity")
			for each_dyad in range_similarities:
				if each_dyad != ndyad - 1:
					ax.plot(
						(
							ranks_df.loc[each_dyad, "Similarity"],
							ranks_df.loc[each_dyad + 1, "Similarity"],
						),
						(
							ranks_df.loc[each_dyad, "Distance_AB"],
							ranks_df.loc[each_dyad + 1, "Distance_AB"],
						),
						color="k",
					)
		else:
			raise SelectionError(command, "No axis selected")
		ax.axis([hor_min, hor_max, vert_min, vert_max])

		self._director.similarities_active.ranks_df = ranks_df

		return fig

	# ------------------------------------------------------------------------

	def request_differences_plot_for_plot_and_gallery_tabs_using_matplotlib(
		self,
	) -> None:
		matplotlib_common = self._director.matplotlib_common

		fig = self._director.current_command.plot_a_heatmap_using_matplotlib()
		matplotlib_common.plot_to_gui_using_matplotlib(fig)
		return

	# ------------------------------------------------------------------------

	def request_scree_plot_for_plot_and_gallery_tabs_using_matplotlib(
		self,
	) -> None:
		matplotlib_common = self._director.matplotlib_common

		fig = self._plot_scree_using_matplotlib()
		matplotlib_common.plot_to_gui_using_matplotlib(fig)
		self._director.set_focus_on_tab("Plot")
		return

	# ------------------------------------------------------------------------

	def request_shepard_plot_for_plot_and_gallery_tabs_using_matplotlib(
		self,
	) -> None:
		matplotlib_common = self._director.matplotlib_common

		fig = self.plot_shep_using_matplotlib()
		matplotlib_common.plot_to_gui_using_matplotlib(fig)
		self._director.set_focus_on_tab("Plot")
		return

	# -- The following comes from rivalry ------------------------------------

	# ------------------------------------------------------------------------

	def add_connector_to_matplotlib_plot(self, ax: plt.Axes) -> None:
		rivalry = self._director.rivalry
		hor_dim = self._director.common.hor_dim
		vert_dim = self._director.common.vert_dim
		point_coords = self._director.configuration_active.point_coords
		rival_a = rivalry.rival_a
		rival_b = rivalry.rival_b

		if self._director.common.show_connector:
			ax.plot(
				[
					point_coords.iloc[rival_a.index, hor_dim],
					point_coords.iloc[rival_b.index, hor_dim],
				],
				[
					point_coords.iloc[rival_a.index, vert_dim],
					point_coords.iloc[rival_b.index, vert_dim],
				],
				color="black",
			)
		return

	# ------------------------------------------------------------------------

	def add_bisector_to_matplotlib_plot(self, ax: plt.Axes) -> None:
		rivalry = self._director.rivalry

		# if self._director.common.have_bisector_info():
		if self._director.common.have_reference_points():
			show_bisector = self._director.common.show_bisector
			start = rivalry.bisector._start
			end = rivalry.bisector._end

			# if show_bisector and self._director.common.have_bisector_info():
			if show_bisector and self._director.common.have_reference_points():
				ax.text(start.x, start.y, "S")
				ax.text(end.x, end.y, "E")
				ax.plot([start.x, end.x], [start.y, end.y])

		return

	# ------------------------------------------------------------------------

	def add_east_to_matplotlib_plot(self, ax: plt.Axes) -> None:
		rivalry = self._director.rivalry
		start = rivalry.east._start
		end = rivalry.east._end

		ax.plot([start.x, end.x], [start.y, end.y])
		ax.text(start.x, start.y, "E_S")
		ax.text(end.x, end.y, "E_E")

		return

	# ------------------------------------------------------------------------

	def add_west_to_matplotlib_plot(self, ax: plt.Axes) -> None:
		rivalry = self._director.rivalry
		start = rivalry.west._start
		end = rivalry.west._end

		ax.plot([start.x, end.x], [start.y, end.y])
		ax.text(start.x, start.y, "W_S")
		ax.text(end.x, end.y, "W_E")

		return

	# ------------------------------------------------------------------------

	def add_first_dim_divider_to_matplotlib_plot(self, ax: plt.Axes) -> None:
		vert_max = self._director.common.plot_ranges.vert_max
		vert_min = self._director.common.plot_ranges.vert_min
		first_div = self._director.rivalry.first_div

		ax.plot([first_div, first_div], [vert_max, vert_min])

		return

	# ------------------------------------------------------------------------

	def add_second_dim_divider_to_matplotlib_plot(self, ax: plt.Axes) -> None:
		hor_max = self._director.common.plot_ranges.hor_max
		hor_min = self._director.common.plot_ranges.hor_min
		second_div = self._director.rivalry.second_div
		ax.plot([hor_max, hor_min], [second_div, second_div])

		return

	# ------------------------------------------------------------------------

	def add_reference_points_to_matplotlib_plot(self, ax: plt.Axes) -> None:
		rivalry = self._director.rivalry
		rival_a = rivalry.rival_a
		rival_b = rivalry.rival_b

		x_coords = []
		y_coords = []

		hor_dim = self._director.common.hor_dim
		vert_dim = self._director.common.vert_dim
		rivalry = self._director.rivalry
		rival_a = rivalry.rival_a
		rival_b = rivalry.rival_b
		point_coords = self._director.configuration_active.point_coords
		# point_labels = self._director.configuration_active.point_labels
		offset = self._director.common.plot_ranges.offset

		if self._director.common.have_reference_points():
			ax.text(
				point_coords.iloc[rival_a.index, hor_dim] + offset,
				point_coords.iloc[rival_a.index, vert_dim],
				rival_a.label,
			)
			ax.text(
				point_coords.iloc[rival_b.index, hor_dim] + offset,
				point_coords.iloc[rival_b.index, vert_dim],
				rival_b.label,
			)
			x_coords.append(point_coords.iloc[rival_a.index, hor_dim])
			y_coords.append(point_coords.iloc[rival_a.index, vert_dim])
			x_coords.append(point_coords.iloc[rival_b.index, hor_dim])
			y_coords.append(point_coords.iloc[rival_b.index, vert_dim])
			#
			ax.scatter(x_coords, y_coords)
		return

	# -- The following comes from director

	# ------------------------------------------------------------------------

	def plot_to_gui_using_matplotlib(self, fig: plt.Figure) -> None:
		# Add the plot to the Plot tab (replace the current plot)
		canvas_plot = FigureCanvas(fig)
		width, height = (
			int(fig.get_size_inches()[0] * fig.dpi),
			int(fig.get_size_inches()[1] * fig.dpi),
		)
		canvas_plot.setFixedSize(width, height)
		canvas_plot.draw()
		self._director.tab_plot_scroll_area.setWidget(canvas_plot)
		# Add the plot to the Gallery tab (append to existing plots)
		canvas_gallery = FigureCanvas(fig)
		canvas_gallery.setFixedSize(width, height)
		canvas_gallery.draw()
		self._director.tab_gallery_layout.addWidget(canvas_gallery)
		# Add a spacer at the end to push plots to the top
		spacer = QSpacerItem(
			20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding
		)
		self._director.tab_gallery_layout.addItem(spacer)
		plt.close(fig)

	# ------------------------------------------------------------------------

	def confidence_ellipse_using_matplotlib(
		self,
		x: list[float],
		y: list[float],
		ax: plt.Axes,
		n_std: float = 3.0,
		facecolor: str = "none",
		**kwargs: str | float,
	) -> Ellipse:
		"""
		Create a plot of the covariance confidence ellipse of *x* and *y*.

		Parameters
		----------
		x, y : array-like, shape (n, )
			Input data.

		ax : matplotlib.axes.Axes
			The Axes object to draw the ellipse into.

		n_std : float
			The number of standard deviations to determine the ellipse's
			radiuses.

		**kwargs
			Forwarded to `~matplotlib.patches.Ellipse`

		Returns
		-------
		matplotlib.patches.Ellipse
		"""

		cov = np.cov(x, y)
		pearson = cov[0, 1] / np.sqrt(cov[0, 0] * cov[1, 1])
		# Using a special case to obtain the eigenvalues of this
		# two-dimensional dataset.
		ell_radius_x = np.sqrt(1 + pearson)
		ell_radius_y = np.sqrt(1 - pearson)
		ellipse = Ellipse(
			(0, 0),
			width=ell_radius_x * 2,
			height=ell_radius_y * 2,
			facecolor=facecolor,
			**kwargs,
		)

		# Calculating the standard deviation of x from
		# the squareroot of the variance and multiplying
		# with the given number of standard deviations.
		scale_x = np.sqrt(cov[0, 0]) * n_std
		mean_x = np.mean(x)

		# calculating the standard deviation of y ...
		scale_y = np.sqrt(cov[1, 1]) * n_std
		mean_y = np.mean(y)

		transf = (
			transforms.Affine2D()
			.rotate_deg(45)
			.scale(scale_x, scale_y)
			.translate(mean_x, mean_y)
		)

		ellipse.set_transform(transf + ax.transData)

		ellipse_patch = ax.add_patch(ellipse)

		return ellipse_patch
