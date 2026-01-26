# Commit & Push Instructions

Run these commands locally in your repository to create a branch, commit the recent changes, and push to origin.

Open a terminal in the project root and run:

```powershell
# Create and switch to a new feature branch
git checkout -b feat/fix-rate-limit-debounce

# Stage changed files (adjust paths if you changed others)
git add backend/routers/system.py src/store/orgStore.ts src/system/systemStore.ts .patch_instructions/PR_DESCRIPTION.md

# Commit
git commit -m "fix(system): handle root org-less requests; debounce org/profile fetches; dev-only rate-limit clamp"

# Push branch
git push -u origin feat/fix-rate-limit-debounce

# Optionally open a PR using GitHub CLI
# gh pr create --fill --title "fix(system): handle root org-less requests; debounce org/profile fetches" --body-file .patch_instructions/PR_DESCRIPTION.md
```

Notes:

- If `git` is not installed, install it first: https://git-scm.com/downloads
- If you use the GitHub CLI (`gh`), the `gh pr create` command will open an interactive PR creation flow using the PR description we created.
- If your remote uses a different name than `origin`, replace it accordingly.
