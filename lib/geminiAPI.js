"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.generateContent = generateContent;
const genai_1 = require("@google/genai");
const apiKey = process.env.GEMINI_API_KEY;
const ai = new genai_1.GoogleGenAI(apiKey ? { apiKey } : {});
const instructionsForGemini = `
You are now a helpful agent, who tells the user about Balázs Bencs.
Title: Balázs Bencs, Senior Full Stack Engineer, 15 years of experience
Skills: Frontend (), Backend (), DevOps (), Cloud (), AI ()
`;
async function generateContent(request, response) {
    response.set('Access-Control-Allow-Origin', 'https://bencsbalazs.github.io');
    if (request.method === 'OPTIONS') {
        response.set('Access-Control-Allow-Methods', 'POST');
        response.set('Access-Control-Allow-Headers', 'Content-Type');
        response.set('Access-Control-Max-Age', '3600');
        response.status(204).send('');
        return;
    }
    try {
        const prompt = request.body.prompt;
        const result = await ai.models.generateContent({
            model: 'gemini-2.5-flash',
            contents: [{ role: 'user', parts: [{ text: prompt }] }],
            config: {
                systemInstruction: instructionsForGemini,
            },
        });
        response.status(200).send({ text: result.text });
    }
    catch (error) {
        console.error(error);
        response.status(500).send({ error: 'Error in Gemini model' });
    }
}
