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


class Quiz:
    """객관식 퀴즈 한 문제를 표현한다."""

    def __init__(self, question, choices, answer):
        self.question = question    # 문제 문장
        self.choices = choices      # 선택지 4개가 담긴 리스트
        self.answer = answer        # 정답 번호 (1~4)

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


def default_quizzes():
    """저장 파일이 없을 때 사용할 기본 퀴즈 목록을 새로 만들어 돌려준다."""
    return [
        Quiz(
            "docker run -p 8080:3000 으로 컨테이너를 실행했다. 브라우저에서 접속할 때 쓰는 포트는?",
            ["3000", "8080", "둘 다 접속된다", "80"],
            2,
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
        ),
        Quiz(
            "컨테이너를 삭제한 뒤에도 데이터를 남기려면 무엇을 써야 하는가?",
            ["이미지 레이어", "컨테이너 쓰기 레이어", "볼륨", "환경 변수"],
            3,
        ),
        Quiz(
            "chmod 755 script.sh 를 실행했을 때 소유자가 갖게 되는 권한은?",
            ["읽기만", "읽기와 쓰기", "읽기와 실행", "읽기, 쓰기, 실행"],
            4,
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
