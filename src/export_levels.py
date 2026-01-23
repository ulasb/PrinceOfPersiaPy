"""
Export all Prince of Persia levels to JSON format.
"""

from levels.loader import LevelLoader


def export_all_levels():
    """Export all 15 levels (0-14) to JSON"""
    loader = LevelLoader()
    
    print("Exporting all Prince of Persia levels...")
    print("=" * 60)
    
    for level_num in range(15):
        print(f"\nLevel {level_num}:")
        level = loader.load_level(level_num)
        
        if level:
            # Count active guards
            active_guards = sum(1 for g in level.info.guards if g.is_active)
            
            print(f"  ✓ Loaded successfully")
            print(f"  Kid starts: Screen {level.info.kid_start_screen}, "
                  f"Block {level.info.kid_start_block}")
            print(f"  Active Guards: {active_guards}")
            
            # Export to JSON
            output_file = f"assets/levels/level_{level_num:02d}.json"
            loader.export_to_json(level, output_file)
        else:
            print(f"  ✗ Failed to load")
    
    print("\n" + "=" * 60)
    print("Export complete!")
    print("\nJSON files saved to: assets/levels/")


if __name__ == "__main__":
    export_all_levels()
