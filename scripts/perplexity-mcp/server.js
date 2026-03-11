#!/usr/bin/env node
/**
 * Perplexity MCP Server for GovCon Content Fact-Checking
 *
 * Provides two tools:
 *   1. fact_check  — Verify a specific claim against current sources
 *   2. research    — Deep-research a topic for content accuracy
 *
 * Env: PERPLEXITY_API_KEY (required)
 */

import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";

const API_KEY = process.env.PERPLEXITY_API_KEY;
if (!API_KEY) {
  console.error("PERPLEXITY_API_KEY environment variable is required");
  process.exit(1);
}

const PERPLEXITY_URL = "https://api.perplexity.ai/chat/completions";

async function queryPerplexity(systemPrompt, userQuery, model = "sonar") {
  const res = await fetch(PERPLEXITY_URL, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${API_KEY}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      model,
      messages: [
        { role: "system", content: systemPrompt },
        { role: "user", content: userQuery },
      ],
    }),
  });

  if (!res.ok) {
    const body = await res.text();
    throw new Error(`Perplexity API ${res.status}: ${body}`);
  }

  const data = await res.json();
  const answer = data.choices?.[0]?.message?.content ?? "(no response)";
  const citations = data.citations ?? [];

  let result = answer;
  if (citations.length > 0) {
    result += "\n\n---\nSources:\n" + citations.map((c, i) => `[${i + 1}] ${c}`).join("\n");
  }
  return result;
}

// Create server
const server = new McpServer({
  name: "perplexity-govcon",
  version: "1.0.0",
});

// Tool 1: Fact-check a specific claim
server.tool(
  "fact_check",
  "Verify a specific government contracting claim or statement against current official sources. Returns verdict (accurate/inaccurate/partially accurate/outdated) with citations.",
  {
    claim: z.string().describe("The specific claim or statement to verify"),
    context: z
      .string()
      .optional()
      .describe("Optional context about where this claim appears (e.g. course name, slide title)"),
  },
  async ({ claim, context }) => {
    const systemPrompt = `You are a federal government contracting fact-checker. Your job is to verify claims about government contracting processes, regulations, websites, and programs.

For each claim, respond with:
1. VERDICT: [ACCURATE / INACCURATE / PARTIALLY ACCURATE / OUTDATED / UNVERIFIABLE]
2. EXPLANATION: Brief explanation of why
3. CURRENT STATUS: What the current correct information is (as of today)
4. KEY CHANGES: If something changed recently (e.g., FPDS merged into SAM.gov), note when and what changed

Focus on:
- Federal contracting websites and systems (SAM.gov, PIEE, WAWF, etc.)
- SBA programs and certifications (8(a), HUBZone, WOSB, SDVOSB)
- FAR/DFARS regulations
- Procurement processes and thresholds
- Government contracting terminology

Always cite official .gov sources when possible.`;

    const query = context
      ? `Context: ${context}\n\nClaim to verify: "${claim}"`
      : `Claim to verify: "${claim}"`;

    const result = await queryPerplexity(systemPrompt, query);
    return { content: [{ type: "text", text: result }] };
  }
);

// Tool 2: Research a topic for content accuracy
server.tool(
  "research",
  "Deep-research a government contracting topic to ensure course content is current and accurate. Returns comprehensive findings with citations.",
  {
    topic: z.string().describe("The topic to research (e.g. 'SAM.gov registration process 2026', '8(a) sole-source thresholds')"),
    specific_questions: z
      .string()
      .optional()
      .describe("Specific questions to answer about this topic"),
  },
  async ({ topic, specific_questions }) => {
    const systemPrompt = `You are a federal government contracting research assistant. Provide thorough, accurate, and current information about government contracting topics.

Structure your response as:
1. CURRENT STATUS: What is the current state of this topic
2. KEY FACTS: Bullet points of verified facts with dates
3. RECENT CHANGES: Any changes in the last 2 years
4. COMMON MISCONCEPTIONS: Things people often get wrong
5. OFFICIAL SOURCES: Links to .gov pages for verification

Focus on accuracy and recency. Flag anything that has changed recently.`;

    const query = specific_questions
      ? `Topic: ${topic}\n\nSpecific questions:\n${specific_questions}`
      : `Topic: ${topic}`;

    const result = await queryPerplexity(systemPrompt, query, "sonar-pro");
    return { content: [{ type: "text", text: result }] };
  }
);

// Start server
const transport = new StdioServerTransport();
await server.connect(transport);
