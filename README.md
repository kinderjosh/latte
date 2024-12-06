# The Patchwork Compiler

> [!IMPORTANT]
> Patchwork is still work-in-progress and not production ready. Use at your own risk.

Patchwork is a transpiler written from scratch that generates C code compatible for Windows, Mac and Linux.

## GCC Requirement

You will need to install GCC and have the command ```gcc``` in your path/system variables.

### Windows

Install GCC with [MinGW](https://sourceforge.net/projects/mingw/).

### Mac

```sh
brew install gcc
```

### Linux

Different between distributions, but for Ubuntu:

```bash
sudo apt install build-essential
```

## Usage

Until the language is rewritten in itself, use the bootstrap compiler written in python:

```bash
python3 pwc.py
```

In some cases on Windows:

```bash
py pwc.py
```

Which generates ```output.c``` and ```output.exe```.

## License

[MIT](./LICENSE)