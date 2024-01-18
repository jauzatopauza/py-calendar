"""Database operations. Provides functions that realize features
provided by modules klient.py and serwer.py.
"""

from __future__ import annotations
from sqlalchemy.orm import DeclarativeBase, relationship, mapped_column
from sqlalchemy.orm import Mapped, validates, sessionmaker
from sqlalchemy import Table, Column, ForeignKey, String, Integer
from sqlalchemy import create_engine, select
from typing import List, Optional
from re import fullmatch
import datetime


class Base(DeclarativeBase):
    pass


uczestnictwa = Table("osoba_wydarzenie",
                     Base.metadata,
                     Column("osoba_id",
                            ForeignKey("osoby.id"),
                            primary_key=True),
                     Column("wydarzenie_id",
                            ForeignKey("wydarzenia.id"),
                            primary_key=True))
"""Table for many-to-many relation: participation of people in events."""


class Wydarzenie(Base):
    """ORM class for events."""

    __tablename__ = "wydarzenia"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nazwa: Mapped[str] = mapped_column(String)
    """Name"""
    data_rozp: Mapped[str] = mapped_column(String)
    """Starting date"""
    godzina_rozp: Mapped[str] = mapped_column(String)
    """Starting hour"""
    data_zak: Mapped[str] = mapped_column(String)
    """Ending date"""
    godzina_zak: Mapped[str] = mapped_column(String)
    """Ending hour"""
    opis: Mapped[str] = mapped_column(String)
    """Description"""
    miejsce_id: Mapped[Optional[int]] \
        = mapped_column(ForeignKey("miejsca.id"))
    miejsce: Mapped[Optional["Miejsce"]] = relationship()
    """Location"""
    uczestnicy: Mapped[List["Osoba"]] \
        = relationship("Osoba", secondary=uczestnictwa,
                       back_populates="wydarzenia")
    """Participants"""

    @validates("godzina_rozp", "godzina_zak")
    def validate_hour(self, key, s):
        (hh, _, mm) = s.partition(":")
        try:
            hour = int(hh)
            minute = int(mm)
            if not 0 <= hour and hour <= 23 and 0 <= minute and minute <= 59:
                raise ValueError("Niepoprawna godzina.")
        except ValueError:
            raise ValueError("Niepoprawna godzina.")
        if key == "godzina_zak":
            if (datetime.datetime.fromisoformat(self.data_rozp + "T"
                                                + self.godzina_rozp)
               > datetime.datetime.fromisoformat(self.data_zak + "T" + s)):
                raise ValueError("Data rozpoczęcia powinna być"
                                 " nie później od daty zakończenia.")
        return s

    @validates("data_rozp", "data_zak")
    def validate_date(self, _, s):
        try:
            datetime.date.fromisoformat(s)
        except ValueError:
            raise ValueError("Niepoprawna data.")
        return s

    @validates("nazwa")
    def validate_nazwa(self, _, s):
        if s == "":
            raise ValueError("Nazwa powinna być niepusta.")
        return s


class Miejsce(Base):
    """ORM class for locations."""

    __tablename__ = "miejsca"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nazwa: Mapped[str] = mapped_column(String)
    """Name"""
    adres: Mapped[Optional[str]] = mapped_column(String)
    """Address"""

    @validates("nazwa")
    def validate_nazwa(self, _, s):
        if s == "":
            raise ValueError("Nazwa powinna być niepusta.")
        return s

    @validates("adres")
    def validate_adres(self, _, s):
        if s == "":
            raise ValueError("Adres powinien być niepusty.")
        return s


class Osoba(Base):
    """ORM class for people."""

    __tablename__ = "osoby"

    id: Mapped[int] = mapped_column(primary_key=True)
    imie: Mapped[str] = mapped_column(String)
    """Name"""
    email: Mapped[str] = mapped_column(String)
    """Email address"""
    wydarzenia: Mapped[List[Wydarzenie]] \
        = relationship("Wydarzenie",
                       secondary=uczestnictwa,
                       back_populates="uczestnicy")
    """Events that the person participates in"""

    @validates("imie")
    def validate_imie(self, _, s):
        if s == "":
            raise ValueError("Imię powinno być niepuste.")
        return s

    @validates("email")
    def validate_email(self, _, s):
        if fullmatch(r"^\S+@[^@\s.]+\.[^@\s]+", s) is None:
            raise ValueError("Niepoprawny adres email.")
        return s


path = "baza/kalendarz.db"
"""Path of database file to be accessed or created.

Relative to directory `projekt`.
"""
dbpath = "sqlite:///" + path
echo = True
"""Parameter passed to SQLAlchemy's engine.

Set to `True` iff the program should display all of its SQL operations
on the database.
"""


def with_engine(f, *args, dispose=False):
    """Call function with a new SQLAlchemy engine.

    Positional arguments:
    f -- function that takes an SQLAlchemy engine as first argument.
    *args -- arguments with which to call f, except the engine.

    Keyword arguments:
    dispose -- set to `True` iff the engine should be disposed of after
    calling `f`. Useful when testing, if one wants to delete the database
    after performing some operations.
    """
    engine = create_engine(dbpath, echo=echo)
    f(engine, *args)
    if dispose:
        engine.dispose()


def utworz(engine):
    """Create database."""
    Base.metadata.create_all(engine)


def dodaj_wydarzenie(engine, nazwa, data_rozp, godzina_rozp,
                     data_zak, godzina_zak, opis):
    """Insert row with given field values into the table of events."""
    Session = sessionmaker(engine)
    with Session() as session:
        wyd = Wydarzenie(nazwa=nazwa,
                         data_rozp=data_rozp,
                         godzina_rozp=godzina_rozp,
                         data_zak=data_zak,
                         godzina_zak=godzina_zak,
                         opis=opis)
        session.add(wyd)
        session.commit()
        res = wyd.id
        session.close()
    return res


def usun_wydarzenie(engine, id_wydarzenia):
    """Delete the row with the given ID from the table of events."""
    Session = sessionmaker(engine)
    with Session() as session:
        wyd = session.get(Wydarzenie, id_wydarzenia)
        session.delete(wyd)
        session.commit()
        session.close()


def mod_wydarzenie(engine, id_wydarzenia, nazwa, data_rozp, godzina_rozp,
                   data_zak, godzina_zak, opis):
    """Modify the row with the given ID in the table of events.

    Pass `None` if a field is not to be modified.
    """
    Session = sessionmaker(engine)
    with Session() as session:
        wyd = session.get(Wydarzenie, id_wydarzenia)

        if nazwa is not None:
            wyd.nazwa = nazwa
        if data_rozp is not None:
            wyd.data_rozp = data_rozp
        if godzina_rozp is not None:
            wyd.godzina_rozp = godzina_rozp
        if data_zak is not None:
            wyd.data_zak = data_zak
        if godzina_zak is not None:
            wyd.godzina_zak = godzina_zak
        if opis is not None:
            wyd.opis = opis

        session.commit()
        session.close()


def dict_of_wydarzenie(wyd):
    """Return a dictionary describing an event.

    Fields:
    id, nazwa, data_rozp, godzina_rozp,
    data_zak, godzina_zak, opis -- see Wydarzenie.
    nazwa_miejsca -- name of location; `None` if no location is assigned.
    """
    return {"id": wyd.id, "nazwa": wyd.nazwa,
            "data_rozp": wyd.data_rozp,
            "data_zak": wyd.data_zak,
            "godzina_rozp": wyd.godzina_rozp,
            "godzina_zak": wyd.godzina_zak,
            "opis": wyd.opis,
            "nazwa_miejsca": (wyd.miejsce.nazwa if wyd.miejsce is not None
                              else None)}


def znajdz_wydarzenie(engine, nazwa):
    """Find events with the exact given name.

    Returns a list of dictionaries -- see dict_of_wydarzenie.
    """
    Session = sessionmaker(engine)
    with Session() as session:
        stmt = select(Wydarzenie).where(Wydarzenie.nazwa == nazwa)
        res = list(map(dict_of_wydarzenie, session.scalars(stmt)))
        session.close()
    return res


def dodaj_miejsce(engine, nazwa, adres):
    """Insert row with given field values into the table of locations."""
    Session = sessionmaker(engine)
    with Session() as session:
        msc = Miejsce(nazwa=nazwa, adres=adres)
        session.add(msc)
        session.commit()
        res = msc.id
        session.close()
    return res


def usun_miejsce(engine, id_miejsca):
    """Delete the row with the given ID from the table of locations."""
    Session = sessionmaker(engine)
    with Session() as session:
        msc = session.get(Miejsce, id_miejsca)
        session.delete(msc)
        session.commit()
        session.close()


def mod_miejsce(engine, id_miejsca, nazwa, adres):
    """Modify the row with the given ID in the table of locations.

    Pass `None` if a field is not to be modified.
    """
    Session = sessionmaker(engine)
    with Session() as session:
        msc = session.get(Miejsce, id_miejsca)
        if nazwa is not None:
            msc.nazwa = nazwa
        if adres is not None:
            msc.adres = adres
        session.commit()
        session.close()


def dict_of_miejsce(msc):
    """Return a dictionary describing a location.

    Fields:
    id, nazwa, adres -- see Miejsce.
    """
    return {"id": msc.id, "nazwa": msc.nazwa, "adres": msc.adres}


def znajdz_miejsce(engine, nazwa_miejsca):
    """Find locations with the exact given name.

    Returns a list of dictionaries -- see dict_of_miejsce.
    """
    Session = sessionmaker(engine)
    with Session() as session:
        stmt = select(Miejsce).where(Miejsce.nazwa == nazwa_miejsca)
        res = list(map(dict_of_miejsce, session.scalars(stmt)))
        session.close()
    return res


def dodaj_miejsce_do_wydarzenia(engine, id_miejsca, id_wydarzenia):
    """Assign a location to an event.

    Modifies the row of the event by updating miejsce_id and miejsce.

    Positional arguments:
    id_miejsca -- the location's ID.
    id_wydarzenia -- the event's ID.
    """
    Session = sessionmaker(engine)
    with Session() as session:
        msc = session.get(Miejsce, id_miejsca)
        wyd = session.get(Wydarzenie, id_wydarzenia)
        wyd.miejsce_id = id_miejsca
        wyd.miejsce = msc
        session.commit()
        session.close()


def usun_miejsce_z_wydarzenia(engine, id_wydarzenia):
    """Removes a location from an event.

    Updates the event row's miejsce and miejsce_id fields to null.

    Positional arguments:
    id_wydarzenia -- the event's ID.
    """
    Session = sessionmaker(engine)
    with Session() as session:
        wyd = session.get(Wydarzenie, id_wydarzenia)
        wyd.miejsce_id = None
        wyd.miejsce = None
        session.commit()
        session.close()


def znajdz_wydarzenia_w_miejscu(engine, nazwa_miejsca):
    """Return events that take place in locations with the given name.

    Returns a list of dictionaries -- see dict_of_wydarzenie.
    """
    Session = sessionmaker(engine)
    with Session() as session:
        stmt = ((select(Wydarzenie)
                 .join(Wydarzenie.miejsce))
                .where(Miejsce.nazwa == nazwa_miejsca))
        res = list(map(dict_of_wydarzenie, session.scalars(stmt)))
        session.close()
    return res


def dodaj_osoba(engine, imie, email):
    """Insert row with the given field values into the table of people."""
    Session = sessionmaker(engine)
    with Session() as session:
        osoba = Osoba(imie=imie, email=email)
        session.add(osoba)
        session.commit()
        res = osoba.id
        session.close()
    return res


def usun_osoba(engine, id_osoby):
    """Delete the row with the given ID from the table of peoble."""
    Session = sessionmaker(engine)
    with Session() as session:
        os = session.get(Osoba, id_osoby)
        session.delete(os)
        session.commit()
        session.close()


def mod_osoba(engine, id_osoby, imie, email):
    """Modify the row with the given ID in the table of people.

    Pass `None` if a field is not to be modified.
    """
    Session = sessionmaker(engine)
    with Session() as session:
        os = session.get(Osoba, id_osoby)
        if imie is not None:
            os.imie = imie
        if email is not None:
            os.email = email
        session.commit()
        session.close()


def dict_of_osoba(os):
    """Return a dictionary describing a person.

    Fields:
    id, imie, email -- see Osoba.
    """
    return {"id": os.id, "imie": os.imie, "email": os.email}


def znajdz_osoba(engine, imie):
    """Find people with the exact given name.

    Returns a list of dictionaries -- see dict_of_osoba.
    """
    Session = sessionmaker(engine)
    with Session() as session:
        oss = session.scalars(select(Osoba).where(Osoba.imie == imie))
        res = list(map(dict_of_osoba, oss))
        session.close()
    return res


def zapisz(engine, email, id_wydarzenia):
    """Sign a person up for an event.

    Inserts a row into the table of participations (see uczestnictwa).
    Modifies the person row's wydarzenia field,
    and the event row's uczestnicy field.
    Assumes that the people's email addresses are unique.

    Positional arguments:
    email -- email address used to query the table of people.
    id_wydarzenia -- the event's ID.
    """
    Session = sessionmaker(engine)
    with Session() as session:
        os = session.scalars(select(Osoba).where(Osoba.email == email)).one()
        wyd = session.get(Wydarzenie, id_wydarzenia)
        wyd.uczestnicy.append(os)
        session.commit()
        session.close()


def wypisz(engine, email, id_wydarzenia):
    """Remove a person from an event.

    Deletes a row from the table of participations (see uczestnictwa).
    Modifies the person row's wydarzenia field
    and the event row's uczestnicy field.
    Assumes that the people's email addresses are unique.

    Positional arguments:
    email -- email address used to query the table of people.
    id_wydarzenia -- the event's ID.
    """
    Session = sessionmaker(engine)
    with Session() as session:
        wyd = session.get(Wydarzenie, id_wydarzenia)
        os = session.scalars(select(Osoba).where(Osoba.email == email)).one()
        wyd.uczestnicy.remove(os)
        session.commit()
        session.close()


def znajdz_wydarzenia_osoby(engine, email):
    """Find events that a person participates in.

    Returns a list of dictionaries with fields id and nazwa.
    Assumes that the people's email addresses are unique.

    Positional arguments:
    email -- email address used to query the table of people.
    """
    Session = sessionmaker(engine)
    with Session() as session:
        stmt = ((select(Osoba.imie, Wydarzenie.id, Wydarzenie.nazwa)
                 .join(Osoba.wydarzenia))
                .where(Osoba.email == email))
        rows = session.execute(stmt)
        res = list(map(lambda row: {"id": row.id, "nazwa": row.nazwa},
                       rows))
        session.close()
    return res


def znajdz_zapisanych_na_wydarzenie(engine, id_wydarzenia):
    """Find the participants of an event.

    Returns a list of dictionaries -- see dict_of_osoba.

    Positional arguments:
    id_wydarzenia -- the event's ID.
    """
    Session = sessionmaker(engine)
    with Session() as session:
        wyd = session.get(Wydarzenie, id_wydarzenia)
        res = list(map(dict_of_osoba, wyd.uczestnicy))
        session.close()
    return res
