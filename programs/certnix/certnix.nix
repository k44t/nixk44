{ config, lib, pkgs, ... }@args:

with lib; with types;

let 

#  cfg = config.services.certnix;

#  pkg = cfg.package.out;





in


{

  imports = [ ];

  options = (import ./common.nix args).options // {
    enable = mkEnableOption "the Certificate Manager";

    package = mkOption {
      type = anything;
      description = "the generated derivation to be included in the path. read only.";
    };
    create-home = mkOption {
      type = bool;
      default = true;
      description = "create the home directory if it does not exist";
    };
    
    home = mkOption {
      type = str;
      default = "/var/lib/certnix";
    };
    
    authorities = (import ./authority.nix args).options.authorities;
    services = (import ./authority.nix args).options.services;
    clients = (import ./authority.nix args).options.clients;
  };
}
