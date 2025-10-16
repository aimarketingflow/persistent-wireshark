# WiFi Security Tab - Usage Instructions

## How to Use the WiFi Security Tab

### Step 1: Launch the GUI
```bash
python3 multi_interface_shark_gui.py
```

### Step 2: Navigate to WiFi Security Tab
Click on the **🛡️ WiFi Security** tab at the top of the window.

### Step 3: Start WiFi Scanning
Click the **🛡️ Start WiFi Threat Detection** button.

### Step 4: View Networks
- Networks will appear in the list within 10 seconds
- The list refreshes automatically every 10 seconds
- Networks are color-coded:
  - 🔒 = Secured (WPA/WPA2/WPA3)
  - 🔓 = Open/Unsecured
  - ❓ = Unknown security

### Step 5: Monitor for Threats
- Threats are automatically detected
- You'll see a popup alert for serious threats
- Threats are also logged in the Monitor Log tab

## Why Networks Aren't Showing

**The WiFi scanning does NOT start automatically!**

You must:
1. Go to the WiFi Security tab
2. Click "Start WiFi Threat Detection"
3. Wait 10-15 seconds for the first scan

## Troubleshooting

### No networks appearing?
1. Make sure you clicked "Start WiFi Threat Detection"
2. Wait at least 15 seconds for the first scan
3. Check the Monitor Log tab for any errors
4. Verify WiFi is enabled on your Mac

### Test WiFi scanning manually:
```bash
python3 test_wifi_scan.py
```

This will show if WiFi scanning works outside the GUI.

## Debug Mode

To see detailed WiFi scanning output:
```bash
python3 multi_interface_shark_gui.py 2>&1 | grep WiFiThread
```

You should see output like:
```
[WiFiThread] Started at 2025-10-15 21:46:10
[WiFiThread] Scanning for networks...
[WiFiThread] Found 26 networks, emitting signal
```

If you don't see this output, the WiFi scanning hasn't been started yet.
