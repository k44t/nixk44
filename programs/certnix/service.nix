{ config, lib, pkgs, ... }@args:
with lib; with types;
let
in
{
  options = {
    enable = mkEnableOption "this authority";

    local = mkOption {
      type = types.anything;
      default = {};
    };
    extended-key-usage = mkOption {
      type = types.anything;
      default = {};
    };
    
    ips = mkOption {
      type = listOf types.str;
      default = [];
    };
    dns = mkOption {
      type = listOf types.str;
      default = [];
    };
  } // (import ./common.nix args).options;
}
