from __future__ import annotations

# Standard library imports
import sys

# from dataclasses import dataclass
from peek import peek
from PySide6.QtGui import QFont
from PySide6.QtCore import QFile, QIODevice
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QApplication, QTextEdit
from director import Status, SplashWindow

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

	# -----------------------------------------------------------------------

	def write(self, text: str) -> int:
		self.text_to_tab.insertPlainText(text)
		return len(text)

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
			f"\nIn this version of Spaces there are "
			f"{len(self.director.request_dict)} "
			f"menu items, "
			f"{len(self.director.widget_dict)} widgets, "
			f"and {len(self.director.commands)} commands "
			f"available."
		)
		peek("Peek seems to be working") # ty: ignore[call-non-callable]
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

	def start_event_loop(self) -> None:
		return self.spaces_app.exec()

	def print_debug_logs(self) -> None:
		peek(f"{self.director.commands_used=}") # ty: ignore[call-non-callable]
		peek(f"{self.director.command_exit_code=}") # ty: ignore[call-non-callable]
		peek(f"{self.director.undo_stack_source=}\n") # ty: ignore[call-non-callable]

	@staticmethod
	def exit_with_error(error_message: str) -> None:
		print(error_message)
		sys.exit(-1)


# --------------------------------------------------------------------------


if __name__ == "__main__":
	my_app = MyApplication()
	my_app.execute()
