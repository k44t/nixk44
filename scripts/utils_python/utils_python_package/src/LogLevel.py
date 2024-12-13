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
import src.eLogLevels as eLogLevels
from src.BetterEnumInstance import BetterEnumInstance

eLogLevels = eLogLevels.eLogLevels
class LogLevel(BetterEnumInstance):
    @classmethod
    def __new__(self, cls, *args):
        newState = None
        if len(args) > 0:
            newState = args[0]
        else:
            newState = eLogLevels.UNKNOWN
        retVal = BetterEnumInstance.__new__(self, newState, LogLevel.__name__, eLogLevels)
        return retVal