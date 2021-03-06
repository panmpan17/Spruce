import pygame
import os
from color import clr
from enviroment import AIR

from pygame_extendtion import *

# class Job:
    # 

class WORK:
    BUILD = "build"
    CHOP = "chop_tree"
    MOVEITEM = "move_item"
    MOVE = "move"
    PRODUCE = "produce"
    OPEN_STORAGE = "open_storage"
    GO_FARM = "open_farm"
    CAPTURE_ANIMAL = "capture_animal"
    BRING_ANIMAL = "bring_animal_to_farm"
    CLEAR_ITEM = "go_storage_clear_unforced_item"
    CLEAR_BUILD_INV = "clear_building_inventory"
    GO_MINE = "go_mine"
    GO_SURFACE = "go_surface"
    MINE_BLOCK = "mining"
    SMELTING = "smelting"
    DO_BUILDING_JOB = "do_building_job"

class Working:
    def __init__(self, type_, location, work_args):
        self.type = type_
        self.args = work_args
        self.location = location

        self.progress = 0

        if type_ == WORK.CHOP:
            self.progress_need = 1
        elif type_ == WORK.MINE_BLOCK:
            self.progress_need = 1
        elif type_ == WORK.DO_BUILDING_JOB:
            self.progress_need = self["work"]["time"]

    def __repr__(self):
        return f"{self.type} {self.args}"

    def __getitem__(self, key):
        return self.args[key]

    def parse(self):
        pass

class JobControler:
    def __init__(self):
        self.queue = []
        self.auto_drop_unforced = True
        self.evnCtlr = None

    def setUpCtlr(self, evnCtlr):
        self.evnCtlr = evnCtlr

    def put(self, work_type, location, work_args):
        self.queue.append(Working(work_type, location, work_args))

    def get(self, location):
        new_work = None
        remove_job = []
        for i, job in enumerate(self.queue):
            if job.location == location:

                if job.type == WORK.MINE_BLOCK:
                    x,y = job.args["id"]
                    if self.evnCtlr.present_layer.map[y][x] == AIR:
                        remove_job.append(i)
                        continue

                new_work = job
                remove_job.append(i)
                break

        remove_job.reverse()
        for job_i in remove_job:
            self.queue.pop(job_i)

        return new_work

