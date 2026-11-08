
REM in RESOURCES

REM generate qt resources
pyside6-rcc.exe -o ..\resources_rc.py resources.qrc
pyside6-rcc.exe -o ..\resources_tutorial_rc.py resources-tutorial.qrc
pyside6-rcc.exe -o ..\resources_cnc_tutorial_rc.py resources-cnc-tutorial.qrc
