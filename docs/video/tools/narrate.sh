#!/bin/zsh
# AI narration per shot: OpenAI gpt-4o-mini-tts (voice "marin"), key read from the macOS Keychain at run time.
# Usage: docs/video/tools/narrate.sh [s01 s02 ...]   (default: every narr/s*.txt)
set -e
cd "${0:A:h}/../narr" && mkdir -p raw
ids=(${@:-${(@)$(ls s*.txt | sed 's/\.txt$//')}})
for id in $ids; do
  python3 -c 'import json,sys;print(json.dumps({"model":"gpt-4o-mini-tts","voice":"marin","input":open(sys.argv[1]).read().strip(),"instructions":"Calm, confident product-demo narrator. Clear American English, measured pace, slight warmth, no hype.","response_format":"wav"}))' $id.txt > raw/.req.json
  code=$(curl -sS -o raw/$id.wav -w '%{http_code}' https://api.openai.com/v1/audio/speech -H "Authorization: Bearer $(security find-generic-password -s openai-api-key -w)" -H "Content-Type: application/json" --data @raw/.req.json)
  [ "$code" = 200 ] || { echo "$id HTTP $code"; continue; }
  ffmpeg -loglevel error -y -i raw/$id.wav -af "silenceremove=start_periods=1:start_threshold=-50dB:start_silence=0.05,areverse,silenceremove=start_periods=1:start_threshold=-50dB:start_silence=0.08,areverse,loudnorm=I=-16:TP=-1.5:LRA=11,aresample=48000" -ar 48000 -ac 1 $id.wav
  echo "$id $(ffprobe -v error -show_entries format=duration -of csv=p=0 $id.wav)"
done
rm -f raw/.req.json
