"""터미널에서 동작하는 퀴즈 게임."""

import json
import os
import random

# 저장 파일은 이 스크립트와 같은 폴더(프로젝트 루트)에 둔다.
STATE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "state.json")

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


class Quiz:
    """객관식 퀴즈 한 문제를 표현한다."""

    def __init__(self, question, choices, answer, hint=None):
        self.question = question    # 문제 문장
        self.choices = choices      # 선택지 4개가 담긴 리스트
        self.answer = answer        # 정답 번호 (1~4)
        self.hint = hint            # 힌트 (없으면 None)

    def show(self, number=None):
        """문제와 선택지를 화면에 출력한다."""
        if number is None:
            print("[문제]")
        else:
            print(f"[문제 {number}]")
        print(self.question)
        for index, choice in enumerate(self.choices, start=1):
            print(f"{index}. {choice}")

    def is_correct(self, picked):
        """고른 번호가 정답이면 True를 돌려준다."""
        return picked == self.answer

    def to_dict(self):
        """JSON으로 저장할 수 있는 딕셔너리로 바꾼다."""
        return {
            "question": self.question,
            "choices": self.choices,
            "answer": self.answer,
            "hint": self.hint,
        }

    @classmethod
    def from_dict(cls, data):
        """저장 파일에서 읽은 딕셔너리로 Quiz 객체를 만든다."""
        # hint 는 나중에 추가된 항목이라 없는 예전 파일도 읽을 수 있게 get 을 쓴다.
        return cls(data["question"], data["choices"], data["answer"], data.get("hint"))


def default_quizzes():
    """저장 파일이 없을 때 사용할 기본 퀴즈 목록을 새로 만들어 돌려준다."""
    return [
        Quiz(
            "docker run -p 8080:3000 으로 컨테이너를 실행했다. 브라우저에서 접속할 때 쓰는 포트는?",
            ["3000", "8080", "둘 다 접속된다", "80"],
            2,
            "-p 호스트:컨테이너 순서를 떠올려 보세요.",
        ),
        Quiz(
            "Dockerfile의 EXPOSE 지시어에 대한 설명으로 옳은 것은?",
            [
                "호스트의 해당 포트를 자동으로 열어준다",
                "컨테이너가 쓰는 포트를 알리는 문서 역할을 한다",
                "방화벽에 허용 규칙을 추가한다",
                "컨테이너 내부의 수신 포트를 바꾼다",
            ],
            2,
            "실제로 포트를 여는 것은 docker run 의 옵션입니다.",
        ),
        Quiz(
            "컨테이너를 삭제한 뒤에도 데이터를 남기려면 무엇을 써야 하는가?",
            ["이미지 레이어", "컨테이너 쓰기 레이어", "볼륨", "환경 변수"],
            3,
            "컨테이너 바깥에 저장되는 공간이어야 합니다.",
        ),
        Quiz(
            "chmod 755 script.sh 를 실행했을 때 소유자가 갖게 되는 권한은?",
            ["읽기만", "읽기와 쓰기", "읽기와 실행", "읽기, 쓰기, 실행"],
            4,
            "읽기 4, 쓰기 2, 실행 1을 더한 값입니다.",
        ),
        Quiz(
            "디렉터리에서 실행(x) 권한이 빠지면 생기는 일은?",
            [
                "파일 이름 목록을 볼 수 없다",
                "디렉터리 이름을 바꿀 수 없다",
                "아무 영향이 없다",
                "디렉터리 안으로 들어갈 수 없다",
            ],
            4,
            "디렉터리에서 x 는 실행이 아니라 다른 뜻입니다.",
        ),
        Quiz(
            "docker ps 와 docker ps -a 의 차이는?",
            [
                "-a 는 중지된 컨테이너까지 함께 보여준다",
                "-a 는 컨테이너 대신 이미지를 보여준다",
                "-a 는 다른 사용자의 컨테이너도 보여준다",
                "둘은 완전히 같은 명령이다",
            ],
            1,
            "a 는 all 의 약자입니다.",
        ),
        Quiz(
            "실행 중인 컨테이너에 docker attach 로 들어간 뒤 exit 하면 어떻게 되는가?",
            [
                "컨테이너가 그대로 실행된다",
                "같은 이미지로 새 컨테이너가 생긴다",
                "컨테이너가 종료된다",
                "컨테이너가 자동으로 재시작된다",
            ],
            3,
            "attach 는 컨테이너의 1번 프로세스에 직접 붙습니다.",
        ),
        Quiz(
            "ls -la 에서 a 옵션이 하는 일은?",
            [
                "파일 크기를 읽기 좋은 단위로 바꾼다",
                "하위 디렉터리까지 모두 훑는다",
                "점으로 시작하는 숨김 파일까지 보여준다",
                "수정 시간 순으로 정렬한다",
            ],
            3,
            "여기서도 a 는 all 입니다.",
        ),
    ]


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


def ask_text(prompt):
    """비어 있지 않은 문자열을 받을 때까지 다시 묻는다."""
    while True:
        text = input(prompt).strip()
        if text:
            return text
        print("입력이 비어 있습니다. 다시 입력해 주세요.")


class QuizGame:
    """퀴즈 목록과 최고 점수를 들고 게임 전체를 진행한다."""

    def __init__(self):
        self.quizzes = []
        self.best_score = None

    # ----- 파일 입출력 -----

    def load(self):
        """state.json에서 퀴즈 목록과 최고 점수를 읽어 온다."""
        if not os.path.exists(STATE_FILE):
            print("저장된 파일이 없어 기본 퀴즈로 시작합니다.")
            self.reset_to_default()
            return

        try:
            with open(STATE_FILE, encoding="utf-8") as state_file:
                data = json.load(state_file)
            quizzes = [Quiz.from_dict(item) for item in data["quizzes"]]
            best_score = data.get("best_score")
        except (OSError, json.JSONDecodeError, KeyError, TypeError) as error:
            print(f"저장 파일을 읽을 수 없습니다 ({error}).")
            print("기본 퀴즈 데이터로 새로 시작합니다.")
            self.reset_to_default()
            return

        self.quizzes = quizzes
        self.best_score = best_score
        print(f"저장된 퀴즈 {len(self.quizzes)}개를 불러왔습니다.")

    def reset_to_default(self):
        """기본 퀴즈로 초기화한다."""
        self.quizzes = default_quizzes()
        self.best_score = None

    def save(self):
        """현재 상태를 state.json에 저장한다."""
        data = {
            "quizzes": [quiz.to_dict() for quiz in self.quizzes],
            "best_score": self.best_score,
        }

        try:
            with open(STATE_FILE, "w", encoding="utf-8") as state_file:
                json.dump(data, state_file, ensure_ascii=False, indent=2)
        except OSError as error:
            print(f"저장하지 못했습니다: {error}")
            return False

        return True

    # ----- 기능 -----

    def show_menu(self):
        """메뉴를 출력한다."""
        print(MENU)

    def update_best_score(self, score):
        """이번 점수가 더 높으면 최고 점수를 갱신한다."""
        if self.best_score is None or score > self.best_score:
            self.best_score = score
            print("새로운 최고 점수입니다.")

    def ask_answer(self, quiz):
        """정답 번호를 받는다. 0을 입력하면 힌트를 보여준다."""
        hint_used = False

        while True:
            picked = ask_int("정답 입력 (0=힌트): ", 0, 4)

            if picked != 0:
                return picked, hint_used

            if quiz.hint is None:
                print("이 문제에는 힌트가 없습니다.")
                continue

            if not hint_used:
                hint_used = True
                print("힌트를 보면 1점이 깎입니다.")
            print(f"힌트: {quiz.hint}")

    def play(self):
        """퀴즈를 순서대로 출제하고 결과를 보여준다."""
        if not self.quizzes:
            print("\n등록된 퀴즈가 없습니다. 메뉴 2번에서 먼저 추가해 주세요.")
            return

        available = len(self.quizzes)
        total = ask_int(f"\n몇 문제를 풀까요? (1-{available}): ", 1, available)

        # 등록된 퀴즈 중 total개를 겹치지 않게 뽑고, 순서도 매번 달라진다.
        selected = random.sample(self.quizzes, total)
        print(f"퀴즈를 시작합니다. (총 {total}문제)")

        correct = 0
        hints = 0
        for number, quiz in enumerate(selected, start=1):
            print("-" * 40)
            quiz.show(number)
            picked, hint_used = self.ask_answer(quiz)

            if hint_used:
                hints += 1

            if quiz.is_correct(picked):
                print("정답입니다.")
                correct += 1
            else:
                correct_text = quiz.choices[quiz.answer - 1]
                print(f"틀렸습니다. 정답은 {quiz.answer}번 ({correct_text})입니다.")

        print("=" * 40)
        print(f"결과: {total}문제 중 {correct}문제 정답")

        score = correct
        if hints:
            score = max(0, correct - hints)
            print(f"힌트 {hints}회 사용으로 {hints}점 차감 → 최종 {score}점")

        self.update_best_score(score)
        print("=" * 40)

        self.save()

    def add(self):
        """사용자에게 입력받아 새 퀴즈를 등록한다."""
        print("\n새 퀴즈를 추가합니다.")

        question = ask_text("문제를 입력하세요: ")

        choices = []
        for number in range(1, 5):
            choices.append(ask_text(f"선택지 {number}: "))

        answer = ask_int("정답 번호 (1-4): ", 1, 4)
        hint = input("힌트 (없으면 그냥 Enter): ").strip() or None

        self.quizzes.append(Quiz(question, choices, answer, hint))
        print(f"퀴즈가 추가되었습니다. (현재 {len(self.quizzes)}개)")

        self.save()

    def show_list(self):
        """등록된 퀴즈 목록을 보여준다."""
        if not self.quizzes:
            print("\n등록된 퀴즈가 없습니다. 메뉴 2번에서 먼저 추가해 주세요.")
            return

        print(f"\n등록된 퀴즈 {len(self.quizzes)}개")
        print("-" * 40)
        for number, quiz in enumerate(self.quizzes, start=1):
            correct_text = quiz.choices[quiz.answer - 1]
            print(f"{number}. {quiz.question}")
            print(f"   정답: {quiz.answer}번 ({correct_text})")
        print("-" * 40)

    def show_best(self):
        """최고 점수를 보여준다."""
        if self.best_score is None:
            print("\n아직 퀴즈를 푼 기록이 없습니다. 메뉴 1번에서 먼저 풀어 보세요.")
            return

        print(f"\n최고 점수: {self.best_score}문제 정답")

    # ----- 실행 -----

    def run(self):
        """저장된 상태를 불러오고 메뉴를 반복해서 보여준다."""
        self.load()

        try:
            while True:
                self.show_menu()
                choice = ask_int("선택: ", 1, 5)

                if choice == 5:
                    print("게임을 종료합니다.")
                    break

                if choice == 1:
                    self.play()
                elif choice == 2:
                    self.add()
                elif choice == 3:
                    self.show_list()
                elif choice == 4:
                    self.show_best()
        finally:
            # 정상 종료든 Ctrl+C 든 마지막 상태는 남긴다.
            self.save()


def main():
    game = QuizGame()
    try:
        game.run()
    except (KeyboardInterrupt, EOFError):
        print()
        print("입력이 중단되었습니다. 진행 상황을 저장하고 종료합니다.")


if __name__ == "__main__":
    main()
