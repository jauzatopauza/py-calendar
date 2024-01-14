import dbops 
from xmlrpc.server import SimpleXMLRPCServer

server = SimpleXMLRPCServer(("localhost", 8000), allow_none=True)
for _ in map(lambda p: server.register_function(*p),
[(dbops.utworz, "utworz"),
 (dbops.dodaj_wydarzenie, "dodaj_wydarzenie"),
 (dbops.usun_wydarzenie, "usun_wydarzenie"),
 (dbops.mod_wydarzenie, "mod_wydarzenie"),
 (dbops.znajdz_wydarzenie, "znajdz_wydarzenie"),
 (dbops.dodaj_miejsce, "dodaj_miejsce"),
 (dbops.usun_miejsce, "usun_miejsce"),
 (dbops.mod_miejsce, "mod_miejsce"),
 (dbops.znajdz_miejsce, "znajdz_miejsce"),
 (dbops.dodaj_miejsce_do_wydarzenia, "dodaj_miejsce_do_wydarzenia"),
 (dbops.usun_miejsce_z_wydarzenia, "usun_miejsce_z_wydarzenia"),
 (dbops.znajdz_wydarzenia_w_miejscu, "znajdz_wydarzenia_w_miejscu"),
 (dbops.dodaj_osoba, "dodaj_osoba"),
 (dbops.usun_osoba, "usun_osoba"),
 (dbops.mod_osoba, "mod_osoba"),
 (dbops.znajdz_osoba, "znajdz_osoba"),
 (dbops.zapisz, "zapisz"),
 (dbops.wypisz, "wypisz"),
 (dbops.znajdz_wydarzenia_osoby, "znajdz_wydarzenia_osoby"),
 (dbops.znajdz_zapisanych_na_wydarzenie, "znajdz_zapisanych_na_wydarzenie")]): pass

server.serve_forever() 
