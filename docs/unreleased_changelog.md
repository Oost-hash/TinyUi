# Unreleased

Add entries here before running a release.
Version tags control which release an entry belongs to.

## Format

Use one line per change:
  - [0.3.1][tinycore] New provider registry API
  - [0.3.1][tinyui][fixed] Settings panel not opening from toolbar
  - [0.3.1][tinywidgets][removed] Legacy overlay shim
  - [0.3.2][plugins][changed] LMU connector now logs session transitions

Known packages:
  - app
  - plugins
  - tinycore
  - tinyui
  - tinywidgets
  - other

## Entries
- [0.3.5][tinycore][changed] Moved live consumer and provider participation into `tinycore.runtime.plugins`, including runtime-owned registry, lifecycle, bindings, provider registration, and subprocess runner paths, so `tinycore.plugin` keeps shrinking toward static plugin description only
- [0.3.5][tinycore][changed] Added a runtime-owned plugin facts seam over session-backed bindings and providers so plugin context, widgets, provider heat, and runtime diagnostics stop reading live participation state directly from `SessionRuntime`
- [0.3.5][tinycore][changed] Renamed live runtime participation around activation, participants, exports, and updates so the runtime graph, service API, and boot paths stop mixing older consumer, capability, lifecycle, and poll terminology into active code
- [0.3.5][tinycore][changed] Folded plugin participation facts, binding storage, and provider-bound controls into one smaller runtime seam so `tinycore.runtime.plugins.facts` owns the public runtime API while old `session` and `capabilities` concepts keep collapsing into exports and participation data
- [0.3.5][tinycore][removed] Removed the remaining `tinycore.plugin` runtime shims and the last `tinycore.poll` compatibility surface so live plugin participation and update driving now only exist under `tinycore.runtime`
- [0.3.5][tinycore][changed] Finished the runtime participation split by shrinking `PluginParticipationRuntime` to registration/orchestration only, renaming the last core `lifecycle` surface to `activation`, and moving provider activity, provider refresh, subprocess entry, and staged update driving under explicit runtime-owned modules
- [0.3.5][tinycore][changed] Finished the staged runtime update model around `refresh` and `derive` so provider refresh and widget state derivation now run through one transparent `RuntimeUpdateLoop` with stage-aware diagnostics and no active poll-era naming left in the runtime path
- [0.3.5][tinywidgets][changed] Renamed widget update mechanics around `WidgetStateParticipant` and the runtime update loop so overlay refresh, widget state derivation, and widget editing surfaces all speak the same participant/update language
- [0.3.5][tinydevtools][changed] Added a dedicated Runtime devtools tab that shows live runtime units, scheduling context, and parent/process relationships outside the state monitor view
- [0.3.5][tinydevtools][changed] Added a copy-all runtime overview action so the live runtime graph can be pasted into reviews while working through the next runtime cleanup pass
- [0.3.5][tinydevtools][changed] Turned the Runtime devtools view into a collapsible tree with state filters, column sorting, and resizable columns so host, provider, and plugin participation reads more like a real process/runtime inspector
- [0.3.5][tinydevtools][changed] Added runtime update stage visibility to the Runtime inspector so the staged `refresh` and `derive` flow is visible in both the live table and copied runtime overview
- [0.3.4][tinycore][fixed] Reduced the runtime inspector to generic snapshot registration and change tracking so plugin-specific devtools source composition no longer lives in core
- [0.3.4][plugins][fixed] Moved connector inspection ownership to the provider runtime through `inspect_snapshot()` so new plugins do not need central inspection schemas to become inspectable
- [0.3.4][tinycore][fixed] Added shared `AppPaths` ownership for source and frozen runtime roots so boot and QML loading stop rebuilding app paths locally
- [0.3.4][tinycore][fixed] Grouped config and settings services under explicit host persistence ownership so persisted state no longer hangs off `HostServices` as unrelated registries
- [0.3.4][tinycore][fixed] Moved widget state persistence into host-owned persistence services so widget layout and config are no longer stored through a separate tinywidgets-only path
- [0.3.4][tinycore][fixed] Tightened the persistence API behind host-facing methods and a plugin `ctx.config` surface so host and plugin code stop reaching through loose registries and loader internals
- [0.3.4][tinycore][fixed] Moved runtime boot, subprocess supervision, host worker ownership, and activation/state tracking into `tinycore.runtime` so app startup no longer owns the live process graph
- [0.3.4][tinycore][fixed] Moved provider activation, provider update routing, and the widget poll loop into runtime-owned services so session facts and widget code stop owning runtime heat and polling behavior
- [0.3.4][tinycore][fixed] Split runtime diagnostics into explicit log and runtime surfaces, removed `tinycore.inspect`, and moved log inspection under logging-owned diagnostics
- [0.3.4][tinycore][fixed] Added runtime scheduling metadata and a core-owned delayed scheduler so widget polling, devtools refresh, boot phases, and plugin grace timers share one runtime vocabulary
- [0.3.4][tinycore][fixed] Added a shared runtime-owned Qt timer adapter and scheduling driver metadata so runtime polling and diagnostics refresh stop building separate raw `QTimer` loops
- [0.3.4][tinycore][fixed] Normalized runtime boot into typed assembly and phase specs so optional devtools and host workers are described through the same boot pipeline instead of late special cases
- [0.3.4][tinycore][changed] Reduced the top-level `tinycore` and `tinycore.runtime` public APIs so runtime internals, diagnostics helpers, and host adapter glue no longer leak through broad package re-exports
- [0.3.4][tinycore][changed] Moved host/runtime service groupings and explicit runtime composition into dedicated `tinycore.services` and `tinycore.composition` modules so runtime boot no longer depends on an app container or `create_app` path
- [0.3.4][tinycore][removed] Removed `tinycore.app` after moving the remaining runtime boot and compatibility routes to explicit composition-owned entrypoints
- [0.3.4][tinycore][changed] Tightened package roots for `tinycore.diagnostics`, `tinycore.persistence`, `tinywidgets`, and `tinydevtools` so broad package-level grab-bags no longer define the public import surface
- [0.3.4][tinycore][fixed] Corrected runtime boot and shutdown ordering so the runtime inspector is attached before devtools state monitoring, `ui.main` reaches `running` before overlay workers start, and host worker shutdown no longer blocks on child runtime units that stop inside the worker callback
- [0.3.4][tinyui][changed] Moved TinyUI host assembly and UI adapter wiring into `tinyui.boot` and `tinyui.ui_adapters` so `tinycore.runtime` no longer imports TinyUI-specific boot, overlay, or devtools UI surfaces
- [0.3.4][tinyui][fixed] Routed settings dialog saves through explicit typed core viewmodel slots so enum and numeric settings no longer fail QML-to-Python conversion during save
- [0.3.4][other][removed] Retired the `app` package, moved the launcher entry path to `tinyui_boot`, and updated the build and script entrypoints to use the new bootloader directly
- [0.3.3][tinycore][changed] Split logging into product logging and optional diagnostics under `tinycore.logging`, removed the old `tinycore.log` shim, and moved startup timing output behind the diagnostics path
- [0.3.3][app][changed] Moved devtools runtime wiring behind an optional `tinydevtools.host.attach_runtime(...)` path so bootstrap can run without a direct devtools package dependency
- [0.3.3][tinyui][changed] Stopped treating Dev Tools as part of the main UI package by loading the devtools window through an optional QML loader and only showing the menu entry when devtools are available
- [0.3.3][plugins][fixed] Mirrored packaged `editors` and `widgets` files into the extracted runtime cache so packaged plugins can keep loading manifest files relative to their runtime module path
- [0.3.3][other][changed] Added a new `tinydevtools` package for the devtools viewmodels, host attachment, and QML window, updated the build script with a `--with-devtools` switch, and clear source-tree `__pycache__` and `*.pyc` files before packaging
- [0.3.2][plugins][changed] Rebuilt the LMU and rF2 connector stack into a single TinyUi-owned `LMU_RF2_Connector` family with shared contracts, source switching, full capability coverage, and no remaining legacy or vendor runtime dependency
- [0.3.2][tinycore][changed] Kept provider inspection contract-first while making the inspection schema more declarative, so connector-specific indexing and tuple selection now live in schema definitions instead of hard-coded string cases inside the runtime inspector
- [0.3.2][tinyui][changed] Added `Copy all`, source recording, and capture path copy actions to the state dev tools, then moved capture writes off the 200 ms refresh path and into a buffered flush flow that records to a user-writable app data location
- [0.3.1][app][changed] Cleaned up the startup import path to delay heavy UI and Qt loading, reducing a measured bootstrap profiling run from about 1.6s to about 0.48s
- [0.3.1][app][changed] Added built-in startup timing logs across manifest discovery, runtime bootstrap, Qt setup, QML load, and pre-run phases so boot costs are visible without ad-hoc profiling
- [0.3.1][plugins][changed] Added a packaged plugin build flow that outputs `runtime`, `widgets`, `editors`, `config/defaults`, `_internal`, and `manifest.lock`, with stricter manifest validation and direct support for deployable zip artifacts
- [0.3.1][plugins][changed] Packaged plugin manifests now load consumer and provider runtimes from `runtime/*.pkg`, preserve user config files on later syncs, and use explicit `widgets` and `editors` paths in the active packaged layout
- [0.3.1][tinycore][changed] Updated plugin manifest scanning for the packaged `_internal/plugin.toml` layout while keeping plugin paths resolved from the plugin root
- [0.3.1][app][changed] Updated the standalone build to use `_runtime`, package plugins into `dist/TinyUi/plugins`, separate app and plugin build steps, and expose clearer `build.py` CLI modes
- [0.3.1][app][changed] Added an internal packaged demo smoke path to verify packaged plugin discovery, runtime loading, and preserved user files in the new distribution flow
- [0.3.1][other][changed] Split release note rendering out of the mutating release flow and added `preview_release_notes.py` so version-tagged release notes can be reviewed without mutating `unreleased`
- [0.3.1][other][changed] Added project-scoped Zed and basedpyright configuration, then cleaned up the active `src` and `scripts` code paths so the current 0.3.1 scope type-checks cleanly while `lmu_connector` stays parked for the next update
- [0.3.1][tinyui][fixed] Fixed the state dev tool so live heartbeat and change updates keep the state list scroll stable, show the correct empty state, and allow quick copying of `key: value` entries
- [0.3.1][tinyui][changed] Replaced the bundled Linux icon font and legacy image set with dedicated SVG chrome assets for menu and window controls
- [0.3.1][tinyui][changed] Increased the custom title bar and menu chrome icons to a cleaner 16px SVG canvas with lighter strokes for better desktop readability
- [0.3.1][tinyui][removed] Removed the old icon glyph loader and unused chrome image/font assets after moving the title bar to direct SVG icons
