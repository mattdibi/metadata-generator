""" Kura projects metadata generator """

import argparse
import sys
import logging
import os
import glob
import json
import xml.etree.ElementTree as ET

logger = logging.getLogger(__name__)

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
</projectDescription>
'''

IGNORE = ['target', 'tools', 'distrib', 'emulator', 'features', 'test-util', 'examples'] # TODO: Either use a .gitignore style file or a command line argument

# See: https://github.com/testforstephen/vscode-pde/issues/56#issuecomment-2467400571

def run():
    """ Kura projects metadata generator """

    parser = argparse.ArgumentParser(
        description="Kura projects metadata generator",)

    parser.add_argument(
            '-d', '--debug',
            help="Print debug information",
            action="store_const", dest="loglevel", const=logging.DEBUG,
            default=logging.INFO, required=False)

    parser.add_argument(
            '--dry-run',
            help="Dry run. Do not write any files to disk",
            action="store_true", required=False)

    args = parser.parse_args()

    logging.basicConfig(level=args.loglevel)

    # List all folders containing a pom.xml file in the current directory
    content = glob.glob('**/pom.xml', recursive=True)
    content = [x for x in content if not any(y in x for y in IGNORE)]
    content.sort()

    #
    # Scan the project pom.xml files
    #
    logger.info("Scanning project pom.xml files...")
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

    logger.info("Found {} projects".format(len(map)))

    #
    # Generate .classpath file
    #
    logger.info("Generating .classpath files...")
    for key,value in map.items():
        logger.debug("Processing project: {}".format(value["name"]))

        if(not value["packaging"] == "eclipse-plugin" and not value["packaging"] == "eclipse-test-plugin"):
            continue

        module_path = value["path"]
        libs = glob.glob(os.path.join(module_path, 'lib/*.jar')) # FIXME: What if the lib folder does not exist (e.g. it's named "libs")?

        classpath = ET.Element('classpath')

        classpathentry = ET.Element('classpathentry')
        classpathentry.set('kind', 'con')
        classpathentry.set('path', 'org.eclipse.jdt.launching.JRE_CONTAINER')
        classpath.append(classpathentry)

        classpathentry = ET.Element('classpathentry')
        classpathentry.set('kind', 'con')
        classpathentry.set('path', 'org.eclipse.pde.core.requiredPlugins')
        classpath.append(classpathentry)

        if os.path.isdir(os.path.join(module_path, 'src/main/java')):
            classpathentry = ET.Element('classpathentry')
            classpathentry.set('kind', 'src')
            classpathentry.set('path', 'src/main/java')

            if value["packaging"] == "eclipse-test-plugin":
                # Add attribute test
                attributes = ET.Element('attributes')
                attribute = ET.Element('attribute')
                attribute.set('name', 'test')
                attribute.set('value', 'true')
                attributes.append(attribute)
                classpathentry.append(attributes)

            classpath.append(classpathentry)

        for lib in libs:
            classpathentry = ET.Element('classpathentry')
            classpathentry.set('kind', 'lib')
            classpathentry.set('path', os.path.join('lib', os.path.basename(lib)))
            classpath.append(classpathentry)

        # TODO: resources

        if value["packaging"] == "eclipse-test-plugin" and os.path.isdir(os.path.join(module_path, 'src/test/java')):
            classpathentry = ET.Element('classpathentry')
            classpathentry.set('kind', 'src')
            classpathentry.set('path', 'src/test/java')

            # Add attribute test
            attributes = ET.Element('attributes')
            attribute = ET.Element('attribute')
            attribute.set('name', 'test')
            attribute.set('value', 'true')
            attributes.append(attribute)
            classpathentry.append(attributes)

            classpath.append(classpathentry)

        classpathentry = ET.Element('classpathentry')
        classpathentry.set('kind', 'output')
        classpathentry.set('path', 'target/classes') # TODO: sometimes this is "bin". How to determine this?
        classpath.append(classpathentry)

        tree = ET.ElementTree(classpath)
        ET.indent(tree.getroot(), space="    ")
        if not args.dry_run:
            tree.write(os.path.join(value["path"], '.classpath'), encoding='utf-8', xml_declaration=True, short_empty_elements=True)


    #
    # Generate .project file
    #
    logger.info("Generating .project files...")
    for key,value in map.items():
        logger.debug("Processing project: {}".format(value["name"]))

        if not value["packaging"] == "eclipse-plugin" and not value["packaging"] == "eclipse-test-plugin" and not value["packaging"] == "pom" and not value["packaging"] == "eclipse-repository":
            continue

        project = ET.fromstring(PROJECT_TEMPLATE)
        project.find('name').text = value["name"]
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
        if not args.dry_run:
            tree.write(os.path.join(value["path"], '.project'), encoding='utf-8', xml_declaration=True, short_empty_elements=False)

    #
    # Generate javaConfig.json
    #
    logger.info("Generating javaConfig.json...")

    target_platform = glob.glob('**/*.target', recursive=True)
    logger.debug("Found target platform files: {}".format(target_platform))
    target_platform = [x for x in target_platform if not any(y in x for y in IGNORE)] # FIXME: the target platform usually resides in the "target-*" folder. This filter gets rid of it.

    if len(target_platform) != 1:
        logger.error("There should be exactly one target platform file. Found: {}".format(len(target_platform)))
        sys.exit(1)

    javaconfig = {}
    projects = []
    for key,value in map.items():
        if(value["packaging"] == "eclipse-plugin" or value["packaging"] == "eclipse-test-plugin"):
            projects.append(value["path"])

    javaconfig["projects"] = projects
    javaconfig["targetPlatform"] = target_platform[0] # TODO: There can be only one target platform

    if not args.dry_run:
        with open('javaConfig.json', 'w') as f:
            f.write(json.dumps(javaconfig, indent=4))