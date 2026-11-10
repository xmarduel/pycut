
REM in RESOURCES

REM generate qt resources
pyside6-rcc.exe -o ..\pycut_rc.py pycut.qrc
pyside6-rcc.exe -o ..\tutorial_rc.py tutorial.qrc
pyside6-rcc.exe -o ..\cnc_tutorial_rc.py cnc-tutorial.qrc
