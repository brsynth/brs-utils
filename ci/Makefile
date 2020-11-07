SELF_DIR := $(dir $(lastword $(MAKEFILE_LIST)))

include $(SELF_DIR)/.env

# HELP
# This will output the help for each task
# thanks to https://marmelab.com/blog/2016/02/29/auto-documented-makefile.html
.PHONY: help test

help:
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

.DEFAULT_GOAL := help

# cli args
ARGS = $(filter-out $@,$(MAKECMDGOALS))

MAKE_CMD = $(MAKE) -s -C makefiles

# PYTHON VERSION
ifneq ($(strip $(python)),)
	PYTHON_ENV = _python$(python)
endif
ifeq ($(env),)
	env = build
endif


all: conda-build conda-test conda-convert conda-publish ## (default) Perform all conda process (build, test, convert, publish)

clean: check-conda
	@$(MAKE_CMD) -f conda-tools.mk clean

# FAST TESTING
check: ## Test code with 'pytest', this is the fastest way to test the code
	   @$(MAKE_CMD) -f test.mk check

test: ## Test code with 'pytest', this is the fastest way to test the code
	   @$(MAKE_CMD) -f test.mk test args=$(args)

check-inconda: check-conda ## Test conda package
ifneq ($(strip $(env)),)
	$(eval env=check)
endif
	@$(MAKE) check-environment-check env=$(env)
	@$(MAKE_CMD) -f conda-env.mk conda-run-env env=check cmd="make -C .. check"

test-inconda: check-conda ## Test code with 'pytest' within a conda environment, this is the fastest way to test the code
ifneq ($(strip $(env)),)
	$(eval env=test)
endif
		 @$(MAKE) check-environment-test env=$(env)
	   @$(MAKE_CMD) -f conda-env.mk conda-run-env env=$(env) \
																					      cmd="make -C .. test" \
																								args=$(ARGS)

# CONDA WORKFLOW
conda-build: check-conda ## Build (without tests) conda package, if 'python=<version>' (default is latest available) is set then the package will be built for this version of Python
	@$(MAKE_CMD) -f conda-tools.mk conda-build-only$(PYTHON_ENV)

conda-test: check-conda ## Test conda package, if 'python=<version>' (default is all variants of package built) is set then the package built for this version of Python will be tested
	@$(MAKE_CMD) -f conda-tools.mk conda-test-only$(PYTHON_ENV)

conda-convert: check-conda ## Convert conda package towards all platforms, if 'python=<version>' (default is all variants of package built) is set then the package built for this version of Python will be converted
	@$(MAKE_CMD) -f conda-tools.mk conda-convert$(PYTHON_ENV)

conda-publish: check-conda ## Publish conda package, if 'python=<version>' (default is all variants of package built) is set then the package built for this version of Python will be published
	@$(MAKE_CMD) -f conda-tools.mk conda-publish$(PYTHON_ENV)

conda-check-recipe: check-conda ## Check conda recipe
	@$(MAKE_CMD) -f conda-tools.mk conda-recipe-check




# ENVIRONMENT CHECKING
ifeq (,$(shell which conda))
    HAS_CONDA=False
else
    HAS_CONDA=True
    ENV_DIR=$(shell conda info --base)
    MY_ENV_DIR=$(ENV_DIR)/envs/$(env)
    CONDA_ACTIVATE=source $$(conda info --base)/etc/profile.d/conda.sh ; conda activate ; conda activate
endif
check-environment-%: check-conda
ifneq ("$(wildcard $(MY_ENV_DIR))","") # check if the directory is there
		@echo ">>> Found '$(env)' environment in $(MY_ENV_DIR). Skipping installation..." > /dev/null
else
		@echo ">>> '$(env)' folder is missing in $(ENV_DIR). Installing ..." > /dev/null
		@$(MAKE_CMD) -f conda-env.mk conda-create-env-$* env=$(env)
endif

check-conda:
ifeq (False,$(HAS_CONDA))
	$(error >>> Install conda first.)
endif
