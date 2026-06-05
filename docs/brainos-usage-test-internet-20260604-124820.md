# BrainOS internet-grounded usage test

- DB path: `/tmp/brainos-usage-20260604-124820.db`
- Verdict: **PASS**
- Corpus: 3 short internet-grounded statements about AI in Poland (regulation, adoption, infrastructure)
- Note: initial scripted pass missed exported env for recall/explain; rerun with `.env` loaded produced vector hits.

## Queries used
- `AI Act w Polsce nadzor i piaskownice regulacyjne`
- `adopcja AI przez polskie firmy i bariery wdrozeń`
- `polska infrastruktura AI i krajowe modele językowe`

## Top recall hits
### AI Act w Polsce nadzor i piaskownice regulacyjne
- score=540.8020985126495 dist=0.7919790148735046 :: W Polsce wdrożenie AI Act obejmuje projekt ustawy tworzącej Komisję Rozwoju i Bezpieczeństwa Sztucznej Inteligencji oraz uruchomienie piaskownic regulacyjnych dla systemów AI.
- score=230.85120677947998 dist=1.0414879322052002 :: Państwo deklaruje rozwój krajowej infrastruktury AI, wsparcie dla polskich modeli językowych oraz budowę ekosystemu suwerenności cyfrowej wokół portalu ai.gov.pl i planowanych fabr
- score=225.3081250190735 dist=1.0469187498092651 :: Polska ma rozdźwięk między wysokim zainteresowaniem AI a niższą systemową adopcją w przedsiębiorstwach; częste bariery to koszty, kompetencje, dane i dostęp do mocy obliczeniowej.

### adopcja AI przez polskie firmy i bariery wdrozeń
- score=464.4296371936798 dist=0.7557036280632019 :: Polska ma rozdźwięk między wysokim zainteresowaniem AI a niższą systemową adopcją w przedsiębiorstwach; częste bariery to koszty, kompetencje, dane i dostęp do mocy obliczeniowej.
- score=239.9735128879547 dist=0.9502648711204529 :: W Polsce wdrożenie AI Act obejmuje projekt ustawy tworzącej Komisję Rozwoju i Bezpieczeństwa Sztucznej Inteligencji oraz uruchomienie piaskownic regulacyjnych dla systemów AI.
- score=225.17260789871216 dist=1.0482739210128784 :: Państwo deklaruje rozwój krajowej infrastruktury AI, wsparcie dla polskich modeli językowych oraz budowę ekosystemu suwerenności cyfrowej wokół portalu ai.gov.pl i planowanych fabr

### polska infrastruktura AI i krajowe modele językowe
- score=445.9120309352875 dist=0.8908796906471252 :: Polska ma rozdźwięk między wysokim zainteresowaniem AI a niższą systemową adopcją w przedsiębiorstwach; częste bariery to koszty, kompetencje, dane i dostęp do mocy obliczeniowej.
- score=260.3578233718872 dist=0.7964217662811279 :: Państwo deklaruje rozwój krajowej infrastruktury AI, wsparcie dla polskich modeli językowych oraz budowę ekosystemu suwerenności cyfrowej wokół portalu ai.gov.pl i planowanych fabr
- score=237.91687965393066 dist=0.9208312034606934 :: W Polsce wdrożenie AI Act obejmuje projekt ustawy tworzącej Komisję Rozwoju i Bezpieczeństwa Sztucznej Inteligencji oraz uruchomienie piaskownic regulacyjnych dla systemów AI.

## Retrieval-explain snapshots
### AI Act w Polsce nadzor i piaskownice regulacyjne
- score=540.8020985126495 dist=0.7919790148735046 :: W Polsce wdrożenie AI Act obejmuje projekt ustawy tworzącej Komisję Rozwoju i Bezpieczeństwa Sztucznej Inteligencji oraz uruchomienie piaskownic regulacyjnych dla systemów AI.
- score=230.85120677947998 dist=1.0414879322052002 :: Państwo deklaruje rozwój krajowej infrastruktury AI, wsparcie dla polskich modeli językowych oraz budowę ekosystemu suwerenności cyfrowej wokół portalu ai.gov.pl i planowanych fabr

### adopcja AI przez polskie firmy i bariery wdrozeń
- score=464.42193031311035 dist=0.7557806968688965 :: Polska ma rozdźwięk między wysokim zainteresowaniem AI a niższą systemową adopcją w przedsiębiorstwach; częste bariery to koszty, kompetencje, dane i dostęp do mocy obliczeniowej.
- score=239.82909083366394 dist=0.9517090916633606 :: W Polsce wdrożenie AI Act obejmuje projekt ustawy tworzącej Komisję Rozwoju i Bezpieczeństwa Sztucznej Inteligencji oraz uruchomienie piaskownic regulacyjnych dla systemów AI.

### polska infrastruktura AI i krajowe modele językowe
- score=445.9120309352875 dist=0.8908796906471252 :: Polska ma rozdźwięk między wysokim zainteresowaniem AI a niższą systemową adopcją w przedsiębiorstwach; częste bariery to koszty, kompetencje, dane i dostęp do mocy obliczeniowej.
- score=260.3578233718872 dist=0.7964217662811279 :: Państwo deklaruje rozwój krajowej infrastruktury AI, wsparcie dla polskich modeli językowych oraz budowę ekosystemu suwerenności cyfrowej wokół portalu ai.gov.pl i planowanych fabr

## Health summary
- status: ok
- summary: benchmark green in vector-ready mode
- action_hint: noop
- issues: []

## Crashes / weirdness
- none
