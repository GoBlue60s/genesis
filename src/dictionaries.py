from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING

from constants import (
	MINIMUM_ALLOWABLE_CUT_OFF,
	MAXIMUM_ALLOWABLE_CUT_OFF,
	DEFAULT_ALLOWABLE_CUT_OFF,
	IS_CUTOFF_AN_INTEGER,
)

if TYPE_CHECKING:
	from director import Status

# Type alias for immutable dictionaries
FrozenDict = MappingProxyType


# ----------------------------------------------------------------------------
# Dictionary: command_dict
# Source: director.py lines 936-977 (active_commands, interactive_only_commands, script_commands, passive_commands)
# Purpose: Command classification and undo metadata for all 108 commands
#          (40 active + 2 interactive_only + 3 script + 63 passive)
# ----------------------------------------------------------------------------

command_dict = MappingProxyType({
	"About": {
		"type": "passive",
		"state_capture": [],
		"script_parameters": []
	},
	"Alike": {
		"type": "passive",
		"state_capture": [],  # Passive command - no state changes
		"script_parameters": ["cutoff"],
		"interactive_getters": {
			"cutoff": {
				"getter_type": "set_value_dialog",
				"title": "Set cutoff level",
				"label": (
					"If similarities, minimum similarity points alike"
					"\nIf dis/similarities, maximum dis/similarity"
				),
				"min_val": MINIMUM_ALLOWABLE_CUT_OFF,
				"max_val": MAXIMUM_ALLOWABLE_CUT_OFF,
				"is_integer": IS_CUTOFF_AN_INTEGER,
				"default": DEFAULT_ALLOWABLE_CUT_OFF
			}
		}
	},
	"Base": {
		"type": "passive"
	},
	"Battleground": {
		"type": "passive"
	},
	"Center": {
		"type": "active",
		"state_capture": ["configuration", "scores", "rivalry"],
		"script_parameters": []
	},
	"Cluster": {
		"type": "active",
		"state_capture": ["conditional"],  # Conditional: scores + (configuration|evaluations|similarities) based on user's data source
		"script_parameters": ["data_source", "n_clusters"],
		"interactive_getters": {
			"data_source": {
				"getter_type": "chose_option_dialog",
				"title": "Select Data Source for Clustering",
				"options_title": "Choose which data source to use for clustering",
				"options": ["distances", "evaluations", "scores", "similarities"]
			},
			"n_clusters": {
				"getter_type": "set_value_dialog",
				"title": "Cluster Analysis",
				"label": "Number of clusters to extract:",
				"min_val": 2,
				"max_val": 15,  # Will be dynamically adjusted based on data
				"is_integer": True,
				"default": 2
			}
		}
	},
	"Compare": {
		"type": "active",
		"state_capture": ["configuration", "target", "scores", "rivalry"],
		"script_parameters": []
	},
	"Configuration": {
		"type": "active",
		"state_capture": ["configuration"],
		"script_parameters": ["file"],
		"interactive_getters": {
			"file": {
				"getter_type": "file_dialog",
				"caption": "Open configuration",
				"filter": "*.txt"
			}
		}
	},
	"Contest": {
		"type": "passive",
		"state_capture": [],
		"script_parameters": []
	},
	"Convertible": {
		"type": "passive"
	},
	"Core supporters": {
		"type": "passive"
	},
	"Correlations": {
		"type": "active",
		"state_capture": ["correlations"],
		"script_parameters": ["file"],
		"interactive_getters": {
			"file": {
				"getter_type": "file_dialog",
				"caption": "Open correlations",
				"filter": "*.txt"
			}
		}
	},
	"Create": {
		"type": "interactive_only",
		"state_capture": ["configuration"]
	},
	"Deactivate": {
		"type": "active",
		"state_capture": ["conditional"]  # Conditional: captures state for each item user selects to deactivate
	},
	"Directions": {
		"type": "passive",
		"state_capture": [],
		"script_parameters": []
	},
	"Distances": {
		"type": "passive",
		"state_capture": [],
		"script_parameters": []
	},
	"Evaluations": {
		"type": "active",
		"state_capture": ["evaluations", "correlations"],
		"script_parameters": ["file"],
		"interactive_getters": {
			"file": {
				"getter_type": "file_dialog",
				"caption": "Open evaluations",
				"filter": "*.csv"
			}
		}
	},
	"Exit": {
		"type": "passive",
		"state_capture": [],
		"script_parameters": []
	},
	"Factor analysis": {
		"type": "active",
		"state_capture": ["configuration", "scores", "evaluations"],
		"script_parameters": ["n_factors"],
		"interactive_getters": {
			"n_factors": {
				"getter_type": "set_value_dialog",
				"title": "Factor analysis",
				"label": "Number of factors to extract:",
				"min_val": 1,
				"max_val": None,  # Dynamic: evaluations_active.nreferent
				"is_integer": True,
				"default": 2
			}
		}
	},
	"Factor analysis machine learning": {
		"type": "active",
		"state_capture": ["configuration", "scores", "evaluations"],
		"script_parameters": ["n_components"],
		"interactive_getters": {
			"n_components": {
				"getter_type": "set_value_dialog",
				"title": "Factor Analysis",
				"label": "Number of factors to extract:",
				"min_val": 1,
				"max_val": None,  # Dynamic: evaluations_active.nitem
				"is_integer": True,
				"default": 2
			}
		}
	},
	"First dimension": {
		"type": "passive"
	},
	"Grouped data": {
		"type": "active",
		"state_capture": ["grouped_data"],
		"script_parameters": ["file"],
		"interactive_getters": {
			"file": {
				"getter_type": "file_dialog",
				"caption": "Open grouped data",
				"filter": "*.txt"
			}
		}
	},
	"Help": {
		"type": "passive",
		"state_capture": [],
		"script_parameters": []
	},
	"History": {
		"type": "passive",
		"state_capture": [],
		"script_parameters": []
	},
	"Individuals": {
		"type": "active",
		"state_capture": ["individuals"],
		"script_parameters": ["file"],
		"interactive_getters": {
			"file": {
				"getter_type": "file_dialog",
				"caption": "Open individuals",
				"filter": "*.csv"
			}
		}
	},
	"Invert": {
		"type": "active",
		"state_capture": ["configuration", "scores", "rivalry"],
		"script_parameters": ["dimensions"],
		"interactive_getters": {
			"dimensions": {
				"getter_type": "modify_items_dialog",
				"title": "Select dimensions to invert",
				"items_source": "configuration_active.dim_names",
				"default_values": None
			}
		}
	},
	"Joint": {
		"type": "passive",
		"state_capture": [],
		"script_parameters": []
	},
	"Likely supporters": {
		"type": "passive"
	},
	"Line of sight": {
		"type": "active",
		"state_capture": ["similarities"],
		"script_parameters": []
	},
	"MDS": {
		"type": "active",
		"state_capture": ["configuration", "rivalry"],
		"script_parameters": ["n_components", "use_metric"],
		"execute_parameters": ["use_metric"],
		"interactive_getters": {
			"n_components": {
				"getter_type": "set_value_dialog",
				"title": "Components to extract",
				"label": "Set number of components to extract",
				"min_val": 1,
				"max_val": 10,
				"is_integer": True,
				"default": 2
			}
		}
	},
	"Move": {
		"type": "active",
		"state_capture": ["configuration", "scores", "rivalry"],
		"script_parameters": ["dimension", "distance"]
	},
	"New grouped data": {
		"type": "interactive_only",
		"state_capture": ["grouped_data"]
	},
	"Open sample design": {
		"type": "active",
		"state_capture": ["uncertainty"],
		"script_parameters": ["file"],
		"interactive_getters": {
			"file": {
				"getter_type": "file_dialog",
				"caption": "Open sample design",
				"filter": "*.txt"
			}
		}
	},
	"Open sample repetitions": {
		"type": "active",
		"state_capture": ["uncertainty"],
		"script_parameters": ["file"],
		"interactive_getters": {
			"file": {
				"getter_type": "file_dialog",
				"caption": "Open sample repetitions",
				"filter": "*.txt"
			}
		}
	},
	"Open sample solutions": {
		"type": "active",
		"state_capture": ["uncertainty"],
		"script_parameters": ["file"],
		"interactive_getters": {
			"file": {
				"getter_type": "file_dialog",
				"caption": "Open sample solutions",
				"filter": "*.txt"
			}
		}
	},
	"Open scores": {
		"type": "active",
		"state_capture": ["scores"],
		"script_parameters": ["file"],
		"interactive_getters": {
			"file": {
				"getter_type": "file_dialog",
				"caption": "Open scores",
				"filter": "*.csv"
			}
		}
	},
	"Open script": {
		"type": "script"  # Meta-command for script operations
	},
	"Paired": {
		"type": "passive",
		"state_capture": [],  # Passive command - no state changes
		"script_parameters": ["focus"],
		"interactive_getters": {
			"focus": {
				"getter_type": "focal_item_dialog",
				"title": "Point comparisons",
				"label": "Select point to view relationships with others",
				"items_source": "configuration_active.point_names"
			}
		}
	},
	"Principal components": {
		"type": "active",
		"state_capture": ["configuration"],
		"script_parameters": ["n_components"],
		"interactive_getters": {
			"n_components": {
				"getter_type": "set_value_dialog",
				"title": "Principal components",
				"label": "Number of components to extract:",
				"min_val": 1,
				"max_val": None,  # Dynamic: based on data
				"is_integer": True,
				"default": 2
			}
		}
	},
	"Print configuration": {
		"type": "passive",
		"state_capture": [],
		"script_parameters": []
	},
	"Print correlations": {
		"type": "passive",
		"state_capture": [],
		"script_parameters": []
	},
	"Print evaluations": {
		"type": "passive",
		"state_capture": [],
		"script_parameters": []
	},
	"Print grouped data": {
		"type": "passive",
		"state_capture": [],
		"script_parameters": []
	},
	"Print individuals": {
		"type": "passive",
		"state_capture": [],
		"script_parameters": []
	},
	"Print sample design": {
		"type": "passive",
		"state_capture": [],
		"script_parameters": []
	},
	"Print sample repetitions": {
		"type": "passive",
		"state_capture": [],
		"script_parameters": []
	},
	"Print sample solutions": {
		"type": "passive",
		"state_capture": [],
		"script_parameters": []
	},
	"Print scores": {
		"type": "passive",
		"state_capture": [],
		"script_parameters": []
	},
	"Print similarities": {
		"type": "passive",
		"state_capture": [],
		"script_parameters": []
	},
	"Print target": {
		"type": "passive",
		"state_capture": [],
		"script_parameters": []
	},
	"Ranks differences": {
		"type": "passive",
		"state_capture": [],
		"script_parameters": []
	},
	"Ranks distances": {
		"type": "passive",
		"state_capture": [],
		"script_parameters": []
	},
	"Ranks similarities": {
		"type": "passive",
		"state_capture": [],
		"script_parameters": []
	},
	"Redo": {
		"type": "active",
		"state_capture": []  # N/A - Meta-command that manages redo stack
	},
	"Reference points": {
		"type": "active",
		"state_capture": ["rivalry"],
		"script_parameters": ["contest"],
		"interactive_getters": {
			"contest": {
				"getter_type": "pair_of_points_dialog",
				"title": "Select a pair of reference points",
				"items_source": "configuration_active.point_names"
			}
		}
	},
	"Rescale": {
		"type": "active",
		"state_capture": ["configuration", "scores", "rivalry"],
		"script_parameters": ["factors"],
		"interactive_getters": {
			"factors": {
				"getter_type": "modify_values_dialog",
				"title": "Rescale configuration",
				"items_source": "configuration_active.dim_names",
				"label": "Amount by which to multiple every point \non selected dimensions",
				"min_val": -9999.9,
				"max_val": 9999.9,
				"is_integer": False,
				"default": 0.0
			}
		}
	},
	"Rotate": {
		"type": "active",
		"state_capture": ["configuration", "scores", "rivalry"],
		"script_parameters": ["degrees"],
		"interactive_getters": {
			"degrees": {
				"getter_type": "set_value_dialog",
				"title": "Degree to rotate configuration",
				"label": \
					"Positive is counter-clockwise\nNegative is clockwise",
				"min_val": -360,
				"max_val": 360,
				"default": 0,
				"is_integer": True
			}
		}
	},
	"Sample designer": {
		"type": "active",
		"state_capture": ["uncertainty"],
		"script_parameters": ["probability_of_inclusion", "nrepetitions"],
		"interactive_getters": {
			"sample_parameters": {
				"getter_type": "modify_values_dialog",
				"title": "Set sample parameters",
				"labels": [
					"Probability of inclusion",
					"Number of repetitions"
				],
				"is_integer": True,
				"defaults": [50, 2],
				"boolean_params": ["probability_of_inclusion", "nrepetitions"]
			}
		}
	},
	"Sample repetitions": {
		"type": "active",
		"state_capture": ["uncertainty"],
		"script_parameters": []
	},
	"Save configuration": {
		"type": "passive",
		"state_capture": [],
		"script_parameters": ["file"],
		"interactive_getters": {
			"file": {
				"getter_type": "file_dialog",
				"caption": "Save active configuration",
				"filter": "*.txt",
				"mode": "save",
				"directory": "data"
			}
		}
	},
	"Save correlations": {
		"type": "passive",
		"state_capture": [],
		"script_parameters": ["file"],
		"interactive_getters": {
			"file": {
				"getter_type": "file_dialog",
				"caption": "Save active correlations",
				"filter": "*.csv",
				"mode": "save",
				"directory": "data"
			}
		}
	},
	"Save grouped data": {
		"type": "passive",
		"state_capture": [],
		"script_parameters": ["file"],
		"interactive_getters": {
			"file": {
				"getter_type": "file_dialog",
				"caption": "Save active grouped data",
				"filter": "*.txt",
				"mode": "save",
				"directory": "data"
			}
		}
	},
	"Save individuals": {
		"type": "passive",
		"state_capture": [],
		"script_parameters": ["file"],
		"interactive_getters": {
			"file": {
				"getter_type": "file_dialog",
				"caption": "Save active individuals",
				"filter": "*.csv",
				"mode": "save",
				"directory": "data"
			}
		}
	},
	"Save sample design": {
		"type": "passive",
		"state_capture": [],
		"script_parameters": ["file"],
		"interactive_getters": {
			"file": {
				"getter_type": "file_dialog",
				"caption": "Save active sample design",
				"filter": "*.txt",
				"mode": "save",
				"directory": "data"
			}
		}
	},
	"Save sample repetitions": {
		"type": "passive",
		"state_capture": [],
		"script_parameters": ["file"],
		"interactive_getters": {
			"file": {
				"getter_type": "file_dialog",
				"caption": "Save active sample repetitions",
				"filter": "*.txt",
				"mode": "save",
				"directory": "data"
			}
		}
	},
	"Save sample solutions": {
		"type": "passive",
		"state_capture": [],
		"script_parameters": ["file"],
		"interactive_getters": {
			"file": {
				"getter_type": "file_dialog",
				"caption": "Save active sample solutions",
				"filter": "*.txt",
				"mode": "save",
				"directory": "data"
			}
		}
	},
	"Save scores": {
		"type": "passive",
		"state_capture": [],
		"script_parameters": ["file"],
		"interactive_getters": {
			"file": {
				"getter_type": "file_dialog",
				"caption": "Save active scores",
				"filter": "*.csv",
				"mode": "save",
				"directory": "data"
			}
		}
	},
	"Save similarities": {
		"type": "passive",
		"state_capture": [],
		"script_parameters": ["file"],
		"interactive_getters": {
			"file": {
				"getter_type": "file_dialog",
				"caption": "Save active similarities",
				"filter": "*.txt",
				"mode": "save",
				"directory": "data"
			}
		}
	},
	"Save target": {
		"type": "passive",
		"state_capture": [],
		"script_parameters": ["file"],
		"interactive_getters": {
			"file": {
				"getter_type": "file_dialog",
				"caption": "Save active target",
				"filter": "*.txt",
				"mode": "save",
				"directory": "data"
			}
		}
	},
	"Save script": {
		"type": "script"  # Meta-command for script operations
	},
	"Score individuals": {
		"type": "active",
		"state_capture": ["scores", "rivalry"],
		"script_parameters": []
	},
	"Scree": {
		"type": "passive",
		"state_capture": [],
		"script_parameters": ["use_metric"],
		"execute_parameters": ["use_metric"],
		"interactive_getters": {
			"use_metric": {
				"getter_type": "option",
				"title": "MDS model",
				"prompt": "Model to use",
				"options": ["Non-metric", "Metric"],
				"map_to_bool": True
			}
		}
	},
	"Second dimension": {
		"type": "passive"
	},
	"Segments": {
		"type": "passive",
		"state_capture": [],
		"script_parameters": []
	},
	"Settings - display sizing": {
		"type": "active",
		"state_capture": ["settings"],
		"script_parameters": ["axis_extra", "displacement", "point_size"],
		"interactive_getters": {
			"axis_extra": {
				"getter_type": "modify_values_dialog",
				"title": "Display sizing settings",
				"labels": ["Axis extra margin (percent of axis):", "Label displacement (percent of axis):", "Point size:"],
				"defaults_source": ["axis_extra", "displacement", "point_size"],
				"defaults_multiplier": [100, 100, 1],
				"min_val": 0,
				"max_val": 50,
				"is_integer": True,
				"boolean_params": ["axis_extra", "displacement", "point_size"]
			}
		}
	},
	"Settings - layout options": {
		"type": "active",
		"state_capture": ["settings"],
		"script_parameters": ["max_cols", "width", "decimals"],
		"interactive_getters": {
			"layout": {
				"getter_type": "modify_values_dialog",
				"title": "Layout options settings",
				"labels": ["Maximum columns:", "Column width:", "Decimal places:"],
				"min_val": 0,
				"max_val": 20,
				"is_integer": True,
				"defaults": [10, 8, 2],
				"defaults_source": ["max_cols", "width", "decimals"],
				"defaults_multiplier": 1,
				"boolean_params": ["max_cols", "width", "decimals"]
			}
		}
	},
	"Settings - plane": {
		"type": "active",
		"state_capture": ["configuration", "settings"],
		"script_parameters": ["horizontal", "vertical"],
		"interactive_getters": {
			"horizontal": {
				"getter_type": "plane_dialog",
				"title": "Settings - plane"
			}
		}
	},
	"Settings - plot settings": {
		"type": "active",
		"state_capture": ["settings"],
		"script_parameters": ["bisector", "connector",
		"reference_points", "just_reference_points"],
		"interactive_getters": {
			"_plot_settings_checkboxes": {
				"getter_type": "modify_items_dialog",
				"title": "Plot settings",
				"items": ["Show bisector", "Show connector", "Show reference points", "Show just reference points"],
				"defaults_source": ["show_bisector", "show_connector", "show_reference_points", "show_just_reference_points"],
				"converts_to_booleans": True,
				"boolean_params": ["bisector", "connector", "reference_points", "just_reference_points"]
			}
		}
	},
	"Settings - presentation layer": {
		"type": "active",
		"state_capture": ["settings"],
		"script_parameters": ["layer"],
		"execute_parameters": ["layer"],
		"interactive_getters": {
			"layer": {
				"getter_type": "chose_option_dialog",
				"title": "Presentation layer settings",
				"options_title": "Select presentation layer:",
				"options": ["matplotlib", "pyqtgraph"]
			}
		}
	},
	"Settings - segment sizing": {
		"type": "active",
		"state_capture": ["settings"],
		"script_parameters": ["battleground", "core"],
		"interactive_getters": {
			"segments": {
				"getter_type": "modify_values_dialog",
				"title": "Setting percent of connector",
				"labels": ["Battleground", "Core"],
				"min_val": 0,
				"max_val": 100,
				"is_integer": True,
				"defaults": [25, 20],
				"defaults_source": ["battleground_size", "core_tolerance"],
				"defaults_multiplier": 100,
				"boolean_params": ["battleground", "core"]
			}
		}
	},
	"Settings - vector sizing": {
		"type": "active",
		"state_capture": ["settings"],
		"script_parameters": ["vector_head_width", "vector_width"],
		"interactive_getters": {
			"vectors": {
				"getter_type": "modify_values_dialog",
				"title": "Vector sizing settings",
				"labels": ["Vector head width (in inches)", "Vector width (in inches)"],
				"min_val": 0.0,
				"max_val": 1.0,
				"is_integer": False,
				"step_size": 0.01,
				"defaults": [0.05, 0.01],
				"defaults_source": ["vector_head_width", "vector_width"],
				"defaults_multiplier": 1,
				"boolean_params": ["vector_head_width", "vector_width"]
			}
		}
	},
	"Shepard": {
		"type": "passive",
		"state_capture": [],
		"script_parameters": ["axis"],
		"execute_parameters": ["axis"],
		"interactive_getters": {
			"axis": {
				"getter_type": "option",
				"title": "Shepard diagram",
				"prompt": "Show similarity on:",
				"options": ["X-axis (horizontal)", "Y-axis (vertical)"]
			}
		}
	},
	"Similarities": {
		"type": "active",
		"state_capture": ["similarities"],
		"script_parameters": ["file", "value_type"],
		"execute_parameters": ["value_type"],
		"interactive_getters": {
			"file": {
				"getter_type": "file_dialog",
				"caption": "Open similarities",
				"filter": "*.txt"
			}
		}
	},
	"Status": {
		"type": "passive",
		"state_capture": [],
		"script_parameters": []
	},
	"Stress contribution": {
		"type": "passive",
		"state_capture": [],  # Passive command - no state changes
		"script_parameters": ["focal_item"],
		"interactive_getters": {
			"focal_item": {
				"getter_type": "focal_item_dialog",
				"title": "Contribution to stress",
				"label": "Select point to see stress contribution",
				"items_source": "configuration_active.point_names"
			}
		}
	},
	"Target": {
		"type": "active",
		"state_capture": ["target"],
		"script_parameters": ["file"],
		"interactive_getters": {
			"file": {
				"getter_type": "file_dialog",
				"caption": "Open target",
				"filter": "*.txt"
			}
		}
	},
	"Terse": {
		"type": "passive",
		"state_capture": [],
		"script_parameters": []
	},
	"Tester": {
		"type": "active",
		"state_capture": []  # N/A - Experimental/debug command
	},
	"Uncertainty": {
		"type": "active",
		"state_capture": ["uncertainty"],
		"script_parameters": ["probability_of_inclusion", "nrepetitions"],
		"interactive_getters": {
			"sample_parameters": {
				"getter_type": "modify_values_dialog",
				"title": "Set sample parameters for uncertainty analysis",
				"labels": [
					"Probability of inclusion",
					"Number of repetitions"
				],
				"is_integer": True,
				"defaults": [50, 100],
				"boolean_params": ["probability_of_inclusion", "nrepetitions"]
			}
		}
	},
	"Undo": {
		"type": "active",
		"state_capture": []  # N/A - Meta-command that manages undo stack
	},
	"Varimax": {
		"type": "active",
		"state_capture": ["configuration", "scores", "rivalry"],
		"script_parameters": []
	},
	"Vectors": {
		"type": "passive",
		"state_capture": [],
		"script_parameters": []
	},
	"Verbose": {
		"type": "passive",
		"state_capture": [],
		"script_parameters": []
	},
	"View configuration": {
		"type": "passive",
		"state_capture": [],
		"script_parameters": []
	},
	"View correlations": {
		"type": "passive",
		"state_capture": [],
		"script_parameters": []
	},
	"View custom": {
		"type": "passive",
		"state_capture": [],
		"script_parameters": []
	},
	"View distances": {
		"type": "passive",
		"state_capture": [],
		"script_parameters": []
	},
	"View evaluations": {
		"type": "passive",
		"state_capture": [],
		"script_parameters": []
	},
	"View grouped data": {
		"type": "passive",
		"state_capture": [],
		"script_parameters": []
	},
	"View individuals": {
		"type": "passive",
		"state_capture": [],
		"script_parameters": []
	},
	"View point uncertainty": {
		"type": "passive",
		"state_capture": [],  # Passive command - no state changes
		"script_parameters": ["plot", "points"],
		"execute_parameters": ["plot"],
		"interactive_getters": {
			"points": {
				"getter_type": "modify_items_dialog",
				"title": "Select Points for Uncertainty Analysis",
				"items_source": "uncertainty_active.point_names"
			}
		}
	},
	"View sample design": {
		"type": "passive",
		"state_capture": [],
		"script_parameters": []
	},
	"View sample repetitions": {
		"type": "passive",
		"state_capture": [],
		"script_parameters": []
	},
	"View sample solutions": {
		"type": "passive",
		"state_capture": [],
		"script_parameters": []
	},
	"View scores": {
		"type": "passive",
		"state_capture": [],
		"script_parameters": []
	},
	"View script": {
		"type": "script"  # Meta-command for script operations
	},
	"View similarities": {
		"type": "passive",
		"state_capture": [],
		"script_parameters": []
	},
	"View spatial uncertainty": {
		"type": "passive",
		"state_capture": [],
		"script_parameters": ["plot"],
		"execute_parameters": ["plot"]
	},
	"View target": {
		"type": "passive",
		"state_capture": [],
		"script_parameters": []
	},
})


# Command class imports for request_dict and widget_dict
from associationsmenu import (
	AlikeCommand,
	DistancesCommand,
	LineOfSightCommand,
	PairedCommand,
	RanksDifferencesCommand,
	RanksDistancesCommand,
	RanksSimilaritiesCommand,
	ScreeCommand,
	ShepardCommand,
	StressContributionCommand,
)
from editmenu import (
	RedoCommand,
	UndoCommand,
)
from experimental import TesterCommand
from filemenu import (
	ConfigurationCommand,
	CorrelationsCommand,
	CreateCommand,
	DeactivateCommand,
	EvaluationsCommand,
	ExitCommand,
	GroupedDataCommand,
	IndividualsCommand,
	NewGroupedDataCommand,
	OpenSampleDesignCommand,
	OpenSampleRepetitionsCommand,
	OpenSampleSolutionsCommand,
	OpenScoresCommand,
	OpenScriptCommand,
	PrintConfigurationCommand,
	PrintCorrelationsCommand,
	PrintEvaluationsCommand,
	PrintGroupedDataCommand,
	PrintIndividualsCommand,
	PrintSampleDesignCommand,
	PrintSampleRepetitionsCommand,
	PrintSampleSolutionsCommand,
	PrintScoresCommand,
	PrintSimilaritiesCommand,
	PrintTargetCommand,
	SaveConfigurationCommand,
	SaveCorrelationsCommand,
	SaveGroupedDataCommand,
	SaveIndividualsCommand,
	SaveSampleDesignCommand,
	SaveSampleRepetitionsCommand,
	SaveSampleSolutionsCommand,
	SaveScoresCommand,
	SaveScriptCommand,
	SaveSimilaritiesCommand,
	SaveTargetCommand,
	SettingsDisplayCommand,
	SettingsLayoutCommand,
	SettingsPlaneCommand,
	SettingsPlotCommand,
	SettingsPresentationLayerCommand,
	SettingsSegmentCommand,
	SettingsVectorSizeCommand,
	SimilaritiesCommand,
	TargetCommand,
)
from helpmenu import (
	AboutCommand,
	HelpCommand,
	StatusCommand,
	TerseCommand,
	VerboseCommand,
)
from modelmenu import (
	ClusterCommand,
	DirectionsCommand,
	FactorAnalysisCommand,
	FactorAnalysisMachineLearningCommand,
	MDSCommand,
	PrincipalComponentsCommand,
	UncertaintyCommand,
	VectorsCommand,
)
from respondentsmenu import (
	BaseCommand,
	BattlegroundCommand,
	ContestCommand,
	ConvertibleCommand,
	CoreSupportersCommand,
	FirstDimensionCommand,
	JointCommand,
	LikelySupportersCommand,
	ReferencePointsCommand,
	SampleDesignerCommand,
	SampleRepetitionsCommand,
	ScoreIndividualsCommand,
	SecondDimensionCommand,
	SegmentsCommand,
)
from transformmenu import (
	CenterCommand,
	CompareCommand,
	InvertCommand,
	MoveCommand,
	RescaleCommand,
	RotateCommand,
	VarimaxCommand,
)
from viewmenu import (
	HistoryCommand,
	ViewConfigurationCommand,
	ViewCorrelationsCommand,
	ViewCustomCommand,
	ViewDistancesCommand,
	ViewEvaluationsCommand,
	ViewGroupedDataCommand,
	ViewIndividualsCommand,
	ViewPointUncertaintyCommand,
	ViewSampleDesignCommand,
	ViewSampleRepetitionsCommand,
	ViewSampleSolutionsCommand,
	ViewScoresCommand,
	ViewScriptCommand,
	ViewSimilaritiesCommand,
	ViewSpatialUncertaintyCommand,
	ViewTargetCommand,
)


# ----------------------------------------------------------------------------
# Dictionary: explain_dict
# Source: director.py lines 1848-2239
# Purpose: Command explanations for help system
# ----------------------------------------------------------------------------

explain_dict = MappingProxyType({
	"About": "About provides information about the program.",
	"Alike": "Alike can be used to place lines between points "
	"with high similarity.\n"
	"Only pairs of points with a similarity "
	"above, or a dissimilarity below, the cutoff will have "
	"a line joining the points.",
	"Base": "Base identifies regions close to the reference "
	"points in the battleground region.\n"
	"Individuals in these areas prefer these candidates.",
	"Battleground": "Battleground is used to define a region of "
	"battleground points within a tolerance "
	"from bisector between reference points.\n"
	"Individuals in these areas may be undecided.",
	"Center": "Center is used to shift points to be centered around "
	"the origin.\n"
	"This is achieved by subtracting the mean of each dimension "
	"from each coordinate.\n"
	"This is especially useful when the coordinates are latitudes "
	"and longitudes.",
	"Cluster": "Cluster used to assign points to clusters.\n"
	"The assignments can be read from a file or determined by "
	"a clustering algorithm.",
	"Compare": "Compare is used to compare the target configuration "
	"with the active configuration.\n"
	"The target configuration will be centered to facilitate "
	"comparison.\n"
	"The active configuration will be rotated and transformed "
	"to minimize the differences with the target configuration.\n"
	"A measure of the difference, disparity, will be computed.\n"
	"The result will be plotted with a line connecting "
	"corresponding points.\n"
	"The line will be labeled with the label for the point.\n"
	"The line will have zero length when the configurations "
	"match perfectly.\n"
	"The point from the rotated configuration with be labeled "
	"with an R.\n"
	"The point from the target congratulation will be labeled "
	"with a T.",
	"Configuration": "Configuration reads in a configuration file.\n"
	"The file must be formatted correctly.\n"
	"The first line should be Configuration.\n"
	"The next line should have two fields: "
	"the number of dimensions and the number of points.\n"
	"For each point: \n"
	"\tA line containing the label, a semicolon, and the "
	"full name for that point.\n"
	"\tA line with the coordinate for the point on each dimension "
	"separated by commas.",
	"Contest": "Contest identifies regions defined by the reference "
	"points.",
	"Convertible": "Convertible identifies regions where \n"
	"individuals might be converted and switch their preference.",
	"Core supporters": "Core supporters identifies regions "
	"immediately around the reference points.\n"
	"Individuals in these areas prefer these candidates the most.",
	"Correlations": "Correlations reads in a correlation matrix "
	"from a file.\n"
	"The file must be in the a format similar to to the OSIRIS "
	"format.\n"
	"The correlations may be used as similarities but more likely "
	"are used as input to Factor.\n"
	"The correlations are stored as similarities and treated as "
	"measures of similarity.",
	"Create": "Create is used to build the \nactive configuration by "
	"using user supplied information.\n"
	"In addition to creating names and labels, coordinates \n"
	"can be supplied by the user, assigned randomly, or use \n"
	"the classic approach of using the order of the points.",
	"Deactivate": "Deactivate is used to deactivate the active \n"
	"configuration, the existing target configuration, \n"
	" existing similarities, and existing correlations.",
	"Directions": "Directions is used to display a plot showing the "
	"direction of each point \n"
	"from the origin to the unit circle.",
	"Distances": "Distances displays a matrix of inter-point "
	"distances.\n"
	"Some alternatives:\n"
	"similarities could be shown above the diagonal\n"
	"optionally ranks could be displayed in place of, or in "
	"addition to, values\n"
	"information could be displayed as a table with a line for "
	"each pair of points",
	"Evaluations": "Evaluations reads in a file containing \n"
	"individual evaluations corresponding to the points in \n"
	"the active configuration.",
	"Exit": "Exit exits the program.",
	"Factor analysis": "Factor creates a factor analysis of the "
	"current correlations.\n"
	"The output is a factor matrix with as many points as in "
	"the correlation matrix.\n"
	"The plot will have vectors from the origin to each point.\n"
	"It displays a Scree diagram with the Eigenvalue for each \n"
	"dimensionality. The dimensionality on the x-axis (1-n and "
	"the Eigenvalue on the y-axis.\n"
	"It asks the user how many dimensions to retain and uses \n"
	"that to determine the number of dimensions to be retained.",
	"Factor analysis machine learning": "Factor creates a factor "
	"analysis of the "
	"current correlations.\n"
	"The output is a factor matrix with as many points as in "
	"the active configuration.\n"
	"The plot will have vectors from the origin to each point.\n"
	"It displays a Scree diagram with the Eigenvalue for each \n"
	"dimensionality. The dimensionality on the x-axis (1-n and "
	"the Eigenvalue on the y-axis.\n"
	"It asks the user how many dimensions to retain and uses \n"
	"that to determine the number of dimensions to be retained.",
	"First dimension": "First dimension identifies regions "
	"defined by the first dimension.",
	"Grouped data": "Grouped data reads in a file with coordinates"
	" for groups of on all dimensions. \n"
	"The number of groups in a file should be small.\n"
	"The number of dimensions must be the same as the active "
	"correlation.\n"
	"If reference points have been established the user can add"
	"the points and the bisector.",
	"Help": "Help displays general information about Spaces.",
	"History": "History displays a list of commands used in this "
	"session.",
	"Individuals": "Individuals is used to establish variables\n"
	"usually scores and filters for a set of individuals.",
	"Invert": "Invert inverts dimension(s).\n"
	"It asks the user which dimension(s) to invert.\n"
	"It multiples each point's coordinate on a dimension by -1.\n"
	"The resulting configuration becomes the active "
	"configuration.",
	"Joint": "Joint creates a plot including points "
	"for individuals as well as points for referents.\n"
	"The user decides whether to include the full active "
	"configuration\n"
	"or just the reference points. The user also decides whether"
	" to \n"
	"include the perpendicular bisector between the reference "
	"points.\n",
	"Likely supporters": "Likely supporters identifies regions "
	"defined by the reference points.\n"
	"Individuals in these areas are likely to prefer these "
	"candidates.",
	"Line of sight": "Line of sight computes the Line of sight "
	"measure of association. \n"
	"Line of sight is a measure of dissimilairity. "
	"It was developed by George Rabinowitz.",
	"MDS": "MDS is used to perform a metric or non-metric "
	"multi-dimensional scaling of the similarities.\n"
	"The user will be asked for the number of components"
	" to be used.\n"
	"The result of MDS will become the active configuration.",
	"Move": "Move is used to add a constant to the coordinates "
	"along dimension(s).\n"
	"The user will be asked which dimension(s) to move.\n"
	"The user will be asked for a value to be used.\n"
	"The value, positive or negative, will be added to each "
	"point's coordinate on the dimension.\n"
	"The resulting configuration becomes the active "
	"configuration.",
	"New grouped data": "New grouped data creates a new grouped "
	"data file.\n"
	"The user will be asked for the grouping variable,"
	"number of groups and the "
	"number of dimensions.\n"
	"For each group the user will be asked for a label, a name, "
	"and the coordinate on each dimension.\n"
	"The result will become the active grouped data.",
	"Open sample design": "Open sample design reads in a file "
	"containing a sample design.",
	"Open sample repetitions": "Open sample repetitions reads in "
	"a file containing sample repetitions.",
	"Open sample solutions": "Open sample solutions reads in "
	"a file containing sample solutions.",
	"Open scores": "Open scores reads in a file containing individual "
	"scores \n"
	"corresponding to the dimensions in the active configuration.",
	"Open script": "Open script reads and executes a script file (.spc) "
	"containing a sequence of Spaces commands.\n"
	"Commands are executed in order to reproduce a previous analysis.",
	"Paired": "Paired is used to obtain information about pairs of "
	"points.\n"
	"The user will be asked to select pairs of points.",
	"Principal components": "Principal components is used to obtain "
	"the axes having the highest explanatory power to \n"
	"describe the correlations.\n",
	"Print configuration": "Print configuration is used to print "
	" the active configuration.",
	"Print correlations": "Print correlations is used to print "
	"the active correlations.",
	"Print evaluations": "Print evaluations is used to print the "
	"active evaluations.",
	"Print grouped data": "Print grouped data is used to print the "
	"active grouped data.",
	"Print individuals": "Print individuals is used to print the "
	"active individuals.",
	"Print sample design": "Print sample design is used to print "
	"the active sample design.",
	"Print sample repetitions": "Print sample repetitions is used "
	"to print the active sample repetitions.",
	"Print sample solutions": "Print sample solutions is used "
	"to print the active sample solutions.",
	"Print scores": "Print scores is used to print the active scores.",
	"Print similarities": "Print similarities is used to print "
	"the active similarities.",
	"Print target": "Print target is used to print the active target.",
	"Ranks differences": "Ranks differences displays a matrix of "
	"inter-point rank differences.",
	"Ranks distances": "Ranks distances is used to display ranks of "
	"inter-point distances.",
	"Ranks similarities": "Ranks similarities is used to display "
	"ranks of inter-point similarities.",
	"Redo": "Redo redoes the last action.",
	"Reference points": "Reference points is used to designate two "
	"points as reference points.\n"
	"Reference points will define the bisector.\n"
	"The active configuration will be shown with a line "
	"between the reference points and \n"
	"a perpendicular bisector.",
	"Rescale": "Rescale is used to increase or decrease coordinates.\n"
	"The user will be asked which dimension(s) to rescale.\n"
	"The user will be asked for a value to be used.\n"
	"The coodinate for each point will be multiplied by the "
	"value.\n"
	"The resulting configuration becomes the active "
	"configuration.",
	"Rotate": "Rotate is used to rotate the current plane of the "
	"active configuration.\n"
	"The user will be asked for an angle of rotation in degrees.\n"
	"The resulting configuration becomes the active"
	" configuration.",
	"Sample designer": "Sample designer is used to create a sample "
	"design matrix.\n"
	"The user will be asked for the number of individuals in"
	"the universe to be sampled \n"
	"the number of repetitions to be created \n"
	"and the probability of selection for each individual.\n"
	"The matrix will contain ones and zeroes to indicate \n"
	"whether an individual is included in a repetition. \n"
	"The matrix will contain a row for each respondent and a \n"
	"column for each repetition.",
	"Sample repetitions": "Sample repetitions is used to create a "
	"matrix of sample \n"
	"repetitions based on the sample design.",
	"Save configuration": "Save configuration is used to save "
	"the active configuration to a file.\n"
	"The user will be asked for a file name.\n",
	"Save correlations": "Save correlations is used to save the "
	"active correlations to a file.\n"
	"The user will be asked for a file name.\n",
	"Save grouped data": "Save grouped data is used to save the "
	"active grouped data to a file.\n"
	"The user will be asked for a file name.\n",
	"Save individuals": "Save individuals is used to save the "
	"active individuals to a file.\n"
	"The user will be asked for a file name.\n",
	"Save sample design": "Save sample design is used to save the "
	"active sample design to a file.\n"
	"The user will be asked for a file name.\n",
	"Save sample repetitions": "Save sample repetitions is used to "
	"save the active sample repetitions to a file.\n"
	"The user will be asked for a file name.\n",
	"Save sample solutions": "Save sample solutions is used to save "
	"the active sample solutions to a file.\n"
	"The user will be asked for a file name.\n",
	"Save scores": "Save scores is used to save the active scores "
	"to a file.\n"
	"The user will be asked for a file name.\n",
	"Save similarities": "Save similarities is used to save the "
	"active similarities to a file.\n"
	"The user will be asked for a file name.\n",
	"Save target": "Save target is used to save the active target "
	"to a file.\n"
	"The user will be asked for a file name.\n",
	"Save script": "Save script exports the command history from the "
	"current session to a script file (.spc).\n"
	"The script can be used later to reproduce the analysis.\n"
	"The user will be asked for a file name.\n",
	"Score individuals": "Score individuals is used to create "
	"scores for individuals based on evaluations.",
	"Scree": "Scree displays a diagram showing stress vs."
	" dimensionality.\n"
	"The Scree diagram is used to help decide how many dimensions"
	" to fit the similarities.\n"
	"The number of dimensions is on the x-axis and stress is on "
	"the y-axis.",
	"Second dimension": "Second dimension identifies regions "
	"defined by the second dimension.",
	"Segments": "Segments identifies regions defined by the"
	" reference points.\n"
	"Individuals are assigned to segments based on their "
	"scores on the dimensions\n"
	" of the active configuration. Segments provides estimates "
	"of the number of \n"
	"individuals in each segment. Segments are not mutually "
	"exclusive.",
	"Settings - display sizing": \
		"Settings - display sizing is used to "
	"set various parameters that affect the display.",
	"Settings - layout options": "Settings - layout options is "
	"used to set a few parameters to be used in reports.",
	"Settings - plane": "Settings - plane is used to define the plane "
	"to be displayed.\n"
	"It requires that the active configuration has been "
	"established.\n"
	"The user is asked which of its dimensions to be used "
	"on the horizontal axis.\n"
	"If there are more than two dimensions the user is also"
	"asked which dimension \n"
	"to use on the vertical axis.",
	"Settings - plot settings": "Settings - plot settings is used to "
	"set whether to include a \n"
	"connector beween reference points, a bisector, the "
	"reference points by \n"
	"themselves or with all points",
	"Settings - presentation layer": "Settings - "
	"presentation layer "
	"is used to select Matplotlib or pyqtgraph\n"
	"as the presentation layer.",
	"Settings - segment sizing": \
		"Settings - segment sizing is used to "
	"set the size of the segments.\n"
	"The user is asked for percentages of the connector length to "
	"use to define the size of \n"
	"the battleground region and core region.",
	"Settings - vector sizing": "Settings - vector sizing is used to "
	"set the length of the \n"
	"vectors and the size of their heads.",
	"Shepard": "Shepard is used to create a Shepard diagram.\n"
	"The user is asked which axis to use for similarities.\n"
	"The other axis will be used for distances.\n"
	"Depending on whether the measures represent \n"
	"similarities or dissimilarities and which axis is used to \n"
	"display similarities, a line will rise or descend from \n"
	"left to right. Each point on the line represents the \n"
	"distance between a pair of items and their corresponding \n"
	"similarity measure.",
	"Similarities": "Similarities reads in a similarity matrix.\n"
	"The similarities reflect how similar each item "
	"is to each other. \n"
	"If an active configuration has been established, "
	"the number of items must match the number of points.\n"
	"The user is asked for a file name.\n"
	"The file must be formatted correctly.\n"
	"The first line should be Lower triangular.\n"
	"The next line should have one field, the number or items:\n"
	"For each item:\n"
	"\tA line containing the label, a semicolon, and the "
	"full name for that item.\n"
	"For each item i from 2 to n:\n"
	"\tA line with the similarity between item i and each of the "
	"previous items 1 to i-1 separated by commas.\n",
	"Status": "Status displays the current status of the program.",
	"Stress contribution": "Stress contribution is used to identify "
	"points that \ncontribute most to stress.",
	"Target": "Target estabishes a target configuration.\n"
	"The target configuration may be used to compare with the "
	"active "
	"configuration by performing a Proscrustean rotation to "
	"orient it \n"
	"as closely as possible to the target configuraion.",
	"Terse": "Terse sets the verbosity level to terse.\n"
	"At this level, explanations of what each command does will "
	"not be provided.",
	"Tester": "Tester is used to test various features of the "
	"program.",
	"Uncertainty": "Uncertainty uses the sample repetitions to create"
	"a plot \n"
	"showing uncertainty in the location of points.\n",
	"Undo": "Undo undoes the last action.",
	"Varimax": "Varimax performs a varimax rotation of the active "
	"configuration.",
	"Vectors": "Vectors creates a plot with vectors from the origin"
	" to each point.",
	"Verbose": "Verbose sets the verbosity level to verbose.\n"
	"At this level, explanations of what each command does will "
	"be provided.",
	"View configuration": "View configuration is used to view "
	"the active configuration.",
	"View correlations": "View correlations is used to view "
	"the active correlations.",
	"View custom": "View custom is used to view a custom matrix.",
	"View distances": "View distances is used to view the active "
	"distances.",
	"View evaluations": "View evaluations is used to view the active "
	"evaluations.",
	"View grouped data": "View grouped data is used to view the "
	"active grouped data.",
	"View individuals": "View individuals is used to view the "
	"active individuals.",
	"View point uncertainty": "View point uncertainty is used to "
	"display the uncertainty of a single point in the "
	"current solution.",
	"View sample design": "View sample design is used to view the "
	"active sample design.",
	"View sample repetitions": "View sample repetitions is used to "
	"view the active sample repetitions.",
	"View sample solutions": "View sample solutions is used to "
	"view the active sample solutions.",
	"View scores": "View scores is used to view the active scores.",
	"View script": "View script displays the current command history "
	"that would be saved if Save script were executed.\n"
	"This allows review of commands before saving to a script file.",
	"View similarities": "View similarities is used to view the "
	"active similarities.",
	"View spatial uncertainty": "View spatial uncertainty is used to "
	"display the uncertainty of all points in the current "
	"solution.",
	"View target": "View target is used to view the active target.",
})


# ----------------------------------------------------------------------------
# Dictionary: tab_dict
# Source: director.py lines 2415-2421
# Purpose: Maps tab names to indices
# ----------------------------------------------------------------------------

tab_dict = MappingProxyType({
	"Plot": 0,
	"Output": 1,
	"Gallery": 2,
	"Log": 3,
	"Record": 4,
})


# ----------------------------------------------------------------------------
# Dictionary: button_dict
# Source: director.py lines 1647-1762
# Purpose: Toolbar button configuration
# ----------------------------------------------------------------------------

button_dict = MappingProxyType({
	"new": (
		"spaces_filenew.png",
		"new_configuration",
		"Create new configuration",
	),
	"open": (
		"spaces_fileopen.png",
		"open_configuration",
		"Open existing configuration",
	),
	"save": (
		"spaces_filesave.png",
		"save_configuration",
		"Save current configuration",
	),
	"undo": ("spaces_undo_icon.jpg", "undo", "Undo last action"),
	"redo": (
		"spaces_redo_icon.jpg",
		"redo",
		"Redo last undone action",
	),
	"center": (
		"spaces_center_icon.jpg",
		"center",
		"Center current configuration",
	),
	"move": (
		"spaces_move_icon.png",
		"move",
		"Move points in current configuration",
	),
	"invert": (
		"spaces_invert_icon.jpg",
		"invert",
		"Invert dimensions",
	),
	"rescale": (
		"spaces_rescale_icon.jpg",
		"rescale",
		"Rescale dimensions",
	),
	"rotate": (
		"spaces_rotate_icon.jpg",
		"rotate",
		"Rotate dimensions",
	),
	"scree": ("spaces_scree_icon.jpg", "scree", "Show Scree diagram"),
	"shepard": (
		"spaces_shepard_icon.jpg",
		"shepard_similarities_on_x",
		"Show Shepard diagram",
	),
	"mds": (
		"spaces_mds_icon.jpg",
		"mds",
		"Perform Multi-Dimensional Scaling",
	),
	"factor_analysis": (
		"spaces_factor_analysis_icon.jpg",
		"factor_analysis",
		"Perform Factor Analysis",
	),
	"principal_components": (
		"spaces_pca_icon.jpg",
		"principal",
		"Perform Principal Components Analysis",
	),
	"reference_points": (
		"spaces_reference_icon.jpg",
		"reference_points",
		"Set reference points",
	),
	"contest": ("spaces_contest_icon.jpg", "contest", "Show contest"),
	"segments": (
		"spaces_segments_icon.jpg",
		"segments",
		"Show segments",
	),
	"core": (
		"spaces_core_icon.jpg",
		"core_regions",
		"Show core supporter regions",
	),
	"base": (
		"spaces_base_icon.jpg",
		"base_regions",
		"Show base supporter regions",
	),
	"likely": (
		"spaces_likely_icon.jpg",
		"likely_regions",
		"Show likely supporter regions",
	),
	"battleground": (
		"spaces_battleground_icon.jpg",
		"battleground_regions",
		"Show battleground regions",
	),
	"convertible": (
		"spaces_convertible_icon.jpg",
		"convertible_regions",
		"Show convertible regions",
	),
	"first": (
		"spaces_first_dim_icon.jpg",
		"first_regions",
		"Show first dimension regions",
	),
	"second": (
		"spaces_second_dim_icon.jpg",
		"second_regions",
		"Show second dimension regions",
	),
	"help": ("spaces_help_icon.jpg", "help_content", "Show help"),
})


# ----------------------------------------------------------------------------
# Dictionary: request_dict (renamed from menu_item_dict, originally traffic_dict)
# Source: director.py lines 2703-2883
# Purpose: Maps menu item request IDs to command classes and parameters
# ----------------------------------------------------------------------------

request_dict = MappingProxyType({
	"new_configuration": (CreateCommand, None),
	"new_grouped_data": (NewGroupedDataCommand, None),
	"open_configuration": (ConfigurationCommand, None),
	"open_target": (TargetCommand, None),
	"open_grouped_data": (GroupedDataCommand, None),
	"open_similarities_dissimilarities": (
		SimilaritiesCommand,
		"dissimilarities",
	),
	"open_similarities_similarities": (
		SimilaritiesCommand,
		"similarities",
	),
	"open_correlations": (CorrelationsCommand, None),
	"open_evaluations": (EvaluationsCommand, None),
	"open_individuals": (IndividualsCommand, None),
	"open_scores": (OpenScoresCommand, None),
	"open_sample_design": (OpenSampleDesignCommand, None),
	"open_sample_repetitions": (OpenSampleRepetitionsCommand, None),
	"open_sample_solutions": (OpenSampleSolutionsCommand, None),
	"open_script": (OpenScriptCommand, None),
	"save_configuration": (SaveConfigurationCommand, None),
	"save_target": (SaveTargetCommand, None),
	"save_correlations": (SaveCorrelationsCommand, None),
	"save_grouped_data": (SaveGroupedDataCommand, None),
	"save_similarities": (SaveSimilaritiesCommand, None),
	"save_individuals": (SaveIndividualsCommand, None),
	"save_scores": (SaveScoresCommand, None),
	"save_sample_design": (SaveSampleDesignCommand, None),
	"save_sample_repetitions": (SaveSampleRepetitionsCommand, None),
	"save_sample_solutions": (SaveSampleSolutionsCommand, None),
	"save_script": (SaveScriptCommand, None),
	"deactivate": (DeactivateCommand, None),
	"settings_plot": (SettingsPlotCommand, None),
	"settings_plane": (SettingsPlaneCommand, None),
	"settings_segment": (SettingsSegmentCommand, None),
	"settings_display": (SettingsDisplayCommand, None),
	"settings_vector": (SettingsVectorSizeCommand, None),
	"settings_presentation_matplotlib": (
		SettingsPresentationLayerCommand,
		"Matplotlib",
	),
	"settings_presentation_pyqtgraph": (
		SettingsPresentationLayerCommand,
		"PyQtGraph",
	),
	"settings_layout": (SettingsLayoutCommand, None),
	"print_configuration": (PrintConfigurationCommand, None),
	"print_target": (PrintTargetCommand, None),
	"print_grouped_data": (PrintGroupedDataCommand, None),
	"print_correlations": (PrintCorrelationsCommand, None),
	"print_similarities": (PrintSimilaritiesCommand, None),
	"print_evaluations": (PrintEvaluationsCommand, None),
	"print_individuals": (PrintIndividualsCommand, None),
	"print_scores": (PrintScoresCommand, None),
	"print_sample_design": (PrintSampleDesignCommand, None),
	"print_sample_repetitions": (PrintSampleRepetitionsCommand, None),
	"print_sample_solutions": (PrintSampleSolutionsCommand, None),
	"exit": (ExitCommand, None),
	"undo": (UndoCommand, None),
	"redo": (RedoCommand, None),
	"view_configuration": (ViewConfigurationCommand, None),
	"view_target": (ViewTargetCommand, None),
	"view_grouped": (ViewGroupedDataCommand, None),
	"view_similarities": (ViewSimilaritiesCommand, None),
	"view_correlations": (ViewCorrelationsCommand, None),
	"view_distances": (ViewDistancesCommand, None),
	"view_evaluations": (ViewEvaluationsCommand, None),
	"view_individuals": (ViewIndividualsCommand, None),
	"view_scores": (ViewScoresCommand, None),
	"view_sample_design": (ViewSampleDesignCommand, None),
	"view_sample_repetitions": (ViewSampleRepetitionsCommand, None),
	"view_sample_solutions": (ViewSampleSolutionsCommand, None),
	"view_script": (ViewScriptCommand, None),
	"view_spatial_uncertainty_lines": (
		ViewSpatialUncertaintyCommand,
		"lines",
	),
	"view_spatial_uncertainty_boxes": (
		ViewSpatialUncertaintyCommand,
		"boxes",
	),
	"view_spatial_uncertainty_ellipses": (
		ViewSpatialUncertaintyCommand,
		"ellipses",
	),
	"view_spatial_uncertainty_circles": (
		ViewSpatialUncertaintyCommand,
		"circles",
	),
	"view_point_uncertainty_lines": (
		ViewPointUncertaintyCommand,
		"lines",
	),
	"view_point_uncertainty_boxes": (
		ViewPointUncertaintyCommand,
		"boxes",
	),
	"view_point_uncertainty_ellipses": (
		ViewPointUncertaintyCommand,
		"ellipses",
	),
	"view_point_uncertainty_circles": (
		ViewPointUncertaintyCommand,
		"circles",
	),
	"history": (HistoryCommand, None),
	"view_custom": (ViewCustomCommand, None),
	"center": (CenterCommand, None),
	"move": (MoveCommand, None),
	"invert": (InvertCommand, None),
	"rescale": (RescaleCommand, None),
	"rotate": (RotateCommand, None),
	"compare": (CompareCommand, None),
	"varimax": (VarimaxCommand, None),
	"correlations": (ViewCorrelationsCommand, None),
	"similarities": (ViewSimilaritiesCommand, None),
	"paired": (PairedCommand, None),
	"line_of_sight": (LineOfSightCommand, None),
	"alike": (AlikeCommand, None),
	"cluster": (ClusterCommand, None),
	"distances": (DistancesCommand, None),
	"ranks_distances": (RanksDistancesCommand, None),
	"ranks_similarities": (RanksSimilaritiesCommand, None),
	"ranks_differences": (RanksDifferencesCommand, None),
	"scree": (ScreeCommand, None),
	"shepard_similarities_on_x": (ShepardCommand, "X"),
	"shepard_similarities_on_y": (ShepardCommand, "Y"),
	"stress_contribution": (StressContributionCommand, None),
	"principal": (PrincipalComponentsCommand, None),
	"factor_analysis": (FactorAnalysisCommand, None),
	"factor_analysis_machine_learning": (
		FactorAnalysisMachineLearningCommand,
		None,
	),
	"mds": (MDSCommand, None),
	"mds_metric": (MDSCommand, True),
	"mds_non_metric": (MDSCommand, False),
	"vectors": (VectorsCommand, None),
	"directions": (DirectionsCommand, None),
	"uncertainty": (UncertaintyCommand, None),
	"evaluations": (ViewEvaluationsCommand, None),
	"sample_designer": (SampleDesignerCommand, None),
	"sample_repetitions": (SampleRepetitionsCommand, None),
	"score_individuals": (ScoreIndividualsCommand, None),
	"joint": (JointCommand, None),
	"reference_points": (ReferencePointsCommand, None),
	"contest": (ContestCommand, None),
	"segments": (SegmentsCommand, None),
	"core_regions": (CoreSupportersCommand, "regions"),
	"core_left": (CoreSupportersCommand, "left"),
	"core_right": (CoreSupportersCommand, "right"),
	"core_both": (CoreSupportersCommand, "both"),
	"core_neither": (CoreSupportersCommand, "neither"),
	"base_regions": (BaseCommand, "regions"),
	"base_left": (BaseCommand, "left"),
	"base_right": (BaseCommand, "right"),
	"base_both": (BaseCommand, "both"),
	"base_neither": (BaseCommand, "neither"),
	"likely_regions": (LikelySupportersCommand, "regions"),
	"likely_left": (LikelySupportersCommand, "left"),
	"likely_right": (LikelySupportersCommand, "right"),
	"likely_both": (LikelySupportersCommand, "both"),
	"convertible_regions": (ConvertibleCommand, "regions"),
	"convertible_left": (ConvertibleCommand, "left"),
	"convertible_right": (ConvertibleCommand, "right"),
	"convertible_both": (ConvertibleCommand, "both"),
	"convertible_settled": (ConvertibleCommand, "settled"),
	"battleground_regions": (BattlegroundCommand, "regions"),
	"battleground_segment": (BattlegroundCommand, "battleground"),
	"battleground_settled": (BattlegroundCommand, "settled"),
	"first_regions": (FirstDimensionCommand, "regions"),
	"first_left": (FirstDimensionCommand, "left"),
	"first_right": (FirstDimensionCommand, "right"),
	"second_regions": (SecondDimensionCommand, "regions"),
	"second_upper": (SecondDimensionCommand, "upper"),
	"second_lower": (SecondDimensionCommand, "lower"),
	"help_content": (HelpCommand, None),
	"status": (StatusCommand, None),
	"about": (AboutCommand, None),
	"terse": (TerseCommand, None),
	"verbose": (VerboseCommand, None),
	"tester": (TesterCommand, None),
})


# ----------------------------------------------------------------------------
# Function to create widget_dict
# Source: director.py lines 3019-3469
# Purpose: Maps command names to widget configuration
# Note: This must be a function because it uses lambda functions that
#       reference parent instance
# ----------------------------------------------------------------------------

def create_widget_dict(parent: Status) -> FrozenDict:
	"""Create widget dictionary with lambda functions for table display.

	This dictionary maps command names to their widget configuration,
	including the command class, sharing type, and a lambda function
	for displaying the appropriate table.

	Args:
		parent: The Status instance (director) providing access to tables

	Returns:
		Immutable dictionary mapping command names to
		[CommandClass, type, callable]
	"""
	return MappingProxyType({
		"About": [AboutCommand, "unique", None],
		"Alike": [
			AlikeCommand,
			"shared",
			lambda: parent.statistics.display_table("alike"),
		],
		"Base": [
			BaseCommand,
			"shared",
			lambda: parent.rivalry_tables.display_table("base"),
		],
		"Battleground": [
			BattlegroundCommand,
			"shared",
			lambda: parent.rivalry_tables.display_table("battleground"),
		],
		"Center": [
			CenterCommand,
			"shared",
			lambda: parent.tables.display_table("configuration"),
		],
		"Cluster": [ClusterCommand, "unique", None],
		"Compare": [
			CompareCommand,
			"shared",
			lambda: parent.statistics.display_table("compare"),
		],
		"Configuration": [
			ConfigurationCommand,
			"shared",
			lambda: parent.tables.display_table("configuration"),
		],
		"Contest": [ContestCommand, "shared", parent.display_a_line],
		"Convertible": [
			ConvertibleCommand,
			"shared",
			lambda: parent.rivalry_tables.display_table("convertible"),
		],
		"Core supporters": [
			CoreSupportersCommand,
			"shared",
			lambda: parent.rivalry_tables.display_table("core"),
		],
		"Correlations": [
			CorrelationsCommand,
			"shared",
			lambda: parent.squares.display_table("correlations"),
		],

		"Create": [
			CreateCommand,
			"shared",
			lambda: parent.tables.display_table("configuration"),
		],
		"Deactivate": [DeactivateCommand, "unique", None],
		"Directions": [
			DirectionsCommand,
			"shared",
			lambda: parent.statistics.display_table("directions"),
		],
		"Distances": [
			DistancesCommand,
			"shared",
			lambda: parent.squares.display_table("distances"),
		],
		"Evaluations": [
			EvaluationsCommand,
			"shared",
			lambda: parent.statistics.display_table("evaluations"),
		],
		"Exit": [ExitCommand, "unique", None],
		"Factor analysis": [
			FactorAnalysisCommand,
			"shared",
			lambda: parent.statistics.display_table("factor_analysis"),
		],
		"Factor analysis machine learning": [
			FactorAnalysisMachineLearningCommand,
			"unique",
			None,
		],
		"First dimension": [
			FirstDimensionCommand,
			"shared",
			lambda: parent.rivalry_tables.display_table("first"),
		],
		"Grouped data": [
			GroupedDataCommand,
			"shared",
			lambda: parent.tables.display_table("grouped_data"),
		],
		"Help": [HelpCommand, "shared", parent.display_coming_soon],
		"History": [HistoryCommand, "unique", None],
		"Individuals": [
			IndividualsCommand,
			"shared",
			lambda: parent.statistics.display_table("individuals"),
		],
		"Invert": [
			InvertCommand,
			"shared",
			lambda: parent.tables.display_table("configuration"),
		],
		"Joint": [JointCommand, "shared", parent.display_a_line],
		"Likely supporters": [
			LikelySupportersCommand,
			"shared",
			lambda: parent.rivalry_tables.display_table("likely"),
		],
		"Line of sight": [
			LineOfSightCommand,
			"shared",
			lambda: parent.squares.display_table("similarities"),
		],
		"MDS": [
			MDSCommand,
			"shared",
			lambda: parent.tables.display_table("configuration"),
		],
		"Move": [
			MoveCommand,
			"shared",
			lambda: parent.tables.display_table("configuration"),
		],
		"New grouped data": [
			NewGroupedDataCommand,
			"shared",
			lambda: parent.tables.display_table("grouped_data"),
		],
		"Open sample design": [
			OpenSampleDesignCommand,
			"shared",
			lambda: parent.statistics.display_table("sample_design"),
		],
		"Open sample repetitions": [
			OpenSampleRepetitionsCommand,
			"shared",
			lambda: parent.statistics.display_table("sample_repetitions"),
		],
		"Open sample solutions": [
			OpenSampleSolutionsCommand,
			"unique",
			None,
		],
		"Open scores": [
			OpenScoresCommand,
			"shared",
			lambda: parent.statistics.display_table("scores"),
		],
		"Open script": [OpenScriptCommand, "unique", None],
		"Paired": [PairedCommand, "unique", None],
		"Principal components": [
			PrincipalComponentsCommand,
			"shared",
			lambda: parent.tables.display_table("configuration"),
		],
		"Print configuration": [
			PrintConfigurationCommand,
			"shared",
			lambda: parent.tables.display_table("configuration"),
		],
		"Print correlations": [
			PrintCorrelationsCommand,
			"shared",
			lambda: parent.squares.display_table("correlations"),
		],
		"Print evaluations": [
			PrintEvaluationsCommand,
			"shared",
			lambda: parent.statistics.display_table("evaluations"),
		],
		"Print grouped data": [
			PrintGroupedDataCommand,
			"shared",
			lambda: parent.tables.display_table("grouped_data"),
		],
		"Print individuals": [
			PrintIndividualsCommand,
			"shared",
			lambda: parent.statistics.display_table("individuals"),
		],
		"Print sample design": [
			PrintSampleDesignCommand,
			"shared",
			lambda: parent.statistics.display_table("sample_design"),
		],
		"Print sample repetitions": [
			PrintSampleRepetitionsCommand,
			"shared",
			lambda: parent.statistics.display_table("sample_repetitions"),
		],
		"Print sample solutions": [
			PrintSampleSolutionsCommand,
			"shared",
			lambda: parent.statistics.display_table("sample_solutions"),
		],
		"Print scores": [
			PrintScoresCommand,
			"shared",
			lambda: parent.statistics.display_table("scores"),
		],
		"Print similarities": [
			PrintSimilaritiesCommand,
			"shared",
			lambda: parent.squares.display_table("similarities"),
		],
		"Print target": [
			PrintTargetCommand,
			"shared",
			lambda: parent.tables.display_table("target"),
		],
		"Ranks differences": [
			RanksDifferencesCommand,
			"shared",
			lambda: parent.squares.display_table("ranked_differences"),
		],
		"Ranks distances": [
			RanksDistancesCommand,
			"shared",
			lambda: parent.squares.display_table("ranked_distances"),
		],
		"Ranks similarities": [
			RanksSimilaritiesCommand,
			"shared",
			lambda: parent.squares.display_table("ranked_similarities"),
		],
		"Redo": [RedoCommand, "unique", None],
		"Reference points": [
			ReferencePointsCommand,
			"shared",
			parent.display_a_line,
		],
		"Rescale": [
			RescaleCommand,
			"shared",
			lambda: parent.tables.display_table("configuration"),
		],
		"Rotate": [
			RotateCommand,
			"shared",
			lambda: parent.tables.display_table("configuration"),
		],
		"Sample designer": [
			SampleDesignerCommand,
			"shared",
			lambda: parent.statistics.display_table("sample_design"),
		],
		"Sample repetitions": [
			SampleRepetitionsCommand,
			"shared",
			lambda: parent.statistics.display_table("sample_repetitions"),
		],
		"Save configuration": [
			SaveConfigurationCommand,
			"shared",
			lambda: parent.tables.display_table("configuration"),
		],
		"Save correlations": [
			SaveCorrelationsCommand,
			"shared",
			lambda: parent.squares.display_table("correlations"),
		],
		"Save grouped data": [
			SaveGroupedDataCommand,
			"shared",
			lambda: parent.tables.display_table("grouped_data"),
		],
		"Save individuals": [
			SaveIndividualsCommand,
			"shared",
			lambda: parent.statistics.display_table("individuals"),
		],
		"Save sample design": [
			SaveSampleDesignCommand,
			"shared",
			lambda: parent.statistics.display_table("sample_design"),
		],
		"Save sample repetitions": [
			SaveSampleRepetitionsCommand,
			"shared",
			lambda: parent.statistics.display_table("sample_repetitions"),
		],
		"Save sample solutions": [
			SaveSampleSolutionsCommand,
			"shared",
			None,
		],
		"Save scores": [
			SaveScoresCommand,
			"shared",
			lambda: parent.statistics.display_table("scores"),
		],
		"Save similarities": [
			SaveSimilaritiesCommand,
			"shared",
			lambda: parent.squares.display_table("similarities"),
		],
		"Save target": [
			SaveTargetCommand,
			"shared",
			lambda: parent.tables.display_table("target"),
		],
		"Save script": [
			SaveScriptCommand,
			"shared",
			lambda: parent.display_a_line(),
		],
		"Score individuals": [
			ScoreIndividualsCommand,
			"shared",
			lambda: parent.statistics.display_table("scores"),
		],
		"Scree": [
			ScreeCommand,
			"shared",
			lambda: parent.statistics.display_table("scree"),
		],
		"Second dimension": [
			SecondDimensionCommand,
			"shared",
			lambda: parent.rivalry_tables.display_table("second"),
		],
		"Segments": [
			SegmentsCommand,
			"shared",
			lambda: parent.rivalry_tables.display_table("segments"),
		],
		"Settings - display sizing": [
			SettingsDisplayCommand,
			"unique",
			None,
		],
		"Settings - layout options": [
			SettingsLayoutCommand,
			"unique",
			None,
		],
		"Settings - plane": [SettingsPlaneCommand, "unique", None],
		"Settings - plot settings": [SettingsPlotCommand, "unique", None],
		"Settings - presentation layer": [
			SettingsPresentationLayerCommand,
			"unique",
			None,
		],
		"Settings - segment sizing": [
			SettingsSegmentCommand,
			"unique",
			None,
		],
		"Settings - vector sizing": [
			SettingsVectorSizeCommand,
			"unique",
			None,
		],
		"Shepard": [
			ShepardCommand,
			"shared",
			lambda: parent.squares.display_table("shepard"),
		],
		"Similarities": [
			SimilaritiesCommand,
			"shared",
			lambda: parent.squares.display_table("similarities"),
		],
		"Status": [StatusCommand, "unique", None],
		"Stress contribution": [
			StressContributionCommand,
			"shared",
			lambda: parent.statistics.display_table("stress_contribution"),
		],
		"Target": [
			TargetCommand,
			"shared",
			lambda: parent.tables.display_table("target"),
		],
		"Terse": [TerseCommand, "shared", parent.display_a_line],
		"Tester": [TesterCommand, "unique", None],
		"Uncertainty": [
			UncertaintyCommand,
			"shared",
			lambda: parent.statistics.display_table("uncertainty"),
		],
		"Undo": [UndoCommand, "unique", None],
		"Varimax": [
			VarimaxCommand,
			"shared",
			lambda: parent.tables.display_table("configuration"),
		],
		"Vectors": [
			VectorsCommand,
			"shared",
			lambda: parent.tables.display_table("configuration"),
		],
		"Verbose": [VerboseCommand, "shared", parent.display_a_line],
		"View configuration": [
			ViewConfigurationCommand,
			"shared",
			lambda: parent.tables.display_table("configuration"),
		],
		"View correlations": [
			ViewCorrelationsCommand,
			"shared",
			lambda: parent.squares.display_table("correlations"),
		],
		"View custom": [ViewCustomCommand, "unique", None],
		"View distances": [
			ViewDistancesCommand,
			"shared",
			lambda: parent.squares.display_table("distances"),
		],
		"View evaluations": [
			ViewEvaluationsCommand,
			"shared",
			lambda: parent.statistics.display_table("evaluations"),
		],
		"View grouped data": [
			ViewGroupedDataCommand,
			"shared",
			lambda: parent.tables.display_table("grouped_data"),
		],
		"View individuals": [
			ViewIndividualsCommand,
			"shared",
			lambda: parent.statistics.display_table("individuals"),
		],
		"View point uncertainty": [
			ViewPointUncertaintyCommand,
			"shared",
			lambda: parent.statistics.display_table("uncertainty"),
		],
		"View sample design": [
			ViewSampleDesignCommand,
			"shared",
			lambda: parent.statistics.display_table("sample_design"),
		],
		"View sample repetitions": [
			ViewSampleRepetitionsCommand,
			"shared",
			lambda: parent.statistics.display_table("sample_repetitions"),
		],
		"View sample solutions": [
			ViewSampleSolutionsCommand,
			"shared",
			lambda: parent.statistics.display_table("sample_solutions"),
		],
		"View scores": [
			ViewScoresCommand,
			"shared",
			lambda: parent.statistics.display_table("scores"),
		],
		"View script": [ViewScriptCommand, "unique", None],
		"View similarities": [
			ViewSimilaritiesCommand,
			"shared",
			lambda: parent.squares.display_table("similarities"),
		],
		"View spatial uncertainty": [
			ViewSpatialUncertaintyCommand,
			"shared",
			lambda: parent.statistics.display_table("spatial_uncertainty"),
		],
		"View target": [
			ViewTargetCommand,
			"shared",
			lambda: parent.tables.display_table("target"),
		],
	})


# ----------------------------------------------------------------------------
# Menu Structure Dictionaries
# Source: director.py lines 413-1252
# Purpose: Define menu structure for the application
# ----------------------------------------------------------------------------

file_menu_dict = MappingProxyType({
	"New": {
		"icon": None,
		"tooltip": "Create something new",
		"items": {
			"Configuration": [
				"spaces_filenew.png",
				"new_configuration",
				"Create a new configuration",
			],
			"Grouped data": [
				"spaces_grouped_data_icon.jpg",
				"new_grouped_data",
				"Create new grouped data",
			],
		},
	},
	"Open": {
		"icon": None,
		"items": {
			"Configuration": [
				"spaces_fileopen.png",
				"open_configuration",
				"Open an existing configuration",
			],
			"Target": [
				"spaces_target_icon.jpg",
				"open_target",
				"Open an existing target",
			],
			"Grouped data": [
				"spaces_grouped_data_icon.jpg",
				"open_grouped_data",
				"Open existing grouped data",
			],
			"Similarities": {
				"icon": "spaces_similarities_icon.jpg",
				"items": {
					"Similarities": [
						None,
						"open_similarities_similarities",
						"Open existing similarities matrix",
					],
					"Dissimilarities": [
						None,
						"open_similarities_dissimilarities",
						"Open existing dissimilarities matrix",
					],
				},
			},
			"Correlations": [
				"spaces_correlations_icon.jpg",
				"open_correlations",
				"Open existing correlations matrix",
			],
			"Evaluations": [
				"spaces_evaluations_icon.jpg",
				"open_evaluations",
				"Open existing evaluations file",
			],
			"Individuals": [
				"spaces_individuals_icon.jpg",
				"open_individuals",
				"Open existing individuals file",
			],
			"Scores": [
				"spaces_scores_icon.jpg",
				"open_scores",
				"Open existing scores file",
			],
			"Sample": {
				"icon": "spaces_sample_icon.jpg",
				"items": {
					"Design": [
						None,
						"open_sample_design",
						"Open existing sample design file",
					],
					"Repetitions": [
						None,
						"open_sample_repetitions",
						"Open existing sample repetitions file",
					],
					"Solutions": [
						None,
						"open_sample_solutions",
						"Open existing sample solutions file",
					],
				},
			},
			"Script": [
				"spaces_open_script_icon.jpg",
				"open_script",
				"Open and execute a script file",
			],
		},
	},
	"Save": {
		"icon": "spaces_filesave.png",
		"items": {
			"Configuration": [
				None,
				"save_configuration",
				"Save the active configuration",
			],
			"Target": [None, "save_target", "Save the active target"],
			"Correlations": [
				None,
				"save_correlations",
				"Save the active correlations",
			],
			"Grouped data": [
				None,
				"save_grouped_data",
				"Save the active grouped data",
			],
			"Similarities": [
				None,
				"save_similarities",
				"Save the active similarities",
			],
			"Individuals": [
				None,
				"save_individuals",
				"Save the active individuals",
			],
			"Scores": [None, "save_scores", "Save the active scores"],
			"Sample": {
				"icon": "spaces_sample_icon.jpg",
				"items": {
					"Design": [
						None,
						"save_sample_design",
						"Save the active sample design",
					],
					"Repetitions": [
						None,
						"save_sample_repetitions",
						"Save the active sample repetitions",
					],
					"Solutions": [
						None,
						"save_sample_solutions",
						"Save the active sample solutions",
					],
				},
			},
			"Script": [
				"spaces_save_script_icon.jpg",
				"save_script",
				"Save command history as script",
			],
		},
	},
	"Deactivate": [
		"spaces_deactivate_icon.jpg",
		"deactivate",
		"Deactivate current features",
	],
	"Settings": {
		"icon": "spaces_settings_icon.jpg",
		"items": {
			"Plot settings": [
				None,
				"settings_plot",
				"Settings for plot",
			],
			"Plane": [None, "settings_plane", "Settings for plane"],
			"Segment sizing": [
				None,
				"settings_segment",
				"Settings for segment sizing",
			],
			"Display sizing": [
				None,
				"settings_display",
				"Settings for display sizing",
			],
			"Vector sizing": [
				None,
				"settings_vector",
				"Settings for vector sizing",
			],
			"Presentation layer": {
				"icon": "spaces_presentation_icon.jpg",
				"items": {
					"Matplotlib": [
						"spaces_matplotlib_icon.jpg",
						"settings_presentation_matplotlib",
						"Use Matplotlib for plots",
					],
					"PyQtGraph": [
						"spaces_QT_icon.webp",
						"settings_presentation_pyqtgraph",
						"Use PyQtGraph for plots",
					],
				},
			},
			"Layout options": [
				None,
				"settings_layout",
				"Settings for layout options",
			],
		},
	},
	"Print": {
		"icon": "spaces_fileprint.png",
		"items": {
			"Configuration": [
				None,
				"print_configuration",
				"Print active configuration",
			],
			"Target": [None, "print_target", "Print active target"],
			"Grouped data": [
				None,
				"print_grouped_data",
				"Print active grouped data",
			],
			"Correlations": [
				None,
				"print_correlations",
				"Print active correlations",
			],
			"Similarities": [
				None,
				"print_similarities",
				"Print active similarities",
			],
			"Evaluations": [
				None,
				"print_evaluations",
				"Print active evaluations",
			],
			"Individuals": [
				None,
				"print_individuals",
				"Print active individuals",
			],
			"Scores": [None, "print_scores", "Print active scores"],
			"Sample": {
				"icon": "spaces_sample_icon.jpg",
				"items": {
					"Design": [
						None,
						"print_sample_design",
						"Print active sample design",
					],
					"Repetitions": [
						None,
						"print_sample_repetitions",
						"Print active sample repetitions",
					],
					"Solutions": [
						None,
						"print_sample_solutions",
						"Print active sample solutions",
					],
				},
			},
		},
	},
	"Exit": ["spaces_exit_icon.jpg", "exit", "Exit Spaces"],
})

edit_menu_dict = MappingProxyType({
	"Undo": {
		"icon": "spaces_undo_icon.jpg",
		"command": "undo",
		"enabled": False,
		"shortcut": "Ctrl+Z",
		"tooltip": "Undo the last action",
	},
	"Redo": {
		"icon": "spaces_redo_icon.jpg",
		"command": "redo",
		"enabled": False,
		"shortcut": "Ctrl+Y",
		"tooltip": "Redo the last undone action",
	},
})

view_menu_dict = MappingProxyType({
	"Configuration": [
		"outer_space_icon.png",
		"view_configuration",
		"View active configuration",
	],
	"Target": [
		"spaces_view_target_icon.jfif",
		"view_target",
		"View active target",
	],
	"Grouped data": [
		"spaces_grouped_data_icon.jpg",
		"view_grouped",
		"View active grouped data",
	],
	"Similarities": [
		"spaces_black_icon.jpg",
		"view_similarities",
		"View active similarities",
	],
	"Correlations": [
		"spaces_r_red_icon.jpg",
		"view_correlations",
		"View active correlations",
	],
	"Distances": [
		"spaces_green_icon.png",
		"view_distances",
		"View active distances",
	],
	"Evaluations": [
		"spaces_evaluations_icon.jpg",
		"view_evaluations",
		"View active evaluations",
	],
	"Individuals": [
		"spaces_individuals_icon.jpg",
		"view_individuals",
		"View active individuals",
	],
	"Scores": [
		"spaces_scores_icon.jpg",
		"view_scores",
		"View active scores",
	],
	"History": [
		"spaces_history_icon.jpg",
		"history",
		"View history of commands",
	],
	"Script": [
		"spaces_view_script_icon.jpg",
		"view_script",
		"View current command history as script",
	],
	"Sample": {
		"icon": "spaces_sample_icon.jpg",
		"items": {
			"Design": [
				None,
				"view_sample_design",
				"View active sample design",
			],
			"Repetitions": [
				None,
				"view_sample_repetitions",
				"View active sample repetitions",
			],
			"Solutions": [
				None,
				"view_sample_solutions",
				"View active sample solutions",
			],
		},
	},
	"Spatial uncertainty": {
		"icon": "spaces_uncertainty_icon.png",
		"items": {
			"Lines": [
				None,
				"view_spatial_uncertainty_lines",
				"View spatial uncertainty as lines",
			],
			"Boxes": [
				None,
				"view_spatial_uncertainty_boxes",
				"View spatial uncertainty as boxes",
			],
			"Ellipses": [
				None,
				"view_spatial_uncertainty_ellipses",
				"View spatial uncertainty as ellipses",
			],
			"Circles": [
				None,
				"view_spatial_uncertainty_circles",
				"View spatial uncertainty as circles",
			],
		},
	},
	"Point uncertainty": {
		"icon": "spaces_uncertainty_icon.png",
		"items": {
			"Lines": [
				None,
				"view_point_uncertainty_lines",
				"View point uncertainty as lines",
			],
			"Boxes": [
				None,
				"view_point_uncertainty_boxes",
				"View point uncertainty as boxes",
			],
			"Ellipses": [
				None,
				"view_point_uncertainty_ellipses",
				"View point uncertainty as ellipses",
			],
			"Circles": [
				None,
				"view_point_uncertainty_circles",
				"View point uncertainty as circles",
			],
		},
	},
	"Custom": [
		"spaces_custom_icon.png",
		"view_custom",
		"View custom display",
	],
})

transform_menu_dict = MappingProxyType({
	"Center": [
		"spaces_center_icon.jpg",
		"center",
		"Center the active configuration",
	],
	"Move": [
		"spaces_move_icon.png",
		"move",
		"Move points in the active configuration",
	],
	"Invert": [
		"spaces_invert_icon.jpg",
		"invert",
		"Invert dimensions in the active configuration",
	],
	"Rescale": [
		"spaces_rescale_icon.jpg",
		"rescale",
		"Rescale dimensions in the active configuration",
	],
	"Rotate": [
		"spaces_rotate_icon.jpg",
		"rotate",
		"Rotate the active configuration",
	],
	"Compare": [
		"spaces_compare_icon.jpg",
		"compare",
		"Compare the active configuration to the active target "
		"configuration",
	],
	"Varimax": {
		"icon": "spaces_varimax_icon.jpg",
		"command": "varimax",
		"enabled": False,
		"tooltip": \
			"Apply Varimax rotation to the active configuration",
	},
})

associations_menu_dict = MappingProxyType({
	"Correlations": [
		"spaces_correlations_icon.jpg",
		"correlations",
		"Compute correlations",
	],
	"Similarities": [
		"spaces_similarities_icon.jpg",
		"similarities",
		"Compute similarities",
	],
	"Line of sight": [
		"spaces_los_icon.jpg",
		"line_of_sight",
		"Compute Line of sight coefficients",
	],
	"Paired": [
		"spaces_paired_icon.jpg",
		"paired",
		"Compare pairs of points",
	],
	"Alike": [
		"spaces_alike_icon.jpg",
		"alike",
		"Select most alike points",
	],
	"Distances": [
		"spaces_distances_icon.jpg",
		"distances",
		"Compute distances in active configuration",
	],
	"Ranks": {
		"icon": "spaces_associations_ranks_icon.jpg",
		"items": {
			"Ranks of distances": [
				None,
				"ranks_distances",
				"Rank distances",
			],
			"Ranks of similarities": [
				None,
				"ranks_similarities",
				"Rank similarities",
			],
			"Difference of ranks": [
				None,
				"ranks_differences",
				"Difference of ranks",
			],
		},
	},
	"Scree diagram": [
		"spaces_scree_icon.jpg",
		"scree",
		"Create a scree diagram",
	],
	"Shepard diagram": {
		"icon": "spaces_shepard_icon.jpg",
		"items": {
			"Similarities on x-axis": [
				None,
				"shepard_similarities_on_x",
				"Display similarities on x-axis in Shepard diagram",
			],
			"Similarities on y-axis": [
				None,
				"shepard_similarities_on_y",
				"Display similarities on y-axis in Shepard diagram",
			],
		},
	},
	"Stress contribution": [
		"spaces_stress_icon.jpg",
		"stress_contribution",
		"Compute point contribution to stress",
	],
})

model_menu_dict = MappingProxyType({
	"Cluster": [
		"spaces_cluster_icon.png",
		"cluster",
		"Cluster the active configuration",
	],
	"Principal Components": [
		"spaces_pca_icon.jpg",
		"principal",
		"Perform Principal Components Analysis",
	],
	"Factor Analysis": [
		"spaces_factor_analysis_icon.jpg",
		"factor_analysis",
		"Perform Factor Analysis",
	],
	"Factor Analysis Machine Learning": [
		"spaces_factor_analysis_icon.jpg",
		"factor_analysis_machine_learning",
		"Perform Machine Learning Factor Analysis",
	],
	"Multi-Dimensional Scaling": {
		"icon": "spaces_mds_icon.jpg",
		"items": {
			"Use non-metric estimation": [
				None,
				"mds_non_metric",
				"Perform non-metric Multi-Dimensional Scaling",
			],
			"Use metric estimation": [
				None,
				"mds_metric",
				"Perform metric Multi-Dimensional Scaling",
			],
		},
	},
	"Vectors": [
		"spaces_vectors_icon.jfif",
		"vectors",
		"Display active configuration as vectors",
	],
	"Directions": [
		"spaces_directions_icon.jfif",
		"directions",
		"Display active configuration as directions",
	],
	"Uncertainty": [
		"spaces_uncertainty_icon.png",
		"uncertainty",
		"Compute uncertainty of active configuration",
	],
})

respondents_menu_dict = MappingProxyType({
	"Evaluations": [
		"spaces_evaluations_icon.jpg",
		"evaluations",
		"Evaluations by respondents",
	],
	"Sample": {
		"icon": "spaces_sample_icon.jpg",
		"items": {
			"Design samples": [
				None,
				"sample_designer",
				"Design samples",
			],
			"Generate repetitions": [
				None,
				"sample_repetitions",
				"Generate repetitions",
			],
		},
	},
	"Score individuals": [
		"spaces_scores_icon.jpg",
		"score_individuals",
		"Score individuals",
	],
	"Joint": [
		"spaces_joint_icon.jpg",
		"joint",
		"Display individuals and active configuration",
	],
	"Reference points": [
		"spaces_reference_icon.jpg",
		"reference_points",
		"Set reference points",
	],
	"Contest": [
		"spaces_contest_icon.jpg",
		"contest",
		"Display contest between rivals",
	],
	"Segments": [
		"spaces_segments_icon.jpg",
		"segments",
		"Describe segments in contest",
	],
	"Core": {
		"icon": "spaces_core_icon.jpg",
		"items": {
			"Spatially defined regions": [
				None,
				"core_regions",
				"Display core supporter regions",
			],
			"Left core supporters": [
				None,
				"core_left",
				"Display core supporters of left rival",
			],
			"Right core supporters": [
				None,
				"core_right",
				"Display core supporters of right rival",
			],
			"Both core supporters": [
				None,
				"core_both",
				"Display core supporters of both rivals",
			],
			"Neither core supporters": [
				None,
				"core_neither",
				"Display individuals not core supporter of rivals",
			],
		},
	},
	"Base supporters": {
		"icon": "spaces_base_icon.jpg",
		"items": {
			"Spatially defined regions": [
				None,
				"base_regions",
				"Display regions defining base of rivals",
			],
			"Left base supporters": [
				None,
				"base_left",
				"Display base supporters of left rival",
			],
			"Right base supporters": [
				None,
				"base_right",
				"Display base supporters of right rival",
			],
			"Both base supporters": [
				None,
				"base_both",
				"Display base supporters of both rivals",
			],
			"Neither base supporters": [
				None,
				"base_neither",
				"Display individuals not in base of rivals",
			],
		},
	},
	"Likely supporters": {
		"icon": "spaces_likely_icon.jpg",
		"items": {
			"Spatially defined regions": [
				None,
				"likely_regions",
				"Display regions defining likely supporters of rivals",
			],
			"Likely left supporters": [
				None,
				"likely_left",
				"Display likely supporters of left rival",
			],
			"Likely right supporters": [
				None,
				"likely_right",
				"Display likely supporters of right rival",
			],
			"Both likely supporters": [
				None,
				"likely_both",
				"Display likely supporters of both rivals",
			],
		},
	},
	"Battleground": {
		"icon": "spaces_battleground_icon.jpg",
		"items": {
			"Spatially defined regions": [
				None,
				"battleground_regions",
				"Display battleground regions",
			],
			"Battleground": [
				None,
				"battleground_segment",
				"Display battleground segment",
			],
			"Settled": [
				None,
				"battleground_settled",
				"Display settled segment",
			],
		},
	},
	"Convertible": {
		"icon": "spaces_convertible_icon.jpg",
		"items": {
			"Spatially defined regions": [
				None,
				"convertible_regions",
				"Display convertible regions",
			],
			"Convertible to the left": [
				None,
				"convertible_left",
				"Display individuals convertible to the left rival",
			],
			"Convertible to the right": [
				None,
				"convertible_right",
				"Display individuals convertible to the right rival",
			],
			"Both": [
				None,
				"convertible_both",
				"Display individuals convertible to both rivals",
			],
			"Settled": [
				None,
				"convertible_settled",
				"Display settled segment",
			],
		},
	},
	"Focused on first dimension": {
		"icon": "spaces_first_dim_icon.jpg",
		"items": {
			"Spatially defined regions": [
				None,
				"first_regions",
				"Display regions defined by first dimension",
			],
			"Left focused": [
				None,
				"first_left",
				"Display individuals on the left of mean on"
				" first dimension",
			],
			"Right focused": [
				None,
				"first_right",
				"Display individuals on the right of mean on"
				" first dimension",
			],
		},
	},
	"Focused on second dimension": {
		"icon": "spaces_second_dim_icon.jpg",
		"items": {
			"Spatially defined regions": [
				None,
				"second_regions",
				"Display regions defined by second dimension",
			],
			"Upper focused": [
				None,
				"second_upper",
				"Display individuals above mean on second dimension",
			],
			"Lower focused": [
				None,
				"second_lower",
				"Display individuals below mean on second dimension",
			],
		},
	},
})

help_menu_dict = MappingProxyType({
	"Help Content": [
		"spaces_help_icon.jpg",
		"help_content",
		"Help content",
	],
	"Status": ["spaces_status_icon.jpg", "status", "Display status"],
	"Verbose": [
		"spaces_verbosity_icon.jfif",
		"verbose",
		"Toggle between Terse and Verbose",
	],
	"About": ["spaces_about_icon.jpg", "about", "About Spaces"],
})

tester_menu_dict = MappingProxyType({
	"Tester": ["spaces_tester_icon.jpg", "tester"],
})


# ----------------------------------------------------------------------------
# Dictionary: basic_table_dict (renamed from display_tables_dict)
# Source: table_builder.py lines 59-84
# Purpose: Configuration for basic (non-square) tables
# ----------------------------------------------------------------------------

basic_table_dict = MappingProxyType({
	"configuration": {
		"source": "configuration_active",
		"data": "point_coords",
		"row_headers": "point_names",
		"column_headers": "dim_names",
		"row_height": 4,
		"format": "8.2f",
	},
	"grouped_data": {
		"source": "grouped_data_active",
		"data": "group_coords",
		"row_headers": "group_names",
		"column_headers": "dim_names",
		"row_height": 4,
		"format": "8.2f",
	},
	"target": {
		"source": "target_active",
		"data": "point_coords",
		"row_headers": "point_names",
		"column_headers": "dim_names",
		"row_height": 4,
		"format": "8.2f",
	},
})


# ----------------------------------------------------------------------------
# Dictionary: square_table_dict (renamed from square_tables_config)
# Source: table_builder.py lines 170-227
# Purpose: Configuration for square matrix tables
# ----------------------------------------------------------------------------

square_table_dict = MappingProxyType({
	"correlations": {
		"source_attr": "correlations_active",
		"data_attr": "correlations_as_dataframe",
		"item_names_attr": "item_names",
		"row_height": 4,
		"format_str": "8.2f",
		"diagonal": "1.00",
	},
	"similarities": {
		"source_attr": "similarities_active",
		"data_attr": "similarities_as_dataframe",
		"item_names_attr": "item_names",
		"row_height": 4,
		"format_str": "8.2f",
		"diagonal": "---",
	},
	"distances": {
		"source_attr": "configuration_active",
		"data_attr": "distances_as_dataframe",
		"item_names_attr": "item_names",
		"row_height": 4,
		"format_str": "8.2f",
		"diagonal": "    0.00",
	},
	"ranked_distances": {
		"source_attr": "configuration_active",
		"data_attr": "ranked_distances_as_dataframe",
		"item_names_attr": "item_names",
		"row_height": 4,
		"format_str": "8.1f",
		"diagonal": "0.0",
	},
	"ranked_similarities": {
		"source_attr": "similarities_active",
		"data_attr": "ranked_similarities_as_dataframe",
		"item_names_attr": "item_names",
		"row_height": 4,
		"format_str": "8.1f",
		"diagonal": "0.0",
	},
	"ranked_differences": {
		"source_attr": "similarities_active",
		"data_attr": "differences_of_ranks_as_dataframe",
		"item_names_attr": "item_names",
		"row_height": 4,
		"format_str": "8.1f",
		"diagonal": "0.0",
	},
	"shepard": {
		"source_attr": "similarities_active",
		"data_attr": "shepard_diagram_table_as_dataframe",
		"item_names_attr": "item_names",
		"row_height": 4,
		"format_str": "8.1f",
		"diagonal": "-",
	},
})


# ----------------------------------------------------------------------------
# Dictionary: statistical_table_dict (renamed from statistics_config)
# Source: table_builder.py lines 315-493
# Purpose: Configuration for general statistical tables
# ----------------------------------------------------------------------------

statistical_table_dict = MappingProxyType({
	"alike": {
		"source_attr": "current_command",
		"data_attr": "alike_df",
		"row_headers": [],
		"column_headers_attr": "data.columns",
		"format_spec": ["s", "s", "8.4f"],
	},
	"compare": {
		"source_attr": "target_active",
		"data_attr": "compare_df",
		"row_headers_attr": "source.point_names",
		"column_headers": [
			"Active\nX",
			"Active\nY",
			"Target\nX",
			"Target\nY",
		],
		"format_spec": ["8.4f", "8.4f", "8.4f", "8.4f"],
	},
	"directions": {
		"source_attr": "configuration_active",
		"data_attr": "directions_df",
		"row_headers_attr": "source.point_names",
		"column_headers": [
			"Slope",
			"Unit Circle\nX",
			"Unit Circle\nY",
			"Angle in\nDegrees",
			"Angle in\nRadians",
			"Quadrant",
		],
		"format_spec": ["16.2f", "8.2f", "8.2f", "8.2f", "8.2f", "s"],
	},
	"evaluations": {
		"source_attr": "evaluations_active",
		"data_attr": "stats_eval_sorted",
		"row_headers_attr": "source.names_eval_sorted",
		"column_headers": [
			"Mean",
			"Standard\nDeviation",
			"Min",
			"First\nquartile",
			"Median",
			"Third\nquartile",
			"Max",
		],
		"format_spec": "8.2f",
	},
	"factor_analysis": {
		"source_attr": "configuration_active",
		"data_attr": "factor_analysis_df",
		"row_headers": [],
		"column_headers": [
			"Eigenvalues",
			"Common Factor\nEigenvalues",
			"Commonalities",
			"Uniquenesses",
			"Item",
			"Loadings\nFactor 1",
			"Loadings\nFactor 2",
		],
		"format_spec": [
			"8.4f",
			"8.4f",
			"8.4f",
			"8.4f",
			"s",
			"8.4f",
			"8.4f",
		],
	},
	"individuals": {
		"source_attr": "individuals_active",
		"data_attr": "stats_inds",
		"row_headers_attr": "source.var_names[1:]",
		"column_headers": [
			"Mean",
			"Standard\nDeviation",
			"Min",
			"Max",
			"First\nquartile",
			"Median",
			"Third\nquartile",
		],
		"format_spec": "8.2f",
	},
	"paired": {
		"source_attr": "current_command",
		"data_attr": "_paired_df",
		"row_headers": [],
		"column_headers_dynamic": True,
		"format_spec": ["s", ".4f", ".4f"],
	},
	"sample_design": {
		"source_attr": "uncertainty_active",
		"data_attr": "sample_design_analysis_df",
		"row_headers": [],
		"column_headers": [
			"Repetition",
			"Selected \n N",
			"Percent",
			"Not selected \n N",
			"Percent",
		],
		"format_spec": ["d", "d", ".1f", "d", ".1f"],
	},
	"sample_repetitions": {
		"source_attr": "uncertainty_active",
		"data_attr": "sample_design_analysis_df",
		"row_headers": [],
		"column_headers": [
			"Repetition",
			"Selected \n N",
			"Percent",
			"Not selected \n N",
			"Percent",
		],
		"format_spec": ["d", "d", ".1f", "d", ".1f"],
	},
	"sample_solutions": {
		"source_attr": "uncertainty_active",
		"data_attr": "solutions_stress_df",
		"row_headers": [],
		"column_headers": ["Solution", "Stress"],
		"format_spec": ["d", "8.4f"],
	},
	"scores": {
		"source_attr": "scores_active",
		"data_attr": "stats_scores",
		"row_headers_attr": "source.dim_names",
		"column_headers": [
			"Mean",
			"Standard\nDeviation",
			"Min",
			"Max",
			"First\nquartile",
			"Median",
			"Third\nquartile",
		],
		"format_spec": "8.2f",
	},
	"scree": {
		"source_attr": "configuration_active",
		"data_attr": "min_stress",
		"row_headers": [],
		"column_headers": ["Dimensionality", "Best Stress"],
		"row_height": 8,
		"format_spec": ["4.0f", "8.2f"],
	},
	"stress_contribution": {
		"source_attr": "current_command",
		"data_attr": "stress_contribution_df",
		"row_headers": [],
		"column_headers": ["Item", "Stress Contribution"],
		"format_spec": ["d", "8.2f"],
	},
	"uncertainty": {
		"source_attr": "uncertainty_active",
		"data_attr": "solutions_stress_df",
		"row_headers": [],
		"column_headers": ["Solution", "Stress"],
		"format_spec": ["d", "8.4f"],
	},
	"spatial_uncertainty": {
		"source_attr": "uncertainty_active",
		"data_attr": "solutions_stress_df",
		"row_headers": [],
		"column_headers": ["Solution", "Stress"],
		"format_spec": ["d", "8.4f"],
	},
	"cluster_results": {
		"source_attr": None,
		"data_attr": None,
		"row_headers": [],
		"column_headers_attr": "list(data.columns)",
		"format_spec_dynamic": True,
	},
})


# ----------------------------------------------------------------------------
# Dictionary: rivalry_table_dict (renamed from rivalry_config)
# Source: table_builder.py lines 621-699
# Purpose: Configuration for rivalry segment tables
# ----------------------------------------------------------------------------

rivalry_table_dict = MappingProxyType({
	"base": {
		"data_attr": "base_pcts_df",
		"column_headers": [
			"Base\nSupporters of:",
			"Percent of\nPopulation",
		],
		"format_spec": "8.1f",
	},
	"battleground": {
		"data_attr": "battleground_pcts_df",
		"column_headers": ["Region", "Percent of\nPopulation"],
		"format_spec": "8.2f",
	},
	"convertible": {
		"data_attr": "conv_pcts_df",
		"column_headers": [
			"Convertible to:", "Percent of\nPopulation"
		],
		"format_spec": "8.1f",
	},
	"core": {
		"data_attr": "core_pcts_df",
		"column_headers": [
			"Core\nSupporters of:",
			"Percent of\nPopulation",
		],
		"format_spec": "8.1f",
	},
	"first": {
		"data_attr": "first_pcts_df",
		"column_headers": [
			"Party Oriented\nSupporters of:",
			"Percent of\nPopulation",
		],
		"format_spec": "8.1f",
	},
	"likely": {
		"data_attr": "likely_pcts_df",
		"column_headers": [
			"Likely\nSupporters of:",
			"Percent of\nPopulation",
		],
		"format_spec": "8.1f",
	},
	"second": {
		"data_attr": "second_pcts_df",
		"column_headers": [
			"Social Oriented\nSupporters of:",
			"Percent of\nPopulation",
		],
		"format_spec": "8.1f",
	},
	"segments": {
		"data_attr": "segments_pcts_df",
		"row_headers": [
			"Likely Supporters:",
			"",
			"Base supporters",
			"",
			"",
			"Core Supporters",
			"",
			"",
			"Party oriented",
			"",
			"Social oriented",
			"",
			"Battleground",
			"",
			"Convertible",
			"",
			"",
		],
		"column_headers": ["Segment", "Percent of\nPopulation"],
		"format_spec": "8.1f",
		"requires_scores": False,
	},
})


# ----------------------------------------------------------------------------
# Dictionary: title_generator_dict
# Purpose: Generate titles for table widgets in BuildOutputForGUI
# Structure: Maps command names to lambda functions that generate titles
# All lambdas take director parameter for uniform access pattern
# Alphabetically ordered for maintainability
# ----------------------------------------------------------------------------

title_generator_dict = MappingProxyType({
	"About": lambda d: (
		"Spaces was developed by Ed Schneider."
		"\n\nIt is based on programs he developed in the 1970s as "
		"a graduate student at "
		"The University of Michigan\nand while consulting on the Obama "
		"2008 campaign."
		"\n\nQuite a few individuals and organizations have "
		"contributed to the development of Spaces."
		"\n\nAmong those who have contributed (in alphabetical order) are:\n"
	),
	"Alike": lambda d: (
		f"Pairs with similarity using cutoff: {d.common.cutoff}"
	),
	"Base": lambda d: (
		f"Base supporters of {d.rivalry.rival_a.name} and "
		f"{d.rivalry.rival_b.name}"
	),
	"Battleground": lambda d: "Size of battleground",
	"Center": lambda d: (
		f"Configuration has {d.configuration_active.ndim} "
		f"dimensions and {d.configuration_active.npoint} points"
	),
	"Cluster": lambda d: (
		f"K-Means Clustering Results using "
		f"{d.common.name_source.capitalize()} (k={d.common.n_clusters})"
	),
	"Compare": lambda d: (
		f"After procrustean rotation active configuration matches "
		f"target configuration with disparity of {d.common.disparity:8.4f}"
	),
	"Configuration": lambda d: (
		f"Configuration has {d.configuration_active.ndim} "
		f"dimensions and {d.configuration_active.npoint} points"
	),
	"Contest": lambda d: (
		f"Segments are based on a contest between "
		f"{d.rivalry.rival_a.name} and {d.rivalry.rival_b.name}"
	),
	"Convertible": lambda d: (
		f"Potential supporters convertible to {d.rivalry.rival_a.name} "
		f"and {d.rivalry.rival_b.name}"
	),
	"Core supporters": lambda d: (
		f"Core supporters of {d.rivalry.rival_a.name} and "
		f"{d.rivalry.rival_b.name}"
	),
	"Correlations": lambda d: (
		"The correlations are shown as a square matrix"
	),
	"Create": lambda d: (
		f"Configuration has {d.configuration_active.ndim} "
		f"dimensions and {d.configuration_active.npoint} points"
	),
	"Deactivate": lambda d: "Deactivate",
	"Directions": lambda d: (
		f"Directions are based on the active configuration which has "
		f"{d.configuration_active.ndim} dimensions and "
		f"{d.configuration_active.npoint} points"
	),
	"Distances": lambda d: "Inter-point distances",
	"Evaluations": lambda d: (
		"Evaluations have been read and correlations computed"
	),
	"Exit": lambda d: "Exiting Spaces",
	"Factor analysis": lambda d: "Factor analysis",
	"Factor analysis machine learning": lambda d: (
		"Factor Analysis - Machine Learning"
	),
	"First dimension": lambda d: "Party oriented segments",
	"Grouped data": lambda d: (
		f"Grouped data has {d.grouped_data_active.ndim} dimensions and "
		f"{d.grouped_data_active.ngroups} groups"
	),
	"Help": lambda d: (
		"Help command under construction - stay tuned, please"
	),
	"History": lambda d: "Commands used",
	"Individuals": lambda d: (
		f"Individuals data has been read "
		f"({len(d.individuals_active.ind_vars)} rows)"
	),
	"Invert": lambda d: (
		f"Configuration has {d.configuration_active.ndim} "
		f"dimensions and {d.configuration_active.npoint} points"
	),
	"Joint": lambda d: (
		"Warning: Make sure the scores match the \n"
		"dimensions AND orientation of the active configuration."
	),
	"Likely supporters": lambda d: (
		f"Likely supporters of {d.rivalry.rival_a.name} and "
		f"{d.rivalry.rival_b.name}"
	),
	"Line of sight": lambda d: (
		f"Line of sight:\n"
		f"The {d.similarities_active.value_type} matrix has "
		f"{d.similarities_active.nreferent} items"
	),
	"MDS": lambda d: (
		f"Configuration has {d.configuration_active.ndim} dimensions and "
		f"{d.configuration_active.npoint} points and stress of "
		f"{d.common.best_stress: 6.4f}"
	),
	"Move": lambda d: (
		f"Configuration has {d.configuration_active.ndim} "
		f"dimensions and {d.configuration_active.npoint} points"
	),
	"New grouped data": lambda d: (
		f"Grouped data has {d.grouped_data_active.ndim} dimensions and "
		f"{d.grouped_data_active.ngroups} groups"
	),
	"Open sample design": lambda d: "Sample design has been read",
	"Open sample repetitions": lambda d: (
		"Sample repetitions have been read"
	),
	"Open sample solutions": lambda d: "Sample solutions have been read",
	"Open scores": lambda d: (
		f"Scores have been read ({len(d.scores_active.scores)} rows)"
	),
	"Open script": lambda d: (
		f"Script executed: {d.common.commands_executed} commands from "
		f"{d.common.script_file_name}"
	),
	"Paired": lambda d: (
		f"Relationships between "
		f"{d.configuration_active.point_names[d.common.focal_index]} "
		f"and other points"
	),
	"Principal components": lambda d: "Principal components",
	"Print configuration": lambda d: "Active configuration",
	"Print correlations": lambda d: "Active correlations",
	"Print evaluations": lambda d: "Active evaluations",
	"Print grouped data": lambda d: "Active grouped data",
	"Print individuals": lambda d: "Active individuals",
	"Print sample design": lambda d: "Active sample design",
	"Print sample repetitions": lambda d: "Active sample repetitions",
	"Print sample solutions": lambda d: "Active sample solutions",
	"Print scores": lambda d: "Active scores",
	"Print similarities": lambda d: "Active similarities",
	"Print target": lambda d: (
		f"Target configuration has {d.target_active.ndim} dimensions and "
		f"{d.target_active.npoint} points"
	),
	"Ranks differences": lambda d: "Difference of Ranks",
	"Ranks distances": lambda d: "Rank of Distances",
	"Ranks similarities": lambda d: "Rank of Similarities",
	"Redo": lambda d: f"Redid {d.common.cmd_state.command_name} command",
	"Reference points": lambda d: (
		f"Reference points will be {d.rivalry.rival_a.name} and "
		f"{d.rivalry.rival_b.name}"
	),
	"Rescale": lambda d: (
		f"Configuration has {d.configuration_active.ndim} "
		f"dimensions and {d.configuration_active.npoint} points"
	),
	"Rotate": lambda d: (
		f"Configuration has {d.configuration_active.ndim} "
		f"dimensions and {d.configuration_active.npoint} points"
	),
	"Sample designer": lambda d: (
		f"Sample design - Size of universe: {d.common.universe_size}, "
		f"Probability of inclusion: {d.common.probability_of_inclusion}"
	),
	"Sample repetitions": lambda d: (
		f"Sample repetitions - Size of universe: {d.common.universe_size}"
	),
	"Save configuration": lambda d: (
		f"The active configuration has been written to: \n"
		f"{d.common.name_of_file_written_to}\n"
	),
	"Save correlations": lambda d: (
		f"The active correlations have been written to:\n"
		f"{d.common.file_name}"
	),
	"Save grouped data": lambda d: (
		f"The active grouped data has been written to: \n"
		f"{d.common.name_of_file_written_to}\n"
	),
	"Save individuals": lambda d: (
		f"The active individuals have been written to:\n"
		f"{d.common.file_name}"
	),
	"Save sample design": lambda d: (
		f"The active sample design has been written to:\n"
		f"{d.common.file_name}"
	),
	"Save sample repetitions": lambda d: (
		f"The active sample repetitions have been written to:\n"
		f"{d.common.file_name}"
	),
	"Save sample solutions": lambda d: (
		f"The active sample solutions have been written to:\n"
		f"{d.common.file_name}"
	),
	"Save scores": lambda d: (
		f"The active scores have been written to:\n{d.common.file_name}"
	),
	"Save script": lambda d: (
		f"Script saved with {len(d.common.script_lines)} commands:\n"
		f"{d.common.file_name}"
	),
	"Save similarities": lambda d: (
		f"The active similarities have been written to:\n"
		f"{d.common.file_name}"
	),
	"Save target": lambda d: (
		f"The active target has been written to: \n"
		f"{d.common.name_of_file_written_to}\n"
	),
	"Score individuals": lambda d: (
		f"There are {d.scores_active.nscores} active scores for "
		f"{d.scores_active.nscored} individuals."
	),
	"Scree": lambda d: "Best stress by dimensionality",
	"Second dimension": lambda d: "Social oriented segments",
	"Segments": lambda d: (
		f"Segments defined by contest between {d.rivalry.rival_a.name} "
		f"and {d.rivalry.rival_b.name}"
	),
	"Settings - display sizing": lambda d: "Display sizing settings updated",
	"Settings - layout options": lambda d: "Layout options updated",
	"Settings - plane": lambda d: "Plane settings updated",
	"Settings - plot settings": lambda d: "Plot settings updated",
	"Settings - presentation layer": lambda d: "Presentation layer updated",
	"Settings - segment sizing": lambda d: (
		"Segment sizing settings updated"
	),
	"Settings - vector sizing": lambda d: "Vector sizing settings updated",
	"Shepard": lambda d: (
		"Rank of similarity above diagonal, "
		"rank of distance below diagonal"
	),
	"Similarities": lambda d: (
		f"The {d.similarities_active.value_type} matrix has "
		f"{d.similarities_active.nreferent} items"
	),
	"Status": lambda d: "Status of current session",
	"Stress contribution": lambda d: (
		f"Stress contribution of "
		f"{d.configuration_active.point_names[d.common.point_index]}"
	),
	"Target": lambda d: (
		f"Target configuration has {d.target_active.ndim} dimensions and "
		f"{d.target_active.npoint} points"
	),
	"Terse": lambda d: "Output will not include explanations",
	"Tester": lambda d: "Tester",
	"Uncertainty": lambda d: (
		"An ellipse around each point delineates with 95% confidence "
		"that the point lies within that point's ellipse"
	),
	"Undo": lambda d: f"Undid {d.common.cmd_state.command_name} command",
	"Varimax": lambda d: "Varimax rotation of active configuration",
	"Vectors": lambda d: (
		f"Vectors are based on the active configuration which has "
		f"{d.configuration_active.ndim} dimensions and "
		f"{d.configuration_active.npoint} points"
	),
	"Verbose": lambda d: "Output will include explanations",
	"View configuration": lambda d: (
		f"Configuration has {d.configuration_active.ndim} "
		f"dimensions and {d.configuration_active.npoint} points"
	),
	"View correlations": lambda d: (
		f"Correlation matrix has {d.correlations_active.nreferent} items"
	),
	"View custom": lambda d: (
		f"Configuration has {d.configuration_active.ndim} "
		f"dimensions and {d.configuration_active.npoint} points"
	),
	"View distances": lambda d: "Inter-point distances",
	"View evaluations": lambda d: "Evaluations",
	"View grouped data": lambda d: (
		f"Configuration is based on {d.common.grouping_var} and has "
		f"{d.grouped_data_active.ndim} dimensions and "
		f"{d.grouped_data_active.ngroups} points"
	),
	"View individuals": lambda d: "Individuals",
	"View point uncertainty": lambda d: (
		f"Point Uncertainty - {len(d.common.selected_indices)} points: "
		f"{', '.join(d.common.selected_points)}"
	),
	"View sample design": lambda d: (
		f"Sample design - Size of universe: {d.common.universe_size}, "
		f"Probability of inclusion: {d.common.probability_of_inclusion}"
	),
	"View sample repetitions": lambda d: "Sample repetitions",
	"View sample solutions": lambda d: (
		f"{d.sample_solutions_active.nsolutions} solutions have "
		f"{d.sample_solutions_active.ndim} dimensions and "
		f"{d.sample_solutions_active.npoint} points"
	),
	"View scores": lambda d: (
		f"There are {d.scores_active.nscores} active scores for "
		f"{d.scores_active.nscored} individuals."
	),
	"View script": lambda d: "Script commands",
	"View similarities": lambda d: (
		f"The {d.similarities_active.value_type} matrix has "
		f"{d.similarities_active.nreferent} items"
	),
	"View spatial uncertainty": lambda d: (
		f"Spatial Uncertainty - {d.sample_solutions_active.nsolutions} "
		f"solutions with {d.sample_solutions_active.ndim} dimensions and "
		f"{d.sample_solutions_active.npoint} points"
	),
	"View target": lambda d: (
		f"Target configuration has {d.target_active.ndim} dimensions and "
		f"{d.target_active.npoint} points"
	),
})


# ----------------------------------------------------------------------------
# Note: Feature dictionaries from dependencies.py are NOT included here
# because they are dynamically created in the __init__ method using
# runtime values from candidate and active objects.
# See dependencies.py lines 292-492 for:
# - new_feature_dict
# - existing_feature_dict
# These will remain in dependencies.py as they require runtime initialization.
# ----------------------------------------------------------------------------
