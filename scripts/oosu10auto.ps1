<# 
.SYNOPSIS
    Downloads and runs O&O ShutUp10 with various modes, including:
      - GUI mode ("customize")
      - Applying recommended settings ("recommended")
      - Resetting policies to factory defaults ("undo")
      - Reverting settings by inverting the recommended config ("revert")

.DESCRIPTION
    The script creates a unique temporary folder where it downloads the O&O ShutUp10 executable.
    For the "recommended" and "revert" actions it checks for a local "OOSU10.cfg" file
    in the same folder as the script. If not found, it downloads the file from a specified URL.
    
    • In "recommended" mode, the config file is used as-is.
    • In "revert" mode, the script reads the recommended config file and generates an inverse version by
      swapping the setting state:
         - A line like "P001    +   # ..." becomes "P001    -   # ..."
         - And vice versa.
    
    After O&O ShutUp10 completes (or the GUI is closed), the script cleans up by deleting the temporary
    folder and its contents.

.PARAMETER action
    Specifies how O&O ShutUp10 should run:
      - customize   : Launch the GUI.
      - recommended : Apply recommended settings silently.
      - undo        : Reset settings to factory defaults silently.
      - revert      : Revert settings by inverting the recommended config.

.EXAMPLE
    .\OOSU10-Auto.ps1 -action revert -Verbose
#>

param (
    [Parameter(Mandatory = $true)]
    [ValidateSet("customize", "recommended", "undo", "revert")]
    [string]$action
)

# Increase verbosity for debugging.
$VerbosePreference = "Continue"

# Save original progress setting and suppress progress during downloads.
$Initial_ProgressPreference = $ProgressPreference
$ProgressPreference = "SilentlyContinue"

# Define URLs for downloads.
$exeURL    = "https://dl5.oo-software.com/files/ooshutup10/OOSU10.exe"
# Replace the URL below with the actual location of your recommended config file if needed.
$configURL = "https://raw.githubusercontent.com/DTLegit/Windows-OOSU10-Auto-Script/refs/heads/main/OOSU10.cfg"

# Create a unique temporary folder.
$tempDir = Join-Path $env:TEMP ("OOSU10_temp_" + [guid]::NewGuid().ToString())
try {
    New-Item -ItemType Directory -Path $tempDir -Force | Out-Null
    Write-Verbose "Created temporary directory: $tempDir"
} catch {
    Write-Error "Failed to create temporary directory: $_"
    exit 1
}

# Define the path for the O&O ShutUp10 executable.
$exePath = Join-Path $tempDir "OOSU10.exe"

# Download O&O ShutUp10 executable.
Write-Verbose "Downloading O&O ShutUp10 from $exeURL"
try {
    Invoke-WebRequest -Uri $exeURL -OutFile $exePath -ErrorAction Stop
    Write-Verbose "Downloaded O&O ShutUp10 to: $exePath"
} catch {
    Write-Error "Failed to download O&O ShutUp10: $_"
    Remove-Item $tempDir -Recurse -Force
    exit 1
}

# Function to obtain the recommended config file.
function Get-RecommendConfigFile {
    param(
        [string]$destPath
    )
    # Check for a local config file in the same directory as the script.
    $localConfigPath = Join-Path $PSScriptRoot "OOSU10.cfg"
    if (Test-Path $localConfigPath) {
        Write-Verbose "Found local recommended config file at: $localConfigPath"
        try {
            Copy-Item -Path $localConfigPath -Destination $destPath -Force
            Write-Verbose "Copied recommended config to temporary directory: $destPath"
        } catch {
            Write-Error "Failed to copy local recommended config file: $_"
            Remove-Item $tempDir -Recurse -Force
            exit 1
        }
    } else {
        Write-Verbose "Local recommended config file not found. Downloading from $configURL"
        try {
            Invoke-WebRequest -Uri $configURL -OutFile $destPath -ErrorAction Stop
            Write-Verbose "Downloaded recommended config file to: $destPath"
        } catch {
            Write-Error "Failed to download recommended config file: $_"
            Remove-Item $tempDir -Recurse -Force
            exit 1
        }
    }
}

# Main action switch.
switch ($action) {
    "customize" {
        Write-Verbose "Launching O&O ShutUp10 in GUI mode..."
        try {
            Start-Process -FilePath $exePath -Wait -Verbose
        } catch {
            Write-Error "Failed to start O&O ShutUp10: $_"
        }
    }
    "recommended" {
        $configPath = Join-Path $tempDir "OOSU_10-Recommended.cfg"
        Get-RecommendConfigFile -destPath $configPath

        Write-Verbose "Executing O&O ShutUp10 with recommended configuration..."
        try {
            Start-Process -FilePath $exePath -ArgumentList $configPath, '/quiet' -Wait -Verbose
        } catch {
            Write-Error "Failed to apply recommended configuration: $_"
        }
    }
    "undo" {
        $configPath = Join-Path $tempDir "OOSU_10-Factory.cfg"
        Write-Verbose "Creating factory default configuration file at: $configPath"
        try {
            @"
# Factory default configuration for O&O ShutUp10.
# (Insert settings to reset policies to factory defaults)
"@ | Out-File -FilePath $configPath -Force -Encoding UTF8
        } catch {
            Write-Error "Failed to create factory default config file: $_"
            Remove-Item $tempDir -Recurse -Force
            exit 1
        }

        Write-Verbose "Executing O&O ShutUp10 with factory default configuration..."
        try {
            Start-Process -FilePath $exePath -ArgumentList $configPath, '/quiet' -Wait -Verbose
        } catch {
            Write-Error "Failed to apply factory default configuration: $_"
        }
    }
    "revert" {
        # First, obtain the recommended config file (either local or downloaded).
        $originalConfigPath = Join-Path $tempDir "OOSU_10-Recommended.cfg"
        Get-RecommendConfigFile -destPath $originalConfigPath

        # Now generate an inverse config file based on the example format.
        # The expected format for setting lines is:
        #   CODE    [+/–]    # Comment...
        $inverseConfigPath = Join-Path $tempDir "OOSU_10-Revert.cfg"
        Write-Verbose "Generating inverse (revert) configuration file at: $inverseConfigPath"
        try {
            $originalLines = Get-Content $originalConfigPath
            $inverseLines = foreach ($line in $originalLines) {
                $trimLine = $line.Trim()
                # Preserve blank lines or comment lines (starting with '#').
                if ($trimLine -eq "" -or $trimLine.StartsWith("#")) {
                    $line
                }
                # Match lines like "P001    +   # Disable ..." or "P009    -   # Disable ..."
                elseif ($trimLine -match "^(?<code>\S+)\s+(?<state>[+-])\s+(?<comment>.*)$") {
                    $code = $matches['code']
                    $state = $matches['state']
                    $comment = $matches['comment']
                    if ($state -eq '+') {
                        # Invert plus to minus.
                        "$code`t-`t$comment"
                    } elseif ($state -eq '-') {
                        "$code`t+`t$comment"
                    } else {
                        $line
                    }
                }
                else {
                    # For any lines that don't match the expected pattern, leave them unchanged.
                    $line
                }
            }
            # Save the inverse configuration file.
            $inverseLines | Out-File -FilePath $inverseConfigPath -Force -Encoding UTF8
            Write-Verbose "Inverse configuration file created successfully."
        } catch {
            Write-Error "Failed to generate inverse configuration file: $_"
            Remove-Item $tempDir -Recurse -Force
            exit 1
        }

        Write-Verbose "Executing O&O ShutUp10 with inverse configuration to revert settings..."
        try {
            Start-Process -FilePath $exePath -ArgumentList $inverseConfigPath, '/quiet' -Wait -Verbose
        } catch {
            Write-Error "Failed to run O&O ShutUp10 with the inverse configuration: $_"
        }
    }
}

# Restore original progress setting.
$ProgressPreference = $Initial_ProgressPreference

# Cleanup: Delete the temporary folder and its contents.
Write-Verbose "Cleaning up temporary files in: $tempDir"
try {
    Remove-Item $tempDir -Recurse -Force
    Write-Verbose "Temporary directory removed."
} catch {
    Write-Warning "Failed to remove temporary directory: $_"
}

Write-Host "Script completed."
