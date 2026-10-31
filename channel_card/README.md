# Locked Tech Lobon Channel Card

This folder is the single source of truth for the channel frame. It contains the user's real logo, background, the reference diagram, licensed fonts, the layout configuration and its rendering component.

The ONLY channel chrome is: channel logo + channel name, main visual stage, and subtitle. Do not add page numbers, progress bars, timestamps, counters, decorative headers, generic CTA, creator watermarks, or unrelated badges. Story-specific numbers or diagrams inside the visual stage are allowed when actually needed by the script; they are not UI chrome.

Portrait uses the user's prior Tech Lobon reference dimensions. Landscape is a careful adaptation of the user's diagram and still needs user review. Do not assert user approval for the adaptation.

`lock.json` is a SHA-256 change guard. The pipeline checks these files before rendering and refuses changed, missing or extra files inside this folder. This detects edits; it is not DRM or an OS-level permission lock. Only an explicit user request authorizes changing the card and regenerating the lock. The input and output project files must never rewrite this folder.
