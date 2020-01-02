import tkinter as tk
import tkinter.messagebox
import os
import re
import glob
import pandas as pd
import datetime
from math import ceil
#from PIL import ImageTk, Image

# Parameter Zone -----------------------------+

file_list = []
pattern_selections = []
usa_selections = []
process_selections = []
disty_selections = []
error_log = []
progress_report = 0

# Window class setup -------------------------+
class Window(tk.Frame):
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        self.master = master
        self.init_window()

    # Creation of init_window
    def init_window(self):

        # changing the title of our master widget
        self.master.title("Disty POS Data Cleaner")

        # allowing the widget to take the full space of the root window
        self.pack(fill="both", expand=1)


# Scrollable Frame Class
# ************************
class ScrollFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent) # create a frame (self)

        self.canvas = tk.Canvas(self, borderwidth=0, background="#ffffff")          #place canvas on self
        self.viewPort = tk.Frame(self.canvas, background="#ffffff")                    #place a frame on the canvas, this frame will hold the child widgets
        self.vsb = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview) #place a scrollbar on self
        self.canvas.configure(yscrollcommand=self.vsb.set)                          #attach scrollbar action to scroll of canvas

        self.vsb.pack(side="right", fill="y")                                       #pack scrollbar to right of self
        self.canvas.pack(side="left", fill="both", expand=True)                     #pack canvas to left of self and expand to fil
        self.canvas_window = self.canvas.create_window((4,4), window=self.viewPort, anchor="nw",            #add view port frame to canvas
                                  tags="self.viewPort")

        self.viewPort.bind("<Configure>", self.onFrameConfigure)                       #bind an event whenever the size of the viewPort frame changes.
        self.canvas.bind("<Configure>", self.onCanvasConfigure)                       #bind an event whenever the size of the viewPort frame changes.

        self.onFrameConfigure(None)                                                 #perform an initial stretch on render, otherwise the scroll region has a tiny border until the first resize

    def onFrameConfigure(self, event):
        '''Reset the scroll region to encompass the inner frame'''
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))                 #whenever the size of the frame changes, alter the scroll region respectively.

    def onCanvasConfigure(self, event):
        '''Reset the canvas window to encompass inner frame when required'''
        canvas_width = event.width
        self.canvas.itemconfig(self.canvas_window, width = canvas_width)            #whenever the size of the canvas changes alter the window region respectively.


class Chooser(tk.Frame):
    def __init__(self, root):
        tk.Frame.__init__(self, root)
        self.scrollFrame = ScrollFrame(self)  # add a new scrollable frame.
        self.scrollFrame.pack(side="top", fill="both", expand=True)

    def printMsg(self, msg):
        print(msg)


# UI Functions ------------------------------+

def shut_down():
    root.destroy()

def change_step(new_step):
    global step_list

    step_list.destroy()
    step_list = tk.Frame(tk_frame_mid_left, borderwidth=10, background="#EEE")
    step_list.pack(expand=False)

    steps = ["Welcome", "Connected to fileserver", "Reference files located", "Processing", "Review"]

    for this_step in steps:

        step_text = "• " + this_step
        item = tk.Label(step_list, borderwidth=10, text=step_text)
        item.configure(font=("Helvetica", 10), foreground="gray")
        if new_step >= steps.index(this_step):
            item.configure(font=("Helvetica", 10, "bold"), foreground="#007770")
        item.pack(anchor="w")


def display(to_display, text=""):
    global tk_frame_display                             # Kill and recreate display frame
    tk_frame_display.destroy()
    tk_frame_display = tk.Frame(tk_frame_mid_right, name="f_display")
    tk_frame_display.pack(fill="both", expand=True)

    if to_display == "welcome":
        welcome_message = "Welcome to the Disty POS Data Cleaner program.\n\n" \
                       "Please connect to the fileserver, then click 'Check connection'"
        tk.Label(tk_frame_display, text=welcome_message, justify="left", borderwidth=20).pack(anchor="w")

    elif to_display == "message":
        if text:
            msg = tk.Label(tk_frame_display, name="l_current_msg", text=text, justify="left", borderwidth=20)
            msg.pack(anchor="w")

    elif to_display == "error":
        tk.Label(tk_frame_display, text="Error", justify="left", padx=20, foreground="red",
                 font=("Helvetica", 20, "bold")).pack(anchor="w")
        if text:
            tk.Label(tk_frame_display, text=text, justify="left", borderwidth=20, foreground="red")\
                .pack(anchor="w")
        else:
            tk.Label(tk_frame_display, text="An unknown error has occurred.", justify="left", borderwidth=20,
                     foreground="red").pack(anchor="w")

    elif to_display == "chooser":
        render_file_chooser()


def render_file_chooser():
    global tk_frame_display
    global pattern_selections
    pattern_selections = []
    global file_list
    global usa_selections
    global process_selections
    global disty_selections

    chooser = Chooser(tk_frame_display)
    chooser.pack(side="top", fill="both", expand=True)

    # Set up buttons
    next_button.config(text="Process Selected", command=process_selected)

    tk.Label(chooser.scrollFrame.viewPort, text="File", bg="#FFF")\
        .grid(row=0, column=0, sticky="w", ipadx=4, ipady=2)
    tk.Label(chooser.scrollFrame.viewPort, text="Pattern (Click to change)", bg="#FFF")\
        .grid(row=0, column=1, sticky="w", ipadx=4, ipady=2)
    tk.Label(chooser.scrollFrame.viewPort, text="Disty Name", bg="#FFF")\
        .grid(row=0, column=2, sticky="w", ipadx=4, ipady=2)
    tk.Label(chooser.scrollFrame.viewPort, text="USA ONLY", bg="#FFF")\
        .grid(row=0, column=3, sticky="w", ipadx=4, ipady=2)
    tk.Label(chooser.scrollFrame.viewPort, text="Process", bg="#FFF")\
        .grid(row=0, column=4, sticky="w", ipadx=4, ipady=2)

    file_list = get_csv_files("fileserver_path_input")
    pattern_list = get_csv_files("fileserver_path_patterns")

    for file_name in file_list:
        row = file_list.index(file_name) + 1

        # Function to retrieve appropriate row background color
        def get_bg(this_row):
            if this_row % 2 == 0:
                return "#FFF"
            else:
                return "#EEE"

        label_frame = tk.Frame(chooser.scrollFrame.viewPort, bg=get_bg(row))
        label_frame.grid(row=row, column=0, ipadx=4, ipady=2, sticky="nsew")

        this_row_label = tk.Label(label_frame, text=file_name, bg=get_bg(row))
        this_row_label.pack(side="left")

        # Pattern dropdown variable
        pattern_var = tk.StringVar(root)

        # Get default pattern and set variable
        file_disty_string = file_name.split(".csv")[0].lower()
        pattern_keys = [x.split("_")[0].lower() for x in pattern_list]
        try:
            pattern_keys.index(file_disty_string.lower())
            pattern_var.set(pattern_list[pattern_keys.index(file_disty_string)])
            pattern_selections.append(pattern_var)
        except ValueError:
            pattern_var.set("[ CLICK TO SELECT ]")
            pattern_selections.append(pattern_var)

        # Pattern display
        pattern_frame = tk.Frame(chooser.scrollFrame.viewPort, bg=get_bg(row))
        pattern_frame.grid(row=row, column=1, sticky="nsew")

        pattern_option = tk.OptionMenu(pattern_frame, pattern_var, *pattern_list)
        pattern_option.config(fg="#007770", relief="flat")
        pattern_option.config(indicatoron=0, highlightthickness=0, bg=get_bg(row))
        pattern_option.config(activeforeground="blue", activebackground=get_bg(row))
        pattern_option.pack(side="left", fill="both")

        # Get default disty and set variable
        disty_disty_string = file_name.split(".csv")[0].strip()
        disty_input = tk.StringVar()
        disty_input.set(disty_disty_string)

        # Disty Field Display
        disty_entry_field = tk.Entry(chooser.scrollFrame.viewPort, textvariable=disty_input)
        disty_entry_field.grid(row=row, column=2, sticky="nsew")
        disty_entry_field.config(highlightthickness=0, bg=get_bg(row))
        disty_selections.append(disty_input)

        # USA checkbutton variable
        is_usa = tk.BooleanVar()

        # USA display
        usa_checkbutton = tk.Checkbutton(chooser.scrollFrame.viewPort, variable=is_usa, bg=get_bg(row))
        usa_checkbutton.grid(row=row, column=3, sticky="nsew")
        usa_selections.append(is_usa)

        # Process checkbutton variable
        to_process = tk.BooleanVar()
        process_checkbutton = tk.Checkbutton(chooser.scrollFrame.viewPort, variable=to_process, bg=get_bg(row))
        process_checkbutton.grid(row=row, column=4, sticky="nsew")
        process_selections.append(to_process)

    # Set up Select All button
    def select_all():
        global process_selections
        if False in [x.get() for x in process_selections]:
            [x.set(True) for x in process_selections]
        else:
            [x.set(False) for x in process_selections]
    select_all_button = tk.Button(tk_frame_bot, text="Select/Clear all")
    select_all_button.pack(side="right", pady=10)
    select_all_button.config(command=select_all)


# Program Functions -------------------------+

def parse_config():
    try:
        config_obj = open("config.ini", "r")
        if config_obj.mode == "r":
            config_text = config_obj.readlines()
            config_obj.close()

            path_dict = {}
            path_list = ["fileserver_path_root",
                         "fileserver_path_reference",
                         "fileserver_path_patterns",
                         "fileserver_path_input",
                         "fileserver_path_output",
                         "zip_fs_path",
                         "prod_fs_path"]

            for line in config_text:
                var_string = line.split("=")[0]
                path_string = line.split("=")[-1].strip()
                for path_to_check in path_list:
                    if path_to_check in var_string:
                        path_dict[path_to_check] = path_string

            return path_dict

    except FileNotFoundError:
        display("error", "Config.ini file could not be found!")
        next_button.config(state="disabled")


def check_for_fileserver():
    global path_dict
    path_to_check = str(path_dict["fileserver_path_root"])
    if os.path.exists(path_to_check):
        change_step(1)
        message_text = "Fileserver connected.\n\nClick Continue to verify that all necessary reference\n"
        message_text += "files can be found on the fileserver."
        display("message", message_text)
        next_button.config(text="Continue", command=verify_files)

    else:
        display("message", "Fileserver not connected.")
        return


def verify_files():
    errors = ""
    for ref_file in path_dict.values():
        if not os.path.exists(ref_file):
            errors += (ref_file.split("/")[-1] + "\n")
    if errors == "":
        change_step(2)
        display("message", "All files successfully located.\n\nClick Continue to load raw data files.")
        next_button.config(text="Continue", command=load_input)
    else:
        error_text = "The following files could not be located:\n\n" + errors
        error_text += "\nPlease double-check config.ini and restart the program."
        display("error", error_text)
        next_button.config(state="disabled")


def get_csv_files(path):
    file_list = []
    os.chdir(path_dict[path])
    for file in glob.glob("*.csv"):
        file_list.append(file)
    return file_list


def load_input():
    # -- Clear all parameters, in case program is being reset -- #
    global file_list
    global pattern_selections
    global usa_selections
    global process_selections
    global disty_selections
    global error_log
    global progress_report

    file_list = []
    pattern_selections = []
    usa_selections = []
    process_selections = []
    disty_selections = []
    error_log = []
    progress_report = 0

    # -- Then, load chooser -- #
    change_step(2)
    display("chooser")


def process_selected():
    global file_list
    global pattern_selections
    global usa_selections
    global process_selections
    global disty_selections
    global progress_report
    global error_log
    global next_button

    progress_report = 0
    error_log = []

    series_file = pd.Series(file_list)
    series_pattern = pd.Series(x.get() for x in pattern_selections)
    series_disty = pd.Series(x.get() for x in disty_selections)
    series_usa = pd.Series(x.get() for x in usa_selections)
    series_process = pd.Series(x.get() for x in process_selections)

    df = pd.concat([series_file, series_pattern, series_disty, series_usa, series_process], axis=1)
    df.columns = ["File", "Pattern", "Disty", "USA", "Process"]
    df.replace(to_replace="[ CLICK TO SELECT ]", value="", inplace=True)

    df_proc = df.loc[(df["Pattern"] != "") & (df["Disty"] != "") & (df["Process"])]

    # Make sure that all files selected to process have the necessary inputs
    total_attempts = len(series_process[series_process == True])        # Checkboxes marked as "Process"
    successes = len(df_proc)                                            # Files with sufficient info
    if successes < total_attempts:
        msg = str(total_attempts - successes) + " of the " + str(total_attempts)
        msg += " selected files can not be processed. Please ensure that all selected files have a valid Pattern file"
        msg += " selected and a Disty name entered."
        tkinter.messagebox.showwarning("Warning", msg)
    elif total_attempts == 0:
        tkinter.messagebox.showwarning("Warning", "Please select at least one file to process.")
    else:
        # If all selected files are probably valid, process them.
        active_ui_setup(df_proc)
        tk_frame_display.update()
        active_process_started(df_proc)
        # Change the "processing" display message to "complete."
        path_to_msg = ".!window.f_mid.f_mid_right.f_display.l_current_msg"
        root.nametowidget(path_to_msg).config(text="Processing complete.")
        # Message box
        tkinter.messagebox.showinfo("Task Complete", "All files have finished processing.\n\n"
                                                     "Please take note of the any failures\n\n"
                                                     "Then, either close the window, or click 'Return to file chooser' "
                                                     "to process additional files.")
        change_step(5)
        next_button.config(state="normal", text="Return to file chooser", command=load_input)


def active_ui_setup(dataframe_to_process):
    global select_all_button
    global next_button

    # UI Wrangling
    tk_frame_bot.pack_slaves()[-1].destroy()            # Destroy the last added button in the bottom frame
    next_button.config(state="disabled")
    change_step(3)
    display("message", "Processing . . .")

    tk.Label(tk_frame_display, text="|░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░|").pack(anchor="w")  #48
    for row in dataframe_to_process.itertuples():
        me = tk.Label(tk_frame_display, name=row.Disty.lower(), text=row.Disty)
        me.pack(anchor="w")


def active_process_started(dataframe_to_process):
    global error_log

    # Process each DataFrame row
    reference_updates()
    for row in dataframe_to_process.itertuples():
        result = process_file(row.File, row.Pattern, row.Disty, row.USA)

        path_to_disty_label = ".!window.f_mid.f_mid_right.f_display." + row.Disty.lower()
        this_disty_result = row.Disty + ": "

        if not result:
            this_disty_result += "FAILED"
            reason = [x[1] for x in error_log if x[0] == row.Disty]
            this_disty_result += " Reason: " + str(reason[0])
            root.nametowidget(path_to_disty_label).config(text=this_disty_result, fg="red")
        else:
            this_disty_result += "COMPLETE"
            root.nametowidget(path_to_disty_label).config(text=this_disty_result, fg="#007770")

        progress_bar_update()


def progress_bar_update():
    global progress_report          # To access the progress bar

    global process_selections       # To get number of files and maximum of progress bar
    series_process = pd.Series(x.get() for x in process_selections)

    # Prepares a current and total value for the progress bar
    progress_report += 1
    total = len(series_process[series_process == True])
    so_far = progress_report / total                        # E.g. 1/4, or .25
    remaining = 1 - so_far                                  # E.g. 3/4, or .75

    # Composes an updated progress bar with the progress report data
    new_bar_string = "|"
    new_bar_string += "▓" * ceil(48 * so_far)
    new_bar_string += "░" * ceil(48 * remaining)
    new_bar_string = new_bar_string[:49]
    new_bar_string += "|"

    tk_frame_display.pack_slaves()[1].config(text=new_bar_string)
    tk_frame_display.update()


# UI Initialization -------------------------+
root = tk.Tk()
root.geometry("800x600")
app = Window(root)

tk_frame_top = tk.Frame(app, height=80, background="#DDD")
tk_frame_top.pack(fill="x", anchor="n")

# -- Title label and logo
tk.Label(tk_frame_top, text="Disty POS Data Cleaner", bg="#DDD", fg="#222", font=("Arial", 20), padx=20).pack(side="left")

#logo_image = Image.open("excelta-logo.png")
#logo_render = ImageTk.PhotoImage(logo_image)

#imagebin = tk.Label(tk_frame_top, image=logo_render, bg="#DDD")
#imagebin.pack(side="right")

tk_frame_mid = tk.Frame(app, name="f_mid", background="#EEE")
tk_frame_mid.pack(fill="both", expand=1)

tk_frame_mid_left = tk.Frame(tk_frame_mid, width=128, background="#EEE")
tk_frame_mid_right = tk.Frame(tk_frame_mid, name="f_mid_right", background="yellow")

tk_frame_mid_left.pack(side="left", fill="both", expand=False)
tk_frame_mid_right.pack(side="right", fill="both", expand=True)

tk_frame_bot = tk.Frame(app, height=40, background="#CCC")
tk_frame_bot.pack(fill="x", anchor="s")

tk_frame_display = tk.Frame(tk_frame_mid_right, name="f_display")
tk_frame_display.pack(fill="both", expand=True)

#
step_list = tk.Frame(tk_frame_mid_left, borderwidth=10, background="#EEE")

next_button = tk.Button(tk_frame_bot, text="Check connection")
next_button.pack(side="right", pady=10, padx=10)
next_button.config(command=check_for_fileserver)

path_dict = parse_config()
change_step(0)
display("welcome")


##########################################################################################
##########################################################################################
##########################################################################################
#########                                                                        #########
#########                    DATA CLEANER PROGRAM STARTS BELOW                   #########
#########                                                                        #########
##########################################################################################
##########################################################################################
##########################################################################################

# Bringing the functionality of cleaner.py into a series of functions with more robust error checking.
# This process can take one or more files along with predefined user choices and perform multiple outputs.

###########
#  SETUP  #
###########

# Master reference DataFrames for Product and Reference. These will be the same for all items in batch run.
ref_zip_ter = ""
ref_item_product = ""

#########################
#  HACKED UP DATETIME   #
#########################


def get_date_field():
    today = datetime.datetime.now()
    year = today.year
    month = today.month - 1
    # In case of January of a new year
    if int(month) == 0:
        year = year - 1
        month = 12
    day = 1
    return str(month) + "/" + str(day) + "/" + str(year)


this_month = get_date_field()

##############################
#  Global / Setup Functions  #
##############################


def reference_updates():
    """ Retrieves the Product Lookup Table and Zip Code Lookup Table from the fileserver. """
    global ref_item_product
    global ref_zip_ter

    # Get the product reference table.
    try:
        prod_fs = pd.read_csv(path_dict["prod_fs_path"], ",", dtype=str)
        ref_item_product_temp = prod_fs.iloc[:, 0:3]
        ref_item_product_temp.columns = ["Item", "Group", "Category"]
        ref_item_product_temp = ref_item_product_temp.applymap(lambda x: x.strip() if isinstance(x, str) else x)
        ref_item_product = ref_item_product_temp  # SAVE to global variable ref_item_product.

    except FileNotFoundError:
        quit("Could not locate products reference table.")

    # Get the zipcode lookup table.
    try:
        zip_fs = pd.read_csv(path_dict["zip_fs_path"], ",", dtype=str)
        ref_zip_ter_temp = zip_fs.iloc[:, 0:2]
        ref_zip_ter_temp.columns = ["FirstZip", "Territory"]

        # Convert zip_ter to zip_ranges
        i = 0
        lastzip_series = []
        while i < len(ref_zip_ter_temp):
            if i == len(ref_zip_ter_temp) - 1:
                lastzip = 99999
            else:
                lastzip = ref_zip_ter_temp.loc[i + 1, "FirstZip"]
                lastzip = int(lastzip) - 1
            lastzip_series.append(lastzip)
            i += 1

        ref_zip_ter_temp.insert(2, "LastZip", lastzip_series, True)  # Add the LastZip column.
        ref_zip_ter = ref_zip_ter_temp  # SAVE to global variable ref_zip_ter.

    except FileNotFoundError:
        quit("Could not locate zip code reference table.")


##########################
#  Processing Functions  #
##########################

def process_file(input_file, pattern_file, disty_name, usa):
    """ Contains the bulk of the data cleaner process. """

    global error_log    # To report fatal errors as well as other incidents.

    # -------------------------------------------------------------   LOAD RAW

    try:
        raw_data = pd.read_csv(path_dict["fileserver_path_input"] + "/" + input_file)  # Load the raw file
    except FileNotFoundError:
        error_log.append([disty_name, "Input file could not be read"])
        return False

    raw_data.rename(columns=lambda x: x.strip(), inplace=True)  # Strip out extra space in column names
    raw_data = raw_data.applymap(lambda x: x.strip() if isinstance(x, str) else x)  # Trim whitespace from all strings

    # Eliminate completely empty columns from the right side of the dataframe
    while len(raw_data.columns) > 0:
        if raw_data.iloc[:, -1].dropna().empty:
            raw_data = raw_data.iloc[:, :-1]
        else:
            break

    # Check to see if all columns have names. Otherwise, rename them with numbers.
    check_cols = [s for s in list(raw_data.columns) if "Unnamed" in s]
    if len(check_cols) > 0:
        alphabet = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M']
        alphabet += ['N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
        alphabet += ['AA', 'AB', 'AC', 'AD', 'AE', 'AF', 'AG', 'AH', 'AI', 'AJ', 'AK', 'AL', 'AM']
        alphabet += ['AN', 'AO', 'AP', 'AQ', 'AR', 'AS', 'AT', 'AU', 'AV', 'AW', 'AX', 'AY', 'AZ']
        col_array = alphabet[:len(raw_data.columns)]
        del alphabet
        raw_data.columns = col_array

    raw_data.dropna(axis="columns", how="all", inplace=True)  # Drop empty columns
    raw_data['Origin'] = raw_data.index  # Finally, give the raw_data DataFrame an index

    # -------------------------------------------------------------   BRING IN PATTERN FILE

    try:
        pattern = pd.read_csv(path_dict["fileserver_path_patterns"] + "/" + pattern_file, ",")
        pattern.set_index('Target', inplace=True)
        pass

    except FileNotFoundError:
        error_log.append([disty_name, "Pattern file could not be read."])
        return False

    # -------------------------------------------------------------   SET UP 'CLEANED' DATAFRAME

    cleaned_columns = ["Origin", "Customer", "City", "St", "Zip", "Item", "Qty", "Cost", "Ext", "Mon", "Disty"]
    cleaned = pd.DataFrame(None, columns=cleaned_columns)

    # --------- ORIGIN COLUMN --------- #

    cleaned["Origin"] = raw_data["Origin"]  # Set 'Origin' column to link to raw data...

    # --------- RAW / PATTERN COLUMN NAME CHECK --------- #

    # --------- STRING PATTERN MATCHES --------- #

    # Loop through string columns and set data from raw
    for column_name in list(["Customer", "City", "St", "Zip", "Item", "Disty"]):
        # Try to grab the pattern row named column_name, or skip if not found.
        try:
            source = pattern.loc[column_name, "Source"]
        except KeyError:
            continue

        if isinstance(source, str):
            try:
                data = raw_data[source].astype(str)
            except KeyError:
                error_log.append([disty_name, "Error reading " + source + " from raw file. Check pattern file."])
                return False
            # --------- STRIP STRING --------- #

            replace_string = pattern.loc[column_name, "Strip String"]
            if isinstance(replace_string, str):
                replace_terms = replace_string.split("|")  # Break into list with delimiter
                for term in replace_terms:  # Process each type of term
                    if term[:2] == ">>":  # If this is an exterminator string, kill all before/after.
                        # Destroy everything after the characters following >>
                        term = term[2:]
                        data = data.apply(lambda x: x.split(term))
                        data = data.apply(lambda x: x[0])
                    elif term[:2] == "<<":
                        # Destroy everything before the characters following <<
                        term = term[2:]
                        data = data.apply(lambda x: x.split(term))
                        data = data.apply(lambda x: x[-1])
                    else:  # Otherwise, just remove the given string.
                        # Replace strip string value with nothing.
                        data = data.str.replace(term, "")

            # --------- END STRIP STRING --------- #

            cleaned[column_name] = data

        else:
            # Since there is no "source" on the pattern file, move along.
            # error_log.append([disty_name, "Invalid data (" + str(source) + ") linked in pattern file."])
            # return False
            continue

    # --------- NUMBER PATTERN MATCHES --------- #

    num_to_calc = ""  # Set an empty string to fill with missing calculated field.

    for column_name in list([["Qty", int], ["Cost", float], ["Ext", float]]):
        source = pattern.loc[column_name[0], "Source"]

        if isinstance(source, str):  # Check that there is a string in the source column of the pattern file.

            data = raw_data[source]  # Set data variable to raw data series
            data = data.replace('[^-.0-9]', '', regex=True)  # Remove all characters other than numbers and decimals
            data = data.replace("", 0)  # Replace empty strings with 0
            data = data.fillna(0)  # Replace any NaN with 0

            i = 0  # Replace anything that is still not a number with zero
            while i < len(data):
                try:
                    float(data[i])
                except ValueError:
                    data[i] = 0
                i = i + 1
            del i

            if column_name[1] == int:  # If type is int, convert to float first to fix negative string bug
                data = data.astype(float)
                data = data.astype(int)

            cleaned[column_name[0]] = data.astype(column_name[1])  # Copy to cleaned DataFrame

        else:  # If not a string, this could calculated field. Quantity is required, so kill if we don't have it.
            if column_name[0] == "Qty":
                error_log.append([disty_name, "Qty field cannot be found."])
                return False

            # Either Ext or Cost may be missing. When the missing field is found, write it to num_to_calc.
            elif column_name[0] == "Ext" and num_to_calc == "":
                num_to_calc = "Ext"
            elif column_name[0] == "Cost" and num_to_calc == "":
                num_to_calc = "Cost"
            # We need either Ext or Cost. If both try to write to num_to_calc, one will fail the above elif.
            else:
                error_log.append([disty_name, "Ext or Cost cannot be found."])
                return False

    # Calculate and add the missing field.
    if num_to_calc != "":
        if num_to_calc == "Ext":  # If we're missing Ext, multiply Cost by Qty.
            cleaned[num_to_calc] = cleaned["Cost"] * cleaned["Qty"]
        elif num_to_calc == "Cost":  # Otherwise, if we're missing Cost, Ext by Qty
            cleaned[num_to_calc] = cleaned["Ext"] / cleaned["Qty"]
        else:
            error_log.append([disty_name, "Error calculating missing Cost or Ext values."])
            return False

    # --------- KNOWN VALUES --------- #

    if cleaned["Disty"].dropna().empty:  # Populate the distributor column
        cleaned["Disty"] = disty_name  # if nothing was found in Pattern file

    cleaned["Mon"] = this_month  # Populate month column

    # --------- ELIMINATING GARBAGE ROWS --------- #

    drop_no_item = cleaned[~cleaned["Item"].isnull()]  # Drop any row without an item number
    drop_no_item = drop_no_item[drop_no_item["Item"] != ""]
    drop_no_item = drop_no_item[drop_no_item["Item"] != "nan"]

    if len(drop_no_item) < len(cleaned):
        cleaned = drop_no_item
        del drop_no_item
    else:
        del drop_no_item

    # Recreate the numeric index for iteration
    cleaned.index = pd.RangeIndex(len(cleaned.index))

    # --------- REFERENCED VALUES --------- #

    # ---------- Territories ---------- #

    # To keep the cleaned DataFrame tidy, create zip_list to process zipcode/territory information
    zip_list = pd.DataFrame()
    zip_list["PostalCode"] = cleaned["Zip"].fillna("")
    zip_list["Terr"] = ""
    zip_list["State"] = ""

    have_states = not cleaned["St"].dropna().empty  # Set a variable to indicate that we have States

    # If we do have states, bring in zip3_to_st file.
    if have_states:
        zip_list["State"] = cleaned["St"]  # Bring in the St field from the cleaned DataFrame
        try:
            zip3_table = pd.read_csv(path_dict["fileserver_path_reference"] + "/" + "zip3_to_st.csv", ",", dtype=str)
        except FileNotFoundError:
            quit("zip3_to_st.csv not found on fileserver.")
    else:
        if usa:
            usa_override = True
        else:
            usa_override = False

    # Define some functions we'll be using ---------------------------------------------------|

    def check_canadian_regex(zip_code):
        """ Function to find all Canadian zip codes and return True/False """
        if not isinstance(zip_code, str):  # Check that the zip code is a string
            return ""
        # Check to see if there is an immediate regex match.
        if re.search(r"\b(?!.{0,7}[DFIOQU])[A-VXY]\d[A-Z][^-\w\d]\d[A-Z]\d\b", zip_code):
            return True
        # Strip to alphanumeric only, add a space, and try again.
        zip_code_trimmed = zip_code.strip()
        zip_code_trimmed = re.sub("[^a-zA-Z0-9]", "", zip_code_trimmed)
        zip_code_trimmed = zip_code_trimmed[:3] + " " + zip_code_trimmed[3:]
        # Check rebuilt zip code for match with original regex pattern.
        if re.search(r"\b(?!.{0,7}[DFIOQU])[A-VXY]\d[A-Z][^-\w\d]\d[A-Z]\d\b", zip_code_trimmed):
            return True
        else:
            return False

    def convert_to_zip5(zip_code):
        """ Takes a string and returns an American-style five-digit zip code with leading zeroes where required, or
        returns an empty string. Valid lengths after removing all non-numeric characters are 3, 4, 5, 7, 8, and 9. """
        zip_code = str(zip_code)
        if zip_code[-2:] == ".0":  # Check to remove accidental float-style numbers.
            zip_code = zip_code.replace(".0", "")
        zip_code = zip_code.strip()  # Remove whitespace
        zip_code = zip_code.replace("-", "")  # Remove hyphens
        if zip_code != re.sub("[^0-9]", "", zip_code):  # Make sure there are no non-numbers left in the string
            return ""
        # If the zip code is too short or too long, end the function:
        if len(zip_code) not in [3, 4, 5, 7, 8, 9]:
            return ""
        # If this zip code is long enough to have had a +4 added, remove 4 characters from the end.
        if len(zip_code) in [7, 8, 9]:
            zip_code = zip_code[:-4]
        # Finally, pad the zip code to 5 characters if it's shorter than 5:
        zip_code = ((5 - len(zip_code)) * "0") + zip_code
        return zip_code

    def assign_usa_terr(zip5):
        """ Takes a American five-digit zip code and returns its territory. """

        # If zip5 is blank, return nothing and the zip will be manually assigned later.
        if not zip5:
            return

        # Search the ref_zip_ter table and return the corresponding territory.
        less_or_equal = ref_zip_ter[ref_zip_ter["FirstZip"].astype(int) <= int(zip5)]
        result = less_or_equal.iloc[-1]
        return result["Territory"]

    # End of functions -----------------------------------------------------------------------|

    # Locate CANADIAN zip codes using the check_canadian_regex() function, fill territory 125, then clean up.
    zip_list["Canadian"] = zip_list.PostalCode.apply(check_canadian_regex)
    zip_list.loc[zip_list["Canadian"], "Terr"] = "125"
    del zip_list["Canadian"]  # Clean up this column.

    # Sets Numeric column to True if US-type candidate (NUMBERS, SPACES, and HYPHENS ONLY)
    zip_list["Numeric"] = zip_list.PostalCode.apply(lambda x: True if re.search("^[- 0-9]+$", x) else False)

    # Produce US-style zip codes where possible.
    zip_list["Zip5"] = zip_list.PostalCode.apply(convert_to_zip5)

    # The following only works if we have states to verify USA
    if have_states:

        # From these, create zip3 codes for comparison with US States
        zip_list["Zip3"] = zip_list["Zip5"].str[0:3]
        zip3_shaped = zip_list.merge(zip3_table, how="left", left_on="Zip3", right_on="Zip3").fillna("")
        zip_list["Zip3St"] = zip3_shaped["St"]
        zip_list["StName"] = zip3_shaped["StName"]

        # Check if added state matched provided state
        is_usa_match = (zip_list["State"] == zip_list["Zip3St"]) | (zip_list["State"] == zip_list["StName"])
        zip_list["USA_match"] = is_usa_match

    else:
        # In absence of state values, rely on answer to USA_override to set the zip_list USA_match column values.
        if usa_override:
            zip_list["USA_match"] = True
        else:
            zip_list["USA_match"] = False

    # Add the chosen territory to the territory list
    shard = zip_list.loc[zip_list["USA_match"]]
    zip_list["Terr"] = shard.Zip5.apply(assign_usa_terr)

    # Manual Review function removed from here <<>>

    # Incorporate automatically detected territories into final DataFrame
    cleaned["Terr"] = zip_list["Terr"]

    # Replace zip codes in cleaned with revised versions in zip_list that were auto-detected as American
    # 1) Find the corresponding rows in cleaned where USA_match == True in zip_list, then:
    # 2) Take only the values from zip_list where USA_match == True and save the Zip5 values to the Zip field in Cleaned
    cleaned.loc[zip_list["USA_match"], "Zip"] = zip_list.loc[zip_list["USA_match"], "Zip5"]

    # ---------- Product Group & Category ---------- #

    # Import product to group and category reference table
    cleaned = pd.merge(cleaned, ref_item_product, how="left", on="Item")

    # -------------------------------------------------------------   FINAL CHECK AND OUTPUT

    cols = ["Customer", "City", "St", "Zip", "Item", "Qty", "Cost", "Ext", "Terr", "Mon", "Disty", "Group", "Category"]
    cleaned = cleaned[cols]
    cleaned.fillna("", inplace=True)

    grouped = pd.DataFrame(columns=cols)
    for index in cleaned.index:  # Loop through each row in the "cleaned" DataFrame and make the "grouped" DataFrame
        row = cleaned.iloc[index]  # Get the data for the current row in "cleaned."
        # Get a list of rows in "grouped" where the Item and Zip match the Item and Zip of the current row.
        rows_located = grouped.loc[(grouped['Item'] == row["Item"]) & (grouped['Zip'] == row["Zip"])]

        if len(rows_located) > 0:  # If a row was found that matches item and zip:
            # Since rows_located contains at least one item, grab the index of the first item. This is our target.
            index_to_change = rows_located.index[0]
            # Add the Qty, Cost, and Ext of the currently evaluated row to the first matching row in "grouped"
            grouped.loc[index_to_change, "Qty"] += row["Qty"]
            grouped.loc[index_to_change, "Cost"] = row["Cost"]  # Don't add unit cost
            grouped.loc[index_to_change, "Ext"] += row["Ext"]
        else:  # If the row was NOT found, append it unchanged to the grouped DataFrame
            grouped = grouped.append(row)
    grouped.fillna("", inplace=True)
    grouped.to_csv(path_dict["fileserver_path_output"] + "/" + disty_name + ".csv", index=False)

    return True

    # -------------------------------------------------------------   END OF PROCESS FILE FUNCTION


#  End of Processing Functions  #
#################################


###############
#  Execution  #
###############

    # fs_connect()

    #process_file(filename, pattern_filename, is_usa, distributor)










# root.mainloop -------------------------+
root.mainloop()
