# LMU Connector Design Note

This is an internal design note for the `lmu_connector` work.

The goal is not to jump straight into implementation. The goal is to make the intended shape of the LMU connector explicit, show the cascade it creates across the runtime, and make the next code steps easy to approve or redirect.

---

# 1. Why Start With LMU

LMU is the best place to start because it already exists in two forms:

* embedded in the old `demo` plugin shape
* partially extracted into `src/plugins/lmu_connector/`

That makes it the right pressure test for the new runtime.

If we can define LMU cleanly as a first-class runtime unit, we get a concrete answer to these questions:

* what a provider-side plugin looks like
* what the manifest needs to say
* what the host has to discover and instantiate
* how widgets or consumer-side plugins should bind to it

---

# 2. Current State

## 2.1 What Exists

There is already a package at:

* `src/plugins/lmu_connector/`

It contains:

* `plugin.toml`
* `connector/lmu.py`

The manifest currently says:

```toml
name = "lmu_connector"
type = "connector"
provides = "telemetry.lmu"

[connector]
module = "plugins.lmu_connector.connector.lmu"
class  = "LMUConnector"
```

The connector implementation in `connector/lmu.py` is real and substantial. It already implements the full `TelemetryReader` contract, but it does so as one large monolithic object.

---

## 2.2 What Is Still True In The Runtime

The current runtime still expects the old manifest shape:

* top-level `module`
* top-level `class`
* optional `[connector]`
* optional `[mock_connector]`
* optional `[widgets]`

That means the new `lmu_connector/plugin.toml` does not fit the current loader in `src/tinycore/plugin/manifest.py`.

So right now the LMU connector exists as a design signal, not as a runtime-compatible plugin.

---

# 3. Proposed Role Of LMU Connector

The LMU connector should become the first real **provider-side plugin** in the new runtime.

Its job is narrow:

* connect to LMU / rFactor 2 shared memory
* expose telemetry capabilities
* publish or provide runtime data
* stay independent from widgets and consumer-side UI concerns

It should not own:

* widgets
* overlay rendering
* UI logic
* game-specific presentation decisions

That separation is the whole point of starting here.

---

# 4. Proposed Design Direction

## 4.1 External Runtime Identity

The plugin should be treated as a provider plugin.

Recommended identity:

```toml
name = "lmu_connector"
type = "plugin.provider"
version = "0.1.0"
```

I would keep the package name `lmu_connector` for now.

Why:

* it matches the current folder
* it describes what it is today
* renaming to `lmu_provider` can be done later if we decide that all provider plugins should use `*_provider`

The runtime contract matters more than the folder name at this stage.

---

## 4.2 Internal Runtime Shape

The current `LMUConnector` is doing too much at once.

It owns:

* shared memory lifecycle
* raw data access
* car data
* tyre data
* timing data
* session and track state
* opponents and standings
* driver inputs

That makes the code harder to navigate, and it also hides the actual shape of the runtime. If everything comes from one big connector object, it is much less obvious which part of the system is responsible for which data.

The cleaner split is:

* one shared LMU source/runtime object underneath
* multiple domain providers on top of it

Recommended shape:

* `LMUSource` or `LMURuntime`
  * owns shared memory `open / update / close`
  * holds the current LMU frame/state
  * is the only thing that talks directly to the LMU shared memory layer
* `LMUStateProvider`
* `LMUSessionProvider`
* `LMUTrackProvider`
* `LMUCarProvider`
* `LMUTyreProvider`
* `LMUTimingProvider`
* `LMUOpponentsProvider`
* `LMUInputsProvider`

That gives a much clearer mental model:

* one source of truth for LMU data
* one provider per responsibility
* no repeated shared memory ownership

It also makes debugging much easier because each part of the runtime has a clear owner.

---

## 4.3 Exported Capabilities

With the provider split above, the LMU plugin should be able to export multiple capabilities instead of one broad monolith.

Suggested capability set:

```toml
exports = [
  "telemetry.state.v1",
  "telemetry.session.v1",
  "telemetry.track.v1",
  "telemetry.car.v1",
  "telemetry.tyre.v1",
  "telemetry.timing.v1",
  "telemetry.opponents.v1",
  "telemetry.inputs.v1"
]
```

This is the more honest shape:

* the exported capabilities match the real provider boundaries
* each domain has a clear owner
* consumers have to move toward the new runtime instead of depending on a bridge

---

## 4.4 Runtime Implementation

The first runtime implementation does not need separate shared memory ownership per provider.

The right shape is:

* one LMU source/runtime object created once
* domain providers constructed around that shared source

So the current `LMUConnector` should not be the final center of the design.

Instead, it should be gradually broken apart until the underlying source/providers become the real runtime API.

---

## 4.5 Why This Split Matters

This split is not just about prettier code.

It directly improves:

* ownership: everyone can see which provider owns which data
* capability design: exports map naturally to domain responsibilities
* consumer design: consumers can ask for exactly what they need
* testing: smaller providers are easier to test than one giant connector
* debugging: state and failures are easier to isolate

---

## 4.6 Clean Break Rule

I do not recommend a compatibility bridge here.

Reason:

* compatibility layers are easy to add and painful to remove
* they keep old assumptions alive for too long
* they make the runtime harder to reason about

So the rule for this work should be:

* build the LMU side in the correct shape
* accept that downstream code will need to be updated after that
* let the breakage show us exactly where the old assumptions still live

That is stricter, but it keeps the architecture honest.

---

# 5. Cascade By Layer

The LMU connector itself is not the hard part. The cascade around it is where most of the work is.

## 5.1 Manifest Layer

Required changes:

* `PluginManifest` must support plugin roles
* it must understand `type = "plugin.provider"`
* it must support `exports`
* it must support `[provider]`

Suggested result:

* one manifest loader that can parse both provider-side and consumer-side plugin declarations
* the parsed manifest should tell the host what runtime role a plugin plays

Immediate implication:

* `src/tinycore/plugin/manifest.py` must stop assuming every plugin has one top-level subprocess plugin class

---

## 5.2 Composition Root

The current composition root in `src/app/main.py` does this:

* discovers manifests
* creates subprocess plugins from `module` + `class`
* separately instantiates host-side connectors from `[connector]`
* registers those connectors by plugin name

That does not fit the LMU connector shape.

If `lmu_connector` is a provider plugin, the composition root needs to stop thinking in terms of:

* "every manifest becomes a subprocess plugin"
* "connectors are optional extra attachments to plugins"

Instead it needs to think in terms of:

* provider plugins
* consumer plugins
* different registration paths for each

Immediate implication:

* `src/app/main.py` will need a first split between provider-manifest handling and consumer-manifest handling

---

## 5.3 Registry Layer

Right now:

* `ConnectorRegistry` is keyed by plugin name
* `ProviderRegistry` exists, but is not the main path for telemetry

If LMU becomes a provider-side plugin, we need to decide what the first real lookup path is.

I recommend:

* register the LMU plugin by exported capability
* make the domain providers the real runtime structure
* treat the old plugin-name connector registry as transitional infrastructure

This gives us the first real runtime cut:

* new runtime concept on top
* shared LMU source underneath

Immediate implication:

* the runtime needs a registry path that can answer "who satisfies `telemetry.car.v1`?"

---

## 5.4 Widget / Consumer Layer

This is where the architectural pressure becomes real.

Today widgets depend on:

* a plugin name
* a source path such as `vehicle.fuel`

If LMU moves out into a provider-side plugin, widgets cannot keep assuming they belong to the same plugin that owns the connector.

That means the widget and consumer side will have to move next.

There is no point hiding that with a bridge.

The consequence of doing this cleanly is simple:

* LMU gets built in the correct shape first
* consumers and widgets get updated after that
* the places that break tell us exactly where the old assumptions still live

Immediate implication:

* widget loading must stop meaning "load widgets for the same plugin that owns the connector"

---

## 5.5 Debugging And State Inspection

LMU is also a good test case for runtime visibility.

Once it becomes a provider-side plugin, dev tools should be able to answer:

* is the provider discovered?
* is it initialized?
* is it active?
* which capabilities does it export?
* which consumers are bound to it?

Immediate implication:

* runtime state inspection should expose provider-level status, not just connector objects and widget contexts

---

# 6. Recommended First Implementation Shape

This is the smallest shape I would aim for first without keeping the LMU side monolithic.

## Phase 1

Make `lmu_connector` a recognized provider-side manifest.

Goal:

* the runtime can discover it without crashing or ignoring it

---

## Phase 2

Extract a shared LMU source/runtime object from the current monolithic connector.

Goal:

* LMU shared memory lifecycle lives in one place
* domain providers can sit on top of it cleanly

---

## Phase 3

Introduce the first domain providers and register them under exported capabilities.

Goal:

* the runtime can answer capability lookups for real LMU domains
* ownership of car, tyre, timing, session, and similar data is explicit

---

## Phase 4

Update the runtime binding path so consumers can resolve the new LMU domain capabilities.

Goal:

* the runtime binds to the new provider shape instead of the old connector ownership model

---

## Phase 5

Update widgets and consumer-side code to consume the new shape.

Goal:

* consumers describe what they need
* widgets stop depending on old plugin-owned connector assumptions
* the runtime owns the connection between providers and consumers

---

# 7. What I Would Not Do Yet

To keep this effort under control, I would not do these in the first LMU connector pass:

* redesign every widget spec at the same time
* rename every plugin folder to match the final vocabulary
* build a full provider priority and preference system before one provider path works cleanly

Those are all valid later steps, but they are not needed to prove the runtime direction.

---

# 8. Risks

## 8.1 Downstream Breakage

Once LMU is split properly, parts of the runtime that still assume the old monolith will break.

That is expected.

The point is to surface those assumptions and update them in order, not to keep them alive behind compatibility code.

---

## 8.2 LMU Becomes The Implicit Standard

The first provider plugin will shape the runtime.

That is useful, but it also means we need to keep an eye on whether the design is generic or just "LMU but generalized in wording."

---

# 9. Proposed Approval Questions

Before implementing, I would want a yes or no on these points:

1. Should `lmu_connector` stay named `lmu_connector` for now, even if its role is provider-side?
2. Do we want the LMU side split immediately into domain providers over a shared LMU source?
3. Are we comfortable making a clean break and updating downstream consumers after the provider split instead of adding compatibility glue?
4. Do we want LMU to be host-side only for now, or should provider plugins eventually also support subprocess hosting where appropriate?

---

# 10. Recommendation

My recommendation is:

* treat `lmu_connector` as the first provider-side plugin
* split it internally into one shared LMU source plus domain providers
* update the manifest and runtime around that split
* accept the downstream breakage that exposes old monolithic assumptions
* update the consumer and widget side after that

That gives us a cleaner path: one part built properly first, then the rest updated around it, without adding temporary architecture we already know we do not want to keep.
