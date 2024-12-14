#!/bin/python3
# ******************************************************************************
# - *-coding: utf-8 -*-
# (c) copyright 2024 Alexander Poeschl
# All rights reserved.
# Secrecy Level STRICTLY CONFIDENTIAL
# ******************************************************************************
# @file ReturnState.py
# @author Alexander Poeschl <apoeschlfreelancing@kwanta.net>
# @brief Implementation for ReturnStates usable in all sorts of Python Projects.
# ******************************************************************************
import src.eReturnStates as eReturnStates
from src.BetterEnumInstance import BetterEnumInstance

eReturnStates = eReturnStates.eReturnStates
class ReturnState(BetterEnumInstance):
    @classmethod
    def __new__(self, cls, *args):
        newState = None
        if len(args) > 0:
            newState = args[0]
        else:
            newState = eReturnStates.FAILED
        retVal = BetterEnumInstance.__new__(self, newState, ReturnState.__name__, eReturnStates)
        return retVal