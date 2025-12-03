from __future__ import annotations

# Standard library imports
import os
from pathlib import Path
from itertools import islice

# from dataclasses import dataclass

import pandas as pd
# import pyqtgraph as pg
import peek # noqa: F401
from PySide6.QtCore import QSize
from PySide6.QtGui import QAction, QBrush, QFont, QIcon, QPalette, QPixmap
from PySide6.QtWidgets import (
	QFileDialog,
	# QHBoxLayout,
	QLabel,
	QMainWindow,
	QMenu,
	QProgressBar,
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
	from command_state import CommandState

from constants import TEST_IF_ACTION_OR_SUBMENU_HAS_THREE_ITEMS
from dependencies import DependencyChecking
from dictionaries import (
	FrozenDict,
	command_dict,
	explain_dict,
	tab_dict,
	button_dict,
	request_dict,
	create_widget_dict,
	title_generator_dict,
	file_menu_dict,
	edit_menu_dict,
	view_menu_dict,
	transform_menu_dict,
	associations_menu_dict,
	model_menu_dict,
	respondents_menu_dict,
	help_menu_dict,
	tester_menu_dict,
	command_dependencies_dict,
)
from exceptions import SpacesError
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

	title_for_table_widget: str = ""

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
		self.command_states = _structure.command_states
		self.command = _structure.command
		self.undo_stack = _structure.undo_stack
		self.undo_stack_source = _structure.undo_stack_source
		self.redo_stack = _structure.redo_stack
		self.redo_stack_source = _structure.redo_stack_source
		self.deactivated_items = _structure.deactivated_items
		self.deactivated_descriptions = _structure.deactivated_descriptions

		self.request_dict = request_dict

		# Script execution state
		self.executing_script = False
		self.script_parameters: dict | None = None

		# Track parameters already obtained for current command
		# Used to prevent re-prompting when get_command_parameters is called
		# multiple times (e.g., when later parameters depend on earlier ones)
		self.obtained_parameters: dict[str, any] = {}

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
		self.widget_dict = create_widget_dict(self)
		self.title_generator_dict = title_generator_dict
		self.column_header_color: str = "#F08080"  #  light coral for lightred
		self.row_header_color: str = "lightgreen"
		self.cell_color: str = "lightyellow"
		self.name_of_file_written_to: str = ""

	# ------------------------------------------------------------------------

	def setup_gui(self) -> None:
		self.setWindowTitle("Spaces")
		self.create_menu_bar()
		self.create_status_bar()
		self.create_explanations()
		self.create_tool_bar()
		self.create_tabs()
		# Initialize Undo and Redo as disabled (no stack items on startup)
		self.disable_undo()
		self.disable_redo()

		# The following checks the consistency of dictionaries
		# Do they all handle all commands and are in the same order!!!!!!!!!!!!
		# self.check_consistency_of_dictionaries_and_arrays()

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
		self.configuration_active = ConfigurationFeature(self)
		self.correlations_active = CorrelationsFeature(self)
		self.evaluations_active = EvaluationsFeature(self)
		self.grouped_data_active = GroupedDataFeature(self)
		self.individuals_active = IndividualsFeature(self)
		self.similarities_active = SimilaritiesFeature(self)
		self.target_active = TargetFeature(self)
		self.scores_active = ScoresFeature(self)
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
		self.tab_widget.setTabPosition(
			QTabWidget.South) # ty: ignore[unresolved-attribute]
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

	def check_consistency_of_dictionaries_and_arrays(self) -> None:

		lowered_commands = []
		print("\nChecking consistency of dictionaries and arrays \n")
		element = 108

		print("Ordering of elements:")
		print(" request_dict: follows the order of the menu items")
		print(" commands: alphabetical order of commands")
		print(" widget_dict: alphabetical order of keys")
		print(" title_generator_dict: alphabetical order of keys")
		print(" explain_dict: alphabetical order of keys")
		print(" command_dependencies_dict: alphabetical order of keys \n")

		print("Lengths of dictionaries and arrays:")
		print(" request_dict: ", len(self.request_dict))
		print(" commands: ", len(self.commands))
		print(" widget_dict: ", len(self.widget_dict))
		print(" title_generator_dict: ", len(self.title_generator_dict))
		print(" explain_dict: ", len(explain_dict))
		print(" command_dependencies_dict: ",
			len(command_dependencies_dict))

		print("Checking that all commands are the same as request_dict keys")
		print(" after translating self.commands entries to lowercase and"
			" replacing spaces with _ ")
		print(" Exceptions are:")
		for each_command in self.commands:
			lowered_commands.append( # noqa: PERF401
				each_command.lower().replace(" ", "_"))
		for menu_item in range(len(self.request_dict)):
			key = next(iter(islice(self.request_dict.keys(),
				menu_item, None)), None)
			if key not in lowered_commands:
				print(" request_dict key not in commands: ", key)

		print(" request_dict key:", key, "\n")
		print("Consistency of element ", element)
		print(" command element:", self.commands[element])
		key = next(iter(islice(self.widget_dict.keys(), element, None)), None)
		print(" widget_dict key:", key)
		key = next(iter(islice(explain_dict.keys(), element, None)), None)
		print(" explain_dict key:", key)
		key = next(iter(islice(self.title_generator_dict.keys(),
			element, None)), None)
		print(" title_generator_dict key:", key)
		print(" command_dependencies_dict key:",
			next(iter(islice(command_dependencies_dict.keys(),
			element, None)), None))

		for element in range(len(self.commands)):
			if next(
				iter(islice(self.widget_dict.keys(), element, None)), None) \
				!= next(iter(islice(explain_dict.keys(),
						element, None)), None):
				print("Inconsistency found at element ", element)
				print("Command is: ", self.commands[element])
				print(" widget_dict key is: ", next(
					iter(islice(self.widget_dict.keys(), element, None)),
					None))
				print(" title_generator_dict key is: ", next(
					iter(islice(self.title_generator_dict.keys(),
						element, None)), None))
				print(" explain_dict key is: ", next(
					iter(islice(explain_dict.keys(), element, None)),
					None))
				print(" command_dependencies_dict key is: ", next(
					iter(islice(command_dependencies_dict.keys(),
						element, None)), None))
				break

		if element == len(self.commands) - 1:
			print("\nNo inconsistencies found -  YEAH!!!!")
		else:
			pass
				
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

	# ------------------------------------------------------------------------

	def plot_to_gui(self, fig: plt.Figure) -> None:
		self.plot_to_gui_using_matplotlib(fig)

	# ------------------------------------------------------------------------

	def create_file_menu(self) -> FrozenDict:
		"""Create dictionary structure for the File menu"""
		return file_menu_dict

	# ------------------------------------------------------------------------

	def create_edit_menu(self) -> FrozenDict:
		"""Create dictionary structure for the Edit menu"""
		return edit_menu_dict

	# ------------------------------------------------------------------------

	def create_view_menu(self) -> FrozenDict:
		"""Create dictionary structure for the View menu"""
		return view_menu_dict

	# ------------------------------------------------------------------------

	def create_transform_menu(self) -> FrozenDict:
		"""Create dictionary structure for the Transform menu"""
		return transform_menu_dict

	# ------------------------------------------------------------------------

	def create_associations_menu(self) -> FrozenDict:
		"""Create dictionary structure for the Associations menu"""
		return associations_menu_dict

	# ------------------------------------------------------------------------

	def create_model_menu(self) -> FrozenDict:
		"""Create dictionary structure for the Model menu"""
		return model_menu_dict

	# ------------------------------------------------------------------------

	def create_respondents_menu(self) -> FrozenDict:
		"""Create dictionary structure for the Respondents menu"""
		return respondents_menu_dict

	# ------------------------------------------------------------------------

	def create_help_menu(self) -> FrozenDict:
		"""Create dictionary structure for the Help menu"""
		return help_menu_dict

	# ------------------------------------------------------------------------

	def create_tester_menu(self) -> FrozenDict:
		"""Create dictionary structure for the Tester menu"""
		return tester_menu_dict

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

		# Store reference to Redo action for enable/disable control
		if name == "Redo":
			self.redo_action = action

		# Store reference to Undo action for enable/disable control
		if name == "Undo":
			self.undo_action = action

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
		return lambda: self.request_control(next_command)

	# -------------------------------------------------------------------------

	def toggle_verbosity(self) -> None:
		current_text = self.help_verbosity_action.text()

		self.request_control(current_text.lower())

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
		self.right_statusbar: QLabel = QLabel(self.right_statusbar_message)

		# Create progress label and bar for long-running operations
		self.progress_label = QLabel()
		self.progress_label.hide()

		self.progress_bar = QProgressBar()
		self.progress_bar.setRange(0, 100)
		self.progress_bar.setTextVisible(False)
		self.progress_bar.setFixedWidth(150)
		self.progress_bar.hide()

		# Create expanding spacer between progress bar and right label
		self.progress_spacer = QWidget()
		self.progress_spacer.setSizePolicy(
			QSizePolicy.Expanding, # type: ignore[attr-defined]
			QSizePolicy.Preferred  # type: ignore[attr-defined]
		)
		self.progress_spacer.hide()

		self.spaces_statusbar.addWidget(self.left_statusbar, 1)
		self.spaces_statusbar.addPermanentWidget(self.progress_label, 0)
		self.spaces_statusbar.addPermanentWidget(self.progress_bar, 0)
		self.spaces_statusbar.addPermanentWidget(self.progress_spacer, 1)
		self.spaces_statusbar.addPermanentWidget(self.right_statusbar, 0)
		self.setStatusBar(self.spaces_statusbar)
		self.left_statusbar.setText("Awaiting your command!")

		# -------------------------------------------------------------------
		# In request_control items are in the menu order
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
			"Factor analysis",
			"Factor analysis machine learning",
			"First dimension",
			"Grouped data",
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
			"Open sample solutions",
			"Open scores",
			"Open script",
			"Paired",
			"Principal components",
			"Print configuration",
			"Print correlations",
			"Print evaluations",
			"Print grouped data",
			"Print individuals",
			"Print sample design",
			"Print sample repetitions",
			"Print sample solutions",
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
			"Save grouped data",
			"Save individuals",
			"Save sample design",
			"Save sample repetitions",
			"Save sample solutions",
			"Save scores",
			"Save script",
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
			"Settings - presentation layer",
			"Settings - segment sizing",
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
			"View individuals",
			"View point uncertainty",
			"View sample design",
			"View sample repetitions",
			"View sample solutions",
			"View scores",
			"View script",
			"View similarities",
			"View spatial uncertainty",
			"View target",
		)


	# ------------------------------------------------------------------------

	def request_control(self, next_command: str) -> None:
		request_dict_local = self.request_dict
		common = self.common

		try:
			command_class = request_dict_local[next_command][0]
			if request_dict_local[next_command][1] is None:
				self.current_command = command_class(self, common)
				self.current_command.execute(common)
			else:
				self.current_command = command_class(self, common)
				self.current_command.execute(
					common, request_dict_local[next_command][1]
				)
		except SpacesError as e:
			self.unable_to_complete_command_set_status_as_failed()
			self.common.error(e.title, e.message)

	# ------------------------------------------------------------------------

	def create_lambda(self, next_command: str) -> Callable:
		return lambda: self.request_control(next_command)

	# ------------------------------------------------------------------------

	def create_tool_bar(self) -> None:
		# Using a title_for_table_widget
		self.spaces_toolbar = QToolBar("Spaces toolbar")
		self.spaces_toolbar.setIconSize(QSize(20, 20))
		self.addToolBar(self.spaces_toolbar)

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

			# Store reference to undo/redo toolbar actions
			if key == "undo":
				self.undo_toolbar_action = button_action
			if key == "redo":
				self.redo_toolbar_action = button_action

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
		print(
			f"DEPRECATED: {self.command} uses "
			"director.record_command_as_selected_and_in_process(). "
			"Use common.initiate_command_processes() instead."
		)
		# Clear obtained parameters from previous command
		self.obtained_parameters.clear()

		self.spaces_statusbar.showMessage(
			f"Starting {self.command} command", 80000
		)
		self.commands_used.append(self.command)
		self.command_exit_code.append(-1)  # -1  command is in process
		self.command_states.append(None)  # Will be updated when state pushed
		print(f"\nStarting {self.command} command: \n")

		active_commands = (
			"Center", "Cluster", "Compare", "Configuration", "Correlations",
			"Deactivate", "Evaluations", "Factor analysis",
			"Factor analysis machine learning", "Grouped data", "Individuals",
			"Invert", "Line of sight", "MDS", "Move",
			"Open sample design", "Open sample repetitions",
			"Open sample solutions", "Open scores",
			"Principal components",
			"Redo",  "Reference points", "Rescale", "Rotate",
			"Sample designer", "Sample repetitions", "Score individuals",
			"Settings - display sizing", "Settings - layout options",
			"Settings - plane", "Settings - plot settings",
			"Settings - presentation layer", "Settings - segment sizing",
			"Settings - vector sizing", "Similarities",
			"Target", "Tester", "Uncertainty", "Undo", "Varimax")
		interactive_only_commands = (
			"Create", "New grouped data")
		script_commands = (
			"Open script", "Save script", "View script")
		passive_commands = (
			"About", "Alike", "Base", "Battleground", "Contest",
			"Convertible", "Core supporters", "Directions",
			"Distances", "Exit", "First dimension","Help", "History", "Joint",
			"Likely supporters",
			"Paired", "Print configuration", "Print correlations",
			"Print evaluations", "Print grouped data", "Print individuals",
			"Print sample design", "Print sample repetitions",
			"Print sample solutions", "Print scores",
			"Print similarities", "Print target", "Ranks differences",
			"Ranks distances", "Ranks similarities",
			"Save configuration",
			"Save correlations", "Save individuals", "Save sample design",
			"Save sample repetitions", "Save sample solutions",
			"Save scores", "Save similarities","Save target", "Scree",
			"Second dimension", "Segments","Shepard",
			"Status", "Stress contribution", "Terse", "Vectors", "Verbose",
			"View configuration", "View correlations", "View custom",
			"View distances", "View evaluations", "View grouped data",
			"View individuals", "View point uncertainty", "View sample design",
			"View sample repetitions", "View sample solutions", "View scores",
			"View similarities", "View spatial uncertainty",
			"View target")

	# ------------------------------------------------------------------------

	def create_explanations(self) -> None:
		# explain_dict is now imported from dictionaries.py
		return



	# ------------------------------------------------------------------------

	def optionally_explain_what_command_does(self) -> str:
		print(
			f"DEPRECATED: {self.command} uses "
			"director.optionally_explain_what_command_does(). "
			"Use common.initiate_command_processes() instead."
		)
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
		self,
		file_caption: str,
		file_filter: str,
		directory: str | None = None
	) -> str:
		self.get_file_name_and_handle_nonexistent_file_names_init_variables()
		dir_to_use = \
			directory if directory is not None else os.fspath(self.filedir)
		ui_file = QFileDialog.getOpenFileName(
			dir=dir_to_use,
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
		self,
		dialog_caption: str,
		dialog_filter: str,
		directory: str = "scripts"
	) -> str:
		# dropped positional arguments message and feedback

		self.get_file_name_to_store_file_initialize_variables()

		file_name, _ = QFileDialog.getSaveFileName(
			None,
			caption=dialog_caption,
			filter=dialog_filter,
			dir=directory
		)

		if len(file_name) == 0:
			raise SpacesError(
				self.empty_response_title, self.empty_response_message
			)

		return file_name

	# ------------------------------------------------------------------------

	def set_focus_on_tab(self, tab_name: str) -> None:
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
		spacer = QSpacerItem(20, 40,
			QSizePolicy.Minimum, # ty: ignore[unresolved-attribute]
			QSizePolicy.Fixed) # ty: ignore[unresolved-attribute]
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
		# eliminate last entry from undo stack ONLY if it
		# belongs to this command
		# (A command may fail before it pushes to the undo stack, in which case
		# we shouldn't remove the previous command's state)
		#
		if len(undo_stack) > 0 and undo_stack_source[-1] == command:
			del undo_stack[-1]
			del undo_stack_source[-1]

		self.command_exit_code = command_exit_code
		self.undo_stack = undo_stack
		self.undo_stack_source = undo_stack_source

		# Clear obtained parameters after command fails
		self.obtained_parameters.clear()

		return

	# ------------------------------------------------------------------------

	def _track_passive_command_for_scripting(self) -> None:
		"""Automatically track passive commands in undo stack for scripting.

		Passive commands don't modify state, but must be recorded so they
		appear in saved scripts. This method checks if the current command
		is passive and adds it to the undo stack automatically.

		If the command was already manually tracked with parameters,
		skip automatic tracking to avoid duplicates.
		"""
		if self.command in command_dict:
			cmd_type = command_dict[self.command].get("type", "active")
			if cmd_type == "passive":
				# Check if command was already manually tracked
				if (
					self.undo_stack
					and self.undo_stack[-1].command_name == self.command
				):
					# Command already tracked with parameters, skip
					return
				# Add passive command to undo stack for script generation
				self.common.push_passive_command_to_undo_stack(
					self.command, {}
				)
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

		# For OpenScript commands, mark the script's index as complete
		# rather than the last command in the exit code array
		from filemenu import OpenScriptCommand  # noqa: PLC0415

		if isinstance(self.current_command, OpenScriptCommand):
			script_index = self.current_command.index_of_script_in_command_used
			command_exit_code[script_index] = 0
		else:
			command_exit_code[-1] = 0

		# Clear obtained parameters after command completes
		self.obtained_parameters.clear()

		self.spaces_statusbar.showMessage(
			f"Completed {command} command", 80000
		)
		print(f"\nSuccessfully completed {command} command.")

		self.command = command
		self.command_exit_code = command_exit_code

		# Automatically track passive commands in undo stack for scripting
		self._track_passive_command_for_scripting()

		return

	# ------------------------------------------------------------------------

	def push_undo_state(
		self,
		cmd_state: CommandState,
		preserve_redo_stack: bool = False
	) -> None:
		"""Push a CommandState onto the undo stack.

		When a new active command executes (not Undo/Redo), clear the redo
		stack and disable Redo, matching Microsoft Word behavior.
		Passive commands (read-only) don't clear the redo stack.

		Args:
			cmd_state: The CommandState to push onto the stack
			preserve_redo_stack: If True, preserve redo stack (used by Redo)
		"""
		self.undo_stack.append(cmd_state)
		self.undo_stack_source.append(cmd_state.command_name)

		# Update command_states for script generation
		# Store this CommandState in the most recent entry
		if self.command_states:
			self.command_states[-1] = cmd_state

		# Enable Undo only if there are active commands that can be undone
		# (passive commands don't modify state and can't be undone)
		if self._has_active_undoable_commands():
			self.enable_undo()

		# Clear redo stack when a new ACTIVE command executes
		# (not Undo/Redo/passive). This matches Microsoft Word behavior.
		# Passive commands are read-only and shouldn't affect undo/redo.
		# Don't clear if preserve_redo_stack is True (called from Redo).
		if (
			not preserve_redo_stack
			and cmd_state.command_name not in ["Undo", "Redo"]
			and cmd_state.command_type == "active"
		):
			self.clear_redo_stack()
			self.disable_redo()

		return

	# ------------------------------------------------------------------------

	def pop_undo_state(self) -> CommandState | None:
		"""Pop and return the most recent CommandState from the undo stack.

		Returns:
			The most recent CommandState, or None if stack is empty
		"""
		if not self.undo_stack:
			return None
		self.undo_stack_source.pop()
		return self.undo_stack.pop()

	# ------------------------------------------------------------------------

	def peek_undo_state(self) -> CommandState | None:
		"""Return the most recent CommandState without removing it.

		Returns:
			The most recent CommandState, or None if stack is empty
		"""
		if not self.undo_stack:
			return None
		return self.undo_stack[-1]

	# ------------------------------------------------------------------------

	def clear_undo_stack(self) -> None:
		"""Clear all CommandStates from the undo stack."""
		self.undo_stack.clear()
		self.undo_stack_source.clear()
		return

	# ------------------------------------------------------------------------

	def push_redo_state(self, cmd_state: CommandState) -> None:
		"""Push a CommandState onto the redo stack.

		Args:
			cmd_state: The CommandState to push onto the stack
		"""
		self.redo_stack.append(cmd_state)
		self.redo_stack_source.append(cmd_state.command_name)
		return

	# ------------------------------------------------------------------------

	def pop_redo_state(self) -> CommandState | None:
		"""Pop and return the most recent CommandState from the redo stack.

		Returns:
			The most recent CommandState, or None if stack is empty
		"""
		if not self.redo_stack:
			return None
		self.redo_stack_source.pop()
		return self.redo_stack.pop()

	# ------------------------------------------------------------------------

	def peek_redo_state(self) -> CommandState | None:
		"""Return the most recent CommandState without removing it.

		Returns:
			The most recent CommandState, or None if stack is empty
		"""
		if not self.redo_stack:
			return None
		return self.redo_stack[-1]

	# ------------------------------------------------------------------------

	def clear_redo_stack(self) -> None:
		"""Clear all CommandStates from the redo stack."""
		self.redo_stack.clear()
		self.redo_stack_source.clear()
		return

	# ------------------------------------------------------------------------

	def _has_active_undoable_commands(self) -> bool:
		"""Check if undo stack contains any active commands that can be undone.

		Returns True if there's at least one active command in the stack.
		Passive commands and Undo/Redo meta-commands don't count since
		they're skipped during undo operations.
		"""
		for cmd_state in self.undo_stack:
			if (
				cmd_state.command_type == "active"
				and cmd_state.command_name not in ("Undo", "Redo")
			):
				return True
		return False

	# ------------------------------------------------------------------------

	def enable_undo(self) -> None:
		"""Enable the Undo command in menu and toolbar."""
		self.undo_action.setEnabled(True)
		self.undo_toolbar_action.setEnabled(True)
		return

	# ------------------------------------------------------------------------

	def disable_undo(self) -> None:
		"""Disable the Undo command in menu and toolbar."""
		self.undo_action.setEnabled(False)
		self.undo_toolbar_action.setEnabled(False)
		return

	# ------------------------------------------------------------------------

	def enable_redo(self) -> None:
		"""Enable the Redo command in menu and toolbar."""
		self.redo_action.setEnabled(True)
		self.redo_toolbar_action.setEnabled(True)
		return

	# ------------------------------------------------------------------------

	def disable_redo(self) -> None:
		"""Disable the Redo command in menu and toolbar."""
		self.redo_action.setEnabled(False)
		self.redo_toolbar_action.setEnabled(False)
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
		self.command_states: list[CommandState | None] = [None]
		self.command: str = ""
		self.undo_stack: list[CommandState] = []
		self.undo_stack_source: list[str] = ["Initialize"]
		self.redo_stack: list[CommandState] = []
		self.redo_stack_source: list[str] = []
		self.deactivated_items: list[str] = []
		self.deactivated_descriptions: list[str] = []
		# self.rivalry = Rivalry(parent, self.command)
		self.basedir = Path(__file__).parent
		# self.dir = Path.cwd()
		self.dir = Path.cwd().parent
		self.filedir = self.dir / "genesis" / "data" / "Elections"


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
			QPalette.Window, # ty: ignore[unresolved-attribute]
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
