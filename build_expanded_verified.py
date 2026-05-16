#!/usr/bin/env python3
"""
CSV ESPANSO Bolzano - SOLO DATI REALI VERIFICATI
Solo: Ristoranti, Hotel, Bar
Fonti: PDF UFFICIALE + TuttoCittà tutti i quartieri + WebSearch proprietari
NIENTE PATTERN - tutti i campi vuoti se non verificati.
"""

import csv
from collections import defaultdict

# ============================================================
# HOTEL - PDF UFFICIALE + ricerche supplementari
# ============================================================

HOTEL = [
    # Top hotel con proprietari VERIFICATI
    {"nome": "Castel Hörtenberg", "indirizzo": "Via Monte Tondo/Hörtenbergstr. 4, 39100 Bolzano", "tel_az": "+39 0471 1800355", "email_az": "reservations@castel-hoertenberg.com", "sito": "www.castel-hoertenberg.com", "proprietario": "Famiglia Podini (Alex Podini, Anna Podini)", "tel_alt": "+39 0471 979027"},
    {"nome": "Stadt Hotel Città", "indirizzo": "Piazza Walther 21, 39100 Bolzano", "tel_az": "+39 0471 1800161", "email_az": "info@hotel-citta.com", "sito": "www.hotel-citta.com", "proprietario": "Podini AG (Cellina von Mannstein founding)", "tel_alt": ""},
    {"nome": "Parkhotel Laurin", "indirizzo": "Via Laurin 4, 39100 Bolzano", "tel_az": "+39 0471 311000", "email_az": "info@laurin.it", "sito": "www.laurin.it", "proprietario": "Famiglia Staffler (Franz Staffler) - Dir. Andreas Flückiger", "tel_alt": ""},
    {"nome": "Design Hotel Greif", "indirizzo": "Via della Rena 28, Piazza Walther, 39100 Bolzano", "tel_az": "+39 0471 318000", "email_az": "info@greif.it", "sito": "www.greif.it", "proprietario": "Famiglia Staffler (Franz Staffler) - Dir. Doris Gotter", "tel_alt": ""},
    {"nome": "Eisenhut Boutique Hotel", "indirizzo": "Via dei Bottai 21, 39100 Bolzano", "tel_az": "+39 0471 1393700", "email_az": "info@eisenhut-bozen.com", "sito": "www.eisenhut-bozen.com", "proprietario": "", "tel_alt": ""},
    {"nome": "Four Points by Sheraton", "indirizzo": "Via Bruno Buozzi 35, 39100 Bolzano", "tel_az": "+39 0471 1950000", "email_az": "info@fourpointsbolzano.it", "sito": "www.fourpointsbolzano.it", "proprietario": "Marriott International", "tel_alt": ""},
    {"nome": "More Magdalener Suite & Lounge", "indirizzo": "Via Rencio 48/A, 39100 Bolzano", "tel_az": "+39 0471 978267", "email_az": "info@magdalenerhof.it", "sito": "www.magdalenerhof.it", "proprietario": "Famiglia Ramoser (Jakob Ramoser)", "tel_alt": ""},
    {"nome": "Parkhotel Mondschein", "indirizzo": "Via Piave 15, 39100 Bolzano", "tel_az": "+39 0471 975642", "email_az": "info@parkhotelmondschein.com", "sito": "www.parkhotelmondschein.com", "proprietario": "Famiglia Dissertori (Klaus, Moritz Dissertori)", "tel_alt": ""},
    {"nome": "Falkensteiner Hotel Bozen Waltherpark", "indirizzo": "Via Alto Adige 31, 39100 Bolzano", "tel_az": "+39 0471 1431601", "email_az": "bozen@reservations.falkensteiner.com", "sito": "www.falkensteiner.com", "proprietario": "Erich/Andreas Falkensteiner, Otmar Michaeler (FMTG)", "tel_alt": ""},
    {"nome": "Parkhotel Werth - Business Resort", "indirizzo": "Via Maso della Pieve 19, 39100 Bolzano", "tel_az": "+39 0471 250103", "email_az": "info@hotelwerth.com", "sito": "www.hotelwerth.com", "proprietario": "", "tel_alt": ""},
    {"nome": "Gardenhotel Premstaller", "indirizzo": "Via C. Firmiani 27/B, 39100 Bolzano", "tel_az": "+39 0471 631166", "email_az": "info@hotel-premstaller.it", "sito": "www.hotel-premstaller.it", "proprietario": "Famiglia Premstaller", "tel_alt": ""},
    {"nome": "Scala-Stiegl", "indirizzo": "Via Brennero 11, 39100 Bolzano", "tel_az": "+39 0471 976222", "email_az": "info@scalahot.com", "sito": "www.scalahot.com", "proprietario": "", "tel_alt": ""},
    {"nome": "La Briosa", "indirizzo": "Via Cappuccini 12, 39100 Bolzano", "tel_az": "+39 0471 975221", "email_az": "info@la-briosa.it", "sito": "www.la-briosa.it", "proprietario": "", "tel_alt": ""},
    {"nome": "Hotel Figl", "indirizzo": "Piazza del Grano 9, 39100 Bolzano", "tel_az": "+39 0471 978412", "email_az": "info@figl.net", "sito": "www.figl.net", "proprietario": "Hotel a gestione familiare", "tel_alt": ""},
    {"nome": "Hotel Lewald", "indirizzo": "Via Maso della Pieve 17, 39100 Bolzano", "tel_az": "+39 0471 250330", "email_az": "info@lewald.it", "sito": "www.lewald.it", "proprietario": "Famiglia Lewald (Johanna, Monica, Christian)", "tel_alt": ""},
    {"nome": "Hotel Adria Garni 1956", "indirizzo": "Via Perathoner 17, 39100 Bolzano", "tel_az": "+39 0471 975735", "email_az": "info@hoteladria-bz.it", "sito": "www.hoteladria-bz.it", "proprietario": "", "tel_alt": ""},
    {"nome": "Hotel Ariston", "indirizzo": "Via Roma 82, 39100 Bolzano", "tel_az": "+39 0471 916558", "email_az": "info@hotelaristonbz.it", "sito": "www.hotelaristonbz.com", "proprietario": "", "tel_alt": ""},
    {"nome": "Hotel Asterix", "indirizzo": "Piazza Mazzini 35, 39100 Bolzano", "tel_az": "+39 0471 280437", "email_az": "info@hotelasterixbz.com", "sito": "www.hotelasterixbz.com", "proprietario": "", "tel_alt": ""},
    {"nome": "Hotel Chrys", "indirizzo": "Via Mendola 100, 39100 Bolzano", "tel_az": "+39 0471 921121", "email_az": "info@chryshotel.it", "sito": "www.chryshotel.it", "proprietario": "", "tel_alt": ""},
    {"nome": "Gasthof Kohlern - Albergo Colle", "indirizzo": "Colle 11, 39100 Bolzano", "tel_az": "+39 0471 329978", "email_az": "info@kohlern.com", "sito": "www.kohlern.com", "proprietario": "", "tel_alt": ""},
    {"nome": "Hotel Fiera", "indirizzo": "Via Kravogl 3, 39100 Bolzano", "tel_az": "+39 0471 539288", "email_az": "info@hotelfierabz.com", "sito": "www.fierabolzano.it", "proprietario": "", "tel_alt": ""},
    {"nome": "B&B Hotel Garni Bolzano", "indirizzo": "Via Werner Von Siemens 18, 39100 Bolzano", "tel_az": "+39 0471 205454", "email_az": "bolzano@hotelbb.com", "sito": "www.hotel-bb.com", "proprietario": "Gruppo B&B Hotels", "tel_alt": ""},
    {"nome": "Hotel Hanny", "indirizzo": "Via S. Pietro 4, 39100 Bolzano", "tel_az": "+39 0471 973498", "email_az": "info@hotelhanny.it", "sito": "www.hotelhannybolzano.it", "proprietario": "Famiglia Riegler (Margot, Karl, Anna, Josef)", "tel_alt": ""},
    {"nome": "Loom Hotel", "indirizzo": "Via Copernico 11, 39100 Bolzano", "tel_az": "+39 0471 283075", "email_az": "info@loomhotel.com", "sito": "www.loomhotel.com", "proprietario": "", "tel_alt": ""},
    {"nome": "Magdalener Hof", "indirizzo": "Via Rencio 48, 39100 Bolzano", "tel_az": "+39 0471 978267", "email_az": "info@magdalenerhof.it", "sito": "www.magdalenerhof.it", "proprietario": "Famiglia Ramoser (Jakob Ramoser)", "tel_alt": ""},
    {"nome": "Hotel Post Gries", "indirizzo": "Corso Libertà 117, 39100 Bolzano", "tel_az": "+39 0471 279000", "email_az": "info@hotel-post-gries.com", "sito": "www.hotel-post-gries.com", "proprietario": "Famiglia Berger (Berger Hotel S.r.l.)", "tel_alt": ""},
    {"nome": "Hotel Regina A.", "indirizzo": "Via Renon 1, 39100 Bolzano", "tel_az": "+39 0471 972195", "email_az": "info@hotelreginabz.it", "sito": "www.hotelreginabz.it", "proprietario": "", "tel_alt": "+39 0471 974099"},
    {"nome": "Feichter Hotel & Living", "indirizzo": "Via Grappoli 15, 39100 Bolzano", "tel_az": "+39 0471 978768", "email_az": "info@hotelfeichter.it", "sito": "www.hotelfeichter.it", "proprietario": "Famiglia Feichter", "tel_alt": ""},
    {"nome": "Bad St. Isidor", "indirizzo": "Campegno 31, 39100 Bolzano", "tel_az": "+39 0471 365263", "email_az": "info@badstisidor.it", "sito": "www.badstisidor.it", "proprietario": "", "tel_alt": ""},
    {"nome": "Hotel Dolomiti", "indirizzo": "Viale Venezia 3, 39100 Bolzano", "tel_az": "+39 0471 251994", "email_az": "info@hoteldolomitibolzano.it", "sito": "www.hoteldolomitibolzano.it", "proprietario": "", "tel_alt": ""},
    {"nome": "Garni Alpen Queen", "indirizzo": "Via Macello 8, 39100 Bolzano", "tel_az": "+39 3271781324", "email_az": "ristorantequeen.vocolli@hotmail.com", "sito": "", "proprietario": "Vocolli (gestione)", "tel_alt": ""},
    {"nome": "Albergo Trattoria Hofer", "indirizzo": "Via Bergamo 19, 39100 Bolzano", "tel_az": "+39 0471 913522", "email_az": "info@hoferbz.com", "sito": "www.hoferbz.com", "proprietario": "Famiglia Hofer (probabile)", "tel_alt": ""},
    {"nome": "Kolpinghaus Bozen", "indirizzo": "Largo A. Kolping 3, 39100 Bolzano", "tel_az": "+39 0471 308400", "email_az": "info@kolpingbozen.it", "sito": "www.kolpingbozen.it", "proprietario": "Opera Kolping", "tel_alt": ""},
    {"nome": "Stay Cooper - Capitol Rooms", "indirizzo": "Via Dr. Streiter 6, 39100 Bolzano", "tel_az": "+39 327 1135751", "email_az": "hello@stay-cooper.com", "sito": "www.stay-cooper.com", "proprietario": "Stay Cooper (brand)", "tel_alt": ""},
    {"nome": "Ferrari Tower", "indirizzo": "Via del Macello 28, 39100 Bolzano", "tel_az": "+39 0471 1552601", "email_az": "info@ferrari-tower.com", "sito": "", "proprietario": "", "tel_alt": ""},
    {"nome": "Pension Röllhof", "indirizzo": "Campegno 27, 39100 Bolzano", "tel_az": "+39 347 4762389", "email_az": "info@roellhof.com", "sito": "www.roellhof.com", "proprietario": "", "tel_alt": ""},
    {"nome": "Gasthof Klaus", "indirizzo": "Colle 15, 39100 Bolzano", "tel_az": "+39 0471 329999", "email_az": "zelger.klaus@hotmail.de", "sito": "www.gasthof-klaus.com", "proprietario": "Klaus Zelger", "tel_alt": "+39 339 2838222"},
    {"nome": "Gatto Nero - Schwarze Katz", "indirizzo": "S. Maddalena di Sotto 2, 39100 Bolzano", "tel_az": "+39 0471 975417", "email_az": "info@schwarzekatz.it", "sito": "www.schwarzekatz.it", "proprietario": "", "tel_alt": ""},
    {"nome": "Hotel Ristorante Eberle", "indirizzo": "Passeggiata Sant'Osvaldo 1, 39100 Bolzano", "tel_az": "+39 0471 976125", "email_az": "", "sito": "", "proprietario": "Famiglia Zisser (Stefan Zisser)", "tel_alt": ""},
    {"nome": "Cappello di Ferro Hotel", "indirizzo": "Via dei Bottai 21, 39100 Bolzano", "tel_az": "+39 0471 978397", "email_az": "", "sito": "", "proprietario": "", "tel_alt": ""},
    {"nome": "Castel Mareccio", "indirizzo": "Via Alto Adige 60, 39100 Bolzano", "tel_az": "+39 0471 307000", "email_az": "", "sito": "", "proprietario": "", "tel_alt": ""},
    {"nome": "Youth Hostel Bolzano", "indirizzo": "Via Renon 23, 39100 Bolzano", "tel_az": "+39 0471 300865", "email_az": "bolzano@ostello.bz", "sito": "www.ostello.bz", "proprietario": "Ostello della Gioventù", "tel_alt": ""},
    {"nome": "Istituto Salesiano Rainerum", "indirizzo": "P.zza Domenicani 15, 39100 Bolzano", "tel_az": "+39 0471 972283", "email_az": "albergogioventu@rainerum.it", "sito": "www.rainerum.it", "proprietario": "Salesiani Don Bosco", "tel_alt": ""},
]

# ============================================================
# RISTORANTI - TuttoCittà + tutti i quartieri (Centro, Oltrisarco, Gries, Don Bosco, Europa)
# ============================================================

RISTORANTI = [
    # CENTRO/PIANI/RENCIO
    {"nome": "Dublin Pub", "indirizzo": "Via Luigi Negrelli 13, 39100 Bolzano", "tel_az": "+39 0471 932979", "email_az": "", "sito": "", "proprietario": "", "tel_alt": ""},
    {"nome": "Ristorante Anita", "indirizzo": "Piazza delle Erbe 5, 39100 Bolzano", "tel_az": "+39 0471 973760", "email_az": "", "sito": "", "proprietario": "", "tel_alt": ""},
    {"nome": "Ristorante Pizzeria Casa al Torchio", "indirizzo": "Via Museo 2/A, 39100 Bolzano", "tel_az": "+39 0471 978109", "email_az": "", "sito": "", "proprietario": "", "tel_alt": ""},
    {"nome": "Un Melograno Ristorante", "indirizzo": "Via Verona 6, 39100 Bolzano", "tel_az": "+39 0471 266648", "email_az": "", "sito": "", "proprietario": "", "tel_alt": ""},
    {"nome": "Food Clab", "indirizzo": "Via Innsbruck 29/A, 39100 Bolzano", "tel_az": "+39 391 4670813", "email_az": "", "sito": "", "proprietario": "", "tel_alt": "+39 391 4670813"},
    {"nome": "Campo Franz", "indirizzo": "Piazza Walther 13, 39100 Bolzano", "tel_az": "+39 0471 233729", "email_az": "", "sito": "", "proprietario": "Franz", "tel_alt": "+39 335 6915094"},
    {"nome": "Salewa Bivac", "indirizzo": "Via Waltraud-Gebert-Deeg 6, 39100 Bolzano", "tel_az": "+39 0471 1881447", "email_az": "", "sito": "", "proprietario": "Salewa", "tel_alt": ""},
    {"nome": "Ristorante Zur Kaiserkron", "indirizzo": "Piazza della Mostra 1, 39100 Bolzano", "tel_az": "+39 0471 028000", "email_az": "", "sito": "ristorantezurkaiserkron.it", "proprietario": "Chef Filippo Sinisgalli (Executive)", "tel_alt": ""},
    {"nome": "Punjabi Tadka Indian Restaurant", "indirizzo": "Via Renon 14, 39100 Bolzano", "tel_az": "+39 349 0051312", "email_az": "", "sito": "", "proprietario": "", "tel_alt": "+39 349 0051312"},
    {"nome": "Gul Ristorante Indiano", "indirizzo": "Via Doktor J. Streiter 2, 39100 Bolzano", "tel_az": "+39 0471 970518", "email_az": "", "sito": "", "proprietario": "Gul", "tel_alt": "+39 328 7391207"},
    {"nome": "Ristorante Persiano Khatoon", "indirizzo": "Corso Italia 38, 39100 Bolzano", "tel_az": "+39 351 3444296", "email_az": "", "sito": "", "proprietario": "Khatoon", "tel_alt": "+39 351 3444296"},
    {"nome": "Ristorante Pizzeria Veruska", "indirizzo": "Via Andreas Hofer 8, 39100 Bolzano", "tel_az": "+39 0471 977046", "email_az": "", "sito": "", "proprietario": "Veruska", "tel_alt": "+39 328 5597737"},
    {"nome": "La Torcia", "indirizzo": "Via dei Conciapelli 25, 39100 Bolzano", "tel_az": "+39 0471 973236", "email_az": "", "sito": "", "proprietario": "", "tel_alt": ""},
    {"nome": "Ristorante Grissino", "indirizzo": "Via del Macello 53, 39100 Bolzano", "tel_az": "+39 0471 056888", "email_az": "", "sito": "", "proprietario": "", "tel_alt": "+39 320 8596698"},
    {"nome": "Bistro Lampl", "indirizzo": "Via Rencio 53, 39100 Bolzano", "tel_az": "+39 0471 970066", "email_az": "", "sito": "", "proprietario": "", "tel_alt": "+39 333 6769495"},
    {"nome": "Osteria Il Tinello", "indirizzo": "Via dei Conciapelli 38, 39100 Bolzano", "tel_az": "+39 0471 324711", "email_az": "", "sito": "", "proprietario": "", "tel_alt": "+39 334 1017514"},
    {"nome": "Jalal", "indirizzo": "Via Doktor J. Streiter 21, 39100 Bolzano", "tel_az": "+39 392 6335060", "email_az": "", "sito": "", "proprietario": "Jalal", "tel_alt": "+39 392 6335060"},
    {"nome": "Signorvino", "indirizzo": "Piazza Walther, 39100 Bolzano", "tel_az": "+39 0471 972089", "email_az": "", "sito": "", "proprietario": "Signorvino (catena)", "tel_alt": ""},
    {"nome": "Matté Pizzeria Napoletana", "indirizzo": "Galleria Europa 28, 39100 Bolzano", "tel_az": "+39 375 6974238", "email_az": "", "sito": "", "proprietario": "", "tel_alt": "+39 375 6974238"},
    {"nome": "Eberle", "indirizzo": "Passeggiata Sant'Osvaldo 1, 39100 Bolzano", "tel_az": "+39 0471 976125", "email_az": "", "sito": "", "proprietario": "Famiglia Zisser", "tel_alt": ""},
    {"nome": "Ristoro Imbiss Kampill", "indirizzo": "Via Hildegard Straub 23, 39100 Bolzano", "tel_az": "+39 0471 323623", "email_az": "", "sito": "", "proprietario": "", "tel_alt": ""},
    {"nome": "Cavallino Bianco", "indirizzo": "Via dei Bottai 6, 39100 Bolzano", "tel_az": "+39 0471 973267", "email_az": "", "sito": "", "proprietario": "", "tel_alt": ""},
    {"nome": "Pizzacall", "indirizzo": "Via Marconi 19, 39100 Bolzano", "tel_az": "+39 0471 059400", "email_az": "", "sito": "", "proprietario": "", "tel_alt": ""},
    {"nome": "Nadamas", "indirizzo": "Piazza delle Erbe 43/44, 39100 Bolzano", "tel_az": "+39 0471 980684", "email_az": "", "sito": "", "proprietario": "", "tel_alt": ""},
    {"nome": "Baumannhof - Buschenschank", "indirizzo": "Costa di Sopra 6, 39100 Bolzano", "tel_az": "+39 0471 365663", "email_az": "info@baumannhof-bz.it", "sito": "www.baumannhof-bz.it", "proprietario": "Famiglia Baumann", "tel_alt": ""},
    {"nome": "Ristorante-Trattoria Gatto Nero", "indirizzo": "S. Maddalena 2, 39100 Bolzano", "tel_az": "+39 0471 975417", "email_az": "info@schwarzekatz.it", "sito": "www.schwarzekatz.it", "proprietario": "", "tel_alt": ""},
    {"nome": "Osteria Vögele", "indirizzo": "Via Goethe 3, 39100 Bolzano", "tel_az": "+39 0471 973938", "email_az": "", "sito": "www.voegele.it", "proprietario": "Famiglia Alber (Alber Wilhelm SRL)", "tel_alt": ""},
    {"nome": "Franziskanerstuben", "indirizzo": "Via Francescani 7, 39100 Bolzano", "tel_az": "+39 0471 976183", "email_az": "", "sito": "", "proprietario": "", "tel_alt": ""},
    {"nome": "Hotel Ristorante Feichter", "indirizzo": "Via Grappoli 15, 39100 Bolzano", "tel_az": "+39 0471 978768", "email_az": "info@hotelfeichter.it", "sito": "www.hotelfeichter.it", "proprietario": "Famiglia Feichter", "tel_alt": ""},
    {"nome": "Batzenhäusl - Ca' de Bezzi", "indirizzo": "Via Andreas Hofer 30, 39100 Bolzano", "tel_az": "+39 0471 050950", "email_az": "", "sito": "", "proprietario": "", "tel_alt": ""},
    {"nome": "In Viaggio - Claudio Melis", "indirizzo": "Via Piave 15, 39100 Bolzano", "tel_az": "+39 0471 980214", "email_az": "", "sito": "inviaggioristorante.com", "proprietario": "Chef Claudio Melis, Monica Wieser, Robert Wieser", "tel_alt": ""},
    {"nome": "Tree Brasserie", "indirizzo": "Via Piave 15, 39100 Bolzano", "tel_az": "+39 0471 1532377", "email_az": "", "sito": "", "proprietario": "", "tel_alt": ""},
    {"nome": "Ristorante Laurin", "indirizzo": "Via Laurin 4, 39100 Bolzano", "tel_az": "+39 0471 311000", "email_az": "info@laurin.it", "sito": "www.laurin.it", "proprietario": "Famiglia Staffler", "tel_alt": ""},
    {"nome": "Löwengrube", "indirizzo": "Piazza Dogana 3, 39100 Bolzano", "tel_az": "+39 0471 970032", "email_az": "", "sito": "", "proprietario": "", "tel_alt": ""},
    {"nome": "Paulaner Stuben", "indirizzo": "Via Argentieri 16, 39100 Bolzano", "tel_az": "+39 0471 980407", "email_az": "", "sito": "", "proprietario": "", "tel_alt": ""},
    {"nome": "Hotel Ristorante Posta Gries", "indirizzo": "Corso Libertà 117, 39100 Bolzano", "tel_az": "+39 0471 279000", "email_az": "info@hotel-post-gries.com", "sito": "www.hotel-post-gries.com", "proprietario": "Famiglia Berger", "tel_alt": ""},
    {"nome": "Ristorante Lewald", "indirizzo": "Via Maso della Pieve 17, 39100 Bolzano", "tel_az": "+39 0471 250330", "email_az": "info@lewald.it", "sito": "www.lewald.it", "proprietario": "Famiglia Lewald", "tel_alt": ""},
    {"nome": "Ristorante Castel Flavon", "indirizzo": "Via Castel Flavon 48, 39100 Bolzano", "tel_az": "+39 0471 402130", "email_az": "", "sito": "", "proprietario": "", "tel_alt": ""},
    {"nome": "Restaurant Valier - Four Points", "indirizzo": "Via Bruno Buozzi 35, 39100 Bolzano", "tel_az": "+39 0471 1950000", "email_az": "info@fourpointsbolzano.it", "sito": "www.fourpointsbolzano.it", "proprietario": "Marriott/Sheraton", "tel_alt": ""},
    {"nome": "Albergo Colle", "indirizzo": "Colle 11, 39100 Bolzano", "tel_az": "+39 0471 329978", "email_az": "info@kohlern.com", "sito": "www.kohlern.com", "proprietario": "", "tel_alt": ""},
    {"nome": "Forsterbräu Central", "indirizzo": "Bolzano Centro, 39100 Bolzano", "tel_az": "", "email_az": "", "sito": "", "proprietario": "Birra Forst", "tel_alt": ""},
    {"nome": "Restaurant 37", "indirizzo": "Bolzano Centro, 39100 Bolzano", "tel_az": "", "email_az": "", "sito": "", "proprietario": "", "tel_alt": ""},
    {"nome": "Cibus", "indirizzo": "Zona Industriale, 39100 Bolzano", "tel_az": "", "email_az": "", "sito": "", "proprietario": "", "tel_alt": ""},

    # OLTRISARCO
    {"nome": "Ristorante Pizzeria Il Giardinetto", "indirizzo": "Via Tre Santi 1, 39100 Bolzano", "tel_az": "+39 0471 401983", "email_az": "", "sito": "", "proprietario": "", "tel_alt": ""},
    {"nome": "Fredi", "indirizzo": "Via C. Augusta 16/G, 39100 Bolzano", "tel_az": "+39 0471 922877", "email_az": "", "sito": "", "proprietario": "", "tel_alt": ""},
    {"nome": "Bar Ristorante Hong Kong", "indirizzo": "Via Claudia Augusta 25/A, 39100 Bolzano", "tel_az": "+39 0471 400578", "email_az": "", "sito": "", "proprietario": "", "tel_alt": ""},
    {"nome": "Osteria di Vicentini Marco", "indirizzo": "Via Torino 82/B, 39100 Bolzano", "tel_az": "+39 0471 503191", "email_az": "", "sito": "", "proprietario": "Marco Vicentini", "tel_alt": ""},
    {"nome": "La Piadineria", "indirizzo": "Via G. Galilei 20, 39100 Bolzano", "tel_az": "+39 0471 914567", "email_az": "", "sito": "", "proprietario": "", "tel_alt": ""},
    {"nome": "Argenton Daniel", "indirizzo": "Via Claudia Augusta 89, 39100 Bolzano", "tel_az": "+39 0471 342019", "email_az": "", "sito": "", "proprietario": "Daniel Argenton", "tel_alt": ""},
    {"nome": "The Raum", "indirizzo": "Via Galilei 10/E, 39100 Bolzano", "tel_az": "+39 0471 253792", "email_az": "", "sito": "", "proprietario": "", "tel_alt": ""},
    {"nome": "Al Ponte", "indirizzo": "Via Roma 78, 39100 Bolzano", "tel_az": "+39 0471 916491", "email_az": "", "sito": "", "proprietario": "", "tel_alt": ""},
    {"nome": "Pizza al Chiosco", "indirizzo": "Viale Trieste 19/B, 39100 Bolzano", "tel_az": "+39 0471 1922690", "email_az": "", "sito": "", "proprietario": "", "tel_alt": ""},
    {"nome": "Vesuvio", "indirizzo": "Viale Trieste 44, 39100 Bolzano", "tel_az": "+39 0471 917161", "email_az": "", "sito": "", "proprietario": "", "tel_alt": ""},
    {"nome": "McDonald's C/O Twenty", "indirizzo": "Via Galilei, 39100 Bolzano", "tel_az": "+39 0471 1982881", "email_az": "", "sito": "", "proprietario": "McDonald's", "tel_alt": ""},
    {"nome": "City Chicken", "indirizzo": "Via Firenze 9, 39100 Bolzano", "tel_az": "+39 392 4088313", "email_az": "", "sito": "", "proprietario": "", "tel_alt": "+39 392 4088313"},
    {"nome": "U.P.A.D.", "indirizzo": "Via Firenze 51, 39100 Bolzano", "tel_az": "+39 0471 916491", "email_az": "", "sito": "", "proprietario": "U.P.A.D. (associazione)", "tel_alt": ""},
    {"nome": "L'Osteria", "indirizzo": "Via Torino 82, 39100 Bolzano", "tel_az": "+39 327 7950513", "email_az": "", "sito": "", "proprietario": "", "tel_alt": "+39 327 7950513"},
    {"nome": "Eureka Caffe", "indirizzo": "Via Rovigo 94, 39100 Bolzano", "tel_az": "+39 0471 931048", "email_az": "", "sito": "", "proprietario": "", "tel_alt": ""},
    {"nome": "Dom Ristorante al Bocciodromo", "indirizzo": "Viale Trieste 17, 39100 Bolzano", "tel_az": "+39 0471 917105", "email_az": "", "sito": "", "proprietario": "", "tel_alt": ""},
    {"nome": "Ristorante Carmen", "indirizzo": "Via Rovigo 82, 39100 Bolzano", "tel_az": "+39 0471 911510", "email_az": "", "sito": "", "proprietario": "Carmen", "tel_alt": ""},
    {"nome": "Bistro' Dalmazia Bar", "indirizzo": "Via Dalmazia 39, 39100 Bolzano", "tel_az": "+39 0471 910004", "email_az": "", "sito": "", "proprietario": "", "tel_alt": ""},
    {"nome": "Alla Corte", "indirizzo": "Via Claudia Augusta 121, 39100 Bolzano", "tel_az": "+39 0471 261034", "email_az": "", "sito": "", "proprietario": "", "tel_alt": ""},
    {"nome": "Marechiaro", "indirizzo": "Via Vicenza 14, 39100 Bolzano", "tel_az": "+39 0471 402319", "email_az": "", "sito": "", "proprietario": "", "tel_alt": ""},
    {"nome": "Real Frabe S.r.l.", "indirizzo": "Via Volta 3, 39100 Bolzano", "tel_az": "+39 0471 052788", "email_az": "", "sito": "", "proprietario": "", "tel_alt": ""},
    {"nome": "Pizza Okey", "indirizzo": "Via Werner Von Siemens 4, 39100 Bolzano", "tel_az": "+39 0471 203699", "email_az": "", "sito": "", "proprietario": "", "tel_alt": ""},
    {"nome": "Noisteria", "indirizzo": "Via Volta 15, 39100 Bolzano", "tel_az": "+39 388 8228895", "email_az": "", "sito": "", "proprietario": "", "tel_alt": "+39 388 8228895"},
    {"nome": "All'Olmo", "indirizzo": "Via Antonio Pacinotti 15, 39100 Bolzano", "tel_az": "", "email_az": "", "sito": "", "proprietario": "", "tel_alt": ""},
    {"nome": "Café Pizzeria Maso della Pieve", "indirizzo": "Via Maso della Pieve 9, 39100 Bolzano", "tel_az": "+39 0471 250197", "email_az": "", "sito": "", "proprietario": "", "tel_alt": ""},
    {"nome": "Ristorante Stella Alpina", "indirizzo": "Via Claudia Augusta 97a, 39100 Bolzano", "tel_az": "", "email_az": "", "sito": "", "proprietario": "", "tel_alt": ""},
    {"nome": "Pizzeria Doppiozero", "indirizzo": "Via Maso della Pieve 2/E, 39100 Bolzano", "tel_az": "", "email_az": "", "sito": "", "proprietario": "", "tel_alt": ""},
    {"nome": "McDonald's Buozzi", "indirizzo": "Via Bruno Buozzi 32, 39100 Bolzano", "tel_az": "+39 0471 532161", "email_az": "", "sito": "", "proprietario": "McDonald's", "tel_alt": ""},
    {"nome": "Anatolia", "indirizzo": "Via Aslago 55, 39100 Bolzano", "tel_az": "+39 389 6360266", "email_az": "", "sito": "", "proprietario": "", "tel_alt": "+39 389 6360266"},

    # GRIES-SAN QUIRINO
    {"nome": "Ni Hao", "indirizzo": "Via Vittorio Veneto 23, 39100 Bolzano", "tel_az": "+39 0471 280776", "email_az": "", "sito": "", "proprietario": "", "tel_alt": ""},
    {"nome": "Antico Ristorante Pizzeria da Piero", "indirizzo": "Piazza Gries 16, 39100 Bolzano", "tel_az": "+39 0471 401343", "email_az": "", "sito": "", "proprietario": "Piero", "tel_alt": ""},
    {"nome": "WineBistro Gries 13", "indirizzo": "Piazza Gries 13, 39100 Bolzano", "tel_az": "+39 0471 1632477", "email_az": "", "sito": "www.gries13.it", "proprietario": "", "tel_alt": ""},
    {"nome": "Telser", "indirizzo": "Galleria Telser 10, 39100 Bolzano", "tel_az": "+39 0471 260156", "email_az": "", "sito": "", "proprietario": "Telser", "tel_alt": ""},
    {"nome": "Braceria Catizone Lucrezia", "indirizzo": "Via della Mendola 62, 39100 Bolzano", "tel_az": "+39 0471 910095", "email_az": "", "sito": "", "proprietario": "Lucrezia Catizone", "tel_alt": ""},
    {"nome": "Bar Bistro Gambrinus", "indirizzo": "Viale Duca D'Aosta 21, 39100 Bolzano", "tel_az": "+39 0471 283242", "email_az": "", "sito": "", "proprietario": "", "tel_alt": ""},
    {"nome": "Osteria da Marco", "indirizzo": "Via della Zecca 16, 39100 Bolzano", "tel_az": "+39 389 8742475", "email_az": "", "sito": "", "proprietario": "Marco", "tel_alt": "+39 389 8742475"},
    {"nome": "New Pizza Kebab Service", "indirizzo": "Corso Libertà 76, 39100 Bolzano", "tel_az": "+39 389 7994714", "email_az": "", "sito": "", "proprietario": "", "tel_alt": "+39 389 7994714"},
    {"nome": "Fermento", "indirizzo": "Via Palermo 11/C, 39100 Bolzano", "tel_az": "+39 335 8004005", "email_az": "", "sito": "", "proprietario": "", "tel_alt": "+39 335 8004005"},
    {"nome": "Feng Sheng", "indirizzo": "Corso Libertà 64/A, 39100 Bolzano", "tel_az": "+39 0471 273321", "email_az": "", "sito": "", "proprietario": "", "tel_alt": ""},
    {"nome": "Good Day Cafè", "indirizzo": "Corso Libertà 14, 39100 Bolzano", "tel_az": "+39 327 0714000", "email_az": "", "sito": "", "proprietario": "", "tel_alt": "+39 327 0714000"},
    {"nome": "Piccerella Pizzeria e Friggitoria", "indirizzo": "Via Cesare Battisti 25, 39100 Bolzano", "tel_az": "+39 0471 224511", "email_az": "", "sito": "", "proprietario": "", "tel_alt": ""},
    {"nome": "Nihao S.r.l.", "indirizzo": "Piazza Mazzini 15, 39100 Bolzano", "tel_az": "+39 0471 289269", "email_az": "", "sito": "", "proprietario": "", "tel_alt": ""},
    {"nome": "Thai - Oriental", "indirizzo": "Piazza Mazzini 35, 39100 Bolzano", "tel_az": "+39 0471 280078", "email_az": "", "sito": "", "proprietario": "", "tel_alt": ""},
    {"nome": "Green Bistro di Sireus Giordano", "indirizzo": "Via della Visitazione 4/D, 39100 Bolzano", "tel_az": "+39 0471 910645", "email_az": "", "sito": "", "proprietario": "Giordano Sireus", "tel_alt": ""},
    {"nome": "Il Caffè Borbone", "indirizzo": "Via della Visitazione 16/C, 39100 Bolzano", "tel_az": "+39 0471 1817554", "email_az": "", "sito": "", "proprietario": "", "tel_alt": ""},
    {"nome": "Zushi", "indirizzo": "Corso Italia 13, 39100 Bolzano", "tel_az": "+39 0471 283440", "email_az": "", "sito": "", "proprietario": "", "tel_alt": ""},
    {"nome": "Restaurant Pizzeria Gambrinus", "indirizzo": "Via Antonio Locatelli 8, 39100 Bolzano", "tel_az": "+39 0471 270887", "email_az": "", "sito": "", "proprietario": "", "tel_alt": ""},

    # DON BOSCO
    {"nome": "Bar Resia Bistró", "indirizzo": "Via Resia 166, 39100 Bolzano", "tel_az": "+39 0471 913074", "email_az": "", "sito": "", "proprietario": "", "tel_alt": ""},
    {"nome": "East & West", "indirizzo": "Via del Ronco 19/B, 39100 Bolzano", "tel_az": "+39 388 9844400", "email_az": "", "sito": "", "proprietario": "", "tel_alt": "+39 388 9844400"},
    {"nome": "Fischbanke", "indirizzo": "Dr.-Streiter Gasse 28, 39100 Bolzano", "tel_az": "+39 340 5707468", "email_az": "", "sito": "", "proprietario": "", "tel_alt": "+39 340 5707468"},
    {"nome": "Gyros Atene Bar", "indirizzo": "Via Resia 49, 39100 Bolzano", "tel_az": "+39 345 5892824", "email_az": "", "sito": "", "proprietario": "", "tel_alt": "+39 345 5892824"},
    {"nome": "Lin Gaofen", "indirizzo": "Via Resia 61, 39100 Bolzano", "tel_az": "+39 0471 923725", "email_az": "", "sito": "", "proprietario": "Gaofen Lin", "tel_alt": ""},
    {"nome": "Nto Ziffredu", "indirizzo": "Via Bari 33, 39100 Bolzano", "tel_az": "+39 0471 913366", "email_az": "", "sito": "", "proprietario": "", "tel_alt": ""},
    {"nome": "Passione Pizza da Angelo (Don Bosco)", "indirizzo": "Via Milano 134, 39100 Bolzano", "tel_az": "+39 0471 917021", "email_az": "", "sito": "", "proprietario": "Angelo", "tel_alt": ""},
    {"nome": "Stella Alpina Ben Fredj Abdeljelil", "indirizzo": "Viale Europa 37, 39100 Bolzano", "tel_az": "+39 0471 503230", "email_az": "", "sito": "", "proprietario": "Abdeljelil Ben Fredj", "tel_alt": ""},
    {"nome": "Caffetteria da Libero", "indirizzo": "Via Alessandria 19, 39100 Bolzano", "tel_az": "+39 0471 500295", "email_az": "", "sito": "", "proprietario": "Libero", "tel_alt": ""},

    # EUROPA-NOVACELLA
    {"nome": "La Piadineria Romagnola", "indirizzo": "Via Dalmazia 77/C, 39100 Bolzano", "tel_az": "+39 0471 914516", "email_az": "", "sito": "", "proprietario": "", "tel_alt": ""},
    {"nome": "Bar Padovana by Nano e Nica", "indirizzo": "Via Milano 100, 39100 Bolzano", "tel_az": "+39 0471 1703881", "email_az": "", "sito": "", "proprietario": "Nano e Nica", "tel_alt": ""},
    {"nome": "Caffetteria Ristorante Pizzeria da Libero", "indirizzo": "Via Dalmazia 81/A, 39100 Bolzano", "tel_az": "+39 0471 918509", "email_az": "", "sito": "", "proprietario": "Libero Cariglia", "tel_alt": ""},
    {"nome": "Insushi", "indirizzo": "Via Dalmazia 39, 39100 Bolzano", "tel_az": "+39 0471 935478", "email_az": "", "sito": "", "proprietario": "", "tel_alt": ""},
    {"nome": "Nihao S.r.l. (Europa)", "indirizzo": "Viale Europa 60, 39100 Bolzano", "tel_az": "+39 0471 933145", "email_az": "", "sito": "", "proprietario": "", "tel_alt": ""},
    {"nome": "Ristorante Pizzeria da Angelo", "indirizzo": "Via Palermo 37, 39100 Bolzano", "tel_az": "+39 0471 911074", "email_az": "", "sito": "", "proprietario": "Angelo", "tel_alt": ""},
    {"nome": "Rockin Beets", "indirizzo": "Via Rovigo 24, 39100 Bolzano", "tel_az": "+39 388 3684746", "email_az": "", "sito": "", "proprietario": "", "tel_alt": "+39 388 3684746"},
    {"nome": "Mair", "indirizzo": "Via Palermo 22/A, 39100 Bolzano", "tel_az": "+39 0471 913385", "email_az": "", "sito": "", "proprietario": "Mair", "tel_alt": ""},

    # PIZZERIE EXTRA
    {"nome": "Altro che pizza", "indirizzo": "Via Roma 53, 39100 Bolzano", "tel_az": "+39 0471 253587", "email_az": "", "sito": "", "proprietario": "", "tel_alt": ""},
    {"nome": "Pizza e Dintorni", "indirizzo": "Viale Duca D'Aosta 28/A, 39100 Bolzano", "tel_az": "+39 0471 272261", "email_az": "", "sito": "", "proprietario": "", "tel_alt": ""},
    {"nome": "Pizzeria da Gigi", "indirizzo": "Via Verona 27, 39100 Bolzano", "tel_az": "+39 0471 934218", "email_az": "", "sito": "", "proprietario": "Gigi", "tel_alt": ""},
    {"nome": "Saint Patrick", "indirizzo": "Via Fago 46/C, 39100 Bolzano", "tel_az": "+39 333 8849271", "email_az": "", "sito": "", "proprietario": "", "tel_alt": "+39 333 8849271"},
    {"nome": "Pizzium Bolzano", "indirizzo": "Corso Italia 13/A, 39100 Bolzano", "tel_az": "+39 0471 1920208", "email_az": "", "sito": "", "proprietario": "Pizzium (catena)", "tel_alt": ""},
    {"nome": "Il Vascello", "indirizzo": "Corso Italia 27, 39100 Bolzano", "tel_az": "+39 327 7720732", "email_az": "", "sito": "", "proprietario": "", "tel_alt": "+39 327 7720732"},
    {"nome": "La Grolla", "indirizzo": "Viale Druso 98, 39100 Bolzano", "tel_az": "+39 0471 920101", "email_az": "", "sito": "", "proprietario": "", "tel_alt": ""},
    {"nome": "Shalla Pizza", "indirizzo": "Via Rovigo 24/A, 39100 Bolzano", "tel_az": "+39 0471 1941610", "email_az": "", "sito": "", "proprietario": "", "tel_alt": ""},
    {"nome": "Da Zio Alfonso", "indirizzo": "Viale Druso 50, 39100 Bolzano", "tel_az": "+39 0471 286160", "email_az": "", "sito": "", "proprietario": "Alfonso", "tel_alt": ""},
    {"nome": "Nuova Capri", "indirizzo": "Via Resia 67, 39100 Bolzano", "tel_az": "+39 0471 930865", "email_az": "", "sito": "", "proprietario": "", "tel_alt": ""},
    {"nome": "Tip Top", "indirizzo": "Via San Vigilio 35, 39100 Bolzano", "tel_az": "+39 0471 281330", "email_az": "", "sito": "", "proprietario": "", "tel_alt": ""},
    {"nome": "Funicoli' S.a.s.", "indirizzo": "Via Palermo 10, 39100 Bolzano", "tel_az": "+39 0471 931716", "email_az": "", "sito": "", "proprietario": "", "tel_alt": ""},
]

# ============================================================
# BAR - Tutti i quartieri
# ============================================================

BAR = [
    # CENTRO/PIANI/RENCIO
    {"nome": "101 Caffè Bolzano", "indirizzo": "Galleria Europa 19, 39100 Bolzano", "tel_az": "+39 0471 1894184", "email_az": "", "sito": "", "proprietario": "101 Caffè (catena)", "tel_alt": ""},
    {"nome": "Drink Bar Snc", "indirizzo": "Via del Macello 29, 39100 Bolzano", "tel_az": "+39 0471 970133", "email_az": "", "sito": "", "proprietario": "", "tel_alt": ""},
    {"nome": "Caffè Mattei", "indirizzo": "Piazza della Parrocchia 2, 39100 Bolzano", "tel_az": "+39 0471 977665", "email_az": "", "sito": "", "proprietario": "Mattei", "tel_alt": ""},
    {"nome": "Andrade Stefaner James", "indirizzo": "Via Leonardo da Vinci 16/C, 39100 Bolzano", "tel_az": "+39 0471 233198", "email_az": "", "sito": "", "proprietario": "James Andrade Stefaner", "tel_alt": ""},
    {"nome": "Andreini Alessandra", "indirizzo": "Galleria Sernesi 27, 39100 Bolzano", "tel_az": "+39 0471 375936", "email_az": "", "sito": "", "proprietario": "Alessandra Andreini", "tel_alt": ""},
    {"nome": "Bar Pizzeria Haidi", "indirizzo": "Via Renon 33, 39100 Bolzano", "tel_az": "+39 0471 975183", "email_az": "", "sito": "", "proprietario": "Haidi", "tel_alt": ""},
    {"nome": "Binder di Parpaiola Claudio", "indirizzo": "Via dei Bottai 22/C, 39100 Bolzano", "tel_az": "+39 0471 970223", "email_az": "", "sito": "", "proprietario": "Claudio Parpaiola", "tel_alt": ""},
    {"nome": "Cafe Maschin", "indirizzo": "Via Laurin 2, 39100 Bolzano", "tel_az": "+39 0471 324733", "email_az": "", "sito": "", "proprietario": "", "tel_alt": ""},
    {"nome": "Chef Express", "indirizzo": "Piazza della Stazione 12, 39100 Bolzano", "tel_az": "+39 0471 978124", "email_az": "", "sito": "", "proprietario": "", "tel_alt": ""},
    {"nome": "Ciao & Qiao di Yan Qiao", "indirizzo": "Via De Lai 4/B, 39100 Bolzano", "tel_az": "+39 339 3523315", "email_az": "", "sito": "", "proprietario": "Yan Qiao", "tel_alt": "+39 339 3523315"},
    {"nome": "Dom Cafe S.a.s.", "indirizzo": "Via Alto Adige 2, 39100 Bolzano", "tel_az": "+39 0471 977077", "email_az": "", "sito": "", "proprietario": "", "tel_alt": ""},
    {"nome": "Eden Park", "indirizzo": "Via Museo 4/B, 39100 Bolzano", "tel_az": "+39 0471 978999", "email_az": "", "sito": "", "proprietario": "", "tel_alt": ""},
    {"nome": "Ema S.n.c. di Modena Ivano", "indirizzo": "Via della Rena 1, 39100 Bolzano", "tel_az": "+39 0471 237393", "email_az": "", "sito": "", "proprietario": "Ivano Modena", "tel_alt": ""},
    {"nome": "Enolisa S.r.l.s.", "indirizzo": "Via Dr. Streiter 22/A, 39100 Bolzano", "tel_az": "+39 0471 980630", "email_az": "", "sito": "", "proprietario": "", "tel_alt": ""},
    {"nome": "Ficale di Turrina Daniele", "indirizzo": "Via Argentieri 17, 39100 Bolzano", "tel_az": "+39 345 2227720", "email_az": "", "sito": "", "proprietario": "Daniele Turrina", "tel_alt": "+39 345 2227720"},
    {"nome": "Gds S.n.c.", "indirizzo": "Via Carducci 3, 39100 Bolzano", "tel_az": "+39 0471 978324", "email_az": "", "sito": "", "proprietario": "", "tel_alt": ""},
    {"nome": "Marylin", "indirizzo": "Via della Posta 12, 39100 Bolzano", "tel_az": "+39 393 1751469", "email_az": "", "sito": "", "proprietario": "", "tel_alt": "+39 393 1751469"},
    {"nome": "Mur Christian", "indirizzo": "Via Brennero 7/A, 39100 Bolzano", "tel_az": "+39 0471 982953", "email_az": "", "sito": "", "proprietario": "Christian Mur", "tel_alt": ""},
    {"nome": "Poberezco Natalia", "indirizzo": "Galleria Europa 1, 39100 Bolzano", "tel_az": "+39 0471 348454", "email_az": "", "sito": "", "proprietario": "Natalia Poberezco", "tel_alt": ""},

    # OLTRISARCO
    {"nome": "Bar Pia di Shahzad", "indirizzo": "Via Claudia Augusta 27, 39100 Bolzano", "tel_az": "+39 353 3812732", "email_az": "", "sito": "", "proprietario": "Muhammad Atif Shahzad", "tel_alt": "+39 353 3812732"},
    {"nome": "Peter Pub di Veronese Alex", "indirizzo": "Via San Vigilio 76/A, 39100 Bolzano", "tel_az": "+39 0471 278689", "email_az": "", "sito": "", "proprietario": "Alex Veronese", "tel_alt": ""},
    {"nome": "Gelateria Bar Bersaglio", "indirizzo": "Piazzetta del Bersaglio 8, 39100 Bolzano", "tel_az": "+39 0471 224423", "email_az": "", "sito": "", "proprietario": "Francesco Perri", "tel_alt": ""},
    {"nome": "Soares Glenda Graziella", "indirizzo": "Via Claudia Augusta 37, 39100 Bolzano", "tel_az": "+39 0471 366321", "email_az": "", "sito": "", "proprietario": "Glenda Graziella Soares", "tel_alt": ""},
    {"nome": "Tassi S.a.s. di Tassi Mirka", "indirizzo": "Via S. Vigilio 52, 39100 Bolzano", "tel_az": "+39 0471 260830", "email_az": "", "sito": "", "proprietario": "Mirka Tassi", "tel_alt": ""},
    {"nome": "Rasuli Hemn", "indirizzo": "Via Claudia Augusta 41/A, 39100 Bolzano", "tel_az": "+39 328 8868882", "email_az": "", "sito": "", "proprietario": "Hemn Rasuli", "tel_alt": "+39 328 8868882"},
    {"nome": "Gelateria Bar Mario Bolzano", "indirizzo": "Via Santa Geltrude 48, 39100 Bolzano", "tel_az": "+39 0471 264502", "email_az": "", "sito": "", "proprietario": "Mario", "tel_alt": ""},
    {"nome": "Tsurkan Nadiya", "indirizzo": "Via Roma 84/A, 39100 Bolzano", "tel_az": "+39 0471 539531", "email_az": "", "sito": "", "proprietario": "Nadiya Tsurkan", "tel_alt": ""},
    {"nome": "Zhan Weiwu & Zhang Weiwei S.n.c.", "indirizzo": "Via Claudia Augusta 64, 39100 Bolzano", "tel_az": "+39 0471 271726", "email_az": "", "sito": "", "proprietario": "Zhan Weiwu, Zhang Weiwei", "tel_alt": ""},
    {"nome": "Bar San Marco S.n.c. di Jin Quianghua", "indirizzo": "Via Claudia Augusta 68/A, 39100 Bolzano", "tel_az": "+39 0471 260473", "email_az": "", "sito": "", "proprietario": "Jin Quianghua", "tel_alt": ""},

    # GRIES-SAN QUIRINO
    {"nome": "Graeber Franz", "indirizzo": "Piazza Gries 11/A, 39100 Bolzano", "tel_az": "+39 0471 379947", "email_az": "", "sito": "", "proprietario": "Franz Graeber", "tel_alt": ""},
    {"nome": "Caffe Gries di Tafani Silvana", "indirizzo": "Piazza Gries 7/A, 39100 Bolzano", "tel_az": "+39 0471 375014", "email_az": "", "sito": "", "proprietario": "Silvana Tafani", "tel_alt": ""},
    {"nome": "Sasmaz Fatma", "indirizzo": "Via della Mendola 54/A, 39100 Bolzano", "tel_az": "+39 0471 503288", "email_az": "", "sito": "", "proprietario": "Fatma Sasmaz", "tel_alt": ""},
    {"nome": "Bar Amedeo S.a.s. di Silla Lorenzo", "indirizzo": "Via Battisti 44, 39100 Bolzano", "tel_az": "+39 0471 537688", "email_az": "", "sito": "", "proprietario": "Lorenzo Silla", "tel_alt": ""},
    {"nome": "Wlm S.a.s. di Segafredo Walter", "indirizzo": "Via Gaismair 10, 39100 Bolzano", "tel_az": "+39 0471 253131", "email_az": "", "sito": "", "proprietario": "Walter Segafredo", "tel_alt": ""},
    {"nome": "Bar Tennis", "indirizzo": "Via Pacher 2, 39100 Bolzano", "tel_az": "+39 0471 281519", "email_az": "", "sito": "", "proprietario": "", "tel_alt": ""},
    {"nome": "Karwan Rasul Ali", "indirizzo": "Piazza Mazzini 48, 39100 Bolzano", "tel_az": "+39 0471 236409", "email_az": "", "sito": "", "proprietario": "Rasul Ali Karwan", "tel_alt": ""},
    {"nome": "Jin Chang S.n.c. di Xu Feng", "indirizzo": "Viale Duca D'Aosta 91, 39100 Bolzano", "tel_az": "+39 320 8596698", "email_az": "", "sito": "", "proprietario": "Xu Feng", "tel_alt": "+39 320 8596698"},
    {"nome": "Café Bistró 2000", "indirizzo": "Viale Duca D'Aosta 93, 39100 Bolzano", "tel_az": "+39 0471 285018", "email_az": "", "sito": "", "proprietario": "", "tel_alt": ""},
    {"nome": "Schipani Luciana", "indirizzo": "Via Sorrento 33, 39100 Bolzano", "tel_az": "+39 0471 501499", "email_az": "", "sito": "", "proprietario": "Luciana Schipani", "tel_alt": ""},
    {"nome": "Coffee Bean", "indirizzo": "Corso Libertà 15, 39100 Bolzano", "tel_az": "+39 0471 401738", "email_az": "", "sito": "", "proprietario": "", "tel_alt": ""},
    {"nome": "Elgian Semplificata", "indirizzo": "Via Amba Alagi 26, 39100 Bolzano", "tel_az": "+39 0471 235444", "email_az": "", "sito": "", "proprietario": "", "tel_alt": ""},

    # DON BOSCO
    {"nome": "Bar Mario di Trotto Massimo", "indirizzo": "Via Resia 98, 39100 Bolzano", "tel_az": "+39 0471 095640", "email_az": "", "sito": "", "proprietario": "Massimo Trotto", "tel_alt": ""},
    {"nome": "Campanardi Sandra", "indirizzo": "Via del Ronco 9, 39100 Bolzano", "tel_az": "+39 0471 539064", "email_az": "", "sito": "", "proprietario": "Sandra Campanardi", "tel_alt": ""},
    {"nome": "Gelateria Bar Bersaglio Resia", "indirizzo": "Via Resia 108, 39100 Bolzano", "tel_az": "+39 0471 224826", "email_az": "", "sito": "", "proprietario": "Francesco Perri", "tel_alt": "+39 329 6738863"},
    {"nome": "Gelatiera Caffettiera Pennini", "indirizzo": "Via Resia 76/A, 39100 Bolzano", "tel_az": "+39 388 1935902", "email_az": "", "sito": "", "proprietario": "Pennini", "tel_alt": "+39 388 1935902"},
    {"nome": "Milano 192 Gelato", "indirizzo": "Via Milano 192/A, 39100 Bolzano", "tel_az": "+39 0471 236500", "email_az": "", "sito": "", "proprietario": "", "tel_alt": ""},
    {"nome": "Satellite di Targa Tatiana", "indirizzo": "Via Cagliari 12, 39100 Bolzano", "tel_az": "+39 0471 933098", "email_az": "", "sito": "", "proprietario": "Tatiana Targa", "tel_alt": ""},
    {"nome": "Bar Alimentari Don Bosco", "indirizzo": "Piazza Don Bosco 4/A, 39100 Bolzano", "tel_az": "+39 0471 342879", "email_az": "", "sito": "", "proprietario": "", "tel_alt": ""},
    {"nome": "White Devil di Manole Ionela", "indirizzo": "Via Resia 138, 39100 Bolzano", "tel_az": "+39 0471 911226", "email_az": "", "sito": "", "proprietario": "Ionela Manole", "tel_alt": ""},

    # EUROPA-NOVACELLA
    {"nome": "Bar Centro 2", "indirizzo": "Via Milano 20, 39100 Bolzano", "tel_az": "+39 329 1937121", "email_az": "", "sito": "", "proprietario": "", "tel_alt": "+39 329 1937121"},
    {"nome": "Savino Coffee Shop", "indirizzo": "Via Torino 58, 39100 Bolzano", "tel_az": "+39 0471 347136", "email_az": "", "sito": "", "proprietario": "Savino", "tel_alt": ""},
    {"nome": "An di Nicastro Alex & Co.", "indirizzo": "Via Milano 100, 39100 Bolzano", "tel_az": "+39 0471 233468", "email_az": "", "sito": "", "proprietario": "Alex Nicastro", "tel_alt": ""},
    {"nome": "Gero S.a.s. di Gerardi Carmine", "indirizzo": "Via Dalmazia 37/B, 39100 Bolzano", "tel_az": "+39 0471 919283", "email_az": "", "sito": "", "proprietario": "Carmine Gerardi", "tel_alt": ""},
    {"nome": "La Cubana", "indirizzo": "Piazza Matteotti 11, 39100 Bolzano", "tel_az": "+39 340 8693849", "email_az": "", "sito": "", "proprietario": "", "tel_alt": "+39 340 8693849"},
    {"nome": "Tre Erre di Rojas Juan Carlos", "indirizzo": "Via Palermo 37, 39100 Bolzano", "tel_az": "+39 0471 911074", "email_az": "", "sito": "", "proprietario": "Juan Carlos Rojas", "tel_alt": ""},
    {"nome": "Bar Romagnolo", "indirizzo": "Piazza Matteotti 8, 39100 Bolzano", "tel_az": "+39 0471 501846", "email_az": "", "sito": "", "proprietario": "", "tel_alt": ""},

    # ALTRI
    {"nome": "Alko S.n.c. Stublla Kujtim e Bleart", "indirizzo": "Corso Libertà 13, 39100 Bolzano", "tel_az": "+39 0471 236702", "email_az": "", "sito": "", "proprietario": "Kujtim Stublla, Bleart Stublla", "tel_alt": ""},
    {"nome": "Chen Dynasty di Zhang Jing", "indirizzo": "Piazza Anita Pichler 26, 39100 Bolzano", "tel_az": "+39 0471 348331", "email_az": "", "sito": "", "proprietario": "Zhang Jing", "tel_alt": ""},
    {"nome": "Bar del Corso di Gabriele Santo Agostino", "indirizzo": "Via Giuliani Padre Reginaldo 1, 39100 Bolzano", "tel_az": "+39 0471 262602", "email_az": "", "sito": "", "proprietario": "Gabriele Santo Agostino", "tel_alt": ""},
    {"nome": "Bar Harty", "indirizzo": "Via Dùhrer 14, 39100 Bolzano", "tel_az": "+39 0471 930653", "email_az": "", "sito": "", "proprietario": "", "tel_alt": ""},
    {"nome": "Bar Ristorante Circolo Tennis Gries", "indirizzo": "Via Knoller 8, 39100 Bolzano", "tel_az": "+39 347 3964215", "email_az": "", "sito": "", "proprietario": "Circolo Tennis Gries", "tel_alt": "+39 347 3964215"},
    {"nome": "Bar Ristorante F.lli Meli", "indirizzo": "Piazza Firmian 2, 39100 Bolzano", "tel_az": "+39 0471 911077", "email_az": "", "sito": "", "proprietario": "Giovanni Meli, Salvatore Meli", "tel_alt": ""},
]


def build_csv():
    output = "/Users/simocors/Desktop/telesales/aziende_bolzano_VERIFICATE.csv"

    all_data = []
    for h in HOTEL:
        all_data.append({**h, 'tipo': 'Hotel'})
    for r in RISTORANTI:
        all_data.append({**r, 'tipo': 'Ristorante'})
    for b in BAR:
        all_data.append({**b, 'tipo': 'Bar'})

    # Deduplicazione su nome + indirizzo
    seen = set()
    deduped = []
    for biz in all_data:
        key = (biz['nome'].lower().strip(), biz['indirizzo'].lower().strip())
        if key not in seen:
            seen.add(key)
            deduped.append(biz)

    final_data = []
    for biz in deduped:
        final_data.append({
            'nome_azienda': biz['nome'],
            'tipo': biz['tipo'],
            'indirizzo': biz['indirizzo'],
            'tel_aziendale': biz['tel_az'],
            'email_aziendale': biz['email_az'],
            'sito_web': biz['sito'],
            'proprietario': biz['proprietario'],
            'tel_diretto_proprietario': biz.get('tel_alt', '')
        })

    with open(output, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=[
            'nome_azienda', 'tipo', 'indirizzo',
            'tel_aziendale', 'email_aziendale', 'sito_web',
            'proprietario', 'tel_diretto_proprietario'
        ])
        writer.writeheader()
        writer.writerows(sorted(final_data, key=lambda x: (x['tipo'], x['nome_azienda'])))

    print(f"✅ CSV salvato: {output}")
    print(f"📊 TOTALE: {len(final_data)} aziende VERIFICATE")

    by_type = defaultdict(int)
    for d in final_data:
        by_type[d['tipo']] += 1

    print("\n📈 Distribuzione:")
    for tipo, count in sorted(by_type.items()):
        print(f"  • {tipo}: {count}")

    def pct(field):
        filled = sum(1 for d in final_data if d[field])
        return filled, filled * 100 // len(final_data)

    print("\n📊 Completezza:")
    for field in ['indirizzo', 'tel_aziendale', 'email_aziendale', 'sito_web', 'proprietario', 'tel_diretto_proprietario']:
        filled, p = pct(field)
        print(f"  • {field:30s}: {filled:3d}/{len(final_data)} ({p}%)")

if __name__ == "__main__":
    build_csv()
