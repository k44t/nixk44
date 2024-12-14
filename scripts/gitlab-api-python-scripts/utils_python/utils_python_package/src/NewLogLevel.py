#!/bin/python3
# ******************************************************************************
# - *-coding: utf-8 -*-
# (c) copyright 2024 Alexander Poeschl
# All rights reserved.
# Secrecy Level STRICTLY CONFIDENTIAL
# ******************************************************************************
# @file NewLogLevel.py
# @author Alexander Poeschl <apoeschlfreelancing@kwanta.net>
# @brief creates a new LogLevel enumeration element
# ******************************************************************************
class NewLogLevel():
    value = None
    names = []
    def __init__(self, value, names):
        self.value = value
        self.names = names
    @classmethod
    def __new__(cls, *args):
        return super(NewLogLevel, cls).__new__(cls)