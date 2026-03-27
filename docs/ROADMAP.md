# Roadmap

TinyUi tracks roadmap items latest-first.

## Next update: still being planned

The next update is not locked yet. The current roadmap is a live document and
will be adjusted once the next scope is clearer.

## 0.3.3 — tinyDevTools and release logging

This step is about separating development tooling from the main app runtime so
release builds stay smaller, quieter, and easier to reason about.

Planned direction:

- [ ] Move devtools into their own `tinyDevTools` / `tinydevtools` package
- [ ] Keep `tinyui` focused on the app UI instead of dev-only tooling
- [ ] Split minimal product logging from development diagnostics
- [ ] Keep release logging to `info`, `warning`, and `error`
- [ ] Make release builds work without the devtools package present
- [ ] Prepare the diagnostics boundary so heavier tooling can later move into its own thread or process

## Later

These are on the radar, but not tied to a release yet:

- Processing / derived data layer
- Editor surface for compounds, vehicle-specific data, and other user-managed plugin data.
- Spotter?
- Custom widgets
- Grouping widgets
- Provider selection UI
- Game detection and source handoff inside provider families
- Widget globals (fonts, bkg_color, size, layout)

## 0.3.2 — Connector consolidation

This step pulled the connector-related submodule work into one coherent
TinyUi-owned program shape so the integration surface is easier to maintain and
easier to inspect.

Completed:

- [x] Consolidate LMU, rF2, and mock into one connector family
- [x] Replace the old connector/submodule layout with a TinyUi-owned runtime, contracts, sources, and shared-memory layer
- [x] Keep full capability coverage inside the new connector family
- [x] Remove legacy and vendor runtime dependencies from the active connector path

Bonus goals completed:

- [x] Add copy-all and snapshot recording tools so live sessions can be captured for later analysis
- [x] Keep connector inspection contract-first so Dev Tools read normalized provider data instead of bolting more discovery logic into the live app path

## 0.3.1 — Foundation extension and release cleanup

This update was about making the platform itself cleaner and more stable before
adding a larger wave of user-facing features.

Focus areas:

- build and distribution cleanup
- startup cleanup
- plugin packaging

Completed:

- [x] Improve startup behavior and reduce eager loading
- [x] Clean up the build output and distribution structure
- [x] Define the plugin packaging direction

# Released

## 0.3.0 — Runtime contracts and plugin split

This release defined the runtime more explicitly: clear plugin roles, explicit
requirements, and binding through contracts instead of plugin-specific wiring.

- [x] Define the new plugin manifest shape around explicit roles and `requires`
- [x] Separate provider-side plugins from consumer-side plugins
- [x] Replace plugin-name-based connector lookup with capability-based binding
- [x] Define the session/runtime services that own activation, binding, and health state
- [x] Improve debugging around runtime state, active bindings, and provider health
- [x] Define the widget-facing data contract model
- [x] Move widget data flow away from direct connector traversal

## 0.2.0 — Widget renderer

This release got live data onto the screen with the first usable widget
workflow.

- [x] Widget system — define and render overlay widgets from plugin data
- [x] Layout engine — position, resize, and stack widgets on screen
- [x] Widget config — per-widget settings via the data-driven config system

## 0.1.0 — Foundation

This release laid down the base: the runtime, the UI shell, and the first
working telemetry connector.

- [x] Plugin system — lifecycle, isolation, subprocess support
- [x] Data-driven config — TOML for plugin definitions, JSON for user data
- [x] QML overlay — windowing, theming, tab layout
- [x] First telemetry contract layer
- [x] LMU connector — first real game connector (Le Mans Ultimate / rFactor 2)
