from cx_Freeze import setup, Executable

#base = "Win32GUI"
base = "Console"
executables = [Executable(script = 'comparer.py', base=base)]
includefiles = ["suivi.xlsx", "LISEZMOI.md", "vendeurs.xlsx"]
packages = ["time", "os", "sys", "numpy", "bs4", "datetime", "urllib3", "openpyxl", "selenium", "pandas", "chromedriver_autoinstaller"]
options = { 'build_exe': { 'packages':packages, 'include_files':includefiles}}

setup(
    name = "Comparateur",
    options = options,
    version = "1.0",
    description = 'Comparaison des prix concurents',
    executables = executables
)