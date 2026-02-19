# FlutterFlow App (Imported into Monorepo)

This folder is a **copy** of the FlutterFlow export that lives on the GitHub branch:
- `flutterflow`

It exists here so the monorepo branch can keep:
- backend (`atlas_core_new/`, `backend/`, etc.)
- docs (`docs/`)
- shared contracts
while still having the Flutter app code available for development.

## Why `lib/` may be missing

If you do not see a `lib/` folder in the FlutterFlow export, it is almost always because the
repository `.gitignore` included:

```
lib/
```

That line will cause Git to ignore the entire Flutter source directory.

Fix:
1. Update the `.gitignore` in the FlutterFlow-export branch to **not** ignore `lib/`.
2. Re-run **Push to GitHub** from FlutterFlow.
3. Then re-import the branch here.

## Re-import procedure (maintainers)

From the monorepo root:

```bash
git fetch origin flutterflow
rm -rf frontend/flutterflow_app
mkdir -p frontend/flutterflow_app
git archive origin/flutterflow | tar -x -C frontend/flutterflow_app
```

Then commit the updated `frontend/flutterflow_app/` directory.

## Notes

- FlutterFlow expects a Flutter project at repo root; this monorepo does not.
  Keeping a dedicated `flutterflow` branch is the cleanest compromise.
- This folder is intended to be buildable by Flutter tooling once `lib/` is present.
