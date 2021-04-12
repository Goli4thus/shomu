#!/usr/bin/env python3
"""ShoMu: Shortcut Multiplexer"""

import tkinter as tk
from tkinter import ttk
from tkinter.ttk import *
from tkinter import messagebox
import subprocess
import os
import json
import platform
import re
import argparse


COMBOBOX_CONTEXT = None
CONTEXT = None
LABEL = None
CONTEXT_LIST = None
CONTEXT_PREV = None
CONFIG = None
PATH_CONFIG = None
HOST_OS = platform.system()


def config_parse(args_config):
    """Parses the respective json config file."""
    global CONFIG
    global PATH_CONFIG

    # Config file search location prioritization
    path_check_local = "./shomu_cfg.json"
    path_check_host_os = os.path.expanduser("~/.config/shomu/shomu_cfg.json")

    if args_config:
        if os.path.exists(args_config):
            PATH_CONFIG = os.path.abspath(os.path.expanduser(args_config))
        else:
            messagebox.showerror("Config not found",
                                 "The config file provided by argument can't be found:\n\n"
                                 "- {}".format(args_config))
            return False
    elif os.path.exists(path_check_local):
        PATH_CONFIG = path_check_local
    elif os.path.exists(path_check_host_os):
        PATH_CONFIG = path_check_host_os
    else:
        messagebox.showerror("Config not found",
                             "The config file can't be found in any of these locations:\n\n"
                             "- {}\n"
                             "- {}".format(path_check_local, path_check_host_os))
        return False

    with open(PATH_CONFIG, 'r') as tmp_file:
        try:
            CONFIG = json.load(tmp_file)
        except ValueError as err:
            messagebox.showerror("Error parsing config",
                                 "The config file '{}' seems to be invalid json data.\n\n"
                                 "{}".format(PATH_CONFIG, err))
            return False

    return config_sanity_check()


def config_sanity_check():
    """Additional config sanity checks (i.e. not so obvious matters)"""
    for con in list(CONFIG.keys()):
        for key in CONFIG[con]['keys']:
            mat = re.fullmatch(r'.*Shift-[a-z]', key)
            if mat:
                messagebox.showerror("Invalid shortcut format",
                                     "The shortcut '{}' is invalid.\n"
                                     "Whenever 'Shift-' is being used, "
                                     "the following character needs to be upper case.".format(key))
                return False

            mat = re.fullmatch(r'.*(?<!Shift-)[A-Z]', key)
            if mat:
                messagebox.showerror("Invalid shortcut format",
                                     "The shortcut '{}' is invalid.\n"
                                     "Whenever a character is not being preceded with 'Shift-', "
                                     "the character needs to be lower case.".format(key))
                return False

        return True


def app_exit():
    """Simply exit app."""
    ROOT.destroy()


def run_command(key_combo):
    """Runs the associated command of a given key combination (based on config file)."""
    # Using 'Popen', cause it doesn't block application from exiting.
    if CONFIG[CONTEXT]['keys'][key_combo]['cwd'] != "None":
        subprocess.Popen(CONFIG[CONTEXT]['keys'][key_combo]['command'],
                         cwd=os.path.expanduser(CONFIG[CONTEXT]['keys'][key_combo]['cwd']),
                         shell=True)
    else:
        subprocess.Popen(CONFIG[CONTEXT]['keys'][key_combo]['command'], shell=True)

    app_exit()


def show_context_info_in_editor():
    """Open config in default OS application associated with json files."""
    if HOST_OS == 'Linux':
        subprocess.Popen(["xdg-open", PATH_CONFIG])
    elif HOST_OS == 'Windows':
        subprocess.Popen(["start", PATH_CONFIG], shell=True)
    else:  # 'Darwin' (i.e. macOS)
        # Just a guess. Can't test it without macOS access.
        subprocess.Popen(["open", PATH_CONFIG], shell=True)

    # Exit application, cause otherwise any config changes wouldn't be loaded.
    # (at least not if there are changes to the already selected context and the
    #  user doesn't toggle between contexts)
    app_exit()


def set_context(index):
    """Set context based on provided index."""
    global CONTEXT
    global CONTEXT_PREV

    if index == -1:
        # Derive index from combobox selection
        index = CONTEXT_LIST.index(COMBOBOX_CONTEXT.get())

    COMBOBOX_CONTEXT.current(index)
    CONTEXT_PREV = CONTEXT
    CONTEXT = COMBOBOX_CONTEXT.get()

    LABEL.config(text=CONTEXT,
                 width=(max(10, len(CONTEXT))),
                 fg=CONFIG[CONTEXT]['conf']['fg_color'],
                 bg=CONFIG[CONTEXT]['conf']['bg_color'])

    bind_context_keys()


def bind_context_keys():
    """Rebind the context keys based on active context."""
    if CONTEXT_PREV:
        # Unbind keys of previous context
        for key in CONFIG[CONTEXT_PREV]['keys']:
            ROOT.unbind('<' + key + '>')

    # Bind keys of new context
    for key in CONFIG[CONTEXT]['keys']:
        ROOT.bind('<' + key + '>', lambda event, key_combo=key: run_command(key_combo))


def arguments_parse():
    """user argument parsing"""
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", help="config file selection")
    args = parser.parse_args()
    return args.config


def main():
    """main"""
    global COMBOBOX_CONTEXT
    global CONTEXT
    global CONTEXT_LIST
    global LABEL

    ROOT.geometry('300x170+200+200')
    ROOT.title('ShoMu')
    if HOST_OS == 'Linux':
        ROOT.style = ttk.Style()
        ROOT.style.theme_use("clam")

    if HOST_OS == 'Windows':
        icon_path = os.path.realpath(__file__).rsplit('\\', 1)[0] + '\\resources\\shomu.png'
    else:
        icon_path = os.path.realpath(__file__).rsplit('/', 1)[0] + '/resources/shomu.png'

    ROOT.tk.call('wm', 'iconphoto', ROOT._w, tk.PhotoImage(file=icon_path))

    args_config = arguments_parse()

    if not config_parse(args_config):
        return

    # Setting up root window
    str_var = tk.StringVar()
    COMBOBOX_CONTEXT = ttk.Combobox(ROOT, width=27, textvariable=str_var, state='readonly')

    CONTEXT_LIST = list(CONFIG.keys())

    CONTEXT = CONTEXT_LIST[0]

    # Adding combobox drop down list
    COMBOBOX_CONTEXT['values'] = CONTEXT_LIST
    COMBOBOX_CONTEXT.pack(side="top", pady=(10, 20))
    COMBOBOX_CONTEXT.current(0)
    COMBOBOX_CONTEXT.bind("<<ComboboxSelected>>", lambda event, index=-1: set_context(index))

    # Only bind first 9 contexts to number keys 1 to 9
    for i, _ in enumerate(CONTEXT_LIST[:9]):
        ROOT.bind(str(i + 1), lambda event, index=i: set_context(index))

    LABEL = tk.Label(ROOT,
                     text="{}".format(CONTEXT),
                     font=("Arial Black", 25),
                     borderwidth=2,
                     relief='ridge',
                     padx=10,
                     pady=3,
                     width=(max(10, len(CONTEXT))))
    LABEL.config(fg=CONFIG[CONTEXT]['conf']['fg_color'], bg=CONFIG[CONTEXT]['conf']['bg_color'])
    LABEL.pack()

    # Context unspecific binds
    ROOT.bind('<Escape>', lambda event: app_exit())
    bind_context_keys()

    button_info = ttk.Button(ROOT, text='Config ( ? )', command=show_context_info_in_editor)
    button_info.pack(side='bottom', pady=(10, 10))
    ROOT.bind('?', lambda event: show_context_info_in_editor())

    ROOT.mainloop()


if __name__ == "__main__":
    ROOT = tk.Tk()
    main()
