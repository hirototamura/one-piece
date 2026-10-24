# Dataset storage and retrieval

Git holds source code, small canonical records and retrieval catalogs. GitHub
Release assets hold immutable, hash-identified run data. This avoids requiring
the original Mac folder layout or copying a complete workspace between hosts.

The first catalog is `datasets/integration_validation_20261024.json`. It indexes
42 datasets and 2,427 historical files. Thirty new archives are kept in the
private `hirototamura/balancing-cube-simulation` Release
`validation-archive-20261024`. Twelve previously published archives are reused
at their existing Release locations because their SHA-256 values match exactly.
Their existing public/private visibility is preserved; new evidence stays private.

The archive retains run outputs, acceptance receipts, historical source packs,
browser captures and validation helper scripts. Each top-level run or fixture is
independently retrievable. Git metadata, symlinks, virtual environments, build
directories, caches and disposable SQLite indexes are excluded. Original local
inputs are retained. An archive does not establish a verification pass or an
adopted engineering baseline.

## Use from another environment

Check out the One-Piece revision containing the catalog and install it with
`python -m pip install -e .`. Authenticate GitHub CLI as yourself (`gh auth login`)
for private assets. No credentials are stored in catalogs or copied from the Mac.

```sh
# Search metadata locally; no download is needed.
onepiece datasets list datasets/integration_validation_20261024.json --query qwen

# Restore one historical trial beneath the selected workspace.
onepiece datasets fetch datasets/integration_validation_20261024.json \
  --id qwen27b-memory10-results-20261012 --destination /path/to/workspace

# Check that the restored files still have their recorded hashes.
onepiece datasets verify datasets/integration_validation_20261024.json \
  --id qwen27b-memory10-results-20261012 --destination /path/to/workspace
```

Pass `--id` more than once to retrieve several datasets. `--path` limits restored
files to an exact logical path or directory prefix within the selected datasets.
The required dataset archive is downloaded once and cached by SHA-256 under
`~/.cache/onepiece/datasets`; subsequent restores reuse verified bytes. Use
`--cache` to select shared local storage or `--assets-dir` for an offline archive copy.
An existing file with different bytes stops the operation before new files are
installed. No overwrite option is provided.

Both archive and individual file sizes/hashes are checked. ZIP contents must
match the catalog, symlinks and unsafe paths are rejected, and selected files
are validated in staging before installation. Raw ZIP/tar source packages are
restored as evidence files; they are not automatically unpacked or executed.

Dataset retrieval restores historical workspace files. It does not import them
into the canonical store. Use the existing `onepiece import`/`fetch` commands to
import a One-Piece evidence bundle under its own record and hash checks.

## Add future datasets

```sh
onepiece datasets pack /path/to/evidence /path/to/prepared-assets \
  --repository hirototamura/balancing-cube-simulation \
  --release validation-YYYYMMDD --catalog-id validation-YYYYMMDD
```

Review the catalog and prepared archives, upload them to a new private Release,
then check remote asset hashes and perform a clean restore. Commit the catalog
to Git only after its locations are available. Do not replace an existing
published archive or rewrite old run data. Record new evidence as a new dataset
or revision. A catalog's location can later change storage providers while
retaining the expected file and archive hashes; the current fetch adapter uses
GitHub CLI and local offline assets.

[Requirements explorer](requirements_explorer.md) · [Engineering strategy](strategy.md)
