from __future__ import annotations

import math
import peek  # noqa: F401
from typing import TYPE_CHECKING

from pyqtgraph import QtCore
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QTableWidget, QTableWidgetItem
from exceptions import SpacesError
# from common import Spaces
from constants import (
	MAXIMUM_NUMBER_OF_ROWS_IN_ACKNOWLEDGEMENTS_TABLE,
	N_ROWS_IN_STATUS_TABLE,
)

if TYPE_CHECKING:
	from director import Status
	from common import Spaces
# ----------------------------------------------------------------------------


class AboutCommand:
	def __init__(self, director: Status, common: Spaces) -> None:
		self._director = director
		self._common = common
		self._director.command = "About"
		self._director.acknowledgements = (
			"Charles Antonelli",
			"Phillipp Acsany",
			"Ned Batchelder",
			"Cornell Belcher",
			"Alexis Castelanas",
			"ChatGPT",
			"Claude Code",
			"Clyde Coombs",
			"Beautiful Corners",
			"Meghan Dailey",
			"Anthony Downs",
			"Lutz Erbring",
			"Chris Gates",
			"James Gerity",
			"GitHub Copilot",
			"Jonathan Golob",
			"Peter Heller",
			"Geir Arne Hjelle",
			"Inter-Univerity Consortium for\nPolitical and Social Research",
			"Institute for Social Research,\nThe University of Michigan",
			"William Jacoby",
			"Jon Kiparsky",
			"William Kruskal",
			"Celinda Lake",
			"Lake Research Partners",
			"Glenn Lehman",
			"Adam Masiarek",
			"Stuart McDonald",
			"Gijs Mos",
			"Blaise Pabon",
			"George Rabinowitz",
			"Real Python",
			"Roger Shepard",
			"Donald Stokes",
			"Waldo Tobler",
			"Ruud van der Ham",
			"Herbert Weisberg",
			"Bartosz Zaczynski",
		)

		return

	# ------------------------------------------------------------------------

	def execute(self, common: Spaces) -> None:
		self._director.record_command_as_selected_and_in_process()
		self._director.optionally_explain_what_command_does()
		self._director.dependency_checker.detect_dependency_problems()
		params = common.get_command_parameters("About")
		common.capture_and_push_undo_state("About", "passive", params)
		self._print_about()
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.set_focus_on_tab("Output")
		self._director.record_command_as_successfully_completed()
		return

	# ------------------------------------------------------------------------

	def _print_about(self) -> None:
		"""Print information about Spaces and acknowledgements."""
		print("\tAbout Spaces\n")
		print(
			"\tSpaces was developed by Ed Schneider."
			"\n\n\tIt is based on programs he developed in the 1970s as "
			"a graduate student"
			"\n\tat The University of Michigan and while "
			"consulting on the Obama 2008"
			"\n\tcampaign."
			"\n\n\tQuite a few individuals and organizations have contributed "
			"to the"
			"\n\tdevelopment of Spaces."
			"\n\n\tAmong those who have contributed (in alphabetical order)"
			" are:\n"
		)
		# Print acknowledgements in 2 columns, preserving newlines within entries
		acknowledgements = self._director.acknowledgements
		# Calculate column width based on longest LINE (not entry)
		max_line_len = max(
			len(line)
			for ack in acknowledgements
			for line in ack.split("\n")
		)
		col_width = max_line_len + 3
		mid = (len(acknowledgements) + 1) // 2

		for i in range(mid):
			left_lines = acknowledgements[i].split("\n")
			right_lines = (
				acknowledgements[i + mid].split("\n")
				if i + mid < len(acknowledgements)
				else [""]
			)
			max_lines = max(len(left_lines), len(right_lines))

			for line_num in range(max_lines):
				left = left_lines[line_num] if line_num < len(left_lines) else ""
				right = right_lines[line_num] if line_num < len(right_lines) else ""
				print(f"\t  {left:<{col_width}}{right}")
		return

	# ------------------------------------------------------------------------

	def _display_initialize_variables(self) -> None:
		self.bad_gui_output_as_widget_title = "Bad gui_output_as_widget"
		self.bad_gui_output_as_widget_message = (
			"gui_output_as_widget is not an instance of QTableWidget"
		)

	# ------------------------------------------------------------------------

	def _display(self) -> QTableWidget:
		self._display_initialize_variables()
		gui_output_as_widget = self._create_table_widget_for_about(
			self._director.acknowledgements
		)
		#
		self._director.set_column_and_row_headers(gui_output_as_widget, [], [])
		#
		if not isinstance(gui_output_as_widget, QTableWidget):
			# had been raise TypeError
			raise SpacesError(
				self.bad_gui_output_as_widget_title,
				self.bad_gui_output_as_widget_message,
			)
		#
		self._director.resize_and_set_table_size(gui_output_as_widget, 4)
		#
		self._director.output_widget_type = "Table"
		return gui_output_as_widget

	# ------------------------------------------------------------------------

	def _create_table_widget_for_about(self, names: list[str]) -> QTableWidget:
		combined_faux_header = "Contributors"
		faux_header_shade = self._director.column_header_color
		#
		table_widget: QTableWidget = QTableWidget(1, 1)
		#
		n_names = len(names)

		if n_names <= MAXIMUM_NUMBER_OF_ROWS_IN_ACKNOWLEDGEMENTS_TABLE:
			table_widget.setRowCount(n_names)
			table_widget.setColumnCount(1)
			#
			table_widget.setHorizontalHeaderLabels([combined_faux_header])
			header_item = QTableWidgetItem(combined_faux_header)
			#
			header_item.setTextAlignment(QtCore.Qt.AlignCenter) \
				# type: ignore[unresolved-attribute]
			header_item.setBackground(QColor(faux_header_shade))
			table_widget.horizontalHeader().show()

			for each_name, item in enumerate(names):
				table_widget.setItem(
					each_name, 0, QTableWidgetItem(str(item)))
		else:
			columns_required = math.ceil(n_names / 10)
			rows_required = min(n_names, 10) + 1  # custom header row

			table_widget.setRowCount(rows_required)
			table_widget.setColumnCount(columns_required)

			header_item = QTableWidgetItem(combined_faux_header)

			# Center the text in the custom header and shade it
			header_item.setTextAlignment(QtCore.Qt.AlignCenter) # type: ignore[unresolved-attribute]
			header_item.setBackground(QColor(faux_header_shade))

			table_widget.setItem(0, 0, header_item)
			table_widget.setSpan(0, 0, 1, columns_required)
			# Span the custom header across all columns
			for each_col in range(columns_required):
				for each_row in range(1, rows_required):
					# skip faux header row
					index = each_col * 10 + (each_row - 1)
					if index < n_names:
						table_widget.setItem(
							each_row,
							each_col,
							QTableWidgetItem(str(names[index])),
						)
		return table_widget

	# ------------------------------------------------------------------------


class HelpCommand:
	def __init__(self, director: Status, common: Spaces) -> None:
		self._director = director
		self.common = common
		director.command = "Help"
		return

	# ------------------------------------------------------------------------

	def execute(self, common: Spaces) -> None:
		self._director.record_command_as_selected_and_in_process()
		self._director.optionally_explain_what_command_does()
		self._director.dependency_checker.detect_dependency_problems()
		params = common.get_command_parameters("Help")
		common.capture_and_push_undo_state("Help", "passive", params)
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.set_focus_on_tab("Output")
		self._director.record_command_as_successfully_completed()
		return


# --------------------------------------------------------------------------


class StatusCommand:
	"""The status command displays all the indicators describing
	the current status.
	"""

	def __init__(self, director: Status, common: Spaces) -> None:
		self._director = director
		self.common = common
		self._director.command = "Status"
		return

	# ------------------------------------------------------------------------

	def execute(self, common: Spaces) -> None:
		common.initiate_command_processes()
		params = common.get_command_parameters("Status")
		common.capture_and_push_undo_state("Status", "passive", params)
		self._print_status()
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.set_focus_on_tab("Output")
		self._director.record_command_as_successfully_completed()
		return

	# ------------------------------------------------------------------------

	def _print_status(self) -> None:

		self._director.common.print_established_elements()
		self._director.common.print_plot_settings()
		self._director.common.print_plane_settings()
		self._director.common.print_segment_sizing_settings()
		self._director.common.print_display_settings()
		self._director.common.print_vector_sizing_settings()
		self._director.common.print_presentation_layer_settings()
		self._director.common.print_layout_options_settings()
		return

	# ------------------------------------------------------------------------


	def _display(self) -> QTableWidget:
		#
		gui_output_as_widget = self._create_table_widget_for_status()
		#
		self._director.set_column_and_row_headers(
			gui_output_as_widget,
			["Have item", "Status", "Setting", "Value"],
			[]
		)
		#
		self._director.resize_and_set_table_size(gui_output_as_widget, 4)
		#
		self._director.output_widget_type = "Table"
		return gui_output_as_widget

	# ------------------------------------------------------------------------

	def _create_table_widget_for_status(self) -> QTableWidget:
		# Calculate rows needed: max of data items (18) and settings (17)
		nrows = N_ROWS_IN_STATUS_TABLE
		table_widget = QTableWidget(nrows, 4)

		# Populate left side (data availability) and right side (settings)
		self._populate_data_availability_columns(table_widget)
		self._populate_settings_columns(table_widget)

		return table_widget

	# ------------------------------------------------------------------------

	def _populate_data_availability_columns(
		self, table_widget: QTableWidget
	) -> None:
		"""Populate columns 0-1 with data availability indicators."""
		table_widget.setItem(0, 0, QTableWidgetItem("Active configuration"))
		table_widget.setItem(
			0,
			1,
			QTableWidgetItem(
				str(self._director.common.have_active_configuration())
			),
		)
		table_widget.setItem(1, 0, QTableWidgetItem("Alike coordinates"))
		table_widget.setItem(
			1,
			1,
			QTableWidgetItem(str(self._director.common.have_alike_coords())),
		)
		table_widget.setItem(2, 0, QTableWidgetItem("Clusters"))
		table_widget.setItem(
			2, 1, QTableWidgetItem(str(self._director.common.have_clusters()))
		)
		table_widget.setItem(3, 0, QTableWidgetItem("Correlations"))
		table_widget.setItem(
			3,
			1,
			QTableWidgetItem(str(self._director.common.have_correlations())),
		)
		table_widget.setItem(4, 0, QTableWidgetItem("Data for groups"))
		table_widget.setItem(
			4,
			1,
			QTableWidgetItem(str(self._director.common.have_grouped_data())),
		)
		table_widget.setItem(5, 0, QTableWidgetItem("Data for individuals"))
		table_widget.setItem(
			5,
			1,
			QTableWidgetItem(
				str(self._director.common.have_individual_data())
			),
		)
		table_widget.setItem(6, 0, QTableWidgetItem("Difference of ranks"))
		table_widget.setItem(
			6,
			1,
			QTableWidgetItem(
				str(self._director.common.have_ranks_differences())
			),
		)
		table_widget.setItem(7, 0, QTableWidgetItem("Distances"))
		table_widget.setItem(
			7, 1, QTableWidgetItem(str(self._director.common.have_distances()))
		)
		table_widget.setItem(8, 0, QTableWidgetItem("Evaluations"))
		table_widget.setItem(
			8,
			1,
			QTableWidgetItem(str(self._director.common.have_evaluations())),
		)
		table_widget.setItem(9, 0, QTableWidgetItem("Factors"))
		table_widget.setItem(
			9, 1, QTableWidgetItem(str(self._director.common.have_factors()))
		)
		table_widget.setItem(10, 0, QTableWidgetItem("MDS results"))
		table_widget.setItem(
			10,
			1,
			QTableWidgetItem(str(self._director.common.have_mds_results())),
		)
		table_widget.setItem(11, 0, QTableWidgetItem("Reference points"))
		table_widget.setItem(
			11,
			1,
			QTableWidgetItem(
				str(self._director.common.have_reference_points())
			),
		)
		table_widget.setItem(12, 0, QTableWidgetItem("Sample design"))
		table_widget.setItem(
			12,
			1,
			QTableWidgetItem(str(self._director.common.have_sample_design())),
		)
		table_widget.setItem(13, 0, QTableWidgetItem("Sample repetitions"))
		table_widget.setItem(
			13,
			1,
			QTableWidgetItem(
				str(self._director.common.have_sample_repetitions())
			),
		)
		table_widget.setItem(14, 0, QTableWidgetItem("Scores"))
		table_widget.setItem(
			14, 1, QTableWidgetItem(str(self._director.common.have_scores()))
		)
		table_widget.setItem(15, 0, QTableWidgetItem("Segments"))
		table_widget.setItem(
			15, 1, QTableWidgetItem(str(self._director.common.have_segments()))
		)
		table_widget.setItem(16, 0, QTableWidgetItem("Similarities"))
		table_widget.setItem(
			16,
			1,
			QTableWidgetItem(str(self._director.common.have_similarities())),
		)
		table_widget.setItem(17, 0, QTableWidgetItem("Target configuration"))
		table_widget.setItem(
			17,
			1,
			QTableWidgetItem(
				str(self._director.common.have_target_configuration())
			),
		)
		table_widget.setItem(18, 0, QTableWidgetItem("Uncertainty solutions"))
		table_widget.setItem(
			18,
			1,
			QTableWidgetItem(
				str(self._director.common.have_sample_solutions())
			),
		)
		table_widget.setItem(
			19, 0, QTableWidgetItem("Commands include explanations")
		)
		table_widget.setItem(
			19,
			1,
			QTableWidgetItem(
				str(
					self._director.include_explanation_when_verbosity_last_set_to_verbose()
				)
			),
		)
		return

	# ------------------------------------------------------------------------

	def _populate_settings_columns(self, table_widget: QTableWidget) -> None:
		"""Populate columns 2-3 with settings."""
		table_widget.setItem(
			0, 2, QTableWidgetItem("Show bisector")
		)
		table_widget.setItem(
			0,
			3,
			QTableWidgetItem(
				str(self._director.common.show_bisector)
			),
		)
		table_widget.setItem(
			1, 2, QTableWidgetItem("Show connector")
		)
		table_widget.setItem(
			1,
			3,
			QTableWidgetItem(
				str(self._director.common.show_connector)
			),
		)
		table_widget.setItem(
			2, 2, QTableWidgetItem("Show reference points")
		)
		table_widget.setItem(
			2,
			3,
			QTableWidgetItem(
				str(self._director.common.show_reference_points)
			),
		)
		table_widget.setItem(
			3, 2, QTableWidgetItem("Show just reference points")
		)
		table_widget.setItem(
			3,
			3,
			QTableWidgetItem(
				str(self._director.common.show_just_reference_points)
			),
		)
		table_widget.setItem(
			4, 2, QTableWidgetItem("Horizontal axis")
		)
		table_widget.setItem(
			4,
			3,
			QTableWidgetItem(
				str(self._get_horizontal_axis_name())
			),
		)
		table_widget.setItem(
			5, 2, QTableWidgetItem("Vertical axis")
		)
		table_widget.setItem(
			5,
			3,
			QTableWidgetItem(
				str(self._get_vertical_axis_name())
			),
		)
		table_widget.setItem(
			6, 2, QTableWidgetItem("Battleground size (%)")
		)
		table_widget.setItem(
			6,
			3,
			QTableWidgetItem(
				f"{self._director.common.battleground_size * 100:.0f}"
			),
		)
		table_widget.setItem(
			7, 2, QTableWidgetItem("Core tolerance (%)")
		)
		table_widget.setItem(
			7,
			3,
			QTableWidgetItem(
				f"{self._director.common.core_tolerance * 100:.0f}"
			),
		)
		table_widget.setItem(
			8, 2, QTableWidgetItem("Axis extra margin (%)")
		)
		table_widget.setItem(
			8,
			3,
			QTableWidgetItem(
				f"{self._director.common.axis_extra * 100:.1f}"
			),
		)
		table_widget.setItem(
			9, 2, QTableWidgetItem("Label displacement (%)")
		)
		table_widget.setItem(
			9,
			3,
			QTableWidgetItem(
				f"{self._director.common.displacement * 100:.1f}"
			),
		)
		table_widget.setItem(
			10, 2, QTableWidgetItem("Point size")
		)
		table_widget.setItem(
			10,
			3,
			QTableWidgetItem(
				str(self._director.common.point_size)
			),
		)
		table_widget.setItem(
			11, 2, QTableWidgetItem("Vector head width")
		)
		table_widget.setItem(
			11,
			3,
			QTableWidgetItem(
				str(self._director.common.vector_head_width)
			),
		)
		table_widget.setItem(
			12, 2, QTableWidgetItem("Vector width")
		)
		table_widget.setItem(
			12,
			3,
			QTableWidgetItem(
				str(self._director.common.vector_width)
			),
		)
		table_widget.setItem(
			13, 2, QTableWidgetItem("Presentation layer")
		)
		table_widget.setItem(
			13,
			3,
			QTableWidgetItem(
				str(self._director.common.presentation_layer)
			),
		)
		table_widget.setItem(
			14, 2, QTableWidgetItem("Maximum columns")
		)
		table_widget.setItem(
			14,
			3,
			QTableWidgetItem(
				str(self._director.common.max_cols)
			),
		)
		table_widget.setItem(
			15, 2, QTableWidgetItem("Column width")
		)
		table_widget.setItem(
			15,
			3,
			QTableWidgetItem(
				str(self._director.common.width)
			),
		)
		table_widget.setItem(
			16, 2, QTableWidgetItem("Decimal places")
		)
		table_widget.setItem(
			16,
			3,
			QTableWidgetItem(
				str(self._director.common.decimals)
			),
		)
		return

	# ------------------------------------------------------------------------

	def _get_horizontal_axis_name(self) -> str:
		"""Get horizontal axis name from configuration or grouped data."""
		if self._director.common.have_active_configuration():
			return self._director.configuration_active.hor_axis_name
		if self._director.common.have_grouped_data():
			return self._director.grouped_data_active.hor_axis_name
		return ""

	# ------------------------------------------------------------------------

	def _get_vertical_axis_name(self) -> str:
		"""Get vertical axis name from configuration or grouped data."""
		if self._director.common.have_active_configuration():
			return self._director.configuration_active.vert_axis_name
		if self._director.common.have_grouped_data():
			return self._director.grouped_data_active.vert_axis_name
		return ""

	# ------------------------------------------------------------------------


class VerboseCommand:
	"""The Verbose command toggles the include_explanation indicator
	to True."""

	def __init__(self, director: Status, common: Spaces) -> None:
		self._director = director
		self.common = common
		self._director.command = "Verbose"
		return

	# ------------------------------------------------------------------------

	def execute(self, common: Spaces) -> None:
		common.initiate_command_processes()
		params = common.get_command_parameters("Verbose")
		common.capture_and_push_undo_state("Verbose", "passive", params)
		self._print_verbose_message()
		# verbosity_toggle = True
		self._director.verbosity_alternative = "Terse"

		# Emit the signal with the boolean value
		# self._director.verbosity_signal.signal.emit(verbosity_toggle)
		self._director.help_verbosity_action.blockSignals(True)  # noqa: FBT003
		self._director.help_verbosity_action.setText("Terse")
		self._director.help_verbosity_action.setChecked(True)
		# self._director.help_verbosity_action.setParent(None)
		# self._director.spaces_menu_bar.removeAction(
		# 	self._director.help_verbosity_action)
		# self._director.spaces_menu_bar.addAction(
		# 	self._director.help_verbosity_action)

		self._director.help_verbosity_action.blockSignals(False)  # noqa: FBT003
		# self._director.verbosity_alternative = "Terse"
		#
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.set_focus_on_tab("Output")
		self._director.record_command_as_successfully_completed()
		return

	# ------------------------------------------------------------------------

	def _print_verbose_message(self) -> None:
		print("\n\tCommands WILL include explanations.")
		return

	# ------------------------------------------------------------------------


class TerseCommand:
	"""The Terse command toggles the include_explanation indicator to False."""

	def __init__(self, director: Status, common: Spaces) -> None:
		self._director = director
		self.common = common
		self._director.command = "Terse"
		return

	# ------------------------------------------------------------------------

	def execute(self, common: Spaces) -> None:
		common.initiate_command_processes()
		params = common.get_command_parameters("Terse")
		common.capture_and_push_undo_state("Terse", "passive", params)
		self._print_terse_message()
		# verbosity_toggle = False
		self._director.verbosity_alternative = "Verbose"

		self._director.help_verbosity_action.blockSignals(True)  # noqa: FBT003
		self._director.help_verbosity_action.setText("Verbose")
		self._director.help_verbosity_action.setChecked(True)
		# self._director.help_verbosity_action.setParent(None)
		# self._director.spaces_menu_bar.removeAction(
		# 	self._director.help_verbosity_action)
		# self._director.spaces_menu_bar.addAction(
		# 	self._director.help_verbosity_action)
		self._director.help_verbosity_action.blockSignals(False)  # noqa: FBT003
		# self._director.verbosity_alternative = "Verbose"
		# self._director.help_verbosity_action.setChecked(False)
		# Emit the signal with the boolean value
		# self._director.verbosity_signal.signal.emit(verbosity_toggle)
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.set_focus_on_tab("Output")
		self._director.record_command_as_successfully_completed()
		return

	# ------------------------------------------------------------------------

	def _print_terse_message(self) -> None:
		print("\n\tCommands will not include explanations.")
		return
