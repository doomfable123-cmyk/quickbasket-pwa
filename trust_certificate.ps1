# Trust Certificate Script - Run as Administrator
# This script installs the QuickBasket certificate in the trusted root store

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "🔐 QuickBasket Certificate Trust Setup" -ForegroundColor Cyan  
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if running as Administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")

if (-not $isAdmin) {
    Write-Host "❌ This script requires Administrator privileges!" -ForegroundColor Red
    Write-Host "Please right-click PowerShell and 'Run as Administrator'" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "✅ Running with Administrator privileges" -ForegroundColor Green
Write-Host ""

try {
    # Find the QuickBasket certificate
    $cert = Get-ChildItem -Path Cert:\CurrentUser\My | Where-Object {$_.Subject -like '*QuickBasket*'} | Select-Object -First 1
    
    if (-not $cert) {
        Write-Host "❌ QuickBasket certificate not found!" -ForegroundColor Red
        Write-Host "Please run the signing process first." -ForegroundColor Yellow
        Write-Host ""
        Read-Host "Press Enter to exit"
        exit 1
    }
    
    Write-Host "🔍 Found certificate:" -ForegroundColor Green
    Write-Host "   Subject: $($cert.Subject)" -ForegroundColor Gray
    Write-Host "   Thumbprint: $($cert.Thumbprint)" -ForegroundColor Gray
    Write-Host ""
    
    # Export certificate
    Write-Host "📋 Exporting certificate..." -ForegroundColor Yellow
    $certPath = "QuickBasket_Trust.cer"
    Export-Certificate -Cert $cert -FilePath $certPath -Force | Out-Null
    
    # Install in Trusted Root
    Write-Host "🔐 Installing in Trusted Root Certification Authorities..." -ForegroundColor Yellow
    Import-Certificate -FilePath $certPath -CertStoreLocation "Cert:\LocalMachine\Root" -Confirm:$false | Out-Null
    
    # Install in Trusted Publishers  
    Write-Host "📋 Installing in Trusted Publishers..." -ForegroundColor Yellow
    Import-Certificate -FilePath $certPath -CertStoreLocation "Cert:\LocalMachine\TrustedPublisher" -Confirm:$false | Out-Null
    
    # Clean up
    Remove-Item $certPath -Force -ErrorAction SilentlyContinue
    
    Write-Host ""
    Write-Host "✅ Certificate successfully installed in trusted stores!" -ForegroundColor Green
    Write-Host ""
    
    # Verify the executable signature now
    Write-Host "🔍 Checking QuickBasket.exe signature..." -ForegroundColor Yellow
    if (Test-Path "dist\QuickBasket.exe") {
        $sig = Get-AuthenticodeSignature "dist\QuickBasket.exe"
        Write-Host "   Status: $($sig.Status)" -ForegroundColor $(if ($sig.Status -eq "Valid") { "Green" } else { "Red" })
        
        if ($sig.Status -eq "Valid") {
            Write-Host ""
            Write-Host "🎉 SUCCESS! QuickBasket.exe is now properly signed and trusted!" -ForegroundColor Cyan
            Write-Host ""
            Write-Host "✅ What this means:" -ForegroundColor Yellow
            Write-Host "   • Windows Defender warnings reduced"
            Write-Host "   • Shows as verified publisher"
            Write-Host "   • Users see fewer security prompts"
            Write-Host ""
        } else {
            Write-Host "   Message: $($sig.StatusMessage)" -ForegroundColor Red
        }
    } else {
        Write-Host "   ⚠️  QuickBasket.exe not found in dist folder" -ForegroundColor Yellow
    }
    
} catch {
    Write-Host ""
    Write-Host "❌ Error occurred:" -ForegroundColor Red
    Write-Host "   $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Read-Host "Press Enter to exit"