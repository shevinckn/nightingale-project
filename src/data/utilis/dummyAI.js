window.getAIAnswer = function (question) {
  const difficultyChances = {
    easy: 0.9,
    medium: 0.7,
    hard: 0.5
  };

  // Base chance depending on difficulty
  let baseChance = difficultyChances[question.difficulty] || 0.6;

  // If there is a video with EF data, adjust the chance
  if (question.isVideo && question.metadata?.EF !== undefined) {
    const ef = question.metadata.EF;

    let predictedClass = '';
    if (ef < 40) {
      predictedClass = 'Reducerat';
      baseChance += 0.15; // Increase base chance for reduced EF
    } else if (ef >= 40 && ef < 50) {
      predictedClass = 'Abnormal';
      baseChance += 0.1; // Slightly increase chance for abnormal EF
    } else {
      predictedClass = 'Normal';
      baseChance += 0.1; // Slight increase for normal EF
    }

    // AI selects the predicted class or a wrong answer
    if (question.answers.includes(predictedClass)) {
      const willBeCorrect = Math.random() < baseChance;
      if (willBeCorrect) {
        return predictedClass; // Return the predicted class if the AI 'decides' it's correct
      } else {
        // If the AI decides it's wrong, pick another wrong answer
        const wrongAnswers = question.answers.filter(opt => opt !== predictedClass);
        return wrongAnswers[Math.floor(Math.random() * wrongAnswers.length)];
      }
    }
  }

  // Fallback – If no video or EF data, base the answer on difficulty alone
  const willBeCorrect = Math.random() < baseChance;
  if (willBeCorrect) {
    return question.correct; // AI picks the correct answer
  } else {
    // Otherwise, pick a random wrong answer
    const wrongAnswers = question.answers.filter(opt => opt !== question.correct);
    return wrongAnswers[Math.floor(Math.random() * wrongAnswers.length)];
  }
};
