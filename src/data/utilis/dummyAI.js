window.getAIAnswer = function (question) {
    const difficultyChances = {
      easy: 0.9,
      medium: 0.7,
      hard: 0.5
    };
  
    // Baschans beroende på svårighetsgrad
    let baseChance = difficultyChances[question.difficulty] || 0.6;
  
    // 💡 Om det är en videofråga med EF-data, justera chansen
    if (question.isVideo && question.metadata?.EF !== undefined) {
      const ef = question.metadata.EF;
  
      // AI förstår kategorin
      let predictedClass = '';
      if (ef < 40) {
        predictedClass = 'Reducerad';
        baseChance += 0.15;
      } else if (ef >= 40 && ef < 50) {
        predictedClass = 'Abnormal';
        baseChance += 0.1;
      } else {
        predictedClass = 'Normal';
        baseChance += 0.1;
      }
  
      // Matcha rätt alternativ
      if (question.options.includes(predictedClass)) {
        const willBeCorrect = Math.random() < baseChance;
        if (willBeCorrect) {
          return predictedClass;
        } else {
          // Välj fel alternativ (utom den rätta)
          const wrongAnswers = question.options.filter(opt => opt !== predictedClass);
          return wrongAnswers[Math.floor(Math.random() * wrongAnswers.length)];
        }
      }
    }
  
    // Fallback – om ingen video eller EF
    const willBeCorrect = Math.random() < baseChance;
    if (willBeCorrect) {
      return question.correctAnswer;
    } else {
      const wrongAnswers = question.options.filter(opt => opt !== question.correctAnswer);
      return wrongAnswers[Math.floor(Math.random() * wrongAnswers.length)];
    }
  };
  