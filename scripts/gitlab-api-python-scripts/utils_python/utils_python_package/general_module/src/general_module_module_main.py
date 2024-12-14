#!/bin/python3
# ******************************************************************************
# - *-coding: utf-8 -*-
# (c) copyright 2024 Alexander Poeschl
# All rights reserved.
# Secrecy Level STRICTLY CONFIDENTIAL
# ******************************************************************************
# @file general_module_module_main.py
# @author Alexander Poeschl <apoeschlfreelancing@kwanta.net>
# @brief GeneralModule-Module from which normal Modules would be derived.
# ******************************************************************************
from utils_python_package.src.Apoeschlutils import Fix_imports
Fix_imports()
from utils_python_package.src.Apoeschlutils import Log_error, Log_verbose, Log_result_error, Log_verbose_func_start, Log_verbose_func_end, Deb
from utils_python_package.src.ReturnState import ReturnState, eReturnStates
from utils_python_package.database_module.src.database_module_main import DatabaseModule
from utils_python_package.general_module.src.general_module_definitions import GeneralModuleDefinitions
import os, sys
import json
import abc

class GeneralModule(metaclass=abc.ABCMeta):
    module_settings_file_path = None
    usual_settings_file_path = os.path.join(os.pardir,"settings.json")
    settings_dict = None

    def __init__(self, create_only = False):
        Log_verbose_func_start()
        retVal = ReturnState()
        retVal = self.module_create(create_only=create_only)
        Log_verbose_func_end()
        if eReturnStates.SUCCESS != retVal:
            return retVal

    def module_create(self, create_only = False):
        Log_verbose_func_start()
        retVal = ReturnState()
        settings_folder = os.path.dirname(os.path.abspath(sys.modules[self.__class__.__module__].__file__))
        self.module_settings_file_path = os.path.join(settings_folder, self.usual_settings_file_path)
        if eReturnStates.SUCCESS > (retVal := self.module_load_settings()):
            Log_result_error(f"load_settings failed.", retVal)
        elif eReturnStates.SUCCESS > (retVal := self.module_apply_settings()):
            Log_result_error(f"apply_settings failed.", retVal)
        elif not create_only and eReturnStates.SUCCESS > (retVal := self.module_load_or_initialize(create_only=create_only)):
            Log_result_error(f"module_load_or_initialize failed.", retVal)
        else:
            Log_verbose("initializing of Module successful")
        Log_verbose_func_end()
        return retVal
    
    @abc.abstractmethod    
    def module_load_or_initialize(self, create_only = False):
        """needs to be implemented in derived class"""  
        Log_verbose_func_start()
        retVal = ReturnState()
        retVal = eReturnStates.SUCCESS
        Log_verbose_func_end()
        return retVal  

    def module_get_initial_settings(self):
        Log_verbose_func_start()
        retVal = ReturnState()
        initial_settings = None
        if not os.path.isfile(self.module_settings_file_path):
            Log_error(f"Settings file '{self.module_settings_file_path}' is not a file or does not exist.")
            retVal = eReturnStates.ERROR
        else:
            try:
                with open(self.module_settings_file_path) as settings_file:
                    initial_settings = json.load(settings_file)
                retVal = eReturnStates.SUCCESS
            except:
                Log_error(f"failed to load settings file: '{self.module_settings_file_path}'")
                retVal = eReturnStates.ERROR
            if retVal != eReturnStates.SUCCESS:
                Log_result_error("failed to load settings.", retVal)
            else:
                Log_verbose("loaded settings successfully")
        Log_verbose_func_end()
        return retVal, initial_settings


    def module_load_settings(self):
        Log_verbose_func_start()
        retVal = ReturnState()
        retVal, settings_from_database = self.module_get_settings_from_database()
        if eReturnStates.SUCCESS != retVal or None == settings_from_database:
            Log_result_error("failed to load settings from database or settings from database were None.", retVal)
            retVal, initial_settings = self.module_get_initial_settings()
            if eReturnStates.SUCCESS != retVal:
                Log_result_error("failed to get initial settings.", retVal)
            elif None == initial_settings:
                Log_error("initial_settings were None.")
                retVal = eReturnStates.ERROR
            else:
                settings_to_load = initial_settings
                retVal = eReturnStates.CONTINUE
        else:
            settings_to_load = settings_from_database
            retVal = eReturnStates.CONTINUE
        if eReturnStates.CONTINUE == retVal:
            self.settings_dict = dict()
            if GeneralModuleDefinitions.GENERAL_MODULE_SETTINGS_NAME in settings_to_load:
                        self.settings_dict[GeneralModuleDefinitions.GENERAL_MODULE_SETTINGS_NAME] = settings_to_load[GeneralModuleDefinitions.GENERAL_MODULE_SETTINGS_NAME]
            else:
                self.settings_dict[GeneralModuleDefinitions.GENERAL_MODULE_SETTINGS_NAME] = dict()
            if GeneralModuleDefinitions.SPECIFIC_MODULE_SETTINGS_NAME in settings_to_load:
                        self.settings_dict[GeneralModuleDefinitions.SPECIFIC_MODULE_SETTINGS_NAME] = settings_to_load[GeneralModuleDefinitions.SPECIFIC_MODULE_SETTINGS_NAME]
            else:
                self.settings_dict[GeneralModuleDefinitions.SPECIFIC_MODULE_SETTINGS_NAME] = dict()
        Log_verbose_func_end()
        return retVal
    
    def module_get_settings(self):
        Log_verbose_func_start()
        retVal = ReturnState()
        if self.settings_dict == None:
            if eReturnStates.SUCCESS != (retVal := self.module_load_settings()):
                Log_result_error("failed to load settings.", retVal)
            else:
                Log_verbose("loaded settings successfully")
        else:
            Log_verbose("settings_dict is already filled.")
            retVal = eReturnStates.SUCCESS
        Log_verbose_func_end()
        return retVal, self.settings_dict
    
    def module_reload_settings(self):
        Log_verbose_func_start()
        retVal = ReturnState()
        if eReturnStates.SUCCESS > (retVal := self.module_load_settings()):
            Log_result_error("failed to load settings.", retVal)
        elif eReturnStates.SUCCESS > (retVal := self.module_apply_settings()):
            Log_result_error("apply_settings failed.", retVal)
        else:
            Log_verbose("loaded settings successfully")
        Log_verbose_func_end()
        return retVal

    def module_store_settings_in_database(self, initial_settings = False, settings_dict_arg = None):
        Log_verbose_func_start()
        retVal = ReturnState()
        database_module = DatabaseModule()
        settings_dict = None
        _ids = None
        if initial_settings:
            if eReturnStates.SUCCESS != (retVal := self.module_load_settings()):
                Log_result_error("failed to load initial module settings.", retVal)
            else:
                retVal = eReturnStates.CONTINUE
        if initial_settings and settings_dict_arg != None:
            Log_error("cant use initial_settings and given settings_dict_arg at the same time.")
            retVal = eReturnStates.ERROR
        elif settings_dict_arg != None:
            settings_dict = settings_dict_arg
            retVal = eReturnStates.CONTINUE
        elif self.settings_dict == None:
            Log_error("self.settings_dict was None.")
            retVal = eReturnStates.ERROR
        else:
            settings_dict = self.settings_dict
            retVal = eReturnStates.CONTINUE
        if settings_dict == None:
            Log_error("settings_dict was None.")
            retVal = eReturnStates.ERROR
        if retVal == eReturnStates.CONTINUE:
            class_to_store_settings_for = self.__class__.__name__
            retVal, _ids = database_module.store_settings(settings_dict, settings_topic_arg=class_to_store_settings_for)
            if eReturnStates.SUCCESS != retVal:
                Log_result_error("failed to store settings to database.", retVal)
                _ids = None
        Log_verbose_func_end()
        return retVal, _ids

    def module_remove_settings_from_database(self, settings_topic_arg = None):
        Log_verbose_func_start()
        retVal = ReturnState()
        database_module = DatabaseModule()
        if settings_topic_arg == None:
            class_to_remove_settings_for = self.__class__.__name__
        else:
            class_to_remove_settings_for = settings_topic_arg
        if eReturnStates.SUCCESS != (retVal := database_module.remove_settings(settings_topic_arg=class_to_remove_settings_for)):
            Log_result_error("failed to remove settings from database.", retVal)
        Log_verbose_func_end()
        return retVal

    def module_get_settings_from_database(self, where = "", settings_topic_arg = None):
        Log_verbose_func_start()
        retVal = ReturnState()
        database_module = DatabaseModule()
        if settings_topic_arg == None:
            class_to_get_settings_for = self.__class__.__name__
        else:
            class_to_get_settings_for = settings_topic_arg
        retVal, retreived_settings = database_module.get_settings(where, settings_topic_arg=class_to_get_settings_for)
        if eReturnStates.SUCCESS != retVal:
            Log_result_error("failed to get settings from database.", retVal)
        elif None == retreived_settings:
            Log_error("retreived settings were None.")
            retVal = eReturnStates.ERROR
        Log_verbose_func_end()
        return retVal, retreived_settings
    
    @abc.abstractmethod
    def module_apply_settings(self):
        """needs to be implemented in derived class"""  
        Log_verbose_func_start()
        retVal = ReturnState()
        retVal = eReturnStates.SUCCESS
        Log_verbose_func_end()
        return retVal  
    
    def __dive_into_settings_name_list(self, settings_name_list, settings_dict):
        Log_verbose_func_start()
        retVal = ReturnState()
        result = None
        current_settings_name = settings_name_list[0]
        if current_settings_name in settings_dict:
            if len(settings_name_list) > 1 and isinstance(settings_dict[current_settings_name], dict):
                retVal, result = self.__dive_into_settings_name_list(settings_name_list[1:], settings_dict[current_settings_name])
            else:
                result = settings_dict[current_settings_name]
                retVal = eReturnStates.SUCCESS
            if eReturnStates.ERROR == retVal:
                result = current_settings_name + "." + result
        else:
            retVal = eReturnStates.ERROR
            result = current_settings_name
        Log_verbose_func_end()
        return retVal, result


    def __load_setting(self, settings_topic, settings_name, settings_type = None, can_be_empty = False, is_Nullable = False):
        Log_verbose_func_start()
        retVal = ReturnState()
        if settings_topic not in self.settings_dict:
            Log_error(f"{settings_topic} was not found in settings_dict.")
            retVal = eReturnStates.ERROR
        if isinstance(settings_name, list):
            retVal, dive_result = self.__dive_into_settings_name_list(settings_name, self.settings_dict[settings_topic])
            if eReturnStates.SUCCESS != retVal:
                Log_result_error(f"could not find '{settings_topic}.{dive_result}' in settings_dict.", retVal)
            else:
                if None == dive_result:
                    Log_error(f"{settings_name} was None.")
                    retVal = eReturnStates.ERROR
                elif not can_be_empty and "" == dive_result:
                    Log_error(f"{settings_name} was empty.")
                    retVal = eReturnStates.ERROR
                else:
                    result = dive_result
                    retVal = eReturnStates.CONTINUE
        else:
            if settings_name not in self.settings_dict[settings_topic]:
                Log_error(f"could not find '{settings_topic}.{settings_name}' in settings_dict")
                retVal = eReturnStates.ERROR
            elif None == self.settings_dict[settings_topic][settings_name]:
                Log_error(f"{settings_name} was None.")
                retVal = eReturnStates.ERROR
            elif not can_be_empty and "" == self.settings_dict[settings_topic][settings_name]:
                Log_error(f"{settings_name} was empty.")
                retVal = eReturnStates.ERROR
            else:
                result = self.settings_dict[settings_topic][settings_name]
                retVal = eReturnStates.CONTINUE
        if eReturnStates.CONTINUE == retVal and None != settings_type:
            try:
                retVal = eReturnStates.EXPECTING
                result = settings_type(result)
                retVal = eReturnStates.CONTINUE
            except ValueError as error:
                Log_error(f"given specific setting '{settings_name}' was not convertable to '{str(settings_type)}'.")
                retVal = eReturnStates.ERROR
            if eReturnStates.CONTINUE == retVal:
                if not isinstance(result, settings_type):
                    Log_error(f"result is not of type '{str(settings_type)}'.")
                    retVal = eReturnStates.ERROR
                elif not is_Nullable and (not isinstance(result, bool) and 0 == result):
                    Log_error(f"result was 0.")
                    retVal = eReturnStates.ERROR
                else:
                    retVal = eReturnStates.SUCCESS
        else:
            retVal = eReturnStates.SUCCESS
        if eReturnStates.SUCCESS != retVal:
            Log_result_error(f"failed to load specific setting '{settings_name}' from settings_dict.", retVal)
            result = None
        Log_verbose_func_end()
        return retVal, result

    def load_general_setting(self, general_settings_name, settings_type = None, can_be_empty = False, is_Nullable = False):
        Log_verbose_func_start()
        retVal = ReturnState()
        retVal, result = self.__load_setting(GeneralModuleDefinitions.GENERAL_MODULE_SETTINGS_NAME, general_settings_name, settings_type=settings_type, can_be_empty=can_be_empty, is_Nullable=is_Nullable)
        if eReturnStates.SUCCESS != retVal:
            Log_result_error(f"failed to load general setting '{general_settings_name}'.", retVal)
            result = None
        Log_verbose_func_end()
        return retVal, result
        


    def load_specific_setting(self, specific_settings_name, settings_type = None, can_be_empty = False, is_Nullable = False):
        Log_verbose_func_start()
        retVal = ReturnState()
        retVal, result = self.__load_setting(GeneralModuleDefinitions.SPECIFIC_MODULE_SETTINGS_NAME, specific_settings_name, settings_type=settings_type, can_be_empty=can_be_empty, is_Nullable=is_Nullable)
        if eReturnStates.SUCCESS != retVal:
            Log_result_error(f"failed to load specific setting '{specific_settings_name}'.", retVal)
            result = None
        Log_verbose_func_end()
        return retVal, result