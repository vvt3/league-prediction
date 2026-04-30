# League Draft Intelligence Tool (v1)

A lightweight, heuristic-based system that analyzes team compositions in **League of Legends** and predicts win probability with human-readable reasoning.

---

## Overview

This project explores how raw game data can be transformed into meaningful insights about team compositions.
Given two teams of five champions, the system evaluates factors like:

- Crowd control (CC)
- Frontline / durability
- Damage profile (AD vs AP)
- Composition balance

It then outputs:

- A win probability estimate
- Key reasons explaining the result

---

## Why this project exists

Most tools either:

- Show raw stats, or
- Use opaque models

This project focuses on:

> **Explainable, system-driven analysis**

The goal is not perfect accuracy, but:

- Consistency
- Interpretability
- Demonstrating system design and data reasoning

---

## Features

- Multi-source data pipeline:
  - Riot Data Dragon (champion stats + tags)
  - Community Dragon (playstyle + CC data)

- Data cleaning & normalization:
  - Extracted and normalized ability status effects
  - Removed noise and inconsistent tags

- Heuristic-based analysis engine:
  - Team aggregation (CC, tankiness, damage)
  - Composition balance checks
  - Conditional logic (e.g. CC effectiveness depends on frontline)

- Explainable outputs:
  - Returns reasons alongside predictions

---

## Example Output

```bash
Win Probability: 0.64

Reasons:
- Stronger CC with frontline to apply it
- Enemy lacks frontline
- Slightly unbalanced damage profile
```

---

## Project Structure

```
/project-root
  main.py                   # Core analysis logic
  clean_champions.py        # Data cleaning pipeline
  fetchChampions.py         # Riot data fetch
  fetchCDragon.py           # Riot data fetch
  champions.json            # Processed champion dataset
  raw_champions.json        # Raw Riot data
  community_champions.json  # Raw Community Dragon data
  requirements.txt
```

---

## How It Works

### 1. Data Ingestion

Champion data is fetched from:

- Riot Data Dragon (base stats, roles)
- Community Dragon (playstyle info, crowd control)

---

### 2. Data Cleaning

- Extract `<status>` tags from ability tooltips
- Normalize inconsistent labels (e.g. "slowed", "slows" → "slow")
- Filter out invalid/noisy tokens

---

### 3. Feature Engineering

Each champion contributes to team-level features:

- `ad` / `ap` → total damage profile
- `tank` → durability + frontline presence
- `cc` → crowd control potential
- `compPhysical` / `compMagic` → composition balance

---

### 4. Heuristic Evaluation

Teams are compared using rule-based logic:

- CC advantage (context-aware)
- Frontline differences
- Damage balance penalties
- Overall damage output

The result is converted into a probability using a sigmoid function.

---

## Running the Project

### 1. Setup virtual environment

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Mac/Linux
source venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run analysis

```bash
python main.py
```

---

## Limitations (v1)

- Heuristic-based (no machine learning yet)
- No patch/meta/item awareness
- Simplified assumptions for engage and scaling
- CC detection relies on text parsing

---

## Future Improvements

- Add team engage and scaling models
- Use AD/AP figures to determine damage output
- Improve role detection (top/jg/mid/adc/sup) (from Riot live data)
- Build a frontend UI (React or Discord bot)
- Introduce ML-based predictions alongside heuristics (optional)
- Incorporate match history for data-driven tuning (optional)

---

## Tech Stack

- Python
- Requests (data fetching)
- JSON-based data pipeline

---

## What this demonstrates

- Data ingestion from multiple sources
- Data cleaning and normalization
- Feature engineering from unstructured inputs
- System design using heuristics
- Explainable AI-style reasoning

---

## Author

V T
GitHub: https://github.com/vvt3

---

## License

MIT
