#!/usr/bin/env python3
"""Test to verify inspect.signature fix for OpenScript"""

import inspect


class TestCommand1:
	"""Command with just common parameter"""
	def execute(self, common):
		print(f"TestCommand1.execute called with common={common}")


class TestCommand2:
	"""Command with common and extra parameter with default"""
	def execute(self, common, use_metric=False):
		print(f"TestCommand2.execute called with common={common}, use_metric={use_metric}")


class TestCommand3:
	"""Command with common and required extra parameter"""
	def execute(self, common, axis):
		print(f"TestCommand3.execute called with common={common}, axis={axis}")


def test_signature_detection():
	"""Test that we correctly detect extra parameters"""
	print("=" * 60)
	print("Testing signature detection...")
	print("=" * 60)

	# Test Command 1 - just 'common'
	cmd1 = TestCommand1()
	sig1 = inspect.signature(cmd1.execute)
	params1 = list(sig1.parameters.keys())
	print(f"\nTestCommand1.execute signature:")
	print(f"  params: {params1}")
	print(f"  len(params): {len(params1)}")
	print(f"  len(params) > 1: {len(params1) > 1}")
	assert len(params1) == 1, "Should have 1 param (common)"
	assert params1[0] == 'common', "First param should be 'common'"

	# Test Command 2 - 'common' and 'use_metric' with default
	cmd2 = TestCommand2()
	sig2 = inspect.signature(cmd2.execute)
	params2 = list(sig2.parameters.keys())
	print(f"\nTestCommand2.execute signature:")
	print(f"  params: {params2}")
	print(f"  len(params): {len(params2)}")
	print(f"  len(params) > 1: {len(params2) > 1}")
	assert len(params2) == 2, "Should have 2 params (common, use_metric)"
	assert params2[0] == 'common', "First param should be 'common'"
	assert params2[1] == 'use_metric', "Second param should be 'use_metric'"
	param_obj = sig2.parameters['use_metric']
	print(f"  use_metric has default: {param_obj.default != inspect.Parameter.empty}")
	print(f"  default value: {param_obj.default}")

	# Test Command 3 - 'common' and required 'axis'
	cmd3 = TestCommand3()
	sig3 = inspect.signature(cmd3.execute)
	params3 = list(sig3.parameters.keys())
	print(f"\nTestCommand3.execute signature:")
	print(f"  params: {params3}")
	print(f"  len(params): {len(params3)}")
	print(f"  len(params) > 1: {len(params3) > 1}")
	assert len(params3) == 2, "Should have 2 params (common, axis)"
	assert params3[0] == 'common', "First param should be 'common'"
	assert params3[1] == 'axis', "Second param should be 'axis'"
	param_obj = sig3.parameters['axis']
	print(f"  axis has default: {param_obj.default != inspect.Parameter.empty}")

	print("\n" + "=" * 60)
	print("All tests passed!")
	print("=" * 60)


def test_call_logic():
	"""Test the actual calling logic"""
	print("\n" + "=" * 60)
	print("Testing call logic...")
	print("=" * 60)

	common_val = "common_object"

	# Test Command 1
	print("\n1. TestCommand1 (no extra params):")
	cmd1 = TestCommand1()
	sig1 = inspect.signature(cmd1.execute)
	params1 = list(sig1.parameters.keys())
	params_dict1 = {}

	if len(params1) > 1:
		print("  ERROR: Should not enter extra param branch")
	else:
		print("  Calling: cmd1.execute(common)")
		cmd1.execute(common_val)

	# Test Command 2 with param provided
	print("\n2. TestCommand2 with use_metric=True:")
	cmd2 = TestCommand2()
	sig2 = inspect.signature(cmd2.execute)
	params2 = list(sig2.parameters.keys())
	params_dict2 = {'use_metric': True}

	if len(params2) > 1:
		param_name = params2[1]
		print(f"  Extra param detected: {param_name}")
		if param_name in params_dict2:
			extra_value = params_dict2[param_name]
			print(f"  Calling: cmd2.execute(common, {extra_value})")
			cmd2.execute(common_val, extra_value)
		else:
			print("  ERROR: Param not in dict")
	else:
		print("  ERROR: Should enter extra param branch")

	# Test Command 2 with param not provided but has default
	print("\n3. TestCommand2 without use_metric (has default):")
	cmd3 = TestCommand2()
	sig3 = inspect.signature(cmd3.execute)
	params3 = list(sig3.parameters.keys())
	params_dict3 = {}

	if len(params3) > 1:
		param_name = params3[1]
		print(f"  Extra param detected: {param_name}")
		if param_name in params_dict3:
			print("  ERROR: Should not find param")
		else:
			param_obj = sig3.parameters[param_name]
			if param_obj.default != inspect.Parameter.empty:
				print(f"  Has default ({param_obj.default}), calling without extra param")
				cmd3.execute(common_val)
			else:
				print("  ERROR: No default")
	else:
		print("  ERROR: Should enter extra param branch")

	print("\n" + "=" * 60)
	print("All call tests passed!")
	print("=" * 60)


if __name__ == "__main__":
	test_signature_detection()
	test_call_logic()
