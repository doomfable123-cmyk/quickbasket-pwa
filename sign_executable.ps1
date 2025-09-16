# QuickBasket Code Signing Script
# This script creates a self-signed certificate and signs the QuickBasket.exe

param(
    [string]$ExePath = "dist\QuickBasket.exe",
    [string]$CertName = "QuickBasket Development Certificate"
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "🔐 QuickBasket Code Signing Utility" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if running as Administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")

if (-not $isAdmin) {
    Write-Host "⚠️  Administrator privileges required for certificate installation!" -ForegroundColor Yellow
    Write-Host "Please run this script as Administrator." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Right-click PowerShell and select 'Run as Administrator', then run:"
    Write-Host "  .\sign_executable.ps1" -ForegroundColor Green
    exit 1
}

# Check if executable exists
if (-not (Test-Path $ExePath)) {
    Write-Host "❌ Executable not found: $ExePath" -ForegroundColor Red
    Write-Host "Please ensure QuickBasket.exe exists in the dist folder." -ForegroundColor Red
    exit 1
}

Write-Host "📋 Certificate Details:" -ForegroundColor Yellow
Write-Host "  Name: $CertName"
Write-Host "  Type: Self-Signed (Development)"
Write-Host "  Valid: 2 years"
Write-Host ""

try {
    # Step 1: Create self-signed certificate
    Write-Host "🔑 Creating self-signed certificate..." -ForegroundColor Green
    $cert = New-SelfSignedCertificate -Subject "CN=$CertName" `
        -CertStoreLocation "Cert:\CurrentUser\My" `
        -KeyUsage DigitalSignature `
        -KeyAlgorithm RSA `
        -KeyLength 2048 `
        -Provider "Microsoft Enhanced RSA and AES Cryptographic Provider" `
        -Type CodeSigningCert `
        -NotAfter (Get-Date).AddYears(2)
    
    Write-Host "✅ Certificate created successfully!" -ForegroundColor Green
    Write-Host "   Thumbprint: $($cert.Thumbprint)" -ForegroundColor Gray
    
    # Step 2: Export certificate to install in Trusted Root
    Write-Host ""
    Write-Host "📋 Installing certificate in Trusted Root..." -ForegroundColor Green
    
    $certPath = "QuickBasket_Certificate.cer"
    Export-Certificate -Cert $cert -FilePath $certPath -Force | Out-Null
    
    # Import to Trusted Root Certification Authorities
    Import-Certificate -FilePath $certPath -CertStoreLocation "Cert:\LocalMachine\Root" -Confirm:$false | Out-Null
    Import-Certificate -FilePath $certPath -CertStoreLocation "Cert:\LocalMachine\TrustedPublisher" -Confirm:$false | Out-Null
    
    Write-Host "✅ Certificate installed in Trusted Root store!" -ForegroundColor Green
    
    # Step 3: Sign the executable
    Write-Host ""
    Write-Host "✍️  Signing QuickBasket.exe..." -ForegroundColor Green
    
    # Use Set-AuthenticodeSignature (built into PowerShell)
    $signature = Set-AuthenticodeSignature -FilePath $ExePath -Certificate $cert -TimestampServer "http://timestamp.digicert.com"
    
    if ($signature.Status -eq "Valid") {
        Write-Host "✅ Executable signed successfully!" -ForegroundColor Green
        Write-Host ""
        Write-Host "🎉 SUCCESS! Your QuickBasket.exe is now signed!" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "📋 What this means:" -ForegroundColor Yellow
        Write-Host "  ✅ Reduced Windows Defender warnings"
        Write-Host "  ✅ Shows as 'Verified publisher' in properties"
        Write-Host "  ✅ Users will see fewer security prompts"
        Write-Host ""
        Write-Host "🔍 To verify the signature:"
        Write-Host "  Right-click QuickBasket.exe → Properties → Digital Signatures"
        Write-Host ""
    } else {
        Write-Host "❌ Failed to sign executable: $($signature.Status)" -ForegroundColor Red
        Write-Host "   Error: $($signature.StatusMessage)" -ForegroundColor Red
    }
    
    # Clean up temporary certificate file
    Remove-Item $certPath -Force -ErrorAction SilentlyContinue
    
} catch {
    Write-Host "❌ Error during signing process:" -ForegroundColor Red
    Write-Host "   $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
    Write-Host "💡 Troubleshooting tips:" -ForegroundColor Yellow
    Write-Host "  1. Ensure you're running as Administrator"
    Write-Host "  2. Check that QuickBasket.exe exists and isn't running"
    Write-Host "  3. Disable antivirus temporarily during signing"
    exit 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "🔐 Code Signing Complete!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan