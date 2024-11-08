########################################################################
# This is a runner file for running different agents against one another
#########################################################################


from sentient_campaign.activity_runner.runner import WerewolfCampaignActivityRunner, PlayerAgentConfig, SentientWerewolfRoles
from transcript.reorg_files import reorg_files
import os
from typing import Dict, List
import random
from dotenv import load_dotenv
load_dotenv()

# The following is the distribution of roles for the game
# You can change the distribution of roles to test different configurations
# By default, we have 2 wolves, 4 villagers, 1 seer, and 1 doctor
# the wolves are controlled by the CoT agent
# the villagers are controlled by the Autogen agent
# the seer and doctor are controlled by the Simple agent
# You can change this by adding any combination of new agents and players

# Default role distribution
ROLE_DISTRIBUTION = {
    "frodo": {"role": SentientWerewolfRoles.WOLF, "agent": "cot"},
    "samwise": {"role": SentientWerewolfRoles.WOLF, "agent": "cot"},
    "meriadoc": {"role": SentientWerewolfRoles.VILLAGER, "agent": "autogen"},
    "peregrin": {"role": SentientWerewolfRoles.VILLAGER, "agent": "autogen"},
    "bilbo": {"role": SentientWerewolfRoles.VILLAGER, "agent": "autogen"},
    "hamfast": {"role": SentientWerewolfRoles.VILLAGER, "agent": "autogen"},
    "fredegar": {"role": SentientWerewolfRoles.SEER, "agent": "simple"},
    "lotho": {"role": SentientWerewolfRoles.DOCTOR, "agent": "simple"}
}
# Your Sentient API key
SENTIENT_API_KEY = os.getenv("MY_UNIQUE_API_KEY")

# Default agent configurations
AGENT_CONFIGS = {
    "cot": {
        "wheel_path": "./src/werewolf_agents/cot_sample/dist/chagent-0.1.0-py3-none-any.whl",
        "module_path": "agent/cot_agent.py",
        "config_path": "./src/werewolf_agents/cot_sample/config.yaml",
        "agent_class": "CoTAgent"
    },
    "autogen": {
        "wheel_path": "./src/werewolf_agents/autogen_sample/dist/autogenwolf-0.0.1-py3-none-any.whl",
        "module_path": "agent/single_agent.py",
        "config_path": "./src/werewolf_agents/autogen_sample/config.yaml",
        "agent_class": "WerewolfAgent"
    },
    "simple": {
        "wheel_path": "./src/werewolf_agents/simple_sample/dist/simplewolf-0.0.1-py3-none-any.whl",
        "module_path": "agent/super_simple.py",
        "config_path": "./src/werewolf_agents/simple_sample/config.yaml",
        "agent_class": "SimpleReactiveAgent"
    }
}

def create_game_config() -> tuple:
    """Creates game configuration"""
    player_roles = {name: config["role"] for name, config in ROLE_DISTRIBUTION.items()}
    
    your_agents = []
    for player_name, config in ROLE_DISTRIBUTION.items():
        agent_config = AGENT_CONFIGS[config["agent"]]
        your_agents.append(
            PlayerAgentConfig(
                player_name=player_name,
                agent_wheel_path=agent_config["wheel_path"],
                module_path=agent_config["module_path"],
                agent_class_name=agent_config["agent_class"],
                agent_config_file_path=agent_config["config_path"]
            )
        )

    # Print player configurations
    for name, config in ROLE_DISTRIBUTION.items():
        print(f"Player: {name}, Class: {config['agent']}, Role: {config['role'].name}")

    return your_agents, player_roles


# Create game configuration (using either default or custom)
your_agents, player_roles = create_game_config()

# Run the game
runner = WerewolfCampaignActivityRunner(com_server_port=8008)

game_result = runner.run_with_your_agents(
    your_agents,
    players_sentient_llm_api_keys=[SENTIENT_API_KEY],
    path_to_final_transcript_dump="transcript",
    player_roles=player_roles,
    force_rebuild_agent_images=False
)

activity_id = game_result.get("activity_id")
print(f"Activity completed with ID: {activity_id}")
# print game result into log file
with open("game_result_{0}.log".format(activity_id), "w") as f:
    f.write(str(game_result))
    f.write(f"\nPlayer Classes: {DEFAULT_ROLE_DISTRIBUTION}")

reorg_files("transcript", "game_result_{0}.log".format(activity_id))


