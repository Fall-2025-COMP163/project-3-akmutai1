"""
COMP 163 - Project 3: Quest Chronicles
Main Game Module - Starter Code

Name: [Your Name Here]

AI Usage: [Document any AI assistance used]

This is the main game file that ties all modules together.
Demonstrates module integration and complete game flow.
"""

# Import all our custom modules
import character_manager
import inventory_system
import quest_handler
import combat_system
import game_data
from custom_exceptions import *

# ============================================================================
# GAME STATE
# ============================================================================

# Global variables for game data
current_character = None
all_quests = {}
all_items = {}
game_running = False

# ============================================================================
# MAIN MENU
# ============================================================================

def main_menu():
    """
    Display main menu and get player choice
    
    Options:
    1. New Game
    2. Load Game
    3. Exit
    
    Returns: Integer choice (1-3)
    """
    print("\nMain Menu:\n1) New Game\n2) Load Game\n3) Exit")
    try:
        choice = int(input("Choose 1-3: ").strip())
    except Exception:
        return 3

    if choice not in (1, 2, 3):
        return 3
    return choice

def new_game():
    """
    Start a new game
    
    Prompts for:
    - Character name
    - Character class
    
    Creates character and starts game loop
    """
    global current_character
    from character_manager import create_character, save_character
    name = input("Enter character name: ").strip()
    cls = input("Choose class (Warrior/Mage/Rogue/Cleric): ").strip()
    try:
        current_character = create_character(name, cls)
        save_character(current_character)
        print(f"Created {name} the {cls}")
        game_loop()
    except Exception as e:
        print(f"Error creating character: {e}")

def load_game():
    """
    Load an existing saved game
    
    Shows list of saved characters
    Prompts user to select one
    """
    global current_character
    from character_manager import list_saved_characters, load_character
    saves = list_saved_characters()
    if not saves:
        print("No saved games available.")
        return

    for i, s in enumerate(saves, 1):
        print(f"{i}) {s}")

    try:
        idx = int(input("Choose save number: ").strip()) - 1
        name = saves[idx]
        current_character = load_character(name)
        print(f"Loaded {name}")
        game_loop()
    except Exception as e:
        print(f"Error loading save: {e}")

# ============================================================================
# GAME LOOP
# ============================================================================

def game_loop():
    """
    Main game loop - shows game menu and processes actions
    """
    global game_running, current_character
    from character_manager import save_character

    if not current_character:
        print("No active character. Returning to main menu.")
        return

    game_running = True
    while game_running:
        choice = game_menu()
        if choice == 1:
            view_character_stats()
        elif choice == 2:
            view_inventory()
        elif choice == 3:
            quest_menu()
        elif choice == 4:
            explore()
        elif choice == 5:
            shop()
        elif choice == 6:
            try:
                save_character(current_character)
            except Exception as e:
                print(f"Save failed: {e}")
            game_running = False
        else:
            print("Invalid choice")

def game_menu():
    """
    Display game menu and get player choice
    
    Options:
    1. View Character Stats
    2. View Inventory
    3. Quest Menu
    4. Explore (Find Battles)
    5. Shop
    6. Save and Quit
    
    Returns: Integer choice (1-6)
    """
    print("\nGame Menu:\n1) View Character Stats\n2) View Inventory\n3) Quest Menu\n4) Explore\n5) Shop\n6) Save and Quit")
    try:
        return int(input("Choose 1-6: ").strip())
    except Exception:
        return 6

# ============================================================================
# GAME ACTIONS
# ============================================================================

def view_character_stats():
    """Display character information"""
    global current_character
    if not current_character:
        print("No character loaded")
        return

    print(f"\nName: {current_character.get('name')}")
    print(f"Class: {current_character.get('class')}")
    print(f"Level: {current_character.get('level')}")
    print(f"HP: {current_character.get('health')}/{current_character.get('max_health')}")
    print(f"STR: {current_character.get('strength')}, MAG: {current_character.get('magic')}")
    print(f"Gold: {current_character.get('gold')}")
    # show quest progress
    try:
        import quest_handler
        quest_handler.display_character_quest_progress(current_character, globals().get('all_quests', {}))
    except Exception:
        pass

def view_inventory():
    """Display and manage inventory"""
    global current_character, all_items
    if not current_character:
        print("No character loaded")
        return

    import inventory_system
    inventory_system.display_inventory(current_character, all_items)

def quest_menu():
    """Quest management menu"""
    global current_character, all_quests
    if not current_character:
        print("No character loaded")
        return

    import quest_handler
    print("\nQuest Menu:\n1) Active\n2) Available\n3) Completed\n4) Accept\n5) Abandon\n6) Complete\n7) Back")
    try:
        c = int(input("Choose: ").strip())
    except Exception:
        return

    if c == 1:
        active = quest_handler.get_active_quests(current_character, all_quests)
        quest_handler.display_quest_list(active)
    elif c == 2:
        avail = quest_handler.get_available_quests(current_character, all_quests)
        quest_handler.display_quest_list(avail)
    elif c == 3:
        comp = quest_handler.get_completed_quests(current_character, all_quests)
        quest_handler.display_quest_list(comp)
    elif c == 4:
        qid = input("Quest ID to accept: ").strip()
        try:
            quest_handler.accept_quest(current_character, qid, all_quests)
            print("Quest accepted")
        except Exception as e:
            print(f"Could not accept quest: {e}")
    elif c == 5:
        qid = input("Quest ID to abandon: ").strip()
        try:
            quest_handler.abandon_quest(current_character, qid)
            print("Quest abandoned")
        except Exception as e:
            print(f"Could not abandon quest: {e}")
    elif c == 6:
        qid = input("Quest ID to complete: ").strip()
        try:
            quest_handler.complete_quest(current_character, qid, all_quests)
            print("Quest completed")
        except Exception as e:
            print(f"Could not complete quest: {e}")
    else:
        return

def explore():
    """Find and fight random enemies"""
    global current_character
    
    global current_character
    if not current_character:
        print("No character loaded")
        return

    import combat_system
    try:
        enemy = combat_system.get_random_enemy_for_level(current_character.get('level', 1))
        battle = combat_system.SimpleBattle(current_character, enemy)
        result = battle.start_battle()
        print(f"Battle ended: {result}")
    except Exception as e:
        print(f"Combat error: {e}")

def shop():
    """Shop menu for buying/selling items"""
    global current_character, all_items
    
    global current_character, all_items
    if not current_character:
        print("No character loaded")
        return

    print("Shop is not implemented in demo.")
    return

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def save_game():
    """Save current game state"""
    global current_character
    
    global current_character
    from character_manager import save_character
    try:
        save_character(current_character)
        return True
    except Exception:
        return False

def load_game_data():
    """Load all quest and item data from files"""
    global all_quests, all_items
    
    global all_quests, all_items
    try:
        all_quests = game_data.load_quests()
        all_items = game_data.load_items()
    except Exception:
        # Let caller handle defaults
        raise

def handle_character_death():
    """Handle character death"""
    global current_character, game_running
    
    global current_character, game_running
    print(f"{current_character.get('name')} has died.")
    choice = input("Revive for 50% health? (y/n): ").strip().lower()
    if choice == 'y':
        from character_manager import revive_character
        revive_character(current_character)
        print("Character revived.")
    else:
        game_running = False

def display_welcome():
    """Display welcome message"""
    print("=" * 50)
    print("     QUEST CHRONICLES - A MODULAR RPG ADVENTURE")
    print("=" * 50)
    print("\nWelcome to Quest Chronicles!")
    print("Build your character, complete quests, and become a legend!")
    print()

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main game execution function"""
    
    # Display welcome message
    display_welcome()
    
    # Load game data
    try:
        load_game_data()
        print("Game data loaded successfully!")
    except MissingDataFileError:
        print("Creating default game data...")
        game_data.create_default_data_files()
        load_game_data()
    except InvalidDataFormatError as e:
        print(f"Error loading game data: {e}")
        print("Please check data files for errors.")
        return
    
    # Main menu loop
    while True:
        choice = main_menu()
        
        if choice == 1:
            new_game()
        elif choice == 2:
            load_game()
        elif choice == 3:
            print("\nThanks for playing Quest Chronicles!")
            break
        else:
            print("Invalid choice. Please select 1-3.")

if __name__ == "__main__":
    main()

