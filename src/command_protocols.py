"""Structural types describing what Spaces expects of a command.

Commands are plain classes with no common base class. These protocols
let the type checker treat any of them uniformly wherever code holds
"some command" (the director's current_command, script execution).
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
	from collections.abc import Callable

	from PySide6.QtWidgets import QWidget

# --------------------------------------------------------------------------


class SpacesCommand(Protocol):
	"""Any command: something with an execute method.

	Commands take execute(common) or execute(common, extra_value), so
	execute is typed loosely; script execution inspects the actual
	signature at run time.
	"""

	execute: Callable[..., None]


# --------------------------------------------------------------------------


class DisplayingCommand(SpacesCommand, Protocol):
	"""A command that builds its own Output tab widget.

	Commands whose widget_dict entry is "unique" provide _display.
	"""

	def _display(self) -> QWidget:
		"""Build the widget shown in the Output and Log tabs."""
		...
