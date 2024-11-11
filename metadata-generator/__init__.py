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
    # Generate .classpath file
    #
    for key,value in map.items():
        if(not value["packaging"] == "eclipse-plugin" and not value["packaging"] == "eclipse-test-plugin"):
            continue

        module_path = value["path"]
        libs = glob.glob(os.path.join(module_path, 'lib/*.jar'))

        classpath = ET.Element('classpath')

        classpathentry = ET.Element('classpathentry')
        classpathentry.set('kind', 'con')
        classpathentry.set('path', 'org.eclipse.jdt.launching.JRE_CONTAINER')
        classpath.append(classpathentry)

        classpathentry = ET.Element('classpathentry')
        classpathentry.set('kind', 'con')
        classpathentry.set('path', 'org.eclipse.pde.core.requiredPlugins')
        classpath.append(classpathentry)

        classpathentry = ET.Element('classpathentry')
        classpathentry.set('kind', 'src')
        classpathentry.set('path', 'src/main/java')
        classpath.append(classpathentry)

        for lib in libs:
            classpathentry = ET.Element('classpathentry')
            classpathentry.set('kind', 'lib')
            classpathentry.set('path', os.path.join('libs', os.path.basename(lib)))
            classpath.append(classpathentry)

        classpathentry = ET.Element('classpathentry')
        classpathentry.set('kind', 'output')
        classpathentry.set('path', 'target/classes')
        classpath.append(classpathentry)

        tree = ET.ElementTree(classpath)
        ET.indent(tree.getroot(), space="    ")
        tree.write(os.path.join(value["path"], '.classpath'), encoding='utf-8', xml_declaration=True)

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
