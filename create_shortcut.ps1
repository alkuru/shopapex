# Создание ярлыка для программы загрузки прайса
$WshShell = New-Object -comObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("$env:USERPROFILE\Desktop\Загрузчик прайса.lnk")
$Shortcut.TargetPath = "$env:USERPROFILE\Desktop\PriceUploader\run_uploader.bat"
$Shortcut.WorkingDirectory = "$env:USERPROFILE\Desktop\PriceUploader"
$Shortcut.Description = "Загрузчик прайса АвтоКонтинента"
$Shortcut.IconLocation = "C:\Windows\System32\shell32.dll,21"
$Shortcut.Save()

Write-Host "Ярлык создан на рабочем столе!" -ForegroundColor Green 