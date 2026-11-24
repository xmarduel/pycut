# ---------------------------------------------------------------------
# Common Host make defines
# ---------------------------------------------------------------------
ifeq ($(HOST_ARCH), darwin)
#PYTHON_VERSION		= 3.12.9
#PYTHON_HOST_VERSION_MIN	= 3.12
#PYCOMP_VER			:= .cpython-312
PYTHON_VERSION		= 3.13.8
PYTHON_HOST_VERSION_MIN	= 3.13
PYCOMP_VER			:= .cpython-313

PYTHON_HOST_HOME	?= /Library/Frameworks/Python.framework/Versions/$(PYTHON_HOST_VERSION_MIN)
PYTHON_HOST			?= $(PYTHON_HOST_HOME)/bin/python3

PYTHON				:= $(PYTHON_HOST)

PYFLAKES			:= $(PYTHON_HOST_HOME)/bin/pyflakes
MYPY				:= $(PYTHON_HOST_HOME)/bin/mypy
MYPY_OPTIONS		:= 
RUFF				:= $(PYTHON_HOST_HOME)/bin/ruff
RUFF_OPTIONS		:= check

PYCACHE				:= __pycache__
MYPY_CACHE			:= .mypy_cache
RUFF_CACHE			:= .ruff_cache

PYSIDE_VERSION		= 6.12.0

PYSIDE_RCC = ${PYTHON_HOST_HOME}/bin/pyside6-rcc
PYSIDE_UIC = ${PYTHON_HOST_HOME}/bin/pyside6-uic
endif

# not tested
ifeq ($(HOST_ARCH), x86-linux64)
PYTHON_VERSION			= 3.9.7
PYTHON_HOST_VERSION_MIN	= 3.9
PYCOMP_VER				:= .cpython-39

PYTHON_HOST_HOME	?=/usr
PYTHON_HOST			?= $(PYTHON_HOST_HOME)/bin/python$(PYTHON_HOST_VERSION_MIN)

PYTHON				:= $(PYTHON_HOST)

PYCACHE			:= __pycache__
endif
