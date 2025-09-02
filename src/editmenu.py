
import peek # noqa: F401
from exceptions import (
	SpacesError
)
from common import Spaces
from director import Status


	# ------------------------------------------------------------------------


class RedoCommand:

	def __init__(
			self,
			director: Status,
			common: Spaces) -> None:
		""" The Redo command has yet to be implemented.
		"""
		self._director = director
		self.common = common
		self._director.command = "Redo"
		self._director.title_for_table_widget \
			= "Redo is under construction - stay tuned, please"
		return

	def execute(self, common: Spaces) -> None: # noqa: ARG002


		self._director.record_command_as_selected_and_in_process()
		self._director.optionally_explain_what_command_does()
		self._director.dependency_checker.detect_dependency_problems()
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.set_focus_on_tab('Output')
		self._director.record_command_as_successfully_completed()

		return

	# ------------------------------------------------------------------------


class UndoCommand:

	def __init__(
			self,
			director: Status,
			common: Spaces) -> None:

		self._director = director
		self.common = common
		self._director.command = "Undo"
		self._director.title_for_table_widget \
			= "Undo is under construction please stay tuned"
		return

	def execute(
			self,
			common: Spaces) -> None:  # noqa: ARG002

		self._director.record_command_as_selected_and_in_process()
		self._director.optionally_explain_what_command_does()
		self._director.dependency_checker.detect_dependency_problems()
		self._return_to_previous_active()
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.set_focus_on_tab('Output')
		self._director.record_command_as_successfully_completed()
		return

	# ------------------------------------------------------------------------

	def _return_to_previous_active(self) -> None:

		undo_stack = self._director.undo_stack
		undo_stack_source = self._director.undo_stack_source
		# active = self._director.active

		if self._director.common.have_previous_active():
			print("\n\tUndoing ", undo_stack_source[-1])
			active = undo_stack[-1]
			#
			if self._director.common.have_active_configuration():
				self._director.configuration_active.print_active_function()
				self._director.\
					create_configuration_plot_for_plot_and_gallery_tabs()
			del undo_stack[-1]
			del undo_stack_source[-1]
		else:
			title_msg = "No previous configuration"
			detail_msg = ("Establish more than one active configuration "
				"before using Undo")
			raise SpacesError(title_msg, detail_msg)
		self._director.undo_stack = undo_stack
		self._director.undo_stack_source = undo_stack_source
		self._director.active = active

		return
