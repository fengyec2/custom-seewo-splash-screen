<!-- .github/copilot-instructions.md: guidance for AI coding agents working on this repo -->
# Copilot / AI agent instructions — custom-seewo-splash-screen

Purpose
- Help an AI agent be productive quickly: architecture, key files, developer workflows, and project-specific patterns.

Quick workflows
- Run locally: create a venv, install deps, then run the GUI
  - python -m venv .venv; .\.venv\Scripts\Activate.ps1; pip install -r requirements.txt
  - python main.py
- Build/package: this repo uses PyInstaller via the included spec and helper
  - python build.py  # produces build/SeewoSplash and dist artifacts; SeewoSplash.spec is the PyInstaller spec
<!-- - Update release version: edit or run the version helper
  - python create_version_file.py (writes/updates version_info.txt) -->

Big-picture architecture (files and responsibilities)
- main.py — app entrypoint that wires app_info, config and the UI.
- core/ — application logic and platform operations
  - core/config_manager.py — central config read/write; uses `utils.resource_path.get_app_data_path`
  - core/image_manager.py — reads presets from `assets/presets` (uses `get_resource_path("assets/presets")`)
  - core/replacer.py, file_protector.py — platform-specific file operations used.
- ui/ — all GUI code (PyQt6). Key files:
  - ui/main_window.py — main window, sets window icon via get_resource_path("assets/icon.ico")
  - ui/controllers/ — controller classes (image_controller.py, path_controller.py, permission_controller.py)
  - ui/widgets/ — reusable widgets (image_list.py, action_bar.py, path_card.py)
- utils/resource_path.py — crucial helper: abstract resource paths for both local run and PyInstaller bundle. Always use it to load assets.
- assets/ — images and presets shipped with the app. Prefers reading via resource helpers, not hard-coded relative paths.

Project-specific patterns and conventions
- Resource loading: always call `get_resource_path(...)` from `utils.resource_path` when referencing files under `assets/` so the code works both in-source and in a PyInstaller bundle. Example: `QIcon(get_resource_path("assets/icon.ico"))` in `ui/main_window.py`.
- Config and data directories: runtime config is read/written through `core/config_manager.py` and stored under app data paths resolved with `get_app_data_path()`.
- UI separation: controllers contain logic (ui/controllers/*.py) and widgets implement presentation (ui/widgets/*.py). Prefer modifying controller behavior rather than embedding logic in widget classes.
- Packaging: `build.py` orchestrates PyInstaller packaging (spec: `SeewoSplash.spec`). After packaging, inspect `build/SeewoSplash` outputs for analysis artifacts.

Integration points / external dependencies
- PyQt6 and PyQt6-Fluent-Widgets — UI framework (see `requirements.txt`).
- Pillow — image handling.
- PyInstaller — used indirectly via `build.py`/`.spec` to build executables.

What an AI agent should do first (priority list)
1. Use `utils/resource_path.get_resource_path` for any new asset access.
2. Inspect `ui/controllers/image_controller.py` and `core/image_manager.py` for image-handling flows before changing UI/image logic.
3. When changing config, update `core/config_manager.py` and ensure `config.json` default values remain valid.
4. If editing startup/packaging behavior, run `python build.py` locally and verify `build/SeewoSplash` contents.

Examples to cite in suggestions
- Loading assets: `QIcon(get_resource_path("assets/icon.ico"))` in `ui/main_window.py`.
- Presets directory: `self.preset_dir = Path(get_resource_path("assets/presets"))` in `core/image_manager.py`.
- Config app data: `get_app_data_path()` invoked from `core/config_manager.py`.

Notes / constraints
- No automated tests are present in the repo; be conservative with cross-file edits and verify by running `python main.py` or `python build.py`.
- Keep UI changes small and test in a virtualenv with `PyQt6` installed.

If anything here is unclear or you want examples added (code snippets, more file references, or packaging notes), tell me which areas to expand.
