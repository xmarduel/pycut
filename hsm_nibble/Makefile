
TOP = ..
MKINC = $(TOP)/make

include $(MKINC)/mk.defaults

SUBDIRS =

PYTHON_SOURCES = \
	arc_fitter.py \
	arc_utils.py \
	debug.py \
	dxf.py \
	geometry.py \
	helpers.py \
	path_assembler.py \
	path_planner.py \
	voronoi_centers.py

PYTHON_UIS = 
PYTHON_RCCS = 

PYTHON_LIBFILES = $(PYTHON_SOURCES:%.py=%.pyc)
PYTHON_UICFILES = $(PYTHON_UIS:%.ui=%_ui.py)
PYTHON_RCCFILES = $(PYTHON_RCCS:%.qrc=%_rc.py)

all:: $(PYTHON_LIBFILES) $(PYTHON_UICFILES) $(PYTHON_RCCFILES)
uic:: $(PYTHON_UICFILES)
rcc:: $(PYTHON_RCCFILES)

include $(MKINC)/mk.rules
