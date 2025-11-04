# Cluster Implementation Plan

## Problem Statement

When clustering data from different sources (scores, distances, evaluations, similarities), the plotting code needs to know:
1. Which data source was clustered
2. Where to get axis names for plot labels

Currently cluster results are stored in `scores_active`, which causes problems:
- When clustering distances (not scores), `scores_active` may be empty or contain unrelated data
- `scores_active.hor_axis_name` and `scores_active.vert_axis_name` may be incorrect for non-score clustering
- Conceptually, clusters are not scores - they're a different data type

## Current Architecture

### Data Sources
Four possible data sources for clustering:
1. **scores** → axis names from `scores_active.hor_axis_name` / `vert_axis_name`
2. **distances** → axis names from `configuration_active.hor_axis_name` / `vert_axis_name`
3. **evaluations** → axis names from `evaluations_active.hor_axis_name` / `vert_axis_name`
4. **similarities** → axis names from `similarities_active.hor_axis_name` / `vert_axis_name`

### Current Storage (in scores_active)
- `cluster_labels` - array of cluster assignments for each point
- `cluster_centers` - centroid coordinates for each cluster
- `n_clusters` - number of clusters
- `original_clustered_data` - the original data that was clustered (for plotting)

### Current Problem
The traceback shows:
```
KeyError: 'Left-Right'
```
When trying to access `scores[hor_axis_name]` where `scores` DataFrame doesn't have the column 'Left-Right' because we clustered distances, not scores.

## Proposed Solution: ClustersFeature or Clusters Class

### Option A: Create ClustersFeature (similar to ScoresFeature)

Add a new feature class in `features.py`:

```python
class ClustersFeature:
    def __init__(self, director: Status) -> None:
        self._director = director

        # Cluster results
        self.cluster_labels: np.ndarray | None = None
        self.cluster_centers: np.ndarray | None = None
        self.n_clusters: int = 0
        self.original_clustered_data: pd.DataFrame | None = None

        # Metadata about what was clustered
        self.clustered_data_source: str = ""  # "scores", "distances", "evaluations", "similarities"

        # Axis names for plotting (copied from appropriate *_active at cluster time)
        self.hor_axis_name: str = ""
        self.vert_axis_name: str = ""
```

Then in `director.py`:
```python
self.clusters_active = ClustersFeature(self)
```

### Option B: Create a Clusters class (not a Feature)

**Design Question**: Features have specific logic and patterns in the codebase. It's unclear if clusters conceptually fit the "feature" pattern.

Clusters might need to be something different that:
- Can have multiple instances (e.g., user creates multiple different clusterings)
- Represents results of an operation rather than a data type
- Has a lifecycle independent of the source data

This needs more research into:
1. What makes something a "feature" in Spaces architecture?
2. Do features always represent input data types, or can they represent derived results?
3. Should there be a concept of "results" or "analysis outputs" separate from features?
4. Can/should users maintain multiple cluster results simultaneously?

## Implementation Changes Required

### 1. Cluster Command (modelmenu.py)

Store cluster results in `clusters_active` instead of `scores_active`:

```python
# Store cluster results
self._director.clusters_active.cluster_labels = cluster_labels
self._director.clusters_active.cluster_centers = cluster_centers
self._director.clusters_active.n_clusters = n_clusters
self._director.clusters_active.original_clustered_data = self.data_for_clustering.copy()
self._director.clusters_active.clustered_data_source = name_source

# Copy appropriate axis names for plotting
if name_source == "scores":
    self._director.clusters_active.hor_axis_name = \
        self._director.scores_active.hor_axis_name
    self._director.clusters_active.vert_axis_name = \
        self._director.scores_active.vert_axis_name
elif name_source == "distances":
    self._director.clusters_active.hor_axis_name = \
        self._director.configuration_active.hor_axis_name
    self._director.clusters_active.vert_axis_name = \
        self._director.configuration_active.vert_axis_name
elif name_source == "evaluations":
    self._director.clusters_active.hor_axis_name = \
        self._director.evaluations_active.hor_axis_name
    self._director.clusters_active.vert_axis_name = \
        self._director.evaluations_active.vert_axis_name
elif name_source == "similarities":
    self._director.clusters_active.hor_axis_name = \
        self._director.similarities_active.hor_axis_name
    self._director.clusters_active.vert_axis_name = \
        self._director.similarities_active.vert_axis_name
```

### 2. Matplotlib Plotting (matplotlib_plots.py)

Change from reading `scores_active` to reading `clusters_active`:

```python
def request_clusters_plot_for_tabs_using_matplotlib(self) -> None:
    director = self._director
    common = director.common
    matplotlib_common = director.matplotlib_common
    clusters_active = director.clusters_active  # Changed from scores_active

    # Set axis ranges based on clustered data
    if clusters_active.original_clustered_data is not None:
        original_data = clusters_active.original_clustered_data
        common.set_axis_extremes_based_on_coordinates(
            original_data.iloc[:, :2])

    fig = self.plot_clusters_using_matplotlib()
    matplotlib_common.plot_to_gui_using_matplotlib(fig)

    return

def plot_clusters_using_matplotlib(self) -> plt.Figure:
    director = self._director
    common = director.common
    matplotlib_common = director.matplotlib_common
    clusters_active = director.clusters_active  # Changed from scores_active
    hor_axis_name = clusters_active.hor_axis_name
    vert_axis_name = clusters_active.vert_axis_name
    point_size = common.point_size

    fig, ax = matplotlib_common.begin_matplotlib_plot_with_title("Clusters")
    ax = matplotlib_common.set_aspect_and_grid_in_matplotlib_plot(ax)

    ax.set_xlabel(hor_axis_name)
    ax.set_ylabel(vert_axis_name)

    matplotlib_common.set_ranges_for_matplotlib_plot(ax)

    # Get the cluster data
    cluster_labels = clusters_active.cluster_labels
    original_data = clusters_active.original_clustered_data

    # Plot points colored by cluster
    data_1 = original_data.iloc[:, 0]
    data_2 = original_data.iloc[:, 1]
    # ... rest of plotting logic
```

### 3. PyQtGraph Plotting (pyqtgraph_plots.py)

Similar changes to use `clusters_active` instead of `scores_active`.

### 4. Dependencies (dependencies.py)

Update dependency checking to look for `clusters_active` data:

```python
def have_clusters(self) -> bool:
    return (self._director.clusters_active.cluster_labels is not None and
            self._director.clusters_active.n_clusters > 0)
```

### 5. Command State (command_state.py)

May need to add capture/restore logic for `clusters_active` state for undo/redo functionality.

## Benefits of This Approach

1. **Conceptual Clarity**: Clusters are treated as their own data type, not conflated with scores
2. **Independence**: Cluster results don't depend on whether scores exist
3. **Correct Axis Labels**: Each cluster result stores its own axis names from the appropriate source
4. **Extensibility**: Easy to add more cluster-related attributes in the future
5. **Multiple Sources**: Clean handling of all four data sources

## Open Questions / Research Needed

1. **Feature Pattern**: What defines a "feature" in Spaces? Do clusters fit that pattern?
2. **Multiple Instances**: Should users be able to maintain multiple cluster results? (e.g., cluster both scores and distances simultaneously)
3. **Lifecycle**: When should cluster results be cleared? Only when new clustering is done, or also when source data changes?
4. **Undo/Redo**: How should cluster state be captured for undo/redo?
5. **Dependencies**: What other code paths access `scores_active.cluster_*` attributes that would need updating?
6. **Status Display**: Should Status show cluster information separately from scores?

## Alternative: Minimal Change Approach

If creating a new feature/class is too disruptive, a minimal fix could:
1. Add `clustered_data_source: str = ""` to `ScoresFeature`
2. Have cluster command set this and copy axis names to `scores_active`
3. Have plotting code read from `scores_active` as it does now

This is less clean architecturally but requires fewer changes.

## Next Steps

1. Research what makes something a "feature" in Spaces codebase
2. Determine if clusters should be a feature or a different construct
3. Decide between clean architecture (new ClustersFeature) vs minimal change
4. Implement chosen approach
5. Test with all four data sources (scores, distances, evaluations, similarities)
