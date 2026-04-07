# Add Character

Add a new character to `comic_maker/data/character_db.json`.

## Steps

1. Read the current `comic_maker/data/character_db.json` to understand the existing schema and avoid duplicate names.
2. Read `comic_maker/core/models.py` to confirm the `CharacterProfile` required fields: `name`, `static.appearance`.
3. Ask the user for:
   - Character name (must be unique in the DB)
   - Appearance description (English, used verbatim in image prompts — be specific: hair color/style, eye color, clothing, distinguishing features)
   - Any optional fields: `gender`, `role`, `personality`, `voice_style`, or custom `dynamic` state fields
4. Construct a new entry matching the existing JSON structure exactly.
5. Insert the entry into the JSON (maintain alphabetical order by `name` if the file is already sorted).
6. Write the updated file back via the Edit tool — never overwrite the whole file if only one entry is being added.
7. Confirm the entry was written and show the user the final JSON block.

## Rules
- `static.appearance` must be in English (it's injected directly into image prompts).
- Do not add fields that don't exist in the current schema unless the user explicitly requests a schema extension.
- If the user requests a schema extension, also update `comic_maker/core/models.py` and `comic_maker/core/storage.py`.
