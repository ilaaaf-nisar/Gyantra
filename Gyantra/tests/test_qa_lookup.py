import unittest

from qa_lookup import find_reviewed_answer, load_reviewed_answers


class ReviewedAnswerMatchingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.answers = load_reviewed_answers()

    def test_matches_plural_paraphrase(self):
        answer = find_reviewed_answer("what are data structures", self.answers)

        self.assertIn("A data structure is a way of organizing", answer)

    def test_matches_reworded_algorithm_question(self):
        answer = find_reviewed_answer("tell me about algorithms", self.answers)

        self.assertIn("An algorithm is a finite", answer)

    def test_does_not_confuse_data_types_with_data_structures(self):
        answer = find_reviewed_answer("what is a data type", self.answers)

        self.assertIn("Python Tutorial 1: Data Types", answer)
        self.assertNotIn("A data structure is", answer)

    def test_unrelated_question_does_not_match(self):
        self.assertIsNone(
            find_reviewed_answer("what is the weather tomorrow", self.answers)
        )

    def test_acknowledges_user_saying_they_are_doing_great(self):
        answer = find_reviewed_answer("I'm doing great", self.answers)

        self.assertIn("Glad to hear it", answer)
        self.assertIn("what would you like to study", answer.casefold())

    def test_matches_thanks_paraphrase(self):
        answer = find_reviewed_answer("thanks for your help", self.answers)

        self.assertIn("You're very welcome", answer)


if __name__ == "__main__":
    unittest.main()
