#!usr/bin/env python3

import os
import glob
import json
import xml.etree.ElementTree as ET

IGNORE = ['target', 'tools', 'distrib', 'emulator', 'features', 'test-util', 'examples'] # TODO: Either use a .gitignore style file or a command line argument

# See: https://github.com/testforstephen/vscode-pde/issues/56#issuecomment-2467400571

def run():
    # List all folders containing a pom.xml file in the current directory
    content = glob.glob('**/pom.xml', recursive=True)
    content = [x for x in content if not any(y in x for y in IGNORE)]
    content.sort()

    #
    # Scan the project pom.xml files
    #
    map = {}
    for pom in content:
        # Read pom.xml file content
        tree = ET.parse(pom)
        root = tree.getroot()

        # Get the project name
        packaging = root.find('{http://maven.apache.org/POM/4.0.0}packaging').text
        name = root.find('{http://maven.apache.org/POM/4.0.0}artifactId').text

        map[pom] = {
                    "path": os.path.dirname(pom),
                    "packaging": packaging,
                    "name": name
                    }


    print(json.dumps(map, indent=4))

    #
    # Generate javaConfig.json
    #
    target_platform = glob.glob('**/*.target', recursive=True)
    target_platform = [x for x in target_platform if not any(y in x for y in IGNORE)]

    javaconfig = {}
    projects = []
    for key,value in map.items():
        if(value["packaging"] == "eclipse-plugin" or value["packaging"] == "eclipse-test-plugin"):
            projects.append(value["path"])

    javaconfig["projects"] = projects
    javaconfig["targetPlatform"] = target_platform

    with open('javaConfig.json', 'w') as f:
        f.write(json.dumps(javaconfig, indent=4))
