"""Server script that exposes XMLRPC API for functions
found in dbops.py on localhost, port 8000. Once started, serves forever.
Quit by keyboard interrupt.
"""

import dbops
from xmlrpc.server import SimpleXMLRPCServer


def app_with_engine(f):
    def res(*args):
        return dbops.with_engine(f, *args)
    return res

def main():
    server = SimpleXMLRPCServer(("localhost", 8000), allow_none=True)
    for f, name in [(dbops.utworz, "utworz"),
                    (dbops.dodaj_wydarzenie, "dodaj_wydarzenie"),
                    (dbops.usun_wydarzenie, "usun_wydarzenie"),
                    (dbops.mod_wydarzenie, "mod_wydarzenie"),
                    (dbops.znajdz_wydarzenie, "znajdz_wydarzenie"),
                    (dbops.dodaj_miejsce, "dodaj_miejsce"),
                    (dbops.usun_miejsce, "usun_miejsce"),
                    (dbops.mod_miejsce, "mod_miejsce"),
                    (dbops.znajdz_miejsce, "znajdz_miejsce"),
                    (dbops.dodaj_miejsce_do_wydarzenia,
                    "dodaj_miejsce_do_wydarzenia"),
                    (dbops.usun_miejsce_z_wydarzenia,
                     "usun_miejsce_z_wydarzenia"),
                    (dbops.znajdz_wydarzenia_w_miejscu,
                    "znajdz_wydarzenia_w_miejscu"),
                    (dbops.dodaj_osoba, "dodaj_osoba"),
                    (dbops.usun_osoba, "usun_osoba"),
                    (dbops.mod_osoba, "mod_osoba"),
                    (dbops.znajdz_osoba, "znajdz_osoba"),
                    (dbops.zapisz, "zapisz"),
                    (dbops.wypisz, "wypisz"),
                    (dbops.znajdz_wydarzenia_osoby,
                     "znajdz_wydarzenia_osoby"),
                    (dbops.znajdz_zapisanych_na_wydarzenie,
                    "znajdz_zapisanych_na_wydarzenie")]:
        server.register_function(app_with_engine(f), name)

    server.serve_forever()

if __name__ == "__main__":
    main()
