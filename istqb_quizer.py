import os
import json
import platform
import signal
import sys

# Track quiz state
current_index = 0
questions = []
correct = 0
wrong = 0
wrong_details = []

def clear_screen():
    os.system("cls" if platform.system() == "Windows" else "clear")

def list_json_files(directory):
    dirFiles = os.listdir(directory)
    dirFiles.sort()
    sorted(dirFiles)
    return [f for f in dirFiles if f.endswith(".json")]

def load_questions(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

def graceful_exit(signum, frame):
    clear_screen()
    print("\n\n👋 Graceful shutdown initiated (Ctrl+C pressed)")
    total_answered = correct + wrong
    percent = (correct / total_answered) * 100 if total_answered > 0 else 0

    print("\n📊 Partial Quiz Summary:")
    print(f"✅ Correct on first try: {correct}")
    print(f"❌ Wrong on first try or skipped: {wrong}")
    print(f"📈 Score: {percent:.1f}%")

    if wrong_details:
        print("\n❗ Questions missed so far:")
        for d in wrong_details:
            print(f"{d['number']}. {d['question']}")
            print(f"   ➤ Correct answer: {d['correct_answer']}")
            print(f"   💡 Explanation: {d.get('explanation', 'No explanation provided.')}\n")
    sys.exit(0)

def ask_question(q, current_number, total):
    global correct, wrong, wrong_details
    clear_screen()
    print(f"📝 Question {current_number} of {total}")
    print(q['question'])
    for key, val in q['alternatives'].items():
        print(f"  {key}. {val}")

    first_attempt = True

    while True:
        answer = input("Your answer (A/B/C/D), or 's' to skip: ").strip().upper()
        if answer == 'S':
            print("⏭️ Skipped.")
            wrong += 1
            wrong_details.append({
                "number": current_number,
                "question": q['question'],
                "correct_answer": q['correct_answer'],
                "explanation": q.get("explanation")
            })
            if "explanation" in q:
                print(f"\n💡 Explanation: {q['explanation']}")
            input("\nPress Enter to continue...")
            return
        elif answer == q['correct_answer']:
            if first_attempt:
                correct += 1
                print("✅ Correct!")
            else:
                wrong += 1
                print("✅ Correct! (but after one or more failed attempts)")
                wrong_details.append({
                    "number": current_number,
                    "question": q['question'],
                    "correct_answer": q['correct_answer'],
                    "explanation": q.get("explanation")
                })

            if "explanation" in q:
                print(f"\n💡 Explanation: {q['explanation']}")
            input("\nPress Enter to continue...")
            return
        elif answer in q['alternatives']:
            if first_attempt:
                first_attempt = False
                wrong += 1
                wrong_details.append({
                    "number": current_number,
                    "question": q['question'],
                    "correct_answer": q['correct_answer'],
                    "explanation": q.get("explanation")
                })
            print("❌ Wrong answer. Try again or type 's' to skip.")
        else:
            print("Invalid input. Please enter A, B, C, D, or 's' to skip.")

def main():
    global questions

    signal.signal(signal.SIGINT, graceful_exit)  # Handle Ctrl+C

    clear_screen()
    print("📂 Available quiz files:\n")
    json_files = list_json_files(".")
    if not json_files:
        print("No JSON quiz files found in the current directory.")
        return

    for i, file in enumerate(json_files):
        print(f"{i + 1}. {file}")

    while True:
        try:
            selected = int(input("\nEnter the number of the quiz file to load: ")) - 1
            if 0 <= selected < len(json_files):
                break
            else:
                print("Please enter a valid number.")
        except ValueError:
            print("Please enter a number.")

    questions = load_questions(json_files[selected])
    total_questions = len(questions)

    for idx, q in enumerate(questions):
        ask_question(q, idx + 1, total_questions)

    clear_screen()
    percent = (correct / total_questions) * 100 if total_questions > 0 else 0
    print("\n📊 Quiz Summary:")
    print(f"✅ Correct on first try: {correct}")
    print(f"❌ Wrong on first try or skipped: {wrong}")
    print(f"📈 Score: {percent:.1f}%")

    if wrong_details:
        print("\n❗ Questions you missed on the first try:")
        for d in wrong_details:
            print(f"{d['number']}. {d['question']}")
            print(f"   ➤ Correct answer: {d['correct_answer']}")
            print(f"   💡 Explanation: {d.get('explanation', 'No explanation provided.')}\n")

if __name__ == "__main__":
    main()
