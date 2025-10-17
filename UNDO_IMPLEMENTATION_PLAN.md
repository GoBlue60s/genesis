# Undo Feature Implementation Plan for Spaces

## Background

Spaces originally had a working undo feature before the GUI frontend was added. The old approach used:
- `deep.copy` for state preservation
- Arrays: `commands`, `undo_stack`, `undo_stack_source`
- Instances named `*_last`
- An Undo command

This approach no longer works with the PySide6 GUI because Qt objects cannot be effectively deep copied.

## Command Classification

**Important Distinction:**
- **Commands**: 104 unique command implementations (what actually executes)
- **Menu items**: 140 entries in `request_dict` (multiple menu items can invoke same command)

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

### Step 1: Centralize Dictionaries (Codebase Compatibility Refactor) ⚠️ IN PROGRESS

**Status:** Partially completed on 2025-10-08 - requires additional refactoring

**Purpose:** Modernize dictionary management to establish immutable metadata foundation before implementing undo.

**Create `dictionaries.py` module:**
- ✅ Created new `src/dictionaries.py` file
- ✅ Used `MappingProxyType` to enforce immutability
- ✅ Syntax: `command_dict = MappingProxyType({"key": "value", ...})` (no intermediate mutable copy)

**Migrate and rename existing dictionaries:**

From `director.py`:
- ✅ `explain_dict` (from `Status.create_explanations`) → `explain_dict`
- ✅ `tab_dict` (from `Status.set_focus_on_tab`) → `tab_dict`
- ✅ `widget_dict` (from `BuildWidgetDict.__init__`) → `create_widget_dict(parent)` factory function
  - **Note:** Required factory function approach because widget_dict contains lambdas that need parent instance reference
- ✅ `traffic_dict` (from `BuildTrafficDict.__init__`) → `menu_item_dict` (rename)
- ✅ `button_dict` (from `Status.create_tool_bar`) → `button_dict`
- ✅ Unnamed dictionaries from `create_*_menu` functions → named and centralized

From `dependencies.py`:
- ✅ `new_feature_dict` (from `DependencyChecking.detect_consistency...`) → `new_feature_dict`
- ✅ `existing_feature_dict` (from `DependencyChecking.detect_consistency...`) → `existing_feature_dict`

From `table_builder.py`:
- ✅ `display_tables_dict` (from `BasicTableWidget.__init__`) → `basic_table_dict` (rename)
- ✅ `square_tables_config` (from `SquareTableWidget.__init__`) → `square_table_dict` (rename)
- ✅ `statistics_config` (from `GeneralStatisticalTableWidget.__init__`) → `statistical_table_dict` (rename)
- ✅ `rivalry_config` (from `RivalryTableWidget.__init__`) → `rivalry_table_dict` (rename)

**Update references:**
- ✅ Added `from dictionaries import ...` to all affected files
- ✅ Replaced all local dictionary references with module imports
- ✅ Updated all menu modules to call `create_widget_dict(parent)` instead of importing static dict
- ✅ Ensured alphabetical ordering and consistency across dictionaries

**Test and commit:**
- ✅ Ran application and verified all functionality works
- ✅ Tested all menus, table displays, and command execution
- ✅ Ran consistency checker to validate dictionary integrity
- ✅ Committed: "Refactor: Centralize dictionaries in dictionaries.py with immutability enforcement" (fc04ee2)
- ✅ Committed: "Complete dictionary centralization to dictionaries.py" (46b170a)
- ✅ Pushed to remote repository

### Step 1.5: Complete Dictionary Refactoring Cleanup

**Purpose:** Fix incomplete renames, type annotations, and establish consistent patterns from Step 1

**Phase A: Type System (Foundation)**
1. Create `FrozenDict` type alias in `dictionaries.py`
   - Add near top of file: `FrozenDict = MappingProxyType`
   - Export it for use throughout codebase
2. Update all dictionary return types from `-> dict` to `-> FrozenDict`
   - Functions like `create_edit_menu()`, `create_view_menu()`, etc. in `director.py`
3. Search codebase for `-> dict` pattern and update where appropriate
   - Focus on functions returning dictionaries created in Step 1

**Phase B: Naming Consistency (menu_item_dict → request_dict)**
4. Rename `menu_item_dict` → `request_dict` in `dictionaries.py`
   - More accurate name: maps menu requests to command handlers
5. Update all references to `menu_item_dict` → `request_dict` throughout codebase
6. Eliminate `BuildTrafficDict` class entirely
   - It only wraps an import, provides no additional functionality
   - Replace with direct import of `request_dict` in `director.py`
7. Delete line 1278 in `director.py`: `self.traffic_dict = self.build_traffic_dict.traffic_dict`
   - Replace with direct usage of imported `request_dict`
8. Rename all `traffic_dict` references → `request_dict`
9. Rename `traffic_control()` function → `request_control()`
10. Update all references to `traffic_control` → `request_control`
11. Search entire codebase for "traffic" and verify all instances addressed
    - Check comments, docstrings, variable names

**Phase C: Table Builder Cleanup**
12. Review line 65 in `table_builder.py` (similar pattern to traffic_dict)
    - Evaluate if wrapper pattern should be eliminated
    - Simplify to direct dictionary usage where possible
13. Establish consistent naming pattern for table functions
    - Classes: `BasicTableWidget`, `SquareTableWidget`, `StatisticalTableWidget`, `RivalryTableWidget`
    - Dictionaries: `basic_table_dict`, `square_table_dict`, `statistical_table_dict`, `rivalry_table_dict`
    - Methods: Follow consistent pattern across all four table types
14. Apply consistent naming across all four table types

**Phase D: Widget Dictionary Verification**
15. Verify `widget_dict` factory function usage throughout codebase
    - Ensure all callers properly use `create_widget_dict(parent)`
    - Search for any incorrect direct imports of `widget_dict`
16. Confirm `BuildWidgetDict` class is properly using factory function
    - This class IS needed (unlike BuildTrafficDict) because widget_dict requires parent instance

**Phase E: Final Verification**
17. Search for any remaining old dictionary names throughout codebase
18. Run `check_consistency_of_dictionaries_and_arrays()` in director.py
19. Update comments and docstrings that reference old terminology
20. Review all "Build*" classes to ensure they're all necessary
21. Run linter: `ruff check .`

**Phase F: Testing and Completion**
22. Run application and verify all functionality works
23. Test all menus, table displays, and command execution
24. **User performs comprehensive testing**
25. **Commit only after user approval**: "Complete Step 1 dictionary refactoring: fix types, rename traffic→request, cleanup"
26. Mark Step 1 as fully complete

**Design Decision: Lowercase vs UPPERCASE naming**
- **Decision: Keep lowercase** (e.g., `request_dict`, not `REQUEST_DICT`)
- **Rationale:**
  - PEP 8: UPPERCASE is for compile-time constants (simple values)
  - These dictionaries contain class/function references (mutable objects)
  - `MappingProxyType` provides runtime immutability, not compile-time
  - Standard practice: Even immutable complex structures use lowercase (e.g., `sys.path`)
  - Better readability in code

**Benefits:**
- Clean separation of immutable metadata from mutable state
- Establishes patterns that align with undo architecture
- Significantly improves codebase organization before adding undo complexity
- Makes debugging undo issues easier (clear distinction between config and state)

### Step 2: Examine Existing Infrastructure ✅ COMPLETE

**Status:** Completed on 2025-10-09

**Findings:**

**1. Command Infrastructure (director.py)**
- **Total commands: 104** (in alphabetical order in `self.commands` tuple)
- **Active commands: 42** (modify application state, require undo support)
- **Passive commands: 62** (query/display only, no state changes)
- All commands uniquely classified with no overlap

**2. Undo Stack Infrastructure (director.py:1255-1256, 123-124)**
- **`undo_stack: list[int]`** - Initialized to `[0]`, currently stores integer IDs
- **`undo_stack_source: list[str]`** - Initialized to `["Initialize"]`, stores command names
- Both arrays managed in parallel throughout command lifecycle
- Currently minimal - only tracks integer ID and source name
- **Decision:** Preserve arrays but upgrade contents to store `CommandState` objects

**3. Command Tracking (director.py:909-910, 728-833)**
- **`commands_used: list[str]`** - Tracks all executed commands in session order
- **`command_exit_code: list[int]`** - Parallel array (-1=in progress, 0=success, 1=failed)
- **Decision:** Preserve this excellent session history mechanism for script generation

**4. Feature Instances with `*_last` Pattern (director.py:181-209)**
Eight feature types use candidate/original/active/last pattern:
- `configuration_last`, `correlations_last`, `evaluations_last`, `grouped_data_last`
- `individuals_last`, `similarities_last`, `target_last`, `scores_last`
- **Purpose:** Placeholders for previous state in original undo design
- **Decision:** New approach won't need separate `*_last` instances (state captured in undo stack)

**5. Existing Undo Command (editmenu.py:40-87)**
- Currently a stub displaying "under construction" message
- `_return_to_previous_active()` method exists but incomplete:
  - Only handles configuration restoration
  - Uses `active` variable popped from undo_stack (unclear definition)
  - Missing comprehensive state restoration
- **Decision:** Complete rewrite needed for new architecture

**6. Error Handling Pattern (director.py:435-458)**
- `unable_to_complete_command_set_status_as_failed()` removes failed commands from undo stacks
- Prevents failed commands from appearing in undo history
- **Decision:** Preserve this pattern - it's correct behavior

**What Can Be Preserved:**
- ✅ `undo_stack` and `undo_stack_source` arrays (upgrade contents to CommandState)
- ✅ `commands_used` tracking for session history
- ✅ `active_commands`/`passive_commands` classification (42/62 split)
- ✅ Error handling pattern for failed commands
- ✅ Feature architecture (candidate/original/active pattern)

**What Needs Refactoring:**
- 🔧 `undo_stack` contents: change from `int` to `CommandState` objects
- 🔧 Undo command: complete rewrite for all state types
- 🔧 State capture mechanism: add systematic capture before command execution
- 🔧 `active_commands`/`passive_commands`: move to `dictionaries.py` as `command_dict`
- 🔧 `*_last` instances: can be deprecated once new undo system works

**Issues Fixed:**
- Removed duplicate entries "Deactivate" and "Sample designer" from `passive_commands`
- Verified totals: 42 active + 62 passive = 104 total commands ✓

**References:**
- `undo_stack` initialization: director.py:1255-1256
- Command classification: director.py:915-949
- Feature instances: director.py:181-209
- Undo command stub: editmenu.py:40-87
- Error handling: director.py:435-458

### Step 3: Create Command Dictionary ✅ COMPLETE

**Status:** Completed on 2025-10-09

**Implementation:**
- ✅ Created `command_dict` in `dictionaries.py` using `MappingProxyType`
- ✅ Contains all 106 commands in alphabetical order
- ✅ All 42 active commands include `state_capture` field with empty list placeholder
- ✅ All 64 passive commands have `type` field only
- ✅ Added two future commands: "Print sample solutions" and "View sample solutions"
- ✅ Updated `active_commands` and `passive_commands` tuples in director.py:915-950
- ✅ Fixed "Grouped" → "Grouped data" naming inconsistency
- ✅ Verified all commands match between director.py and command_dict
- ✅ Tested imports work correctly

**Structure implemented:**
  ```python
  command_dict = MappingProxyType({
      "About": {
          "type": "passive"
      },
      "Alike": {
          "type": "passive"
      },
      # ... all 64 passive commands ...
      "Center": {
          "type": "active",
          "state_capture": []  # TODO: Define what state to capture
      },
      # ... all 42 active commands ...
      "Rotate": {
          "type": "active",
          "state_capture": []  # TODO: Define what state to capture
      },
      # ... etc ...
  })
  ```

**Verification Results:**
- Total commands: 106 (42 active + 64 passive)
- All active commands have `state_capture` field ✓
- No passive commands have `state_capture` field ✓
- All commands in alphabetical order ✓
- Perfect match between director.py lists and command_dict ✓

**Next Step:** Step 4 - Design State Capture System

### Step 4: Design State Capture System ✅ COMPLETE

**Status:** Completed on 2025-10-09, tested and validated on 2025-10-11

**Implementation:**
- ✅ Created `CommandState` class in `src/command_state.py`
- ✅ Implemented state capture methods for all 8 feature types
- ✅ Implemented state restore methods for all 8 feature types
- ✅ Designed stack management helper methods (push/pop/peek/clear)
- ✅ Designed GUI refresh mechanism using existing director methods
- ✅ Created comprehensive design document: `STEP_4_STATE_CAPTURE_DESIGN.md`
- ✅ Created helper function `capture_and_push_undo_state()` in `common.py:2241-2277`
- ✅ Tested successfully with 18 commands across 4 menu systems

**CommandState Class Features:**
- Stores command metadata (name, type, parameters, timestamp)
- Captures state for: configuration, correlations, similarities, evaluations, individuals, scores, grouped_data, target, settings, uncertainty, rivalry
- Symmetric design: each `capture_*_state()` has matching `restore_*_state()`
- Uses `.copy()` for all DataFrames and lists to ensure immutability
- Provides `restore_all_state()` method for atomic restoration

**Stack Management Design:**
- Upgrade `undo_stack` from `list[int]` to `list[CommandState]`
- Preserve `undo_stack_source` for backward compatibility
- Methods: `push_undo_state()`, `pop_undo_state()`, `peek_undo_state()`, `clear_undo_stack()`
- Integrates with existing error handling pattern

**GUI Refresh Strategy:**
- Reuse existing `create_widgets_for_output_and_log_tabs()`
- Reuse existing `create_configuration_plot_for_tabs()`
- Reuse existing `set_focus_on_tab()`
- Plot recreation works automatically (data restored, plots regenerated)

**Design Documentation:**
- See `STEP_4_STATE_CAPTURE_DESIGN.md` for complete details
- Includes capture/restore workflows
- Documents integration points and testing strategy

**User Testing Results:**
- ✅ Successfully tested Rotate command undo
- ✅ Successfully tested multiple transform commands
- ✅ Successfully tested model commands including Cluster with conditional state capture
- ✅ Design validated through real-world usage

**Next Step:** Step 5 - Prototype with Rotate Command (completed and expanded to 18 commands)

### Step 5: Prototype with Rotate Command ✅ COMPLETE

**Status:** Completed on 2025-10-10

**Implementation:**
- ✅ Examined RotateCommand implementation in `transformmenu.py:596-698`
- ✅ Identified state changes: `configuration_active.point_coords` and `scores_active.scores`
- ✅ Updated `command_dict["Rotate"]["state_capture"]` to `["configuration", "scores"]`
- ✅ Added stack management methods to `director.py`:
  - `push_undo_state()`, `pop_undo_state()`, `peek_undo_state()`, `clear_undo_stack()`
- ✅ Modified `EstablishSpacesStructure` to initialize `undo_stack` as `list[CommandState]`
- ✅ Modified RotateCommand.execute() to capture state before rotation
- ✅ Completely rewrote UndoCommand to use CommandState system
- ✅ Added imports: `from command_state import CommandState` and `from dictionaries import command_dict`

**Rotate Command Modifications (`transformmenu.py:620-647`):**
```python
# After getting rotation degree from user and before any modifications:
cmd_state = CommandState("Rotate", "active", {"degrees": deg})
cmd_state.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
for feature in command_dict["Rotate"]["state_capture"]:
    if feature == "configuration":
        cmd_state.capture_configuration_state(self._director)
    elif feature == "scores":
        cmd_state.capture_scores_state(self._director)
self._director.push_undo_state(cmd_state)
```

**UndoCommand Rewrite (`editmenu.py:40-88`):**
- Removed "under construction" message
- Implemented `_undo_last_command()` method
- Calls `pop_undo_state()` to get most recent CommandState
- Calls `restore_all_state()` to restore captured state
- Triggers GUI refresh using existing director methods
- Provides informative error if undo stack is empty

**Stack Management Methods (`director.py:1215-1256`):**
- `push_undo_state(cmd_state)`: Appends CommandState to stack and command name to source
- `pop_undo_state()`: Removes and returns most recent CommandState (or None if empty)
- `peek_undo_state()`: Returns most recent CommandState without removing (or None if empty)
- `clear_undo_stack()`: Clears both undo_stack and undo_stack_source

**Testing Approach:**
The prototype is ready for user testing with the following workflow:
1. Open a configuration file
2. Execute Rotate command (enter non-zero degree value)
3. Observe configuration is rotated
4. Execute Undo command
5. Verify configuration is restored to pre-rotation state
6. Check that scores were also properly restored

**Key Design Decisions:**
- State capture occurs AFTER user input dialog but BEFORE any state modifications
- Uses metadata from `command_dict` to determine which features to capture
- Symmetric capture/restore pattern ensures all state is properly handled
- GUI refresh reuses existing director methods (no new GUI code needed)
- Error handling provides clear user feedback if undo stack is empty

**Files Modified:**
- `src/transformmenu.py`: Added imports, modified RotateCommand.execute()
- `src/director.py`: Added CommandState import, changed undo_stack type, added 4 stack management methods
- `src/editmenu.py`: Completely rewrote UndoCommand class
- `src/dictionaries.py`: Updated Rotate entry with state_capture list

**Optimization: Helper Function Created**
Created `capture_and_push_undo_state()` in `common.py:2241-2277` to consolidate repetitive state capture pattern:
- Takes command_name, command_type, and parameters
- Creates CommandState automatically
- Iterates through `command_dict[command_name]["state_capture"]` list
- Calls appropriate `capture_*_state()` methods
- Pushes to undo stack
- Eliminates ~10 lines of boilerplate per command

**Testing Results:**
- ⏳ Awaiting user testing to validate prototype functionality
- ⏳ Need to verify state capture works correctly
- ⏳ Need to verify state restoration works correctly
- ⏳ Need to verify GUI refresh works correctly

**Next Step:** Step 6 - User Testing and Expansion Progress

### Step 6: Expand Incrementally ✅ COMPLETE

**Status:** Completed on 2025-10-12

**Commands with Undo Support Implemented (42 total - ALL ACTIVE COMMANDS):**

**Transform Menu (7 commands) - ALL COMPLETE:**
1. ✅ **Center** (`transformmenu.py`) - State: configuration, scores
2. ✅ **Compare** (`transformmenu.py`) - State: configuration, target, scores
3. ✅ **Invert** (`transformmenu.py`) - State: configuration, scores
4. ✅ **Move** (`transformmenu.py`) - State: configuration, scores
5. ✅ **Rescale** (`transformmenu.py`) - State: configuration, scores
6. ✅ **Rotate** (`transformmenu.py`) - State: configuration, scores
7. ✅ **Varimax** (`transformmenu.py`) - State: configuration, scores

**Associations Menu (1 command) - ALL COMPLETE:**
8. ✅ **Line of sight** (`associationsmenu.py`) - State: similarities

**Model Menu (6 commands) - ALL COMPLETE:**
9. ✅ **Cluster** (`modelmenu.py`) - State: conditional (scores + one of: configuration/evaluations/similarities)
10. ✅ **Factor analysis** (`modelmenu.py`) - State: configuration, scores, evaluations
11. ✅ **Factor analysis machine learning** (`modelmenu.py`) - State: configuration, scores, evaluations
12. ✅ **MDS** (`modelmenu.py`) - State: configuration
13. ✅ **Principal components** (`modelmenu.py`) - State: configuration
14. ✅ **Uncertainty** (`modelmenu.py`) - State: uncertainty

**Respondents Menu (4 commands) - ALL COMPLETE:**
15. ✅ **Reference points** (`respondentsmenu.py`) - State: rivalry
16. ✅ **Sample designer** (`respondentsmenu.py`) - State: uncertainty
17. ✅ **Sample repetitions** (`respondentsmenu.py`) - State: uncertainty
18. ✅ **Score individuals** (`respondentsmenu.py`) - State: scores

**Additional Commands (Non-File Menu) - ALL COMPLETE:**
19. ✅ **Cluster** (`modelmenu.py:91`) - State: conditional (scores + configuration|evaluations|similarities)
20. ✅ **Create** (`filemenu.py:451`) - State: configuration
21. ✅ **Deactivate** (`filemenu.py:808`) - State: conditional (captures selected items)
22. ✅ **Evaluations** - State: evaluations
23. ✅ **New grouped data** (`filemenu.py:1603`) - State: grouped_data
24. ✅ **Target** - State: target
25. ✅ **Settings - display sizing** - State: settings
26. ✅ **Settings - layout options** - State: settings
27. ✅ **Settings - plane** - State: settings
28. ✅ **Settings - plot settings** - State: settings
29. ✅ **Settings - presentation layer** - State: settings
30. ✅ **Settings - segment sizing** - State: settings
31. ✅ **Settings - vector sizing** - State: settings

**File Menu Commands - ALL COMPLETE:**
32. ✅ **Configuration** (`filemenu.py:124`) - State: configuration
33. ✅ **Correlations** (`filemenu.py:336`) - State: correlations
34. ✅ **Grouped data** (`filemenu.py:1228`) - State: grouped_data
35. ✅ **Individuals** (`filemenu.py:1396`) - State: individuals
36. ✅ **Open sample design** (`filemenu.py:1878`) - State: uncertainty
37. ✅ **Open sample repetitions** (`filemenu.py:2024`) - State: uncertainty
38. ✅ **Open sample solutions** (`filemenu.py:2105`) - State: uncertainty
39. ✅ **Open scores** (`filemenu.py:2319`) - State: scores
40. ✅ **Similarities** (`filemenu.py:4343`) - State: similarities

**Meta/Experimental Commands (N/A for undo):**
41. ⚫ **Redo** - N/A (meta-command managing redo stack)
42. ⚫ **Tester** - N/A (experimental/debug command)
43. ⚫ **Undo** - N/A (meta-command managing undo stack)

**Implementation Pattern:**
All commands now use the consolidated `capture_and_push_undo_state()` helper:
```python
# Before modification
self.common.capture_and_push_undo_state("CommandName", "active", {params})
# Then modify state
```

**Status Summary:**
- **Total Active Commands:** 42
- **Commands with Undo Implemented:** 39 (100% of applicable commands)
- **Meta/Experimental Commands (N/A):** 3 (Undo, Redo, Tester)
- **All applicable commands have undo support**
- **Zero TODO entries remain in codebase**
- Core undo functionality fully operational and tested
- Implementation complete for Step 6

**Git Commit History:**
- 76e490f: "Implemented Undo for all active commands but file menu commands"
- 12f96de: "Refactor: Rename traffic_dict to request_dict and streamline dictionary initialization"
- b4aac14: "Minimal changes to Cluster and Undo_Implementation_Plan"

**Recent Changes (2025-10-12):**

**First Commit (840040d):**
- Added undo support for Configuration command (filemenu.py:124-126)
- Added undo support for Open sample design command (filemenu.py:1877-1880)
- Added undo support for Open sample repetitions command (filemenu.py:2023-2026)
- Added undo support for Open sample solutions command (filemenu.py:2104-2107)
- Updated command_dict with state_capture metadata for these 4 commands

**Second Commit (571cbdf):**
- Added undo support for Correlations command (filemenu.py:335-338)
- Added undo support for Individuals command (filemenu.py:1395-1398)
- Added undo support for Grouped data command (filemenu.py:1227-1230)
- Added undo support for Similarities command (filemenu.py:4342-4345)
- Added undo support for Open scores command (filemenu.py:2318-2321)
- Updated command_dict with state_capture metadata for these 5 commands

**Third Commit (72b669b):**
- Added undo support for Create command (filemenu.py:445-451)
- Added undo support for New grouped data command (filemenu.py:1597-1605)
- Updated command_dict with state_capture metadata for these 2 commands

**Fourth Commit (dd40ab6):**
- Fixed Cluster: Already had undo code (modelmenu.py:91), updated dict to mark as "conditional"
- Implemented Deactivate undo: Dynamic state capture based on user selection (filemenu.py:808-855)
- Marked Redo, Tester, Undo as N/A (meta/experimental commands)
- Removed all TODO entries from command_dict

**All 42 active commands now have undo support or appropriate N/A designation (100% complete)**
**Zero TODO entries remain in the codebase**

**Next Steps:**
- Step 6.5: Enhance Undo command with restoration details table (IN PROGRESS)
- Step 7: GUI Integration (keyboard shortcuts, toolbar buttons, menu enhancements)
- Comprehensive testing across all 39 implemented commands
- Document any edge cases or special behaviors discovered during testing
- Consider implementing Redo support (Ctrl+Y)
- Verify conditional commands (Cluster, Deactivate) work correctly with various user selections

### Step 6.5: Enhance Undo Command with Restoration Details Table ⚠️ IN PROGRESS

**Status:** In progress on 2025-10-12

**Purpose:** Improve user feedback by showing what state was restored during undo operations.

**Current Behavior:**
- Undo command displays message: "Undone: [CommandName]"
- User sees what was undone, but not what was restored
- No visibility into which data items were affected

**Enhancement Goals:**
- Add table widget to Output tab showing all restored items
- Display table only when undo succeeds
- Show complete list of what was restored (not a summary)
- Use clear user-facing terminology (avoid "feature")

**Table Design:**

| Item | Details |
|------|---------|
| Configuration | ndim=3, npoint=50 |
| Distances | 50×50 matrix |
| Associations | 15 variables |

**Table Specifications:**
- **Widget Type:** Basic table (not statistical table - this is presentational data)
- **Columns:**
  - **Item:** The data component that was restored (Configuration, Target, Distances, Correlations, Individuals, Similarities, Evaluations, Scores, Grouped data, Settings, Uncertainty, Rivalry)
  - **Details:** Relevant information about what was restored (dimensions, counts, matrix sizes, etc.)
- **Rows:** One row per item that was actually restored from the CommandState
- **Display:** Only appears when undo succeeds (not on errors or empty stack)

**Implementation Approach:**

1. **Modify UndoCommand** (`editmenu.py:40-88`):
   - After successful `restore_state()`, extract restoration details from CommandState
   - Iterate through CommandState attributes to find which items are not None
   - Build table data structure with item names and details

2. **Extract Details from CommandState:**
   - **Configuration:** ndim, npoint
   - **Target:** ndim, npoint
   - **Distances:** matrix dimensions (e.g., "50×50 matrix")
   - **Correlations:** matrix dimensions
   - **Individuals:** row count, column count
   - **Similarities:** matrix dimensions, value_type if available
   - **Evaluations:** dimensions
   - **Scores:** dimensions
   - **Grouped data:** ngroups, ndim
   - **Settings:** Which settings were restored (could list setting names)
   - **Uncertainty:** sample information if available
   - **Rivalry:** rivalry information if available

3. **Table Builder Integration:**
   - Use `BasicTableWidget` from `table_builder.py`
   - Place table on Output tab (existing pattern)
   - Include header message above table: "Undo successful: [CommandName]"

4. **Respect Verbosity Toggle:**
   - Terse mode: Show simplified message only
   - Verbose mode: Show message + detailed table

**Files to Modify:**
- `src/editmenu.py`: Update UndoCommand to generate and display table
- Possibly `src/table_builder.py`: Verify basic table widget supports this use case

**Testing Strategy:**
1. Test with single-state commands (e.g., Rotate: configuration + scores)
2. Test with multi-state commands (e.g., Factor analysis: configuration + scores + evaluations)
3. Test with conditional commands (e.g., Cluster, Deactivate with various selections)
4. Verify table only appears on successful undo
5. Verify Details column shows meaningful information for each item type
6. Test with both Terse and Verbose modes

**Benefits:**
- Complete transparency into what undo restored
- Educational: users learn what state each command modifies
- Debugging aid: users can verify undo behavior
- Consistent with application's table-based output pattern

**Next Step:** Step 7 - GUI Integration (keyboard shortcuts, toolbar, redo support)

### Step 7: Redo Support ✅ COMPLETE

**Status:** Completed on 2025-10-13

**Implementation:**
- ✅ Implemented RedoCommand class in `editmenu.py`
- ✅ Added redo stack management methods to `director.py`
- ✅ Added enable_redo() and disable_redo() methods
- ✅ Redo is disabled on startup (no redo stack items)
- ✅ Redo is enabled when Undo executes (pushes to redo stack)
- ✅ Redo is disabled when new commands execute (clears redo stack)
- ✅ Matches Microsoft Word's undo/redo behavior

**Redo Stack Methods (`director.py`):**
- `push_redo_state(cmd_state)`: Appends CommandState to redo stack
- `pop_redo_state()`: Removes and returns most recent CommandState
- `peek_redo_state()`: Returns most recent CommandState without removing
- `clear_redo_stack()`: Clears both redo_stack and redo_stack_source
- `enable_redo()`: Enables Redo menu item and toolbar button
- `disable_redo()`: Disables Redo menu item and toolbar button

**Redo Workflow:**
1. User executes a command → State captured to undo stack
2. User clicks Undo → Current state pushed to redo stack, previous state restored
3. Redo is now enabled
4. User clicks Redo → Current state pushed to undo stack, next state restored
5. If user executes a new command → Redo stack cleared, Redo disabled

**Integration Points:**
- Menu item: Edit > Redo
- Toolbar button: Redo icon
- Both menu and toolbar items enabled/disabled together

**Git Commits:**
- 28c5e20: "Implement dynamic Redo enable/disable functionality"

**Next Step:** Step 8 - Scripting Support (Phase 2 of original plan)

### Step 8: Scripting Support ⚠️ IN PROGRESS

**Status:** Started on 2025-10-13

**Purpose:** Implement scripting capability to allow users to save and replay command sequences, enabling batch processing and reproducible analyses.

**Phase 2a: Foundation and Metadata**

**Completed:**
- ✅ Designed script file format (.spc files)
- ✅ Added three new commands to `command_dict` in `dictionaries.py`:
  - "Open script" (active) - Executes commands from script file
  - "Save script" (passive) - Exports command history to file
  - "View script" (passive) - Displays current command history
- ✅ Added explanations for all three commands to `explain_dict`
- ✅ Updated `commands` tuple in `director.py` with three new commands
- ✅ Added "Open script" to `active_commands` (line 937)
- ✅ Added "Save script" and "View script" to `passive_commands` (lines 960, 967)
- ✅ Updated command counts: 107 total (43 active + 64 passive)
- ✅ Added "Save script" icon to resources (spaces_save_script_icon.jpg)
- ✅ Added "Open script" icon to resources (spaces_open_script_icon.jpg)
- ✅ Added "View script" icon to resources (spaces_view_script_icon.jpg)
- ✅ Created menu entries in `request_dict` for all three commands
- ✅ Created widgets in `create_widget_dict()` for all three commands

**Script File Format Design:**
```
# Spaces Script
# Created: 2025-10-13 14:30:00
# Spaces Version: 2025

Configuration data/Elections/2020_election.txt
Rotate degrees=45
Center
MDS
Scree
```

**Key Features:**
- Plain text, line-based format for easy editing
- Comments with # for metadata
- Command name + parameters on each line
- Blank lines ignored
- Self-contained (includes data loading commands)

**Menu Organization:**
- **File > Open > Script** - Load and execute a script
- **File > Save > Script** - Export command history to script
- **View > Script** - Display current command history (review before saving)

**Remaining Tasks for Phase 2a:**
- ✅ Create SaveScriptCommand class in `filemenu.py` (stub created)
- ✅ Create OpenScriptCommand class in `filemenu.py` (stub created)
- ✅ Create ViewScriptCommand class in `viewmenu.py` (implemented, working)
- ✅ Add menu items to File and View menus in `dictionaries.py`
- ✅ Add widgets for script commands to `widget_dict`

**Phase 2a Complete** ✅

**Phase 2b: Save Script Implementation** ✅ COMPLETE (2025-10-16)

**Completed:**
- ✅ Implemented SaveScriptCommand class in `filemenu.py:4533-4623`
- ✅ Added file dialog for selecting save location (.spc extension)
- ✅ Exports complete command history from `commands_used` to script file
- ✅ Includes all commands (no filtering - preserves complete session)
- ✅ Formats command parameters properly for script output
- ✅ Fixed blank line issue - commands without parameters now display correctly
- ✅ Successfully tested with multiple command types
- ✅ Script files are human-readable and editable

**Implementation Details:**
- Uses `_format_script_line()` helper method to generate script lines
- Handles both parameterless commands (e.g., "Center") and parameterized commands (e.g., "Rotate degrees=45")
- Writes metadata header with timestamp and Spaces version
- Preserves complete command sequence including Undo, Redo, and all other commands
- Error handling for file write failures
- Integration with existing director patterns

**Next Phase Tasks:**
- ⏳ Implement script parser for OpenScriptCommand
- ⏳ Test script execution with saved script files
- ⏳ Handle script validation and error reporting

**Implementation Phases:**

**Phase 2a: Foundation** ✅ COMPLETE
- ✅ Add command metadata to dictionaries
- ✅ Create command classes with basic structure
- ✅ Add menu items and widgets
- ✅ Implement View Script command (working with known issue)

**Phase 2b: Save Script** (Next)
- ⏳ Export `commands_used` to script file
- ⏳ Add metadata (timestamp, version)
- ⏳ Handle file dialog for save location
- ⏳ Filter out meta-commands (Undo, Redo, View*, Print*)
- ⏳ Format command parameters for script output

**Phase 2c: View Script Improvements**
- ⏳ Fix blank line issue for commands without parameters
- ⏳ Consider adding command numbers/line numbers
- ⏳ Consider showing filtered vs unfiltered commands (meta-commands)

**Phase 2d: Open Script**
- ⏳ Parse script file (line-by-line)
- ⏳ Validate commands exist and are executable
- ⏳ Execute commands in sequence
- ⏳ Handle errors gracefully
- ⏳ Provide progress feedback

**Benefits:**
- Batch processing of multiple datasets
- Reproducible analyses
- Automation of repetitive workflows
- Testing and validation
- Training and documentation

**Next Steps:**
- Complete Phase 2a by creating command classes
- Add menu integration
- Test Save Script and View Script first (simpler)
- Then implement Open Script with parser

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
