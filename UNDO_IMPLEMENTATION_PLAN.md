# Undo Feature Implementation Plan for Spaces

## Background

Spaces originally had a working undo feature before the GUI frontend was added. The old approach used:
- `deep.copy` for state preservation
- Arrays: `commands`, `undo_stack`, `undo_stack_source`
- Instances named `*_last`
- An Undo command

This approach no longer works with the PySide6 GUI because Qt objects cannot be effectively deep copied.

## Command Classification

Commands are classified into two immutable types based on whether they modify application state:

**Active Commands:** Modify application state and require state snapshots for undo
- Data transformations (Center, Rotate, Rescale, Invert)
- Model operations (MDS, Factor analysis, Principal components, Varimax)
- Data loading/creation (Configuration, Create, Open*, Similarities)
- Analysis operations (Correlations, Evaluations, Grouped, Individuals)
- Sampling operations (Sample designer, Sample repetitions)
- Settings commands (Settings - display sizing, Settings - layout options, Settings - plane, Settings - plot settings, Settings - presentation layer, Settings - segment sizing, Settings - vector sizing)

**Passive Commands:** Query or display existing state without modification
- Reports/queries (Directions, Distances, History, Print*)
- View operations (About, Help, Alike, Paired, Joint)
- Output displays (Base, Battleground, Contest, Convertible, Core supporters)
- Verbosity toggles (Terse, Verbose)
- Display-only analysis (Scree)

**Implementation:**
- Command type is an **immutable property**, not runtime state
- Store in `command_dict` within `dictionaries.py` module
- Use `MappingProxyType` for immutability and O(1) lookup
- Never rebuild these structures per-command (wasteful)

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
           self.command_name = ""         # Command identifier
           self.command_type = ""         # "active" or "passive" (immutable property)
           self.command_params = {}       # Parameters for script generation
           self.state_snapshot = None     # Only populated for active commands
           # State snapshot components (for active commands):
           self.data_snapshot = None      # DataFrame.copy()
           self.config_snapshot = {}      # Dict of settings
           self.plot_params = {}          # Plot configuration
           self.model_state = {}          # Model parameters/results
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

6. **Command Dictionary Integration**
   - Leverage `command_dict` from `dictionaries.py` for command classification
   - Use metadata to determine state capture requirements per command
   - Access via: `from dictionaries import command_dict`
   - Example lookup: `command_dict["Rotate"]["type"]` → `"active"`
   - Example state capture: `command_dict["Rotate"]["state_capture"]` → `["data", "plot"]`

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

## Active vs Passive Command Handling

**All commands go on the command stack** for complete session recording, but are handled differently:

**Active Commands:**
- Capture full state snapshot before execution
- State restoration on undo
- Heavier memory footprint (state data)

**Passive Commands:**
- Record command name and parameters only
- No state snapshot needed
- Replay by re-execution with saved params (idempotent)
- Minimal memory footprint

**Rationale for recording both:**
1. **Complete session history** for script generation/replay
2. **User transparency** - full command sequence visible
3. **Debugging** - complete audit trail
4. **Minimal cost** - passive commands store name + params only

**Undo behavior:**
- Active: Restore state snapshot
- Passive: Skip (or optionally re-execute if needed for consistency)

## Implementation Steps

### Step 0: Repository Backup and Preparation
- Clone existing Spaces repository as `Spaces_Before_Undo` for rollback safety
- Continue all development work in the original `Spaces` repository
- This provides a clean comparison point without relying on git branches

### Step 1: Centralize Dictionaries (Codebase Compatibility Refactor)

**Purpose:** Modernize dictionary management to establish immutable metadata foundation before implementing undo.

**Create `dictionaries.py` module:**
- Create new `src/dictionaries.py` file
- Use `MappingProxyType` to enforce immutability
- Syntax: `command_dict = MappingProxyType({"key": "value", ...})` (no intermediate mutable copy)

**Migrate and rename existing dictionaries:**

From `director.py`:
- `explain_dict` (from `Status.create_explanations`) → `explain_dict`
- `tab_dict` (from `Status.set_focus_on_tab`) → `tab_dict`
- `widget_dict` (from `BuildWidgetDict.__init__`) → `widget_dict`
- `traffic_dict` (from `BuildTrafficDict.__init__`) → `menu_item_dict` (rename)
- `button_dict` (from `Status.create_tool_bar`) → `button_dict`
- Unnamed dictionaries from `create_*_menu` functions → named and centralized

From `dependencies.py`:
- `new_feature_dict` (from `DependencyChecking.detect_consistency...`) → `new_feature_dict`
- `existing_feature_dict` (from `DependencyChecking.detect_consistency...`) → `existing_feature_dict`

From `table_builder.py`:
- `display_tables_dict` (from `BasicTableWidget.__init__`) → `basic_table_dict` (rename)
- `square_tables_config` (from `SquareTableWidget.__init__`) → `square_table_dict` (rename)
- `statistics_config` (from `GeneralStatisticalTableWidget.__init__`) → `statistical_table_dict` (rename)
- `rivalry_config` (from `RivalryTableWidget.__init__`) → `rivalry_table_dict` (rename)

**Update references:**
- Add `from dictionaries import ...` to all affected files
- Replace all local dictionary references with module imports
- Ensure alphabetical ordering and consistency across dictionaries

**Test and commit:**
- Run application and verify all functionality works
- Test all menus, table displays, and command execution
- Run consistency checker to validate dictionary integrity
- Commit: "Refactor: Centralize dictionaries in dictionaries.py with immutability enforcement"

**Benefits:**
- Clean separation of immutable metadata from mutable state
- Establishes patterns that align with undo architecture
- Significantly improves codebase organization before adding undo complexity
- Makes debugging undo issues easier (clear distinction between config and state)

### Step 2: Examine Existing Infrastructure
- Review current `undo_stack`, `undo_stack_source`, `commands` arrays
- Identify `*_last` instances and their purpose
- Review existing Undo command implementation
- Determine what can be preserved vs. needs refactoring

### Step 3: Create Command Dictionary

**Add to `dictionaries.py`:**
- Define `command_dict` (using `MappingProxyType`) with command classification and metadata
- **Must contain ALL ~150 commands in alphabetical order**
- Commands not yet fully implemented will have minimal/placeholder entries
- Structure:
  ```python
  command_dict = MappingProxyType({
      "About": {
          "type": "passive"
      },
      "Alike": {
          "type": "passive"
      },
      # ... all commands in alphabetical order ...
      "Center": {
          "type": "active",
          "state_capture": ["data", "plot"]
      },
      # ... all commands ...
      "Rotate": {
          "type": "active",
          "state_capture": ["data", "plot"]  # First to implement fully
      },
      # ... all commands ...
      "Scree": {
          "type": "passive"
      },
      # ... remaining commands alphabetically
  })
  ```
- Provides single source of truth for command classification
- Indicates what state to capture for each active command
- Alphabetical ordering ensures easy lookup and maintenance

### Step 4: Design State Capture System
- Create `CommandState` class
- Implement core state capture methods in `director.py`
- Design stack management (push/pop/clear)
- Plan GUI refresh mechanism after restore

### Step 5: Prototype with Rotate Command
- Examine Rotate command implementation
- Identify exactly what state changes
- Add state capture before rotation using `command_dict` metadata
- Implement restore logic
- Test undo/redo cycle
- Refine approach based on results

### Step 6: Expand Incrementally
- Choose next command to implement
- Apply learned patterns
- Build library of reusable capture/restore methods
- Document any special cases

### Step 7: GUI Integration
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
- **Plain text line-based format** for easy editing and readability
- **Include metadata**: timestamp, Spaces version (as comments)
- **Command structure**: One command per line, parameters space-separated
- **Self-contained**: Scripts specify complete workflow including data loading
- **Validation**: Check script compatibility before execution

**Example Script Format:**
```
# Spaces Session Script
# Created: 2025-10-05 14:30:00
# Spaces Version: 1.0

Open Elections/2020_election.csv
Configuration Elections/2020_config.txt
Rotate degrees=45
Center
MDS dimensions=2
Scree
```

**Parser Design:**
- Split each line on whitespace
- First token = command name
- Remaining tokens = parameters (key=value pairs or positional)
- Lines starting with `#` are comments (metadata or user notes)
- Blank lines ignored

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

**For Step 0 (Repository Backup):**
"Let's begin implementing the undo feature by creating a backup clone of the Spaces repository as Spaces_Before_Undo."

**For Step 1 (Dictionary Centralization):**
"Let's implement Step 1 of the undo plan: Create dictionaries.py and migrate all dictionaries to use MappingProxyType for immutability."

**For Step 2+ (Undo Implementation):**
"Let's continue with the undo implementation starting at Step 2: examining the existing infrastructure and beginning work on the CommandState class."
