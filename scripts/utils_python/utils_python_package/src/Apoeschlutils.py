#!/bin/python3
# ******************************************************************************
# - *-coding: utf-8 -*-
# (c) copyright 2024 Alexander Poeschl
# All rights reserved.
# Secrecy Level STRICTLY CONFIDENTIAL
# ******************************************************************************
# @file apoeschlutils.py
# @author Alexander Poeschl <apoeschlfreelancing@kwanta.net>
# @brief Some utils that can be used in all sorts of Python Projects.
# ******************************************************************************


import sys, os
from inspect import currentframe, getframeinfo
from datetime import datetime
from utils_python_package.src.Apoeschllogging import *
from src.eLogLevels import eLogLevels
from utils_python_package.src.CLIColors import clicolors
from datetime import datetime
from utils_python_package.src.ReturnState import ReturnState, eReturnStates

#DO NOT DELETE THIS INFO: __debug__ is always true, except if you call the script with -o or -oo option (python optimizations)


def Check_test_result_and_cleanup(retVal_under_test, cleanup, message = "", level = eLogLevels.ERROR, show_additional_info = False):
    retVal = False
    if "" != message:
        message = message + " "
    if eReturnStates.SUCCESS != cleanup:
        message = message + "Cleanup failed."
        retValCleanup = False
    else:
        message = message + "Cleanup succeeded."
        retValCleanup = True
    retVal = Check_test_result(retVal_under_test, message, level=level, show_additional_info=show_additional_info)
    return retVal and retValCleanup

def Check_test_result(retVal_under_test, message = "", level = eLogLevels.ERROR, show_additional_info = False):
    retVal = False
    if "" != message:
        message = message + " "
    if eReturnStates.SUCCESS != retVal_under_test:
        message = message + "Test failed."
        retVal = False
        Log_result_error(message, retVal_under_test, level=level, show_additional_info=show_additional_info)
    else:
        message = message + "Test succeeded."
        retVal = True
        Log_result(message, retVal_under_test, level=eLogLevels.SUCCESS, show_additional_info=show_additional_info)
    return retVal

def Get_Result_Message(retVal):
    return f" retVal was: '{retVal}'"

def Log_result(message, retVal, level = eLogLevels.SUCCESS, show_additional_info = False):
    message = message + Get_Result_Message(retVal)
    Log(message, level, show_additional_info, wrapper=True)

def Log_result_error(message, retVal, level = eLogLevels.ERROR, show_additional_info = False):
    message = message + Get_Result_Message(retVal)
    Log(message, level, show_additional_info, wrapper=True)


def Get_filename():
    frameInfo = getframeinfo(sys._getframe().f_back)
    fileName = frameInfo.filename.split('/')[-1]
    return fileName

def Get_folder_of_current_file():
    frameInfo = getframeinfo(sys._getframe().f_back)
    fileName = frameInfo.filename.split('/')[-1]
    folder = os.path.dirname(os.path.realpath(fileName))
    return folder


def __line__():
    frameInfo = getframeinfo(sys._getframe().f_back)
    fileName = frameInfo.filename.split('/')[-1]
    lineNumber = frameInfo.lineno
    return lineNumber