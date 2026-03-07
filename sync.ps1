$remoteName = "neworigin"
$branchName = "main"
$sleepIntervalSeconds = 10

Write-Host "========== REAL-TIME SYNC STARTED =========="
Write-Host "Target: $remoteName/$branchName"
Write-Host "Interval: $sleepIntervalSeconds seconds"
Write-Host "============================================"

while ($true) {
    # 1. PULL CHANGES (Syncing with remote)
    git fetch $remoteName $branchName
    $local = git rev-parse HEAD
    $remote = git rev-parse "$remoteName/$branchName"
    $base = git merge-base HEAD "$remoteName/$branchName"

    if ($local -ne $remote -and $local -eq $base) {
        Write-Host "[$(Get-Date -Format 'HH:mm:ss')] Remote changes detected. Pulling..."
        $stashResult = git stash
        git pull $remoteName $branchName
        if ($stashResult -match "Saved working directory") {
            git stash pop
        }
        Write-Host "[$(Get-Date -Format 'HH:mm:ss')] Pull successful."
    } elseif ($local -ne $remote -and $remote -ne $base) {
        Write-Host "[$(Get-Date -Format 'HH:mm:ss')] WARNING: Branches have diverged. Conflicts may occur."
    }

    # 2. PUSH CHANGES (Syncing with local)
    $status = git status --porcelain
    if ($status) {
        Write-Host "[$(Get-Date -Format 'HH:mm:ss')] Local changes detected. Committing and pushing..."
        git add .
        $date = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        git commit -m "Auto-commit at $date"
        git push $remoteName $branchName
        Write-Host "[$(Get-Date -Format 'HH:mm:ss')] Push successful."
    }

    Start-Sleep -Seconds $sleepIntervalSeconds
}
