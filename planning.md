# Project 1 Planning: The Unofficial Guide

> Write this document before you write any pipeline code.
> Your spec and architecture diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation - the more specific they are, the more useful the generated code will be.
> Update the Retrieval Approach and Chunking Strategy sections if you change your approach during implementation.
> Update this file before starting any stretch features.

---

## Domain

<!-- What domain did you choose? Why is this knowledge valuable and hard to find through official channels? -->

Syllabus of classes from previous years - Often, as professors change and the class content changes, it is often difficut to find the syllabus. University may not want to post previous syllabi due to the changes mentioned previously. Students may want to see previous syllabi very early on in order to identify what classes they want to take.

---

## Documents

<!-- List your specific sources: URLs, subreddit names, forum threads, or file descriptions.
     Aim for at least 10 sources that together cover different subtopics or perspectives within your domain. -->

| # | Source | Description | URL or location |
|---|--------|-------------|-----------------|
| 1 | BEPP 2330 (Spring 2023) | Business Economics & Public Policy 2330 - markets, regulation, policy analysis | `documents/BEPP 2330 Syllabus Spring 2023.pdf` |
| 2 | Corporate Valuation (2014) | Finance elective covering DCF, comparables, LBO, and valuation frameworks | `documents/Corporate Valuation Syllabus 2014.pdf` |
| 3 | FNCE 250 (Spring 2016) | Intermediate corporate finance - capital structure, payout, and risk | `documents/FNCE 250 Syllabus Spring 2016.pdf` |
| 4 | FNCE 101 (Fall 2021) | Introductory finance; time value of money, NPV, basic valuation | `documents/FNCE101_Syllabus_Asher_F21.pdf` |
| 5 | MEAM 210 | Mechanical Engineering & Applied Mechanics 210 - dynamics and modeling | `documents/MEAM 210 Syllabus.pdf` |
| 6 | MGMT 237 (Spring 2015) | Management elective - organizational behavior or strategy | `documents/MGMT-237-Syllabus-Spring-2015.pdf` |
| 7 | MGMT 100 | Introductory management; teamwork, leadership, organizational fundamentals | `documents/MGMT_100_Syllabus.pdf` |
| 8 | ACCT 101 (Fall 2010) | Introductory financial accounting - income statement, balance sheet, cash flows | `documents/Syllabus ACCT101 FALL 2010.pdf` |
| 9 | ACCT 102 (Spring 2017) | Intermediate accounting - managerial accounting and cost analysis | `documents/Syllabus and schedule -Spring 2017 ACCT 102.pdf` |
| 10 | General Chemistry 101 | Intro general chemistry - atomic structure, bonding, stoichiometry | `documents/Syllabus for General Chemistry 101.pdf` |
| 11 | FNCE 239/739 (2020) | Advanced finance seminar - cross-listed undergrad/grad topics | `documents/Syllabus_FNCE239-739_2020.pdf` |

---

## Chunking Strategy

<!-- How will you split documents into chunks?
     State your chunk size (in tokens or characters), overlap size, and explain why those
     numbers fit the structure of your documents.
     A review-heavy corpus warrants different chunking than a long FAQ. -->

     I want to use the Recursive Chunking Strategy as I want to first follow the syllabus natural document structure. A semantic or fixed size chunking strategy may not be the most appropriate for Syllabus style documents.

**Chunk size:** 500 characters

**Overlap:** 50 characters

**Reasoning:** Syllabi have short, discrete sections (course description, grading breakdown, weekly schedule, policies) - 500 chars keeps most paragraphs and policy blocks intact without splitting mid-sentence. Recursive splitting respects these natural boundaries: tries paragraph breaks first, falls back to sentences, then words, so grading tables and bullet-point policies stay coherent. 50-char overlap (10%) ensures boundary context carries over - e.g. a section header isn't orphaned from its content. Fixed-size would blindly cut mid-table; semantic would require embeddings at ingestion time. Recursive is the right fit for inconsistently formatted real-world PDFs like these.

---

## Retrieval Approach

<!-- Which embedding model are you using (e.g., all-MiniLM-L6-v2 via sentence-transformers)?
     How many chunks will you retrieve per query (top-k)?
     If you were deploying this for real users and cost wasn't a constraint, what tradeoffs
     would you weigh in choosing a different embedding model - context length, multilingual
     support, accuracy on domain-specific text, latency? -->

**Embedding model:** `all-MiniLM-L6-v2` via sentence-transformers (free, runs locally, no API key required)

**Top-k:** 3

**Production tradeoff reflection:** `all-MiniLM-L6-v2` is fast and free but has a 256-token context window - a chunk near the size limit may get truncated. For production with no cost constraint, I'd consider OpenAI's `text-embedding-3-large` (3072 dimensions, much higher accuracy) or `text-embedding-3-small` (1536 dimensions, better cost/quality tradeoff). Tradeoffs to weigh: (1) **Context length** - `3-large` handles longer chunks without truncation; (2) **Domain accuracy** - OpenAI models are trained on broader corpora and tend to retrieve more precisely on academic/structured text like syllabi; (3) **Latency** - local MiniLM wins at inference speed, but remote OpenAI adds network round-trip; (4) **Multilingual** - syllabi here are English-only so not a concern, but `paraphrase-multilingual-MiniLM-L12-v2` would matter for a global student corpus.

---

## Evaluation Plan

<!-- List your 5 test questions with their expected correct answers.
     Questions should be specific enough that you can judge whether the system's response
     is right or wrong. "What are good dining halls?" is too vague.
     "What do students say about wait times at [dining hall name] during lunch?" is testable. -->

| # | Question | Expected answer |
|---|----------|-----------------|
| 1 | What is the grading breakdown for ACCT 101? | Specific percentages for exams, homework, participation, or quizzes as listed in the ACCT 101 syllabus |
| 2 | What textbook is required for FNCE 101? | The required textbook title and author listed in the FNCE 101 Fall 2021 syllabus |
| 3 | What late work or attendance policy does MGMT 100 have? | The specific late work or attendance policy stated in the MGMT 100 syllabus |
| 4 | How many exams or assessments are there in FNCE 250? | The number and types of graded assessments listed in the FNCE 250 Spring 2016 syllabus |
| 5 | What topics are covered in the first weeks of General Chemistry 101? | The specific week-by-week topics from the course schedule in the General Chemistry 101 syllabus |

---

## Anticipated Challenges

<!-- What could go wrong? Name at least two specific risks with reasoning.
     Consider: noisy or inconsistent documents, missing source attribution, off-topic
     retrieval, chunks that split key information across boundaries. -->

1. **Noisy PDF text extraction from tables and formatted sections.** Syllabus grading breakdowns are often in tables (e.g., "Midterm | 30%"). pdfplumber may extract these as jumbled rows without clear structure (e.g., "Midterm 30% Final 40% Participation 30%"), making it hard for the model to parse or for retrieval to return a coherent grading chunk. Overlap won't help if the entire table lands in one chunk that reads as garbled text.

2. **Cross-course confusion on overlapping finance syllabi.** Five of the eleven documents are finance courses (FNCE 101, 250, 239/739, Corporate Valuation, BEPP 2330). A query like "what is the grading policy?" may retrieve chunks from the wrong course because all-MiniLM-L6-v2's 256-token context window limits how much disambiguating course-name context fits in a single chunk. The model may then cite the wrong syllabus without the user realizing it.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  INGESTION (ingest.py)                                      │
│                                                             │
│  documents/*.pdf                                            │
│       │                                                     │
│       ▼  pdfplumber                                         │
│  Raw text extraction + cleaning (regex)                     │
│       │                                                     │
│       ▼  recursive_split() - 500 chars / 50 overlap         │
│  Chunks [ ][ ][ ][ ] ...                                    │
│       │                                                     │
│       ▼  sentence-transformers (all-MiniLM-L6-v2)           │
│  Embeddings [0.23, 0.71, ...]                               │
│       │                                                     │
│       ▼  chromadb (persistent, ./chroma_db/)                │
│  Vector Store  ← stored with source filename metadata       │
└─────────────────────────────────────────────────────────────┘

         ┌──────────────────────────────────────────┐
         │  QUERY (query.py)                        │
         │                                          │
         │  User question (CLI)                     │
         │       │                                  │
         │       ▼  all-MiniLM-L6-v2                │
         │  Query embedding                         │
         │       │                                  │
         │       ▼  ChromaDB similarity search      │
         │  Top-3 chunks + source filenames         │
         │       │                                  │
         │       ▼  Groq (llama-3.3-70b-versatile)   │
         │  Grounded answer + [Source: ...] cite    │
         │       │                                  │
         │       ▼  stdout                          │
         │  Answer printed to terminal              │
         └──────────────────────────────────────────┘
```

---

## AI Tool Plan

<!-- For each part of the pipeline below, describe:
     - Which AI tool you plan to use (Claude, Copilot, ChatGPT, etc.)
     - What you'll give it as input (which sections of this planning.md, which requirements)
     - What you expect it to produce
     - How you'll verify the output matches your spec

     "I'll use AI to help me code" is not a plan.
     "I'll give Claude my Chunking Strategy section and ask it to implement chunk_text()
     with my specified chunk size and overlap" is a plan. -->

**Milestone 3 - Ingestion and chunking:**
- Tool: Claude Code
- Input: Chunking Strategy section from this planning.md + requirement to use pdfplumber + recursive splitting at 500 chars / 50 overlap
- Expected output: `ingest.py` with `extract_text()`, `clean_text()`, and `recursive_split()` functions
- Verification: run `python ingest.py`, confirm chunk count printed per file is reasonable (not 1 giant chunk, not hundreds of 1-word chunks)

**Milestone 4 - Embedding and retrieval:**
- Tool: Claude Code
- Input: Retrieval Approach section + `ingest.py` skeleton + requirement to use all-MiniLM-L6-v2 and ChromaDB
- Expected output: embedding loop in `ingest.py` and `query_system()` function in `query.py` that returns top-3 chunks with source metadata
- Verification: run a known-answer query and confirm the retrieved chunks come from the expected document

**Milestone 5 - Generation and interface:**
- Tool: Claude Code
- Input: Grounded Response Generation requirement + system prompt design + `query.py` skeleton
- Expected output: Groq API call (llama-3.3-70b-versatile) with grounding system prompt; answer always includes `[Source: ...]` citation; CLI loop in `main()`
- Verification: run all 5 eval questions; confirm each answer cites a source and does not hallucinate information not in the retrieved chunks
