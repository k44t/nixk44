#!/bin/python3
# ******************************************************************************
# - *-coding: utf-8 -*-
# (c) copyright 2024 Alexander Poeschl
# All rights reserved.
# Secrecy Level STRICTLY CONFIDENTIAL
# ******************************************************************************
# @file test_general_module_module.py
# @author Alexander Poeschl <apoeschlfreelancing@kwanta.net>
# @brief Tests for the GeneralModule-Module.
# ******************************************************************************
from utils_python_package.src.Apoeschlutils import Fix_imports
Fix_imports()
from utils_python_package.src.Apoeschlutils import Log_error, Log_verbose, Log_result_error, Check_test_result_and_cleanup, Check_test_result, Log_verbose_func_start, Log_verbose_func_end
from utils_python_package.src.ReturnState import ReturnState, eReturnStates
from utils_python_package.general_module.tests.derived_module.src.derived_module_main import DerivedModule
from database_module.src.database_module_main import DatabaseModule
import pytest

    


class Test_GeneralModule_TestMethods():
    def test_module_create(self):
        Log_verbose_func_start()
        retVal = ReturnState()
        derived_module = DerivedModule(create_only = True)
        retVal = derived_module.module_create()
        assert Check_test_result(retVal)
        Log_verbose_func_end()

    def test_module_load_or_initialize(self):
        Log_verbose_func_start()
        retVal = ReturnState()
        derived_module = DerivedModule(create_only = True)
        retVal = derived_module.module_load_or_initialize()
        assert Check_test_result(retVal)
        Log_verbose_func_end()

    def test_module_get_initial_settings(self):
        Log_verbose_func_start()
        retVal = ReturnState()
        derived_module = DerivedModule()
        retVal, derived_module_initial_settings = derived_module.module_get_initial_settings()
        if eReturnStates.SUCCESS != retVal:
            Log_result_error(f"get_settings failed.", retVal)
            assert Check_test_result(retVal)
        elif None == derived_module_initial_settings:
            Log_error(f"test failed. derived_module_settings were None.")
            retVal = eReturnStates.ERROR
        assert Check_test_result(retVal)
        Log_verbose_func_end()

    def test_module_load_settings(self):
        Log_verbose_func_start()
        retVal = ReturnState()
        derived_module = DerivedModule(create_only = True)
        retVal = derived_module.module_load_settings()
        assert Check_test_result(retVal)
        Log_verbose_func_end()

    def test_module_get_settings(self):
        Log_verbose_func_start()
        retVal = ReturnState()
        derived_module = DerivedModule()
        retVal, derived_module_settings = derived_module.module_get_settings()
        if eReturnStates.SUCCESS != retVal:
            Log_result_error(f"get_settings failed.", retVal)
        elif None == derived_module_settings:
            Log_error(f"test failed. derived_module_settings were None.")
            retVal = eReturnStates.ERROR
        assert Check_test_result(retVal)
        Log_verbose_func_end()

    def test_reload_settings(self):
        Log_verbose_func_start()
        retVal = ReturnState()
        derived_module = DerivedModule(create_only=True)
        if eReturnStates.SUCCESS > (retVal := derived_module.module_reload_settings()):
            Log_result_error(f"reload_settings failed.", retVal)
        assert Check_test_result(retVal)
        Log_verbose_func_end()

    def test_derived_module_store_settings_in_database(self):
        Log_verbose_func_start()
        retVal = ReturnState()
        cleanup = ReturnState()
        derived_module = DerivedModule()
        database_module = DatabaseModule()
        retVal, database_backup_path = database_module.backup_database(is_test=True)
        if eReturnStates.SUCCESS != retVal:
            Log_result_error("backup_database failed.", retVal)
        else:
            retVal = database_module.drop_complete_database()
        if eReturnStates.SUCCESS != retVal:
            Log_result_error("drop_complete_database failed.", retVal)
        else:
            retVal, initial_settings = derived_module.module_get_initial_settings()
        if eReturnStates.SUCCESS != retVal:
            Log_result_error("failed to get initial settings from derived_module.", retVal)
        elif eReturnStates.SUCCESS != (retVal := derived_module.module_store_settings_in_database(initial_settings=True)):
            Log_result_error("test failed because store_settings_in_database failed.", retVal)
        else:
            retVal = eReturnStates.CONTINUE
        if eReturnStates.CONTINUE == retVal:
            retVal, stored_settings = derived_module.module_get_settings_from_database(settings_topic_arg="DerivedModule")
        if eReturnStates.SUCCESS != retVal:
            Log_result_error("getting the settings to test them if they got stored correctly failed.", retVal)
        elif None == stored_settings:
            Log_error("retreived stored_settings were None.")
            retVal = eReturnStates.ERROR
        else:
            retVal = eReturnStates.CONTINUE
        if eReturnStates.CONTINUE == retVal:
            for key, value in stored_settings.items():
                if key == "_id":
                    continue
                elif stored_settings[key] != initial_settings[key]:
                    Log_error(f"retreived setting for key '{key}' was not the same as initial setting.")
                    retVal = eReturnStates.ERROR
                    break
                else:
                    retVal = eReturnStates.SUCCESS
        if eReturnStates.SUCCESS != retVal:
            Log_error("test failed because the retreived stored settings were not the same as the settings that were stored into the database")
        if eReturnStates.SUCCESS != (cleanup := database_module.restore_backup_in_database(database_backup_path)):
            Log_error("restore_backup_in_database failed")
        assert Check_test_result_and_cleanup(retVal, cleanup)
        Log_verbose_func_end()

    def test_remove_settings_from_database(self):
        Log_verbose_func_start()
        retVal = ReturnState()
        cleanup = ReturnState()
        derived_module = DerivedModule()
        database_module = DatabaseModule()
        retVal, database_backup_path = database_module.backup_database(is_test=True)
        if eReturnStates.SUCCESS != retVal:
            Log_result_error("backup_database failed.", retVal)
        else:
            retVal = database_module.drop_complete_database()
        if eReturnStates.SUCCESS != retVal:
            Log_result_error("drop_complete_database failed.", retVal)
        else:
            retVal, initial_settings = derived_module.module_get_initial_settings()
        if eReturnStates.SUCCESS != retVal:
            Log_result_error("failed to get initial settings from derived_module.", retVal)
        elif eReturnStates.SUCCESS != (retVal := derived_module.module_store_settings_in_database(initial_settings=True)):
            Log_result_error("test failed because store_settings_in_database failed.", retVal)
        else:
            retVal = eReturnStates.CONTINUE
        if eReturnStates.CONTINUE == retVal:
            retVal, stored_settings = derived_module.module_get_settings_from_database()
        if eReturnStates.SUCCESS != retVal:
            Log_result_error("test failed because getting the settings to test them if they got stored correctly failed.", retVal)
        elif None == stored_settings:
            Log_error("test failed because the retreived stored_settings were None.")
            retVal = eReturnStates.ERROR
        else:
            retVal = eReturnStates.CONTINUE
        if eReturnStates.CONTINUE == retVal:
            for key, value in stored_settings.items():
                if key == "_id":
                    continue
                elif stored_settings[key] != initial_settings[key]:
                    Log_error(f"retreived setting for key '{key}' was not the same as initial setting.")
                    retVal = eReturnStates.ERROR
                    break
                else:
                    retVal = eReturnStates.CONTINUE
        if eReturnStates.CONTINUE != retVal:
            Log_error("test failed because the retreived stored settings were not the same as the settings that were stored into the database")
        elif eReturnStates.SUCCESS != (retVal := derived_module.module_remove_settings_from_database()):
            Log_result_error("test failed because remove_settings_from_database for current settings failed.", retVal)
        else:
            retVal = eReturnStates.CONTINUE
        if eReturnStates.CONTINUE == retVal:
            retVal, stored_settings = derived_module.module_get_settings_from_database()
        if eReturnStates.ERROR != retVal:
            Log_result_error("test failed, because getting the settings to test them if they got removed correctly did not result in ERROR.", retVal)
        elif None == stored_settings:
            retVal = eReturnStates.SUCCESS
        if eReturnStates.SUCCESS != retVal:
            Log_result_error("test failed because the retreived stored settings were still the same as the settings that were stored into the database.", retVal)
        if eReturnStates.SUCCESS != (cleanup := database_module.restore_backup_in_database(database_backup_path)):
            Log_error("restore_backup_in_database failed")
        assert Check_test_result_and_cleanup(retVal, cleanup)
        Log_verbose_func_end()

    def test_get_settings_from_database(self):
        Log_verbose_func_start()
        retVal = ReturnState()
        cleanup = ReturnState()
        derived_module = DerivedModule()
        database_module = DatabaseModule()
        retVal, database_backup_path = database_module.backup_database(is_test=True)
        if eReturnStates.SUCCESS != retVal:
            Log_result_error("backup_database failed.", retVal)
        else:
            retVal = database_module.drop_complete_database()
        if eReturnStates.SUCCESS != retVal:
            Log_result_error("drop_complete_database failed.", retVal)
        else:
            retVal, initial_settings = derived_module.module_get_initial_settings()
        if eReturnStates.SUCCESS != retVal:
            Log_result_error("failed to get initial settings from derived_module.", retVal)
        elif eReturnStates.SUCCESS != (retVal := derived_module.module_store_settings_in_database(initial_settings=True)):
            Log_result_error("store_settings_in_database failed.", retVal)
        else:
            retVal = eReturnStates.CONTINUE
        if eReturnStates.CONTINUE == retVal:
            retVal, stored_settings = derived_module.module_get_settings_from_database()
        if eReturnStates.SUCCESS != retVal:
            Log_result_error("test failed because getting the settings to test them if they got stored correctly failed.", retVal)
        elif None == stored_settings:
            Log_error("test failed because the retreived stored_settings were None.")
            retVal = eReturnStates.ERROR
        else:
            retVal = eReturnStates.CONTINUE
        if eReturnStates.CONTINUE == retVal:
                for key, value in stored_settings.items():
                    if key == "_id":
                        continue
                    elif stored_settings[key] != initial_settings[key]:
                        Log_error(f"retreived setting for key '{key}' was not the same as initial setting.")
                        retVal = eReturnStates.ERROR
                        break
                    else:
                        retVal = eReturnStates.SUCCESS
        if eReturnStates.SUCCESS != retVal:
            Log_error("test failed because the retreived stored settings were not the same as the settings that were stored into the database")
        if eReturnStates.SUCCESS != (cleanup := database_module.restore_backup_in_database(database_backup_path)):
            Log_error("restore_backup_in_database failed")
        assert Check_test_result_and_cleanup(retVal, cleanup)
        Log_verbose_func_end()

    def test_load_specific_setting(self):
        Log_verbose_func_start()
        retVal = ReturnState()
        retVal = eReturnStates.NOT_IMPLEMENTED
        assert Check_test_result(retVal)
        Log_verbose_func_end()
        
    
if __name__ == '__main__':
    pytest.main()