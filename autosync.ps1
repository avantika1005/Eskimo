$repoPath = "C:\Users\Sam\Desktop\hkt"
$gitExe = "C:\Program Files\Git\cmd\git.exe"

Set-Location $repoPath
Write-Host "Auto-sync started for $repoPath"

while ($true) {
    # Check if there are any changes (modified, deleted, or untracked files)
    $status = & $gitExe status --porcelain
    
    if ($status) {
        $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        Write-Host "Changes detected at $timestamp. Syncing..."

        # Add all changes
        & $gitExe add -A

        # Commit changes
        & $gitExe commit -m "Auto-sync update at $timestamp"

        # Push changes to the main branch
        & $gitExe push origin main

        Write-Host "Sync completed."
    }
    
    # Wait for 10 seconds before checking again
    Start-Sleep -Seconds 10
}
