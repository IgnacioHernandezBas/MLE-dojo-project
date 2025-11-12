# MLE-Dojo Baseline Pipeline - Critical Review & Action Plan

**Date:** 2025-11-11
**Status:** Initial baseline review completed

---

## Executive Summary

The current baseline pipeline has good architectural foundations but **0% success rate** due to critical integration issues. The agent never successfully completes episodes, indicating broken environment interaction. This document provides a comprehensive analysis and actionable fixes.

---

## 1. CURRENT STATE ASSESSMENT

### Baseline Results
Location: `experiments/baselines/baseline_20251111_141450/`

**Metrics:**
- Success rate: **0%** (0/10 episodes)
- Steps taken: **0** per episode
- Trajectories: **Empty** (no interactions recorded)
- Reward: **0.0** across all episodes

**Root Cause:** Agent never successfully interacts with MLE-Dojo environment.

---

## 2. ARCHITECTURAL STRENGTHS

### What's Working Well:

1. **Clean Abstraction Layers**
   - `BaseAgent` → `LocalModelAgent` → `MLEDojoWrapper`
   - Easy to swap models and frameworks

2. **Configuration Management**
   - YAML-based configs in `agent/configs/`
   - Separation of agent, wrapper, and eval settings

3. **Modular Design**
   - Framework-agnostic core
   - Pluggable wrappers for different environments

4. **Type Safety**
   - Good use of type hints throughout

5. **File Organization**
   - Clear separation: core, wrappers, training, configs

---

## 3. CRITICAL ISSUES & WEAKNESSES

### A. Pipeline Architecture Problems

#### Issue #1: Brittle Code Extraction
**Location:** `agent/wrappers/mledojo_wrapper.py:279-319`

**Problem:**
```python
def _extract_code(self, response: str) -> str:
    if "```python" in response:
        parts = response.split("```python")
        if len(parts) > 1:
            code_part = parts[1].split("```")[0]
            return code_part.strip()
```

**Issues:**
- Naive string parsing fails with complex responses
- No validation before execution
- Doesn't handle multiple code blocks
- Falls back to returning entire response

**Impact:** Agent's code never executes properly → 0 success rate

**Fix Priority:** 🔴 Critical

---

#### Issue #2: Simplistic Action Heuristic
**Location:** `agent/wrappers/mledojo_wrapper.py:236-250`

**Problem:**
```python
if "```python" in agent_response or "import " in agent_response:
    code = self._extract_code(agent_response)
    obs, step_reward = env.step("execute_code", code=code)
else:
    obs, step_reward = env.step("request_info", info_type="data_structure")
```

**Issues:**
- Binary decision: execute code OR request info
- No planning phase
- No validation or testing
- No multi-step reasoning

**What MLE Tasks Need:**
- Exploration → Analysis → Implementation → Testing → Debugging → Refinement
- Iterative workflows with feedback loops

**Fix Priority:** 🔴 Critical

---

#### Issue #3: Insufficient Prompt Engineering
**Location:** `agent/core/prompts.py:20-30`

**Problem:**
```python
SYSTEM_PROMPT = """You are an expert machine learning engineer working on implementing solutions to ML tasks.
You have access to a Python environment where you can write and execute code.

Your goal is to:
1. Understand the task requirements
2. Plan your implementation approach
3. Write clean, efficient code
4. Test your solution
5. Debug and improve as needed
"""
```

**Issues:**
- Generic prompt doesn't guide agent through MLE-Dojo's action space
- No action format specifications
- No examples of correct responses
- No environment feedback interpretation guidance
- No multi-step workflow patterns

**What's Missing:**
- Chain-of-thought prompting
- Few-shot examples
- Action templates (request_info, execute_code, submit)
- Structured response format

**Fix Priority:** 🔴 Critical

---

#### Issue #4: Inadequate Context Management
**Location:** `agent/configs/agent_config.yaml:10-17`

**Problem:**
```yaml
max_new_tokens: 512
max_history_turns: 3
max_context_length: 2048
```

**Issues:**
- 512 tokens too limiting for code generation
- Only 3 turns of history loses debugging context
- 2048 context length insufficient for MLE tasks

**MLE Tasks Require:**
- Long context for data structures, error messages, code history
- 1024-2048 tokens for code generation
- 10+ turns for debugging workflows

**Fix Priority:** 🟡 High

---

### B. Training Framework Issues

#### Issue #5: No RL Training Implementation
**Location:** `agent/training/train_rl.py:54-69`

**Problem:**
```python
# TODO: Implement actual RL training
print("\n" + "="*60)
print("WARNING: RL training implementation is pending")
print("="*60)
```

**Missing:**
- Verl integration
- PPO/DPO implementation
- Reward shaping
- Policy optimization loop
- Checkpoint management
- Metrics logging

**Impact:** Cannot train the agent at all

**Fix Priority:** 🟡 High

---

#### Issue #6: Broken Trajectory Generation
**Location:** `agent/training/generate_trajectories.py:53-56`

**Problem:**
```python
# TODO: Initialize MLE-Dojo environment
print("\nWARNING: MLE-Dojo environment initialization not yet implemented")
```

**Issues:**
- Doesn't actually run episodes
- Creates empty trajectory files
- No proper environment instantiation

**Fix Priority:** 🟡 High

---

### C. Evaluation Framework Issues

#### Issue #7: Wrong Success Criteria
**Location:** `agent/training/evaluate.py:147`

**Problem:**
```python
success = reward > 0.0  # Consider any positive reward as success
```

**Issues:**
- MLE-Dojo uses position scores (leaderboard ranking), not binary success
- Any positive score counts as success (too lenient)

**Better Metrics:**
- Top-N% threshold (e.g., top 50% = success)
- Improvement over baseline
- Actual task completion rate

**Fix Priority:** 🟢 Medium

---

#### Issue #8: Inconsistent Configuration
**Location:** Multiple config files

**Problem:**
```yaml
# eval_config.yaml
max_steps: 5

# agent_config.yaml
max_steps_per_episode: 100
```

**Issues:**
- 5 steps too few for MLE tasks
- Inconsistent limits across configs
- Typical MLE task needs 20-50 interactions minimum

**Fix Priority:** 🟢 Medium

---

### D. MLE-Dojo Integration Issues

#### Issue #9: Incomplete Environment Initialization
**Location:** `agent/training/evaluate.py:80-108`

**Issues:**
- No error handling for missing competition data
- Hard-coded to single competition: `home-data-for-ml-course`
- No support for competition variety or difficulty levels
- Assumes data is already prepared

**Fix Priority:** 🟢 Medium

---

#### Issue #10: Simplistic Observation Formatting
**Location:** `agent/wrappers/mledojo_wrapper.py:98-123`

**Problem:**
```python
def _format_observation(self, observation: Dict[str, Any]) -> str:
    if "text" in observation:
        return observation["text"]
    # ... simple string concatenation
```

**Issues:**
- MLE-Dojo observations are rich (feedback, metrics, file listings, errors)
- No structured parsing of feedback types
- No error message extraction
- No metric trend analysis

**Fix Priority:** 🟢 Medium

---

## 4. WHY NOT SUITABLE FOR MLE TASKS

### Current Pipeline Limitations:

#### A. Ignores Iterative Nature of MLE
- **MLE workflow:** Explore → Analyze → Implement → Test → Debug → Refine
- **Current pipeline:** Generate code once → Execute → Done
- **Missing:** Feedback loops, iterative refinement

#### B. No Multi-Step Reasoning
**MLE-Dojo competitions need:**
1. Understanding data structure
2. Exploratory data analysis
3. Feature engineering
4. Model selection
5. Hyperparameter tuning
6. Ensemble methods
7. Submission formatting

**Current agent:** Single-shot code generation

#### C. Missing Critical MLE Capabilities
- ❌ No code debugging (can't fix errors from feedback)
- ❌ No experimentation tracking (can't compare approaches)
- ❌ No validation (no checking code before execution)
- ❌ No planning (no high-level strategy)

#### D. Weak LLM Utilization
**Qwen2.5-Coder-7B is capable, but:**
- Prompts don't leverage its coding abilities
- No code explanation requests
- No step-by-step generation
- No self-correction loops

---

## 5. RECOMMENDATIONS

### Week 1: Core Fixes (CRITICAL)

#### 1. Fix Code Extraction
**File:** `agent/wrappers/mledojo_wrapper.py:279-319`

**Changes:**
- Use regex + AST validation
- Handle multiple code blocks
- Validate syntax before execution
- Extract imports separately
- Add error handling

#### 2. Fix Code Execution Logic
**File:** `agent/wrappers/mledojo_wrapper.py:236-250`

**Changes:**
- Parse structured agent responses
- Support multiple action types
- Add validation step
- Implement error recovery

#### 3. Improve Prompts for MLE-Dojo
**File:** `agent/core/prompts.py`

**Changes:**
- Add MLE-Dojo action space specifications
- Include few-shot examples
- Add structured response format (XML/JSON tags)
- Add chain-of-thought guidance
- Include error handling instructions

#### 4. Increase Context Limits
**File:** `agent/configs/agent_config.yaml`

**Changes:**
```yaml
max_new_tokens: 2048  # Was 512
max_history_turns: 10  # Was 3
max_context_length: 8192  # Was 2048
```

#### 5. Test on Simple Competition
**Goal:** Get ONE competition working end-to-end
- Use `home-data-for-ml-course` (beginner level)
- Verify environment integration
- Confirm trajectory collection
- Debug until success rate > 0%

---

### Week 2: Agent Loop Enhancement

#### 6. Implement Multi-Step Reasoning
**New file:** `agent/core/mle_agent.py`

**Structure:**
```python
class MLEAgent:
    def run_competition(self, env):
        # Phase 1: Exploration
        data_info = self.explore_data(env)

        # Phase 2: Planning
        strategy = self.plan_approach(data_info)

        # Phase 3: Implementation
        for iteration in range(max_iterations):
            code = self.generate_code(strategy)
            result = env.execute(code)
            if result.success:
                break
            strategy = self.refine_strategy(result.feedback)

        # Phase 4: Submission
        self.submit(env)
```

#### 7. Add Action Parser
**File:** `agent/wrappers/mledojo_wrapper.py`

**New method:**
```python
def _parse_agent_action(self, response: str) -> Dict[str, Any]:
    """Parse structured agent response into action"""
    # Support: CODE, REQUEST_INFO, SUBMIT, ANALYZE
    # Use JSON or XML-tagged responses
```

#### 8. Implement Error Recovery
**Changes:**
- Track error history
- Generate fix attempts
- Learn from failures

#### 9. Test on Multiple Competitions
- Test on 5 beginner competitions
- Measure success rate
- Collect quality trajectories

---

### Week 3: Training Pipeline

#### 10. Implement Reward Shaping
**File:** `agent/training/rewards.py`

**Reward structure:**
```python
rewards = {
    "code_executes": 0.1,
    "improves_score": 0.5,
    "beats_baseline": 1.0,
    "top_50%": 2.0,
    "top_10%": 5.0,
    "syntax_error": -0.2,
    "runtime_error": -0.1,
}
```

#### 11. Implement RL Training Pipeline
**File:** `agent/training/train_rl.py`

**Framework:** Verl with PPO

**Components:**
- Policy network (Qwen2.5-Coder-7B)
- Value network
- Experience replay buffer
- PPO update loop
- Checkpoint saving
- Metrics logging (TensorBoard/W&B)

#### 12. Collect Training Data
- Run baseline on 20+ competitions
- Collect diverse trajectories
- Include successes and failures
- Annotate with rewards

#### 13. Run First Training Experiment
- Train on collected trajectories
- Monitor reward curves
- Evaluate on held-out competitions
- Compare to baseline

---

### Long-Term (Month 2-3)

#### 14. Build MLE-Specific Architecture
```
Agent Components:
├── PlannerModule: High-level strategy
├── CoderModule: Code generation
├── DebuggerModule: Error fixing
├── AnalyzerModule: Result interpretation
└── MemoryModule: Track experiments
```

#### 15. Curriculum Learning
```python
difficulties = ["beginner", "intermediate", "advanced"]
# Train on easy competitions first
# Gradually increase difficulty
# Use transfer learning
```

#### 16. Add Tool Use
```python
tools = {
    "pandas_profiling": analyze_data,
    "hyperparameter_search": tune_model,
    "ensemble_builder": combine_models,
    "error_debugger": fix_errors,
}
```

---

## 6. COMPATIBILITY ASSESSMENT

### Current Compatibility: 2/10 (Low)

**Why:**
- Agent doesn't complete any episodes successfully
- No understanding of competition structure
- Can't handle feedback properly
- No iteration or refinement

### Required for Success:

#### Beginner Competitions:
- ✅ Basic code execution (partially works)
- ❌ Data exploration workflow
- ❌ Simple model training
- ❌ Submission formatting

#### Intermediate Competitions:
- ❌ Feature engineering
- ❌ Model selection
- ❌ Hyperparameter tuning
- ❌ Error handling
- ❌ Cross-validation

#### Advanced Competitions:
- ❌ Complex pipelines
- ❌ Ensemble methods
- ❌ Domain knowledge
- ❌ Optimization strategies
- ❌ Advanced debugging

---

## 7. PRIORITY ACTION ITEMS

### Immediate (Week 1)
1. ✅ Complete pipeline review
2. ⬜ Fix code extraction logic (mledojo_wrapper.py:279-319)
3. ⬜ Improve prompts with action specs (prompts.py)
4. ⬜ Increase context limits (agent_config.yaml)
5. ⬜ Test on 1 simple competition

### High Priority (Week 2)
6. ⬜ Implement multi-step reasoning loop
7. ⬜ Add structured action parser
8. ⬜ Implement basic error recovery
9. ⬜ Test on 5 beginner competitions

### Medium Priority (Week 3)
10. ⬜ Implement reward shaping
11. ⬜ Build Verl/PPO training pipeline
12. ⬜ Collect quality trajectories
13. ⬜ Run first training experiment

---

## 8. SUCCESS METRICS

### Week 1 Goals:
- [ ] Success rate > 0% on any competition
- [ ] Agent completes at least 1 episode with steps > 0
- [ ] Code extraction works reliably
- [ ] Trajectories contain actual interactions

### Week 2 Goals:
- [ ] Success rate > 20% on beginner competitions
- [ ] Multi-step reasoning implemented
- [ ] Average steps per episode > 10
- [ ] Error recovery working

### Week 3 Goals:
- [ ] RL training pipeline functional
- [ ] Collect 100+ trajectories
- [ ] Train first model iteration
- [ ] Show improvement over baseline

---

## 9. CONCLUSION

**Current State:** The baseline architecture is sound but the implementation is incomplete and broken. The 0% success rate indicates critical integration issues that must be fixed before any training can begin.

**Good News:** The modular design makes fixes straightforward. The architecture won't need major changes.

**Recommended Approach:**
1. **Don't try to build everything at once**
2. **Get ONE competition working first** (end-to-end)
3. **Then add complexity** (multi-step reasoning, RL training)
4. **Iterate on a working baseline**

**Timeline Estimate:**
- Week 1: Working agent on 1 competition
- Week 2: Multi-step reasoning on 5 competitions
- Week 3: First RL training run
- Month 2-3: Production-ready agent

---

## 10. REFERENCES

### Key Files to Modify:
1. `agent/wrappers/mledojo_wrapper.py` - Core execution logic
2. `agent/core/prompts.py` - Prompt engineering
3. `agent/configs/agent_config.yaml` - Context limits
4. `agent/training/train_rl.py` - RL training loop
5. `agent/training/evaluate.py` - Evaluation metrics

### MLE-Dojo Documentation:
- Repository: `mle-dojo-source/`
- Environment API: `mle-dojo-source/mledojo/gym/env.py`
- Competitions: `mle-dojo-source/prepare/mle.json`
- README: `mle-dojo-source/README.md`

---

## Appendix: Detailed Code Locations

### Critical Issues:
1. **Code Extraction:** `agent/wrappers/mledojo_wrapper.py:279-319`
2. **Action Logic:** `agent/wrappers/mledojo_wrapper.py:236-250`
3. **Prompts:** `agent/core/prompts.py:20-30`
4. **Context Limits:** `agent/configs/agent_config.yaml:10-17`
5. **RL Training:** `agent/training/train_rl.py:54-69`
6. **Trajectory Gen:** `agent/training/generate_trajectories.py:53-56`
7. **Success Criteria:** `agent/training/evaluate.py:147`
8. **Step Limits:** `agent/configs/eval_config.yaml:31`
9. **Env Init:** `agent/training/evaluate.py:80-108`
10. **Obs Format:** `agent/wrappers/mledojo_wrapper.py:98-123`

---

**Last Updated:** 2025-11-11
**Next Review:** After Week 1 fixes are implemented
