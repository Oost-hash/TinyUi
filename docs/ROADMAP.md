# Roadmap

TinyUi tracks roadmap items latest-first so the current direction is visible
without scrolling through older releases first.

## Current focus: 0.4.0

This update is about making the platform itself cleaner and more stable before
adding a larger wave of user-facing features.

### 0.4.0 — Platform cleanup and release structure

Focus areas:

- build and distribution cleanup
- startup cleanup
- plugin packaging direction
- clearer docs and project framing

Planned:

- [ ] Improve startup behavior and reduce eager loading
- [ ] Clean up the build output and distribution structure
- [ ] Define and stabilize the plugin packaging direction
- [ ] Move roadmap and project planning into clearer docs
- [ ] Improve project framing in the README and supporting docs

## 0.5.0 — UI contracts, widget globals, and interaction

Once the platform and packaging direction are cleaner, the focus can shift to
day-to-day overlay usability.

Planned:

- [ ] Implement widget global settings
- [ ] Implement hotkey support
- [ ] Add clear runtime indicators for things like hotkeys and game connection
- [ ] Improve the day-to-day interaction model around overlay usage

## Later

These are on the radar, but not tied to a release yet:

- Processing / derived data layer
- Spotter?
- Custom widgets
- Grouping widgets
- Provider selection UI
- Game detection and source handoff inside provider families
- More connectors and capability coverage

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
