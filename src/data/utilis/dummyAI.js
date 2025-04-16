export function getAIAnswer(question) {
const difficultyChances = {
    easy: 0.9,
    medium: 0.7,
    hard: 0.5
};

const chanceToBeCorrect = difficultyChances[question.difficulty] || 0.6;
const willBeCorrect = Math.random() < chanceToBeCorrect;

if (willBeCorrect) {
    return question.correctAnswer;
} else {
    const wrongAnswers = question.options.filter(opt => opt !== question.correctAnswer);
    return wrongAnswers[Math.floor(Math.random() * wrongAnswers.length)];
}
}
export function getAIAnswer(question) {
    const difficultyChances = {
    easy: 0.9,
    medium: 0.7,
    hard: 0.5
    };

    const chanceToBeCorrect = difficultyChances[question.difficulty] || 0.6;
    const willBeCorrect = Math.random() < chanceToBeCorrect;

    if (willBeCorrect) {
    return question.correctAnswer;
    } else {
    const wrongAnswers = question.options.filter(opt => opt !== question.correctAnswer);
      return wrongAnswers[Math.floor(Math.random() * wrongAnswers.length)];
    }
}
