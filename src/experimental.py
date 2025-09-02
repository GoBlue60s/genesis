from __future__ import annotations

import pandas as pd
import peek # noqa: F401

from pyqtgraph.Qt import QtCore
from PySide6.QtWidgets import (
	QTableWidget, QTableWidgetItem, QVBoxLayout,QWidget
)
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from director import Status
    from common import Spaces
from constants import (
	INDEX_OF_FIRST_DIMENSION_NAME_IN_DIM_NAMES,
	INDEX_OF_FOURTH_DIMENSION_NAME_IN_DIM_NAMES,
	INDEX_OF_SECOND_DIMENSION_NAME_IN_DIM_NAMES,
	INDEX_OF_THIRD_DIMENSION_NAME_IN_DIM_NAMES,
	INDEX_OF_LABEL_IN_ROW,
	INDEX_OF_LOCATION_IN_ROW,
	INDEX_OF_NAME_IN_ROW,
	LEN_WHEN_NAME_AND_LABEL_ONLY,
	LEN_WHEN_NAME_ONLY,
	TEST_FOR_LESS_THAN_FOUR_COORDINATES,
	TEST_FOR_LESS_THAN_THREE_COORDINATES,
	TEST_FOR_LESS_THAN_TWO_COORDINATES,
	TEST_FOR_MIN_ROW_LENGTH,
)
from exceptions import SpacesError
from geometry import Point



# --------------------------------------------------------------------------


class DataFrameViewer(QWidget):
	#   This is used by the tester command
	def __init__(
			self,
			dataframe: pd.DataFrame = None) -> None:
		super().__init__()

		self.table_widget: QTableWidget = QTableWidget()
		self.dataframe = dataframe if dataframe is not None else pd.DataFrame()

		self.init_ui()

# --------------------------------------------------------------------------

	def init_ui(self) -> None:
		"""Initialize the user interface components of the DataFrame Viewer.
		
		Sets up the window title, dimensions, and creates a QTableWidget
		to display the pandas DataFrame. The table is configured with
		appropriate headers and populated with data from the DataFrame.
		"""
		tab_height = 800  # had been 1000
		tab_width = 800  # had been 1000
		self.setWindowTitle("DataFrame Viewer")
		self.setGeometry(300, 500, tab_width, tab_height)

		# Create a QTableWidget to display the DataFrame
		self.table_widget = QTableWidget(self)
		self.table_widget.setRowCount(self.dataframe.shape[0])
		self.table_widget.setColumnCount(self.dataframe.shape[1])
		self.table_widget.setHorizontalHeaderLabels(map(
			str, self.dataframe.columns))
		self.table_widget.setVerticalHeaderLabels(map(
			str, self.dataframe.index))

		# Populate the QTableWidget with the DataFrame data
		for row in range(self.dataframe.shape[0]):
			for col in range(self.dataframe.shape[1]):
				item = QTableWidgetItem(str(self.dataframe.iloc[row, col]))
				item.setTextAlignment(
					QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
				self.table_widget.setItem(row, col, item)

		self.table_widget.resizeColumnsToContents()
		self.table_widget.resizeRowsToContents()  # ????????????????

		# Create a layout and add the table widget to it
		tab_output_layout = QVBoxLayout()
		tab_output_layout.addWidget(self.table_widget)

		self.setLayout(tab_output_layout)

# -------------------------------------------------------------------------


class Item:
	def __init__(
			self,
			name: str = "",
			label: str = "",
			location: Point = None) -> None:
		"""Initialize an Item with a name, label, and location.
		
		Args:
			name: The name of the item
			label: The display label for the item
			location: The Point object representing the item's location
		"""

		# self.index: int = index
		self.name: str = name
		self.label: str = label
		self.location: Point = location if location else Point()

# -------------------------------------------------------------------------

class ItemFrame:
	"""A DataFrame-like structure for storing points with dimensional
	coordinates.
	
	Provides storage for Items with locations and offers dimension-specific
	coordinate lists for plotting.
	"""

	def __init__(
			self,
			data: dict | None=None,
			index: int | None=None,
			columns: list[str] | None=None,
			dim_names: list[str] | None=None,
			dim_labels: list[str] | None=None) -> None:
		"""Initialize an ItemFrame with configuration data.
		
		Args:
			data: Dictionary of Item objects or list of values
			index: Row indices or names
			columns: Names of Item attributes to expose as columns
			dim_names: Names of dimensions for coordinate data
			dim_labels: Display labels for dimensions
		
		"""
		"""Initialize an ItemFrame with configuration data.
		
		Args:
			data: Dictionary of Item objects or list of values
			index: Row indices or names
			columns: Names of Item attributes to expose as columns
			dim_names: Names of dimensions for coordinate data
			dim_labels: Display labels for dimensions
		
		"""
		self._data = {}
		self._index = index if index is not None else []
		self._columns = columns \
			if columns is not None else ["name", "label", "location"]
		self._dim_names = dim_names if dim_names is not None else ["x", "y"]
		self._dim_labels = dim_labels \
			if dim_labels is not None else ["X", "Y"]
		self._empty_ItemFrame_error_title = "Empty ItemFrame"
		self._empty_ItemFrame_error_message = "The ItemFrame contains no data."

		# Process input data
		if isinstance(data, dict):
			self._data = data
			if not index:
				self._index = list(data.keys())
		elif isinstance(data, list):
			for item_index, row in enumerate(data):
				idx = index[item_index] \
					if index and item_index < len(index) else item_index
				if isinstance(row, Item):
					self._data[idx] = row
				else:
					# Assume row contains values in column order
					self._data[idx] = self._create_item_from_row(row)
		
		# Set shape attribute (rows, columns)
		self._shape = (len(self._data), len(self._columns))

	def _create_item_from_row(self, row: int) -> Item:
		"""Create an Item from a list of values.
		
		Args:
			row: List of values [name, label, *coordinates]
			
		Returns:
			Item: A new Item object with the provided values
		
		"""
		
		if len(row) >= TEST_FOR_MIN_ROW_LENGTH \
			and isinstance(row[INDEX_OF_LOCATION_IN_ROW], Point):
			item = Item(
				name=row[INDEX_OF_NAME_IN_ROW],
				label=row[INDEX_OF_LABEL_IN_ROW],
				location=row[INDEX_OF_LOCATION_IN_ROW])
			return item
		if len(row) >= TEST_FOR_MIN_ROW_LENGTH:
			# Name, label, plus at least one coordinate
			coord_dict = {}
			
			# Map coordinates to dimension names
			for dim_index, dim_name in enumerate(self._dim_names):
				if dim_index + 2 < len(row):
					# +2 because first two elements are name, label
					coord_dict[dim_name] = row[dim_index + 2]
			
			# Create Point with mapped coordinates
			location = Point(**coord_dict)
			item = Item(name=row[INDEX_OF_NAME_IN_ROW],
				label=row[INDEX_OF_LABEL_IN_ROW], location=location)
			return item
		if len(row) == LEN_WHEN_NAME_AND_LABEL_ONLY:
			item = Item(name=row[INDEX_OF_NAME_IN_ROW],\
				label=row[INDEX_OF_LABEL_IN_ROW])
			return item
		if len(row) == LEN_WHEN_NAME_ONLY:
			item = Item(name=row[INDEX_OF_NAME_IN_ROW])
			return item
		
		# Default case if none of the above conditions are met
		return Item()
	
	def item(self, index: int | str) -> Item:
		"""Get an item by index."""
		return self[index]

	def get_dimension_coords(self, dim_name: str) -> list[float]:
		"""Get all coordinate values for a specific dimension.
		
		Args:
			dim_name: Name of the dimension to extract
			
		Returns:
			list: List of coordinates for the specified dimension
		
		"""
		coords = []
		for idx in self._index:
			item = self._data.get(idx)
			if item and hasattr(item, "location"):
				# Try to get the coordinate, default to None if not found
				try:
					coord_value = item.location[dim_name]
					coords.append(coord_value)
				except (KeyError, AttributeError):
					coords.append(None)
		return coords
	
	def get_all_dimension_coords(self) -> dict:
		"""Get all coordinate values organized by dimension.
		
		Returns:
			dict: Dictionary with dimension names as keys and coordinate
			lists as values
		
		"""
		dim_coords = {}
		for dim_name in self._dim_names:
			coord_list = self.get_dimension_coords(dim_name)
			dim_coords[dim_name] = coord_list
		return dim_coords
	
	@property
	def dim_1_coords(self) -> list[float]:
		"""Get all coordinates for dimension 1 as a list."""

		dim_name = self._dim_names[
			INDEX_OF_FIRST_DIMENSION_NAME_IN_DIM_NAMES] \
				if self._dim_names else "x"
		coords = self.get_dimension_coords(dim_name)
		return coords
	
	@property
	def dim_2_coords(self) -> list[float]:
		"""Get all coordinates for dimension 2 as a list."""
		if len(self._dim_names) < TEST_FOR_LESS_THAN_TWO_COORDINATES:
			return []
		dim_name = self._dim_names[
			INDEX_OF_SECOND_DIMENSION_NAME_IN_DIM_NAMES]
		coords = self.get_dimension_coords(dim_name)
		return coords
	
	@property
	def dim_3_coords(self) -> list[float]:
		"""Get all coordinates for dimension 3 as a list."""
		if len(self._dim_names) < TEST_FOR_LESS_THAN_THREE_COORDINATES:
			return []
		dim_name = self._dim_names[INDEX_OF_THIRD_DIMENSION_NAME_IN_DIM_NAMES]
		coords = self.get_dimension_coords(dim_name)
		return coords
	
	@property
	def dim_4_coords(self) -> list[float]:
		"""Get all coordinates for dimension 4 as a list."""
		if len(self._dim_names) < TEST_FOR_LESS_THAN_FOUR_COORDINATES:
			return []
		dim_name = self._dim_names[INDEX_OF_FOURTH_DIMENSION_NAME_IN_DIM_NAMES]
		coords = self.get_dimension_coords(dim_name)
		return coords
	
	def __getitem__(self, key: int | str) -> Item:
		"""Access an item by index or name.
		
		Args:
			key: Integer index or string name
			
		Returns:
			Item: The requested item
		
		Raises:
			SpacesError: If the item is not found
		
		"""
		# If key is an integer, use it as an index in _index
		if isinstance(key, int):
			if key >= len(self._index):
				index_error_title = "Index Error"
				error_message = f"Index {key} out of range"
				raise SpacesError(index_error_title, error_message)
				
			idx = self._index[key]
			item = self._data[idx]
			return item
			
		# If key is a string, find the item with matching name
		if isinstance(key, str):
			# First check if it's directly in _data
			if key in self._data:
				item = self._data[key]
				return item
				
			# Then search by name
			for idx in self._index:
				item = self._data.get(idx)
				if item and item.name == key:
					return item
					
			key_error_title = "Key Error"
			error_message = f"No item with name '{key}' found"
			raise SpacesError(key_error_title, error_message)
		type_error_title = "Type Error"
		type_error_message = f"Invalid key type: {type(key)}"
		raise SpacesError(type_error_title, type_error_message)

	def __str__(self) -> str:
		"""Create a simplified string representation of the ItemFrame
		without labels.
		
		Returns:
			str: Formatted table showing items with their coordinates
		
		"""
		if not self._data:
			error_title = "Empty ItemFrame"
			error_message = "The ItemFrame contains no data."
			raise SpacesError(error_title, error_message)
		
		# Calculate column widths
		name_width = \
			max([len(item.name) for item in self._data.values()] + [4])
		coord_width = 10  # Fixed width for coordinates
		
		# Create data rows without labels column
		rows = []
		
		# Create header row - include dimension names for coordinate
		# columns only
		header_parts = [' ' * name_width]  # Empty space for name column
		for dim in self._dim_labels:
			dim_str = f"{dim:>{coord_width}}"
			header_parts.append(dim_str)
		
		header = ' '.join(header_parts)
		rows.append(header)
		
		for idx in self._index:
			item = self._data.get(idx)
			if item and hasattr(item, 'location'):
				row_parts = [
					f"{item.name:<{name_width}}"
				]
				
				for dim in self._dim_names:
					value = item.location[dim]
					# Check if value is None before formatting
					if value is None:
						row_parts.append(f"{'N/A':>{coord_width}}")
					else:
						row_parts.append(f"{value:>{coord_width}.4f}")
				
				row = ' '.join(row_parts)
				rows.append(row)
		
		# Join rows with newlines
		result = "\n".join(rows)
		return result
	
	def full(self, *, show_headers: bool = True) -> str:
		"""Create a detailed string representation of the ItemFrame.
		
		It will include dimension headers and labels.

		Args:
			show_headers: Whether to show column headers (default: True)

		Returns:
			str: Formatted table showing detailed item data including labels
		
		"""
		if not self._data:
			raise SpacesError(
				self._empty_ItemFrame_error_title,
				self._empty_ItemFrame_error_message)

		# Calculate column widths
		name_width = \
			max([len(item.name) for item in self._data.values()] + [4])
		label_width = \
			max([len(item.label) for item in self._data.values()] + [5])
		coord_width = 10  # Fixed width for coordinates
		
		# Create header with dimension names only (no headers for Name/Label)
		header = f"{'Name':<{name_width}} {'Label':<{label_width}}"
		if show_headers:
			for dim in self._dim_labels:
				header += f" {dim:>{coord_width}}"
		
		# Create rows
		rows = [header]
		for idx in self._index:
			item = self._data.get(idx)
			if item and hasattr(item, 'location'):
				row = f"{item.name:<{name_width}} {item.label:<{label_width}}"
				for dim in self._dim_names:
					if hasattr(item.location, '_coords') \
						and dim in item.location._coords:
						value = item.location._coords[dim]
						if value is None:
							row += f" {'N/A':>{coord_width}}"
						else:
							row += f" {value:>{coord_width}.4f}"
					else:
						row += f" {'N/A':>{coord_width}}"
				rows.append(row)
		
		# Combine header and rows
		result = "\n".join(rows)
		return result


	# ------------------------------------------------------------------------

class RepresentationOfPoints:
	"""
	Configuration for representing points in a visualization.
	
	This class defines how a set of points from an ItemFrame should be
	displayed, including styling options and labels.
	
	Parameters
	----------
	itemframe : ItemFrame
		The ItemFrame containing the coordinate data for the points.
	label : str, optional
		Label to use for this set of points in legends or tooltips.
		Default is taken from itemframe.point_labels.
	color : str, optional
		Color to use for these points. Default is auto-assigned.
	marker : str, optional
		Marker style for the points. Default is 'o'.
	size : int, optional
		Size of the markers. Default is 5.
	"""
	
	def __init__(self,
			itemframe: ItemFrame,
			label: str | None = None,
			color: str | None = None,
			marker: str = 'o',
			size: int = 5) -> None:
		self.itemframe = itemframe
		# self.label = label if label is not None else itemframe.point_labels
		self.label = label
		self.color = color
		self.marker = marker
		self.size = size
		

	# ------------------------------------------------------------------------


class TesterCommand:
	""" The Tester command
	"""
	def __init__(
			self,
			director: Status,
			common: Spaces) -> None:

		self._director = director
		self.common = common
		self._director.command = "Tester"

		return

	# ------------------------------------------------------------------------

	def execute(
			self,
			common: Spaces) -> None:  # noqa: ARG002

		point_coords = self._director.configuration_active.point_coords

		self._director.record_command_as_selected_and_in_process()
		#
		print(point_coords)
		# app = QDialog()
		window = DataFrameViewer(point_coords)
		window.show()
		self._director.title_for_table_widget = "Tester"
		self._director.record_command_as_successfully_completed()
		return
