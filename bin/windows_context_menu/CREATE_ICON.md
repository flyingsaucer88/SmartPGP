# Creating an Icon for AEPGP Installer

## Quick Start

If you already have a `.ico` file:

1. Name it `aepgp_icon.ico`
2. Place it in the `windows_context_menu/` folder
3. Rebuild: `build_exe.bat`
4. Done! Your executable will have the icon.

## Creating an Icon from Scratch

### Option 1: Online Icon Converter (Easiest)

1. **Create or find an image:**
   - PNG or JPG format
   - Square dimensions (e.g., 256x256, 512x512)
   - Represents AEPGP (lock, shield, key, card, etc.)

2. **Convert to .ico:**
   - Visit: https://convertio.co/png-ico/
   - Or: https://www.icoconverter.com/
   - Upload your image
   - Download the `.ico` file

3. **Save the icon:**
   - Name it: `aepgp_icon.ico`
   - Place it in: `bin/windows_context_menu/`

4. **Rebuild:**
   ```cmd
   build_exe.bat
   ```

### Option 2: Using GIMP (Free Software)

1. **Download GIMP:**
   - https://www.gimp.org/downloads/

2. **Create/Open your image:**
   - File → New → 256x256 pixels
   - Or open existing image

3. **Design your icon:**
   - Simple, clear design works best
   - Use high contrast
   - Test at small sizes (16x16, 32x32)

4. **Export as ICO:**
   - File → Export As
   - Choose file type: "Microsoft Windows icon (*.ico)"
   - Save as: `aepgp_icon.ico`
   - Select icon sizes: 16, 32, 48, 256 (check all)

5. **Place and rebuild:**
   - Copy to `windows_context_menu/`
   - Run `build_exe.bat`

### Option 3: Using Python (For Developers)

If you have a PNG file and want to convert it programmatically:

```python
# install: pip install pillow
from PIL import Image

img = Image.open('your_image.png')
# Resize if needed
img = img.resize((256, 256), Image.LANCZOS)
# Save as icon with multiple sizes
img.save('aepgp_icon.ico', format='ICO', sizes=[(16,16), (32,32), (48,48), (256,256)])
```

## Icon Design Guidelines

### Recommended Characteristics:
- **Size:** 256x256 pixels (source)
- **Format:** .ico with multiple sizes embedded
- **Colors:** Clear, high contrast
- **Style:** Simple, recognizable at small sizes
- **Theme:** Security-related (lock, shield, key, card)

### What to Avoid:
- ❌ Too much detail (won't be visible at 16x16)
- ❌ Low contrast colors
- ❌ Text (hard to read when small)
- ❌ Complex gradients
- ❌ Very thin lines

### Good Icon Ideas for AEPGP:
- 🔒 Padlock with card
- 🛡️ Shield with key
- 💳 Smart card with lock
- 🔐 Key symbol
- 🔑 Classic key with digital elements

## Icon Sizes to Include

Your `.ico` file should contain multiple sizes:
- **16x16** - Small taskbar/system tray
- **32x32** - Standard icon size
- **48x48** - Large icons view
- **256x256** - High DPI displays

Most icon converters handle this automatically.

## Testing Your Icon

After rebuilding with the icon:

1. **Check in File Explorer:**
   - Navigate to `dist/`
   - Look at `AEPGP_Installer.exe`
   - The icon should be visible

2. **Check in different views:**
   - Small icons
   - Medium icons
   - Large icons
   - Extra large icons

3. **Check when running:**
   - Run the executable
   - Check the taskbar
   - Check the window title bar

## Default Icon (No Custom Icon)

If you don't provide an icon, PyInstaller will use:
- Python's default icon (snake/feather)
- Or a generic executable icon

This works fine but isn't as professional.

## Current Configuration

The `aepgp_installer.spec` file is already configured to use an icon:

```python
exe = EXE(
    ...
    icon='aepgp_icon.ico',  # Already configured!
    ...
)
```

Just add the `aepgp_icon.ico` file and rebuild.

## Troubleshooting

### "Icon file not found" error
**Solution:** Make sure `aepgp_icon.ico` is in the same folder as `aepgp_installer.spec`

### Icon doesn't show
**Solution:**
- Clear icon cache: Delete `IconCache.db` from `%LocalAppData%`
- Restart Explorer: Task Manager → Windows Explorer → Restart
- Rebuild: `build_exe.bat`

### Icon looks pixelated
**Solution:**
- Use higher resolution source image
- Ensure .ico contains 256x256 size
- Use proper icon converter

### Wrong icon appears
**Solution:**
- Windows caches icons aggressively
- Rename the .exe file slightly
- Or restart Windows

## Free Icon Resources

If you want to use pre-made icons (check licenses):

1. **Flaticon:** https://www.flaticon.com/
   - Search: "lock", "security", "card", "encryption"
   - Download PNG, convert to ICO

2. **Icons8:** https://icons8.com/
   - Free icons available
   - Download and convert

3. **Noun Project:** https://thenounproject.com/
   - Simple, clear icons
   - Great for security symbols

4. **Font Awesome:** https://fontawesome.com/
   - Icon fonts
   - Can be converted to images

**Always check the license!** Some require attribution.

## File Structure

After adding icon:

```
windows_context_menu/
├── aepgp_icon.ico          ← Your icon file (add this)
├── aepgp_installer.py
├── aepgp_installer.spec    ← Already configured for icon
├── build_exe.bat
└── dist/
    └── AEPGP_Installer.exe ← Will have your icon
```

## Quick Steps Summary

```
1. Create/find square image (256x256 PNG)
2. Convert to .ico using online tool
3. Save as: aepgp_icon.ico
4. Place in: windows_context_menu/
5. Run: build_exe.bat
6. Check: dist/AEPGP_Installer.exe now has icon!
```

## Example Icon Concept (Text Description)

Since I can't create actual images, here's a concept you can give to a designer:

**AEPGP Icon Concept:**
- Base: Blue shield shape
- Center: White/silver smart card silhouette
- Overlay: Golden padlock symbol
- Style: Flat design, modern
- Colors: Blue (#0066CC), White (#FFFFFF), Gold (#FFD700)

This conveys: Security (shield + lock) + Smart card technology

## Next Steps

Once you have `aepgp_icon.ico`:
1. Place it in the `windows_context_menu/` folder
2. Run `build_exe.bat`
3. Your executable will automatically include the icon
4. Distribute the new version!

The spec file is already configured - just add the icon file!
