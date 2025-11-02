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

**OR** (cleaner but requires more refactoring):
```python
# Read file directly into active
self._director.configuration_active = common.read_configuration_type_file(
    file_name, "Configuration"
)

# Validate
self._director.dependency_checker.detect_consistency_issues()
# If validation fails, an exception is raised and active remains unchanged
# due to how undo restoration works
```

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

#### Variant B: Read directly into active, rely on undo
- Read directly into active object, validate, if validation fails raise exception
- Undo system already captured previous state, so exception causes undo
- **Riskiest approach** - active briefly in invalid state if validation fails
- No need for `copy_from()`
- Requires ensuring validation exceptions properly trigger undo

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

## Implementation Phases

### Phase 1: Fix the Bug (Option 1)
1. Add `copy_from()` method to `ConfigurationFeature`
2. Update `ConfigurationCommand` to use `copy_from()`
3. Test thoroughly with configuration files
4. Remove debug print statements from `command_state.py`

### Phase 2: Extend to All Features (Option 1)
1. Add `copy_from()` to remaining 7 feature classes
2. Update all file-loading commands to use `copy_from()`
3. Comprehensive testing across all features

### Phase 3: Evaluate Option 3A (Future)
1. Analyze all references to `*_candidate` objects
2. Document current validation patterns
3. Design temp object + copy_from pattern
4. Create detailed refactoring plan
5. Implement incrementally, one feature at a time
6. Extensive testing after each feature conversion

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

## Next Steps

1. **Sleep on it** ✓
2. **Search codebase** for all `*_candidate` references to understand full scope
3. **Review dependency checker** to understand validation dependencies
4. **Decide on approach** (likely Option 1 now, Option 3A later)
5. **Implement chosen option**
6. **Test thoroughly**
