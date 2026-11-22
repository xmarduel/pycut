
TOP = .
MKINC = $(TOP)/make

# warning: my modified pyflakes for makefiles
export WITH_FLAKES=YES
export WITH_MYPY=YES
export WITH_RUFF=YES

include $(MKINC)/mk.defaults

SUBDIRS = gcodesimulator gcodeviewer

PYTHON_SOURCES = \
	gcode_generator.py \
	material_widget.py \
	operations_tableview.py \
	pycut.py \
	shapely_cam.py \
	shapely_ext.py \
	shapely_matplotlib.py \
	shapely_svgpath_io.py \
	shapely_utils.py \
	svgviewer.py \
	tabs_tableview.py \
	val_with_unit.py

PYTHON_LIBFILES = $(PYTHON_SOURCES:%.py=%.pyc)

all:: $(PYTHON_LIBFILES)

include $(MKINC)/mk.rules
