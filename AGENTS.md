# Agent operating instructions — Tech Lobon Video Production V1

## Start
1. Read `README.md`, `docs/WORKFLOW.bn.md`, `channel_card/README.md` and `learning_box/README.md`.
2. Identify the user's goal and check `input/brief.md`, optional audio, `input/src/`, config and required services. If input is missing, ask the user; do not invent a script. Local CLI reports missing input; the conversational agent asks.
3. The current owner requested creation first and will supply input and ask for a test later. Do not create a demo or run a test job before they ask.
4. Follow active `learning_box/rules.json` for the channel/project in every creative plan. `python -m app run` records applied rules in the job.

## Locked card
`channel_card/` is user-owned, separately locked and checked by hash. Its only channel chrome is logo, channel name, visual stage, and subtitle. No pagination, page numbers, progress strips, counters, generic CTAs, extra watermark or unrelated decorative overlay. Story-relevant numbers/graphics inside the stage may be used only when content requires them. Never change this folder or re-lock it without an explicit user instruction authorizing that specific change. The horizontal layout is an adaptation, not yet user-approved.

## Creative and audio rules
- Meaningful visual actions driven by narration, not a static slide with subtitle changes or a generic loop pretending to be relevant animation. Use objects, character, visual states, images, diagrams, screenshots and transitions appropriate to the story. Word-level target checks do not guarantee quality; inspect/listen to encoded output during user-authorized review.
- User-approved words spoken in audio remain spoken; English technical terms are written as English in subtitle display. Never automatically read an example token, code or random characters aloud. Preserve screen-only exact contents visually.
- Do not replace user's narration, remove material or make claims without authorization. Audio word timing must be real evidence; ASR is not human verification. Ask for reviewed timing if audio/script do not align.
- Use user-provided assets first. Record online source and rights. The bundled Commons search and explicit public-URL capture do not verify creative relevance or content rights. No login/private-network capture. Do not invent assets.
- FavStash snapshot and upstream notices are in `references/`. Use applicable editing guidance, never use preview imagery or curated sound as licensed stock by assumption. Engine SFX are separately identified original Apache-2.0 synthesis.
- Technical QA or pixel motion metrics do not prove creative quality or audio sync. Never claim listening or publication approval that did not happen.

## Feedback and Learning Box
After each completed output the pipeline logs a pending-review checkpoint. When the user gives an explicit correction, summarize it accurately and call `python -m app feedback add ...`; select project scope for one-off feedback, channel scope only for a channel-wide preference, global only if requested. Do not invent feedback, silently generalize, or put secrets in memory. Apply active rules to future jobs. If rules conflict, ask. A revision uses `python -m app revise JOB_ID` and produces a new version; do not overwrite previous output.

## Delivery
Output is review-only: Video.mp4, three PNG thumbnails, uploadInfo.txt and Subtitle.srt. No automatic upload/publication. No external secrets in Git, no input/work/output private media committed by default. Distinguish implemented, configured, and actually verified capabilities; this V1 has not yet had the owner's requested test input.
