{
  description = "MCP server for memory management";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
        python = pkgs.python313;
        pythonPkgs = python.pkgs;

        mcp-memory = pythonPkgs.buildPythonApplication {
          pname = "mcp-memory-server";
          version = "0.2.0";
          pyproject = true;

          src = ./.;

          build-system = [ pythonPkgs.hatchling ];

          dependencies = [
            pythonPkgs.psutil
            pythonPkgs.pydantic
            (pythonPkgs.buildPythonPackage rec {
              pname = "fastmcp";
              version = "0.4.1";
              pyproject = true;

              src = pythonPkgs.fetchPypi {
                inherit pname version;
                hash = "sha256-cTrTuOTgSEHJ4vPKAisFOtuJoobO/60Naa57VvMcvmQ=";
              };

              build-system = [
                pythonPkgs.hatchling
                pythonPkgs.hatch-vcs
              ];

              dependencies = with pythonPkgs; [
                anyio
                httpx
                httpx-sse
                pydantic
                pydantic-settings
                sse-starlette
                starlette
                uvicorn
                opentelemetry-api
                opentelemetry-sdk
                exceptiongroup
                mcp
                typer
                python-dotenv
                jinja2
              ];

              doCheck = false;
            })
          ];

          doCheck = false;

          meta = {
            description = "MCP server for memory management";
            mainProgram = "mcp-memory";
          };
        };
      in {
        packages = {
          default = mcp-memory;
          mcp-memory = mcp-memory;
        };

        apps.default = {
          type = "app";
          program = "${mcp-memory}/bin/mcp-memory";
        };

        devShells.default = pkgs.mkShell {
          packages = [
            python
            pythonPkgs.pip
            pythonPkgs.pytest
            pythonPkgs.pytest-asyncio
            pythonPkgs.psutil
            pythonPkgs.pydantic
            pythonPkgs.mkdocs
            pythonPkgs.mkdocs-material
            pkgs.just
          ];

          shellHook = ''
            export PYTHONPATH="$PWD/src:$PYTHONPATH"
          '';
        };
      });
}
