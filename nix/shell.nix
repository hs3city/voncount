{ self, ... }:
{
  perSystem =
    { pkgs, system, ... }:
    with pkgs;
    {
      devShells.default = mkShell {
        buildInputs = [
          self.checks.${system}.pre-commit-check.enabledPackages
          hatch
        ];

        shellHook = '''' + self.checks.${system}.pre-commit-check.shellHook;
      };

    };
}
