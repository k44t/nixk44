#!/bin/python3
# ******************************************************************************
# - *-coding: utf-8 -*-
# (c) copyright 2024 Alexander Poeschl
# All rights reserved.
# Secrecy Level STRICTLY CONFIDENTIAL
# ******************************************************************************
# @file eReturnStates.py
# @author Alexander Poeschl <apoeschlfreelancing@kwanta.net>
# @brief Definitions for eReturnStates.
# ******************************************************************************
from src.BetterEnum import BetterEnum
from src.ReturnState import ReturnState

class eReturnStates(BetterEnum):
    FAILED = ReturnState(0, ["ERROR", "Failed", "Fail"])
    SUCCESS = ReturnState(1, "SUCCESS")
    ERROR = FAILED
    NOT_IMPLEMENTED = ReturnState(-1, ["NOT_IMPLEMENTED"])
    EXISTS = ReturnState(2, ["EXISTS", "TRUE"])
    EXISTS_NOT = ReturnState(-2, ["EXISTS_NOT", "FALSE"])
    INITIALIZED = ReturnState(3, ["INITIALIZED", "TRUE"])
    INITIALIZED_NOT = ReturnState(-3, ["INITIALIZED_NOT", "FALSE"])
    ALREADY_EXISTS = ReturnState(-4, ["ALREADY_EXISTS"])
    ALREADY_EXISTS_NOT = ReturnState(4, ["ALREADY_EXISTS_NOT"])
    CONTINUE = ReturnState(5, ["CONTINUE"])
    EXPECTING = ReturnState(-5, ["EXPECTING"])
    IS_RUNNING = ReturnState(6, ["IS_RUNNING"])
    IS_RUNNING_NOT = ReturnState(-6, ["IS_RUNNING_NOT"])
    FINISHED = ReturnState(7, ["FINISHED"])
    IS_FINISHED_NOT = ReturnState(-7, ["IS_FINISHED_NOT"])
