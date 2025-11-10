# Plan to Eliminate Candidate/Active Instance Split

## Safe Restore Point

**Branch**: master
**Commit Hash**: a6c2b44396d51e66c0f90d663b36a4fb10fed320
**Author**: Ed Schneider <ejschnei@umich.edu>
**Date**: Sun Nov 2 00:05:50 2025 -0400
**Message**: Add debug logging and clean up Status table

**Purpose**: This commit represents a clean, stable state before beginning work on eliminating candidate instances. If needed, revert to this commit using:
```bash
git checkout a6c2b44396d51e66c0f90d663b36a4fb10fed320
```

Or to reset the branch to this point:
```bash
git reset --hard a6c2b44396d51e66c0f90d663b36a4fb10fed320
```

**Feature Branch**: `feature/eliminate-candidate-instances`

---

## Problem Statement

The undo/redo system is incompatible with the current candidate/active architecture for feature objects. This creates a fundamental design conflict that prevents undo from working correctly.

### Root Cause

When a file is loaded (e.g., Configuration command):

1. **Before loading**: `configuration_candidate` and `configuration_active` are two separate `ConfigurationFeature` objects (let's call them ObjectA and ObjectB)
2. **Undo captures state**: Saves the data from ObjectB (the current `configuration_active`)
3. **Command loads file**: Reads file and creates/populates `configuration_candidate` (ObjectA) with new data
4. **Command assigns by reference**: `configuration_active = configuration_candidate` makes both variables point to ObjectA
5. **ObjectB is orphaned**: The original empty object is now unreferenced
6. **Undo attempts to restore**: Restores the captured empty data into `configuration_active`, which now points to ObjectA (not the original ObjectB that was captured)

**Result**: After undo, `configuration_active` still points to the object created during file load, just with its data replaced. But any other references or state associated with the object identity are lost.

### Affected Features

All features using the candidate/active pattern:
- `configuration_candidate` / `configuration_active`
- `correlations_candidate` / `correlations_active`
- `evaluations_candidate` / `evaluations_active`
- `grouped_data_candidate` / `grouped_data_active`
- `individuals_candidate` / `individuals_active`
- `similarities_candidate` / `similarities_active`
- `target_candidate` / `target_active`
- `scores_candidate` / `scores_active`

Each of these is initialized in `director.py` lines 195-210 as separate object pairs.

### Current Assignment Pattern

Example from `ConfigurationCommand` (filemenu.py:56-62):
```python
self._director.configuration_candidate = \
    common.read_configuration_type_file(file_name, "Configuration")
# ... validation ...
self._director.configuration_active = (
    self._director.configuration_candidate)
```

This **assigns by reference**, making both variables point to the same object.

---

## Option 1: Add `copy_from()` Method Using Dictionary-Based Approach

### Description
Add a `copy_from()` method to each feature class that copies all data from one instance to another while preserving object identity.

### Implementation

```python
def copy_from(self, other: ConfigurationFeature) -> None:
    """Copy all data from another ConfigurationFeature into this one.

    This preserves the object identity while replacing all data.
    Used to maintain object references for the undo/redo system.

    Args:
        other: The ConfigurationFeature to copy data from
    """
    import copy

    # Copy all attributes except private/internal ones
    for attr_name, attr_value in vars(other).items():
        if attr_name.startswith('_'):
            # Skip internal attributes like _director
            continue

        if isinstance(attr_value, pd.DataFrame):
            setattr(self, attr_name, attr_value.copy())
        elif isinstance(attr_value, (list, dict)):
            setattr(self, attr_name, copy.deepcopy(attr_value))
        else:
            # For immutable types (int, str, bool, range, etc.)
            setattr(self, attr_name, attr_value)
```

Then change commands from:
```python
self._director.configuration_active = self._director.configuration_candidate
```

To:
```python
self._director.configuration_active.copy_from(self._director.configuration_candidate)
```

### Pros
- **Minimal changes** to existing architecture
- **Preserves candidate/active validation pattern** - files are still read into candidate first
- **Dictionary-based approach** is maintainable - automatically handles all attributes
- **Only touches feature classes and file-loading commands** (~8 feature classes, ~8-10 commands per feature)
- **Clear semantics** - `copy_from()` clearly indicates copying data while preserving identity

### Cons
- **Adds method to each feature class** (8 classes need this method)
- **Slight performance overhead** from deep copying (though this already happens during file loading)
- **Still maintains two separate objects** even though they'll always have identical data after loading
- **Need to ensure copy_from() handles all edge cases** (empty DataFrames, None values, complex nested structures)

### Estimated Effort
- Add `copy_from()` to 8 feature classes: **2-3 hours**
- Update all file-loading commands to use `copy_from()`: **2-3 hours**
- Testing across all features: **2-3 hours**
- **Total: 6-9 hours**

---

## Option 2: Copy Data Without Adding copy_from() Method

### Description
Similar to Option 1, but inline the copying logic directly in commands instead of adding a method to feature classes.

### Implementation

In each command, replace:
```python
self._director.configuration_active = self._director.configuration_candidate
```

With:
```python
import copy
candidate = self._director.configuration_candidate
active = self._director.configuration_active

for attr_name, attr_value in vars(candidate).items():
    if attr_name.startswith('_'):
        continue
    if isinstance(attr_value, pd.DataFrame):
        setattr(active, attr_name, attr_value.copy())
    elif isinstance(attr_value, (list, dict)):
        setattr(active, attr_name, copy.deepcopy(attr_value))
    else:
        setattr(active, attr_name, attr_value)
```

### Pros
- **No changes to feature classes** - keeps them simpler
- **Preserves candidate/active validation pattern**

### Cons
- **Code duplication** - same logic repeated in many commands
- **Higher maintenance burden** - changes need to be replicated across commands
- **Less clear intent** - the copying logic is verbose and obscures the command logic
- **Error-prone** - easy to forget to copy a new attribute type correctly

### Estimated Effort
- Update all file-loading commands: **3-4 hours**
- Testing: **2-3 hours**
- **Total: 5-7 hours**

### Recommendation
**Not recommended** - Option 1 is cleaner with the centralized `copy_from()` method.

---

## Option 3: Eliminate Candidate Instances Entirely

### Description
Remove the candidate/active split. Use only `_active` instances and perform validation on them directly. This simplifies the architecture significantly.

### Current Architecture Purpose

The candidate/active split serves these purposes:
1. **Validation**: Read file into candidate, validate it, then promote to active only if valid
2. **Atomicity**: If validation fails, active remains unchanged
3. **Rollback**: If something goes wrong, candidate can be discarded

### Proposed Architecture

**Instead of**:
```python
self.configuration_candidate = ConfigurationFeature(self)
self.configuration_active = ConfigurationFeature(self)
```

**Use**:
```python
self.configuration_active = ConfigurationFeature(self)
```

**File loading becomes**:
```python
# Read file into temporary object
temp_config = common.read_configuration_type_file(file_name, "Configuration")

# Validate the temporary object
self._director.dependency_checker.detect_consistency_issues_for_object(temp_config)

# If validation passes, copy into active (preserving undo capture)
# The undo system already captured the old state before we got here
self.configuration_active.copy_from(temp_config)  # Still need copy_from!
```

**OR** (cleaner and simpler - Variant 3B):
```python
# Capture state BEFORE making changes (already done in execute())
self.common.capture_and_push_undo_state("Configuration", "active", params)

# Read file directly into active
self._director.configuration_active = common.read_configuration_type_file(
    file_name, "Configuration"
)

# Validate - if validation fails, restore state before raising exception
try:
    self._director.dependency_checker.detect_consistency_issues()
except SpacesError as e:
    # Restore previous state before re-raising
    cmd_state = self._director.pop_undo_state()
    cmd_state.restore_all_state(self._director)
    raise e
```

**Key insight**: The undo system captures state BEFORE file loading. If validation fails, we explicitly restore that state before raising the exception. This maintains atomicity without needing temporary objects or copy_from().

### Pros
- **Eliminates redundancy** - only one object per feature instead of two
- **Simpler architecture** - easier to understand and maintain
- **Reduces memory usage** - half the feature objects
- **Aligns with undo/redo** - undo naturally restores the previous state if validation fails
- **Cleaner conceptual model** - "active" is the single source of truth
- **Fewer variables to track** - no confusion about candidate vs active

### Cons
- **Requires undo system to handle validation failures** - if validation fails after file load, need to ensure undo can restore
- **Changes validation pattern** - validation would happen on active instead of candidate
- **More extensive refactoring** - need to:
  - Remove all `*_candidate` attributes from director (8 features)
  - Update all file-loading commands (~40-50 commands across all features)
  - Update any code that references `*_candidate` objects
  - Update dependency checker if it specifically looks for candidate objects
  - May need to adjust validation logic
- **Risk of partial state** - if validation fails midway through setting attributes, could leave active in inconsistent state (though this is unlikely with current file reading approach)
- **May still need copy_from()** - see variant below

### Two Variants

#### Variant A: Use copy_from() with temporary objects
- Read into temporary object, validate, then `copy_from()` into active
- **Safest approach** - active only changes if validation passes
- Still need `copy_from()` method (same as Option 1)
- Very clean separation: temp object for validation, active for state

#### Variant B: Read directly into active, restore on validation failure
- Read directly into active object, validate, if validation fails restore then raise exception
- Undo system already captured previous state before file load
- Exception handler explicitly restores state before re-raising
- **Simplest approach** - no `copy_from()` needed, no temporary objects
- Requires intercepting exceptions at validation points to trigger restore
- **Decision needed**: Where to intercept exceptions (in commands? in validation? wrapper function?)
- **Decision needed**: Should user be given choice to accept invalid state vs. restore?

### Estimated Effort

#### Variant A (with copy_from and temp objects):
- Add `copy_from()` to 8 feature classes: **2-3 hours**
- Remove `*_candidate` attributes from director: **1 hour**
- Update all file-loading commands to use temp objects: **4-6 hours**
- Update any code referencing candidate objects: **2-3 hours**
- Update validation/dependency checker if needed: **1-2 hours**
- Comprehensive testing across all features: **4-6 hours**
- **Total: 14-21 hours**

#### Variant B (direct load into active):
- Remove `*_candidate` attributes from director: **1 hour**
- Update all file-loading commands: **4-6 hours**
- Update any code referencing candidate objects: **2-3 hours**
- Ensure validation exceptions work with undo: **2-3 hours**
- Update validation/dependency checker: **1-2 hours**
- Comprehensive testing: **4-6 hours**
- **Total: 14-21 hours**

---

## Comparison Matrix

| Aspect | Option 1: copy_from() | Option 2: Inline Copy | Option 3A: Eliminate + copy_from | Option 3B: Eliminate + Direct |
|--------|----------------------|----------------------|----------------------------------|-------------------------------|
| **Effort** | 6-9 hours | 5-7 hours | 14-21 hours | 14-21 hours |
| **Complexity** | Low | Low | Medium | Medium-High |
| **Maintainability** | Good | Poor | Excellent | Good |
| **Architecture Clarity** | OK | OK | Excellent | Very Good |
| **Safety** | High | High | Very High | Medium |
| **Memory Usage** | Current (2x) | Current (2x) | Improved (1x) | Improved (1x) |
| **Undo Compatibility** | Fixed | Fixed | Fixed | Fixed |
| **Future Extensibility** | OK | Poor | Excellent | Good |

---

## Recommendation

### Immediate/Short-term: **Option 1**
Implement `copy_from()` method with dictionary-based approach. This:
- **Fixes the undo/redo bug immediately**
- **Minimal risk** - small, focused change
- **Preserves current architecture** - doesn't disrupt existing patterns
- **Provides time to evaluate** Option 3 more carefully

### Long-term: **Option 3A (Variant A)**
After Option 1 is working and stable, consider refactoring to eliminate candidate instances using the temporary object + `copy_from()` pattern. This:
- **Simplifies architecture** significantly
- **Reuses the copy_from() method** already created in Option 1
- **Safer than Variant B** - validation on temp object before affecting active
- **Cleaner conceptual model** - single source of truth
- **Better long-term maintainability**

### Why Not Option 2?
Code duplication and poor maintainability make this a non-starter.

### Why Not Option 3B (Variant B)?
While conceptually appealing (fewest lines of code), it's riskier because:
- Active object is briefly in invalid state if validation fails
- Harder to reason about exception handling and undo interaction
- Need to ensure all validation failures properly trigger undo
- More potential for edge cases and bugs

---

## Standard Steps for Converting Each Feature

For each feature (correlations, evaluations, configuration, grouped_data, individuals, similarities, target, scores), follow these steps:

### Step 1: Remove Candidate Initialization
1. Remove `*_candidate` initialization from director.py

### Step 2: Update File-Loading Commands
1. Update commands to read directly into `*_active` instead of `*_candidate`
2. Remove any `*_active = *_candidate` assignments

### Step 3: Add Exception Handling with Restoration

#### Step 3A: Add Restore Calls in Read Functions (common.py)
1. Determine which read function(s) the feature uses (e.g., `read_lower_triangular_matrix()`, `read_configuration_type_file()`, etc.)
2. Examine the read function and ALL helper functions it calls
3. Find EVERY location where an exception can be raised
4. Before EACH exception, add `event_driven_automatic_restoration()` call

#### Step 3B: Add Try/Except Wrapper in Command Class (filemenu.py)
1. Create a helper method `_read_X()` in the Command class if it doesn't exist
2. Wrap the read operation in a try/except block
3. Catch relevant exceptions (FileNotFoundError, PermissionError, ValueError, SpacesError, etc.)
4. In except block, call `event_driven_optional_restoration("feature_name")`
5. Only re-raise exception if restoration failed
6. Test with malformed files to verify each exception path works correctly

### Step 4: Update Dependencies
1. Update dependencies.py to use `*_active` in new_feature_dict instead of `*_candidate`

### Step 5: Test Thoroughly
1. Test with valid files
2. Test with various malformed files to trigger different exception paths
3. Verify undo/redo works correctly after successful loads
4. Verify state is restored correctly when loads fail

---

## Open Questions

1. **Are candidate objects referenced anywhere outside file-loading commands?**
   - Need to search for all `*_candidate` references
   - May affect dependency checking or other validation logic

2. **Does validation logic depend on candidate/active distinction?**
   - Need to review `dependency_checker` implementation
   - May need to pass object to validate as parameter

3. **Are there any commands that compare candidate vs active?**
   - Could be used for "show changes before apply" type features
   - Need to search codebase

4. **Do any features have special handling that depends on candidate?**
   - Some features might have unique validation or processing patterns

5. **Is there any UI that shows candidate state before activation?**
   - Preview dialogs, confirmation screens, etc.

---

## Risk Assessment

### Option 1 Risks: **LOW**
- Limited scope, focused change
- Easy to test and verify
- Easy to roll back if issues arise

### Option 3A Risks: **MEDIUM**
- Broader scope affects many commands
- Need careful testing of validation flow
- Potential for subtle bugs if candidate was used in unexpected ways

### Option 3B Risks: **MEDIUM-HIGH**
- Active object temporarily invalid
- Complex interaction with exception handling
- Harder to test all edge cases
- More potential for state corruption bugs

---

---

## Research Findings (Completed)

### Undo System Investigation ✓
- State capture happens BEFORE modifications via `capture_and_push_undo_state()`
- State restore copies data INTO current `_active` object (not object reassignment)
- Restore methods in `command_state.py` lines 469-921
- **Key insight**: Undo doesn't care about object identity, only data

### Consistency Checker Investigation ✓
- **Purpose**: Compare newly loaded feature against OTHER existing features
- **NOT**: Comparing new vs old of same feature
- Example: New configuration checked against existing similarities for matching point names
- Uses `new_feature_dict` (reads from `_candidate`) vs `existing_feature_dict` (reads from `_active`)
- Determines "new" feature from command name via `_create_new_from_command_without_open()`

### Candidate References Count ✓
Total: 167 occurrences across 5 files
- `director.py`: 8 (initialization)
- `dependencies.py`: 38 (consistency checker)
- `filemenu.py`: 102 (file loading commands)
- `associationsmenu.py`: 17 (line of sight command)
- `viewmenu.py`: 2 (**BUG** - should use `_active`)

---

## Design Decisions for Option 3B

### Decision 1: Where to intercept exceptions for state restoration?

**Option A: In each command's execute() method** - ❌ ELIMINATED
- Wrap validation calls in try/except within execute()
- **Reason for elimination**: We never raise exceptions in execute functions
- This option is not viable

**Option B: In validation methods themselves**
- Modify `detect_consistency_issues()` and related methods to restore before raising
- Add restore logic within the validation method itself

```python
def detect_consistency_issues(self):
    try:
        # ... validation logic ...
        if not dimensions_match:
            raise SpacesError(title, message)
    except SpacesError as e:
        cmd_state = self._director.pop_undo_state()
        cmd_state.restore_all_state(self._director)
        raise e
```

- **Pros**: Centralized in validation layer, no duplication across commands
- **Cons**: Validation method needs access to undo stack, assumes all validation failures need restore

**Option C: In central exception handler**
- Modify `director.request_control()` exception handler (line 862)
- Add logic to determine if restore is needed before showing error

```python
except SpacesError as e:
    # Determine if we need to restore (was state captured? was it modified?)
    if self._should_restore_on_failure():
        cmd_state = self.pop_undo_state()
        cmd_state.restore_all_state(self)
    self.unable_to_complete_command_set_status_as_failed()
    self.common.error(e.title, e.message)
```

- **Pros**: Single location handles all commands uniformly
- **Cons**: Hard to determine when restore is appropriate, may restore when not needed or fail to restore when needed

**Option D: At each specific exception raise point (after _active modified)** - ⭐ MOST FLEXIBLE
- Add restore logic directly before each `raise` statement that occurs in the "danger zone"
- **Danger zone** = code between `_active` assignment and successful command completion
- Applies to ALL exception types (SpacesError, ValueError, KeyError, file errors, pandas errors, etc.)
- Can use direct restore OR wrapper function for user choice

Direct restore approach:
```python
# In dependencies.py, consistency checking:
if not dimensions_match:
    # Restore before raising
    cmd_state = self._director.pop_undo_state()
    cmd_state.restore_all_state(self._director)
    raise SpacesError(title, message)

# In file reading functions:
if file_error:
    cmd_state = self._director.pop_undo_state()
    cmd_state.restore_all_state(self._director)
    raise SpacesError(title, message)
```

Wrapper function approach (with user choice):
```python
if not dimensions_match:
    self._handle_failure_with_user_choice(
        title="Dimension mismatch",
        message="Configuration has 3 dimensions but Similarities expects 2",
        error_type=SpacesError
    )
    # Wrapper shows dialog asking user to choose:
    #   - Restore previous state (undo the load)
    #   - Keep new data (accept inconsistency)
    #   - Cancel (don't raise exception, try to continue)
    # Then raises exception based on user choice
```

- **Pros**:
  - Most precise control - only affects exact failure points
  - Enables user choice per failure (aligns with philosophy)
  - Can combine direct restore AND user choice as appropriate
  - Clear about what's in "danger zone"
- **Cons**:
  - More locations to modify
  - Need to identify every raise point in danger zone (not just validation)
- **Key insight**: Must handle ANY exception type, not just SpacesError

**Recommendation**: Option D with wrapper function for user choice
- Aligns with development philosophy: transparency and user agency
- Most flexible - can use direct restore for critical errors, user choice for validation failures
- Clear mapping to problem: "after this line, _active is modified"

---

### Decision 2: User control over restoration

**Options:**
- **A. Always restore automatically** - Validation failure = automatic rollback
- **B. Ask user per failure** - Dialog: "Validation failed. Restore previous state or keep new data?"
- **C. Restore but allow re-undo** - Automatic restore, but user can undo the restoration
- **D. Never restore automatically** - User must manually Undo if they want previous state
- **E. User preference/setting** - Let user configure default behavior

**Considerations:**
- User agency and transparency (per development philosophy)
- When might user want to keep "invalid" state? (debugging, exploration, edge cases)
- Some errors are critical (file not found), others are warnings (dimension mismatch)
- Could categorize errors: critical (auto-restore) vs. recoverable (ask user)

**Recommendation**: Option B (ask user) with Option E (make it configurable)
- Default: Ask user for validation failures
- Allow preference for "always restore" or "never restore"
- Critical errors (file I/O, etc.) could auto-restore without asking

---

### Decision 3: Which exception raise points need restore?

**Need to identify:**
- All locations that `raise` any exception type
- **After** `_active` has been assigned new data
- **Before** command successfully completes

**Categories of exceptions in danger zone:**
1. **Consistency validation** - `detect_consistency_issues()` in dependencies.py
2. **File reading errors** - in `read_configuration_type_file()` and similar
3. **Data processing errors** - pandas operations, numpy calculations
4. **Unexpected runtime errors** - any Python exception during command execution

**Scope:**
- File-loading commands: Configuration, Correlations, Evaluations, Grouped data, Individuals, Scores, Similarities, Target
- Data generation commands: Line of sight, Create, New grouped data
- Any other command that assigns to `_active`

---

## Implementation Progress

### Approach Selected: Option 3B (Direct Load into Active)

We are eliminating candidate instances by reading directly into `_active` instances. The undo system handles rollback if validation fails.

### Features In Progress

#### correlations_candidate - ✓ COMPLETE
- ✓ Step 1: Removed `correlations_candidate` initialization from director.py
- ✓ Step 2: Updated filemenu.py to use `correlations_active` directly
- ✓ Step 3: Added restore calls to all read function exceptions (9 total)
- ✓ Step 4: Updated dependencies.py to use `correlations_active` in new_feature_dict
- ✓ Step 5: Testing complete - verified working correctly

**Read functions used**: `read_lower_triangular_matrix()` and its helpers:
- ✓ `read_lower_triangle_size()` - added restore before 4 exception points (lines 1865, 1872, 1880, 1888)
- ✓ `read_lower_triangle_dictionary()` - added restore before 1 exception point (line 1918)
- ✓ `read_lower_triangle_values()` - added restore before 1 exception point (line 1959)
- ✓ Catch blocks - added restore before 3 exception points (lines 1790, 1796, 1802)

#### evaluations_candidate - ✓ COMPLETE
- ✓ Step 1: Removed `evaluations_candidate` initialization from director.py
- ✓ Step 2: Updated filemenu.py to use `evaluations_active` directly
- ✓ Step 3: Reviewed read functions - all exception points already covered
- ✓ Step 4: Updated dependencies.py to use `evaluations_active` in new_feature_dict
- ✓ Step 5: Testing complete - verified working correctly

**Read approach**: Evaluations uses `pd.read_csv()` and directly populates `evaluations_active` fields.
- Exception handling in `_read_evaluations()` (lines 504-537) already covers all exception points
- Catches: FileNotFoundError, PermissionError, EmptyDataError, ParserError, ValueError
- Calls `event_driven_optional_restoration()` on any exception (line 531)
- **No changes needed** - exception handling was already complete

**Known Issue**: CSV files that are like Evaluations (e.g., score files, sample design files) will currently work when they should be caught as invalid. The proper solution is to add file typing (first line of file), but this is deferred for now since it's not straightforward for CSV files.

### Remaining Features

#### configuration_candidate - ✓ COMPLETE
- ✓ Step 1: Removed `configuration_candidate` initialization from director.py
- ✓ Step 2: Updated filemenu.py ConfigurationCommand to use `configuration_active` directly
- ✓ Step 3: Updated filemenu.py CreateCommand to use `configuration_active` directly
- ✓ Step 4: Read functions already had exception handling from common.py
- ✓ Step 5: Updated dependencies.py to use `configuration_active` in new_feature_dict
- ✓ Step 6: Testing complete - verified working correctly with multiple test scenarios

**Read functions used**: `read_configuration_type_file()` which uses:
- `read_first_integer()` - exception handling already in place
- `read_identifiers()` - exception handling already in place
- Direct file reading with pandas - exception handling in command class
- All restoration paths working correctly for both empty and populated states

**CreateCommand pattern**: Gathers all input into local variables before capturing state and modifying `configuration_active`, so all cancellation exceptions occur safely before any state modification. No additional exception handling needed.

**CreateCommand refactoring completed**: Removed all if statements and exceptions from execute() method by extracting logic into helper methods:
- `_get_configuration_information_from_user()` - Orchestrates gathering all user input
- `_get_number_of_points()` - Gets npoint with validation
- `_get_number_of_dimensions()` - Gets ndim with validation
- `_get_point_labels_and_names()` - Gets point labels and names with validation
- `_get_dimension_labels_and_names()` - Gets dimension labels and names with validation
- `_get_coordinates_for_points()` - Gets coordinates with validation

The execute() method is now flat with no if statements or exceptions, following the project standard that exceptions should be raised in helper functions at the point of failure.

#### grouped_data_candidate - ✓ COMPLETE
- ✓ Step 1: Removed `grouped_data_candidate` initialization from director.py
- ✓ Step 2: Updated file loading commands to use `grouped_data_active` directly
- ✓ Step 3: Updated NewGroupedDataCommand to use `grouped_data_active` directly
- ✓ Step 4: Updated dependencies.py to use `grouped_data_active` in new_feature_dict
- ✓ Step 5: Testing complete - verified working correctly

#### individuals_candidate - ✓ COMPLETE
- ✓ Step 1: Removed `individuals_candidate` initialization from director.py
- ✓ Step 2: Updated IndividualsCommand to use `individuals_active` directly
- ✓ Step 3: Updated dependencies.py to use `individuals_active` in new_feature_dict
- ✓ Step 4: Testing complete - verified working correctly

**Read approach**: Individuals uses `pd.read_csv()` and directly populates `individuals_active` fields (similar to evaluations and scores).
- Exception handling in `_read_individuals()` (lines 591-619) already covers all exception points
- Catches: FileNotFoundError, PermissionError, EmptyDataError, ParserError, ValueError
- Calls `event_driven_optional_restoration()` on any exception
- All restoration paths working correctly

#### similarities_candidate - ✓ COMPLETE
- ✓ Step 1: Removed `similarities_candidate` initialization from director.py
- ✓ Step 2: Updated filemenu.py SimilaritiesCommand to use `similarities_active` directly
- ✓ Step 3: Added restore calls to all read function exceptions
- ✓ Step 4: Updated dependencies.py to use `similarities_active` in new_feature_dict
- ✓ Step 5: Testing complete - verified working correctly

**Read functions used**: `read_lower_triangular_matrix()` (same as correlations)
- Uses the same helper functions that were already updated for correlations
- All exception points already have restore calls from correlations work

#### target_candidate - ✓ COMPLETE
- ✓ Step 1: Removed `target_candidate` initialization from director.py
- ✓ Step 2: Updated file loading commands to use `target_active` directly
- ✓ Step 3: Updated dependencies.py to use `target_active` in new_feature_dict
- ✓ Step 4: Testing complete - verified working correctly

#### scores_candidate - ✓ COMPLETE
- ✓ Step 1: Removed `scores_candidate` initialization from director.py
- ✓ Step 2: Updated OpenScoresCommand to use `scores_active` directly
- ✓ Step 3: Added restore calls to exception points in `_read_scores()`
- ✓ Step 4: Updated dependencies.py to use `scores_active` in new_feature_dict
- ✓ Step 5: Testing complete - verified working correctly

**Read approach**: Scores uses `pd.read_csv()` and directly populates `scores_active` fields (similar to evaluations).
- Exception handling in `_read_scores()` already had comprehensive coverage
- Catches: FileNotFoundError, PermissionError, EmptyDataError, ParserError, ValueError
- All exception paths now call restoration appropriately

**Debugging statements removed**: Cleaned up all debugging print statements from consistency checking functions (`do_dimensions_match()` and `do_points_match()` in dependencies.py).

**Other commands that create scores**: ScoreIndividualsCommand, FactorAnalysisCommand, and FactorAnalysisMachineLearningCommand also create scores but don't read from files. These commands create scores computationally and will be reviewed separately as needed.

---

## Consistency Checking Restoration Enhancement - ✓ COMPLETE

### Problem Identified
When consistency checking fails and the user chooses to abandon the new feature, the system needs to decide whether to restore the previous state or leave the feature empty. The original code had two issues:

1. **No restoration at all**: Consistency checking called `abandon_dict[new]()` which manually cleared fields, but never used the undo system
2. **Nonsensical question**: Even when using restoration, asking "Do you want to restore previous state?" when there was no previous state (feature was empty) is meaningless

### Solution Implemented

#### 1. Added Helper Method: `_was_feature_empty_in_state()` (common.py:3280)
- Checks if a feature was empty in the captured undo state
- Supports all 8 features: configuration, correlations, evaluations, grouped_data, individuals, scores, similarities, target
- Returns `True` if feature was empty (nothing to restore), `False` otherwise
- Implementation checks feature-specific emptiness indicators:
  - correlations: `nitem == 0` or `correlations_as_dataframe.empty`
  - evaluations: `evaluations.empty`
  - scores: `len(scores) == 0`
  - configuration: `npoint == 0`
  - similarities: `nreferent == 0`
  - target: `npoint == 0`
  - grouped_data: `ngroup == 0`
  - individuals: `nindividual == 0`

#### 2. Enhanced `event_driven_optional_restoration()` (common.py:3327)
- Now peeks at undo stack before showing dialog
- If previous state was empty: automatically clears feature without asking user
- If previous state had data: shows "Restore or Clear?" dialog
- Updated docstring to reflect new behavior
- **Key insight**: Only asks questions that make sense

#### 3. Updated Consistency Checking (dependencies.py:763)
- Modified `resolve_conflict_w_existing_data()` to use restoration system
- Added `feature_name_map` to translate display names ("Correlations") to internal names ("correlations")
- Updated 3 code paths to call `event_driven_optional_restoration()`:
  - **Case 1**: User chooses to abandon new feature (keep existing)
  - **Case _**: Unexpected/default case
  - **Else**: Dialog cancelled or failed
- Replaced direct `abandon_dict[new]()` calls with proper restoration

### Why Not Check in `event_driven_automatic_restoration()`?

Decision: **Leave automatic restoration as-is** (no emptiness check needed)

**Reasoning**:
- Used for critical errors where restoration is always appropriate
- Restoring empty to empty is harmless and correct (no-op)
- No user question involved, so no "nonsensical question" issue
- Simpler code is more robust for critical error paths
- Performance overhead is negligible

### Benefits

1. **Smarter UX**: Never asks users to restore nothing
2. **Consistent with undo system**: Consistency checking now properly uses undo/restore
3. **Single source of truth**: All restoration logic centralized in `event_driven_optional_restoration()`
4. **Handles both cases**: Works correctly whether previous state was empty or populated
5. **No breaking changes**: Existing calls continue to work unchanged
6. **Better error recovery**: User gets appropriate choices based on actual state

### Testing Scenarios

**Test 1: Empty previous state + consistency error**
- Setup: No correlations exist
- Action: Load correlations that fail consistency check, choose to abandon new
- Expected: Automatically clears, no restoration dialog

**Test 2: Non-empty previous state + consistency error**
- Setup: Correlations A exists
- Action: Load correlations that fail consistency check, choose to abandon new
- Expected: Dialog asks "Restore A or clear?", restores if Yes

**Test 3: Empty previous state + file error**
- Setup: No correlations exist
- Action: Try to read malformed correlations file
- Expected: Automatically clears, no restoration dialog

**Test 4: Non-empty previous state + file error**
- Setup: Correlations A exists
- Action: Try to read malformed correlations file
- Expected: Dialog asks "Restore A or clear?"

### Files Modified
- `src/common.py`: Added `_was_feature_empty_in_state()`, enhanced `event_driven_optional_restoration()`
- `src/dependencies.py`: Updated `resolve_conflict_w_existing_data()` to use restoration system

---

## Next Steps

1. ✓ **Sleep on it**
2. ✓ **Search codebase** for all `*_candidate` references
3. ✓ **Review dependency checker** to understand validation dependencies
4. ✓ **Review undo/redo system** to understand state capture/restore
5. ✓ **Implement direct load pattern** - Started with correlations and evaluations
6. ✓ **Fix consistency checking restoration** - Completed
7. **Continue implementing remaining features** - One at a time with testing
8. **Complete all 8 features**
9. **Final comprehensive testing**
10. **Execute Cleanup Phase** - See below

---

## Phase 4: Cleanup

After completing the elimination of candidate instances for all 8 features, the following cleanup tasks should be performed:

### 1. Individuals Feature Completion - ✓ COMPLETE
- ✓ Complete conversion of `individuals_candidate` to direct `individuals_active` usage
- ✓ Test individuals file loading and validation

### 2. File Typing for CSV Files - ✓ COMPLETE (Commit: e1ec46b)
Currently CSV files (scores, evaluations, uncertainty, individuals) lack file type identification, which causes the system to accept invalid files that happen to match the CSV format.

**Implementation Complete:**
- ✓ Designed file typing approach using comment line (e.g., `# TYPE: SCORES`) as first line
- ✓ Added `write_csv_with_type_header()` in common.py to write type headers
- ✓ Added `read_csv_with_type_check()` in common.py to validate type headers
- ✓ Implemented in save commands:
  - ✓ Save Scores - writes SCORES type header
  - ✓ Save Individuals - writes INDIVIDUALS type header
  - Note: Evaluations are never created within Spaces (only read), so no Save Evaluations command
  - Note: Uncertainty still needs architectural decisions (deferred to task #3)
- ✓ Implemented in read commands:
  - ✓ Open Scores - validates SCORES type header
  - ✓ Open Evaluations - validates EVALUATIONS type header
  - ✓ Open Individuals - validates INDIVIDUALS type header
  - Note: Uncertainty deferred to task #3
- ✓ Added specific SpacesError exceptions for:
  - Missing type headers
  - Type mismatches
  - File not found
  - Permission errors
- ✓ All errors trigger proper restoration flow

**What Was Done:**
- CSV files now include type metadata as comment line: `# TYPE: SCORES`
- Pandas `read_csv()` automatically skips comment lines, so format is backward compatible
- Type validation ensures users can't accidentally load wrong file type
- Consistent error handling with restoration across all CSV features

### 3. Uncertainty, Sample Design, Sample Repetitions, and Sample Solutions
Resolve architectural and implementation decisions for these related features:
- Determine how uncertainty should be handled in the undo/redo system
- Decide on candidate/active pattern (if applicable)
- Review sample design, repetitions, and solutions features
- Ensure consistent patterns across these related features

### 4. Refactor `get_command_parameters()` to Use Dictionary-Based Helper
Current implementation uses multiple `if/elif` statements to handle different getter types. Consider refactoring for better maintainability.

**Proposal:**
- Create `getter_type_dict` mapping getter types to handler functions
- Extract handler logic into helper function `create_getter_type_dict()`
- Simplify main `get_command_parameters()` function to use dictionary lookup

**Current getter types used:**
- `file_dialog` - File selection dialogs
- `set_value_dialog` - Numeric value input (SetValueDialog)
- `pair_of_points_dialog` - Select exactly two items (PairofPointsDialog)
- `chose_option_dialog` - Radio button selection (ChoseOptionDialog)
- `focal_item_dialog` - Select single item from list
- `select_items_dialog` - Multiple item selection (SelectItemsDialog)
- `get_string_dialog` - Text input (GetStringDialog)
- `get_integer_dialog` - Integer input (GetIntegerDialog)
- `get_coordinates_dialog` - Coordinate input (GetCoordinatesDialog)
- `modify_items_dialog` - Modify list of items (ModifyItemsDialog)
- `modify_values_dialog` - Modify numeric values (ModifyValuesDialog)
- `modify_text_dialog` - Modify text fields (ModifyTextDialog)
- `move_dialog` - Reorder items (MoveDialog)
- `matrix_dialog` - Matrix input (MatrixDialog)
- `set_names_dialog` - Set names for items (SetNamesDialog)

**Benefits:**
- Easier to add new getter types
- More maintainable and readable
- Follows same dictionary-driven pattern used elsewhere in Spaces

### 5. Investigate Undo/Redo Enable/Disable for Toolbar and Menu Items
Currently unclear how toolbar and menu items for Undo and Redo are enabled/disabled based on stack state.

**Tasks:**
- Search for Undo/Redo enable/disable logic
- Verify proper enabling when undo stack has items
- Verify proper disabling when undo stack is empty
- Verify proper enabling when redo stack has items
- Verify proper disabling when redo stack is empty
- Test that toolbar and menu items stay synchronized
- Consider if this needs enhancement or is working correctly

### 6. Scan for Remaining `_candidate` References
Perform comprehensive search for any remaining references to candidate instances:

**Tasks:**
- Search for all `*_candidate` patterns in codebase
- Verify each reference has been properly updated or removed
- Check for:
  - Direct attribute access (`self._director.configuration_candidate`)
  - String references in error messages or logs
  - Comments that still reference old architecture
  - Documentation that needs updating

**Known locations to check:**
- `director.py` - Initialization and attributes
- `dependencies.py` - Consistency checking
- `filemenu.py` - File loading commands
- `associationsmenu.py` - Line of sight and other commands
- `viewmenu.py` - Status and other view commands
- Any other menu files that might reference features

### 7. Consider Renaming All `_active` References
Now that candidate instances are eliminated, the `_active` suffix is no longer necessary (there's no candidate/active distinction).

**Decision needed:**
- Should we rename `configuration_active` → `configuration`?
- Should we rename `correlations_active` → `correlations`?
- And so on for all 8 features?

**Considerations:**
- **Pro**: Simpler, cleaner names without unnecessary suffix
- **Pro**: Matches new architecture (single instance per feature)
- **Pro**: More consistent with naming elsewhere in codebase
- **Con**: Very large refactoring across entire codebase
- **Con**: May introduce bugs if any references are missed
- **Con**: Git history becomes harder to follow (major rename)
- **Con**: Not strictly necessary - current names are functional

**Recommendation**: Defer this decision until after all other cleanup is complete. The `_active` suffix is not harmful and can remain indefinitely if the refactoring effort is deemed too risky or time-consuming.

### 8. Review Parameter Names and Consider Standardizing
Review parameter names used throughout the codebase for consistency:

**Tasks:**
- Identify common parameter patterns
- Look for inconsistencies in naming conventions
- Consider standardizing names like:
  - `file_name` vs `filename` vs `file_path`
  - `value_type` vs `type` vs `data_type`
  - `item_name` vs `name` vs `label`
  - Dimension-related parameters
  - Point-related parameters

**Goal**: Improve consistency and readability across the codebase

**Approach:**
- Document current parameter naming patterns
- Propose standard naming conventions
- Assess impact of changes (how many files affected?)
- Decide if standardization is worth the effort
- If proceeding, create phased plan for parameter renaming

### 9. Review Execute Functions in all commands starting with filemenu.py
Review all execute methods in all commands to ensure adherence to standards and completeness:

**Tasks:**
- Review each execute function in current filemenu.py for adherence to project standards:
  - Execute methods should be flat with minimal nesting
  - No if statements or exceptions in execute() - all should be in helper methods
  - Proper use of helper methods for complex logic
  - Consistent error handling patterns
  - Proper documentation and type hints
  - See Spaces documentation - flow within commands
- Compare each execute function to its archived version to verify functionality:
  - Locate corresponding archived versions in `archive/` directory
  - Verify all functionality from archived versions is preserved
  - Check that no features or edge cases were lost during refactoring
  - Document any intentional differences or improvements
- Identify any commands that need refactoring to meet standards
- Create list of any missing functionality that needs to be restored

**Commands in filemenu.py to review:**
- ConfigurationCommand
- CreateCommand
- CorrelationsCommand
- EvaluationsCommand
- GroupedDataCommand
- IndividualsCommand
- ScoresCommand
- SimilaritiesCommand
- TargetCommand
- All other file-loading and data-creation commands in filemenu.py

**Goal**: Ensure all execute methods follow consistent patterns and retain full functionality from previous implementations

**Commands whose review has been completed

- Active commands
  - configuration
  
- Passive commands
  - compare

- Other commands

---
### 10. Reduce command/function compexity
- get_command_parameters
- capture_and_push_undo_state
- Deactivate command
- SaveScript command
  - read_grouped_data