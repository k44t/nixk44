#!/bin/python3
# ******************************************************************************
# - *-coding: utf-8 -*-
# (c) copyright 2024 Alexander Poeschl
# All rights reserved.
# Secrecy Level STRICTLY CONFIDENTIAL
# ******************************************************************************
# @file mongodb_module_main.py
# @author Alexander Poeschl <apoeschlfreelancing@kwanta.net>
# @brief Wrapper Module for the MongoDB Package.
# ******************************************************************************
from utils_python_package.src.Apoeschlutils import Fix_imports
Fix_imports()
from utils_python_package.src.Apoeschlutils import Log_error, Log_verbose, Log_result_error, Log_verbose_func_start, Log_verbose_func_end
from utils_python_package.src.ReturnState import ReturnState, eReturnStates
import os
import json
import pymongo
from pymongo import MongoClient

class MongoDBModule():
    mongodb_database_module_settings_file_path = os.path.dirname(os.path.abspath(__file__)) + "/../settings.json"
    mongodb_client = None
    mongodb_adress = None
    mongodb_port = None
    init_text = "init_you_can_delete_this"

    def __init__(self):
        self.create()
    
    def create(self):
        Log_verbose_func_start()
        retVal = ReturnState()
        if eReturnStates.SUCCESS > (retVal := self.load_settings()):
            Log_result_error(f"load_settings failed.", retVal)
        elif eReturnStates.SUCCESS > (retVal := self.apply_settings()):
            Log_result_error(f"apply_settings failed.", retVal)
        elif eReturnStates.SUCCESS > (retVal := self.initialize_mongodb_client()):
            Log_result_error(f"initialize_mongodb_client failed.", retVal)
        else:
            Log_verbose("initializing of MongoDBModule successful")
        Log_verbose_func_end()
        return retVal

    def load_settings(self):
        Log_verbose_func_start()
        retVal = ReturnState()
        if not os.path.isfile(self.mongodb_database_module_settings_file_path):
            Log_error(f"Settings file '{self.mongodb_database_module_settings_file_path}' is not a file or does not exist.")
            retVal = eReturnStates.ERROR
        else:
            try:
                with open(self.mongodb_database_module_settings_file_path) as settings_file:
                    self.settings_dict = json.load(settings_file)
                retVal = eReturnStates.SUCCESS
            except:
                Log_error(f"failed to load settings file: '{self.mongodb_database_module_settings_file_path}'")
                retVal = eReturnStates.ERROR
            if retVal != eReturnStates.SUCCESS:
                Log_result_error("failed to load settings.", retVal)
            else:
                Log_verbose("loaded settings successfully")
        Log_verbose_func_end()
        return retVal
    
    def apply_settings(self):
        Log_verbose_func_start()
        retVal = ReturnState()
        if self.settings_dict == None:
            Log_error("settings_dict was None. Maybe settings were not loaded from settingsfile before?")
            retVal = eReturnStates.ERROR
        elif "mongodb_adress" not in self.settings_dict:
            Log_error(f"could not find 'mongodb_adress' in '{self.mongodb_database_module_settings_file_path}'")
            retVal = eReturnStates.ERROR
        elif self.settings_dict["mongodb_adress"] == None:
            Log_error(f"could not find 'mongodb_adress' in '{self.mongodb_database_module_settings_file_path}'")
            retVal = eReturnStates.ERROR
        elif self.settings_dict["mongodb_adress"] == "":
            Log_error(f"'mongodb_adress' in '{self.mongodb_database_module_settings_file_path}' was empty.")
            retVal = eReturnStates.ERROR
        else:
            self.mongodb_adress = self.settings_dict["mongodb_adress"]
            Log_verbose(f"set mongodb_adress to '{self.mongodb_adress}'")
            retVal = eReturnStates.SUCCESS
        if eReturnStates.SUCCESS != retVal:
            Log_result_error("failed to load mongodb_adress.", retVal)
        if "mongodb_port" not in self.settings_dict:
            Log_error(f"could not find 'mongodb_port' in '{self.mongodb_database_module_settings_file_path}'")
            retVal = eReturnStates.ERROR
        elif self.settings_dict["mongodb_port"] == None:
            Log_error(f"could not find 'mongodb_port' in '{self.mongodb_database_module_settings_file_path}'")
            retVal = eReturnStates.ERROR
        elif self.settings_dict["mongodb_port"] == "":
            Log_error(f"'mongodb_port' in '{self.mongodb_database_module_settings_file_path}' was empty.")
            retVal = eReturnStates.ERROR
        else:
            mongodb_port_to_convert = self.settings_dict["mongodb_port"]
            try:
                mongodb_port = int(mongodb_port_to_convert)
                retVal = eReturnStates.SUCCESS
            except ValueError as e:
                Log_error(f"given mongodb_port ({mongodb_port_to_convert}) was not convertable to a number.")
                retVal = eReturnStates.ERROR
        if not isinstance(mongodb_port, int):
            Log_error(f"given mongodb_port is not a number.")
            retVal = eReturnStates.ERROR
        elif 0 == mongodb_port:
            Log_error("given mongodb_port was zero.")
            retVal = eReturnStates.ERROR
        elif eReturnStates.SUCCESS != retVal:
            Log_result_error("failed to load mongodb_port.", retVal)
        else:
            self.mongodb_port = mongodb_port
            retVal = eReturnStates.SUCCESS
            Log_verbose(f"set mongodb_port to '{self.mongodb_port}'")
        if eReturnStates.SUCCESS == retVal:
            Log_verbose("applied settings successfully")
        Log_verbose_func_end()
        return retVal
    
    def reload_settings(self):
        Log_verbose_func_start()
        retVal = ReturnState()
        if eReturnStates.SUCCESS > (retVal := self.load_settings()):
            Log_result_error(f"load_settings failed.", retVal)
        elif eReturnStates.SUCCESS > (retVal := self.apply_settings()):
            Log_result_error(f"apply_settings failed.", retVal)
        elif eReturnStates.SUCCESS > (retVal := self.initialize_mongodb_client()):
            Log_result_error(f"initialize_mongodb_client failed.", retVal)
        if eReturnStates.SUCCESS == retVal:
            Log_verbose("reloaded settings successfully")
        Log_verbose_func_end()
        return retVal
    
    def get_settings(self):
        Log_verbose_func_start()
        retVal = ReturnState()
        if self.settings_dict == None:
            if eReturnStates.SUCCESS > (retVal := self.load_settings()):
                Log_result_error("failed to load settings.", retVal)
            else:
                Log_verbose("loaded settings successfully")
        else:
            Log_verbose("settings_dict is already filled.")
            retVal = eReturnStates.SUCCESS
        if eReturnStates.SUCCESS == retVal:
            Log_verbose("return settings successfully.")
            retVal = eReturnStates.SUCCESS
        Log_verbose_func_end()
        return retVal, self.settings_dict
    
    def initialize_mongodb_client(self):
        Log_verbose_func_start()
        retVal = ReturnState()
        if self.mongodb_adress == None:
            Log_error("mongodb_adress was None.")
            retVal = eReturnStates.ERROR
        elif self.mongodb_adress == "":
            Log_error("mongodb_adress was empty.")
            retVal = eReturnStates.ERROR
        elif self.mongodb_port == None:
            Log_error("mongodb_port was None.")
            retVal = eReturnStates.ERROR
        elif not isinstance(self.mongodb_port, int):
            Log_error("mongodb_port was not a number.")
            retVal = eReturnStates.ERROR
        else:
            mongodb_full_adress = "mongodb://" + self.mongodb_adress + ":" + str(self.mongodb_port) + "/"
            try:
                mongodb_client = MongoClient(mongodb_full_adress)
                if mongodb_client != None:
                    self.mongodb_client = mongodb_client
                    retVal = eReturnStates.SUCCESS
                    Log_verbose("initialized mongodb_client successfully.")
                else:
                    Log_result_error(f"failed to initialize mongodb client.", retVal)
            except Exception as error:
                Log_error(f"mongodb_client could not be initialized. Errormessage was: '{error}'")
                retVal = eReturnStates.ERROR
        Log_verbose_func_end()
        return retVal
    
    def __initialize_database(self, database_names, ignore_if_database_exists = False):
        Log_verbose_func_start()
        retVal = ReturnState()
        if eReturnStates.INITIALIZED != (retVal := self.__check_if_mongodb_client_is_initialized()):
            Log_result_error(f"mongodb_client is not initialized.", retVal)
            retVal = eReturnStates.ERROR
        elif isinstance(database_names, str):
            database_names = [database_names]
        elif not isinstance(database_names, list):
            Log_error("database_names was neither a string nor a list.")
            retVal = eReturnStates.ERROR
        if eReturnStates.ERROR != retVal:
            for database_name in database_names:
                if not isinstance(database_name, str):
                    Log_error(f"database_name '{database_name}' was not a string.")
                    retVal = eReturnStates.ERROR
                    break
                elif not ignore_if_database_exists and eReturnStates.EXISTS_NOT != (retVal := self.__check_if_database_exists(database_name)):
                    Log_result_error(f"database '{database_name}' already exists.", retVal)
                    retVal = eReturnStates.ERROR
                else:
                    database = self.mongodb_client[database_name]
                    init_table = database[self.init_text]
                    init_table.insert_one({self.init_text:self.init_text})
                    if eReturnStates.EXISTS != (retVal := self.__check_if_database_exists(database_name)):
                        Log_result_error(f"database '{database_name}' could not be created.", retVal)
                        retVal = eReturnStates.ERROR
                    else:
                        Log_verbose(f"database '{database_name}' was created.")
                        retVal = eReturnStates.SUCCESS
        Log_verbose_func_end()
        return retVal
    
    def __initialize_collection(self, database_name, collection_names, create_database_if_necessary = False, ignore_if_database_exists = False, ignore_if_collection_exists = False):
        Log_verbose_func_start()
        retVal = ReturnState()
        if eReturnStates.INITIALIZED != (retVal := self.__check_if_mongodb_client_is_initialized()):
            Log_result_error(f"mongodb_client is not initialized.", retVal)
            retVal = eReturnStates.ERROR
        elif not create_database_if_necessary and eReturnStates.EXISTS != (retVal := self.__check_if_database_exists(database_name)):
            Log_result_error(f"database '{database_name}' does not exist.", retVal)
            retVal = eReturnStates.ERROR
        elif create_database_if_necessary and eReturnStates.EXISTS != (retVal := self.__check_if_database_exists(database_name)):
                retVal = self.__initialize_database(database_name, ignore_if_database_exists=ignore_if_database_exists)
        if eReturnStates.SUCCESS != retVal:
            Log_result_error("__initialize_database failed.", retVal)
        elif isinstance(collection_names, str):
            collection_names = [collection_names]
        elif not isinstance(collection_names, list):
            Log_error("collection_names was neither a string nor a list.")
            retVal = eReturnStates.ERROR
        if eReturnStates.ERROR != retVal:
            for collection_name in collection_names:
                if not isinstance(collection_name, str):
                    Log_error(f"collection_name '{collection_name}' was not a string.")
                    retVal = eReturnStates.ERROR
                    break
                elif not ignore_if_collection_exists and eReturnStates.EXISTS_NOT != (retVal := self.__check_if_collection_exists(database_name, collection_name)):
                    Log_result_error(f"collection '{collection_name}' already exists in database '{database_name}'.", retVal)
                    retVal = eReturnStates.ERROR
                    break
                else:
                    database = self.mongodb_client[database_name]
                    retVal, already_existing_collections_in_database = self.get_table_names(database_name)
                    if eReturnStates.SUCCESS != retVal:
                        Log_result_error(f"failed to get table_names for database '{database_name}'.", retVal)
                    elif len(already_existing_collections_in_database) == 1:
                        if self.init_text == already_existing_collections_in_database[0]:
                            database[self.init_text].drop()
                    collection = database[collection_name]
                    collection.insert_one({self.init_text:self.init_text})
                    if eReturnStates.EXISTS != (retVal := self.__check_if_collection_exists(database_name, collection_name)):
                        Log_result_error(f"collection '{collection_name}' could not be created in '{database_name}'.", retVal)
                        retVal = eReturnStates.ERROR
                        break
                    else:
                        Log_verbose(f"collection '{collection_name}' was created in '{database_name}'.")
                        retVal = eReturnStates.SUCCESS
        Log_verbose_func_end()
        return retVal

    def __drop_collection(self, database_name, collection_name, ignore_if_database_not_exists = False, ignore_if_collection_not_exists = False):
        Log_verbose_func_start()
        retVal = ReturnState()
        if eReturnStates.INITIALIZED != (retVal := self.__check_if_mongodb_client_is_initialized()):
            Log_result_error(f"mongodb_client is not initialized.", retVal)
            retVal = eReturnStates.ERROR
        elif not ignore_if_database_not_exists and eReturnStates.EXISTS != (retVal := self.__check_if_database_exists(database_name)):
            Log_result_error(f"database '{database_name}' does not exist.", retVal)
            retVal = eReturnStates.ERROR
        elif not ignore_if_collection_not_exists and eReturnStates.EXISTS != (retVal := self.__check_if_collection_exists(database_name, collection_name)):
            Log_result_error(f"collection '{collection_name}' does not exist in database '{database_name}'.", retVal)
            retVal = eReturnStates.ERROR
        else:
            retVal, all_existing_collections_in_database = self.__get_collection_names(database_name)
            if eReturnStates.SUCCESS != retVal:
                Log_result_error("__get_collection_names failed.", retVal)
                retVal = eReturnStates.ERROR
            # in case we would drop the last collection, we need to initialize some "init collection" so that database does not disappear.
            elif len(all_existing_collections_in_database) == 1:
                init_collection = self.mongodb_client[database_name][self.init_text]
                init_collection.insert_one({self.init_text : self.init_text})
            if eReturnStates.ERROR != retVal:
                try:
                    self.mongodb_client[database_name][collection_name].drop()
                except Exception as error:
                    Log_error(f"Collection '{collection_name}' does not exist in database '{database_name}'. Errormessage was '{error}'")
                    retVal = eReturnStates.ERROR
                if eReturnStates.EXISTS_NOT != (retVal := self.__check_if_collection_exists(database_name, collection_name)):
                    Log_result_error(f"failed to drop collection. Collection '{collection_name}' still exist in database '{database_name}'.", retVal)
                    retVal = eReturnStates.ERROR
                else:
                    retVal = eReturnStates.SUCCESS
        Log_verbose_func_end()
        return retVal
    
    def __drop_database(self, database_name, ignore_if_not_exists = False):
        Log_verbose_func_start()
        retVal = ReturnState()
        if "admin" == database_name:
            Log_error("dropping the admin database is prohibited by mongodb")
            retVal = eReturnStates.SUCCESS
        elif eReturnStates.INITIALIZED != (retVal := self.__check_if_mongodb_client_is_initialized()):
            Log_result_error(f"mongodb_client is not initialized.", retVal)
            retVal = eReturnStates.ERROR
        elif not ignore_if_not_exists and eReturnStates.EXISTS != (retVal := self.__check_if_database_exists(database_name)):
            Log_result_error(f"database '{database_name}' does not exist.", retVal)
            retVal = eReturnStates.ERROR
        else:
            try:
                self.mongodb_client.drop_database(database_name)
                retVal = eReturnStates.SUCCESS
            except Exception as error:
                Log_error(f"failed to drop database. Errormessage was: '{error}'")
                retVal = eReturnStates.ERROR
        Log_verbose_func_end()
        return retVal


    def __check_if_database_exists(self, database_name):
        Log_verbose_func_start()
        retVal = ReturnState()
        if eReturnStates.INITIALIZED != (retVal := self.__check_if_mongodb_client_is_initialized()):
            Log_result_error(f"mongodb_client is not initialized.", retVal)
            retVal = eReturnStates.ERROR
        else:
            database_names = self.mongodb_client.list_database_names()
            if database_name in database_names:
                Log_verbose(f"database '{database_name}' exists.")
                retVal = eReturnStates.EXISTS
            else:
                Log_verbose(f"Database '{database_name}' doesn't exist")
                retVal = eReturnStates.EXISTS_NOT
        Log_verbose_func_end()
        return retVal

    def __check_if_collection_exists(self, database_name, collection_name):
        Log_verbose_func_start()
        retVal = ReturnState()
        if eReturnStates.INITIALIZED != (retVal := self.__check_if_mongodb_client_is_initialized()):
            Log_result_error(f"mongodb_client is not initialized.", retVal)
            retVal = eReturnStates.ERROR
        elif eReturnStates.EXISTS != (retVal := self.__check_if_database_exists(database_name)):
            Log_result_error(f"database '{database_name}' does not exist.", retVal)
            retVal = eReturnStates.ERROR
        else:
            try:
                self.mongodb_client[database_name].validate_collection(collection_name)
                retVal = eReturnStates.EXISTS
            except pymongo.errors.OperationFailure:
                Log_verbose(f"Collection '{collection_name}' doesn't exist")
                retVal = eReturnStates.EXISTS_NOT
        Log_verbose_func_end()
        return retVal
    
    
    
    def __get_collection_names(self, database_name):
        Log_verbose_func_start()
        retVal = ReturnState()
        result = None
        if eReturnStates.INITIALIZED != (retVal := self.__check_if_mongodb_client_is_initialized()):
            Log_result_error(f"mongodb_client is not initialized.", retVal)
            retVal = eReturnStates.ERROR
        elif eReturnStates.EXISTS != (retVal := self.__check_if_database_exists(database_name)):
            Log_result_error(f"database '{database_name}' does not exist.", retVal)
            retVal = eReturnStates.ERROR
        else:
            result = self.mongodb_client[database_name].list_collection_names()
            if result == None:
                Log_error(f"list_collection_names failed for database '{database_name}'")
                retVal = eReturnStates.ERROR
            else:
                retVal = eReturnStates.SUCCESS
        Log_verbose_func_end()
        return retVal, result
    
    def __get_database_names(self):
        Log_verbose_func_start()
        retVal = ReturnState()
        result = None
        if eReturnStates.INITIALIZED != (retVal := self.__check_if_mongodb_client_is_initialized()):
            Log_result_error(f"mongodb_client is not initialized.", retVal)
            retVal = eReturnStates.ERROR
        else:
            result = self.mongodb_client.list_database_names()
            if None == result:
                retVal = eReturnStates.ERROR
            else:
                retVal = eReturnStates.SUCCESS
        Log_verbose_func_end()
        return retVal, result
    
    def __get_database_status(self, database_name):
        Log_verbose_func_start()
        retVal = ReturnState()
        result = None
        if eReturnStates.INITIALIZED != (retVal := self.__check_if_mongodb_client_is_initialized()):
            Log_result_error(f"mongodb_client is not initialized.", retVal)
            retVal = eReturnStates.ERROR
        elif eReturnStates.EXISTS != (retVal := self.__check_if_database_exists(database_name)):
            Log_result_error(f"database '{database_name}' does not exist.", retVal)
            retVal = eReturnStates.ERROR
        else:
            result = self.mongodb_client[database_name].command("dbstats")
            retVal = eReturnStates.SUCCESS
        Log_verbose_func_end()
        return retVal, result
    
    def __check_if_mongodb_client_is_initialized(self):
        Log_verbose_func_start()
        retVal = ReturnState()
        if self.mongodb_client == None:
            Log_error("mongodb_client was None.")
            retVal = eReturnStates.ERROR
        else:
            Log_verbose("mongodb_client seems initialized.")
            retVal = eReturnStates.INITIALIZED
        Log_verbose_func_end()
        return retVal


    def __insert_into_collection(self, database_name, collection_name, entries, create_database_if_necessary = False, create_collection_if_necessary = False):
        Log_verbose_func_start()
        retVal = ReturnState()
        entry = None
        _ids = None
        if eReturnStates.INITIALIZED != (retVal := self.__check_if_mongodb_client_is_initialized()):
            Log_result_error(f"mongodb_client is not initialized.", retVal)
            retVal = eReturnStates.ERROR
        elif not isinstance(entries, dict) and not isinstance(entries, list):
            Log_error(f"given entry was neither a dictionary nor a list.")
            retVal = eReturnStates.ERROR
        elif not create_database_if_necessary and eReturnStates.EXISTS != (retVal := self.__check_if_database_exists(database_name)):
            Log_result_error(f"database '{database_name}' does not exist.", retVal)
            retVal = eReturnStates.ERROR
        elif not create_collection_if_necessary and eReturnStates.EXISTS != (retVal := self.__check_if_collection_exists(collection_name)):
            Log_result_error(f"collection '{collection_name}' does not exist.", retVal)
        else:
            try:
                table = self.mongodb_client[database_name][collection_name]
                if isinstance(entries, dict):
                    entry = table.insert_one(entries)
                    if entry.inserted_id is not None:
                        _ids = entry.inserted_id
                    retVal = eReturnStates.SUCCESS
                elif isinstance(entries, list):
                    for entry_to_check in entries:
                        if not isinstance(entry_to_check, dict):
                            Log_error(f"given entry was neither a dictionary.")
                            retVal = eReturnStates.ERROR
                            break
                    entry = table.insert_many(entries)
                    if entry.inserted_ids is not None:
                        _ids = entry.inserted_ids
                    retVal = eReturnStates.SUCCESS
                else:
                    Log_error(f"failed to insert '{entries}' into table: '{collection_name}'.")
                    retVal = eReturnStates.ERROR
            except Exception as error:
                Log_error(f"failed to insert '{entries}' into table: '{collection_name}'. Errormessage was: '{error}'")
                retVal = eReturnStates.ERROR
                _ids = None
        Log_verbose_func_end()
        return retVal, _ids

    def __get_elements_from_collection(self, database_name, collection_name, where):
        Log_verbose_func_start()
        retVal = ReturnState()
        result = None
        if self.mongodb_client == None:
            Log_error("mongodb_client was None.")
            retVal = eReturnStates.ERROR
        elif eReturnStates.EXISTS != (retVal := self.__check_if_collection_exists(database_name, collection_name)):
            Log_result_error(f"collection '{collection_name}' does not exist in mongodb database.", retVal)
            retVal = eReturnStates.ERROR
        else:
            try:
                result = self.mongodb_client[database_name][collection_name].find(where)
                retVal = eReturnStates.SUCCESS
            except Exception as error:
                Log_error(f"failed to find elements, where: '{where}' in collection: '{collection_name}' in database '{database_name}'. Errormessage was: '{error}'")
                retVal = eReturnStates.ERROR
                result = None
        Log_verbose_func_end()
        return retVal, result

    def __delete_one_from_collection(self, database_name, collection_name, where):
        Log_verbose_func_start()
        retVal = ReturnState()
        result = None
        if self.mongodb_client == None:
            Log_error("mongodb_client was None.")
            retVal = eReturnStates.ERROR
        elif eReturnStates.EXISTS != (retVal := self.__check_if_database_exists(database_name)):
            Log_result_error(f"database_name '{database_name}' does not exist.", retVal)
            retVal = eReturnStates.ERROR
        elif eReturnStates.EXISTS != (retVal := self.__check_if_collection_exists(database_name, collection_name)):
            Log_result_error(f"collection '{collection_name}' does not exist.", retVal)
            retVal = eReturnStates.ERROR
        else:
            if isinstance(where, dict):
                where = [where]
            elif not isinstance(where, list):
                Log_error(f"'where' ({where}) was neither a dict, nor a list.")
                retVal = eReturnStates.ERROR
            if eReturnStates.ERROR != retVal:
                for current_where in where:
                    try:
                        result = self.mongodb_client[database_name][collection_name].delete_one(current_where)
                        retVal = eReturnStates.SUCCESS
                    except Exception as error:
                        Log_error(f"failed to delete elements, where: '{current_where}' in collection: '{collection_name}' in database '{database_name}'. Errormessage was: '{error}'")
                        retVal = eReturnStates.ERROR
                        result = None
        Log_verbose_func_end()
        return retVal, result

    def __delete_many_from_collection(self, database_name, collection_name, where):
        Log_verbose_func_start()
        retVal = ReturnState()
        result = None
        if self.mongodb_client == None:
            Log_error("mongodb_client was None.")
            retVal = eReturnStates.ERROR
        elif eReturnStates.EXISTS != (retVal := self.__check_if_database_exists(database_name)):
            Log_result_error(f"database_name '{database_name}' does not exist.", retVal)
            retVal = eReturnStates.ERROR
        elif eReturnStates.EXISTS != (retVal := self.__check_if_collection_exists(database_name, collection_name)):
            Log_result_error(f"collection '{collection_name}' does not exist.", retVal)
            retVal = eReturnStates.ERROR
        else:
            if isinstance(where, dict):
                where = [where]
            elif not isinstance(where, list):
                Log_error(f"'where' ({where}) was neither a dict, nor a list.")
                retVal = eReturnStates.ERROR
            if eReturnStates.ERROR != retVal:
                for current_where in where:
                    try:
                        result = self.mongodb_client[database_name][collection_name].delete_many(current_where)
                        retVal = eReturnStates.SUCCESS
                    except Exception as error:
                        Log_error(f"failed to delete elements, where: '{current_where}' in collection: '{collection_name}' in database '{database_name}'. Errormessage was: '{error}'")
                        retVal = eReturnStates.ERROR
                        result = None
        Log_verbose_func_end()
        return retVal, result

    #interface
    def initialize_database(self, database_name, ignore_if_database_exists = False):
        Log_verbose_func_start()
        retVal = ReturnState()
        if eReturnStates.SUCCESS > (retVal := self.__initialize_database(database_name, ignore_if_database_exists=ignore_if_database_exists)):
            Log_result_error(f"failed to initialize database: '{database_name}'.", retVal)
        else:
            Log_verbose("initializing database was successfull.")
        Log_verbose_func_end()
        return retVal
    
    def initialize_table(self, database_name, table_names, create_database_if_necessary = False, ignore_if_database_exists = False, ignore_if_table_exists = False):
        Log_verbose_func_start()
        retVal = ReturnState()
        if eReturnStates.SUCCESS > (retVal := self.__initialize_collection(database_name, table_names, create_database_if_necessary=create_database_if_necessary, ignore_if_database_exists=ignore_if_database_exists, ignore_if_collection_exists=ignore_if_table_exists)):
            Log_result_error(f"failed to initialize table: '{table_names}'.", retVal)
        Log_verbose_func_end()
        return retVal

    def drop_database(self, database_name, ignore_if_not_exists = False):
        Log_verbose_func_start()
        retVal = ReturnState()
        if eReturnStates.SUCCESS > (retVal := self.__drop_database(database_name, ignore_if_not_exists=ignore_if_not_exists)):
            Log_result_error(f"failed to drop database: '{database_name}'.", retVal)
        Log_verbose_func_end()
        return retVal

    def drop_table(self, database_name, table_name, ignore_if_database_not_exists = False, ignore_if_table_not_exists = False):
        Log_verbose_func_start()
        retVal = ReturnState()
        if eReturnStates.SUCCESS > (retVal := self.__drop_collection(database_name, table_name, ignore_if_database_not_exists=ignore_if_database_not_exists, ignore_if_collection_not_exists=ignore_if_table_not_exists)):
            Log_result_error(f"failed to drop table: '{table_name}'.", retVal)
        Log_verbose_func_end()
        return retVal
    
    def check_if_database_exists(self, database_name):
        Log_verbose_func_start()
        retVal = ReturnState()
        if eReturnStates.ERROR == (retVal := self.__check_if_database_exists(database_name)):
            Log_result_error(f"failed to check if database '{database_name}' exists.", retVal)
        Log_verbose_func_end()
        return retVal
    
    def check_if_table_exists(self, database_name, table_name):
        Log_verbose_func_start()
        retVal = ReturnState()
        if eReturnStates.ERROR == (retVal := self.__check_if_collection_exists(database_name, table_name)):
            Log_result_error(f"failed to check if: '{table_name}' exists in database '{database_name}'.", retVal)
        Log_verbose_func_end()
        return retVal
    
    def get_database_status(self, database_name):
        Log_verbose_func_start()
        retVal = ReturnState()
        result = None
        retVal, result = self.__get_database_status(database_name)
        if eReturnStates.ERROR == retVal:
            Log_result_error(f"failed to get status for database '{database_name}'.", retVal)
        Log_verbose_func_end()
        return retVal, result
    
    def get_table_names(self, database_name):
        Log_verbose_func_start()
        retVal = ReturnState()
        result = None
        retVal, result = self.__get_collection_names(database_name)
        if eReturnStates.SUCCESS != retVal:
            Log_result_error(f"failed to get table_names for database '{database_name}'.", retVal)
            retVal = eReturnStates.ERROR
        Log_verbose_func_end()
        return retVal, result
    
    def get_database_names(self):
        Log_verbose_func_start()
        retVal = ReturnState()
        result = None
        retVal, result = self.__get_database_names()
        if eReturnStates.SUCCESS != retVal:
            Log_result_error(f"failed to get database_names.", retVal)
            retVal = eReturnStates.ERROR
        Log_verbose_func_end()
        return retVal, result
    
    def insert_into_table(self, database_name, table_name, entries, create_database_if_necessary = False, create_table_if_necessary = False):
        Log_verbose_func_start()
        retVal = ReturnState()
        _ids = None
        retVal, _ids = self.__insert_into_collection(database_name, table_name, entries, create_database_if_necessary=create_database_if_necessary, create_collection_if_necessary=create_table_if_necessary)
        if eReturnStates.SUCCESS != retVal:
            Log_result_error(f"failed to insert entries '{entries}' into table '{table_name}' in database '{database_name}'.", retVal)
            retVal = eReturnStates.ERROR
            _ids = None
        Log_verbose_func_end()
        return retVal, _ids

    def get_elements_from_table(self, database_name, table_name, where):
        Log_verbose_func_start()
        retVal = ReturnState()
        _ids = None
        retVal, _ids = self.__get_elements_from_collection(database_name, table_name, where)
        if eReturnStates.SUCCESS != retVal:
            Log_result_error(f"failed to get elements (where: '{where}').", retVal)
            _ids = None
        Log_verbose_func_end()
        return retVal, _ids

    def delete_one_from_table(self, database_name, table_name, where):
        Log_verbose_func_start()
        retVal = ReturnState()
        result = None
        retVal, result = self.__delete_one_from_collection(database_name, table_name, where)
        if eReturnStates.SUCCESS != retVal:
            Log_result_error(f"failed to delete elements (where: '{where}').", retVal)
            result = None
        Log_verbose_func_end()
        return retVal, result

    def delete_many_from_table(self, database_name, table_name, where):
        Log_verbose_func_start()
        retVal = ReturnState()
        result = None
        retVal, result = self.__delete_many_from_collection(database_name, table_name, where)
        if eReturnStates.SUCCESS != retVal:
            Log_result_error(f"failed to delete elements (where: '{where}').", retVal)
            result = None
        Log_verbose_func_end()
        return retVal, result


