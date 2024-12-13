{pkgs, ...}@args: {
  nixpkgs.overlays = [
    (final: prev: {
      # kmonad = (pkgs.callPackage <derivations/kmonad> {});

      list-input-devices = import <nixk44/scripts/list-input-devices.nix> args;

      start-kmonad = import <nixk44/scripts/start-kmonad.nix> args;



    })
  ];

}
