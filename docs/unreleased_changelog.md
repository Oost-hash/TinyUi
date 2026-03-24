# Unreleased

Add entries here before running a release. Use the correct section to control
how the version number is bumped. The script automatically sorts entries into
Added / Changed / Fixed / Removed based on keywords in the text.

Keyword rules:
  - **Removed**  → line starts with "Removed" or contains "removed from"
  - **Fixed**    → line contains " now " (was broken, works now) or starts with "Fixed"
  - **Changed**  → line contains: moved · refactored · extracted · aligned · replaced · renamed · updated
  - **Added**    → anything in major/minor that does not match the above
  - **Changed**  → anything in patch that does not match the above

Running a release:
  python scripts/release.py patch    # 0.2.0 → 0.2.1  (bug fixes)
  python scripts/release.py minor    # 0.2.0 → 0.3.0  (new features)
  python scripts/release.py major    # 0.2.0 → 1.0.0  (breaking changes)

### major
<!-- Breaking changes that affect existing plugins or config -->

### minor
<!-- New features and additions -->

### patch
<!-- Bug fixes, small improvements, and cleanup -->
