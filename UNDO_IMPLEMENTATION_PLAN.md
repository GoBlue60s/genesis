# Undo Feature Implementation Plan for Spaces

## Background

Spaces originally had a working undo feature before the GUI frontend was added. The old approach used:
- `deep.copy` for state preservation
- Arrays: `commands`, `undo_stack`, `undo_stack_source`
- Instances named `*_last`
- An Undo command

This approach no longer works with the PySide6 GUI because Qt objects cannot be effectively deep copied.

## Solution Strategy

Implement undo using the **Command Pattern** with **selective state snapshots** instead of deep copying entire objects.

### Core Principle: Separate Data from Presentation

**Store (serializable state):**
- pandas DataFrames
- numpy arrays
- Python dictionaries
- Primitive types (int, float, str, bool)
- Configuration parameters
- Plot parameters (positions, labels, colors)

**Don't Store (GUI objects):**
- QWidgets
- matplotlib figures
- pyqtgraph objects

**On Undo:** Restore data state, then trigger existing GUI refresh methods in `director`

## Implementation Approach

### Phase 1: Build Core Framework (One-Time)

Create general undo infrastructure:

1. **State Snapshot Class**
   ```python
   class CommandState:
       """Lightweight state snapshot with scriptability support"""
       def __init__(self):
           self.data_snapshot = None      # DataFrame.copy()
           self.config_snapshot = {}      # Dict of settings
           self.plot_params = {}          # Plot configuration
           self.command_name = ""         # For display/debugging
           self.command_params = {}       # Parameters for script generation
   ```

2. **Undo Stack Management**
   - Reuse existing `undo_stack` array if possible
   - Add methods: `push_undo_state()`, `pop_undo_state()`
   - Track current position for redo capability

3. **State Capture Methods** (reusable across commands)
   - `save_data_state()` - captures `common.data`
   - `save_model_state()` - captures model parameters + results
   - `save_plot_state()` - captures plot configuration
   - `save_config_state()` - captures relevant settings

4. **State Restore Methods**
   - `restore_data_state()`
   - `restore_model_state()`
   - `restore_plot_state()`
   - `restore_config_state()`

5. **Undo Command Implementation**
   - Update existing Undo command to work with new framework
   - Add GUI integration (menu item, toolbar button, Ctrl+Z)

### Phase 2: Implement Command-Specific Undo (Incremental)

Add undo support one command at a time:

1. **Start with Rotate Command** (first prototype)
   - Examine what state Rotate modifies
   - Implement state capture before rotation
   - Implement state restore
   - Test thoroughly

2. **Expand to Other Commands Gradually**
   - Choose simple commands first (single state changes)
   - Build to complex commands (multi-step operations)
   - Not all commands need undo (see below)

### Command-Specific vs General Implementation

**General Framework** (implemented once):
- Undo stack management
- State snapshot mechanism
- Undo/redo execution logic
- GUI integration

**Command-Specific** (per command that needs undo):
- **What** state to capture (varies by command)
- **When** to capture (before execution)
- **How** to restore (usually standard, occasionally custom)

**Common Patterns** (reusable):
- Data transformations → `save_data_state()`
- Model operations → `save_model_state()`
- Configuration changes → `save_config_state()`
- Plot modifications → `save_plot_state()`

Most commands will use one or more of these standard patterns.

## Commands That Don't Need Undo

**Operations that use current state only** don't modify state and don't need undo:

- **View operations**: Zoom, pan, change tab focus
- **Display toggles**: Show/hide labels, change colors/themes
- **Queries**: Display statistics, show help, export data
- **Reports**: Generate tables, print output

These show or rearrange existing data without changing underlying data or model state.

## Implementation Steps

### Step 1: Examine Existing Infrastructure
- Review current `undo_stack`, `undo_stack_source`, `commands` arrays
- Identify `*_last` instances and their purpose
- Review existing Undo command implementation
- Determine what can be preserved vs. needs refactoring

### Step 2: Design State Capture System
- Create `CommandState` class
- Implement core state capture methods in `director.py`
- Design stack management (push/pop/clear)
- Plan GUI refresh mechanism after restore

### Step 3: Prototype with Rotate Command
- Examine Rotate command implementation
- Identify exactly what state changes
- Add state capture before rotation
- Implement restore logic
- Test undo/redo cycle
- Refine approach based on results

### Step 4: Expand Incrementally
- Choose next command to implement
- Apply learned patterns
- Build library of reusable capture/restore methods
- Document any special cases

### Step 5: GUI Integration
- Update Undo menu item
- Add toolbar button
- Implement keyboard shortcut (Ctrl+Z)
- Add Redo support (Ctrl+Y)
- Update status/feedback to user

## Strategic Design Considerations

### Cross-Command State Integrity

**Challenge:** Commands may modify shared state (e.g., `configuration_active.point_coords`). How do we ensure undo works correctly when multiple commands affect the same objects?

**Solution:** Sequential snapshot approach handles this automatically:

1. **Complete State Snapshots**: Each command captures the entire relevant state before execution, not just deltas
2. **Sequential Restoration**: Undo restores the complete snapshot from before the command executed
3. **No Dependency Tracking Needed**: Unlike the old instance-based approach, we don't track relationships between objects

**Example Flow:**
```
Initial state: point_coords = [original positions]
↓
Command A (Rotate): Saves snapshot → modifies point_coords
↓
Command B (Center): Saves snapshot → modifies point_coords again
↓
Undo B: Restores point_coords to post-Rotate state
↓
Undo A: Restores point_coords to original state
```

This is **superior to the feature/instance approach** because:
- No complex object relationship tracking
- Each command is self-contained
- Cross-command effects are automatically handled
- Simpler mental model and implementation

### Script Generation Capability

**Opportunity:** The command-based architecture enables restoring Spaces' original scripting capability.

**Implementation Strategy:**

1. **Leverage Existing Infrastructure**:
   - `commands_used` list (director.py:1800) already tracks command execution
   - `CommandState.command_params` can capture parameters for each command
   - Sequential command history provides execution order

2. **Command Serialization**:
   ```python
   # Each command implements:
   def serialize_params(self) -> dict:
       """Return parameters needed to replay this command"""
       return self.command_params
   ```

3. **Script Export**:
   ```python
   def export_script(self, filepath: str) -> None:
       """Write command history as executable script"""
       # For each CommandState in undo_stack:
       #   - Write command name
       #   - Write serialized parameters
       #   - Maintain execution order
   ```

4. **Script Replay**:
   ```python
   def execute_script(self, filepath: str) -> None:
       """Execute commands from script file"""
       # Read script
       # For each command:
       #   - Instantiate command with saved parameters
       #   - Execute command
   ```

**Benefits:**
- Batch processing of datasets
- Reproducible analyses
- Automation of repetitive tasks
- Command history becomes reusable workflow
- Testing and validation scenarios

**Integration with Undo:**
- Same `CommandState` class serves both undo and scripting
- Parameter capture happens once during command execution
- Minimal additional overhead per command
- Commands become both undoable and scriptable

### GUI Integration for Scripting

**Menu Items** (likely in File menu):
- **Open Script...** - Load and execute a previously saved script
- **Save Session...** - Export current command history as executable script
- **Recent Scripts** - Quick access to recently used scripts (optional)

**Command Classes** (in `filemenu.py`):
- **`OpenScriptCommand`** - Handles script file loading and execution
- **`SaveSessionCommand`** - Exports command history with parameters

**File Format Considerations:**
- **Human-readable format** (JSON or YAML) for easy editing/debugging
- **Include metadata**: timestamp, Spaces version, data files used
- **Command structure**: name, parameters, execution order
- **Validation**: Check script compatibility before execution

**Example Script Format:**
```json
{
  "metadata": {
    "created": "2025-10-05T14:30:00",
    "spaces_version": "1.0",
    "data_file": "Elections/2020_election.csv"
  },
  "commands": [
    {
      "name": "Configuration",
      "params": {"file": "config.txt"}
    },
    {
      "name": "Rotate",
      "params": {"degrees": 45}
    },
    {
      "name": "Center",
      "params": {}
    }
  ]
}
```

**User Experience:**
- **Save Session**: Captures all commands since file opened (or session start)
- **Open Script**: Prompts for confirmation, shows command preview before execution
- **Error Handling**: Clear messages if script incompatible with current data
- **Progress Feedback**: Show which command is executing during script replay

### Implementation Priority

**Phase 1 (Undo):** Focus on state snapshots and restoration
- Implement `CommandState` class with `command_params`
- Build undo/redo functionality
- Test with Rotate and other commands

**Phase 2 (Script Export):** Add serialization and export once undo is stable
- Implement `serialize_params()` for each command
- Create `SaveSessionCommand` class
- Design and implement script file format
- Add "Save Session..." menu item

**Phase 3 (Script Replay):** Implement script execution after export is working
- Create `OpenScriptCommand` class
- Implement script parser and validator
- Add "Open Script..." menu item
- Build execution engine with progress feedback
- Handle errors gracefully during script execution

**Phase 4 (Enhancements - Optional):**
- Recent Scripts menu
- Script editing capabilities
- Script templates for common workflows
- Batch script execution for multiple datasets

This staged approach allows us to:
1. Validate the command pattern with undo
2. Ensure parameter capture is complete and accurate
3. Build scripting on proven foundation
4. Add GUI integration incrementally

## Notes

- This approach preserves the original design intent (undo capability)
- Compatible with PySide6 GUI architecture
- Incremental implementation reduces risk
- Can be tested command-by-command
- Follows existing Spaces patterns (exceptions, dependencies, director)
- Extends naturally to support scripting capability
- Sequential snapshots solve cross-command state change concerns

## Next Session Prompt

"Please review UNDO_IMPLEMENTATION_PLAN.md and let's implement the undo feature starting with the Rotate command as discussed."
