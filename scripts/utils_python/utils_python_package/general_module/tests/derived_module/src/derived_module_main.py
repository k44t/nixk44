
#!/bin/python3
# ******************************************************************************
# - *-coding: utf-8 -*-
# (c) copyright 2024 Alexander Poeschl
# All rights reserved.
# Secrecy Level STRICTLY CONFIDENTIAL
# ******************************************************************************
# @file derived_module_main.py
# @author Alexander Poeschl <apoeschlfreelancing@kwanta.net>
# @brief DerivedModule for testing the GeneralModule Implementation.
# ******************************************************************************
from utils_python_package.src.Apoeschlutils import Fix_imports
Fix_imports()
from utils_python_package.src.Apoeschlutils import Log_error, Log_verbose, Log_verbose_func_start, Log_verbose_func_end
from utils_python_package.src.ReturnState import ReturnState, eReturnStates
from general_module.src.general_module_module_main import GeneralModule

@GeneralModule.register
class DerivedModule(GeneralModule):
    def module_load_or_initialize(self, create_only = False):
        Log_verbose_func_start()
        retVal = ReturnState()
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
        if eReturnStates.SUCCESS == retVal:
            Log_verbose("applied settings successfully")
        Log_verbose_func_end()
        return retVal