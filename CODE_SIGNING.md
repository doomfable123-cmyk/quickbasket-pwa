# 🔐 Code Signing Guide for QuickBasket

This guide explains how to digitally sign your QuickBasket.exe to reduce Windows Defender warnings.

## 🎯 Why Sign Your Executable?

When users download and run unsigned executables, Windows shows warnings like:
- "Windows protected your PC" (SmartScreen)
- "Unknown publisher" warnings
- Antivirus false positives

Code signing adds a digital signature that:
- ✅ Identifies you as the publisher
- ✅ Proves the file hasn't been tampered with
- ✅ Reduces security warnings
- ✅ Builds trust with users

## 🚀 Quick Start (Self-Signed Certificate)

**Best for:** Personal use, testing, immediate deployment

1. **Run the signing utility:**
   ```bash
   # Double-click this file:
   Sign QuickBasket.bat
   ```

2. **What it does:**
   - Creates a self-signed development certificate
   - Signs QuickBasket.exe with the certificate
   - Installs certificate in Windows trusted store
   - Reduces "Unknown Publisher" warnings

3. **Requirements:**
   - Administrator privileges (the script will prompt)
   - QuickBasket.exe must exist in dist/ folder

## 📋 Certificate Options Comparison

| Type | Cost | Trust Level | Warnings Reduced | Best For |
|------|------|-------------|------------------|----------|
| **Self-Signed** | Free | Low | Some | Development, Personal Use |
| **Standard Code Signing** | $200-500/year | High | Most | Commercial Software |
| **EV Code Signing** | $400-800/year | Highest | All | Enterprise, High Security |

## 🔧 Advanced Options

### Option 1: Commercial Code Signing Certificate

**Providers:**
- [DigiCert](https://www.digicert.com/signing/code-signing-certificates) - $474/year
- [Sectigo](https://sectigo.com/ssl-certificates-tls/code-signing) - $254/year  
- [GlobalSign](https://www.globalsign.com/en/code-signing-certificate) - $249/year

**Steps:**
1. Purchase certificate from provider
2. Verify your identity (business verification)
3. Install certificate on your development machine
4. Use signtool.exe or our PowerShell script to sign

### Option 2: Free Certificate for Open Source

**GitHub Actions + SignPath:**
1. Apply for free certificate at [SignPath.io](https://signpath.io)
2. Set up GitHub Actions workflow
3. Automatic signing on every release

### Option 3: Windows SDK + Manual Signing

**If you have Windows SDK installed:**
```bash
# Sign with timestamp
signtool sign /a /tr http://timestamp.digicert.com /td sha256 /fd sha256 dist\QuickBasket.exe

# Verify signature
signtool verify /pa /v dist\QuickBasket.exe
```

## 🔍 Verifying the Signature

After signing, verify it worked:

1. **Command Line:**
   ```powershell
   Get-AuthenticodeSignature "dist\QuickBasket.exe"
   ```

2. **Windows Explorer:**
   - Right-click QuickBasket.exe
   - Properties → Digital Signatures tab
   - Should show your certificate

3. **PowerShell (detailed):**
   ```powershell
   $sig = Get-AuthenticodeSignature "dist\QuickBasket.exe"
   Write-Host "Status: $($sig.Status)"
   Write-Host "Signer: $($sig.SignerCertificate.Subject)"
   ```

## 📤 After Signing

1. **Test the executable:**
   ```bash
   # Should show fewer warnings
   .\dist\QuickBasket.exe
   ```

2. **Update GitHub:**
   ```bash
   git add dist/QuickBasket.exe
   git commit -m "Add digitally signed QuickBasket.exe"
   git push origin main
   ```

3. **Update documentation:**
   - Mention signed executable in README
   - Add certificate details to releases

## 🐛 Troubleshooting

**"Set-AuthenticodeSignature failed"**
- Run PowerShell as Administrator
- Ensure executable isn't currently running
- Check antivirus isn't blocking the operation

**"Unknown publisher" still appears**
- Self-signed certificates still show warnings to other users
- Consider commercial certificate for wider distribution
- Certificate needs time to build reputation

**Certificate not trusted on other machines**
- Self-signed certificates are only trusted on your machine
- Other users need to install your certificate manually
- Commercial certificates are automatically trusted

## 🎯 Recommendations

**For Personal Use:**
- Use the provided self-signed solution
- Quick and free
- Reduces warnings on your machine

**For Distribution:**
- Get a commercial code signing certificate
- Much better user experience
- Professional appearance

**For Open Source Projects:**
- Apply for free SignPath certificate
- Set up automated signing with GitHub Actions
- Best long-term solution

---

**Need Help?** 
- Run `Sign QuickBasket.bat` for guided signing
- Check Windows Event Viewer for detailed error messages
- Ensure you have the latest version of PowerShell