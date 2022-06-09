# Top-level targets

.PHONY: default
default:
	echo "No default target"

.PHONY: clean
clean:
	rm -rf .build .pipcache
