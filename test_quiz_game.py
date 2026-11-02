"""quiz_game 동작 확인용 테스트.

표준 라이브러리만 쓴다. 실행:  python3 test_quiz_game.py
"""

import json
import os
import tempfile
import unittest
from unittest.mock import patch

import quiz_game
from quiz_game import Quiz, QuizGame, ask_int, ask_text, default_quizzes


class TestQuiz(unittest.TestCase):
    """문제 한 건을 다루는 Quiz 클래스."""

    def setUp(self):
        self.quiz = Quiz("문제", ["가", "나", "다", "라"], 2, "힌트")

    def test_정답이면_True(self):
        self.assertTrue(self.quiz.is_correct(2))

    def test_오답이면_False(self):
        self.assertFalse(self.quiz.is_correct(1))

    def test_딕셔너리로_바꿨다_되돌려도_같다(self):
        복원 = Quiz.from_dict(self.quiz.to_dict())
        self.assertEqual(복원.question, self.quiz.question)
        self.assertEqual(복원.choices, self.quiz.choices)
        self.assertEqual(복원.answer, self.quiz.answer)
        self.assertEqual(복원.hint, self.quiz.hint)

    def test_힌트_없는_예전_파일도_읽힌다(self):
        옛날 = {"question": "문제", "choices": ["가", "나", "다", "라"], "answer": 1}
        self.assertIsNone(Quiz.from_dict(옛날).hint)


class TestAskInt(unittest.TestCase):
    """숫자 입력 검증. 미션 요구 3번의 네 가지 경우."""

    def _입력(self, 값들):
        with patch("builtins.input", side_effect=값들):
            return ask_int("> ", 1, 5)

    def test_정상_입력(self):
        self.assertEqual(self._입력(["3"]), 3)

    def test_앞뒤_공백은_제거된다(self):
        self.assertEqual(self._입력(["  3  "]), 3)

    def test_빈_입력이면_다시_묻는다(self):
        self.assertEqual(self._입력(["", "3"]), 3)

    def test_숫자가_아니면_다시_묻는다(self):
        self.assertEqual(self._입력(["abc", "3"]), 3)

    def test_범위_밖이면_다시_묻는다(self):
        self.assertEqual(self._입력(["0", "9", "3"]), 3)

    def test_경계값은_통과한다(self):
        self.assertEqual(self._입력(["1"]), 1)
        self.assertEqual(self._입력(["5"]), 5)


class TestAskText(unittest.TestCase):
    """문자열 입력 검증."""

    def test_빈_입력이면_다시_묻는다(self):
        with patch("builtins.input", side_effect=["", "   ", "문제"]):
            self.assertEqual(ask_text("> "), "문제")

    def test_앞뒤_공백은_제거된다(self):
        with patch("builtins.input", side_effect=["  문제  "]):
            self.assertEqual(ask_text("> "), "문제")


class TestQuizGame(unittest.TestCase):
    """게임 전체를 관리하는 QuizGame 클래스."""

    def setUp(self):
        # 테스트마다 임시 파일을 저장 경로로 쓴다. 실제 state.json은 건드리지 않는다.
        self.임시 = tempfile.mkdtemp()
        self.경로 = os.path.join(self.임시, "state.json")
        self.원래경로 = quiz_game.STATE_FILE
        quiz_game.STATE_FILE = self.경로
        self.game = QuizGame()

    def tearDown(self):
        quiz_game.STATE_FILE = self.원래경로

    def test_기본_퀴즈는_다섯개_이상이고_형식이_맞다(self):
        목록 = default_quizzes()
        self.assertGreaterEqual(len(목록), 5)
        for 문제 in 목록:
            self.assertEqual(len(문제.choices), 4)
            self.assertIn(문제.answer, (1, 2, 3, 4))

    def test_파일이_없으면_기본_퀴즈로_시작한다(self):
        self.game.load()
        self.assertEqual(len(self.game.quizzes), len(default_quizzes()))
        self.assertIsNone(self.game.best_score)

    def test_저장한_뒤_다시_읽으면_그대로다(self):
        self.game.reset_to_default()
        self.game.best_score = 7
        self.game.quizzes.append(Quiz("추가", ["가", "나", "다", "라"], 1))
        self.game.save()

        새게임 = QuizGame()
        새게임.load()
        self.assertEqual(len(새게임.quizzes), len(self.game.quizzes))
        self.assertEqual(새게임.best_score, 7)
        self.assertEqual(새게임.quizzes[-1].question, "추가")

    def test_한글이_이스케이프되지_않는다(self):
        self.game.reset_to_default()
        self.game.save()
        with open(self.경로, encoding="utf-8") as f:
            내용 = f.read()
        self.assertNotIn("\\u", 내용)

    def test_저장_후_임시파일이_남지_않는다(self):
        self.game.reset_to_default()
        self.game.save()
        self.assertFalse(os.path.exists(self.경로 + ".tmp"))

    def test_깨진_파일이면_기본_퀴즈로_복구한다(self):
        with open(self.경로, "w", encoding="utf-8") as f:
            f.write("{{{ 깨진 JSON")
        self.game.load()
        self.assertEqual(len(self.game.quizzes), len(default_quizzes()))

    def test_필요한_키가_없어도_복구한다(self):
        with open(self.경로, "w", encoding="utf-8") as f:
            json.dump({"다른키": 1}, f)
        self.game.load()
        self.assertEqual(len(self.game.quizzes), len(default_quizzes()))

    def test_history_키가_없는_예전_파일도_읽힌다(self):
        데이터 = {"quizzes": [q.to_dict() for q in default_quizzes()], "best_score": 3}
        with open(self.경로, "w", encoding="utf-8") as f:
            json.dump(데이터, f, ensure_ascii=False)
        self.game.load()
        self.assertEqual(self.game.best_score, 3)
        self.assertEqual(self.game.history, [])

    def test_최고_점수_갱신_규칙(self):
        self.game.best_score = None
        self.game.update_best_score(5)
        self.assertEqual(self.game.best_score, 5)

        self.game.update_best_score(3)          # 낮으면 그대로
        self.assertEqual(self.game.best_score, 5)

        self.game.update_best_score(5)          # 동점도 그대로
        self.assertEqual(self.game.best_score, 5)

        self.game.update_best_score(8)          # 높으면 갱신
        self.assertEqual(self.game.best_score, 8)

    def test_힌트를_보면_사용_여부가_참이_된다(self):
        문제 = Quiz("문제", ["가", "나", "다", "라"], 2, "힌트다")
        with patch("builtins.input", side_effect=["0", "2"]):
            고른값, 힌트썼나 = self.game.ask_answer(문제)
        self.assertEqual(고른값, 2)
        self.assertTrue(힌트썼나)

    def test_같은_문제에서_힌트를_두번_봐도_한번으로_센다(self):
        문제 = Quiz("문제", ["가", "나", "다", "라"], 2, "힌트다")
        with patch("builtins.input", side_effect=["0", "0", "2"]):
            _, 힌트썼나 = self.game.ask_answer(문제)
        self.assertTrue(힌트썼나)   # True 하나뿐이라 차감도 1회

    def test_힌트가_없는_문제에서_0을_누르면_안내만_한다(self):
        문제 = Quiz("문제", ["가", "나", "다", "라"], 1)
        with patch("builtins.input", side_effect=["0", "1"]):
            고른값, 힌트썼나 = self.game.ask_answer(문제)
        self.assertEqual(고른값, 1)
        self.assertFalse(힌트썼나)

    def test_퀴즈가_없으면_풀기가_그냥_돌아온다(self):
        self.game.quizzes = []
        self.game.play()        # 예외 없이 끝나야 한다

    def test_퀴즈_추가가_목록과_파일에_반영된다(self):
        self.game.reset_to_default()
        이전 = len(self.game.quizzes)
        입력 = ["새 문제", "가", "나", "다", "라", "2", "힌트"]
        with patch("builtins.input", side_effect=입력):
            self.game.add()
        self.assertEqual(len(self.game.quizzes), 이전 + 1)

        새게임 = QuizGame()
        새게임.load()
        self.assertEqual(새게임.quizzes[-1].question, "새 문제")

    def test_퀴즈_삭제가_목록과_파일에_반영된다(self):
        self.game.reset_to_default()
        이전 = len(self.game.quizzes)
        지울문제 = self.game.quizzes[0].question
        with patch("builtins.input", side_effect=["1"]):
            self.game.delete()
        self.assertEqual(len(self.game.quizzes), 이전 - 1)
        self.assertNotEqual(self.game.quizzes[0].question, 지울문제)

    def test_삭제를_0으로_취소하면_그대로다(self):
        self.game.reset_to_default()
        이전 = len(self.game.quizzes)
        with patch("builtins.input", side_effect=["0"]):
            self.game.delete()
        self.assertEqual(len(self.game.quizzes), 이전)


class TestMenuFlow(unittest.TestCase):
    """메뉴를 선택했을 때 해당 기능이 불리는지 확인한다."""

    def setUp(self):
        self.임시 = tempfile.mkdtemp()
        self.원래경로 = quiz_game.STATE_FILE
        quiz_game.STATE_FILE = os.path.join(self.임시, "state.json")

    def tearDown(self):
        quiz_game.STATE_FILE = self.원래경로

    def _메뉴(self, 번호):
        game = QuizGame()
        with patch("builtins.input", side_effect=[str(번호), "7"]):
            return game

    def test_각_번호가_해당_기능을_부른다(self):
        짝 = {1: "play", 2: "add", 3: "show_list", 4: "show_best",
              5: "delete", 6: "show_history"}
        for 번호, 메서드 in 짝.items():
            with self.subTest(메뉴=번호):
                game = QuizGame()
                with patch.object(QuizGame, 메서드) as 불린것, \
                     patch("builtins.input", side_effect=[str(번호), "7"]):
                    game.run()
                불린것.assert_called_once()

    def test_7번을_누르면_종료된다(self):
        game = QuizGame()
        with patch("builtins.input", side_effect=["7"]):
            game.run()      # 무한 루프에 빠지지 않고 끝나야 한다

    def test_중단되어도_예외가_새어나가지_않는다(self):
        game = QuizGame()
        with patch("builtins.input", side_effect=KeyboardInterrupt):
            with self.assertRaises(KeyboardInterrupt):
                game.run()  # run 은 저장만 하고 그대로 올려보낸다


if __name__ == "__main__":
    unittest.main(verbosity=2)
