import yaml
import os

# Function to load prompts from YAML
def load_prompts():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    yaml_path = os.path.join(current_dir, "prompts.yaml")
    
    with open(yaml_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

_prompts = load_prompts()

ROUTER_PROMPT = _prompts.get("router_prompt", "")
ANALYST_PROMPT = _prompts.get("analyst_prompt", "")
CREATOR_PROMPT = _prompts.get("creator_prompt", "")
CHAT_PROMPT = _prompts.get("chat_prompt", "")

