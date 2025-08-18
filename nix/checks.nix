{ inputs, ... }:
{
  imports = [ inputs.git-hooks.flakeModule ];
  perSystem =
    {
      lib,
      config,
      system,
      ...
    }:
    let

      # don't check these
      check_excludes = [
        "flake.lock"
      ];

      mkHook =
        prev:
        lib.attrsets.recursiveUpdate {
          excludes = check_excludes;
          enable = true;
          fail_fast = false;
          verbose = true;
        } prev;
    in
    {

      checks = {
        pre-commit-check = inputs.git-hooks.lib.${system}.run {
          src = ../.;
          hooks = {
            # make sure our nix code is of good quality before we commit
            statix = mkHook { };
            deadnix = mkHook { };

            # ensure we have nice formatting
            treefmt = mkHook { package = config.treefmt.build.wrapper; };

            # Git police
            check-merge-conflicts = mkHook { };
            commitizen = mkHook { };

            # Various Artists
            # check-added-large-files = mkHook { };
            check-case-conflicts = mkHook { };
            detect-private-keys = mkHook { };
            fix-byte-order-marker = mkHook { };
            mixed-line-endings = mkHook { };
            end-of-file-fixer = mkHook { };

            # Python
            pyupgrade = mkHook { };
            ruff = mkHook { };

            # Spellchecking
            typos = mkHook { };
          };
        };
      };
    };
}
