window.getAIAnswer = async function (question) {
  if (question.isVideo && question.metadata) {
    const payload = {
      ESV: question.metadata.ESV,
      EDV: question.metadata.EDV,
      FrameHeight: question.metadata.FrameHeight,
      FrameWidth: question.metadata.FrameWidth,
      FPS: question.metadata.FPS,
      NumberOfFrames: question.metadata.NumberOfFrames
    };

    const response = await fetch("http://localhost:5000/api/ai-answer", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    const data = await response.json();
    return data.answer;
  }

  // Fallback (om ingen metadata finns)
  return question.correct;
};
