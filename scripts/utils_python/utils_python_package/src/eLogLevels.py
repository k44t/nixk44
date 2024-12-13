#!/bin/python3
# ******************************************************************************
# - *-coding: utf-8 -*-
# (c) copyright 2024 Alexander Poeschl
# All rights reserved.
# Secrecy Level STRICTLY CONFIDENTIAL
# ******************************************************************************
# @file eLogLevels.py
# @author Alexander Poeschl <apoeschlfreelancing@kwanta.net>
# @brief Definitions for eLogLevels.
# ******************************************************************************
from src.BetterEnum import BetterEnum
from src.LogLevel import LogLevel

class eLogLevels(BetterEnum):
    ERROR = LogLevel(0, ["Error", "Failed", "Fail"])
    SUCCESS = LogLevel(1, "Success")
    INFO = LogLevel(2, "Info")
    DEBUG = LogLevel(3, "Debug")
    DEBCONFIG = LogLevel(4, "DebConfig")
    UNKNOWN = LogLevel(5, "Unknown")
    VERBOSE = LogLevel(6, "Verbose")
    FAILED = ERROR