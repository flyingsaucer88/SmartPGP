// AEPGPContextMenu.cs
// AEPGP Windows 11 Primary Context Menu Shell Extension
//
// Implements IShellExtInit + IContextMenu so that AEPGP entries appear in
// Windows 11's primary right-click context menu.
//
// Background: HKCR\*\shell\ verb entries are demoted to the legacy
// "Show more options" sub-menu on Windows 11.  IContextMenu COM shell
// extensions registered under shellex\ContextMenuHandlers\ appear in the
// primary (top-level) context menu on all Windows versions including Win11.
//
// Compiled at install time by install_menu.py:
//   csc.exe /target:library /platform:x64
//           /out:AEPGPContextMenu.dll AEPGPContextMenu.cs
//
// Registered via RegAsm.exe /codebase /nologo.
//
// At runtime the DLL reads pythonw.exe and aepgp_launch.py paths from:
//   HKLM\SOFTWARE\AEPGP\ContextMenu  (LauncherPath, PythonPath)
// These values are written by install_menu.py — no recompile needed if
// paths change; just re-run the installer.

using System;
using System.Diagnostics;
using System.Runtime.InteropServices;
using System.Runtime.InteropServices.ComTypes;
using System.Text;
using Microsoft.Win32;

namespace AEPGP
{
    // CLSID: {3F7E8D9A-B1C2-4E5F-8A6B-9C0D1E2F3A4B}
    // This GUID must NEVER change after the first deployment; changing it
    // orphans any already-registered handler entries in the registry.
    [ComVisible(true)]
    [Guid("3F7E8D9A-B1C2-4E5F-8A6B-9C0D1E2F3A4B")]
    [ClassInterface(ClassInterfaceType.None)]
    [ProgId("AEPGP.ContextMenu")]
    public class AEPGPContextMenu : IShellExtInit, IContextMenu
    {
        // ── Command ID offsets (relative to idCmdFirst) ──────────────────
        private const int CMD_ENCRYPT        = 0;
        private const int CMD_DECRYPT        = 1;
        private const int CMD_GENERATE_KEYS  = 2;
        private const int CMD_DELETE_KEYS    = 3;
        private const int CMD_CHANGE_PIN     = 4;
        private const int CMD_COUNT          = 5;  // total IDs assigned

        private string _selectedFile = string.Empty;

        // ── IShellExtInit ─────────────────────────────────────────────────

        public int Initialize(IntPtr pidlFolder, IntPtr pDataObj, IntPtr hKeyProgID)
        {
            if (pDataObj == IntPtr.Zero) return 0; // S_OK — no file, e.g. desktop bg

            try
            {
                // Wrap the raw IDataObject* in a .NET RCW so we can call GetData
                var dataObj = (IDataObject)Marshal.GetObjectForIUnknown(pDataObj);

                FORMATETC fmt = new FORMATETC
                {
                    cfFormat = CF_HDROP,
                    ptd      = IntPtr.Zero,
                    dwAspect = DVASPECT.DVASPECT_CONTENT,
                    lindex   = -1,
                    tymed    = TYMED.TYMED_HGLOBAL
                };

                STGMEDIUM stg = new STGMEDIUM();
                dataObj.GetData(ref fmt, out stg);
                try
                {
                    // Only pick up the first selected file; encrypt/decrypt
                    // operate on one file at a time.
                    var sb = new StringBuilder(260);
                    if (DragQueryFile(stg.unionmember, 0, sb, sb.Capacity) > 0)
                        _selectedFile = sb.ToString();
                }
                finally
                {
                    ReleaseStgMedium(ref stg);
                }
            }
            catch { /* ignore — never crash Explorer during initialisation */ }

            return 0; // S_OK
        }

        // ── IContextMenu ──────────────────────────────────────────────────

        public int QueryContextMenu(IntPtr hMenu, uint indexMenu,
                                    int idCmdFirst, int idCmdLast, uint uFlags)
        {
            // CMF_DEFAULTONLY: shell only wants the default verb — skip
            const uint CMF_DEFAULTONLY = 0x00000001;
            if ((uFlags & CMF_DEFAULTONLY) != 0) return 0;

            // Build the AEPGP popup submenu
            IntPtr hSub = CreatePopupMenu();

            AppendMenuW(hSub, MF_STRING,    (IntPtr)(idCmdFirst + CMD_ENCRYPT),
                        "Encrypt File");
            AppendMenuW(hSub, MF_STRING,    (IntPtr)(idCmdFirst + CMD_DECRYPT),
                        "Decrypt File");
            AppendMenuW(hSub, MF_SEPARATOR, IntPtr.Zero, null);
            AppendMenuW(hSub, MF_STRING,    (IntPtr)(idCmdFirst + CMD_GENERATE_KEYS),
                        "Generate Keys in Card");
            AppendMenuW(hSub, MF_STRING,    (IntPtr)(idCmdFirst + CMD_DELETE_KEYS),
                        "Delete Keys from Card");
            AppendMenuW(hSub, MF_SEPARATOR, IntPtr.Zero, null);
            AppendMenuW(hSub, MF_STRING,    (IntPtr)(idCmdFirst + CMD_CHANGE_PIN),
                        "Change Card PIN");

            // Insert the "AEPGP" parent entry with the popup as its submenu.
            // MF_POPUP + MF_BYPOSITION: uIDNewItem holds the HMENU of hSub.
            InsertMenuW(hMenu, indexMenu,
                        MF_BYPOSITION | MF_POPUP | MF_STRING,
                        hSub, "AEPGP");

            // Return the number of command IDs consumed (IDs 0 .. CMD_COUNT-1)
            return CMD_COUNT;
        }

        public int InvokeCommand(IntPtr pici)
        {
            try
            {
                var ci = (CMINVOKECOMMANDINFO)Marshal.PtrToStructure(
                    pici, typeof(CMINVOKECOMMANDINFO));

                // High word != 0 means lpVerb is a string verb (not our ordinal)
                long lpVerb = ci.lpVerb.ToInt64();
                if ((lpVerb >> 16) != 0) return 0;

                int offset = (int)(lpVerb & 0xFFFF);
                string action;
                switch (offset)
                {
                    case CMD_ENCRYPT:       action = "encrypt";       break;
                    case CMD_DECRYPT:       action = "decrypt";       break;
                    case CMD_GENERATE_KEYS: action = "generate_keys"; break;
                    case CMD_DELETE_KEYS:   action = "delete_keys";   break;
                    case CMD_CHANGE_PIN:    action = "change_pin";    break;
                    default: return 0;
                }

                LaunchHandler(action, _selectedFile);
            }
            catch { /* must not propagate exceptions into Explorer */ }

            return 0; // S_OK
        }

        public int GetCommandString(IntPtr idCmd, uint uType,
                                    IntPtr pReserved, IntPtr pszName, uint cchMax)
        {
            // GCS_VALIDATEA / GCS_VALIDATEW: confirm the command ID exists
            const uint GCS_VALIDATEA = 0x00000001;
            const uint GCS_VALIDATEW = 0x00000005;
            if ((uType & GCS_VALIDATEW) == GCS_VALIDATEW ||
                (uType & GCS_VALIDATEA) == GCS_VALIDATEA)
            {
                int id = (int)(idCmd.ToInt64() & 0xFFFF);
                return (id >= 0 && id < CMD_COUNT)
                    ? 0
                    : unchecked((int)0x80004001); // S_OK : E_NOTIMPL
            }
            // Verb-name requests: not implemented (acceptable for basic extensions)
            return unchecked((int)0x80004001); // E_NOTIMPL
        }

        // ── Launch helper ─────────────────────────────────────────────────

        private static void LaunchHandler(string action, string filePath)
        {
            try
            {
                string launcher = null, pythonw = null;

                // Paths written by install_menu.py at installation time
                using (var k = Registry.LocalMachine.OpenSubKey(
                    @"SOFTWARE\AEPGP\ContextMenu"))
                {
                    if (k == null) return;
                    launcher = k.GetValue("LauncherPath") as string;
                    pythonw  = k.GetValue("PythonPath")   as string;
                }

                if (string.IsNullOrEmpty(launcher) || string.IsNullOrEmpty(pythonw))
                    return;

                string args = string.IsNullOrEmpty(filePath)
                    ? string.Format("\"{0}\" {1}", launcher, action)
                    : string.Format("\"{0}\" {1} \"{2}\"", launcher, action, filePath);

                Process.Start(new ProcessStartInfo
                {
                    FileName        = pythonw,
                    Arguments       = args,
                    UseShellExecute = false,
                    CreateNoWindow  = true,
                    WindowStyle     = ProcessWindowStyle.Hidden
                });
            }
            catch { /* silently swallow — must not crash Explorer */ }
        }

        // ── COM self-registration (called by RegAsm) ──────────────────────

        [ComRegisterFunction]
        public static void RegisterClass(Type t)
        {
            string clsid = "{" + typeof(AEPGPContextMenu).GUID.ToString("D").ToUpper() + "}";

            // Register as IContextMenu handler for all files (*) and for
            // the desktop background (Directory\Background).
            // Both go to HKLM so they are visible to all users.
            using (var k = Registry.LocalMachine.CreateSubKey(
                @"SOFTWARE\Classes\*\shellex\ContextMenuHandlers\AEPGP"))
                k.SetValue("", clsid);

            using (var k = Registry.LocalMachine.CreateSubKey(
                @"SOFTWARE\Classes\Directory\Background\shellex\ContextMenuHandlers\AEPGP"))
                k.SetValue("", clsid);
        }

        [ComUnregisterFunction]
        public static void UnregisterClass(Type t)
        {
            SafeDeleteKey(Registry.LocalMachine,
                @"SOFTWARE\Classes\*\shellex\ContextMenuHandlers\AEPGP");
            SafeDeleteKey(Registry.LocalMachine,
                @"SOFTWARE\Classes\Directory\Background\shellex\ContextMenuHandlers\AEPGP");
        }

        private static void SafeDeleteKey(RegistryKey root, string path)
        {
            try { root.DeleteSubKeyTree(path); } catch { }
        }

        // ── Win32 P/Invoke ────────────────────────────────────────────────

        private const short CF_HDROP      = 15;
        private const uint  MF_STRING     = 0x00000000;
        private const uint  MF_SEPARATOR  = 0x00000800;
        private const uint  MF_POPUP      = 0x00000010;
        private const uint  MF_BYPOSITION = 0x00000400;

        [DllImport("shell32.dll", CharSet = CharSet.Unicode)]
        private static extern uint DragQueryFile(
            IntPtr hDrop, uint iFile, StringBuilder lpszFile, int cch);

        [DllImport("ole32.dll")]
        private static extern void ReleaseStgMedium(ref STGMEDIUM pmedium);

        [DllImport("user32.dll")]
        private static extern IntPtr CreatePopupMenu();

        // uIDNewItem is IntPtr: holds a command ID (int cast) or an HMENU
        // (when MF_POPUP is set).  IntPtr is pointer-sized on both 32/64-bit.
        [DllImport("user32.dll", SetLastError = true, CharSet = CharSet.Unicode)]
        private static extern bool AppendMenuW(
            IntPtr hMenu, uint uFlags, IntPtr uIDNewItem, string lpNewItem);

        [DllImport("user32.dll", SetLastError = true, CharSet = CharSet.Unicode)]
        private static extern bool InsertMenuW(
            IntPtr hMenu, uint uPosition, uint uFlags,
            IntPtr uIDNewItem, string lpNewItem);
    }

    // ── CMINVOKECOMMANDINFO ───────────────────────────────────────────────

    [StructLayout(LayoutKind.Sequential)]
    internal struct CMINVOKECOMMANDINFO
    {
        public uint   cbSize;
        public uint   fMask;
        public IntPtr hwnd;
        public IntPtr lpVerb;       // low word = command offset when high word == 0
        public IntPtr lpParameters;
        public IntPtr lpDirectory;
        public int    nShow;
        public uint   dwHotKey;
        public IntPtr hIcon;
    }

    // ── IShellExtInit ─────────────────────────────────────────────────────

    [ComImport]
    [InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
    [Guid("000214E8-0000-0000-C000-000000000046")]
    internal interface IShellExtInit
    {
        [PreserveSig]
        int Initialize(IntPtr pidlFolder, IntPtr pDataObj, IntPtr hKeyProgID);
    }

    // ── IContextMenu ──────────────────────────────────────────────────────

    [ComImport]
    [InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
    [Guid("000214E4-0000-0000-C000-000000000046")]
    internal interface IContextMenu
    {
        [PreserveSig]
        int QueryContextMenu(IntPtr hmenu, uint iMenu,
                             int idCmdFirst, int idCmdLast, uint uFlags);

        [PreserveSig]
        int InvokeCommand(IntPtr pici);

        [PreserveSig]
        int GetCommandString(IntPtr idCmd, uint uType, IntPtr pReserved,
                             IntPtr pszName, uint cchMax);
    }
}
