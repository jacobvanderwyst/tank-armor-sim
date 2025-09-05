#!/usr/bin/env python3
"""
Tank Armor Penetration Simulator - Universal Launcher

This script provides a unified entry point for both CLI and GUI versions
of the Tank Armor Penetration Simulator.

Usage:
    python launcher.py            # Default: Launch GUI if available, fallback to CLI
    python launcher.py --gui      # Force GUI mode
    python launcher.py --cli      # Force CLI mode
    python launcher.py --help     # Show help information
"""

import sys
import argparse
import os

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Tank Armor Penetration Simulator - Universal Launcher",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python launcher.py              Launch GUI (default)
  python launcher.py --gui        Launch GUI interface
  python launcher.py --cli        Launch CLI interface
  python launcher.py --help       Show this help

The simulator provides educational modeling of tank armor penetration
mechanics using realistic physics calculations and advanced visualizations.
        """
    )
    
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument(
        '--gui', 
        action='store_true',
        help='Launch the graphical user interface (default)'
    )
    mode_group.add_argument(
        '--cli', 
        action='store_true',
        help='Launch the command-line interface'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='Tank Armor Penetration Simulator v2.0'
    )
    
    return parser.parse_args()

def check_gui_dependencies():
    """Check if GUI dependencies are available."""
    try:
        import tkinter
        import PIL
        return True
    except ImportError as e:
        print(f"GUI dependencies not available: {e}")
        return False

def launch_gui():
    """Launch the GUI version."""
    print("Launching Tank Armor Penetration Simulator - GUI Mode...")
    
    if not check_gui_dependencies():
        print("Error: GUI dependencies not available.")
        print("Please install required packages: pip install Pillow")
        print("Falling back to CLI mode...")
        return launch_cli()
    
    try:
        # Import and launch GUI
        from gui_main import TankArmorSimulatorGUI
        app = TankArmorSimulatorGUI()
        app.run()
        return 0
    except ImportError as e:
        print(f"Error importing GUI module: {e}")
        print("Falling back to CLI mode...")
        return launch_cli()
    except Exception as e:
        print(f"Error launching GUI: {e}")
        print("Falling back to CLI mode...")
        return launch_cli()

def launch_cli():
    """Launch the CLI version."""
    print("Launching Tank Armor Penetration Simulator - CLI Mode...")
    
    try:
        # Import and launch CLI
        sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
        from main import TankArmorSimulator
        simulator = TankArmorSimulator()
        simulator.run()
        return 0
    except ImportError as e:
        print(f"Error importing CLI module: {e}")
        print("Please ensure all required dependencies are installed.")
        return 1
    except Exception as e:
        print(f"Error launching CLI: {e}")
        return 1

def show_startup_banner():
    """Display startup banner."""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║                Tank Armor Penetration Simulator              ║
║                          Version 2.0                        ║
╠══════════════════════════════════════════════════════════════╣
║  Educational simulation of armor penetration mechanics       ║
║  Features realistic physics, advanced visualizations,       ║
║  and comprehensive ammunition/armor analysis tools          ║
╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def main():
    """Main launcher function."""
    show_startup_banner()
    
    args = parse_arguments()
    
    # Determine launch mode
    if args.cli:
        # Force CLI mode
        return launch_cli()
    elif args.gui:
        # Force GUI mode
        return launch_gui()
    else:
        # Default behavior: Try GUI first, fallback to CLI
        print("Auto-detecting best interface mode...")
        
        if check_gui_dependencies():
            print("GUI dependencies available - launching GUI mode")
            return launch_gui()
        else:
            print("GUI dependencies not available - launching CLI mode")
            return launch_cli()

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        sys.exit(1)
