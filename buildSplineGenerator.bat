pyinsset PYTHONOPTIMIZE=2
set PYTHONDONTWRITEBYTECODE=1
 
pipenv run pyinstaller ^
--windowed ^
--onefile ^
--optimize=2 ^
--strip ^
--noupx ^
--icon="splineIcon.ico" ^
splineGenerator.py ^
--clean ^
--name "Image To Spline" ^
--hiddenimport pyside6 ^
--noconfirm ^
