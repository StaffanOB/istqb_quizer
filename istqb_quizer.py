#!/usr/bin/env python3
import os
import json
import platform
import signal
import sys
from datetime import datetime
import textwrap
import logging
from logging.handlers import TimedRotatingFileHandler

# Track stats
correct = 0
wrong = 0
skipped = 0
wrong_details = []

def clear_screen():
    os.system("cls" if platform.system() == "Windows" else "clear")

def setup_logger():
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)

    log_filename = os.path.join(log_dir, "quiz_log.log")

    logger = logging.getLogger("QuizLogger")
    logger.setLevel(logging.INFO)

    # Avoid duplicate handlers if setup is called multiple times
    if not logger.handlers:
        handler = TimedRotatingFileHandler(
            log_filename,
            when="midnight",
            interval=1,
            backupCount=7,
            encoding="utf-8"
        )
        formatter = logging.Formatter('%(asctime)s | %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger

def list_json_files(directory="questions"):
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"📁 Created missing directory: {directory}")
        print("⚠️  No JSON files found. Please add quiz files to the 'questions/' folder.")
        return []

    files = [f for f in os.listdir(directory) if f.endswith(".json")]
    return sorted(files, key=lambda f: f.lower())

def load_questions(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        # questions = load_questions(filepath)  # Removed recursive call
        total_questions = len(questions)
        return json.load(f)

def graceful_exit(signum, frame):
    clear_screen()
    print("\n\n👋 Graceful shutdown (Ctrl+C detected)")
    show_results(partial=True)
    sys.exit(0)
def wrap_text(text, width=120, indent=""):
    return "\n".join(textwrap.wrap(text, width=width, initial_indent=indent, subsequent_indent=indent))

def ask_question(q, current_number, total):
    global correct, wrong, skipped, wrong_details
    clear_screen()
    print(wrap_text(f"📝 Question {current_number} of {total}", 120))
    print(wrap_text(q['question'], 120))
    print("")  # blank line before alternatives
    for key, val in q['alternatives'].items():
        print(wrap_text(f"  {key}. {val}", 120))

    first_attempt = True
    attempted = False
    answered = False
    counted_as_wrong = False

    while not answered:
        print("")  # Blank line before input
        answer = input("Your answer (A/B/C/D), or 's' to skip: ").strip().upper()

        if answer == 'S':
            if not attempted:
                skipped += 1
                print("⏭️ Skipped.")
            else:
                print("⏭️ Skipped after attempting. Not counted as skipped.")
            answered = True

        elif answer == q['correct_answer']:
            if first_attempt:
                correct += 1
                print("✅ Correct on first try!")
            else:
                if not counted_as_wrong:
                    wrong += 1
                    counted_as_wrong = True
                    wrong_details.append({
                        "number": current_number,
                        "question": q['question'],
                        "correct_answer": q['correct_answer'],
                        "explanation": q.get("explanation")
                    })
                print("✅ Correct (but not counted as correct – previous wrong attempt)")
            answered = True

        elif answer in q['alternatives']:
            if first_attempt:
                first_attempt = False
            if not counted_as_wrong:
                wrong += 1
                counted_as_wrong = True
                wrong_details.append({
                    "number": current_number,
                    "question": q['question'],
                    "correct_answer": q['correct_answer'],
                    "explanation": q.get("explanation")
                })
            attempted = True
            print("❌ Wrong answer. Try again or type 's' to skip.")

        else:
            print("Invalid input. Please enter A, B, C, D, or 's'.")

    # Show explanation if available
    explanation = q.get("explanation")
    if explanation:
        print("\n💡 Explanation:")
        print(wrap_text(explanation, 120, indent="   "))
    input("\nPress Enter to continue...")

def show_results(partial=False):
    total = correct + wrong + skipped
    percent = (correct / total * 100) if total > 0 else 0

    label = "📊 Partial Quiz Summary:" if partial else "📊 Final Quiz Summary:"
    print(f"\n{label}")
    print(f"✅ Correct on first try: {correct}")
    print(f"❌ Wrong on first try (or eventually correct after wrong): {wrong}")
    print(f"⏭️ Skipped: {skipped}")
    print(f"📈 Score: {percent:.1f}%")

    if wrong_details:
        print("\n❗ Questions you missed or got wrong on first try:")
        for d in wrong_details:
            print(f"{d['number']}. {d['question']}")
            print(f"   ➤ Correct answer: {d['correct_answer']}")
            if d.get("explanation"):
                print(f"   💡 Explanation: {d['explanation']}")
            print()


def write_results(quiz_name):
    # Ensure the results directory exists
    results_dir = "results"
    os.makedirs(results_dir, exist_ok=True)

    # Build the filename
    date_str = datetime.now().strftime("%Y-%m-%d")
    base_filename = f"{quiz_name}_{date_str}"
    run_number = 1

    while True:
        filename = f"{base_filename}_run{run_number}.md"
        filepath = os.path.join(results_dir, filename)
        if not os.path.exists(filepath):
            break
        run_number += 1

    # Build result content
    total = correct + wrong + skipped
    percent = (correct / total * 100) if total > 0 else 0

    lines = [
        f"# Quiz Results – {quiz_name}",
        f"**Date:** {date_str}",
        f"**Run:** {run_number}",
        "",
        "## Summary",
        f"- ✅ Correct on first try: **{correct}**",
        f"- ❌ Wrong on first try: **{wrong}**",
        f"- ⏭️ Skipped: **{skipped}**",
        f"- 📈 Score: **{percent:.1f}%**",
        ""
    ]

    if wrong_details:
        lines.append("## Questions You Missed or Skipped")
        for d in wrong_details:
            lines.append(f"### {d['number']}. {d['question']}")
            lines.append(f"- **Correct Answer:** {d['correct_answer']}")
            if d.get("explanation"):
                lines.append(f"- 💡 **Explanation:** {d['explanation']}")
            lines.append("")

    # Save to file
    with open(filepath, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"\n📄 Results saved to: {filepath}")

#!/usr/bin/env python3

def print_banner():
    print(r"""

    ┳┏┓┏┳┓┏┓┳┓  ┏┓┳┳┳┏┓┏┓┏┓┳┓    
    ┃┗┓ ┃ ┃┃┣┫  ┃┃┃┃┃┏┛┏┛┣ ┣┫    
    ┻┗┛ ┻ ┗┻┻┛  ┗┻┗┛┻┗┛┗┛┗┛┛┗ 
    An ISTQB Practice Quizzer
    """)


def main():
    signal.signal(signal.SIGINT, graceful_exit)

    clear_screen()
    print_banner()  # Show ASCII logo

    print("📂 Available quiz files: ")
    json_files = list_json_files("questions")
    if not json_files:
        print("❌ No JSON quiz files found in the 'questions/' directory.")
        return

    for i, file in enumerate(json_files):
        print(f"{i + 1}. {file[:-5]}")  # Strip '.json' from display

    while True:
        try:
            selected = int(input(" Enter the number of the quiz file to load: ")) - 1
            if 0 <= selected < len(json_files):
                break
            else:
                print("Please enter a valid number.")
        except ValueError:
            print("Please enter a number.")

    filepath = os.path.join("questions", json_files[selected])
    quiz_name = json_files[selected][:-5]
    logger = setup_logger()
    logger.info(f"STARTING QUIZ from file: {json_files[selected]}")

    with open(filepath, "r", encoding="utf-8") as f:
        questions = json.load(f)

    total_questions = len(questions)

    for idx, q in enumerate(questions):
        clear_screen()
        print(wrap_text(f"📝 Question {idx + 1} of {total_questions}", 120))
        print(wrap_text(q['question'], 120))
        print("")  # blank line before alternatives
        for key, val in q['alternatives'].items():
            print(wrap_text(f"  {key}. {val}", 120))

        first_attempt = True
        attempted = False
        answered = False
        counted_as_wrong = False

        while not answered:
            print("")  # Blank line before input
            answer = input("Your answer (A/B/C/D), or 's' to skip: ").strip().upper()

            if answer == 'S':
                if not attempted:
                    global skipped
                    skipped += 1
                    print("⏭️ Skipped.")
                    logger.info(f"Question {idx + 1}: Skipped")
                else:
                    print("⏭️ Skipped after attempting. Not counted as skipped.")
                answered = True

            elif answer == q['correct_answer']:
                if first_attempt:
                    global correct
                    correct += 1
                    print("✅ Correct on first try!")
                    logger.info(f"Question {idx + 1}: Selected: {answer} | Correct on first try")
                else:
                    global wrong
                    if not counted_as_wrong:
                        wrong += 1
                        counted_as_wrong = True
                        wrong_details.append({
                            "number": idx + 1,
                            "question": q['question'],
                            "correct_answer": q['correct_answer'],
                            "explanation": q.get("explanation")
                        })
                    print("✅ Correct (but not counted as correct – previous wrong attempt)")
                    logger.info(f"Question {idx + 1}: Selected: {answer} | Correct after wrong attempt")
                answered = True

            elif answer in q['alternatives']:
                if first_attempt:
                    first_attempt = False
                if not counted_as_wrong:
                    wrong += 1
                    counted_as_wrong = True
                    wrong_details.append({
                        "number": idx + 1,
                        "question": q['question'],
                        "correct_answer": q['correct_answer'],
                        "explanation": q.get("explanation")
                    })
                attempted = True
                print("❌ Wrong answer. Try again or type 's' to skip.")
                logger.info(f"Question {idx + 1}: Selected: {answer} | Wrong answer on first try")

            else:
                print("Invalid input. Please enter A, B, C, D, or 's'.")

        explanation = q.get("explanation")
        if explanation:
            print("💡 Explanation:")
            print(wrap_text(explanation, 120, indent="   "))
        input("Press Enter to continue...")

    clear_screen()
    show_results()
    write_results(quiz_name=quiz_name)


if __name__ == "__main__":
    main()
