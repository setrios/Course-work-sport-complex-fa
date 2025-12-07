"""
Скрипт для швидкого запуску различних наборів тестів
Розташований у кореневій директорії проєкту

Використання:
    python run_tests.py           # Запустити всі тести
    python run_tests.py --auth    # Тільки тести аутентифікації
    python run_tests.py --coverage # З покриттям коду
"""

import subprocess
import sys
from pathlib import Path

# Інші опції для запуску
QUICK_RUN = "-q"  # Короткий формат
VERBOSE = "-v"    # Детальний формат
COVERAGE = "--cov=app --cov=main --cov-report=html --cov-report=term-missing"
MARKERS = {
    "auth": "-m auth",
    "sport": "-m sport",
    "ecommerce": "-m ecommerce",
    "db": "-m db_queries",
    "frontend": "-m frontend",
    "integration": "-m integration",
}

def run_pytest(args):
    """Запустити pytest з вказаними аргументами"""
    cmd = ["pytest"] + args
    print(f"Running: {' '.join(cmd)}\n")
    result = subprocess.run(cmd, cwd=Path(__file__).parent)
    return result.returncode

def main():
    if len(sys.argv) < 2:
        # Запустити всі тести
        return run_pytest([VERBOSE])
    
    arg = sys.argv[1].lower().lstrip("-")
    
    if arg == "coverage":
        # З покриттям коду
        return run_pytest([VERBOSE, COVERAGE])
    
    elif arg in MARKERS:
        # Конкретна категорія тестів
        return run_pytest([VERBOSE, MARKERS[arg]])
    
    elif arg == "quick":
        # Швидкий запуск
        return run_pytest([QUICK_RUN])
    
    elif arg == "fail-fast":
        # Стоп на першій помилці
        return run_pytest([VERBOSE, "-x"])
    
    elif arg == "parallel":
        # Паралельне виконання
        return run_pytest([VERBOSE, "-n", "auto"])
    
    elif arg == "last-failed":
        # Запустити тільки останні невдалі тести
        return run_pytest([VERBOSE, "--lf"])
    
    elif arg == "list":
        # Показати список всіх тестів без запуску
        return run_pytest(["--collect-only", "-q"])
    
    else:
        print(f"Usage: python run_tests.py [OPTION]")
        print("\nOptions:")
        print("  (none)        - Run all tests")
        print("  --coverage    - Run with coverage report")
        print("  --auth        - Run authentication tests only")
        print("  --sport       - Run sport complex tests only")
        print("  --ecommerce   - Run e-commerce tests only")
        print("  --db          - Run database query tests only")
        print("  --frontend    - Run frontend tests only")
        print("  --integration - Run integration tests only")
        print("  --quick       - Quick run with minimal output")
        print("  --fail-fast   - Stop on first failure")
        print("  --parallel    - Run tests in parallel")
        print("  --last-failed - Run only previously failed tests")
        print("  --list        - List all tests without running")
        return 1

if __name__ == "__main__":
    sys.exit(main())
