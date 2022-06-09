# Top-level targets

.PHONY: default
default:
	echo "No default target"

# Install system-level dependencies necessary to build the project
.PHONY: deps
deps:
	pip3 install pip-tools

# Clean build and dependency caches
.PHONY: clean
clean:
	rm -rf .build .pipcache
