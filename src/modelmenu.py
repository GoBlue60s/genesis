
from factor_analyzer import FactorAnalyzer
import numpy as np
# import matplotlib.pyplot as plt
# from matplotlib import transforms
# from matplotlib.patches import Ellipse
import pandas as pd
import peek

from PySide6 import QtCore
from PySide6.QtWidgets import QDialog, QTableWidget, QTableWidgetItem
from scipy.spatial import procrustes
from sklearn.decomposition import FactorAnalysis, PCA
from sklearn.preprocessing import StandardScaler
from tabulate import tabulate

from constants import (
	# MAXIMUM_NUMBER_OF_DIMENSIONS_FOR_PLOTTING,
	MINIMAL_DIFFERENCE_FROM_ZERO
)
from dialogs import SetValueDialog
from exceptions import (
	MissingInformationError,
	SpacesError
)
from features import (
    EvaluationsFeature,
	SimilaritiesFeature,
	TargetFeature
)
from common import Spaces
from director import Status
from table_builder import StatisticalTableWidget

# --------------------------------------------------------------------------


class DirectionsCommand:

	def __init__(
			self,
			director: Status,
			common: Spaces) -> None:

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

	def execute(
			self,
			common: Spaces) -> None: # noqa: ARG002

		self._director.record_command_as_selected_and_in_process()
		self._director.optionally_explain_what_command_does()
		self._director.dependency_checker.detect_dependency_problems()
		self._calculate_point_directions()
		# self._director.configuration_active.print_active_function()
		self._print_directions_df()
		self._director.common.create_plot_for_plot_and_gallery_tabs(
			"directions")
		ndim = self._director.configuration_active.ndim
		npoint = self._director.configuration_active.npoint
		self._director.title_for_table_widget = (
			f"Directions are based on the active configuration"
			f" which has {ndim} dimensions and "
			f"{npoint} points")
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.record_command_as_successfully_completed()
		return

# --------------------------------------------------------------------------

	def _print_directions_df(self) -> None:
		"""Print the directions DataFrame to the output tab"""
		directions_df = self._director.configuration_active.directions_df
		directions_df.rename(
			columns={
				'Slope': 'Slope',
				'Unit_Circle_x': 'Unit Circle \n X',
				'Unit_Circle_y': 'Unit Circle \n Y',
				'Angle_Degrees': 'Angle in \n Degrees',
				'Angle_Radians': 'Angle in \n Radians',
				'Quadrant': 'Quadrant'}, inplace=True)

		table = tabulate(
			directions_df,
			headers='keys',
			tablefmt='plain',
			showindex=True,
			floatfmt=['.2f', '.2f', '.2f', '.2f', '.2f', '.2f', '.0f'])
		
		print(f"{table}")

		return

# --------------------------------------------------------------------------

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
				slope = float('inf') if y >= 0 else float('-inf')
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
			if abs(x) < MINIMAL_DIFFERENCE_FROM_ZERO \
				and abs(y) < MINIMAL_DIFFERENCE_FROM_ZERO:
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
		directions_df = pd.DataFrame({
			'Slope': slopes,
			'Unit_Circle_x': unit_circle_x,
			'Unit_Circle_y': unit_circle_y,
			'Angle_Degrees': angles_degrees,
			'Angle_Radians': angles_radians,
			'Quadrant': quadrants
		}, index=point_names)
		
		self._director.configuration_active.directions_df = directions_df
		
		return directions_df


	# ------------------------------------------------------------------------


class FactorAnalysisCommand:
	""" The Factor command calculates latent variables to explain the
	variation in evaluations.
	"""
	def __init__(
			self,
			director: Status,
			common: Spaces) -> None:

		self._director = director
		self.common = common
		self._director.command = "Factor analysis"


		# self._director.configuration_active.fa = pd.DataFrame()
		# self._director.configuration_active.loadings = pd.DataFrame()
		# self._director.configuration_active.eigen = pd.DataFrame()
		# self._director.configuration_active.eigen_common = pd.DataFrame()
		# self._director.configuration_active.commonalities = pd.DataFrame()
		# self._director.configuration_active.factor_variance = pd.DataFrame()
		# self._director.configuration_active.uniquenesses = pd.DataFrame()
		# self._director.configuration_active.ndim = 0
		# self._director.configuration_active.nitem = \
		# 	self._director.evaluations_active.nreferent
		# self._director.configuration_active.range_dims = \
		# 	range(self._director.configuration_active.ndim)
		# self._director.configuration_active.range_item = \
		# 	range(self._director.configuration_active.nitem)
		# self._director.configuration_active.dim_names = []
		# self._director.configuration_active.dim_labels = []
		# self._director.configuration_active.point_names = []
		# self._director.configuration_active.point_coords = pd.DataFrame()
		# self._director.configuration_active.distances = []


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

	def execute(
			self,
			common: Spaces) -> None: # noqa: ARG002

		self._director.record_command_as_selected_and_in_process()
		self._director.optionally_explain_what_command_does()
		self._director.dependency_checker.detect_dependency_problems()
		ext_fact = self._get_factors_to_extract_from_user(
			self._title, self._label, self._min_allowed, self._max_allowed,
			self._an_integer, self._default)
		self._director.configuration_active.ndim = int(ext_fact)
		self._factors_and_scores()
		# self._create_scree_diagram_for_plot_and_gallery_tabs()
		self._director.common.create_plot_for_plot_and_gallery_tabs("scree")
		self._create_factor_analysis_table()
		self._print_factor_analysis_results()
		self._fill_configuration()
		self._director.title_for_table_widget = "Factor analysis"
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.record_command_as_successfully_completed()
		return

	# ------------------------------------------------------------------------

	def _factors_and_scores(self) -> None:

		ndim = self._director.configuration_active.ndim
		nreferent = self._director.evaluations_active.nreferent
		evaluations = self._director.evaluations_active.evaluations
		item_names = self._director.evaluations_active.item_names

		score_1_name = "Factor 1"
		score_2_name = "Factor 2"
		# score_1_label = "Fa1"
		# score_2_label = "Fa2"
		dim_names = []
		dim_labels = []

		fa = FactorAnalyzer(
			n_factors=ndim, rotation="varimax", is_corr_matrix=False)
		# self._director.configuration_active.fa = FactorAnalyzer(
		# 	n_factors=self._director.configuration_active.ndim,
		# rotation="varimax", is_corr_matrix=True)
		print(f"DEBUG -- after FactorAnalyzer {fa=}")
		fa.fit(evaluations)
		print(f"DEBUG -- just  done fa.fit {fa.fit=}")
		range_dims = range(ndim)
		for each_dim in range_dims:
			dim_names.append("Factor " + str(each_dim + 1))
			dim_labels.append("FA" + str(each_dim + 1))
		range_items = range(nreferent)
		range_points = range(nreferent)
		print(f"DEBUG -- in FA classic {range_points=}")
		# for each_point in self._director.evaluations_active.range_items:
		# 	self._director.configuration_active.point_names.append(
		# self._director.evaluations_active.item_names[each_point])
		# 	item = self._director.evaluations_active.item_names[each_point]
		# 	self._director.configuration_active.point_labels.append(item[0:4])

		print(f"DEBUG -- {dim_names=} \n{item_names=}")
		print(f"DEBUG -- just before fa.loadings {nreferent=}")
		print("DEBUG -- in FA classic also just before fa.loadings"
			f" {range_items=}")
		the_loadings = fa.loadings_
		print("DEBUG -- in FA classic also just after fa.loadings"
			f" {the_loadings=}")
		print(f"DEBUG -- {dim_names=} \n{item_names=}")
		loadings = pd.DataFrame(the_loadings, columns=dim_names,
			index=item_names)
		print(f"DEBUG -- in FA classic just after loadings {range_items=}")
		# print(f"DEBUG -- {self._director.configuration_active.loadings=}")
		#
		# self._director.configuration_active.loadings =
		# pd.DataFrame.from_records(
		# self._director.configuration_active.loadings,
		# columns=self._director.configuration_active.dim_names,
		# index=self._director.configuration_active.item_names)
		# print(f"DEBUG -- {self._director.configuration_active.loadings=}")
		#
		# self._director.configuration_active.point_coords =
		# pd.DataFrame.from_records(
		# self._director.configuration_active.loadings,
		# columns=self._director.configuration_active.dim_names,
		# index=self._director.configuration_active.item_names)
		point_coords = pd.DataFrame(\
			loadings, columns=dim_names, index=item_names)
		#
		# Get the eigenvector and the eigenvalues
		ev, v = fa.get_eigenvalues()
		#
		# self._director.configuration_active.eigen
		# = pd.DataFrame(data=ev, columns=["Eigenvalue"],
		# index=self._director.configuration_active.item_names)
		eigen = pd.DataFrame(data=ev, columns=["Eigenvalue"])
		print(f"DEBUG in factors_and_scores -- {eigen=}")
		# self._director.configuration_active.eigen_common
		# = pd.DataFrame(data=v, columns=["Eigenvalue"],
		# index=self._director.configuration_active.item_names)
		eigen_common = pd.DataFrame(data=v, columns=["Eigenvalue"])
		print(f"DEBUG in factors_and_scores -- {eigen_common=}")
		get_commonalities = fa.get_communalities()
		commonalities = pd.DataFrame(
			data=get_commonalities, columns=["Commonality"], index=item_names)
		factor_variance = pd.DataFrame(
			fa.get_factor_variance(),
			columns=dim_names,
			index=["Variance", "Proportional", "Cumulative"])
		uniquenesses = pd.DataFrame(
			fa.get_uniquenesses(), columns=["Uniqueness"], index=item_names)
		scores = pd.DataFrame(fa.transform(evaluations), columns=dim_names)
		scores.reset_index(inplace=True)
		scores.rename(columns={'index': 'Resp no'}, inplace=True)

		score_1 = scores[score_1_name]
		score_2 = scores[score_2_name]

		self._director.configuration_active.range_dims = range_dims
		self._director.configuration_active.point_coords = point_coords
		self._director.configuration_active.dim_names = dim_names
		self._director.configuration_active.eigen = eigen
		self._director.configuration_active.eigen_common = eigen_common
		self._director.configuration_active.commonalities = commonalities
		self._director.configuration_active.factor_variance = factor_variance
		self._director.configuration_active.uniquenesses = uniquenesses
		self._director.evaluations_active.range_items = range_items
		self._director.evaluations_active.range_points = range_points
		self._director.configuration_active.fa = fa
		self._director.configuration_active.loadings = loadings
		# potentially move summarize scores to separate function

		self._director.configuration_active.npoint = \
			self._director.evaluations_active.nreferent
		self._director.configuration_active.nreferent = \
			self._director.evaluations_active.nreferent
		self._director.configuration_active.point_names = \
			self._director.evaluations_active.item_names
		self._director.configuration_active.point_labels = \
			self._director.evaluations_active.item_labels
		self._director.configuration_active.range_points = \
			self._director.evaluations_active.range_items
		self._director.configuration_active.inter_point_distances()
		self._director.scores_active.scores = scores
		self._director.scores_active.score_1 = score_1
		self._director.scores_active.score_2 = score_2
		self._director.scores_active.nscores = \
			self._director.configuration_active.ndim
		self._director.scores_active.nscored_individ = \
			self._director.evaluations_active.nevaluators
		self._director.scores_active.nscored_items = \
			self._director.configuration_active.npoint
		# self._director.scores_active.nscored_items = \
		# 	self._director.configuration_active.nitem
		self._director.scores_active.dim_names = \
			self._director.configuration_active.dim_names
		self._director.scores_active.dim_labels = \
			self._director.configuration_active.dim_labels
		self._director.scores_active.score_1_name = score_1_name
		self._director.scores_active.score_2_name = score_2_name
		# self._director.scores_active.first_label = score_1_label
		# self._director.scores_active.second_label = score_2_label
		self._director.scores_active.hor_axis_name = score_1_name
		self._director.scores_active.vert_axis_name = score_2_name

		return

	# ------------------------------------------------------------------------

	def _fill_configuration(self) -> None:

		self._director.configuration_active.nreferent = \
			self._director.evaluations_active.nreferent

		return

# ------------------------------------------------------------------------


	def _get_factors_to_extract_from_user_initialize_variables(self) -> None:
		"""Initialize variables for the factor extraction dialog."""
	
		self.zero_factors_error_title = "Factor analysis"
		self.zero_factors_error_message = "Need number of factors."

	# ------------------------------------------------------------------------

	def _get_factors_to_extract_from_user(
		self,
		title: str,
		label: str,
		min_allowed: int,
		max_allowed: int,
		an_integer: bool, # noqa: FBT001
		default: int) -> int:
		
		self._get_factors_to_extract_from_user_initialize_variables()
		# ext_fact = 0
		ext_fact_dialog = SetValueDialog(
			title, label, min_allowed, max_allowed, an_integer, default)
		result = ext_fact_dialog.exec()
		if result == QDialog.Accepted:
			ext_fact = ext_fact_dialog.getValue()
		else:
			raise SpacesError(
				self.zero_factors_error_title,
				self.zero_factors_error_message)

		if ext_fact == 0:
			raise SpacesError(
				self.zero_factors_error_title,
				self.zero_factors_error_message)

		return ext_fact

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

# --------------------------------------------------------------------------

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
		loadings_factor2 = \
			source.loadings.iloc[:, 1].to_numpy() \
				if source.ndim > 1 else [0] * nreferent
		
		# Create DataFrame with all columns
		factor_analysis_df = pd.DataFrame({
			"Eigenvalues": eigenvalues[:nreferent],
			"Common Factor\nEigenvalues": common_eigenvalues[:nreferent],
			"Commonalities": commonalities,
			"Uniquenesses": uniquenesses,
			"Item": item_names,
			"Loadings\nFactor 1": loadings_factor1,
			"Loadings\nFactor 2": loadings_factor2
		})

		self._director.configuration_active.factor_analysis_df = \
			factor_analysis_df
		
		return factor_analysis_df

	# ------------------------------------------------------------------------


class FactorAnalysisMachineLearningCommand:

	def __init__(
			self,
			director: Status,
			common: Spaces) -> None:
		""" The Factor command calculates latent variables to explain the
		variation in evaluations.
		"""
		self._director = director
		self.command = common
		self._director.command = "Factor analysis machine learning"
		# components: pd.DataFrame = pd.DataFrame()

		# self._director.configuration_active.covar = pd.DataFrame()
		# self._director.configuration_active.ndim = 0
		# self._director.configuration_active.range_dims = \
		# 	range(self._director.configuration_active.ndim)
		# self._director.configuration_active.dim_names = []
		# self._director.configuration_active.dim_labels = []
		# self._director.configuration_active.point_coords = pd.DataFrame()
		# self._director.configuration_active.distances = []

		self._director.evaluations_active.item_labels = []
		self._director.evaluations_active.range_items = \
			range(self._director.evaluations_active.nitem)
		# self._hor_max: float = 0.0
		# self._hor_min: float = 0.0
		# self._vert_max: float = 0.0
		# self._vert_min: float = 0.0
		# self._offset: float = 0.0

		return

	# ------------------------------------------------------------------------

	def execute(
			self,
			common: Spaces) -> None: # noqa: ARG002

		self._director.record_command_as_selected_and_in_process()
		self._director.optionally_explain_what_command_does()
		self._director.dependency_checker.detect_dependency_problems()
		#
		# Perform factor analysis - move to separate function
		#
		item_names = self._director.evaluations_active.item_names
		# covar = self._director.configuration_active.covar
		evaluations = self._director.evaluations_active.evaluations
		dim_names = []
		dim_labels = []
		
		X = evaluations # noqa: N806
		scaler = StandardScaler()
		print("\n\nscaler: \n", scaler)
		scaler.fit(X)
		print("\nScaler.fit(X): \n", scaler.fit(X))
		StandardScaler()
		print("\nStandardScaler(): \n", StandardScaler())
		print("\nscaler.mean_: \n", scaler.mean_)
		scaler.transform(X)
		print("\nScaler.transform(X): ", scaler.transform(X))
		#
		# X, _ = load_digits(return_X_y=True)
		# transformer = FactorAnalysis(
		# 	n_components=2, svd_method="lapack", copy=True, rotation="varimax",
		# 	random_state=0)
		transformer = FactorAnalysis(
			n_components=2, svd_method="randomized", copy=True,
			rotation="varimax",
			random_state=0)
		print("\n\tTransformer: ", transformer)
		# x_fit = transformer.fit(X)
		# print("\nX-fit: \n", x_fit)
		X_transformed = transformer.fit_transform(X) # noqa: N806
		print("\nX_transformed.shape: ", X_transformed.shape)
		# print("\ncomponents_\n", transformer.components_)
		pd.set_option('display.max_columns', None)
		pd.set_option('display.precision', 2)
		pd.set_option('display.max_colwidth', 300)
		components = pd.DataFrame(
			transformer.components_,
			index=transformer.get_feature_names_out(), columns=item_names)

		# X_transformed.columns = transformer.get_feature_names_out() badddd
		x_trans = pd.DataFrame(
			X_transformed, columns=transformer.get_feature_names_out())
		# x_trans = pd.DataFrame(
		# 	X_transformed, columns=["Factor 1", "Factor 2"])
		print("\nX_Trans: \n", x_trans)

		print("\ntransformer.get_params(): \n", transformer.get_params())
		print(
			"\ntransformer.get_feature_names_out(): ",
			transformer.get_feature_names_out())
		# dim_names = transformer.get_feature_names_out()
		# dim_names = ["Factor 1", "Factor 2"]
		#  print("Get_covariance: ", transformer.get_covariance())
		covar = pd.DataFrame(
			transformer.get_covariance(), columns=item_names, index=item_names)

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
			columns=transformer.get_feature_names_out())
		# self._director.configuration_active.x_new = pd.DataFrame(
		# 	transformer.transform(X),
		# 	columns=["Factor 1", "Factor 2"])
		print("\nX_new: \n", x_new)

		transpose = components.transpose()
		print("\nTranspose: \n", transpose)
		trans = pd.DataFrame(transpose)
		print(f"\nDEBUG -- in execute {trans=}\n")

		ndim = len(trans.columns)
		nitem = len(trans.index)
		print(f"DEBUG -- {ndim=}")
		print(f"DEBUG -- in FA machine learning execute {nitem=}")
		range_dims = range(ndim)
		print(f"\nDEBUG -- {range_dims=}")
		range_items = range(nitem)
		print(f"DEBUG -- {trans.columns=}")
		print(f"DEBUG -- {trans.columns[0]=}")
		for each_dim in range_dims:
			# print(f"DEBUG -- {each_dim=}")
			# dim_names.append(trans.columns[each_dim])
			dim_names.append("Factor " + str(each_dim))
			dim_labels.append("FA"+str(each_dim))
		print(f"DEBUG -- in FA machine learning {item_names=}")
		print(f"DEBUG -- in FA machine learning {range_items=}")

		score_1_name = "Factor 1"
		score_2_name = "Factor 2"
		# self._director.configuration_active.first_label = "Fa1"
		# self._director.configuration_active.second_label = "Fa2"

		for each_point in range_items:
			# print(f"DEBUG -- {each_point=}")
			self._director.evaluations_active.item_labels.append(
				self._director.evaluations_active.item_names[each_point][0:4])
		# rivalry.rival_a.index = -1
		# rivalry.rival_b.index = -1

		# self._director.configuration_active.bisector.case = "Unknown"
		# self._director.configuration_active.bisector.direction = "Unknown"
		self._director.common.show_bisector = False
		self._director.common.show_connector = False
		self._director.configuration_active.distances.clear()
		self._director.configuration_active.point_coords = pd.DataFrame(trans)
		self._director.configuration_active.point_coords.columns = \
			['Factor 1', 'Factor 2']
		self._director.configuration_active.dim_names = \
			["Factor 1", "Factor 2"]
		self._director.configuration_active.dim_labels = ["FA1", "FA2"]
		scaler2 = StandardScaler()
		print("\n\nscaler2: \n", scaler2)
		scaler2.fit(trans)
		print("\nScaler2.fit(X): \n", scaler2.fit(trans))
		StandardScaler()
		print("\nStandardScaler(): \n", StandardScaler())
		print("\nscaler2.mean_: \n", scaler2.mean_)
		new_trans = scaler2.transform(trans)
		print("\nnew_trans: ", new_trans)
		self._director.configuration_active.point_coords = \
			pd.DataFrame(new_trans)
		print("\nPoint_coords: \n",
			self._director.configuration_active.point_coords)
		#
		print(
			"DEBUG -- in FA machine learning after trans "
			f"{self._director.evaluations_active.item_names=}")
		self._director.evaluations_active.nitem = \
			self._director.evaluations_active.nreferent
		print(
			"DEBUG -- in FA machine learning before inter point call "
			f"{self._director.evaluations_active.item_names=}")
		self._director.configuration_active.inter_point_distances()

		self._director.common.set_axis_extremes_based_on_coordinates(
			self._director.configuration_active.point_coords)

		self._director.configuration_active.range_points = \
			self._director.evaluations_active.range_items
		self._director.configuration_active.point_names = \
			self._director.evaluations_active.item_names
		self._director.configuration_active.point_labels = \
			self._director.evaluations_active.item_labels
		self._director.configuration_active.scores = x_new
		# self._director.configuration_active.x_new

		self._director.configuration_active.scores.reset_index(inplace=True)
		self._director.configuration_active.scores.rename(
			columns={'index': 'Resp no'}, inplace=True)
		self._director.scores_active.scores = \
			self._director.configuration_active.scores
		self._director.scores_active.nscores = \
			self._director.configuration_active.ndim
		self._director.scores_active.range_scores = \
			range(self._director.configuration_active.ndim)
		self._director.scores_active.nscored_individ = \
			self._director.evaluations_active.nevaluators
		self._director.scores_active.nscored_items = \
			self._director.evaluations_active.nitem
		self._director.scores_active.dim_names = \
			self._director.configuration_active.dim_names
		
		self._director.scores_active.dim_labels = \
			self._director.configuration_active.dim_labels
		self._director.scores_active.score_1 = \
			self._director.scores_active.scores['factoranalysis0']
		self._director.scores_active.score_2 = \
			self._director.scores_active.scores['factoranalysis1']
		self._director.scores_active.scores = \
			self._director.scores_active.scores.rename(
				columns={
					'factoranalysis0': 'Factor 1',
					'factoranalysis1': 'Factor 2'})
		self._director.scores_active.score_1_name = score_1_name
		# self._director.configuration_active.score_1_name
		self._director.scores_active.score_2_name = score_2_name
		# self._director.configuration_active.score_2_name
		# potentially summarize here
		self._director.scores_active.summarize_scores()

		# self._director.configuration_active.dim_names =
		# ["a one???", "a two???"]

		self._director.common.set_axis_extremes_based_on_coordinates(
			self._director.scores_active.scores.iloc[:, 1:])

		if self._director.configuration_active.ndim > 1:
			fig = \
				self._director.configuration_active.\
				plot_a_configuration_using_matplotlib()
			self._director.plot_to_gui(fig)
			#
			# self._director.create_widgets_for_output_and_log_tabs() <<<< tbd
			#
			self._director.show()
			self._director.set_focus_on_tab('Plot')





		print("\nDEBUG -- in FA machine learning execute just before"
			" _display()")

		self._display()
		#  print??????????
		print("\nDEBUG -- in FA machine learning execute just after"
			" _display()")
		self._fill_configuration()
		self._director.title_for_table_widget = "Factor analysis"
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.record_command_as_successfully_completed()

		self._director.configuration_active.x_new = x_new
		self._director.configuration_active.ndim = ndim
		self._director.configuration_active.range_dims = range_dims
		self._director.configuration_active.dim_names = dim_names
		self._director.configuration_active.dim_labels = dim_labels
		self._director.configuration_active.covar = covar

		self._director.evaluations_active.nitem = nitem
		self._director.evaluations_active.range_items = range_items
		self._director.configuration_active.score_1_name = score_1_name
		self._director.configuration_active.score_2_name = score_2_name

		#
		# Display configuration with vectors from origin to each point
		#
		print("DEBUG -- at the end of FA machine learning execute")

		return

	# ------------------------------------------------------------------------

	def _fill_configuration(self) -> None:

		self._director.configuration_active.nreferent = \
			self._director.evaluations_active.nreferent

		return

	# ------------------------------------------------------------------------

	def _display(self) -> QTableWidget:
		#
		gui_output_as_widget = \
			self._create_table_widget_for_factor_machine_learning()
		#
		self.set_column_and_row_headers(
			gui_output_as_widget,
			[
				"Eigenvalues", "Common Factor\nEigenvalues",
				"Commonalities",
				"Uniquenesses", "Item", "Loadings\nFactor 1",
				"Loadings\nFactor 2"],
			[])
		#
		self._director.resize_and_set_table_size(gui_output_as_widget, 20)
		#
		self._director.output_widget_type = "Table"
		return gui_output_as_widget

	# ------------------------------------------------------------------------

	def _create_table_widget_for_factor_machine_learning(self) -> QTableWidget:
		#
		# print("DEBUG -- at top of _create_table_widget_for_factor_machine"
		# 	"_learning")
		
		ncols = 5 + self._director.configuration_active.ndim
		table_widget = QTableWidget(
			self._director.evaluations_active.nreferent, ncols)
		#
		# Populate the QTableWidget with the DataFrame data
		for row in range(self._director.evaluations_active.nreferent):
			for col in range(ncols):
				match col:
					case 0:
						temp_dataframe: pd.DataFrame = \
							self._director.configuration_active.eigen
						item = QTableWidgetItem(
							f"{temp_dataframe.iloc[row, 0]:6.4f}")
						item.setTextAlignment(
							QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)
						table_widget.setItem(row, col, item)
					case 1:
						temp_dataframe = \
							self._director.configuration_active.eigen_common
						item = QTableWidgetItem(
							f"{temp_dataframe.iloc[row, 0]:6.4f}")
						item.setTextAlignment(
							QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)
						table_widget.setItem(row, col, item)
					case 2:
						temp_dataframe = \
							self._director.configuration_active.commonalities
						item = QTableWidgetItem(
							f"{temp_dataframe.iloc[row, 0]:6.4f}")
						item.setTextAlignment(
							QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)
						table_widget.setItem(row, col, item)
					case 3:
						temp_dataframe = \
							self._director.configuration_active.uniquenesses
						item = QTableWidgetItem(
							f"{temp_dataframe.iiloc[row, 0]:6.4f}")
						item.setTextAlignment(
							QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)
						table_widget.setItem(row, col, item)
					case 4:
						item = QTableWidgetItem(
							self._director.evaluations_active.item_names[row])
						item.setTextAlignment(
							QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
						table_widget.setItem(row, col, item)
					case 5:
						temp_dataframe = \
							self._director.configuration_active.loadings
						item = QTableWidgetItem(
							f"{temp_dataframe.iloc[row, 0]:6.4f}")
						item.setTextAlignment(
							QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)
						table_widget.setItem(row, col, item)
					case 6:
						temp_dataframe = \
							self._director.configuration_active.loadings
						item = QTableWidgetItem(
							f"{temp_dataframe.iloc[row, 1]:6.4f}")
						item.setTextAlignment(
							QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)
						table_widget.setItem(row, col, item)
		return table_widget

	# ------------------------------------------------------------------------


class MDSCommand:
	"""The MDS command performs multidimensional scaling
	on the active configuration. An initial configuration and
	similarities have to have been established.
	"""
	def __init__(
			self,
			director: Status,
			common: Spaces) -> None:

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
			common, # noqa: ANN001, ARG002
			use_metric: bool=False) -> None: # noqa: FBT001, FBT002
		
		self._director.record_command_as_selected_and_in_process()
		self._director.optionally_explain_what_command_does()
		self._director.dependency_checker.detect_dependency_problems()
		self._director.configuration_active.use_metric = use_metric
		self._get_n_components_to_use_from_user(
			self._mds_components_title, self._mds_components_label,
			self._mds_components_min_allowed, self._mds_components_max_allowed,
			self._mds_components_default, self._mds_components_an_integer)
		self._perform_mds_pick_up_point_labelling_from_similarities()
		ndim = self._director.configuration_active.ndim
		npoint = self._director.configuration_active.npoint
		best_stress = self._director.configuration_active.best_stress
		self._director.configuration_active.inter_point_distances()
		self._director.similarities_active.\
			rank_when_similarities_match_configuration(
				self._director, self.common)
		self._print_best_stress(ndim, best_stress)
		self._director.rivalry.create_or_revise_rivalry_attributes(
			self._director, self.common)
		self._director.configuration_active.print_active_function()
		self._director.common.create_plot_for_plot_and_gallery_tabs(
			"configuration")
		self._director.title_for_table_widget = (
			f"Configuration has  {ndim} dimensions and "
			f"{npoint} points and stress of {best_stress: 6.4f}")
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.record_command_as_successfully_completed()
		return

# --------------------------------------------------------------------------

	def _get_n_components_to_use_from_user_initialize_variables(self) -> None:

		self.missing_n_components_error_title = self._director.command
		self.missing_n_components_error_message = \
			"Need number of components to use."
		
# --------------------------------------------------------------------------

	def _get_n_components_to_use_from_user(
		self, mds_components_title: str, mds_components_label: str,
		mds_components_min_allowed: int, mds_components_max_allowed: int,
		mds_components_default: float,
		mds_components_an_integer: bool) -> None: # noqa: FBT001

		self._get_n_components_to_use_from_user_initialize_variables()
		dialog = SetValueDialog(
			mds_components_title, mds_components_label,
			mds_components_min_allowed, mds_components_max_allowed,
			mds_components_an_integer, mds_components_default)
		result = dialog.exec()
		if result == QDialog.Accepted:
			self._director.configuration_active.n_comp = dialog.getValue()
		else:
			raise MissingInformationError(
				self.missing_n_components_error_title,
				self.missing_n_components_error_message)
		if self._director.configuration_active.n_comp == 0:
			raise MissingInformationError(
				self.missing_n_components_error_title,
				self.missing_n_components_error_message)
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
			n_comp, use_metric, similarities_instance)

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

		self._director.configuration_active.point_coords = \
			configuration_instance.point_coords

		self._director.rivalry.create_or_revise_rivalry_attributes(
			self._director, self.common)

		return

# ------------------------------------------------------------------------

	def _print_best_stress(
			self,
			ndim: int,
			best_stress: float) -> None:
		
		print(f"Best stress in {ndim} dimensions:    {best_stress: 6.4}\n")

		return

	# ------------------------------------------------------------------------


class PrincipalComponentsCommand:
	""" The Principal components command
	"""
	def __init__(
			self,
			director: Status,
			common: Spaces) -> None:

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

	def execute(
			self,
			common: Spaces) -> None: # noqa: ARG002

		self._director.record_command_as_selected_and_in_process()
		self._director.optionally_explain_what_command_does()
		self._director.dependency_checker.detect_dependency_problems()
		(pca_transformer,
			X_pca_transformed, # noqa:N806
			x_pca_trans, transpose, trans) = \
			self._perform_principal_component_analysis()
		self._establish_principal_components_as_active_configuration(trans)
		self._establish_pca_results_as_scores(X_pca_transformed)
		self._print_pca(
			pca_transformer,
			X_pca_transformed,
			x_pca_trans, transpose)
		# Display scree diagram showing eigenvalues by dimensionality
		# Ask user how many dimensions to be retained
		# Display configuration with vectors from origin to each point
		self._director.common.create_plot_for_plot_and_gallery_tabs(
			"configuration")
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.record_command_as_successfully_completed()
		print(f"DEBUG -- at bottom of PrincipalComponentsCommand"
			f" {self._director.configuration_active.point_coords=}")
		return

	# ------------------------------------------------------------------------

	def _perform_principal_component_analysis(self) -> tuple:

		item_names = self._director.evaluations_active.item_names

		X_pca = self._director.evaluations_active.evaluations # noqa: N806
		pca_transformer = PCA(n_components=2, copy=True, random_state=0)
		X_pca_transformed = pca_transformer.fit_transform(X_pca) # noqa: N806
		pd.set_option('display.max_columns', None)
		pd.set_option('display.precision', 2)
		pd.set_option('display.max_colwidth', 300)
		components = pd.DataFrame(
			pca_transformer.components_,
			index=pca_transformer.get_feature_names_out(),
			columns=item_names)
		x_pca_trans = pd.DataFrame(
			X_pca_transformed,
			columns=pca_transformer.get_feature_names_out())
		self._director.configuration_active.pca_covar = pd.DataFrame(
			pca_transformer.get_covariance(),
			columns=item_names,
			index=item_names)
		transpose = components.transpose()
		trans = pd.DataFrame(transpose)
		return (
			pca_transformer, X_pca_transformed, x_pca_trans, transpose,
			trans)

	# ------------------------------------------------------------------------

	def _establish_principal_components_as_active_configuration(
			self,
			trans: pd.DataFrame) -> None:
		"""Establish the principal components as the active configuration.
		"""
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
			dim_labels.append("CO"+str(each_dim))
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
			self,
			X_pca_transformed: np.array) -> None: # noqa: N803

		score_1_name = self._director.configuration_active.dim_names[0]
		score_2_name = self._director.configuration_active.dim_names[1]
		hor_axis_name = self._director.configuration_active.dim_names[0]
		vert_axis_name = self._director.configuration_active.dim_names[1]
		dim_names = self._director.configuration_active.dim_names
			
		scores = pd.DataFrame(X_pca_transformed, columns=dim_names)
		scores.reset_index(inplace=True)
		scores.rename(columns={'index': 'Resp no'}, inplace=True)

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
			X_pca_transformed: np.array, # noqa: N803
			x_pca_trans: pd.DataFrame,
			transpose: pd.DataFrame) -> None:

		pca_covar = self._director.configuration_active.pca_covar
		point_coords = self._director.configuration_active.point_coords
		scores = self._director.configuration_active.scores

		print("\n\t", pca_transformer)
		print("X_pca_transformed.shape: ", X_pca_transformed.shape)
		print("X_pca_Trans: \n", x_pca_trans)
		print("pca_transformer.get_params(): \n", pca_transformer.get_params())
		print(
			"pca_transformer.get_feature_names_out(): ",
			pca_transformer.get_feature_names_out())
		print("PCA Covariance: \n", pca_covar)
		print("\nTranspose: \n", transpose)
		print("\nPoint_coords: \n", point_coords)
		print(f"\nScores from components\n {scores=}")
		return

# --------------------------------------------------------------------------


class VectorsCommand:
	""" The Vectors command plots the active configuration using vectors.
	"""
	def __init__(
			self,
			director: Status,
			common: Spaces) -> None:

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

	def execute(
			self,
			common: Spaces) -> None:  # noqa: ARG002

		self._director.record_command_as_selected_and_in_process()
		self._director.optionally_explain_what_command_does()
		self._director.dependency_checker.detect_dependency_problems()
		self._director.configuration_active.print_active_function()
		self._director.common.create_plot_for_plot_and_gallery_tabs("vectors")
		ndim = self._director.configuration_active.ndim
		npoint = self._director.configuration_active.npoint
		self._director.title_for_table_widget = (
			f"Vectors are based on the active configuration "
			f"which has {ndim} dimensions and {npoint} points")
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.record_command_as_successfully_completed()
		return

	# ------------------------------------------------------------------------

	def compute_vector_length_angle_and_angle_degree(
			self,
			x: float,
			y: float) -> tuple[float, float, float]:
		
		length = np.sqrt(x ** 2 + y ** 2)
		angle = np.arctan2(y, x)
		angle_degree = np.rad2deg(angle)
		return length, angle, angle_degree

# --------------------------------------------------------------------------


class UncertaintyAnalysis:

	def __init__(
			self,
			director: Status) -> None:

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
		self.number_of_repetitions: int = 0
		self.probability_of_inclusion: float = 0.0
		self.sample_design: pd.DataFrame = pd.DataFrame()
		self.sample_design_frequencies: pd.DataFrame = pd.DataFrame()
		self.sample_repetitions: pd.DataFrame = pd.DataFrame()
		self.sample_repetitions_stress: list[float] = []
		self.repetitions_stress_df: pd.DataFrame = pd.DataFrame()
		self.sample_solutions: pd.DataFrame = pd.DataFrame()
		self.ndim: int = 0
		self.npoint: int = 0
		self.nsolutions: int = 0
		self.dim_names: list[str] = []
		self.dim_labels: list[str] = []
		self.point_names: list[str] = []
		self.point_labels: list[str] = []
		self.target_out: np.ndarray = np.array([])
		self.repetitions_rotated: pd.DataFrame = pd.DataFrame()




	# ------------------------------------------------------------------------

	def create_table_widget_for_sample_designer(self) -> QTableWidget:

		nrepetitions = self._director.uncertainty_active.number_of_repetitions
		repetition_freqs = self._director.uncertainty_active. \
			sample_design_frequencies
		universe_size = self._director.uncertainty_active.universe_size

		table_widget = QTableWidget(nrepetitions, 5)

		for each_repetition in range(1, nrepetitions + 1):

			_repetition_selected = (
				(repetition_freqs['Repetition'] == each_repetition)
				& (repetition_freqs['Selected']))
			_repetition_not_selected = (
				(repetition_freqs['Repetition'] == each_repetition)
				& (~repetition_freqs['Selected']))

			value_1 = f"{each_repetition}"
			item_1 = QTableWidgetItem(value_1)
			item_1.setTextAlignment(QtCore.Qt.AlignCenter)
			table_widget.setItem(
				each_repetition - 1, 0, QTableWidgetItem(item_1))

			if repetition_freqs.loc[_repetition_selected]['Count'].empty:
				value_2 = "0"
				percent_value_2 = 0.0
			else:
				value_2 = \
					f"{repetition_freqs.loc[\
						_repetition_selected]['Count'].to_numpy()[0]}"
				percent_value_2 = (
					repetition_freqs.loc[\
						_repetition_selected]['Count'].to_numpy()[0]
					/ universe_size)
			item_2 = QTableWidgetItem(value_2)
			item_2.setTextAlignment(QtCore.Qt.AlignCenter)
			table_widget.setItem(
				each_repetition - 1, 1, QTableWidgetItem(item_2))
			value_3 = f"{percent_value_2:.2%}"
			item_3 = QTableWidgetItem(value_3)
			item_3.setTextAlignment(QtCore.Qt.AlignCenter)
			table_widget.setItem(
				each_repetition - 1, 2, QTableWidgetItem(item_3))
			if repetition_freqs.loc[_repetition_not_selected]['Count'].empty:
				value_4 = "0"
				percent_value_4 = 0.0
			else:
				value_4 = \
					f"{repetition_freqs.loc[\
						_repetition_not_selected]['Count'].to_numpy()[0]}"
				percent_value_4 = repetition_freqs.\
					loc[_repetition_not_selected]['Count'].to_numpy()[0] \
					/ universe_size
			item_4 = QTableWidgetItem(value_4)
			item_4.setTextAlignment(QtCore.Qt.AlignCenter)
			table_widget.setItem(
				each_repetition - 1, 3, QTableWidgetItem(item_4))
			value_5 = f"{percent_value_4:.2%}"
			item_5 = QTableWidgetItem(value_5)
			item_5.setTextAlignment(QtCore.Qt.AlignCenter)
			table_widget.setItem(
				each_repetition - 1, 4, QTableWidgetItem(item_5))
			
		return table_widget

	# ------------------------------------------------------------------------


class UncertaintyCommand:

	def __init__(
			self,
			director: Status,
			common: Spaces) -> None:

		self._director = director
		self.common = common
		self._director.command = "Uncertainty"

		self.repetitions_rotated: pd.DataFrame = pd.DataFrame(
			columns=[self._director.target_active.dim_names])
		self.repetitions_rotated: pd.DataFrame = pd.DataFrame()
		self._director.uncertainty_active.sample_solutions: pd.DataFrame = \
			pd.DataFrame()
		self.target_out: np.array = np.array([])
		self.active_out: np.array = np.array([])
		self.target_adjusted = TargetFeature(self._director)

		return

# --------------------------------------------------------------------------

	def execute(
			self,
			common: Spaces) -> None:

		peek("DEBUG -- at top of UncertaintyCommand execute")
		sample_repetitions = \
			self._director.uncertainty_active.sample_repetitions
		nreferent = self._director.evaluations_active.nreferent

		self._director.record_command_as_selected_and_in_process()
		self._director.optionally_explain_what_command_does()
		self._director.dependency_checker.detect_dependency_problems()

		self.target_out, self.active_out = self._get_repetition_mds_solutions(
			common, sample_repetitions, nreferent)
		self._director.uncertainty_active.target_out = self.target_out
		self._director.uncertainty_active.repetitions_rotated = \
			self.repetitions_rotated
		self._director.uncertainty_active.sample_solutions = \
			self.repetitions_rotated
		peek("DEBUG -- after _get_repetition_mds_solutions - solutions")
		peek(f"{self._director.uncertainty_active.sample_solutions}")
		self.common.create_uncertainty_table()

		print(self._director.uncertainty_active.repetitions_stress_df.\
			to_string(index=False))
		peek("DEBUG -- after _get_repetition_mds_solutions\n")
		self._director.common.create_plot_for_plot_and_gallery_tabs(
			"uncertainty")
		peek("DEBUG -- after create_plot_for_plot_and_gallery_tabs")
		self._director.title_for_table_widget = (
			"An ellipse around each point delineates with 95% confidence that "
			"the point lies within that point's ellipse")
		self._director.create_widgets_for_output_and_log_tabs()
		self._director.set_focus_on_tab('Plot')
		self._director.record_command_as_successfully_completed()

		return

# --------------------------------------------------------------------------

	def _get_repetition_mds_solutions(
			self,
			common: Spaces,
			sample_repetitions: pd.DataFrame,
			nreferent: int) -> tuple[np.array, np.array]:

		director = self._director
		configuration_active = director.configuration_active
		target_active = director.target_active
		uncertainty_active = director.uncertainty_active
		dim_names = target_active.dim_names
		# dim_labels = target_active.dim_labels
		self.ndim = target_active.ndim
		repetition_freqs = \
			uncertainty_active.sample_design_frequencies
		nrepetitions = uncertainty_active.number_of_repetitions
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
			range_repetitions, repetition_freqs)

		start_case = 0
		extract_ndim = 2
		repetition_n = 1
		for repetition_size in repetition_sizes:

			(current_repetition, start_case) = self.get_current_repetition(
				start_case, repetition_size, sample_repetitions,
				nreferent, item_names, item_labels)

			line_of_sight = self._director.common.los(current_repetition)
			self.duplicate_repetition_line_of_sight(common, line_of_sight)

			the_loadings = self._director.common.mds(
				extract_ndim, use_metric, line_of_sight)

			uncertainty_active.sample_repetitions_stress.append(
				the_loadings.best_stress)

			active_in = np.array(the_loadings.point_coords)

			target_in = np.array(target_active.point_coords)

			target_out, active_out, disparity = \
				procrustes(target_in, active_in)

			active_out_as_df = pd.DataFrame(active_out)
			# print(f"\nDEBUG -- in _get_repetition after procrustes plus "
			# 	f"\nactive_out_as_df: \n{active_out_as_df}")
			self.repetitions_rotated = pd.concat(
				[self.repetitions_rotated, active_out_as_df], ignore_index=True
			)

			# start_case = end_case
			repetition_n += 1

		repetitions_rotated_columns = dim_names

		self.target_out = target_out
		self.active_out = active_out

		self.target_last = target_out
		self.repetitions_rotated.columns = repetitions_rotated_columns
		target_active = self._director.target_active

		self.establish_sample_solutions_info()

		# uncertainty_active.nrepetitions = nrepetitions

		# peek("At end of _get_repetition_mds_solutions\n",
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
		uncertainty_active.point_coords = \
			uncertainty_active.repetitions_rotated
		uncertainty_active.npoints = target_active.npoint
		uncertainty_active.ndim = target_active.ndim
		uncertainty_active.dim_names = target_active.dim_names
		uncertainty_active.dim_labels = target_active.dim_labels
		uncertainty_active.point_names = target_active.point_names
		uncertainty_active.point_labels = target_active.point_labels
		uncertainty_active.nsolutions = \
			uncertainty_active.number_of_repetitions
		
		return
# -------------------------------------------------------------------------

	def get_repetition_sizes(
			self,
			range_repetitions: range,
			repetition_freqs: pd.DataFrame) -> list[int]:

		repetition_sizes = []
		for each_repetition in range_repetitions:
			row_with_repetition_size: int = (each_repetition * 2) + 1
			column_with_repetition_size: int = 2
			size = repetition_freqs \
				.iloc[row_with_repetition_size, column_with_repetition_size]
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
			item_labels:list[str]) -> \
				tuple[EvaluationsFeature, int]:
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
			self._director)
		current_repetition.evaluations = sample_repetitions.iloc[
			start_case:end_case]
		current_repetition.nreferent = nreferent
		current_repetition.item_names = item_names
		current_repetition.item_labels = item_labels
		current_repetition.nevaluators = repetition_size
		start_case = end_case + 1
		return current_repetition, start_case

# -------------------------------------------------------------------------

	def duplicate_repetition_line_of_sight(
			self,
			common: Spaces,
			line_of_sight: SimilaritiesFeature) -> None:

		(
			line_of_sight.similarities_as_dataframe,
			line_of_sight.similarities_as_dict,
			line_of_sight.similarities_as_list,
			line_of_sight.similarities_as_square,
			line_of_sight.sorted_similarities_w_pairs,
			line_of_sight.ndyad,
			line_of_sight.range_dyads,
			line_of_sight.range_items) = \
			common.duplicate_in_different_structures(
				line_of_sight.similarities,
				line_of_sight.item_names,
				line_of_sight.item_labels,
				line_of_sight.nitem,
				line_of_sight.value_type)

	# ------------------------------------------------------------------------

	def _display(self) -> QTableWidget:
		
		table_widget = StatisticalTableWidget(self._director)
		gui_output_as_widget = table_widget.display_table("uncertainty")
		
		self._director.output_widget_type = "Table"
		return gui_output_as_widget

