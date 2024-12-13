#!/bin/python3
# ******************************************************************************
# - *-coding: utf-8 -*-
# (c) copyright 2024 Alexander Poeschl
# All rights reserved.
# Secrecy Level STRICTLY CONFIDENTIAL
# ******************************************************************************
# @file test_general_module_with_submodule_module.py
# @author Alexander Poeschl <apoeschlfreelancing@kwanta.net>
# @brief Tests for the GeneralModuleWithSubmodule-Module.
# ******************************************************************************
from utils_python_package.src.Apoeschlutils import Fix_imports
Fix_imports()
from utils_python_package.src.Apoeschlutils import Log_error, Log_verbose, Log_result_error, Log_verbose_func_start, Check_test_result_and_cleanup, Check_test_result, Log_verbose_func_end
from utils_python_package.src.ReturnState import ReturnState, eReturnStates
from general_module_with_submodule.tests.derived_module_with_submodule_module.src.derived_module_with_submodule_module_main import DerivedModuleWithSubmodule
from database_module.src.database_module_main import DatabaseModule
import pytest

    


class Test_GeneralModuleWithSubmodule_TestMethods():
    def test_DerivedModuleWithSubmodule_module_create(self):
        Log_verbose_func_start()
        retVal = ReturnState()
        derived_module_with_submodule = DerivedModuleWithSubmodule()
        retVal = derived_module_with_submodule.module_create()
        assert Check_test_result(retVal)
        Log_verbose_func_end()

    def test_module_get_initial_settings(self):
        Log_verbose_func_start()
        retVal = ReturnState()
        derived_module_with_submodule = DerivedModuleWithSubmodule()
        retVal, derived_module_with_submodule_initial_settings = derived_module_with_submodule.module_get_initial_settings()
        if eReturnStates.SUCCESS != retVal:
            Log_result_error(f"get_settings failed.", retVal)
            assert Check_test_result(retVal)
        elif None == derived_module_with_submodule_initial_settings:
            Log_error(f"test failed. derived_module_with_submodule_settings were None.")
            retVal = eReturnStates.ERROR
        assert Check_test_result(retVal)
        Log_verbose_func_end()

    def test_module_load_settings(self):
        Log_verbose_func_start()
        retVal = ReturnState()
        derived_module_with_submodule = DerivedModuleWithSubmodule()
        if eReturnStates.SUCCESS != (retVal := derived_module_with_submodule.module_load_settings()):
            Log_result_error(f"load_settings for general derived module failed.", retVal)
        elif eReturnStates.SUCCESS != (retVal := derived_module_with_submodule.module_load_used_sub_module()):
            Log_result_error(f"load_sst_module failed.", retVal)
        elif eReturnStates.SUCCESS != (retVal := derived_module_with_submodule.module_load_settings()):
            Log_result_error(f"load_settings for specific derived module failed.", retVal)
        assert Check_test_result(retVal)
        Log_verbose_func_end()

    def test_module_apply_settings(self):
        Log_verbose_func_start()
        retVal = ReturnState()
        derived_module_with_submodule = DerivedModuleWithSubmodule()
        if eReturnStates.SUCCESS > (retVal := derived_module_with_submodule.module_apply_settings()):
            Log_result_error(f"apply_settings for general derived module failed.", retVal)
        elif eReturnStates.SUCCESS > (retVal := derived_module_with_submodule.module_load_used_sub_module()):
            Log_result_error(f"load_sst_module failed.", retVal)
        elif eReturnStates.SUCCESS > (retVal := derived_module_with_submodule.module_apply_settings()):
            Log_result_error(f"apply_settings for specific derived module failed.", retVal)
        assert Check_test_result(retVal)
        Log_verbose_func_end()

    def test_module_load_derived_module_with_submodule(self):
        Log_verbose_func_start()
        retVal = ReturnState()
        derived_module_with_submodule = DerivedModuleWithSubmodule()
        retVal = derived_module_with_submodule.module_load_used_sub_module()
        assert Check_test_result(retVal)
        Log_verbose_func_end()

    def test_set_used_derived_module_with_submodule(self):
        Log_verbose_func_start()
        retVal = ReturnState()
        derived_module_with_submodule = DerivedModuleWithSubmodule()
        retVal, used_derived_module_with_submodule = derived_module_with_submodule.get_used_sub_module()
        if eReturnStates.SUCCESS != retVal:
            Log_result_error(f"get_used_derived_module_with_submodule failed.", retVal)
        elif eReturnStates.SUCCESS != (retVal := derived_module_with_submodule.set_used_sub_module(used_derived_module_with_submodule)):
            Log_result_error(f"set_used_derived_module_with_submodule failed.", retVal)
        assert Check_test_result(retVal)
        Log_verbose_func_end()

    def test_get_used_derived_module_with_submodule(self):
        Log_verbose_func_start()
        retVal = ReturnState()
        derived_module_with_submodule = DerivedModuleWithSubmodule()
        retVal, used_derived_module_with_submodule = derived_module_with_submodule.get_used_sub_module()
        if eReturnStates.SUCCESS > retVal:
            Log_result_error(f"get_used_derived_module_with_submodule failed.", retVal)
        assert Check_test_result(retVal)
        Log_verbose_func_end()

    def test_module_get_settings(self):
        Log_verbose_func_start()
        retVal = ReturnState()
        derived_module_with_submodule = DerivedModuleWithSubmodule(create_only=True)
        retVal, first_result = derived_module_with_submodule.module_get_settings()
        first_result_str = str(first_result)
        if eReturnStates.SUCCESS > retVal:
            Log_result_error(f"get_settings for general stt module failed.", retVal)
        elif eReturnStates.SUCCESS > (retVal := derived_module_with_submodule.module_load_used_sub_module()):
            Log_result_error(f"load_sst_module module failed.", retVal)
        else:
            retVal, second_result = derived_module_with_submodule.module_get_settings()
        if eReturnStates.SUCCESS > retVal:
            Log_result_error(f"get_settings for specific stt module failed.", retVal)
        if first_result_str == str(second_result):
            Log_error(f"it seems that the specific module was not loaded properly, because the settings for general module and the settings for specific module were the same. first_result was: '{first_result}' and second_result was: '{second_result}'")
            retVal = eReturnStates.ERROR
        assert Check_test_result(retVal)
        Log_verbose_func_end()

    def test_reload_settings(self):
        Log_verbose_func_start()
        retVal = ReturnState()
        derived_module_with_submodule = DerivedModuleWithSubmodule(create_only=True)
        if eReturnStates.SUCCESS > (retVal := derived_module_with_submodule.module_reload_settings()):
            Log_result_error(f"reload_settings failed.", retVal)
        assert Check_test_result(retVal)
        Log_verbose_func_end()

    def test_derived_module_store_settings_in_database(self):
        Log_verbose_func_start()
        retVal = ReturnState()
        cleanup = ReturnState()
        derived_module = DerivedModuleWithSubmodule()
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
            retVal, stored_settings = derived_module.module_get_settings_from_database(settings_topic_arg="DerivedModuleWithSubmodule")
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
            Log_result_error("test failed because the retreived stored settings were not the same as the settings that were stored into the database.", retVal)
        if eReturnStates.SUCCESS != (cleanup := database_module.restore_backup_in_database(database_backup_path)):
            Log_error("restore_backup_in_database failed")
        assert Check_test_result_and_cleanup(retVal, cleanup)
        Log_verbose_func_end()

    def test_remove_settings_from_database(self):
        Log_verbose_func_start()
        retVal = ReturnState()
        cleanup = ReturnState()
        derived_module = DerivedModuleWithSubmodule()
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
        elif eReturnStates.SUCCESS > (retVal := derived_module.module_store_settings_in_database(initial_settings=True)):
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
            Log_result_error("test failed because the retreived stored settings were not the same as the settings that were stored into the database.", retVal)
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
        derived_module = DerivedModuleWithSubmodule()
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
            Log_result_error("test failed because the retreived stored settings were not the same as the settings that were stored into the database.", retVal)
        if eReturnStates.SUCCESS != (cleanup := database_module.restore_backup_in_database(database_backup_path)):
            Log_error("restore_backup_in_database failed")
        assert Check_test_result_and_cleanup(retVal, cleanup)
        Log_verbose_func_end()
        
if __name__ == '__main__':
    pytest.main()