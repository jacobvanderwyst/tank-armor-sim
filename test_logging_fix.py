"""
Test script to verify the logging system JSON serialization fix.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from logging_system import get_logger
from ammunition import APFSDS
from armor import CompositeArmor

def test_logging_with_advanced_physics():
    """Test that logging works with advanced physics objects."""
    
    print("🔧 Testing Logging System JSON Serialization Fix...")
    
    # Create test objects
    ammo = APFSDS(
        name="M829A4 APFSDS",
        caliber=120,
        penetrator_diameter=22,
        penetrator_mass=7.0,
        muzzle_velocity=1670,
        penetrator_length=685
    )
    
    armor = CompositeArmor(
        name="Test Composite",
        thickness=650,
        steel_layers=250,
        ceramic_layers=400,
        other_layers=0
    )
    
    # Enable advanced physics
    ammo.enable_advanced_physics()
    armor.enable_advanced_physics()
    
    # Get logger
    logger = get_logger()
    
    try:
        # Calculate penetration with advanced physics
        print("📊 Calculating penetration with advanced physics...")
        
        # Use realistic test conditions
        test_range = 2.0  # km
        test_angle = 15.0  # degrees
        
        # Get advanced results
        environmental_conditions = {
            'temperature': 20.0,
            'altitude': 100.0,
            'humidity': 50.0
        }
        
        ricochet_params = {
            'impact_angle': test_angle,
            'target_hardness': armor.hardness if hasattr(armor, 'hardness') else 1.0,
            'projectile_hardness': 1.5
        }
        
        temperature_conditions = {
            'ambient_temperature': 20.0,
            'propellant_temperature': 25.0,
            'barrel_temperature': 30.0
        }
        
        advanced_results = ammo.calculate_advanced_penetration(
            armor, 
            test_range * 1000,  # Convert km to meters
            test_angle,
            environmental_conditions,
            temperature_conditions,
            ricochet_params
        )
        
        print("✓ Advanced physics calculation completed")
        
        # Test logging with complex objects
        print("📝 Testing logging system...")
        
        logger.log_penetration_test(
            ammunition_name=ammo.name,
            armor_name=armor.name,
            angle=test_angle,
            distance=test_range * 1000,
            penetration=advanced_results['final_penetration'],
            effective_thickness=armor.get_effective_thickness('kinetic', test_angle),
            result="TEST",
            advanced_results=advanced_results
        )
        
        print("✅ Logging test PASSED!")
        print(f"   - Advanced penetration: {advanced_results['final_penetration']:.1f}mm RHA")
        print(f"   - Base penetration: {advanced_results['base_penetration']:.1f}mm RHA")
        print("   - Complex objects successfully serialized to JSON")
        
        return True
        
    except Exception as e:
        print(f"❌ Logging test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_simple_logging():
    """Test basic logging functionality."""
    
    print("\n🔧 Testing Basic Logging...")
    
    try:
        logger = get_logger()
        
        # Test with simple data
        test_data = {
            "test": "simple",
            "number": 42,
            "float": 3.14,
            "boolean": True,
            "null": None
        }
        
        logger.info("Simple test", test_data)
        logger.debug("Debug test", {"debug": True})
        logger.warning("Warning test", {"warning_level": "medium"})
        
        print("✅ Basic logging test PASSED!")
        return True
        
    except Exception as e:
        print(f"❌ Basic logging test FAILED: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Testing Logging System JSON Serialization Fix")
    print("=" * 60)
    
    # Run tests
    test1 = test_simple_logging()
    test2 = test_logging_with_advanced_physics()
    
    # Summary
    print("\n" + "=" * 60)
    if test1 and test2:
        print("🎉 All logging tests PASSED!")
        print("The JSON serialization issue has been fixed.")
    else:
        print("⚠️  Some tests failed. Check error messages above.")
    
    print("\nTest logs should be available in the 'logs/' directory.")
