# Graph Report - despatch  (2026-07-30)

## Corpus Check
- 60 files · ~28,828 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 853 nodes · 1295 edges · 66 communities (59 shown, 7 thin omitted)
- Extraction: 98% EXTRACTED · 0% INFERRED · 0% AMBIGUOUS · INFERRED: 1 edges (avg confidence: 0.8)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `dcee8c4d`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- EnvoyGateway
- StackMonitor
- SettingsStore
- ApplicationEntry
- Despatch
- test_envoy_gateway.py
- _documentation.py
- _icons.py
- WindowsGlobalShortcut
- test_catalog.py
- despatch/__init__.py
- MainWindow
- StackState
- AutostartService
- SingleInstance
- _launch_worker.py
- _globalPoint
- render_ui.py
- _theme.py
- DespatchApplication
- Docstring Standards
- test_main_window.py
- test_stack_monitor.py
- Settings
- ._onStateLoaded
- ._showErrorDialog
- ._refreshViews
- release_automation.py
- _search.py
- Stack Examples
- test_settings.py
- .__init__
- ._submit
- ._onCatalogRefreshError
- parseArgs
- ._requestCatalogRefresh
- .start
- Troubleshooting
- TitleBar
- test_search.py
- Despatch
- Bundle Manifests
- qtApplication
- Despatch Repository Instructions
- Build Despatch Executable
- build-executable.ps1
- resources/__init__.py
- envoy-despatch
- Getting Started
- Launcher and Tray
- Choosing a Stack
- index.md
- Architecture
- _activationReason
- cli.md
- __main__.py
- ._populateApplications
- _DocumentationRequestHandler
- ReleaseAutomationTests
- setupLogging
- .setReady
- ._onItemClicked

## God Nodes (most connected - your core abstractions)
1. `DespatchApplication` - 34 edges
2. `MainWindow` - 29 edges
3. `EnvoyGateway` - 23 edges
4. `SettingsStore` - 22 edges
5. `StackMonitor` - 21 edges
6. `makeEnvoyModule()` - 17 edges
7. `FakeGateway` - 16 edges
8. `makeBundle()` - 14 edges
9. `Docstring Standards` - 14 edges
10. `ApplicationEntry` - 13 edges

## Surprising Connections (you probably didn't know these)
- `makeLauncher()` --references--> `MainWindow`  [EXTRACTED]
  tests/render_ui.py → py/despatch/_main_window.py
- `makeApplication()` --references--> `ApplicationEntry`  [EXTRACTED]
  tests/render_ui.py → py/despatch/_models.py
- `makeSettingsDialog()` --references--> `SettingsDialog`  [EXTRACTED]
  tests/render_ui.py → py/despatch/_settings_dialog.py
- `_createApplication()` --calls--> `loadProductIcon()`  [EXTRACTED]
  py/despatch/__main__.py → py/despatch/_icons.py
- `main()` --calls--> `DespatchApplication`  [EXTRACTED]
  py/despatch/__main__.py → py/despatch/_application.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Stack Lifecycle** — Despatch, Stack, Bundle, Manifest, Catalog [1.0]
- **UI Interaction Model** — LauncherWindow, TrayIcon, SearchIndex, Favorites, GlobalShortcut [1.0]

## Communities (66 total, 7 thin omitted)

### Community 0 - "EnvoyGateway"
Cohesion: 0.07
Nodes (33): EnvoyGateway, EnvoyUnavailableError, Any, ModuleType, Path, RuntimeError, Validate and persist a named or custom Stack globally. Args: stack_value:…, Clear the shared Stack setting for Automatic resolution. (+25 more)

### Community 1 - "StackMonitor"
Cohesion: 0.07
Nodes (26): Reflect Stack-monitor health independently from catalog status., Lightweight filesystem identity used to detect Stack updates., StackFileState, BaseException, Disable monitoring and discard all selection-specific state., Pause scheduling while preserving the current selection and baseline., Resume a previously suspended explicit Stack monitor., Stop scheduling; any blocked daemon probe may finish independently. (+18 more)

### Community 2 - "SettingsStore"
Cohesion: 0.05
Nodes (31): _defaultData(), getDefaultSettingsPath(), _getEnvoyConfigRoot(), _nonEmptyEnvironmentPath(), Any, Path, Atomic persistence for Despatch user preferences., Theme preference: system, light, or dark. (+23 more)

### Community 3 - "ApplicationEntry"
Cohesion: 0.10
Nodes (25): CatalogLoader, getCurrentPlatform(), _ManifestRecord, Any, Path, Read one manifest and report recoverable parse failures., Validate and construct applications from one manifest., One validated manifest and its contributing bundle. (+17 more)

### Community 4 - "Despatch"
Cohesion: 0.10
Nodes (26): Automatic Stack Resolution, Envoy Bundle, Application Catalog, Despatch, Envoy, Envoy Gateway, Favorites, GitHub Actions CI/CD (+18 more)

### Community 5 - "test_envoy_gateway.py"
Cohesion: 0.14
Nodes (19): explicitState(), FakeUserConfig, makeApplication(), makeEnvoyModule(), testAutomaticModeUsesFullEnvoyDiscovery(), testAutomaticResolutionUnsetsStack(), testCustomStackFileStateUsesSelectedPathWithoutRegistryResolution(), testCustomStackPersistsCanonicalPath() (+11 more)

### Community 6 - "_documentation.py"
Cohesion: 0.14
Nodes (22): Popen, DocumentationError, _DocumentationServer, _documentationServerCommand(), getDocumentationSite(), _openBrowser(), openDocumentation(), Path (+14 more)

### Community 7 - "_icons.py"
Cohesion: 0.16
Nodes (20): clearCache(), _extractLeadingMark(), _findResourceIcon(), _loadEmbeddedImageIcon(), _loadFileIcon(), loadPackagedIcon(), loadPathIcon(), loadProductIcon() (+12 more)

### Community 8 - "WindowsGlobalShortcut"
Cohesion: 0.12
Nodes (11): _NativeHotkeyFilter, QApplication, Forward native Windows messages to a QObject-owned callback., Forward the native message address and continue event processing., Register one Windows global shortcut without binding-specific imports., Whether a shortcut is currently registered., Register a portable shortcut string. Args: shortcut: Combination such as…, Release the current shortcut if registered. (+3 more)

### Community 9 - "test_catalog.py"
Cohesion: 0.33
Nodes (16): FakeGateway, makeBundle(), testApplicationSuppressionKeepsSiblingsAndIgnoresMissingTargets(), testApplicationUsesGlobalGroupDeclaredByLaterBundle(), testApplicationWithUndeclaredGlobalGroupIsOmitted(), testBundleSuppressionIsCatalogWideAndPreservesSharedGroup(), testDuplicateGlobalGroupUsesFirstDeclarationAndLoadsApplications(), testInvalidSchemaIsRecoverable() (+8 more)

### Community 10 - "despatch/__init__.py"
Cohesion: 0.13
Nodes (15): Qt application coordinator for Despatch., Load Despatch manifests from active Envoy bundles., Constants shared by Despatch modules., Boundary between Despatch and the Envoy Python API., Despatch is a tray-based launcher for Envoy-managed applications., Frameless search-first Despatch launcher window., Typed domain models used by Despatch., The active Despatch Stack-resolution mode. (+7 more)

### Community 11 - "MainWindow"
Cohesion: 0.10
Nodes (12): Primary launcher window., MainWindow, Show a loading state and disable mutation controls., Display a recoverable catalog or launch error., Show or clear the dedicated Stack-monitor health warning. Args: message:…, Show, raise, and focus the launcher., Focus and select the search field., Allow the next close event to destroy the window. (+4 more)

### Community 12 - "StackState"
Cohesion: 0.17
Nodes (12): Populate the Envoy Stack selector. Args: stacks: Available published Stacks.…, CatalogSnapshot, NamedStack, A complete immutable application catalog snapshot., A published Envoy Stack., The Stack resolution state used by the catalog and launch flow., StackState, DespatchTrayIcon (+4 more)

### Community 13 - "AutostartService"
Cohesion: 0.17
Nodes (9): AutostartService, Path, Return the Windows Run-key path., Manage per-user Windows login startup., Whether this platform supports the implementation., Return whether the autostart registry value exists., Enable or disable login startup. Args: enabled: Requested startup state.…, Create a hidden launcher script and register it for the current user. (+1 more)

### Community 14 - "SingleInstance"
Cohesion: 0.16
Nodes (9): Own a per-user local server or notify the existing instance., Whether this object owns the local server., Become the primary instance or ask it to show its window. Returns: True for the…, Close and remove the local server., Attach asynchronous readers to all pending sockets., Accumulate and handle newline-delimited IPC messages., Drain and release a disconnected client socket., SingleInstance (+1 more)

### Community 15 - "_launch_worker.py"
Cohesion: 0.24
Nodes (12): launchApplication(), main(), Any, ModuleType, Path, Isolated worker that dispatches one application through Envoy., Spawn an application through the Envoy Python API. Args: request: Validated…, Read and validate one JSON launch request from disk. (+4 more)

### Community 16 - "_globalPoint"
Cohesion: 0.22
Nodes (6): _globalPoint(), Return a mouse event's global point across supported Qt versions., Show contextual actions for an application row., Begin a window drag from the custom title bar., Move the window during a fallback title-bar drag., QPoint

### Community 17 - "render_ui.py"
Cohesion: 0.19
Nodes (10): Return the current editor values. Returns: Keyword arguments accepted by…, Edit user-facing launcher preferences. Args: settings: Current settings store.…, SettingsDialog, main(), makeApplication(), makeLauncher(), makeSettingsDialog(), Render a representative Despatch window for visual QA. (+2 more)

### Community 18 - "_theme.py"
Cohesion: 0.23
Nodes (12): applyTheme(), _baseStyle(), _darkStyle(), _lightStyle(), QApplication, System-aware light and dark Qt styles., Apply the selected theme and return its resolved name. Args: application:…, Return the light theme stylesheet. (+4 more)

### Community 19 - "DespatchApplication"
Cohesion: 0.18
Nodes (7): DespatchApplication, Persist window state and stop the tray process., Persist an explicit Stack or enable Automatic resolution., Prompt for a custom `.estack` file and request its activation., Copy a platform-quoted Envoy command to the clipboard., Coordinate the window, tray, Envoy services, and background work., Dispatch completed future callbacks on the Qt main thread.

### Community 20 - "Docstring Standards"
Cohesion: 0.10
Nodes (19): Args Section Format, Args Section with Type Hints, Class Docstrings, Critical Rule: Empty Line at End, Docstring Standards, Examples Section, Exception Standards, Function Overrides (+11 more)

### Community 21 - "test_main_window.py"
Cohesion: 0.20
Nodes (3): makeSnapshot(), testSearchEnterLaunchesFirstMatch(), testSingleClickRequestsLaunch()

### Community 22 - "test_stack_monitor.py"
Cohesion: 0.48
Nodes (11): makeFileState(), makeSelection(), testAutomaticModeCanDisablePendingMonitoring(), testFailureBackoffCapsAtFiveMinutesWithoutShorteningLongIntervals(), testReloadFailureKeepsOldBaselineAndSchedulesRetry(), testResultFromPreviousSelectionIsIgnored(), testSlowProbeWarnsAndCannotOverlap(), testStableChangeRequiresConfirmationBeforeNotification() (+3 more)

### Community 23 - "Settings"
Cohesion: 0.14
Nodes (12): Configuration, Despatch settings, Environment variables, Envoy user configuration, Logging, Appearance, Global shortcut, Launch behavior (+4 more)

### Community 24 - "._onStateLoaded"
Cohesion: 0.20
Nodes (6): _CatalogLoadResult, Load all state required for an atomic UI refresh., Atomically apply refreshed Envoy state., Release the refresh guard and run one coalesced manual refresh., Enable monitoring only for an explicit named or custom Stack., Complete catalog state plus its explicit Stack-file baseline.

### Community 25 - "._showErrorDialog"
Cohesion: 0.25
Nodes (5): Create a retained non-modal error dialog., Release a deleted non-modal error dialog., ErrorDialog, Actionable process and application error dialog., Display an error summary with optional diagnostic output. Args: title: Dialog…

### Community 27 - "._refreshViews"
Cohesion: 0.25
Nodes (4): Toggle a favorite and refresh both launch surfaces., Show settings and apply accepted changes transactionally., Apply the requested global shortcut registration., Refresh main and tray views from one state snapshot.

### Community 28 - "release_automation.py"
Cohesion: 0.12
Nodes (30): ArgumentParser, Pattern, buildIssueReport(), buildParser(), checkRelease(), classifyImpact(), gitOutput(), lockfileHasDependencyChanges() (+22 more)

### Community 29 - "_search.py"
Cohesion: 0.32
Nodes (7): _isSubsequence(), rankApplications(), Deterministic application search and ranking., Return applications ordered by text relevance and user preference. Args:…, Calculate a lower-is-better search score., Return whether query characters occur in order within text., _scoreApplication()

### Community 32 - "Stack Examples"
Cohesion: 0.20
Nodes (8): Minimal workstation Stack, Portable development Stack, Published production Stack, Stack Examples, Complete schema, Named and contextual Stacks, Path handling, Stack Files

### Community 34 - ".__init__"
Cohesion: 0.29
Nodes (5): _isDevModeEnabled(), Path, QApplication, Connect view requests to coordinator operations., Return whether Despatch should default to Automatic resolution.

### Community 35 - "._submit"
Cohesion: 0.29
Nodes (4): Any, Prepare and spawn a catalog application asynchronously., Open the Despatch documentation without blocking the Qt thread., Submit background work for polling on the Qt thread.

### Community 36 - "._onCatalogRefreshError"
Cohesion: 0.38
Nodes (4): BaseException, Handle catalog failures according to their initiating surface., Preserve prior state and surface a refresh failure., Restore the prior Stack selector state after a failed switch.

### Community 37 - "parseArgs"
Cohesion: 0.33
Nodes (6): main(), parseArgs(), Namespace, Run a build-time Python command and persist its real exit code., Parse wrapper arguments and the child Python command., Run the child interpreter and write its exit code for PowerShell.

### Community 38 - "._requestCatalogRefresh"
Cohesion: 0.33
Nodes (3): Refresh Stacks and application manifests asynchronously., Start or coalesce a background catalog refresh. Args: trigger: ``manual`` for…, Reingest a confirmed changed Stack without blocking interaction.

### Community 39 - ".start"
Cohesion: 0.33
Nodes (3): Start the tray application and load its first catalog. Args: popup: Show the…, Show and focus the main launcher., Restore persisted Qt geometry when it is valid.

### Community 40 - "Troubleshooting"
Cohesion: 0.22
Nodes (9): A Stack cannot be selected, An application fails to start, Applications do not appear, Documentation does not open, Stack update checks are unavailable, Start at sign in fails, The global shortcut cannot be enabled, The wrong Stack is active (+1 more)

### Community 41 - "TitleBar"
Cohesion: 0.22
Nodes (5): Build the launcher interface., Connect all UI events., Custom title bar for the frameless launcher., Finish a fallback title-bar drag., TitleBar

### Community 42 - "test_search.py"
Cohesion: 0.70
Nodes (4): makeApplication(), testExactAndPrefixMatchesRankFirst(), testFavoritesBreakEqualRelevanceTies(), testSubsequenceMatching()

### Community 43 - "Despatch"
Cohesion: 0.25
Nodes (6): Application manifests, Current milestone, Despatch, Development, Runtime, Standalone executable

### Community 44 - "Bundle Manifests"
Cohesion: 0.25
Nodes (8): Applications, Bundle Manifests, Example, Groups, Icons and path safety, Suppression, Top-level fields, Validation and diagnostics

### Community 46 - "Despatch Repository Instructions"
Cohesion: 0.29
Nodes (6): Coding standards, Despatch Repository Instructions, Domain terminology, Executable and release work, graphify, Runtime contract

### Community 47 - "Build Despatch Executable"
Cohesion: 0.29
Nodes (6): Build and validate, Build Despatch Executable, Inspect the packaging contract, Keep dependency pins coherent, Preserve frozen-runtime behavior, Report the result

### Community 52 - "Getting Started"
Cohesion: 0.29
Nodes (5): Choose your environment, Find and launch an application, Getting Started, Open the launcher, Understand the sections

### Community 53 - "Launcher and Tray"
Cohesion: 0.29
Nodes (6): Application menu, Favorites and history, Launcher and Tray, Main launcher, Notification-area menu, Search and keyboard controls

### Community 54 - "Choosing a Stack"
Cohesion: 0.33
Nodes (6): Automatic resolution, Automatic updates, Choosing a Stack, Custom Stack files, Named Stacks, Resolution at startup

### Community 55 - "index.md"
Cohesion: 0.40
Nodes (3): Despatch, How Despatch fits with Envoy, Start here

### Community 56 - "Architecture"
Cohesion: 0.50
Nodes (3): Architecture, Responsibilities, Source and frozen execution

### Community 57 - "_activationReason"
Cohesion: 0.50
Nodes (3): _activationReason(), Return a tray activation enum across Qt versions., Show the main UI only for a left-click activation.

### Community 59 - "__main__.py"
Cohesion: 0.20
Nodes (10): _createApplication(), main(), _parseArgs(), Namespace, QApplication, Command-line entry point for the Despatch tray application., Parse Despatch command-line arguments., Create and configure the shared Qt application. (+2 more)

### Community 60 - "._populateApplications"
Cohesion: 0.17
Nodes (6): Display a new catalog snapshot and user ranking state., Rebuild the visible catalog for the current query., Append a non-interactive section label., Append one interactive application row., Append a centered non-interactive empty-state row., Build a concise HTML application tooltip.

### Community 61 - "_DocumentationRequestHandler"
Cohesion: 0.18
Nodes (7): _DocumentationRequestHandler, Any, Serve static files quietly and record the latest request time., Record and serve one GET request., Record and serve one HEAD request., Disable directory listings for the packaged static site., Suppress standard-library request logging.

### Community 62 - "ReleaseAutomationTests"
Cohesion: 0.20
Nodes (6): Tests for Despatch release automation., Exercise deterministic release preparation., Valid SemVer values are returned unchanged., Invalid release values are rejected., Preparation synchronizes both versions and both Envoy defaults., ReleaseAutomationTests

### Community 63 - "setupLogging"
Cohesion: 0.38
Nodes (6): Logger, getLogger(), Logging configuration for Despatch., Configure the Despatch logger once. Args: level: DEBUG, INFO, WARNING, or…, Return a child logger. Args: module_name: Usually the caller's ``__name__``.…, setupLogging()

### Community 64 - ".setReady"
Cohesion: 0.33
Nodes (3): Restore interactive controls and display a status message., Display a status message that cannot clear newer UI state. Args: message:…, Clear a transient status only when no newer status replaced it.

## Knowledge Gaps
- **81 isolated node(s):** `envoy-despatch`, `Inspect the packaging contract`, `Preserve frozen-runtime behavior`, `Keep dependency pins coherent`, `Build and validate` (+76 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **7 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `DespatchApplication` connect `DespatchApplication` to `StackMonitor`, `.__init__`, `._submit`, `._onCatalogRefreshError`, `._requestCatalogRefresh`, `.start`, `__main__.py`, `despatch/__init__.py`, `MainWindow`, `._onStateLoaded`, `._showErrorDialog`, `._refreshViews`?**
  _High betweenness centrality (0.103) - this node is a cross-community bridge._
- **Why does `MainWindow` connect `MainWindow` to `.setReady`, `._onItemClicked`, `.__init__`, `TitleBar`, `despatch/__init__.py`, `StackState`, `_globalPoint`, `render_ui.py`, `._populateApplications`?**
  _High betweenness centrality (0.081) - this node is a cross-community bridge._
- **Why does `SettingsStore` connect `SettingsStore` to `render_ui.py`?**
  _High betweenness centrality (0.064) - this node is a cross-community bridge._
- **What connects `envoy-despatch`, `Inspect the packaging contract`, `Preserve frozen-runtime behavior` to the rest of the system?**
  _81 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `EnvoyGateway` be split into smaller, more focused modules?**
  _Cohesion score 0.07402031930333818 - nodes in this community are weakly interconnected._
- **Should `StackMonitor` be split into smaller, more focused modules?**
  _Cohesion score 0.07246376811594203 - nodes in this community are weakly interconnected._
- **Should `SettingsStore` be split into smaller, more focused modules?**
  _Cohesion score 0.05333333333333334 - nodes in this community are weakly interconnected._