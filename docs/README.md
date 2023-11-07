# Build ```pynasapower``` documentation

## Installing requirements
```bash
pip install .[docs]
```
or

```bash
pip install -r ./docs/requirements-docs.txt
```

## Quickstart with ```sphinx``` (Already implemented in this repository)

Start by moving in ```docs``` folder. If the current path is in
main folder run:

```bash
cd docs/
```

then inside the ```docs/``` folder run:

```bash
sphinx-quickstart
```

and start configuring the project.

## Automatic docstring documentation with ```sphinx-apidoc```

```bash
sphinx-apidoc ../pynasapower/ -o .
```

## Build ```HTML``` pages

```bash
make html
```