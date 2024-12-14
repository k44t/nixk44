#!/bin/python3
# ******************************************************************************
# - *-coding: utf-8 -*-
# (c) copyright 2024 Alexander Poeschl
# All rights reserved.
# Secrecy Level STRICTLY CONFIDENTIAL
# ******************************************************************************
# @file create_module_setup.py
# @author Alexander Poeschl <apoeschlfreelancing@kwanta.net>
# @brief Script for setting up new modules (their inner structure and some templated files).
# ******************************************************************************
import os

verbose=False
silent=False
module_language="python"
parent_folder="C:/p/gohomeagent/utils_python/utils_python_package"
module_name="asyncio"
brief_of_main_file="Module for asyncio implementation."

#optional
#argparser
add_argparser=True
argparser_program_name="TestProgram"
argparser_program_description="This is just a test description"
argparser_string_argument="test_argument_string"
argparser_string_argument_default="empty"
argparser_string_argument_help="This is the helper"
#argparser_end
#optional_end

verbose_flag = ""
if verbose:
    verbose_flag = "--verbose"
silent_flag = ""
if silent:
    silent_flag = "--silent"
argparser_flag = ""
if add_argparser:
    add_argparser_flag = "--add_argparser"
command = f'python c:/p/gohomeagent/utils_python//create_new_module/create_module.py {verbose_flag} {silent_flag} {add_argparser_flag} --module_language="{module_language}" --parent_folder="{parent_folder}" --module_name="{module_name}" --brief_of_main_file="{brief_of_main_file}"'
print(command)
os.system(command)