#!/usr/bin/env python
"""
Setup and manage translations for Downtime Tracker
Run this script to initialize or update translations
"""

import os
import sys
import subprocess

def run_command(cmd, description):
    """Run a shell command and handle errors"""
    print(f"\n{description}...")
    print(f"Running: {cmd}")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ Success: {description}")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed: {description}")
        if e.stdout:
            print(f"Output: {e.stdout}")
        if e.stderr:
            print(f"Error: {e.stderr}")
        return False

def main():
    """Main setup function"""
    print("=" * 60)
    print("DOWNTIME TRACKER - TRANSLATION SETUP")
    print("=" * 60)
    
    # Check if translations directory exists
    if not os.path.exists('translations'):
        os.makedirs('translations')
        print("✅ Created translations directory")
    
    # Initialize or update translations
    if len(sys.argv) > 1 and sys.argv[1] == 'update':
        # Update existing translations
        print("\nUpdating translations...")
        
        # Extract all translatable strings - simplified command
        run_command(
            "pybabel extract -F babel.cfg -o translations/messages.pot .",
            "Extracting messages"
        )
        
        # Update existing language files
        run_command(
            "pybabel update -i translations/messages.pot -d translations",
            "Updating language files"
        )
        
    else:
        # Initial setup
        print("\nInitializing new translations...")
        
        # Extract all translatable strings - simplified command
        success = run_command(
            "pybabel extract -F babel.cfg -o translations/messages.pot .",
            "Extracting messages"
        )
        
        if not success:
            print("\nNo translatable strings found yet. Creating empty template...")
            # Create an empty POT file
            pot_content = """# Translations template for Downtime Tracker.
# Copyright (C) 2024
# This file is distributed under the same license as the project.
#
msgid ""
msgstr ""
"Project-Id-Version: Downtime Tracker 1.4.0\\n"
"Report-Msgid-Bugs-To: \\n"
"POT-Creation-Date: 2024-01-01 00:00+0000\\n"
"PO-Revision-Date: YEAR-MO-DA HO:MI+ZONE\\n"
"Last-Translator: FULL NAME <EMAIL@ADDRESS>\\n"
"Language-Team: LANGUAGE <LL@li.org>\\n"
"MIME-Version: 1.0\\n"
"Content-Type: text/plain; charset=utf-8\\n"
"Content-Transfer-Encoding: 8bit\\n"
"Generated-By: Babel 2.13.1\\n"
"""
            os.makedirs('translations', exist_ok=True)
            with open('translations/messages.pot', 'w', encoding='utf-8') as f:
                f.write(pot_content)
            print("✅ Created empty messages.pot template")
        
        # Initialize English (US)
        if not os.path.exists('translations/en'):
            run_command(
                "pybabel init -i translations/messages.pot -d translations -l en",
                "Initializing English (US)"
            )
        
        # Initialize Spanish (US/Mexico)
        if not os.path.exists('translations/es'):
            run_command(
                "pybabel init -i translations/messages.pot -d translations -l es",
                "Initializing Spanish (US/Mexico)"
            )
    
    # Compile all translations
    run_command(
        "pybabel compile -d translations",
        "Compiling translations"
    )
    
    print("\n" + "=" * 60)
    print("✅ Translation setup complete!")
    print("\nNext steps:")
    print("1. Add _() to Python strings that need translation")
    print("2. Add {{ _('text') }} to template strings")
    print("3. Run: python setup_translations.py update")
    print("4. Edit translations/es/LC_MESSAGES/messages.po")
    print("5. Run: pybabel compile -d translations")
    print("=" * 60)

if __name__ == '__main__':
    main()