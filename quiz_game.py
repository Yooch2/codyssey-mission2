"""터미널에서 동작하는 퀴즈 게임."""

MENU = """
========================================
            나만의 퀴즈 게임
========================================
1. 퀴즈 풀기
2. 퀴즈 추가
3. 퀴즈 목록
4. 점수 확인
5. 종료
========================================"""


def ask_int(prompt, low, high):
    """low 이상 high 이하의 정수를 받을 때까지 다시 묻는다."""
    while True:
        answer = input(prompt).strip()

        if not answer:
            print("입력이 비어 있습니다. 다시 입력해 주세요.")
            continue

        try:
            number = int(answer)
        except ValueError:
            print(f"'{answer}'는 숫자가 아닙니다. 다시 입력해 주세요.")
            continue

        if not low <= number <= high:
            print(f"{low}부터 {high} 사이의 숫자를 입력해 주세요.")
            continue

        return number


def show_menu():
    print(MENU)


def run():
    while True:
        show_menu()
        choice = ask_int("선택: ", 1, 5)

        if choice == 5:
            print("게임을 종료합니다.")
            break

        print("아직 구현되지 않은 기능입니다.")


def main():
    try:
        run()
    except (KeyboardInterrupt, EOFError):
        print()
        print("입력이 중단되어 게임을 종료합니다.")


if __name__ == "__main__":
    main()
