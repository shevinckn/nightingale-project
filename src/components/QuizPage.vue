<template>
    <div v-if="!isQuizFinished" class="quiz-container">
      <h2 class="question">{{ currentQuestion.question }}</h2>
  
      <ul class="options">
        <li
          v-for="option in currentQuestion.options"
          :key="option"
          :class="{
            correct: showResult && option === currentQuestion.correctAnswer,
            wrong: showResult && option === aiAnswer && option !== currentQuestion.correctAnswer,
          }"
        >
          {{ option }}
        </li>
      </ul>
  
      <p v-if="isThinking">🤖 AI tänker...</p>
      <p v-else-if="showResult">AI svarade: <strong>{{ aiAnswer }}</strong></p>
  
      <p>Poäng: {{ aiScore }}</p>
  
      <button @click="nextQuestion" :disabled="isThinking || !showResult">
        Nästa fråga
      </button>
    </div>
  
    <div v-else class="result-container">
      <h2>✅ Quiz klart!</h2>
      <p>AI:s slutpoäng: <strong>{{ aiScore }}/{{ questions.length }}</strong></p>
      <p class="comment">{{ getComment() }}</p>
  
      <button @click="restartQuiz">🔁 Starta om</button>
    </div>
  </template>
  
  <script setup>
  import { ref, computed } from 'vue';
  import questions from '@/data/questions.json';
  import { getAIAnswer } from '@/utils/dummyAI';
  
  const currentIndex = ref(0);
  const aiAnswer = ref(null);
  const aiScore = ref(0);
  const isThinking = ref(false);
  const showResult = ref(false);
  const isQuizFinished = ref(false);
  
  const currentQuestion = computed(() => questions[currentIndex.value]);
  
  function simulateAIAnswer() {
    isThinking.value = true;
    showResult.value = false;
  
    setTimeout(() => {
      aiAnswer.value = getAIAnswer(currentQuestion.value);
      isThinking.value = false;
      showResult.value = true;
  
      if (aiAnswer.value === currentQuestion.value.correctAnswer) {
        aiScore.value++;
      }
    }, 1500);
  }
  
  function nextQuestion() {
    if (currentIndex.value < questions.length - 1) {
      currentIndex.value++;
      simulateAIAnswer();
    } else {
      isQuizFinished.value = true;
    }
  }
  
  function restartQuiz() {
    currentIndex.value = 0;
    aiScore.value = 0;
    isQuizFinished.value = false;
    simulateAIAnswer();
  }
  
  function getComment() {
    const ratio = aiScore.value / questions.length;
    if (ratio === 1) return '🚀 Perfekt! AI är på topp!';
    if (ratio > 0.6) return '🧠 Bra jobbat, AI!';
    if (ratio > 0.3) return '😅 AI gjorde sitt bästa!';
    return '🤖 AI behöver lite mer träning!';
  }
  
  simulateAIAnswer();
  </script>
  
  <style scoped>
  .quiz-container, .result-container {
    max-width: 600px;
    margin: auto;
    padding: 20px;
    text-align: center;
  }
  
  .question {
    font-size: 1.4rem;
    margin-bottom: 10px;
  }
  
  .options {
    list-style: none;
    padding: 0;
    margin-bottom: 10px;
  }
  
  .options li {
    padding: 10px;
    margin: 6px 0;
    border-radius: 10px;
    background: #eee;
    transition: background-color 0.3s ease;
  }
  
  .options li.correct {
    background-color: #c8f7c5;
  }
  
  .options li.wrong {
    background-color: #f7c5c5;
  }
  
  .comment {
    font-style: italic;
    font-size: 1.1rem;
    margin-top: 10px;
  }
  </style>