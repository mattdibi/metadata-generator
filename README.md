# Kura projects metadata generator

This project is a simple tool to generate Eclipse metadata for Kura projects. Its main goal is to provide a simple to use solution to generate the metadata files required by VSCode to provide code completion and validation for Kura projects.

## How to use

### Installation

To use this tool, you need to have Python 3 installed in your system. You can download it from the [official website](https://www.python.org/downloads/).

After installing Python, you can download the latest release of this tool from the [releases page](). Simply install the tool by running the following command:

```bash
pip3 install metadata_generator-<version>.whl
```

After installing the tool, you can run it by executing the following command:

```bash
metadata_generator
```

### Usage

To generate the metadata files, you need to change the current working directory to the root directory of your Kura project. You can do this by running the following command:

> [!IMPORTANT]
> A successfull maven build is required before running the metadata generator.

```bash
cd /path/to/your/kura/project
```

After changing the working directory, you can run the following command to generate the metadata files:

```bash 
metadata_generator
```

The tool will generate the following files:
- `javaConfig.json` at the root of the project. This config file is used to tell the PDE extension about the locations of the sub projects and target platform file.
- `.project` file in each sub project. This file is used by Eclipse to identify the project type and dependencies.
- `.classpath` file in each sub project. This file is used by Eclipse to identify the classpath of the project.
