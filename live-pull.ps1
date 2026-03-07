$remoteName = "neworigin"
$branchName = "main"
$sleepIntervalSeconds = 10

Write-Host "Started auto-pull script for real-time syncing..."

while ($true) {
    # Fetch latest information from remote
    git fetch $remoteName $branchName
    
    # Check if we are behind the remote
    $local = git rev-parse HEAD
    $remote = git rev-parse "$remoteName/$branchName"
    $base = git merge-base HEAD "$remoteName/$branchName"

    if ($local -eq $remote) {
        # Up to date, do nothing
    } elseif ($local -eq $base) {
        Write-Host "Local is behind. Pulling latest changes..."
        # We are behind, can fast-forward
        # Use stash to handle any dirty working directory
        $stashResult = git stash
        git pull $remoteName $branchName
        if ($stashResult -match "Saved working directory") {
            git stash pop
        }
        Write-Host "Successfully pulled at $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
    } elseif ($remote -eq $base) {
        # We are ahead, nothing to pull
    } else {
        Write-Host "Diverged. Manual intervention might be needed for conflict resolution."
    }

    Start-Sleep -Seconds $sleepIntervalSeconds
}
