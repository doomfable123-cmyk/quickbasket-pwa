# Administrator signing script
Write-Host "QuickBasket Signing Script - Admin Required" -ForegroundColor Cyan
Write-Host ""

# Check admin privileges
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")
Write-Host "Running as Administrator: $isAdmin"

if (-not $isAdmin) {
    Write-Host "This script must be run as Administrator to install the certificate in the trusted store." -ForegroundColor Yellow
    exit 1
}

try {
    Write-Host "Step 1: Creating self-signed certificate..." -ForegroundColor Green
    $cert = New-SelfSignedCertificate -Subject "CN=QuickBasket Development" -CertStoreLocation "Cert:\CurrentUser\My" -Type CodeSigningCert
    Write-Host "Certificate created: $($cert.Subject)"
    
    Write-Host ""
    Write-Host "Step 2: Installing certificate in trusted root store..." -ForegroundColor Green
    
    # Export certificate
    $tempCertPath = "temp_quickbasket_cert.cer"
    Export-Certificate -Cert $cert -FilePath $tempCertPath -Force | Out-Null
    
    # Import to trusted root and trusted publisher stores
    Import-Certificate -FilePath $tempCertPath -CertStoreLocation "Cert:\LocalMachine\Root" -Confirm:$false | Out-Null
    Import-Certificate -FilePath $tempCertPath -CertStoreLocation "Cert:\LocalMachine\TrustedPublisher" -Confirm:$false | Out-Null
    
    # Clean up temp file
    Remove-Item $tempCertPath -Force
    
    Write-Host "Certificate installed in trusted stores"
    
    Write-Host ""
    Write-Host "Step 3: Signing the executable..." -ForegroundColor Green
    $signature = Set-AuthenticodeSignature -FilePath "dist\QuickBasket.exe" -Certificate $cert
    
    Write-Host "Signing result: $($signature.Status)"
    
    if ($signature.Status -eq "Valid") {
        Write-Host ""
        Write-Host "SUCCESS! QuickBasket.exe is now digitally signed!" -ForegroundColor Green
        Write-Host "The executable should now show fewer Windows Defender warnings." -ForegroundColor Green
    } else {
        Write-Host "Signing failed: $($signature.StatusMessage)" -ForegroundColor Red
    }
    
} catch {
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "Final verification:"
$check = Get-AuthenticodeSignature "dist\QuickBasket.exe"
Write-Host "Status: $($check.Status)"
Write-Host "Signer: $($check.SignerCertificate.Subject)"