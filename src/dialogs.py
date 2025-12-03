from __future__ import annotations

import sys

import peek  # noqa: F401
from PySide6.QtWidgets import (
	QCheckBox,
	QDialog,
	QHBoxLayout,
	QRadioButton,
	QPushButton,
	QLabel,
	QLineEdit,
	QDialogButtonBox,
	QGridLayout,
	QDoubleSpinBox,
	QScrollArea,
	QSpinBox,
	QVBoxLayout,
	QWidget,
)
from PySide6 import QtCore
from constants import MUST_HAVE_EXACTLY_TWO_SELECTIONS
from exceptions import SelectionError

# --------------------------------------------------------------------------


class ChoseOptionDialog(QDialog):
	def __init__(
		self,
		title: str,
		options_title: str,
		options: list[str],
		parent: QWidget | None = None,
		default_index: int | None = None,
	) -> None:
		super().__init__(parent)

		self.setWindowTitle(title)
		self.setFixedWidth(300)
		self.group = QVBoxLayout()
		self.button_group = QHBoxLayout()
		self.main_layout = QVBoxLayout()
		self.selected_option = default_index
		self.options = options
		label = QLabel(options_title)
		self.group.addWidget(label)
		for each_option, option in enumerate(options):
			rb = QRadioButton(option)
			rb.toggled.connect(self._update_selected_option)
			# Pre-select the default option if specified
			if default_index is not None and each_option == default_index:
				rb.setChecked(True)
			self.group.addWidget(rb)
		ok_button = QPushButton("OK")
		ok_button.clicked.connect(self.accept)
		cancel_button = QPushButton("Cancel")
		cancel_button.clicked.connect(self.reject)
		self.button_group.addWidget(ok_button)
		self.button_group.addWidget(cancel_button)
		self.main_layout.addLayout(self.group)
		self.main_layout.addLayout(self.button_group)
		self.setLayout(self.main_layout)

	# ------------------------------------------------------------------------

	def _update_selected_option(self, checked: bool) -> None:  # noqa: FBT001
		if checked:
			sender = self.sender()
			self.selected_option = self.options.index(sender.text())


# --------------------------------------------------------------------------


class MatrixDialog(QDialog):
	def __init__(
		self,
		title: str,
		label: list[str],
		column_labels: list[str],
		row_labels: list[str],
		parent: QWidget | None = None,
	) -> None:
		super().__init__(parent)

		self.spin_boxes: object = None
		self.column_labels = column_labels
		self.row_labels = row_labels
		self.setWindowTitle(title)
		self.init_ui(label)

	# ------------------------------------------------------------------------

	def init_ui(self, label: str) -> None:
		"""Initialize the dialog's UI components.

		Args:
			label (str): The instructional text to display above the grid.
		"""
		layout = QVBoxLayout()
		instruction_label = QLabel(label)
		layout.addWidget(instruction_label)
		grid_layout = QGridLayout()
		self.spin_boxes = []
		for j, col_label in enumerate(self.column_labels):
			column_label_widget = QLabel(col_label)
			grid_layout.addWidget(
				column_label_widget,
				0,
				j + 1,
				QtCore.Qt.AlignmentFlag.AlignHCenter,
			)

		for i, row_label_text in enumerate(self.row_labels):
			row_label = QLabel(row_label_text)
			grid_layout.addWidget(
				row_label, i + 1, 0, QtCore.Qt.AlignmentFlag.AlignRight
			)

			row_spin_boxes = []
			for j in range(len(self.column_labels)):
				spin_box = QDoubleSpinBox()
				spin_box.setRange(-1000.0, 1000.0)
				spin_box.setValue(0.0)
				grid_layout.addWidget(spin_box, i + 1, j + 1)
				row_spin_boxes.append(spin_box)
			self.spin_boxes.append(row_spin_boxes)

		layout.addLayout(grid_layout)

		button_box = QDialogButtonBox(
			QDialogButtonBox.Ok | QDialogButtonBox.Cancel
		)
		button_box.accepted.connect(self.accept)
		button_box.rejected.connect(self.reject)

		layout.addWidget(button_box)
		self.setLayout(layout)

	def get_matrix(self) -> list[list[float]]:
		matrix = [
			[
				self.spin_boxes[i][j].value()
				for j in range(len(self.column_labels))
			]
			for i in range(len(self.row_labels))
		]
		return matrix


# --------------------------------------------------------------------------


class ModifyItemsDialog(QDialog):
	def __init__(
		self,
		title: str,
		items: list[str],
		default_values: list[bool] | None = None,
		parent: QWidget | None = None,
	) -> None:
		super().__init__(parent)

		self.setWindowTitle(title)
		self.setFixedWidth(225)
		self.items = items
		self.checkboxes = []
		self.layout = QVBoxLayout()
		for i, item in enumerate(items):
			default_value = (
				default_values[i]
				if default_values and i < len(default_values)
				else False
			)
			checkbox = QCheckBox(item)
			self.checkboxes.append(checkbox)
			checkbox.setChecked(default_value)
			self.layout.addWidget(checkbox)
		self.checkbox_box = QDialogButtonBox(
			QDialogButtonBox.Ok | QDialogButtonBox.Cancel
		)
		self.checkbox_box.accepted.connect(self.accept)
		self.checkbox_box.rejected.connect(self.reject)

		checkbox_layout = QHBoxLayout()
		checkbox_layout.addWidget(self.checkbox_box)
		checkbox_layout.setAlignment(QtCore.Qt.AlignHCenter)
		self.checkbox_box.layout().setContentsMargins(0, 0, 0, 0)
		self.checkbox_box.layout().setAlignment(QtCore.Qt.AlignLeft)
		self.layout.addLayout(checkbox_layout)
		self.setLayout(self.layout)

	def selected_items(self) -> list[str]:
		selected = [
			self.items[i]
			for i, checkbox in enumerate(self.checkboxes)
			if checkbox.isChecked()
		]
		return selected


# --------------------------------------------------------------------------


class ModifyTextDialog(QDialog):
	def __init__(
		self,
		title: str,
		items: list[str],
		default_values: list[str] | None = None,
		parent: QWidget | None = None,
	) -> None:
		super().__init__(parent)

		self.setWindowTitle(title)
		self.setFixedWidth(325)
		self.items = items
		self.spinboxes = []
		self.layout = QVBoxLayout()
		for item, default_value in zip(
			items, default_values or [], strict=False
		):
			hbox = QHBoxLayout()
			label = QLabel(item)
			spinbox = QSpinBox()
			spinbox.setMinimum(0)
			spinbox.setMaximum(100)
			spinbox.setValue(default_value)
			spinbox.setAlignment(QtCore.Qt.AlignRight)
			hbox.addWidget(label)
			hbox.addWidget(spinbox)

			self.spinboxes.append(spinbox)

			self.layout.addLayout(hbox)
		self.checkbox_box = QDialogButtonBox(
			QDialogButtonBox.Ok | QDialogButtonBox.Cancel
		)
		self.checkbox_box.accepted.connect(self.accept)
		self.checkbox_box.rejected.connect(self.reject)

		checkbox_layout = QHBoxLayout()
		checkbox_layout.addWidget(self.checkbox_box)
		checkbox_layout.setAlignment(QtCore.Qt.AlignHCenter)
		self.checkbox_box.layout().setContentsMargins(0, 0, 0, 0)
		self.checkbox_box.layout().setAlignment(QtCore.Qt.AlignLeft)
		self.layout.addLayout(checkbox_layout)
		self.setLayout(self.layout)

	def selected_items(self) -> list[tuple[str, int]]:
		selected = [
			(self.items[i], self.spinboxes[i].value())
			for i in range(len(self.items))
		]
		return selected


# --------------------------------------------------------------------------


class ModifyValuesDialog(QDialog):
	def __init__(
		self,
		title: str,
		items: list[str],
		integers: bool,  # noqa:FBT001
		default_values: list[int] | None = None,
		parent: QWidget | None = None,
	) -> None:
		super().__init__(parent)
		self.setWindowTitle(title)
		self.setFixedWidth(325)
		self.items = items
		self.spinboxes = []
		self.layout = QVBoxLayout()
		for item, default_value in zip(
			items, default_values or [], strict=False
		):
			hbox = QHBoxLayout()
			label = QLabel(item)
			spinbox = QSpinBox() if integers else QDoubleSpinBox()
			spinbox.setMinimum(0)
			spinbox.setMaximum(1000)
			# Integer spinboxes need integer step,
			#  double spinboxes need decimal step
			if integers:
				spinbox.setSingleStep(1)
			else:
				spinbox.setSingleStep(0.01)
			spinbox.setValue(default_value)
			# spinbox.setGeometry(10,20,51,22)
			spinbox.setAlignment(QtCore.Qt.AlignRight)
			hbox.addWidget(spinbox)
			hbox.addWidget(label)

			self.spinboxes.append(spinbox)

			self.layout.addLayout(hbox)
		self.checkbox_box = QDialogButtonBox(
			QDialogButtonBox.Ok | QDialogButtonBox.Cancel
		)
		self.checkbox_box.accepted.connect(self.accept)
		self.checkbox_box.rejected.connect(self.reject)

		checkbox_layout = QHBoxLayout()
		checkbox_layout.addWidget(self.checkbox_box)
		checkbox_layout.setAlignment(QtCore.Qt.AlignHCenter)
		self.checkbox_box.layout().setContentsMargins(0, 0, 0, 0)
		self.checkbox_box.layout().setAlignment(QtCore.Qt.AlignLeft)
		self.layout.addLayout(checkbox_layout)
		self.setLayout(self.layout)

	# ------------------------------------------------------------------------

	def selected_items(self) -> list[tuple[str, int]]:
		selected = [
			(self.items[i], round(self.spinboxes[i].value(), 2))
			for i in range(len(self.items))
		]
		return selected


# --------------------------------------------------------------------------


class MoveDialog(QDialog):
	def __init__(
		self,
		title: str,
		value_title: str,
		options: list[str],
		parent: QWidget | None = None,
	) -> None:
		super().__init__(parent)

		self.setWindowTitle(title)
		self.setFixedWidth(400)
		self.group = QVBoxLayout()
		self.input_group = QHBoxLayout()
		self.button_group = QHBoxLayout()
		self.main_layout = QVBoxLayout()
		self.selected_option = None
		self.options = options
		self.decimal_input = QDoubleSpinBox()
		self.decimal_input.setRange(-sys.float_info.max, sys.float_info.max)
		for option in options:
			rb = QRadioButton(option)
			rb.toggled.connect(self._updateSelectedOption)
			self.group.addWidget(rb)
		self.input_group.addWidget(QLabel(value_title))
		self.input_group.addWidget(self.decimal_input)
		self.group.addLayout(self.input_group)
		ok_button = QPushButton("OK")
		ok_button.clicked.connect(self.accept)
		cancel_button = QPushButton("Cancel")
		cancel_button.clicked.connect(self.reject)
		self.button_group.addWidget(ok_button)
		self.button_group.addWidget(cancel_button)
		self.group.addLayout(self.button_group)
		self.main_layout.addLayout(self.group)
		self.setLayout(self.main_layout)

	# ------------------------------------------------------------------------

	def _updateSelectedOption(  # noqa: N802
		self, checked: bool  # noqa: FBT001
	) -> None:
		if checked:
			sender = self.sender()
			self.selected_option = self.options.index(sender.text())

	# ------------------------------------------------------------------------

	def getSelectedOption(self) -> int:  # noqa: N802
		return self.selected_option

	# ------------------------------------------------------------------------

	def getDecimalValue(self) -> float:  # noqa: N802
		return self.decimal_input.value()


# --------------------------------------------------------------------------


class PairofPointsDialog(QDialog):
	def __init__(
		self, title: str, items: list[str], parent: QWidget | None = None
	) -> None:
		super().__init__(parent)
		self.setWindowTitle(title)
		# self.setFixedWidth(225)
		self.setMinimumWidth(250)  # Allows wider but sets minimum
		self.items = items
		self.checkboxes = []
		self.layout = QVBoxLayout()
		for item in items:
			checkbox = QCheckBox(item)
			self.checkboxes.append(checkbox)
			self.layout.addWidget(checkbox)
		self.checkbox_box = QDialogButtonBox(
			QDialogButtonBox.Ok | QDialogButtonBox.Cancel
		)
		self.checkbox_box.accepted.connect(self.accept)
		self.checkbox_box.rejected.connect(self.reject)

		checkbox_layout = QHBoxLayout()
		checkbox_layout.addWidget(self.checkbox_box)
		checkbox_layout.setAlignment(QtCore.Qt.AlignHCenter)
		self.checkbox_box.layout().setContentsMargins(0, 0, 0, 0)
		self.checkbox_box.layout().setAlignment(QtCore.Qt.AlignLeft)
		self.layout.addLayout(checkbox_layout)
		self.setLayout(self.layout)
		self.selection_error_title = "Selection Error"
		self.selection_error_message = (
			"Exactly 2 points must be selected for this operation."
		)

	# -----------------------------------------------------------------------

	def selected_items(self) -> list[str]:
		selected = [
			self.items[i]
			for i, checkbox in enumerate(self.checkboxes)
			if checkbox.isChecked()
		]
		if len(selected) != MUST_HAVE_EXACTLY_TWO_SELECTIONS:
			raise SelectionError(
				self.selection_error_title, self.selection_error_message
			)

		return selected

	# ------------------------------------------------------------------------


class SelectItemsDialog(QDialog):
	def __init__(
		self, title: str, items: list[str], parent: QWidget | None = None
	) -> None:
		super().__init__(parent)
		self.setWindowTitle(title)
		self.setFixedWidth(225)
		self.items = items
		self.checkboxes = []
		self.layout = QVBoxLayout()
		for item in items:
			checkbox = QCheckBox(item)
			self.checkboxes.append(checkbox)
			self.layout.addWidget(checkbox)

		self.checkbox_box = QDialogButtonBox(
			QDialogButtonBox.Ok | QDialogButtonBox.Cancel
		)
		self.checkbox_box.accepted.connect(self.accept)
		self.checkbox_box.rejected.connect(self.reject)

		checkbox_layout = QHBoxLayout()
		checkbox_layout.addWidget(self.checkbox_box)
		checkbox_layout.setAlignment(QtCore.Qt.AlignHCenter)
		self.checkbox_box.layout().setContentsMargins(0, 0, 0, 0)
		self.checkbox_box.layout().setAlignment(QtCore.Qt.AlignLeft)

		# THIS LINE WAS MISSING - add the button layout to the main layout
		self.layout.addLayout(checkbox_layout)

		self.setLayout(self.layout)

	def selected_items(self) -> list[str]:
		selected = [
			self.items[i]
			for i, checkbox in enumerate(self.checkboxes)
			if checkbox.isChecked()
		]
		return selected


# --------------------------------------------------------------------------


class SetNamesDialog(QDialog):
	def __init__(
		self,
		title: str,
		label: str,
		default_names: list[str],
		max_chars: int,
		parent: QWidget | None = None,
	) -> None:
		super().__init__(parent)

		self.setWindowTitle(title)
		self.setMinimumSize(400, 200)

		# Create a layout for the dialog
		layout = QVBoxLayout(self)

		# Create a label to instruct the user
		instruction_label = QLabel(label, self)
		layout.addWidget(instruction_label)

		# Create a scroll area for the line edits
		scroll_area = QScrollArea(self)
		scroll_area.setWidgetResizable(True)
		layout.addWidget(scroll_area)

		# Create a container widget for the line edits
		container = QWidget()
		scroll_area.setWidget(container)
		line_edit_layout = QVBoxLayout(container)

		# Create a list of line edits to allow the user to input multiple names
		self.line_edits = []
		for default_name in default_names:
			line_edit = QLineEdit(self)
			line_edit.setText(default_name)
			line_edit.setMaxLength(max_chars)
			line_edit_layout.addWidget(line_edit)
			self.line_edits.append(line_edit)

		# Create a button box with OK and Cancel buttons
		button_box = QDialogButtonBox(
			QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self
		)
		button_box.accepted.connect(self.validate_and_accept)
		button_box.rejected.connect(self.reject)

		# Add the button box to the layout
		layout.addWidget(button_box)

		# Set the dialog to return the value of the line edits when accepted
		self.setResult(0)

	def getNames(self) -> list:  # noqa: N802
		# Retrieve the text of the line edits when the dialog is accepted
		return [line_edit.text() for line_edit in self.line_edits]

	def validate_and_accept(self) -> None:
		#
		if len(self.line_edits) != len(set(self.line_edits)):
			title = "Duplicate Names/labels"
			message = (
				"All names/labels must be distinct. "
				"Please correct the duplicate names."
			)
			raise SelectionError(title, message)
		self.accept()


# --------------------------------------------------------------------------


class SetValueDialog(QDialog):
	def __init__(
		self,
		title: str,
		label: str,
		min_val: float,
		max_val: float,
		an_integer: bool,  # noqa: FBT001
		default_value: float,
		parent: QWidget | None = None,
	) -> None:
		super().__init__(parent)

		self.setWindowTitle(title)
		self.setFixedSize(325, 125)

		# Create a layout for the dialog
		layout = QVBoxLayout(self)

		# Create a label and spin box to allow the user to set a value
		label = QLabel(label, self)
		if an_integer:  # == True
			self.spin_box = QSpinBox(self)
		else:
			self.spin_box = QDoubleSpinBox(self)
		self.spin_box.setFixedWidth(100)
		self.spin_box.setAlignment(QtCore.Qt.AlignHCenter)
		self.spin_box.setMinimum(min_val)
		self.spin_box.setMaximum(max_val)
		self.spin_box.setValue(default_value)

		# Add the label and spin box to the layout
		layout.addWidget(label)
		layout.addWidget(self.spin_box)
		layout.setAlignment(QtCore.Qt.AlignHCenter)

		# Create a button box with OK and Cancel buttons
		button_box = QDialogButtonBox(
			QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self
		)
		button_box.accepted.connect(self.accept)
		button_box.rejected.connect(self.reject)

		# Add the button box to the layout
		layout.addWidget(button_box)

		# Set the dialog to return the value of the spin box when accepted
		self.setResult(0)

	def getValue(self) -> float:  # noqa: N802
		# Retrieve the value of the spin box when the dialog is accepted
		return self.spin_box.value()


# --------------------------------------------------------------------------


class GetIntegerDialog(QDialog):
	"""Simple dialog to get an integer value with min/max validation."""

	def __init__(
		self,
		title: str,
		message: str,
		min_value: int = 1,
		max_value: int = 100,
		default_value: int | None = None,
		parent: QWidget | None = None,
	) -> None:
		super().__init__(parent)

		self.setWindowTitle(title)
		self.setFixedSize(350, 150)

		# Create main layout
		layout = QVBoxLayout(self)

		# Add message label
		label = QLabel(message, self)
		layout.addWidget(label)

		# Create spin box for integer input
		self.spin_box = QSpinBox(self)
		self.spin_box.setFixedWidth(100)
		self.spin_box.setAlignment(QtCore.Qt.AlignHCenter)
		self.spin_box.setMinimum(min_value)
		self.spin_box.setMaximum(max_value)
		if default_value is None:
			default_value = min_value
		self.spin_box.setValue(default_value)

		# Add spin box to layout
		layout.addWidget(self.spin_box)
		layout.setAlignment(QtCore.Qt.AlignHCenter)

		# Create button box with OK and Cancel buttons
		button_box = QDialogButtonBox(
			QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self
		)
		button_box.accepted.connect(self.accept)
		button_box.rejected.connect(self.reject)

		# Add button box to layout
		layout.addWidget(button_box)

	# ------------------------------------------------------------------------

	def get_value(self) -> int:
		"""Return the integer value entered by the user."""
		return self.spin_box.value()


# --------------------------------------------------------------------------


class GetStringDialog(QDialog):
	"""Simple dialog to get a string value with optional max length."""

	def __init__(
		self,
		title: str,
		message: str,
		max_length: int = 32,
		default_value: str = "",
		parent: QWidget | None = None,
	) -> None:
		super().__init__(parent)

		self.setWindowTitle(title)
		self.setFixedSize(400, 150)

		# Create main layout
		layout = QVBoxLayout(self)

		# Add message label
		label = QLabel(message, self)
		layout.addWidget(label)

		# Create line edit for string input
		self.line_edit = QLineEdit(self)
		self.line_edit.setMaxLength(max_length)
		self.line_edit.setText(default_value)

		# Add line edit to layout
		layout.addWidget(self.line_edit)

		# Create button box with OK and Cancel buttons
		button_box = QDialogButtonBox(
			QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self
		)
		button_box.accepted.connect(self.accept)
		button_box.rejected.connect(self.reject)

		# Add button box to layout
		layout.addWidget(button_box)

	# ------------------------------------------------------------------------

	def get_value(self) -> str:
		"""Return the string value entered by the user."""
		return self.line_edit.text()


# --------------------------------------------------------------------------


class GetCoordinatesDialog(QDialog):
	"""Dialog to get N coordinate values for N-dimensional space."""

	def __init__(
		self,
		title: str,
		message: str,
		ndim: int,
		parent: QWidget | None = None,
	) -> None:
		super().__init__(parent)

		self.setWindowTitle(title)
		self.setFixedSize(400, 100 + (ndim * 40))

		# Create main layout
		layout = QVBoxLayout(self)

		# Add message label
		label = QLabel(message, self)
		layout.addWidget(label)

		# Create grid layout for coordinate inputs
		grid_layout = QGridLayout()

		# Create spin boxes for each dimension
		self.spin_boxes: list[QDoubleSpinBox] = []
		for each_dim in range(ndim):
			dim_label = QLabel(f"Dimension {each_dim + 1}:", self)
			grid_layout.addWidget(dim_label, each_dim, 0)

			spin_box = QDoubleSpinBox(self)
			spin_box.setMinimum(-9999.0)
			spin_box.setMaximum(9999.0)
			spin_box.setDecimals(3)
			spin_box.setValue(0.0)
			grid_layout.addWidget(spin_box, each_dim, 1)

			self.spin_boxes.append(spin_box)

		layout.addLayout(grid_layout)

		# Create button box with OK and Cancel buttons
		button_box = QDialogButtonBox(
			QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self
		)
		button_box.accepted.connect(self.accept)
		button_box.rejected.connect(self.reject)

		# Add button box to layout
		layout.addWidget(button_box)

	# ------------------------------------------------------------------------

	def get_values(self) -> list[float]:
		"""Return the list of coordinate values entered by the user."""
		return [spin_box.value() for spin_box in self.spin_boxes]
