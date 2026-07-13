param(
    [string]$Path
)

if (-not (Test-Path $Path)) {
    Write-Output "Path not found: $Path"
    exit
}

$items = Get-ChildItem -Path $Path -Directory -ErrorAction SilentlyContinue
$results = @()

foreach ($item in $items) {
    $size = 0
    Get-ChildItem -Path $item.FullName -Recurse -ErrorAction SilentlyContinue -File | ForEach-Object { $size += $_.Length }
    $gb = [math]::Round($size / 1GB, 2)
    if ($gb -gt 0.1) {
        $results += [PSCustomObject]@{ SizeGB = $gb; Name = $item.Name }
    }
}

$results | Sort-Object SizeGB -Descending | ForEach-Object {
    Write-Output ("{0:N2} GB  {1}" -f $_.SizeGB, $_.Name)
}
