# Step 4: State Capture System Design

## Overview

This document describes the design of the state capture system for implementing undo functionality in Spaces. The design was completed on 2025-10-09.

## CommandState Class

**Location:** `src/command_state.py`

### Purpose

The `CommandState` class is the core data structure for undo support. It captures both command metadata and application state snapshots before command execution.

### Key Responsibilities

1. **Command Metadata Storage**
   - Command name (e.g., "Rotate", "Center")
   - Command type ("active" or "passive")
   - Command parameters (for script generation)
   - Timestamp of execution

2. **State Snapshot Capture**
   - Configuration data (points, dimensions, coordinates)
   - Correlations data
   - Similarities data
   - Evaluations data
   - Individuals data
   - Scores data
   - Grouped data
   - Target configuration
   - Application settings

3. **State Restoration**
   - Individual feature restoration methods
   - Complete state restoration via `restore_all_state()`

### Design Principles

1. **Copy, Don't Reference**
   - All DataFrames are copied using `.copy()`
   - All lists are copied using `.copy()`
   - Ensures immutability of snapshots

2. **Selective Capture**
   - Only capture features that exist (check for empty DataFrames)
   - Avoid capturing unnecessary data

3. **Symmetric Design**
   - Each `capture_*_state()` method has a corresponding `restore_*_state()` method
   - Consistent parameter patterns across all methods

## State Snapshot Structure

The `state_snapshot` dictionary contains nested dictionaries for each feature type:

```python
{
    "configuration": {
        "point_coords": DataFrame,
        "point_names": list[str],
        "point_labels": list[str],
        "dim_names": list[str],
        "dim_labels": list[str],
        "ndim": int,
        "npoint": int,
        "range_dims": range,
        "range_points": range,
        "hor_axis_name": str,
        "vert_axis_name": str,
        "distances_as_dataframe": DataFrame,
        "ranked_distances_as_dataframe": DataFrame
    },
    "correlations": { ... },
    "similarities": { ... },
    "evaluations": { ... },
    "individuals": { ... },
    "scores": { ... },
    "grouped_data": { ... },
    "target": { ... },
    "settings": { ... }
}
```

## Stack Management Design

### Existing Infrastructure (Preserved)

From `director.py`:
- `undo_stack: list[int]` - Currently stores integer IDs
- `undo_stack_source: list[str]` - Stores command names

### Proposed Enhancement

**Change:** Upgrade `undo_stack` to store `CommandState` objects instead of integers

**Implementation approach:**
```python
# In director.py EstablishSpacesStructure.__init__:
self.undo_stack: list[CommandState] = []  # Changed from list[int]
self.undo_stack_source: list[str] = []    # Preserved for compatibility
```

### Stack Management Methods (to be added to director.py)

```python
def push_undo_state(self, cmd_state: CommandState) -> None:
    """Add a command state to the undo stack.

    Args:
        cmd_state: The CommandState instance to push
    """
    self.undo_stack.append(cmd_state)
    self.undo_stack_source.append(cmd_state.command_name)

def pop_undo_state(self) -> CommandState | None:
    """Remove and return the most recent command state.

    Returns:
        The most recent CommandState, or None if stack is empty
    """
    if not self.undo_stack:
        return None

    self.undo_stack_source.pop()
    return self.undo_stack.pop()

def peek_undo_state(self) -> CommandState | None:
    """View the most recent command state without removing it.

    Returns:
        The most recent CommandState, or None if stack is empty
    """
    if not self.undo_stack:
        return None
    return self.undo_stack[-1]

def clear_undo_stack(self) -> None:
    """Clear all entries from the undo stack."""
    self.undo_stack.clear()
    self.undo_stack_source.clear()
```

### Integration with Existing Error Handling

The existing `unable_to_complete_command_set_status_as_failed()` method in `director.py` (lines 248-272) already handles removing failed commands from the undo stack. This pattern will continue to work with `CommandState` objects:

```python
def unable_to_complete_command_set_status_as_failed(self) -> None:
    # ... existing code ...

    # Remove last entry from undo stack
    if len(self.undo_stack) != 0:  # Changed condition from != 1
        del self.undo_stack[-1]
        del self.undo_stack_source[-1]

    # ... rest of existing code ...
```

## Capture Workflow

### For Active Commands

1. **Before command execution:**
   ```python
   from command_state import CommandState
   from dictionaries import command_dict

   # Determine what to capture based on command_dict metadata
   state_to_capture = command_dict[self.command]["state_capture"]

   # Create CommandState instance
   cmd_state = CommandState(
       command_name=self.command,
       command_type="active",
       command_params={}  # Populate with actual parameters
   )

   # Capture appropriate state
   if "configuration" in state_to_capture:
       cmd_state.capture_configuration_state(self)
   if "similarities" in state_to_capture:
       cmd_state.capture_similarities_state(self)
   # ... etc for other features

   # Push to undo stack
   self.push_undo_state(cmd_state)
   ```

2. **Execute command**

3. **If command fails:**
   - `unable_to_complete_command_set_status_as_failed()` removes the state

### For Passive Commands

Passive commands don't need state snapshots, but we still track them for session history:

```python
cmd_state = CommandState(
    command_name=self.command,
    command_type="passive",
    command_params={}  # For script generation
)
# Don't capture state - just record command was executed
self.push_undo_state(cmd_state)
```

## Restore Workflow

### Undo Command Execution

```python
# In UndoCommand.execute():
cmd_state = self.pop_undo_state()

if cmd_state is None:
    raise SpacesError("No previous command", "Nothing to undo")

if cmd_state.command_type == "passive":
    # Passive commands don't modify state, nothing to restore
    print(f"Undoing passive command: {cmd_state.command_name}")
    return

# Restore state for active command
cmd_state.restore_all_state(self._director)

# Trigger GUI refresh
self._director.create_widgets_for_output_and_log_tabs()
self._director.set_focus_on_tab("Output")

# If configuration was restored, recreate the plot
if "configuration" in cmd_state.state_snapshot:
    if self._director.common.have_active_configuration():
        self._director.create_configuration_plot_for_tabs()
```

## GUI Refresh Mechanism

### Existing Methods (Reused)

The director already has methods for refreshing the GUI after state changes:

1. **`create_widgets_for_output_and_log_tabs()`** (director.py:225-244)
   - Rebuilds the Output and Log tab widgets
   - Uses `BuildOutputForGUI` to create appropriate widgets

2. **`create_configuration_plot_for_tabs()`** (needs to be examined)
   - Recreates the plot based on current configuration
   - Already handles matplotlib/pyqtgraph selection

3. **`set_focus_on_tab(tab_name)`** (director.py:216-221)
   - Switches to the specified tab
   - Updates the tab widget

### Refresh Strategy

After restoring state, trigger the same GUI refresh sequence that normal commands use:

```python
def refresh_gui_after_undo(self, cmd_state: CommandState) -> None:
    """Refresh GUI elements after undo operation.

    Args:
        cmd_state: The command state that was just restored
    """
    # Rebuild output widgets
    self.create_widgets_for_output_and_log_tabs()

    # Recreate plot if configuration was affected
    if "configuration" in cmd_state.state_snapshot:
        if self.common.have_active_configuration():
            self.create_configuration_plot_for_tabs()
            self.set_focus_on_tab("Plot")
        else:
            self.set_focus_on_tab("Output")
    else:
        self.set_focus_on_tab("Output")

    # Update status bar
    self.spaces_statusbar.showMessage(
        f"Undid {cmd_state.command_name} command",
        5000
    )
```

### Plot Recreation

The plot system already separates data from presentation:
- **Data:** Stored in features (configuration, scores, etc.)
- **Presentation:** Created on-demand by matplotlib/pyqtgraph plotters

After restoring data state, calling the existing plot methods will automatically recreate the correct visualization.

## Memory Considerations

### Data Copying

Each `CommandState` stores complete copies of all relevant DataFrames. For typical Spaces datasets (10-50 points, 2-10 dimensions):
- Configuration: ~1-10 KB per snapshot
- Similarities: ~1-20 KB per snapshot
- Total per command: ~5-50 KB

A session with 100 commands would use ~0.5-5 MB for undo history - negligible on modern systems.

### Optimization Strategies (Future)

If memory becomes a concern:
1. **Limit stack depth** - Keep only N most recent commands
2. **Differential snapshots** - Store only changed features
3. **Compression** - Pickle and compress snapshots

## Integration Points

### Files Modified

1. **`src/director.py`**
   - Add stack management methods
   - Update `undo_stack` type annotation
   - Modify `record_command_as_selected_and_in_process()` to capture state

2. **`src/editmenu.py`**
   - Rewrite `UndoCommand.execute()` to use new system
   - Implement `RedoCommand` (future)

3. **`src/dictionaries.py`**
   - Already complete with `command_dict`
   - Will be referenced for `state_capture` metadata

### Files Created

1. **`src/command_state.py`**
   - Complete - no further changes needed

## Next Steps (Step 5)

With the state capture system designed, Step 5 will prototype the full undo cycle with the Rotate command:

1. Identify exact state changes in Rotate
2. Update `command_dict` with Rotate's `state_capture` requirements
3. Modify Rotate command to capture state before execution
4. Test undo/redo cycle
5. Verify GUI refresh works correctly
6. Document any issues or refinements needed

## Design Decisions and Rationale

### Why Separate Capture Methods?

Each feature has its own capture method (`capture_configuration_state()`, etc.) because:
- Features have different attributes and structure
- Allows selective capture based on `command_dict` metadata
- Makes code more maintainable and testable
- Enables future optimization (only capture what changed)

### Why Copy Everything?

Using `.copy()` for all DataFrames and lists because:
- Ensures snapshot immutability
- Prevents accidental mutation of historical states
- Slight performance cost is negligible for Spaces' data sizes
- Simpler than tracking references and mutations

### Why Not Use `*_last` Instances?

The existing `*_last` feature instances (configuration_last, etc.) could theoretically be reused, but the `CommandState` approach is superior because:
- Supports multiple undo levels (not just one)
- Captures all features in one atomic snapshot
- Includes command metadata for script generation
- Cleaner separation of concerns
- Easier to extend (redo, script replay)

### Why Keep `undo_stack_source`?

We preserve the parallel `undo_stack_source` list even though `CommandState` already contains the command name because:
- Minimal memory overhead
- Backward compatibility with existing code
- Quick command name lookup without dereferencing objects
- Useful for debugging and logging

## Testing Strategy

### Unit Tests (Future)

```python
def test_command_state_capture_configuration():
    """Test capturing configuration state."""
    # Create mock director with test data
    # Capture state
    # Verify all fields copied correctly

def test_command_state_restore_configuration():
    """Test restoring configuration state."""
    # Create mock director with modified data
    # Restore from snapshot
    # Verify data matches original state
```

### Integration Tests (Step 5)

- Test with actual Rotate command
- Verify undo restores exact previous state
- Test multiple undo levels
- Test undo after failed command
- Test undo with empty features

## Summary

The state capture system design is complete and ready for implementation in Step 5. The `CommandState` class provides a robust foundation for:

- Capturing all necessary application state
- Restoring state atomically
- Supporting future features (redo, scripts)
- Integrating cleanly with existing code

The design preserves existing infrastructure where possible while adding the minimal new components needed for full undo support.
