#!/bin/python3
# ******************************************************************************
# - *-coding: utf-8 -*-
# (c) copyright 2024 Alexander Poeschl
# All rights reserved.
# Secrecy Level STRICTLY CONFIDENTIAL
# ******************************************************************************
# @file apoeschllogging.py
# @author Alexander Poeschl <apoeschlfreelancing@kwanta.net>
# @brief Some logging functions that are needed somewhere, but would result in circular imports if implemented inside apoeschlutils. You usually dont want to import this file, but apoeschlutils.py instead!
# ******************************************************************************

from threading import Thread
import queue
import time
import os, sys
from datetime import datetime
import inspect
import re
import traceback
from inspect import currentframe, getframeinfo
from src.LogLevel import LogLevels
from utils_python_package.src.CLIColors import clicolors
from utils_python.utils_python_package.src.LogLevel import LogLevels

Deb_callbackfunction = None
Deb_usePrintFunction = True
Deb_printCallstack = False
Deb_activateCallback = False
Deb_activateMessages_flag = True
Deb_logfolder = "./logs/apoeschllogs/"
Deb_writeToLogfile = False
Deb_suppressLevels = set()
Deb_suppressLevelsFlag = False
Deb_onlyAllowLevels = set()
Deb_onlyAllowLevelFlag = False
Deb_additional_info = ""
Deb_additional_info_flag = False
Deb_suppressVerboseFlag = True
LogfileCounter = 0
Logfile = None
Logfilename = ""
Output_thread = None

class OutputThread(Thread):
    name = ""
    output_queue = queue.Queue()
    def __init__(self):
        super().__init__(daemon=True)
    
    def run(self):
        name = datetime.now()
        while True:
            if not self.output_queue.empty():
                logMessage = self.output_queue.get()
                if Deb_writeToLogfile:
                    Logfile.write(logMessage + "\n")
                if Deb_activateMessages_flag:
                    if Deb_usePrintFunction:
                        print(logMessage)
                    if Deb_activateCallback:
                        Deb_callbackfunction(logMessage)
            else:
                time.sleep(0.1)


    def Add_to_queue(self, message):
        self.output_queue.put(message)

Output_thread = OutputThread()
Output_thread.start()

def Deb_set_callbackfunction(callbackfunction):
    Log("Deb_set_callbackfunction " + str(callbackfunction), level=LogLevels.DEBCONFIG)
    global Deb_callbackfunction
    Deb_callbackfunction = callbackfunction

def Get_timestamp_for_filenames():
    current_timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    return current_timestamp

def Get_timestamp():
    current_timestamp = datetime.now().strftime("%Y-%m-%d-%H:%M:%S:%f")
    return current_timestamp

if Deb_writeToLogfile:
    if not os.path.isdir(Deb_logfolder):
        os.mkdir(Deb_logfolder)
    Logfilename = Deb_logfolder + Get_timestamp_for_filenames() + "_logfile.txt"
    if os.path.isfile(Logfilename):
        Logfile = open(Logfilename, "a")
    else:
        Logfile = open(Logfilename, "w")

def Log_verbose_func_start(suppress = False, show_additional_info = False):
    if Deb_suppressVerboseFlag and suppress:
        return
    frame = sys._getframe().f_back
    function_qualifier_name = frame.f_code.co_qualname
    message = function_qualifier_name + " start"
    Log(message, LogLevels.VERBOSE, show_additional_info, wrapper=True)

def Log_verbose_func_end(suppress = False, show_additional_info = False):
    if Deb_suppressVerboseFlag and suppress:
        return
    frame = sys._getframe().f_back
    function_qualifier_name = frame.f_code.co_qualname
    message = function_qualifier_name + " end"
    Log(message, LogLevels.VERBOSE, show_additional_info, wrapper=True)

def Log_verbose(message, level = LogLevels.VERBOSE, show_additional_info = False):
    Log(message, level, show_additional_info, wrapper=True)

def Log_warn(message, level = LogLevels.WARNING, show_additional_info = False):
    Log(message, level, show_additional_info, wrapper=True)

def Log_info(message, level = LogLevels.INFO, show_additional_info = False):
    Log(message, level, show_additional_info, wrapper=True)

def Log_error(message, level = LogLevels.ERROR, show_additional_info = False):
    Log(message, level, show_additional_info, wrapper=True)

    
def Deb(message, level = LogLevels.DEBUG, show_additional_info = False):
    Log(message, level, show_additional_info, wrapper=True)

def Log(message, level = LogLevels.UNKNOWN, show_additional_info = False, wrapper = False):
    if not Deb_activateMessages_flag and not Deb_writeToLogfile and not Deb_activateCallback:
        return
    if not Deb_onlyAllowLevelFlag and Deb_suppressLevelsFlag:
        for suppressLevel in Deb_suppressLevels:
            if level == suppressLevel:
                return
    else:
        levelAllowed = False
        for onlyAllowLevel in Deb_onlyAllowLevels:
            if level == onlyAllowLevel:
                levelAllowed = True
    if Deb_onlyAllowLevelFlag and not levelAllowed:
        return
    if wrapper:
        frame = sys._getframe().f_back
        frameInfo = getframeinfo(frame)
        fileName = frameInfo.filename.split('/')[-1]
        while "Apoeschllogging.py" in fileName:
            frame = frame.f_back
            frameInfo = getframeinfo(frame)
            fileName = frameInfo.filename.split('/')[-1]
    else:
        frameInfo = getframeinfo(sys._getframe().f_back)
    fileName = frameInfo.filename.split('/')[-1]
    lineNumber = frameInfo.lineno


    if Deb_printCallstack:
        callStack = ""
        raw_tb = traceback.extract_stack()
        entries = traceback.format_list(raw_tb)
        for line in entries:
            if ".vscode-server" in line or "/nix/store/" in line or "Apoeschllogging.py" in line:
                continue
            else:
                regexp_pattern = r'in (.*?)\n'
                regexp = re.compile(regexp_pattern)
                match = re.search(regexp_pattern, line).group(1)
                if match == "<module>":
                    callstack = match
                else:
                    callstack = callstack + "->" + match
        callstack = callstack + ": "

    debugMessage = clicolors.BOLD + clicolors.OKGREEN + Get_timestamp() + " " + clicolors.OKBLUE + fileName + ":" + str(lineNumber) + " : "
    if Deb_printCallstack:
        debugMessage = debugMessage + callstack
    if LogLevels.UNKNOWN != level:
        if LogLevels.ERROR == level:
            levelMessage = clicolors.FAIL + "\n>>>>>>> ERROR >>>>>>\n"
            debugMessage = debugMessage + levelMessage
        else:
            debugMessage = debugMessage + str(level) + ": "
    if LogLevels.ERROR == level:
        debugMessage = debugMessage + str(message)
    elif LogLevels.DEBUG == level:
        debugMessage = debugMessage + clicolors.DEBUG + str(message) + clicolors.ENDCOLOR
    else:
        debugMessage = debugMessage + clicolors.ENDCOLOR + str(message)
    if show_additional_info or Deb_additional_info_flag:
        debugMessage = debugMessage + " ### additional_info: " + str(Deb_additional_info)
    if LogLevels.ERROR == level:
        debugMessage = debugMessage + "\n<<<<<<< ERROR <<<<<<<<\n" + clicolors.ENDCOLOR
    Output_thread.Add_to_queue(debugMessage)
    global LogfileCounter
    if Deb_writeToLogfile:
        LogfileCounter = LogfileCounter + 1
        if LogfileCounter > 1000:
            logfile.close()
            global Logfilename
            if not os.path.isdir(Deb_logfolder):
                os.mkdir(Deb_logfolder)
            Logfilename = Deb_logfolder + Get_timestamp_for_filenames() + "_logfile.txt"
            if os.path.isfile(Logfilename):
                logfile = open(Logfilename, "a")
            else:
                logfile = open(Logfilename, "w")
            LogfileCounter = 0

def Fix_imports():
    frameInfo = getframeinfo(sys._getframe().f_back)
    file_path = frameInfo.filename
    pardir = None
    current_dir = os.path.dirname(os.path.abspath(file_path))
    if os.path.dirname(current_dir) not in sys.path:
        sys.path.append(os.path.dirname(current_dir))
    sys_paths = sys.path
    while pardir != "":
        parent_dir = os.path.abspath(os.path.join(current_dir, os.pardir))
        pardir = os.path.basename(parent_dir)
        current_dir = parent_dir
        dir_name = os.path.dirname(parent_dir)
        if parent_dir not in sys.path:
            sys.path.append(parent_dir)
        if dir_name not in sys.path:
            sys.path.append(dir_name)
        sys_paths = sys.path

        
def Deb_set_additional_info(additional_info):
    Log("Deb_set_additional_info " + str(additional_info), level=LogLevels.DEBCONFIG)
    global Deb_additional_info
    Deb_additional_info = additional_info

def Deb_set_additional_info_flag(additional_info_flag):
    Log("Deb_set_additional_info_flag " + str(additional_info_flag), level=LogLevels.DEBCONFIG)
    global Deb_additional_info_flag
    Deb_additional_info_flag = additional_info_flag

def Deb_remove_suppress_level(suppress_level):
    Log("Deb_remove_suppress_level " + str(suppress_level), level=LogLevels.DEBCONFIG)
    global Deb_suppressLevels
    Deb_suppressLevels.remove(suppress_level)

def Deb_add_suppress_level(suppress_level):
    Log("Deb_add_suppress_level " + str(suppress_level), level=LogLevels.DEBCONFIG)
    global Deb_suppressLevels
    Deb_suppressLevels.add(suppress_level)

def Deb_add_suppress_levels(suppress_levels):
    Log("Deb_add_suppress_level " + str(suppress_levels), level=LogLevels.DEBCONFIG)
    global Deb_suppressLevels
    for suppress_level in suppress_levels:
        Deb_suppressLevels.add(suppress_level)

def Deb_set_suppress_levels(suppress_levels):
    Log("Deb_set_suppress_levels " + str(suppress_levels), level=LogLevels.DEBCONFIG)
    global Deb_suppressLevels
    Deb_suppressLevels = suppress_levels

def Deb_get_suppress_levels():
    global Deb_suppressLevels
    Log("Deb_get_suppress_levels " + str(Deb_suppressLevels), level=LogLevels.DEBCONFIG)
    return Deb_suppressLevels

def Deb_get_usePrintFunction():
    global Deb_usePrintFunction
    Log("Deb_get_usePrintFunction " + str(Deb_usePrintFunction), level=LogLevels.DEBCONFIG)
    return Deb_usePrintFunction

def Deb_get_printCallstack():
    global Deb_printCallstack
    Log("Deb_get_printCallstack " + str(Deb_printCallstack), level=LogLevels.DEBCONFIG)
    return Deb_printCallstack

def Deb_remove_only_allow_level(only_allow_level):
    Log("Deb_remove_only_allow_level " + str(only_allow_level), level=LogLevels.DEBCONFIG)
    global Deb_onlyAllowLevels
    Deb_onlyAllowLevels.remove(only_allow_level)

def Deb_add_only_allow_level(only_allow_level):
    Log("Deb_add_only_allow_level " + str(only_allow_level), level=LogLevels.DEBCONFIG)
    global Deb_onlyAllowLevels
    Deb_onlyAllowLevels.add(only_allow_level)

def Deb_set_only_allow_levels(allow_levels):
    Log("Deb_set_only_allow_levels " + str(allow_levels), level=LogLevels.DEBCONFIG)
    global Deb_onlyAllowLevels
    Deb_onlyAllowLevels = allow_levels

def Deb_get_only_allow_levels():
    global Deb_onlyAllowLevels
    Log("Deb_get_only_allow_levels " + str(Deb_onlyAllowLevels), level=LogLevels.DEBCONFIG)
    return Deb_onlyAllowLevels

def Deb_set_only_allow_levels_flag(only_allow_levels_flag):
    Log("Deb_set_only_allow_levels_flag " + str(only_allow_levels_flag), level=LogLevels.DEBCONFIG)
    global Deb_onlyAllowLevelFlag
    Deb_onlyAllowLevelFlag = only_allow_levels_flag

def Deb_set_suppress_levels_flag(suppress_levels_flag):
    Log("Deb_set_suppress_levels_flag " + str(suppress_levels_flag), level=LogLevels.DEBCONFIG)
    global Deb_suppressLevelsFlag
    Deb_suppressLevelsFlag = suppress_levels_flag

def Deb_set_activate_messages_flag(activate_messages_flag):
    Log("Deb_set_activate_messages_flag " + str(activate_messages_flag), level=LogLevels.DEBCONFIG)
    global Deb_activateMessages_flag
    Deb_activateMessages_flag = activate_messages_flag

def Deb_set_logfolder_path(logfolder_path):
    Log("Deb_set_logfolder_path " + str(logfolder_path), level=LogLevels.DEBCONFIG)
    global Deb_logfolder
    Deb_logfolder = logfolder_path

def Deb_set_activate_callbackfunction(activate_callbackfunction):
    Log("Deb_set_activate_callbackfunction " + str(activate_callbackfunction), level=LogLevels.DEBCONFIG)
    global Deb_activateCallback
    Deb_activateCallback = activate_callbackfunction

def Deb_set_writetologfile(activate_writetologfile):
    Log("Deb_set_writetologfile " + str(activate_writetologfile), level=LogLevels.DEBCONFIG)
    global Deb_writeToLogfile
    Deb_writeToLogfile = activate_writetologfile

def Deb_set_usePrintFunction(activate_usePrintFunction):
    global Deb_usePrintFunction
    Deb_usePrintFunction = activate_usePrintFunction
    Log("Deb_set_writetologfile " + str(activate_usePrintFunction), level=LogLevels.DEBCONFIG)
    
def Deb_set_printCallstack(activate_printCallstack):
    global Deb_printCallstack
    Deb_printCallstack = activate_printCallstack
    Log("Deb_set_printCallstack " + str(activate_printCallstack), level=LogLevels.DEBCONFIG)