import python_deps

class Dep:
	def __init__(self, name, language, count):
		self.name = name
		self.language = language
		self.count = count
	def __repr__(self):
		return f'Dep(name={self.name}, language={self.language}, count={self.count})'

def get_deps(path):
	deps = []
	deps.extend(get_language_deps(path, python_deps))
	return deps
	
def get_language_deps(path, language):
	files = language.get_files(path)
	deps_map = {}
	for f in files:
		f_deps = language.get_deps_for_file(f)
		if f_deps is None:
			continue
		for dep in f_deps:
			if dep in deps_map:
				deps_map[dep].count += 1
			else:
				deps_map[dep] = Dep(dep, 'python', 1)
	return list(deps_map.values())
