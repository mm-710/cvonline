# Phase: Description Optimization

The description field in SKILL.md frontmatter is the primary triggering mechanism. After creating or improving a skill, offer to optimize it for better triggering accuracy.

---

## Step 1: Generate trigger eval queries

Create 20 eval queries — a mix of should-trigger and should-not-trigger. Save as JSON:

```json
[
  {"query": "the user prompt", "should_trigger": true},
  {"query": "another prompt", "should_trigger": false}
]
```

Queries must be realistic and concrete — specific file paths, personal context, column names, company names, backstory. Mix of lengths, some lowercase or with typos, focus on edge cases.

**Bad:** `"Format this data"`, `"Extract text from PDF"`, `"Create a chart"`

**Good:** `"ok so my boss just sent me this xlsx file (its in my downloads, called something like 'Q4 sales final FINAL v2.xlsx') and she wants me to add a column that shows the profit margin as a percentage. The revenue is in column C and costs are in column D i think"`

**For should-trigger (8–10):** Different phrasings of the same intent — formal and casual. Include cases where the user doesn't name the skill but clearly needs it. Include uncommon use cases and competition cases.

**For should-not-trigger (8–10):** Near-misses are the most valuable. Queries that share keywords but actually need something different. Adjacent domains, ambiguous phrasing, contexts where another tool is more appropriate. **Never use obviously irrelevant negatives** — "Write a fibonacci function" against a PDF skill tests nothing.

---

## Step 2: Review with user

Present the eval set using the HTML template:

1. Read `assets/eval_review.html`
2. Replace placeholders:
   - `__EVAL_DATA_PLACEHOLDER__` → the JSON array (no quotes — it's a JS variable)
   - `__SKILL_NAME_PLACEHOLDER__` → skill name
   - `__SKILL_DESCRIPTION_PLACEHOLDER__` → current description
3. Write to `/tmp/eval_review_<skill-name>.html` and open: `open /tmp/eval_review_<skill-name>.html`
4. User edits queries, toggles should-trigger, then clicks "Export Eval Set"
5. File downloads to `~/Downloads/eval_set.json` — check for most recent if multiple exist

This step matters — bad eval queries produce bad descriptions.

---

## Step 3: Run the optimization loop

Tell the user: "This will take some time — I'll run the optimization loop in the background and check on it periodically."

Save the eval set to the workspace, then run in the background:

```bash
python -m scripts.run_loop \
  --eval-set <path-to-trigger-eval.json> \
  --skill-path <path-to-skill> \
  --model <model-id-powering-this-session> \
  --max-iterations 5 \
  --verbose
```

Use the model ID from your system prompt — the triggering test should match what the user actually experiences.

While running, periodically tail output and give the user updates: current iteration, current scores.

**What it does:** Splits eval set 60/40 train/test, evaluates current description (3 runs per query for reliability), calls Claude to propose improvements based on failures, re-evaluates each candidate on train and test, iterates up to 5 times. Returns `best_description` selected by test score (not train) to avoid overfitting. Opens HTML report in browser when done.

---

## Step 4: Apply the result

Take `best_description` from the JSON output and update `SKILL.md` frontmatter. Show user before/after with scores.

---

## How skill triggering works

Skills appear in Claude's `available_skills` list with name + description. Claude consults a skill based on whether the description matches the task — but only for tasks it can't easily handle directly. Simple one-step queries ("read this PDF") may not trigger a skill even with a perfect description. Complex, multi-step, or specialized queries reliably trigger.

Implication: eval queries should be substantive enough that Claude would actually benefit from consulting a skill. Simple queries are poor test cases regardless of description quality.
