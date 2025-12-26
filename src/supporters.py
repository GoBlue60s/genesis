from __future__ import annotations

from typing import TYPE_CHECKING

from exceptions import SpacesError

if TYPE_CHECKING:
	from director import Spaces, Status


# --------------------------------------------------------------------------


class AbstractCommand:
	def __init__(self, director: Status, common: Spaces) -> None:
		self._director = director
		self.common = common

	# ------------------------------------------------------------------------


class ASupporterGrouping(AbstractCommand):
	def __init__(self, director: Status, common: Spaces) -> None:
		super().__init__(director, common)

		self._hor_dim = self._director.common.hor_dim
		self._vert_dim = self._director.common.vert_dim
		self._point_size = self._director.common.point_size
		self._show_connector = self._director.common.show_connector
		self._dim_names = self._director.configuration_active.dim_names
		self._point_names = self._director.configuration_active.point_names
		self._point_labels = self._director.configuration_active.point_labels
		self._point_coords = self._director.configuration_active.point_coords
		self._offset = self._director.common.plot_ranges.offset

		rivalry = self._director.rivalry

		if self._director.common.have_reference_points():
			self._bisector = rivalry.bisector
			if self._bisector is None:
				error_title = "Missing Bisector"
				error_message = "Bisector not set with reference points"
				raise SpacesError(error_title, error_message)
			self._direction = self._bisector._direction
			self._west = rivalry.west
			self._east = rivalry.east
			self._seg = rivalry.seg
			self._score_1_name = self._director.scores_active.score_1_name
			self._score_2_name = self._director.scores_active.score_2_name
			self._core_left = rivalry.core_left
			self._core_right = rivalry.core_right
			self._core_neither = rivalry.core_neither
			self._base_left = rivalry.base_left
			self._base_right = rivalry.base_right
			self._base_neither = rivalry.base_neither
			self._likely_left = rivalry.likely_left
			self._likely_right = rivalry.likely_right
			self._battleground_segment = rivalry.battleground_segment
			self._battleground_settled = rivalry.battleground_settled

			self._convertible_to_left = rivalry.convertible_to_left
			self._convertible_to_right = rivalry.convertible_to_right

			self._convertible_settled = rivalry.convertible_settled
			self._first_left = rivalry.first_left
			self._first_right = rivalry.first_right
			self._second_up = rivalry.second_up
			self._second_down = rivalry.second_down
			self._east_cross_x = rivalry.east._cross_x
			self._east_cross_y = rivalry.east._cross_y
			self._west_cross_x = rivalry.west._cross_x
			self._west_cross_y = rivalry.west._cross_y

		self._nscored_individ = self._director.scores_active.nscored_individ
		return
