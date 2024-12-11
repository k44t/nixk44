
import os
import shutil
import re
from natsort import natsorted

import argparse

# Create the parser
parser = argparse.ArgumentParser(description="virtual machine worker")

subparser = parser.add_subparsers(help='Commands', required=True)

shared_parser = argparse.ArgumentParser()
shared_parser.add_argument("vmname" , help="Name of the virtual machine.")

external_parser = argparse.ArgumentParser("existing vm")
external_parser.add_argument("--path", type=str)

# Add arguments
create_parser = subparser.add_parser('create', parents=[shared_parser], help='create a new virtual machine.')
mount_parser = subparser.add_parser('mount', parents=[shared_parser], help='mount an already existing virtual machine.')
unmount_parser = subparser.add_parser('unmount', parents=[shared_parser], help='unmount an already existing virtual machine.')
resize_parser = subparser.add_parser('resize', parents=[shared_parser], help='resize an already existing virtual machine.')
install_parser = subparser.add_parser('install', parents=[shared_parser, external_parser], help='install an already existing virtual machine.')
enter_parser = subparser.add_parser('enter', parents=[shared_parser, external_parser], help='enter an already existing virtual machine.')

args = parser.parse_args()

def create(args):
    pass

def mount(args):
    pass

def unmount(args):
    pass

def resize(args):
    pass

def install(args):
    if args.path != None:
        # install under this path, and ignore the vmname
    else:
        # install under vmname

def enter(args):
    if args.path != None:
        # install under this path, and ignore the vmname
    else:
        # install under vmname


create_parser.set_defaults(func=create)

mount_parser.set_defaults(func=mount)

unmount_parser.set_defaults(func=unmount)

resize_parser.set_defaults(func=resize)

install_parser.set_defaults(func=install)

enter_parser.set_defaults(func=enter)

args.func(args)

