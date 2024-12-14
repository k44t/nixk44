#!/bin/python3
# ******************************************************************************
# - *-coding: utf-8 -*-
# (c) copyright 2024 Alexander Poeschl
# All rights reserved.
# Secrecy Level STRICTLY CONFIDENTIAL
# ******************************************************************************
# @file test_LogLevel.py
# @author Alexander Poeschl <apoeschlfreelancing@kwanta.net>
# @brief Tests for the LogLevels.
# ******************************************************************************
import pytest
from utils_python_package.src.Apoeschlutils import Log_info, Log_verbose_func_start, Log_verbose_func_end
from utils_python_package.src.LogLevel import LogLevel, eLogLevels


fail_representations = [eLogLevels.ERROR, "failed", "FAILED", "error", "ERROR", "fail", "FAIL"]
success_representations = [eLogLevels.SUCCESS, "success", "SUCCESS"]
class Test_TestMethods():
    def test_EqualityTests(self):
        Log_verbose_func_start()
        equality_test_cases = {
            "test"                                  :-1,
            -1000                                   :-1,
            eLogLevels.SUCCESS                   :1,
            eLogLevels.ERROR                    :0
        }
        for fail_representation in fail_representations:
            equality_test_cases[fail_representation] = eLogLevels.ERROR
        for success_representation in success_representations:
            equality_test_cases[success_representation] = eLogLevels.SUCCESS
        for test_value, expected_value in equality_test_cases.items():
            Log_info(f"testing test_value: '{test_value}' with expected value '{expected_value}'")
            result = LogLevel(test_value)
            assert result == expected_value
            Log_info("Test was OK.")
            Log_info(f"testing test_value: '{test_value}' with expected value '{expected_value}' on greaterThanOrEqual")
            result = LogLevel(test_value)
            assert result >= expected_value
            Log_info("Test was OK.")
            Log_info(f"testing test_value: '{test_value}' with expected value '{expected_value}' on lessThanOrEqual")
            result = LogLevel(test_value)
            assert result <= expected_value
            Log_info("Test was OK.")
        Log_verbose_func_end()
        
    def test_GreaterThanTests(self):
        Log_verbose_func_start()
        greaterThan_test_cases = {}
        for fail_representation in fail_representations:
            greaterThan_test_cases[fail_representation] = -1
        for success_representation in success_representations:
            greaterThan_test_cases[success_representation] = eLogLevels.ERROR
        for test_value, expected_value in greaterThan_test_cases.items():
            Log_info(f"testing test_value: '{test_value}' with expected value '{expected_value}'")
            result = LogLevel(test_value)
            assert result > expected_value
            Log_info("Test was OK.")
        Log_verbose_func_end()
        
    def test_LessThanTests(self):
        Log_verbose_func_start()
        lessThan_test_cases = {}
        for fail_representation in fail_representations:
            lessThan_test_cases[fail_representation] = eLogLevels.SUCCESS
        for test_value, expected_value in lessThan_test_cases.items():
            Log_info(f"testing test_value: '{test_value}' with expected value '{expected_value}'")
            result = LogLevel(test_value)
            assert result < expected_value
            Log_info("Test was OK.")
        Log_verbose_func_end()

        
if __name__ == '__main__':
    pytest.main()