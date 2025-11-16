#!/usr/bin/env python
"""Extract command names and title assignments from all menu files."""

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
			lines = f.readlines()

		current_class = None
		current_command = None
		in_execute = False
		execute_indent = 0
		title_lines = []
		collecting_title = False

		for i, line in enumerate(lines):
			# Detect class definition
			class_match = re.match(r'^class\s+(\w+Command):', line)
			if class_match:
				current_class = class_match.group(1)
				current_command = None
				continue

			# Detect command assignment
			if current_class:
				cmd_match = re.search(r'(?:self\._director|director|self)\.command\s*=\s*"([^"]+)"', line)
				if cmd_match:
					current_command = cmd_match.group(1)
					continue

			# Detect execute method
			if re.match(r'\tdef execute\(', line):
				in_execute = True
				execute_indent = len(line) - len(line.lstrip('\t'))
				continue

			# End of execute method
			if in_execute and line.strip() and not line.startswith('\t' * (execute_indent + 1)):
				in_execute = False
				collecting_title = False
				if title_lines and current_command:
					# Join and clean the title
					title_text = ''.join(title_lines)
					commands[current_command] = {
						'class': current_class,
						'title': title_text.strip(),
						'file': filepath
					}
				title_lines = []

			# Collect title assignment
			if in_execute:
				title_match = re.search(r'(?:self\._director|director|self)\.title_for_table_widget\s*=\s*(.+)', line)
				if title_match:
					collecting_title = True
					title_lines = [title_match.group(1)]
					# Check if title is complete on this line
					if title_lines[0].count('(') == title_lines[0].count(')'):
						if current_command:
							commands[current_command] = {
								'class': current_class,
								'title': title_lines[0].strip(),
								'file': filepath
							}
						title_lines = []
						collecting_title = False
				elif collecting_title:
					# Continue collecting multi-line title
					title_lines.append(line.rstrip('\n'))
					# Check if we've closed all parentheses
					full_text = ''.join(title_lines)
					if full_text.count('(') == full_text.count(')'):
						if current_command:
							commands[current_command] = {
								'class': current_class,
								'title': full_text.strip(),
								'file': filepath
							}
						title_lines = []
						collecting_title = False

	except Exception as e:
		print(f'Error processing {filepath}: {e}')

# Print results sorted by command name
print("CATALOG OF COMMAND TITLES")
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
		variables = [v.split(':')[0].split('.')[0].strip() for v in var_matches]

	print(f"Command: {cmd_name}")
	print(f"Title: {title}")
	print(f"Type: {title_type}")
	if variables:
		print(f"Variables: {', '.join(set(variables))}")
	print()
