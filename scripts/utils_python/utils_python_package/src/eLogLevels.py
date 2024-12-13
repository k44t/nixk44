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
from src.NewLogLevel import NewLogLevel

class eLogLevels(BetterEnum):
    ERROR = NewLogLevel(0, ["Error", "Failed", "Fail"])
    SUCCESS = NewLogLevel(1, "Success")
    INFO = NewLogLevel(2, "Info")
    DEBUG = NewLogLevel(3, "Debug")
    DEBCONFIG = NewLogLevel(4, "DebConfig")
    UNKNOWN = NewLogLevel(5, "Unknown")
    VERBOSE = NewLogLevel(6, "Verbose")
    WARNING = NewLogLevel(7, "Warning")
    FAILED = ERROR