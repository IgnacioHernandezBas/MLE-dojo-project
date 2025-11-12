# MLE-Dojo Evaluation Metrics Explained

**Date:** 2025-11-11

---

## How MLE-Dojo Evaluates Submissions

MLE-Dojo runs agents in Kaggle-style competitions where the agent must:
1. Understand the task
2. Explore the data
3. Build ML models
4. Generate predictions
5. Submit predictions in the correct format

### Key Concept: Position Score

When an agent executes code that saves a `submission.csv` file, MLE-Dojo:
1. **Evaluates it against the actual test set** (private/public split)
2. **Computes the competition metric** (e.g., accuracy, RMSE, F1, etc.)
3. **Ranks it against a leaderboard** of baseline submissions
4. **Returns a position_score** indicating leaderboard placement (0-100 scale)

---

## Evaluation Metrics We Track

### Per-Episode Metrics

Saved in `eval_results_*.json` under `episodes[]`:

```json
{
  "episode_id": 0,
  "final_position_score": 45.2,      // Last submission's position score
  "best_position_score": 52.8,        // Best submission across all steps
  "steps_taken": 15,                   // Number of agent actions
  "success": true,                     // Whether any submission scored > 0
  "feedback_history": [...]            // Action-by-action details
}
```

**Key Metrics:**
- **best_position_score** - Most important! The best submission the agent generated
- **steps_taken** - How many actions the agent took (0 = agent didn't interact)
- **success** - Whether the agent generated ANY valid submission with score > 0
- **feedback_history** - Detailed log of each action and environment response

### Aggregate Metrics

Saved in `eval_results_*.json` under `metrics`:

```json
{
  "avg_best_position_score": 48.5,     // Average of best scores across episodes
  "max_best_position_score": 65.3,     // Highest score achieved in any episode
  "min_best_position_score": 12.1,     // Lowest score achieved
  "success_rate": 0.80,                 // % of episodes with successful submissions
  "total_episodes": 10,
  "successful_episodes": 8,
  "avg_steps_taken": 12.4,              // Average actions per episode
  "episodes_with_steps": 10             // Episodes where agent took actions
}
```

**Key Metrics:**
- **avg_best_position_score** - Primary performance metric (higher = better)
- **success_rate** - % of episodes with valid submissions
- **avg_steps_taken** - Measures agent engagement (0 = baseline problem)
- **episodes_with_steps** - Sanity check (should = total_episodes)

---

## What Good Performance Looks Like

### Baseline (Week 0 - Before Fixes)
```
✗ avg_best_position_score: 0.0
✗ success_rate: 0%
✗ avg_steps_taken: 0
✗ episodes_with_steps: 0/10
```
**Diagnosis:** Agent never interacted with environment

### Minimum Viable (Week 1 - After Fixes)
```
✓ avg_best_position_score: > 0
✓ success_rate: > 0%
✓ avg_steps_taken: > 5
✓ episodes_with_steps: 10/10
```
**Diagnosis:** Agent interacts and generates submissions

### Good Performance (Week 2 Target)
```
✓ avg_best_position_score: 30-50
✓ success_rate: > 50%
✓ avg_steps_taken: > 10
✓ episodes_with_steps: 10/10
```
**Diagnosis:** Agent consistently generates decent submissions

### Strong Performance (Week 3+ Target)
```
✓ avg_best_position_score: > 60
✓ success_rate: > 80%
✓ avg_steps_taken: 15-20
✓ max_best_position_score: > 80
```
**Diagnosis:** Agent competes at upper tier of leaderboard

---

## Understanding Position Scores

Position scores are **leaderboard rankings** on a 0-100 scale:

| Position Score | Meaning | Quality |
|----------------|---------|---------|
| 0-20 | Bottom 20% of leaderboard | Poor |
| 20-40 | Lower tier | Below average |
| 40-60 | Middle tier | Average |
| 60-80 | Upper tier | Good |
| 80-100 | Top 20% | Excellent |

**Note:** These are relative to baseline/reference submissions in MLE-Dojo, not the actual Kaggle leaderboard.

---

## Interpreting Results

### Scenario 1: No Steps Taken
```json
{
  "avg_best_position_score": 0.0,
  "avg_steps_taken": 0,
  "episodes_with_steps": 0
}
```
**Problem:** Agent initialization or prompt issues
**Fix:** Check logs for errors, verify environment setup

### Scenario 2: Steps But No Success
```json
{
  "avg_best_position_score": 0.0,
  "avg_steps_taken": 15,
  "success_rate": 0.0
}
```
**Problem:** Agent takes actions but submissions invalid/missing
**Fix:** Check if agent generates submission.csv, review feedback_history

### Scenario 3: Some Success
```json
{
  "avg_best_position_score": 25.3,
  "success_rate": 0.60,
  "avg_steps_taken": 12
}
```
**Problem:** Agent works but quality is low
**Fix:** Improve prompts, add multi-step reasoning, better ML approaches

### Scenario 4: Good Performance
```json
{
  "avg_best_position_score": 55.7,
  "success_rate": 0.90,
  "max_best_position_score": 72.1
}
```
**Success!** Agent is working well, ready for harder competitions

---

## Comparing Baselines

When comparing different approaches, track:

### Primary Metrics
1. **avg_best_position_score** - Overall performance
2. **success_rate** - Reliability
3. **max_best_position_score** - Potential

### Secondary Metrics
4. **avg_steps_taken** - Efficiency (less is better if quality maintained)
5. **consistency** - Standard deviation of position scores

### Example Comparison

```
Baseline A (Pre-fixes):
  avg_score: 0.0, success: 0%, steps: 0
  → Agent doesn't work

Baseline B (Week 1 fixes):
  avg_score: 28.4, success: 70%, steps: 14.2
  → Functional but needs improvement

Baseline C (Week 2 improvements):
  avg_score: 51.2, success: 90%, steps: 16.8, max: 68.9
  → Good performance, ready for training
```

---

## Feedback History Analysis

Each episode saves detailed `feedback_history`:

```json
{
  "step": 1,
  "action_status": "INFO_SUCCESS",
  "reward": 0.0,
  "cumulative_score": 0.0
}
```

**Action Status Values:**
- `INFO_SUCCESS` - Information request succeeded
- `CODE_EXEC_SUCCESS` - Code executed successfully
- `SUBMISSION_SUCCESS` - Valid submission generated and scored
- `ERROR_*` - Various error conditions

**Analysis Tips:**
- Look for patterns in successful episodes
- Identify where failures occur (step 1? 10? 20?)
- Check if agent iterates and improves scores
- See if errors are recoverable or fatal

---

## Week 1 Test Success Criteria

### Minimum (Must Achieve)
- [ ] `episodes_with_steps` = total episodes (agent takes actions)
- [ ] `avg_steps_taken` > 5 (meaningful interaction)
- [ ] At least 1 episode with `best_position_score` > 0

### Target (Good Success)
- [ ] `success_rate` > 20%
- [ ] `avg_best_position_score` > 15
- [ ] `avg_steps_taken` > 10

### Stretch (Excellent)
- [ ] `success_rate` > 50%
- [ ] `avg_best_position_score` > 30
- [ ] `max_best_position_score` > 50

---

## Next Steps After Evaluation

### If Minimum Not Met:
1. Check evaluation logs for errors
2. Review feedback_history for failure points
3. Verify code extraction is working
4. Check if prompts guide agent correctly

### If Target Met:
1. Analyze successful episodes - what worked?
2. Implement Week 2 improvements (multi-step reasoning)
3. Test on 2-3 more competitions
4. Prepare for RL training

### If Stretch Met:
1. Test on harder competitions
2. Start RL training pipeline
3. Implement curriculum learning
4. Scale to more episodes

---

## Useful Analysis Commands

### Quick Check
```bash
# View metrics summary
cat experiments/week1_test/*/eval_results_*.json | jq '.metrics'

# Count successful episodes
cat experiments/week1_test/*/eval_results_*.json | jq '.episodes[] | select(.success == true)' | wc -l

# Get all position scores
cat experiments/week1_test/*/eval_results_*.json | jq '.episodes[].best_position_score'
```

### Detailed Analysis
```python
import json

with open('eval_results_week1_test.json') as f:
    results = json.load(f)

# Find best episode
best_ep = max(results['episodes'], key=lambda x: x['best_position_score'])
print(f"Best episode: {best_ep['episode_id']} scored {best_ep['best_position_score']}")

# Analyze feedback patterns
for ep in results['episodes']:
    if ep['success']:
        print(f"Episode {ep['episode_id']}: {ep['steps_taken']} steps → {ep['best_position_score']:.2f}")
```

---

## References

- MLE-Dojo Environment: `mle-dojo-source/mledojo/gym/env.py`
- Scoring Logic: Lines 366-390 (submission evaluation)
- Evaluation Script: `agent/training/evaluate.py`
- Wrapper: `agent/wrappers/mledojo_wrapper.py`

---

**Last Updated:** 2025-11-11
