import { describe, expect, it } from "vitest";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";

describe("vite renderer configuration", () => {
  it("uses relative asset paths so Electron can load the built renderer from file URLs", () => {
    const configSource = readFileSync(resolve(__dirname, "../../vite.config.ts"), "utf8");

    expect(configSource).toContain('base: "./"');
  });
});
