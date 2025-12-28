from __future__ import annotations

import itertools

from typing import NamedTuple
from exceptions import SpacesError

import numpy as np
from dataclasses import dataclass

from typing import TYPE_CHECKING

if TYPE_CHECKING:
	from director import Status

from constants import (
	TEST_FOR_MORE_THAN_ONE_COORDINATE,
	TEST_FOR_MORE_THAN_TWO_COORDINATES,
	MINIMAL_DIFFERENCE_FROM_ZERO,
)


# --------------------------------------------------------------------------


class Region:
	def __init__(
		self,
		name: str = "",
		fill: str = "None",
		tribe: str = "None",
		color: str = "None",
		thickness: int = 1,
		style: str = "None",
		points: PeoplePoints | None = None,
	) -> None:
		self._name: str = name
		self._fill: str = fill
		self._tribe: str = tribe
		self._color: str = color
		self._thickness: int = thickness
		self._style = style
		self._points: PeoplePoints = (
			points if points is not None else PeoplePoints([], [])
		)


# --------------------------------------------------------------------------


class Circle(Region):
	def __init__(
		self,
		center: Point | None = None,
		radius: float | None = None,
		name: str = "",
		fill: str = "None",
		tribe: str = "None",
		points: PeoplePoints | None = None,
		color: str = "None",
		thickness: int = 1,
		style: str = "None",
	) -> None:
		super().__init__(name, fill, tribe, color, thickness, style)

		self._center = center
		self._radius = radius
		self._points: PeoplePoints = points if points else PeoplePoints([], [])
		self._fill = fill
		self._tribe: str = tribe
		self._color: str = color
		self._thickness: int = thickness
		self._style = style


# -------------------------------------------------------------------------


class Corners(NamedTuple):
	upper_left: bool = False
	lower_left: bool = False
	upper_right: bool = False
	lower_right: bool = False


# -------------------------------------------------------------------------


class LineInPlot:
	def __init__(
		self,
		director: Status | None = None,
		point_on_line: Point | None = None,
		slope: float | None = None,
		color: str = "black",
		thickness: int = 1,
		style: str = "solid",
	) -> None:
		# Initialize all attributes with default values
		self._director: Status | None = None
		self._direction: str = ""
		self._intercept: float = 0.0
		self._theoretical_extremes: TheoreticalExtremes = TheoreticalExtremes()
		self._potential_extremes: TheoreticalExtremes = TheoreticalExtremes()
		self._y_at_hor_max: float = 0.0
		self._y_at_hor_min: float = 0.0
		self._x_at_vert_max: float = 0.0
		self._x_at_vert_min: float = 0.0
		self._goes_through: Sides = Sides()
		self._intersects: Sides = Sides()
		self._right_side: bool = False
		self._left_side: bool = False
		self._top: bool = False
		self._bottom: bool = False
		self._x: float | None = None
		self._y: float | None = None
		self._cross_x: float | None = None
		self._cross_y: float | None = None
		self._slope: float = 0.0
		self._color: str = color
		self._thickness: int = thickness
		self._style: str = style
		self._case: str = ""
		self._start: Point = Point(0.0, 0.0)
		self._end: Point = Point(0.0, 0.0)

		# Only execute if all required parameters are provided
		if (
			director is not None
			and point_on_line is not None
			and slope is not None
		):
			self._execute(
				director, point_on_line, slope, color, thickness, style
			)

	def _execute(
		self,
		director: Status,
		point_on_line: Point,
		slope: float,
		color: str,
		thickness: int,
		style: str,
	) -> None:
		self._director = director
		direction, intercept = self._get_line_direction_and_intercept(
			slope, point_on_line
		)
		potential_extremes = self._get_extremes(
			slope, intercept, direction, point_on_line
		)
		intersects = self._sides_line_goes_through(
			direction, potential_extremes
		)
		self._get_line_case_start_and_end(
			direction, intersects, point_on_line, potential_extremes
		)

		self._x = point_on_line.x
		self._y = point_on_line.y
		self._cross_x = point_on_line.x
		self._cross_y = point_on_line.y
		self._slope = slope
		self._color = color
		self._thickness = thickness
		self._style = style

	# ------------------------------------------------------------------------

	def _get_line_direction_and_intercept(
		self, slope: float, point_on_line: Point
	) -> tuple[str, float]:
		direction = self._line_direction(slope)
		intercept = self._line_intercept(point_on_line, slope)

		self._direction = direction
		self._intercept = intercept

		return (direction, intercept)

	# ------------------------------------------------------------------------

	def _get_extremes(
		self,
		slope: float,
		intercept: float,
		direction: str,
		point_on_line: Point
	) -> TheoreticalExtremes:
		theoretical_extremes = self._calculate_theoretical_extremes(
			slope, intercept, point_on_line
		)

		potential_extremes = self._adjust_extremes_when_flat(
			direction, theoretical_extremes
		)

		self._theoretical_extremes = theoretical_extremes
		self._potential_extremes = potential_extremes
		self._y_at_hor_max = potential_extremes.y_at_hor_max
		self._y_at_hor_min = potential_extremes.y_at_hor_min
		self._x_at_vert_max = potential_extremes.x_at_vert_max
		self._x_at_vert_min = potential_extremes.x_at_vert_min

		return potential_extremes

	# -----------------------------------------------------------------------

	def _sides_line_goes_through(
		self, direction: str, potential_extremes: TheoreticalExtremes
	) -> Sides:
		right_side = self._check_right_side(
			direction, potential_extremes.y_at_hor_max
		)
		left_side = self._check_left_side(direction, potential_extremes)
		top = self._check_top(direction, potential_extremes)
		bottom = self._check_bottom(direction, potential_extremes)
		goes_through = Sides(left_side, right_side, top, bottom)

		intersects = self._handle_corners(goes_through, potential_extremes)

		self._goes_through = goes_through
		self._intersects = intersects
		self._right_side = intersects.right_side
		self._left_side = intersects.left_side
		self._top = intersects.top
		self._bottom = intersects.bottom

		return intersects

	# ------------------------------------------------------------------------

	def _get_line_case_start_and_end(
		self,
		direction: str,
		intersects: Sides,
		point_on_line: Point,
		potential_extremes: TheoreticalExtremes,
	) -> tuple[str, Point, Point]:
		case = self._line_case(direction, intersects)
		(start, end) = self._line_ends_by_case(
			case, point_on_line, potential_extremes
		)

		self._case = case
		self._start = start
		self._end = end

		return (case, start, end)

	# ------------------------------------------------------------------------

	def _line_direction(self, slope: float) -> str:
		"""
		Determines the direction of a line based on its slope.
		"""

		if slope == float("inf") or slope == float("-inf"):
			direction = "Vertical"
		elif slope == 0.0:
			direction = "Flat"
		elif slope > 0.0:
			direction = "Upward slope"
		elif slope < 0.0:
			direction = "Downward slope"
		else:
			direction = "Direction needed to be set but was not"

		return direction

	# ------------------------------------------------------------------------

	def _line_intercept(self, point_on_line: Point, slope: float) -> float:
		"""Calculates the y-intercept, c,  of a line."""
		x = point_on_line.x
		y = point_on_line.y
		if x is None or y is None:
			error_title = "Invalid Point"
			error_message = "Point must have coordinates for line calculations"
			raise SpacesError(error_title, error_message)

		if abs(slope) < MINIMAL_DIFFERENCE_FROM_ZERO or slope == float("inf"):
			c = y
		else:
			c = y - (slope * x)
		return c

	# ------------------------------------------------------------------------

	def _calculate_theoretical_extremes(
		self, slope: float, intercept: float, point_on_line: Point
	) -> TheoreticalExtremes:
		(hor_max, hor_min, vert_max, vert_min) = (
			self._director.common.use_plot_ranges()
		)

		if slope == float("inf") or slope == float("-inf"):
			x_value = point_on_line.x
			if x_value is None:
				error_title = "Invalid Point"
				error_message = "Point must have x coordinate"
				raise SpacesError(error_title, error_message)
			return TheoreticalExtremes(
				float("NaN"), float("NaN"), x_value, x_value
			)

		y_at_hor_max = (slope * hor_max) + intercept
		y_at_hor_min = (slope * hor_min) + intercept

		if abs(slope) < MINIMAL_DIFFERENCE_FROM_ZERO:
			x_at_vert_max = hor_max
			x_at_vert_min = hor_min
		else:
			x_at_vert_max = (vert_max - intercept) / slope
			x_at_vert_min = (vert_min - intercept) / slope

		return TheoreticalExtremes(
			y_at_hor_max, y_at_hor_min, x_at_vert_max, x_at_vert_min
		)

	# ------------------------------------------------------------------------

	def _adjust_extremes_when_flat(
		self, direction: str, theoretical_extremes: TheoreticalExtremes
	) -> TheoreticalExtremes:
		"""
		Adjusts the theoretical extremes when the line is flat.

		"""
		(hor_max, hor_min, vert_max, vert_min) = (
			self._director.common.use_plot_ranges()
		)

		y_at_hor_max = theoretical_extremes.y_at_hor_max
		y_at_hor_min = theoretical_extremes.y_at_hor_min
		x_at_vert_max = theoretical_extremes.x_at_vert_max
		x_at_vert_min = theoretical_extremes.x_at_vert_min

		if direction == "Flat":
			if y_at_hor_max > vert_max > vert_min:
				y_at_hor_max = vert_max
			if y_at_hor_max < vert_min < vert_max:
				y_at_hor_max = vert_min
			if y_at_hor_min > vert_max > vert_min:
				y_at_hor_min = vert_max
			if y_at_hor_min < vert_min < vert_max:
				y_at_hor_min = vert_min
			if x_at_vert_max > hor_max > hor_min:
				x_at_vert_max = hor_max
			if x_at_vert_max < hor_min < hor_max:
				x_at_vert_max = hor_min
			if x_at_vert_min > hor_max > hor_min:
				x_at_vert_min = hor_max
			if x_at_vert_min < hor_min < hor_max:
				x_at_vert_min = hor_min

		return TheoreticalExtremes(
			y_at_hor_max, y_at_hor_min, x_at_vert_max, x_at_vert_min
		)

	# ------------------------------------------------------------------------

	def _check_right_side(self, direction: str, y_at_hor_max: float) -> bool:
		vert_max = self._director.common.plot_ranges.vert_max
		vert_min = self._director.common.plot_ranges.vert_min

		right_side = False

		if direction == "Flat" or (vert_min <= y_at_hor_max <= vert_max):
			right_side = True

		return right_side

	# ------------------------------------------------------------------------

	def _check_left_side(
		self, direction: str, potential_extremes: TheoreticalExtremes
	) -> bool:
		vert_max = self._director.common.plot_ranges.vert_max
		vert_min = self._director.common.plot_ranges.vert_min
		y_at_hor_min = potential_extremes.y_at_hor_min
		left_side = False

		if direction == "Flat" or (vert_min <= y_at_hor_min <= vert_max):
			left_side = True

		return left_side

	# ------------------------------------------------------------------------

	def _check_top(
		self, direction: str, potential_extremes: TheoreticalExtremes
	) -> bool:
		hor_max = self._director.common.plot_ranges.hor_max
		hor_min = self._director.common.plot_ranges.hor_min
		x_at_vert_max = potential_extremes.x_at_vert_max
		top = False

		if direction == "Flat":
			top = False
		elif hor_min <= x_at_vert_max <= hor_max:
			top = True

		return top

	# ------------------------------------------------------------------------

	def _check_bottom(
		self, direction: str, potential_extremes: TheoreticalExtremes
	) -> bool:
		hor_max = self._director.common.plot_ranges.hor_max
		hor_min = self._director.common.plot_ranges.hor_min
		x_at_vert_min = potential_extremes.x_at_vert_min
		bottom = False

		if direction == "Flat":
			bottom = False
		elif hor_min <= x_at_vert_min <= hor_max:
			bottom = True

		return bottom

	# ------------------------------------------------------------------------

	def _handle_corners(
		self, goes_through: Sides, potential_extremes: TheoreticalExtremes
	) -> Sides:
		rivalry = self._director.rivalry

		(hor_max, hor_min, vert_max, vert_min) = (
			self._director.common.use_plot_ranges()
		)

		left_side = goes_through.left_side
		right_side = goes_through.right_side
		top = goes_through.top
		bottom = goes_through.bottom

		y_at_hor_max = potential_extremes.y_at_hor_max
		y_at_hor_min = potential_extremes.y_at_hor_min
		x_at_vert_max = potential_extremes.x_at_vert_max
		x_at_vert_min = potential_extremes.x_at_vert_min

		# Handle lines going through corners
		#
		# upper right
		if x_at_vert_max == hor_max and y_at_hor_max == vert_max:
			(top, right_side) = rivalry.choose_a_side_function()
		# upper left
		if x_at_vert_max == hor_min and y_at_hor_min == vert_max:
			(top, left_side) = rivalry.choose_a_side_function()
		# lower right
		if x_at_vert_min == hor_max and y_at_hor_max == vert_min:
			(bottom, right_side) = rivalry.choose_a_side_function()
		# lower left
		if x_at_vert_min == hor_min and y_at_hor_min == vert_min:
			(bottom, left_side) = rivalry.choose_a_side_function()

		return Sides(left_side, right_side, top, bottom)

	# -----------------------------------------------------------------------

	def _line_case(self, direction: str, intersects: Sides) -> str:
		left_side = intersects.left_side
		right_side = intersects.right_side
		top = intersects.top
		bottom = intersects.bottom

		case_dict = {
			("Flat",): "0a",
			("Vertical",): "0b",
			("Upward slope", True, True, False, False): "Ia",
			("Upward slope", True, False, True, False): "IIa",
			("Upward slope", False, True, False, True): "IIIa",
			("Upward slope", False, False, True, True): "IVa",
			("Downward slope", True, True, False, False): "Ib",
			("Downward slope", True, False, False, True): "IIb",
			("Downward slope", False, True, True, False): "IIIb",
			("Downward slope", False, False, True, True): "IVb",
		}

		# Construct the key
		key = (
			(direction,)
			if direction in ("Flat", "Vertical")
			else (direction, left_side, right_side, top, bottom)
		)

		case = case_dict.get(key, "Case needed to but was not set")

		return case

	# ------------------------------------------------------------------------

	def _line_ends_by_case(
		self,
		case: str,
		point_on_line: Point,
		potential_extremes: TheoreticalExtremes,
	) -> tuple[Point, Point]:


		start = Point()
		end = Point()

		(hor_max, hor_min, vert_max, vert_min) = (
			self._director.common.use_plot_ranges()
		)

		y_at_hor_max = potential_extremes.y_at_hor_max
		y_at_hor_min = potential_extremes.y_at_hor_min
		x_at_vert_max = potential_extremes.x_at_vert_max
		x_at_vert_min = potential_extremes.x_at_vert_min

		x = point_on_line.x
		y = point_on_line.y

		end_dict = {
			"0a": [hor_min, y, hor_max, y],
			"0b": [x, vert_max, x, vert_min],
			"Ia": [hor_min, y_at_hor_min, hor_max, y_at_hor_max],
			"IIa": [hor_min, y_at_hor_min, x_at_vert_max, vert_max],
			"IIIa": [x_at_vert_min, vert_min, hor_max, y_at_hor_max],
			"IVa": [x_at_vert_min, vert_min, x_at_vert_max, vert_max],
			"Ib": [hor_min, y_at_hor_min, hor_max, y_at_hor_max],
			"IIb": [hor_min, y_at_hor_min, x_at_vert_min, vert_min],
			"IIIb": [x_at_vert_max, vert_max, hor_max, y_at_hor_max],
			"IVb": [x_at_vert_max, vert_max, x_at_vert_min, vert_min],
		}

		if case not in end_dict:
			line_case_title = "Line Case Error"
			line_case_message = (
				f"Unhandled line case: '{case}'. "
				f"Direction: {self._direction}, "
				f"Intersects: left={self._left_side}, "
				f"right={self._right_side}, top={self._top}, "
				f"bottom={self._bottom}"
			)
			raise SpacesError(line_case_title, line_case_message)

		start.x = end_dict[case][0]
		start.y = end_dict[case][1]
		end.x = end_dict[case][2]
		end.y = end_dict[case][3]

		return (start, end)


# -------------------------------------------------------------------------


class PairOfPoints:
	def __init__(self, value: float, point_a: Point, point_b: Point) -> None:
		self._value: float = value
		self._point_a: Point = point_a
		self._point_b: Point = point_b
		self._name: str = point_a.name + "_" + point_b.name
		self._label: str = point_a.label + "_" + point_b.label


# --------------------------------------------------------------------------


@dataclass
class CoordinateLists:
	x: list[float]
	y: list[float]


# --------------------------------------------------------------------------


class PeoplePoints(CoordinateLists):
	def __init__(
		self,
		x: list[float],
		y: list[float],
		color: str = "black",
		size: int = 1,
		style: str = "dot",
	) -> None:
		super().__init__(x, y)
		self._x: list[float] = x
		self._y: list[float] = y
		self._color: str = color
		self._size: int = size
		self._style: str = style


# -----------------------------------------------------------------------


class PlotExtremes(NamedTuple):
	# Extremes renamed to PlotExtremes

	hor_max: float = 0.0
	hor_min: float = 0.0
	vert_max: float = 0.0
	vert_min: float = 0.0
	offset: float = 0.0


# ----------------------------------------------------------------------


class Point:
	def __init__(
		self, *args: float, **kwargs: float | str | None
	) -> None:
		"""Represents a point in n-dimensional space with dimension-neutral
		coordinate naming.

		The class uses 'dim_1', 'dim_2', etc. for internal storage but
		provides x, y, z properties as convenience accessors that don't
		dictate the coordinate meanings.

		Args:
			*args: Positional coordinates that map to dim_1, dim_2, etc.
			**kwargs: Named coordinates or metadata attributes
				- index: Optional index value for the point
				- name: Name of the point
				- label: Display label for the point
				- color: Color for visual display
				- size: Size when displayed
				- style: Display style (e.g., "dot")
				- kind: Type classification for the point
				- Any other keyword arguments will be treated as named
				coordinates

		Examples:
			# Standard positional usage (stores as x, y, z)
			pt1 = Point(1.0, 2.5, 3.0, name="Alpha")

			# Named coordinates with standard keywords
			pt2 = Point(x=1.0, y=2.5, z=3.0, name="Beta")

			# Named coordinates with custom dimension names (order matters
			#  for x/y/z mapping)
			pt3 = Point(Economic=1.0, Social=2.5, Foreign=3.0, name="Gamma")

			# For hyphenated or special dimension names, access them
			#  using dictionary notation:
			pt4 = Point(
				**{"Left-Right": 1.0, "Liberal-Conservative": 2.5},
				name="Delta")
			print(pt4["Left-Right"])  # Access hyphenated dimension: 1.0

			# Standard access methods
			print(pt1.x)              # Access standard coordinate: 1.0
			print(pt3["Economic"])    # Access named coordinate: 1.0
			print(pt3[0])            # Access first coordinate by index: 1.0

		"""
		# Store metadata attributes
		self.index: int | None = kwargs.pop("index", None)
		self.name: str = kwargs.pop("name", "")
		self.label: str = kwargs.pop("label", "")
		self.color: str = kwargs.pop("color", "black")
		self.size: int = kwargs.pop("size", 1)
		self.style: str = kwargs.pop("style", "dot")
		self.kind: str = kwargs.pop("kind", "")
		self.text_item: object | None = None  # For pyqtgraph TextItem widget

		# Store coordinates with dimension-neutral naming
		self._coords = {}

		# Handle positional args as dim_1, dim_2, etc.
		for i, arg in enumerate(args):
			dim_name = f"dim_{i + 1}"
			self._coords[dim_name] = float(arg)

		# Handle named coordinates from kwargs
		for key, value in kwargs.items():
			if value is not None:
				self._coords[key] = float(value)

	# x, y, z properties as convenience accessors that map to dimensions
	@property
	def x(self) -> float:
		"""First coordinate, regardless of its semantic meaning."""
		if "dim_1" in self._coords:
			return self._coords["dim_1"]
		if self._coords:
			return next(iter(self._coords.values()))
		msg = "Point has no coordinates - cannot access x"
		raise ValueError(msg)

	@x.setter
	def x(self, value: float | None) -> None:
		"""Set the first coordinate."""
		if value is None:
			return
		if "dim_1" in self._coords:
			self._coords["dim_1"] = float(value)
		elif self._coords:
			first_key = next(iter(self._coords.keys()))
			self._coords[first_key] = float(value)
		else:
			self._coords["dim_1"] = float(value)

	@property
	def y(self) -> float:
		"""Second coordinate, regardless of its semantic meaning."""

		if "dim_2" in self._coords:
			return self._coords["dim_2"]
		if len(self._coords) > TEST_FOR_MORE_THAN_ONE_COORDINATE:
			return next(itertools.islice(self._coords.values(), 1, None))
		msg = "Point has no coordinates - cannot access y"
		raise ValueError(msg)

	@y.setter
	def y(self, value: float | None) -> None:
		"""Set the second coordinate."""
		if value is None:
			return
		if "dim_2" in self._coords:
			self._coords["dim_2"] = float(value)
		elif len(self._coords) > TEST_FOR_MORE_THAN_ONE_COORDINATE:
			second_key = next(itertools.islice(self._coords.keys(), 1, None))
			self._coords[second_key] = float(value)
		else:
			self._coords["dim_2"] = float(value)

	@property
	def z(self) -> float | None:
		"""Third coordinate, regardless of its semantic meaning."""
		if "dim_3" in self._coords:
			return self._coords["dim_3"]
		if len(self._coords) > TEST_FOR_MORE_THAN_TWO_COORDINATES:
			return next(itertools.islice(self._coords.values(), 2, None))
		return None

	@z.setter
	def z(self, value: float | None) -> None:
		"""Set the third coordinate."""
		if value is None:
			return
		if "dim_3" in self._coords:
			self._coords["dim_3"] = float(value)
		elif len(self._coords) > TEST_FOR_MORE_THAN_TWO_COORDINATES:
			third_key = next(itertools.islice(self._coords.keys(), 2, None))
			self._coords[third_key] = float(value)
		else:
			self._coords["dim_3"] = float(value)

	def __getitem__(self, key: str | int) -> float | None:
		"""Access a coordinate value by name or index.

		Args:
			key: Either a string dimension name or integer index

		Returns:
			float: The coordinate value, or None if not found

		Examples:
			point["x"]    # Access by dimension name
			point[0]      # Access first coordinate by index
		"""
		# Allow access by dimension name, index, or semantic role
		if isinstance(key, int):
			# Access by index: point[0] -> first dimension
			dim_name = f"dim_{key + 1}"
			if dim_name in self._coords:
				return self._coords[dim_name]
			# If no dim_N naming, fall back to order of insertion
			try:
				return list(self._coords.values())[key]
			except IndexError:
				return None  # Out of range index
		else:
			# Direct key access: point["economic"] or point["dim_1"]
			return self._coords.get(key)

	def __setitem__(self, key: str | int, value: float) -> None:
		self._coords[key] = float(value)

	def __str__(self) -> str:
		"""Return a string representation of the Point with formatted
		coordinates.

		Returns:
			str: A string in the format 'Point(dim_1=1.234, dim_2=5.678, ...)'
		"""
		coords_str = ", ".join(f"{k}={v:.3f}" for k, v in self._coords.items())
		return f"Point({coords_str})"


# --------------------------------------------------------------------------


class Polygon(Region):
	def __init__(
		self,
		outline: np.ndarray | None = None,
		vertices: CoordinateLists | None = None,
		corners: Corners | None = None,
		name: str = "",
		fill: str = "None",
		tribe: str = "None",
		points: PeoplePoints | None = None,
		color: str = "None",
		thickness: int = 1,
		style: str = "None",
	) -> None:
		super().__init__(name, fill, tribe, color, thickness, style)

		self._outline = outline if outline is not None else np.array([], [])
		if vertices is None:
			vertices = CoordinateLists([], [])

		self._x: list[float] = vertices.x
		self._y: list[float] = vertices.y
		self._corners: Corners = corners
		self._points: PeoplePoints = points if points else PeoplePoints([], [])
		self._fill = fill
		self._tribe: str = tribe
		self._color: str = color
		self._thickness: int = thickness
		self._style = style

	@property
	def vertices(self) -> CoordinateLists:
		"""Return vertices as a CoordinateLists object."""
		return CoordinateLists(self._x, self._y)

	@vertices.setter
	def vertices(self, value: CoordinateLists) -> None:
		"""Set vertices from a CoordinateLists object."""
		self._x = value.x
		self._y = value.y

	@property
	def outline(self) -> np.ndarray:
		"""Return polygon outline."""
		return self._outline

	@outline.setter
	def outline(self, value: np.ndarray) -> None:
		"""Set polygon outline."""
		self._outline = value


# -------------------------------------------------------------------------


class Sides(NamedTuple):
	left_side: bool = False
	right_side: bool = False
	top: bool = False
	bottom: bool = False


# -------------------------------------------------------------------------


class TheoreticalExtremes(NamedTuple):
	y_at_hor_max: float = 0.0
	y_at_hor_min: float = 0.0
	x_at_vert_max: float = 0.0
	x_at_vert_min: float = 0.0
