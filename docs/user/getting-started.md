# Getting Started

Despatch normally runs in the Windows notification area. Your studio may start
it automatically when you sign in, or provide it as an Envoy command.

## Open the launcher

Use whichever method your studio supports:

- Left-click the Despatch icon in the notification area.
- Press the configured global shortcut. The default is ++ctrl+alt+space++.
- Run `envoy despatch --popup` from PowerShell.
- Run the standalone `despatch.exe`.

Closing the launcher hides it; Despatch remains available in the notification
area. Choose **Quit** from its tray menu to stop it completely.

## Choose your environment

The **Stack** selector at the top of the launcher chooses the complete runtime
environment used by every displayed application.

1. Open the Stack selector.
2. Select a named Stack supplied by your studio, such as **studio** or
   **production**.
3. Wait for the catalog to refresh.
4. If you were given a Stack file directly, choose **Choose custom Stack…** and
   select its `.estack` file.

The choice is shared with Envoy command-line tools. See
[Choosing a Stack](stacks.md) for Automatic resolution and custom files.

## Find and launch an application

- Type part of an application's name, description, command, or keyword in the
  search box.
- Select an application to start it.
- Press ++enter++ to launch the first visible search result.
- Right-click an application for terminal, favorite, and command-copy actions.

Despatch hides after a successful launch unless **Keep launcher open after
starting an app** is enabled in Settings.

## Understand the sections

| Section | Meaning |
|---|---|
| Favorites | Applications you marked for quick access |
| Recent | Applications you launched most recently |
| Named sections | Groups defined by bundle authors, such as Creative or Development |
| Other | Applications whose manifests do not assign a group |

An application can appear in Favorites or Recent as well as its normal group.
