#!/usr/bin/env bash
set -euo pipefail

# Sync version from pyproject.toml to flake.nix

NEW_VERSION=$(grep -oP '^version = "\K[^"]+' pyproject.toml)
OLD_VERSION=$(grep -oP 'version = "\K[^"]+' flake.nix | head -1)

echo "pyproject.toml version: $NEW_VERSION"
echo "flake.nix version: $OLD_VERSION"

if [ "$NEW_VERSION" = "$OLD_VERSION" ]; then
    echo "Versions match, nothing to do"
    exit 0
fi

echo "Updating flake.nix..."
sed -i "s/version = \"$OLD_VERSION\"/version = \"$NEW_VERSION\"/" flake.nix

if [ "${CI:-}" = "true" ]; then
    git config user.name "github-actions[bot]"
    git config user.email "github-actions[bot]@users.noreply.github.com"
    git add flake.nix
    git commit -m "fix: sync flake.nix version to $NEW_VERSION"
    git push
fi

echo "Done"
