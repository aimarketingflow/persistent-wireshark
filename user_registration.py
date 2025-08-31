#!/usr/bin/env python3
"""
StealthShark User Registration
Optional user registration for analytics and updates
"""

import json
import hashlib
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
import base64

class UserRegistration:
    """Handle user registration and data storage"""
    
    def __init__(self):
        self.settings_file = Path(__file__).parent / "stealthshark_settings.json"
        self.user_file = Path(__file__).parent / ".user_profile"  # Hidden file
        self.settings = self.load_settings()
        self.user_data = self.load_user_data()
    
    def load_settings(self) -> Dict[str, Any]:
        """Load settings from JSON file"""
        if self.settings_file.exists():
            with open(self.settings_file, 'r') as f:
                return json.load(f)
        return {}
    
    def save_settings(self):
        """Save settings to JSON file"""
        with open(self.settings_file, 'w') as f:
            json.dump(self.settings, f, indent=4)
    
    def load_user_data(self) -> Dict[str, Any]:
        """Load existing user data if available"""
        if self.user_file.exists():
            try:
                with open(self.user_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {}
    
    def save_user_data(self):
        """Save user data locally"""
        with open(self.user_file, 'w') as f:
            json.dump(self.user_data, f, indent=4)
        # Make file hidden on Unix systems
        if hasattr(self.user_file, 'chmod'):
            self.user_file.chmod(0o600)  # Read/write for owner only
    
    def generate_user_id(self) -> str:
        """Generate unique user ID"""
        if 'user_id' in self.user_data:
            return self.user_data['user_id']
        return str(uuid.uuid4())
    
    def hash_email(self, email: str) -> str:
        """Hash email for privacy"""
        return hashlib.sha256(email.encode()).hexdigest()
    
    def register_user(self, name: str = "", email: str = "") -> Dict[str, Any]:
        """Register user with optional name and email"""
        
        # Generate or get user ID
        user_id = self.generate_user_id()
        
        # Prepare registration data
        registration = {
            'user_id': user_id,
            'registered_at': datetime.now().isoformat(),
            'version': self.get_version()
        }
        
        # Add optional fields
        if name:
            registration['name'] = name
        
        if email:
            # Store hashed email for privacy
            registration['email_hash'] = self.hash_email(email)
            # Store encrypted email locally only
            registration['email_encrypted'] = self.simple_encrypt(email)
        
        # Update user data
        self.user_data.update(registration)
        self.save_user_data()
        
        # Update settings to indicate registration
        if 'user' not in self.settings:
            self.settings['user'] = {}
        self.settings['user']['registered'] = True
        self.settings['user']['registration_date'] = registration['registered_at']
        self.save_settings()
        
        return {
            'user_id': user_id,
            'status': 'registered',
            'message': 'Thank you for registering!'
        }
    
    def simple_encrypt(self, text: str) -> str:
        """Simple encryption for local storage only"""
        # This is basic obfuscation, not cryptographic security
        encoded = base64.b64encode(text.encode()).decode()
        return encoded[::-1]  # Reverse for obfuscation
    
    def simple_decrypt(self, text: str) -> str:
        """Decrypt locally stored data"""
        try:
            reversed_text = text[::-1]
            decoded = base64.b64decode(reversed_text).decode()
            return decoded
        except:
            return ""
    
    def get_version(self) -> str:
        """Get current StealthShark version"""
        try:
            import subprocess
            result = subprocess.run(
                ['git', 'rev-parse', '--short', 'HEAD'],
                capture_output=True,
                text=True,
                cwd=Path(__file__).parent
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except:
            pass
        return "unknown"
    
    def is_registered(self) -> bool:
        """Check if user is already registered"""
        return bool(self.user_data.get('user_id'))
    
    def get_registration_info(self) -> Dict[str, Any]:
        """Get registration information"""
        if not self.is_registered():
            return {'registered': False}
        
        info = {
            'registered': True,
            'user_id': self.user_data.get('user_id'),
            'registration_date': self.user_data.get('registered_at')
        }
        
        if 'name' in self.user_data:
            info['name'] = self.user_data['name']
        
        if 'email_encrypted' in self.user_data:
            info['email'] = self.simple_decrypt(self.user_data['email_encrypted'])
        
        return info
    
    def prompt_registration(self) -> bool:
        """Interactive registration prompt"""
        print("\n🦈 StealthShark User Registration (Optional)")
        print("=" * 50)
        print("Help us improve StealthShark by registering.")
        print("Your information is stored locally and kept private.\n")
        
        # Check if already registered
        if self.is_registered():
            info = self.get_registration_info()
            print(f"✅ Already registered as: {info.get('name', 'Anonymous User')}")
            update = input("\nUpdate registration? (y/n) [n]: ").lower()
            if update != 'y':
                return False
        
        # Registration prompt
        register = input("Would you like to register? (y/n) [n]: ").lower()
        if register != 'y':
            print("Registration skipped. You can register anytime.")
            return False
        
        # Collect information
        name = input("\nName (optional, press Enter to skip): ").strip()
        email = input("Email (optional, for updates only): ").strip()
        
        # Validate email if provided
        if email and '@' not in email:
            print("⚠️ Invalid email format")
            email = ""
        
        # Register
        result = self.register_user(name, email)
        
        if result['status'] == 'registered':
            print(f"\n✅ {result['message']}")
            if name:
                print(f"   Welcome, {name}!")
            print(f"   User ID: {result['user_id'][:8]}...")
            return True
        
        return False

def check_and_prompt_registration():
    """Check if user should be prompted for registration"""
    reg = UserRegistration()
    
    # Skip if already registered
    if reg.is_registered():
        return
    
    # Skip if user has been asked recently
    settings = reg.settings
    last_prompt = settings.get('user', {}).get('last_registration_prompt')
    
    if last_prompt:
        from datetime import datetime
        try:
            last_date = datetime.fromisoformat(last_prompt)
            days_since = (datetime.now() - last_date).days
            if days_since < 7:  # Don't ask more than once a week
                return
        except:
            pass
    
    # Prompt for registration
    reg.prompt_registration()
    
    # Update last prompt time
    if 'user' not in settings:
        settings['user'] = {}
    settings['user']['last_registration_prompt'] = datetime.now().isoformat()
    reg.save_settings()

def main():
    """Main entry point"""
    import sys
    
    reg = UserRegistration()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--info":
            info = reg.get_registration_info()
            if info['registered']:
                print(f"Registered: Yes")
                print(f"User ID: {info['user_id'][:8]}...")
                if 'name' in info:
                    print(f"Name: {info['name']}")
                if 'email' in info:
                    print(f"Email: {info['email']}")
                print(f"Date: {info['registration_date']}")
            else:
                print("Not registered")
        elif sys.argv[1] == "--register":
            reg.prompt_registration()
        else:
            print("Usage: python3 user_registration.py [--info|--register]")
    else:
        # Interactive registration
        reg.prompt_registration()

if __name__ == "__main__":
    main()
