# PowerShell helper to create branch, commit and push changes
# Run this from project root in a shell where git is available.

$branch = 'feat/fix-rate-limit-debounce'

Write-Host "Switching/creating branch: $branch"
if (-not (git rev-parse --verify $branch -q)) {
  git checkout -b $branch
} else {
  git checkout $branch
}

Write-Host "Staging files..."
git add backend/routers/system.py src/store/orgStore.ts src/system/systemStore.ts .patch_instructions/PR_DESCRIPTION.md

Write-Host "Committing..."
git commit -m "fix(system): handle root org-less requests; debounce org/profile fetches; dev-only rate-limit clamp" || Write-Host "No changes to commit"

Write-Host "Pushing to origin/$branch..."
git push -u origin $branch

Write-Host "Done. If you have GitHub CLI installed, run:\n gh pr create --fill --title \"fix(system): handle root org-less requests; debounce org/profile fetches\" --body-file .patch_instructions/PR_DESCRIPTION.md"
