{pkgs, lib,  ...}@args:
(import <lib/scripts.nix> args).mkBashScript "list-input-devices" (builtins.readFile ./list-input-devices.sh)