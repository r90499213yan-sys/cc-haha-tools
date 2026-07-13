$targets = @(
    "AppData\Local",
    "AppData\Roaming",
    "AppData\LocalLow",
    "Documents",
    "Downloads",
    "Desktop",
    "Pictures",
    "Videos",
    "Music"
)

$userProfile = [Environment]::GetFolderPath("UserProfile")

foreach ($sub in $targets) {
    $p = Join-Path $userProfile $sub
    if (Test-Path $p) {
        $size = 0
        Get-ChildItem -Path $p -Recurse -ErrorAction SilentlyContinue -File | ForEach-Object { $size += $_.Length }
        $gb = [math]::Round($size / 1GB, 2)
        Write-Output ("{0:N2} GB  {1}" -f $gb, $sub)
    }
}
