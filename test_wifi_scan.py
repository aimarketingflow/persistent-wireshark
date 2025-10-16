#!/usr/bin/env python3
"""
Test WiFi scanning using system_profiler
"""

import subprocess
import re
from datetime import datetime

def scan_wifi_networks():
    """Scan for WiFi networks using system_profiler"""
    try:
        result = subprocess.run(
            ['system_profiler', 'SPAirPortDataType'],
            capture_output=True,
            text=True,
            timeout=15
        )
        
        networks = []
        current_network = None
        in_other_networks = False
        
        for line in result.stdout.split('\n'):
            # Check if we're in the "Other Local Wi-Fi Networks" section
            if 'Other Local Wi-Fi Networks:' in line:
                in_other_networks = True
                continue
            
            # Stop if we hit another section
            if in_other_networks and line and not line.startswith(' '):
                break
            
            if in_other_networks:
                # Check for network name (SSID) - it's indented and ends with ':'
                if line.strip() and line.strip().endswith(':') and '  ' in line[:20]:
                    # Save previous network if exists
                    if current_network and current_network.get('ssid'):
                        networks.append(current_network)
                    
                    # Start new network
                    ssid = line.strip().rstrip(':')
                    current_network = {
                        'ssid': ssid,
                        'channel': 'Unknown',
                        'security': 'Unknown',
                        'rssi': -100,
                        'bssid': 'Unknown',
                        'timestamp': datetime.now().isoformat()
                    }
                
                # Parse network properties
                elif current_network:
                    if 'Channel:' in line:
                        # Extract channel info: "Channel: 157 (5GHz, 80MHz)"
                        match = re.search(r'Channel:\s+(\d+)\s+\(([^)]+)\)', line)
                        if match:
                            current_network['channel'] = f"{match.group(1)} ({match.group(2)})"
                    
                    elif 'Security:' in line:
                        security = line.split('Security:')[1].strip()
                        current_network['security'] = security if security else 'Open'
                    
                    elif 'Signal / Noise:' in line:
                        # Extract signal: "Signal / Noise: -39 dBm / -92 dBm"
                        match = re.search(r'Signal / Noise:\s+(-?\d+)\s+dBm', line)
                        if match:
                            current_network['rssi'] = int(match.group(1))
        
        # Add last network
        if current_network and current_network.get('ssid'):
            networks.append(current_network)
        
        return networks
        
    except Exception as e:
        print(f"Network scan error: {e}")
        import traceback
        traceback.print_exc()
        return []

def is_potential_threat(network):
    """Basic threat detection logic"""
    # Check for suspicious patterns
    suspicious_ssids = ['Free WiFi', 'Public', 'Guest', 'Open', 'Pineapple', 'xfinitywifi']
    
    # Check for open networks with suspicious names
    if network['security'] in ['Open', 'None'] and any(sus.lower() in network['ssid'].lower() for sus in suspicious_ssids):
        return True
    
    # Check for very strong signal (potential evil twin)
    if network['rssi'] > -30:
        return True
    
    return False

if __name__ == "__main__":
    print("🛡️ Testing WiFi Network Scanning\n")
    print("=" * 80)
    
    networks = scan_wifi_networks()
    
    print(f"\n✅ Found {len(networks)} networks:\n")
    
    for i, network in enumerate(networks, 1):
        threat_indicator = "🚨 THREAT" if is_potential_threat(network) else "✅ OK"
        
        # Security icon
        if network['security'] in ['Open', 'None']:
            sec_icon = "🔓"
        elif 'WPA' in network['security']:
            sec_icon = "🔒"
        else:
            sec_icon = "❓"
        
        print(f"{i}. {threat_indicator} {sec_icon} {network['ssid']}")
        print(f"   Channel: {network['channel']}")
        print(f"   Security: {network['security']}")
        print(f"   Signal: {network['rssi']} dBm")
        print()
    
    # Count threats
    threats = [n for n in networks if is_potential_threat(n)]
    if threats:
        print(f"\n⚠️  WARNING: {len(threats)} potential threat(s) detected!")
        for threat in threats:
            print(f"   - {threat['ssid']} ({threat['security']}, {threat['rssi']} dBm)")
    else:
        print("\n✅ No obvious threats detected")
