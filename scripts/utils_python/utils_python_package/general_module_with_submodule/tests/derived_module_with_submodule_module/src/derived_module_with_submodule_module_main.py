#!/bin/python3
# ******************************************************************************
# - *-coding: utf-8 -*-
# (c) copyright 2024 Alexander Poeschl
# All rights reserved.
# Secrecy Level STRICTLY CONFIDENTIAL
# ******************************************************************************
# @file derived_module_with_submodule_module_main.py
# @author Alexander Poeschl <apoeschlfreelancing@kwanta.net>
# @brief DerivedModuleWithSubmodule for testing the GeneralModuleWithSubmodule Implementation.
# ******************************************************************************

from utils_python_package.src.Apoeschlutils import Fix_imports
Fix_imports()
from utils_python_package.src.Apoeschlutils import Log_error, Log_verbose, Log_result_error, Log_verbose_func_start, Log_verbose_func_end
from utils_python_package.src.ReturnState import ReturnState, eReturnStates
from general_module_with_submodule.src.general_module_with_submodule_module_main import GeneralModuleWithSubmodule

@GeneralModuleWithSubmodule.register
class DerivedModuleWithSubmodule(GeneralModuleWithSubmodule):
    def module_load_or_initialize(self, create_only = False):
        Log_verbose_func_start()
        retVal = ReturnState()
        if eReturnStates.SUCCESS != (retVal := super().module_load_or_initialize(create_only = create_only)):
            Log_result_error(f"super().module_load_or_initialize failed.", retVal)
        #nothing to do here!
        retVal = eReturnStates.SUCCESS
        Log_verbose_func_end()
        return retVal
    
    def module_apply_settings(self):
        Log_verbose_func_start()
        retVal = ReturnState()
        if self.settings_dict == None:
            Log_error("settings_dict was None. Maybe settings were not loaded from settingsfile before?")
            retVal = eReturnStates.ERROR
        else:
            retVal = eReturnStates.SUCCESS
        if eReturnStates.SUCCESS > (retVal := super().module_apply_settings()):
            Log_result_error(f"super().module_apply_settings failed.", retVal)
        if eReturnStates.SUCCESS == retVal:
            Log_verbose("applied settings successfully")
        Log_verbose_func_end()
        return retVal