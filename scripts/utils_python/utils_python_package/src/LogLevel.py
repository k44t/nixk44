#!/bin/python3
# ******************************************************************************
# - *-coding: utf-8 -*-
# (c) copyright 2024 Alexander Poeschl
# All rights reserved.
# Secrecy Level STRICTLY CONFIDENTIAL
# ******************************************************************************
# @file LogLevel.py
# @author Alexander Poeschl <apoeschlfreelancing@kwanta.net>
# @brief LogLevel, used in apoeschlutils logging capability.
# ******************************************************************************
from src.BetterEnumInstance import BetterEnumInstance
from newLogLevel import newLogLevel

class LogLevel(BetterEnumInstance):
    @classmethod
    def __new__(self, cls, *args):
        newState = None
        if len(args) > 0:
            newState = args[0]
        else:
            newState = 5 # 5 is error
        retVal = BetterEnumInstance.__new__(self, newState, LogLevel.__name__, eLogLevels)
        return retVal