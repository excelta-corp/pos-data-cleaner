# Creating an executable
If changes are made to the data cleaner, sharing the altered program
with Excelta's employees is typically done by creating an executable
file that can run without fuss on any Windows machine. Unfortunately,
there is not a one-button solution for this; however, the process is
relatively straightforward and easy to repeat.

A very useful module called PyInstaller "freezes" all the source code
necessary to run the program and bundles it together.

## Preparing to use PyInstaller
In order to create an executable that can run on any windows machine,
you must first prepare a Python environment on your own machine. See
["Running from source"](README.md#running-from-source) in the README for
more information.

PyInstaller's setup instructions can be found
[here](https://www.pyinstaller.org/).

## Creating a new executable
Once Python 3, Pandas, and PyInstaller are all working on your local
machine, you're ready to put together the executable. To minimize risk
of errors, make sure the program runs from source before proceeding.

1. From the repository, download `cleaner.py` and the entire `patterns/`
   and `reference/` subdirectories along with their contents. You should
   now have the following directory structure copied to your machine:
    ```
    ── pos-data-cleaner/
       │
       ├── patterns/
       │   ├── Disty1_PATTERN.csv
       │   ├── Disty2_PATTERN.csv
       │   └── etc ...
       ├── reference/
       │   ├── fileserver-path.txt
       │   ├── products.csv
       │   ├── state_abbreviations.csv
       │   ├── zip3_to_st_str.csv
       │   └── zip_ranges.csv
       └── cleaner.py
    ```
   *Please note that it may be easier to download the entire repository,
   and then simply delete unnecessary files.*
2. Open the pos-data-cleaner folder in Windows Explorer. In this folder,
   hold Shift and right click to open the expanded context menu, then
   choose **Open PowerShell window here.**
3. Type the following, then press Enter. 
    ```
    pyinstaller cleaner.py --exclude-module matplotlib --onefile
    ```
4.  When PyInstaller has finished, close the command prompt and have
    another look at the pos-data-cleaner folder. Notice the new `dist/`
    folder: This contains the `cleaner.exe` file. However, this
    executable will be looking for the `patterns/` and `reference/`
    subdirectories which are now above it. Some reorganization is
    necessary.
5.  Open the `dist/` folder and Cut `cleaner.exe`.
    Return to the `pos-data-cleaner` directory and Paste. 
    
    `cleaner.exe`
    and `cleaner.py` should now be in the same folder.
6.  Delete the `__pycache__`, `build`, and `dist` folders, then delete
    `cleaner.py` and `cleaner.spec`. 
    
    Only `cleaner.exe` and the `patterns/` and `reference/` folders
    should remain in the directory.
7.  Now, it's time to zip up the whole folder for distribution.
    Right-click on `pos-data-cleaner` and choose **Send to > Compressed
    (zipped) folder**
    
    Congratulations-you're done! This zipped folder can now be
    distributed to users or added to the next release.