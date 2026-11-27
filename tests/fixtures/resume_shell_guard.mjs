// Test-only V2 execution control. Copied into a disposable runtime directory;
// never installed by install-global or discovered from the operator's HOME.
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

export function authorize(policy, location, command, cwd) {
  if (typeof command !== "string" ||
      (cwd !== undefined && typeof cwd !== "string")) {
    throw new Error("fixture shell: invalid raw invocation");
  }
  const directory = path.resolve(location, cwd ?? location);
  // An exact cwd AND an exact raw command are required. No scanning, prefix
  // matching, shell token normalization, expansions or declaration exceptions.
  if (!Object.hasOwn(policy.commands, directory) ||
      fs.realpathSync(directory) !== directory ||
      !policy.commands[directory].includes(command)) {
    throw new Error("fixture shell: raw command/cwd denied");
  }
  return directory;
}

export default {
  id: "issue61.disposable-shell-guard",
  async setup(ctx) {
    const policy = JSON.parse(fs.readFileSync(
      new URL("./policy.json", import.meta.url), "utf8"));
    const audit = (event) => fs.appendFileSync(policy.audit, JSON.stringify(event) + "\n");
    const check = (boundary, command, cwd) => {
      try {
        const directory = authorize(policy, ctx.location.directory, command, cwd);
        audit({boundary, decision: "allow", command, cwd: directory});
        return directory;
      } catch (error) {
        audit({boundary, decision: "deny", command, cwd: cwd ?? ctx.location.directory});
        throw error;
      }
    };
    const tool = await ctx.tool.hook("execute.before", (event) => {
      if (event.tool !== "shell") return;
      check("tool.execute.before", event.input?.command, event.input?.workdir);
    });
    const shell = await ctx.shell.hook("create.before", (event) => {
      event.cwd = check("shell.create.before", event.command, event.cwd);
      // Do not inherit session overrides, BASH_ENV/ENV, GIT_*, exported
      // functions, loader variables or an alternate shell. Only fixture-owned
      // constants enter the child; native ShellTool adds its agent/session IDs.
      event.shell = "/bin/sh";
      event.env = {...policy.env};
      event.timeout = Math.min(event.timeout || 30_000, 30_000);
    });
    audit({boundary: "setup", decision: "active", source: fileURLToPath(import.meta.url)});
    return async () => {
      await tool.dispose();
      await shell.dispose();
      audit({boundary: "cleanup", decision: "disposed"});
    };
  },
};
