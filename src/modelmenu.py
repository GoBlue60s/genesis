from __future__ import annotations

from typing import TYPE_CHECKING

from factor_analyzer import FactorAnalyzer
import numpy as np
import pandas as pd


from PySide6 import QtCore
from PySide6.QtWidgets import QDialog, QTableWidget, QTableWidgetItem
from scipy.spatial import procrustes

from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.decomposition import FactorAnalysis
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

from tabulate import tabulate

if TYPE_CHECKING:
	# from sklearn.decomposition import PCA, FactorAnalysis
	# from sklearn.preprocessing import StandardScaler
	from director import Status
	from common import Spaces

from constants import (
	DEFAULT_NUMBER_OF_CLUSTERS,
	# MAXIMUM_NUMBER_OF_DIMENSIONS_FOR_PLOTTING,
	MINIMAL_DIFFERENCE_FROM_ZERO,
)
from dialogs import ChoseOptionDialog, SetValueDialog
from exceptions import MissingInformationError, SpacesError
from features import EvaluationsFeature, SimilaritiesFeature, TargetFeature

# --------------------------------------------------------------------------


class ClusterCommand:
	"""The Cluster command - is not yet implemented"""

	def __init__(self, director: Status, common: Spaces) -> None:
		self._director = director
		self.common = common
		self._director.command = "Cluster"
		self.selection_title = "Select Data Source for Clustering"
		self.selection_message = \
			"Choose which data source to use for clustering"
		self.data_source_options = [
			"distances",
			"evaluations",
			"scores",
			"similarities"
		]
		self.selection_required_title = "Selection required"
		self.selection_required_message = (
			"A data source must be selected for clustering."
		)
		self.data_for_clustering = pd.DataFrame()
		self.number_clusters_title = "Cluster Analysis"
		self.number_clusters_message = "Number of clusters to extract:"
		self.number_clusters_min_allowed = 2

		self.number_clusters_integer = True
		self.number_clusters_default = 2

		return

	# ------------------------------------------------------------------------
		
	def execute(self, common: Spaces) -> None:  # noqa: ARG002
		
		self._director.record_command_as_selected_and_in_process()
		self._director.optionally_explain_what_command_does()
		# Ask user which data source to use
		(name_source, self.data_for_clustering) = \
			self.get_data_source_from_user()
		# Ask user for number of clusters
		self.number_clusters_max_allowed = \
			min(15, len(self.data_for_clustering) - 1)
		n_clusters = self.common.get_components_to_extract_from_user(
			self.number_clusters_title,
			self.number_clusters_message,
			self.number_clusters_min_allowed,
			self.number_clusters_max_allowed,
			self.number_clusters_integer,
			self.number_clusters_default
		)
		# peek(f"{n_clusters=}")
		# Perform k-means clustering on the selected data

		kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
		cluster_labels = kmeans.fit_predict(self.data_for_clustering)
		cluster_centers = kmeans.cluster_centers_
		# peek(f"{cluster_labels=}")
		# peek(f"{cluster_centers=}")

		# Store cluster results
		self._director.scores_active.cluster_labels = cluster_labels
		self._director.scores_active.cluster_centers = cluster_centers
		self._director.scores_active.n_clusters = n_clusters

		# Store original data for plotting when clustering scores
		if name_source == "scores":
			self._director.scores_active.original_clustered_data = \
				self.data_for_clustering.copy()

		# Set up scores DataFrame for plotting (using cluster centers)
		if cluster_centers.shape[1] >= 2:
			scores_df = pd.DataFrame(cluster_centers[:, :2],
									columns=["Dimension 1", "Dimension 2"])
			cluster_names = [f"Cluster {i+1}" for i in range(n_clusters)]
			scores_df.insert(0, "Item", cluster_names)

			self._director.scores_active.scores = scores_df
			self._director.scores_active.hor_axis_name = "Dimension 1"
			self._director.scores_active.vert_axis_name = "Dimension 2"
			dim_names = ["Dimension 1", "Dimension 2"]
			self._director.scores_active.dim_names = dim_names

		# Print cluster results table
		self._print_cluster_results(cluster_centers, n_clusters)

		# Set up display
		self._director.title_for_table_widget = \
			("K-Means Clustering Results using "
			f"{name_source.capitalize()} (k={n_clusters})")
		self._director.create_widgets_for_output_and_log_tabs()

		# Create cluster plot
		self._director.common.create_plot_for_tabs("clusters")
		self._director.record_command_as_successfully_completed()
		return

	# ------------------------------------------------------------------------
	
	def get_data_source_from_user(self) -> None:

		dialog = ChoseOptionDialog(
			self.selection_title,
			self.selection_message,
			self.data_source_options
		)
		if dialog.exec() == QDialog.Accepted:
			selected_source = \
				self.data_source_options[dialog.selected_option]
		else:
			raise SpacesError(
				self.selection_required_title, self.selection_required_message
			)
		
		# Check if the selected data source is available
		if selected_source == "distances":
			self.common.needs_distances("cluster")
			data_for_clustering = (
				self._director.configuration_active.distances_as_dataframe
			)
		elif selected_source == "evaluations":
			self.common.needs_evaluations("cluster")
			data_for_clustering = \
				self._director.evaluations_active.evaluations
		elif selected_source == "scores":
			self.common.needs_scores("cluster")
			scores_df = self._director.scores_active.scores
			# Remove index columns
			# (unnamed columns or columns that are just row numbers)
			data_for_clustering = scores_df.loc[
				:, ~scores_df.columns.str.contains('^Unnamed')]
		elif selected_source == "similarities":
			self.common.needs_similarities("cluster")
			data_for_clustering = \
				self._director.similarities_active.similarities
			
		return selected_source, data_for_clustering
	
	# ------------------------------------------------------------------------


	def _find_optimal_clusters(self, data: pd.DataFrame) -> int:
		"""Find optimal number of clusters using elbow method and
		silhouette analysis"""



		# Test cluster counts from 2 to min(15, n_samples-1) for
		# case clustering
		max_k = min(15, len(data) - 1)
		if max_k < DEFAULT_NUMBER_OF_CLUSTERS:
			# Not enough data points to form multiple clusters
			return DEFAULT_NUMBER_OF_CLUSTERS
			
		k_range = range(2, max_k + 1)
		inertias = []
		silhouette_scores = []
		
		for k in k_range:
			kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
			cluster_labels = kmeans.fit_predict(data)
			inertias.append(kmeans.inertia_)
			
			# Calculate silhouette score
			sil_score = silhouette_score(data, cluster_labels)
			silhouette_scores.append(sil_score)
		
		# Find optimal k using elbow method (look for biggest
		#  decrease in inertia)
		if len(inertias) >= 2:
			# Calculate the rate of decrease in inertia
			decreases = [inertias[i] - inertias[i+1]\
				for i in range(len(inertias)-1)]
			# Find the elbow point (where decrease starts to level off)
			elbow_k = k_range[decreases.index(max(decreases))]
		else:
			elbow_k = 2
			
		# Find k with highest silhouette score
		best_sil_k = k_range[silhouette_scores.index(max(silhouette_scores))]
		
		# Choose the smaller of the two (more conservative clustering)
		optimal_k = min(elbow_k, best_sil_k)
		
		print(f"Cluster analysis: elbow method suggests k={elbow_k}, "
			f"silhouette analysis suggests k={best_sil_k}, "
			f"using k={optimal_k}")
		
		return optimal_k

	# ------------------------------------------------------------------------

	def _calculate_reference_point_proximity(
		self, cluster_centers: np.ndarray, n_clusters: int  # noqa: ARG002
	) -> tuple[list[str], list[list[str]]]:
		"""Calculate percentage closer to each reference point"""
		if not self._director.common.have_reference_points():
			return [], []

		rivalry = self._director.rivalry
		point_coords = self._director.configuration_active.point_coords
		point_names = self._director.configuration_active.point_names

		# Get reference point coordinates and names
		rival_a_coords = np.array([
			point_coords.iloc[rivalry.rival_a.index, 0],
			point_coords.iloc[rivalry.rival_a.index, 1]
		])
		rival_b_coords = np.array([
			point_coords.iloc[rivalry.rival_b.index, 0],
			point_coords.iloc[rivalry.rival_b.index, 1]
		])
		rival_a_name = point_names[rivalry.rival_a.index]
		rival_b_name = point_names[rivalry.rival_b.index]

		# Create column headers
		ref_headers = [
			f"Closer to {rival_a_name}", f"Closer to {rival_b_name}"
		]

		# Calculate percentages for each cluster
		cluster_labels = self._director.scores_active.cluster_labels
		ref_percentages = []

		for i in range(n_clusters):
			# Get all points in this cluster
			cluster_mask = cluster_labels == i
			cluster_point_coords = (
				self.data_for_clustering[cluster_mask].to_numpy()
			)

			# Calculate distances to each reference point for
			#  all points in cluster
			distances_to_a = np.linalg.norm(
				cluster_point_coords - rival_a_coords, axis=1
			)
			distances_to_b = np.linalg.norm(
				cluster_point_coords - rival_b_coords, axis=1
			)

			# Count how many are closer to each reference point
			closer_to_a = np.sum(distances_to_a < distances_to_b)
			closer_to_b = np.sum(distances_to_b < distances_to_a)
			total_in_cluster = len(cluster_point_coords)

			# Calculate percentages
			percent_closer_to_a = (
				(closer_to_a / total_in_cluster) * 100
				if total_in_cluster > 0 else 0
			)
			percent_closer_to_b = (
				(closer_to_b / total_in_cluster) * 100
				if total_in_cluster > 0 else 0
			)

			ref_percentages.append([
				f"{percent_closer_to_a:.1f}%", f"{percent_closer_to_b:.1f}%"
			])

		return ref_headers, ref_percentages

	# ------------------------------------------------------------------------

	def _print_cluster_results(
		self, cluster_centers: np.ndarray, n_clusters: int
	) -> None:
		"""Print cluster results table to console"""
		# Get column names for headers
		all_columns = self.data_for_clustering.columns.tolist()
		column_names = [col for col in all_columns
						if not (str(col).isdigit()
								or str(col).startswith('Unnamed'))]

		# Define colors
		colors = ['red', 'blue', 'green', 'orange', 'purple', 'brown', 'pink',
				'gray', 'olive', 'cyan']

		# Calculate cluster counts and percentages
		cluster_labels = self._director.scores_active.cluster_labels
		total_points = len(cluster_labels)
		cluster_counts = np.bincount(cluster_labels)

		# Get reference point proximity data if available
		ref_headers, ref_percentages = \
			self._calculate_reference_point_proximity(
			cluster_centers, n_clusters
		)

		# Create table data
		headers = ["Cluster", "Color", "Percent", *column_names, *ref_headers]
		table_data = []

		for i in range(n_clusters):
			count = cluster_counts[i]
			percent = (count / total_points) * 100
			row = [str(i+1), colors[i % len(colors)], f"{percent:.1f}%"]
			# Format coordinates without parentheses, fixed format
			for coord in cluster_centers[i]:
				row.append(f"{coord:.3f}")
			# Add reference point proximity percentages if available
			if ref_percentages:
				row.extend(ref_percentages[i])
			table_data.append(row)

		# Print table using tabulate
		print("\nK-Means Clustering Results")
		print(tabulate(table_data, headers=headers))

	# ------------------------------------------------------------------------

	def _display(self) -> QTableWidget:
		"""Create and return the cluster results table widget for display"""
		# Create cluster results DataFrame for display
		cluster_centers = self._director.scores_active.cluster_centers
		n_clusters = self._director.scores_active.n_clusters

		# Get column names, excluding any that look like indices
		all_columns = self.data_for_clustering.columns.tolist()
		# Filter out numeric-only column names (likely indices)
		#  and unnamed columns
		column_names = [col for col in all_columns
						if not (str(col).isdigit()
								or str(col).startswith('Unnamed'))]

		# Create DataFrame with cluster centers including cluster
		# names and colors
		colors = ['red', 'blue', 'green', 'orange', 'purple', 'brown', 'pink',
				'gray', 'olive', 'cyan']

		# Calculate cluster counts and percentages
		cluster_labels = self._director.scores_active.cluster_labels
		total_points = len(cluster_labels)
		cluster_counts = np.bincount(cluster_labels)

		# Get reference point proximity data if available
		ref_headers, ref_percentages = \
			self._calculate_reference_point_proximity(
			cluster_centers, n_clusters
		)

		# Build the data with cluster numbers, colors, percentages,
		# and coordinates
		cluster_data = []
		for i in range(n_clusters):
			count = cluster_counts[i]
			percent = (count / total_points) * 100
			row = (
				[i+1, colors[i % len(colors)], f"{percent:.1f}%"]
				+ cluster_centers[i].tolist()
			)
			# Add reference point proximity percentages if available
			if ref_percentages:
				row.extend(ref_percentages[i])
			cluster_data.append(row)

		# Create DataFrame with all columns
		all_columns = [
			"Cluster", "Color", "Percent", *column_names, *ref_headers
		]
		cluster_df = pd.DataFrame(cluster_data, columns=all_columns)

		# Store the cluster data for the statistical table widget
		self._director.cluster_results = cluster_df

		gui_output_as_widget = self._director.statistics.display_table(
			"cluster_results"
		)

		self._director.output_widget_type = "Table"
		return gui_output_as_widget

	# ------------------------------------------------------------------------



class DirectionsCommand:
	def __init__(self, director: Status, common: Spaces) -> None:
		self._director = director
		self.common = common
		self._director.command = "Directions"
		self._width = 8
		self._decimals = 2

		self.npoint = self._director.configuration_active.npoint
		# still needed
		self.point_coords = self._director.configuration_active.point_coords
		self.point_labels = self._director.configuration_active.point_labels
		self.range_points = self._director.configuration_active.range_points
		self._hor_dim = self._director.common.hor_dim
		self._vert_dim = self._director.common.vert_dim
		self.ndim = self._director.configuration_active.ndim  # still needed
		self.dim_names = self._director.configuration_active.dim_names

		self.offset = self._director.common.plot_ranges.offset
		return

	# ------------------------------------------------------------------------

	def execute(self, common: Spaces) -> None:  # noqa: ARG002
		self._director.record_command_as_selected_and_in_process()
		self._director.optionally_explain_what_command_does()
		self._director.dependency_checker.detect_dependency_problems()
		self._calculate_point_directions()
		# self._director.configuration_active.print_active_function()
		self._print_directions_df()
		self._director.common.create_plot_for_tabs("directions")
		ndim = self._director.configuration_active.ndim
		npoint = self._director.configuration_active.npoint
		self._director.title_for_table_widget = (
			f"Directions are based on the active configuration"
			f" which has {ndim} dimensions and "
			f"{npoint} points"
		)
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.record_command_as_successfully_completed()
		return

	# ------------------------------------------------------------------------

	def _print_directions_df(self) -> None:
		"""Print the directions DataFrame to the output tab"""
		directions_df = self._director.configuration_active.directions_df
		directions_df.rename(
			columns={
				"Slope": "Slope",
				"Unit_Circle_x": "Unit Circle \n X",
				"Unit_Circle_y": "Unit Circle \n Y",
				"Angle_Degrees": "Angle in \n Degrees",
				"Angle_Radians": "Angle in \n Radians",
				"Quadrant": "Quadrant",
			},
			inplace=True,
		)

		table = tabulate(
			directions_df,
			headers="keys",
			tablefmt="plain",
			showindex=True,
			floatfmt=[".2f", ".2f", ".2f", ".2f", ".2f", ".2f", ".0f"],
		)

		print(f"{table}")

		return

	# ------------------------------------------------------------------------

	def _calculate_point_directions(self) -> pd.DataFrame:
		"""Calculate direction information for each point including slope,
		unit circle coordinates, and angles"""

		point_coords = self._director.configuration_active.point_coords
		point_names = self._director.configuration_active.point_names

		# Initialize lists to store direction information
		slopes = []
		unit_circle_x = []
		unit_circle_y = []
		angles_degrees = []
		angles_radians = []
		quadrants = []

		for i in range(len(point_coords)):
			x = point_coords.iloc[i, 0]
			y = point_coords.iloc[i, 1]

			# Calculate the angle from the origin
			angle_radians = np.arctan2(y, x)
			angle_degrees_val = np.degrees(angle_radians)

			# Ensure angle is in [0, 360) range
			if angle_degrees_val < 0:
				angle_degrees_val += 360

			# Calculate coordinates on unit circle using the angle
			# These will always be at distance 1 from origin
			unit_x = np.cos(angle_radians)
			unit_y = np.sin(angle_radians)

			# Calculate slope (dimension 2 / dimension 1)
			if abs(x) < MINIMAL_DIFFERENCE_FROM_ZERO:
				slope = float("inf") if y >= 0 else float("-inf")
			else:
				slope = y / x

			# Determine quadrant based on unit circle coordinates
			if unit_x >= 0 and unit_y >= 0:
				quadrant = 1
			elif unit_x < 0 and unit_y >= 0:
				quadrant = 2
			elif unit_x < 0 and unit_y < 0:
				quadrant = 3
			else:  # unit_x >= 0 and unit_y < 0
				quadrant = 4

			# Special case for origin point
			if (
				abs(x) < MINIMAL_DIFFERENCE_FROM_ZERO
				and abs(y) < MINIMAL_DIFFERENCE_FROM_ZERO
			):
				unit_x = 0
				unit_y = 0
				quadrant = 0
				angle_degrees_val = 0
				angle_radians = 0
				slope = 0

			# Append values to lists
			slopes.append(slope)
			unit_circle_x.append(unit_x)
			unit_circle_y.append(unit_y)
			angles_degrees.append(angle_degrees_val)
			angles_radians.append(angle_radians)
			quadrants.append(quadrant)

		# Create DataFrame with all direction information
		# Note: Quadrant is placed last as requested
		directions_df = pd.DataFrame(
			{
				"Slope": slopes,
				"Unit_Circle_x": unit_circle_x,
				"Unit_Circle_y": unit_circle_y,
				"Angle_Degrees": angles_degrees,
				"Angle_Radians": angles_radians,
				"Quadrant": quadrants,
			},
			index=point_names,
		)

		self._director.configuration_active.directions_df = directions_df

		return directions_df

	# ------------------------------------------------------------------------


class FactorAnalysisCommand:
	"""The Factor command calculates latent variables to explain the
	variation in evaluations.
	"""

	def __init__(self, director: Status, common: Spaces) -> None:
		self._director = director
		self.common = common
		self._director.command = "Factor analysis"

		self._director.scores_active.factor_scores = pd.DataFrame()
		self._director.scores_active.score_1_name = ""
		self._director.scores_active.score_2_name = ""

		self._title = "Factor analysis"
		self._label = "Number of factors to extract:"
		self._min_allowed = 1
		self._max_allowed = self._director.evaluations_active.nreferent
		self._an_integer = True
		self._default = 2

		return

	# ------------------------------------------------------------------------

	def execute(self, common: Spaces) -> None:
		director = self._director
		common = self.common

		configuration_active = director.configuration_active
		director.record_command_as_selected_and_in_process()
		director.optionally_explain_what_command_does()
		director.dependency_checker.detect_dependency_problems()
		ext_fact = common.get_components_to_extract_from_user(
			self._title,
			self._label,
			self._min_allowed,
			self._max_allowed,
			self._an_integer,
			self._default,
		)
		configuration_active.ndim = int(ext_fact)
		self._factors_and_scores()
		self._director.common.create_plot_for_tabs("scree")
		self._create_factor_analysis_table()
		self._print_factor_analysis_results()
		self._fill_configuration()
		director.title_for_table_widget = "Factor analysis"
		director.create_widgets_for_output_and_log_tabs()
		director.record_command_as_successfully_completed()
		return

	# ------------------------------------------------------------------------

	def _factors_and_scores(self) -> None:
		ndim = self._director.configuration_active.ndim
		nreferent = self._director.evaluations_active.nreferent
		evaluations = self._director.evaluations_active.evaluations
		item_names = self._director.evaluations_active.item_names

		fa = self._perform_factor_analysis(ndim, evaluations)

		(dim_names, _dim_labels, range_dims, range_items,
			range_points) = self._generate_dimension_data(ndim, nreferent)

		(loadings, point_coords, eigen, eigen_common, commonalities,
			factor_variance, uniquenesses, scores, score_1,
			score_2) = self._extract_factor_results(
			fa, dim_names, item_names, evaluations
		)

		self._setup_configuration_attributes(
			range_dims, point_coords, dim_names, eigen, eigen_common,
			commonalities, factor_variance, uniquenesses, range_items,
			range_points, fa, loadings
		)

		self._setup_scores_attributes(scores, score_1, score_2)

		return

	# ------------------------------------------------------------------------

	def _perform_factor_analysis(
		self, ndim: int, evaluations: pd.DataFrame
	) -> FactorAnalyzer:
		"""Perform the factor analysis using FactorAnalyzer."""
		fa = FactorAnalyzer(
			n_factors=ndim, rotation="varimax", is_corr_matrix=False
		)
		fa.fit(evaluations)
		return fa

	# ------------------------------------------------------------------------

	def _generate_dimension_data(
		self, ndim: int, nreferent: int
	) -> tuple[list[str], list[str], range, range, range]:
		"""Generate dimension names, labels, and ranges."""
		dim_names = []
		dim_labels = []
		range_dims = range(ndim)

		for each_dim in range_dims:
			dim_names.append("Factor " + str(each_dim + 1))
			dim_labels.append("FA" + str(each_dim + 1))

		range_items = range(nreferent)
		range_points = range(nreferent)

		return dim_names, dim_labels, range_dims, range_items, range_points

	# ------------------------------------------------------------------------

	def _extract_factor_results(
		self, fa: FactorAnalyzer, dim_names: list[str], item_names: list[str],
		evaluations: pd.DataFrame
	) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame,
		pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame,
		pd.DataFrame, pd.DataFrame]:
		"""Extract all results from the factor analysis."""
		the_loadings = fa.loadings_
		loadings = pd.DataFrame(
			the_loadings, columns=dim_names, index=item_names
		)
		point_coords = pd.DataFrame(
			loadings, columns=dim_names, index=item_names
		)

		ev, v = fa.get_eigenvalues()
		eigen = pd.DataFrame(data=ev, columns=["Eigenvalue"])
		eigen_common = pd.DataFrame(data=v, columns=["Eigenvalue"])

		get_commonalities = fa.get_communalities()
		commonalities = pd.DataFrame(
			data=get_commonalities, columns=["Commonality"], index=item_names
		)

		factor_variance = pd.DataFrame(
			fa.get_factor_variance(),
			columns=dim_names,
			index=["Variance", "Proportional", "Cumulative"],
		)

		uniquenesses = pd.DataFrame(
			fa.get_uniquenesses(), columns=["Uniqueness"], index=item_names
		)

		scores = pd.DataFrame(fa.transform(evaluations), columns=dim_names)
		scores.reset_index(inplace=True)
		scores.rename(columns={"index": "Resp no"}, inplace=True)

		score_1_name = "Factor 1"
		score_2_name = "Factor 2"
		score_1 = scores[score_1_name]
		score_2 = scores[score_2_name]

		return (loadings, point_coords, eigen, eigen_common, commonalities,
			factor_variance, uniquenesses, scores, score_1, score_2)

	# ------------------------------------------------------------------------

	def _setup_configuration_attributes( # noqa: PLR0913
		self, range_dims: range, point_coords: pd.DataFrame,
		dim_names: list[str], eigen: pd.DataFrame,
		eigen_common: pd.DataFrame, commonalities: pd.DataFrame,
		factor_variance: pd.DataFrame, uniquenesses: pd.DataFrame,
		range_items: range, range_points: range, fa: FactorAnalyzer,
		loadings: pd.DataFrame
	) -> None:
		"""Set up all configuration_active attributes."""
		configuration_active = self._director.configuration_active
		evaluations_active = self._director.evaluations_active

		configuration_active.range_dims = range_dims
		configuration_active.point_coords = point_coords
		configuration_active.dim_names = dim_names
		configuration_active.eigen = eigen
		configuration_active.eigen_common = eigen_common
		configuration_active.commonalities = commonalities
		configuration_active.factor_variance = factor_variance
		configuration_active.uniquenesses = uniquenesses
		configuration_active.range_items = range_items
		configuration_active.range_points = range_points
		configuration_active.fa = fa
		configuration_active.loadings = loadings

		configuration_active.npoint = evaluations_active.nreferent
		configuration_active.nreferent = evaluations_active.nreferent
		configuration_active.point_names = evaluations_active.item_names
		configuration_active.point_labels = evaluations_active.item_labels
		configuration_active.range_points = evaluations_active.range_items
		configuration_active.inter_point_distances()

	# ------------------------------------------------------------------------

	def _setup_scores_attributes(
		self, scores: pd.DataFrame, score_1: pd.DataFrame,
		score_2: pd.DataFrame
	) -> None:
		"""Set up all scores_active attributes."""
		scores_active = self._director.scores_active
		configuration_active = self._director.configuration_active
		evaluations_active = self._director.evaluations_active

		score_1_name = "Factor 1"
		score_2_name = "Factor 2"

		scores_active.scores = scores
		scores_active.score_1 = score_1
		scores_active.score_2 = score_2
		scores_active.nscores = configuration_active.ndim
		scores_active.nscored_individ = evaluations_active.nevaluators
		scores_active.nscored_items = configuration_active.npoint
		scores_active.dim_names = configuration_active.dim_names
		scores_active.dim_labels = configuration_active.dim_labels
		scores_active.score_1_name = score_1_name
		scores_active.score_2_name = score_2_name
		scores_active.hor_axis_name = score_1_name
		scores_active.vert_axis_name = score_2_name

	# ------------------------------------------------------------------------

	def _fill_configuration(self) -> None:
		self._director.configuration_active.nreferent = (
			self._director.evaluations_active.nreferent
		)

		return

	# ------------------------------------------------------------------------


	def _print_factor_analysis_results(self) -> None:
		loadings = self._director.configuration_active.loadings
		point_coords = self._director.configuration_active.point_coords
		eigen = self._director.configuration_active.eigen
		eigen_common = self._director.configuration_active.eigen_common
		commonalities = self._director.configuration_active.commonalities
		factor_variance = self._director.configuration_active.factor_variance
		uniquenesses = self._director.configuration_active.uniquenesses
		scores = self._director.scores_active.scores

		print("\nLoadings: \n", loadings)
		print("\nPoint_coords: \n", point_coords)
		print("\nEigenvalues: \n", eigen)
		print("\nCommon Factor Eigenvalues: \n", eigen_common)
		print("\nCommonalities: \n", commonalities)
		print("\nFactor Variance:")
		print("\n\tNote: Variance is sum of squared loadings \n")
		print(factor_variance)
		print("\nUniquenesses: \n")
		print(uniquenesses)
		print("\nFactor Scores: \n")
		print(scores)
		return

	# ------------------------------------------------------------------------

	def _create_factor_analysis_table(self) -> pd.DataFrame:
		"""Create a DataFrame containing factor analysis results
		with all relevant columns.

		Returns:
			pd.DataFrame: Combined DataFrame with eigenvalues,
			common factor eigenvalues, communalities, uniquenesses,
			item names, and factor loadings.
		"""
		source = self._director.configuration_active
		item_names = source.point_names
		nreferent = len(item_names)

		# Get all required data components
		eigenvalues = source.eigen["Eigenvalue"].to_numpy()
		common_eigenvalues = source.eigen_common["Eigenvalue"].to_numpy()
		commonalities = source.commonalities["Commonality"].to_numpy()
		uniquenesses = source.uniquenesses["Uniqueness"].to_numpy()
		loadings_factor1 = source.loadings.iloc[:, 0].to_numpy()
		loadings_factor2 = (
			source.loadings.iloc[:, 1].to_numpy()
			if source.ndim > 1
			else [0] * nreferent
		)

		# Create DataFrame with all columns
		factor_analysis_df = pd.DataFrame(
			{
				"Eigenvalues": eigenvalues[:nreferent],
				"Common Factor\nEigenvalues": common_eigenvalues[:nreferent],
				"Commonalities": commonalities,
				"Uniquenesses": uniquenesses,
				"Item": item_names,
				"Loadings\nFactor 1": loadings_factor1,
				"Loadings\nFactor 2": loadings_factor2,
			}
		)

		self._director.configuration_active.factor_analysis_df = (
			factor_analysis_df
		)

		return factor_analysis_df

	# ------------------------------------------------------------------------


class FactorAnalysisMachineLearningCommand:
	def __init__(self, director: Status, common: Spaces) -> None:
		"""The Factor command calculates latent variables to explain the
		variation in evaluations.
		"""
		self._director = director
		self.command = common
		self._director.command = "Factor analysis machine learning"

		self._director.evaluations_active.item_labels = []
		self._director.evaluations_active.range_items = range(
			self._director.evaluations_active.nitem
		)
		self._get_ncomponents_title = "Factor Analysis"
		self._get_ncomponents_label = "Number of factors to extract:"
		self._get_ncomponents_default = 2
		self._get_ncomponents_min_allowed = 1
		self._transformer_method = "randomized"
		self._transformer_rotation = "varimax"
		self._factor_name_stem = "Factor "
		self._factor_label_stem = "FA"
		self._factor_1_name = "Factor 1"
		self._factor_2_name = "Factor 2"
		self._factor_1_label = "FA1"
		self._factor_2_label = "FA2"
		self._factoranalysis0_name = "factoranalysis0"
		self._factoranalysis1_name = "factoranalysis1"
		return

	# ------------------------------------------------------------------------

	def execute(self, common: Spaces) -> None:  # noqa: ARG002
		self._director.record_command_as_selected_and_in_process()
		self._director.optionally_explain_what_command_does()
		self._director.dependency_checker.detect_dependency_problems()
		n_components = self._get_components_from_user()
		self._perform_factor_analysis_m_l_and_setup(n_components)
		self._director.common.create_plot_for_tabs("scree")
		self._display()
		self._director.title_for_table_widget = \
			"Factor analysis (Machine Learning)"
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.set_focus_on_tab("Plot")
		self._director.record_command_as_successfully_completed()
		return

	# ------------------------------------------------------------------------

	def _get_components_from_user(self) -> int:
		"""Get number of components to extract from user."""
		nreferent = self._director.evaluations_active.nreferent
		return self.command.get_components_to_extract_from_user(
			title=self._get_ncomponents_title,
			label=self._get_ncomponents_label,
			min_allowed=self._get_ncomponents_min_allowed,
			max_allowed=nreferent - 1,
			an_integer=True,
			default=self._get_ncomponents_default,
		)

	# ------------------------------------------------------------------------

	def _perform_factor_analysis_m_l_and_setup(self, n_components: int) \
		-> None:
		"""Perform factor analysis and set up all configuration and scores."""


		evaluations = self._director.evaluations_active.evaluations
		item_names = self._director.evaluations_active.item_names
		nreferent = self._director.evaluations_active.nreferent

		X = evaluations  # noqa: N806
		scaler = StandardScaler()
		scaler.fit(X)
		scaler.transform(X)

		transformer = FactorAnalysis(
			n_components=n_components,
			svd_method=self._transformer_method,
			copy=True,
			rotation=self._transformer_rotation,
			random_state=0,
		)
		X_transformed = transformer.fit_transform(X)  # noqa: N806

		self._setup_pandas_display_options()

		components = pd.DataFrame(
			transformer.components_,
			index=transformer.get_feature_names_out(),
			columns=item_names,
		)

		x_trans = pd.DataFrame(
			X_transformed, columns=transformer.get_feature_names_out()
		)

		covar = pd.DataFrame(
			transformer.get_covariance(), columns=item_names, index=item_names
		)

		x_new = pd.DataFrame(
			transformer.transform(X),
			columns=transformer.get_feature_names_out(),
		)

		transpose = components.transpose()
		trans = pd.DataFrame(transpose)

		self._setup_dimension_and_item_data(trans)
		self._setup_configuration_from_factor_analysis_m_l(
			trans, x_new, covar
		)
		self._setup_scores_from_factor_analysis_m_l()
		self._store_sklearn_results_for_display(
			transformer, X, item_names, nreferent
		)
		self._print_factor_analysis_m_l_results(
			scaler, X, transformer, X_transformed, x_trans, covar, trans,
			nreferent
		)

	# ------------------------------------------------------------------------

	def _setup_pandas_display_options(self) -> None:
		"""Set pandas display options for better output formatting."""
		pd.set_option("display.max_columns", None)
		pd.set_option("display.precision", 2)
		pd.set_option("display.max_colwidth", 300)

	# ------------------------------------------------------------------------

	def _setup_dimension_and_item_data(self, trans: pd.DataFrame) -> None:
		"""Set up dimension and item data from factor analysis results."""
		ndim = len(trans.columns)
		nitem = len(trans.index)
		range_dims = range(ndim)
		range_items = range(nitem)

		dim_names = []
		dim_labels = []
		for each_dim in range_dims:
			dim_names.append(self._factor_name_stem + str(each_dim))
			dim_labels.append(self._factor_label_stem + str(each_dim))

		for each_point in range_items:
			self._director.evaluations_active.item_labels.append(
				self._director.evaluations_active.item_names[each_point][0:4]
			)

		self._director.configuration_active.ndim = ndim
		self._director.configuration_active.range_dims = range_dims
		self._director.evaluations_active.nitem = nitem
		self._director.evaluations_active.range_items = range_items

		# Store for later use
		self._dim_names = dim_names
		self._dim_labels = dim_labels

	# ------------------------------------------------------------------------

	def _setup_configuration_from_factor_analysis_m_l(
		self, trans: pd.DataFrame, x_new: pd.DataFrame, covar: pd.DataFrame
	) -> None:
		"""Set up configuration from factor analysis results."""


		director = self._director
		common = director.common
		configuration_active = director.configuration_active
		evaluations_active = director.evaluations_active
		matplotlib_plotter = director.matplotlib_plotter

		common.show_bisector = False
		common.show_connector = False
		configuration_active.distances.clear()

		scaler2 = StandardScaler()
		scaler2.fit(trans)
		new_trans = scaler2.transform(trans)
		configuration_active.point_coords = pd.DataFrame(
			new_trans
		)

		configuration_active.point_coords.columns = [
			self._factor_1_name,
			self._factor_2_name,
		]
		configuration_active.dim_names = [
			self._factor_1_name,
			self._factor_2_name,
		]
		
		configuration_active.dim_labels = [
			self._factor_1_label,
			self._factor_2_label,
		]

		configuration_active.inter_point_distances()
		common.set_axis_extremes_based_on_coordinates(
			configuration_active.point_coords
		)

		configuration_active.range_points = evaluations_active.range_items
		configuration_active.point_names = evaluations_active.item_names
		configuration_active.point_labels = evaluations_active.item_labels
		configuration_active.scores = x_new
		configuration_active.scores.reset_index(inplace=True)
		configuration_active.scores.rename(
			columns={"index": "Resp no"}, inplace=True
		)
		configuration_active.covar = covar

		if configuration_active.ndim > 1:
			matplotlib_plotter.\
				request_configuration_plot_for_tabs_using_matplotlib()

	# ------------------------------------------------------------------------

	def _setup_scores_from_factor_analysis_m_l(self) -> None:
		"""Set up scores from factor analysis results."""
		self._director.scores_active.scores = (
			self._director.configuration_active.scores
		)
		self._director.scores_active.nscores = (
			self._director.configuration_active.ndim
		)
		self._director.scores_active.range_scores = range(
			self._director.configuration_active.ndim
		)
		self._director.scores_active.nscored_individ = (
			self._director.evaluations_active.nevaluators
		)
		self._director.scores_active.nscored_items = (
			self._director.evaluations_active.nitem
		)
		self._director.scores_active.dim_names = (
			self._director.configuration_active.dim_names
		)
		self._director.scores_active.dim_labels = (
			self._director.configuration_active.dim_labels
		)

		self._director.scores_active.score_1 = (
			self._director.scores_active.scores[self._factoranalysis0_name]
		)
		self._director.scores_active.score_2 = (
			self._director.scores_active.scores[self._factoranalysis1_name]
		)
		self._director.scores_active.scores = (
			self._director.scores_active.scores.rename(
				columns={
					self._factoranalysis0_name: self._factor_1_name,
					self._factoranalysis1_name: self._factor_2_name,
				}
			)
		)

		self._director.scores_active.score_1_name = self._factor_1_name
		self._director.scores_active.score_2_name = self._factor_2_name
		self._director.scores_active.summarize_scores()

		self._director.common.set_axis_extremes_based_on_coordinates(
			self._director.scores_active.scores.iloc[:, 1:]
		)

		self._director.configuration_active.score_1_name = self._factor_1_name
		self._director.configuration_active.score_2_name = self._factor_2_name
		self._director.scores_active.hor_axis_name = self._factor_1_name
		self._director.scores_active.vert_axis_name = self._factor_2_name
		self._director.scores_active.ndim = \
			self._director.configuration_active.ndim

	# ------------------------------------------------------------------------

	def _store_sklearn_results_for_display(
		self, transformer: object, X: pd.DataFrame, # noqa: N803
		item_names: list[str], nreferent: int
	) -> None:
		"""Store sklearn results in format expected by table widget."""
		ndim = self._director.configuration_active.ndim
		range_dims = range(ndim)

		self._director.configuration_active.x_new = pd.DataFrame(
			transformer.transform(X),
			columns=transformer.get_feature_names_out(),
		)
		self._director.configuration_active.ndim = ndim
		self._director.configuration_active.range_dims = range_dims

		correlation_matrix = np.corrcoef(X.T)
		eigenvalues, _ = np.linalg.eigh(correlation_matrix)
		eigenvalues = np.sort(eigenvalues)[::-1]

		self._director.configuration_active.eigen = pd.DataFrame(
			eigenvalues[:nreferent], columns=["Eigenvalue"]
		)

		explained_variance = np.var(transformer.components_, axis=1)
		self._director.configuration_active.eigen_common = pd.DataFrame(
			explained_variance, columns=["Eigenvalue"]
		)

		loadings_matrix = transformer.components_.T
		pseudo_communalities = np.sum(loadings_matrix**2, axis=1)
		self._director.configuration_active.commonalities = pd.DataFrame(
			pseudo_communalities, columns=["Commonality"], index=item_names
		)

		pseudo_uniquenesses = 1 - pseudo_communalities
		self._director.configuration_active.uniquenesses = pd.DataFrame(
			pseudo_uniquenesses, columns=["Uniqueness"], index=item_names
		)

		self._director.configuration_active.loadings = pd.DataFrame(
			loadings_matrix,
			columns=[f"Factor {i+1}" for i in range(transformer.n_components)],
			index=item_names
		)

		self._director.configuration_active.\
			transformer_mean = transformer.mean_
		self._director.configuration_active.\
			transformer_noise_variance = transformer.noise_variance_

		self._director.configuration_active.nreferent = nreferent
		self._director.configuration_active.dim_names = self._dim_names
		self._director.configuration_active.dim_labels = self._dim_labels

	# ------------------------------------------------------------------------

	def _print_factor_analysis_m_l_results(
		self, scaler: object, X: pd.DataFrame, transformer: object, # noqa: N803
		X_transformed: pd.DataFrame, x_trans: pd.DataFrame, # noqa: N803
		covar: pd.DataFrame, trans: pd.DataFrame, nreferent: int
	) -> None:
		"""Print factor analysis results using existing helper method."""

		scaler2_data = self._director.configuration_active.point_coords
		new_trans = scaler2_data.to_numpy()

		correlation_matrix = np.corrcoef(X.T)
		eigenvalues, _ = np.linalg.eigh(correlation_matrix)
		eigenvalues = np.sort(eigenvalues)[::-1]

		# Create scaler2 for the debug printing function
		scaler2 = StandardScaler()

		self._print_factor_analysis_m_l(
			scaler, X, transformer, X_transformed, x_trans, covar, trans,
			scaler2, new_trans, eigenvalues, nreferent
		)

	# ------------------------------------------------------------------------

	# def _fill_configuration(self) -> None:
	# 	self._director.configuration_active.nreferent = (
	# 		self._director.evaluations_active.nreferent
	# 	)

	# 	return

	# ------------------------------------------------------------------------

	def _print_factor_analysis_m_l( # noqa: PLR0913
		self,
		scaler: StandardScaler,
		X: np.ndarray, # noqa: N803
		transformer: FactorAnalysis,
		X_transformed: np.ndarray, # noqa: N803
		x_trans: pd.DataFrame,
		covar: pd.DataFrame,
		trans: pd.DataFrame,
		scaler2: StandardScaler,
		new_trans: np.ndarray,
		eigenvalues: np.ndarray,
		nreferent: int
	) -> None:
		"""Print all Factor Analysis Machine Learning debug and
		output information."""

		print("\n\nscaler: \n", scaler)
		print("\nScaler.fit(X): \n", scaler.fit(X))
		print("\nStandardScaler(): \n", StandardScaler())
		print("\nscaler.mean_: \n", scaler.mean_)
		print("\nScaler.transform(X): ", scaler.transform(X))
		print("\n\tTransformer: ", transformer)
		print("\nX_transformed.shape: ", X_transformed.shape)
		print("\nX_Trans: \n", x_trans)
		print("\ntransformer.get_params(): \n", transformer.get_params())
		print(
			"\ntransformer.get_feature_names_out(): ",
			transformer.get_feature_names_out(),
		)
		print("\nCovariance: \n", covar)
		print("\nPrecision: ", transformer.get_precision())
		print("\nScore: \n", transformer.score(X))
		print("\nScore_samples: \n", transformer.score_samples(X))
		print("\n\tComponents_: \n", transformer.components_)
		print("\n\tn_features_in_: ", transformer.n_features_in_)
		print("\n\tnoise_variance_: \n", transformer.noise_variance_)
		print("\n\tmean_: \n", transformer.mean_)
		x_new = pd.DataFrame(
			transformer.transform(X),
			columns=transformer.get_feature_names_out(),
		)
		print("\nX_new: \n", x_new)
		print("\nTranspose: \n", trans)
		print("\n\nscaler2: \n", scaler2)
		print("\nScaler2.fit(X): \n", scaler2.fit(trans))
		print("\nStandardScaler(): \n", StandardScaler())
		print("\nscaler2.mean_: \n", scaler2.mean_)
		print("\nnew_trans: ", new_trans)
		print(
			"\nPoint_coords: \n",
			self._director.configuration_active.point_coords,
		)
		print("\nEigenvalues:")
		for i, eigenvalue in enumerate(eigenvalues[:nreferent]):
			print(f"  Component {i+1}: {eigenvalue:.4f}")

		return

	# ------------------------------------------------------------------------

	def _display(self) -> QTableWidget:
		#
		gui_output_as_widget = (
			self._create_table_widget_for_factor_machine_learning()
		)
		#
		self._director.set_column_and_row_headers(
			gui_output_as_widget,
			[
				"Eigenvalues",
				"Feature\nMeans",
				"Noise\nVariance",
				"Item",
				"Components\nFactor 1",
				"Components\nFactor 2",
			],
			[],
		)
		#
		self._director.resize_and_set_table_size(gui_output_as_widget, 20)
		#
		self._director.output_widget_type = "Table"
		return gui_output_as_widget

	# ------------------------------------------------------------------------

	def _create_table_widget_for_factor_machine_learning(self) -> QTableWidget:
		"""Create a QTableWidget to display factor analysis results
		from the machine learning approach.

		Returns:
			QTableWidget: Table widget populated with factor analysis data.
		"""
		# Define number of columns
		# Eigenvalues, Mean, Noise Variance, Item, Factor 1, Factor 2
		ncols = 6
		table_widget = QTableWidget(
			self._director.evaluations_active.nreferent, ncols
		)
		
		# Get the transformer from the execute method context (stored earlier)
		# Access eigenvalues, mean_, noise_variance_, item_names, and loadings
		eigenvalues = self._director.configuration_active.eigen[
			"Eigenvalue"].to_numpy()
		item_names = self._director.evaluations_active.item_names
		loadings = self._director.configuration_active.loadings
		
		# We need to access the transformer to get mean_ and noise_variance_
		# These should be stored during execution - let's access from
		#  the current context
		
		# Populate the QTableWidget with the DataFrame data
		for row in range(self._director.evaluations_active.nreferent):
			# Column 0: Eigenvalues
			item = QTableWidgetItem(f"{eigenvalues[row]:6.4f}")
			item.setTextAlignment(
				QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)
			table_widget.setItem(row, 0, item)
			
			# Column 1: Mean (we'll need to store this from transformer)
			mean_val = self._director.configuration_active.\
				transformer_mean[row]
			item = QTableWidgetItem(f"{mean_val:6.4f}")
			item.setTextAlignment(
				QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)
			table_widget.setItem(row, 1, item)
			
			# Column 2: Noise Variance (scalar value, same for all rows)
			noise_val = self._director.configuration_active.\
				transformer_noise_variance
			# Take mean of noise variances across features for display
			noise_val = float(noise_val.mean())
			item = QTableWidgetItem(f"{noise_val:6.4f}")
			item.setTextAlignment(
				QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)
			table_widget.setItem(row, 2, item)
			
			# Column 3: Item names
			item = QTableWidgetItem(item_names[row])
			item.setTextAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
			table_widget.setItem(row, 3, item)
			
			# Column 4: Factor 1 components (loadings)
			item = QTableWidgetItem(f"{loadings.iloc[row, 0]:6.4f}")
			item.setTextAlignment(
				QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)
			table_widget.setItem(row, 4, item)
			
			# Column 5: Factor 2 components (loadings)
			item = QTableWidgetItem(f"{loadings.iloc[row, 1]:6.4f}")
			item.setTextAlignment(
				QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)
			table_widget.setItem(row, 5, item)
			
		return table_widget

	# ------------------------------------------------------------------------


class MDSCommand:
	"""The MDS command performs multidimensional scaling
	on the active configuration. An initial configuration and
	similarities have to have been established.
	"""

	def __init__(self, director: Status, common: Spaces) -> None:
		self._director = director
		self.common = common
		self._director.command = "MDS"
		self._director.configuration_active.best_stress = -1
		self._director.configuration_active.use_metric = False
		self._mds_components_title = "Components to extract"
		self._mds_components_label = "Set number of components to extract"
		self._mds_components_min_allowed = 1
		self._mds_components_max_allowed = 10
		self._mds_components_default = 2
		self._mds_components_an_integer = True
		return

	# ------------------------------------------------------------------------

	def execute(
		self,
		common,  # noqa: ANN001, ARG002
		use_metric: bool = False) -> None:  # noqa: FBT001, FBT002
		self._director.record_command_as_selected_and_in_process()
		self._director.optionally_explain_what_command_does()
		self._director.dependency_checker.detect_dependency_problems()
		self._director.configuration_active.use_metric = use_metric
		self._get_n_components_to_use_from_user(
			self._mds_components_title,
			self._mds_components_label,
			self._mds_components_min_allowed,
			self._mds_components_max_allowed,
			self._mds_components_default,
			self._mds_components_an_integer,
		)
		self._perform_mds_pick_up_point_labelling_from_similarities()
		ndim = self._director.configuration_active.ndim
		npoint = self._director.configuration_active.npoint
		best_stress = self._director.configuration_active.best_stress
		self._director.configuration_active.inter_point_distances()
		self._director.similarities_active.rank_when_similarities_match_configuration(
			self._director, self.common
		)
		self._print_best_stress(ndim, best_stress)
		self._director.rivalry.create_or_revise_rivalry_attributes(
			self._director, self.common
		)
		self._director.configuration_active.print_active_function()
		self._director.common.create_plot_for_tabs("configuration")
		self._director.title_for_table_widget = (
			f"Configuration has  {ndim} dimensions and "
			f"{npoint} points and stress of {best_stress: 6.4f}"
		)
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.record_command_as_successfully_completed()
		return

	# ------------------------------------------------------------------------

	def _get_n_components_to_use_from_user_initialize_variables(self) -> None:
		self.missing_n_components_error_title = self._director.command
		self.missing_n_components_error_message = (
			"Need number of components to use."
		)

	# ------------------------------------------------------------------------

	def _get_n_components_to_use_from_user(
		self,
		mds_components_title: str,
		mds_components_label: str,
		mds_components_min_allowed: int,
		mds_components_max_allowed: int,
		mds_components_default: float,
		mds_components_an_integer: bool) -> None:  # noqa: FBT001
		self._get_n_components_to_use_from_user_initialize_variables()
		dialog = SetValueDialog(
			mds_components_title,
			mds_components_label,
			mds_components_min_allowed,
			mds_components_max_allowed,
			mds_components_an_integer,
			mds_components_default,
		)
		result = dialog.exec()
		if result == QDialog.Accepted:
			self._director.configuration_active.n_comp = dialog.getValue()
		else:
			raise MissingInformationError(
				self.missing_n_components_error_title,
				self.missing_n_components_error_message,
			)
		if self._director.configuration_active.n_comp == 0:
			raise MissingInformationError(
				self.missing_n_components_error_title,
				self.missing_n_components_error_message,
			)
		return

	# ------------------------------------------------------------------------

	def _perform_mds_pick_up_point_labelling_from_similarities(self) -> None:
		ndim = self._director.configuration_active.ndim
		n_comp = self._director.configuration_active.n_comp
		use_metric = self._director.configuration_active.use_metric
		similarities_instance = self._director.similarities_active
		nitem = self._director.similarities_active.nitem
		npoint = self._director.similarities_active.nitem
		nreferent = self._director.similarities_active.nreferent
		point_names = self._director.similarities_active.item_names
		point_labels = self._director.similarities_active.item_labels
		item_names = self._director.similarities_active.item_names
		item_labels = self._director.similarities_active.item_labels

		if self._director.common.have_scores():
			self._director.abandon_scores()
		if ndim == 0:
			ndim = n_comp
		configuration_instance = self._director.common.mds(
			n_comp, use_metric, similarities_instance
		)

		range_points = range(nitem)
		if len(point_labels) == 0:
			npoint = nreferent
			point_names = item_names
			point_labels = item_labels

		self._director.configuration_active = configuration_instance
		self._director.configuration_active.ndim = ndim
		self._director.configuration_active.range_points = range_points
		self._director.configuration_active.npoint = npoint
		self._director.configuration_active.point_labels = point_labels
		self._director.configuration_active.range_points = range_points
		self._director.configuration_active.point_names = point_names
		self._director.configuration_active.item_names = point_names
		self._director.configuration_active.item_labels = point_labels

		self._director.configuration_active.point_coords = (
			configuration_instance.point_coords
		)

		self._director.rivalry.create_or_revise_rivalry_attributes(
			self._director, self.common
		)

		return

	# ------------------------------------------------------------------------

	def _print_best_stress(self, ndim: int, best_stress: float) -> None:
		print(f"Best stress in {ndim} dimensions:    {best_stress: 6.4}\n")

		return

	# ------------------------------------------------------------------------


class PrincipalComponentsCommand:
	"""The Principal components command"""

	def __init__(self, director: Status, common: Spaces) -> None:
		self._director = director
		self.common = common
		self._director.command = "Principal components"
		self._director.common.ndim = 0
		self._director.title_for_table_widget = "Principal components"

		# self._director.configuration_active.pca_covar = pd.DataFrame()
		# self._director.configuration_active.npoint = 0
		# self._director.configuration_active.range_dims = \
		# 	range(self._director.common.ndim)
		# self._director.configuration_active.range_points = \
		# 	range(self._director.configuration_active.npoint)
		# self._director.configuration_active.dim_names = []
		# self._director.configuration_active.dim_labels = []
		# self._director.configuration_active.point_names = []
		# self._director.configuration_active.point_labels = []
		# self._director.configuration_active.distances.clear()

		return

	# ------------------------------------------------------------------------

	def execute(self, common: Spaces) -> None:  # noqa: ARG002
		self._director.record_command_as_selected_and_in_process()
		self._director.optionally_explain_what_command_does()
		self._director.dependency_checker.detect_dependency_problems()
		(
			pca_transformer,
			X_pca_transformed,  # noqa:N806
			x_pca_trans,
			transpose,
			trans,
		) = self._perform_principal_component_analysis()
		self._establish_principal_components_as_active_configuration(trans)
		self._establish_pca_results_as_scores(X_pca_transformed)
		self._print_pca(
			pca_transformer, X_pca_transformed, x_pca_trans, transpose
		)
		# Display scree diagram showing eigenvalues by dimensionality
		# Ask user how many dimensions to be retained
		# Display configuration with vectors from origin to each point
		self._director.common.create_plot_for_tabs("configuration")
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.record_command_as_successfully_completed()
		print(
			# f"DEBUG -- at bottom of PrincipalComponentsCommand"
			f" {self._director.configuration_active.point_coords=}"
		)
		return

	# ------------------------------------------------------------------------

	def _perform_principal_component_analysis(self) -> tuple:


		item_names = self._director.evaluations_active.item_names

		X_pca = self._director.evaluations_active.evaluations  # noqa: N806
		pca_transformer = PCA(n_components=2, copy=True, random_state=0)
		X_pca_transformed = pca_transformer.fit_transform(X_pca)  # noqa: N806
		pd.set_option("display.max_columns", None)
		pd.set_option("display.precision", 2)
		pd.set_option("display.max_colwidth", 300)
		components = pd.DataFrame(
			pca_transformer.components_,
			index=pca_transformer.get_feature_names_out(),
			columns=item_names,
		)
		x_pca_trans = pd.DataFrame(
			X_pca_transformed, columns=pca_transformer.get_feature_names_out()
		)
		self._director.configuration_active.pca_covar = pd.DataFrame(
			pca_transformer.get_covariance(),
			columns=item_names,
			index=item_names,
		)
		transpose = components.transpose()
		trans = pd.DataFrame(transpose)
		return (
			pca_transformer,
			X_pca_transformed,
			x_pca_trans,
			transpose,
			trans,
		)

	# ------------------------------------------------------------------------

	def _establish_principal_components_as_active_configuration(
		self, trans: pd.DataFrame
	) -> None:
		"""Establish the principal components as the active configuration."""
		ndim = trans.shape[1]
		npoint = trans.shape[0]
		dim_names = []
		dim_labels = []
		point_names = []
		point_labels = []

		range_dims = range(ndim)
		range_points = range(npoint)

		for each_dim in range_dims:
			dim_names.append(trans.columns[each_dim])
			dim_labels.append("CO" + str(each_dim))
		for each_point in range_points:
			point_names.append(trans.index[each_point])
			point_labels.append(point_names[each_point][0:4])
		point_coords = pd.DataFrame(trans)

		self._director.configuration_active.ndim = ndim
		self._director.configuration_active.npoint = npoint
		self._director.configuration_active.range_dims = range_dims
		self._director.configuration_active.range_points = range_points
		self._director.configuration_active.dim_names = dim_names
		self._director.configuration_active.dim_labels = dim_labels
		self._director.configuration_active.point_names = point_names
		self._director.configuration_active.point_labels = point_labels
		self._director.configuration_active.point_coords = point_coords

		return

	# ------------------------------------------------------------------------

	def _establish_pca_results_as_scores(
		self, X_pca_transformed: np.array # noqa: N803
	) -> None:
		score_1_name = self._director.configuration_active.dim_names[0]
		score_2_name = self._director.configuration_active.dim_names[1]
		hor_axis_name = self._director.configuration_active.dim_names[0]
		vert_axis_name = self._director.configuration_active.dim_names[1]
		dim_names = self._director.configuration_active.dim_names

		scores = pd.DataFrame(X_pca_transformed, columns=dim_names)
		scores.reset_index(inplace=True)
		scores.rename(columns={"index": "Resp no"}, inplace=True)

		self._director.configuration_active.score_1_name = score_1_name
		self._director.configuration_active.score_2_name = score_2_name
		self._director.configuration_active.hor_axis_name = hor_axis_name
		self._director.configuration_active.vert_axis_name = vert_axis_name
		self._director.configuration_active.scores = scores

		return

	# ------------------------------------------------------------------------

	def _print_pca(
		self,
		pca_transformer: PCA,
		X_pca_transformed: np.array,  # noqa: N803
		x_pca_trans: pd.DataFrame,
		transpose: pd.DataFrame,
	) -> None:
		pca_covar = self._director.configuration_active.pca_covar
		point_coords = self._director.configuration_active.point_coords
		scores = self._director.configuration_active.scores

		print("\n\t", pca_transformer)
		print("X_pca_transformed.shape: ", X_pca_transformed.shape)
		print("X_pca_Trans: \n", x_pca_trans)
		print("pca_transformer.get_params(): \n", pca_transformer.get_params())
		print(
			"pca_transformer.get_feature_names_out(): ",
			pca_transformer.get_feature_names_out(),
		)
		print("PCA Covariance: \n", pca_covar)
		print("\nTranspose: \n", transpose)
		print("\nPoint_coords: \n", point_coords)
		print(f"\nScores from components\n {scores=}")
		return


# --------------------------------------------------------------------------


class VectorsCommand:
	"""The Vectors command plots the active configuration using vectors."""

	def __init__(self, director: Status, common: Spaces) -> None:
		self._director = director
		self.common = common
		self._director.command = "Vectors"

		self.npoint = self._director.configuration_active.npoint
		self.point_coords = self._director.configuration_active.point_coords
		self.point_labels = self._director.configuration_active.point_labels
		self.range_points = self._director.configuration_active.range_points
		self._hor_dim = self._director.common.hor_dim
		self._vert_dim = self._director.common.vert_dim
		self.ndim = self._director.configuration_active.ndim
		self.dim_names = self._director.configuration_active.dim_names

		return

	# ------------------------------------------------------------------------

	def execute(self, common: Spaces) -> None:  # noqa: ARG002
		self._director.record_command_as_selected_and_in_process()
		self._director.optionally_explain_what_command_does()
		self._director.dependency_checker.detect_dependency_problems()
		self._director.configuration_active.print_active_function()
		self._director.common.create_plot_for_tabs("vectors")
		ndim = self._director.configuration_active.ndim
		npoint = self._director.configuration_active.npoint
		self._director.title_for_table_widget = (
			f"Vectors are based on the active configuration "
			f"which has {ndim} dimensions and {npoint} points"
		)
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.record_command_as_successfully_completed()
		return

	# ------------------------------------------------------------------------

	def compute_vector_length_angle_and_angle_degree(
		self, x: float, y: float
	) -> tuple[float, float, float]:
		length = np.sqrt(x**2 + y**2)
		angle = np.arctan2(y, x)
		angle_degree = np.rad2deg(angle)
		return length, angle, angle_degree


# --------------------------------------------------------------------------


class UncertaintyAnalysis:
	def __init__(self, director: Status) -> None:
		self._director = director
		self._hor_dim = director.common.hor_dim
		self._vert_dim = director.common.vert_dim
		self.file_handle: str = ""
		self.npoint: int = 0
		self.npoints: int = 0
		self.range_points: range = range(0)
		self.ndim: int = 0
		self.dim_names: list[str] = []
		self.dim_labels: list[str] = []
		self.range_dims: range = range(0)
		self.point_names: list[str] = []
		self.point_labels: list[str] = []
		self.point_coords: pd.DataFrame = pd.DataFrame()
		self.item_names: list[str] = []
		self.item_labels: list[str] = []
		self.nreferent: int = 0

		self.universe_size: int = 0
		self.nrepetitions: int = 0
		self.probability_of_inclusion: float = 0.0
		self.sample_design: pd.DataFrame = pd.DataFrame()
		self.sample_design_frequencies: pd.DataFrame = pd.DataFrame()
		self.sample_repetitions: pd.DataFrame = pd.DataFrame()
		self.solutions_stress_df: pd.DataFrame = pd.DataFrame()
		self.sample_solutions: pd.DataFrame = pd.DataFrame()
		self.ndim: int = 0
		self.npoint: int = 0
		self.nsolutions: int = 0
		self.dim_names: list[str] = []
		self.dim_labels: list[str] = []
		self.point_names: list[str] = []
		self.point_labels: list[str] = []
		self.target_out: np.ndarray = np.array([])
		self.solutions: pd.DataFrame = pd.DataFrame()

	# ------------------------------------------------------------------------

	def create_table_widget_for_sample_designer(self) -> QTableWidget:
		nrepetitions = self._director.uncertainty_active.nrepetitions
		repetition_freqs = (
			self._director.uncertainty_active.sample_design_frequencies
		)
		universe_size = self._director.uncertainty_active.universe_size

		table_widget = QTableWidget(nrepetitions, 5)

		for each_repetition in range(1, nrepetitions + 1):
			_repetition_selected = (
				repetition_freqs["Repetition"] == each_repetition
			) & (repetition_freqs["Selected"])
			_repetition_not_selected = (
				repetition_freqs["Repetition"] == each_repetition
			) & (~repetition_freqs["Selected"])

			value_1 = f"{each_repetition}"
			item_1 = QTableWidgetItem(value_1)
			item_1.setTextAlignment(QtCore.Qt.AlignCenter)
			table_widget.setItem(
				each_repetition - 1, 0, QTableWidgetItem(item_1)
			)

			if repetition_freqs.loc[_repetition_selected]["Count"].empty:
				value_2 = "0"
				percent_value_2 = 0.0
			else:
				value_2 = f"{
					repetition_freqs.loc[_repetition_selected][
						'Count'
					].to_numpy()[0]
				}"
				percent_value_2 = (
					repetition_freqs.loc[_repetition_selected][
						"Count"
					].to_numpy()[0]
					/ universe_size
				)
			item_2 = QTableWidgetItem(value_2)
			item_2.setTextAlignment(QtCore.Qt.AlignCenter)
			table_widget.setItem(
				each_repetition - 1, 1, QTableWidgetItem(item_2)
			)
			value_3 = f"{percent_value_2:.2%}"
			item_3 = QTableWidgetItem(value_3)
			item_3.setTextAlignment(QtCore.Qt.AlignCenter)
			table_widget.setItem(
				each_repetition - 1, 2, QTableWidgetItem(item_3)
			)
			if repetition_freqs.loc[_repetition_not_selected]["Count"].empty:
				value_4 = "0"
				percent_value_4 = 0.0
			else:
				value_4 = f"{
					repetition_freqs.loc[_repetition_not_selected][
						'Count'
					].to_numpy()[0]
				}"
				percent_value_4 = (
					repetition_freqs.loc[_repetition_not_selected][
						"Count"
					].to_numpy()[0]
					/ universe_size
				)
			item_4 = QTableWidgetItem(value_4)
			item_4.setTextAlignment(QtCore.Qt.AlignCenter)
			table_widget.setItem(
				each_repetition - 1, 3, QTableWidgetItem(item_4)
			)
			value_5 = f"{percent_value_4:.2%}"
			item_5 = QTableWidgetItem(value_5)
			item_5.setTextAlignment(QtCore.Qt.AlignCenter)
			table_widget.setItem(
				each_repetition - 1, 4, QTableWidgetItem(item_5)
			)

		return table_widget

	# ------------------------------------------------------------------------


class UncertaintyCommand:
	def __init__(self, director: Status, common: Spaces) -> None:
		self._director = director
		self.common = common
		self._director.command = "Uncertainty"

		self.solutions: pd.DataFrame = pd.DataFrame(
			columns=[self._director.target_active.dim_names]
		)
		self.solutions: pd.DataFrame = pd.DataFrame()
		self._director.uncertainty_active.sample_solutions = pd.DataFrame()
		self.target_out: np.array = np.array([])
		self.active_out: np.array = np.array([])
		self.target_adjusted = TargetFeature(self._director)

		return

	# ------------------------------------------------------------------------

	def execute(self, common: Spaces) -> None:
		director = self._director
		common = self.common
		uncertainty_active = director.uncertainty_active
		sample_repetitions = uncertainty_active.sample_repetitions
		nreferent = director.evaluations_active.nreferent

		director.record_command_as_selected_and_in_process()
		director.optionally_explain_what_command_does()
		director.dependency_checker.detect_dependency_problems()

		self.target_out, self.active_out = self._get_solutions_from_mds(
			common, sample_repetitions, nreferent
		)
		uncertainty_active.target_out = self.target_out
		uncertainty_active.solutions = self.solutions
		uncertainty_active.sample_solutions = self.solutions

		common.create_solutions_table()

		print(
			director.uncertainty_active.solutions_stress_df.to_string(
				index=False
			)
		)

		director.common.create_plot_for_tabs("uncertainty")
		director.title_for_table_widget = (
			"An ellipse around each point delineates with 95% confidence that "
			"the point lies within that point's ellipse"
		)
		director.create_widgets_for_output_and_log_tabs()
		director.set_focus_on_tab("Plot")
		director.record_command_as_successfully_completed()

		return

	# ------------------------------------------------------------------------

	def _get_solutions_from_mds(
		self, common: Spaces, sample_repetitions: pd.DataFrame, nreferent: int
	) -> tuple[np.array, np.array]:
		director = self._director
		configuration_active = director.configuration_active
		target_active = director.target_active
		uncertainty_active = director.uncertainty_active
		dim_names = target_active.dim_names
		# dim_labels = target_active.dim_labels
		self.ndim = target_active.ndim
		repetition_freqs = uncertainty_active.sample_design_frequencies
		nrepetitions = uncertainty_active.nrepetitions
		range_repetitions = range(nrepetitions)
		# current_repetition: EvaluationsFeature = \
		# EvaluationsFeature(self._director)
		line_of_sight = SimilaritiesFeature(self._director)
		# the_loadings = ConfigurationFeature(self._director)
		line_of_sight.nreferent = 0
		line_of_sight.value_type = "dissimilarities"
		use_metric = configuration_active.use_metric
		item_names = uncertainty_active.item_names
		item_labels = uncertainty_active.item_labels

		repetition_sizes = self.get_repetition_sizes(
			range_repetitions, repetition_freqs
		)

		start_case = 0
		extract_ndim = 2
		repetition_n = 1
		stress_data = []
		for repetition_size in repetition_sizes:
			(current_repetition, start_case) = self.get_current_repetition(
				start_case,
				repetition_size,
				sample_repetitions,
				nreferent,
				item_names,
				item_labels,
			)

			line_of_sight = self._director.common.los(current_repetition)
			self.duplicate_repetition_line_of_sight(common, line_of_sight)

			the_loadings = self._director.common.mds(
				extract_ndim, use_metric, line_of_sight
			)

			stress_data.append([repetition_n, the_loadings.best_stress])

			active_in = np.array(the_loadings.point_coords)

			target_in = np.array(target_active.point_coords)

			target_out, active_out, disparity = procrustes(
				target_in, active_in
			)

			active_out_as_df = pd.DataFrame(active_out)
			# print(f"\nDEBUG -- in _get_repetition after procrustes plus "
			# 	f"\nactive_out_as_df: \n{active_out_as_df}")
			self.solutions = pd.concat(
				[self.solutions, active_out_as_df], ignore_index=True
			)

			# start_case = end_case
			repetition_n += 1

		# Create solutions_stress_df from the collected stress data
		uncertainty_active.solutions_stress_df = pd.DataFrame(
			stress_data, columns=["Solution", "Stress"]
		)

		solutions_columns = dim_names

		self.target_out = target_out
		self.active_out = active_out

		self.target_last = target_out
		self.solutions.columns = solutions_columns
		target_active = self._director.target_active

		self.establish_sample_solutions_info()

		# uncertainty_active.nrepetitions = nrepetitions

		# peek("At end of _get_solutions_from_mds\n",
		# 	"self._director.uncertainty_active.sample_solutions: \n"
		# 	f"{self._director.uncertainty_active.sample_solutions}\n"
		# 	"self._director.uncertainty_active.sample_repetitions_stress: \n"
		# 	f"{self._director.uncertainty_active.sample_repetitions_stress}\n"
		# )

		return target_out, active_out

	# -------------------------------------------------------------------------

	def establish_sample_solutions_info(self) -> None:
		uncertainty_active = self._director.uncertainty_active
		target_active = self._director.target_active
		uncertainty_active.point_coords = uncertainty_active.solutions
		uncertainty_active.npoints = target_active.npoint
		uncertainty_active.ndim = target_active.ndim
		uncertainty_active.dim_names = target_active.dim_names
		uncertainty_active.dim_labels = target_active.dim_labels
		uncertainty_active.point_names = target_active.point_names
		uncertainty_active.point_labels = target_active.point_labels
		uncertainty_active.nsolutions = uncertainty_active.nrepetitions
		uncertainty_active.range_points = range(uncertainty_active.npoints)

		return

	# -------------------------------------------------------------------------

	def get_repetition_sizes(
		self, range_repetitions: range, repetition_freqs: pd.DataFrame
	) -> list[int]:
		repetition_sizes = []
		for each_repetition in range_repetitions:
			row_with_repetition_size: int = (each_repetition * 2) + 1
			column_with_repetition_size: int = 2
			size = repetition_freqs.iloc[
				row_with_repetition_size, column_with_repetition_size
			]
			repetition_sizes.append(size)

		return repetition_sizes

	# -------------------------------------------------------------------------

	def get_current_repetition(
		self,
		start_case: int,
		repetition_size: int,
		sample_repetitions: pd.DataFrame,
		nreferent: int,
		item_names: list[str],
		item_labels: list[str],
	) -> tuple[EvaluationsFeature, int]:
		"""
		Creates an EvaluationsFeature instance for the current repetition.

		Parameters:
		-----------
		start_case : int
			The starting index for the current repetition
		repetition_size : int
			The number of cases in this repetition
		sample_repetitions : pandas.DataFrame
			The data for all repetitions
		nreferent : int
			Number of referents in the evaluation
		item_names_and_labels : tuple
			Tuple containing (item_names, item_labels)

		Returns:
		--------
		tuple
			(EvaluationsFeature instance for current repetition, new start
			case)
		"""
		# item_names, item_labels = item_names_and_labels

		end_case = start_case + repetition_size
		current_repetition: EvaluationsFeature = EvaluationsFeature(
			self._director
		)
		current_repetition.evaluations = sample_repetitions.iloc[
			start_case:end_case
		]
		current_repetition.nreferent = nreferent
		current_repetition.item_names = item_names
		current_repetition.item_labels = item_labels
		current_repetition.nevaluators = repetition_size
		start_case = end_case + 1
		return current_repetition, start_case

	# -------------------------------------------------------------------------

	def duplicate_repetition_line_of_sight(
		self, common: Spaces, line_of_sight: SimilaritiesFeature
	) -> None:
		(
			line_of_sight.similarities_as_dataframe,
			line_of_sight.similarities_as_dict,
			line_of_sight.similarities_as_list,
			line_of_sight.similarities_as_square,
			line_of_sight.sorted_similarities_w_pairs,
			line_of_sight.ndyad,
			line_of_sight.range_dyads,
			line_of_sight.range_items,
		) = common.duplicate_in_different_structures(
			line_of_sight.similarities,
			line_of_sight.item_names,
			line_of_sight.item_labels,
			line_of_sight.nitem,
			line_of_sight.value_type,
		)

	# ------------------------------------------------------------------------

	def _display(self) -> QTableWidget:
		gui_output_as_widget = self._director.statistics.display_table(
			"uncertainty"
		)

		self._director.output_widget_type = "Table"
		return gui_output_as_widget
