import sys
import dependancy_calculator as d

dir = sys.argv[1]
deps = d.get_deps(dir)
print(deps)
