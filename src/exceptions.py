from __future__ import annotations
import peek # noqa: F401

# -------------------------------------------------------------------------


class SpacesError(Exception):

	def __init__(
			self,
			title: str,
			message: str) -> None:
		super().__init__(title, message)
		self.title = title
		self.message = message
		return

# -------------------------------------------------------------------------


class DependencyError(SpacesError):

	def __init__(
			self,
			title: str,
			message: str) -> None:
		super().__init__(title, message)
		return

# -------------------------------------------------------------------------


class SelectionError(SpacesError):

	def __init__(
			self,
			title: str,
			message: str) -> None:
		super().__init__(title, message)
		return

# -------------------------------------------------------------------------


class InconsistentInformationError(SpacesError):

	def __init__(
			self,
			title: str,
			message: str) -> None:
		super().__init__(title, message)
		return
	
# -------------------------------------------------------------------------


class MissingInformationError(SpacesError):

	def __init__(
			self,
			title: str,
			message: str) -> None:
		super().__init__(title, message)
		return
	
# -------------------------------------------------------------------------


class UnderDevelopmentError(SpacesError):

	def __init__(
			self,
			title: str,
			message: str) -> None:
		super().__init__(title, message)
		return
# -------------------------------------------------------------------------


class UnknownTypeError(SpacesError):

	def __init__(
			self,
			title: str,
			message: str) -> None:
		super().__init__(title, message)
		return

# -------------------------------------------------------------------------


class SituationToBeNamedLaterError(SpacesError):

	def __init__(
			self,
			title: str,
			message: str) -> None:
		super().__init__(title, message)
		return

# ----------------------------------------------------------------------------


class ProblemReadingFileError(SpacesError):

	def __init__(
			self,
			title: str,
			message: str) -> None:
		super().__init__(title, message)
		return
