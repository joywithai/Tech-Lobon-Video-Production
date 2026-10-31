# Video Making Engine

The renderer accepts a validated `plan.json` built from real narration word timings, explicit scene nodes/connections, per-word target actions and event-specific SFX. It uses the locked `channel_card/BrandCard.tsx`, and writes a silent H.264 stage render. The Python orchestrator mixes narration and SFX after rendering and emits the final MP4.

Scene types are intentionally data-bound: server/client/token/person/screen/code/image/shield/clock/text. Relationships and object actions come from a creative planner; a missing provider or invalid scene plan is a blocked job, not a falsely successful video. The engine provides starter movement; complex artistic concepts may require future scene adapters and real creative review. No software can infer that every animation is artistically meaningful from pixel change alone.

FavStash source snapshot is in `references/favstash-ai-video-editing-skills/`; the engine includes only original synthesized FavStash SFX, retaining the manifest and attribution. Curated recordings and preview images are not automatically reused.
