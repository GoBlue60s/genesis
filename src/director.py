from __future__ import annotations

# Standard library imports
import os
from pathlib import Path

# from dataclasses import dataclass

import pandas as pd
import pyqtgraph as pg
from PySide6.QtCore import QSize
from PySide6.QtGui import QAction, QBrush, QFont, QIcon, QPalette, QPixmap
from PySide6.QtWidgets import (
	QFileDialog,
	QLabel,
	QMainWindow,
	QMenu,
	QPushButton,
	QScrollArea,
	QSizePolicy,
	QSpacerItem,
	QStatusBar,
	QTableWidget,
	QTabWidget,
	QTextEdit,
	QToolBar,
	QToolButton,
	QVBoxLayout,
	QWidget,
)

# Typing imports
from typing import TYPE_CHECKING

from matplotlib_common import MatplotlibCommon
from pyqtgraph_common import PyQtGraphCommon

if TYPE_CHECKING:
	from collections.abc import Callable
	from matplotlib import pyplot as plt

from constants import TEST_IF_ACTION_OR_SUBMENU_HAS_THREE_ITEMS
from dependencies import DependencyChecking
from exceptions import SpacesError
from experimental import TesterCommand
from geometry import Point
from table_builder import (
	BuildOutputForGUI,
	BasicTableWidget,
	SquareTableWidget,
	GeneralStatisticalTableWidget,
	RivalryTableWidget,
)
from common import Spaces
from matplotlib_plots import MatplotlibMethods
from pyqtgraph_plots import PyQtGraphMethods


# --------------------------------------------------------------------------


class Status(QMainWindow):
	"""Main Window."""

	def __init__(self, parent: QWidget | None = None) -> None:
		"""Initializer."""
		super().__init__(parent)  # Call the base class constructor

		from rivalry import Rivalry  # noqa: PLC0415

		self.dependency_checker = DependencyChecking(self)
		self.tables = BasicTableWidget(self)
		self.squares = SquareTableWidget(self)
		self.statistics = GeneralStatisticalTableWidget(self)
		self.rivalry_tables = RivalryTableWidget(self)

		#
		# Establish initialization groups
		#

		self.establish_spaces_structure: EstablishSpacesStructure = (
			EstablishSpacesStructure(self)
		)
		self.build_traffic_dict: BuildTrafficDict = BuildTrafficDict(self)
		self.build_widget_dict: BuildWidgetDict = BuildWidgetDict(self)

		self.variables_used_for_command_handling()
		self.directories_being_used_for_data()
		self.rivalry = Rivalry(self)
		self.create_instances()

		self.variables_used_for_widget_building_etc()
		#
		self.setup_gui()

		# self.squares = SquareTableWidget(self)

	# ------------------------------------------------------------------------

	def variables_used_for_command_handling(self) -> None:
		_structure = self.establish_spaces_structure
		self.common = _structure.common
		self.current_command = _structure.current_command
		self.commands_used = _structure.commands_used
		self.command_exit_code = _structure.command_exit_code
		self.command = _structure.command
		self.undo_stack = _structure.undo_stack
		self.undo_stack_source = _structure.undo_stack_source
		self.deactivated_items = _structure.deactivated_items
		self.deactivated_descriptions = _structure.deactivated_descriptions

		self.traffic_dict = self.build_traffic_dict.traffic_dict

	# ------------------------------------------------------------------------

	def directories_being_used_for_data(self) -> None:
		_structure = self.establish_spaces_structure
		self.basedir = _structure.basedir
		self.filedir = _structure.filedir
		self.dir = _structure.dir

		basedir_str = str(self.basedir).replace("src", "resources")
		self.basedir = Path(basedir_str)

	# ------------------------------------------------------------------------

	def variables_used_for_widget_building_etc(self) -> None:
		_widget = self.build_widget_dict
		# self.title_for_table_widget = _widget.title_for_table_widget
		# self.output_widget_type = _widget.output_widget_type
		self.widget_dict = _widget.widget_dict
		self.column_header_color: str = "#F08080"  #  light coral for lightred
		self.row_header_color: str = "lightgreen"
		self.cell_color: str = "lightyellow"
		self.name_of_file_written_to: str = ""

	# ------------------------------------------------------------------------

	def setup_gui(self) -> None:
		self.setWindowTitle("Spaces")
		self.create_menu_bar()
		self.create_status_bar()
		self.create_tool_bar()
		self.create_tabs()

	# ------------------------------------------------------------------------

	def create_instances(self) -> None:
		"""This includes all the features and one analysis"""

		from modelmenu import UncertaintyAnalysis  # noqa: PLC0415
		from features import (  # noqa: PLC0415
			ConfigurationFeature,
			CorrelationsFeature,
			EvaluationsFeature,
			GroupedDataFeature,
			IndividualsFeature,
			ScoresFeature,
			SimilaritiesFeature,
			TargetFeature,
		)

		self.configuration_candidate = ConfigurationFeature(self)
		self.configuration_original = ConfigurationFeature(self)
		self.configuration_active = ConfigurationFeature(self)
		self.configuration_last = ConfigurationFeature(self)
		self.correlations_candidate = CorrelationsFeature(self)
		self.correlations_original = CorrelationsFeature(self)
		self.correlations_active = CorrelationsFeature(self)
		self.correlations_last = CorrelationsFeature(self)
		self.evaluations_candidate = EvaluationsFeature(self)
		self.evaluations_original = EvaluationsFeature(self)
		self.evaluations_active = EvaluationsFeature(self)
		self.evaluations_last = EvaluationsFeature(self)
		self.grouped_data_candidate = GroupedDataFeature(self)
		self.grouped_data_original = GroupedDataFeature(self)
		self.grouped_data_active = GroupedDataFeature(self)
		self.grouped_data_last = GroupedDataFeature(self)
		self.individuals_candidate = IndividualsFeature(self)
		self.individuals_original = IndividualsFeature(self)
		self.individuals_active = IndividualsFeature(self)
		self.individuals_last = IndividualsFeature(self)
		self.similarities_candidate = SimilaritiesFeature(self)
		self.similarities_original = SimilaritiesFeature(self)
		self.similarities_active = SimilaritiesFeature(self)
		self.similarities_last = SimilaritiesFeature(self)
		self.target_candidate = TargetFeature(self)
		self.target_original = TargetFeature(self)
		self.target_active = TargetFeature(self)
		self.target_last = TargetFeature(self)
		self.scores_candidate = ScoresFeature(self)
		self.scores_original = ScoresFeature(self)
		self.scores_active = ScoresFeature(self)
		self.scores_last = ScoresFeature(self)
		self.uncertainty_active = UncertaintyAnalysis(self)
		self.matplotlib_plotter = MatplotlibMethods(self)
		self.pyqtgraph_plotter = PyQtGraphMethods(self)
		self.matplotlib_common = MatplotlibCommon(self)
		self.pyqtgraph_common = PyQtGraphCommon(self)

	# ------------------------------------------------------------------------

	def create_tabs(self) -> None:
		self.tab_height: int = 600  # 1000
		self.tab_width: int = 800  # 1000
		self.setGeometry(1500, 300, self.tab_width, self.tab_height)
		# 1500, 800
		#
		self.tab_widget = QTabWidget(self)
		self.setCentralWidget(self.tab_widget)
		self.tab_widget.setTabPosition(QTabWidget.South)
		#
		self.text_to_tab = QTextEdit()
		#
		self.tab_plot_scroll_area = QScrollArea()
		self.tab_output_widget = QWidget()
		self.tab_output_layout = QVBoxLayout()
		self.tab_output_widget.setLayout(self.tab_output_layout)
		#
		self.tab_gallery_widget = QWidget()
		self.tab_gallery_layout = QVBoxLayout()
		self.tab_gallery_widget.setLayout(self.tab_gallery_layout)

		self.tab_gallery_scroll_area = QScrollArea()
		self.tab_gallery_scroll_area.setWidgetResizable(True)
		self.tab_gallery_scroll_area.setWidget(self.tab_gallery_widget)
		#
		self.tab_log_widget = QWidget()
		self.tab_log_layout = QVBoxLayout()
		# self.tab_log.setLayout(self.tab_log_layout)
		self.tab_log_widget.setLayout(self.tab_log_layout)
		#
		self.tab_log_scroll_area = QScrollArea()
		self.tab_log_scroll_area.setWidgetResizable(True)
		self.tab_log_scroll_area.setWidget(self.tab_log_widget)
		#
		self.tab_widget.addTab(self.tab_plot_scroll_area, "Plot")
		self.tab_widget.addTab(self.tab_output_widget, "Output")
		self.tab_widget.addTab(self.tab_gallery_scroll_area, "Gallery")
		self.tab_widget.addTab(self.tab_log_scroll_area, "Log")
		# self.tab_widget.addTab(self.tab_log, "Log")
		self.tab_widget.addTab(self.text_to_tab, "Record")
		#
		# Set the Qt Style Sheet for the QTabWidget
		#
		self.tab_widget.tabBar().setStyleSheet("""
			QTabBar::tab:hover {
			font-weight: bold;
			}
		""")

	# ------------------------------------------------------------------------

	def widget_control(self, next_output: str) -> object:
		widget_dict = self.widget_dict
		# _current_command = self.current_command

		gui_output_as_widget = None
		if next_output in widget_dict:
			if widget_dict[next_output][1] == "unique":
				gui_output_as_widget = self.current_command._display()
			else:
				which_shared = widget_dict[next_output][2]
				if callable(which_shared):
					gui_output_as_widget = which_shared()
				else:
					gui_output_as_widget = which_shared
		else:
			print("Key not found in the widget control dictionary")
		# self.current_command = _current_command
		return gui_output_as_widget

	# ------------------------------------------------------------------------

	def display_a_line(self) -> QTextEdit:
		gui_output_as_widget = QTextEdit()
		# gui_output_as_widget = QTextEdit(self.title_for_table_widget)
		self.output_widget_type = "Text"
		return gui_output_as_widget

	# ------------------------------------------------------------------------

	def display_coming_soon(self) -> QTextEdit:
		title_for_table_widget = self.title_for_table_widget

		gui_output_as_widget = QTextEdit(title_for_table_widget)
		self.output_widget_type = "Text"
		return gui_output_as_widget

	# ------------------------------------------------------------------------

	def set_column_and_row_headers(
		self,
		table_widget: QTableWidget,
		column_header: list[str],
		row_header: list[str],
	) -> None:
		if len(column_header) == 0:
			table_widget.horizontalHeader().hide()
		else:
			table_widget.setHorizontalHeaderLabels(column_header)
			table_widget.horizontalHeader().setStyleSheet(
				f"QHeaderView::section"
				f"{{ background-color: {self.column_header_color} }}"
			)
		if len(row_header) == 0:
			table_widget.verticalHeader().hide()
		else:
			table_widget.setVerticalHeaderLabels(row_header)
			table_widget.verticalHeader().setStyleSheet(
				f"QHeaderView::section"
				f"{{ background-color: {self.row_header_color} }}"
			)

	# ------------------------------------------------------------------------

	@staticmethod
	def resize_and_set_table_size(
		gui_output_as_widget: QTableWidget, fudge: int
	) -> None:
		"""Resize a table widget to fit its contents plus a fudge factor.

		Args:
			gui_output_as_widget: The table widget to resize
			fudge: Additional height in pixels to add
		"""
		n_rows = gui_output_as_widget.rowCount()
		gui_output_as_widget.resizeColumnsToContents()
		gui_output_as_widget.resizeRowsToContents()
		height_of_rows = sum(
			[gui_output_as_widget.rowHeight(row) for row in range(n_rows)]
		)
		height_of_header = gui_output_as_widget.horizontalHeader().height()
		gui_output_as_widget.setFixedHeight(
			height_of_rows + height_of_header + fudge
		)
		return

	# ------------------------------------------------------------------------

	def disable_mouse_events(
		self, graphics_layout_widget: pg.GraphicsLayoutWidget
	) -> None:
		# Loop over each row
		if hasattr(graphics_layout_widget, "ci"):
			for row in range(graphics_layout_widget.ci.layout.rowCount()):
				# Loop over each column
				for col in range(
					graphics_layout_widget.ci.layout.columnCount()
				):
					# Get the item in the cell
					item = graphics_layout_widget.ci.layout.itemAt(row, col)
					# Check if item is a PlotItem
					if isinstance(item, pg.graphicsItems.PlotItem.PlotItem):
						# Disable mouse events for this PlotItem
						item.vb.setMouseEnabled(x=False, y=False)
		else:
			print(
				"At bottom of disable_mouse_events, "
				"graphics_layout_widget does not have attribute 'ci'"
			)

	# ------------------------------------------------------------------------

	def plot_to_gui(self, fig: plt.Figure) -> None:
		self.plot_to_gui_using_matplotlib(fig)

	# ------------------------------------------------------------------------

	def create_file_menu(self) -> dict:
		"""Create dictionary structure for the File menu"""
		return {
			"New": {
				"icon": None,
				"tooltip": "Create something new",
				"items": {
					"Configuration": [
						"spaces_filenew.png",
						"new_configuration",
						"Create a new configuration",
					],
					"Grouped data": [
						"spaces_grouped_data_icon.jpg",
						"new_grouped_data",
						"Create new grouped data",
					],
				},
			},
			"Open": {
				"icon": None,
				"items": {
					"Configuration": [
						"spaces_fileopen.png",
						"open_configuration",
						"Open an existing configuration",
					],
					"Target": [
						"spaces_target_icon.jpg",
						"open_target",
						"Open an existing target",
					],
					"Grouped data": [
						"spaces_grouped_data_icon.jpg",
						"open_grouped_data",
						"Open existing grouped data",
					],
					"Similarities": {
						"icon": "spaces_similarities_icon.jpg",
						"items": {
							"Similarities": [
								None,
								"open_similarities_similarities",
								"Open existing similarities matrix",
							],
							"Dissimilarities": [
								None,
								"open_similarities_dissimilarities",
								"Open existing dissimilarities matrix",
							],
						},
					},
					"Correlations": [
						"spaces_correlations_icon.jpg",
						"open_correlations",
						"Open existing correlations matrix",
					],
					"Evaluations": [
						"spaces_evaluations_icon.jpg",
						"open_evaluations",
						"Open existing evaluations file",
					],
					"Individuals": [
						"spaces_individuals_icon.jpg",
						"open_individuals",
						"Open existing individuals file",
					],
					"Scores": [
						"spaces_scores_icon.jpg",
						"open_scores",
						"Open existing scores file",
					],
					"Sample": {
						"icon": "spaces_sample_icon.jpg",
						"items": {
							"Design": [
								None,
								"open_sample_design",
								"Open existing sample design file",
							],
							"Repetitions": [
								None,
								"open_sample_repetitions",
								"Open existing sample repetitions file",
							],
							"Solutions": [
								None,
								"open_sample_solutions",
								"Open existing sample solutions file",
							],
						},
					},
				},
			},
			"Save": {
				"icon": "spaces_filesave.png",
				"items": {
					"Configuration": [
						None,
						"save_configuration",
						"Save the active configuration",
					],
					"Target": [None, "save_target", "Save the active target"],
					"Correlations": [
						None,
						"save_correlations",
						"Save the active correlations",
					],
					"Similarities": [
						None,
						"save_similarities",
						"Save the active similarities",
					],
					"Individuals": [
						None,
						"save_individuals",
						"Save the active individuals",
					],
					"Scores": [None, "save_scores", "Save the active scores"],
					"Sample": {
						"icon": "spaces_sample_icon.jpg",
						"items": {
							"Design": [
								None,
								"save_sample_design",
								"Save the active sample design",
							],
							"Repetitions": [
								None,
								"save_sample_repetitions",
								"Save the active sample repetitions",
							],
							"Solutions": [
								None,
								"save_sample_solutions",
								"Save the active sample solutions",
							],
						},
					},
				},
			},
			"Deactivate": [
				"spaces_deactivate_icon.jpg",
				"deactivate",
				"Deactivate current features",
			],
			"Settings": {
				"icon": "spaces_settings_icon.jpg",
				"items": {
					"Plot settings": [
						None,
						"settings_plot",
						"Settings for plot",
					],
					"Plane": [None, "settings_plane", "Settings for plane"],
					"Segment sizing": [
						None,
						"settings_segment",
						"Settings for segment sizing",
					],
					"Display sizing": [
						None,
						"settings_display",
						"Settings for display sizing",
					],
					"Vector sizing": [
						None,
						"settings_vector",
						"Settings for vector sizing",
					],
					"Presentation layer": {
						"icon": "spaces_presentation_icon.jpg",
						"items": {
							"Matplotlib": [
								"spaces_matplotlib_icon.jpg",
								"settings_presentation_matplotlib",
								"Use Matplotlib for plots",
							],
							"PyQtGraph": [
								"spaces_QT_icon.webp",
								"settings_presentation_pyqtgraph",
								"Use PyQtGraph for plots",
							],
						},
					},
					"Layout options": [
						None,
						"settings_layout",
						"Settings for layout options",
					],
				},
			},
			"Print": {
				"icon": "spaces_fileprint.png",
				"items": {
					"Configuration": [
						None,
						"print_configuration",
						"Print active configuration",
					],
					"Target": [None, "print_target", "Print active target"],
					"Grouped data": [
						None,
						"print_grouped_data",
						"Print active grouped data",
					],
					"Correlations": [
						None,
						"print_correlations",
						"Print active correlations",
					],
					"Similarities": [
						None,
						"print_similarities",
						"Print active similarities",
					],
					"Evaluations": [
						None,
						"print_evaluations",
						"Print active evaluations",
					],
					"Individuals": [
						None,
						"print_individuals",
						"Print active individuals",
					],
					"Scores": [None, "print_scores", "Print active scores"],
					"Sample": {
						"icon": "spaces_sample_icon.jpg",
						"items": {
							"Design": [
								None,
								"print_sample_design",
								"Print active sample design",
							],
							"Repetitions": [
								None,
								"print_sample_repetitions",
								"Print active sample repetitions",
							],
							"Solutions": [
								None,
								"print_sample_solutions",
								"Print active sample solutions",
							],
						},
					},
				},
			},
			"Exit": ["spaces_exit_icon.jpg", "exit", "Exit Spaces"],
		}

	# ------------------------------------------------------------------------

	def create_edit_menu(self) -> dict:
		"""Create dictionary structure for the Edit menu"""
		return {
			"Undo": {
				"icon": "spaces_undo_icon.jpg",
				"command": "undo",
				"enabled": False,
				"tooltip": "Undo the last action",
			},
			"Redo": {
				"icon": "spaces_redo_icon.jpg",
				"command": "redo",
				"enabled": False,
				"tooltip": "Redo the last undone action",
			},
		}

	# ------------------------------------------------------------------------

	def create_view_menu(self) -> dict:
		"""Create dictionary structure for the View menu"""
		return {
			"Configuration": [
				"outer_space_icon.png",
				"view_configuration",
				"View active configuration",
			],
			"Target": [
				"spaces_view_target_icon.jfif",
				"view_target",
				"View active target",
			],
			"Grouped data": [
				"spaces_grouped_data_icon.jpg",
				"view_grouped",
				"View active grouped data",
			],
			"Similarities": [
				"spaces_black_icon.jpg",
				"view_similarities",
				"View active similarities",
			],
			"Correlations": [
				"spaces_r_red_icon.jpg",
				"view_correlations",
				"View active correlations",
			],
			"Distances": [
				"spaces_green_icon.png",
				"view_distances",
				"View active distances",
			],
			"Evaluations": [
				"spaces_evaluations_icon.jpg",
				"view_evaluations",
				"View active evaluations",
			],
			"Individuals": [
				"spaces_individuals_icon.jpg",
				"view_individuals",
				"View active individuals",
			],
			"Scores": [
				"spaces_scores_icon.jpg",
				"view_scores",
				"View active scores",
			],
			"History": [
				"spaces_history_icon.jpg",
				"history",
				"View history of commands",
			],
			"Sample": {
				"icon": "spaces_sample_icon.jpg",
				"items": {
					"Design": [
						None,
						"view_sample_design",
						"View active sample design",
					],
					"Repetitions": [
						None,
						"view_sample_repetitions",
						"View active sample repetitions",
					],
					"Solutions": [
						None,
						"view_sample_solutions",
						"View active sample solutions",
					],
				},
			},
			"Spatial uncertainty": {
				"icon": "spaces_uncertainty_icon.png",
				"items": {
					"Lines": [
						None,
						"view_spatial_uncertainty_lines",
						"View spatial uncertainty as lines",
					],
					"Boxes": [
						None,
						"view_spatial_uncertainty_boxes",
						"View spatial uncertainty as boxes",
					],
					"Ellipses": [
						None,
						"view_spatial_uncertainty_ellipses",
						"View spatial uncertainty as ellipses",
					],
					"Circles": [
						None,
						"view_spatial_uncertainty_circles",
						"View spatial uncertainty as circles",
					],
				},
			},
			"Point uncertainty": {
				"icon": "spaces_uncertainty_icon.png",
				"items": {
					"Lines": [
						None,
						"view_point_uncertainty_lines",
						"View point uncertainty as lines",
					],
					"Boxes": [
						None,
						"view_point_uncertainty_boxes",
						"View point uncertainty as boxes",
					],
					"Ellipses": [
						None,
						"view_point_uncertainty_ellipses",
						"View point uncertainty as ellipses",
					],
					"Circles": [
						None,
						"view_point_uncertainty_circles",
						"View point uncertainty as circles",
					],
				},
			},
			"Custom": [
				"spaces_custom_icon.png",
				"view_custom",
				"View custom display",
			],
		}

	# ------------------------------------------------------------------------

	def create_transform_menu(self) -> dict:
		"""Create dictionary structure for the Transform menu"""
		return {
			"Center": [
				"spaces_center_icon.jpg",
				"center",
				"Center the active configuration",
			],
			"Move": [
				"spaces_move_icon.png",
				"move",
				"Move points in the active configuration",
			],
			"Invert": [
				"spaces_invert_icon.jpg",
				"invert",
				"Invert dimensions in the active configuration",
			],
			"Rescale": [
				"spaces_rescale_icon.jpg",
				"rescale",
				"Rescale dimensions in the active configuration",
			],
			"Rotate": [
				"spaces_rotate_icon.jpg",
				"rotate",
				"Rotate the active configuration",
			],
			"Compare": [
				"spaces_compare_icon.jpg",
				"compare",
				"Compare the active configuration to the active target "
				"configuration",
			],
			"Varimax": {
				"icon": "spaces_varimax_icon.jpg",
				"command": "varimax",
				"enabled": False,
				"tooltip": \
					"Apply Varimax rotation to the active configuration",
			},
		}

	# ------------------------------------------------------------------------

	def create_associations_menu(self) -> dict:
		"""Create dictionary structure for the Associations menu"""
		return {
			"Correlations": [
				"spaces_correlations_icon.jpg",
				"correlations",
				"Compute correlations",
			],
			"Similarities": [
				"spaces_similarities_icon.jpg",
				"similarities",
				"Compute similarities",
			],
			"Line of sight": [
				"spaces_los_icon.jpg",
				"line_of_sight",
				"Compute Line of sight coefficients",
			],
			"Paired": [
				"spaces_paired_icon.jpg",
				"paired",
				"Compare pairs of points",
			],
			"Alike": [
				"spaces_alike_icon.jpg",
				"alike",
				"Select most alike points",
			],
			"Distances": [
				"spaces_distances_icon.jpg",
				"distances",
				"Compute distances in active configuration",
			],
			"Ranks": {
				"icon": "spaces_associations_ranks_icon.jpg",
				"items": {
					"Ranks of distances": [
						None,
						"ranks_distances",
						"Rank distances",
					],
					"Ranks of similarities": [
						None,
						"ranks_similarities",
						"Rank similarities",
					],
					"Difference of ranks": [
						None,
						"ranks_differences",
						"Difference of ranks",
					],
				},
			},
			"Scree diagram": [
				"spaces_scree_icon.jpg",
				"scree",
				"Create a scree diagram",
			],
			"Shepard diagram": {
				"icon": "spaces_shepard_icon.jpg",
				"items": {
					"Similarities on x-axis": [
						None,
						"shepard_similarities_on_x",
						"Display similarities on x-axis in Shepard diagram",
					],
					"Similarities on y-axis": [
						None,
						"shepard_similarities_on_y",
						"Display similarities on y-axis in Shepard diagram",
					],
				},
			},
			"Stress contribution": [
				"spaces_stress_icon.jpg",
				"stress_contribution",
				"Compute point contribution to stress",
			],
		}

	# ------------------------------------------------------------------------

	def create_model_menu(self) -> dict:
		"""Create dictionary structure for the Model menu"""
		return {
			"Cluster": [
				"spaces_cluster_icon.png",
				"cluster",
				"Cluster the active configuration",
			],
			"Principal Components": [
				"spaces_pca_icon.jpg",
				"principal",
				"Perform Principal Components Analysis",
			],
			"Factor Analysis": [
				"spaces_factor_analysis_icon.jpg",
				"factor_analysis",
				"Perform Factor Analysis",
			],
			"Factor Analysis Machine Learning": [
				"spaces_factor_analysis_icon.jpg",
				"factor_analysis_machine_learning",
				"Perform Machine Learning Factor Analysis",
			],
			"Multi-Dimensional Scaling": {
				"icon": "spaces_mds_icon.jpg",
				"items": {
					"Use non-metric estimation": [
						None,
						"mds_non_metric",
						"Perform non-metric Multi-Dimensional Scaling",
					],
					"Use metric estimation": [
						None,
						"mds_metric",
						"Perform metric Multi-Dimensional Scaling",
					],
				},
			},
			"Vectors": [
				"spaces_vectors_icon.jfif",
				"vectors",
				"Display active configuration as vectors",
			],
			"Directions": [
				"spaces_directions_icon.jfif",
				"directions",
				"Display active configuration as directions",
			],
			"Uncertainty": [
				"spaces_uncertainty_icon.png",
				"uncertainty",
				"Compute uncertainty of active configuration",
			],
		}

	# ------------------------------------------------------------------------

	def create_respondents_menu(self) -> dict:
		"""Create dictionary structure for the Respondents menu"""
		return {
			"Evaluations": [
				"spaces_evaluations_icon.jpg",
				"evaluations",
				"Evaluations by respondents",
			],
			"Sample": {
				"icon": "spaces_sample_icon.jpg",
				"items": {
					"Design samples": [
						None,
						"sample_designer",
						"Design samples",
					],
					"Generate repetitions": [
						None,
						"sample_repetitions",
						"Generate repetitions",
					],
				},
			},
			"Score individuals": [
				"spaces_scores_icon.jpg",
				"score_individuals",
				"Score individuals",
			],
			"Joint": [
				"spaces_joint_icon.jpg",
				"joint",
				"Display individuals and active configuration",
			],
			"Reference points": [
				"spaces_reference_icon.jpg",
				"reference_points",
				"Set reference points",
			],
			"Contest": [
				"spaces_contest_icon.jpg",
				"contest",
				"Display contest between rivals",
			],
			"Segments": [
				"spaces_segments_icon.jpg",
				"segments",
				"Describe segments in contest",
			],
			"Core": {
				"icon": "spaces_core_icon.jpg",
				"items": {
					"Spatially defined regions": [
						None,
						"core_regions",
						"Display core supporter regions",
					],
					"Left core supporters": [
						None,
						"core_left",
						"Display core supporters of left rival",
					],
					"Right core supporters": [
						None,
						"core_right",
						"Display core supporters of right rival",
					],
					"Both core supporters": [
						None,
						"core_both",
						"Display core supporters of both rivals",
					],
					"Neither core supporters": [
						None,
						"core_neither",
						"Display individuals not core supporter of rivals",
					],
				},
			},
			"Base supporters": {
				"icon": "spaces_base_icon.jpg",
				"items": {
					"Spatially defined regions": [
						None,
						"base_regions",
						"Display regions defining base of rivals",
					],
					"Left base supporters": [
						None,
						"base_left",
						"Display base supporters of left rival",
					],
					"Right base supporters": [
						None,
						"base_right",
						"Display base supporters of right rival",
					],
					"Both base supporters": [
						None,
						"base_both",
						"Display base supporters of both rivals",
					],
					"Neither base supporters": [
						None,
						"base_neither",
						"Display individuals not in base of rivals",
					],
				},
			},
			"Likely supporters": {
				"icon": "spaces_likely_icon.jpg",
				"items": {
					"Spatially defined regions": [
						None,
						"likely_regions",
						"Display regions defining likely supporters of rivals",
					],
					"Likely left supporters": [
						None,
						"likely_left",
						"Display likely supporters of left rival",
					],
					"Likely right supporters": [
						None,
						"likely_right",
						"Display likely supporters of right rival",
					],
					"Both likely supporters": [
						None,
						"likely_both",
						"Display likely supporters of both rivals",
					],
				},
			},
			"Battleground": {
				"icon": "spaces_battleground_icon.jpg",
				"items": {
					"Spatially defined regions": [
						None,
						"battleground_regions",
						"Display battleground regions",
					],
					"Battleground": [
						None,
						"battleground_segment",
						"Display battleground segment",
					],
					"Settled": [
						None,
						"battleground_settled",
						"Display settled segment",
					],
				},
			},
			"Convertible": {
				"icon": "spaces_convertible_icon.jpg",
				"items": {
					"Spatially defined regions": [
						None,
						"convertible_regions",
						"Display convertible regions",
					],
					"Convertible to the left": [
						None,
						"convertible_left",
						"Display individuals convertible to the left rival",
					],
					"Convertible to the right": [
						None,
						"convertible_right",
						"Display individuals convertible to the right rival",
					],
					"Both": [
						None,
						"convertible_both",
						"Display individuals convertible to both rivals",
					],
					"Settled": [
						None,
						"convertible_settled",
						"Display settled segment",
					],
				},
			},
			"Focused on first dimension": {
				"icon": "spaces_first_dim_icon.jpg",
				"items": {
					"Spatially defined regions": [
						None,
						"first_regions",
						"Display regions defined by first dimension",
					],
					"Left focused": [
						None,
						"first_left",
						"Display individuals on the left of mean on"
						" first dimension",
					],
					"Right focused": [
						None,
						"first_right",
						"Display individuals on the right of mean on"
						" first dimension",
					],
				},
			},
			"Focused on second dimension": {
				"icon": "spaces_second_dim_icon.jpg",
				"items": {
					"Spatially defined regions": [
						None,
						"second_regions",
						"Display regions defined by second dimension",
					],
					"Upper focused": [
						None,
						"second_upper",
						"Display individuals above mean on second dimension",
					],
					"Lower focused": [
						None,
						"second_lower",
						"Display individuals below mean on second dimension",
					],
				},
			},
		}

	# ------------------------------------------------------------------------

	def create_help_menu(self) -> dict:
		"""Create dictionary structure for the Help menu"""
		return {
			"Help Content": [
				"spaces_help_icon.jpg",
				"help_content",
				"Help content",
			],
			"Status": ["spaces_status_icon.jpg", "status", "Display status"],
			"Verbose": [
				"spaces_verbosity_icon.jfif",
				"verbose",
				"Toggle between Terse and Verbose",
			],
			"About": ["spaces_about_icon.jpg", "about", "About Spaces"],
		}

	# ------------------------------------------------------------------------

	def create_tester_menu(self) -> dict:
		"""Create dictionary structure for the Tester menu"""
		return {"Tester": ["spaces_tester_icon.jpg", "tester"]}

	# ------------------------------------------------------------------------

	def create_menu_bar(self) -> None:
		#
		# Creating menu using a QMenu object

		self.spaces_menu_bar = self.menuBar()
		# self.spaces_menu_bar.setToolTipsVisible(True)

		file_menu = self.create_file_menu()
		edit_menu = self.create_edit_menu()
		view_menu = self.create_view_menu()
		transform_menu = self.create_transform_menu()
		associations_menu = self.create_associations_menu()
		model_menu = self.create_model_menu()
		respondents_menu = self.create_respondents_menu()
		help_menu = self.create_help_menu()
		tester_menu = self.create_tester_menu()

		menus = [
			("File", file_menu),
			("Edit", edit_menu),
			("View", view_menu),
			("Transform", transform_menu),
			("Associations", associations_menu),
			("Model", model_menu),
			("Respondents", respondents_menu),
			("Help", help_menu),
			("Tester", tester_menu),
		]

		for menu_name, menu_dict in menus:
			menu = self.spaces_menu_bar.addMenu(menu_name)
			self.add_submenus(menu, menu_dict)

	# ------------------------------------------------------------------------

	def assemble_submenus(self, menus: list[tuple[str, dict]]) -> None:
		"""Assemble all menus from their individual dictionaries
		Args:
			menu items: list of tuples, each containing (menu name,
			menu_dictionary)
		"""

		for menu_name, submenus in menus:
			menu = self.spaces_menu_bar.addMenu(menu_name)
			self.add_submenus(menu, submenus)

	# ------------------------------------------------------------------------

	def add_menus_initialize_variables(self) -> None:
		self.menu_dict_key_error_title = "Menu dictionary key error"
		self.menu_dict_key_error_message = (
			"Menu item has invalid key. "
			"Valid keys are 'icon', 'command', 'enabled', "
			"'shortcut', 'items', 'tooltip'."
		)
		self.valid_keys = {
			"icon",
			"command",
			"enabled",
			"shortcut",
			"items",
			"tooltip",
		}
		self.needs_separator = [
					"cluster",
					"deactivate",
					"open_grouped_data",
					"open_correlations",
					"print_target",
					"print_grouped_data",
					"print_similarities",
					"line_of_sight",
					"contest",
					"joint",
		]
	# ------------------------------------------------------------------------

	def add_submenus(self, menu: QMenu, submenus: dict) -> None:
		"""Add submenus and menu items recursively"""
		self.add_menus_initialize_variables()

		for submenu_name, action_or_submenu in submenus.items():
			if isinstance(action_or_submenu, dict):
				self._validate_menu_dict_keys(action_or_submenu)
				if "command" in action_or_submenu:
					self._create_menu_action_from_dict(
						menu, submenu_name, action_or_submenu
					)
				else:
					self._create_submenu_from_dict(
						menu, submenu_name, action_or_submenu
					)
			else:
				self._create_simple_menu_action(
					menu, submenu_name, action_or_submenu
				)

	def _validate_menu_dict_keys(self, action_or_submenu: dict) -> None:
		"""Validate that all keys in the menu dictionary are allowed"""
		for key in action_or_submenu:
			if key not in self.valid_keys:
				raise SpacesError(
					self.menu_dict_key_error_title,
					self.menu_dict_key_error_message,
				)

	def _create_icon_path(self, icon_name: str) -> str:
		"""Create the full path for an icon file"""
		return str(Path(self.basedir) / "Spaces_icons" / icon_name)

	def _create_action_with_icon(
		self, name: str, icon_name: str | None
	) -> QAction:
		"""Create a QAction with or without an icon"""
		if icon_name:
			return QAction(
				QIcon(self._create_icon_path(icon_name)), name, self
			)
		return QAction(name, self)

	def _configure_action_properties(
		self, action: QAction, properties: dict
	) -> None:
		"""Configure action properties like tooltip, enabled state, etc."""
		if "tooltip" in properties:
			action.setToolTip(properties["tooltip"])

		if properties.get("enabled") is False:
			action.setEnabled(False)

		if "shortcut" in properties:
			action.setShortcut(properties["shortcut"])

	def _create_menu_action_from_dict(
		self, menu: QMenu, name: str, properties: dict
	) -> None:
		"""Create a menu action from a dictionary of properties"""
		action = self._create_action_with_icon(name, properties.get("icon"))
		self._configure_action_properties(action, properties)

		action.triggered.connect(
			self.create_lambda_with_toggle(properties["command"])
		)
		menu.addAction(action)

	def _create_submenu_from_dict(
		self, menu: QMenu, name: str, properties: dict
	) -> None:
		"""Create a submenu from a dictionary of properties"""
		submenu = menu.addMenu(name)
		submenu.setToolTipsVisible(True)

		if properties.get("icon"):
			submenu.setIcon(QIcon(self._create_icon_path(properties["icon"])))

		self.add_submenus(submenu, properties["items"])

		# Special case for Multi-Dimensional Scaling submenu
		if name == "Multi-Dimensional Scaling":
			menu.addSeparator()

	def _create_simple_menu_action(
		self, menu: QMenu, name: str, action_data: list
	) -> None:
		"""Create a simple menu action from a list [icon, command] or
		[icon, command, tooltip]"""
		icon, command, tooltip = self._parse_simple_action_data(action_data)

		action = self._create_action_with_icon(name, icon)

		if tooltip:
			action.setToolTip(tooltip)
			action.setWhatsThis(tooltip)

		self._connect_action_command(action, name, command)
		menu.addAction(action)

		if command in self.needs_separator:
			menu.addSeparator()

	def _parse_simple_action_data(
		self, action_data: list
	) -> tuple[str | None, str, str | None]:
		"""Parse simple action data and return icon, command, and tooltip"""
		if len(action_data) == TEST_IF_ACTION_OR_SUBMENU_HAS_THREE_ITEMS:
			return action_data[0], action_data[1], action_data[2]
		return action_data[0], action_data[1], None

	def _connect_action_command(
		self, action: QAction, name: str, command: str
	) -> None:
		"""Connect the action to the appropriate command handler"""
		if name == "Verbose":
			action.setCheckable(True)
			self.help_verbosity_action = action
			action.triggered.connect(self.toggle_verbosity)
		else:
			action.triggered.connect(self.create_lambda_with_toggle(command))

	def create_lambda_with_toggle(self, next_command: str) -> Callable:
		return lambda: self.traffic_control(next_command)

	# -------------------------------------------------------------------------

	def toggle_verbosity(self) -> None:
		current_text = self.help_verbosity_action.text()

		self.traffic_control(current_text.lower())

		new_text = "Terse" if current_text == "Verbose" else "Verbose"
		self.help_verbosity_action.blockSignals(True)  # noqa: FBT003
		self.help_verbosity_action.setText(new_text)
		self.help_verbosity_action.setParent(None)
		self.spaces_menu_bar.removeAction(self.help_verbosity_action)
		self.spaces_menu_bar.addAction(self.help_verbosity_action)
		self.help_verbosity_action.blockSignals(False)  # noqa: FBT003

	# ------------------------------------------------------------------------

	def create_status_bar(self) -> None:
		# self.spaces_statusbar: QStatusBar = QStatusBar()

		self.spaces_statusbar: QStatusBar = QStatusBar()
		self.left_statusbar_message: str = "Left"
		self.center_statusbar_message: str = ""
		self.right_statusbar_message: str = "Spaces 2025"
		self.left_statusbar: QLabel = QLabel(self.left_statusbar_message)
		self.center_statusbar: QLabel = QLabel(self.center_statusbar_message)
		self.right_statusbar: QLabel = QLabel(self.right_statusbar_message)
		left_spacer = QWidget()
		left_spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
		right_spacer = QWidget()
		right_spacer.setSizePolicy(
			QSizePolicy.Expanding, QSizePolicy.Expanding
		)
		self.spaces_statusbar.addWidget(self.left_statusbar)
		self.spaces_statusbar.addWidget(left_spacer)
		self.spaces_statusbar.addWidget(self.center_statusbar)
		self.spaces_statusbar.addWidget(right_spacer)
		self.spaces_statusbar.addPermanentWidget(self.right_statusbar)
		self.setStatusBar(self.spaces_statusbar)
		self.left_statusbar.setText("Awaiting your command!")

		# -------------------------------------------------------------------
		# In traffic_control items are in the menu order
		# BUT one entry can handle multiple menu items
		#     thus there are fewer match cases than menu items

		self.commands = (
			"About",
			"Alike",
			"Base",
			"Battleground",
			"Center",
			"Cluster",
			"Compare",
			"Configuration",
			"Contest",
			"Convertible",
			"Core supporters",
			"Correlations",
			"Create",
			"Deactivate",
			"Directions",
			"Distances",
			"Evaluations",
			"Exit",
			"Factor classic",
			"Factor machine learning",
			"First dimension",
			"Grouped",
			"Help",
			"History",
			"Individuals",
			"Invert",
			"Joint",
			"Likely supporters",
			"Line of sight",
			"MDS",
			"Move",
			"New grouped data",
			"Open sample design",
			"Open sample repetitions",
			"Open scores",
			"Paired",
			"Principal Components",
			"Print configuration",
			"Print correlations",
			"Print evaluations",
			"Print grouped data",
			"Print sample design",
			"Print sample repetitions",
			"Print scores",
			"Print similarities",
			"Print target",
			"Ranks differences",
			"Ranks distances",
			"Ranks similarities",
			"Redo",
			"Reference points",
			"Rescale",
			"Rotate",
			"Sample designer",
			"Sample repetitions",
			"Save configuration",
			"Save correlations",
			"Save individuals",
			"Save sample design",
			"Save sample repetitions",
			"Save scores",
			"Save similarities",
			"Save target",
			"Score individuals",
			"Scree",
			"Second dimension",
			"Segments",
			"Settings - display sizing",
			"Settings - layout options",
			"Settings - plane",
			"Settings - plot settings",
			"Settings - presentation layer Matplotlib",
			"Settings - presentation layer PyQtGraph",
			"Settings - segment",
			"Settings - vector sizing",
			"Shepard",
			"Similarities",
			"Status",
			"Stress contribution",
			"Target",
			"Terse",
			"Tester",
			"Uncertainty",
			"Undo",
			"Varimax",
			"Vectors",
			"Verbose",
			"View configuration",
			"View correlations",
			"View custom",
			"View distances",
			"View evaluations",
			"View grouped data",
			"View point uncertainty",
			"View sample design",
			"View sample repetitions",
			"View scores",
			"View similarities",
			"View spatial uncertainty",
			"View target",
		)
		# peek(len(self.commands))

	# ------------------------------------------------------------------------

	def traffic_control(self, next_command: str) -> None:
		traffic_dict = self.build_traffic_dict.traffic_dict
		common = self.common

		try:
			command_class = traffic_dict[next_command][0]
			if traffic_dict[next_command][1] is None:
				self.current_command = command_class(self, common)
				self.current_command.execute(common)
			else:
				self.current_command = command_class(self, common)
				self.current_command.execute(
					common, traffic_dict[next_command][1]
				)
		except SpacesError as e:
			self.unable_to_complete_command_set_status_as_failed()
			self.common.error(e.title, e.message)

	# ------------------------------------------------------------------------

	def create_lambda(self, next_command: str) -> Callable:
		return lambda: self.traffic_control(next_command)

	# ------------------------------------------------------------------------

	def create_tool_bar(self) -> None:
		# Using a title_for_table_widget
		self.spaces_toolbar = QToolBar("Spaces toolbar")
		self.spaces_toolbar.setIconSize(QSize(20, 20))
		self.addToolBar(self.spaces_toolbar)

		button_dict = {
			"new": (
				"spaces_filenew.png",
				"new_configuration",
				"Create new configuration",
			),
			"open": (
				"spaces_fileopen.png",
				"open_configuration",
				"Open existing configuration",
			),
			"save": (
				"spaces_filesave.png",
				"save_configuration",
				"Save current configuration",
			),
			"undo": ("spaces_undo_icon.jpg", "undo", "Undo last action"),
			"redo": (
				"spaces_redo_icon.jpg",
				"redo",
				"Redo last undone action",
			),
			"center": (
				"spaces_center_icon.jpg",
				"center",
				"Center current configuration",
			),
			"move": (
				"spaces_move_icon.png",
				"move",
				"Move points in current configuration",
			),
			"invert": (
				"spaces_invert_icon.jpg",
				"invert",
				"Invert dimensions",
			),
			"rescale": (
				"spaces_rescale_icon.jpg",
				"rescale",
				"Rescale dimensions",
			),
			"rotate": (
				"spaces_rotate_icon.jpg",
				"rotate",
				"Rotate dimensions",
			),
			"scree": ("spaces_scree_icon.jpg", "scree", "Show Scree diagram"),
			"shepard": (
				"spaces_shepard_icon.jpg",
				"shepard_similarities_on_x",
				"Show Shepard diagram",
			),
			"mds": (
				"spaces_mds_icon.jpg",
				"mds",
				"Perform Multi-Dimensional Scaling",
			),
			"factor_analysis": (
				"spaces_factor_analysis_icon.jpg",
				"factor_analysis",
				"Perform Factor Analysis",
			),
			"principal_components": (
				"spaces_pca_icon.jpg",
				"principal",
				"Perform Principal Components Analysis",
			),
			"reference_points": (
				"spaces_reference_icon.jpg",
				"reference_points",
				"Set reference points",
			),
			"contest": ("spaces_contest_icon.jpg", "contest", "Show contest"),
			"segments": (
				"spaces_segments_icon.jpg",
				"segments",
				"Show segments",
			),
			"core": (
				"spaces_core_icon.jpg",
				"core_regions",
				"Show core supporter regions",
			),
			"base": (
				"spaces_base_icon.jpg",
				"base_regions",
				"Show base supporter regions",
			),
			"likely": (
				"spaces_likely_icon.jpg",
				"likely_regions",
				"Show likely supporter regions",
			),
			"battleground": (
				"spaces_battleground_icon.jpg",
				"battleground_regions",
				"Show battleground regions",
			),
			"convertible": (
				"spaces_convertible_icon.jpg",
				"convertible_regions",
				"Show convertible regions",
			),
			"first": (
				"spaces_first_dim_icon.jpg",
				"first_regions",
				"Show first dimension regions",
			),
			"second": (
				"spaces_second_dim_icon.jpg",
				"second_regions",
				"Show second dimension regions",
			),
			"help": ("spaces_help_icon.jpg", "help_content", "Show help"),
		}
		icon_directory = "Spaces_icons"
		# Loop through the dictionary to create and set the tool buttons

		for key, (icon, _next_command, _) in button_dict.items():
			# Create the QAction dynamically
			button_action = QAction(
				QIcon(str(Path(self.basedir) / icon_directory / icon)),
				key.capitalize(),
				self,
			)

			button_action.triggered.connect(self.create_lambda(_next_command))

			# Create the QToolButton dynamically
			tool_button = QToolButton()
			tool_button.setDefaultAction(button_action)
			tool_button.installEventFilter(self)

			# Set the tool button as an attribute of the class
			setattr(self, f"{key}_tool_button", tool_button)

			# Add the tool button to the toolbar
			self.spaces_toolbar.addWidget(tool_button)

			# Add separators after specific buttons

			if key in ["redo", "shepard", "principal_components"]:
				self.spaces_toolbar.addSeparator()

		return

	# ------------------------------------------------------------------------

	def record_command_as_selected_and_in_process(self) -> None:
		"""The start method is called at the beginning of each command to
		indicate that the command is in process.
		"""
		self.spaces_statusbar.showMessage(
			f"Starting {self.command} command", 80000
		)
		self.commands_used.append(self.command)
		self.command_exit_code.append(-1)  # -1  command is in process
		print(f"\nStarting {self.command} command: \n")
		#
		# Create previous for undo
		#
		# passive_commands = (
		# 	"About", "Base", "Battleground", "Bisector", "Contest",
		# 	"Convertible", "Core supporters", "Deactivate",
		# 	"Distances", "Exit", "Help", "History", "Joint",
		#  "Likely supporters",
		# 	"Paired", "Ranks", "Sample designer", "Save configuration",
		# 	"Save individuals", "Save scores", "Save target", "Shepard",
		#  "Status",
		# 	"Stress contribution", "Terse", "Undo", "Verbose",
		# 	"View configuration", "View custom", "View grouped data",
		# 	"View correlations", "View distances", "View similarities",
		# 	"View target")

	# ------------------------------------------------------------------------

	def optionally_explain_what_command_does(self) -> str:
		explain_dict = {
			"About": "About provides information about the program.",
			"Alike": "Alike can be used to place lines between points "
			"with high similarity.\n"
			"Only pairs of points with a similarity "
			"above, or a dissimilarity below, the cutoff will have "
			"a line joining the points.",
			"Base": "Base identifies regions close to the reference "
			"points in the battleground region.\n"
			"Individuals in these areas prefer these candidates.",
			"Battleground": "Battleground is used to define a region of "
			"battleground points within a tolerance "
			"from bisector between reference points.\n"
			"Individuals in these areas may be undecided.",
			"Center": "Center is used to shift points to be centered around "
			"the origin.\n"
			"This is achieved by subtracting the mean of each dimension "
			"from each coordinate.\n"
			"This is especially useful when the coordinates are latitudes "
			"and longitudes.",
			"Cluster": "Cluster used to assign points to clusters.\n"
			"The assignments can be read from a file or determined by "
			"a clustering algorithm.",
			"Compare": "Compare is used to compare the target configuration "
			"with the active configuration.\n"
			"The target configuration will be centered to facilitate "
			"comparison.\n"
			"The active configuration will be rotated and transformed "
			"to minimize the differences with the target configuration.\n"
			"A measure of the difference, disparity, will be computed.\n"
			"The result will be plotted with a line connecting "
			"corresponding points.\n"
			"The line will be labeled with the label for the point.\n"
			"The line will have zero length when the configurations "
			"match perfectly.\n"
			"The point from the rotated configuration with be labeled "
			"with an R.\n"
			"The point from the target congratulation will be labeled "
			"with a T.",
			"Configuration": "Configuration reads in a configuration file.\n"
			"The file must be formatted correctly.\n"
			"The first line should be Configuration.\n"
			"The next line should have two fields: "
			"the number of dimensions and the number of points.\n"
			"For each point: \n"
			"\tA line containing the label, a semicolon, and the "
			"full name for that point.\n"
			"\tA line with the coordinate for the point on each dimension "
			"separated by commas.",
			"Contest": "Contest identifies regions defined by the reference "
			"points.",
			"Convertible": "Convertible identifies regions where \n"
			"individuals might be converted and switch their preference.",
			"Core supporters": "Core supporters identifies regions "
			"immediately around the reference points.\n"
			"Individuals in these areas prefer these candidates the most.",
			"Open correlations": "Correlations reads in a correlation matrix "
			"from a file.\n"
			"The file must be in the a format similar to to the OSIRIS "
			"format.\n"
			"The correlations may be used as similarities but more likely "
			"are used as input to Factor.\n"
			"The correlations are stored as similarities and treated as "
			"measures of similarity.",
			"Create": "Create is used to build the \nactive configuration by "
			"using user supplied information.\n"
			"In addition to creating names and labels, coordinates \n"
			"can be supplied by the user, assigned randomly, or use \n"
			"the classic approach of using the order of the points.",
			"Deactivate": "Deactivate is used to deactivate the active \n"
			"configuration, the existing target configuration, \n"
			" existing similarities, and existing correlations.",
			"Directions": "Directions is used to display a plot showing the "
			"direction of each point \n"
			"from the origin to the unit circle.",
			"Distances": "Distances displays a matrix of inter-point "
			"distances.\n"
			"Some alternatives:\n"
			"similarities could be shown above the diagonal\n"
			"optionally ranks could be displayed in place of, or in "
			"addition to, values\n"
			"information could be displayed as a table with a line for "
			"each pair of points",
			"Evaluations": "Evaluations reads in a file containing \n"
			"individual evaluations corresponding to the points in \n"
			"the active configuration.",
			"Factor analysis": "Factor creates a factor analysis of the "
			"current correlations.\n"
			"The output is a factor matrix with as many points as in "
			"the correlation matrix.\n"
			"The plot will have vectors from the origin to each point.\n"
			"It displays a Scree diagram with the Eigenvalue for each \n"
			"dimensionality. The dimensionality on the x-axis (1-n and "
			"the Eigenvalue on the y-axis.\n"
			"It asks the user how many dimensions to retain and uses \n"
			"that to determine the number of dimensions to be retained.",
			"Factor analysis machine learning": "Factor creates a factor "
			"analysis of the "
			"current correlations.\n"
			"The output is a factor matrix with as many points as in "
			"the active configuration.\n"
			"The plot will have vectors from the origin to each point.\n"
			"It displays a Scree diagram with the Eigenvalue for each \n"
			"dimensionality. The dimensionality on the x-axis (1-n and "
			"the Eigenvalue on the y-axis.\n"
			"It asks the user how many dimensions to retain and uses \n"
			"that to determine the number of dimensions to be retained.",
			"First dimension": "First dimension identifies regions "
			"defined by the first dimension.",
			"Grouped data": "Grouped data reads in a file with coordinates"
			" for groups of on all dimensions. \n"
			"The number of groups in a file should be small.\n"
			"The number of dimensions must be the same as the active "
			"correlation.\n"
			"If reference points have been established the user can add"
			"the points and the bisector.",
			"Help": "Help displays general information about Spaces.",
			"History": "History displays a list of commands used in this "
			"session.",
			"Individuals": "Individuals is used to establish variables\n"
			"usually scores and filters for a set of individuals.",
			"Invert": "Invert inverts dimension(s).\n"
			"It asks the user which dimension(s) to invert.\n"
			"It multiples each point's coordinate on a dimension by -1.\n"
			"The resulting configuration becomes the active "
			"configuration.",
			"Joint": "Joint creates a plot including points "
			"for individuals as well as points for referents.\n"
			"The user decides whether to include the full active "
			"configuration\n"
			"or just the reference points. The user also decides whether"
			" to \n"
			"include the perpendicular bisector between the reference "
			"points.\n",
			"Likely supporters": "Likely supporters identifies regions "
			"defined by the reference points.\n"
			"Individuals in these areas are likely to prefer these "
			"candidates.",
			"Line of sight": "Line of sight computes the Line of sight "
			"measure of association. \n"
			"Line of sight is a measure of dissimilairity. "
			"It was developed by George Rabinowitz.",
			"MDS": "MDS is used to perform a metric or non-metric "
			"multi-dimensional scaling of the similarities.\n"
			"The user will be asked for the number of components"
			" to be used.\n"
			"The result of MDS will become the active configuration.",
			"Move": "Move is used to add a constant to the coordinates "
			"along dimension(s).\n"
			"The user will be asked which dimension(s) to move.\n"
			"The user will be asked for a value to be used.\n"
			"The value, positive or negative, will be added to each "
			"point's coordinate on the dimension.\n"
			"The resulting configuration becomes the active "
			"configuration.",
			"New grouped data": "New grouped data creates a new grouped "
			"data file.\n"
			"The user will be asked for the grouping variable,"
			"number of groups and the "
			"number of dimensions.\n"
			"For each group the user will be asked for a label, a name, "
			"and the coordinate on each dimension.\n"
			"The result will become the active grouped data.",
			"Open sample design": "Open sample design reads in a file "
			"containing a sample design.",
			"Open sample repetitions": "Open sample repetitions reads in "
			"a file containing sample repetitions.",
			"Open sample solutions": "Open sample solutions reads in "
			"a file containing sample solutions.",
			"Open scores": "Open scores reads in a file containing individual "
			"scores \n"
			"corresponding to the dimensions in the active configuration.",
			"Paired": "Paired is used to obtain information about pairs of "
			"points.\n"
			"The user will be asked to select pairs of points.",
			"Plane": "Plane is used to define the plane to be displayed",
			"Principal components": "Principal components is used to obtain "
			"the axes having the highest explanatory power to \n"
			"describe the correlations.\n",
			"Print configuration": "Print configuration is used to print "
			" the active configuration.",
			"Print correlations": "Print correlations is used to print "
			"the active correlations.",
			"Print evaluations": "Print evaluations is used to print the "
			"active evaluations.",
			"Print grouped data": "Print grouped data is used to print the "
			"active grouped data.",
			"Print sample design": "Print sample design is used to print "
			"the active sample design.",
			"Print sample repetitions": "Print sample repetitions is used "
			"to print the active sample repetitions.",
			"Print scores": "Print scores is used to print the active scores.",
			"Print similarities": "Print similarities is used to print "
			"the active similarities.",
			"Print target": "Print target is used to print the active target.",
			"Ranks differences": "Ranks differences displays a matrix of "
			"inter-point rank differences.",
			"Ranks distances": "Ranks distances is used to display ranks of "
			"inter-point distances.",
			"Ranks similarities": "Ranks similarities is used to display "
			"ranks of inter-point similarities.",
			"Redo": "Redo redoes the last action.",
			"Reference points": "Reference points is used to designate two "
			"points as reference points.\n"
			"Reference points will define the bisector.\n"
			"The active configuration will be shown with a line "
			"between the reference points and \n"
			"a perpendicular bisector.",
			"Rescale": "Rescale is used to increase or decrease coordinates.\n"
			"The user will be asked which dimension(s) to rescale.\n"
			"The user will be asked for a value to be used.\n"
			"The coodinate for each point will be multiplied by the "
			"value.\n"
			"The resulting configuration becomes the active "
			"configuration.",
			"Rotate": "Rotate is used to rotate the current plane of the "
			"active configuration.\n"
			"The user will be asked for an angle of rotation in degrees.\n"
			"The resulting configuration becomes the active"
			" configuration.",
			"Sample designer": "Sample designer is used to create a sample "
			"design matrix.\n"
			"The user will be asked for the number of individuals in"
			"the universe to be sampled \n"
			"the number of repetitions to be created \n"
			"and the probability of selection for each individual.\n"
			"The matrix will contain ones and zeroes to indicate \n"
			"whether an individual is included in a repetition. \n"
			"The matrix will contain a row for each respondent and a \n"
			"column for each repetition.",
			"Sample repetitions": "Sample repetitions is used to create a "
			"matrix of sample \n"
			"repetitions based on the sample design.",
			"Save configuration": "Save configuration is used to save "
			"the active configuration to a file.\n"
			"The user will be asked for a file name.\n",
			"Save correlations": "Save correlations is used to save the "
			"active correlations to a file.\n"
			"The user will be asked for a file name.\n",
			"Save individuals": "Save individuals is used to save the "
			"active individuals to a file.\n"
			"The user will be asked for a file name.\n",
			"Save sample design": "Save sample design is used to save the "
			"active sample design to a file.\n"
			"The user will be asked for a file name.\n",
			"Save sample repetitions": "Save sample repetitions is used to "
			"save the active sample repetitions to a file.\n"
			"The user will be asked for a file name.\n",
			"Save sample solutions": "Save sample solutions is used to save "
			"the active sample solutions to a file.\n"
			"The user will be asked for a file name.\n",
			"Save scores": "Save scores is used to save the active scores "
			"to a file.\n"
			"The user will be asked for a file name.\n",
			"Save similarities": "Save similarities is used to save the "
			"active similarities to a file.\n"
			"The user will be asked for a file name.\n",
			"Save target": "Save target is used to save the active target "
			"to a file.\n"
			"The user will be asked for a file name.\n",
			"Score individuals": "Score individuals is used to create "
			"scores for individuals based on evaluations.",
			"Scree": "Scree displays a diagram showing stress vs."
			" dimensionality.\n"
			"The Scree diagram is used to help decide how many dimensions"
			" to fit the similarities.\n"
			"The number of dimensions is on the x-axis and stress is on "
			"the y-axis.",
			"Second dimension": "Second dimension identifies regions "
			"defined by the second dimension.",
			"Segments": "Segments identifies regions defined by the"
			" reference points.\n"
			"Individuals are assigned to segments based on their "
			"scores on the dimensions\n"
			" of the active configuration. Segments provides estimates "
			"of the number of \n"
			"individuals in each segment. Segments are not mutually "
			"exclusive.",
			"Settings - plot settings": "Settings - plot settings is used to "
			"set whether to include a \n"
			"connector beween reference points, a bisector, the "
			"reference points by \n"
			"themselves or with all points",
			"Settings - plane": "Settings - plane is used to define the plane "
			"to be displayed.\n"
			"It requires that the active configuration has been "
			"established.\n"
			"The user is asked which of its dimensions to be used "
			"on the horizontal axis.\n"
			"If there are more than two dimensions the user is also"
			"asked which dimension \n"
			"to use on the vertical axis.",
			"Settings - segment sizing": \
				"Settings - segment sizing is used to "
			"set the size of the segments.\n"
			"The user is asked for percentages of the connector size to "
			"use to set the size of \n"
			"the battleground and convertible segments as well as the core"
			"supporter segments.",
			"Settings - display sizing": \
				"Settings - display sizing is used to "
			"set various parameters that affect the display.",
			"Settings - vector sizing": "Settings - vector sizing is used to "
			"set the length of the \n"
			"vectors and the size of their heads.",
			"Settings - presentation layer": "Settings - "
			"presentation layer "
			"is used to select Matplotlib or pyqtgraph\n"
			"as the presentation layer.",
			"Settings - presentation layer pyqtgraph": "Settings - "
			"presentation layer pyqtgraph \n"
			"is used to select pyqtgraph as the presentation layer.",
			"Settings - layout options": "Settings - layout options is "
			"used to set a few parameters to be used in reports.",
			"Shepard": "Shepard is used to create a Shepard diagram.\n"
			"The user is asked which axis to use for similarities.\n"
			"The other axis will be used for distances.\n"
			"Depending on whether the measures represent \n"
			"similarities or dissimilarities and which axis is used to \n"
			"display similarities, a line will rise or descend from \n"
			"left to right. Each point on the line represents the \n"
			"distance between a pair of items and their corresponding \n"
			"similarity measure.",
			"Similarities": "Similarities reads in a similarity matrix.\n"
			"The similarities reflect how similar each item "
			"is to each other. \n"
			"If an active configuration has been established, "
			"the number of items must match the number of points.\n"
			"The user is asked for a file name.\n"
			"The file must be formatted correctly.\n"
			"The first line should be Lower triangular.\n"
			"The next line should have one field, the number or items:\n"
			"For each item:\n"
			"\tA line containing the label, a semicolon, and the "
			"full name for that item.\n"
			"For each item i from 2 to n:\n"
			"\tA line with the similarity between item i and each of the "
			"previous items 1 to i-1 separated by commas.\n",
			"Status": "Status displays the current status of the program.",
			"Stress contribution": "Stress contribution is used to identify "
			"points that \ncontribute most to stress.",
			"Target": "Target estabishes a target configuration.\n"
			"The target configuration may be used to compare with the "
			"active "
			"configuration by performing a Proscrustean rotation to "
			"orient it \n"
			"as closely as possible to the target configuraion.",
			"Terse": "Terse sets the verbosity level to terse.\n"
			"At this level, explanations of what each command does will "
			"not be provided.",
			"Uncertainty": "Uncertainty uses the sample repetitions to create"
			"a plot \n"
			"showing uncertainty in the location of points.\n",
			"Undo": "Undo undoes the last action.",
			"Varimax": "Varimax performs a varimax rotation of the active "
			"configuration.",
			"Vectors": "Vectors creates a plot with vectors from the origin"
			" to each point.",
			"Verbose": "Verbose sets the verbosity level to verbose.\n"
			"At this level, explanations of what each command does will "
			"be provided.",
			"View configuration": "View configuration is used to view "
			"the active configuration.",
			"View correlations": "View correlations is used to view "
			"the active correlations.",
			"View custom": "View custom is used to view a custom matrix.",
			"View distances": "View distances is used to view the active "
			"distances.",
			"View evaluations": "View evaluations is used to view the active "
			"evaluations.",
			"View grouped data": "View grouped data is used to view the "
			"active grouped data.",
			"View individuals": "View individuals is used to view the "
			"active individuals.",
			"View point uncertainty": "View point uncertainty is used to "
			"display the uncertainty of a single point in the "
			"current solution.",
			"View sample design": "View sample design is used to view the "
			"active sample design.",
			"View sample repetitions": "View sample repetitions is used to "
			"view the active sample repetitions.",
			"View sample solutions": "View sample solutions is used to "
			"view the active sample solutions.",
			"View scores": "View scores is used to view the active scores.",
			"View similarities": "View similarities is used to view the "
			"active similarities.",
			"View spatial uncertainty": "View spatial uncertainty is used to "
			"display the uncertainty of all points in the current "
			"solution.",
			"View target": "View target is used to view the active target.",
		}
		msg = explain_dict[self.command]

		return msg

	# ------------------------------------------------------------------------

	def abandon_configuration(self) -> None:
		self.common.hor_dim = 0
		self.common.vert_dim = 1
		self.configuration_active.ndim = 0
		self.configuration_active.npoint = 0
		self.configuration_active.dim_labels.clear()
		self.configuration_active.dim_names.clear()
		self.configuration_active.point_labels.clear()
		self.configuration_active.point_names.clear()
		self.configuration_active.point_coords = pd.DataFrame()
		self.configuration_active.distances.clear()
		if self.common.have_reference_points():
			self.rivalry.rival_a = Point()
			self.rivalry.rival_b = Point()
			# self.rivalry.rival_a.index = None
			# self.rivalry.rival_b.index = None
			self.rivalry.seg = pd.DataFrame()
			# self.rivalry.bisector.case = "Unknown"
			# self.rivalry.bisector.direction = "Unknown"

		return

	# ------------------------------------------------------------------------

	def abandon_correlations(self) -> None:
		self.correlations_active.correlations = []
		self.correlations_active.correlations_as_dict = {}
		self.correlations_active.correlations_as_list.clear()
		self.correlations_active.correlations_as_square.clear()
		self.correlations_active.correlations_as_dataframe = pd.DataFrame()
		# self.correlations_active.sorted_correlations_w_pairs.clear()
		return

	# ------------------------------------------------------------------------

	def abandon_evaluations(self) -> None:
		self.evaluations_active.evaluations = pd.DataFrame()
		return

	# ------------------------------------------------------------------------

	def abandon_grouped_data(self) -> None:
		self.grouped_data_active.dim_labels.clear()
		self.grouped_data_active.dim_names.clear()
		self.grouped_data_active.group_labels.clear()
		self.grouped_data_active.group_names.clear()
		self.grouped_data_active.group_coords = pd.DataFrame()
		return

	# ----------------------------------------------------------------------

	def abandon_individual_data(self) -> None:
		self.individuals_active.ind_vars = pd.DataFrame()
		return

	# ------------------------------------------------------------------------

	def abandon_reference_points(self) -> None:
		self.rival_a = Point()
		self.rival_b = Point()
		# self.rival_a.index = None
		# self.rival_b.index = None
		# self.configuration_active.bisector = Line()
		# self.configuration_active.west = Line()
		# self.configuration_active.east = Line()
		# self.configuration_active.connector = Line()
		self.seg = pd.DataFrame()

		return

	# ------------------------------------------------------------------------

	def abandon_scores(self) -> None:
		self.scores_active.scores = pd.DataFrame()
		return

	# ------------------------------------------------------------------------

	def abandon_similarities(self) -> None:
		self.similarities_active.similarities.clear()
		self.similarities_active.similarities_as_dict = {}
		self.similarities_active.similarities_as_list.clear()
		self.similarities_active.similarities_as_square.clear()
		self.similarities_active.similarities_as_dataframe = pd.DataFrame()
		self.similarities_active.sorted_similarities = {}
		self.similarities_active.sorted_similarities_w_pairs.clear()
		return

	# ------------------------------------------------------------------------

	def abandon_target(self) -> None:
		from features import TargetFeature  # noqa: PLC0415

		self.target_active = TargetFeature(self)

		return

	# ------------------------------------------------------------------------

	def get_file_name_and_handle_nonexistent_file_names_init_variables(
		self,
	) -> None:
		self.empty_response_title = "Empty response"
		self.empty_response_message = (
			"A file name is needed, select file in dialog."
		)

	# ------------------------------------------------------------------------

	def get_file_name_and_handle_nonexistent_file_names(
		self, file_caption: str, file_filter: str
	) -> str:
		self.get_file_name_and_handle_nonexistent_file_names_init_variables()
		ui_file = QFileDialog.getOpenFileName(
			dir=os.fspath(self.filedir),
			caption=file_caption,
			filter=file_filter,
		)
		file = ui_file[0]
		if len(file) == 0:
			raise SpacesError(
				self.empty_response_title, self.empty_response_message
			)
		return file

	# ------------------------------------------------------------------------

	def get_file_name_to_store_file_initialize_variables(self) -> None:
		self.empty_response_title = "Empty response"
		self.empty_response_message = (
			"A file name is needed, select file in dialog."
		)

	# ------------------------------------------------------------------------

	def get_file_name_to_store_file(
		self, dialog_caption: str, dialog_filter: str
	) -> str:
		# dropped positional arguments message and feedback

		self.get_file_name_to_store_file_initialize_variables()

		file_name, _ = QFileDialog.getSaveFileName(
			None, caption=dialog_caption, filter=dialog_filter
		)

		# Debug: Log the filename returned from the dialog
		print(f"DEBUG: QFileDialog returned filename: '{file_name}'")
		print(f"DEBUG: filename type: {type(file_name)}")
		print(f"DEBUG: filename length: {len(file_name)}")

		if len(file_name) == 0:
			raise SpacesError(
				self.empty_response_title, self.empty_response_message
			)

		# Debug: Log the filename being returned
		print(f"DEBUG: Returning filename: '{file_name}'")
		return file_name

	# ------------------------------------------------------------------------

	def set_focus_on_tab(self, tab_name: str) -> None:
		tab_dict = {
			"Plot": 0,
			"Output": 1,
			"Gallery": 2,
			"Log": 3,
			"Record": 4,
		}

		tab_index = tab_dict[tab_name]

		self.tab_widget.setCurrentIndex(tab_index)
		self.tab_widget.update()
		return

	# ------------------------------------------------------------------------

	def create_widgets_for_output_and_log_tabs(self) -> None:
		_tab_output_layout = self.tab_output_layout
		_tab_log_layout = self.tab_log_layout

		for i in reversed(range(_tab_output_layout.count())):
			_tab_output_layout.itemAt(i).widget().setParent(None)
		table_to_output = BuildOutputForGUI(self)
		_tab_output_layout.addWidget(table_to_output)
		table_to_log = BuildOutputForGUI(self)
		spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Fixed)
		# Adjust size as needed
		_tab_log_layout.addItem(spacer)
		_tab_log_layout.addWidget(table_to_log)

		self.tab_output_layout = _tab_output_layout
		self.tab_log_layout = _tab_log_layout

		return

	# ------------------------------------------------------------------------

	def unable_to_complete_command_set_status_as_failed(self) -> None:
		# changes last exit code from in process to 1 indicating command failed
		#
		command_exit_code = self.command_exit_code
		command = self.command
		undo_stack = self.undo_stack
		undo_stack_source = self.undo_stack_source

		command_exit_code[-1] = 1
		self.spaces_statusbar.showMessage(
			f"Unable to complete {command} command", 80000
		)
		print(f"Unable to complete {command} command")
		#
		# eliminate last entry to undo stack
		#
		if len(undo_stack) != 1:
			del undo_stack[-1]
			del undo_stack_source[-1]

		self.command_exit_code = command_exit_code
		self.undo_stack = undo_stack
		self.undo_stack_source = undo_stack_source

		return

	# ------------------------------------------------------------------------

	def record_command_as_successfully_completed(self) -> None:
		"""The Complete command is used to indicate the end of a command.
		It is called at the end of each command.
		"""
		# changes last exit code from in process to success
		#

		command = self.command
		command_exit_code = self.command_exit_code

		command_exit_code[-1] = 0
		self.spaces_statusbar.showMessage(
			f"Completed {command} command", 80000
		)
		print(f"\nSuccessfully completed {command} command.")

		self.command = command
		self.command_exit_code = command_exit_code

		return

	# ------------------------------------------------------------------------

	def print_the_configuration(self) -> None:
		ndim = self.configuration_active.ndim
		npoint = self.configuration_active.npoint
		# _point_coords = self.configuration_active.point_coords
		print(f"\n\tConfiguration has {ndim} dimensions and {npoint} points\n")
		self.configuration_active.point_coords.style.format(
			precision=3, thousands=",", decimal="."
		)
		self.configuration_active.print_active_function()
		return

	# ------------------------------------------------------------------------

	def include_explanation_when_verbosity_last_set_to_verbose(self) -> bool:
		if (
			len(self.commands_used) > 0
			and self.commands_used[0] == "Verbose"
			and len(self.commands_used) == 1
		):
			return True
		for i in reversed(range(len(self.commands_used))):
			match self.commands_used[i]:
				case "Terse":
					return False
				case "Verbose":
					return True
				case _:
					continue
		return False


# --------------------------------------------------------------------------


class EstablishSpacesStructure:
	def __init__(self, parent: Status) -> None:
		self.parent = parent
		self.common: Spaces = Spaces(parent, parent)
		self.current_command: Spaces = Spaces(parent, parent)
		self.commands_used: list[str] = ["Initialize"]
		self.command_exit_code: list[int] = [0]
		self.command: str = ""
		self.undo_stack: list[int] = [0]
		self.undo_stack_source: list[str] = ["Initialize"]
		self.deactivated_items: list[str] = []
		self.deactivated_descriptions: list[str] = []
		# self.rivalry = Rivalry(parent, self.command)
		self.basedir = Path(__file__).parent
		# self.dir = Path.cwd()
		self.dir = Path.cwd().parent
		self.filedir = self.dir / "genesis" / "data" / "Elections"


# --------------------------------------------------------------------------


class BuildTrafficDict:
	def __init__(self, parent: Status) -> None:
		"""Build the traffic dictionary for the Spaces application."""

		from associationsmenu import (  # noqa: PLC0415
			AlikeCommand,
			DistancesCommand,
			LineOfSightCommand,
			PairedCommand,
			RanksDifferencesCommand,
			RanksDistancesCommand,
			RanksSimilaritiesCommand,
			ScreeCommand,
			ShepardCommand,
			StressContributionCommand,
		)

		from editmenu import (  # noqa: PLC0415
			RedoCommand,
			UndoCommand,
		)

		# from features import (
		# 	ConfigurationFeature,
		# 	CorrelationsFeature,
		# 	EvaluationsFeature,
		# 	GroupedDataFeature,
		# 	IndividualsFeature,
		# 	ScoresFeature,
		# 	SimilaritiesFeature,
		# 	TargetFeature
		# )
		from filemenu import (  # noqa: PLC0415
			ConfigurationCommand,
			CorrelationsCommand,
			CreateCommand,
			DeactivateCommand,
			EvaluationsCommand,
			ExitCommand,
			GroupedDataCommand,
			IndividualsCommand,
			NewGroupedDataCommand,
			OpenSampleDesignCommand,
			OpenSampleRepetitionsCommand,
			OpenSampleSolutionsCommand,
			OpenScoresCommand,
			PrintConfigurationCommand,
			PrintCorrelationsCommand,
			PrintEvaluationsCommand,
			PrintGroupedDataCommand,
			PrintIndividualsCommand,
			PrintSampleDesignCommand,
			PrintSampleRepetitionsCommand,
			PrintSampleSolutionsCommand,
			PrintScoresCommand,
			PrintSimilaritiesCommand,
			PrintTargetCommand,
			SaveConfigurationCommand,
			SaveCorrelationsCommand,
			SaveIndividualsCommand,
			SaveSampleDesignCommand,
			SaveSampleRepetitionsCommand,
			SaveSampleSolutionsCommand,
			SaveScoresCommand,
			SaveSimilaritiesCommand,
			SaveTargetCommand,
			SettingsDisplayCommand,
			SettingsLayoutCommand,
			SettingsPlaneCommand,
			SettingsPlotCommand,
			SettingsPresentationLayerCommand,
			SettingsSegmentCommand,
			SettingsVectorSizeCommand,
			SimilaritiesCommand,
			TargetCommand,
		)
		from helpmenu import (  # noqa: PLC0415
			AboutCommand,
			HelpCommand,
			StatusCommand,
			TerseCommand,
			VerboseCommand,
		)
		from modelmenu import (  # noqa: PLC0415
			ClusterCommand,
			DirectionsCommand,
			FactorAnalysisCommand,
			FactorAnalysisMachineLearningCommand,
			MDSCommand,
			PrincipalComponentsCommand,
			UncertaintyCommand,
			VectorsCommand,
		)
		from respondentsmenu import (  # noqa: PLC0415
			BaseCommand,
			BattlegroundCommand,
			ContestCommand,
			ConvertibleCommand,
			CoreSupportersCommand,
			FirstDimensionCommand,
			JointCommand,
			LikelySupportersCommand,
			ReferencePointsCommand,
			SampleDesignerCommand,
			SampleRepetitionsCommand,
			ScoreIndividualsCommand,
			SecondDimensionCommand,
			SegmentsCommand,
		)

		from transformmenu import (  # noqa: PLC0415
			CompareCommand,
			CenterCommand,
			InvertCommand,
			MoveCommand,
			RescaleCommand,
			RotateCommand,
			VarimaxCommand,
		)
		from viewmenu import (  # noqa: PLC0415
			HistoryCommand,
			ViewConfigurationCommand,
			ViewCorrelationsCommand,
			ViewCustomCommand,
			ViewDistancesCommand,
			ViewEvaluationsCommand,
			ViewGroupedDataCommand,
			ViewIndividualsCommand,
			ViewPointUncertaintyCommand,
			ViewSampleDesignCommand,
			ViewSampleRepetitionsCommand,
			ViewSampleSolutionsCommand,
			ViewScoresCommand,
			ViewSimilaritiesCommand,
			ViewSpatialUncertaintyCommand,
			ViewTargetCommand,
			# ViewUncertaintyCommand
		)

		self.parent = parent
		self.common: Spaces = Spaces(parent, parent)

		self.traffic_dict = {
			"new_configuration": (CreateCommand, None),
			"new_grouped_data": (NewGroupedDataCommand, None),
			"open_configuration": (ConfigurationCommand, None),
			"open_target": (TargetCommand, None),
			"open_grouped_data": (GroupedDataCommand, None),
			"open_similarities_dissimilarities": (
				SimilaritiesCommand,
				"dissimilarities",
			),
			"open_similarities_similarities": (
				SimilaritiesCommand,
				"similarities",
			),
			"open_correlations": (CorrelationsCommand, None),
			"open_evaluations": (EvaluationsCommand, None),
			"open_individuals": (IndividualsCommand, None),
			"open_scores": (OpenScoresCommand, None),
			"open_sample_design": (OpenSampleDesignCommand, None),
			"open_sample_repetitions": (OpenSampleRepetitionsCommand, None),
			"open_sample_solutions": (OpenSampleSolutionsCommand, None),
			"save_configuration": (SaveConfigurationCommand, None),
			"save_target": (SaveTargetCommand, None),
			"save_correlations": (SaveCorrelationsCommand, None),
			"save_similarities": (SaveSimilaritiesCommand, None),
			"save_individuals": (SaveIndividualsCommand, None),
			"save_scores": (SaveScoresCommand, None),
			"save_sample_design": (SaveSampleDesignCommand, None),
			"save_sample_repetitions": (SaveSampleRepetitionsCommand, None),
			"save_sample_solutions": (SaveSampleSolutionsCommand, None),
			"deactivate": (DeactivateCommand, None),
			"settings_plot": (SettingsPlotCommand, None),
			"settings_plane": (SettingsPlaneCommand, None),
			"settings_segment": (SettingsSegmentCommand, None),
			"settings_display": (SettingsDisplayCommand, None),
			"settings_vector": (SettingsVectorSizeCommand, None),
			"settings_presentation_matplotlib": (
				SettingsPresentationLayerCommand,
				"Matplotlib",
			),
			"settings_presentation_pyqtgraph": (
				SettingsPresentationLayerCommand,
				"PyQtGraph",
			),
			"settings_layout": (SettingsLayoutCommand, None),
			"print_configuration": (PrintConfigurationCommand, None),
			"print_target": (PrintTargetCommand, None),
			"print_grouped_data": (PrintGroupedDataCommand, None),
			"print_correlations": (PrintCorrelationsCommand, None),
			"print_similarities": (PrintSimilaritiesCommand, None),
			"print_evaluations": (PrintEvaluationsCommand, None),
			"print_individuals": (PrintIndividualsCommand, None),
			"print_scores": (PrintScoresCommand, None),
			"print_sample_design": (PrintSampleDesignCommand, None),
			"print_sample_repetitions": (PrintSampleRepetitionsCommand, None),
			"print_sample_solutions": (PrintSampleSolutionsCommand, None),
			"exit": (ExitCommand, None),
			"undo": (UndoCommand, None),
			"redo": (RedoCommand, None),
			"view_configuration": (ViewConfigurationCommand, None),
			"view_target": (ViewTargetCommand, None),
			"view_grouped": (ViewGroupedDataCommand, None),
			"view_similarities": (ViewSimilaritiesCommand, None),
			"view_correlations": (ViewCorrelationsCommand, None),
			"view_distances": (ViewDistancesCommand, None),
			"view_evaluations": (ViewEvaluationsCommand, None),
			"view_individuals": (ViewIndividualsCommand, None),
			"view_scores": (ViewScoresCommand, None),
			"view_sample_design": (ViewSampleDesignCommand, None),
			"view_sample_repetitions": (ViewSampleRepetitionsCommand, None),
			"view_sample_solutions": (ViewSampleSolutionsCommand, None),
			"view_spatial_uncertainty_lines": (
				ViewSpatialUncertaintyCommand,
				"lines",
			),
			"view_spatial_uncertainty_boxes": (
				ViewSpatialUncertaintyCommand,
				"boxes",
			),
			"view_spatial_uncertainty_ellipses": (
				ViewSpatialUncertaintyCommand,
				"ellipses",
			),
			"view_spatial_uncertainty_circles": (
				ViewSpatialUncertaintyCommand,
				"circles",
			),
			"view_point_uncertainty_lines": (
				ViewPointUncertaintyCommand,
				"lines",
			),
			"view_point_uncertainty_boxes": (
				ViewPointUncertaintyCommand,
				"boxes",
			),
			"view_point_uncertainty_ellipses": (
				ViewPointUncertaintyCommand,
				"ellipses",
			),
			"view_point_uncertainty_circles": (
				ViewPointUncertaintyCommand,
				"circles",
			),
			"history": (HistoryCommand, None),
			"view_custom": (ViewCustomCommand, None),
			"center": (CenterCommand, None),
			"move": (MoveCommand, None),
			"invert": (InvertCommand, None),
			"rescale": (RescaleCommand, None),
			"rotate": (RotateCommand, None),
			"compare": (CompareCommand, None),
			"varimax": (VarimaxCommand, None),
			"correlations": (ViewCorrelationsCommand, None),
			"similarities": (ViewSimilaritiesCommand, None),
			"paired": (PairedCommand, None),
			"line_of_sight": (LineOfSightCommand, None),
			"alike": (AlikeCommand, None),
			"cluster": (ClusterCommand, None),
			"distances": (DistancesCommand, None),
			"ranks_distances": (RanksDistancesCommand, None),
			"ranks_similarities": (RanksSimilaritiesCommand, None),
			"ranks_differences": (RanksDifferencesCommand, None),
			"scree": (ScreeCommand, None),
			"shepard_similarities_on_x": (ShepardCommand, "X"),
			"shepard_similarities_on_y": (ShepardCommand, "Y"),
			"stress_contribution": (StressContributionCommand, None),
			"principal": (PrincipalComponentsCommand, None),
			"factor_analysis": (FactorAnalysisCommand, None),
			"factor_analysis_machine_learning": (
				FactorAnalysisMachineLearningCommand,
				None,
			),
			"mds": (MDSCommand, None),
			"mds_metric": (MDSCommand, True),
			"mds_non_metric": (MDSCommand, False),
			"vectors": (VectorsCommand, None),
			"directions": (DirectionsCommand, None),
			"uncertainty": (UncertaintyCommand, None),
			"evaluations": (ViewEvaluationsCommand, None),
			"sample_designer": (SampleDesignerCommand, None),
			"sample_repetitions": (SampleRepetitionsCommand, None),
			"score_individuals": (ScoreIndividualsCommand, None),
			"joint": (JointCommand, None),
			"reference_points": (ReferencePointsCommand, None),
			"contest": (ContestCommand, None),
			"segments": (SegmentsCommand, None),
			"core_regions": (CoreSupportersCommand, "regions"),
			"core_left": (CoreSupportersCommand, "left"),
			"core_right": (CoreSupportersCommand, "right"),
			"core_both": (CoreSupportersCommand, "both"),
			"core_neither": (CoreSupportersCommand, "neither"),
			"base_regions": (BaseCommand, "regions"),
			"base_left": (BaseCommand, "left"),
			"base_right": (BaseCommand, "right"),
			"base_both": (BaseCommand, "both"),
			"base_neither": (BaseCommand, "neither"),
			"likely_regions": (LikelySupportersCommand, "regions"),
			"likely_left": (LikelySupportersCommand, "left"),
			"likely_right": (LikelySupportersCommand, "right"),
			"likely_both": (LikelySupportersCommand, "both"),
			"convertible_regions": (ConvertibleCommand, "regions"),
			"convertible_left": (ConvertibleCommand, "left"),
			"convertible_right": (ConvertibleCommand, "right"),
			"convertible_both": (ConvertibleCommand, "both"),
			"convertible_settled": (ConvertibleCommand, "settled"),
			"battleground_regions": (BattlegroundCommand, "regions"),
			"battleground_segment": (BattlegroundCommand, "battleground"),
			"battleground_settled": (BattlegroundCommand, "settled"),
			"first_regions": (FirstDimensionCommand, "regions"),
			"first_left": (FirstDimensionCommand, "left"),
			"first_right": (FirstDimensionCommand, "right"),
			"second_regions": (SecondDimensionCommand, "regions"),
			"second_upper": (SecondDimensionCommand, "upper"),
			"second_lower": (SecondDimensionCommand, "lower"),
			"help_content": (HelpCommand, None),
			"status": (StatusCommand, None),
			"about": (AboutCommand, None),
			"terse": (TerseCommand, None),
			"verbose": (VerboseCommand, None),
			"tester": (TesterCommand, None),
		}
		# peek(len(self.traffic_dict))


# --------------------------------------------------------------------------


class BuildWidgetDict:
	def __init__(self, parent: Status) -> None:
		from associationsmenu import (  # noqa: PLC0415
			AlikeCommand,
			DistancesCommand,
			LineOfSightCommand,
			PairedCommand,
			RanksDifferencesCommand,
			RanksDistancesCommand,
			RanksSimilaritiesCommand,
			ScreeCommand,
			ShepardCommand,
			StressContributionCommand,
		)
		from editmenu import (  # noqa: PLC0415
			RedoCommand,
			UndoCommand,
		)
		from filemenu import (  # noqa: PLC0415
			ConfigurationCommand,
			CorrelationsCommand,
			CreateCommand,
			DeactivateCommand,
			EvaluationsCommand,
			# ExitCommand,
			GroupedDataCommand,
			IndividualsCommand,
			NewGroupedDataCommand,
			OpenSampleDesignCommand,
			OpenSampleRepetitionsCommand,
			OpenSampleSolutionsCommand,
			OpenScoresCommand,
			PrintConfigurationCommand,
			PrintCorrelationsCommand,
			PrintEvaluationsCommand,
			PrintGroupedDataCommand,
			PrintIndividualsCommand,
			PrintSampleDesignCommand,
			PrintSampleRepetitionsCommand,
			# PrintSampleSolutionsCommand,
			PrintScoresCommand,
			PrintSimilaritiesCommand,
			PrintTargetCommand,
			SaveConfigurationCommand,
			SaveCorrelationsCommand,
			SaveIndividualsCommand,
			SaveSampleDesignCommand,
			SaveSampleRepetitionsCommand,
			SaveSampleSolutionsCommand,
			SaveScoresCommand,
			SaveSimilaritiesCommand,
			SaveTargetCommand,
			SettingsDisplayCommand,
			SettingsLayoutCommand,
			SettingsPlaneCommand,
			SettingsPlotCommand,
			SettingsPresentationLayerCommand,
			SettingsSegmentCommand,
			SettingsVectorSizeCommand,
			SimilaritiesCommand,
			TargetCommand,
		)
		from helpmenu import (  # noqa: PLC0415
			AboutCommand,
			HelpCommand,
			StatusCommand,
			TerseCommand,
			VerboseCommand,
		)
		from modelmenu import (  # noqa: PLC0415
			ClusterCommand,
			DirectionsCommand,
			FactorAnalysisCommand,
			FactorAnalysisMachineLearningCommand,
			MDSCommand,
			PrincipalComponentsCommand,
			UncertaintyCommand,
			VectorsCommand,
		)
		from respondentsmenu import (  # noqa: PLC0415
			BaseCommand,
			BattlegroundCommand,
			ContestCommand,
			ConvertibleCommand,
			CoreSupportersCommand,
			FirstDimensionCommand,
			JointCommand,
			LikelySupportersCommand,
			ReferencePointsCommand,
			SampleDesignerCommand,
			SampleRepetitionsCommand,
			ScoreIndividualsCommand,
			SecondDimensionCommand,
			SegmentsCommand,
		)

		from transformmenu import (  # noqa: PLC0415
			CompareCommand,
			CenterCommand,
			InvertCommand,
			MoveCommand,
			RescaleCommand,
			RotateCommand,
			VarimaxCommand,
		)
		from viewmenu import (  # noqa: PLC0415
			HistoryCommand,
			ViewConfigurationCommand,
			ViewCorrelationsCommand,
			ViewCustomCommand,
			ViewDistancesCommand,
			ViewEvaluationsCommand,
			ViewGroupedDataCommand,
			ViewIndividualsCommand,
			ViewPointUncertaintyCommand,
			ViewSampleDesignCommand,
			ViewSampleRepetitionsCommand,
			ViewSampleSolutionsCommand,
			ViewScoresCommand,
			ViewSimilaritiesCommand,
			ViewSpatialUncertaintyCommand,
			ViewTargetCommand,
		)

		self.parent = parent
		self.common: Spaces = Spaces(parent, parent)

		# self.table_widget: object
		self.title_for_table_widget: str = ""
		self.output_widget_type: str = ""
		self.widget_dict = {
			"About": [AboutCommand, "unique", None],
			"Alike": [
				AlikeCommand,
				"shared",
				lambda: parent.statistics.display_table("alike"),
			],
			"Base": [
				BaseCommand,
				"shared",
				lambda: parent.rivalry_tables.display_table("base"),
			],
			"Battleground": [
				BattlegroundCommand,
				"shared",
				lambda: parent.rivalry_tables.display_table("battleground"),
			],
			"Center": [
				CenterCommand,
				"shared",
				lambda: parent.tables.display_table("configuration"),
			],
			"Cluster": [ClusterCommand, "unique", None],
			"Compare": [
				CompareCommand,
				"shared",
				lambda: parent.statistics.display_table("compare"),
			],
			"Configuration": [
				ConfigurationCommand,
				"shared",
				lambda: parent.tables.display_table("configuration"),
			],
			"Contest": [ContestCommand, "shared", parent.display_a_line],
			"Convertible": [
				ConvertibleCommand,
				"shared",
				lambda: parent.rivalry_tables.display_table("convertible"),
			],
			"Core supporters": [
				CoreSupportersCommand,
				"shared",
				lambda: parent.rivalry_tables.display_table("core"),
			],
			"Correlations": [
				CorrelationsCommand,
				"shared",
				lambda: parent.squares.display_table("correlations"),
			],
			"Create": [
				CreateCommand,
				"shared",
				lambda: parent.tables.display_table("configuration"),
			],
			"Deactivate": [DeactivateCommand, "unique", None],
			"Directions": [
				DirectionsCommand,
				"shared",
				lambda: parent.statistics.display_table("directions"),
			],
			"Distances": [
				DistancesCommand,
				"shared",
				lambda: parent.squares.display_table("distances"),
			],
			"Evaluations": [
				EvaluationsCommand,
				"shared",
				lambda: parent.statistics.display_table("evaluations"),
			],
			"Factor analysis": [
				FactorAnalysisCommand,
				"shared",
				lambda: parent.statistics.display_table("factor_analysis"),
			],
			"Factor analysis machine learning": [
				FactorAnalysisMachineLearningCommand,
				"unique",
				None,
			],
			"First dimension": [
				FirstDimensionCommand,
				"shared",
				lambda: parent.rivalry_tables.display_table("first"),
			],
			"Grouped data": [
				GroupedDataCommand,
				"shared",
				lambda: parent.tables.display_table("grouped_data"),
			],
			"Help": [HelpCommand, "shared", parent.display_coming_soon],
			"History": [HistoryCommand, "unique", None],
			"Individuals": [
				IndividualsCommand,
				"shared",
				lambda: parent.statistics.display_table("individuals"),
			],
			"Invert": [
				InvertCommand,
				"shared",
				lambda: parent.tables.display_table("configuration"),
			],
			"Joint": [JointCommand, "shared", parent.display_a_line],
			"Likely supporters": [
				LikelySupportersCommand,
				"shared",
				lambda: parent.rivalry_tables.display_table("likely"),
			],
			"Line of sight": [
				LineOfSightCommand,
				"shared",
				lambda: parent.squares.display_table("similarities"),
			],
			"MDS": [
				MDSCommand,
				"shared",
				lambda: parent.tables.display_table("configuration"),
			],
			"Move": [
				MoveCommand,
				"shared",
				lambda: parent.tables.display_table("configuration"),
			],
			"New grouped data": [
				NewGroupedDataCommand,
				"shared",
				lambda: parent.tables.display_table("grouped_data"),
			],
			"Open correlations": [
				CorrelationsCommand,
				"shared",
				lambda: parent.squares.display_table("correlations"),
			],
			"Open scores": [
				OpenScoresCommand,
				"shared",
				lambda: parent.statistics.display_table("scores"),
			],
			"Open sample design": [
				OpenSampleDesignCommand,
				"shared",
				lambda: parent.statistics.display_table("sample_design"),
			],
			"Open sample repetitions": [
				OpenSampleRepetitionsCommand,
				"shared",
				lambda: parent.statistics.display_table("sample_repetitions"),
			],
			"Open sample solutions": [
				OpenSampleSolutionsCommand,
				"unique",
				None,
			],
			"Paired": [PairedCommand, "unique", None],
			"Principal components": [
				PrincipalComponentsCommand,
				"shared",
				lambda: parent.tables.display_table("configuration"),
			],
			"Print configuration": [
				PrintConfigurationCommand,
				"shared",
				lambda: parent.tables.display_table("configuration"),
			],
			"Print correlations": [
				PrintCorrelationsCommand,
				"shared",
				lambda: parent.squares.display_table("correlations"),
			],
			"Print evaluations": [
				PrintEvaluationsCommand,
				"shared",
				lambda: parent.statistics.display_table("evaluations"),
			],
			"Print grouped data": [
				PrintGroupedDataCommand,
				"shared",
				lambda: parent.tables.display_table("grouped_data"),
			],
			"Print individuals": [
				PrintIndividualsCommand,
				"shared",
				lambda: parent.statistics.display_table("individuals"),
			],
			"Print sample design": [
				PrintSampleDesignCommand,
				"shared",
				lambda: parent.statistics.display_table("sample_design"),
			],
			"Print sample repetitions": [
				PrintSampleRepetitionsCommand,
				"shared",
				lambda: parent.statistics.display_table("sample_repetitions"),
			],
			"Print similarities": [
				PrintSimilaritiesCommand,
				"shared",
				lambda: parent.squares.display_table("similarities"),
			],
			"Print scores": [
				PrintScoresCommand,
				"shared",
				lambda: parent.statistics.display_table("scores"),
			],
			"Print target": [
				PrintTargetCommand,
				"shared",
				lambda: parent.tables.display_table("target"),
			],
			"Ranks distances": [
				RanksDistancesCommand,
				"shared",
				lambda: parent.squares.display_table("ranked_distances"),
			],
			"Ranks similarities": [
				RanksSimilaritiesCommand,
				"shared",
				lambda: parent.squares.display_table("ranked_similarities"),
			],
			"Ranks differences": [
				RanksDifferencesCommand,
				"shared",
				lambda: parent.squares.display_table("ranked_differences"),
			],
			"Redo": [RedoCommand, "shared", parent.display_coming_soon],
			"Reference points": [
				ReferencePointsCommand,
				"shared",
				parent.display_a_line,
			],
			"Rescale": [
				RescaleCommand,
				"shared",
				lambda: parent.tables.display_table("configuration"),
			],
			"Rotate": [
				RotateCommand,
				"shared",
				lambda: parent.tables.display_table("configuration"),
			],
			"Sample designer": [
				SampleDesignerCommand,
				"shared",
				lambda: parent.statistics.display_table("sample_design"),
			],
			"Sample repetitions": [
				SampleRepetitionsCommand,
				"shared",
				lambda: parent.statistics.display_table("sample_repetitions"),
			],
			"Save configuration": [
				SaveConfigurationCommand,
				"shared",
				lambda: parent.tables.display_table("configuration"),
			],
			"Save target": [
				SaveTargetCommand,
				"shared",
				lambda: parent.tables.display_table("target"),
			],
			"Save correlations": [
				SaveCorrelationsCommand,
				"shared",
				lambda: parent.squares.display_table("correlations"),
			],
			"Save similarities": [
				SaveSimilaritiesCommand,
				"shared",
				lambda: parent.squares.display_table("similarities"),
			],
			"Save individuals": [
				SaveIndividualsCommand,
				"shared",
				lambda: parent.statistics.display_table("individuals"),
			],
			"Save scores": [
				SaveScoresCommand,
				"shared",
				lambda: parent.statistics.display_table("scores"),
			],
			"Save sample design": [
				SaveSampleDesignCommand,
				"shared",
				lambda: parent.statistics.display_table("sample_design"),
			],
			"Save sample repetitions": [
				SaveSampleRepetitionsCommand,
				"shared",
				lambda: parent.statistics.display_table("sample_repetitions"),
			],
			"Save sample solutions": [
				SaveSampleSolutionsCommand,
				"shared",
				None,
			],
			"Score individuals": [
				ScoreIndividualsCommand,
				"shared",
				lambda: parent.statistics.display_table("scores"),
			],
			"Scree": [
				ScreeCommand,
				"shared",
				lambda: parent.statistics.display_table("scree"),
			],
			"Second dimension": [
				SecondDimensionCommand,
				"shared",
				lambda: parent.rivalry_tables.display_table("second"),
			],
			"Segments": [
				SegmentsCommand,
				"shared",
				lambda: parent.rivalry_tables.display_table("segments"),
			],
			"Settings - plot settings": [SettingsPlotCommand, "unique", None],
			"Settings - plane": [SettingsPlaneCommand, "unique", None],
			"Settings - segment sizing": [
				SettingsSegmentCommand,
				"unique",
				None,
			],
			"Settings - display sizing": [
				SettingsDisplayCommand,
				"unique",
				None,
			],
			"Settings - vector sizing": [
				SettingsVectorSizeCommand,
				"unique",
				None,
			],
			"Settings - presentation layer": [
				SettingsPresentationLayerCommand,
				"shared",
				parent.display_a_line,
			],
			"Settings - layout options": [
				SettingsLayoutCommand,
				"unique",
				None,
			],
			"Shepard": [
				ShepardCommand,
				"shared",
				lambda: parent.squares.display_table("shepard"),
			],
			"Similarities": [
				SimilaritiesCommand,
				"shared",
				lambda: parent.squares.display_table("similarities"),
			],
			"Status": [StatusCommand, "unique", None],
			"Stress contribution": [
				StressContributionCommand,
				"shared",
				lambda: parent.statistics.display_table("stress_contribution"),
			],
			"Target": [
				TargetCommand,
				"shared",
				lambda: parent.tables.display_table("target"),
			],
			"Terse": [TerseCommand, "shared", parent.display_a_line],
			"Uncertainty": [
				UncertaintyCommand,
				"shared",
				lambda: parent.statistics.display_table("uncertainty"),
			],
			"Undo": [UndoCommand, "shared", parent.display_coming_soon],
			"Varimax": [
				VarimaxCommand,
				"shared",
				lambda: parent.tables.display_table("configuration"),
			],
			"Vectors": [
				VectorsCommand,
				"shared",
				lambda: parent.tables.display_table("configuration"),
			],
			"Verbose": [VerboseCommand, "shared", parent.display_a_line],
			"View configuration": [
				ViewConfigurationCommand,
				"shared",
				lambda: parent.tables.display_table("configuration"),
			],
			"View correlations": [
				ViewCorrelationsCommand,
				"shared",
				lambda: parent.squares.display_table("correlations"),
			],
			"View custom": [ViewCustomCommand, "unique", None],
			"View distances": [
				ViewDistancesCommand,
				"shared",
				lambda: parent.squares.display_table("distances"),
			],
			"View evaluations": [
				ViewEvaluationsCommand,
				"shared",
				lambda: parent.statistics.display_table("evaluations"),
			],
			"View grouped data": [
				ViewGroupedDataCommand,
				"shared",
				lambda: parent.tables.display_table("grouped_data"),
			],
			"View individuals": [
				ViewIndividualsCommand,
				"shared",
				lambda: parent.statistics.display_table("individuals"),
			],
			"View scores": [
				ViewScoresCommand,
				"shared",
				lambda: parent.statistics.display_table("scores"),
			],
			"View sample design": [
				ViewSampleDesignCommand,
				"shared",
				lambda: parent.statistics.display_table("sample_design"),
			],
			"View sample repetitions": [
				ViewSampleRepetitionsCommand,
				"shared",
				lambda: parent.statistics.display_table("sample_repetitions"),
			],
			"View sample solutions": [
				ViewSampleSolutionsCommand,
				"shared",
				lambda: parent.statistics.display_table("sample_solutions"),
			],
			"View similarities": [
				ViewSimilaritiesCommand,
				"shared",
				lambda: parent.squares.display_table("similarities"),
			],
			"View point uncertainty": [
				ViewPointUncertaintyCommand,
				"shared",
				lambda: parent.statistics.display_table("uncertainty"),
			],
			"View spatial uncertainty": [
				ViewSpatialUncertaintyCommand,
				"shared",
				lambda: parent.statistics.display_table("spatial_uncertainty"),
			],
			"View target": [
				ViewTargetCommand,
				"shared",
				lambda: parent.tables.display_table("target"),
			],
		}
		# peek(len(self.widget_dict))


# --------------------------------------------------------------------------


class SplashWindow(QWidget):
	def __init__(self) -> None:
		super().__init__()

		splash_position_x = 1375
		splash_position_y = 300

		self.setWindowTitle("Welcome")
		self.move(splash_position_x, splash_position_y)

		# Set the background image
		palette = QPalette()
		palette.setBrush(
			QPalette.Window,
			QBrush(
				QPixmap(
					"c:/PythonProjects/genesis/resources/Constellation.jpg"
				)
			),
		)
		self.setPalette(palette)

		# Create the labels

		spaces_label = QLabel(self)
		spaces_label.setText("Welcome to Spaces")
		spaces_label.setFont(QFont("Arial", 44))
		spaces_label.setStyleSheet("color: white")
		spaces_label.setGeometry(100, 100, 750, 50)

		purpose_label = QLabel(self)
		purpose_label.setText(
			"Spaces helps you visually explore preferences using similarity "
			"\n      measures and models."
		)
		purpose_label.setFont(QFont("Arial", 18))
		purpose_label.setStyleSheet("color: white")
		purpose_label.setGeometry(150, 225, 750, 50)

		how_label = QLabel(self)
		how_label.setText(
			"If you have a configuration file or a similarity matrix "
			"you can use the"
			" \n     File menu to open the file(s)."
		)
		how_label.setFont(QFont("Arial", 14))
		how_label.setStyleSheet("color: white")
		how_label.setGeometry(150, 400, 750, 50)

		ok_button = QPushButton("OK", self)
		ok_button.clicked.connect(self.ok_clicked)
		ok_button.setFixedWidth(96)
		ok_button.move(300, 600)

		cancel_button = QPushButton("Cancel", self)
		cancel_button.clicked.connect(self.cancel_clicked)
		cancel_button.setFixedWidth(96)
		cancel_button.move(500, 600)

	def ok_clicked(self) -> None:
		self.close()

	def cancel_clicked(self) -> None:
		self.close()
