1. Define reusable prompts
Create a template prompt per chapter style. For example:

Keep variants handy (portrait, square, concise, detailed). When you hit a new chapter, drop in its specific numbers and let the AI do the layout heavy lifting.

2. Feed the AI structured source material
AI outputs improve when the input is organized. For each chapter, supply a mini “factsheet”:

Chapter title and intent
Core parameters (e.g., stack size, blinds, pot)
Analytic thresholds, EVs, formulas
Solver settings (iterations, buckets)
Key takeaways or insights
Paste that into your prompt along with the layout instructions. This keeps the AI from hallucinating and ensures accuracy.

3. Experiment with aspect ratios and detail levels
Since you haven’t settled on portrait/landscape/square or concise/standard/detailed:

Generate a quick draft in each aspect ratio.
See how it feels embedded in your README vs social platforms vs a print-style handout.
Decide which aspect ratio serves your main audience, but keep the others as optional exports. The same prompt with “make this square” swapped in should pivot easily.
For detail levels:

Start with a “standard” version (mid detail).
For a concise variant, instruct the AI to drop charts and keep just headline numbers and a tagline.
For a detailed variant, ask it to add extra panels like game tree snippets, deeper equations, or solver diagnostics.
4. Maintain visual consistency
Even with AI-generated assets, you can enforce brand cues:

Mention color palette (“use deep navy, emerald green, and off-white”) in your prompts.
Specify typography vibes (“bold sans-serif for headings, clean sans-serif body”).
Include consistent icons (“use chip icon for EV, cards for thresholds”). Repeating these instructions nudges the AI toward a cohesive look.
5. Keep a review checklist
AI can occasionally tweak numbers or misplace a decimal. Before publishing each graphic:

Verify every numeric element against the chapter’s analytics.
Make sure labels match your nomenclature (jam vs shove, call thresholds, etc.).
Export at high resolution (AI tools often let you specify 2x or 4x scale).
6. Build a gallery in the repo
Once the graphics are ready:

Store them under something like assets/infographics/ch12_standard.png.
Link them from each chapter README and the root README so readers can jump straight to the visuals.
Optionally, note how you generated them (e.g., “Created with [tool name], prompt template in docs/prompts/infographic_chapter.txt”) so you can reproduce or tweak later.