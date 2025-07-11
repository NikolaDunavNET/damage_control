from opticka_analiza_izvestaja import process_raw_output

ulaz = """" D.O.A.A.1.Rend, Beograd, ilica Žorža Komensova, broj 19, predmet, služba na Belaškove se događuje od
    17.8.2024. godine, obaveštavamo vas da je danas 17.8.2024. godine, oko 19.4. i 31 minut, dežurna služba saobraćene
    policijske ispostave u Zrenjaninu obaveštena da se u Tomaševcu ulici Žarka Zrenjaninu naspram kućnog broja 70
    dogodila saobraćena nezgoda u kojoj su učestvovali putničko vozilo registracijalnih oznaka BG-1903-CB, kojim je
    upravljala nepoznatovice, putničko vozilo regionalna oznaka ZR216-DO kojim je upravljala opet nepoznatovice.
    Obzirom na činjenicu da se u konkretnom slučaju radi o saobraćene nezgodi sa malom materijalnom štetom bez povređenih
    i poginulih lica, shodno članu 172 ZOPS-a na putevima učestniti su popunili evropski izvaštaj o saobraćene nezgodi,
    a koji je predviđen članom 31 zakona o obaveznom osiguranju saobraćenja. I pred policijskim službenicima potpisali
    sužbenu belešku o saobraćenju nezgodi bez povređenih lica, samo sa manjom materijalnom štetom za koju se ne vrši
    uviđaj parama. Napredna vedenom, shodno članu 170-181 ZOPS-a na putevima policijskih službenici nisu vršli uviđaj,
    nisu potvrđivali usrok saobraćenju nezgodi, tj. učesnici su po razmeni podataka i upnjavanju evropskog izvaštaja
    napustili velice nezgodi. Ďakujem."""

llm_izlaz = process_raw_output(ulaz)

llm_izlaz['transkript'] = ulaz
print(llm_izlaz)