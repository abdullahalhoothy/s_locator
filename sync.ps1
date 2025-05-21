$ErrorActionPreference = "Continue"
$scriptPath = $PSScriptRoot
$source = "F:\git\s_locator"
$destination = "G:\My Drive\Personal\Work\offline\Jupyter\Git\s_locator"
$logFile = "$source\logs\sync_log_$(Get-Date -Format 'yyyy-MM-dd').txt"
$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"

# Create log directory if it doesn't exist
$logDir = "$source\logs"
if (!(Test-Path $logDir)) {
    New-Item -ItemType Directory -Path $logDir -Force
}

# Log start of sync
Add-Content -Path $logFile -Value "[$timestamp] Starting sync from '$source' to '$destination'"
Add-Content -Path $logFile -Value "[$timestamp] Script running from: $scriptPath"

try {
    # Check if source exists
    if (!(Test-Path $source)) {
        throw "Source folder does not exist: $source"
    }
    
    # Create destination directory if it doesn't exist
    if (!(Test-Path $destination)) {
        New-Item -ItemType Directory -Path $destination -Force
        Add-Content -Path $logFile -Value "[$timestamp] Created destination directory: $destination"
    }
    
    # Run robocopy with mirror option
    $robocopyArgs = @(
        "`"$source`"",
        "`"$destination`"",
        "/MIR",
        "/R:3",
        "/W:5",
        "/NP",
        "/NDL",
        "/LOG+:`"$logFile`""
    )
    
    Add-Content -Path $logFile -Value "[$timestamp] Running: robocopy $($robocopyArgs -join ' ')"
    
    $result = & robocopy @robocopyArgs
    $exitCode = $LASTEXITCODE
    
    # Robocopy exit codes: 0-7 are success, 8+ are errors
    if ($exitCode -lt 8) {
        $message = "[$timestamp] Sync completed successfully (Exit code: $exitCode)"
        Add-Content -Path $logFile -Value $message
        Write-Host $message -ForegroundColor Green
    } else {
        $message = "[$timestamp] Sync completed with errors (Exit code: $exitCode)"
        Add-Content -Path $logFile -Value $message
        Write-Host $message -ForegroundColor Yellow
    }
    
} catch {
    $errorMessage = "[$timestamp] Sync failed: $($_.Exception.Message)"
    Add-Content -Path $logFile -Value $errorMessage
    Write-Host $errorMessage -ForegroundColor Red
    exit 1
}

Add-Content -Path $logFile -Value "[$timestamp] Sync operation finished"
Add-Content -Path $logFile -Value "----------------------------------------"