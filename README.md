# Uruchamianie testów
Polecenie `python -m unittest testy/test.py`.

# Formatowanie kodu
Używałem narzędzia `pycodestyle`.

# Generowanie dokumentacji
Polecenie `python -m pydoc -w <nazwa modułu>`.

# Sprawdzanie typów
Użyłem wtyczki Pylance do Visual Studio Code.

# Dystrybucja
Tworzę folder o strukturze

```
projekt_klient
    aplikacja
        - dbops.py
        - klient.py
    - __main__.py
```

i poleceniem 

```python -m pip install sqlalchemy --target projekt_klient```

instaluję w nim SQLAlchemy. Następnie używam

```python -m zipapp -p "/usr/bin/env python3" projekt_klient```

Utworzony plik PYZ umieszczam w folderze z plikiem `help.txt`
oraz pustym folderem `baza`.

Dla serwera analogicznie. 
