{ inputs, ... }:
{
  imports = [ inputs.treefmt-nix.flakeModule ];
  perSystem =
    { config, pkgs, ... }:
    let
      fmt_excludes = [
        "flake.lock"
        ".vscode/extensions.json"
        "data"
        "package-lock.json"
      ];
    in
    {
      formatter = config.treefmt.build.wrapper;

      treefmt = {
        projectRootFile = "flake.nix";

        settings.global.excludes = fmt_excludes;

        settings.formatter = {
          ini = {
            command = "${pkgs.gnused}/bin/sed";
            options = [
              "-i"
              "-e"
              "s/^[ \\t]\\+/\\t/"
            ];
            includes = [ "*.ini" ];
          };
          pinact = {
            options = [
              "--verify"
            ];

          };
        };

        programs = {
          actionlint = {
            enable = true;
          };
          biome = {
            enable = true;
          };
          clang-format = {
            enable = true;
          };
          deadnix = {
            enable = true;
          };
          dos2unix = {
            enable = true;
          };
          mdformat = {
            enable = true;
          };
          nixfmt = {
            enable = true;
          };
          pinact = {
            enable = true;
          };
          ruff-format = {
            enable = true;
          };
          taplo = {
            enable = true;
          };
        };
      };
    };
}
