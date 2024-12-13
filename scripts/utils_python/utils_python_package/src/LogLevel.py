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
from src.eLogLevels import eLogLevels


class newLogLevels(eLogLevels):
    UNKNOWN = eLogLevels.UNKNOWN
    pass


class LogLevel(BetterEnumInstance):
    @classmethod
    def __new__(self, cls, *args):
        newState = None
        if len(args) > 0:
            newState = args[0]
        else:
            newState = LogLevels.UNKNOWN
        name = args[1]
        retVal = BetterEnumInstance.__new__(self, newState, name, eLogLevels)
        return retVal


LogLevels = newLogLevels()
LogLevelDefinitions = [attr for attr in vars(eLogLevels) if not callable(getattr(eLogLevels, attr)) and not attr.startswith("__")]
definitions = LogLevelDefinitions
for definition in definitions:
    definition_attr = getattr(eLogLevels, definition)
    definition_value = definition_attr.value
    definition_names = definition_attr.names
    result_LogLevel = LogLevel(definition_value, definition, definition_names)
    LogLevels.__setattr__(definition, result_LogLevel)
print(LogLevels)