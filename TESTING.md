# Upwind — testing guide

`node tests/run_all.js` runs the suite in about a second (U0: 38 checks). `python3 tests/browser_check.py` opens the real page in Chromium at 320, 390 and 844 px with slow taps and fails on any JavaScript error, overflow, or button under 44 px.

Rules this module adds to the platform's (see CLAUDE.md for the platform rules):

0. **Facts have one home.** Every ERG guide number, class and distance comes from `MAT`. An entry a drill or incident lists in `mats` must carry `checked` (who read it from the printed ERG2024 or the PHMSA app, and when). The `facts` section fails otherwise, and also fails if the page prints any distance before its line is checked. Prove it can fail: set `checked` on a used entry to `null` in a scratch copy.
1. **No phone numbers, no NFPA section numbers in the app.** Both are scanned for.
2. **The Operations boundary is tested as content now and as behavior from U2** (every forbidden action played, penalized and explained; "Call the team · Isolate · Deny entry" never penalized; missed defensive actions named in the debrief).
3. **Zones are checked against an independent recalculation** from U2 (`tests/zones.js`), never against the app's own function.
4. **Wind, plume and meter run on real seconds**; bots advance `global.__T` like BLS Ready's.

## U0 checks (added October 3, 2026)
- syntax: script compiles; `APP_VERSION` and `sw.js` `CACHE` match; the helper clears only `upwind-v*` and never caches statistics; the shared core loads first, is cached, its hash matches and it is byte-identical to the hub's copy; fonts self-hosted and cached; statistics snippet with module code `uw`; drill-night bar, picker and the full settings sheet present; manifest and icons exist; the harness boots.
- facts: every material names its ERG2024 source; nothing in use is unchecked (nothing is in use yet); no distance printed; the "use your current ERG" line; generic meter defaults and the "know yours" line, no brand names.
- content: the boundary statements; no phone numbers; the to-confirm list in About; no NFPA section numbers; notices; a Close on every overlay; wake lock off at home.
- home: readiness 0 of 16; eight drills and seven incidents listed, disabled, "Soon"; three tiers with help text; the pocket reference (ERG order, zones, meter, always-right line, no distances); ERG edition printed; the instructor switch saves and is remembered; a Drill Night turns it on by itself and shows the bar.
- record: shared run shape; drill-night stamping; best-score chips; progress screen and CSV.
- privacy: the snippet cleans paths, uses coarse bands, honors the opt-out; the app never passes a name or typed text to it.
- browser: home, settings, reference, about, progress, Chaos tier, instructor switch, drill picker and bar, large text, Daylight, the daily-link stub, landscape and landscape settings.

## U1 checks (added October 3, 2026)

- `balance`: the lesson's options plus twenty generated banks of every drill; the right answer may be the longest or the shortest in at most 45 % of questions. The `ppe` drill picks one of two equal-meaning phrasings per option each run so no answer is always the longest; the `meter` action strings are kept within a few characters of each other for the same reason. Ties count as longest, so equal lengths are avoided on purpose.
- `lesson`: all slides right scores 100 and is recorded; all first tries wrong scores 0; Next stays disabled until the check is answered; Leave the lesson returns home; twelve slides with three options, one good, a why, and the "know yours" line on the meter slide.
- `drills`: every bank has at least eight distinct questions with two distractors that never include the answer; placard class keys are re-derived from the test's own class table (30 generations), meter keys from the test's own alarm points (40 generations), zone keys from the test's own compass (30), 704 keys from the highest field (30); the ERG drill asks no guide numbers while `MAT` has no checked entry; no question, answer or distractor carries an ERG distance.
- `quiz`: a right run scores 100 and records `{kind:'drill'}`; a wrong run scores 0; options are shuffled once and a second tap on the same question is ignored; Quit closes and goes home; `?drill=placard` opens that drill and an unknown id is ignored; chips read Due and Again from `pcSpacing`; the statistics calls are `begin:uw/drill-…`, `abandon`, `begin:uw/lesson` with nothing typed in them.
- Browser check: lesson row (answer by visible text, Next advances), one row per drill answered by visible text, the meter drill played to the end with real taps and a saved run, the daily link opening the drill.
- Prove it can fail: set a `MAT` entry's `checked` and watch the ERG drill start asking its guide; flip one `H704` meaning and the 704 recalculation fails; change a placard class in `PLACARDS` and the placard recalculation fails.
