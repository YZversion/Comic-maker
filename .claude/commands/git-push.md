# Git Push

Safety-check, commit, and push all local changes to GitHub.

## Steps

1. Run the following in parallel:
   - `git status` — see what's staged/unstaged/untracked
   - `git diff` — see unstaged changes
   - `git diff --cached` — see staged changes
   - `git log --oneline -5` — see recent commit style

2. **Security scan** — scan staged + unstaged diffs for secrets before doing anything else:
   ```bash
   git diff HEAD | grep -iE 'sk-|AIza|api_key\s*=\s*["\x27][^"\x27]+|secret\s*=\s*["\x27][^"\x27]+|token\s*=\s*["\x27][^"\x27]+|bearer\s+[a-z0-9_\-]{20,}'
   ```
   If any matches are found: **stop immediately**, show the user the matched lines, and do not proceed.

3. Check that `.env` is NOT in the staged files. If it is, unstage it and warn the user.

4. Show the user a summary of what will be committed:
   - List of changed files (grouped: modified / new / deleted)
   - Proposed commit message (drafted from the diff)
   Ask for confirmation before proceeding.

5. Stage and commit:
   ```bash
   git add <specific files — never git add -A blindly>
   git commit -m "..."
   ```

6. Push:
   ```bash
   git push origin HEAD
   ```
   If the push fails because the remote has new commits: run `git pull --rebase origin HEAD` first, then push again.

7. Show the GitHub URL of the pushed commit (from `git remote get-url origin` + last commit hash).

## Commit message format

Follow the repo's existing style (check `git log`). Default format:
```
<type>: <short summary>

<optional body — what changed and why, not how>
```
Types: `feat`, `fix`, `refactor`, `docs`, `test`, `chore`

## Safety rules

- Never commit `.env`, `*.log`, or files in `comic_maker/output/` or `comic_maker/data/panel_manifest.json`.
- Never use `git add -A` or `git add .` — always add files by name.
- Never force-push (`--force`) without explicit user instruction.
- Never skip hooks (`--no-verify`).
- If there is nothing to commit (clean working tree), say so and stop.
- If the user says "push everything" or similar, still do the security scan first.
