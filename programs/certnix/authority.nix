{ config, lib, pkgs, ... }@args:
with lib; with types;
{
  options = # mkMerge [
    {
      enable = mkEnableOption "this authority";

      # not inheritable!
      revoked = mkOption {
        
        # this is represented as a hex number, thus a string
        type = attrsOf (submodule {
          options = {
            serial = mkOption {
              type = either int str;
              description = "often specified as a hex string";
              default = null;
            };
            reason = mkOption {
              type = nullOr (strMatching "unspecified|keyCompromise|CACompromise|affiliationChanged|superseded|cessationOfOperation|certificateHold|removeFromCRL");
              default = null;
            };
          };
        });
        default = {};
      };
      
      
      authorities = mkOption {
        type = attrsOf (submodule (import ./authority.nix));
        default = {};
      };
      
      services = mkOption {
        type = attrsOf (submodule (import ./service.nix));
        default = {};
      };
      
      clients = mkOption {
        type = attrsOf (submodule (import ./client.nix));
        default = {};
      };
    }
    // (import ./common.nix args).options
  # ]
  ;
}
