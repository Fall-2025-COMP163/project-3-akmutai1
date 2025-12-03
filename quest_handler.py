"""
COMP 163 - Project 3: Quest Chronicles
Quest Handler Module - Starter Code

Name: [Your Name Here]

AI Usage: [Document any AI assistance used]

This module handles quest management, dependencies, and completion.
"""

from custom_exceptions import (
    QuestNotFoundError,
    QuestRequirementsNotMetError,
    QuestAlreadyCompletedError,
    QuestNotActiveError,
    InsufficientLevelError
)

# ============================================================================
# QUEST MANAGEMENT
# ============================================================================

def accept_quest(character, quest_id, quest_data_dict):
    """
    Accept a new quest
    
    Args:
        character: Character dictionary
        quest_id: Quest to accept
        quest_data_dict: Dictionary of all quest data
    
    Requirements to accept quest:
    - Character level >= quest required_level
    - Prerequisite quest completed (if any)
    - Quest not already completed
    - Quest not already active
    
    Returns: True if quest accepted
    Raises:
        QuestNotFoundError if quest_id not in quest_data_dict
        InsufficientLevelError if character level too low
        QuestRequirementsNotMetError if prerequisite not completed
        QuestAlreadyCompletedError if quest already done
    """
    if quest_id not in quest_data_dict:
        raise QuestNotFoundError()

    quest = quest_data_dict[quest_id]

    # level check
    req_level = quest.get('required_level', 1)
    if character.get('level', 1) < req_level:
        raise InsufficientLevelError()

    # already completed
    if quest_id in character.get('completed_quests', []):
        raise QuestAlreadyCompletedError()

    # prerequisite
    prereq = quest.get('prerequisite', 'NONE')
    if prereq and prereq != 'NONE' and prereq not in character.get('completed_quests', []):
        raise QuestRequirementsNotMetError()

    # already active
    if quest_id in character.get('active_quests', []):
        return True

    character.setdefault('active_quests', []).append(quest_id)
    return True

def complete_quest(character, quest_id, quest_data_dict):
    """
    Complete an active quest and grant rewards
    
    Args:
        character: Character dictionary
        quest_id: Quest to complete
        quest_data_dict: Dictionary of all quest data
    
    Rewards:
    - Experience points (reward_xp)
    - Gold (reward_gold)
    
    Returns: Dictionary with reward information
    Raises:
        QuestNotFoundError if quest_id not in quest_data_dict
        QuestNotActiveError if quest not in active_quests
    """
    if quest_id not in quest_data_dict:
        raise QuestNotFoundError()

    if quest_id not in character.get('active_quests', []):
        raise QuestNotActiveError()

    quest = quest_data_dict[quest_id]
    xp = int(quest.get('reward_xp', 0))
    gold = int(quest.get('reward_gold', 0))

    # remove from active, add to completed
    character['active_quests'].remove(quest_id)
    character.setdefault('completed_quests', []).append(quest_id)

    # grant rewards
    from character_manager import gain_experience, add_gold
    gain_experience(character, xp)
    add_gold(character, gold)

    return {'xp': xp, 'gold': gold}

def abandon_quest(character, quest_id):
    """
    Remove a quest from active quests without completing it
    
    Returns: True if abandoned
    Raises: QuestNotActiveError if quest not active
    """
    if quest_id not in character.get('active_quests', []):
        raise QuestNotActiveError()

    character['active_quests'].remove(quest_id)
    return True

def get_active_quests(character, quest_data_dict):
    """
    Get full data for all active quests
    
    Returns: List of quest dictionaries for active quests
    """
    res = []
    for qid in character.get('active_quests', []):
        if qid in quest_data_dict:
            res.append(quest_data_dict[qid])
    return res

def get_completed_quests(character, quest_data_dict):
    """
    Get full data for all completed quests
    
    Returns: List of quest dictionaries for completed quests
    """
    res = []
    for qid in character.get('completed_quests', []):
        if qid in quest_data_dict:
            res.append(quest_data_dict[qid])
    return res

def get_available_quests(character, quest_data_dict):
    """
    Get quests that character can currently accept
    
    Available = meets level req + prerequisite done + not completed + not active
    
    Returns: List of quest dictionaries
    """
    res = []
    for qid, q in quest_data_dict.items():
        if qid in character.get('completed_quests', []) or qid in character.get('active_quests', []):
            continue

        # level and prereq
        if character.get('level', 1) < int(q.get('required_level', 1)):
            continue

        prereq = q.get('prerequisite', 'NONE')
        if prereq != 'NONE' and prereq not in character.get('completed_quests', []):
            continue

        res.append(q)
    return res

# ============================================================================
# QUEST TRACKING
# ============================================================================

def is_quest_completed(character, quest_id):
    """
    Check if a specific quest has been completed
    
    Returns: True if completed, False otherwise
    """
    return quest_id in character.get('completed_quests', [])

def is_quest_active(character, quest_id):
    """
    Check if a specific quest is currently active
    
    Returns: True if active, False otherwise
    """
    return quest_id in character.get('active_quests', [])

def can_accept_quest(character, quest_id, quest_data_dict):
    """
    Check if character meets all requirements to accept quest
    
    Returns: True if can accept, False otherwise
    Does NOT raise exceptions - just returns boolean
    """
    if quest_id not in quest_data_dict:
        return False

    q = quest_data_dict[quest_id]
    if character.get('level', 1) < int(q.get('required_level', 1)):
        return False

    prereq = q.get('prerequisite', 'NONE')
    if prereq != 'NONE' and prereq not in character.get('completed_quests', []):
        return False

    if quest_id in character.get('completed_quests', []) or quest_id in character.get('active_quests', []):
        return False

    return True

def get_quest_prerequisite_chain(quest_id, quest_data_dict):
    """
    Get the full chain of prerequisites for a quest
    
    Returns: List of quest IDs in order [earliest_prereq, ..., quest_id]
    Example: If Quest C requires Quest B, which requires Quest A:
             Returns ["quest_a", "quest_b", "quest_c"]
    
    Raises: QuestNotFoundError if quest doesn't exist
    """
    if quest_id not in quest_data_dict:
        raise QuestNotFoundError()

    chain = []
    current = quest_id
    while True:
        if current not in quest_data_dict:
            raise QuestNotFoundError()
        chain.insert(0, current)
        prereq = quest_data_dict[current].get('prerequisite', 'NONE')
        if not prereq or prereq == 'NONE':
            break
        current = prereq

    return chain

# ============================================================================
# QUEST STATISTICS
# ============================================================================

def get_quest_completion_percentage(character, quest_data_dict):
    """
    Calculate what percentage of all quests have been completed
    
    Returns: Float between 0 and 100
    """
    total = max(1, len(quest_data_dict))
    completed = len(character.get('completed_quests', []))
    return (completed / total) * 100

def get_total_quest_rewards_earned(character, quest_data_dict):
    """
    Calculate total XP and gold earned from completed quests
    
    Returns: Dictionary with 'total_xp' and 'total_gold'
    """
    total_xp = 0
    total_gold = 0
    for qid in character.get('completed_quests', []):
        q = quest_data_dict.get(qid)
        if q:
            total_xp += int(q.get('reward_xp', 0))
            total_gold += int(q.get('reward_gold', 0))
    return {'total_xp': total_xp, 'total_gold': total_gold}

def get_quests_by_level(quest_data_dict, min_level, max_level):
    """
    Get all quests within a level range
    
    Returns: List of quest dictionaries
    """
    res = []
    for q in quest_data_dict.values():
        lvl = int(q.get('required_level', 1))
        if min_level <= lvl <= max_level:
            res.append(q)
    return res

# ============================================================================
# DISPLAY FUNCTIONS
# ============================================================================

def display_quest_info(quest_data):
    """
    Display formatted quest information
    
    Shows: Title, Description, Rewards, Requirements
    """
    print(f"\n=== {quest_data.get('title','') } ===")
    print(f"Description: {quest_data.get('description','')}")
    print(f"Required Level: {quest_data.get('required_level','')}")
    print(f"Rewards: XP {quest_data.get('reward_xp',0)}, Gold {quest_data.get('reward_gold',0)}")
    return True

def display_quest_list(quest_list):
    """
    Display a list of quests in summary format
    
    Shows: Title, Required Level, Rewards
    """
    for q in quest_list:
        print(f"- {q.get('title', q.get('quest_id'))} (Level {q.get('required_level',1)}) - XP:{q.get('reward_xp',0)} Gold:{q.get('reward_gold',0)}")
    return True

def display_character_quest_progress(character, quest_data_dict):
    """
    Display character's quest statistics and progress
    
    Shows:
    - Active quests count
    - Completed quests count
    - Completion percentage
    - Total rewards earned
    """
    active = len(character.get('active_quests', []))
    completed = len(character.get('completed_quests', []))
    pct = get_quest_completion_percentage(character, quest_data_dict)
    totals = get_total_quest_rewards_earned(character, quest_data_dict)
    print(f"Active quests: {active}")
    print(f"Completed quests: {completed}")
    print(f"Completion: {pct:.1f}%")
    print(f"Total rewards earned: XP {totals['total_xp']}, Gold {totals['total_gold']}")
    return True

# ============================================================================
# VALIDATION
# ============================================================================

def validate_quest_prerequisites(quest_data_dict):
    """
    Validate that all quest prerequisites exist
    
    Checks that every prerequisite (that's not "NONE") refers to a real quest
    
    Returns: True if all valid
    Raises: QuestNotFoundError if invalid prerequisite found
    """
    for q in quest_data_dict.values():
        prereq = q.get('prerequisite', 'NONE')
        if prereq and prereq != 'NONE' and prereq not in quest_data_dict:
            raise QuestNotFoundError()
    return True


# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    print("=== QUEST HANDLER TEST ===")
    
    # Test data
    # test_char = {
    #     'level': 1,
    #     'active_quests': [],
    #     'completed_quests': [],
    #     'experience': 0,
    #     'gold': 100
    # }
    #
    # test_quests = {
    #     'first_quest': {
    #         'quest_id': 'first_quest',
    #         'title': 'First Steps',
    #         'description': 'Complete your first quest',
    #         'reward_xp': 50,
    #         'reward_gold': 25,
    #         'required_level': 1,
    #         'prerequisite': 'NONE'
    #     }
    # }
    #
    # try:
    #     accept_quest(test_char, 'first_quest', test_quests)
    #     print("Quest accepted!")
    # except QuestRequirementsNotMetError as e:
    #     print(f"Cannot accept: {e}")

