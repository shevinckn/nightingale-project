<template>
  <div v-if="!isQuizFinished">
    <div v-if="currentQuestion">
      <video :src="currentQuestion.videoUrl" controls width="400" />

      <p>{{ currentQuestion.question }}</p>

      <div>
        <button
          v-for="answer in currentQuestion.answers"
          :key="answer"
          @click="handleAnswer(answer)"
        >
          {{ answer }}
        </button>
      </div>
    </div>
  </div>

  <div v-else>
    <h2>Quiz klart!</h2>
    <p>Ditt resultat: {{ userScore }} / {{ questions.length }}</p>
    <p>AI:s resultat: {{ aiScore }} / {{ questions.length }}</p>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue';

// State
const questions = ref([]);
const currentIndex = ref(0);
const userScore = ref(0);
const aiScore = ref(0);
const isQuizFinished = ref(false);

// Hämta frågor från backend
onMounted(async () => {
  try {
    const response = await fetch('http://localhost:5000/api/questions');
    const data = await response.json();
    questions.value = data;
  } catch (error) {
    console.error('Kunde inte hämta frågor:', error);
  }
});

// Returnera nuvarande fråga
const currentQuestion = computed(() => questions.value[currentIndex.value]);

// Hämta AI-svar
async function getAIAnswerFromAPI(questionObj) {
  try {
    const response = await fetch('http://localhost:5000/api/predict', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        ESV: questionObj.metadata.ESV,
        EDV: questionObj.metadata.EDV,
        FrameHeight: questionObj.metadata.FrameHeight,
        FrameWidth: questionObj.metadata.FrameWidth,
        FPS: questionObj.metadata.FPS,
        NumberOfFrames: questionObj.metadata.NumberOfFrames,
      }),
    });

    const data = await response.json();
    return data.prediction;
  } catch (error) {
    console.error('API error:', error);
    return "Normal"; // fallback
  }
}

// Hantera svar
async function handleAnswer(userAnswer) {
  const question = currentQuestion.value;
  const correctAnswer = question.correct;

  const aiAnswer = await getAIAnswerFromAPI(question);

  if (userAnswer === correctAnswer) userScore.value++;
  if (aiAnswer === correctAnswer) aiScore.value++;

  currentIndex.value++;

  if (currentIndex.value >= questions.value.length) {
    isQuizFinished.value = true;
  }
}

// Skicka resultat till backend
watch(isQuizFinished, async (finished) => {
  if (finished) {
    try {
      const response = await fetch("http://localhost:5000/api/submit_results", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          userID: "test_user", // Kan ersättas med dynamisk ID
          score: userScore.value,
          ai_score: aiScore.value,
          total: questions.value.length,
        }),
      });

      const data = await response.json();
      console.log("Resultat sparat:", data);
    } catch (error) {
      console.error("Misslyckades spara resultat:", error);
    }
  }
});
</script>

<style scoped>
button {
  margin: 8px;
  padding: 10px 20px;
  font-size: 16px;
}
</style>
