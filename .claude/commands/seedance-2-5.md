---
description: Generate a video with Seedance 2.5 through Kie
argument-hint: "[video description]"
---

Use the `kie_generate_video` MCP tool now.

- Set `model` to `bytedance/seedance-2-5`.
- Pass the user's request as `prompt`: `$ARGUMENTS`.
- Set `input` to `{ "duration": 5, "resolution": "720p", "aspect_ratio": "16:9", "generate_audio": false }` unless the user explicitly requests different settings.
- If `$ARGUMENTS` is empty, ask for the video description before using the tool.
- The tool returns a `task_id`; do not start another generation. Check the same task with `kie_get_task` after 30 seconds, then return the video URL when it is ready.
