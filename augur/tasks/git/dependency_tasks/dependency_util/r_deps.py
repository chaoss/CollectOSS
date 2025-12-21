import re
from pathlib import Path


def get_files(path):
	"""Find all R DESCRIPTION files in the path"""
	dir = path
	p = Path(dir)
	files = list(p.glob('**/DESCRIPTION'))
	return files


def get_deps_for_file(path):
	"""
	Parse R package dependencies from DESCRIPTION file.
	Extracts package names from Depends, Imports, and Suggests fields.
	"""
	try:
		with open(path, 'r', encoding='utf-8') as f:
			content = f.read()
	except UnicodeDecodeError:
		# Try with latin-1 encoding as fallback
		with open(path, 'r', encoding='latin-1') as f:
			content = f.read()
	
	deps = set()
	
	# Parse Depends, Imports, and Suggests fields
	# These can span multiple lines and use commas to separate packages
	for field in ['Depends', 'Imports', 'Suggests']:
		# Match the field and capture everything until the next field or end of content
		# Fields are at the start of a line
		pattern = rf'^{field}:\s*(.+?)(?=^[A-Z][^:]*:|$)'
		match = re.search(pattern, content, re.MULTILINE | re.DOTALL)
		
		if match:
			field_content = match.group(1)
			# Split by comma and process each package entry
			packages = field_content.split(',')
			
			for package in packages:
				# Clean up the package name
				# Remove version specifications like (>= 1.0), [>= 2.0], etc
				package = re.sub(r'\s*\([^)]*\)\s*', '', package)
				package = re.sub(r'\s*\[[^\]]*\]\s*', '', package)
				# Remove whitespace and newlines
				package = package.strip()
				
				# Skip empty strings and R base packages
				if package and package != 'R':
					deps.add(package)
	
	return list(deps) if deps else None
