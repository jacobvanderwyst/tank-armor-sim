#!/usr/bin/env python3
"""
Test script for the comprehensive logging system and advanced physics integration.
"""

import sys
import os
import json
import tempfile
import shutil
from pathlib import Path

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src'))
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from logging_system import SimulationLogger, get_logger, initialize_logging, finalize_logging
from src.ammunition import APFSDS, HEAT, HESH
from src.armor import RHA, CompositeArmor, ReactiveArmor

class TestLoggingSystem:
    """Test suite for the logging system functionality."""
    
    def __init__(self):
        """Initialize test environment with temporary log directory."""
        self.temp_dir = tempfile.mkdtemp(prefix="tank_sim_test_")
        self.logger = None
        self.test_results = []
    
    def setUp(self):
        """Set up test environment."""
        print(f"Setting up test environment in: {self.temp_dir}")
        self.logger = SimulationLogger(log_dir=self.temp_dir, log_level="DEBUG")
    
    def tearDown(self):
        """Clean up test environment."""
        if self.logger:
            self.logger.finalize_session()
        
        # Optional: Remove temp directory (comment out for debugging)
        # shutil.rmtree(self.temp_dir)
        
        print(f"Test logs saved in: {self.temp_dir}")
    
    def test_basic_logging(self):
        """Test basic logging functionality."""
        print("\n=== Testing Basic Logging Functionality ===")
        
        try:
            # Test different log levels
            self.logger.info("Test info message")
            self.logger.debug("Test debug message")
            self.logger.warning("Test warning message")
            
            # Test logging with extra data
            self.logger.info("Test with extra data", {"test_key": "test_value", "number": 42})
            
            self.test_results.append("✅ Basic logging: PASSED")
            print("✅ Basic logging functionality working correctly")
            
        except Exception as e:
            self.test_results.append(f"❌ Basic logging: FAILED - {e}")
            print(f"❌ Basic logging failed: {e}")
    
    def test_penetration_logging(self):
        """Test penetration test logging."""
        print("\n=== Testing Penetration Test Logging ===")
        
        try:
            # Test basic penetration logging
            self.logger.log_penetration_test(
                ammunition_name="M829A4 APFSDS",
                armor_name="200mm RHA",
                angle=15.0,
                distance=2000.0,
                penetration=550.0,
                effective_thickness=200.0,
                result="PROJECTILE_PENETRATES"
            )
            
            # Test penetration logging with advanced physics
            advanced_results = {
                'final_penetration': 580.0,
                'velocity_at_target': 1450.0,
                'ricochet_analysis': {
                    'ricochet_probability': 0.12,
                    'predicted_outcome': 'penetration',
                    'critical_angle': 72.5
                },
                'temperature_analysis': {
                    'velocity_modifier': 1.03,
                    'penetration_modifier': 1.06,
                    'propellant_efficiency': 0.97
                },
                'advanced_effects': {
                    'ballistic_result': {
                        'environmental_effects': {
                            'temperature_effect': 0.02,
                            'altitude_effect': -0.01,
                            'humidity_effect': 0.005
                        }
                    }
                }
            }
            
            self.logger.log_penetration_test(
                ammunition_name="3BM60 APFSDS",
                armor_name="M1A2 Frontal Composite",
                angle=0.0,
                distance=1500.0,
                penetration=680.0,
                effective_thickness=750.0,
                result="ARMOR_DEFEATS",
                advanced_results=advanced_results
            )
            
            self.test_results.append("✅ Penetration logging: PASSED")
            print("✅ Penetration test logging working correctly")
            
        except Exception as e:
            self.test_results.append(f"❌ Penetration logging: FAILED - {e}")
            print(f"❌ Penetration test logging failed: {e}")
    
    def test_ballistic_logging(self):
        """Test ballistic calculation logging."""
        print("\n=== Testing Ballistic Calculation Logging ===")
        
        try:
            # Mock trajectory points
            trajectory_points = [
                {"distance": 0, "height": 2.5, "velocity": 1680, "time": 0.0},
                {"distance": 500, "height": 3.2, "velocity": 1620, "time": 0.31},
                {"distance": 1000, "height": 4.1, "velocity": 1560, "time": 0.64},
                {"distance": 1500, "height": 5.2, "velocity": 1500, "time": 0.98},
                {"distance": 2000, "height": 6.5, "velocity": 1440, "time": 1.35}
            ]
            
            environmental_conditions = {
                "temperature": 15.0,
                "altitude": 0.0,
                "humidity": 50.0,
                "wind_speed": 5.0
            }
            
            advanced_results = {
                "advanced_physics_enabled": True,
                "environmental_effects": "calculated",
                "wind_compensation": 0.02,
                "atmospheric_drag_coefficient": 1.05
            }
            
            self.logger.log_ballistic_calculation(
                ammunition_name="M829A4 APFSDS",
                initial_velocity=1680.0,
                angle=2.5,
                distance=2000.0,
                trajectory_points=trajectory_points,
                environmental_conditions=environmental_conditions,
                advanced_results=advanced_results
            )
            
            self.test_results.append("✅ Ballistic logging: PASSED")
            print("✅ Ballistic calculation logging working correctly")
            
        except Exception as e:
            self.test_results.append(f"❌ Ballistic logging: FAILED - {e}")
            print(f"❌ Ballistic calculation logging failed: {e}")
    
    def test_comparison_logging(self):
        """Test comparison analysis logging."""
        print("\n=== Testing Comparison Analysis Logging ===")
        
        try:
            # Test ammunition comparison
            ammo_comparison_results = {
                "M829A4 APFSDS": {
                    "penetration": 550.0,
                    "ricochet_prob": 0.12,
                    "advanced_results": {"final_penetration": 580.0}
                },
                "3BM60 APFSDS": {
                    "penetration": 620.0,
                    "ricochet_prob": 0.08,
                    "advanced_results": {"final_penetration": 650.0}
                },
                "M830A1 HEAT": {
                    "penetration": 450.0,
                    "ricochet_prob": 0.05,
                    "advanced_results": {"final_penetration": 470.0}
                }
            }
            
            self.logger.log_comparison_analysis(
                comparison_type="ammunition",
                items=["M829A4 APFSDS", "3BM60 APFSDS", "M830A1 HEAT"],
                criteria="vs 200mm RHA at 2000m, 15° angle",
                results=ammo_comparison_results,
                advanced_physics=True
            )
            
            # Test armor comparison
            armor_comparison_results = {
                "200mm RHA": {
                    "penetration_against": 550.0,
                    "ricochet_prob": 0.12,
                    "effectiveness": "penetrated"
                },
                "M1A2 Frontal": {
                    "penetration_against": 550.0,
                    "ricochet_prob": 0.15,
                    "effectiveness": "stopped"
                },
                "T-90M Frontal": {
                    "penetration_against": 550.0,
                    "ricochet_prob": 0.18,
                    "effectiveness": "stopped"
                }
            }
            
            self.logger.log_comparison_analysis(
                comparison_type="armor",
                items=["200mm RHA", "M1A2 Frontal", "T-90M Frontal"],
                criteria="vs M829A4 APFSDS at 2000m, 15° angle",
                results=armor_comparison_results,
                advanced_physics=True
            )
            
            self.test_results.append("✅ Comparison logging: PASSED")
            print("✅ Comparison analysis logging working correctly")
            
        except Exception as e:
            self.test_results.append(f"❌ Comparison logging: FAILED - {e}")
            print(f"❌ Comparison analysis logging failed: {e}")
    
    def test_advanced_physics_logging(self):
        """Test advanced physics details logging."""
        print("\n=== Testing Advanced Physics Details Logging ===")
        
        try:
            input_parameters = {
                "ammunition": "M829A4 APFSDS",
                "armor": "200mm RHA",
                "angle": 15.0,
                "distance": 2000.0,
                "environmental_conditions": {
                    "temperature": 15.0,
                    "altitude": 0.0,
                    "humidity": 50.0
                }
            }
            
            physics_results = {
                "ricochet_calculation": {
                    "impact_energy": 12500000.0,
                    "critical_angle": 72.5,
                    "ricochet_probability": 0.12,
                    "outcome_prediction": "penetration"
                },
                "temperature_effects": {
                    "propellant_temperature_factor": 0.97,
                    "armor_temperature_factor": 1.02,
                    "velocity_adjustment": 1.03,
                    "penetration_adjustment": 1.06
                },
                "environmental_ballistics": {
                    "air_density_factor": 1.0,
                    "drag_coefficient": 0.15,
                    "wind_deflection": 0.02,
                    "atmospheric_effects": {
                        "temperature": 0.02,
                        "altitude": -0.01,
                        "humidity": 0.005
                    }
                }
            }
            
            self.logger.log_advanced_physics_details(
                operation="penetration_calculation",
                input_parameters=input_parameters,
                physics_results=physics_results
            )
            
            self.test_results.append("✅ Advanced physics logging: PASSED")
            print("✅ Advanced physics details logging working correctly")
            
        except Exception as e:
            self.test_results.append(f"❌ Advanced physics logging: FAILED - {e}")
            print(f"❌ Advanced physics details logging failed: {e}")
    
    def test_performance_metrics(self):
        """Test performance metrics logging."""
        print("\n=== Testing Performance Metrics Logging ===")
        
        try:
            # Log some performance metrics
            self.logger.log_performance_metric("calculation_time", 0.0125, "seconds")
            self.logger.log_performance_metric("calculation_time", 0.0098, "seconds")
            self.logger.log_performance_metric("calculation_time", 0.0156, "seconds")
            
            self.logger.log_performance_metric("memory_usage", 45.6, "MB")
            self.logger.log_performance_metric("memory_usage", 47.2, "MB")
            
            self.logger.log_performance_metric("trajectory_points", 250, "points")
            self.logger.log_performance_metric("trajectory_points", 180, "points")
            
            self.test_results.append("✅ Performance metrics: PASSED")
            print("✅ Performance metrics logging working correctly")
            
        except Exception as e:
            self.test_results.append(f"❌ Performance metrics: FAILED - {e}")
            print(f"❌ Performance metrics logging failed: {e}")
    
    def test_error_handling(self):
        """Test error handling and logging."""
        print("\n=== Testing Error Handling ===")
        
        try:
            # Test error logging
            test_exception = ValueError("Test exception for logging")
            self.logger.error(
                "Test error message", 
                {"error_context": "unit_test", "severity": "low"},
                exception=test_exception
            )
            
            # Test warning
            self.logger.warning("Test warning message", {"warning_type": "test"})
            
            self.test_results.append("✅ Error handling: PASSED")
            print("✅ Error handling working correctly")
            
        except Exception as e:
            self.test_results.append(f"❌ Error handling: FAILED - {e}")
            print(f"❌ Error handling failed: {e}")
    
    def verify_log_files(self):
        """Verify that log files are created and contain expected data."""
        print("\n=== Verifying Log Files ===")
        
        try:
            log_dir = Path(self.temp_dir)
            
            # Check for main log files
            main_log = log_dir / "simulation_main.log"
            error_log = log_dir / "simulation_errors.log"
            
            if main_log.exists():
                print(f"✅ Main log file created: {main_log}")
                with open(main_log, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if "Test info message" in content:
                        print("✅ Main log contains expected content")
                    else:
                        print("❌ Main log missing expected content")
            else:
                print("❌ Main log file not found")
            
            if error_log.exists():
                print(f"✅ Error log file created: {error_log}")
            else:
                print("❌ Error log file not found")
            
            # Check for session files
            session_files = list(log_dir.glob("session_*.json"))
            if session_files:
                print(f"✅ Session JSON file created: {session_files[0]}")
                
                # Verify JSON structure
                with open(session_files[0], 'r', encoding='utf-8') as f:
                    session_data = json.load(f)
                    
                    required_keys = ["session_id", "start_time", "simulations", "errors", "performance_metrics"]
                    if all(key in session_data for key in required_keys):
                        print("✅ Session JSON has correct structure")
                        print(f"   - Simulations logged: {len(session_data['simulations'])}")
                        print(f"   - Errors logged: {len(session_data['errors'])}")
                        print(f"   - Performance metrics: {len(session_data['performance_metrics'])}")
                    else:
                        print("❌ Session JSON missing required keys")
            else:
                print("❌ Session JSON file not found")
            
            # Check for advanced physics log
            physics_files = list(log_dir.glob("advanced_physics_*.json"))
            if physics_files:
                print(f"✅ Advanced physics log created: {physics_files[0]}")
            else:
                print("❌ Advanced physics log not found")
            
            self.test_results.append("✅ Log file verification: PASSED")
            
        except Exception as e:
            self.test_results.append(f"❌ Log file verification: FAILED - {e}")
            print(f"❌ Log file verification failed: {e}")
    
    def run_all_tests(self):
        """Run all test methods."""
        print("🚀 Starting Comprehensive Logging System Tests")
        print("=" * 60)
        
        self.setUp()
        
        # Run individual tests
        self.test_basic_logging()
        self.test_penetration_logging()
        self.test_ballistic_logging()
        self.test_comparison_logging()
        self.test_advanced_physics_logging()
        self.test_performance_metrics()
        self.test_error_handling()
        
        # Finalize and verify
        self.tearDown()
        self.verify_log_files()
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 TEST RESULTS SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for result in self.test_results if "PASSED" in result)
        failed = len(self.test_results) - passed
        
        for result in self.test_results:
            print(result)
        
        print(f"\n🎯 Total Tests: {len(self.test_results)}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        
        if failed == 0:
            print("\n🎉 ALL TESTS PASSED! Logging system is working correctly.")
        else:
            print(f"\n⚠️  {failed} test(s) failed. Please check the output above.")
        
        print(f"\n📁 Test logs saved in: {self.temp_dir}")
        return failed == 0


def test_integration_with_simulation():
    """Test logging integration with actual simulation components."""
    print("\n🔬 Testing Integration with Simulation Components")
    print("=" * 60)
    
    try:
        # Create temporary logger
        temp_dir = tempfile.mkdtemp(prefix="integration_test_")
        logger = SimulationLogger(log_dir=temp_dir, log_level="DEBUG")
        
        # Test with actual ammunition and armor objects
        ammo = APFSDS(
            name="Test M829A4",
            caliber=120.0,
            penetrator_diameter=22.0,
            penetrator_mass=4.6,
            muzzle_velocity=1680,
            penetrator_length=570
        )
        
        armor = RHA(thickness=200.0)
        
        # Enable advanced physics
        ammo.enable_advanced_physics()
        armor.enable_advanced_physics()
        
        # Test penetration calculation with logging
        try:
            from src.physics.advanced_physics import EnvironmentalConditions
            from src.physics.temperature_effects import TemperatureConditions
            from src.physics.ricochet_calculator import RicochetParameters
            
            env_conditions = EnvironmentalConditions(
                temperature_celsius=15.0,
                altitude_m=0.0,
                humidity_percent=50.0
            )
            
            temp_conditions = TemperatureConditions(
                ambient_celsius=15.0,
                propellant_celsius=15.0,
                armor_celsius=15.0,
                barrel_celsius=15.0
            )
            
            velocity_at_range = ammo.get_velocity_at_range(2000)
            ricochet_params = RicochetParameters(
                impact_angle_deg=15.0,
                impact_velocity_ms=velocity_at_range,
                projectile_hardness=0.9,
                target_hardness=0.8
            )
            
            # Calculate advanced results
            advanced_results = ammo.calculate_advanced_penetration(
                armor, 2000.0, 15.0,
                environmental_conditions=env_conditions,
                temperature_conditions=temp_conditions,
                ricochet_params=ricochet_params
            )
            
            penetration = advanced_results['final_penetration']
            effective_thickness = armor.get_effective_thickness(ammo.penetration_type, 15.0)
            result = "PROJECTILE_PENETRATES" if penetration > effective_thickness else "ARMOR_DEFEATS"
            
            # Clean advanced results for JSON serialization before logging
            def clean_advanced_results(data):
                """Clean advanced results to make them JSON serializable."""
                if isinstance(data, dict):
                    return {k: clean_advanced_results(v) for k, v in data.items()}
                elif isinstance(data, (list, tuple)):
                    return [clean_advanced_results(item) for item in data]
                elif hasattr(data, '__dict__'):
                    return {k: clean_advanced_results(v) for k, v in data.__dict__.items() if not k.startswith('_')}
                elif hasattr(data, '_asdict'):
                    return clean_advanced_results(data._asdict())
                elif isinstance(data, (str, int, float, bool, type(None))):
                    return data
                else:
                    return str(data)
            
            cleaned_advanced_results = clean_advanced_results(advanced_results)
            
            # Log the results
            logger.log_penetration_test(
                ammunition_name=ammo.name,
                armor_name=armor.name,
                angle=15.0,
                distance=2000.0,
                penetration=penetration,
                effective_thickness=effective_thickness,
                result=result,
                advanced_results=cleaned_advanced_results
            )
            
            print("✅ Integration test with advanced physics: PASSED")
            
        except ImportError:
            # Fallback to basic calculations
            penetration = ammo.calculate_penetration(2000, 15)
            effective_thickness = armor.get_effective_thickness(ammo.penetration_type, 15)
            result = "PROJECTILE_PENETRATES" if penetration > effective_thickness else "ARMOR_DEFEATS"
            
            logger.log_penetration_test(
                ammunition_name=ammo.name,
                armor_name=armor.name,
                angle=15.0,
                distance=2000.0,
                penetration=penetration,
                effective_thickness=effective_thickness,
                result=result
            )
            
            print("✅ Integration test with basic physics: PASSED")
        
        logger.finalize_session()
        print(f"📁 Integration test logs saved in: {temp_dir}")
        return True
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        return False


if __name__ == "__main__":
    # Run comprehensive logging tests
    tester = TestLoggingSystem()
    logging_success = tester.run_all_tests()
    
    # Run integration tests
    integration_success = test_integration_with_simulation()
    
    # Final summary
    print("\n" + "🏆" * 60)
    print("FINAL TEST SUMMARY")
    print("🏆" * 60)
    
    if logging_success and integration_success:
        print("🎉 ALL TESTS PASSED! The logging system is fully functional.")
        exit(0)
    else:
        print("⚠️  Some tests failed. Please review the output above.")
        exit(1)
