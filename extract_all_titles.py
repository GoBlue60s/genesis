#!/usr/bin/env python
"""Extract ALL command names and their corresponding title assignments."""

import re
from pathlib import Path

# Read all menu files
menu_files = [
	'src/filemenu.py',
	'src/editmenu.py',
	'src/viewmenu.py',
	'src/modelmenu.py',
	'src/transformmenu.py',
	'src/associationsmenu.py',
	'src/respondentsmenu.py',
	'src/helpmenu.py'
]

commands = {}

for filepath in menu_files:
	try:
		with open(filepath, 'r', encoding='utf-8') as f:
			content = f.read()

		# Split into classes
		class_splits = re.split(r'\nclass\s+(\w+Command):', content)

		# Process each class (skip first element which is before first class)
		for i in range(1, len(class_splits), 2):
			class_name = class_splits[i]
			class_body = class_splits[i+1]

			# Find command name assignment
			cmd_patterns = [
				r'self\._director\.command\s*=\s*"([^"]+)"',
				r'director\.command\s*=\s*"([^"]+)"',
				r'self\.command\s*=\s*"([^"]+)"'
			]

			command_name = None
			for pattern in cmd_patterns:
				match = re.search(pattern, class_body)
				if match:
					command_name = match.group(1)
					break

			if not command_name:
				continue

			# Find execute method
			exec_match = re.search(r'def execute\([^)]+\):[^}]+?(?=\n\tdef\s|\n\nclass\s|$)', class_body, re.DOTALL)
			if not exec_match:
				# Command has no execute method or we couldn't find it
				# Check __init__ for title
				init_match = re.search(r'def __init__\([^)]+\):[^}]+?(?=\n\tdef\s)', class_body, re.DOTALL)
				if init_match:
					init_body = init_match.group(0)
					title_match = re.search(r'self\._director\.title_for_table_widget\s*=\s*(.+?)(?=\n\t\t\w|\n\t\treturn|\n\n)', init_body, re.DOTALL)
					if title_match:
						title_expr = title_match.group(1).strip()
						commands[command_name] = {
							'class': class_name,
							'title': title_expr,
							'file': filepath,
							'location': '__init__'
						}
				continue

			exec_body = exec_match.group(0)

			# Find ALL title assignments (there may be multiple)
			title_patterns = [
				r'self\._director\.title_for_table_widget\s*=\s*(.+?)(?=\n\t\t[a-z_]|\n\t\tself\.|\n\t\tdirector\.|\n\t\treturn)',
				r'director\.title_for_table_widget\s*=\s*(.+?)(?=\n\t\t[a-z_]|\n\t\tself\.|\n\t\tdirector\.|\n\t\treturn)',
				r'self\.title_for_table_widget\s*=\s*(.+?)(?=\n\t\t[a-z_]|\n\t\tself\.|\n\t\tdirector\.|\n\t\treturn)'
			]

			all_titles = []
			for pattern in title_patterns:
				matches = re.findall(pattern, exec_body, re.DOTALL)
				all_titles.extend(matches)

			if all_titles:
				# Use the LAST title assignment (the final one before return)
				title_expr = all_titles[-1].strip()

				# Clean up multiline strings
				title_expr = re.sub(r'\s+', ' ', title_expr)
				title_expr = title_expr.replace('( ', '(').replace(' )', ')')

				commands[command_name] = {
					'class': class_name,
					'title': title_expr,
					'file': filepath,
					'location': 'execute'
				}
			elif command_name not in commands:
				# No title in execute, check __init__
				init_match = re.search(r'def __init__\([^)]+\):[^}]+?(?=\n\tdef\s)', class_body, re.DOTALL)
				if init_match:
					init_body = init_match.group(0)
					for pattern in title_patterns:
						title_match = re.search(pattern, init_body, re.DOTALL)
						if title_match:
							title_expr = title_match.group(1).strip()
							title_expr = re.sub(r'\s+', ' ', title_expr)
							commands[command_name] = {
								'class': class_name,
								'title': title_expr,
								'file': filepath,
								'location': '__init__'
							}
							break

	except Exception as e:
		print(f'Error processing {filepath}: {e}')
		import traceback
		traceback.print_exc()

# Print results sorted by command name
print("COMPLETE CATALOG OF COMMAND TITLES")
print("=" * 80)
print()

for cmd_name in sorted(commands.keys()):
	info = commands[cmd_name]
	title = info['title']

	# Determine if title is dynamic or static
	is_dynamic = bool(re.search(r'\{[^}]+\}|f"', title))
	title_type = "dynamic" if is_dynamic else "static"

	# Extract variables used
	variables = []
	if is_dynamic:
		var_matches = re.findall(r'\{([^}]+)\}', title)
		variables = [v.split(':')[0].strip() for v in var_matches]
		# Clean up variable names
		cleaned_vars = []
		for v in variables:
			# Extract just the primary variable reference
			if '.' in v:
				parts = v.split('.')
				cleaned_vars.append(parts[0])
			elif '[' in v:
				cleaned_vars.append(v.split('[')[0])
			else:
				cleaned_vars.append(v)
		variables = list(set(cleaned_vars))

	print(f"Command: {cmd_name}")
	print(f"Class: {info['class']}")
	print(f"Title: {title}")
	print(f"Type: {title_type}")
	if variables:
		print(f"Variables: {', '.join(sorted(variables))}")
	print()

print(f"\nTotal commands found: {len(commands)}")
