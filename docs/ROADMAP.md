# Roadmap

TinyUi tracks roadmap items latest-first so the current direction is visible
without scrolling through older releases first.

## Current focus: 0.3.1

This update is about making the platform itself cleaner and more stable before
adding a larger wave of user-facing features.

### 0.3.1 — Foundation extension and release cleanup

Focus areas:

- build and distribution cleanup
- startup cleanup
- plugin packaging

Planned:

- [ ] Improve startup behavior and reduce eager loading
- [ ] Clean up the build output and distribution structure
- [ ] Define and stabilize the plugin packaging direction
- [ ] Move roadmap and project planning into clearer docs
- [ ] Improve project framing in the README and supporting docs

## 0.3.2 — Connector consolidation

This step is about pulling the connector-related submodule work into one more
coherent program shape so the integration surface is easier to maintain.

Planned:

- [ ] Consolidate the connector submodules
- [ ] Reduce connector-specific fragmentation in the current workflow

## Later

These are on the radar, but not tied to a release yet:

- Offload the original connector submodule into its own repository once the integration boundary is clean
- Processing / derived data layer
- Spotter?
- Custom widgets
- Grouping widgets
- Provider selection UI
- Game detection and source handoff inside provider families

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
