"""
COMP 163 - Project 3: Quest Chronicles
Inventory System Module - Starter Code

Name: [Your Name Here]

AI Usage: [Document any AI assistance used]

This module handles inventory management, item usage, and equipment.
"""

from custom_exceptions import (
    InventoryFullError,
    ItemNotFoundError,
    InsufficientResourcesError,
    InvalidItemTypeError
)

# Maximum inventory size
MAX_INVENTORY_SIZE = 20

# ============================================================================
# INVENTORY MANAGEMENT
# ============================================================================

def add_item_to_inventory(character, item_id):
    """
    Add an item to character's inventory
    
    Args:
        character: Character dictionary
        item_id: Unique item identifier
    
    Returns: True if added successfully
    Raises: InventoryFullError if inventory is at max capacity
    """
    inv = character.setdefault('inventory', [])
    if len(inv) >= MAX_INVENTORY_SIZE:
        raise InventoryFullError()

    inv.append(item_id)
    return True

def remove_item_from_inventory(character, item_id):
    """
    Remove an item from character's inventory
    
    Args:
        character: Character dictionary
        item_id: Item to remove
    
    Returns: True if removed successfully
    Raises: ItemNotFoundError if item not in inventory
    """
    inv = character.setdefault('inventory', [])
    if item_id not in inv:
        raise ItemNotFoundError()

    inv.remove(item_id)
    return True

def has_item(character, item_id):
    """
    Check if character has a specific item
    
    Returns: True if item in inventory, False otherwise
    """
    return item_id in character.get('inventory', [])

def count_item(character, item_id):
    """
    Count how many of a specific item the character has
    
    Returns: Integer count of item
    """
    return character.get('inventory', []).count(item_id)

def get_inventory_space_remaining(character):
    """
    Calculate how many more items can fit in inventory
    
    Returns: Integer representing available slots
    """
    used = len(character.get('inventory', []))
    return max(0, MAX_INVENTORY_SIZE - used)

def clear_inventory(character):
    """
    Remove all items from inventory
    
    Returns: List of removed items
    """
    removed = list(character.get('inventory', []))
    character['inventory'] = []
    return removed

# ============================================================================
# ITEM USAGE
# ============================================================================

def use_item(character, item_id, item_data):
    """
    Use a consumable item from inventory
    
    Args:
        character: Character dictionary
        item_id: Item to use
        item_data: Item information dictionary from game_data
    
    Item types and effects:
    - consumable: Apply effect and remove from inventory
    - weapon/armor: Cannot be "used", only equipped
    
    Returns: String describing what happened
    Raises: 
        ItemNotFoundError if item not in inventory
        InvalidItemTypeError if item type is not 'consumable'
    """
    inv = character.setdefault('inventory', [])
    if item_id not in inv:
        raise ItemNotFoundError()

    if item_data.get('type') != 'consumable':
        raise InvalidItemTypeError()

    # parse effect
    effect = item_data.get('effect', '')
    stat, val = parse_item_effect(effect)
    apply_stat_effect(character, stat, val)

    # remove one instance
    inv.remove(item_id)
    return f"Used {item_id}: {stat} {'+' if val>=0 else ''}{val}"

def equip_weapon(character, item_id, item_data):
    """
    Equip a weapon
    
    Args:
        character: Character dictionary
        item_id: Weapon to equip
        item_data: Item information dictionary
    
    Weapon effect format: "strength:5" (adds 5 to strength)
    
    If character already has weapon equipped:
    - Unequip current weapon (remove bonus)
    - Add old weapon back to inventory
    
    Returns: String describing equipment change
    Raises:
        ItemNotFoundError if item not in inventory
        InvalidItemTypeError if item type is not 'weapon'
    """
    inv = character.setdefault('inventory', [])
    if item_id not in inv:
        raise ItemNotFoundError()

    if item_data.get('type') != 'weapon':
        raise InvalidItemTypeError()

    # Unequip current weapon
    if 'equipped_weapon' in character and character['equipped_weapon']:
        # reverse old bonus
        old_id = character['equipped_weapon']
        old_bonus = character.get('equipped_weapon_bonus', 0)
        character['strength'] = character.get('strength', 0) - old_bonus
        # return old weapon to inventory
        if len(inv) >= MAX_INVENTORY_SIZE:
            raise InventoryFullError()
        inv.append(old_id)

    # apply new weapon bonus
    stat, val = parse_item_effect(item_data.get('effect', ''))
    if stat != 'strength':
        # weapons expected to modify strength
        pass
    character['strength'] = character.get('strength', 0) + val
    character['equipped_weapon'] = item_id
    character['equipped_weapon_bonus'] = val
    # remove from inventory
    inv.remove(item_id)
    return f"Equipped {item_id}" 

def equip_armor(character, item_id, item_data):
    """
    Equip armor
    
    Args:
        character: Character dictionary
        item_id: Armor to equip
        item_data: Item information dictionary
    
    Armor effect format: "max_health:10" (adds 10 to max_health)
    
    If character already has armor equipped:
    - Unequip current armor (remove bonus)
    - Add old armor back to inventory
    
    Returns: String describing equipment change
    Raises:
        ItemNotFoundError if item not in inventory
        InvalidItemTypeError if item type is not 'armor'
    """
    inv = character.setdefault('inventory', [])
    if item_id not in inv:
        raise ItemNotFoundError()

    if item_data.get('type') != 'armor':
        raise InvalidItemTypeError()

    # Unequip current armor
    if 'equipped_armor' in character and character['equipped_armor']:
        old_id = character['equipped_armor']
        old_bonus = character.get('equipped_armor_bonus', 0)
        character['max_health'] = character.get('max_health', 0) - old_bonus
        # ensure current health doesn't exceed new max
        character['health'] = min(character.get('health', 0), character['max_health'])
        if len(inv) >= MAX_INVENTORY_SIZE:
            raise InventoryFullError()
        inv.append(old_id)

    stat, val = parse_item_effect(item_data.get('effect', ''))
    if stat != 'max_health':
        pass
    character['max_health'] = character.get('max_health', 0) + val
    character['equipped_armor'] = item_id
    character['equipped_armor_bonus'] = val
    inv.remove(item_id)
    return f"Equipped {item_id}"

def unequip_weapon(character):
    """
    Remove equipped weapon and return it to inventory
    
    Returns: Item ID that was unequipped, or None if no weapon equipped
    Raises: InventoryFullError if inventory is full
    """
    if 'equipped_weapon' not in character or not character['equipped_weapon']:
        return None

    inv = character.setdefault('inventory', [])
    if len(inv) >= MAX_INVENTORY_SIZE:
        raise InventoryFullError()

    item_id = character['equipped_weapon']
    bonus = character.get('equipped_weapon_bonus', 0)
    character['strength'] = character.get('strength', 0) - bonus
    character['equipped_weapon'] = None
    character['equipped_weapon_bonus'] = 0
    inv.append(item_id)
    return item_id

def unequip_armor(character):
    """
    Remove equipped armor and return it to inventory
    
    Returns: Item ID that was unequipped, or None if no armor equipped
    Raises: InventoryFullError if inventory is full
    """
    if 'equipped_armor' not in character or not character['equipped_armor']:
        return None

    inv = character.setdefault('inventory', [])
    if len(inv) >= MAX_INVENTORY_SIZE:
        raise InventoryFullError()

    item_id = character['equipped_armor']
    bonus = character.get('equipped_armor_bonus', 0)
    character['max_health'] = character.get('max_health', 0) - bonus
    character['health'] = min(character.get('health', 0), character['max_health'])
    character['equipped_armor'] = None
    character['equipped_armor_bonus'] = 0
    inv.append(item_id)
    return item_id

# ============================================================================
# SHOP SYSTEM
# ============================================================================

def purchase_item(character, item_id, item_data):
    """
    Purchase an item from a shop
    
    Args:
        character: Character dictionary
        item_id: Item to purchase
        item_data: Item information with 'cost' field
    
    Returns: True if purchased successfully
    Raises:
        InsufficientResourcesError if not enough gold
        InventoryFullError if inventory is full
    """
    cost = int(item_data.get('cost', 0))
    if character.get('gold', 0) < cost:
        raise InsufficientResourcesError()

    if get_inventory_space_remaining(character) <= 0:
        raise InventoryFullError()

    character['gold'] = character.get('gold', 0) - cost
    add_item_to_inventory(character, item_id)
    return True

def sell_item(character, item_id, item_data):
    """
    Sell an item for half its purchase cost
    
    Args:
        character: Character dictionary
        item_id: Item to sell
        item_data: Item information with 'cost' field
    
    Returns: Amount of gold received
    Raises: ItemNotFoundError if item not in inventory
    """
    if item_id not in character.get('inventory', []):
        raise ItemNotFoundError()

    price = int(item_data.get('cost', 0)) // 2
    remove_item_from_inventory(character, item_id)
    character['gold'] = character.get('gold', 0) + price
    return price

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def parse_item_effect(effect_string):
    """
    Parse item effect string into stat name and value
    
    Args:
        effect_string: String in format "stat_name:value"
    
    Returns: Tuple of (stat_name, value)
    Example: "health:20" → ("health", 20)
    """
    if ':' not in effect_string:
        return ('', 0)

    stat, val = effect_string.split(':', 1)
    try:
        ival = int(val)
    except Exception:
        ival = 0
    return (stat.strip(), ival)

def apply_stat_effect(character, stat_name, value):
    """
    Apply a stat modification to character
    
    Valid stats: health, max_health, strength, magic
    
    Note: health cannot exceed max_health
    """
    if stat_name not in ('health', 'max_health', 'strength', 'magic'):
        return False

    if stat_name == 'health':
        character['health'] = min(character.get('max_health', 0), character.get('health', 0) + value)
    else:
        character[stat_name] = character.get(stat_name, 0) + value

    return True

def display_inventory(character, item_data_dict):
    """
    Display character's inventory in formatted way
    
    Args:
        character: Character dictionary
        item_data_dict: Dictionary of all item data
    
    Shows item names, types, and quantities
    """
    inv = character.get('inventory', [])
    counts = {}
    for it in inv:
        counts[it] = counts.get(it, 0) + 1

    print(f"\nInventory for {character.get('name', 'Player')}:\n")
    for item_id, qty in counts.items():
        name = item_data_dict.get(item_id, {}).get('name', item_id)
        typ = item_data_dict.get(item_id, {}).get('type', 'unknown')
        print(f"- {name} (id:{item_id}) x{qty} [{typ}]")
    if not counts:
        print("(empty)")
    return True

# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    print("=== INVENTORY SYSTEM TEST ===")
    
    # Test adding items
    # test_char = {'inventory': [], 'gold': 100, 'health': 80, 'max_health': 80}
    # 
    # try:
    #     add_item_to_inventory(test_char, "health_potion")
    #     print(f"Inventory: {test_char['inventory']}")
    # except InventoryFullError:
    #     print("Inventory is full!")
    
    # Test using items
    # test_item = {
    #     'item_id': 'health_potion',
    #     'type': 'consumable',
    #     'effect': 'health:20'
    # }
    # 
    # try:
    #     result = use_item(test_char, "health_potion", test_item)
    #     print(result)
    # except ItemNotFoundError:
    #     print("Item not found")

