#!usr/bin/env python3

import glob
import json
import xml.etree.ElementTree as ET

IGNORE = ['target', 'tools', 'distrib', 'emulator', 'features', 'test-util', 'examples'] # TODO: Either use a .gitignore style file or a command line argument

# See: https://github.com/testforstephen/vscode-pde/issues/56#issuecomment-2467400571

def run():
    # List all folders containing a pom.xml file in the current directory
    content = glob.glob('**/pom.xml', recursive=True)
    # Filter out ignored folders
    content = [x for x in content if not any(y in x for y in IGNORE)]

    # Sort the list
    content.sort()

    # Parse the pom.xml files
    map = {}
    for pom in content:
        # Read pom.xml file content
        tree = ET.parse(pom)
        root = tree.getroot()

        # Get the project name
        packaging = root.find('{http://maven.apache.org/POM/4.0.0}packaging').text

        map[pom] = packaging


    print(json.dumps(map, indent=4))
