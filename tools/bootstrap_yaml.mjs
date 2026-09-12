import fs from "node:fs";

const source = JSON.parse(fs.readFileSync("decision_tree.generated.json", "utf8"));
delete source._meta;

function scalar(value, indent) {
  if (value === null) return "null";
  if (typeof value === "boolean" || typeof value === "number") return String(value);
  const text = String(value);
  if (text.includes("\n")) return `|\n${text.trimEnd().split("\n").map(line => " ".repeat(indent + 2) + line).join("\n")}`;
  return JSON.stringify(text);
}

function emit(value, indent = 0) {
  const pad = " ".repeat(indent);
  if (Array.isArray(value)) return value.map(item => {
    if (item && typeof item === "object") {
      const nested = emit(item, indent + 2).split("\n");
      return `${pad}- ${nested[0].trimStart()}\n${nested.slice(1).join("\n")}`;
    }
    return `${pad}- ${scalar(item, indent)}`;
  }).join("\n");
  return Object.entries(value).map(([key, item]) => {
    const yamlKey = /^(?:on|off|yes|no|true|false|null)$/i.test(key) ? JSON.stringify(key) : key;
    if (item && typeof item === "object") return `${pad}${yamlKey}:\n${emit(item, indent + 2)}`;
    return `${pad}${yamlKey}: ${scalar(item, indent)}`;
  }).join("\n");
}

fs.writeFileSync("decision_tree.yaml", emit(source) + "\n", "utf8");
console.log("Wrote decision_tree.yaml from the supplied generated artifact.");
