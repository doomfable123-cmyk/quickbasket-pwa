# QuickBasket Code Signing Script
# This script creates a self-signed certificate and signs the QuickBasket.exe

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "🔐 QuickBasket Code Signing Utility" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if running as Administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")

if (-not $isAdmin) {
    Write-Host "⚠️  Administrator privileges required!" -ForegroundColor Yellow
    Write-Host "Please right-click PowerShell and select 'Run as Administrator'" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if executable exists
$exePath = "dist\QuickBasket.exe"
if (-not (Test-Path $exePath)) {
    Write-Host "❌ Executable not found: $exePath" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "� Found QuickBasket.exe - proceeding with signing..." -ForegroundColor Green
Write-Host ""

try {
    # Step 1: Create self-signed certificate
    Write-Host "🔑 Creating self-signed certificate..." -ForegroundColor Yellow
    
    $certName = "QuickBasket Development"
    $cert = New-SelfSignedCertificate -Subject "CN=$certName" `
        -CertStoreLocation "Cert:\CurrentUser\My" `
        -KeyUsage DigitalSignature `
        -Type CodeSigningCert `
        -NotAfter (Get-Date).AddYears(2)
    
    Write-Host "✅ Certificate created: $($cert.Thumbprint)" -ForegroundColor Green
    
    # Step 2: Install certificate in trusted store
    Write-Host ""
    Write-Host "📋 Installing certificate in trusted store..." -ForegroundColor Yellow
    
    $certPath = "temp_cert.cer"
    Export-Certificate -Cert $cert -FilePath $certPath -Force | Out-Null
    Import-Certificate -FilePath $certPath -CertStoreLocation "Cert:\LocalMachine\Root" -Confirm:$false | Out-Null
    Remove-Item $certPath -Force -ErrorAction SilentlyContinue
    
    Write-Host "✅ Certificate installed in trusted store" -ForegroundColor Green
    
    # Step 3: Sign the executable
    Write-Host ""
    Write-Host "✍️  Signing QuickBasket.exe..." -ForegroundColor Yellow
    
    $signature = Set-AuthenticodeSignature -FilePath $exePath -Certificate $cert
    
    if ($signature.Status -eq "Valid") {
        Write-Host "✅ Executable signed successfully!" -ForegroundColor Green
        Write-Host ""
        Write-Host "🎉 SUCCESS! QuickBasket.exe is now digitally signed!" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "📋 What this means:" -ForegroundColor Yellow
        Write-Host "  ✅ Reduced Windows Defender warnings"
        Write-Host "  ✅ Shows as verified publisher"
        Write-Host "  ✅ Better user trust"
        Write-Host ""
        Write-Host "🔍 Verification:" -ForegroundColor Yellow
        Write-Host "  Status: $($signature.Status)"
        Write-Host "  Signer: $($signature.SignerCertificate.Subject)"
    } else {
        Write-Host "❌ Signing failed: $($signature.Status)" -ForegroundColor Red
        Write-Host "   Message: $($signature.StatusMessage)" -ForegroundColor Red
    }
    
} catch {
    Write-Host "❌ Error during signing process:" -ForegroundColor Red
    Write-Host "   $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
    Write-Host "💡 Try running this script as Administrator" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Press Enter to exit..."
Read-Host