#!/bin/python3
# ******************************************************************************
# - *-coding: utf-8 -*-
# (c) copyright 2024 Alexander Poeschl
# All rights reserved.
# Secrecy Level STRICTLY CONFIDENTIAL
# ******************************************************************************
# @file BetterEnumEntry.py
# @author Alexander Poeschl <apoeschlfreelancing@kwanta.net>
# @brief Implementation for EnumEntries that are better than normal enums entries (e.g. ERROR for ReturnState).
# ******************************************************************************
class BetterEnumEntry():
    value = 0
    name = "Unknown"
    alternative_names = [name]
    def __init__(self, *args):
        self.value = args[0]
        naming = args[1]
        if isinstance(naming, list):
            self.name = naming[0]
            self.alternative_names = set(naming)
        elif isinstance(naming, set):
            self.name = naming[0]
            self.alternative_names = naming
        elif isinstance(naming, str):
            self.name = naming
            self.alternative_names = [naming]
    def __str__(self):
        return self.name
    def __int__(self):
        return self.value
    def __bool__(self):
        if self.value > 0:
            return True
        else:
            return False
    def __eq__(self, value):
        if isinstance(value, tuple):
            value = value[0]
        return self.value == value
    def __ne__(self, value):
        if isinstance(value, tuple):
            value = value[0]
        return self.value != value
    def __gt__(self, value):
        if isinstance(value, tuple):
            value = value[0]
        return self.value > value
    def __lt__(self, value):
        if isinstance(value, tuple):
            value = value[0]
        return self.value < value
    def __ge__(self, value):
        if isinstance(value, tuple):
            value = value[0]
        return self.value >= value
    def __le__(self, value):
        if isinstance(value, tuple):
            value = value[0]
        return self.value <= value
    def ToInt(self):
        return self.value
    def ToString(self):
        return self.name
    def __hash__(self):
        return hash(self.value, self.name, self.alternative_names)