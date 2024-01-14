import argparse
import dbops
import xmlrpc.client

## Formatowanie odpowiedzi
def format_id_output(tbl, id):
    return "Dodano {0} nr {1}.".format(tbl, id)

def format_wydarzenie_output(wyd_dict):
    res = "nr {0} nazwa: {1}; zaczyna się {2} {3}; kończy się {4} {5};\nopis: {6}".format(wyd_dict["id"], wyd_dict["nazwa"], 
                                                                                          wyd_dict["data_rozp"], wyd_dict["godzina_rozp"],
                                                                                          wyd_dict["data_zak"], wyd_dict["godzina_zak"],
                                                                                          wyd_dict["opis"]) 
    if wyd_dict["nazwa_miejsca"] is not None:
        res += "\nmiejsce: {0}".format(wyd_dict["nazwa_miejsca"]) 
    return res 

def format_osoba_output(os_dict):
    return "nr {0} imię: {1}; email: {2}".format(os_dict["id"], os_dict["imie"], os_dict["email"])

def format_miejsce_output(msc_dict):
    return "nr {0} nazwa: {1}; adres {2}".format(msc_dict["id"], msc_dict["nazwa"], msc_dict["adres"])

def print_list_output(xs):
    print("----WYNIKI----")
    num_of_results = 0
    for x in xs:
        print(x, end="\n\n")
        num_of_results += 1 
    print(f"(liczba wyników: {num_of_results})")


## Interakcja z użytkownikiem
def configure_parser(parser):
    parser.add_argument("-s",              help="Dostęp przez API.", action="store_true")
    parser.add_argument("--nr-wydarzenia", help="Podaje numer wydarzenia.")
    parser.add_argument("--nazwa",         help="Podaje nazwę (wydarzenia lub miejsca, w zależności od komendy).")
    parser.add_argument("--godz-rozp",     help="Podaje godzinę GG:MM rozpoczęcia.")
    parser.add_argument("--data-rozp",     help="Podaje datę RRRR-MM-DD rozpoczęcia.")
    parser.add_argument("--godz-zak",      help="Podaje godzinę GG:MM zakończenia.")
    parser.add_argument("--data-zak",      help="Podaje datę RRRR-MM-DD zakończenia.")
    parser.add_argument("--opis",          help="Podaje opis.")
    parser.add_argument("--nr-miejsca",    help="Podaje numer miejsca.")
    parser.add_argument("--adres",         help="Podaje adres.")
    parser.add_argument("--nr-osoby",      help="Podaje numer osoby.")
    parser.add_argument("--imie",          help="Podaje imię.")
    parser.add_argument("--email",         help="Podaje adres email.")
    
    grp = parser.add_mutually_exclusive_group()
    grp.add_argument("--dodaj-wydarzenie", 
                        help="""Dodaje wydarzenie do kalendarza. Podać (za pomocą odpowiednich opcji)
                              - nazwę - datę rozpoczęcia RRRR-MM-DD
                              - godzinę rozpoczęcia GG:MM - datę zakończenia - godzinę zakończenia - opis""",
                              action="store_true")
    grp.add_argument("--usun-wydarzenie",   help="Usuwa wydarzenie z kalendarza. Podać - nr wydarzenia.",                                action="store_true")
    grp.add_argument("--mod-wydarzenie",    help="Modyfikuje wydarzenie. Podać - nr wydarzenia [- pola do modyfikacji].",                action="store_true")
    grp.add_argument("--znajdz-wydarzenie", help="Szuka wydarzenia o podanej nazwie. Podać - nazwę.",                                    action="store_true")
    grp.add_argument("--utworz-miejsce",    help="Dodaj miejsce do bazy miejsc. Podać - nazwę [- adres].",                               action="store_true")
    grp.add_argument("--zapomnij-miejsce",  help="Usuwa miejsce z bazy miejsc. Podać - nr miejsca.",                                     action="store_true")
    grp.add_argument("--mod-miejsce",       help="Modyfikuje miejsce. Podać - nr miejsca [- pola do modyfikacji].",                      action="store_true")
    grp.add_argument("--znajdz-miejsce",    help="Szuka miejsca o podanej nazwie. Podać - nazwę.",                                       action="store_true")
    grp.add_argument("--dodaj-miejsce",     help="Dodaje miejsce do wydarzenia. Podać - nr wydarzenia - nr miejsca.",                    action="store_true")
    grp.add_argument("--usun-miejsce",      help="Usuwa miejsce z wydarzenia. Podać - nr wydarzenia.",                                   action="store_true")
    grp.add_argument("--wydarzenia-w",      help="Szuka wydarzeń w miejscu o podanej nazwie. Podać - nazwę.",                            action="store_true")
    grp.add_argument("--utworz-osobe",      help="Dodaje osobę do bazy osób. Podać - imię - adres email.",                               action="store_true")
    grp.add_argument("--zapomnij-osobe",    help="Usuwa osobę z bazy osób. Podać - nr osoby.",                                           action="store_true")
    grp.add_argument("--mod-osoba",         help="Modyfikuje dane osoby. Podać - nr osoby [- pola do modyfikacji].",                     action="store_true")
    grp.add_argument("--znajdz-osobe",      help="Szuka osób o podanym imieniu. Podać - imię.",                                          action="store_true")
    grp.add_argument("--zapisz",            help="Zapisuje osobę na wydarzenie. Podać - email tej osoby - nr wydarzenia.",               action="store_true")
    grp.add_argument("--wypisz",            help="Wypisuje osobę z wydarzenia. Podać - email tej osoby - nr wydarzenia.",                action="store_true")
    grp.add_argument("--gdzie-idzie",       help="Szuka wydarzeń, na które zapisana jest osoba o podanym adresie email. Podać - email.", action="store_true")
    grp.add_argument("--kto-idzie",         help="Szuka osób zapisanych na wydarzenie. Podać - nr wydarzenia.",                          action="store_true")

def invoke_action(action, action_args, online):
    if online:
        server = xmlrpc.client.ServerProxy("http://localhost:8000", allow_none=True)
        return eval("server." + action + "(*action_args)", globals(), locals())
    else:
        return eval("dbops.with_engine(dbops." + action + ", *action_args)", globals(), locals())

def main():
    parser = argparse.ArgumentParser()
    configure_parser(parser)
    args = parser.parse_args()
    
    if args.dodaj_wydarzenie:
        id = invoke_action("dodaj_wydarzenie", [args.nazwa, args.data_rozp, args.godz_rozp, args.data_zak, args.godz_zak, args.opis], args.s)
        print(format_id_output("wydarzenie", id))
    elif args.usun_wydarzenie:
        invoke_action("usun_wydarzenie", [args.nr_wydarzenia], args.s)
    elif args.mod_wydarzenie:
        invoke_action("mod_wydarzenie", [args.nr_wydarzenia, args.nazwa, args.data_rozp, args.godz_rozp, args.data_zak, args.godz_zak, args.opis], args.s)
    elif args.znajdz_wydarzenie:
        print_list_output(map(format_wydarzenie_output, invoke_action("znajdz_wydarzenie", [args.nazwa], args.s)))
    elif args.utworz_miejsce:
        print(format_id_output("miejsce", invoke_action("dodaj_miejsce", [args.nazwa, args.adres], args.s)))
    elif args.zapomnij_miejsce:
        invoke_action("usun_miejsce", [args.nr_miejsca], args.s)
    elif args.mod_miejsce:
        invoke_action("mod_miejsce", [args.nr_miejsca, args.nazwa, args.adres], args.s)
    elif args.znajdz_miejsce:
        print_list_output(map(format_miejsce_output, invoke_action("znajdz_miejsce", [args.nazwa], args.s)))
    elif args.dodaj_miejsce:
        invoke_action("dodaj_miejsce_do_wydarzenia", [args.nr_miejsca, args.nr_wydarzenia], args.s)
    elif args.usun_miejsce:
        invoke_action("usun_miejsce_z_wydarzenia", [args.nr_wydarzenia], args.s)
    elif args.wydarzenia_w:
        print_list_output(map(format_wydarzenie_output, invoke_action("znajdz_wydarzenia_w_miejscu", [args.nazwa], args.s)))
    elif args.utworz_osobe:
        print(format_id_output("osobę", invoke_action("dodaj_osoba", [args.imie, args.email], args.s)))
    elif args.zapomnij_osobe:
        invoke_action("usun_osoba", [args.nr_osoby], args.s)
    elif args.mod_osoba:
        invoke_action("mod_osoba", [args.nr_osoby, args.imie, args.email], args.s)
    elif args.znajdz_osobe:
        print_list_output(map(format_osoba_output, invoke_action("znajdz_osoba", [args.imie], args.s)))
    elif args.zapisz:
        invoke_action("zapisz", [args.email, args.nr_wydarzenia], args.s)
    elif args.wypisz:
        invoke_action("wypisz", [args.email, args.nr_wydarzenia], args.s)
    elif args.gdzie_idzie:
        print_list_output(map(format_wydarzenie_output, invoke_action("znajdz_wydarzenia_osoby", [args.email], args.s)))
    elif args.kto_idzie:
        print_list_output(map(format_osoba_output, invoke_action("znajdz_zapisanych_na_wydarzenie", [args.nr_wydarzenia], args.s)))
    else:
        invoke_action("utworz", [], args.s)

if __name__ == "__main__":
    main()
