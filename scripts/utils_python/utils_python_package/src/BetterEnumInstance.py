#!/bin/python3
# ******************************************************************************
# - *-coding: utf-8 -*-
# (c) copyright 2024 Alexander Poeschl
# All rights reserved.
# Secrecy Level STRICTLY CONFIDENTIAL
# ******************************************************************************
# @file BetterEnumInstance.py
# @author Alexander Poeschl <apoeschlfreelancing@kwanta.net>
# @brief Implementation for BetterEnumInstance (For creation of custom Enums).
# ******************************************************************************
from utils_python_package.src.Apoeschllogging import Log_error
from src.BetterEnumEntry import BetterEnumEntry

class BetterEnumInstance():
    state = None
    name = None
    def __init__(self, arg_state, arg_name, betterEnumStateDefinitions):
        retVal = -1
        self.name = arg_name
        definitions = [attr for attr in vars(betterEnumStateDefinitions) if not callable(getattr(betterEnumStateDefinitions, attr)) and not attr.startswith("__")]
        betterEnumStateTypes = []
        for betterEnumStateType in definitions:
            returnStateTypeDefinition = getattr(betterEnumStateDefinitions, betterEnumStateType)
            betterEnumStateTypes.append(returnStateTypeDefinition)
        if isinstance(arg_state, int):
            for betterEnumStateType in betterEnumStateTypes:
                if betterEnumStateType.value == arg_state:
                    self.state = betterEnumStateType
                    retVal = 1
                    break
            if retVal != 1:
                Log_error("Could not convert state of type int ('" + str(arg_state) + "') to " + self.name + ". '" + str(arg_state) + "' is unknown.")
        elif isinstance(arg_state, str):
            for betterEnumStateType in betterEnumStateTypes:
                for alternative_string in betterEnumStateType.alternative_strings:
                    if alternative_string.lower() == arg_state.lower():
                        self.state = betterEnumStateType
                        retVal = 1
                        break
                if retVal == 1:
                    break
            if retVal != 1:
                Log_error("Could not convert state of type string ('" + str(arg_state) + "') to " + self.name + ". '" + str(arg_state) + "' is unknown.")
        elif isinstance(arg_state, BetterEnumEntry):
            self.state = arg_state
            retVal = 1
        else:
            try:
                Log_error("Could not convert state ('" + str(arg_state) + "') to " + self.name + ". '" + str(arg_state) + "' is unknown.")
            except:
                Log_error("Could not convert state to string and state could not be converted to " + self.name + ".")
        return retVal
    

    @classmethod
    def __new__(self, cls, *args):
        retVal = BetterEnumInstance.__init__(self, args[0], args[1], args[2])
        if retVal != 1:
            return retVal
        else:
            super().__new__(cls)
            return self.state
