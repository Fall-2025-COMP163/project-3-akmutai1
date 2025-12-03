"""
COMP 163 - Project 3: Quest Chronicles
Game Data Module - Starter Code

Name: [Your Name Here]

AI Usage: [Document any AI assistance used]

This module handles loading and validating game data from text files.
"""

import os
from custom_exceptions import (
    InvalidDataFormatError,
    MissingDataFileError,
    CorruptedDataError
)

# ============================================================================
# DATA LOADING FUNCTIONS
# ============================================================================

def load_quests(filename="data/quests.txt"):
    """
    Load quest data from file
    
    Expected format per quest (separated by blank lines):
    QUEST_ID: unique_quest_name
    TITLE: Quest Display Title
    DESCRIPTION: Quest description text
    REWARD_XP: 100
    REWARD_GOLD: 50
    REQUIRED_LEVEL: 1
    PREREQUISITE: previous_quest_id (or NONE)
    
    Returns: Dictionary of quests {quest_id: quest_data_dict}
    Raises: MissingDataFileError, InvalidDataFormatError, CorruptedDataError
    """
    if not os.path.exists(filename):
        raise MissingDataFileError()

    try:
        with open(filename, "r") as f:
            content = f.read()
    except Exception:
        raise CorruptedDataError()

    blocks = [b.strip() for b in content.split('\n\n') if b.strip()]
    quests = {}

    try:
        for block in blocks:
            lines = [l.strip() for l in block.split('\n') if l.strip()]
            q = parse_quest_block(lines)
            validate_quest_data(q)
            quests[q['quest_id']] = q
    except InvalidDataFormatError:
        raise
    except Exception:
        raise InvalidDataFormatError()

    return quests

def load_items(filename="data/items.txt"):
    """
    Load item data from file
    
    Expected format per item (separated by blank lines):
    ITEM_ID: unique_item_name
    NAME: Item Display Name
    TYPE: weapon|armor|consumable
    EFFECT: stat_name:value (e.g., strength:5 or health:20)
    COST: 100
    DESCRIPTION: Item description
    
    Returns: Dictionary of items {item_id: item_data_dict}
    Raises: MissingDataFileError, InvalidDataFormatError, CorruptedDataError
    """
    if not os.path.exists(filename):
        raise MissingDataFileError()

    try:
        with open(filename, "r") as f:
            content = f.read()
    except Exception:
        raise CorruptedDataError()

    blocks = [b.strip() for b in content.split('\n\n') if b.strip()]
    items = {}

    try:
        for block in blocks:
            lines = [l.strip() for l in block.split('\n') if l.strip()]
            it = parse_item_block(lines)
            validate_item_data(it)
            items[it['item_id']] = it
    except InvalidDataFormatError:
        raise
    except Exception:
        raise InvalidDataFormatError()

    return items

def validate_quest_data(quest_dict):
    """
    Validate that quest dictionary has all required fields
    
    Required fields: quest_id, title, description, reward_xp, 
                    reward_gold, required_level, prerequisite
    
    Returns: True if valid
    Raises: InvalidDataFormatError if missing required fields
    """
    required = ['quest_id', 'title', 'description', 'reward_xp', 'reward_gold', 'required_level', 'prerequisite']
    for key in required:
        if key not in quest_dict:
            raise InvalidDataFormatError(f"Missing quest field: {key}")

    # numeric checks
    try:
        quest_dict['reward_xp'] = int(quest_dict['reward_xp'])
        quest_dict['reward_gold'] = int(quest_dict['reward_gold'])
        quest_dict['required_level'] = int(quest_dict['required_level'])
    except Exception:
        raise InvalidDataFormatError("Numeric fields must be integers")

    return True

def validate_item_data(item_dict):
    """
    Validate that item dictionary has all required fields
    
    Required fields: item_id, name, type, effect, cost, description
    Valid types: weapon, armor, consumable
    
    Returns: True if valid
    Raises: InvalidDataFormatError if missing required fields or invalid type
    """
    required = ['item_id', 'name', 'type', 'effect', 'cost', 'description']
    for key in required:
        if key not in item_dict:
            raise InvalidDataFormatError(f"Missing item field: {key}")

    if item_dict['type'] not in ('weapon', 'armor', 'consumable'):
        raise InvalidDataFormatError(f"Invalid item type: {item_dict['type']}")

    # cost must be integer
    try:
        item_dict['cost'] = int(item_dict['cost'])
    except Exception:
        raise InvalidDataFormatError("Item cost must be an integer")

    return True

def create_default_data_files():
    """
    Create default data files if they don't exist
    This helps with initial setup and testing
    """
    if not os.path.exists('data'):
        os.makedirs('data')

    quests_path = os.path.join('data', 'quests.txt')
    items_path = os.path.join('data', 'items.txt')

    if not os.path.exists(quests_path):
        default_quests = (
            "QUEST_ID: first_steps\nTITLE: First Steps\nDESCRIPTION: Help the village.\nREWARD_XP: 50\nREWARD_GOLD: 25\nREQUIRED_LEVEL: 1\nPREREQUISITE: NONE\n"
        )
        with open(quests_path, 'w') as f:
            f.write(default_quests)

    if not os.path.exists(items_path):
        default_items = (
            "ITEM_ID: health_potion\nNAME: Health Potion\nTYPE: consumable\nEFFECT: health:20\nCOST: 10\nDESCRIPTION: Restores health.\n"
        )
        with open(items_path, 'w') as f:
            f.write(default_items)

    return True

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def parse_quest_block(lines):
    """
    Parse a block of lines into a quest dictionary
    
    Args:
        lines: List of strings representing one quest
    
    Returns: Dictionary with quest data
    Raises: InvalidDataFormatError if parsing fails
    """
    data = {}
    try:
        for line in lines:
            if ': ' not in line:
                raise InvalidDataFormatError(f"Invalid line: {line}")
            key, val = line.split(': ', 1)
            key = key.strip().lower()
            if key == 'quest_id':
                data['quest_id'] = val.strip()
            elif key == 'title':
                data['title'] = val.strip()
            elif key == 'description':
                data['description'] = val.strip()
            elif key == 'reward_xp':
                data['reward_xp'] = val.strip()
            elif key == 'reward_gold':
                data['reward_gold'] = val.strip()
            elif key == 'required_level':
                data['required_level'] = val.strip()
            elif key == 'prerequisite':
                data['prerequisite'] = val.strip()
            else:
                # ignore unknown fields
                data[key] = val.strip()
    except Exception:
        raise InvalidDataFormatError()

    return data

def parse_item_block(lines):
    """
    Parse a block of lines into an item dictionary
    
    Args:
        lines: List of strings representing one item
    
    Returns: Dictionary with item data
    Raises: InvalidDataFormatError if parsing fails
    """
    data = {}
    try:
        for line in lines:
            if ': ' not in line:
                raise InvalidDataFormatError(f"Invalid line: {line}")
            key, val = line.split(': ', 1)
            key = key.strip().lower()
            if key == 'item_id':
                data['item_id'] = val.strip()
            elif key == 'name':
                data['name'] = val.strip()
            elif key == 'type':
                data['type'] = val.strip()
            elif key == 'effect':
                data['effect'] = val.strip()
            elif key == 'cost':
                data['cost'] = val.strip()
            elif key == 'description':
                data['description'] = val.strip()
            else:
                data[key] = val.strip()
    except Exception:
        raise InvalidDataFormatError()

    return data

# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    print("=== GAME DATA MODULE TEST ===")
    
    # Test creating default files
    # create_default_data_files()
    
    # Test loading quests
    # try:
    #     quests = load_quests()
    #     print(f"Loaded {len(quests)} quests")
    # except MissingDataFileError:
    #     print("Quest file not found")
    # except InvalidDataFormatError as e:
    #     print(f"Invalid quest format: {e}")
    
    # Test loading items
    # try:
    #     items = load_items()
    #     print(f"Loaded {len(items)} items")
    # except MissingDataFileError:
    #     print("Item file not found")
    # except InvalidDataFormatError as e:
    #     print(f"Invalid item format: {e}")

