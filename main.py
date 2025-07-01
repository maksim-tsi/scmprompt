"""
Maritime Logistics Case Generator - Entry Point

This module serves as the main entry point for the maritime logistics case generator,
providing a command-line interface to run the pipeline and configure its behavior.
"""

import sys
import argparse
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List

# Ensure the package is in the Python path
sys.path.insert(0, str(Path(__file__).parent))

# Import core functionality
from src.pipeline.runner import run_case_generation_pipeline
from src.pipeline.checkpointing import list_checkpoints, load_checkpoint, cleanup_checkpoints, delete_checkpoint

def setup_logging(debug: bool = False) -> None:
    """
    Configure logging for the application.
    
    Args:
        debug: Whether to enable debug-level logging
    """
    log_level = logging.DEBUG if debug else logging.INFO
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    logging.basicConfig(
        level=log_level,
        format=log_format,
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(f"maritime_case_generator_{datetime.now().strftime('%Y%m%d')}.log")
        ]
    )

def main() -> None:
    """Main entry point function."""
    # Create argument parser
    parser = argparse.ArgumentParser(
        description="Maritime Logistics Case Generator",
        epilog="Generate realistic maritime logistics cases with solutions."
    )
    
    # Create subparsers for different commands
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Create parser for "generate" command
    generate_parser = subparsers.add_parser("generate", help="Generate a new case")
    generate_parser.add_argument("--resume", help="Resume from a specific case ID", default=None)
    generate_parser.add_argument("--no-checkpoints", help="Disable checkpoint saving", action="store_true")
    generate_parser.add_argument("--no-debug", help="Disable debug output", action="store_true")
    generate_parser.add_argument("--teaching-notes", help="Generate teaching notes", action="store_true")
    generate_parser.add_argument("--model", help="Override the LLM model to use", default=None)
    
    # Create parser for "list" command
    list_parser = subparsers.add_parser("list", help="List available checkpoints")
    list_parser.add_argument("--limit", help="Maximum number of checkpoints to list", type=int, default=10)
    list_parser.add_argument("--all", help="Include completed cases", action="store_true")
    
    # Create parser for "cleanup" command
    cleanup_parser = subparsers.add_parser("cleanup", help="Clean up old checkpoints")
    cleanup_parser.add_argument("--days", help="Keep checkpoints newer than specified days", type=int, default=30)
    cleanup_parser.add_argument("--keep-completed", help="Keep completed cases", action="store_true", default=True)
    
    # Create parser for "delete" command
    delete_parser = subparsers.add_parser("delete", help="Delete a specific checkpoint")
    delete_parser.add_argument("case_id", help="ID of the case to delete")
    
    # Parse arguments
    args = parser.parse_args()
    
    # Configure logging
    setup_logging(debug=not getattr(args, "no_debug", False))
    
    # Execute requested command
    if args.command == "generate":
        # Run the pipeline
        run_case_generation_pipeline(
            resume_from=args.resume,
            save_checkpoints=not args.no_checkpoints,
            debug=not args.no_debug,
            generate_teaching_materials=args.teaching_notes,
            llm_model=args.model
        )
    elif args.command == "list":
        # List checkpoints
        list_checkpoints(limit=args.limit, include_completed=args.all)
    elif args.command == "cleanup":
        # Clean up old checkpoints
        cleanup_checkpoints(keep_days=args.days, keep_completed=args.keep_completed)
    elif args.command == "delete":
        # Delete a checkpoint
        delete_checkpoint(args.case_id)
    else:
        # No command specified, show help
        parser.print_help()

if __name__ == "__main__":
    main()