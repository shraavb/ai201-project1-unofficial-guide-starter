# The Unofficial Guide - Project 1

> **How to use this template:**
> Complete each section *after* you've built and tested the corresponding part of your system.
> Do not write placeholder text - if a section isn't done yet, leave it blank and come back.
> Every section below is required for submission. One-liners will not receive full credit.

---

## Demo

[Video walkthrough](https://drive.google.com/file/d/1yECg-jQlHoMxJCojHGoJ8tzhPGoHeWeg/view?usp=sharing)

---

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env   # then add your GROQ_API_KEY
python ingest.py       # load, chunk, embed, and store all PDFs
python query.py        # start the interactive CLI
```

---

## Domain

University course syllabi from previous years. This knowledge is valuable because students often want to preview course structure, workload, grading policies, and required readings before enrolling - but universities rarely publish archived syllabi publicly, and content changes each semester as professors update their courses. The system makes this institutional knowledge searchable.

---

## Document Sources

| # | Source | Type | URL or file path |
|---|--------|------|-----------------|
| 1 | BEPP 2330 (Spring 2023) | PDF syllabus | `documents/BEPP 2330 Syllabus Spring 2023.pdf` |
| 2 | Corporate Valuation (2014) | PDF syllabus | `documents/Corporate Valuation Syllabus 2014.pdf` |
| 3 | FNCE 250 (Spring 2016) | PDF syllabus | `documents/FNCE 250 Syllabus Spring 2016.pdf` |
| 4 | FNCE 101 (Fall 2021) | PDF syllabus | `documents/FNCE101_Syllabus_Asher_F21.pdf` |
| 5 | MEAM 210 | PDF syllabus | `documents/MEAM 210 Syllabus.pdf` |
| 6 | MGMT 237 (Spring 2015) | PDF syllabus | `documents/MGMT-237-Syllabus-Spring-2015.pdf` |
| 7 | MGMT 100 | PDF syllabus | `documents/MGMT_100_Syllabus.pdf` |
| 8 | ACCT 101 (Fall 2010) | PDF syllabus | `documents/Syllabus ACCT101 FALL 2010.pdf` |
| 9 | ACCT 102 (Spring 2017) | PDF syllabus | `documents/Syllabus and schedule -Spring 2017 ACCT 102.pdf` |
| 10 | General Chemistry 101 | PDF syllabus | `documents/Syllabus for General Chemistry 101.pdf` |
| 11 | FNCE 239/739 (2020) | PDF syllabus | `documents/Syllabus_FNCE239-739_2020.pdf` |

---

## Chunking Strategy

**Chunk size:** 500 characters

**Overlap:** 50 characters

**Why these choices fit your documents:** Syllabi have short, discrete sections - course description, grading breakdown, weekly schedule, policies. 500 characters keeps most policy paragraphs and grading descriptions intact without splitting mid-sentence. Recursive splitting is used (`ingest.py → recursive_split()`), which tries paragraph breaks (`\n\n`) first, falls back to line breaks (`\n`), then sentence endings, then words. This respects the natural document structure instead of blindly cutting at a fixed offset. The 50-character overlap (10%) ensures that section headers are not orphaned from the content that follows them across a chunk boundary.

**Final chunk count:** 403 chunks total across 11 documents (range: 5–83 per document; average ~37)

---

## Embedding Model

**Model used:** `all-MiniLM-L6-v2` via `sentence-transformers` (runs locally, no API key required)

**Production tradeoff reflection:** `all-MiniLM-L6-v2` is fast and free but has a 256-token context window - chunks near the size limit risk truncation. For a production system with no cost constraint, I would weigh: (1) **Context length** - OpenAI `text-embedding-3-large` supports much longer inputs, reducing the risk of mid-chunk truncation; (2) **Domain accuracy** - larger models trained on broader corpora tend to retrieve more precisely on academic structured text like syllabi; (3) **Latency** - the local MiniLM model is faster at inference since there is no network round-trip, while API-hosted models add latency; (4) **Multilingual support** - the syllabi here are English-only, so this is not a concern for this project, but `paraphrase-multilingual-MiniLM-L12-v2` would be important for a global student corpus.

---

## Grounded Generation

**System prompt grounding instruction:**

```
You are a syllabus assistant for university courses.
Answer questions ONLY using the retrieved syllabus excerpts provided in the user message.
Do not use any outside or general knowledge.
If the excerpts do not contain enough information to answer the question, respond with:
"I could not find that information in the available syllabi."
Always end your answer by citing the source document(s) in brackets,
e.g. [Source: FNCE101_Syllabus_Asher_F21.pdf].
```

**How source attribution is surfaced in the response:** The system prompt instructs the model to always end every answer with a `[Source: filename.pdf]` citation. In addition, `query.py` prints the source filenames of the retrieved chunks below the answer, so the user can see which documents were consulted even if the model fails to cite them inline.

---

## Sample Chunks

Five chunks retrieved from ChromaDB (`syllabi` collection, `limit=5`):

**Chunk 1** - `BEPP 2330 Syllabus Spring 2023.pdf`
```
University of Pennsylvania
The Wharton School
Spring 2023
BEPP 2330: CONSUMERS, FIRMS AND MARKETS IN DEVELOPING
COUNTRIES
Class location: Huntsman 240 Class times: T/Th noon and 1:45pm
Instructor: Shing-Yi Wang Email: was@wharton.upenn.edu
Office hour location: Vance Hall 323
Office hours: Fridays 3:45-4:45pm or by appointment
Undergraduate Teaching Assistants:
Justin Lipitz, jlipitz@sas.upenn.edu
Office hours: Thursdays 10:15-11:45am in Huntsman G90
Rachel Pang, rpang@wharton.upenn.edu
```

**Chunk 2** - `BEPP 2330 Syllabus Spring 2023.pdf`
```
Huntsman G90
Rachel Pang, rpang@wharton.upenn.edu
Office hours: Wednesdays 1:45-3:15pm n Huntsman G90
Description
Nearly four-fifths of the world's population lives in low income or developing countries.
Though currently far behind the U.S., the 15 fastest growing economies/markets in the
world are all developing countries. And developing countries already account for 6 of the
world's 15 largest economies. This course will examine economic life, including
```

**Chunk 3** - `BEPP 2330 Syllabus Spring 2023.pdf`
```
This course will examine economic life, including
consumers, firms and markets, in low income countries. We will apply both economic
theory and empirical analysis for the roles of both business and government in consumption,
production and market equilibria.
Prerequisites
Students are expected to be familiar with basic regressions analysis. For students who have
not yet had exposure to regressions, a handout will be posted on Canvas covering the
knowledge on regressions expected in the course.
```

**Chunk 4** - `BEPP 2330 Syllabus Spring 2023.pdf`
```
e
knowledge on regressions expected in the course.
Reading Materials
The lectures provide the primary course content. Attending class is the most important
responsibility. There will be supplemental material drawn from a range of sources.
The book by Abhijit Banerjee and Esther Duflo, Poor Economics: A Radical Rethinking of
the Way to Fight Global Poverty, covers some of the material we cover in class. As does
```

**Chunk 5** - `BEPP 2330 Syllabus Spring 2023.pdf`
```
rs some of the material we cover in class. As does
the textbook by Debraj Ray, Development Economics (denoted by RAY in the reading list).
Given that we are only using a couple of chapters of the Ray textbook (and many of these
are suggested readings), I do not recommend that you buy the whole books but instead use
it on e-reserve at the library.
Grades and Assignments
There will be two problem sets, two exams and a team presentation. The schedule below
```

---

## Retrieval Test

Three eval questions run against ChromaDB (`TOP_K=3`). Chunks shown truncated to 300 chars.

---

**Q1: "What is the grading breakdown for ACCT 101?"**

| # | Source | Chunk preview |
|---|--------|---------------|
| 1 | `Corporate Valuation Syllabus 2014.pdf` | `oject – Part I 10% / Valuation Project – Part II 20% / Valuation Project – Part III 15% / Quiz # 1 10% / Quiz # 2 10% / Final Examination 30% / Total 100%...` |
| 2 | `Syllabus and schedule -Spring 2017 ACCT 102.pdf` | `Division to obtain its approval... RE-GRADES: I and the TAs follow a grading scheme that is designed to award partial credit...` |
| 3 | `Syllabus and schedule -Spring 2017 ACCT 102.pdf` | `ery poor weighted average scores (e.g., a weighted average score of less than 45%) will likely receive a final grade of F...` |

**Why off-target:** Query "ACCT 101" embeds closer to ACCT 102 and other accounting docs. The actual ACCT 101 chunks likely lack the phrase "grading breakdown," so cosine similarity favors Corporate Valuation (which has a literal grading table) and ACCT 102 (accounting keyword match).

---

**Q2: "What late work or attendance policy does MGMT 100 have?"**

| # | Source | Chunk preview |
|---|--------|---------------|
| 1 | `Corporate Valuation Syllabus 2014.pdf` | `to pick your company well in advance of that date as Part I of the project is due October 1... 5. Attendance a...` |
| 2 | `MEAM 210 Syllabus.pdf` | `not handed in on time will be considered late and will be given a grade of 0. This policy is firm...` |
| 3 | `MGMT_100_Syllabus.pdf` | `ng: Since Management 100 is highly interactive and experiential, class attendance is required. Lateness and unexcused absences will have a negative impact...` |

**Why partially works:** 1 of 3 chunks from correct doc. "Late work" and "attendance" are generic policy terms - other syllabi contain similar language, pulling in MEAM 210 and Corporate Valuation. The model correctly extracts from the one relevant chunk.

---

**Q3: "What topics are covered in the first weeks of General Chemistry 101?"**

| # | Source | Chunk preview |
|---|--------|---------------|
| 1 | `Syllabus for General Chemistry 101.pdf` | `Covalent Bonding: Orbitals, Molecular Spectroscopy / Chapter 21 - Organic and Biochemical Molecules... Chapter 16 - Liquids & Solids...` |
| 2 | `Syllabus for General Chemistry 101.pdf` | `Syllabus for General Chemistry 101 – Summer 2016 / Textbook: Zumdahl – Chemical Principles (7th Edition) / Introductory Material / Units of measurement...` |
| 3 | `MEAM 210 Syllabus.pdf` | `recitation section per week. Lectures will include a discussion of essential concepts, applications, and relevant example problems...` |

**Why works:** Correct doc retrieved twice. Chunk 2 contains the exact intro topic list (units, atoms, molecules). Chunk 1 is late-course material - noise within the correct document. MEAM 210 chunk is irrelevant but model ignores it.

---

## Evaluation Report

<!-- Run your 5 test questions from planning.md through your system and record the results.
     Be honest - a partially accurate or inaccurate result that you explain well is more
     valuable than a suspiciously perfect result. -->

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | What is the grading breakdown for ACCT 101? | Specific percentages for exams, homework, participation, or quizzes from ACCT 101 syllabus | "I could not find that information in the available syllabi." [Source: Corporate Valuation Syllabus 2014.pdf, Syllabus and schedule -Spring 2017 ACCT 102.pdf] | Off-target - retrieved Corporate Valuation and ACCT 102, not ACCT 101 | Inaccurate |
| 2 | What textbook is required for FNCE 101? | Required textbook title and author from FNCE 101 Fall 2021 syllabus | "I could not find that information in the available syllabi." [Source: Syllabus ACCT101 FALL 2010.pdf, Corporate Valuation Syllabus 2014.pdf] | Off-target - retrieved ACCT 101 and Corporate Valuation, not FNCE 101 | Inaccurate |
| 3 | What late work or attendance policy does MGMT 100 have? | Specific late work or attendance policy from MGMT 100 syllabus | "Lateness and unexcused absences in MGMT 100 will have a negative impact on your individual performance evaluation and final grade." [Source: MGMT_100_Syllabus.pdf] | Partially relevant - 1 of 3 retrieved chunks from correct doc | Partially accurate |
| 4 | How many exams or assessments are there in FNCE 250? | Number and types of graded assessments from FNCE 250 Spring 2016 syllabus | "I could not find that information in the available syllabi." [Source: Syllabus ACCT101 FALL 2010.pdf, FNCE101_Syllabus_Asher_F21.pdf] | Off-target - retrieved ACCT 101 and FNCE 101, not FNCE 250 | Inaccurate |
| 5 | What topics are covered in the first weeks of General Chemistry 101? | Week-by-week topics from General Chemistry 101 course schedule | "Introductory Material, Units of measurement, physical properties of Atoms and Molecules, Chapter 2 - Atoms, Molecules & Ions - Review. Isotopes from Chapter 20 also referenced." [Source: Syllabus for General Chemistry 101.pdf] | Relevant - correct doc retrieved | Accurate |

**Retrieval quality:** Relevant / Partially relevant / Off-target  
**Response accuracy:** Accurate / Partially accurate / Inaccurate

---

## Failure Case Analysis

**Question that failed:** "What is the grading breakdown for ACCT 101?"

**What the system returned:** "I could not find that information in the available syllabi." - retrieved chunks from `Corporate Valuation Syllabus 2014.pdf` and `Syllabus and schedule -Spring 2017 ACCT 102.pdf`, not from `Syllabus ACCT101 FALL 2010.pdf`.

**Root cause (tied to a specific pipeline stage):** Retrieval failure. Five of the eleven documents are finance or accounting courses with heavily overlapping vocabulary (grades, exams, assignments, participation). The `all-MiniLM-L6-v2` embedding model has a 256-token context window, so a 500-character chunk often does not contain enough disambiguating course-name context alongside the grading content. The query embedding for "grading breakdown for ACCT 101" matched generic grading-related chunks from other courses more closely than the ACCT 101 chunks that contained the actual breakdown. The chunk containing the grading table likely did not also contain the course identifier "ACCT 101," so the model had no signal to distinguish it from ACCT 102.

**What you would change to fix it:** Prepend each chunk's course name as a prefix before embedding - e.g., `"[ACCT 101 Fall 2010] Grading: Midterm 30%..."`. This anchors the course identifier to every chunk embedding regardless of where chunk boundaries fall, making course-specific queries far more precise.

---

## Spec Reflection

**One way the spec helped you during implementation:** The architecture diagram in planning.md (Ingestion → Chunking → Embedding → ChromaDB → Retrieval → Generation) directly mapped to the function structure in `ingest.py` and `query.py`. Having the tool choices labeled on each stage (pdfplumber, all-MiniLM-L6-v2, ChromaDB, Groq) meant implementation was filling in each box rather than making tool decisions mid-build.

**One way your implementation diverged from the spec, and why:** The spec and starter repo specified Groq (llama-3.3-70b-versatile) as the LLM. During implementation, the Groq API key was unavailable (an xAI key was mistakenly used instead), so the system was temporarily built with Gemini (gemini-2.0-flash via google-genai). Once a valid Groq key was obtained, query.py was reverted to match the spec.

---

## AI Usage

**Instance 1**

- *What I gave the AI:* The Chunking Strategy section from planning.md, specifying recursive splitting at 500 characters with 50-character overlap, plus the requirement to use pdfplumber for PDF extraction.
- *What it produced:* `ingest.py` with `extract_text()`, `clean_text()`, and `recursive_split()` implemented using a separator-based fallback approach (`\n\n` → `\n` → `. ` → ` ` → character split).
- *What I changed or overrode:* Verified the separator order and overlap logic matched the spec exactly. Confirmed chunk size constants (CHUNK_SIZE = 500, CHUNK_OVERLAP = 50) were used consistently and not hardcoded in multiple places.

**Instance 2**

- *What I gave the AI:* The Retrieval Approach section from planning.md and the system prompt grounding requirement, asking it to implement `query_system()` with Groq and a grounding-only instruction.
- *What it produced:* `query.py` with the system prompt, context formatting, and CLI loop.
- *What I changed or overrode:* Initially switched the LLM from Groq to Gemini (google-genai) due to API key issues, then reverted back to Groq once a valid key was available. Verified the system prompt explicitly says "ONLY using the retrieved syllabus excerpts" and confirmed source attribution was printed both inline (by the LLM) and programmatically below the answer.
