import unittest
import os
from aplikacja import dbops
from sqlalchemy import create_engine


class TestWydarzenie(unittest.TestCase):
    def setUp(self):
        eng = create_engine(dbops.dbpath, echo=False)
        dbops.utworz(eng)
        eng.dispose()

    def tearDown(self):
        os.remove(dbops.path)

    def testCorrectAddSearchDelete(self):
        eng = create_engine(dbops.dbpath, echo=False)
        wyd1 = {"nazwa": "wykład",
                "data_rozp": "2024-01-14", "godzina_rozp": "14:15",
                "data_zak": "2024-01-14", "godzina_zak": "16:00",
                "opis": "systemy typów", "nazwa_miejsca": None}
        wyd2 = {"nazwa": "wykład",
                "data_rozp": "2024-01-13", "godzina_rozp": "08:15",
                "data_zak": "2024-01-13", "godzina_zak": "10:00",
                "opis": "teoria kategorii", "nazwa_miejsca": None}
        wyd1["id"] = dbops.dodaj_wydarzenie(eng,
                                            wyd1["nazwa"],
                                            wyd1["data_rozp"],
                                            wyd1["godzina_rozp"],
                                            wyd1["data_zak"],
                                            wyd1["godzina_zak"],
                                            wyd1["opis"])
        wyd2["id"] = dbops.dodaj_wydarzenie(eng,
                                            wyd2["nazwa"],
                                            wyd2["data_rozp"],
                                            wyd2["godzina_rozp"],
                                            wyd2["data_zak"],
                                            wyd2["godzina_zak"],
                                            wyd2["opis"])
        xs = dbops.znajdz_wydarzenie(eng, "wykład")
        self.assertEqual(len(xs), 2, "zła liczba wyników")
        self.assertIn(wyd1, xs, "brakuje rekordu")
        self.assertIn(wyd2, xs, "brakuje rekordu")
        dbops.usun_wydarzenie(eng, wyd1["id"])
        dbops.usun_wydarzenie(eng, wyd2["id"])
        xs = dbops.znajdz_wydarzenie(eng, "wykład")
        self.assertEqual(xs, [], "nie usunięto")
        eng.dispose(close=True)

    def testIncorrectAdd(self):
        eng = create_engine(dbops.dbpath, echo=False)
        self.assertRaises(ValueError, dbops.dodaj_wydarzenie, eng,
                          "niemożliwe",
                          "2024-01-01", "00:00",
                          "2023-12-31", "23:59",
                          "podróż w czasie")
        eng.dispose()

    def testMod(self):
        eng = create_engine(dbops.dbpath, echo=False)
        id = dbops.dodaj_wydarzenie(eng, "wykład",
                                    "2024-01-14", "14:15",
                                    "2024-01-14", "16:00",
                                    "systemy typów")
        dbops.mod_wydarzenie(eng, id, "wykład z systemów typów",
                             None, None, None, None,
                             "wykładowca XYZ")
        xs = dbops.znajdz_wydarzenie(eng, "wykład z systemów typów")
        self.assertEqual(xs,
                         [{"id": id, "nazwa": "wykład z systemów typów",
                           "data_rozp": "2024-01-14", "godzina_rozp": "14:15",
                           "data_zak": "2024-01-14", "godzina_zak": "16:00",
                           "opis": "wykładowca XYZ",
                           "nazwa_miejsca": None}],
                         "błędna modyfikacja rekordu")
        eng.dispose()


class TestOsoba(unittest.TestCase):
    def setUp(self):
        eng = create_engine(dbops.dbpath, echo=False)
        dbops.utworz(eng)
        eng.dispose()

    def tearDown(self):
        os.remove(dbops.path)

    def testCorrectAddSearch(self):
        eng = create_engine(dbops.dbpath, echo=False)
        id = dbops.dodaj_osoba(eng,
                               "Ferdynand Kiepski",
                               "ferdek@kiepski.pl")
        xs = dbops.znajdz_osoba(eng, "Ferdynand Kiepski")
        self.assertIn({"id": id,
                       "imie": "Ferdynand Kiepski",
                       "email": "ferdek@kiepski.pl"},
                      xs, "brakuje rekordu")
        eng.dispose()

    def testIncorrectAdd(self):
        eng = create_engine(dbops.dbpath, echo=False)
        self.assertRaises(ValueError, dbops.dodaj_osoba,
                          eng, "Ferdynand", "ferdek")
        eng.dispose()

    def testSignupQuit(self):
        eng = create_engine(dbops.dbpath, echo=False)
        wyd_id = dbops.dodaj_wydarzenie(eng, "libacja",
                                        "2024-01-13", "20:00",
                                        "2024-01-14", "05:00",
                                        "godzina zakończenia jest umowna")
        osoba = {"imie": "Marian Paździoch", "email": "marian@pazdzioch.pl"}
        osoba["id"] = dbops.dodaj_osoba(eng, osoba["imie"], osoba["email"])

        dbops.zapisz(eng, osoba["email"], wyd_id)
        xs = dbops.znajdz_zapisanych_na_wydarzenie(eng, wyd_id)
        self.assertIn(osoba, xs, "brakuje rekordu")

        dbops.wypisz(eng, osoba["email"], wyd_id)
        xs = dbops.znajdz_zapisanych_na_wydarzenie(eng, wyd_id)
        self.assertNotIn(osoba, xs, "nie usunięto")
        eng.dispose()
