# Graph Report - V:\repo\gtvfx-contrib\gt\despatch  (2026-07-28)

## Corpus Check
- Corpus is ~25,640 words - fits in a single context window. You may not need a graph.

## Summary
- 688 nodes · 1106 edges · 52 communities (42 shown, 10 thin omitted)
- Extraction: 98% EXTRACTED · 0% INFERRED · 0% AMBIGUOUS · INFERRED: 1 edges (avg confidence: 0.8)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- Envoy Gateway
- Application Model
- Catalog Loader
- Stack Monitor
- Main Window UI
- Search Engine
- Settings System
- Theme & Icons
- Tray Icon Integration
- Documentation Server
- Single Instance Lock
- Launch Worker
- Error Dialogs
- Constants & Platform
- Logging System
- Application Core
- Stack File Parsing
- Bundle Discovery
- Manifest Validation
- Icon Resolution
- Path Utilities
- Qt Compatibility Shim
- Application Launch
- Favorites & History
- Global Shortcut
- Autostart Integration
- Stack Selection UI
- Settings Dialog
- Search Indexing
- Process Spawning
- Terminal Launch
- Copy Command Utility
- Stack State Tracking
- Bundle Metadata
- YAML Parsing
- File System Utilities
- Application Groups
- Suppression Logic
- Keyword Matching
- Test Infrastructure
- Build Scripting
- PyInstaller Config
- CI/CD Workflows
- Documentation Examples
- Graphify Skill
- Copilot Instructions
- Test Fixtures
- Root Package Init

## God Nodes (most connected - your core abstractions)
1. `DespatchApplication` - 34 edges
2. `MainWindow` - 29 edges
3. `EnvoyGateway` - 23 edges
4. `SettingsStore` - 22 edges
5. `StackMonitor` - 21 edges
6. `FakeGateway` - 16 edges
7. `makeEnvoyModule()` - 16 edges
8. `makeBundle()` - 14 edges
9. `ApplicationEntry` - 13 edges
10. `writeManifest()` - 13 edges

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

## Communities (52 total, 10 thin omitted)

### Community 0 - "Envoy Gateway"
Cohesion: 0.06
Nodes (43): EnvoyGateway, EnvoyUnavailableError, Any, ModuleType, Path, RuntimeError, Boundary between Despatch and the Envoy Python API., Validate and persist a named or custom Stack globally. Args: stack_value:… (+35 more)

### Community 1 - "Application Model"
Cohesion: 0.07
Nodes (27): Reflect Stack-monitor health independently from catalog status., Lightweight filesystem identity used to detect Stack updates., StackFileState, BaseException, Non-blocking polling for changes to an explicitly selected Stack., Disable monitoring and discard all selection-specific state., Pause scheduling while preserving the current selection and baseline., Resume a previously suspended explicit Stack monitor. (+19 more)

### Community 2 - "Catalog Loader"
Cohesion: 0.06
Nodes (26): _defaultData(), getDefaultSettingsPath(), Any, Path, Base64-encoded Qt window geometry., Return whether an application is a favorite. Args: stable_id: Stable…, Toggle and persist an application's favorite state. Args: stable_id: Stable…, Move an application to the front of launch history. Args: stable_id: Stable… (+18 more)

### Community 3 - "Stack Monitor"
Cohesion: 0.10
Nodes (25): CatalogLoader, getCurrentPlatform(), _ManifestRecord, Any, Path, Load Despatch manifests from active Envoy bundles., Read one manifest and report recoverable parse failures., Validate and construct applications from one manifest. (+17 more)

### Community 4 - "Main Window UI"
Cohesion: 0.10
Nodes (26): Automatic Stack Resolution, Envoy Bundle, Application Catalog, Despatch, Envoy, Envoy Gateway, Favorites, GitHub Actions CI/CD (+18 more)

### Community 5 - "Search Engine"
Cohesion: 0.14
Nodes (18): explicitState(), FakeUserConfig, makeApplication(), makeEnvoyModule(), testAutomaticModeUsesFullEnvoyDiscovery(), testAutomaticResolutionUnsetsStack(), testCustomStackFileStateUsesSelectedPathWithoutRegistryResolution(), testCustomStackPersistsCanonicalPath() (+10 more)

### Community 6 - "Settings System"
Cohesion: 0.17
Nodes (20): Popen, DocumentationError, _documentationServerCommand(), getDocumentationSite(), _openBrowser(), openDocumentation(), Path, RuntimeError (+12 more)

### Community 7 - "Theme & Icons"
Cohesion: 0.16
Nodes (20): clearCache(), _extractLeadingMark(), _findResourceIcon(), _loadEmbeddedImageIcon(), _loadFileIcon(), loadPackagedIcon(), loadPathIcon(), loadProductIcon() (+12 more)

### Community 8 - "Tray Icon Integration"
Cohesion: 0.12
Nodes (11): _NativeHotkeyFilter, QApplication, Forward native Windows messages to a QObject-owned callback., Forward the native message address and continue event processing., Register one Windows global shortcut without binding-specific imports., Whether a shortcut is currently registered., Register a portable shortcut string. Args: shortcut: Combination such as…, Release the current shortcut if registered. (+3 more)

### Community 9 - "Documentation Server"
Cohesion: 0.33
Nodes (16): FakeGateway, makeBundle(), testApplicationSuppressionKeepsSiblingsAndIgnoresMissingTargets(), testApplicationUsesGlobalGroupDeclaredByLaterBundle(), testApplicationWithUndeclaredGlobalGroupIsOmitted(), testBundleSuppressionIsCatalogWideAndPreservesSharedGroup(), testDuplicateGlobalGroupUsesFirstDeclarationAndLoadsApplications(), testInvalidSchemaIsRecoverable() (+8 more)

### Community 10 - "Single Instance Lock"
Cohesion: 0.19
Nodes (9): Qt application coordinator for Despatch., Constants shared by Despatch modules., Despatch is a tray-based launcher for Envoy-managed applications., Frameless search-first Despatch launcher window., Windows-first operating-system integrations., Despatch preference editor., Atomic persistence for Despatch user preferences., Single-instance coordination using Qt local IPC. (+1 more)

### Community 11 - "Launch Worker"
Cohesion: 0.11
Nodes (10): Primary launcher window., MainWindow, Show a loading state and disable mutation controls., Display a recoverable catalog or launch error., Show or clear the dedicated Stack-monitor health warning. Args: message:…, Allow the next close event to destroy the window., Hide to tray unless application shutdown is in progress., Launch the first visible application result. (+2 more)

### Community 12 - "Error Dialogs"
Cohesion: 0.15
Nodes (11): CatalogSnapshot, A complete immutable application catalog snapshot., Return applications keyed by stable identity. Returns: Mapping of stable…, _activationReason(), DespatchTrayIcon, Return a tray activation enum across Qt versions., Return the compact label for the active Stack mode., Show the main UI only for a left-click activation. (+3 more)

### Community 13 - "Constants & Platform"
Cohesion: 0.17
Nodes (9): AutostartService, Path, Return the Windows Run-key path., Manage per-user Windows login startup., Whether this platform supports the implementation., Return whether the autostart registry value exists., Enable or disable login startup. Args: enabled: Requested startup state.…, Create a hidden launcher script and register it for the current user. (+1 more)

### Community 14 - "Logging System"
Cohesion: 0.16
Nodes (9): Own a per-user local server or notify the existing instance., Whether this object owns the local server., Become the primary instance or ask it to show its window. Returns: True for the…, Close and remove the local server., Attach asynchronous readers to all pending sockets., Accumulate and handle newline-delimited IPC messages., Drain and release a disconnected client socket., SingleInstance (+1 more)

### Community 15 - "Application Core"
Cohesion: 0.24
Nodes (12): launchApplication(), main(), Any, ModuleType, Path, Isolated worker that dispatches one application through Envoy., Spawn an application through the Envoy Python API. Args: request: Validated…, Read and validate one JSON launch request from disk. (+4 more)

### Community 16 - "Stack File Parsing"
Cohesion: 0.17
Nodes (9): _globalPoint(), Return a mouse event's global point across supported Qt versions., Custom title bar for the frameless launcher., Show contextual actions for an application row., Begin a window drag from the custom title bar., Move the window during a fallback title-bar drag., Finish a fallback title-bar drag., TitleBar (+1 more)

### Community 17 - "Bundle Discovery"
Cohesion: 0.19
Nodes (10): Return the current editor values. Returns: Keyword arguments accepted by…, Edit user-facing launcher preferences. Args: settings: Current settings store.…, SettingsDialog, main(), makeApplication(), makeLauncher(), makeSettingsDialog(), Render a representative Despatch window for visual QA. (+2 more)

### Community 18 - "Manifest Validation"
Cohesion: 0.23
Nodes (12): applyTheme(), _baseStyle(), _darkStyle(), _lightStyle(), QApplication, System-aware light and dark Qt styles., Apply the selected theme and return its resolved name. Args: application:…, Return the light theme stylesheet. (+4 more)

### Community 19 - "Icon Resolution"
Cohesion: 0.18
Nodes (7): DespatchApplication, Persist window state and stop the tray process., Persist an explicit Stack or enable Automatic resolution., Prompt for a custom `.estack` file and request its activation., Copy a platform-quoted Envoy command to the clipboard., Coordinate the window, tray, Envoy services, and background work., Dispatch completed future callbacks on the Qt main thread.

### Community 20 - "Path Utilities"
Cohesion: 0.20
Nodes (10): _createApplication(), main(), _parseArgs(), Namespace, QApplication, Command-line entry point for the Despatch tray application., Parse Despatch command-line arguments., Create and configure the shared Qt application. (+2 more)

### Community 21 - "Qt Compatibility Shim"
Cohesion: 0.20
Nodes (3): makeSnapshot(), testSearchEnterLaunchesFirstMatch(), testSingleClickRequestsLaunch()

### Community 22 - "Application Launch"
Cohesion: 0.48
Nodes (11): makeFileState(), makeSelection(), testAutomaticModeCanDisablePendingMonitoring(), testFailureBackoffCapsAtFiveMinutesWithoutShorteningLongIntervals(), testReloadFailureKeepsOldBaselineAndSchedulesRetry(), testResultFromPreviousSelectionIsIgnored(), testSlowProbeWarnsAndCannotOverlap(), testStableChangeRequiresConfirmationBeforeNotification() (+3 more)

### Community 23 - "Favorites & History"
Cohesion: 0.18
Nodes (7): _DocumentationRequestHandler, Any, Serve static files quietly and record the latest request time., Record and serve one GET request., Record and serve one HEAD request., Disable directory listings for the packaged static site., Suppress standard-library request logging.

### Community 24 - "Global Shortcut"
Cohesion: 0.20
Nodes (6): _CatalogLoadResult, Load all state required for an atomic UI refresh., Atomically apply refreshed Envoy state., Release the refresh guard and run one coalesced manual refresh., Enable monitoring only for an explicit named or custom Stack., Complete catalog state plus its explicit Stack-file baseline.

### Community 25 - "Autostart Integration"
Cohesion: 0.25
Nodes (5): Create a retained non-modal error dialog., Release a deleted non-modal error dialog., ErrorDialog, Actionable process and application error dialog., Display an error summary with optional diagnostic output. Args: title: Dialog…

### Community 27 - "Stack Selection UI"
Cohesion: 0.25
Nodes (4): Toggle a favorite and refresh both launch surfaces., Show settings and apply accepted changes transactionally., Apply the requested global shortcut registration., Refresh main and tray views from one state snapshot.

### Community 28 - "Settings Dialog"
Cohesion: 0.25
Nodes (4): Display a new catalog snapshot and user ranking state., Rebuild the visible catalog for the current query., Append a non-interactive section label., Append a centered non-interactive empty-state row.

### Community 29 - "Search Indexing"
Cohesion: 0.32
Nodes (7): _isSubsequence(), rankApplications(), Deterministic application search and ranking., Return applications ordered by text relevance and user preference. Args:…, Calculate a lower-is-better search score., Return whether query characters occur in order within text., _scoreApplication()

### Community 32 - "Process Spawning"
Cohesion: 0.38
Nodes (6): Logger, getLogger(), Logging configuration for Despatch., Configure the Despatch logger once. Args: level: DEBUG, INFO, WARNING, or…, Return a child logger. Args: module_name: Usually the caller's ``__name__``.…, setupLogging()

### Community 34 - "Copy Command Utility"
Cohesion: 0.29
Nodes (5): _isDevModeEnabled(), Path, QApplication, Connect view requests to coordinator operations., Return whether Despatch should default to Automatic resolution.

### Community 35 - "Stack State Tracking"
Cohesion: 0.29
Nodes (4): Any, Prepare and spawn a catalog application asynchronously., Open the Despatch documentation without blocking the Qt thread., Submit background work for polling on the Qt thread.

### Community 36 - "Bundle Metadata"
Cohesion: 0.38
Nodes (4): BaseException, Handle catalog failures according to their initiating surface., Preserve prior state and surface a refresh failure., Restore the prior Stack selector state after a failed switch.

### Community 37 - "YAML Parsing"
Cohesion: 0.33
Nodes (6): main(), parseArgs(), Namespace, Run a build-time Python command and persist its real exit code., Parse wrapper arguments and the child Python command., Run the child interpreter and write its exit code for PowerShell.

### Community 38 - "File System Utilities"
Cohesion: 0.33
Nodes (3): Refresh Stacks and application manifests asynchronously., Start or coalesce a background catalog refresh. Args: trigger: ``manual`` for…, Reingest a confirmed changed Stack without blocking interaction.

### Community 39 - "Application Groups"
Cohesion: 0.33
Nodes (3): Start the tray application and load its first catalog. Args: popup: Show the…, Show and focus the main launcher., Restore persisted Qt geometry when it is valid.

### Community 40 - "Suppression Logic"
Cohesion: 0.33
Nodes (3): Restore interactive controls and display a status message., Display a status message that cannot clear newer UI state. Args: message:…, Clear a transient status only when no newer status replaced it.

### Community 42 - "Test Infrastructure"
Cohesion: 0.70
Nodes (4): makeApplication(), testExactAndPrefixMatchesRankFirst(), testFavoritesBreakEqualRelevanceTies(), testSubsequenceMatching()

## Knowledge Gaps
- **1 isolated node(s):** `envoy-despatch`
  These have ≤1 connection - possible missing edges or undocumented components.
- **10 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `DespatchApplication` connect `Icon Resolution` to `Application Model`, `Copy Command Utility`, `Stack State Tracking`, `Bundle Metadata`, `File System Utilities`, `Application Groups`, `Single Instance Lock`, `Launch Worker`, `Path Utilities`, `Global Shortcut`, `Autostart Integration`, `Stack Selection UI`?**
  _High betweenness centrality (0.155) - this node is a cross-community bridge._
- **Why does `MainWindow` connect `Launch Worker` to `Envoy Gateway`, `Copy Command Utility`, `Suppression Logic`, `Keyword Matching`, `Single Instance Lock`, `Build Scripting`, `PyInstaller Config`, `Graphify Skill`, `Stack File Parsing`, `Bundle Discovery`, `Settings Dialog`?**
  _High betweenness centrality (0.122) - this node is a cross-community bridge._
- **Why does `SettingsStore` connect `Catalog Loader` to `Bundle Discovery`, `Single Instance Lock`?**
  _High betweenness centrality (0.097) - this node is a cross-community bridge._
- **What connects `envoy-despatch` to the rest of the system?**
  _1 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Envoy Gateway` be split into smaller, more focused modules?**
  _Cohesion score 0.05827505827505827 - nodes in this community are weakly interconnected._
- **Should `Application Model` be split into smaller, more focused modules?**
  _Cohesion score 0.06914893617021277 - nodes in this community are weakly interconnected._
- **Should `Catalog Loader` be split into smaller, more focused modules?**
  _Cohesion score 0.05555555555555555 - nodes in this community are weakly interconnected._