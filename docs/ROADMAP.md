# Roadmap

TinyUi tracks roadmap items latest-first.

## Next

These are on the radar, not tied to a release yet:

- Widget globals (font, background, opacity, layout)
- Processing / derived data layer
- Game detection and automatic source handoff inside provider families
- Provider selection UI
- Editor surface for compounds, vehicle-specific data, and other user-managed plugin data
- Spotter?
- Custom widgets
- Grouping widgets

---

# Released

## 0.4.0 — Runtime consolidation

This release rewrote the shape of TinyUi's core. `tinycore.runtime` is now the
live execution owner. The old `app`, `session`, `capabilities`, and `poll` layers
are gone. Plugin participation, process supervision, scheduling, staged updates,
and runtime diagnostics all live under one coherent runtime model.

- [x] Replace the `App` container and flat registry boot path with explicit host/runtime composition
- [x] Move live plugin participation into `tinycore.runtime.plugins` (activation, providers, exports, subprocess lifecycle)
- [x] Introduce staged update model with explicit `refresh` and `derive` phases driven by one `RuntimeUpdateLoop`
- [x] Build a runtime graph with declared units, process relationships, scheduling metadata, and live state
- [x] Add a runtime inspector with devtools Runtime tab: tree view, state filters, sorting, update-stage visibility
- [x] Remove `session`, `capabilities`, and `poll` as architectural owners
- [x] Clean up runtime vocabulary around activation, participants, exports, update, and runtime

## 0.3.3 — tinyDevTools and release logging

This step separated development tooling from the main app runtime so release
builds stay smaller and quieter.

- [x] Move devtools into their own `tinydevtools` package
- [x] Keep `tinyui` focused on the app UI instead of dev-only tooling
- [x] Split minimal product logging from development diagnostics
- [x] Keep release logging to `info`, `warning`, and `error`
- [x] Make release builds work without the devtools package present

## 0.3.2 — Connector consolidation

This step pulled connector-related submodule work into one coherent
TinyUi-owned program shape so the integration surface is easier to maintain
and easier to inspect.

- [x] Consolidate LMU, rF2, and mock into one connector family
- [x] Replace the old connector/submodule layout with a TinyUi-owned runtime, contracts, sources, and shared-memory layer
- [x] Keep full capability coverage inside the new connector family
- [x] Remove legacy and vendor runtime dependencies from the active connector path
- [x] Add copy-all and snapshot recording tools so live sessions can be captured for later analysis

## 0.3.1 — Foundation extension and release cleanup

This update made the platform cleaner and more stable before adding a larger
wave of user-facing features.

- [x] Improve startup behavior and reduce eager loading
- [x] Clean up the build output and distribution structure
- [x] Define the plugin packaging direction

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

This release got live data onto the screen with the first usable widget workflow.

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
