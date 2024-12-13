#!/bin/python3
# ******************************************************************************
# - *-coding: utf-8 -*-
# (c) copyright 2024 Alexander Poeschl
# All rights reserved.
# Secrecy Level STRICTLY CONFIDENTIAL
# ******************************************************************************
# @file test_asyncio_module.py
# @author Alexander Poeschl <apoeschlfreelancing@kwanta.net>
# @brief Tests for asyncio module.
# ******************************************************************************

from utils_python_package.src.Apoeschlutils import Fix_imports
Fix_imports()
from utils_python_package.src.Apoeschlutils import Log_error, Log_verbose, Log_result_error, Check_test_result_and_cleanup, Check_test_result, Log_verbose_func_start, Log_verbose_func_end
from utils_python_package.src.ReturnState import ReturnState, eReturnStates
from asyncio_module.src.asyncio_module_main import AsyncioModule
import pytest
from datetime import datetime, timedelta
import asyncio

test_arg = "test_arg"
test_callback_arg = "test_callback_arg"

class Test_AsyncioModule_TestMethods():


    async def asyncio_test_task_with_arguments(self, task_arguments, callback, callback_arguments):
        Log_verbose_func_start()
        retVal = ReturnState()
        if test_arg != task_arguments[0]:
            Log_error(f"test failed because test_arguments did not contain '{test_arg}'.")
            retVal = eReturnStates.ERROR
        else:
            retVal = eReturnStates.CONTINUE
        if eReturnStates.CONTINUE == retVal:
            retVal = callback(callback_arguments)
        if eReturnStates.SUCCESS != retVal:
            Log_error("test failed because callback failed.")
        Log_verbose_func_end()
        return retVal

    def asyncio_test_callback(self, callback_arguments):
        Log_verbose_func_start()
        retVal = ReturnState()
        if test_callback_arg != callback_arguments[0]:
            Log_error(f"test failed because callback_arguments did not contain '{test_callback_arg}'.")
            retVal = eReturnStates.ERROR
        else:
            retVal = eReturnStates.SUCCESS
        Log_verbose_func_end()
        return retVal

    def test_task_with_arguments_and_callback(self):
        Log_verbose_func_start()
        retVal = ReturnState()
        asyncio_module = AsyncioModule()
        task_args = [test_arg]
        callback_args = [test_callback_arg]
        retVal, asyncio_test_task_runner = asyncio_module.start_task_with_callback_and_wait_for_finish(task=self.asyncio_test_task_with_arguments(task_arguments=task_args,callback=self.asyncio_test_callback,callback_arguments=callback_args))
        if eReturnStates.SUCCESS != retVal:
            Log_result_error(f"start_task_with_callback failed.", retVal)
        else:
            retVal = asyncio_module.sleep(1)
            if eReturnStates.SUCCESS != retVal:
                Log_result_error(f"sleep failed.", retVal)
        assert Check_test_result(retVal)
        Log_verbose_func_end()
        
    async def asyncio_test_longrunning_task_with_arguments(self, task_arguments, callback, callback_arguments):
        Log_verbose_func_start()
        retVal = ReturnState()
        if test_arg != task_arguments[0]:
            Log_error(f"test failed because test_arguments did not contain '{test_arg}'.")
            retVal = eReturnStates.ERROR
        else:
            retVal = eReturnStates.CONTINUE
        if eReturnStates.CONTINUE == retVal:
            max_time = datetime.now() + timedelta(seconds=5)
            while max_time > datetime.now():
                retVal = callback(callback_arguments)
                await asyncio.sleep(1)
        if eReturnStates.SUCCESS != retVal:
            Log_result_error("test failed because callback failed.", retVal)
        Log_verbose_func_end()
        return retVal

    
    def test_stop_longrunningtask_with_arguments_and_callback(self):
        Log_verbose_func_start()
        retVal = ReturnState()
        asyncio_module = AsyncioModule()
        task_args = [test_arg]
        callback_args = [test_callback_arg]
        retVal, asyncio_test_task_runner = asyncio_module.start_task_with_callback_and_return_without_finish(task=self.asyncio_test_longrunning_task_with_arguments(task_arguments=task_args,callback=self.asyncio_test_callback, callback_arguments=callback_args))
        if eReturnStates.IS_RUNNING != retVal:
            Log_result_error(f"start_task_with_callback failed.", retVal)
        else:
            retVal = asyncio_module.sleep(3)
            if eReturnStates.SUCCESS != retVal:
                Log_result_error(f"sleep failed.", retVal)
            else:
                retVal = eReturnStates.CONTINUE
        if eReturnStates.CONTINUE == retVal:
            retVal = asyncio_module.stop_runner(asyncio_test_task_runner)
            if eReturnStates.SUCCESS != retVal:
                Log_result_error(f"stop_task failed.", retVal)
            else:
                retVal = eReturnStates.SUCCESS
        assert Check_test_result(retVal)
        Log_verbose_func_end()
        
    async def asyncio_test_infiniterunning_task_with_arguments(self, task_arguments, callback, callback_arguments):
        Log_verbose_func_start()
        retVal = ReturnState()
        if test_arg != task_arguments[0]:
            Log_error(f"test failed because test_arguments did not contain '{test_arg}'.")
            retVal = eReturnStates.ERROR
        else:
            retVal = eReturnStates.CONTINUE
        if eReturnStates.CONTINUE == retVal:
            try:
                while True:
                    retVal = callback(callback_arguments)
                    await asyncio.sleep(1)
            except asyncio.CancelledError:
                print('task has been cancelled. normally in this codeblock you would do "CLEANUP" HERE!')
        if eReturnStates.SUCCESS != retVal:
            Log_result_error("test failed because callback failed.", retVal)
        Log_verbose_func_end()
        return retVal

    
    def test_stop_infiniterunningtask_with_arguments_and_callback(self):
        Log_verbose_func_start()
        retVal = ReturnState()
        asyncio_module = AsyncioModule()
        task_args = [test_arg]
        callback_args = [test_callback_arg]
        retVal, asyncio_test_task_runner = asyncio_module.start_task_with_callback_and_return_without_finish(task=self.asyncio_test_infiniterunning_task_with_arguments(task_arguments=task_args,callback=self.asyncio_test_callback, callback_arguments=callback_args))
        if eReturnStates.IS_RUNNING != retVal:
            Log_result_error(f"start_task_with_callback failed.", retVal)
        else:
            retVal = asyncio_module.sleep(10)
            if eReturnStates.SUCCESS != retVal:
                Log_result_error(f"sleep failed.", retVal)
            else:
                retVal = eReturnStates.CONTINUE
        if eReturnStates.CONTINUE == retVal:
            retVal = asyncio_module.stop_runner(asyncio_test_task_runner)
            if eReturnStates.SUCCESS != retVal:
                Log_result_error(f"stop_task failed.", retVal)
            else:
                retVal = eReturnStates.SUCCESS
        assert Check_test_result(retVal)
        Log_verbose_func_end()
    
if __name__ == '__main__':
    if False:
        test_methods = Test_AsyncioModule_TestMethods()
        test_methods.test_stop_longrunningtask_with_arguments_and_callback()
    else:
        pytest.main()