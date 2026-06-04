{
  inputs.nixpkgs.url = "github:nixos/nixpkgs/nixos-26.05";

  outputs =
    { self, ... }@inputs:
    let
      inherit (inputs.nixpkgs) lib;

      supportedSystems = [
        "x86_64-linux"
        "aarch64-darwin"
      ];

      forEachSupportedSystem =
        f:
        lib.genAttrs supportedSystems (
          system:
          f {
            inherit system;
            pkgs = import inputs.nixpkgs {
              inherit system;
              config.allowUnfree = true;
            };
          }
        );
    in
    {
      devShells = forEachSupportedSystem (
        { pkgs, system }:
        let
          inherit (pkgs.lib) attrValues;

          python = pkgs.python314.withPackages (
            ps:
            attrValues {
              inherit (ps)
                debugpy
                ipython
                mypy
                coverage
                ;
            }
          );
        in
        {
          default = pkgs.mkShellNoCC {
            packages = attrValues {
              inherit (pkgs)
                just
                ;
              inherit python;
            };
          };
        }
      );
    };
}
