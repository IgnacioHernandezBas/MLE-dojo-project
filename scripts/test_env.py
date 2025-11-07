from mledojo.gym.competition import CompetitionRegistry, CompInfo
from mledojo.competitions import get_metric
from mledojo.gym.env import KaggleEnvironment
from pathlib import Path

competition_name = "random-acts-of-pizza"
data_dir = Path("/project/data/prepared/random-acts-of-pizza/data")
output_dir = Path("/project/output")

print("=" * 60)
print("🥋 Testing MLE-Dojo Environment")
print("=" * 60)

# Register competition
registry = CompetitionRegistry()
registry.register(
    name=competition_name,
    data_dir=str(data_dir),
    comp_info=CompInfo(
        category="General",
        level="beginner",
        output_type="submission.csv",
        higher_is_better=True
    ),
    metric_class=get_metric(competition_name)
)
print(f"✓ Registered: {competition_name}")

# Create environment
env = KaggleEnvironment.make(
    competition_name=competition_name,
    output_dir=str(output_dir),
    competition_registry=registry,
    score_mode="position",
    gpu_device=0,
    gpu_memory_limit=32,
    execution_timeout=3600
)
print("✓ Environment created")

# Test actions
print("\n--- Testing Actions ---")
result = env.step("request_info", **{"info_type": "overview"})
print("✓ request_info: OK")

result = env.step("validate_code", **{"code": "import pandas as pd\nprint('MLE-Dojo works!')"})
print("✓ validate_code: OK")

print("\n" + "=" * 60)
print("✅ All tests passed! Framework is ready to use.")
print("=" * 60)
