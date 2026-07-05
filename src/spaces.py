from __future__ import annotations

# Standard library imports
import re
import sys

# from dataclasses import dataclass
# from peek import peek
from PySide6.QtGui import QFont
from PySide6.QtCore import QFile, QIODevice
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QApplication, QTextEdit
from director import Status, SplashWindow  # ty: ignore[unresolved-import]


# end of imports

# warnings.simplefilter(action='ignore', category=FutureWarning)
# warnings.simplefilter(action='ignore', category=DeprecationWarning)

# --------------------------------------------------------------------------


class MyTextEditWrapper:
	def __init__(self, text_to_tab: QTextEdit) -> None:
		self.text_to_tab = text_to_tab
		# Could use "Consolas" or "Courier New" for fixed font
		# or "Monaco" or "Menlo" for Mac -- not rendered as fixed width
		# or "DejaVu Sans Mono" for Linux
		# or "Lucida Console" for Windows
		# or "Andale Mono" for Windows
		# or "Source Code Pro" for Windows
		# or "Courier" for Windows
		# or "Fira Code" from Mozilla
		# or "Hack" from Source Foundry -- not rendered as fixed width
		# or "JetBrains Mono" from JetBrains -- not rendered as fixed width

		fixed_font = QFont("Lucida Console", 11)
		self.text_to_tab.setFont(fixed_font)
		# super().__init__(StringIO())

		# Tracks how many consecutive newlines currently sit at the end
		# of the Record tab, so runs split across separate write() calls
		# (e.g. print()'s own text followed by its "\n" end argument)
		# are still capped consistently to at most one blank line.
		self._trailing_newlines = 0

	# -----------------------------------------------------------------------

	def write(self, text: str) -> int:
		original_length = len(text)
		text = self._normalize_blank_lines(text)
		if text:
			self.text_to_tab.insertPlainText(text)
		return original_length

	# -----------------------------------------------------------------------

	def _normalize_blank_lines(self, text: str) -> str:
		"""Cap consecutive newlines so no more than one blank line
		ever appears in the Record tab, regardless of how many
		newlines the individual print() calls on either side of a
		seam happen to contribute.
		"""
		if not text:
			return text

		# Collapse any run of 3+ newlines within this chunk to one
		# blank line (2 newlines).
		text = re.sub(r"\n{3,}", "\n\n", text)

		leading_newlines = len(text) - len(text.lstrip("\n"))
		if leading_newlines:
			allowed_total = min(self._trailing_newlines + leading_newlines, 2)
			kept = max(0, allowed_total - self._trailing_newlines)
			text = "\n" * kept + text[leading_newlines:]

		if text.strip("\n") == "":
			self._trailing_newlines = min(
				self._trailing_newlines + len(text), 2
			)
		else:
			self._trailing_newlines = len(text) - len(text.rstrip("\n"))

		return text

	# -----------------------------------------------------------------------

	def flush(self) -> None:
		pass

# --------------------------------------------------------------------------


class MyApplication:
	def __init__(self) -> None:
		self.spaces_app = QApplication(sys.argv)
		self.director = self.initialize_gui_window()
		self.welcome_splash = None

	def execute(self) -> None:
		self.print_python_version_info()
		self.welcome_splash = SplashWindow()
		self.welcome_splash.show()
		print(
			f"\nIn this version of {self.director.right_statusbar_message} "
			f"there are {len(self.director.request_dict)} menu items, "
			f"\n{len(self.director.widget_dict)} widgets, "
			f"{len(self.director.commands)} commands and "
			f"{len(self.director.title_generator_dict)} tables available."
			"\n\nHave fun - Go boldly where no man has gone before!!!!!!! \n"
		)
		# peek("Peek seems to be working")
		self.start_event_loop()
		self.print_debug_logs()
		sys.exit()

	@staticmethod
	def print_python_version_info() -> None:
		print(sys.version)
		print(sys.version_info)
		return

	@staticmethod
	def initialize_gui_window() -> Status:
		director = Status()
		director.show()
		sys.stdout = MyTextEditWrapper(director.text_to_tab)
		# sys.stdout = open('record_of_output.txt', 'wt')
		return director

	def load_welcome_dialog(self, ui_filename: str) -> None:
		ui_file = QFile(ui_filename)
		if not ui_file.open(
			QIODevice.ReadOnly): # ty: ignore[unresolved-attribute]
			self.exit_with_error(
				f"Cannot open {ui_filename}: {ui_file.errorString()}"
			)
		loader = QUiLoader()
		welcome_dialog = loader.load(ui_file)
		ui_file.close()
		if not welcome_dialog:
			self.exit_with_error(loader.errorString())
		welcome_dialog.show()
		welcome_dialog.exec() # ty: ignore[unresolved-attribute]

	def start_event_loop(self) -> int:
		return self.spaces_app.exec()

	def print_debug_logs(self) -> None:
		print(f"{self.director.commands_used=}")
		print(f"{self.director.command_exit_code=}")
		print(f"{self.director.undo_stack_source=}\n")

	@staticmethod
	def exit_with_error(error_message: str) -> None:
		print(error_message)
		sys.exit(-1)


# --------------------------------------------------------------------------


if __name__ == "__main__":

	my_app = MyApplication()
	my_app.execute()
	
