import unittest 
import os
from ..aplikacja.dbops import *

class TestWydarzenie(unittest.TestCase):
    def setUp(self):
        utworz()
    
    def tearDown(self):
        os.remove(path)

    def testCorrectAddSearchDelete(self):
        wyd1 = {"nazwa" : "wykład",
                "data_rozp" : "2024-01-14", "godzina_rozp" : "14:15", 
                "data_zak" : "2024-01-14", "godzina_zak" : "16:00",
                "opis" : "systemy typów", "nazwa_miejsca" : None }
        wyd2 = {"nazwa" : "wykład",
                "data_rozp" : "2024-01-13", "godzina_rozp" : "8:15", 
                "data_zak" : "2024-01-13", "godzina_zak" : "10:00",
                "opis" : "teoria kategorii", "nazwa_miejsca" : None }
        wyd1["id"] = dodaj_wydarzenie(wyd1["nazwa"], wyd1["data_rozp"], wyd1["godzina_rozp"], wyd1["data_zak"],wyd1["godzina_zak"], wyd1["godzina_zak"])
        wyd2["id"] = dodaj_wydarzenie(wyd2["nazwa"], wyd2["data_rozp"], wyd2["godzina_rozp"], wyd2["data_zak"],wyd2["godzina_zak"], wyd2["godzina_zak"])
        xs = znajdz_wydarzenie("wykład")
        self.assertEquals(len(xs), 2, "zła liczba wyników")
        self.assertIn(wyd1, xs, "brakuje rekordu")
        self.assertIn(wyd2, xs, "brakuje rekordu")
        usun_wydarzenie(wyd1["id"])
        usun_wydarzenie(wyd2["id"])
        xs = znajdz_wydarzenie("wykład")
        self.assertEquals(xs, [], "nie usunięto")
    
    def testIncorrectAdd(self):
        self.assertRaises(ValueError, dodaj_wydarzenie, ("niemożliwe", "2024-01-01", "00:00", "2023-12-31", "23:59", "podróż w czasie"))
    
    def testMod(self):
        id = dodaj_wydarzenie("wykład", "2024-01-14", "14:15", "2024-01-14", "16:00", "systemy typów")
        mod_wydarzenie(id, "wykład z systemów typów", None, None, None, None, "wykładowca Piotr Polesiuk")
        xs = znajdz_wydarzenie("wykład z systemów typów")
        self.assertEquals(xs,
                          [{"id" : id, "nazwa" : "wykład z systemów typów",
                            "data_rozp" : "2024-01-14", "godzina_rozp" : "14:15", 
                            "data_zak" : "2024-01-14", "godzina_zak" : "16:00",
                            "opis" : "wykładowca Piotr Polesiuk", "nazwa_miejsca" : None }],
                          "błędna modyfikacja rekordu")

class TestOsoba(unittest.TestCase):
    def setUp(self):
        utworz()
    
    def tearDown(self):
        os.remove(path)

    def testCorrectAddSearch(self):
        id = dodaj_osoba("Ferdynand Kiepski", "ferdek@kiepski.pl")
        xs = znajdz_osoba("Ferdynand Kiepski")
        self.assertIn({"id" : id, "imie" : "Ferdynand Kiepski", "email" : "ferdek@kiepski.pl"}, xs, "brakuje rekordu")

    def testIncorrectAdd(self):
        self.assertRaises(ValueError, dodaj_osoba, ("Ferdynand", "ferdek"))
    
    def testSignupQuit(self):
        wyd_id = dodaj_wydarzenie("libacja", "2024-01-13", "20:00", "2024-01-14", "5:00", "UWAGA. godzina zakończenia jest umowna")
        osoba = {"imie" : "Marian Paździoch", "email" : "marian@pazdzioch.pl"}
        osoba["id"] = dodaj_osoba(osoba["imie"], osoba["email"])
        
        zapisz(osoba["email"], wyd_id)
        xs = znajdz_zapisanych_na_wydarzenie(wyd_id)
        self.assertIn(osoba, xs, "brakuje rekordu")
        
        wypisz(osoba["email", wyd_id])
        xs = znajdz_zapisanych_na_wydarzenie(wyd_id)
        self.assertNotIn(osoba, xs, "nie usunięto")

if __name__ == "__main__":
    unittest.main()
