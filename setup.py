from cx_Freeze import setup, Executable
#base = "Win32GUI"
base = "Console"
executables = [Executable("comparer.py", base=base)]
includefiles = ["adoucisseurs.json","chauffe_eaux.json", "chromedriver.exe", "README.md"]
packages = ["time", "bs4", "json", "selenium", "chromedriver_binary", "xlsxwriter", "datetime", "os", "pandas", "urllib3"]
options = {
    'build_exe': {    
        'packages':packages,
        'include_files':includefiles,
    },  
}

setup(
    name = "Comparateur de prix",
    options = options,
    version = "1.0",
    description = 'Comparaison des prix concurents',
    executables = executables
)