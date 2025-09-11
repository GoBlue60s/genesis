import math
import peek  # noqa: F401

from pyqtgraph import QtCore
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QTableWidget, QTableWidgetItem
from exceptions import SpacesError
from common import Spaces
from director import Status
from constants import (
	MAXIMUM_NUMBER_OF_ROWS_IN_ACKNOWLEDGEMENTS_TABLE,
	N_ROWS_IN_STATUS_TABLE,
)
# ----------------------------------------------------------------------------


class AboutCommand:
	def __init__(self, director: Status, common: Spaces) -> None:
		self._director = director
		self._common = common
		self._director.command = "About"
		self._director.acknowledgements = (
			"Charles Antonelli",
			"Ned Batchelder",
			"Cornell Belcher",
			"Alexis Castelanas",
			"ChatGPT",
			"Claude",
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
			"Warren Tobler",
			"Ruud van der Ham",
			"Herbert Weisberg",
			"Bartosz Zaczynski",
		)

		return

	# ------------------------------------------------------------------------

	def execute(self, common: Spaces) -> None:  # noqa: ARG002
		self._director.record_command_as_selected_and_in_process()
		self._director.title_for_table_widget = (
			"Spaces was developed by Ed Schneider."
			"\n\nIt is based on programs he developed in the 1970s as "
			"a graduate student at"
			"The University of Michigan and while consulting on the Obama "
			"2008 campaign."
			"\n\nQuite a few individuals and organizations have "
			"contributed to the development of Spaces."
			"\nAmong those who have contributed (in alphabetical order) are:"
		)
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.set_focus_on_tab("Output")
		self._director.record_command_as_successfully_completed()
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
			header_item.setTextAlignment(QtCore.Qt.AlignCenter)
			header_item.setBackground(QColor(faux_header_shade))
			table_widget.horizontalHeader().show()

			for each_name, item in enumerate(names):
				table_widget.setItem(each_name, 0, QTableWidgetItem(str(item)))
		else:
			columns_required = math.ceil(n_names / 10)
			rows_required = min(n_names, 10) + 1  # custom header row

			table_widget.setRowCount(rows_required)
			table_widget.setColumnCount(columns_required)

			header_item = QTableWidgetItem(combined_faux_header)

			# Center the text in the custom header and shade it
			header_item.setTextAlignment(QtCore.Qt.AlignCenter)
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
		self._director.title_for_table_widget = (
			"Help command under construction - stay tuned, please"
		)
		return

	# ------------------------------------------------------------------------

	def execute(self, common: Spaces) -> None:  # noqa: ARG002
		self._director.record_command_as_selected_and_in_process()
		self._director.optionally_explain_what_command_does()
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.set_focus_on_tab("Output")
		self._director.unable_to_complete_command_set_status_as_failed()
		return
		# self._director.record_command_as_successfully_completed()
		# return


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

	def execute(self, common: Spaces) -> None:  # noqa: ARG002
		self._director.record_command_as_selected_and_in_process()
		self._director.optionally_explain_what_command_does()
		self._director.common.print_established_elements()
		self._director.common.print_plot_settings()
		self._director.common.print_plane_settings()
		self._director.common.print_segment_sizing_settings()
		self._director.common.print_display_settings()
		self._director.common.print_vector_sizing_settings()
		self._director.common.print_layout_options_settings()
		# self._print_status()
		self._director.title_for_table_widget = "Status of current session"
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.set_focus_on_tab("Output")
		self._director.record_command_as_successfully_completed()
		return

	# ------------------------------------------------------------------------

	def _display(self) -> QTableWidget:
		#
		gui_output_as_widget = self._create_table_widget_for_status()
		#
		self._director.set_column_and_row_headers(
			gui_output_as_widget, ["Have item", "Status"], []
		)
		#
		self._director.resize_and_set_table_size(gui_output_as_widget, 4)
		#
		self._director.output_widget_type = "Table"
		return gui_output_as_widget

	# ------------------------------------------------------------------------

	def _create_table_widget_for_status(self) -> QTableWidget:
		#
		nrows = N_ROWS_IN_STATUS_TABLE
		table_widget = QTableWidget(nrows, 2)
		#
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
		# table_widget.setItem(
		# 	2, 0, QTableWidgetItem("Bisector information"))
		# table_widget.setItem(
		# 	2, 1, QTableWidgetItem(
		# 		# str(self._director.common.have_bisector_info())))
		# 		str(self._director.common.have_reference_points())))
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
		table_widget.setItem(6, 0, QTableWidgetItem("Distances"))
		table_widget.setItem(
			6, 1, QTableWidgetItem(str(self._director.common.have_distances()))
		)
		table_widget.setItem(7, 0, QTableWidgetItem("Evaluations"))
		table_widget.setItem(
			7,
			1,
			QTableWidgetItem(str(self._director.common.have_evaluations())),
		)
		table_widget.setItem(8, 0, QTableWidgetItem("Factors"))
		table_widget.setItem(
			8, 1, QTableWidgetItem(str(self._director.common.have_factors()))
		)
		table_widget.setItem(9, 0, QTableWidgetItem("MDS results"))
		table_widget.setItem(
			9,
			1,
			QTableWidgetItem(str(self._director.common.have_mds_results())),
		)
		table_widget.setItem(
			10, 0, QTableWidgetItem("Previous active configuration")
		)
		table_widget.setItem(
			10,
			1,
			QTableWidgetItem(
				str(self._director.common.have_previous_active())
			),
		)
		table_widget.setItem(11, 0, QTableWidgetItem("Ranks"))
		table_widget.setItem(
			11,
			1,
			QTableWidgetItem(
				str(self._director.common.have_ranks_of_similarities())
			),
		)
		table_widget.setItem(12, 0, QTableWidgetItem("Reference points"))
		table_widget.setItem(
			12,
			1,
			QTableWidgetItem(
				str(self._director.common.have_reference_points())
			),
		)
		table_widget.setItem(13, 0, QTableWidgetItem("Scores"))
		table_widget.setItem(
			13, 1, QTableWidgetItem(str(self._director.common.have_scores()))
		)
		table_widget.setItem(14, 0, QTableWidgetItem("Segments"))
		table_widget.setItem(
			14, 1, QTableWidgetItem(str(self._director.common.have_segments()))
		)
		table_widget.setItem(15, 0, QTableWidgetItem("Similarities"))
		table_widget.setItem(
			15,
			1,
			QTableWidgetItem(str(self._director.common.have_similarities())),
		)
		table_widget.setItem(16, 0, QTableWidgetItem("Target configuration"))
		table_widget.setItem(
			16,
			1,
			QTableWidgetItem(
				str(self._director.common.have_target_configuration())
			),
		)
		table_widget.setItem(
			17, 0, QTableWidgetItem("Commands include explanations")
		)
		table_widget.setItem(
			17,
			1,
			QTableWidgetItem(
				str(
					self._director.include_explanation_when_verbosity_last_set_to_verbose()
				)
			),
		)
		return table_widget

	# ------------------------------------------------------------------------


class VerboseCommand:
	"""The Verbose command toggles the include_explanation indicator
	to True."""

	def __init__(self, director: Status, common: Spaces) -> None:
		self._director = director
		self.common = common
		self._director.command = "Verbose"
		self._director.title_for_table_widget = (
			"Output will include explanations"
		)
		return

	# ------------------------------------------------------------------------

	def execute(self, common: Spaces) -> None:  # noqa: ARG002
		self._director.record_command_as_selected_and_in_process()
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
		self._director.title_for_table_widget = (
			"Output will not include explanations"
		)
		return

	# ------------------------------------------------------------------------

	def execute(self, common: Spaces) -> None:  # noqa: ARG002
		self._director.record_command_as_selected_and_in_process()
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
