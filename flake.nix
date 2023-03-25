{
  inputs.flake-utils.url = "github:numtide/flake-utils";
  inputs.nixpkgs.url = "github:NixOS/nixpkgs";

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
        pyproject = builtins.fromTOML(builtins.readFile(./pyproject.toml));
        name = pyproject.tool.poetry.name;
        default-python = pkgs.python311;
        nix-dev-dependencies = [
          pkgs.poetry
        ];
      in {
        devShell = pkgs.mkShell {
          buildInputs = nix-dev-dependencies ++ [default-python];
          shellHook = ''
            if [ ! -f poetry.lock ] || [ ! -f build/poetry-$(sha1sum poetry.lock | cut -f1 -d' ') ]; then
                poetry install --sync
                if [ ! -d build ]; then
                    mkdir build
                fi
                touch build/poetry-$(sha1sum poetry.lock | cut -f1 -d' ')
            fi
            export PREPEND_TO_PS1="(${name}) "
            export PYTHONNOUSERSITE=true
            export VIRTUAL_ENV=$(poetry env info --path)
            export PATH=$VIRTUAL_ENV/bin:$PATH
            #export LD_LIBRARY_PATH=${pkgs.gcc-unwrapped.lib}/lib:$LD_LIBRARY_PATH
          '';
        };
      });
}
