#!/usr/bin/env python3
"""
MakkelijkPdf - Versie Management Script
"""

import os
import sys
import json
from datetime import datetime
from version import VERSION_INFO, CHANGELOG

def update_version(major=None, minor=None, patch=None, codename=None):
    """Update versie nummer"""
    new_version = VERSION_INFO.copy()
    
    if major is not None:
        new_version['major'] = major
    if minor is not None:
        new_version['minor'] = minor
    if patch is not None:
        new_version['patch'] = patch
    if codename is not None:
        new_version['codename'] = codename
    
    new_version['build'] = str(int(new_version['build']) + 1).zfill(3)
    new_version['date'] = datetime.now().strftime("%Y-%m-%d")
    
    return new_version

def create_release_notes(version):
    """Maak release notes"""
    version_key = f"{version['major']}.{version['minor']}.{version['patch']}"
    
    if version_key in CHANGELOG:
        changelog_entry = CHANGELOG[version_key]
        notes = f"# Release {version_key} - {version['date']}\n\n"
        notes += f"**Codename:** {version['codename']}\n\n"
        
        if changelog_entry.get('features'):
            notes += "## Nieuwe Features\n"
            for feature in changelog_entry['features']:
                notes += f"- {feature}\n"
            notes += "\n"
        
        if changelog_entry.get('fixes'):
            notes += "## Bug Fixes\n"
            for fix in changelog_entry['fixes']:
                notes += f"- {fix}\n"
            notes += "\n"
        
        if changelog_entry.get('breaking_changes'):
            notes += "## Breaking Changes\n"
            for change in changelog_entry['breaking_changes']:
                notes += f"- {change}\n"
            notes += "\n"
        
        return notes
    
    return f"# Release {version_key} - {version['date']}\n\nGeen changelog beschikbaar."

def main():
    """Hoofdfunctie"""
    if len(sys.argv) < 2:
        print("Gebruik: python version_manager.py [command]")
        print("Commands:")
        print("  current - Toon huidige versie")
        print("  bump [major|minor|patch] - Verhoog versie")
        print("  release - Maak release notes")
        print("  tag - Maak Git tag")
        return
    
    command = sys.argv[1]
    
    if command == "current":
        print(f"Huidige versie: {VERSION_INFO['major']}.{VERSION_INFO['minor']}.{VERSION_INFO['patch']}")
        print(f"Build: {VERSION_INFO['build']}")
        print(f"Datum: {VERSION_INFO['date']}")
        print(f"Codename: {VERSION_INFO['codename']}")
    
    elif command == "bump":
        if len(sys.argv) < 3:
            print("Specificeer versie type: major, minor, of patch")
            return
        
        bump_type = sys.argv[2]
        current = VERSION_INFO
        
        if bump_type == "major":
            new_version = update_version(major=current['major'] + 1, minor=0, patch=0)
        elif bump_type == "minor":
            new_version = update_version(minor=current['minor'] + 1, patch=0)
        elif bump_type == "patch":
            new_version = update_version(patch=current['patch'] + 1)
        else:
            print("Ongeldig versie type. Gebruik: major, minor, of patch")
            return
        
        print(f"Nieuwe versie: {new_version['major']}.{new_version['minor']}.{new_version['patch']}")
        print("Update version.py handmatig met nieuwe versie informatie.")
    
    elif command == "release":
        version_key = f"{VERSION_INFO['major']}.{VERSION_INFO['minor']}.{VERSION_INFO['patch']}"
        notes = create_release_notes(VERSION_INFO)
        
        filename = f"RELEASE_{version_key}.md"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(notes)
        
        print(f"Release notes opgeslagen in {filename}")
    
    elif command == "tag":
        version_key = f"{VERSION_INFO['major']}.{VERSION_INFO['minor']}.{VERSION_INFO['patch']}"
        tag_name = f"v{version_key}"
        
        print(f"Maak Git tag: {tag_name}")
        print(f"Git command: git tag -a {tag_name} -m \"Release {version_key}\"")
        print(f"Push command: git push origin {tag_name}")

if __name__ == "__main__":
    main()
