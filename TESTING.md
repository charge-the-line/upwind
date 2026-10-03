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

## U2 part one checks (added October 3, 2026)

- `tests/uw_bot.js` plays an incident through `runAct` only, the handlers behind the buttons, the handles and the map taps, at about 1.2 s per tap on `global.__T`, running `runTick` between taps. Options: `variant`, `route` (good, down, cross), `choice` or `choiceAt:{stepId:kind}`, `binoMiss`, `binoWrong`, `ergWrong`, `hot`, `warm`, `stageDownwind`, `stageCross`, `stageInside`, `notifyMiss`, `notifyExtra`, `notifySkipTeam`, `noTeam`, `dwell` (seconds added after each decision, to reach the Chaos wind shift), `fast`.
- `tests/zones.js` is the independent zone rule, written from CLAUDE.md, not from `zoneFit`. Distances are judged in whole feet, the number the player sees; one disagreement in 400 came from comparing a fraction of a foot, so the rule says so.
- `gate`: the facts rule applied to incidents. An incident whose material is unchecked is built and tested but listed as locked; `runStart` refuses it. The test clears `MAT.gasoline.checked` first to prove the lock, since the entry has been checked for real since 0.3.1.
- `clean`, `mistakes`, `chaos`, `smooth` as listed in CLAUDE.md. The smooth check wraps `innerHTML` on the run screen's containers and counts writes during 10 s of ticks: zero.
- Browser check: the incident at both widths with a real drag of the hot handle (press, move in eight small steps, release), a tap on the map upwind for staging, the warm nudge buttons until the fit is good, every decision answered by its visible text, the notifications ticked by text, and a 100 on the result screen.
- Prove it can fail: change `PEN.routeDown` and the downwind test fails; move the staging tap downwind in the browser check and the fit row fails; set a plume half-angle floor above 60° and the side-thinning check fails.

## 0.3.1 checks (added October 3, 2026, Guide 128 checked by Max)
- `facts`: `MAT.gasoline` carries the three Guide 128 lines Max read (150 ft, 1000 ft large-spill evacuation, 800 m tank fire) and a `checked` stamp naming him, the app and the guide.
- `home`: the I-75 incident is live and the six incidents still to build stay disabled with a Soon chip.
- `drills`: the ERG drill asks "UN1203, Gasoline: which guide?" with two distinct wrong guide numbers (padded from nearby guides while gasoline is the only checked material), and asks no guide question when nothing is checked.
- `mistakes`: layout B adds the downwind evacuation decision; choosing shelter costs 10 and the debrief line reads "Right call: Evacuate the truck stop crosswind, now. The guide says consider downwind evacuation for 1000 feet…".
- Browser check: the incident now opens from the home list with no unlock hook, the way a phone does. The staging tap scrolls the map back into view first, because the warm nudge taps can scroll the top of the map away at 320 px (that was a harness miss on layout C, not an app bug).

## 0.4.0 checks (added October 3, 2026, the nurse tank; Guide 125, Table 1 and Table 3 read by Max)
- `facts`: ammonia carries the Guide 125 lines, the Table 1 small-spill row and the Table 3 nurse-tank row; `iso` is the nurse-tank row; any checked entry carries `iso`.
- `gate`: a checked stamp alone does not unlock the nurse tank; it needs `iso` and `t3` (the test clears them and watches the card stay disabled and `runStart` refuse, then restores them).
- `balance`: every decision of every incident in every layout, right call longest or shortest no more than 45 %. It caught 25 of 33 longest before the wording was rebalanced; keep running it after any new decision.
- `clean`: nurse tank, three layouts × three tiers, 100 at human pace; layout C includes the farmer step.
- `mistakes` (nurse tank): trusting a zero on the 4-gas; a crew in on air to close the valve (Operations boundary, −30); the cloud left to the team named under "Defensive actions missed"; a straight stream on the fitting; the family sent through the cloud on layout A (right call: shelter, with the 0.3-mile day distance quoted) and sheltered on layout B when a road out was open (right call: evacuate, with the 0.2-mile night distance quoted); driving through the cloud; going in on air for the farmer on layout C; the ambulance before decon; the co-op and the farm agency left off the first report.
- `tests/uw_bot.js` exports `standIn(api)`, which fills labeled stand-in numbers for a material whose green-page rows are unread; with ammonia read it does nothing. Stand-ins are never ERG values and never reach the page.
- Browser check: the incident flow is `incident(pg, w, scn, pre, unlock, force)`; I-75 runs at both widths and the nurse tank layout C at 390 px, opened from the home list the way a phone does.
