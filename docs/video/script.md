# Demo video script (final)

The demo is recorded by `scripts/record_demo.py`, which drives the real UI at 1280×720 with the captions burned in. Mangesh records the voiceover in his own voice (no synthetic voice), reading each line at its timestamp. The video runs 3:59.

**Mux your voice in** (after recording `voice.m4a` or `.wav`):
```bash
ffmpeg -i video/demo.mp4 -i voice.m4a -map 0:v -map 1:a -c:v copy -c:a aac -b:a 160k -shortest video/demo_final.mp4
```

| Time | Screen | Say |
|---|---|---|
| 0:02 | Title slide | Hi, I'm Mangesh. Operators lose hours digging through inspections, repair reports and SOPs. |
| 0:08 | Title slide | I built a copilot that answers in seconds, with the evidence and the right visual. |
| 0:14 | Architecture slide | The core idea: the language model never does arithmetic. A loader puts every dataset into SQLite. |
| 0:21 | Architecture slide | It extracts the rules from the manuals and SOPs, even containment times hidden in free-text repair reports. |
| 0:28 | Architecture slide | Deterministic, tested tools compute every number, and one composable query covers unseen questions. |
| 0:35 | Architecture slide | Open-weight Gemma 4 plans when the rules aren't sure, writes summaries, and reads inspection photos. |
| 0:42 | Architecture slide | Memory is scoped with provenance, and the copilot is honest when people disagree with the data. |
| 0:48 | App: empty state, history, user picker | This is the app: a clean chat with suggested questions, chat history and a user picker. |
| 0:54 | Field briefing view | The field briefing is computed proactively: breaches, open fines, long downtime, stale status. |
| 1:00 | App and field briefing | Every alert cites the record it came from. |
| 1:04 | App and field briefing | Let's run one question end to end, as Michael Turner, a production supervisor. |
| 1:30 | Compliance question for WELL-0001 | Four breaches, all from the 11 June spill: SR-01 reported after 41 hours, SR-03 and RC-04 overdue. |
| 1:37 | Evidence drawer (MNT-0001-029) | SR-02: contained after about 7 hours. That fact only exists in the repair report. Let's open it. |
| 1:43 | Reasoning trace and Gemma 4 summary | The evidence drawer shows the raw record and highlights the exact sentence in the report. |
| 1:50 | Reasoning trace and Gemma 4 summary | 'How I got this' shows the tool that ran and each rule with the document it came from. |
| 1:58 | Bar chart, downtime | Gemma 4 adds a plain-language summary. It's rejected if it invents any number. |
| 2:06 | Correction 4.5 → 5.4 bbl | A bar chart when you compare wells: WELL-0121 at 49 days, then WELL-0138 and WELL-0107 at 42. |
| 2:12 | Correction 4.5 → 5.4 bbl | Now feedback. The AI estimated a spill at 4.5 barrels; the crew measured 5.4. |
| 2:18 | Correction 4.5 → 5.4 bbl | It keeps the AI's estimate, records who corrected it and why, and re-checks the SOP rules. |
| 2:24 | Correction 4.5 → 5.4 bbl | At 5.4 barrels the spill is reportable, no notice was filed, so it flags a possible SR-01 breach. |
| 2:30 | Laura sees the correction | Switch to Laura Simmons, the HSE officer. The correction reaches her too. |
| 2:35 | Laura sees the correction | WELL-0151 is now listed because of Michael's correction, and the missing notice is flagged as overdue. |
| 2:43 | Jessica: private memory | Private memory: Jessica has no such conversation, so it never borrows Michael's history. |
| 2:51 | Jessica: private memory | Tyler says WELL-0175 is running. The latest inspection says otherwise, so it's flagged as a data conflict. |
| 2:58 | Tyler: data conflict | Both statements stay on record; his is marked unconfirmed and it asks him to confirm. |
| 3:31 | Closing slide | Gemma 4 is multimodal: it reads an inspection photo, and its notes stay advisory next to the records. |
| 3:38 | Closing slide | For the final hour, one command loads the test data, answers every question and fills in my results page. |
| 3:45 | Closing slide | Deterministic tools, rules from documents, scoped memory with provenance, and honesty. Thanks for watching. |
