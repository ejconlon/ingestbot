# Targets for python applications. Define COMPONENT_NAME and include this file.
# See `Makefile.base` for more documentation.

include ../../python/Makefile.base

# Freeze dependencies specified in requirements files
.PHONY: pipcompile
pipcompile:
	python3 -m piptools compile requirements.in
	cp ../../python/dev-requirements.app.in ./dev-requirements.in
	python3 -m piptools compile dev-requirements.in
	rm dev-requirements.in

# Run the server locally with the default args.
# Copy the command and run it in bash to pass custom args.
.PHONY: run
run:
	.venv/bin/python3 -m $(COMPONENT_NAME).main

# Package the application
.PHONY: package
package:
	mkdir -p ../../.build
	cd ../../.build && rm -rf $(COMPONENT_NAME).zip requirements.$(COMPONENT_NAME).txt $(COMPONENT_NAME)
	cd ../../.build && sed -e"s/-e //g" ../components/$(COMPONENT_NAME)/requirements.txt > requirements.$(COMPONENT_NAME).txt
	python3 -m pip --cache-dir ../../.pipcache install -t ../../.build/$(COMPONENT_NAME) -r ../../.build/requirements.$(COMPONENT_NAME).txt
	cd ../../.build && cp -r ../components/$(COMPONENT_NAME)/$(COMPONENT_NAME) $(COMPONENT_NAME)
	cd ../../.build && sed -e"s/__COMPONENT_NAME__/$(COMPONENT_NAME)/g" ../python/entrypoint.sh.tpl > $(COMPONENT_NAME)/entrypoint.sh
	cd ../../.build && chmod +x $(COMPONENT_NAME)/entrypoint.sh
	cd ../../.build/$(COMPONENT_NAME) && zip -rq ../$(COMPONENT_NAME).zip .
	cd ../../.build && unzip -l $(COMPONENT_NAME).zip

# Run the packaged application
.PHONY: runpackage
runpackage:
	cd ../../.build && $(COMPONENT_NAME)/entrypoint.sh
