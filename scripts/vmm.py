
import os
import shutil
import re
from natsort import natsorted

import argparse

# Create the parser
parser = argparse.ArgumentParser(description="virtual machine worker")

subparser = parser.add_subparsers(required=True)

shared_parser = argparse.ArgumentParser(add_help=False)
shared_parser.add_argument("vmname", type=str, help="the name of the vm")

external_parser = argparse.ArgumentParser(add_help=False)
external_parser.add_argument("--path", type=str, help="path to where the nixos installation is mounted")


zvol_parser = argparse.ArgumentParser(add_help=False)
zvol_parser.add_argument("--zvol-parent-path", required=True, help="the zfs parent path under which to create the block devices")


# Add arguments
create_parser = subparser.add_parser('create', parents=[shared_parser, zvol_parser], help='checks if the virtual machine already exists, otherwise creates the virtual machine')
mount_parser = subparser.add_parser('mount', parents=[shared_parser], help='mount an already existing virtual machine.')
unmount_parser = subparser.add_parser('unmount', parents=[shared_parser], help='unmount an already existing virtual machine.')
resize_parser = subparser.add_parser('resize', parents=[shared_parser, zvol_parser], help='resize an already existing virtual machine.')
install_parser = subparser.add_parser('install', parents=[shared_parser, external_parser], help='install an already existing virtual machine.')
enter_parser = subparser.add_parser('enter', parents=[shared_parser, external_parser], help='enter an already existing virtual machine.')

create_parser.add_argument("--data-only", dest="data_only", help="wether to ONLY create a data disk.")
create_parser.add_argument("--no-data", dest="no_data", help="wether to NOT create a data disk.")

resize_parser.add_argument("--data", help="whether to resize the data volume")


def execute_command(command):
    return os.popen(command).read()
def yes(question):
    print(question + " (type yes):")
    is_sure = input()
    return is_sure == "yes"
def create(args):
    if yes("are you sure?"):
        if not args.data_only:
            # create main disk
            blockdev = f"/dev/zvol/{args.zvol_parent_path}/vm-{vmname}-vda"
            execute_command(f"parted {blockdev} --mklabel gpt")
            execute_command(f"parted {blockdev} --mklabel gpt")
            pass
        if not args.no_data:
            # create data disk
            blockdev = f"/dev/zvol/{args.zvol_parent_path}/{vm-nama}-data"
            pass
        else:

def mount(args):
    pass
# echo mount host; set name eg-esh; set division ''; mkdir -p /mnt/$name; zpool import $name -f -R /mnt/$name -N; mount -t zfs $name/fsroot /mnt/$name/; mount -t zfs $name/etc /mnt/$name/etc; mount -t zfs $name/nix /mnt/$name/nix; mount -t zfs $name/data /mnt/$name/data; zfs mount $name/data; zpool import $name-data -f -R /mnt/$name; mount -t zfs $name-data /mnt/$name/data; zfs mount $name-data; mount /dev/disk/by-partlabel/$name$division-boot /mnt/$name/boot; mount -o bind /mnt/$name/data/home/ /mnt/$name/home/; mount -o bind /mnt/$name/data/root/ /mnt/$name/root/

def unmount(args):
    pass
    # set name moria; echo unmount host $name; umount -R /mnt/$name; zpool export $name; zpool export $name-data

def resize(args):
    blockdev = f"/dev/zvol/{args.zvol_parent_path}/"
    pass

def install(args):
    if args.path != None:
        # install under this path, and ignore the vmname
        pass
    else:
        # install under vmname
        pass

def enter(args):
    if args.path != None:
        # install under this path, and ignore the vmname
        pass
    else:
        # install under vmname
        pass


create_parser.set_defaults(func=create)

mount_parser.set_defaults(func=mount)

unmount_parser.set_defaults(func=unmount)

resize_parser.set_defaults(func=resize)

install_parser.set_defaults(func=install)

enter_parser.set_defaults(func=enter)

args = parser.parse_args()

args.func(args)

