## для powershell
function Show-Tree {
    param (
        [string]$Path = (Get-Location),
        [int]$Indent = 0
    )
    $items = Get-ChildItem -Path $Path
    foreach ($item in $items) {
        Write-Host (' ' * $Indent) + '+--' + $item.Name
        if ($item.PSIsContainer) {
            Show-Tree -Path $item.FullName -Indent ($Indent + 4)
        }
    }
}

Show-Tree
