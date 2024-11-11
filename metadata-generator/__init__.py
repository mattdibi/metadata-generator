#!usr/bin/env python3

import os
import glob
import json
import xml.etree.ElementTree as ET

PROJECT_TEMPLATE = '''<?xml version="1.0" encoding="UTF-8"?>
<projectDescription>
	<name>NAME</name>
	<comment></comment>
	<projects>
    </projects>
	<buildSpec>
		<buildCommand>
			<name>org.eclipse.m2e.core.maven2Builder</name>
			<arguments>
			</arguments>
		</buildCommand>
	</buildSpec>
	<natures>
		<nature>org.eclipse.m2e.core.maven2Nature</nature>
	</natures>
	<filteredResources>
		<filter>
			<id>ID</id>
			<name></name>
			<type>30</type>
			<matcher>
				<id>org.eclipse.core.resources.regexFilterMatcher</id>
				<arguments>node_modules|\\.git|__CREATED_BY_JAVA_LANGUAGE_SERVER__</arguments>
			</matcher>
		</filter>
	</filteredResources>
</projectDescription>
'''

IGNORE = ['target', 'tools', 'distrib', 'emulator', 'features', 'test-util', 'examples', 'test'] # TODO: Either use a .gitignore style file or a command line argument

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

        # TODO: resources

        # TODO: test sources

        classpathentry = ET.Element('classpathentry')
        classpathentry.set('kind', 'output')
        classpathentry.set('path', 'target/classes')
        classpath.append(classpathentry)

        tree = ET.ElementTree(classpath)
        ET.indent(tree.getroot(), space="    ")
        tree.write(os.path.join(value["path"], '.classpath'), encoding='utf-8', xml_declaration=True, short_empty_elements=False)

    #
    # Generate .project file
    #
    id = 1681116377780
    for key,value in map.items():
        if not value["packaging"] == "eclipse-plugin" and not value["packaging"] == "eclipse-test-plugin" and not value["packaging"] == "pom" and not value["packaging"] == "eclipse-repository":
            continue

        project = ET.fromstring(PROJECT_TEMPLATE)
        project.find('name').text = value["name"]
        project.find('.//id').text = str(id)
        project.find('comment').text = ""

        if value["packaging"] == "eclipse-plugin" or value["packaging"] == "eclipse-test-plugin":
            buildSpec = project.find('buildSpec')

            buildCommand = ET.Element('buildCommand')
            buildCommandName = ET.Element('name')
            buildCommandName.text = 'org.eclipse.jdt.core.javabuilder'
            buildCommand.append(buildCommandName)

            buildArguments = ET.Element('arguments')
            buildCommand.append(buildArguments)

            buildSpec.append(buildCommand)

            buildCommand = ET.Element('buildCommand')
            buildCommandName = ET.Element('name')
            buildCommandName.text = 'org.eclipse.pde.ManifestBuilder'
            buildCommand.append(buildCommandName)

            buildArguments = ET.Element('arguments')
            buildCommand.append(buildArguments)

            buildSpec.append(buildCommand)

            buildCommand = ET.Element('buildCommand')
            buildCommandName = ET.Element('name')
            buildCommandName.text = 'org.eclipse.pde.SchemaBuilder'
            buildCommand.append(buildCommandName)

            buildArguments = ET.Element('arguments')
            buildCommand.append(buildArguments)

            buildSpec.append(buildCommand)

            natures = project.find('natures')
            nature = ET.Element('nature')
            nature.text = 'org.eclipse.pde.PluginNature'
            natures.append(nature)

            nature = ET.Element('nature')
            nature.text = 'org.eclipse.jdt.core.javanature'
            natures.append(nature)

        tree = ET.ElementTree(project)
        ET.indent(tree.getroot(), space="    ")
        tree.write(os.path.join(value["path"], '.project'), encoding='utf-8', xml_declaration=True, short_empty_elements=False)

        id += 1

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
