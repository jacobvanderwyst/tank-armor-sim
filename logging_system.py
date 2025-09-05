"""
Comprehensive logging system for tank armor simulation.
Provides detailed logging capabilities for debugging, verification, and analysis.
"""

import os
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List
import traceback

class SimulationLogger:
    """
    Advanced logging system for tank armor simulation.
    Supports multiple log levels, structured data logging, and file output.
    """
    
    def __init__(self, log_dir: str = "logs", log_level: str = "INFO"):
        """
        Initialize the simulation logger.
        
        Args:
            log_dir: Directory to store log files
            log_level: Minimum log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # Session tracking (must be set before file handlers)
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.session_log_file = self.log_dir / f"session_{self.session_id}.json"
        
        # Set up main logger
        self.logger = logging.getLogger("TankArmorSim")
        self.logger.setLevel(getattr(logging, log_level.upper()))
        
        # Clear existing handlers
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)
        
        # Create formatters
        self.detailed_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
        )
        self.simple_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        
        # Set up file handlers (requires session_id to be set)
        self._setup_file_handlers()
        self.session_data = {
            "session_id": self.session_id,
            "start_time": datetime.now().isoformat(),
            "simulations": [],
            "errors": [],
            "performance_metrics": {}
        }
        
        self.info(f"Simulation logging session started: {self.session_id}")
    
    def _setup_file_handlers(self):
        """Set up file handlers for different log levels."""
        
        # Main log file (all levels)
        main_handler = logging.FileHandler(
            self.log_dir / "simulation_main.log", 
            mode='a', 
            encoding='utf-8'
        )
        main_handler.setFormatter(self.detailed_formatter)
        main_handler.setLevel(logging.DEBUG)
        self.logger.addHandler(main_handler)
        
        # Error log file (warnings and above)
        error_handler = logging.FileHandler(
            self.log_dir / "simulation_errors.log", 
            mode='a', 
            encoding='utf-8'
        )
        error_handler.setFormatter(self.detailed_formatter)
        error_handler.setLevel(logging.WARNING)
        self.logger.addHandler(error_handler)
        
        # Debug log file (debug level only)
        debug_handler = logging.FileHandler(
            self.log_dir / f"debug_{self.session_id}.log", 
            mode='w', 
            encoding='utf-8'
        )
        debug_handler.setFormatter(self.detailed_formatter)
        debug_handler.setLevel(logging.DEBUG)
        self.logger.addHandler(debug_handler)
    
    def debug(self, message: str, extra_data: Optional[Dict] = None):
        """Log debug message with optional structured data."""
        self.logger.debug(message)
        if extra_data:
            try:
                clean_data = self._clean_for_json(extra_data)
                self.logger.debug(f"Debug data: {json.dumps(clean_data, indent=2)}")
            except Exception as e:
                self.logger.debug(f"Debug data (serialization error): {str(extra_data)}")
                self.logger.warning(f"Failed to serialize debug data to JSON: {e}")
    
    def info(self, message: str, extra_data: Optional[Dict] = None):
        """Log info message with optional structured data."""
        self.logger.info(message)
        if extra_data:
            try:
                clean_data = self._clean_for_json(extra_data)
                self.logger.info(f"Info data: {json.dumps(clean_data, indent=2)}")
            except Exception as e:
                self.logger.info(f"Info data (serialization error): {str(extra_data)}")
                self.logger.warning(f"Failed to serialize info data to JSON: {e}")
    
    def warning(self, message: str, extra_data: Optional[Dict] = None):
        """Log warning message with optional structured data."""
        self.logger.warning(message)
        if extra_data:
            try:
                clean_data = self._clean_for_json(extra_data)
                self.logger.warning(f"Warning data: {json.dumps(clean_data, indent=2)}")
            except Exception as e:
                self.logger.warning(f"Warning data (serialization error): {str(extra_data)}")
                self.logger.warning(f"Failed to serialize warning data to JSON: {e}")
    
    def error(self, message: str, extra_data: Optional[Dict] = None, exception: Optional[Exception] = None):
        """Log error message with optional structured data and exception details."""
        self.logger.error(message)
        if extra_data:
            try:
                clean_data = self._clean_for_json(extra_data)
                self.logger.error(f"Error data: {json.dumps(clean_data, indent=2)}")
            except Exception as e:
                self.logger.error(f"Error data (serialization error): {str(extra_data)}")
                self.logger.warning(f"Failed to serialize error data to JSON: {e}")
        if exception:
            self.logger.error(f"Exception: {str(exception)}")
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            
        # Add to session errors
        error_entry = {
            "timestamp": datetime.now().isoformat(),
            "message": message,
            "data": extra_data,
            "exception": str(exception) if exception else None
        }
        self.session_data["errors"].append(error_entry)
    
    def _clean_for_json(self, obj, max_depth=10, current_depth=0):
        """Recursively clean objects for JSON serialization."""
        # Prevent infinite recursion
        if current_depth > max_depth:
            return f"<Max depth {max_depth} exceeded>"
            
        try:
            if isinstance(obj, dict):
                return {str(k): self._clean_for_json(v, max_depth, current_depth + 1) 
                       for k, v in obj.items()}
            elif isinstance(obj, (list, tuple, set)):
                return [self._clean_for_json(item, max_depth, current_depth + 1) for item in obj]
            elif hasattr(obj, '__dict__'):
                # Handle custom objects with __dict__
                return {
                    "_class": obj.__class__.__name__,
                    **{k: self._clean_for_json(v, max_depth, current_depth + 1) 
                       for k, v in obj.__dict__.items() if not k.startswith('_')}
                }
            elif hasattr(obj, '_asdict'):
                # Handle namedtuples
                return {
                    "_class": obj.__class__.__name__,
                    **self._clean_for_json(obj._asdict(), max_depth, current_depth + 1)
                }
            elif isinstance(obj, (str, int, float, bool, type(None))):
                return obj
            elif hasattr(obj, 'isoformat'):  # datetime objects
                return obj.isoformat()
            else:
                return str(obj)
        except Exception as e:
            return f"<Serialization error: {str(e)}>"
    
    
    def log_penetration_test(self,
                           ammunition_name: str,
                           armor_name: str,
                           angle: float,
                           distance: float,
                           penetration: float,
                           effective_thickness: float,
                           result: str,
                           advanced_results: Optional[Dict] = None):
        """Log detailed penetration test results."""
        
        test_data = {
            "test_type": "penetration",
            "timestamp": datetime.now().isoformat(),
            "inputs": {
                "ammunition": ammunition_name,
                "armor": armor_name,
                "angle": angle,
                "distance": distance
            },
            "results": {
                "penetration": penetration,
                "effective_thickness": effective_thickness,
                "outcome": result,
                "advanced_physics": advanced_results
            }
        }
        
        self.info(f"Penetration Test: {ammunition_name} vs {armor_name}", test_data)
        
        # Deep clean test_data for JSON serialization before adding to session
        clean_test_data = self._clean_for_json(test_data)
        self.session_data["simulations"].append(clean_test_data)
        self._update_session_file()
    
    def log_ballistic_calculation(self,
                                ammunition_name: str,
                                initial_velocity: float,
                                angle: float,
                                distance: float,
                                trajectory_points: List[Dict],
                                environmental_conditions: Optional[Dict] = None,
                                advanced_results: Optional[Dict] = None):
        """Log ballistic trajectory calculation results."""
        
        calc_data = {
            "calculation_type": "ballistic_trajectory",
            "timestamp": datetime.now().isoformat(),
            "inputs": {
                "ammunition": ammunition_name,
                "initial_velocity": initial_velocity,
                "angle": angle,
                "target_distance": distance,
                "environmental_conditions": environmental_conditions
            },
            "results": {
                "trajectory_points": len(trajectory_points),
                "max_range": max(point.get("distance", 0) for point in trajectory_points) if trajectory_points else 0,
                "max_height": max(point.get("height", 0) for point in trajectory_points) if trajectory_points else 0,
                "advanced_physics": advanced_results
            },
            "trajectory_data": trajectory_points[:10]  # Log first 10 points for verification
        }
        
        self.info(f"Ballistic Calculation: {ammunition_name} at {angle}° for {distance}m", calc_data)
        clean_calc_data = self._clean_for_json(calc_data)
        self.session_data["simulations"].append(clean_calc_data)
        self._update_session_file()
    
    def log_comparison_analysis(self,
                              comparison_type: str,
                              items: List[str],
                              criteria: str,
                              results: Dict,
                              advanced_physics: bool = False):
        """Log ammunition or armor comparison analysis."""
        
        comparison_data = {
            "analysis_type": f"{comparison_type}_comparison",
            "timestamp": datetime.now().isoformat(),
            "inputs": {
                "items": items,
                "criteria": criteria,
                "advanced_physics_enabled": advanced_physics
            },
            "results": results
        }
        
        self.info(f"{comparison_type.title()} Comparison: {', '.join(items)}", comparison_data)
        clean_comparison_data = self._clean_for_json(comparison_data)
        self.session_data["simulations"].append(clean_comparison_data)
        self._update_session_file()
    
    def log_advanced_physics_details(self,
                                   operation: str,
                                   input_parameters: Dict,
                                   physics_results: Dict):
        """Log detailed advanced physics calculations for verification."""
        
        physics_data = {
            "operation": operation,
            "timestamp": datetime.now().isoformat(),
            "input_parameters": self._clean_for_json(input_parameters),
            "physics_calculations": self._clean_for_json(physics_results)
        }
        
        self.debug(f"Advanced Physics - {operation}", physics_data)
        
        # Also save to separate advanced physics log
        physics_log_file = self.log_dir / f"advanced_physics_{self.session_id}.json"
        try:
            if physics_log_file.exists():
                with open(physics_log_file, 'r') as f:
                    existing_data = json.load(f)
            else:
                existing_data = {"session_id": self.session_id, "physics_calculations": []}
            
            existing_data["physics_calculations"].append(physics_data)
            
            # Custom JSON serializer for advanced physics data
            def physics_json_serializer(obj):
                """Custom JSON serializer for complex physics objects."""
                if hasattr(obj, '__dict__'):
                    return {k: v for k, v in obj.__dict__.items() if not k.startswith('_')}
                elif hasattr(obj, '_asdict'):
                    return obj._asdict()
                else:
                    return str(obj)
            
            with open(physics_log_file, 'w') as f:
                json.dump(existing_data, f, indent=2, default=physics_json_serializer)
        except Exception as e:
            self.error(f"Failed to write advanced physics log: {e}")
    
    def log_performance_metric(self, metric_name: str, value: float, unit: str = ""):
        """Log performance metrics for analysis."""
        
        metric_data = {
            "timestamp": datetime.now().isoformat(),
            "value": value,
            "unit": unit
        }
        
        if metric_name not in self.session_data["performance_metrics"]:
            self.session_data["performance_metrics"][metric_name] = []
        
        self.session_data["performance_metrics"][metric_name].append(metric_data)
        self.debug(f"Performance Metric - {metric_name}: {value} {unit}")
    
    def _update_session_file(self):
        """Update the session JSON file with current data."""
        try:
            # Custom JSON serializer to handle non-serializable objects
            def json_serializer(obj):
                """Custom JSON serializer for complex objects."""
                if hasattr(obj, '__dict__'):
                    # Convert objects with __dict__ to dictionary
                    return obj.__dict__
                elif hasattr(obj, '_asdict'):
                    # Handle namedtuples
                    return obj._asdict()
                else:
                    # Fallback to string representation
                    return str(obj)
            
            with open(self.session_log_file, 'w') as f:
                json.dump(self.session_data, f, indent=2, default=json_serializer)
        except Exception as e:
            self.logger.error(f"Failed to update session file: {e}")
    
    def finalize_session(self):
        """Finalize the logging session and create summary."""
        
        self.session_data["end_time"] = datetime.now().isoformat()
        self.session_data["summary"] = {
            "total_simulations": len(self.session_data["simulations"]),
            "total_errors": len(self.session_data["errors"]),
            "simulation_types": {}
        }
        
        # Count simulation types
        for sim in self.session_data["simulations"]:
            sim_type = sim.get("test_type") or sim.get("calculation_type") or sim.get("analysis_type", "unknown")
            self.session_data["summary"]["simulation_types"][sim_type] = \
                self.session_data["summary"]["simulation_types"].get(sim_type, 0) + 1
        
        self._update_session_file()
        self.info(f"Simulation session finalized: {self.session_data['summary']}")
        
        # Create session summary file
        summary_file = self.log_dir / f"session_summary_{self.session_id}.txt"
        with open(summary_file, 'w') as f:
            f.write(f"Tank Armor Simulation Session Summary\n")
            f.write(f"====================================\n\n")
            f.write(f"Session ID: {self.session_id}\n")
            f.write(f"Start Time: {self.session_data['start_time']}\n")
            f.write(f"End Time: {self.session_data['end_time']}\n\n")
            f.write(f"Total Simulations: {self.session_data['summary']['total_simulations']}\n")
            f.write(f"Total Errors: {self.session_data['summary']['total_errors']}\n\n")
            f.write("Simulation Types:\n")
            for sim_type, count in self.session_data['summary']['simulation_types'].items():
                f.write(f"  {sim_type}: {count}\n")
            
            if self.session_data["performance_metrics"]:
                f.write("\nPerformance Metrics:\n")
                for metric, values in self.session_data["performance_metrics"].items():
                    avg_value = sum(v["value"] for v in values) / len(values)
                    unit = values[0]["unit"] if values else ""
                    f.write(f"  {metric}: avg {avg_value:.3f} {unit} ({len(values)} measurements)\n")


# Global logger instance
_global_logger: Optional[SimulationLogger] = None

def get_logger() -> SimulationLogger:
    """Get the global simulation logger instance."""
    global _global_logger
    if _global_logger is None:
        _global_logger = SimulationLogger()
    return _global_logger

def initialize_logging(log_dir: str = "logs", log_level: str = "INFO") -> SimulationLogger:
    """Initialize the global logging system."""
    global _global_logger
    _global_logger = SimulationLogger(log_dir, log_level)
    return _global_logger

def finalize_logging():
    """Finalize the global logging session."""
    global _global_logger
    if _global_logger:
        _global_logger.finalize_session()
        _global_logger = None
