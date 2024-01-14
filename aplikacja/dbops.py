from __future__ import annotations 
from sqlalchemy.orm import DeclarativeBase, relationship, mapped_column, Mapped, validates, sessionmaker
from sqlalchemy import Table, Column, ForeignKey, String, Integer, create_engine, select
from typing import List, Optional
from re import fullmatch
import datetime

## Baza danych
class Base(DeclarativeBase):
    pass 

uczestnictwa = Table("osoba_wydarzenie",
                     Base.metadata,
                     Column("osoba_id", ForeignKey("osoby.id"), primary_key=True),
                     Column("wydarzenie_id", ForeignKey("wydarzenia.id"), primary_key=True))

class Wydarzenie(Base):
    __tablename__ = "wydarzenia"

    id : Mapped[int] = mapped_column(Integer, primary_key=True)
    nazwa : Mapped[str] = mapped_column(String)
    data_rozp : Mapped[str] = mapped_column(String)
    godzina_rozp : Mapped[str] = mapped_column(String)
    data_zak : Mapped[str] = mapped_column(String)
    godzina_zak : Mapped[str] = mapped_column(String)
    opis : Mapped[str] = mapped_column(String)
    miejsce_id : Mapped[Optional[int]] = mapped_column(ForeignKey("miejsca.id"))
    miejsce : Mapped[Optional["Miejsce"]] = relationship()
    uczestnicy : Mapped[List["Osoba"]] = relationship("Osoba", secondary=uczestnictwa, back_populates="wydarzenia")

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
            if datetime.datetime.fromisoformat(self.data_rozp + "T" + self.godzina_rozp) > datetime.datetime.fromisoformat(self.data_zak + "T" + s):
                raise ValueError("Data rozpoczęcia powinna być nie później od daty zakończenia.")
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
    __tablename__ = "miejsca"

    id : Mapped[int] = mapped_column(Integer, primary_key=True)
    nazwa : Mapped[str] = mapped_column(String)
    adres : Mapped[Optional[str]] = mapped_column(String)

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
    __tablename__ = "osoby"
    
    id : Mapped[int] = mapped_column(primary_key=True)
    imie  : Mapped[str] = mapped_column(String)
    email : Mapped[str] = mapped_column(String)
    wydarzenia : Mapped[List[Wydarzenie]] = relationship("Wydarzenie", secondary=uczestnictwa, back_populates="uczestnicy")
    
    @validates("imie")
    def validate_imie(self, _, s):
        if s == "":
            raise ValueError("Imię powinno być niepuste.")
        return s
    
    @validates("email")
    def validate_email(self, _, s):
        if fullmatch("^\S+@[^@\s.]+\.[^@\s]+", s) is None:
            raise ValueError("Niepoprawny adres email.")
        return s

## Operacje na bazie danych
# path = "..\\baza\\kalendarz.db"
path = "baza/kalendarz.db"
dbpath = "sqlite:///" + path
echo = True 

def with_engine(f, *args, dispose=False):
    engine = create_engine(dbpath, echo=echo)
    f(engine, *args)
    if dispose:
        engine.dispose()

def utworz(engine):
    Base.metadata.create_all(engine)

def dodaj_wydarzenie(engine, nazwa, data_rozp, godzina_rozp, data_zak, godzina_zak, opis):
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
    Session = sessionmaker(engine)
    with Session() as session:
        wyd = session.get(Wydarzenie, id_wydarzenia)
        session.delete(wyd)
        session.commit()
        session.close() 

def mod_wydarzenie(engine, id_wydarzenia, nazwa, data_rozp, godzina_rozp, data_zak, godzina_zak, opis):
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
    return {"id" : wyd.id, "nazwa" : wyd.nazwa, 
            "data_rozp" : wyd.data_rozp, "data_zak" : wyd.data_zak,
            "godzina_rozp" : wyd.godzina_rozp, "godzina_zak" : wyd.godzina_zak,
            "opis" : wyd.opis, 
            "nazwa_miejsca" : (wyd.miejsce.nazwa if wyd.miejsce is not None else None)}

def znajdz_wydarzenie(engine, nazwa):
    Session = sessionmaker(engine)
    with Session() as session:
        stmt = select(Wydarzenie).where(Wydarzenie.nazwa == nazwa)
        res = list(map(dict_of_wydarzenie, session.scalars(stmt)))
        session.close()
    return res 

def dodaj_miejsce(engine, nazwa, adres):
    Session = sessionmaker(engine)
    with Session() as session:
        msc = Miejsce(nazwa=nazwa, adres=adres)
        session.add(msc)
        session.commit()
        res = msc.id 
        session.close()
    return res 

def usun_miejsce(engine, id_miejsca):
    Session = sessionmaker(engine)
    with Session() as session:
        msc = session.get(Miejsce, id_miejsca)
        session.delete(msc)
        session.commit()
        session.close() 

def mod_miejsce(engine, id_miejsca, nazwa, adres):
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
    return {"id" : msc.id, "nazwa" : msc.nazwa, "adres" : msc.adres}

def znajdz_miejsce(engine, nazwa_miejsca):
    Session = sessionmaker(engine)
    with Session() as session:
        stmt = select(Miejsce).where(Miejsce.nazwa == nazwa_miejsca)
        res = list(map(dict_of_miejsce, session.scalars(stmt)))
        session.close()
    return res 

def dodaj_miejsce_do_wydarzenia(engine, id_miejsca, id_wydarzenia):
    Session = sessionmaker(engine)
    with Session() as session:
        msc = session.get(Miejsce, id_miejsca)
        wyd = session.get(Wydarzenie, id_wydarzenia)
        wyd.miejsce_id = id_miejsca 
        wyd.miejsca = msc 
        session.commit()
        session.close()

def usun_miejsce_z_wydarzenia(engine, id_wydarzenia):
    Session = sessionmaker(engine)
    with Session() as session:
        wyd = session.get(Wydarzenie, id_wydarzenia)
        wyd.miejsce_id = None 
        wyd.miejsce = None 
        session.commit()
        session.close()

def znajdz_wydarzenia_w_miejscu(engine, nazwa_miejsca):
    Session = sessionmaker(engine)
    with Session() as session:
        stmt = select(Wydarzenie).join(Wydarzenie.miejsce).where(Miejsce.nazwa == nazwa_miejsca)
        res = list(map(dict_of_wydarzenie, session.scalars(stmt)))
        session.close()
    return res 

def dodaj_osoba(engine, imie, email):
    Session = sessionmaker(engine)
    with Session() as session:
        osoba = Osoba(imie=imie, email=email)
        session.add(osoba)
        session.commit()
        res = osoba.id 
        session.close()
    return res 

def usun_osoba(engine, id_osoby):
    Session = sessionmaker(engine)
    with Session() as session:
        os = session.get(Osoba, id_osoby)
        session.delete(os)
        session.commit()
        session.close()

def mod_osoba(engine, id_osoby, imie, email):
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
    return {"id" : os.id, "imie" : os.imie, "email" : os.email}

def znajdz_osoba(engine, imie):
    Session = sessionmaker(engine)
    with Session() as session:
        oss = session.scalars(select(Osoba).where(Osoba.imie == imie))
        res = list(map(dict_of_osoba, oss))
        session.close()
    return res

def zapisz(engine, email, id_wydarzenia):
    Session = sessionmaker(engine)
    with Session() as session:
        os = session.scalars(select(Osoba).where(Osoba.email == email)).one()
        wyd = session.get(Wydarzenie, id_wydarzenia)
        wyd.uczestnicy.append(os)
        session.commit()
        session.close()

def wypisz(engine, email, id_wydarzenia):
    Session = sessionmaker(engine)
    with Session() as session:
        wyd = session.get(Wydarzenie, id_wydarzenia)
        os = session.scalars(select(Osoba).where(Osoba.email == email)).one()
        wyd.uczestnicy.remove(os)
        session.commit()
        session.close()

def znajdz_wydarzenia_osoby(engine, email):
    Session = sessionmaker(engine)
    with Session() as session:
        stmt = select(Osoba.imie, Wydarzenie.id, Wydarzenie.nazwa).join(Osoba.wydarzenia).where(Osoba.email == email)
        rows = session.execute(stmt)
        res = list(map(lambda row: {"id" : row.id, "nazwa" : row.nazwa}, rows))
        session.close()
    return res 

def znajdz_zapisanych_na_wydarzenie(engine, id_wydarzenia):
    Session = sessionmaker(engine)
    with Session() as session:
        wyd = session.get(Wydarzenie, id_wydarzenia)
        res = list(map(dict_of_osoba, wyd.uczestnicy))
        session.close()
    return res 
