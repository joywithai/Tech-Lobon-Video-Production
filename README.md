# Tech Lobon — AI Video Production V1

একটি review-first ভিডিও তৈরির repository: `brief.md` ও optional audio/resources থেকে scene plan, word-timed visual motion, locked channel card, subtitle, event-based SFX, ৩টি thumbnail ও upload information। **Learning Box** user-এর স্পষ্ট correction পরের কাজের জন্য সংরক্ষণ করে।

> **বর্তমান অবস্থা:** V1 source তৈরি করা হয়েছে, কিন্তু owner-এর নির্দেশ অনুযায়ী এখনও কোনো test job বা test video চালানো হয়নি। Runtime dependencies, LLM endpoint, voice, description unit ও কোনো external service configure করা বাকি। পুরো pipeline-এর সফলতা এখনও যাচাই করা হয়নি।

## Repository

```text
input/                         User-এর brief, optional audio ও src/
channel_card/                  আলাদা ও hash-locked Tech Lobon frame
engines/video-making/          Remotion visual renderer ও SFX
engines/thumbnail/             তিনটি PNG layout renderer
learning_box/                  Feedback history ও persistent active rules
references/favstash-.../       FavStash upstream source snapshot
app/                           Input, audio, planning, memory, QA ও CLI
config.yaml                    Channel/provider/format configuration
work/                          Private intermediate data; Git ignored
output/                        Final deliverables; Git ignored
```

## Quick start — পরে test করার সময়

1. `docs/INSTALL.bn.md` অনুসরণ করে Python/Node/FFmpeg dependencies এবং একটি OpenAI-compatible planner configure করো।
2. `config.yaml`-এ description-এর unit (`words` বা `characters`) ও brief-only job-এর জন্য user-approved voice সেট করো।
3. `examples/brief.template.md` দেখে `input/brief.md` তৈরি করো। Optional একটি audio এবং `input/src/`-তে assets দাও।
4. User test চাইলে:

```bash
python -m app run --input input
```

যদি input, provider, timing বা অন্য প্রয়োজনীয় কিছু না থাকে, CLI কাজ থামিয়ে জানাবে। Conversational agent user-এর কাছে তা চাইবে। নিজের account-এ Git repository বা provider নিজে থেকে তৈরি করবে না।

## Learning Box

Output তৈরি হলে pending-review event লেখা হয়। User কোনো সংশোধন দিলে:

```bash
python -m app feedback add --job JOB_ID \
  --observation "User কী অপছন্দ করেছেন" \
  --instruction "ভবিষ্যতে কীভাবে করতে হবে" \
  --scope channel
python -m app feedback list
python -m app revise JOB_ID
```

সক্রিয় rules পরের creative plan-এ দেওয়া হয় এবং প্রতিটি job-এ কোন rules ব্যবহার হয়েছে তার snapshot রাখা হয়। এটি model retraining নয়; সংশোধন কার্যকর হয়েছে কি না final review প্রয়োজন। নিয়ম `learning_box/`-এ থাকে—অন্য clone-এ নিতে চাইলে উপযুক্ত Git sync করতে হবে।

## Locked Channel Card

`channel_card/`-এ user-এর logo/background/reference, layout এবং rendering component আলাদা। শুধু **logo + channel name + main visual + subtitle** থাকবে; page number, progress bar, counter, generic CTA ইত্যাদি থাকবে না। Pipeline SHA-256 lock যাচাই করে। Explicit user request ছাড়া card edit বা lock বদলানো নিষিদ্ধ। Portrait পূর্বের reference ধরে; horizontal user diagram থেকে তৈরি adaptation, এখনও user-approved নয়।

## V1 scope এবং সীমাবদ্ধতা

- Model-powered plan, per-word action validation, actual audio-derived/explicit timing, Remotion renderer, event SFX mixer, 3 thumbnail layouts ও technical QA-এর source যুক্ত আছে। এগুলো এখনও বাস্তব production input দিয়ে যাচাই হয়নি।
- Creative planner-এর জন্য external/local OpenAI-compatible LLM; timing-এর জন্য faster-whisper বা supplied word-timing; TTS-এর জন্য Edge TTS; optional screenshot-এর জন্য Playwright দরকার। কোনো model, credentials বা browser bundle নেই।
- Commons search ও user-requested public HTTPS screenshot/recording আছে। Relevance, license ও page content rights মানব-পরীক্ষা দরকার। কোনো paid stock search বা generative image provider bundled নয়।
- Supplied script ও automatic ASR যথেষ্ট না মিললে job থামে; মিথ্যা timestamps তৈরি করে না। `description_unit` user এখনও স্থির করেননি, তাই production run-এর আগে সেট করতে হবে।
- Scene engine কিছু reusable object/relationship primitive দেয়; sophisticated custom animation ও creative quality এখনো মানুষের review ও ভবিষ্যৎ adapters-এর ওপর নির্ভর করে। Pixel movement মানেই meaningful storytelling নয়।
- Automatic publication বন্ধ; `quality-report.json` কখনও শুনে যাচাই বা creative approval-এর মিথ্যা দাবি করে না।

বিস্তারিত: [`docs/WORKFLOW.bn.md`](docs/WORKFLOW.bn.md), [`docs/INSTALL.bn.md`](docs/INSTALL.bn.md), [`learning_box/README.md`](learning_box/README.md), [`channel_card/README.md`](channel_card/README.md)।
