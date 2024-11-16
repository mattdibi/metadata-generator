# Kura projects metadata generator

This project is a simple tool to generate Eclipse metadata for Kura projects. Its main goal is to provide a simple to use solution to generate the metadata files required by VSCode to provide code completion and validation for Kura projects.

## How to use

### Installation

To use this tool, you need to have Python 3 installed in your system. You can download it from the [official website](https://www.python.org/downloads/).

After installing Python, you can download the latest release of this tool from the [releases page](https://github.com/mattdibi/metadata-generator/releases). Simply install the tool by running the following command:

```bash
pip3 install metadata_generator-<version>.whl
```

### Usage

```bash
usage: kura-gen [-h] [-d] [--dry-run] [--patch-target-platform]

Kura projects metadata generator

options:
  -h, --help            show this help message and exit
  -d, --debug           Print debug information
  --dry-run             Dry run. Do not write any files to disk
  --patch-target-platform
                        Patch the target platform file with the correct paths
```

> [!NOTE]
The `--patch-target-platform` option is used to substitute the `${git_work_tree}` variable in the target platform file with the path of the git repository root. **This is only needed for the Kura repository**.

### Generating metadata files

To generate the metadata files, you need to change the current working directory to the root directory of your Kura project. You can do this by running the following command:

> [!IMPORTANT]
> A successfull maven build is required before running the metadata generator.

```bash
cd /path/to/your/kura/project
```

After changing the working directory, you can run the following command to generate the metadata files:

```bash 
kura-gen
```

The tool will generate the following files:
- `javaConfig.json` at the root of the project. This config file is used to tell the PDE extension about the locations of the sub projects and target platform file.
- `.project` file in each sub project. This file is used by Eclipse to identify the project type and dependencies.
- `.classpath` file in each sub project. This file is used by Eclipse to identify the classpath of the project.
- **if the `--patch-target-platform` option is used** the script will also update the target platform file with the correct paths (i.e. substitute the `${git_work_tree}` variable with the path of the git repository root).

After generating the metadata files, you can open the project in VSCode and install the required extensions. The following extensions are required to provide code completion and validation for Kura projects:

- [Eclipse PDE support for VS Code](https://marketplace.visualstudio.com/items?itemName=yaozheng.vscode-pde)
- [Language Support for Java by Red Hat](https://marketplace.visualstudio.com/items?itemName=redhat.java)
- [Debugger for Java](https://marketplace.visualstudio.com/items?itemName=vscjava.vscode-java-debug)
- [Java Test Runner](https://marketplace.visualstudio.com/items?itemName=vscjava.vscode-java-test)

## Development environment setup

#### Install uv

Take a look at the official documentation [here](https://docs.astral.sh/uv/getting-started/installation/)

#### Run the tool

```bash
uv run generator.py
```

#### Build the sources and wheels archives

```bash
uv build
```
