from __future__ import annotations

from time import perf_counter

from PySide6.QtCore import QTimer

from tinyqt_logging import configure
from tinyruntime_schema import get_logger
from tinycore.paths import AppPaths
from tinyplugins.user_files import sync_user_files
from tinyruntime.boot import boot_runtime, discover_manifests
from tinyqt.apps import TINYUI_HOST_ASSEMBLY, build_tinyui_launch_spec
from tinyqt.launch import launch_qml_app


def main() -> int:
    configure()
    log = get_logger(__name__)
    paths = AppPaths.detect()
    manifests = discover_manifests(paths.plugins_dir)
    sync_user_files(paths.app_root, manifests)
    runtime = boot_runtime(paths, manifests, host_assembly=TINYUI_HOST_ASSEMBLY)
    spec = build_tinyui_launch_spec(runtime)
    opened = {"value": False}

    def pre_run() -> None:
        if runtime.units.get("ui.main") is not None:
            runtime.units.set_state("ui.main", "running")
        runtime.start_host_workers()

    def on_before_exec(host) -> None:
        controller = host.window.property("devToolsController")
        if controller is None:
            raise RuntimeError("No devToolsController property found on TinyUiMain root")

        def _open() -> None:
            controller.toggle()
            opened["value"] = True
            log.info("devtools_lazy_smoke opened devtools")

        QTimer.singleShot(50, _open)
        QTimer.singleShot(400, host.window.close)

    spec = spec.__class__(
        app_name=spec.app_name,
        version=spec.version,
        qml_path=spec.qml_path,
        app_manifest=spec.app_manifest,
        theme=spec.theme,
        log_inspector=spec.log_inspector,
        build_registrations=spec.build_registrations,
        restore_state_scope=spec.restore_state_scope,
        module=spec.module,
        on_host_ready=spec.on_host_ready,
        on_before_exec=on_before_exec,
    )

    start = perf_counter()
    exit_code = launch_qml_app(runtime, spec, pre_run=pre_run, extra_context=None)
    elapsed_ms = round((perf_counter() - start) * 1000, 1)
    print(f"lazy_smoke exit={exit_code} opened={opened['value']} elapsed_ms={elapsed_ms}")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
