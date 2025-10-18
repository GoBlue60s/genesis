"""Test script parsing logic."""

import ast

def parse_script_line(line: str) -> tuple[str, dict]:
	"""Parse a script line into command name and parameters."""
	parts = line.split()

	# For this test, assume single-word command
	command_name = parts[0]

	# Parse parameters
	params_dict = {}
	param_start = 1

	# Rejoin remaining parts
	param_str = " ".join(parts[param_start:])

	if param_str:
		current_key = None
		current_value = ""
		in_brackets = 0

		i = 0
		while i < len(param_str):
			char = param_str[i]

			if char == "=" and current_key is None and in_brackets == 0:
				current_key = current_value.strip()
				current_value = ""
			elif char in "[{(":
				in_brackets += 1
				current_value += char
			elif char in "]})":
				in_brackets -= 1
				current_value += char
			elif char == " " and in_brackets == 0:
				if current_key and current_value:
					try:
						params_dict[current_key] = ast.literal_eval(
							current_value.strip()
						)
						print(f"Evaluated {current_key}={current_value.strip()} as literal")
					except (ValueError, SyntaxError) as e:
						val = current_value.strip()
						if (
							(val.startswith('"') and val.endswith('"'))
							or (val.startswith("'") and val.endswith("'"))
						):
							val = val[1:-1]
						params_dict[current_key] = val
						print(f"Stored {current_key}={val} as string (error: {e})")
					current_key = None
					current_value = ""
			else:
				current_value += char

			i += 1

		# Handle last parameter
		if current_key and current_value:
			try:
				params_dict[current_key] = ast.literal_eval(
					current_value.strip()
				)
				print(f"Evaluated {current_key}={current_value.strip()} as literal")
			except (ValueError, SyntaxError) as e:
				val = current_value.strip()
				if (
					(val.startswith('"') and val.endswith('"'))
					or (val.startswith("'") and val.endswith("'"))
				):
					val = val[1:-1]
				params_dict[current_key] = val
				print(f"Stored {current_key}={val} as string (error: {e})")

	return command_name, params_dict


# Test with the problematic line
line = "Similarities file_name=C:/PythonProjects/genesis/data/Elections/1976/post_1976_los.txt value_type=dissimilarities"
cmd, params = parse_script_line(line)
print(f"\nCommand: {cmd}")
print(f"Parameters: {params}")
