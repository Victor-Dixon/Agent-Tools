import fs from "fs";
import path from "path";

type ChatPresenceConfig = {
  oauth_token?: string;
  nickname?: string;
  channel?: string;
};

const CONFIG_PATH = path.resolve(__dirname, "..", "config", "chat_presence.json");

function loadConfig(): ChatPresenceConfig {
  if (!fs.existsSync(CONFIG_PATH)) {
    throw new Error(`config not found at ${CONFIG_PATH}`);
  }
  const raw = fs.readFileSync(CONFIG_PATH, "utf-8");
  return JSON.parse(raw) as ChatPresenceConfig;
}

function validateToken(token: string | undefined): string[] {
  const issues: string[] = [];
  if (!token) {
    issues.push("oauth_token missing");
    return issues;
  }
  if (/\s/.test(token.trim())) {
    issues.push("oauth_token contains whitespace; should be plain token");
  }
  if (!token.startsWith("oauth:")) {
    issues.push("oauth_token must start with 'oauth:'");
  }
  if (token.includes("pip ") || token.includes("cd ") || token.includes("findstr")) {
    issues.push("oauth_token looks like a shell command; replace with real token");
  }
  if (token.length < 20) {
    issues.push("oauth_token too short; expected full length token from Twitch");
  }
  return issues;
}

function main() {
  try {
    const config = loadConfig();
    const issues = validateToken(config.oauth_token);
    if (issues.length === 0) {
      console.log("✅ oauth_token looks valid for Twitch bot usage.");
      process.exit(0);
    }
    console.error("❌ oauth_token validation failed:");
    issues.forEach((msg) => console.error(`- ${msg}`));
    process.exit(1);
  } catch (err) {
    console.error(`❌ Failed to validate oauth_token: ${(err as Error).message}`);
    process.exit(2);
  }
}

main();

