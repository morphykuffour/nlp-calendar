{
  description = "NLP Calendar - Natural language calendar event creation";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
        pythonEnv = pkgs.python312.withPackages (ps: with ps; [
          openai
        ]);
      in
      {
        devShells.default = pkgs.mkShell {
          packages = [ pythonEnv ];

          shellHook = ''
            echo "NLP Calendar environment loaded"
            echo "Run: python nlp_calendar.py \"your event description\""
          '';
        };

        packages.default = pkgs.writeShellScriptBin "nlp-calendar" ''
          # Load API key from config file if not already set
          CONFIG_FILE="$HOME/.config/nlp-calendar/env"
          if [ -z "$OPENAI_API_KEY" ] && [ -f "$CONFIG_FILE" ]; then
            set -a
            source "$CONFIG_FILE"
            set +a
          fi
          exec ${pythonEnv}/bin/python ${./nlp_calendar.py} "$@"
        '';

        apps.default = {
          type = "app";
          program = "${self.packages.${system}.default}/bin/nlp-calendar";
        };
      }
    );
}
