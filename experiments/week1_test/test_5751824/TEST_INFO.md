# Week 1 Test Run

## Test Information
- Date: Tue Nov 11 19:21:22 EST 2025
- Model: Qwen/Qwen2.5-Coder-7B-Instruct
- Episodes: 5
- Competition: home-data-for-ml-course
- Job ID: 5751824
- Node: cml12

## Fixes Being Tested
1. ✅ Robust code extraction with AST validation
2. ✅ Enhanced error handling and recovery
3. ✅ MLE-Dojo specific prompts
4. ✅ Increased context limits (2048 tokens, 10 turns, 20 steps)

## Expected Improvements
- Success rate: > 0% (baseline was 0%)
- Steps per episode: > 5 (baseline was 0)
- Trajectories: Non-empty with actual interactions

## Evaluation Criteria
- **Minimum Success**: Agent completes episodes with steps > 0
- **Good Success**: Success rate > 5%, avg steps > 5
- **Excellent Success**: Success rate > 20%, meaningful ML workflow

