#!/bin/python3
# ******************************************************************************
# - *-coding: utf-8 -*-
# (c) copyright 2024 Alexander Poeschl
# All rights reserved.
# Secrecy Level STRICTLY CONFIDENTIAL
# ******************************************************************************
# @file create_module.py
# @author Alexander Poeschl <apoeschlfreelancing@kwanta.net>
# @brief This is the main function for generating a new module with its structure. You would not use this script directly! Use the create_module_setup.py for that, instead. 
# ******************************************************************************

from utils_python_package.src.Apoeschlutils import Fix_imports
Fix_imports()
from utils_python_package.src.Apoeschlutils import Log_verbose, Log_error, Log_verbose_func_start, Log_verbose_func_end, Get_folder_of_current_file, Deb
from datetime import date
import os, sys
import argparse

python_init_filename = "__init__.py"
current_date = date.today()
current_year = current_date.year

def replace_copyright_template_placeholders(name_of_the_file, brief_of_the_file, comments_template_content):
    result = ""
    for copyright_line in copyright_template_lines:
        copyright_line = copyright_line.replace("#YEAR", str(current_year))
        copyright_line = copyright_line.replace("#NAME_OF_THE_FILE", name_of_the_file)
        copyright_line = copyright_line.replace("#INSERT_BRIEF", brief_of_the_file)
        result = result + comments_template_content + copyright_line
    result = result + "\n"
    return result

def python_replace_init_file_template_placeholders(init_file_template_lines, fix_imports_content):
    result = ""
    for init_file_template_content_line in init_file_template_lines:
        init_file_template_content_line = init_file_template_content_line.replace("#FIX_IMPORTS", fix_imports_content)
        result = result + init_file_template_content_line
    result = result + "\n"
    return result

def python_replace_main_file_template_placeholders(main_file_template_lines, fix_imports_template_content, start_of_main_message, name_of_main_file, comments_template_content):
    result = ""
    imports_content = ""
    if add_argparser:
        argparser_is_imports_content = False
        argparser_is_main_content = False
        arg_parser_imports_content = ""
        arg_parser_main_content = ""
        python_arg_parser_template_path = os.path.join(templates_folder, "python_arg_parser_template.txt")
        with open(python_arg_parser_template_path, "r") as arg_parser_template_file:
            arg_parser_template_lines = arg_parser_template_file.readlines()
        for arg_parser_template_content_line in arg_parser_template_lines:
            line_to_test = arg_parser_template_content_line.strip().replace("\r\n","").replace("\n","").replace("\r","")
            if "# IMPORTS" == line_to_test:
                argparser_is_imports_content = True
                continue
            if "# IMPORTS_END" == line_to_test:
                argparser_is_imports_content = False
                continue
            if "# MAIN" == line_to_test:
                argparser_is_main_content = True
                continue
            if "# MAIN_END" == line_to_test:
                argparser_is_main_content = False
                continue
            if argparser_is_imports_content:
                arg_parser_imports_content = arg_parser_imports_content + arg_parser_template_content_line
            if argparser_is_main_content:
                arg_parser_main_content = arg_parser_main_content + arg_parser_template_content_line
    copyright_template_content = replace_copyright_template_placeholders( name_of_the_file=name_of_main_file, brief_of_the_file=brief_of_main_file, comments_template_content=comments_template_content)
    python_loggers_template_path = os.path.join(templates_folder, "python_loggers_template.txt")
    with open(python_loggers_template_path, "r") as loggers_template_file:
        loggers_template_lines = loggers_template_file.readlines()
    loggers_template_content = ""
    for loggers_template_line in loggers_template_lines:
        loggers_template_content = loggers_template_content + loggers_template_line + "\n"
    imports_content = imports_content + fix_imports_template_content + "\n"
    imports_content = imports_content + loggers_template_content + "\n"
    if add_argparser:
        imports_content = imports_content + arg_parser_imports_content + "\n"
    # creating resulting main content
    result = result + copyright_template_content + "\n"
    for main_file_template_content_line in main_file_template_lines:
        main_file_template_content_line = main_file_template_content_line.replace("#IMPORTS", imports_content)
        main_file_template_content_line = main_file_template_content_line.replace("#START_OF_MAIN_MESSAGE", start_of_main_message)
        main_file_template_content_line = main_file_template_content_line.replace("#ARG_PARSER", arg_parser_main_content)
        result = result + main_file_template_content_line
    return result

def create_module():
    Log_verbose_func_start()
    if not os.path.isdir(parent_folder):
        os.mkdir(parent_folder)
    module_path = os.path.join(parent_folder, module_name + "_module")
    if not os.path.isdir(module_path):
        os.mkdir(module_path)
    sources_folder = os.path.join(module_path, "src")
    if not os.path.isdir(sources_folder):
        os.mkdir(sources_folder)
    tests_folder = os.path.join(module_path, "tests")
    if not os.path.isdir(tests_folder):
        os.mkdir(tests_folder)
    if module_language == "python":
        python_script_template_path = os.path.join(templates_folder, "python_script_template.txt")
        with open(python_script_template_path, "r") as script_template_file:
            script_template_lines = script_template_file.readlines()
        script_template_content = ""
        for script_template_line in script_template_lines:
            script_template_content = script_template_content + script_template_line + "\n"
        python_comments_template_path = os.path.join(templates_folder, "python_comments_template.txt")
        with open(python_comments_template_path, "r") as comments_template_file:
            comments_template_lines = comments_template_file.readlines()
        comments_template_content = ""
        for comments_template_line in comments_template_lines:
            comments_template_content = comments_template_content + comments_template_line
        python_fix_imports_template_path = os.path.join(templates_folder, "python_fix_imports_template.txt")
        with open(python_fix_imports_template_path, "r") as fix_imports_template_file:
            fix_imports_template_lines = fix_imports_template_file.readlines()
        fix_imports_template_content = ""
        for fix_imports_template_line in fix_imports_template_lines:
            fix_imports_template_content = fix_imports_template_content + fix_imports_template_line
        # stuff for init files
        python_init_file_template_path = os.path.join(templates_folder, "python_init_file_template.txt")
        with open(python_init_file_template_path, "r") as init_file_template_file:
            init_file_template_lines = init_file_template_file.readlines()
        init_file_template_content = python_replace_init_file_template_placeholders(init_file_template_lines, fix_imports_template_content)
        brief_of_the_file = "Python Init file for folders."
        name_of_the_file = "__init__.py"
        copyright_template_content = replace_copyright_template_placeholders(name_of_the_file=name_of_the_file, brief_of_the_file=brief_of_the_file, comments_template_content=comments_template_content)
        init_file_content = script_template_content
        init_file_content = init_file_content + copyright_template_content
        init_file_content = init_file_content + init_file_template_content
        module_path_init_file_path = os.path.join(module_path, python_init_filename)
        with open(module_path_init_file_path, "w") as module_path_init_file:
            module_path_init_file.write(init_file_content)
        sources_path_init_file_path = os.path.join(sources_folder, python_init_filename)
        with open(sources_path_init_file_path, "w") as sources_path_init_file_file:
            sources_path_init_file_file.write(init_file_content)
        tests_path_init_file_path = os.path.join(tests_folder, python_init_filename)
        with open(tests_path_init_file_path, "w") as tests_path_init_file_file:
            tests_path_init_file_file.write(init_file_content)
        # stuff for main file
        python_main_file_template_path = os.path.join(templates_folder, "python_main_file_template.txt")
        with open(python_main_file_template_path, "r") as main_file_template_file:
            main_file_template_lines = main_file_template_file.readlines()
        name_of_main_file = module_name + "_module_main.py"
        start_of_main_message = f"\"Start of Main Function of {module_name}....\""
        main_file_template_content = python_replace_main_file_template_placeholders(main_file_template_lines, fix_imports_template_content, start_of_main_message, name_of_main_file, comments_template_content)
        brief_of_the_file = "Python Init file for folders."
        name_of_the_file = "__init__.py"
        main_file_content = ""
        main_file_content = main_file_content + script_template_content
        main_file_content = main_file_content + main_file_template_content
        sources_path_main_file_path = os.path.join(sources_folder, name_of_main_file)
        with open(sources_path_main_file_path, "w") as sources_path_main_file_file:
            sources_path_main_file_file.write(main_file_content)
    Log_verbose_func_end()

if __name__ == "__main__":
    Log_verbose("Generating new module structure...")
    parser = argparse.ArgumentParser(
        prog='New Module Creator',
        description='This program is used fastly generate new modules with src and tests folders, init files and main failes',
        epilog='In case of Problems, Bugs or for Feature Requests, feel free to get in touch with me <apoeschlfreelancing@kwanta.net>.'
    )
    parser.add_argument('--verbose',
                        dest='verbose',
                        action='store_true',
                        default=False,
                        help='output verbose'
                        )
    parser.add_argument('--silent',
                        dest='silent',
                        action='store_true',
                        default=False,
                        help='silence output'
                        )
    parser.add_argument('--add_argparser',
                        dest='add_argparser',
                        action='store_true',
                        default=False,
                        help='If the creator should add an argparser.'
                        )
    parser.add_argument('--module_language',
                        dest='module_language',
                        default="python",
                        type=str,
                        help='Module language, e.g. "python", "java", "javascript", "c++", "c#".'
                        )
    parser.add_argument('--parent_folder',
                        dest='parent_folder',
                        default="./parent_folder",
                        type=str,
                        help='path/to/parentfolder where new_module shall be created.'
                        )
    parser.add_argument('--module_name',
                        dest='module_name',
                        default="new_module_name",
                        type=str,
                        help='new_module_name'
                        )
    parser.add_argument('--brief_of_main_file',
                        dest='brief_of_main_file',
                        default="brief_of_main_file",
                        type=str,
                        help='Brief of the main file.'
                        )
    args, unknown = parser.parse_known_args()
    if None != unknown and len(unknown) > 0:
        Log_error(f"unknown arguments: {unknown}")
    verbose = args.verbose
    silent = args.silent
    module_language = args.module_language
    parent_folder = args.parent_folder
    module_name = args.module_name
    brief_of_main_file = args.brief_of_main_file
    add_argparser = args.add_argparser

    # for debugging purposes
    if hasattr(sys, 'gettrace') and sys.gettrace() is not None:  # is True, when vscode debug mode is active
        verbose=False
        silent=False
        module_language="python"
        parent_folder="c:/p/gohomeagent/utils_python/test_create_module"
        module_name="asyncio"
        brief_of_main_file="Module for asyncio implementation."
        add_argparser=True


    create_module_folder = Get_folder_of_current_file()
    templates_folder = os.path.join(create_module_folder, "templates")
    templates_list = os.listdir(templates_folder)
    copyright_template_path = os.path.join(templates_folder, "copyright_template.txt")
    with open(copyright_template_path, "r") as copyright_template_file:
        copyright_template_lines = copyright_template_file.readlines()
    create_module()