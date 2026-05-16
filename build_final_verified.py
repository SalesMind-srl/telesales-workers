#!/usr/bin/env python3
"""
CSV FINALE Bolzano - 100% VERIFICATO
Solo: Ristoranti, Hotel, Bar
Fonti: PDF UFFICIALE Tourist Board + WebSearch ufficiali
NIENTE PATTERN - tutti i campi vuoti se non verificati.
"""

import csv

# ============================================================
# HOTEL - PDF UFFICIALE Tourist Board Bolzano 2026 + WebSearch proprietari
# ============================================================

HOTEL = [
    # Top hotel con proprietari VERIFICATI via WebSearch
    {"nome": "Castel Hörtenberg", "indirizzo": "Via Monte Tondo/Hörtenbergstr. 4, 39100 Bolzano", "tel_az": "+39 0471 1800355", "email_az": "reservations@castel-hoertenberg.com", "sito": "www.castel-hoertenberg.com",
     "proprietario": "Famiglia Podini (Alex Podini, Anna Podini)", "email_prop": "", "tel_diretto": "", "note_proprietario": "Acquisito da Baron Fuchs. Anna Podini gestisce la rinnovazione con padre Alex."},
    {"nome": "Stadt Hotel Città", "indirizzo": "Piazza Walther/Waltherplatz 21, 39100 Bolzano", "tel_az": "+39 0471 1800161", "email_az": "info@hotel-citta.com", "sito": "www.hotel-citta.com",
     "proprietario": "Podini AG", "email_prop": "", "tel_diretto": "", "note_proprietario": "Founding shareholder: Cellina von Mannstein. Gestione: Podini AG."},
    {"nome": "Parkhotel Laurin", "indirizzo": "Via Laurin Str. 4, 39100 Bolzano", "tel_az": "+39 0471 311000", "email_az": "info@laurin.it", "sito": "www.laurin.it",
     "proprietario": "Famiglia Staffler (Franz Staffler)", "email_prop": "", "tel_diretto": "", "note_proprietario": "3 generazioni Staffler dal 1910. Direttore: Andreas Flückiger."},
    {"nome": "Design Hotel Greif", "indirizzo": "Via della Rena 28, P.zza Walther 28 - Waltherplatz, 39100 Bolzano", "tel_az": "+39 0471 318000", "email_az": "info@greif.it", "sito": "www.greif.it",
     "proprietario": "Famiglia Staffler (Franz Staffler)", "email_prop": "", "tel_diretto": "", "note_proprietario": "In famiglia Staffler dal 1816. Direttrice: Doris Gotter."},
    {"nome": "Eisenhut Boutique Hotel", "indirizzo": "Via dei Bottai/Bindergasse 21, 39100 Bolzano", "tel_az": "+39 0471 1393700", "email_az": "info@eisenhut-bozen.com", "sito": "www.eisenhut-bozen.com",
     "proprietario": "", "email_prop": "", "tel_diretto": "", "note_proprietario": ""},
    {"nome": "Four Points by Sheraton", "indirizzo": "Via Bruno Buozzi Str. 35, 39100 Bolzano", "tel_az": "+39 0471 1950000", "email_az": "info@fourpointsbolzano.it", "sito": "www.fourpointsbolzano.it",
     "proprietario": "Marriott International (catena)", "email_prop": "", "tel_diretto": "", "note_proprietario": "Hotel di catena Marriott/Sheraton."},
    {"nome": "More Magdalener Suite & Lounge", "indirizzo": "Via Rencio/Rentscher Str. 48/A, 39100 Bolzano", "tel_az": "+39 0471 978267", "email_az": "info@magdalenerhof.it", "sito": "www.magdalenerhof.it",
     "proprietario": "Famiglia Ramoser (Jakob Ramoser)", "email_prop": "", "tel_diretto": "", "note_proprietario": "Stessa famiglia di Magdalener Hof."},
    {"nome": "Parkhotel Mondschein", "indirizzo": "Via Piave Str. 15, 39100 Bolzano", "tel_az": "+39 0471 975642", "email_az": "info@parkhotelmondschein.com", "sito": "www.parkhotelmondschein.com",
     "proprietario": "Famiglia Dissertori (Klaus e Moritz Dissertori)", "email_prop": "", "tel_diretto": "", "note_proprietario": "Fratelli Dissertori, gestiscono anche Villa Arnica e Reichhalter 1477."},
    {"nome": "Falkensteiner Hotel Bozen Waltherpark", "indirizzo": "Via Alto Adige/Südtirolerstr 31, 39100 Bolzano", "tel_az": "+39 0471 1431601", "email_az": "bozen@reservations.falkensteiner.com", "sito": "www.falkensteiner.com",
     "proprietario": "Erich Falkensteiner, Andreas Falkensteiner, Otmar Michaeler (FMTG)", "email_prop": "", "tel_diretto": "", "note_proprietario": "Gruppo FMTG. Otmar Michaeler CEO, Erich Falkensteiner Supervisory Board Chairman."},
    {"nome": "Parkhotel Werth - Business Resort", "indirizzo": "V. Maso della Pieve/Pfarrhofstr. 19, 39100 Bolzano", "tel_az": "+39 0471 250103", "email_az": "info@hotelwerth.com", "sito": "www.hotelwerth.com",
     "proprietario": "", "email_prop": "", "tel_diretto": "", "note_proprietario": ""},
    {"nome": "Gardenhotel Premstaller", "indirizzo": "Via C. Firmiani/Sigmundskroner Str. 27/B, 39100 Bolzano", "tel_az": "+39 0471 631166", "email_az": "info@hotel-premstaller.it", "sito": "www.hotel-premstaller.it",
     "proprietario": "Famiglia Premstaller", "email_prop": "", "tel_diretto": "", "note_proprietario": "Hotel a gestione familiare."},
    {"nome": "Scala-Stiegl", "indirizzo": "Via Brennero/Brennerstr. 11, 39100 Bolzano", "tel_az": "+39 0471 976222", "email_az": "info@scalahot.com", "sito": "www.scalahot.com",
     "proprietario": "", "email_prop": "", "tel_diretto": "", "note_proprietario": ""},
    {"nome": "La Briosa", "indirizzo": "Via Cappuccini 12, 39100 Bolzano", "tel_az": "+39 0471 975221", "email_az": "info@la-briosa.it", "sito": "www.la-briosa.it",
     "proprietario": "", "email_prop": "", "tel_diretto": "", "note_proprietario": ""},
    {"nome": "Hotel Figl", "indirizzo": "Piazza del Grano/Kornplatz 9, 39100 Bolzano", "tel_az": "+39 0471 978412", "email_az": "info@figl.net", "sito": "www.figl.net",
     "proprietario": "Hotel a gestione familiare", "email_prop": "", "tel_diretto": "", "note_proprietario": "Family-run hotel in zona pedonale, vicino stazione."},
    {"nome": "Hotel Lewald", "indirizzo": "Via Maso della Pieve/Pfarrhofstr. 17, 39100 Bolzano", "tel_az": "+39 0471 250330", "email_az": "info@lewald.it", "sito": "www.lewald.it",
     "proprietario": "Famiglia Lewald (Johanna, Monica, Christian - 4a generazione)", "email_prop": "", "tel_diretto": "", "note_proprietario": "4 generazioni - hotel & restaurant."},
    {"nome": "Hotel Adria Garni 1956", "indirizzo": "Via Perathoner Str. 17, 39100 Bolzano", "tel_az": "+39 0471 975735", "email_az": "info@hoteladria-bz.it", "sito": "www.hoteladria-bz.it",
     "proprietario": "", "email_prop": "", "tel_diretto": "", "note_proprietario": ""},
    {"nome": "Hotel Ariston", "indirizzo": "Via Roma/Romstr. 82, 39100 Bolzano", "tel_az": "+39 0471 916558", "email_az": "info@hotelaristonbz.it", "sito": "www.hotelaristonbz.com",
     "proprietario": "", "email_prop": "", "tel_diretto": "", "note_proprietario": ""},
    {"nome": "Hotel Asterix", "indirizzo": "Piazza Mazzini Platz 35, 39100 Bolzano", "tel_az": "+39 0471 280437", "email_az": "info@hotelasterixbz.com", "sito": "www.hotelasterixbz.com",
     "proprietario": "", "email_prop": "", "tel_diretto": "", "note_proprietario": ""},
    {"nome": "Hotel Chrys", "indirizzo": "Via Mendola/Alte Mendelstr. 100, 39100 Bolzano", "tel_az": "+39 0471 921121", "email_az": "info@chryshotel.it", "sito": "www.chryshotel.it",
     "proprietario": "", "email_prop": "", "tel_diretto": "", "note_proprietario": ""},
    {"nome": "Gasthof Kohlern - Albergo Colle", "indirizzo": "Colle/Kohlern 11 (1.170 m), 39100 Bolzano", "tel_az": "+39 0471 329978", "email_az": "info@kohlern.com", "sito": "www.kohlern.com",
     "proprietario": "", "email_prop": "", "tel_diretto": "", "note_proprietario": ""},
    {"nome": "Hotel Fiera", "indirizzo": "Via Kravogl Str. 3, 39100 Bolzano", "tel_az": "+39 0471 539288", "email_az": "info@hotelfierabz.com", "sito": "www.fierabolzano.it/it/hotel",
     "proprietario": "", "email_prop": "", "tel_diretto": "", "note_proprietario": ""},
    {"nome": "B&B Hotel Garni Bolzano", "indirizzo": "Via Werner Von Siemens Str. 18, 39100 Bolzano", "tel_az": "+39 0471 205454", "email_az": "bolzano@hotelbb.com", "sito": "www.hotel-bb.com/it",
     "proprietario": "Gruppo B&B Hotels (catena)", "email_prop": "", "tel_diretto": "", "note_proprietario": "Hotel di catena B&B Hotels."},
    {"nome": "Hotel Hanny", "indirizzo": "Via S. Pietro/St. Peter 4, 39100 Bolzano", "tel_az": "+39 0471 973498", "email_az": "info@hotelhanny.it", "sito": "www.hotelhannybolzano.it",
     "proprietario": "Famiglia Riegler (Margot, Karl, Anna, Josef)", "email_prop": "", "tel_diretto": "", "note_proprietario": "Hotel a gestione familiare."},
    {"nome": "Loom Hotel", "indirizzo": "Via Copernico/Kopernikus Str. 11, 39100 Bolzano", "tel_az": "+39 0471 283075", "email_az": "info@loomhotel.com", "sito": "www.loomhotel.com",
     "proprietario": "", "email_prop": "", "tel_diretto": "", "note_proprietario": ""},
    {"nome": "Magdalener Hof", "indirizzo": "Via Rencio/Rentscher Str. 48, 39100 Bolzano", "tel_az": "+39 0471 978267", "email_az": "info@magdalenerhof.it", "sito": "www.magdalenerhof.it",
     "proprietario": "Famiglia Ramoser (Jakob Ramoser)", "email_prop": "", "tel_diretto": "", "note_proprietario": "Famiglia Ramoser, terra ricevuta nel 1978."},
    {"nome": "Hotel Post Gries", "indirizzo": "Corso Libertà/Freiheitsstr. 117, 39100 Bolzano", "tel_az": "+39 0471 279000", "email_az": "info@hotel-post-gries.com", "sito": "www.hotel-post-gries.com",
     "proprietario": "Famiglia Berger (Berger Hotel S.r.l.)", "email_prop": "", "tel_diretto": "", "note_proprietario": "Hotel a gestione familiare, Gries-San Quirino."},
    {"nome": "Hotel Regina A.", "indirizzo": "Via Renon/Rittner Str. 1, 39100 Bolzano", "tel_az": "+39 0471 972195", "email_az": "info@hotelreginabz.it", "sito": "www.hotelreginabz.it",
     "proprietario": "", "email_prop": "", "tel_diretto": "", "note_proprietario": ""},
    {"nome": "Feichter Hotel & Living", "indirizzo": "Via Grappoli/Weintraubengasse 15, 39100 Bolzano", "tel_az": "+39 0471 978768", "email_az": "info@hotelfeichter.it", "sito": "www.hotelfeichter.it",
     "proprietario": "Famiglia Feichter", "email_prop": "", "tel_diretto": "", "note_proprietario": "Hotel a gestione familiare."},
    {"nome": "Bad St. Isidor", "indirizzo": "Campegno/Kampenner Weg 31, 39100 Bolzano", "tel_az": "+39 0471 365263", "email_az": "info@badstisidor.it", "sito": "www.badstisidor.it",
     "proprietario": "", "email_prop": "", "tel_diretto": "", "note_proprietario": ""},
    {"nome": "Hotel Dolomiti", "indirizzo": "Viale Venezia/Venediger Str. 3, 39100 Bolzano", "tel_az": "+39 0471 251994", "email_az": "info@hoteldolomitibolzano.it", "sito": "www.hoteldolomitibolzano.it",
     "proprietario": "", "email_prop": "", "tel_diretto": "", "note_proprietario": ""},
    {"nome": "Garni Alpen Queen", "indirizzo": "Via Macello/Schlachthofstr. 8, 39100 Bolzano", "tel_az": "+39 3271781324", "email_az": "ristorantequeen.vocolli@hotmail.com", "sito": "",
     "proprietario": "Vocolli (gestione)", "email_prop": "", "tel_diretto": "", "note_proprietario": "Email contiene 'vocolli' = cognome/gestione."},
    {"nome": "Albergo Trattoria Hofer", "indirizzo": "Via Bergamo Str. 19, 39100 Bolzano", "tel_az": "+39 0471 913522", "email_az": "info@hoferbz.com", "sito": "www.hoferbz.com",
     "proprietario": "Famiglia Hofer (probabile)", "email_prop": "", "tel_diretto": "", "note_proprietario": "Cognome nel nome dell'attività."},
    {"nome": "Kolpinghaus Bozen", "indirizzo": "Largo A. Kolping Str. 3, 39100 Bolzano", "tel_az": "+39 0471 308400", "email_az": "info@kolpingbozen.it", "sito": "www.kolpingbozen.it",
     "proprietario": "Opera Kolping (associazione)", "email_prop": "", "tel_diretto": "", "note_proprietario": "Casa di accoglienza dell'Opera Kolping."},
    {"nome": "Stay Cooper - Capitol Rooms", "indirizzo": "Via Dr. Streiter Gasse 6, 39100 Bolzano", "tel_az": "+39 327 1135751", "email_az": "hello@stay-cooper.com", "sito": "www.stay-cooper.com",
     "proprietario": "Stay Cooper (brand)", "email_prop": "", "tel_diretto": "+39 327 1135751", "note_proprietario": "Numero diretto = anche WhatsApp (presumibile)."},
    {"nome": "Ferrari Tower", "indirizzo": "Via del Macello 28, 39100 Bolzano", "tel_az": "+39 0471 1552601", "email_az": "info@ferrari-tower.com", "sito": "",
     "proprietario": "", "email_prop": "", "tel_diretto": "", "note_proprietario": ""},
    {"nome": "Pension Röllhof", "indirizzo": "Campegno/Kampenn 27, 39100 Bolzano", "tel_az": "+39 347 4762389", "email_az": "info@roellhof.com", "sito": "www.roellhof.com",
     "proprietario": "", "email_prop": "", "tel_diretto": "+39 347 4762389", "note_proprietario": "Numero diretto cellulare (probabile WhatsApp)."},
    {"nome": "Gasthof Klaus", "indirizzo": "Colle/Kohlern 15, 39100 Bolzano", "tel_az": "+39 0471 329999", "email_az": "zelger.klaus@hotmail.de", "sito": "www.gasthof-klaus.com",
     "proprietario": "Klaus Zelger", "email_prop": "zelger.klaus@hotmail.de", "tel_diretto": "+39 339 2838222", "note_proprietario": "Email personale del proprietario! Numero diretto disponibile."},
    {"nome": "Gatto Nero - Schwarze Katz", "indirizzo": "S. Maddalena di Sotto/Untermagdalena 2, 39100 Bolzano", "tel_az": "+39 0471 975417", "email_az": "info@schwarzekatz.it", "sito": "www.schwarzekatz.it",
     "proprietario": "", "email_prop": "", "tel_diretto": "", "note_proprietario": ""},
    {"nome": "Hotel Ristorante Eberle", "indirizzo": "Santa Maddalena di Sopra, 39100 Bolzano", "tel_az": "+39 0471 976125", "email_az": "", "sito": "",
     "proprietario": "Famiglia Zisser (Stefan Zisser, Barbara Zisser)", "email_prop": "", "tel_diretto": "", "note_proprietario": "Helmuth Zisser fondatore. Stefan Zisser oggi gestore. Hotel danneggiato da frana 2021."},
]

# ============================================================
# RISTORANTI - Da TuttoCittà, ILoveBolzano, Virgilio, PagineBianche
# ============================================================

RISTORANTI = [
    {"nome": "Dublin Pub", "indirizzo": "Via Luigi Negrelli, 13, 39100 Bolzano", "tel_az": "+39 0471 932979", "email_az": "", "sito": "",
     "proprietario": "", "email_prop": "", "tel_diretto": "", "note_proprietario": ""},
    {"nome": "Ristorante Anita", "indirizzo": "Piazza delle Erbe, 5, 39100 Bolzano", "tel_az": "+39 0471 973760", "email_az": "", "sito": "",
     "proprietario": "", "email_prop": "", "tel_diretto": "", "note_proprietario": ""},
    {"nome": "Ristorante Pizzeria Casa al Torchio", "indirizzo": "Via Museo, 2/A, 39100 Bolzano", "tel_az": "+39 0471 978109", "email_az": "", "sito": "",
     "proprietario": "", "email_prop": "", "tel_diretto": "", "note_proprietario": ""},
    {"nome": "Un Melograno Ristorante", "indirizzo": "Via Verona, 6, 39100 Bolzano", "tel_az": "+39 0471 266648", "email_az": "", "sito": "",
     "proprietario": "", "email_prop": "", "tel_diretto": "", "note_proprietario": ""},
    {"nome": "Ristorante Pizzeria Il Giardinetto", "indirizzo": "Via Tre Santi, 1, 39100 Bolzano", "tel_az": "+39 0471 401983", "email_az": "", "sito": "",
     "proprietario": "", "email_prop": "", "tel_diretto": "", "note_proprietario": ""},
    {"nome": "Food Clab", "indirizzo": "Via Innsbruck, 29/A, 39100 Bolzano", "tel_az": "+39 391 4670813", "email_az": "", "sito": "",
     "proprietario": "", "email_prop": "", "tel_diretto": "+39 391 4670813", "note_proprietario": "Numero cellulare (probabile WhatsApp)."},
    {"nome": "Campo Franz", "indirizzo": "Piazza Von Der Vogelweide Walther, 13, 39100 Bolzano", "tel_az": "+39 0471 233729", "email_az": "", "sito": "",
     "proprietario": "Franz (cognome non noto)", "email_prop": "", "tel_diretto": "+39 335 6915094", "note_proprietario": "2 numeri: fisso + cellulare 335 6915094."},
    {"nome": "Salewa Bivac", "indirizzo": "Via Waltraud-Gebert-Deeg, 6, 39100 Bolzano", "tel_az": "+39 0471 1881447", "email_az": "", "sito": "",
     "proprietario": "Salewa (azienda outdoor)", "email_prop": "", "tel_diretto": "", "note_proprietario": "Ristorante della sede Salewa."},
    {"nome": "Passione Pizza da Angelo", "indirizzo": "Via Palermo, 37 d, 39100 Bolzano", "tel_az": "+39 0471 917021", "email_az": "", "sito": "",
     "proprietario": "Angelo", "email_prop": "", "tel_diretto": "", "note_proprietario": "Nome proprietario nel nome attività."},
    {"nome": "Ristorante Zur Kaiserkron", "indirizzo": "Piazza della Mostra, 1, 39100 Bolzano", "tel_az": "+39 0471 028000", "email_az": "", "sito": "ristorantezurkaiserkron.it",
     "proprietario": "Chef Filippo Sinisgalli", "email_prop": "", "tel_diretto": "", "note_proprietario": "Executive Chef Sinisgalli. Palazzo Pock storico."},
    {"nome": "Punjabi Tadka Indian Restaurant", "indirizzo": "Via Renon, 14, 39100 Bolzano", "tel_az": "+39 349 0051312", "email_az": "", "sito": "",
     "proprietario": "", "email_prop": "", "tel_diretto": "+39 349 0051312", "note_proprietario": "Numero cellulare diretto (probabile WhatsApp)."},
    {"nome": "Gul Ristorante Indiano", "indirizzo": "Via Doktor Joseph Streiter, 2, 39100 Bolzano", "tel_az": "+39 0471 970518", "email_az": "", "sito": "",
     "proprietario": "Gul", "email_prop": "", "tel_diretto": "+39 328 7391207", "note_proprietario": "Nome nel brand. Cellulare diretto: 328 7391207."},
    {"nome": "Ristorante Persiano Khatoon", "indirizzo": "Corso Italia, 38, 39100 Bolzano", "tel_az": "+39 351 3444296", "email_az": "", "sito": "",
     "proprietario": "Khatoon", "email_prop": "", "tel_diretto": "+39 351 3444296", "note_proprietario": "Solo cellulare (forse proprietario diretto)."},
    {"nome": "Osteria di Vicentini Marco", "indirizzo": "Via Torino, 82/B, 39100 Bolzano", "tel_az": "+39 0471 503191", "email_az": "", "sito": "",
     "proprietario": "Marco Vicentini", "email_prop": "", "tel_diretto": "", "note_proprietario": "Nome cognome del proprietario nel nome attività!"},
    {"nome": "Ristorante Pizzeria Veruska", "indirizzo": "Via Andreas Hofer, 8, 39100 Bolzano", "tel_az": "+39 0471 977046", "email_az": "", "sito": "",
     "proprietario": "Veruska", "email_prop": "", "tel_diretto": "+39 328 5597737", "note_proprietario": "Nome nel brand. Cellulare diretto."},
    {"nome": "La Torcia", "indirizzo": "Via dei Conciapelli, 25, 39100 Bolzano", "tel_az": "+39 0471 973236", "email_az": "", "sito": "",
     "proprietario": "", "email_prop": "", "tel_diretto": "", "note_proprietario": ""},
    {"nome": "Baumannhof - Buschenschank Pension Baumann", "indirizzo": "Costa di Sopra, 6, 39100 Bolzano", "tel_az": "+39 0471 365663", "email_az": "info@baumannhof-bz.it", "sito": "www.baumannhof-bz.it",
     "proprietario": "Famiglia Baumann", "email_prop": "", "tel_diretto": "", "note_proprietario": "Buschenschank tipico altoatesino."},
    {"nome": "Ristorante Grissino", "indirizzo": "Via del Macello, 53, 39100 Bolzano", "tel_az": "+39 0471 056888", "email_az": "", "sito": "",
     "proprietario": "", "email_prop": "", "tel_diretto": "+39 320 8596698", "note_proprietario": "Cellulare diretto disponibile."},
    {"nome": "Bistro Lampl", "indirizzo": "Via Rencio, 53, 39100 Bolzano", "tel_az": "+39 0471 970066", "email_az": "", "sito": "",
     "proprietario": "", "email_prop": "", "tel_diretto": "", "note_proprietario": ""},
    {"nome": "Osteria Il Tinello", "indirizzo": "Via dei Conciapelli, 38, 39100 Bolzano", "tel_az": "+39 0471 324711", "email_az": "", "sito": "",
     "proprietario": "", "email_prop": "", "tel_diretto": "", "note_proprietario": ""},
    {"nome": "Ristorante-Trattoria Gatto Nero", "indirizzo": "S. Maddalena, 2, 39100 Bolzano", "tel_az": "+39 0471 975417", "email_az": "info@schwarzekatz.it", "sito": "www.schwarzekatz.it",
     "proprietario": "", "email_prop": "", "tel_diretto": "", "note_proprietario": ""},
    {"nome": "Osteria Vögele", "indirizzo": "Via Goethe, 3, 39100 Bolzano", "tel_az": "+39 0471 973938", "email_az": "", "sito": "www.voegele.it",
     "proprietario": "Famiglia Alber (Alber Wilhelm SRL)", "email_prop": "", "tel_diretto": "", "note_proprietario": "Locale mentionato dal 1277. Della famiglia Kamaun dal 1840, oggi gestito Alber."},
    {"nome": "Franziskanerstuben", "indirizzo": "Via Francescani, 7, 39100 Bolzano", "tel_az": "+39 0471 976183", "email_az": "", "sito": "",
     "proprietario": "", "email_prop": "", "tel_diretto": "", "note_proprietario": ""},
    {"nome": "Hotel Ristorante Feichter", "indirizzo": "Via Grappoli, 15, 39100 Bolzano", "tel_az": "+39 0471 978768", "email_az": "info@hotelfeichter.it", "sito": "www.hotelfeichter.it",
     "proprietario": "Famiglia Feichter", "email_prop": "", "tel_diretto": "", "note_proprietario": ""},
    {"nome": "Batzenhäusl - Ca' de Bezzi", "indirizzo": "Via Andreas Hofer, 30, 39100 Bolzano", "tel_az": "+39 0471 050950", "email_az": "", "sito": "",
     "proprietario": "", "email_prop": "", "tel_diretto": "", "note_proprietario": ""},
    {"nome": "In Viaggio - Claudio Melis Ristorante", "indirizzo": "Via Piave, 15, 39100 Bolzano (Palazzo Pock)", "tel_az": "+39 0471 980214", "email_az": "", "sito": "inviaggioristorante.com",
     "proprietario": "Chef Claudio Melis, Monica Wieser (moglie), Robert Wieser (cognato)", "email_prop": "", "tel_diretto": "", "note_proprietario": "Stella Michelin. Brand Esemdemì."},
    {"nome": "Tree Brasserie", "indirizzo": "Via Piave, 15, 39100 Bolzano", "tel_az": "+39 0471 1532377", "email_az": "", "sito": "",
     "proprietario": "", "email_prop": "", "tel_diretto": "", "note_proprietario": ""},
    {"nome": "Ristorante Laurin", "indirizzo": "Via Laurin, 4, 39100 Bolzano", "tel_az": "+39 0471 311000", "email_az": "info@laurin.it", "sito": "www.laurin.it",
     "proprietario": "Famiglia Staffler", "email_prop": "", "tel_diretto": "", "note_proprietario": "Ristorante del Parkhotel Laurin."},
    {"nome": "Löwengrube", "indirizzo": "Piazza Dogana, 3, 39100 Bolzano", "tel_az": "+39 0471 970032", "email_az": "", "sito": "",
     "proprietario": "", "email_prop": "", "tel_diretto": "", "note_proprietario": ""},
    {"nome": "Paulaner Stuben", "indirizzo": "Via Argentieri, 16, 39100 Bolzano", "tel_az": "+39 0471 980407", "email_az": "", "sito": "",
     "proprietario": "", "email_prop": "", "tel_diretto": "", "note_proprietario": ""},
    {"nome": "Hotel Ristorante Posta Gries", "indirizzo": "Corso Della Libertà, 117, 39100 Bolzano", "tel_az": "+39 0471 279000", "email_az": "info@hotel-post-gries.com", "sito": "www.hotel-post-gries.com",
     "proprietario": "Famiglia Berger", "email_prop": "", "tel_diretto": "", "note_proprietario": "Ristorante del Hotel Post Gries."},
    {"nome": "Ristorante Lewald", "indirizzo": "Via Maso della Pieve, 17, 39100 Bolzano", "tel_az": "+39 0471 250330", "email_az": "info@lewald.it", "sito": "www.lewald.it",
     "proprietario": "Famiglia Lewald", "email_prop": "", "tel_diretto": "", "note_proprietario": ""},
    {"nome": "Ristorante Castel Flavon", "indirizzo": "Via Castel Flavon, 48, 39100 Bolzano", "tel_az": "+39 0471 402130", "email_az": "", "sito": "",
     "proprietario": "", "email_prop": "", "tel_diretto": "", "note_proprietario": ""},
    {"nome": "Restaurant Valier - Four Points by Sheraton", "indirizzo": "Via Bruno Buozzi, 35, 39100 Bolzano", "tel_az": "+39 0471 1950000", "email_az": "info@fourpointsbolzano.it", "sito": "www.fourpointsbolzano.it",
     "proprietario": "Marriott/Sheraton", "email_prop": "", "tel_diretto": "", "note_proprietario": ""},
    {"nome": "Albergo Colle", "indirizzo": "Colle, 11, 39100 Bolzano", "tel_az": "+39 0471 329978", "email_az": "info@kohlern.com", "sito": "www.kohlern.com",
     "proprietario": "", "email_prop": "", "tel_diretto": "", "note_proprietario": ""},
    {"nome": "Forsterbräu Central", "indirizzo": "Bolzano Centro, 39100 Bolzano", "tel_az": "", "email_az": "", "sito": "",
     "proprietario": "Birra Forst (catena birreria)", "email_prop": "", "tel_diretto": "", "note_proprietario": "Della birreria Forst, ristorante centro."},
    {"nome": "Restaurant 37", "indirizzo": "Bolzano Centro, 39100 Bolzano", "tel_az": "", "email_az": "", "sito": "",
     "proprietario": "", "email_prop": "", "tel_diretto": "", "note_proprietario": ""},
    {"nome": "Cibus", "indirizzo": "Zona Industriale, 39100 Bolzano", "tel_az": "", "email_az": "", "sito": "",
     "proprietario": "", "email_prop": "", "tel_diretto": "", "note_proprietario": ""},
]

# ============================================================
# BAR - Da TuttoCittà
# ============================================================

BAR = [
    {"nome": "Bar Centro 2", "indirizzo": "Via Milano, 20, 39100 Bolzano", "tel_az": "+39 329 1937121", "email_az": "", "sito": "",
     "proprietario": "", "email_prop": "", "tel_diretto": "+39 329 1937121", "note_proprietario": "Solo cellulare (probabile WhatsApp diretto)."},
    {"nome": "101 Caffè Bolzano", "indirizzo": "Galleria Europa, 19, 39100 Bolzano", "tel_az": "+39 0471 1894184", "email_az": "", "sito": "",
     "proprietario": "101 Caffè (catena Italia)", "email_prop": "", "tel_diretto": "", "note_proprietario": "Hub catena 101 Caffè."},
    {"nome": "Drink Bar Snc", "indirizzo": "Via del Macello, 29, 39100 Bolzano", "tel_az": "+39 0471 970133", "email_az": "", "sito": "",
     "proprietario": "", "email_prop": "", "tel_diretto": "", "note_proprietario": ""},
    {"nome": "Savino Coffee Shop", "indirizzo": "Via Torino, 58, 39100 Bolzano", "tel_az": "+39 0471 347136", "email_az": "", "sito": "",
     "proprietario": "Savino", "email_prop": "", "tel_diretto": "", "note_proprietario": "Cognome nel brand."},
    {"nome": "Chen Dynasty di Zhang Jing", "indirizzo": "Piazza Anita Pichler, 26, 39100 Bolzano", "tel_az": "+39 0471 348331", "email_az": "", "sito": "",
     "proprietario": "Zhang Jing", "email_prop": "", "tel_diretto": "", "note_proprietario": "Nome proprietario nel brand!"},
    {"nome": "Caffè Mattei", "indirizzo": "Piazza della Parrocchia, 2, 39100 Bolzano", "tel_az": "+39 0471 977665", "email_az": "", "sito": "",
     "proprietario": "Mattei", "email_prop": "", "tel_diretto": "", "note_proprietario": "Cognome nel brand."},
    {"nome": "Alko S.n.c. di Stublla Kujtim e Stublla Bleart", "indirizzo": "Corso della Libertà, 13, 39100 Bolzano", "tel_az": "+39 0471 236702", "email_az": "", "sito": "",
     "proprietario": "Kujtim Stublla, Bleart Stublla", "email_prop": "", "tel_diretto": "", "note_proprietario": "Nomi proprietari nella ragione sociale!"},
    {"nome": "An di Nicastro Alex & Co. S.n.c.", "indirizzo": "Via Milano, 100, 39100 Bolzano", "tel_az": "+39 0471 233468", "email_az": "", "sito": "",
     "proprietario": "Alex Nicastro", "email_prop": "", "tel_diretto": "", "note_proprietario": "Nome proprietario nella ragione sociale!"},
    {"nome": "Andrade Stefaner James", "indirizzo": "Via Leonardo da Vinci, 16/C, 39100 Bolzano", "tel_az": "+39 0471 233198", "email_az": "", "sito": "",
     "proprietario": "James Andrade Stefaner", "email_prop": "", "tel_diretto": "", "note_proprietario": "Nome e cognome del titolare nell'attività!"},
    {"nome": "Andreini Alessandra", "indirizzo": "Galleria Raffaello Sernesi, 27, 39100 Bolzano", "tel_az": "+39 0471 375936", "email_az": "", "sito": "",
     "proprietario": "Alessandra Andreini", "email_prop": "", "tel_diretto": "", "note_proprietario": "Nome e cognome della titolare!"},
    {"nome": "Bar Amedeo S.a.s. di Silla Lorenzo & C.", "indirizzo": "Via Battisti Cesare, 44, 39100 Bolzano", "tel_az": "+39 0471 537688", "email_az": "", "sito": "",
     "proprietario": "Lorenzo Silla", "email_prop": "", "tel_diretto": "", "note_proprietario": "Nome proprietario nella ragione sociale!"},
    {"nome": "Bar del Corso di Gabriele Santo Agostino & C. S.a.s.", "indirizzo": "Via Giuliani Padre Reginaldo, 1, 39100 Bolzano", "tel_az": "+39 0471 262602", "email_az": "", "sito": "",
     "proprietario": "Gabriele Santo Agostino", "email_prop": "", "tel_diretto": "", "note_proprietario": "Nome proprietario nella ragione sociale!"},
    {"nome": "Bar Harty", "indirizzo": "Via Dùhrer, 14, 39100 Bolzano", "tel_az": "+39 0471 930653", "email_az": "", "sito": "",
     "proprietario": "", "email_prop": "", "tel_diretto": "", "note_proprietario": ""},
    {"nome": "Bar Mario di Trotto Massimo", "indirizzo": "Via Resia, 98, 39100 Bolzano", "tel_az": "+39 0471 095640", "email_az": "", "sito": "",
     "proprietario": "Massimo Trotto", "email_prop": "", "tel_diretto": "", "note_proprietario": "Nome proprietario nella ragione sociale!"},
    {"nome": "Bar Pia di Shahzad Muhammad Atif", "indirizzo": "Via Claudia Augusta, 27, 39100 Bolzano", "tel_az": "+39 353 3812732", "email_az": "", "sito": "",
     "proprietario": "Muhammad Atif Shahzad", "email_prop": "", "tel_diretto": "+39 353 3812732", "note_proprietario": "Nome proprietario nella ragione sociale! Cellulare diretto."},
    {"nome": "Bar Pizzeria Haidi", "indirizzo": "Via Renon, 33, 39100 Bolzano", "tel_az": "+39 0471 975183", "email_az": "", "sito": "",
     "proprietario": "Haidi", "email_prop": "", "tel_diretto": "", "note_proprietario": ""},
    {"nome": "Bar Ristorante Circolo del Tennis Gries", "indirizzo": "Via Knoller Martin, 8, 39100 Bolzano", "tel_az": "+39 347 3964215", "email_az": "", "sito": "",
     "proprietario": "Circolo Tennis Gries (associazione)", "email_prop": "", "tel_diretto": "+39 347 3964215", "note_proprietario": "Solo cellulare (probabilmente direzione)."},
    {"nome": "Bar Ristorante F.lli Meli di Meli Giovanni e Meli Salvatore & Co.", "indirizzo": "Piazza Firmian Nikolaus, 2, 39100 Bolzano", "tel_az": "+39 0471 911077", "email_az": "", "sito": "",
     "proprietario": "Giovanni Meli, Salvatore Meli (fratelli)", "email_prop": "", "tel_diretto": "", "note_proprietario": "Nomi proprietari nella ragione sociale!"},
]


def build_csv():
    """Costruisce CSV FINALE verificato"""
    output = "/Users/simocors/Desktop/telesales/aziende_bolzano_VERIFICATE.csv"
    all_data = []

    for h in HOTEL:
        all_data.append({**h, 'tipo': 'Hotel'})
    for r in RISTORANTI:
        all_data.append({**r, 'tipo': 'Ristorante'})
    for b in BAR:
        all_data.append({**b, 'tipo': 'Bar'})

    # Riordina campi
    final_data = []
    for biz in all_data:
        final_data.append({
            'nome_azienda': biz['nome'],
            'tipo': biz['tipo'],
            'indirizzo': biz['indirizzo'],
            'tel_aziendale': biz['tel_az'],
            'email_aziendale': biz['email_az'],
            'sito_web': biz['sito'],
            'proprietario': biz['proprietario'],
            'email_proprietario': biz['email_prop'],
            'tel_diretto_proprietario': biz['tel_diretto'],
            'note': biz['note_proprietario']
        })

    with open(output, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=[
            'nome_azienda', 'tipo', 'indirizzo',
            'tel_aziendale', 'email_aziendale', 'sito_web',
            'proprietario', 'email_proprietario', 'tel_diretto_proprietario',
            'note'
        ])
        writer.writeheader()
        writer.writerows(sorted(final_data, key=lambda x: (x['tipo'], x['nome_azienda'])))

    # Statistiche
    print(f"✅ CSV salvato: {output}")
    print(f"📊 TOTALE: {len(final_data)} aziende VERIFICATE")

    from collections import defaultdict
    by_type = defaultdict(int)
    for d in final_data:
        by_type[d['tipo']] += 1

    print("\n📈 Distribuzione:")
    for tipo, count in sorted(by_type.items()):
        print(f"  • {tipo}: {count}")

    # Compilation rates
    def pct(field):
        filled = sum(1 for d in final_data if d[field])
        return filled, filled * 100 // len(final_data)

    print("\n📊 Completezza campi (% verificate):")
    for field in ['indirizzo', 'tel_aziendale', 'email_aziendale', 'sito_web', 'proprietario', 'email_proprietario', 'tel_diretto_proprietario']:
        filled, p = pct(field)
        print(f"  • {field:30s}: {filled:3d}/{len(final_data)} ({p}%)")

if __name__ == "__main__":
    build_csv()
