# Test av ny emoji-arkitektur (2026-11-07)

Användaren valde att prova att Swype behåller sin befintliga emoji-panel men får en **ny katalogleverantör** som ger rätt kategoriordning och använder Androids font/glyph-stöd.

## Reproducerbart prototyptest utfört

Koden är `EmojiCatalogBridge.java` + `EmojiCatalogBridgeTest.java` i det exporterade samtalspaketet `Swype-SystemEmoji-Brygga-Testkod.zip`.

Funktioner:
- Moderna Unicode-sekvenser kommer som `Entry(unicode, category, sortOrder)` från en framtida komplett katalog; `sortOrder` avgör **synlig ordning**, inte Swypes gamla centralregister.
- Androids stöd frågas genom `GlyphSupport.canDisplay()` (kopplas i APK:n till korrekt OEM-fontkontroll).
- Ursprungliga Swype-emojis som saknas i importen bevaras som reserv i respektive kategori.
- Dubbletter undviks, kategorierna returnerar oföränderliga listor.
- Ingen extra emoji-panel, inget extra tangentbord.

Lokalt körd kontroll:

```
javac -encoding UTF-8 -d classes EmojiCatalogBridge.java EmojiCatalogBridgeTest.java
java -ea -cp classes com.swypedragon.emoji.EmojiCatalogBridgeTest
# PASS: modern order independent of legacy array; OEM glyph filtering; no duplicate; old fallback
```

Testfall återskapar det riktiga 🥰-felet genom att lägga 🥰 och 🤩 sist i gamla Swype-listan, men nära andra ansikten i en modern ordnad katalog. Bryggan levererar rätt ordning ändå.

**VIKTIG BEGRÄNSNING:** Testet är en fristående Java-enhetstest. Det är **inte en installerbar Swype-APK**, ingen fullständig Unicode/CLDR-import, och fungerar inte i Samsung-telefonen förrän kopplingarna till `EmojiCategoryStandard.getEmojiList()` / `EmojiPagerAdapter` / `EmojiPageView.setItems()` har implementerats och prövats. Vi har inte löst det befintliga runtime-ordningsfelet genom det här testet.

## Nästa integrationsgräns

1. Bevara den på Samsung bekräftat fungerande `Swype-Emoji-9-STABLE-RECENTS-v3-DIAG-signed.apk` som orörd bas.
2. Integrera bryggans kategoriordnade och glyfkontrollerade listor där Swypes gamla kategoridata lämnas till pagern; skilj recents från statiska kategorier.
3. Importera den officiella, fullständiga Unicode emoji-test/CLDR-ordningen (inklusive fullständiga sammansatta sekvenser) med Swype-kategorimappning.
4. Kontrollera att 🥰 ligger nära liknande ansikten i `EmojiPageView.setItems()` på den *riktiga* telefonen, inte bara i resurstabellen.
5. Testa Senaste, emojiinfogning, 3+ teman och olika Android-versioner innan någon APK godkänns.

GIF, språk och RDR-temat är fortfarande utanför.
