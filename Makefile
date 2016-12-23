OS := $(shell uname)
VERSION = `cat VERSION`
default:
	@echo
	@echo "Available tasks:"
	@echo
	@echo "inst   - (re)installs dependencies"
	@echo "wheel  - build & install wheel"
	@echo "egg    - build & install egg"
	@echo "test   - test"

.PHONY: inst
inst: inst2 inst3

.PHONY: inst2
inst2:	pip2 install --user cython pytest

.PHONY: inst3
inst3: pip3 install --user cython pytest

.PHONY: test
test: test2 test3

.PHONY: test2
test2:
	python2 -m pytest -vv

.PHONY: test3
test3:
	python3 -m pytest -vv

.PHONY: wheel
wheel: wheel2 wheel3

.PHONY: wheel2
wheel2: wheel2
	-yes | pip2 uninstall pyrfc
	python2 setup.py bdist_wheel
	pip2 install --user dist/pyrfc-$(VERSION)-cp27-cp27mu-linux_x86_64.whl
	#pip2 install --user dist/pyrfc-$(VERSION)-cp35-cp35m-win_amd64.whl

.PHONY: wheel3
wheel3: wheel3
	-yes | pip3 uninstall pyrfc
	python3 setup.py bdist_wheel
	pip3 install --user dist/pyrfc-$(VERSION)-cp35-cp35m-linux_x86_64.whl
	#pip2 install --user dist/pyrfc-$(VERSION)-cp27-cp27m-win_amd64.whl

.PHONY: egg
egg: egg2 egg3

.PHONY: egg2
egg2:
	-yes | pip2 uninstall pyrfc
	python2 setup.py bdist_egg
	python2 setup.py install --user

.PHONY: egg3
egg3:
	-yes | pip3 uninstall pyrfc
	python3 setup.py bdist_egg
	python3 setup.py install --user
