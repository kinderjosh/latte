# The Patchwork Compiler

> [!IMPORTANT]
> Patchwork is still work-in-progress and not production ready. Use at your own risk.

Patchwork is a compiler written from scratch that generates C code compatible for Windows, Mac and Linux.

Some key features of the language as of now is that it isn't object oriented, it does (hopefully) have garbage collection, and it allows for dynamic lists out of the box.

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

## Quick Start

```bash
git clone https://github.com/kinderjosh/patchwork.git
cd patchwork
python3 src/pwc.py test/Input.pw
```

Which should compile [test/Input.pw](test/Input.pw) into ```output.exe```, then run:

```console
$ ./output.exe
Hello world!
```

## Usage

Until the language is rewritten in itself, use the bootstrap compiler written in python:

```bash
python3 pwc.py <input file>
```

Which generates ```output.c``` and ```output.exe```.

## License

[MIT](./LICENSE)
