
TOP = .
MKINC = $(TOP)/make

# warning: my modified pyflakes for makefiles
export WITH_FLAKES=YES
export WITH_MYPY=YES
export WITH_RUFF=YES

include $(MKINC)/mk.defaults

SUBDIRS = gcodesimulator gcodeviewer gcodeviewer_11_2 viewers_settings

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

PYTHON_UIS = mainwindow.ui
PYTHON_RCCS = 

PYTHON_LIBFILES = $(PYTHON_SOURCES:%.py=%.pyc)
PYTHON_UICFILES = $(PYTHON_UIS:%.ui=%_ui.py)
PYTHON_RCCFILES = $(PYTHON_RCCS:%.qrc=%_rc.py)

all:: $(PYTHON_LIBFILES) $(PYTHON_UICFILES) $(PYTHON_RCCFILES)
uic:: $(PYTHON_UICFILES)
rcc:: $(PYTHON_RCCFILES)

include $(MKINC)/mk.rules
