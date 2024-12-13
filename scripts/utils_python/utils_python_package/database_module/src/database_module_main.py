#!/bin/python3
# ******************************************************************************
# - *-coding: utf-8 -*-
# (c) copyright 2024 Alexander Poeschl
# All rights reserved.
# Secrecy Level STRICTLY CONFIDENTIAL
# ******************************************************************************
# @file database_module_main.py
# @author Alexander Poeschl <apoeschlfreelancing@kwanta.net>
# @brief Module for Database Connections.
# ******************************************************************************
from utils_python_package.src.Apoeschlutils import Fix_imports
Fix_imports()
from utils_python_package.src.Apoeschlutils import Log_error, Log_verbose, Log_result_error, Log_verbose_func_start, Log_verbose_func_end, Get_timestamp_for_filenames, Deb
from utils_python_package.src.ReturnState import ReturnState, eReturnStates
from database_module.src.database_definitions import DatabaseModuleDefinitions
import json
import bson
import sys, os, shutil
from glob import glob
import importlib
import inspect

class DatabaseModule():
    general_database_module_settings_file_path = os.path.dirname(os.path.abspath(__file__)) + "/../settings.json"
    database_backups_path = "C:/p/database_backups/"
    latest_database_backup_path = "latest_database_backup"
    settings_dict = None
    used_database_module = None
    used_database_module_instance = None

    def __init__(self, *args):
        if len(args) > 0 and False == args[0]:
            if eReturnStates.SUCCESS > (retVal := self.module_create()):
                Log_result_error(f"create failed.", retVal)
        elif eReturnStates.SUCCESS > (retVal := self.module_create_and_load()):
            Log_result_error(f"create_and_load failed.", retVal)
    
    def module_create(self):
        Log_verbose_func_start()
        retVal = ReturnState()
        if eReturnStates.SUCCESS > (retVal := self.module_load_settings()):
            Log_result_error(f"load_settings failed.", retVal)
        elif eReturnStates.SUCCESS > (retVal := self.module_apply_settings()):
            Log_result_error(f"apply_settings failed.", retVal)
        else:
            Log_verbose("initializing of DatabaseModule successful")
        Log_verbose_func_end()
        return retVal
    
    def module_create_and_load(self):
        Log_verbose_func_start()
        retVal = ReturnState()
        if eReturnStates.SUCCESS > (retVal := self.module_create()):
            Log_result_error(f"create failed.", retVal)
        elif eReturnStates.SUCCESS > (retVal := self.module_load_database_module()):
            Log_result_error(f"initialize_database_client failed.", retVal)
        Log_verbose_func_end()
        return retVal

    def module_load_settings(self):
        Log_verbose_func_start()
        retVal = ReturnState()
        if not os.path.isfile(self.general_database_module_settings_file_path):
            Log_error(f"Settings file '{self.general_database_module_settings_file_path}' is not a file or does not exist.")
            retVal = eReturnStates.ERROR
        else:
            try:
                with open(self.general_database_module_settings_file_path) as settings_file:
                    self.settings_dict = json.load(settings_file)
                retVal = eReturnStates.SUCCESS
            except:
                Log_error(f"failed to load settings file: '{self.general_database_module_settings_file_path}'")
                retVal = eReturnStates.ERROR
            if retVal != eReturnStates.SUCCESS:
                Log_result_error("failed to load settings.", retVal)
            else:
                Log_verbose("loaded settings successfully")
        Log_verbose_func_end()
        return retVal
    
    def module_apply_settings(self):
        Log_verbose_func_start()
        retVal = ReturnState()
        if self.settings_dict == None:
            Log_error("settings_dict was None. Maybe settings were not loaded from settingsfile before?")
            retVal = eReturnStates.ERROR
        elif "used_database_module" not in self.settings_dict:
            Log_error(f"could not find 'used_database_module' in '{self.general_database_module_settings_file_path}'")
            retVal = eReturnStates.ERROR
        elif None == self.settings_dict["used_database_module"]:
            Log_error("could not find used_database_module in settings file.")
            retVal = eReturnStates.ERROR
        elif "" == self.settings_dict["used_database_module"]:
            Log_error("used_database_module in settings file was empty.")
            retVal = eReturnStates.ERROR
        else:
            used_database_module_to_set = self.settings_dict["used_database_module"]
            retVal = self.module_set_used_database_module(used_database_module_to_set)
        if eReturnStates.SUCCESS != retVal:
            Log_result_error(f"set_used_database_module failed.", retVal)
        else:
            retVal, used_database_module = self.module_get_used_database_module()
        if eReturnStates.SUCCESS != retVal:
            Log_result_error("module_get_used_database_module failed.", retVal)
        elif used_database_module_to_set != used_database_module:
            Log_error(f"failed to set used_database_module to '{used_database_module_to_set}'.")
            retVal = eReturnStates.ERROR
        else:
            Log_verbose(f"successfully set used_database_module to: '{self.used_database_module}'")
        if eReturnStates.SUCCESS == retVal:
            Log_verbose("applied settings successfully")
        if eReturnStates.SUCCESS == retVal and self.used_database_module_instance is not None:
            if eReturnStates.SUCCESS > (retVal := self.used_database_module_instance.apply_settings()):
                Log_result_error("failed to apply settings for used_database_module_instance.", retVal)
        Log_verbose_func_end()
        return retVal

    def module_load_database_module(self):
        Log_verbose_func_start()
        retVal = ReturnState()
        modules_path = (os.path.dirname(os.path.abspath(__file__)) + "/../modules/").replace("\\","/")
        modules_search_pattern = modules_path + "*"
        available_modules = []
        found_modules = glob(modules_search_pattern, recursive = False)
        for found_module in found_modules:
            module_basename = os.path.basename(found_module)
            if "__" != module_basename[:2]:
                available_modules.append(module_basename)
        if self.used_database_module not in available_modules:
            Log_error(f"selected module '{self.used_database_module}' was not found in '{modules_path}'.")
            retVal = eReturnStates.ERROR
            return retVal
        path_to_append_for_import = modules_path + self.used_database_module + "/src"
        if not os.path.isdir(path_to_append_for_import):
            Log_error(f"folder '{path_to_append_for_import}' does not exist.")
            retVal = eReturnStates.ERROR
            return retVal
        if path_to_append_for_import not in sys.path:
            sys.path.append(path_to_append_for_import)
        database_module_name = self.used_database_module + "_main"
        path_to_database_module = path_to_append_for_import + "/" + database_module_name + ".py"
        if not os.path.isfile(path_to_database_module):
            Log_error(f"file '{path_to_database_module}' does not exist.")
            retVal = eReturnStates.ERROR
            return retVal
        try:
            module_to_use = importlib.import_module(database_module_name)
        except ModuleNotFoundError as error:
            Log_error(f"Got an ModuleNotFoundError for '{database_module_name}'. Errormessage was: '{error}'")
            retVal = eReturnStates.ERROR
            return retVal
        except ImportError as error:
            Log_error(f"Got an ImportError for '{database_module_name}'. Errormessage was: '{error}'")
            retVal = eReturnStates.ERROR
            return retVal
        except Exception as error:
            Log_error(f"Got an Error when trying to import '{database_module_name}'. Errormessage was: '{error}'")
            retVal = eReturnStates.ERROR
            return retVal
        for database_module_to_use_name, database_module_to_use_class in inspect.getmembers(module_to_use, inspect.isclass):
            if database_module_name in database_module_to_use_class.__module__:
                database_module_to_use_instance = database_module_to_use_class()
                self.used_database_module_instance = database_module_to_use_instance
                retVal = eReturnStates.SUCCESS
                break
        Log_verbose_func_end()
        return retVal
    
    def module_set_used_database_module(self, database_module_to_use):
        Log_verbose_func_start()
        retVal = ReturnState()
        if database_module_to_use == None:
            Log_error("database_module_to_use was None")
            retVal = eReturnStates.ERROR
        elif database_module_to_use == "":
            Log_error("database_module_to_use was empty")
            retVal = eReturnStates.ERROR
        else:
            self.used_database_module = database_module_to_use
            retVal = eReturnStates.SUCCESS
        Log_verbose_func_end()
        return retVal

    def module_get_used_database_module(self):
        Log_verbose_func_start()
        retVal = ReturnState()
        result = None
        if self.used_database_module == None:
            Log_error(f"used_database_module could not be returned. used_database_module was None.")
        elif self.used_database_module == "":
            Log_error(f"used_database_module could not be returned. used_database_module is empty.")
        else:
            result = self.used_database_module
            retVal = eReturnStates.SUCCESS
        Log_verbose_func_end()
        return retVal, result
    
    def module_reload_settings(self):
        Log_verbose_func_start()
        retVal = ReturnState()
        if eReturnStates.SUCCESS > (retVal := self.module_load_settings()):
            Log_result_error("failed to load settings.", retVal)
        elif eReturnStates.SUCCESS > (retVal := self.module_apply_settings()):
            Log_result_error("apply_settings failed.", retVal)
        else:
            Log_verbose("loaded settings successfully")
        if eReturnStates.SUCCESS == retVal and self.used_database_module_instance is not None:
            if eReturnStates.SUCCESS > (retVal := self.used_database_module_instance.reload_settings()):
                Log_result_error("failed to reload settings for used_database_module_instance.", retVal)
        Log_verbose_func_end()
        return retVal
    
    def module_get_settings(self):
        Log_verbose_func_start()
        retVal = ReturnState()
        if self.settings_dict == None:
            if eReturnStates.SUCCESS > (retVal := self.module_load_settings()):
                Log_result_error("failed to load settings.", retVal)
            else:
                Log_verbose("loaded settings successfully")
        else:
            Log_verbose("settings_dict is already filled.")
            retVal = eReturnStates.SUCCESS
        if eReturnStates.SUCCESS == retVal:
            Log_verbose("return settings successfully.")
            retVal = eReturnStates.SUCCESS
        if eReturnStates.SUCCESS == retVal and self.used_database_module_instance is not None:
            retVal, used_database_module_instance_settings = self.used_database_module_instance.get_settings()
            if eReturnStates.SUCCESS != retVal:
                Log_result_error("failed to get settings from used_database_module_instance.", retVal)
            else:
                self.settings_dict[self.used_database_module] = used_database_module_instance_settings
        Log_verbose_func_end()
        return retVal, self.settings_dict
    
    def module_is_used_database_module_instance_initialized(self):
        Log_verbose_func_start()
        retVal = ReturnState()
        if self.used_database_module_instance is not None:
            retVal = eReturnStates.INITIALIZED
            Log_verbose("used_database_module_instance is initialized.")
        else:
            retVal = eReturnStates.INITIALIZED_NOT
            Log_verbose("used_database_module_instance is not initialized.")
        Log_verbose_func_end()
        return retVal


    #interface from outside to submodules
    def initialize_database(self, database_name, ignore_if_database_exists = False):
        Log_verbose_func_start()
        retVal = ReturnState()
        if eReturnStates.INITIALIZED != (retVal := self.module_is_used_database_module_instance_initialized()):
            Log_result_error("used_database_module_instance is not initialized.", retVal)
            retVal = eReturnStates.ERROR
        elif eReturnStates.SUCCESS > (retVal := self.used_database_module_instance.initialize_database(database_name, ignore_if_database_exists=ignore_if_database_exists)):
            Log_result_error(f"failed to initialize database: '{database_name}'.", retVal)
        else:
            Log_verbose("initializing database was successfull.")
        Log_verbose_func_end()
        return retVal
    
    def initialize_table(self, database_name, table_names, create_database_if_necessary = False, ignore_if_database_exists = False, ignore_if_table_exists = False):
        Log_verbose_func_start()
        retVal = ReturnState()
        if eReturnStates.INITIALIZED != (retVal := self.module_is_used_database_module_instance_initialized()):
            Log_result_error("used_database_module_instance is not initialized.", retVal)
            retVal = eReturnStates.ERROR
        elif eReturnStates.SUCCESS > (retVal := self.used_database_module_instance.initialize_table(database_name, table_names, create_database_if_necessary=create_database_if_necessary, ignore_if_database_exists=ignore_if_database_exists, ignore_if_table_exists=ignore_if_table_exists)):
            Log_result_error(f"failed to initialize table: '{table_names}'.", retVal)
        Log_verbose_func_end()
        return retVal

    def drop_database(self, database_name, ignore_if_not_exists = False):
        Log_verbose_func_start()
        retVal = ReturnState()
        if eReturnStates.INITIALIZED != (retVal := self.module_is_used_database_module_instance_initialized()):
            Log_result_error("used_database_module_instance is not initialized.", retVal)
            retVal = eReturnStates.ERROR
        elif eReturnStates.SUCCESS > (retVal := self.used_database_module_instance.drop_database(database_name, ignore_if_not_exists=ignore_if_not_exists)):
            Log_result_error(f"failed to drop database: '{database_name}'.", retVal)
        Log_verbose_func_end()
        return retVal

    def drop_table(self, database_name, table_name, ignore_if_database_not_exists = False, ignore_if_table_not_exists = False):
        Log_verbose_func_start()
        retVal = ReturnState()
        if eReturnStates.INITIALIZED != (retVal := self.module_is_used_database_module_instance_initialized()):
            Log_result_error("used_database_module_instance is not initialized.", retVal)
            retVal = eReturnStates.ERROR
        elif eReturnStates.SUCCESS > (retVal := self.used_database_module_instance.drop_table(database_name, table_name, ignore_if_database_not_exists=ignore_if_database_not_exists, ignore_if_table_not_exists=ignore_if_table_not_exists)):
            Log_result_error(f"failed to drop table: '{table_name}'.", retVal)
        Log_verbose_func_end()
        return retVal
    
    def check_if_database_exists(self, database_name):
        Log_verbose_func_start()
        retVal = ReturnState()
        if eReturnStates.INITIALIZED != (retVal := self.module_is_used_database_module_instance_initialized()):
            Log_result_error("used_database_module_instance is not initialized.", retVal)
            retVal = eReturnStates.ERROR
        elif eReturnStates.SUCCESS > (retVal := self.used_database_module_instance.check_if_database_exists(database_name)):
            Log_result_error(f"failed to check if database '{database_name}' exists.", retVal)
        Log_verbose_func_end()
        return retVal
    
    def check_if_table_exists(self, database_name, table_name):
        Log_verbose_func_start()
        retVal = ReturnState()
        if eReturnStates.INITIALIZED != (retVal := self.module_is_used_database_module_instance_initialized()):
            Log_result_error("used_database_module_instance is not initialized.", retVal)
            retVal = eReturnStates.ERROR
        elif eReturnStates.SUCCESS > (retVal := self.used_database_module_instance.check_if_table_exists(database_name, table_name)):
            Log_result_error(f"failed to check if: '{table_name}' exists in database '{database_name}'.", retVal)
        Log_verbose_func_end()
        return retVal
    
    def get_database_status(self, database_name):
        Log_verbose_func_start()
        retVal = ReturnState()
        if eReturnStates.INITIALIZED != (retVal := self.module_is_used_database_module_instance_initialized()):
            Log_result_error("used_database_module_instance is not initialized.", retVal)
            retVal = eReturnStates.ERROR
        else:
            result = None
            retVal, result = self.used_database_module_instance.get_database_status(database_name)
            if eReturnStates.SUCCESS != retVal:
                Log_result_error(f"failed to get status for database '{database_name}'.", retVal)
        Log_verbose_func_end()
        return retVal, result
    
    def get_table_names(self, database_name):
        Log_verbose_func_start()
        retVal = ReturnState()
        if eReturnStates.INITIALIZED != (retVal := self.module_is_used_database_module_instance_initialized()):
            Log_result_error("used_database_module_instance is not initialized.", retVal)
            retVal = eReturnStates.ERROR
        else:
            result = None
            retVal, result = self.used_database_module_instance.get_table_names(database_name)
            if eReturnStates.SUCCESS != retVal:
                Log_result_error(f"failed to get table_names for database '{database_name}'.", retVal)
                retVal = eReturnStates.ERROR
        Log_verbose_func_end()
        return retVal, result
    
    def get_database_names(self):
        Log_verbose_func_start()
        retVal = ReturnState()
        result = None
        if eReturnStates.INITIALIZED != (retVal := self.module_is_used_database_module_instance_initialized()):
            Log_result_error("used_database_module_instance is not initialized.", retVal)
            retVal = eReturnStates.ERROR
        else:
            result = None
            retVal, result = self.used_database_module_instance.get_database_names()
            if eReturnStates.SUCCESS != retVal:
                Log_result_error(f"failed to get database_names.", retVal)
                retVal = eReturnStates.ERROR
        Log_verbose_func_end()
        return retVal, result
    
    def insert_into_table(self, database_name, table_name, entries, create_database_if_necessary = False, create_table_if_necessary = False):
        Log_verbose_func_start()
        retVal = ReturnState()
        _ids = None
        if eReturnStates.INITIALIZED != (retVal := self.module_is_used_database_module_instance_initialized()):
            Log_result_error("used_database_module_instance is not initialized.", retVal)
            retVal = eReturnStates.ERROR
        else:
            retVal, _ids = self.used_database_module_instance.insert_into_table(database_name, table_name, entries, create_database_if_necessary=create_database_if_necessary, create_table_if_necessary=create_table_if_necessary)
            if eReturnStates.SUCCESS != retVal:
                Log_result_error(f"failed to insert entries '{entries}' into table '{table_name}' in database '{database_name}'.", retVal)
                retVal = eReturnStates.ERROR
                _ids = None
        Log_verbose_func_end()
        return retVal, _ids

    def get_elements_from_table(self, database_name, table_name, where):
        Log_verbose_func_start()
        retVal = ReturnState()
        if eReturnStates.INITIALIZED != (retVal := self.module_is_used_database_module_instance_initialized()):
            Log_result_error("used_database_module_instance is not initialized.", retVal)
            retVal = eReturnStates.ERROR
        else:
            result = None
            retVal, result = self.used_database_module_instance.get_elements_from_table(database_name, table_name, where)
        if eReturnStates.SUCCESS != retVal:
            Log_result_error(f"failed to get elements (where: '{where}').", retVal)
            result = None
        Log_verbose_func_end()
        return retVal, result

    def delete_one_from_table(self, database_name, table_name, where):
        Log_verbose_func_start()
        retVal = ReturnState()
        if eReturnStates.INITIALIZED != (retVal := self.module_is_used_database_module_instance_initialized()):
            Log_result_error("used_database_module_instance is not initialized.", retVal)
            retVal = eReturnStates.ERROR
        else:
            result = None
            retVal, result = self.used_database_module_instance.delete_one_from_table(database_name, table_name, where)
        if eReturnStates.SUCCESS != retVal:
            Log_result_error(f"failed to delete elements (where: '{where}').", retVal)
            result = None
        Log_verbose_func_end()
        return retVal, result

    def delete_many_from_table(self, database_name, table_name, where):
        Log_verbose_func_start()
        retVal = ReturnState()
        if eReturnStates.INITIALIZED != (retVal := self.module_is_used_database_module_instance_initialized()):
            Log_result_error("used_database_module_instance is not initialized.", retVal)
            retVal = eReturnStates.ERROR
        else:
            result = None
            retVal, result = self.used_database_module_instance.delete_many_from_table(database_name, table_name, where)
        if eReturnStates.SUCCESS != retVal:
            Log_result_error(f"failed to delete elements (where: '{where}').", retVal)
            result = None
        Log_verbose_func_end()
        return retVal, result
    
    def store_settings(self, settings_dict, settings_topic_arg = None):
        Log_verbose_func_start()
        retVal = ReturnState()
        settings_topic = None
        _ids = None
        if settings_topic_arg == None:
            frame = sys._getframe().f_back
            qualifier_name = frame.f_code.co_qualname
            class_to_store_settings_for = qualifier_name.split(".")[0]
            settings_topic = class_to_store_settings_for
            retVal = eReturnStates.CONTINUE
        else:
            settings_topic = settings_topic_arg
            retVal = eReturnStates.CONTINUE
        if settings_topic == None:
            Log_error("settings_topic was None.")
            retVal = eReturnStates.ERROR
        if retVal == eReturnStates.CONTINUE:
            retVal, _ids = self.insert_into_table( DatabaseModuleDefinitions.SETTINGS, settings_topic, settings_dict, create_database_if_necessary=True, create_table_if_necessary=True)
            if eReturnStates.SUCCESS != retVal:
                Log_result_error("failed to store settings into database.", retVal)
                _ids = None
        Log_verbose_func_end()
        return retVal, _ids
    
    def remove_settings(self, settings_topic_arg = None):
        Log_verbose_func_start()
        retVal = ReturnState()
        settings_topic = None
        if settings_topic_arg == None:
            frame = sys._getframe().f_back
            qualifier_name = frame.f_code.co_qualname
            class_to_store_settings_for = qualifier_name.split(".")[0]
            settings_topic = class_to_store_settings_for
        else:
            settings_topic = settings_topic_arg
        if settings_topic == None:
            Log_error("settings_topic was None.")
            retVal = eReturnStates.ERROR
        elif eReturnStates.SUCCESS != (retVal := self.drop_table(DatabaseModuleDefinitions.SETTINGS, settings_topic, ignore_if_database_not_exists=True, ignore_if_table_not_exists=True)):
            Log_result_error("failed to remove settings from database.", retVal)
        Log_verbose_func_end()
        return retVal
    
    def get_settings(self, where, settings_topic_arg = None):
        Log_verbose_func_start()
        retVal = ReturnState()
        settings_topic = None
        retreived_settings = None
        if settings_topic_arg == None:
            frame = sys._getframe().f_back
            qualifier_name = frame.f_code.co_qualname
            class_to_store_settings_for = qualifier_name.split(".")[0]
            settings_topic = class_to_store_settings_for
        else:
            settings_topic = settings_topic_arg
        if settings_topic == None:
            Log_error("settings_topic was None.")
            retVal = eReturnStates.ERROR
        else:
            retVal, retreived_elements = self.get_elements_from_table(DatabaseModuleDefinitions.SETTINGS, settings_topic, where)
            if eReturnStates.SUCCESS != retVal:
                Log_result_error("failed to get settings from database.", retVal)
                retreived_settings = None
            else:
                retreived_settings = retreived_elements[0]
                #TODO what is that?
                #else:
                #    log_error("retrieved elements did not contain any settings.")
                #    retVal = eReturnStates.ERROR
        Log_verbose_func_end()
        return retVal, retreived_settings
    
    def backup_database(self, is_test = False):
        Log_verbose_func_start()
        retVal = ReturnState()
        backup_folder_path = None
        if not os.path.isdir(self.database_backups_path):
            os.mkdir(self.database_backups_path)
        backup_folder_path = self.database_backups_path + Get_timestamp_for_filenames() + "_database_backup"
        if not os.path.isdir(backup_folder_path):
            os.mkdir(backup_folder_path)
        retVal, database_names = self.get_database_names()
        if eReturnStates.SUCCESS != retVal:
            Log_result_error(f"failed to get database_names from database.", retVal)
        else:
            retVal = eReturnStates.CONTINUE
        if eReturnStates.CONTINUE == retVal:
            for database_name in database_names:
                database_folder_path = os.path.join(backup_folder_path, database_name)
                if not os.path.isdir(database_folder_path):
                    os.mkdir(database_folder_path)
                retVal, table_names = self.get_table_names(database_name)
                if eReturnStates.SUCCESS != retVal:
                    Log_result_error(f"failed to get table_names from database '{database_name}'.", retVal)
                else:
                    retVal = eReturnStates.CONTINUE
                if eReturnStates.CONTINUE == retVal:
                    for table_name in table_names:
                        table_folder_path = os.path.join(database_folder_path, table_name)
                        if not os.path.isdir(table_folder_path):
                            os.mkdir(table_folder_path)
                        retVal, elements = self.get_elements_from_table(database_name, table_name, "")
                        if eReturnStates.SUCCESS != retVal:
                            Log_result_error(f"failed to get elements from table '{table_name}' from database '{database_name}'.", retVal)
                        else:
                            retVal = eReturnStates.CONTINUE
                        if eReturnStates.CONTINUE == retVal:
                            for index, element in enumerate(elements):
                                element_backup_path = os.path.join(table_folder_path, str(index) + ".bson")
                                with open(element_backup_path, 'wb+') as backup_file:
                                    try:
                                        bson_data = bson.BSON.encode(element)
                                        backup_file.write(bson_data)
                                        retVal = eReturnStates.SUCCESS
                                    except Exception as error:
                                        Log_error(f"failed to write table '{table_name}' from database '{database_name}' to backup_file {element_backup_path}")
                                        retVal = eReturnStates.ERROR
                                if eReturnStates.SUCCESS != retVal:
                                    break
                        if eReturnStates.SUCCESS != retVal:
                            break
                if eReturnStates.SUCCESS != retVal:
                    break
        if not is_test:
            latest_database_backup_path = os.path.join(self.database_backups_path, self.latest_database_backup_path)
            shutil.rmtree(latest_database_backup_path, ignore_errors=True)
            shutil.copytree(backup_folder_path, latest_database_backup_path)
        Log_verbose_func_end()
        return retVal, backup_folder_path
    
    def drop_complete_database(self):
        Log_verbose_func_start()
        retVal = ReturnState()
        retVal, database_names = self.get_database_names()
        if eReturnStates.SUCCESS != retVal:
            Log_result_error(f"failed to get database_names from database.", retVal)
        else:
            for database_name in database_names:
                retVal = self.drop_database(database_name)
                if eReturnStates.SUCCESS != retVal:
                    Log_result_error(f"failed to drop database '{database_name}'.", retVal)
                    break
        Log_verbose_func_end()
        return retVal
 
    def restore_backup_in_database(self, backup_folder_path, dont_drop_database = False):
        Log_verbose_func_start()
        retVal = ReturnState()
        if not os.path.isdir(backup_folder_path):
            Log_error(f"backup_path '{backup_folder_path}' is not a directory.")
            retVal = eReturnStates.ERROR
        elif not dont_drop_database and eReturnStates.SUCCESS != (retVal := self.drop_complete_database()):
            Log_result_error(f"drop_complete_database failed.", retVal)
        else:
            database_names = os.listdir(backup_folder_path)
            for database_name in database_names:
                database_folder_path = os.path.join(backup_folder_path, database_name)
                if not os.path.isdir(database_folder_path):
                    Log_error(f"database_folder_path '{database_folder_path}' is not a directory.")
                    retVal = eReturnStates.ERROR
                    break
                else:
                    retVal = eReturnStates.CONTINUE
                if eReturnStates.CONTINUE == retVal:
                    table_names = os.listdir(database_folder_path)
                    for table_name in table_names:
                        table_folder_path = os.path.join(database_folder_path, table_name)
                        if not os.path.isdir(table_folder_path):
                            Log_error(f"table_folder_path '{table_folder_path}' is not a directory.")
                            retVal = eReturnStates.ERROR
                            break
                        else:
                            retVal = eReturnStates.CONTINUE
                        if eReturnStates.CONTINUE == retVal:
                            element_filenames = os.listdir(table_folder_path)
                            for element_name in element_filenames:
                                element_file_path = os.path.join(table_folder_path, element_name) 
                                if not os.path.isfile(element_file_path):
                                    Log_error(f"element_file_path '{element_file_path}' is not a file.")
                                    retVal = eReturnStates.ERROR
                                    break
                                else:
                                    retVal = eReturnStates.CONTINUE
                                if eReturnStates.CONTINUE == retVal:
                                    with open(element_file_path, 'rb') as backup_file:
                                        try:
                                            bson_data = bson.decode_all(backup_file.read())
                                            retVal = self.insert_into_table(database_name, table_name, bson_data, create_database_if_necessary=True, create_table_if_necessary=True)
                                        except Exception as error:
                                            Log_error(f"failed to store table '{table_name}' in database '{database_name}' from backup_file {element_file_path}")
                                            retVal = eReturnStates.ERROR
        Log_verbose_func_end()
        return retVal
    
    def restore_latest_backup_in_database(self, dont_drop_database = False):
        Log_verbose_func_start()
        retVal = ReturnState()
        latest_database_backup_path = os.path.join(self.database_backups_path, self.latest_database_backup_path)
        if eReturnStates.SUCCESS != (retVal := self.restore_backup_in_database(latest_database_backup_path, dont_drop_database=dont_drop_database)):
            Log_result_error("failed to restore latest database backup.", retVal)
        Log_verbose_func_end()
        return retVal