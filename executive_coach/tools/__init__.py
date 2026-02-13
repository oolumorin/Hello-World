from executive_coach.tools.obsidian import (
    read_obsidian_note,
    write_obsidian_note,
    list_obsidian_notes,
    search_obsidian_vault,
)
from executive_coach.tools.slack import (
    send_slack_dm,
    send_slack_channel,
    get_slack_history,
)
from executive_coach.tools.utils import (
    get_current_datetime,
    log_decision,
    get_decision_log,
)

obsidian_tools = [
    read_obsidian_note,
    write_obsidian_note,
    list_obsidian_notes,
    search_obsidian_vault,
]

slack_tools = [
    send_slack_dm,
    send_slack_channel,
    get_slack_history,
]

utility_tools = [
    get_current_datetime,
    log_decision,
    get_decision_log,
]

all_tools = obsidian_tools + slack_tools + utility_tools
