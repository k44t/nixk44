#!/bin/python3
# ******************************************************************************
# - *-coding: utf-8 -*-
# (c) copyright 2024 Alexander Poeschl
# All rights reserved.
# Secrecy Level STRICTLY CONFIDENTIAL
# ******************************************************************************
# @file test_apoeschlutils.py
# @author Alexander Poeschl <apoeschlfreelancing@kwanta.net>
# @brief Tests for the apoeschlutils.py.
# ******************************************************************************
import pytest
import subprocess
from utils_python_package.src.Apoeschlutils import Log_error, Log_result_error, Log_result_error, Check_test_result_and_cleanup, Check_test_result, Log_verbose_func_start, Log_verbose_func_end
from utils_python_package.src.ReturnState import ReturnState, eReturnStates

class Test_TestMethods():
    def test_DebugOutput(self):
        proc = subprocess.Popen(["python", "-c", "from utils_python_package.src.Apoeschlutils import deb; deb('test_string')"], stdout=subprocess.PIPE)
        out = proc.communicate()[0]
        assert "\\x1b[94m<string>:1 : Debug: \\x1b[93mtest_string\\x1b[0m\\r\\n" in str(out)

    def test_check_test_result_and_cleanup(self):
        Log_verbose_func_start()
        retVal = ReturnState()
        cleanup = ReturnState()
        assert Check_test_result_and_cleanup(retVal, cleanup) == False
        retVal = eReturnStates.ERROR
        cleanup = eReturnStates.ERROR
        assert Check_test_result_and_cleanup(retVal, cleanup) == False
        retVal = eReturnStates.SUCCESS
        cleanup = eReturnStates.ERROR
        assert Check_test_result_and_cleanup(retVal, cleanup) == False
        retVal = eReturnStates.ERROR
        cleanup = eReturnStates.SUCCESS
        assert Check_test_result_and_cleanup(retVal, cleanup) == False
        retVal = eReturnStates.SUCCESS
        cleanup = eReturnStates.SUCCESS
        assert Check_test_result_and_cleanup(retVal, cleanup) == True
        Log_verbose_func_end()

    def test_check_test_result(self):
        Log_verbose_func_start()
        retVal = ReturnState()
        assert Check_test_result(retVal) == False
        retVal = eReturnStates.ERROR
        assert Check_test_result(retVal) == False
        retVal = eReturnStates.SUCCESS
        assert Check_test_result(retVal) == True
        Log_verbose_func_end()


if __name__ == '__main__':
    if True:
        test_methods = Test_TestMethods()
        test_methods.test_check_test_result_and_cleanup()
    else:
        pytest.main()