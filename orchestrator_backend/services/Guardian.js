const { GoogleGenerativeAI } = require('@google/generative-ai');
const genAI = process.env.GEMINI_API_KEY ? new GoogleGenerativeAI(process.env.GEMINI_API_KEY) : null;
module.exports = {
  ethicalReview: async (missionPurpose) => {
    if (!genAI) return { isApproved: true, justification: 'AI Core not configured. Bypassing ethical review.' };
    const model = genAI.getGenerativeModel({ model: "gemini-1.5-pro-latest" });
    const prompt = 'Review the following mission description. If it violates ethical norms, respond with only "VETO". Otherwise, respond with "PROCEED".\n\nMission: "' + missionPurpose + '"';
    const result = await model.generateContent(prompt);
    const decision = result.response.text().trim().toUpperCase();
    return { isApproved: !decision.includes('VETO'), justification: decision };
  },
  genAI: genAI
};
