# Phase: Improving the Skill

This is the heart of the loop. You've run the test cases, the user has reviewed the results, and now you need to make the skill better based on their feedback.

## How to think about improvements

1. **Generalize from the feedback.** You're iterating on a few examples, but the skill will be used a million times on prompts you've never seen. Don't make fiddly, overfitty changes or oppressively rigid MUSTs. Instead, understand *why* the failures happened and encode that understanding broadly. Try different metaphors, different working patterns — it's cheap to experiment.

2. **Keep the prompt lean.** Remove things that aren't pulling their weight. Read the run transcripts, not just the final outputs — if the skill is causing the model to waste time on unproductive steps, cut the parts causing that behavior.

3. **Explain the why.** Today's models are smart. When you explain *why* something matters rather than just saying ALWAYS/NEVER, the model can generalize it. If you find yourself writing in all caps, that's a yellow flag — try reframing as reasoning instead of commands.

4. **Look for repeated work across test cases.** If all 3 test runs independently wrote a `create_docx.py` or `build_chart.py`, that's a strong signal the skill should bundle that script. Write it once in `scripts/`, tell the skill to use it.

---

## The iteration loop

After improving the skill:

1. Apply improvements to the skill
2. Rerun all test cases into `iteration-<N+1>/`
   - If creating a new skill: baseline is always `without_skill` (no skill) — stays constant across iterations
   - If improving existing: use your judgment — original version or previous iteration as baseline
3. Hand off to `agents/eval-runner.md` subagent with updated workspace paths
4. Wait for the subagent to return its JSON summary
5. Read the feedback summary, improve again, repeat

### When to stop

Keep iterating until:
- The user says they're happy
- All feedback is empty
- You're not making meaningful progress across two consecutive iterations

---

## Advanced: Blind comparison

For rigorous A/B comparison between two skill versions ("is the new version actually better?"):

Read `agents/comparator.md` and `agents/analyzer.md`. An independent agent evaluates two outputs without knowing which is which. Most users won't need this — the human review loop is usually sufficient.
