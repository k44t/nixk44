{pkgs, lib,  ...}@args:
pkgs.writeScriptBin "list-input-devices" (builtins.readFile ./list-input-devices.sh)
