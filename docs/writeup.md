# Asset Intelligence Copilot: System Design
*Mangesh Raut · FlytBase challenge, AHC × Hacktoberfest 2026 · MIT · github.com/mangeshraut712/asset-intelligence-copilot*

**Principle: the model never does arithmetic.** Every number comes from a deterministic, unit-tested tool over SQLite. Every threshold and deadline is extracted from the manuals and SOPs. Every answer cites record IDs and document passages. The open-weight **Gemma 4** model plans tool calls, phrases answers and reads photos, and is checked at each step.

**Storage and indexing.** A re-runnable loader ingests any number of dataset folders: wells, equipment, inspections (indexed by well and date), maintenance, regulator events, notes and documents. It follows each `report_file` and extracts facts that exist only in prose (*"contained about 7 hours after the inspection flight"*, also "after/within", minutes). It also builds a `rules` table from the documents: producing at Δ ≥ 15 °C (T200) and 20 °C (T350); reportable at ≥ 5 bbl; notice within 24 h; containment within 4 h; verification within 60 d; NOV response within 30 d; RCA at 3 repairs. New wells, areas or manuals need no code change; 400 wells load in about 1 s.

**Tools.** `effective_inspections` is the single source of truth: raw readings + correction notes + runtime corrections, with the originals kept. Specialised tools cover status, temperature series, spills, downtime (7 days per non-producing inspection, causes from overlapping repairs and notes), compliance (SR-01/02/03, RC-02, RC-04, RCA), containment, reportable spills and repair history. A **composable query** covers the long tail: metric (downtime, spills, volume, repairs, cost, fines, regulator events, not producing, stale status, notes) × scope (well, area, type, team, field) × window (right now, last N, season, month, quarter, half, between dates) × group-by (well, area, type, team, month, equipment).

**Agent (Gemma 4 by default).** 1) Feedback detection (correction, type-wide rule or well statement). 2) Private-memory recall. 3) A confident rule router. 4) Otherwise **Gemma 4 as planner** fills the structured query (function calling, with a JSON fallback). Its arguments are **validated**; an invalid or empty result triggers **one retry** through the rule router, and the rule router stays authoritative whenever it is confident. Gemma 4 runs via the **Gemini API** (`GEMINI_API_KEY`) or OpenRouter, or locally via Ollama. Gemma 4 also writes a plain-language summary, accepted only if it introduces **no number absent from the tool output**. **Multimodal:** Gemma 4 describes an uploaded inspection photo (equipment, staining, % of pad), shown as advisory next to the records and never overriding them. Picks are cached, and any LLM failure falls back to rules, so a rate limit can't block a run. The visual is the one the user asked for, or else the best fit (card, table, line, bar, map or heatmap).

**Memory with scope and provenance.**
| Level | Scope | Behaviour |
|---|---|---|
| Conversations | one user | "the wells we discussed yesterday" resolves only from that user's own chats |
| Well facts | all users | attributed, timestamped, *confirmed / unconfirmed / planned* |
| Corrections | one inspection field, all users | original + new value, author, reason; rules re-evaluated (4.5 → 5.4 bbl ⇒ SR-01/SR-03) |
| Type rules | every well of one type only | "T350: RCA after 2" changes T350 only; the answer cites the user, not the manual |

**Honesty about conflicts.** Claims are checked against the latest inspection. A contradiction is stored as *unconfirmed*, and the answer names the inspection that disagrees and the user who agrees, then asks for confirmation. A correction that clashes with an inspector note is flagged, and disagreeing notes are shown side by side. Only formal corrections override detections.

**Demo layer.** Proactive field briefing (SOP breaches, unreported spills, open fines, RC-03 downtime, stale status). A clickable evidence drawer with highlighted report and SOP passages. A **"How I got this"** trace (tools, arguments, rules with their source documents). Confidence and conflict badges, follow-up chips, and dark and light themes.

**Quality, cost, next.** 101 pytest tests, including an SR-02 regression test, a Gemma 4 number-guard test, the 18 examples (27/27) and 46 unseen questions whose answers were computed independently from the raw files (46/46). The final-hour command loads, answers and fills the results page in about 2 s. Model cost: $0 (free Gemma 4). Demo video (4:41, my own voice): https://vimeo.com/1236779581. Runs locally; no hosted deployment. Next: embedding retrieval over reports, multi-turn follow-ups, and Gemma 4 spill-area estimation from real drone imagery.
