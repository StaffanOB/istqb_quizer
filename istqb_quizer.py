import os
import json

def list_json_files(directory):
    return [f for f in os.listdir(directory) if f.endswith(".json")]

def load_questions(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

def ask_question(q, current_number, total):
    print(f"\n📝 Question {current_number} of {total}: {q['question']}")
    for key, val in q['alternatives'].items():
        print(f"  {key}. {val}")

    first_attempt = True

    while True:
        answer = input("Your answer (A/B/C/D), or 's' to skip: ").strip().upper()
        if answer == 'S':
            print("⏭️ Skipped.")
            return False
        elif answer == q['correct_answer']:
            if first_attempt:
                print("✅ Correct!")
                return True
            else:
                print("✅ Correct! (but after one or more failed attempts)")
                return False
        elif answer in q['alternatives']:
            if first_attempt:
                first_attempt = False
            print("❌ Wrong answer. Try again or type 's' to skip.")
        else:
            print("Invalid input. Please enter A, B, C, D, or 's' to skip.")

def main():
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

    print(f"\n🧠 Starting quiz: {json_files[selected]}")
    print(f"Total questions: {total_questions}")

    correct = 0
    wrong = 0
    wrong_details = []

    for idx, q in enumerate(questions):
        question_number = idx + 1
        result = ask_question(q, question_number, total_questions)
        if result:
            correct += 1
        else:
            wrong += 1
            wrong_details.append({
                "number": question_number,
                "question": q['question'],
                "correct_answer": q['correct_answer']
            })

    total = correct + wrong
    percent = (correct / total) * 100 if total > 0 else 0

    print("\n📊 Quiz Summary:")
    print(f"✅ Correct on first try: {correct}")
    print(f"❌ Wrong on first try or skipped: {wrong}")
    print(f"📈 Score: {percent:.1f}%")

    if wrong_details:
        print("\n❗ Questions you missed on the first try:")
        for d in wrong_details:
            print(f"{d['number']}. {d['question']}")
            print(f"   ➤ Correct answer: {d['correct_answer']}\n")

if __name__ == "__main__":
    main()
