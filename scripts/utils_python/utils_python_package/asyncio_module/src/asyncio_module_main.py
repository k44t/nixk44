#!/bin/python3
# ******************************************************************************
# - *-coding: utf-8 -*-
# (c) copyright 2024 Alexander Poeschl
# All rights reserved.
# Secrecy Level STRICTLY CONFIDENTIAL
# ******************************************************************************
# @file asyncio_module_main.py
# @author Alexander Poeschl <apoeschlfreelancing@kwanta.net>
# @brief Module for asyncio implementation.
# ******************************************************************************

from utils_python_package.src.Apoeschlutils import Fix_imports
Fix_imports()
from utils_python_package.src.Apoeschlutils import Log_verbose, Log_error, Log_verbose_func_start, Log_verbose_func_end, Deb
from utils_python_package.src.ReturnState import ReturnState, eReturnStates

import asyncio
from threading import Thread



class AsyncioModule(Thread):
    loop = None
    def __init__(self):
        Log_verbose_func_start()
        retVal = ReturnState()
        super().__init__(daemon=True)
        self.loop = asyncio.new_event_loop()
        Log_verbose("start Thread...")
        self.start()
        Log_verbose("Thread started.")
        Log_verbose_func_end()
    
    def run(self):
        Log_verbose_func_start()
        retVal = ReturnState()
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()
        Log_verbose_func_end()

    def set_debug(self, debug = True):
        Log_verbose_func_start()
        retVal = ReturnState()
        if None == self.loop:
            retVal, self.loop = self.get_loop()
        self.loop.set_debug(debug)
        Log_verbose_func_end()
        return retVal, self.loop


    def get_loop(self):
        Log_verbose_func_start()
        retVal = ReturnState()
        if None == self.loop:
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
        if None == self.loop:
            retVal = eReturnStates.ERROR
        else:
            retVal = eReturnStates.SUCCESS
        Log_verbose_func_end()
        return retVal, self.loop


    def sleep(self, seconds):
        Log_verbose_func_start()
        retVal = ReturnState()
        Log_verbose(f"Sleep for: '{str(seconds)}' second(s).")
        done = asyncio.run(asyncio.sleep(seconds))
        Log_verbose(f"Sleep finished.")
        retVal = eReturnStates.SUCCESS
        Log_verbose_func_end()
        return retVal

    def _check_if_future_has_finished_with_success(self, future, future_result_can_be_none = False):
        Log_verbose_func_start()
        retVal = ReturnState()
        if eReturnStates.SUCCESS != (retVal := future.result()):
            if not future_result_can_be_none:
                Log_error(f"'{future}' has not yet finished.")
                retVal = eReturnStates.ERROR
            else:
                retVal = eReturnStates.SUCCESS
        Log_verbose_func_end()
        return retVal

    def start_task_with_callback_and_wait_for_finish(self, task, future_result_can_be_none = False):
        Log_verbose_func_start()
        retVal = ReturnState()
        runner = asyncio.run_coroutine_threadsafe(task, self.loop)
        retVal = self._check_if_future_has_finished_with_success(runner, future_result_can_be_none)
        Log_verbose_func_end()
        return retVal, runner
    

    def start_task_and_wait_for_finish(self, task, future_result_can_be_none = False):
        Log_verbose_func_start()
        retVal = ReturnState()
        runner = asyncio.run_coroutine_threadsafe(task, self.loop)
        retVal = self._check_if_future_has_finished_with_success(runner, future_result_can_be_none)
        Log_verbose_func_end()
        return retVal, runner
    
    def start_task_and_return_without_finish(self, task):
        Log_verbose_func_start()
        retVal = ReturnState()
        runner = asyncio.run_coroutine_threadsafe(task, self.loop)
        retVal = eReturnStates.IS_RUNNING
        Log_verbose_func_end()
        return retVal, runner

    def start_task_with_callback_and_return_without_finish(self, task):
        Log_verbose_func_start()
        retVal = ReturnState()
        runner = asyncio.run_coroutine_threadsafe(task, self.loop)
        retVal = eReturnStates.IS_RUNNING
        Log_verbose_func_end()
        return retVal, runner
    
    def stop_runner(self, runner):
        Log_verbose_func_start()
        retVal = ReturnState()
        if runner._state != "FINISHED":
            Log_verbose(f"try to cancel runner '{runner}'...")
            was_cancelled = runner.cancel()
            if was_cancelled:
                Log_verbose(f"'{runner}' was_cancelled successfully.")
                retVal = eReturnStates.SUCCESS
            else:
                Log_error(f"failed to cancel runner '{runner}'.")
        else:
            retVal = eReturnStates.SUCCESS
        Log_verbose_func_end()
        return retVal
