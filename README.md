# TinyUi

![Version](https://img.shields.io/badge/version-0.1.0-purple)
![Status](https://img.shields.io/badge/status-work%20in%20progress-orange)
![License](https://img.shields.io/badge/license-GPLv3-green)
[![GitHub Sponsors](https://img.shields.io/badge/Sponsor-%E2%9D%A4-%23db61a2?logo=github)](https://github.com/sponsors/oost-hash)

A modular overlay based on [TinyPedal](https://github.com/TinyPedal/TinyPedal), the open-source racing overlay application.

While exploring how TinyPedal works internally, I noticed that the current architecture is very tightly coupled. Even small changes in one part of the codebase can have widespread effects across the project. This makes it difficult to extend or integrate new functionality without risking unintended side effects.

My original goal was to create an adapter layer that would allow TinyUI to plug into TinyPedal without modifying its core. However, due to the strong coupling between components, I couldn't find a clean or logical way to implement such an adapter.

Because of this, I decided to take a different approach: breaking apart some of TinyPedal’s internal assumptions and moving toward a more data-driven architecture.

Current Direction

The idea is to restructure how data flows through the system so that UI components depend on structured data rather than tightly bound application logic. By separating data sources, processing, and presentation, the overlay system becomes:

- more modular
- easier to extend
- safer to modify

# Current idea

This diagram illustrates a possible architectural direction, not a finalized design. Many aspects of the system are still undefined and may change as the project evolves.

To explore different approaches, I am experimenting with AI agents that iterate on the concept and help generate prototype implementations. The goal is to rapidly test ideas and identify which patterns work well in practice.

```mermaid
graph TB

    subgraph Core["tinycore — Core Engine"]
        direction TB
        store[Config Store]
        bus[Event Bus]
        pluginsys[Plugin System\nlifecycle · isolation · subprocess]
        providers[Provider Registry]
        telemetry[Telemetry ABCs\n🚧 in progress]
    end

    subgraph QML["tinyui_qml — UI Platform  •  QML"]
        direction TB
        qmlviews[QML Views\ncomponents · layout · tabs]
        viewmodels[ViewModels]
        windowing[Windowing]
    end

    subgraph Plugins["Plugins"]
        direction TB
        tp[tinypedal\nloaders · models]
        demo[demo\nreference implementation]
        connector[LMU Connector\n🚧 in progress]
    end

    Plugins -->|register providers| Core
    QML -->|uses core services| Core
    demo --> connector
    connector -.->|implements| telemetry

    style Core fill:#2c3e50,color:#fff
    style QML fill:#2980b9,color:#fff
    style Plugins fill:#e67e22,color:#fff
```

## Help Wanted: TinyUi Logo

I am looking for a community-contributed logo for **TinyUi**!

The current placeholder is a modified version of the [TinyPedal](https://github.com/s-victor/TinyPedal) icon and is not a permanent solution. I'd love something that truly represents this project.

### How to contribute

1. Open a new **Issue** with the text `[logo-proposal]`
2. Share your design idea, sketch, or finished logo in the issue
3. All submissions are welcome — rough concepts, SVG files, PNG mockups, anything!

### License

By submitting a logo, you agree to release it under the **[CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/)** license, keeping TinyUi open and its assets freely usable by the community.

### What we're looking for

- Something clean and recognizable at small sizes (32×32 up to 256×256)
- Fits the vibe of a lightweight UI overlay tool
- "Ui" or "TinyUi" incorporated in some way is a plus, but not required

Contributors will of course be credited! ⭐

*Feel free to comment on existing proposals too — feedback and votes help a lot.*

---

## License

GPLv3 — see [LICENSE](LICENSE).

TinyUi builds on [TinyPedal](https://github.com/TinyPedal/TinyPedal) by s-victor, which is also licensed under GPLv3.
