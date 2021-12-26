
REM in RESOURCES

REM generate qt resources
%PYTHONHOME%\Scripts\pyside6-rcc.exe -o ..\resources_rc.py %PYCUT_HOME%\RESOURCES\resources.qrc
