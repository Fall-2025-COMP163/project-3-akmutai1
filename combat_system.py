"""
COMP 163 - Project 3: Quest Chronicles
Combat System Module - Starter Code

Name: [Your Name Here]

AI Usage: [Document any AI assistance used]

Handles combat mechanics
"""

from custom_exceptions import (
    InvalidTargetError,
    CombatNotActiveError,
    CharacterDeadError,
    AbilityOnCooldownError
)

# ============================================================================
# ENEMY DEFINITIONS
# ============================================================================

def create_enemy(enemy_type):
    """
    Create an enemy based on type
    
    Example enemy types and stats:
    - goblin: health=50, strength=8, magic=2, xp_reward=25, gold_reward=10
    - orc: health=80, strength=12, magic=5, xp_reward=50, gold_reward=25
    - dragon: health=200, strength=25, magic=15, xp_reward=200, gold_reward=100
    
    Returns: Enemy dictionary
    Raises: InvalidTargetError if enemy_type not recognized
    """
    enemy_type = enemy_type.lower()

    templates = {
        'goblin': {'name': 'Goblin', 'health': 50, 'strength': 8, 'magic': 2, 'xp_reward': 25, 'gold_reward': 10},
        'orc': {'name': 'Orc', 'health': 80, 'strength': 12, 'magic': 5, 'xp_reward': 50, 'gold_reward': 25},
        'dragon': {'name': 'Dragon', 'health': 200, 'strength': 25, 'magic': 15, 'xp_reward': 200, 'gold_reward': 100}
    }

    if enemy_type not in templates:
        raise InvalidTargetError(f"Unknown enemy type: {enemy_type}")

    tpl = templates[enemy_type]
    return {
        'name': tpl['name'],
        'type': enemy_type,
        'health': tpl['health'],
        'max_health': tpl['health'],
        'strength': tpl['strength'],
        'magic': tpl['magic'],
        'xp_reward': tpl['xp_reward'],
        'gold_reward': tpl['gold_reward']
    }

def get_random_enemy_for_level(character_level):
    """
    Get an appropriate enemy for character's level
    
    Level 1-2: Goblins
    Level 3-5: Orcs
    Level 6+: Dragons
    
    Returns: Enemy dictionary
    """
    if character_level <= 2:
        return create_enemy('goblin')
    elif 3 <= character_level <= 5:
        return create_enemy('orc')
    else:
        return create_enemy('dragon')

# ============================================================================
# COMBAT SYSTEM
# ============================================================================

class SimpleBattle:
    """
    Simple turn-based combat system
    
    Manages combat between character and enemy
    """
    
    def __init__(self, character, enemy):
        """Initialize battle with character and enemy"""
        self.character = character
        self.enemy = enemy
        self.combat_active = True
        self.turn = 0
        # simple cooldown tracking for special ability usage
        self.ability_used = False
    
    def start_battle(self):
        """
        Start the combat loop
        
        Returns: Dictionary with battle results:
                {'winner': 'player'|'enemy', 'xp_gained': int, 'gold_gained': int}
        
        Raises: CharacterDeadError if character is already dead
        """
        from character_manager import is_character_dead, gain_experience, add_gold

        if is_character_dead(self.character):
            raise CharacterDeadError()

        # simple loop: player then enemy until one dies or escape
        while self.combat_active:
            self.turn += 1
            # player acts
            self.player_turn()

            # check end
            result = self.check_battle_end()
            if result is not None:
                break

            # enemy acts
            self.enemy_turn()

            result = self.check_battle_end()
            if result is not None:
                break

        winner = self.check_battle_end()

        if winner == 'player':
            rewards = get_victory_rewards(self.enemy)
            # grant rewards
            gain_experience(self.character, rewards['xp'])
            add_gold(self.character, rewards['gold'])

            return {'winner': 'player', 'xp_gained': rewards['xp'], 'gold_gained': rewards['gold']}
        elif winner == 'enemy':
            return {'winner': 'enemy', 'xp_gained': 0, 'gold_gained': 0}

        # If combat ended without clear winner (escape)
        return {'winner': 'none', 'xp_gained': 0, 'gold_gained': 0}
    
    def player_turn(self):
        """
        Handle player's turn
        
        Displays options:
        1. Basic Attack
        2. Special Ability (if available)
        3. Try to Run
        
        Raises: CombatNotActiveError if called outside of battle
        """
        if not self.combat_active:
            raise CombatNotActiveError()

        # For automated tests and non-interactive use, default to basic attack
        # If running interactively, we could prompt; here we perform basic attack
        # Basic attack
        damage = self.calculate_damage(self.character, self.enemy)
        self.apply_damage(self.enemy, damage)
        display_battle_log(f"{self.character['name']} attacks {self.enemy['name']} for {damage} damage.")

        # Reset ability flag per-turn (simple model)
        self.ability_used = False
    
    def enemy_turn(self):
        """
        Handle enemy's turn - simple AI
        
        Enemy always attacks
        
        Raises: CombatNotActiveError if called outside of battle
        """
        if not self.combat_active:
            raise CombatNotActiveError()

        damage = self.calculate_damage(self.enemy, self.character)
        self.apply_damage(self.character, damage)
        display_battle_log(f"{self.enemy['name']} attacks {self.character['name']} for {damage} damage.")
    
    def calculate_damage(self, attacker, defender):
        """
        Calculate damage from attack
        
        Damage formula: attacker['strength'] - (defender['strength'] // 4)
        Minimum damage: 1
        
        Returns: Integer damage amount
        """
        base = attacker.get('strength', 0)
        reduced = defender.get('strength', 0) // 4
        dmg = base - reduced
        if dmg < 1:
            dmg = 1
        return dmg
    
    def apply_damage(self, target, damage):
        """
        Apply damage to a character or enemy
        
        Reduces health, prevents negative health
        """
    # reduce health but not below zero
        target['health'] = max(0, target.get('health', 0) - int(damage))
    
    def check_battle_end(self):
        """
        Check if battle is over
        
        Returns: 'player' if enemy dead, 'enemy' if character dead, None if ongoing
        """
        if self.enemy.get('health', 0) <= 0:
            self.combat_active = False
            return 'player'

        if self.character.get('health', 0) <= 0:
            self.combat_active = False
            return 'enemy'

        return None
    
    def attempt_escape(self):
        """
        Try to escape from battle
        
        50% success chance
        
        Returns: True if escaped, False if failed
        """
        import random

        success = random.random() < 0.5
        if success:
            self.combat_active = False
            display_battle_log(f"{self.character['name']} successfully escaped from {self.enemy['name']}!")
            return True

        display_battle_log(f"{self.character['name']} failed to escape.")
        return False

# ============================================================================
# SPECIAL ABILITIES
# ============================================================================

def use_special_ability(character, enemy):
    """
    Use character's class-specific special ability
    
    Example abilities by class:
    - Warrior: Power Strike (2x strength damage)
    - Mage: Fireball (2x magic damage)
    - Rogue: Critical Strike (3x strength damage, 50% chance)
    - Cleric: Heal (restore 30 health)
    
    Returns: String describing what happened
    Raises: AbilityOnCooldownError if ability was used recently
    """
    cls = character.get('class', '').lower()

    if cls == 'warrior':
        return warrior_power_strike(character, enemy)
    elif cls == 'mage':
        return mage_fireball(character, enemy)
    elif cls == 'rogue':
        return rogue_critical_strike(character, enemy)
    elif cls == 'cleric':
        return cleric_heal(character)
    else:
        raise AbilityOnCooldownError("Unknown class or ability not available")

def warrior_power_strike(character, enemy):
    """Warrior special ability"""
    damage = max(1, character.get('strength', 0) * 2 - (enemy.get('strength', 0) // 4))
    enemy['health'] = max(0, enemy.get('health', 0) - damage)
    return f"{character['name']} uses Power Strike for {damage} damage!"

def mage_fireball(character, enemy):
    """Mage special ability"""
    damage = max(1, character.get('magic', 0) * 2)
    enemy['health'] = max(0, enemy.get('health', 0) - damage)
    return f"{character['name']} casts Fireball for {damage} damage!"

def rogue_critical_strike(character, enemy):
    """Rogue special ability"""
    import random

    base = character.get('strength', 0)
    if random.random() < 0.5:
        damage = max(1, base * 3 - (enemy.get('strength', 0) // 4))
        enemy['health'] = max(0, enemy.get('health', 0) - damage)
        return f"{character['name']} lands a critical strike for {damage} damage!"
    else:
        damage = max(1, base - (enemy.get('strength', 0) // 4))
        enemy['health'] = max(0, enemy.get('health', 0) - damage)
        return f"{character['name']} performs a quick strike for {damage} damage."

def cleric_heal(character):
    """Cleric special ability"""
    heal_amt = 30
    before = character.get('health', 0)
    character['health'] = min(character.get('max_health', 0), before + heal_amt)
    actual = character['health'] - before
    return f"{character['name']} casts Heal and restores {actual} HP."

# ============================================================================
# COMBAT UTILITIES
# ============================================================================

def can_character_fight(character):
    """
    Check if character is in condition to fight
    
    Returns: True if health > 0 and not in battle
    """
    return character.get('health', 0) > 0

def get_victory_rewards(enemy):
    """
    Calculate rewards for defeating enemy
    
    Returns: Dictionary with 'xp' and 'gold'
    """
    return {'xp': enemy.get('xp_reward', 0), 'gold': enemy.get('gold_reward', 0)}

def display_combat_stats(character, enemy):
    """
    Display current combat status
    
    Shows both character and enemy health/stats
    """
    print(f"\n{character['name']}: HP={character['health']}/{character['max_health']}")
    print(f"{enemy['name']}: HP={enemy['health']}/{enemy['max_health']}")

def display_battle_log(message):
    """
    Display a formatted battle message
    """
    print(f">>> {message}")

# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    print("=== COMBAT SYSTEM TEST ===")
    
    # Test enemy creation
    # try:
    #     goblin = create_enemy("goblin")
    #     print(f"Created {goblin['name']}")
    # except InvalidTargetError as e:
    #     print(f"Invalid enemy: {e}")
    
    # Test battle
    # test_char = {
    #     'name': 'Hero',
    #     'class': 'Warrior',
    #     'health': 120,
    #     'max_health': 120,
    #     'strength': 15,
    #     'magic': 5
    # }
    #
    # battle = SimpleBattle(test_char, goblin)
    # try:
    #     result = battle.start_battle()
    #     print(f"Battle result: {result}")
    # except CharacterDeadError:
    #     print("Character is dead!")

