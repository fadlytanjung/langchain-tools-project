#!/usr/bin/env python3
"""
Test runner script for the LangChain Tools API

This script provides an easy way to run different types of tests.
"""

import os
import sys
import subprocess
import argparse
import logging


def setup_logging(verbose=False):
    """Set up logging configuration"""
    level = logging.DEBUG if verbose else logging.INFO
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )
    
    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    # Configure root logger
    logger = logging.getLogger('test_runner')
    logger.setLevel(level)
    logger.addHandler(console_handler)
    
    return logger


def run_command(cmd, description, logger):
    """Run a command and handle errors"""
    logger.info("=" * 60)
    logger.info(f"Running: {description}")
    logger.debug(f"Command: {cmd}")
    logger.info("=" * 60)
    
    try:
        _ = subprocess.run(cmd, shell=True, check=True, capture_output=False)
        logger.info(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ {description} failed with exit code {e.returncode}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Run tests for LangChain Tools API")
    parser.add_argument("--basic", action="store_true", help="Run basic tests only")
    parser.add_argument("--all", action="store_true", help="Run all tests")
    parser.add_argument("--websocket", action="store_true", help="Run WebSocket tests only")
    parser.add_argument("--coverage", action="store_true", help="Run tests with coverage")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    # Set up logging
    logger = setup_logging(args.verbose)
    
    # Set up environment
    os.environ["OPENAI_API_KEY"] = "test-api-key"
    os.environ["DEFAULT_MODEL"] = "gpt-4o-mini"
    os.environ["OPENWEATHER_API_KEY"] = "test-weather-key"
    
    logger.info("🧪 Starting test execution")
    logger.debug("Environment variables set for testing")
    
    # Default to basic tests if no option specified
    if not any([args.basic, args.all, args.websocket, args.coverage]):
        args.basic = True
        logger.info("No test type specified, defaulting to basic tests")
    
    verbose_flag = "-v" if args.verbose else ""
    success_count = 0
    total_count = 0
    
    if args.basic:
        total_count += 1
        logger.info("🔍 Running basic tests")
        if run_command(f"python -m pytest tests/test_basic.py {verbose_flag}", "Basic Tests", logger):
            success_count += 1
    
    if args.websocket:
        total_count += 1
        logger.info("🔌 Running WebSocket tests")
        if run_command(f"python -m pytest tests/test_websocket.py {verbose_flag}", "WebSocket Tests", logger):
            success_count += 1
    
    if args.all:
        logger.info("🔍 Running all tests")
        test_files = [
            ("tests/test_basic.py", "Basic Tests"),
            ("tests/test_agent.py", "Agent Tests"),
            ("tests/test_api.py", "API Tests"),
            ("tests/test_tools.py", "Tool Tests"),
            ("tests/test_websocket.py", "WebSocket Tests"),
        ]
        
        for test_file, description in test_files:
            total_count += 1
            if run_command(f"python -m pytest {test_file} {verbose_flag}", description, logger):
                success_count += 1
    
    if args.coverage:
        total_count += 1
        logger.info("📊 Running tests with coverage")
        if run_command(f"python -m pytest tests/ --cov=app --cov-report=html {verbose_flag}", "Coverage Tests", logger):
            success_count += 1
            logger.info("📊 Coverage report generated in htmlcov/index.html")
    
    # Summary
    logger.info("=" * 60)
    logger.info("TEST SUMMARY")
    logger.info("=" * 60)
    logger.info(f"✅ Passed: {success_count}/{total_count}")
    logger.info(f"❌ Failed: {total_count - success_count}/{total_count}")
    
    if success_count == total_count:
        logger.info("🎉 All tests passed!")
        sys.exit(0)
    else:
        logger.error("💥 Some tests failed!")
        sys.exit(1)


if __name__ == "__main__":
    main() 