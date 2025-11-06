import { GoogleGenAI } from '@google/genai';

// The authentication should be automatic if it runs on Google Cloud
const ai = new GoogleGenAI({}); 

const instructionsForGemini = `
You are now a helpful agent, who tells the user about Balázs Bencs.
Title: Balázs Bencs, Senior Full Stack Engineer, 15 years of experience
Skills: Frontend (), Backend (), DevOps (), Cloud (), AI ()
`

export async function generateContent(request: any, response: any) {
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
    } catch (error) {
        console.error(error);
        response.status(500).send({ error: 'Error in Gemini model' });
    }
}