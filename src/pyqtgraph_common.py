from __future__ import annotations

import math
import numpy as np
import pyqtgraph as pg

from typing import TYPE_CHECKING

if TYPE_CHECKING:
	# import numpy as np
	from director import Status
from exceptions import UnderDevelopmentError, SelectionError

from PySide6.QtWidgets import QSizePolicy, QSpacerItem, QVBoxLayout, QWidget


class PyQtGraphCommon:
	def __init__(self, director: Status) -> None:
		from director import Status  # noqa: PLC0415, F401

		self._director = director

	# -- The following code comes from common.py------------------------------

	# ------------------------------------------------------------------------

	def begin_pyqtgraph_plot_with_title(
		self, title: str
	) -> tuple[pg.GraphicsLayoutWidget, pg.PlotItem]:
		graphics_layout_widget = pg.GraphicsLayoutWidget()
		graphics_layout_widget.setBackground("w")
		plot = graphics_layout_widget.addPlot(
			title=title, color="k", size="25pt"
		)
		return graphics_layout_widget, plot

	# ------------------------------------------------------------------------

	def begin_pyqtgraph_heatmap_with_title(
		self, title: str
	) -> tuple[pg.GraphicsLayoutWidget, pg.PlotItem]:
		graphics_layout_widget = pg.GraphicsLayoutWidget()
		graphics_layout_widget.setBackground("w")
		plot_item = graphics_layout_widget.addPlot(title=title)
		plot_item.getViewBox().setDefaultPadding(0)

		return graphics_layout_widget, plot_item

	# ------------------------------------------------------------------------

	def set_aspect_and_grid_in_pyqtgraph_plot(
		self, plot: pg.PlotItem
	) -> pg.PlotItem:
		plot.setAspectLocked(True, ratio=1)
		plot.showGrid(x=True, y=True)
		return plot

	# ------------------------------------------------------------------------

	def add_axes_labels_to_pyqtgraph_plot(
		self, plot: pg.PlotItem
	) -> pg.PlotItem:
		hor_dim = self._director.common.hor_dim
		vert_dim = self._director.common.vert_dim
		dim_names = self._director.configuration_active.dim_names

		plot.setLabel("bottom", dim_names[hor_dim], color="k", size="15pt")
		plot.setLabel("left", dim_names[vert_dim], color="k", size="15pt")

		return

	# ------------------------------------------------------------------------

	def add_axes_names_to_pyqtgraph_heatmap(
		self, plot: pg.PlotItem, name: str
	) -> pg.PlotItem:
		plot.setLabel("bottom", name, color="k", size="15pt")
		plot.setLabel("left", name, color="k", size="15pt")

		return plot

	# ------------------------------------------------------------------------

	def add_tick_marks_names_and_labels_to_pyqtgraph_heatmap(
		self, plot: pg.PlotItem, tick_names: list[str], tick_labels: list[str]
	) -> pg.PlotItem:
		nsize = len(tick_names)
		tick_range = list(range(nsize))

		# Set up axes with proper spacing for labels
		x_axis = plot.getAxis("bottom")
		y_axis = plot.getAxis("left")
		x_axis.setHeight(80)  # More space for labels

		# Create tick lists - reverse left ticks to match flipped data
		bottom_ticks = list(zip(tick_range, tick_labels, strict=True))
		left_ticks = list(
			zip(tick_range, list(reversed(tick_names)), strict=True)
		)

		# Set ticks
		x_axis.setTicks([bottom_ticks])
		y_axis.setTicks([left_ticks])

		# Set view range to show the matrix properly
		plot.getViewBox().setRange(
			xRange=(-0.5, nsize - 0.5), yRange=(-0.5, nsize - 0.5)
		)

		return plot

	# -----------------------------------------------------------------------

	def add_heatmap_to_pyqtgraph_heatmap(
		self, plot: pg.PlotItem, data: np.ndarray, shading: str
	) -> pg.ImageItem:
		im = pg.ImageItem()

		# Map matplotlib colormap names to pyqtgraph colormaps
		colormap_mapping = {
			"binary": "gist_yarg",
			"binary_r": "gist_gray",
			"viridis": "viridis",
			"plasma": "plasma",
			"inferno": "inferno",
			"magma": "magma",
			"cividis": "CET-C6",
			"hot": "hot",
			"cool": "cool",
			"spring": "spring",
			"summer": "summer",
			"autumn": "autumn",
			"winter": "winter",
			"gist_gray": "CET-L1",
			"gist_yarg": "CET-L1_r",
		}

		# Use the mapped colormap or try matplotlib directly
		pg_colormap_name = colormap_mapping.get(shading, shading)

		# Check if we need to reverse the colormap
		reverse_colormap = pg_colormap_name.endswith("_r")
		if reverse_colormap:
			pg_colormap_name = pg_colormap_name[:-2]  # Remove '_r' suffix

		try:
			# Try to get pyqtgraph native colormap first
			colormap = pg.colormap.get(pg_colormap_name)
			if reverse_colormap:
				colormap = colormap.reverse()
			im.setColorMap(colormap)
		except Exception:
			try:
				# If native colormap fails, try matplotlib colormap
				colormap = pg.colormap.getFromMatplotlib(shading)
				im.setColorMap(colormap)
			except Exception:
				# Final fallback to default colormap
				colormap = pg.colormap.get("viridis")
				im.setColorMap(colormap)

		# Set image data first before setting rectangle
		# Flip data vertically before setting image
		data = np.flipud(data)
		data = data.T
		im.setImage(data, autoLevels=True, autoDownsample=True)

		# Now set the image rectangle to position matrix correctly
		nsize = data.shape[0]
		im.setRect(pg.QtCore.QRectF(-0.5, -0.5, nsize, nsize))
		plot.addItem(im)

		return im

	# -----------------------------------------------------------------------

	def add_colorbar_to_pyqtgraph_heatmap(
		self,
		graphics_layout: pg.GraphicsLayoutWidget,
		plot: pg.PlotItem,
		im: pg.ImageItem,
	) -> None:
		# Handle NaN values in image data
		image_data = im.image
		if np.isnan(image_data).all():
			# If all values are NaN, use default range
			min_val, max_val = 0.0, 1.0
		else:
			# Use nanmin/nanmax to ignore NaN values
			min_val = np.nanmin(image_data)
			max_val = np.nanmax(image_data)

			# If min and max are the same, create a small range
			if min_val == max_val:
				if min_val == 0:
					min_val, max_val = 0.0, 1.0
				else:
					range_val = abs(min_val) * 0.01
					min_val -= range_val
					max_val += range_val

		colorbar = pg.ColorBarItem(
			values=(min_val, max_val), colorMap=im.getColorMap()
		)
		# Use setImageItem with insert_in parameter to properly align
		# with data area
		colorbar.setImageItem(im, insert_in=plot)

		return

	# -----------------------------------------------------------------------

	def create_heatmap_using_pyqtgraph(  # noqa: PLR0913
		self,
		title: str,
		data: np.ndarray | list[list[float]],
		shading: str,
		names: list[str],
		labels: list[str],
		axes_names: str,
	) -> pg.GraphicsLayoutWidget:
		# Use the full square matrix without any masking
		data_to_plot = np.array(data, dtype=float)

		graphics_layout, plot = self.begin_pyqtgraph_heatmap_with_title(title)
		im = self.add_heatmap_to_pyqtgraph_heatmap(plot, data_to_plot, shading)
		self.add_colorbar_to_pyqtgraph_heatmap(graphics_layout, plot, im)
		# Use original names to match the unflipped data
		self.add_tick_marks_names_and_labels_to_pyqtgraph_heatmap(
			plot, names, labels
		)
		self.add_axes_names_to_pyqtgraph_heatmap(plot, axes_names)

		return graphics_layout

	# ------------------------------------------------------------------------

	def add_configuration_to_pyqtgraph_plot(self, plot: pg.PlotItem) -> None:
		director = self._director
		common = director.common
		hor_dim = common.hor_dim
		vert_dim = common.vert_dim
		configuration_active = director.configuration_active
		point_coords = configuration_active.point_coords
		point_labels = configuration_active.point_labels
		range_points = configuration_active.range_points
		point_size = common.point_size

		# conf = self._director.configuration_active.config_as_itemframe

		x_coords = []
		y_coords = []
		for each_point in range_points:
			x_coords.append(point_coords.iloc[each_point, hor_dim])
			y_coords.append(point_coords.iloc[each_point, vert_dim])
			# a_label = pg.TextItem(
			# 	text=conf.item(each_point).label,
			# 	color="k", border='w', fill=None)
			# a_label.setPos(
			# 	conf.dim_1_coords[each_point],
			# 	conf.dim_2_coords[each_point])
			# plot.addItem(a_label)

			a_label = pg.TextItem(
				text=point_labels[each_point], color="k", border="w", fill=None
			)
			a_label.setPos(
				point_coords.iloc[each_point, hor_dim],
				point_coords.iloc[each_point, vert_dim],
			)
			plot.addItem(a_label)
		pen = pg.mkPen(color="black")

		# x_coords = conf.dim_1_coords
		# y_coords = conf.dim_2_coords
		# rep = RepresentationOfPoints(conf, color=pg.mkPen(color="black"),
		# 	marker='o', size=7)
		# plot.scatterPlot(
		# 	x_coords, y_coords, pen=rep.color, symbol=rep.marker,
		# 	symbolSize=rep.size)
		plot.scatterPlot(
			x_coords,
			y_coords,
			pen=pen,
			symbol="o",
			symbolSize=point_size,
			symbolBrush="k",
		)  # size had been 5
		return

	# ------------------------------------------------------------------------

	def set_ranges_for_pyqtgraph_plot(self, plot: pg.PlotItem) -> None:
		(hor_max, hor_min, vert_max, vert_min) = (
			self._director.common.use_plot_ranges()
		)

		# Validate range values to prevent NaN errors in PyQtGraph
		if (
			np.isnan(hor_min)
			or np.isnan(hor_max)
			or np.isnan(vert_min)
			or np.isnan(vert_max)
		):
			# Skip setting ranges if any value is NaN
			return

		# Set ranges to match matplotlib coordinate system
		plot.setXRange(hor_min, hor_max, padding=None)
		plot.setYRange(vert_min, vert_max, padding=None)

		return

	# ------------------------------------------------------------------------

	def _plot_scree_using_pyqtgraph(self) -> pg.GraphicsLayoutWidget:
		use_metric = self._use_metric
		min_stress = self._min_stress

		graphics_layout_widget, plot = (
			self._director.pyqtgraph_common.begin_pyqtgraph_plot_with_title(
				"Scree Diagram"
			)
		)
		plot.showGrid(x=True, y=True)
		# plot.setAspectLocked(True, ratio=1) <<< this caused problems
		plot.setLabel("bottom", "Number of Dimensions", color="k", size="15pt")
		plot.setLabel("left", "Stress", color="k", size="15pt")

		pen = pg.mkPen(color=(255, 0, 0))
		x_coords = min_stress["Dimensionality"].tolist()
		y_coords = min_stress["Best Stress"].tolist()
		plot.setXRange(1, 10, padding=None)
		if use_metric:
			max_stress = max(y_coords)
			show_max_stress = math.ceil(max_stress)
			plot.disableAutoRange("xy")
			plot.setYRange(1, show_max_stress, padding=0)
		else:
			# show_min_stress = int(min_stress.iloc[0, 1] + 2)
			# show_min_stress = max(y_coords)
			# ax.axis([1, 10, 0, show_min_stress])
			plot.disableAutoRange("xy")
			# plot.setYRange(0, show_min_stress, padding=0)
			plot.setYRange(0, 1, padding=0)
			# plot.setYRange(0, 1, padding=0)
			# y_range = plot.viewRange()[1]

		line = pg.PlotDataItem(x_coords, y_coords, pen=pen)
		plot.addItem(line)
		# y2_range = plot.viewRange()[1]

		return graphics_layout_widget

	# -----------------------------------------------------------------------

	def plot_shep_using_pyqtgraph(self) -> pg.GraphicsLayoutWidget:
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
		shepard_axis = self.shepard_axis
		command = self._director.command

		x_coords = []
		y_coords = []
		graphics_layout_widget, plot = (
			self._director.pyqtgraph_common.begin_pyqtgraph_plot_with_title(
				"Shepard Diagram"
			)
		)
		plot.showGrid(x=True, y=True)
		pen = pg.mkPen(color=(255, 0, 0))
		if shepard_axis == "Y":
			hor_max = max(distances_as_list)
			hor_min = min(distances_as_list)
			vert_max = max(similarities_as_list)
			vert_min = min(similarities_as_list)
			plot.setLabel("bottom", "Distance", color="k", size="15pt")
			plot.setLabel("left", "Similarity", color="k", size="15pt")
			for each_dyad in range_similarities:
				if each_dyad != ndyad - 1:
					x_coords.append(ranks_df.loc[each_dyad, "Distance_AB"])
					y_coords.append(ranks_df.loc[each_dyad, "Similarity"])

		elif shepard_axis == "X":
			# elif self._director.current_command.shepard_axis == "X":
			vert_max = max(distances_as_list)
			vert_min = min(distances_as_list)
			hor_max = max(similarities_as_list)
			hor_min = min(similarities_as_list)
			plot.setLabel("left", "Distance", color="k", size="15pt")
			plot.setLabel("bottom", "Similarity", color="k", size="15pt")
			for each_dyad in range_similarities:
				if each_dyad != ndyad - 1:
					x_coords.append(ranks_df.loc[each_dyad, "Similarity"])
					y_coords.append(ranks_df.loc[each_dyad, "Distance_AB"])
		else:
			raise SelectionError(command, "No axis selected")
		line = pg.PlotDataItem(x_coords, y_coords, pen=pen)
		plot.addItem(line)
		plot.setXRange(hor_min, hor_max)
		plot.setYRange(vert_min, vert_max)
		return graphics_layout_widget

	# ------------------------------------------------------------------------

	def request_differences_plot_for_plot_and_gallery_tabs_using_pyqtgraph(
		self,
	) -> None:
		under_development_error_title = "This method is not yet implemented"
		under_development_error_message = (
			"Consider using the matplotlib version"
		)
		raise UnderDevelopmentError(
			under_development_error_title, under_development_error_message
		)

		return

	# ------------------------------------------------------------------------

	def request_scree_plot_for_plot_and_gallery_tabs_using_pyqtgraph(
		self,
	) -> None:
		pyqtgraph_common = self._director.pyqtgraph_common
		tab_plot_widget = self._plot_scree_using_pyqtgraph()
		tab_gallery_widget = self._plot_scree_using_pyqtgraph()
		pyqtgraph_common.plot_to_gui_using_pyqtgraph(
			tab_plot_widget, tab_gallery_widget
		)
		self._director.set_focus_on_tab("Plot")
		return

	# ------------------------------------------------------------------------

	def request_shepard_plot_for_plot_and_gallery_tabs_using_pyqtgraph(
		self,
	) -> None:
		pyqtgraph_common = self._director.pyqtgraph_common
		tab_plot_widget = self.plot_shep_using_pyqtgraph()
		tab_gallery_widget = self.plot_shep_using_pyqtgraph()
		pyqtgraph_common.plot_to_gui_using_pyqtgraph(
			tab_plot_widget, tab_gallery_widget
		)
		self._director.set_focus_on_tab("Plot")
		return

	# -- The following comes from rivalry -----------------------------------

	# ------------------------------------------------------------------------

	def add_connector_to_pyqtgraph_plot(self, the_plot: pg.PlotItem) -> None:
		hor_dim = self._director.common.hor_dim
		vert_dim = self._director.common.vert_dim
		point_coords = self._director.configuration_active.point_coords
		rivalry = self._director.rivalry
		rival_a = rivalry.rival_a
		rival_b = rivalry.rival_b

		if (
			self._director.common.show_connector
			# and self._director.common.have_bisector_info):
			and self._director.common.have_reference_points()
		):
			the_plot.plot(
				[
					point_coords.iloc[rival_a.index, hor_dim],
					point_coords.iloc[rival_b.index, hor_dim],
				],
				[
					point_coords.iloc[rival_a.index, vert_dim],
					point_coords.iloc[rival_b.index, vert_dim],
				],
				pen="b",
			)
		return

	# ------------------------------------------------------------------------

	def add_bisector_to_pyqtgraph_plot(self, the_plot: pg.PlotItem) -> None:
		# pen: pg.QtGui.QPen) -> None:

		show_bisector = self._director.common.show_bisector
		rivalry = self._director.rivalry

		# if (show_bisector and self._director.common.have_bisector_info()):
		if show_bisector and self._director.common.have_reference_points():
			start = rivalry.bisector._start
			end = rivalry.bisector._end

			start.name = pg.TextItem(
				text="S", color=(0, 0, 0), anchor=(1.0, 0.0)
			)
			start.name.setPos(start.x, start.y)
			the_plot.addItem(start.name)
			end.name = pg.TextItem(
				text="E", color=(0, 0, 0), anchor=(1.0, 0.0)
			)
			end.name.setPos(end.x, end.y)
			the_plot.addItem(end.name)
			the_plot.plot([start.x, end.x], [start.y, end.y])

		return

	# ------------------------------------------------------------------------

	def add_east_to_pyqtgraph_plot(self, the_plot: pg.PlotItem) -> None:
		# pen: pg.QtGui.QPen) -> None:

		rivalry = self._director.rivalry
		start = rivalry.east._start
		end = rivalry.east._end

		start.name = pg.TextItem(
			text="E_S", color=(0, 0, 0), anchor=(1.0, 0.0)
		)
		start.name.setPos(start.x, start.y)
		the_plot.addItem(start.name)
		east_end_name = pg.TextItem(
			text="E_E", color=(0, 0, 0), anchor=(1.0, 0.0)
		)
		east_end_name.setPos(end.x, end.y)
		the_plot.addItem(east_end_name)
		the_plot.plot([start.x, end.x], [start.y, end.y])
		return

	# ------------------------------------------------------------------------
	def add_west_to_pyqtgraph_plot(self, the_plot: pg.PlotItem) -> None:
		# pen: pg.QtGui.QPen) -> None:

		rivalry = self._director.rivalry
		start = rivalry.west._start
		end = rivalry.west._end

		start.name = pg.TextItem(
			text="W_S", color=(0, 0, 0), anchor=(1.0, 0.0)
		)
		start.name.setPos(start.x, start.y)
		the_plot.addItem(start.name)
		end.name = pg.TextItem(text="W_E", color=(0, 0, 0), anchor=(1.0, 0.0))
		end.name.setPos(end.x, end.y)
		the_plot.addItem(end.name)
		the_plot.plot([start.x, end.x], [start.y, end.y])
		return

	# ------------------------------------------------------------------------

	def add_first_dim_divider_to_pyqtgraph_plot(
		self, the_plot: pg.PlotItem
	) -> None:
		# pen: pg.QtGui.QPen) -> None:

		first_div = self._director.rivalry.first_div
		vert_max = self._director.common.plot_ranges.vert_max
		vert_min = self._director.common.plot_ranges.vert_min

		if self._director.common.have_scores():
			the_plot.plot([first_div, first_div], [vert_max, vert_min])
		else:
			the_plot.plot([first_div, first_div], [vert_max, vert_min])
		return

	# ------------------------------------------------------------------------

	def add_second_dim_divider_to_pyqtgraph_plot(
		self, the_plot: pg.PlotItem
	) -> None:
		# pen: pg.QtGui.QPen) -> None:

		hor_max = self._director.common.plot_ranges.hor_max
		hor_min = self._director.common.plot_ranges.hor_min
		second_div = self._director.rivalry.second_div

		if self._director.common.have_scores():
			the_plot.plot([hor_max, hor_min], [second_div, second_div])
		else:
			the_plot.plot([hor_max, hor_min], [second_div, second_div])
		return

	# ------------------------------------------------------------------------

	def add_reference_points_to_pyqtgraph_plot(
		self, plot: pg.PlotItem
	) -> None:
		director = self._director
		common = director.common
		point_size = common.point_size
		configuration_active = director.configuration_active
		hor_dim = common.hor_dim
		vert_dim = common.vert_dim
		rivalry = director.rivalry
		rival_a = rivalry.rival_a
		rival_b = rivalry.rival_b
		point_coords = configuration_active.point_coords
		offset = common.plot_ranges.offset

		x = []
		y = []

		if self._director.common.have_reference_points():
			x.append(point_coords.iloc[rival_a.index, hor_dim])
			y.append(point_coords.iloc[rival_a.index, vert_dim])
			x.append(point_coords.iloc[rival_b.index, hor_dim])
			y.append(point_coords.iloc[rival_b.index, vert_dim])
			points = pg.ScatterPlotItem(
				x=x, y=y, pen="b", symbol="o", size=point_size
			)
			plot.addItem(points)
			rival_a_label = pg.TextItem(
				text=rival_a.label, color=(0, 0, 0), anchor=(1.0, 0.0)
			)
			rival_a_label.setPos(
				point_coords.iloc[rival_a.index, hor_dim] + offset,
				point_coords.iloc[rival_a.index, vert_dim],
			)
			plot.addItem(rival_a_label)
			rival_b_label = pg.TextItem(
				text=rival_b.label, color=(0, 0, 0), anchor=(1.0, 0.0)
			)
			rival_b_label.setPos(
				point_coords.iloc[rival_b.index, hor_dim] + offset,
				point_coords.iloc[rival_b.index, vert_dim],
			)
			plot.addItem(rival_b_label)
		return

	# -- The following comes from director -----------------------------------

	# ------------------------------------------------------------------------

	def plot_to_gui_using_pyqtgraph(
		self,
		plot_widget: pg.GraphicsLayoutWidget,
		gallery_widget: pg.GraphicsLayoutWidget,
	) -> None:
		# had been called add_plot_using_pyqtgraph(
		# self, plot_widget1, plot_widget2)
		# Add the plot to the Plot tab (replace the current plot)
		self._director.tab_plot_scroll_area.setWidget(plot_widget)
		# Disable mouse events on the plot in tab_gallery
		self._director.disable_mouse_events(gallery_widget)
		# Add the plot to the Gallery tab (append to existing plots)
		widget = QWidget()
		widget.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
		layout = QVBoxLayout()
		layout.addWidget(gallery_widget)
		layout.setSizeConstraint(QVBoxLayout.SetNoConstraint)

		# Add a spacer at the end to push plots to the top
		spacer = QSpacerItem(
			20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding
		)
		layout.addItem(spacer)

		widget.setLayout(layout)
		self._director.tab_gallery_layout.addWidget(widget)

	# ------------------------------------------------------------------------

	def confidence_ellipse_using_pyqtgraph(
		self,
		x: np.ndarray,
		y: np.ndarray,
		n_std: float = 3.0,
		edgecolor: str = "r",
	) -> pg.QtWidgets.QGraphicsEllipseItem:
		"""
		Create a covariance confidence ellipse of *x* and *y* for pyqtgraph.

		Parameters
		----------
		x, y : array-like, shape (n, )
			Input data.

		n_std : float
			The number of standard deviations to determine the ellipse's
			radiuses.

		edgecolor : str
			Edge color for the ellipse

		Returns
		-------
		pg.QtWidgets.QGraphicsEllipseItem
		"""
		cov = np.cov(x, y)
		pearson = cov[0, 1] / np.sqrt(cov[0, 0] * cov[1, 1])

		# Using a special case to obtain the eigenvalues of this
		# two-dimensional dataset.
		ell_radius_x = np.sqrt(1 + pearson)
		ell_radius_y = np.sqrt(1 - pearson)

		# Calculating the standard deviation of x from
		# the squareroot of the variance and multiplying
		# with the given number of standard deviations.
		scale_x = np.sqrt(cov[0, 0]) * n_std
		mean_x = np.mean(x)

		# calculating the standard deviation of y ...
		scale_y = np.sqrt(cov[1, 1]) * n_std
		mean_y = np.mean(y)

		# Calculate final ellipse dimensions
		width = ell_radius_x * scale_x * 2
		height = ell_radius_y * scale_y * 2

		# Create ellipse centered at the mean
		ellipse = pg.QtWidgets.QGraphicsEllipseItem(
			mean_x - width / 2, mean_y - height / 2, width, height
		)

		# Set appearance
		pen_color = pg.QtGui.QColor(edgecolor)
		ellipse.setPen(pg.mkPen(color=pen_color, width=2))
		ellipse.setBrush(pg.mkBrush(None))  # No fill

		# Apply rotation (45 degrees like matplotlib version)
		transform = pg.QtGui.QTransform()
		transform.translate(mean_x, mean_y)
		transform.rotate(45)
		transform.translate(-mean_x, -mean_y)
		ellipse.setTransform(transform)

		return ellipse
