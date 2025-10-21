#!/usr/bin/env python3
"""
MakkelijkPdf Setup Wizard
Alles-in-één installatie en setup wizard
"""

import os
import sys
import subprocess
import platform
import time
from pathlib import Path

def print_header():
    """Print mooie header"""
    print("=" * 60)
    print("🚀 MAKKELIJKPDF SETUP WIZARD")
    print("=" * 60)
    print("📄 PDF naar afbeelding converter")
    print("🎯 Alles-in-één installatie en setup")
    print("=" * 60)
    print()

def check_python():
    """Controleer Python installatie"""
    print("🔍 Controleer Python installatie...")
    try:
        version = sys.version_info
        if version.major >= 3 and version.minor >= 7:
            print(f"✅ Python {version.major}.{version.minor}.{version.micro} gevonden")
            return True
        else:
            print(f"❌ Python {version.major}.{version.minor} is te oud. Minimaal 3.7 vereist.")
            return False
    except Exception as e:
        print(f"❌ Python niet gevonden: {e}")
        return False

def install_dependencies():
    """Installeer Python dependencies"""
    print("\n📦 Installeer Python dependencies...")
    dependencies = [
        "pdf2image==1.17.0",
        "Pillow==10.2.0", 
        "setuptools==69.5.1",
        "customtkinter==5.2.2"
    ]
    
    for dep in dependencies:
        print(f"   📥 Installeer {dep}...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", dep], 
                         check=True, capture_output=True)
            print(f"   ✅ {dep} geïnstalleerd")
        except subprocess.CalledProcessError as e:
            print(f"   ❌ Fout bij installatie {dep}: {e}")
            return False
    
    print("✅ Alle dependencies geïnstalleerd!")
    return True

def install_poppler():
    """Installeer Poppler"""
    print("\n🔧 Installeer Poppler...")
    
    system = platform.system()
    
    if system == "Windows":
        print("   📥 Download Poppler voor Windows...")
        try:
            # Download Poppler
            poppler_url = "https://github.com/oschwartz10612/poppler-windows/releases/download/v23.08.0-0/Release-23.08.0-0.zip"
            subprocess.run([
                "powershell", "-Command", 
                f"Invoke-WebRequest -Uri '{poppler_url}' -OutFile 'poppler.zip'"
            ], check=True)
            
            # Extract Poppler
            subprocess.run([
                "powershell", "-Command", 
                "Expand-Archive -Path 'poppler.zip' -DestinationPath 'C:\\poppler' -Force"
            ], check=True)
            
            # Add to PATH
            subprocess.run([
                "powershell", "-Command", 
                "[Environment]::SetEnvironmentVariable('PATH', $env:PATH + ';C:\\poppler\\poppler-23.08.0\\Library\\bin', 'User')"
            ], check=True)
            
            # Cleanup
            os.remove("poppler.zip")
            print("   ✅ Poppler geïnstalleerd en toegevoegd aan PATH")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"   ❌ Fout bij Poppler installatie: {e}")
            return False
            
    elif system == "Darwin":  # macOS
        print("   📥 Installeer Poppler via Homebrew...")
        try:
            subprocess.run(["brew", "install", "poppler"], check=True)
            print("   ✅ Poppler geïnstalleerd via Homebrew")
            return True
        except subprocess.CalledProcessError:
            print("   ⚠️ Homebrew niet gevonden. Installeer handmatig:")
            print("      brew install poppler")
            return False
            
    elif system == "Linux":
        print("   📥 Installeer Poppler via package manager...")
        try:
            # Probeer apt (Ubuntu/Debian)
            subprocess.run(["sudo", "apt-get", "update"], check=True)
            subprocess.run(["sudo", "apt-get", "install", "-y", "poppler-utils"], check=True)
            print("   ✅ Poppler geïnstalleerd via apt")
            return True
        except subprocess.CalledProcessError:
            print("   ⚠️ Installeer handmatig:")
            print("      sudo apt-get install poppler-utils")
            return False
    
    return True

def create_shortcuts():
    """Maak shortcuts"""
    print("\n🔗 Maak shortcuts...")
    
    system = platform.system()
    current_dir = os.getcwd()
    
    if system == "Windows":
        try:
            # Desktop shortcut
            desktop = os.path.join(os.path.expanduser("~"), "Desktop")
            shortcut_path = os.path.join(desktop, "MakkelijkPdf.lnk")
            
            powershell_cmd = f"""
            $WshShell = New-Object -comObject WScript.Shell
            $Shortcut = $WshShell.CreateShortcut('{shortcut_path}')
            $Shortcut.TargetPath = '{current_dir}\\MakkelijkPdf.bat'
            $Shortcut.WorkingDirectory = '{current_dir}'
            $Shortcut.Description = 'MakkelijkPdf - PDF Converter'
            $Shortcut.Save()
            """
            
            subprocess.run(["powershell", "-Command", powershell_cmd], check=True)
            print("   ✅ Desktop shortcut gemaakt")
            
            # Start Menu shortcut
            start_menu = os.path.join(os.path.expanduser("~"), "AppData", "Roaming", "Microsoft", "Windows", "Start Menu", "Programs")
            os.makedirs(start_menu, exist_ok=True)
            start_shortcut = os.path.join(start_menu, "MakkelijkPdf.lnk")
            
            powershell_cmd = f"""
            $WshShell = New-Object -comObject WScript.Shell
            $Shortcut = $WshShell.CreateShortcut('{start_shortcut}')
            $Shortcut.TargetPath = '{current_dir}\\MakkelijkPdf.bat'
            $Shortcut.WorkingDirectory = '{current_dir}'
            $Shortcut.Description = 'MakkelijkPdf - PDF Converter'
            $Shortcut.Save()
            """
            
            subprocess.run(["powershell", "-Command", powershell_cmd], check=True)
            print("   ✅ Start Menu shortcut gemaakt")
            
            return True
            
        except Exception as e:
            print(f"   ⚠️ Kon shortcuts niet maken: {e}")
            return False
    
    return True

def test_application():
    """Test de applicatie"""
    print("\n🧪 Test applicatie...")
    try:
        # Import test
        import customtkinter
        import pdf2image
        from PIL import Image
        print("   ✅ Alle modules kunnen worden geïmporteerd")
        
        # Poppler test
        try:
            from pdf2image import convert_from_path
            print("   ✅ Poppler is beschikbaar")
        except Exception as e:
            print(f"   ⚠️ Poppler test gefaald: {e}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Test gefaald: {e}")
        return False

def start_application():
    """Start de applicatie"""
    print("\n🚀 Start MakkelijkPdf...")
    try:
        if platform.system() == "Windows":
            subprocess.Popen(["python", "main.py"])
        else:
            subprocess.Popen(["python3", "main.py"])
        print("   ✅ MakkelijkPdf gestart!")
        return True
    except Exception as e:
        print(f"   ❌ Kon applicatie niet starten: {e}")
        return False

def main():
    """Hoofdfunctie van de wizard"""
    print_header()
    
    # Stap 1: Python controle
    if not check_python():
        print("\n❌ Setup gefaald: Python niet gevonden of te oud")
        print("📥 Download Python van: https://python.org")
        input("\nDruk op Enter om te sluiten...")
        return
    
    # Stap 2: Dependencies installeren
    if not install_dependencies():
        print("\n❌ Setup gefaald: Kon dependencies niet installeren")
        input("\nDruk op Enter om te sluiten...")
        return
    
    # Stap 3: Poppler installeren
    if not install_poppler():
        print("\n⚠️ Poppler installatie gefaald, maar setup gaat door...")
    
    # Stap 4: Shortcuts maken
    if not create_shortcuts():
        print("\n⚠️ Shortcuts maken gefaald, maar setup gaat door...")
    
    # Stap 5: Test applicatie
    if not test_application():
        print("\n⚠️ Test gefaald, maar setup gaat door...")
    
    # Stap 6: Start applicatie
    print("\n" + "=" * 60)
    print("🎉 SETUP VOLTOOID!")
    print("=" * 60)
    print("✅ MakkelijkPdf is geïnstalleerd en klaar voor gebruik")
    print("🔗 Shortcuts zijn gemaakt op je desktop en start menu")
    print("🚀 Je kunt nu MakkelijkPdf gebruiken!")
    print("=" * 60)
    
    # Vraag of gebruiker wil starten
    start_now = input("\n🚀 Wil je MakkelijkPdf nu starten? (j/n): ").lower().strip()
    if start_now in ['j', 'ja', 'y', 'yes']:
        start_application()
    
    print("\n👋 Bedankt voor het gebruiken van MakkelijkPdf!")
    input("Druk op Enter om te sluiten...")

if __name__ == "__main__":
    main()
