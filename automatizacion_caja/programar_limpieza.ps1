# Ejecutar en el equipo que aloja Flask. Sin -Aplicar solo programa revisión.
param([switch]$Aplicar)
$ErrorActionPreference = 'Stop'
$proyectoBuffet = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$pythonBuffet = Join-Path $proyectoBuffet '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $pythonBuffet)) { throw 'No existe el entorno Python del proyecto.' }
$argumentosBuffet = '-m automatizacion_caja.limpiar_logs --dias 90'
if ($Aplicar) { $argumentosBuffet += ' --aplicar --respaldo logs/respaldos-accesos' }
$accionBuffet = New-ScheduledTaskAction -Execute $pythonBuffet -Argument $argumentosBuffet -WorkingDirectory $proyectoBuffet
$disparoBuffet = New-ScheduledTaskTrigger -Daily -At '03:00'
$opcionesBuffet = New-ScheduledTaskSettingsSet -StartWhenAvailable -MultipleInstances IgnoreNew
$usuarioBuffet = [System.Security.Principal.WindowsIdentity]::GetCurrent().Name
$principalBuffet = New-ScheduledTaskPrincipal -UserId $usuarioBuffet -LogonType Interactive -RunLevel Limited
Register-ScheduledTask -TaskName 'BenditoBuffet-RetencionAccesos' -Action $accionBuffet -Trigger $disparoBuffet -Settings $opcionesBuffet -Principal $principalBuffet -Description 'Retención de accesos de 90 días; conserva actividad y respalda antes de eliminar.' -Force
Write-Output 'Tarea diaria registrada a las 03:00. Requiere sesión iniciada; si el equipo no estaba disponible se ejecuta al volver a estarlo.'
