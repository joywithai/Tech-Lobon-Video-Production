# Installation / configuration

## Prerequisites

- Python 3.10+ (faster-whisper-এর সমর্থিত version ব্যবহার করো)
- Node.js 20+ / npm
- FFmpeg এবং ffprobe system PATH-এ
- প্রয়োজনে Playwright Chromium
- একটি user-configured OpenAI-compatible LLM endpoint ও model
- Brief-only job-এর জন্য user-approved Edge TTS voice ও network access

Commands (project root থেকে):

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
npm install
python -m playwright install chromium  # শুধু page capture লাগলে
```

Faster-whisper প্রথম run-এ model download করতে পারে এবং CPU/RAM/storage প্রয়োজন। Edge TTS অনলাইন service; availability ও voice supported কি না run-এর সময় নির্ভর করে। Remotion/browser-ও প্রয়োজনীয় browser download চাইতে পারে। Downloads ও external provider ব্যবহারে তাদের terms পরীক্ষা করো।

## LLM configuration

```bash
export VME_LLM_BASE_URL="https://YOUR_COMPATIBLE_PROVIDER/v1"
export VME_LLM_MODEL="YOUR_MODEL"
export VME_LLM_API_KEY="YOUR_KEY"
```

Local OpenAI-compatible endpoint উদাহরণ `http://localhost:11434/v1` হতে পারে; সেটি আলাদাভাবে install/run করতে হয়। Key দরকার না হলে ফাঁকা রাখা যায়। `.env.example` শুধু template; app `.env` নিজে পড়ে না—shell-এ environment variables সেট করো। API key বা personal files Git-এ দিও না। Hosted provider-এ brief, word timing, resource names ও learning rules পাঠানো হয়; sensitive input দেওয়া আগে privacy বিবেচনা করো।

`config.yaml`-এ প্রয়োজনমতো `description_unit: words` অথবা `characters` এবং user-approved TTS voice সেট করো। Input-এ audio থাকলে TTS voice লাগবে না।

## Run পরে

```bash
# Copy your own brief to input/brief.md, and optional audio/assets.
python -m app run --input input
python -m app feedback list
```

User এখন test করতে বলেননি, তাই নতুন implementation কোনো test job বা video দিয়ে চালানো হয়নি। পরবর্তী test-এর জন্য user-এর input প্রয়োজন।
