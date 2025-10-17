/**
 * Agent-side helpers to call the `exa` CLI from Node/TypeScript.
 *
 * Ensure `EXA_API_KEY` is set in the environment and the `exa` command is
 * available on PATH (installed via `pip install -e .`).
 *
 * Run with ts-node:
 *   EXA_API_KEY=sk-... npx ts-node examples/agents_node.ts
 */

import { execFile } from "node:child_process";
import { promisify } from "node:util";

const pexecFile = promisify(execFile);

async function runExa(args: string[]) {
  const { stdout } = await pexecFile("exa", args, {
    env: { ...process.env, EXA_API_KEY: process.env.EXA_API_KEY ?? "" },
    maxBuffer: 10 * 1024 * 1024,
  });
  return JSON.parse(stdout) as Record<string, unknown>;
}

export async function exaSearch(query: string, type = "fast") {
  return runExa(["search", "--query", query, "--type", type]);
}

export async function exaResearch(
  instructionsPath: string,
  schemaPath: string,
  model = "exa-research"
) {
  const start = await runExa([
    "research",
    "start",
    "--instructions",
    `@${instructionsPath}`,
    "--schema",
    `@${schemaPath}`,
    "--model",
    model,
  ]);
  const id = (start as any).id ?? (start as any).taskId;
  if (!id) {
    throw new Error(`No task id in ${JSON.stringify(start)}`);
  }
  return runExa(["research", "poll", "--id", id, "--model", model, "--timeout", "900"]);
}

async function main() {
  if (!process.env.EXA_API_KEY) {
    console.error("EXA_API_KEY not set. Export it before running.");
    process.exit(1);
  }
  const res = await exaSearch("hybrid search vector databases");
  // eslint-disable-next-line no-console
  console.log(JSON.stringify(res, null, 2));
}

if (require.main === module) {
  // eslint-disable-next-line unicorn/prefer-top-level-await
  main().catch((err) => {
    console.error(err);
    process.exit(1);
  });
}

