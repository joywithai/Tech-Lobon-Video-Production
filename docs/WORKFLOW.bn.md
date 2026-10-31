# V1 পূর্ণ workflow

```text
Repository instructions
   -> input folder ও প্রয়োজনীয় সেটিং পরীক্ষা
   -> brief পড়া
   -> narration বনাম screen-only data আলাদা
   -> দেওয়া audio ব্যবহার / অনুমোদিত voice দিয়ে narration তৈরি
   -> বাস্তব audio থেকে word timing, অথবা supplied timing
   -> resource সংগ্রহ, source ও license record
   -> learning-box এর সক্রিয় নিয়ম পড়া
   -> model দিয়ে scene/word action, 3 thumbnail, 3 title ও description plan
   -> plan validity ও সম্পূর্ণ timing coverage পরীক্ষা
   -> LOCKED channel card + Video Making Engine
   -> SFX ও voice mix
   -> 3 PNG + uploadInfo + subtitle
   -> technical QA ও pending human review
   -> output checkpoint learning box-এ
   -> user feedback দিলে নিয়ম সংরক্ষণ
   -> আগের input snapshot ও নতুন নিয়ম দিয়ে revision
```

## Input

`input/brief.md` দরকার। `examples/brief.template.md`-এর format অনুসরণ করো। `input/`-এ একটি `.mp3`, `.wav`, `.m4a`, `.aac`, `.flac` বা `.ogg` narration রাখা যায়। একাধিক audio থাকলে অস্পষ্টতা এড়াতে কাজ থামে। Image বা video দাও `input/src/`-তে। শুধুমাত্র brief হলে `providers.voice` বা brief-এর `voice`-এ user-approved Edge TTS voice দিতে হবে।

`[SCREEN_ONLY] ... [/SCREEN_ONLY]` বা fenced code হলো screen-এর জন্য; তা TTS-এ যাবে না। Natural spoken explanation নিজে script-এ দিতে হবে। Spoken narration-এ raw JWT/দীর্ঘ code পাওয়া গেলে এটি আটকে দেয়, নিজে থেকে বক্তব্য বদলায় না।

## Audio ও timing

যদি `input/word-timing.json` থাকে, তার `words` array-তে প্রতিটি spoken word-এর `word`, `start`, `end` থাকতে হবে; সময় সঠিক ক্রমে ও audio duration-এর ভেতরে হতে হবে। এটি supplied/unverified হিসেবে চিহ্নিত হয়। না থাকলে `faster-whisper` audio থেকে timestamps নেয়। Whisper যদি script-এর সব শব্দ মেলাতে না পারে, `work/<job>/audio-timing.json`-এ diagnostic রেখে থামে—কোনো ফাঁকা timestamp আন্দাজ করে ভরে না। Faster-whisper output-ও মানব-শ্রবণ যাচাই নয়।

## Resources

প্রথমে user-এর src files। নির্দিষ্ট real-world প্রয়োজন থাকলে planner-এর query দিয়ে optional Wikimedia Commons search; license metadata ও source রাখা হয়। Downloaded image-এর relevance ও rights মানব review দরকার। User frontmatter-এ explicit `capture_urls` দিলে Playwright public HTTPS page screenshot নিতে পারে; `record_seconds` 1–30 হলে screen recording নেয়। Login/private URLs অনুমোদিত নয়। অন্যান্য search providers বা copyrighted stock libraries অন্তর্ভুক্ত নয়।

## Planning ও video

Configured OpenAI-compatible LLM-কে audio words, script, visual-only data, resource IDs এবং সক্রিয় learning rules দেওয়া হয়। Provider user-configured; এই repository নিজে LLM model bundle করে না। Plan-এ scene duration, node type, links, প্রতিটি word-এর লক্ষ্য ও action, semantic SFX, English display spelling, তিনটি thumbnail/title ও description থাকে। Strict validator সম্পূর্ণ timeline coverage, সব word-এর জন্য action, target, asset, sound এবং output metadata যাচাই করে। Model ভুল plan দিলে job আটকে যায়। এটি artistic quality বা নিখুঁত sync প্রমাণ করে না।

Video engine কেবল locked `channel_card` ব্যবহার করে; সম্পূর্ণ visual stage-এর ভেতরে server, client, person, token, image, video, shield, clock, screen, text ও code node animate করে। Complex animation-এর জন্য অতিরিক্ত creative adapters ভবিষ্যতে লাগতে পারে। Generic movement-কে meaningful storytelling হিসেবে ধরে নেওয়া যাবে না। Screen-only text যেন হুবহু দৃশ্যে থাকে, validator তা দেখে; অতিরিক্ত লম্বা code একাধিক node-এ ভাগ করতে হবে।

## Output ও QA

```text
output/<job-id>/
  Video.mp4
  Thumbnail1.png
  Thumbnail2.png
  Thumbnail3.png
  uploadInfo.txt
  Subtitle.srt
```

`work/<job-id>/`-এ input snapshot, timing, resource/source metadata, applied learning rules, creative plan, render plan, SFX ও quality report থাকে। Job collision হলে overwrite করে না। Technical QA পুরো video decode করে এবং visual-stage frame difference নোট করে; এটি শ্রবণ বা creative review-এর বিকল্প নয়। সম্পূর্ণ video, SFX, captions, resource rights ও factual correctness user/মানুষ review করবে। Automatic publishing নেই।

## Learning ও revision

প্রতিটি সফল output-এর পর `learning_box/events.jsonl`-এ pending review checkpoint যুক্ত হয়। User feedback দিলে নির্দিষ্ট observation ও instruction rule হিসেবে যোগ করো:

```bash
python -m app feedback add --job JOB_ID \
  --observation "Animation too static" \
  --instruction "Use relevant action during narration" \
  --scope channel
python -m app feedback list
python -m app revise JOB_ID
```

Revision একটি নতুন job/output; পুরোনোটি overwrite নয়। Rule global নয় যদি user global বলেননি। বিরোধপূর্ণ নিয়ম পেলে user-এর সিদ্ধান্ত নাও। Model retraining হয় না; এটি persistent instruction memory। Repository Git-এ push না করলে local feedback অন্য clone-এ যাবে না।
