# Outlook Add-in Icon Assets

This directory contains icon files for the SmartPGP Outlook add-in.

## Files

- **Ambimat-Logo.ico** - Original Windows icon file (106x36, 32-bit)
- **icon-source.png** - Base PNG conversion from ICO
- **icon-16.png** - 16x16 icon for ribbon buttons
- **icon-32.png** - 32x32 icon for manifest
- **icon-64.png** - 64x64 high-resolution icon
- **icon-80.png** - 80x80 icon for larger displays

## Usage

These icons are referenced in `manifest/manifest.xml`:
- Lines 12-13: IconUrl and HighResolutionIconUrl (legacy)
- Lines 50-54: Compose button icon
- Lines 63-67: Decrypt button icon
- Lines 85-88: Resource images (icon16, icon32, icon80)

## Customization

To use custom branding:
1. Replace `Ambimat-Logo.ico` with your logo
2. Run the conversion script to regenerate PNGs:
   ```bash
   sips -s format png Ambimat-Logo.ico --out icon-source.png
   sips -z 16 16 icon-source.png --out icon-16.png
   sips -z 32 32 icon-source.png --out icon-32.png
   sips -z 64 64 icon-source.png --out icon-64.png
   sips -z 80 80 icon-source.png --out icon-80.png
   ```

## Design Guidelines

For best results, icons should:
- Use transparent backgrounds
- Be square aspect ratio (will be scaled to different sizes)
- Have clear, simple designs that work at small sizes
- Follow Microsoft Office add-in icon guidelines
