# Slide 06 — Labour & Delivery (the delivered / post-natal patient)
## Explainer-video beat plan

**Core idea of the slide:** if she has delivered, walk the BIRTH (where, how, how hard, what was used),
then the RECOVERY (consciousness, bowel, bladder, walking, feeding, bleeding).
Donkey analogy: a flight report — the flight itself, then the landing & recovery.

**Registers:** `PIXEL` = hand-coded pixel scene (our cast) · `DIAGRAM` = clean animated line-art/infographic · `HYBRID` = pixel scene + diagram overlay.
Every beat: dark theme, shared palette, true 4K, loop-safe / length-flexible for narration, procedural SFX.

| # | Beat | Teaches | Visual | Register | Animates | Status |
|---|------|---------|--------|----------|----------|--------|
| 1 | **Two sweeps (intro)** | birth → recovery framing | our room transforms labour→birth→recovery | PIXEL | done | ✅ DONE (demo) |
| — | *PART A — THE BIRTH* | | | | | |
| 2 | **Site** | home vs hospital | same patient/bed in a home bedroom ↔ hospital room | PIXEL | cross-fade / toggle | plan |
| 3 | **Route of delivery** | vaginal → assisted (forceps/vacuum) → caesarean | 3-branch decision tree, mini-icon per branch; baby travels chosen path | DIAGRAM | branches draw in | plan ⭐ |
| 4 | **Easy vs difficult + duration** | how hard, how long | effort gauge + clock | DIAGRAM | needle swings, clock ticks | plan |
| 5 | **Episiotomy** | the cut + follow-up (bleeding, perineal pain, dysuria, haematuria) | small perineum diagram + symptom icons pop | DIAGRAM | icons appear | plan |
| 6 | **Anaesthesia — "don't assume general"** | GA vs spinal/epidural | two vignettes: asleep+mask ↔ awake+needle-in-back | HYBRID | flip / reveal | plan |
| — | *PART B — IF CAESAREAN* | | | | | |
| 7 | **Pre-op** | elective/emergency + indication, FHR, investigations, crossmatch, IV, catheter | pre-op checklist clipboard | DIAGRAM | items tick on | plan |
| 8 | **Intra-op** | time/duration, anaesthesia, smooth/difficult; bleeding/transfusion/organ injury | pixel OR scene + complication flags | HYBRID | flags light up | plan |
| 9 | **Why the C-section (indications)** | prev scar, breech/transverse, praevia, failure to progress, fetal compromise; NOT "elective"; sterilisation ≠ indication | fan-out cards, each a mini-diagram; wrong ones crossed | DIAGRAM | cards fan in | plan ⭐ |
| — | *PART C — THE RECOVERY* | | | | | |
| 10 | **Post-op recovery checklist** | consciousness, nausea/appetite, flatus/bowel, catheter/urine, IV/analgesia, walking, breastfeeding, fever | "systems rebooting" around pixel patient in recovery bed (reuse our recovery scene) | HYBRID | each system lights in turn | plan ⭐ (reuse) |
| 11 | **Post-partum haemorrhage** | ask specifically re heavy bleeding; recurrence risk | blood-loss gauge / jug filling, flag | HYBRID | gauge fills | plan |
| 12 | **Wound inspection** | pain, redness, swelling, pus, gaping, bleeding, fever | zoom to C-section wound + callouts | DIAGRAM | callouts appear | plan |
| 13 | **VTE warning + mobilisation** | unilateral leg pain/swelling, breathless/chest pain; early walking lowers clot risk | swollen leg + lungs flag; pixel patient gets out of bed & walks; clot-risk meter drops | HYBRID | pixel walk cycle, meter drops | plan ⭐ |
| — | *EXAM PEARLS* | | | | | |
| 14 | **The "show"** | blood-stained mucus plug = labour near | small close-up / icon | DIAGRAM | subtle | plan |
| 15 | **True vs false labour** | TRUE = regular contractions + progressive cervical dilatation & effacement; FALSE = contractions, cervix unchanged | side-by-side: dilating/effacing cervix + contraction-wave graph | DIAGRAM | cervix opens, waves | plan ⭐⭐ (highest value) |
| 16 | **MCQ / recap** *(optional)* | post-op markers = consciousness, flatus, micturition, bleeding | quick quiz card | DIAGRAM | option highlight | optional |

⭐ = hero / high-value beat.

## Decisions (locked)
- **Scope now = Parts A, B, C only** (beats 2–13). Beat 1 done (demo). Exam pearls (14 show, 15 true/false labour, 16 MCQ) = LATER, out of scope for now.
- **Clips are BACKGROUND B-roll.** User records VO separately, explaining the slide, and plays the clip under it while keeping the clip's own audio. ⇒ every beat must be **self-contained + SEAMLESS-LOOPING** (runs for any length he talks) with a **gentle ambient audio bed** (quiet, speak-over-able, NOT synced to specific words).
- **Max detail / quality** per beat (don't skimp).
- **Order = slide order** (2→13); may pull a later concept earlier if it must be explained first.
- **Build order:** slide order — Beat 2 (Site) first.

## Build log
- Beat 1 (two sweeps) ✅  — `birth_recovery.py` (+ sfx + music)
- Beat 2 (Site) ✅ — `beat02_site.py` + `beat02_audio.py` → `beat02_site_sfx_4K.mp4` (seamless home↔hospital loop).
- **HISTORY-TAKING TEMPLATE (now standard for every beat):** student/examinee at bedside ASKS (speech bubble = the slide's Say line) → the **HISTORY SHEET** HUD writes the answer → upcoming fields pending. New cast: `BR.student()`. HUD module `hud.py` (`history_sheet`, `speech_bubble`). Updated ref sheet `pixel_reference_sheet_v2.png`. No generated assets needed — all hand-coded.
- Beat 3 (Route of delivery) ✅ — `beat03_route.py` + `beat03_audio.py` → `beat03_route_sfx_4K.mp4`. Diagram register: 3 route cards (vaginal/assisted/caesarean) cycling, active card glows + "ANSWER" tag + check; sheet shows SITE✓ (continuity) + ROUTE filling; per-route pearl. Enriched text (Pixelify Sans 4K) + SFX. Established: continuity on the sheet across beats; the "answer" can be marked on a diagram card instead of a patient bubble.
- Beat 4 (Easy/difficult + duration) ✅ — `beat04_difficulty.py` + `beat04_audio.py` → `beat04_difficulty_sfx_4K.mp4`. Effort gauge (needle EASY<->HARD) + duration timer, cycles easy/short vs difficult/long; sheet SITE✓ ROUTE✓ -> DIFFICULTY. New reusable bits: `gauge()`, `timer()`.
- Beat 5 (Episiotomy) ✅ — `beat05_episiotomy.py` + `beat05_audio.py` → `beat05_episiotomy_sfx_4K.mp4`. Stitched-cut schematic (answer YES) + 4 follow-up symptom chips (bleeding/site pain/dysuria/haematuria) highlight-cycling, per-chip pearl. Sheet SITE✓ ROUTE✓ DIFFICULTY✓ -> EPISIOTOMY. **PART A (The Birth) COMPLETE** (beats 2-5 + anaesthesia beat 6 still pending... see note).
- Beat 6 (Anaesthesia) ✅ RICH — `beat06_anaesthesia.py` : depicts GENERAL (asleep+mask+Zzz) vs SPINAL (sitting, needle in back, numb legs). PART A COMPLETE.
- Beat 7 (C-section pre-op) ✅ RICH — `beat07_preop.py` + `beat07_audio.py` : pregnant patient prepped; depicts elective/emergency, fetal-heart CTG, investigations, crossmatch, IV, catheter; PRE-OP CHECKLIST ticks through.
- Beat 5 rebuilt RICH (`beat05_episiotomy.py`): symptoms depicted (bleeding/pain-starburst+OUCH+wince/dysuria-toilet/haematuria-cup).
- Beat 8 (C-section intra-op) ✅ RICH — `beat08_intraop.py` + `beat08_audio.py` : modest theatre scene (surgical lights, draped patient, surgeon hands) cycling time/duration, smooth-vs-difficult gauge, excessive-bleeding, transfusion, organ-injury; Intra-op Notes checklist. (Reverted to the FIRST draped-patient version — enlarged upper-body version rejected.)
- Beat 9 (C-section indications) ✅ RICH — `beat09_indications.py` + `beat09_audio.py` : cycles 5 real indications as mini-diagrams — previous scar (sutured belly), breech/transverse (baby head-up in `womb()`), placenta praevia (placenta over the os), failure to progress (clock + stalled dilation bar), fetal compromise (CTG with decelerations). Persistent red "NOT AN INDICATION" card ('elective' alone, sterilisation). New reusable bits: `womb()`, `baby()` (curled fetus), `clock()`. **PART B (If Caesarean) COMPLETE** (beats 7-9).
- Beat 10 (Post-op recovery check) ✅ RICH — `beat10_recovery.py` + `beat10_audio.py` : reuses the warm recovery-bed scene (mother cradling baby, `recovery_bg()` static/loop-safe); 8 recovery systems light in turn as icon badges (`icon()` + `spotlight()`) — consciousness, nausea/appetite, flatus/bowels, urine/catheter, IV/pain, mobilising, breastfeeding, fever; real elements glow (IV, catheter bag, baby); "Recovery Check" panel ticks through. s cycles every 1.5s (8 items = 12s).
- Beat 11 (Post-partum haemorrhage) ✅ RICH — `beat11_pph.py` + `beat11_audio.py` : hero blood-loss measuring `jug()` (500 mL PPH line, wobble, filled ~700=PPH); 6 questions cycle as icon chips (`icon()`+`chip()`) — soaked pads, clots in a dish, primary<24h vs secondary, faint/dizzy, treatment (bag+uterotonic), previous PPH/recurrence; persistent "RED FLAGS" card; "BLEEDING Hx" panel ticks. Object-based / modest. s cycles every 2s (6 items).
- Beat 12 (Wound inspection) ✅ RICH — `beat12_wound.py` + `beat12_audio.py` : framed close-up of the sutured wound (`wound_panel()`: skin band + stapled incision); 6 signs cycle as annotations ON the wound — tenderness (burst), redness band, swelling (puffy + arrows), discharge/pus, gaping (edges parted, modest dark lens), bleeding (stained gauze); persistent infection/breakdown/bleeding note; "WOUND CHECK" panel ticks. Modest (skin+line only). s cycles every 2s (6 items).
- Beat 13 (VTE + mobilisation) ✅ RICH — `beat13_vte.py` + `beat13_audio.py` : warning signs (DVT = `dvt()` normal vs swollen-red calf; PE = `pe()` lungs + clot + burst + SOB puffs) then mobilisation payoff (`walker()` hijab patient walk cycle + `clot_meter()` dropping HIGH->LOW green over t=6..12); ASK->ADVISE bubble switch; persistent RED FLAGS card; VTE checklist. s cycles every 3s (4 items); footstep SFX in walking half.

## **SLIDE 06 PARTS A-C COMPLETE (beats 1-13).** ✅
All beats rendered + muxed: `beatNN_*_sfx_4K.mp4`. Remaining = EXAM PEARLS (14 show, 15 true/false labour ⭐⭐, 16 MCQ) — parked, out of current scope.
Still-pending polish (optional): Beats 2,3,4 are older icon/gauge style (pre-rich-template); retrofit to the rich depictive style only if the user asks.

## FOCUS / LOCKED CLIPS (user-requested, in progress)
User wants per-concept "locked" clips to talk over (the montage auto-cycles too fast for VO). Treatment chosen = **Spotlight + tiny progress + student cue** (approved on the praevia demo). Each sub-concept = its own HELD 12s seamless clip: big centred visual + concept title + "N / M" progress dots + one pearl + a small top-left student bust & speech bubble ("THE EXAMINEE ASKS"), decluttered (no side panel/cards). Shared scaffold = `focus_kit.py` (glow/progress/ask_cue/frame/render_all, shared TLX, CX,CY=236,132). Per-beat file `beatNN_focus.py` supplies `hero(d,s,t)` (concept drawn centred around CX,CY at scale K), TITLES/PEARL/PLAB/SUF/CUE. Output `beatNN_focus_<k_name>_sfx_4K.mp4`, muxed with generic `focus_ambient.wav` (steady pad + 1 soft ding). USAGE = montage opener sets the frame, then cut to focus clips per point.
Done: ALL 13 beats have focus clips = **54 locked clips** (b02 home/hospital · b03 vaginal/assisted/caesarean · b04 easy/difficult · b05 4 · b06 general/spinal · b07 6 · b08 5 · b09 6 · b10 8 · b11 6 · b12 6 · b13 4). Montage versions kept for the openers.

## "NEXT QUESTION" PARTS (question-asking + bridge, 1080p)
User workflow: they do the EXPLAINING (focus clips / own visuals) then the QUESTION ASKING. Wanted: after the patient answers, a transition that notes it and moves to the next question - NO fade, NO re-typing, SAME environment. Final = `nextq.py` renders a per-topic "next question" beat in THAT topic's own environment (reconstructs each: hosp/ward bedside + history sheet for site/route/difficulty/anaesthesia/episiotomy; ward+pregnant+PRE-OP checklist for preop; warm recovery room for recovery; dark diagram + done-checklist + centre "RECORDED" tick for intraop/indications/pph/wound/vte), answer ticked + "NOW ASK: <next>" bubble + pigeon doctor. `make_all_parts.py` renders all 12, muxes `bridge3_ambient.wav`, then HARD-CUT concats montage + nextq and scales to **1920x1080** -> `partNN_<topic>_1080p.mp4` (NN = play order = history-sheet order: site,route,difficulty,anaesthesia,episiotomy,preop,intraop,indications,recovery,pph,wound,vte; VTE ends "HISTORY COMPLETE"). beat02 montage trimmed to 9.8s (end in hospital) before the cut. Superseded `bridge.py`(v1 abstract card, rejected)/`bridge2.py`(writing animation, rejected)/`bridge3.py`(Site-only prototype).

## CONTINUOUS VIDEO (final order: ASK -> EXPLAIN -> ANSWER -> BRIDGE)
User reordered to question->explaining->answer->bridge and wanted ONE continuous video. `nextq.py` extended with MODE: 'ask' (question asked, nothing recorded) and 'next' (answer recorded/ticked + "NOW ASK: <next>" = answer+bridge). `make_continuous.py`: renders 12 ask beats, builds per-topic segments [ask + focus(explaining, sorted) + nextq], all crossfaded 0.5s + scaled to 1080p, then crossfade-joins the 12 segments -> `SLIDE06_continuous_1080p.mp4` (11:46, 1920x1080). The MONTAGE clips are NOT used in this version (ask+nextq beats replace them; focus clips carry the explaining). Topic/play order = history-sheet order (site,route,difficulty,anaesthesia,episiotomy,preop,intraop,indications,recovery,pph,wound,vte). Could still top/tail with intro_walkin + midwife_leaves if asked.

## PER-SECTION MERGES (earlier output)
One video PER BEAT = that beat's montage opener + its focus clips, 0.5s crossfades (xfade + acrossfade). Built by `merge_part.py <codes...>` (xfade offset_k=k*11.5, preset veryfast crf20) -> `beatNN_section_crossfade_4K.mp4` (12 files, beats 02-13). Chosen over the single 13-min `merge_slide06.py` (that one kept getting killed by session teardown mid-render; the per-section files are short, fast, robust, and easier to edit with). The single-merge script still exists if ever wanted. ALL 12 SECTIONS DELIVERED.

---

# HISTORY-TAKING TEACHING SET (separate thread — the HOPI / chief-complaint clips)
Built on top of the beats: a set teaching *how to organise & take* the obstetric history. Scripts: `pph_vs_normal.py`, `labour_history_map.py`, `rule_headline_detail.py`, `worked_case.py` (bedside, patient answers → sheet), `worked_hopi.py` (flowing written HOPI, continuous paragraph, sub-phase tints, corner pigeon). Cast reuses `BR.student()` pigeon + `hud.py`. Chill music bed + SFX on each.

## The 6 HOPI "branch" types (from the deck's station-5 "branch according to the complaint")
Backbone (demographic → CC → HOPI → ROS → past obs/gynae → PMH/FH/SH) is FIXED every case; only the HOPI grows per complaint. The 6 branches:
1. Lower abdominal / labour pain → SOCRATES-style characterisation
2. Elective C-section (asymptomatic planned admission) → pre/intra/post-op story
3. Vaginal bleeding → amount·colour·clots·onset·timing·pain(painless=praevia/painful=abruption)·contractions·shock·fetal movements·precipitants
4. Watery discharge / ROM → colour·smell·amount·timing·±contractions·fetal movements·±bleeding
5. Pre-eclampsia symptoms → headache·visual disturbance·epigastric pain·swelling·±BP
6. Reduced fetal movement → onset·pattern·last felt·associated bleeding/pain

## EXAM FREQUENCY ANALYSIS (5 exams: 2022-23 2nd+3rd course, 2024 course1+course2, + Exam_1) — DONE
Tallied ~103 case stations by chief complaint across all 5 files:
| HOPI type | Count | Status |
|---|---|---|
| Abdominal / labour pain | ~34 | ✅ done (SOCRATES clip) |
| Elective C-section | ~30 | ✅ done (Huda worked case) |
| **Vaginal bleeding** | ~14 | ❌ BUILD NEXT (biggest gap) |
| **Watery discharge / ROM** | ~9 | ❌ build |
| **Pre-eclampsia symptoms** | ~8 | ❌ build |
| Post-date | ~4 | ⚠️ not in the 6; reads as a *reason* for CS/induction, fold into existing content |
| **Reduced fetal movement** | ~2 | ❌ build last (rare) |
| Hyperemesis (vomiting) | ~1 | out of scope (deck correctly excluded) |
| Cervical cerclage | ~1 | out of scope (early-pregnancy, rare) |

**Key finding:** the 2 clips already built ARE the 2 highest-frequency types. Highest-yield work is done.
**Build priority for the remaining 4:** (1) Vaginal bleeding ~14 → (2) Watery discharge/ROM ~9 → (3) Pre-eclampsia ~8 → (4) Reduced fetal movement ~2.
Each new clip = same format (`worked_case` bedside and/or `worked_hopi` written paragraph), silent B-roll (concept already taught by VO in the abdominal-pain & elective-CS clips), only the symptom-characterisation question-set changes per type.

## CC vs HOPI — EPISIOTOMY CORRECTION (verified against the deck)
Earlier the rule clip flipped EPISIOTOMY to the Chief Complaint (grouped with route, per the history-sheet layout line "vaginal delivery / cesarean section / episiotomy"). Re-checked against the deck (381063a9-...RESTORED-STRICT-SOURCE-ONLY.html) and reverted it: **episiotomy -> HOPI**, not CC.
Deck evidence (Slide 06, the current-delivery HPI): mode is "(spontaneous/assisted vaginal, or caesarean)" then **"separately - forceps/vacuum; episiotomy; type of anaesthesia; complications"** -> episiotomy is an intra-partum detail, listed separately from the mode. Plus the conditional "If an episiotomy was performed, also ask about bleeding, perineal/episiotomy-site pain, urine output, dysuria, haematuria." Slide 05 (chief complaint) branches do NOT include episiotomy. (Cases-book episiotomy case p.88 CC box is handwriting that didn't extract; exams only show episiotomy as discussion topics.)
**Rule now: only ROUTE / mode of delivery -> Chief Complaint; everything else (episiotomy, difficulty, anaesthesia, PPH, recovery) -> HOPI.** `rule_headline_detail.py` updated accordingly (EPISIOTOMY dest CC->HOPI; subtitle/footer reworded; removed the "route + episiotomy" CC merge) and re-rendered `rule_headline_detail_1080p.mp4`. Also made `birth_recovery.py` FFMPEG and `uitext.py` FONT_PATH portable (fall back to PATH/relative when the Windows paths are absent) so the project renders on Linux/cloud too.
