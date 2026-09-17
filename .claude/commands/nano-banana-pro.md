---
description: Generate an image with Nano Banana Pro through Kie
argument-hint: "[image description]"
---

Use the `kie_generate_image` MCP tool now.

- Set `model` to `google/nano-banana-pro`.
- Use `2K`, PNG, and `1:1` unless the user specifies another resolution, format, or aspect ratio.
- Pass the user's request as `prompt`: `$ARGUMENTS`.
- If `$ARGUMENTS` is empty, ask for the image description before using the tool.
- Return the resulting image URL and the settings used.
