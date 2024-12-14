#!/bin/python3
# ******************************************************************************
# - *-coding: utf-8 -*-
# (c) copyright 2024 Alexander Poeschl
# All rights reserved.
# Secrecy Level STRICTLY CONFIDENTIAL
# ******************************************************************************
# @file BasicThread.py
# @author Alexander Poeschl <apoeschlfreelancing@kwanta.net>
# @brief Thread implementation you can use in python projects to extend your own custom thread class from.
# ******************************************************************************
from threading import Thread

class BasicThread:
    def task():
        pass
    thread = Thread(target=task)

    def __init(self, task, *args):
        thread = Thread(target=task)
        thread.start()
        thread.join()
        thread.is_alive
        thread.notify()

    def Start(self):
        self.thread.start()
    
    def Join(self):
        self.thread.join()

    def IsAlive(self):
        return self.thread.is_alive
    
    def Notify(self):
        self.thread.notify()
    
    def Wait
