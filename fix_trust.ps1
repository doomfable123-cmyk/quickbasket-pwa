# Manual Certificate Trust Fix
# Run this as Administrator to manually trust the certificate

Write-Host "🔐 Manual Certificate Trust Setup" -ForegroundColor Cyan
Write-Host ""

# Check admin
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")
if (-not $isAdmin) {
    Write-Host "❌ Run as Administrator!" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Get the certificate thumbprint from the signed executable
$sig = Get-AuthenticodeSignature "dist\QuickBasket.exe"
if ($sig.SignerCertificate) {
    Write-Host "✅ Found certificate in executable" -ForegroundColor Green
    Write-Host "   Subject: $($sig.SignerCertificate.Subject)" -ForegroundColor Gray
    
    # Install directly from the signature
    $store = New-Object System.Security.Cryptography.X509Certificates.X509Store("Root", "LocalMachine")
    $store.Open("ReadWrite")
    $store.Add($sig.SignerCertificate)
    $store.Close()
    
    Write-Host "✅ Certificate installed in LocalMachine\Root" -ForegroundColor Green
    
    # Also add to TrustedPublisher
    $store2 = New-Object System.Security.Cryptography.X509Certificates.X509Store("TrustedPublisher", "LocalMachine")
    $store2.Open("ReadWrite")  
    $store2.Add($sig.SignerCertificate)
    $store2.Close()
    
    Write-Host "✅ Certificate installed in TrustedPublisher" -ForegroundColor Green
    Write-Host ""
    
    # Test the signature again
    $newSig = Get-AuthenticodeSignature "dist\QuickBasket.exe"
    Write-Host "🔍 New signature status: $($newSig.Status)" -ForegroundColor $(if ($newSig.Status -eq "Valid") { "Green" } else { "Red" })
    
} else {
    Write-Host "❌ No certificate found in executable" -ForegroundColor Red
}

Read-Host "Press Enter to exit"