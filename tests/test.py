import re
import unittest
import time

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import TestCase

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select

from quiz.tests.mocks import create_mock_survey

def test_url(url: str, pattern: str) -> bool:
    regex = re.compile(pattern)
    return regex.search(url) is not None

class NewVisitorTest(StaticLiveServerTestCase, TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.test_survey = create_mock_survey()

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.browser = webdriver.Firefox()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.browser.quit()
        super().tearDownClass()

    # Anna is a student who is learning about the ecosystems of Colombia. Anna
    # recently heard about a page that could help her study to her incomming exam.
    # The first time she enter the page, she sees the logo page, a list of topics
    # to choose from, and a help me button. 

    # She is curious about the help me button, so she click it, and it shows
    # a modal with information about the dynamic of the quizzes, it contains three
    # sections, one with general information of the site, the second with 
    # informations about the mechanics of the game, and the third one let her know
    # that she can create new quizzes.

    def test_instructions_modal(self):
        self.browser.get(self.live_server_url)

        modal = self.browser.find_element(By.ID, 'instructions')

        self.assertFalse(modal.is_displayed())

        button = self.browser.find_element(By.ID, 'info-button')
        button.click()

        self.assertTrue(modal.is_displayed())
        
        for elem in ["info-intro", "info-how", "info-create"]:
            e = modal.find_element(By.ID, elem)
            self.assertIsNotNone(e)

        modal.find_element(By.ID, 'info-close').click()
        self.assertFalse(modal.is_displayed())

    # Once she is done, she close the modal and get ready to try the quizzes.
    # She tries the topic 'Paramos'. The game starts and she is redirected to 
    # a page that asked her to be ready. 
    def test_start_game(self):
        self.browser.get(self.live_server_url)

        select_elem = self.browser.find_element(By.NAME, "topic")
        select = Select(select_elem)
        select.select_by_value("PAR")

        button = self.browser.find_element(By.ID, 'start-button')
        button.click()

        url = self.browser.current_url
        self.assertRegex(url, "quiz/.+/play", msg="Button not redirect correctly")

        button = self.browser.find_element(By.CSS_SELECTOR, 'label[for="hack"]')
        button.click()

        url = self.browser.current_url
        self.assertURLEqual(url, f"{self.live_server_url}/quiz/1/play?ready=1&question=1")


    # Once the 5 seconds of wait are done, the page reloads and she sees a
    # question. It's a simple question with two options, she choose a answer
    # and got a correct answer, she knows it for a green check that appears
    # bellow the options, after five seconds, the page change again an she is
    # in another question.
    def test_correct_answer(self):
        self.browser.get(self.live_server_url)

        select_elem = self.browser.find_element(By.NAME, "topic")
        select = Select(select_elem)
        select.select_by_value("PAR")

        button = self.browser.find_element(By.ID, 'start-button')
        button.click()

        button = self.browser.find_element(By.CSS_SELECTOR, 'label[for="hack"]')
        button.click()

        button = self.browser.find_element(By.CSS_SELECTOR, 'label[for="choice1"]')
        button.click()

        feedback = self.browser.find_element(By.ID, 'feedback')
        self.assertEqual("Correct!", feedback.text)

    #   pass

    # In this one, she choose a wrong answer, and bellow the options appears a 
    # simple rectangle with a red cross, and a paragraph with a simple explanation
    # about why the answer is wrong. 
    # def test_wrong_answer(self):
    #     pass

    # after this process repeats five times, she finish the quizz, and sees her
    # final score.
    # def test_final_score(self):
    #     pass

    # For comparison, she is able to see the top 5 scores of the quiz, in a 
    # table.
    # def test_table_for_anonymous_user(self):
    #     pass

    # def none(self):
    #     return 0

if __name__ == "__main__":
    unittest.main(warnings='ignore')

