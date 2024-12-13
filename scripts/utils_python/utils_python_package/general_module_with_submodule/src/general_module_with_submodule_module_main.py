#!/bin/python3
# ******************************************************************************
# - *-coding: utf-8 -*-
# (c) copyright 2024 Alexander Poeschl
# All rights reserved.
# Secrecy Level STRICTLY CONFIDENTIAL
# ******************************************************************************
# @file general_module_with_submodule_module_main.py
# @author Alexander Poeschl <apoeschlfreelancing@kwanta.net>
# @brief GeneralModuleWithSubmodule-Module from which Modules with Submodules (specific implementations e.g. MongoDB for the DatabaseModule) would be derived.
# ******************************************************************************
from utils_python_package.src.Apoeschlutils import Fix_imports
Fix_imports()
from utils_python_package.src.Apoeschlutils import Log_error, Log_verbose, Log_result_error, Log_verbose_func_start, Log_verbose_func_end
from utils_python_package.src.ReturnState import ReturnState, eReturnStates
from general_module.src.general_module_module_main import GeneralModule, GeneralModuleDefinitions
from general_module_with_submodule.src.general_module_with_submodule_definitions import GeneralModuleWithSubmoduleDefinitions
import sys, os
from glob import glob
import importlib
import inspect


@GeneralModule.register
class GeneralModuleWithSubmodule(GeneralModule):
    modules_default_path = "modules"
    modules_search_pattern_addition = "*"
    path_to_submodules_main = "src"
    submodule_main_naming_convention = "_main"
    used_sub_module = None
    used_sub_module_instance = None

    def module_load_or_initialize(self, create_only = False):
        Log_verbose_func_start()
        retVal = ReturnState()
        if eReturnStates.SUCCESS != (retVal := self.module_load_used_sub_module()):
            Log_result_error(f"module_load_used_sub_module failed.", retVal)
        retVal = eReturnStates.SUCCESS
        Log_verbose_func_end()
        return retVal
    
    
    def module_apply_settings(self):
        Log_verbose_func_start()
        retVal = ReturnState()
        if self.settings_dict == None:
            Log_error("settings_dict was None. Maybe settings were not loaded from settingsfile before?")
            retVal = eReturnStates.ERROR
        elif GeneralModuleDefinitions.GENERAL_MODULE_SETTINGS_NAME not in self.settings_dict:
            Log_error(f"{GeneralModuleDefinitions.GENERAL_MODULE_SETTINGS_NAME} were not in settings_dict.")
            retVal = eReturnStates.ERROR
        elif GeneralModuleWithSubmoduleDefinitions.USED_SUB_MODULE_SETTINGS_NAME not in self.settings_dict[GeneralModuleDefinitions.GENERAL_MODULE_SETTINGS_NAME]:
            Log_error(f"could not find 'used_sub_module' in '{self.module_settings_file_path}'")
            retVal = eReturnStates.ERROR
        elif None == self.settings_dict[GeneralModuleDefinitions.GENERAL_MODULE_SETTINGS_NAME][GeneralModuleWithSubmoduleDefinitions.USED_SUB_MODULE_SETTINGS_NAME]:
            Log_error("could not find used_sub_module in settings file.")
            retVal = eReturnStates.ERROR
        elif "" == self.settings_dict[GeneralModuleDefinitions.GENERAL_MODULE_SETTINGS_NAME][GeneralModuleWithSubmoduleDefinitions.USED_SUB_MODULE_SETTINGS_NAME]:
            Log_error("used_sub_module in settings file was empty.")
            retVal = eReturnStates.ERROR
        else:
            used_sub_module_to_set = self.settings_dict[GeneralModuleDefinitions.GENERAL_MODULE_SETTINGS_NAME][GeneralModuleWithSubmoduleDefinitions.USED_SUB_MODULE_SETTINGS_NAME]
            retVal = self.set_used_sub_module(used_sub_module_to_set)
        if eReturnStates.SUCCESS != retVal:
            Log_result_error(f"set_used_sub_module failed.", retVal)
        else:
            retVal, used_sub_module = self.get_used_sub_module()
        if used_sub_module_to_set != used_sub_module:
            Log_error(f"failed to set used_sub_module to '{used_sub_module_to_set}'.")
            retVal = eReturnStates.ERROR
        else:
            Log_verbose(f"successfully set used_sub_module to: '{self.used_sub_module}'")
        if eReturnStates.SUCCESS == retVal:
            Log_verbose("applied settings successfully")
        if eReturnStates.SUCCESS == retVal and self.used_sub_module_instance is not None:
            if eReturnStates.SUCCESS != (retVal := self.used_sub_module_instance.module_apply_settings()):
                Log_result_error("failed to apply settings for used_sub_module_instance.", retVal)
        Log_verbose_func_end()
        return retVal

    def module_load_used_sub_module(self):
        Log_verbose_func_start()
        retVal = ReturnState()
        modules_folder = os.path.dirname(os.path.abspath(sys.modules[self.__class__.__module__].__file__))
        modules_path = os.path.join(modules_folder, os.pardir, self.modules_default_path)
        modules_search_pattern = os.path.join(modules_path, self.modules_search_pattern_addition)
        available_modules = []
        found_modules = glob(modules_search_pattern, recursive = False)
        for found_module in found_modules:
            module_basename = os.path.basename(found_module)
            if "__" != module_basename[:2]:
                available_modules.append(module_basename)
        if self.used_sub_module not in available_modules:
            Log_error(f"selected module '{self.used_sub_module}' was not found in '{modules_path}'.")
            retVal = eReturnStates.ERROR
            return retVal
        path_to_append_for_import = os.path.join(modules_path, self.used_sub_module, self.path_to_submodules_main)
        if not os.path.isdir(path_to_append_for_import):
            Log_error(f"folder '{path_to_append_for_import}' does not exist.")
            retVal = eReturnStates.ERROR
            return retVal
        if path_to_append_for_import not in sys.path:
            sys.path.append(path_to_append_for_import)
        sub_module_name = self.used_sub_module + self.submodule_main_naming_convention
        path_to_sub_module = os.path.join(path_to_append_for_import, sub_module_name + ".py")
        if not os.path.isfile(path_to_sub_module):
            Log_error(f"file '{path_to_sub_module}' does not exist.")
            retVal = eReturnStates.ERROR
            return retVal
        try:
            module_to_use = importlib.import_module(sub_module_name)
        except ModuleNotFoundError as error:
            Log_error(f"Got an ModuleNotFoundError for '{sub_module_name}'. Errormessage was: '{error}'")
            retVal = eReturnStates.ERROR
            return retVal
        except ImportError as error:
            Log_error(f"Got an ImportError for '{sub_module_name}'. Errormessage was: '{error}'")
            retVal = eReturnStates.ERROR
            return retVal
        except Exception as error:
            Log_error(f"Got an Error when trying to import '{sub_module_name}'. Errormessage was: '{error}'")
            retVal = eReturnStates.ERROR
            return retVal
        for sub_module_to_use_name, sub_module_to_use_class in inspect.getmembers(module_to_use, inspect.isclass):
            if sub_module_name in sub_module_to_use_class.__module__:
                sub_module_to_use_instance = sub_module_to_use_class()
                self.used_sub_module_instance = sub_module_to_use_instance
                retVal = eReturnStates.SUCCESS
        Log_verbose_func_end()
        return retVal
    
    def set_used_sub_module(self, sub_module_to_use):
        Log_verbose_func_start()
        retVal = ReturnState()
        if sub_module_to_use == None:
            Log_error("sub_module_to_use was None")
            retVal = eReturnStates.ERROR
        elif sub_module_to_use == "":
            Log_error("sub_module_to_use was empty")
            retVal = eReturnStates.ERROR
        else:
            self.used_sub_module = sub_module_to_use
            self.settings_dict[GeneralModuleDefinitions.GENERAL_MODULE_SETTINGS_NAME][GeneralModuleWithSubmoduleDefinitions.USED_SUB_MODULE_SETTINGS_NAME]
            retVal = eReturnStates.SUCCESS
        Log_verbose_func_end()
        return retVal

    def get_used_sub_module(self):
        Log_verbose_func_start()
        retVal = ReturnState()
        result = None
        if self.used_sub_module == None:
            Log_error(f"used_sub_module could not be returned. used_sub_module was None.")
        elif self.used_sub_module == "":
            Log_error(f"used_sub_module could not be returned. used_sub_module is empty.")
        else:
            result = self.used_sub_module
            retVal = eReturnStates.SUCCESS
        Log_verbose_func_end()
        return retVal, result
    
    def module_get_settings(self):
        Log_verbose_func_start()
        retVal = ReturnState()
        retVal, self.settings_dict = super().module_get_settings()
        if eReturnStates.SUCCESS != retVal:
            Log_result_error(f"super().module_get_settings() failed.", retVal)
        elif self.settings_dict == None:
            Log_error(f"settings_dict is None.")
            retVal = eReturnStates.ERROR
        if eReturnStates.SUCCESS == retVal and hasattr(self, "used_sub_module_instance") and self.used_sub_module_instance is not None:
            retVal, used_sub_module_instance_settings = self.used_sub_module_instance.module_get_settings()
            if eReturnStates.SUCCESS != retVal:
                Log_result_error("failed to get settings from used_sub_module_instance.", retVal)
            else:
                self.settings_dict[GeneralModuleWithSubmoduleDefinitions.SUBMODULE_SETTINGS_NAME] = dict()
                self.settings_dict[self.used_sub_module] = used_sub_module_instance_settings
        if eReturnStates.SUCCESS == retVal:
            Log_verbose("return settings successfully.")
            retVal = eReturnStates.SUCCESS
        Log_verbose_func_end()
        return retVal, self.settings_dict
    
    def module_is_used_sub_module_instance_initialized(self):
        Log_verbose_func_start()
        retVal = ReturnState()
        if self.used_sub_module_instance is not None:
            retVal = eReturnStates.INITIALIZED
            Log_verbose("used_sub_module_instance is initialized.")
        else:
            retVal = eReturnStates.INITIALIZED_NOT
            Log_verbose("used_sub_module_instance is not initialized.")
        Log_verbose_func_end()
        return retVal