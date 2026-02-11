{
  description = "Download YouTube subtitles and summarize them with Ollama";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  };

  outputs =
    { self, nixpkgs }:
    let
      forAllSystems =
        f:
        nixpkgs.lib.genAttrs [
          "x86_64-linux"
          "aarch64-linux"
          "aarch64-darwin"
          "x86_64-darwin"
        ] (system: f nixpkgs.legacyPackages.${system});

      yt-subs =
        pkgs:
        let
          python = pkgs.python3;
        in
        python.pkgs.buildPythonApplication {
          pname = "yt-subs";
          version = "1.0.0";
          pyproject = true;

          src = ./.;

          build-system = [ python.pkgs.setuptools ];

          dependencies = [ python.pkgs.yt-dlp ];

          nativeCheckInputs = [
            python.pkgs.pytestCheckHook
            python.pkgs.pytest-bdd
          ];
        };
    in
    {
      packages = forAllSystems (pkgs: {
        yt-subs = yt-subs pkgs;
        default = self.packages.${pkgs.stdenv.hostPlatform.system}.yt-subs;
      });

      devShells = forAllSystems (pkgs: {
        default = pkgs.mkShellNoCC {
          packages =
            let
              python = pkgs.python3;
              pythonWithPkgs = python.withPackages (ps: [
                ps.yt-dlp
                ps.pytest
                ps.pytest-bdd
              ]);
            in
            [
              pythonWithPkgs
              pkgs.ollama
            ];
        };
      });

      overlays.default = _final: prev: {
        yt-subs = yt-subs prev;
      };
    };
}
