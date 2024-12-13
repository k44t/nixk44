#!/bin/python3
# ******************************************************************************
# - *-coding: utf-8 -*-
# (c) copyright 2024 Alexander Poeschl
# All rights reserved.
# Secrecy Level STRICTLY CONFIDENTIAL
# ******************************************************************************
# @file test_database_module.py
# @author Alexander Poeschl <apoeschlfreelancing@kwanta.net>
# @brief Tests for the DatabaseModule.
# ******************************************************************************
from utils_python_package.src.Apoeschlutils import Fix_imports
Fix_imports()
import pytest
from utils_python_package.src.Apoeschlutils import Log_verbose, Log_error, Log_result_error, Check_test_result_and_cleanup, Check_test_result, Log_verbose_func_start, Log_verbose_func_end
from utils_python_package.src.ReturnState import ReturnState, eReturnStates
from database_module.src.database_module_main import DatabaseModule

class Test_DatabaseModule_TestMethods():
    def test_DatabaseModule_module_create(self):
        Log_verbose_func_start()
        retVal = ReturnState()
        database_module = DatabaseModule(False)
        retVal = database_module.module_create()
        assert Check_test_result(retVal)
        Log_verbose_func_end()

    def test_module_load_settings(self):
        Log_verbose_func_start()
        retVal = ReturnState()
        database_module = DatabaseModule(False)
        if eReturnStates.SUCCESS > (retVal := database_module.module_load_settings()):
            Log_result_error(f"module_load_settings for general database module failed.", retVal)
        elif eReturnStates.SUCCESS > (retVal := database_module.module_load_database_module()):
            Log_result_error(f"module_load_database_module failed.", retVal)
        elif eReturnStates.SUCCESS > (retVal := database_module.module_load_settings()):
            Log_result_error(f"module_load_settings for specific database module failed.", retVal)
        assert Check_test_result(retVal)
        Log_verbose_func_end()

    def test_module_apply_settings(self):
        Log_verbose_func_start()
        retVal = ReturnState()
        database_module = DatabaseModule(False)
        if eReturnStates.SUCCESS > (retVal := database_module.module_apply_settings()):
            Log_result_error(f"module_apply_settings for general database module failed.", retVal)
        elif eReturnStates.SUCCESS > (retVal := database_module.module_load_database_module()):
            Log_result_error(f"module_load_database_module failed.", retVal)
        elif eReturnStates.SUCCESS > (retVal := database_module.module_apply_settings()):
            Log_result_error(f"module_apply_settings for specific database module failed.", retVal)
        assert Check_test_result(retVal)
        Log_verbose_func_end()

    def test_module_load_database_module(self):
        Log_verbose_func_start()
        retVal = ReturnState()
        database_module = DatabaseModule(False)
        retVal = database_module.module_load_database_module()
        assert Check_test_result(retVal)
        Log_verbose_func_end()

    def test_module_set_used_database_module(self):
        Log_verbose_func_start()
        retVal = ReturnState()
        database_module = DatabaseModule(False)
        retVal, used_database_module = database_module.module_get_used_database_module()
        if eReturnStates.SUCCESS > retVal:
            Log_result_error(f"module_get_used_database_module failed.", retVal)
        elif eReturnStates.SUCCESS > (retVal := database_module.module_set_used_database_module(used_database_module)):
            Log_result_error(f"module_set_used_database_module failed.", retVal)
        assert Check_test_result(retVal)
        Log_verbose_func_end()

    def test_module_get_used_database_module(self):
        Log_verbose_func_start()
        retVal = ReturnState()
        database_module = DatabaseModule(False)
        retVal, used_database_module = database_module.module_get_used_database_module()
        if eReturnStates.SUCCESS > retVal:
            Log_result_error(f"test failed because module_get_used_database_module failed.", retVal)
        assert Check_test_result(retVal)
        Log_verbose_func_end()

    def test_module_reload_settings(self):
        Log_verbose_func_start()
        retVal = ReturnState()
        stt_module = DatabaseModule()
        if eReturnStates.SUCCESS > (retVal := stt_module.module_reload_settings()):
            Log_result_error(f"test failed because module_reload_settings failed.", retVal)
        assert Check_test_result(retVal)
        Log_verbose_func_end()

    def test_module_get_settings(self):
        Log_verbose_func_start()
        retVal = ReturnState()
        database_module = DatabaseModule(False)
        retVal, first_result = database_module.module_get_settings()
        first_result_str = str(first_result)
        if eReturnStates.SUCCESS > retVal:
            Log_result_error(f"test failed because module_get_settings for general database module failed.", retVal)
        elif eReturnStates.SUCCESS > (retVal := database_module.module_load_database_module()):
            Log_result_error(f"module_load_database_module module failed.", retVal)
        else:
            retVal, second_result = database_module.module_get_settings()
        if eReturnStates.SUCCESS > retVal:
            Log_result_error(f"test failed because module_get_settings for specific database module failed.", retVal)
        if first_result_str == str(second_result):
            Log_error(f"it seems that the specific module was not loaded properly, because the settings for general module and the settings for specific module were the same. first_result was: '{first_result}' and second_result was: '{second_result}'")
            retVal = eReturnStates.ERROR
        assert Check_test_result(retVal)
        Log_verbose_func_end()

    #interface from outside to submodule
    def test_initialize_database(self):
        Log_verbose_func_start()
        retVal = ReturnState()
        cleanup = ReturnState()
        database_module = DatabaseModule()
        test_database_name = "test_database_name"
        if eReturnStates.SUCCESS != (retVal := database_module.initialize_database(test_database_name)):
            Log_result_error(f"test failed.", retVal)
        elif eReturnStates.EXISTS != (retVal := database_module.check_if_database_exists(test_database_name)):
            Log_result_error(f"test failed because database was not found.", retVal)
        else:
            retVal = eReturnStates.SUCCESS
        if eReturnStates.SUCCESS != (cleanup := self.cleanup_database(test_database_name)):
            Log_error("cleanup of database after test failed.")
        else:
            Log_verbose("cleaned up database after test.")
        assert Check_test_result_and_cleanup(retVal, cleanup)
        Log_verbose_func_end()
        
    def test_initialize_database_failed(self):
        Log_verbose_func_start()
        retVal = ReturnState()
        database_module = DatabaseModule()
        test_database_name = 1
        if eReturnStates.ERROR != (retVal := database_module.initialize_database(test_database_name)):
            Log_result_error(f"test failed.", retVal)
        else:
            retVal = eReturnStates.SUCCESS
        assert Check_test_result(retVal)
        Log_verbose_func_end()

    def test_initialize_table(self):
        Log_verbose_func_start()
        retVal = ReturnState()
        cleanup = ReturnState()
        database_module = DatabaseModule()
        test_database_name = "test_database_name"
        test_table_name = "test_table"
        if eReturnStates.SUCCESS != (retVal := database_module.initialize_database(test_database_name)):
            Log_result_error(f"test failed because initialize_database failed.", retVal)
        elif eReturnStates.SUCCESS != (retVal := database_module.initialize_table(test_database_name, test_table_name)):
            Log_result_error(f"initialize_table failed.", retVal)
        elif eReturnStates.EXISTS != (retVal := database_module.check_if_table_exists(test_database_name, test_table_name)):
            Log_result_error(f"could not find'{test_table_name}'in database. It seems that initializing the table had failed.", retVal)
        else:
            retVal = eReturnStates.SUCCESS
        if eReturnStates.SUCCESS != (cleanup := self.cleanup_database(test_database_name)):
            Log_error("cleanup of database after test failed.")
        else:
            Log_verbose("cleaned up database after test.")
        assert Check_test_result_and_cleanup(retVal, cleanup)
        Log_verbose_func_end()

    def test_initialize_table_failed(self):
        Log_verbose_func_start()
        retVal = ReturnState()
        cleanup = ReturnState()
        database_module = DatabaseModule()
        test_database_name = "test_database_name"
        test_table_name = 1
        if eReturnStates.SUCCESS != (retVal := database_module.initialize_database(test_database_name)):
            Log_result_error(f"test failed because initialize_database failed.", retVal)
        elif eReturnStates.ERROR != (retVal := database_module.initialize_table(test_database_name, test_table_name)):
            Log_result_error(f"initialize_table failed.", retVal)
        else:
            retVal = eReturnStates.SUCCESS
        if eReturnStates.SUCCESS != (cleanup := self.cleanup_database(test_database_name)):
            Log_error("cleanup of database after test failed.")
        else:
            Log_verbose("cleaned up database after test.")
        assert Check_test_result_and_cleanup(retVal, cleanup)
        Log_verbose_func_end()

    def test_drop_database(self):
        Log_verbose_func_start()
        retVal = ReturnState()
        cleanup = ReturnState()
        database_module = DatabaseModule()
        test_database_name = "test_database_name"
        if eReturnStates.SUCCESS != (retVal := database_module.initialize_database(test_database_name)):
            Log_result_error(f"initialize_database failed.", retVal)
        elif eReturnStates.SUCCESS != (retVal := database_module.drop_database(test_database_name)):
            Log_result_error(f"test failed because drop_database failed.", retVal)
        elif eReturnStates.EXISTS_NOT != (retVal := database_module.check_if_database_exists(test_database_name)):
            Log_result_error(f"test failed because database was not found.", retVal)
            retVal = eReturnStates.ERROR
        else:
            retVal = eReturnStates.SUCCESS
        if eReturnStates.SUCCESS != (cleanup := self.cleanup_database(test_database_name)):
            Log_error("cleanup of database after test failed.")
        else:
            Log_verbose("cleaned up database after test.")
        assert Check_test_result_and_cleanup(retVal, cleanup)
        Log_verbose_func_end()

    def test_drop_table(self):
        Log_verbose_func_start()
        retVal = ReturnState()
        cleanup = ReturnState()
        database_module = DatabaseModule()
        test_database_name = "test_database_name"
        test_table_name = "test_table_name"
        if eReturnStates.SUCCESS != (retVal := database_module.initialize_table(test_database_name, test_table_name, create_database_if_necessary=True)):
            Log_result_error(f"initialize_table failed.", retVal)
        elif eReturnStates.SUCCESS != (retVal := database_module.drop_table(test_database_name, test_table_name)):
            Log_result_error(f"test failed because drop_table failed.", retVal)
        elif eReturnStates.EXISTS_NOT != (retVal := database_module.check_if_table_exists(test_database_name, test_table_name)):
            Log_result_error(f"could still find'{test_table_name}'in database. It seems that cleaning up (dropping the table) after the test had failed.", retVal)
            retVal = eReturnStates.ERROR
        else:
            retVal = eReturnStates.SUCCESS
        if eReturnStates.SUCCESS != (cleanup := self.cleanup_database(test_database_name)):
            Log_error("cleanup of database after test failed.")
        else:
            Log_verbose("cleaned up database after test.")
        assert Check_test_result_and_cleanup(retVal, cleanup)
        Log_verbose_func_end()
        
    def test_check_if_database_exists(self):
        Log_verbose_func_start()
        retVal = ReturnState()
        cleanup = ReturnState()
        database_module = DatabaseModule()
        test_database_name = "test_database_name"
        if eReturnStates.SUCCESS != (retVal := database_module.initialize_database(test_database_name)):
            Log_result_error(f"could not initialize database.", retVal)
        elif eReturnStates.EXISTS != (retVal := database_module.check_if_database_exists(test_database_name)):
            Log_result_error(f"test failed. check_if_database_exists did not answer correctly.", retVal)
            retVal = eReturnStates.ERROR
        elif eReturnStates.SUCCESS != (retVal := database_module.drop_database(test_database_name)):
            Log_result_error(f"drop_database failed.", retVal)
        elif eReturnStates.EXISTS_NOT != (retVal := database_module.check_if_database_exists(test_database_name)):
            Log_result_error(f"test failed. check_if_database_exists did not answer correctly.", retVal)
            retVal = eReturnStates.ERROR
        else:
            retVal = eReturnStates.SUCCESS
        if eReturnStates.SUCCESS != (cleanup := self.cleanup_database(test_database_name)):
            Log_error("cleanup of database after test failed.")
        else:
            Log_verbose("cleaned up database after test.")
        assert Check_test_result_and_cleanup(retVal, cleanup)
        Log_verbose_func_end()


    def test_check_if_table_exists(self):
        Log_verbose_func_start()
        retVal = ReturnState()
        cleanup = ReturnState()
        database_module = DatabaseModule()
        test_database_name = "test_database_name"
        test_table_name = "test_table_name"
        if eReturnStates.SUCCESS != (retVal := database_module.initialize_table(test_database_name, test_table_name, create_database_if_necessary=True)):
            Log_result_error(f"could not initialize database.", retVal)
        elif eReturnStates.EXISTS != (retVal := database_module.check_if_table_exists(test_database_name, test_table_name)):
            Log_result_error(f"test failed. check_if_table_exists did not answer correctly.", retVal)
            retVal = eReturnStates.ERROR
        elif eReturnStates.SUCCESS != (retVal := database_module.drop_table(test_database_name, test_table_name)):
            Log_result_error(f"drop_database failed.", retVal)
        elif eReturnStates.EXISTS_NOT != (retVal := database_module.check_if_table_exists(test_database_name, test_table_name)):
            Log_result_error(f"test failed. check_if_table_exists did not answer correctly.", retVal)
            retVal = eReturnStates.ERROR
        else:
            retVal = eReturnStates.SUCCESS
        if eReturnStates.SUCCESS != (cleanup := self.cleanup_database(test_database_name)):
            Log_error("cleanup of database after test failed.")
        else:
            Log_verbose("cleaned up database after test.")
        assert Check_test_result_and_cleanup(retVal, cleanup)
        Log_verbose_func_end()

    def test_get_database_status(self):
        Log_verbose_func_start()
        retVal = ReturnState()
        cleanup = ReturnState()
        database_module = DatabaseModule()
        test_database_name = "test_database_name"
        if eReturnStates.SUCCESS != (retVal := database_module.initialize_database(test_database_name)):
            Log_result_error(f"initialize_database failed.", retVal)
        else:
            retVal, result = database_module.get_database_status(test_database_name)
        if eReturnStates.SUCCESS != retVal:
            Log_result_error(f"test failed because get_database_status failed.", retVal)
        elif result == None:
            Log_result_error(f"test failed because result was None.", retVal)
            retVal = eReturnStates.ERROR
        else:
            retVal = eReturnStates.SUCCESS
        if eReturnStates.SUCCESS != (cleanup := self.cleanup_database(test_database_name)):
            Log_error("cleanup of database after test failed.")
        else:
            Log_verbose("cleaned up database after test.")
        assert Check_test_result_and_cleanup(retVal, cleanup)
        Log_verbose_func_end()
        
    def test_get_table_names(self):
        Log_verbose_func_start()
        retVal = ReturnState()
        cleanup = ReturnState()
        database_module = DatabaseModule()
        test_database_name = "test_database_name"
        test_table_names = ["test_table_name_1", "test_table_name_2", "test_table_name_3"]
        if eReturnStates.SUCCESS != (cleanup := self.cleanup_database(test_database_name)):
            Log_error("cleanup of database after test failed.")
            retVal = eReturnStates.ERROR
        else:
            retVal = eReturnStates.CONTINUE
        if eReturnStates.CONTINUE == retVal:
            if eReturnStates.SUCCESS != (retVal := database_module.initialize_table(test_database_name, test_table_names, create_database_if_necessary=True)):
                Log_result_error(f"could not initialize database.", retVal)
            else:
                retVal, result = database_module.get_table_names(test_database_name)
            if eReturnStates.SUCCESS != retVal:
                Log_result_error(f"get_table_names failed.", retVal)
            else:
                for test_table_name in test_table_names:
                    if test_table_name not in result:
                        Log_error("test failed because get_table_names gave wrong answer.")
                        retVal = eReturnStates.ERROR
                        break
                    else:
                        retVal = eReturnStates.SUCCESS
        if eReturnStates.SUCCESS != (cleanup := self.cleanup_database(test_database_name)):
            Log_error("cleanup of database after test failed.")
        else:
            Log_verbose("cleaned up database after test.")
        assert Check_test_result_and_cleanup(retVal, cleanup)
        Log_verbose_func_end()

    def test_get_database_names(self):
        Log_verbose_func_start()
        retVal = ReturnState()
        cleanup = ReturnState()
        database_module = DatabaseModule()
        test_database_name = ["test_database_name1", "test_database_name2", "test_database_name3"]
        if eReturnStates.SUCCESS != (retVal := database_module.initialize_database(test_database_name)):
            Log_result_error(f"could not initialize database.", retVal)
        else:
            retVal, result = database_module.get_database_names()
        if eReturnStates.SUCCESS != retVal:
            Log_result_error(f"get_database_names failed.", retVal)
        else:
            if None == result:
                Log_error("test failed because get_database_names gave wrong answer.")
                retVal = eReturnStates.ERROR
            else:
                retVal = eReturnStates.SUCCESS
        if eReturnStates.SUCCESS != (cleanup := self.cleanup_database(test_database_name)):
            Log_error("cleanup of database after test failed.")
        else:
            Log_verbose("cleaned up database after test.")
        assert Check_test_result_and_cleanup(retVal, cleanup)
        Log_verbose_func_end()

    def test_insert_singleentry_into_table(self):
        Log_verbose_func_start()
        retVal = ReturnState()
        cleanup = ReturnState()
        database_module = DatabaseModule()
        test_database_name = "test_database_name"
        test_table_name = "test_table_name"
        test_key_1 = "name"
        test_key_2 = "adresse"
        test_value_1 = "ein_name"
        test_value_2 = "eine_adresse"
        test_dictionary = dict()
        test_dictionary[test_key_1] = test_value_1
        test_dictionary[test_key_2] = test_value_2
        where_dictionary = dict()
        where_dictionary[test_key_1] = test_value_1
        retVal, _id = database_module.insert_into_table(test_database_name, test_table_name, test_dictionary, create_database_if_necessary=True, create_table_if_necessary=True)
        if eReturnStates.SUCCESS != retVal:
            Log_result_error(f"test failed because insert_into_table failed.", retVal)
        elif _id == None:
            Log_error("test failed because returned _id was None.")
            retVal = eReturnStates.ERROR
        else:
            retVal, results = database_module.get_elements_from_table(test_database_name, test_table_name, where_dictionary)
            for result in results:
                if result[test_key_1] != test_dictionary[test_key_1]:
                    retVal = eReturnStates.ERROR
                    break
                if result[test_key_2] != test_dictionary[test_key_2]:
                    retVal = eReturnStates.ERROR
                    break
        if eReturnStates.SUCCESS != (cleanup := self.cleanup_database(test_database_name)):
            Log_error("cleanup of database after test failed.")
        else:
            Log_verbose("cleaned up database after test.")
        assert Check_test_result_and_cleanup(retVal, cleanup)
        Log_verbose_func_end()

    def test_insert_multientries_into_table(self):
        Log_verbose_func_start()
        retVal = ReturnState()
        cleanup = ReturnState()
        database_module = DatabaseModule()
        test_database_name = "test_database_name"
        test_table_name = "test_table_name"
        test_key_1 = "name"
        test_key_2 = "adresse"
        test_value_1 = "ein_name"
        test_value_2 = "eine_adresse"
        test_value_3 = "ein_anderer_name"
        test_value_4 = "eine_andere_adresse"
        test_dictionary1 = dict()
        test_dictionary1[test_key_1] = test_value_1
        test_dictionary1[test_key_2] = test_value_2
        test_dictionary2 = dict()
        test_dictionary2[test_key_1] = test_value_3
        test_dictionary2[test_key_2] = test_value_4
        test_list = [test_dictionary1, test_dictionary2]
        where_dictionary = dict()
        where_dictionary[test_key_1] = test_value_3
        retVal, _id = database_module.insert_into_table(test_database_name, test_table_name, test_list, create_database_if_necessary=True, create_table_if_necessary=True)
        if eReturnStates.SUCCESS != retVal:
            Log_result_error(f"test failed because insert_into_table failed.", retVal)
        elif _id == None:
            Log_error("test failed because returned _id was None.")
            retVal = eReturnStates.ERROR
        else:
            retVal, results = database_module.get_elements_from_table(test_database_name, test_table_name, where_dictionary)
            for result in results:
                if result[test_key_1] != test_dictionary2[test_key_1]:
                    retVal = eReturnStates.ERROR
                    Log_error(f"test failed because test_key_1 was not in database.")
                    break
                if result[test_key_2] != test_dictionary2[test_key_2]:
                    retVal = eReturnStates.ERROR
                    Log_error(f"test failed because test_key_2 was not in database.")
                    break
        if eReturnStates.SUCCESS != (cleanup := self.cleanup_database(test_database_name)):
            Log_error("cleanup of database after test failed.")
        else:
            Log_verbose("cleaned up database after test.")
        assert Check_test_result_and_cleanup(retVal, cleanup)
        Log_verbose_func_end()

    def test_get_elements_from_table(self):
        Log_verbose_func_start()
        retVal = ReturnState()
        cleanup = ReturnState()
        database_module = DatabaseModule()
        test_database_name = "test_database_name"
        test_table_name = "test_table_name"
        test_key_1 = "name"
        test_key_2 = "adresse"
        test_value_1 = "ein_name"
        test_value_2 = "eine_adresse"
        test_value_3 = "ein_anderer_name"
        test_value_4 = "eine_andere_adresse"
        test_dictionary1 = dict()
        test_dictionary1[test_key_1] = test_value_1
        test_dictionary1[test_key_2] = test_value_2
        test_dictionary2 = dict()
        test_dictionary2[test_key_1] = test_value_3
        test_dictionary2[test_key_2] = test_value_4
        test_list = [test_dictionary1, test_dictionary2]
        where_dictionary = dict()
        where_dictionary[test_key_1] = test_value_3
        retVal, _id = database_module.insert_into_table(test_database_name, test_table_name, test_list, create_database_if_necessary=True, create_table_if_necessary=True)
        if eReturnStates.SUCCESS != retVal:
            Log_result_error(f"test failed because insert_into_table failed.", retVal)
        elif _id == None:
            Log_error("test failed because returned _id was None.")
            retVal = eReturnStates.ERROR
        else:
            retVal, results = database_module.get_elements_from_table(test_database_name, test_table_name, where_dictionary)
            for result in results:
                if result[test_key_1] != test_dictionary2[test_key_1]:
                    retVal = eReturnStates.ERROR
                    Log_error(f"test failed because test_key_1 was not in database.")
                    break
                if result[test_key_2] != test_dictionary2[test_key_2]:
                    retVal = eReturnStates.ERROR
                    Log_error(f"test failed because test_key_2 was not in database.")
                    break
        if eReturnStates.SUCCESS != (cleanup := self.cleanup_database(test_database_name)):
            Log_error("cleanup of database after test failed.")
        else:
            Log_verbose("cleaned up database after test.")
        assert Check_test_result_and_cleanup(retVal, cleanup)
        Log_verbose_func_end()

    def test_delete_one_from_table(self):
        Log_verbose_func_start()
        retVal = ReturnState()
        cleanup = ReturnState()
        database_module = DatabaseModule()
        test_database_name = "test_database_name"
        test_table_name = "test_table_name"
        test_key_1 = "name"
        test_key_2 = "adresse"
        test_value_1 = "ein_name"
        test_value_2 = "eine_adresse"
        test_value_3 = "ein_anderer_name"
        test_value_4 = "eine_andere_adresse"
        test_dictionary1 = dict()
        test_dictionary1[test_key_1] = test_value_1
        test_dictionary1[test_key_2] = test_value_2
        test_dictionary2 = dict()
        test_dictionary2[test_key_1] = test_value_3
        test_dictionary2[test_key_2] = test_value_4
        test_list = [test_dictionary1, test_dictionary2]
        where_dictionary = dict()
        where_dictionary[test_key_1] = test_value_3
        retVal, _id = database_module.insert_into_table(test_database_name, test_table_name, test_list, create_database_if_necessary=True, create_table_if_necessary=True)
        if eReturnStates.SUCCESS != retVal:
            Log_result_error(f"insert_into_table failed.", retVal)
        elif _id == None:
            Log_error("returned _id was None.")
            retVal = eReturnStates.ERROR
        else:
            retVal, results = database_module.get_elements_from_table(test_database_name, test_table_name, where_dictionary)
            for result in results:
                if result[test_key_1] != test_dictionary2[test_key_1]:
                    retVal = eReturnStates.ERROR
                    Log_error(f"test_key_1 was not in database.")
                    break
                if result[test_key_2] != test_dictionary2[test_key_2]:
                    retVal = eReturnStates.ERROR
                    Log_error(f"test_key_2 was not in database.")
                    break
        retVal, delete_acknowledge = database_module.delete_one_from_table(test_database_name, test_table_name, where_dictionary)
        if eReturnStates.SUCCESS != retVal:
            Log_result_error(f"test failed because delete_one_from_table failed.", retVal)
        elif delete_acknowledge.deleted_count == 0:
            Log_error("delete_acknowledge.deleted_count was zero")
            retVal = eReturnStates.ERROR
        else:
            retVal, results = database_module.get_elements_from_table(test_database_name, test_table_name, where_dictionary)
            for result in results:
                if result[test_key_1] == test_dictionary2[test_key_1]:
                    retVal = eReturnStates.ERROR
                    Log_error(f"test failed because test_key_1 was still in database.")
                    break
                if result[test_key_2] == test_dictionary2[test_key_2]:
                    retVal = eReturnStates.ERROR
                    Log_error(f"test failed because test_key_2 was still in database.")
                    break
        if eReturnStates.SUCCESS != (cleanup := self.cleanup_database(test_database_name)):
            Log_error("cleanup of database after test failed.")
        else:
            Log_verbose("cleaned up database after test.")
        assert Check_test_result_and_cleanup(retVal, cleanup)
        Log_verbose_func_end()

    def test_delete_many_from_table(self):
        Log_verbose_func_start()
        retVal = ReturnState()
        cleanup = ReturnState()
        database_module = DatabaseModule()
        test_database_name = "test_database_name"
        test_table_name = "test_table_name"
        test_key_1 = "name"
        test_key_2 = "adresse"
        test_value_1 = "ein_name"
        test_value_2 = "selbe_adresse"
        test_value_3 = "ein_anderer_name"
        test_value_4 = "selbe_adresse"
        test_dictionary1 = dict()
        test_dictionary1[test_key_1] = test_value_1
        test_dictionary1[test_key_2] = test_value_2
        test_dictionary2 = dict()
        test_dictionary2[test_key_1] = test_value_3
        test_dictionary2[test_key_2] = test_value_4
        test_list = [test_dictionary1, test_dictionary2]
        where_dictionary = dict()
        where_dictionary[test_key_2] = {"$regex": "[" + test_value_2 + "]"}
        retVal, _id = database_module.insert_into_table(test_database_name, test_table_name, test_list, create_database_if_necessary=True, create_table_if_necessary=True)
        if eReturnStates.SUCCESS != retVal:
            Log_result_error(f"insert_into_table failed.", retVal)
        elif _id == None:
            Log_error("returned _id was None.")
            retVal = eReturnStates.ERROR
        else:
            retVal, results = database_module.get_elements_from_table(test_database_name, test_table_name, where_dictionary)
            for result in results:
                if result[test_key_1] != test_dictionary2[test_key_1]:
                    retVal = eReturnStates.ERROR
                    Log_error(f"test_key_1 was not in database.")
                    break
                if result[test_key_2] != test_dictionary2[test_key_2]:
                    retVal = eReturnStates.ERROR
                    Log_error(f"test_key_2 was not in database.")
                    break
        retVal, delete_acknowledge = database_module.delete_many_from_table(test_database_name, test_table_name, where_dictionary)
        if eReturnStates.SUCCESS != retVal:
            Log_result_error(f"test failed because delete_many_from_table failed.", retVal)
        elif delete_acknowledge.deleted_count == 0:
            Log_error("delete_acknowledge.deleted_count was zero")
            retVal = eReturnStates.ERROR
        else:
            retVal, results = database_module.get_elements_from_table(test_database_name, test_table_name, where_dictionary)
            for result in results:
                if result[test_key_1] == test_dictionary2[test_key_1]:
                    retVal = eReturnStates.ERROR
                    Log_error(f"test failed because test_key_1 still not in database.")
                    break
                if result[test_key_2] == test_dictionary2[test_key_2]:
                    retVal = eReturnStates.ERROR
                    Log_error(f"test failed because test_key_2 still not in database.")
                    break
        if eReturnStates.SUCCESS != (cleanup := self.cleanup_database(test_database_name)):
            Log_error("cleanup of database after test failed.")
        else:
            Log_verbose("cleaned up database after test.")
        assert Check_test_result_and_cleanup(retVal, cleanup)
        Log_verbose_func_end()

    def test_backup_database(self):
        Log_verbose_func_start()
        retVal = ReturnState()
        database_module = DatabaseModule()
        retVal, backup_path = database_module.backup_database(is_test=True)
        if eReturnStates.SUCCESS != retVal:
            Log_result_error(f"test failed because backup_database failed.", retVal)
        assert Check_test_result(retVal)
        Log_verbose_func_end()

    def test_drop_complete_database(self):
        Log_verbose_func_start()
        retVal = ReturnState()
        cleanup = ReturnState()
        database_module = DatabaseModule()
        retVal, backup_path = database_module.backup_database(is_test=True)
        if eReturnStates.SUCCESS != retVal:
            Log_result_error(f"failed to backup database.", retVal)
        else:
            retVal = database_module.drop_complete_database()
            if eReturnStates.SUCCESS != retVal:
                Log_result_error(f"test failed because drop_complete_database failed.", retVal)
        cleanup = database_module.restore_backup_in_database(backup_path)
        if eReturnStates.SUCCESS != cleanup:
            Log_error(f"restore_backup_in_database failed. cleanup was: '{cleanup}'")
        assert Check_test_result_and_cleanup(retVal, cleanup)
        Log_verbose_func_end()

    def test_restore_backup_in_database(self):
        Log_verbose_func_start()
        retVal = ReturnState()
        database_module = DatabaseModule()
        retVal, backup_path = database_module.backup_database(is_test=True)
        if eReturnStates.SUCCESS != retVal:
            Log_result_error(f"failed to backup database.", retVal)
        else:
            retVal = database_module.restore_backup_in_database(backup_path)
            if eReturnStates.SUCCESS != retVal:
                Log_result_error(f"test failed because restore_backup_in_database failed.", retVal)
        assert Check_test_result(retVal)
        Log_verbose_func_end()

    def test_restore_latest_backup_in_database(self):
        Log_verbose_func_start()
        retVal = ReturnState()
        database_module = DatabaseModule()
        retVal = database_module.restore_latest_backup_in_database()
        if eReturnStates.SUCCESS != retVal:
            Log_result_error(f"test failed because restore_latest_backup_in_database failed.", retVal)
        assert Check_test_result(retVal)
        Log_verbose_func_end()

    #test cleanup helpers
    @pytest.mark.skip(reason="we only do this manually. if you need this, uncomment it.")
    def test_take_backup(self):
        database_module = DatabaseModule()
        retVal = database_module.backup_database()

    @pytest.mark.skip(reason="we only do this manually. if you need this, uncomment it.")
    def test_restore_latest_backup_in_database_without_drop(self):
        database_module = DatabaseModule()
        retVal = database_module.restore_latest_backup_in_database(dont_drop_database=False)

    @pytest.mark.skip(reason="we only do this manually. if you need this, uncomment it.")
    def test_cleanup_database(self):
        self.cleanup_database("test_database_name")

    def cleanup_database(self, test_database_names):
        Log_verbose_func_start()
        retVal = ReturnState()
        database_module = DatabaseModule()
        if isinstance(test_database_names,str):
            retVal = database_module.drop_database(test_database_names, ignore_if_not_exists=True)
        elif isinstance(test_database_names, list):
            for test_database_name in test_database_names:
                if isinstance(test_database_name, str):
                    retVal = database_module.drop_database(test_database_name, ignore_if_not_exists=True)
                if eReturnStates.SUCCESS != retVal:
                    Log_result_error(f"cleanup drop_database failed.", retVal)
                    assert Check_test_result(retVal)
                retVal = database_module.check_if_database_exists(test_database_name)
                if eReturnStates.EXISTS_NOT != retVal:
                    Log_result_error(f"cleanup failed because database still exists.", retVal)
                    assert Check_test_result(retVal)
                else:
                    retVal = eReturnStates.SUCCESS
        assert Check_test_result(retVal)
        Log_verbose_func_end()
        return retVal




if __name__ == '__main__':
    pytest.main()