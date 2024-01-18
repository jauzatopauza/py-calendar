"""Client script with command line user interface. Run with -h for help.
Requires a help.txt file to exist in directory `projekt/aplikacja`.
To learn the required format, see configure_parser.
"""

import argparse
import dbops
import xmlrpc.client


def format_id_output(tbl, id):
    """Return a string with a message that some entity has been added.
    
    Positional arguments:
    tbl -- Polish name of the entity in the accusative case;
    "wydarzenie" for event, "miejsce" for location, "osobę" for person.
    id -- the added entity's ID.
    """
    return "Dodano {0} nr {1}.".format(tbl, id)


def format_wydarzenie_output(wyd_dict):
    """Return a string summarizing an event.
    
    Positional arguments:
    wyd_dict -- dictionary representing an event --
    see dbops.dict_of_wydarzenie.
    """
    res = ("nr {0} nazwa: {1}; zaczyna się {2} {3};"
           " kończy się {4} {5};\nopis: {6}")
    res = res.format(wyd_dict["id"], wyd_dict["nazwa"],
                     wyd_dict["data_rozp"], wyd_dict["godzina_rozp"],
                     wyd_dict["data_zak"], wyd_dict["godzina_zak"],
                     wyd_dict["opis"])
    if wyd_dict["nazwa_miejsca"] is not None:
        res += "\nmiejsce: {0}".format(wyd_dict["nazwa_miejsca"])
    return res


def format_osoba_output(os_dict):
    """Return a string summarizing a person.
    
    Positional arguments:
    os_dict -- dictionary representing a person --
    see dbops.dict_of_osoba.
    """
    return "nr {0} imię: {1}; email: {2}".format(os_dict["id"],
                                                 os_dict["imie"],
                                                 os_dict["email"])


def format_miejsce_output(msc_dict):
    """Return a string summarizing a location.
    
    Positional arguments:
    wyd_dict -- dictionary representing a location --
    see dbops.dict_of_miejsce.
    """
    return "nr {0} nazwa: {1}; adres {2}".format(msc_dict["id"],
                                                 msc_dict["nazwa"],
                                                 msc_dict["adres"])


def print_list_output(xs):
    """Print a list of strings, separated by double newline.
    
    Also outputs the number of results i.e. the length of the list.
    """
    print("----WYNIKI----")
    num_of_results = 0
    for x in xs:
        print(x, end="\n\n")
        num_of_results += 1
    print(f"(liczba wyników: {num_of_results})")


class BadParserConfigFileError(Exception):
    """Exception raised by configure_parser."""
    pass


def configure_parser(parser):
    r"""Configure the command line argument parser 
    according to help.txt. Required format:
    
    - first line is exactly "OPTIONS\n", where \n is the newline character
    - the following lines specify arguments that do not accept a parameter
    and can be used independently of other arguments;
    notation: name of the argument and help text separated by a single space
    - some further line is exactly "PARAMS\n"
    - the following lines specify arguments that accept a parameter
    and can be used independently of other arguments
    - some further line is exactly "ACTIONS\n"
    - the following lines specify arguments that do not accept a parameter
    and cannot be used together with any of the other arguments listed
    under ACTIONS.
    
    The first requirement is enforced by raising BadParserConfigFileError.
    """
    with open("aplikacja/help.txt", "r", encoding="utf-8") as f:
        line = f.readline()
        if line != "OPTIONS\n":
            raise BadParserConfigFileError()
        line = f.readline()
        while line != "PARAMS\n":
            xs = line.split(" ", maxsplit=1)
            parser.add_argument(xs[0], help=xs[1], action="store_true")
            line = f.readline()
        line = f.readline()
        while line != "ACTIONS\n":
            xs = line.split(" ", maxsplit=1)
            parser.add_argument(xs[0], help=xs[1])
            line = f.readline()
        line = f.readline()
        grp = parser.add_mutually_exclusive_group()
        while line != "":
            xs = line.split(" ", maxsplit=1)
            grp.add_argument(xs[0], help=xs[1], action="store_true")
            line = f.readline()


def invoke_action(action, action_args, online):
    if online:
        server = xmlrpc.client.ServerProxy("http://localhost:8000",
                                           allow_none=True)
        return eval("server." + action + "(*action_args)",
                    globals(), locals())
    else:
        return eval("dbops.with_engine(dbops." + action + ", *action_args)",
                    globals(), locals())


def main():
    parser = argparse.ArgumentParser()
    configure_parser(parser)
    args = parser.parse_args()

    if args.dodaj_wydarzenie:
        id = invoke_action("dodaj_wydarzenie", [args.nazwa,
                                                args.data_rozp, args.godz_rozp,
                                                args.data_zak, args.godz_zak,
                                                args.opis], args.s)
        print(format_id_output("wydarzenie", id))
    elif args.usun_wydarzenie:
        invoke_action("usun_wydarzenie", [args.nr_wydarzenia], args.s)
    elif args.mod_wydarzenie:
        invoke_action("mod_wydarzenie", [args.nr_wydarzenia, args.nazwa,
                                         args.data_rozp, args.godz_rozp,
                                         args.data_zak, args.godz_zak,
                                         args.opis], args.s)
    elif args.znajdz_wydarzenie:
        print_list_output(map(format_wydarzenie_output,
                              invoke_action("znajdz_wydarzenie",
                                            [args.nazwa], args.s)))
    elif args.utworz_miejsce:
        print(format_id_output("miejsce",
                               invoke_action("dodaj_miejsce",
                                             [args.nazwa, args.adres],
                                             args.s)))
    elif args.zapomnij_miejsce:
        invoke_action("usun_miejsce", [args.nr_miejsca], args.s)
    elif args.mod_miejsce:
        invoke_action("mod_miejsce", [args.nr_miejsca,
                                      args.nazwa,
                                      args.adres],
                      args.s)
    elif args.znajdz_miejsce:
        print_list_output(map(format_miejsce_output,
                              invoke_action("znajdz_miejsce",
                                            [args.nazwa], args.s)))
    elif args.dodaj_miejsce:
        invoke_action("dodaj_miejsce_do_wydarzenia",
                      [args.nr_miejsca, args.nr_wydarzenia], args.s)
    elif args.usun_miejsce:
        invoke_action("usun_miejsce_z_wydarzenia",
                      [args.nr_wydarzenia], args.s)
    elif args.wydarzenia_w:
        print_list_output(map(format_wydarzenie_output,
                              invoke_action("znajdz_wydarzenia_w_miejscu",
                                            [args.nazwa], args.s)))
    elif args.utworz_osobe:
        print(format_id_output("osobę",
                               invoke_action("dodaj_osoba",
                                             [args.imie, args.email], args.s)))
    elif args.zapomnij_osobe:
        invoke_action("usun_osoba", [args.nr_osoby], args.s)
    elif args.mod_osoba:
        invoke_action("mod_osoba", [args.nr_osoby,
                                    args.imie,
                                    args.email],
                      args.s)
    elif args.znajdz_osobe:
        print_list_output(map(format_osoba_output,
                              invoke_action("znajdz_osoba",
                                            [args.imie], args.s)))
    elif args.zapisz:
        invoke_action("zapisz", [args.email, args.nr_wydarzenia], args.s)
    elif args.wypisz:
        invoke_action("wypisz", [args.email, args.nr_wydarzenia], args.s)
    elif args.gdzie_idzie:
        print_list_output(map(format_wydarzenie_output,
                              invoke_action("znajdz_wydarzenia_osoby",
                                            [args.email], args.s)))
    elif args.kto_idzie:
        print_list_output(map(format_osoba_output,
                              invoke_action("znajdz_zapisanych_na_wydarzenie",
                                            [args.nr_wydarzenia], args.s)))
    else:
        invoke_action("utworz", [], args.s)


if __name__ == "__main__":
    main()
