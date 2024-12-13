{ config, lib, pkgs, ... }@args:
with lib; with types;
let
in
{
  options = {
    local = mkOption {
      type = types.anything;
      default = {};
    };
    extended-key-usage = mkOption {
      type = types.anything;
      default = {};
    };

  } // (import ./common.nix args).options;
}
