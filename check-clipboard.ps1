Add-Type -AssemblyName System.Windows.Forms
$clip = [System.Windows.Forms.Clipboard]::GetDataObject()
if ($clip -eq $null) {
    Write-Host "Clipboard is empty"
} else {
    $formats = $clip.GetFormats()
    Write-Host "Clipboard formats:"
    foreach ($f in $formats) {
        Write-Host "  $f"
    }
    if ($clip.ContainsImage()) {
        Write-Host "IMAGE: YES"
        $img = $clip.GetImage()
        Write-Host "Size: $($img.Width)x$($img.Height)"
    } else {
        Write-Host "IMAGE: NO"
    }
}
