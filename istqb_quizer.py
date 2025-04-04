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
        return json.load(f)

def graceful_exit(signum, frame):
    clear_screen()
    print("\n\n👋 Graceful shutdown (Ctrl+C detected)")
    show_results(partial=True)
    sys.exit(0)
def wrap_text(text, width=120, indent=""):
    return "\n".join(textwrap.wrap(text, width=width, initial_indent=indent, subsequent_indent=indent))



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

def fortmat_fixed_width(number: int, width: int) -> str:
    return str(number).rjust(width)

def print_banner():
    print(r"""

    ┳┏┓┏┳┓┏┓┳┓  ┏┓┳┳┳┏┓┏┓┏┓┳┓ 
    ┃┗┓ ┃ ┃┃┣┫  ┃┃┃┃┃┏┛┏┛┣ ┣┫ 
    ┻┗┛ ┻ ┗┻┻┛  ┗┻┗┛┻┗┛┗┛┗┛┛┗ 
    An ISTQB Practice Quizzer 
    """)


def main():
    global correct, wrong, skipped, wrong_details
    signal.signal(signal.SIGINT, graceful_exit)

    clear_screen()
    print_banner()  # Show ASCII logo

    print("Available quiz files: ")
    json_files = list_json_files("questions")
    if not json_files:
        print("❌ No JSON quiz files found in the 'questions/' directory.")
        return

    for i, file in enumerate(json_files):
        print(f"  {fortmat_fixed_width(i + 1, 3)} | {file[:-5]}")  # Strip '.json' from display

    while True:
        try:
            selected = int(input("\nEnter the number of the quiz file to load: ")) - 1
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

    # Normalize answers
    for q in questions:
        if isinstance(q['correct_answer'], list):
            q['correct_answer'] = [a.upper() for a in q['correct_answer']]
        else:
            q['correct_answer'] = q['correct_answer'].upper()
        q['alternatives'] = {k.upper(): v for k, v in q['alternatives'].items()}

    total_questions = len(questions)

    for idx, q in enumerate(questions):

        clear_screen()
        print(wrap_text(f"📝 Question {idx + 1} of {total_questions}", 120))
        print(wrap_text(q['question'], 120))
        print("")  # blank line before alternatives
        for key, val in q['alternatives'].items():
            print(wrap_text(f"  {key.upper()}. {val}", 120))

        first_attempt = True
        attempted = False
        answered = False
        counted_as_wrong = False

        while not answered:
            print("")  # Blank line before input
            answer = input("Your answer (A/B/C/D or multiple like 'A,C'), or 's' to skip: ").strip().upper()
            
            if answer == 'S':
                if not attempted:
                    skipped += 1
                    print("⏭️ Skipped.")
                    logger.info(f"Question {idx + 1}: Skipped")
                else:
                    print("⏭️ Skipped after attempting. Not counted as skipped.")
                answered = True
            else:
                selected_answers = [a.strip() for a in answer.split(',') if a.strip()]
            
                # Validate input
                if not all(a in q['alternatives'] for a in selected_answers):
                    print("Invalid input. Please enter valid option letters (A-D), separated by commas.")
                    logger.info(f"Invalid input.")
                    continue
            
                # Check correctness
                if isinstance(q['correct_answer'], list):
                    is_correct = sorted(selected_answers) == sorted(q['correct_answer'])
                else:
                    is_correct = len(selected_answers) == 1 and selected_answers[0] == q['correct_answer']
            
                if is_correct:
                    if first_attempt:
                        correct += 1
                        print("✅ Correct on first try!")
                        logger.info(f"Question {idx + 1}: Selected: {answer} | Correct ")
                    else:
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
            
                else:
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
                    logger.info(f"Question {idx + 1}: Selected: {answer} | Wrong answer")


        explanation = q.get("explanation")
        if explanation:
            print("💡 Explanation:")
            print(wrap_text(explanation, 120, indent="   "))
        input("Press Enter to continue...")

    clear_screen()
    show_results()
    write_results(quiz_name=quiz_name)

def is_correct_answer(user_input, correct_answer):
    """
    Check if user input matches the correct answer.
    user_input: list of answers (e.g., ['A'] or ['C', 'D'])
    correct_answer: a string (e.g., 'A') or list (e.g., ['C', 'D'])
    """
    if isinstance(correct_answer, list):
        return sorted(user_input) == sorted(correct_answer)
    else:
        return len(user_input) == 1 and user_input[0] == correct_answer

if __name__ == "__main__":
    main()
