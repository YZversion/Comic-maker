# Add Scene

Add a new scene/location to `comic_maker/data/scene_db.json`.

## Steps

1. Read `comic_maker/data/scene_db.json` to understand the current schema and avoid duplicate entries.
2. Ask the user for:
   - Scene/location name (Chinese or English key — match the convention already used in the file)
   - English visual description (injected into image prompts — describe lighting, atmosphere, architectural details, color palette)
   - Optional: time-of-day variants or weather variants if the scene appears in multiple contexts
3. Construct the new entry matching the existing JSON structure.
4. Insert it into the file using the Edit tool.
5. Show the user the written entry and confirm.

## Rules
- The visual description must be in English.
- The key (scene name) must match whatever naming convention the chapter text uses, so `segmenter` and `planner` can look it up correctly.
- Do not restructure the whole file — only insert the new entry.
