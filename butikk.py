import sqlite3
import random
from datetime import datetime
import os

filename = 'penger.txt'
if os.path.exists(filename):
    with open(filename, 'r') as file:
        penger = int(file.read())
else:
    penger = 10000
    with open(filename, 'w') as file:
        file.write(str(penger))

databasekobling = sqlite3.connect("butikk.db")
c = databasekobling.cursor() 

c.execute("""
    CREATE TABLE IF NOT EXISTS inventar(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        navn TEXT NOT NULL,
        pris REAL NOT NULL,
        antall INTEGER NOT NULL           
    )    
""")



bok_priser = {}
def legg_til_vare():
    while True:
        bok = input("Skriv EXIT for å gå tilbake til ansatt menyen\nSkriv navnet på boka: ")
        if bok == "EXIT":
            return False
        else:
            c.execute("SELECT id, antall FROM inventar WHERE navn = ?", (bok,))
            resultat = c.fetchall()
            if resultat:
                rad = resultat[0]
                iid = rad[0]
                antall = rad[1]
                pris = bok_priser[bok]
                antall_tillegg = int(input("hvor mange skal du legge til? - "))
                totalt = antall_tillegg * pris

                # Sjekk om du har nok penger før du bekrefter kjøpet
                with open("penger.txt", "r") as f:
                    tidligere_penger = int(f.read())
                if tidligere_penger < totalt:
                    print(f"Du har ikke råd til å kjøpe {antall_tillegg} av {bok}. Du har {tidligere_penger}kr, men det koster {totalt}kr.")
                    continue  # Gå tilbake og prøv igjen eller avbryt

                nytt_aantall = antall + antall_tillegg
                c.execute("UPDATE inventar SET antall = ? WHERE id = ?", (nytt_aantall, iid))
                print(f"antall {bok} er nå {nytt_aantall}\n")
                ny_penger = tidligere_penger - totalt
                with open("penger.txt", "w") as f:
                    f.write(f"{ny_penger}")
                break
            else:
                pris = random.randint(250, 450)
                bok_priser[bok] = pris 
                print(f"En {bok} koster {pris}")
                antall = int(input("Skriv antall ønsket kopier:  "))
                totalt = antall * pris

                # Sjekk om du har råd før du bekrefter
                with open("penger.txt", "r") as f:
                    tidligere_penger = int(f.read())
                if tidligere_penger < totalt:
                    print(f"Du har ikke råd til å kjøpe {antall} av {bok}. Du har {tidligere_penger}kr, men det koster {totalt}kr.")
                    login()

                print(f"totalt koster det {totalt}")
                konfirmasjon = input("bekreft bestilling (ja/nei) - ")
                if konfirmasjon == "ja":
                    print(f"bestilling bekreftet for {antall} utgaver av {bok} som kostet totalt {totalt}\n")
                    c.execute("INSERT INTO inventar (navn, pris, antall) VALUES (?,?,?)",(bok,pris,antall))
                    databasekobling.commit()
                    ny_penger = tidligere_penger - totalt
                    with open("penger.txt", "w") as f:
                        f.write(f"{ny_penger}")
                    break
                else:
                    break

def vis_lager():
    c.execute("SELECT * FROM inventar")
    kolonne_antall = c.fetchall()
    for vare in kolonne_antall:
        print(f"ID: {vare[0]}, Navn: {vare[1]}, Pris: {vare[2]}, Antall: {vare[3]}")
    with open("penger.txt", "r") as f:
        print("\n")
        print(f.read())

def salg(): #funksjon for slag
    valgte_varer = [] #lager en liste for varene til å lagres for senere
    c.execute("SELECT * FROM inventar") #henter databasen
    kolonne_antall = c.fetchall() #bruker infoen til databasen
    for vare in kolonne_antall: #bruker linjen før til å lage en løkke som kjører så mange ganger som det er varer
        print(f"ID: {vare[0]}, Navn: {vare[1]}, Pris: {vare[2]}") #skriver en og en vare
        valgte_varer.append(vare) #legger til varen i en liste for senere

    vare_id_input = input("\nSkriv inn ID på varen du skal Kjøpe: ") #brukeren skriver id på varen de ønsker
    valgt_vare = None #lager en variabel for senere bruk
    if vare_id_input.isdigit(): #sjekker om inputen er en digit hvis ikke er det login
        vare_id = int(vare_id_input) #gjør det om til en integer
        for i in valgte_varer: #går gjennom antall varer igjen
            if i[0] == vare_id: #sjekker om vare_id stemmer 
                valgt_vare = i #setter valgt vare til varen som trengs
                break
        if valgt_vare is None:
            print("Fant ingen vare med dette ID.")
            salg()
    elif vare_id_input == "LOGIN": #mulighet for ansatte å logge inn på lager og bestilling
        login()
    
    print(f"Du har valgt: {valgt_vare[1]}, Pris per enhet: {valgt_vare[2]}kr, På lager: {valgt_vare[3]}") #viser hva som ble valgt

    try:    #spør hvor mange kopier og må ha et nummer
        antall_kopier = int(input("Hvor mange kopier? "))
    except ValueError:
        print("Ugyldig antall. Vennligst prøv igjen.")
        return
    
    if antall_kopier > valgt_vare[3]: #sjekker at det er nok kopier og at 0 ikke skrives
        print(f"Beklager det er kun {valgt_vare[3]} stykker på lager.\n\n")
        salg()
    elif antall_kopier <= 0:
        print("Vennligst skriv et antall større enn 0.\n\n")
        salg()

    nytt_antall = valgt_vare[3] - antall_kopier
    total_pris = antall_kopier * vare[2]
    c.execute("UPDATE inventar SET antall = ? WHERE id = ?", (nytt_antall, vare_id))
    databasekobling.commit()
    print(f"\nREGNING \n{antall_kopier} stk av {valgt_vare[1]} for {total_pris}kr\n\n")

    with open("penger.txt", "r") as f:
        tidligere_penger = int(f.read())
    ny_penger = tidligere_penger + total_pris
    with open("penger.txt", "w") as f:
        f.write(f"{ny_penger}")

def login():
    passord = "bok123"
    konfirmasjon = input("Hva er passordet? - ")
    if konfirmasjon == passord:
        while True:
            valg = input("\n\npress ENTER for å legge til vare \nskriv LAGER for å åpne lageret \nskriv LOGOUT for å returnere til hovedsiden\n\n")
            if valg == "":
                legg_til_vare()
            elif valg == "LAGER":
                vis_lager()
            elif valg == "LOGOUT":
                print("\n" * 100)
                salg()
                break
    else:
        print("Du har ikke tilgang til denne siden")
        pass

while True:
    salg()

databasekobling.commit()
databasekobling.close()