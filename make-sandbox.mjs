/* Generates sandbox.html from index.html.
 *
 * The sandbox is a throwaway copy to design in: it opens on the empty
 * redesign shell, keeps its own browser storage so it can never overwrite
 * the reference layout, and gains a Reset button.
 *
 *   node make-sandbox.mjs
 */
import { readFileSync, writeFileSync } from "node:fs";

const SRC = "index.html";
const OUT = "sandbox.html";

let s = readFileSync(SRC, "utf8");
const swap = (find, replace, label) => {
  if (!s.includes(find)) throw new Error(`make-sandbox: could not find ${label}`);
  s = s.replaceAll(find, replace);
};

swap("<title>Joinery Bench</title>", "<title>Joinery Bench Sandbox</title>", "title");

swap(
  '<span class="sub">Cabinetry&nbsp;layout</span>',
  '<span class="sub sandbox">Sandbox</span>',
  "brand subtitle"
);

// its own storage, so the sandbox and the reference never share a layout
swap('"joinery-bench-v1"', '"joinery-bench-sandbox-v1"', "layout storage key");
swap('"joinery-bench-seen-help"', '"joinery-bench-sandbox-seen-help"', "help storage key");

// open on the cleared shell rather than the consented layout
swap('presetId:"tara-kitchen",', 'presetId:"tara-redesign",', "initial preset");
swap('}else{\n  loadPreset("tara-kitchen");\n}', '}else{\n  loadPreset("tara-redesign");\n}',
     "boot fallback preset");
swap('}catch(err){ loadPreset("tara-kitchen"); }', '}catch(err){ loadPreset("tara-redesign"); }',
     "restore fallback preset");

swap(
  '<button class="btn" id="saveBtn" title="Save to this browser">Save</button>',
  '<button class="btn" id="saveBtn" title="Save to this browser">Save</button>\n' +
  '    <button class="btn" id="resetBtn" title="Throw this layout away and start again">Reset</button>',
  "save button"
);

swap(
  '$("trashBtn").onclick = deleteSelection;',
  '$("resetBtn").onclick = () => {\n' +
  '  if(S.items.length && !confirm("Throw this layout away and start again?")) return;\n' +
  '  try{ localStorage.removeItem(LS_KEY); }catch(err){}\n' +
  '  loadPreset(S.presetId);\n' +
  '  flash("Sandbox reset");\n' +
  '};\n' +
  '$("trashBtn").onclick = deleteSelection;',
  "trash handler"
);

// a quiet marker so it is obvious which copy you have open
swap(
  ".brand .sub{font-size:10.5px;color:var(--graphite-2);letter-spacing:.08em;text-transform:uppercase}",
  ".brand .sub{font-size:10.5px;color:var(--graphite-2);letter-spacing:.08em;text-transform:uppercase}\n" +
  ".brand .sub.sandbox{color:var(--stamp);border:1px solid color-mix(in srgb,var(--stamp) 40%,transparent);" +
  "border-radius:3px;padding:1px 5px;font-weight:600}",
  "brand styles"
);

writeFileSync(OUT, s);
console.log(`wrote ${OUT} (${(s.length / 1024).toFixed(0)} KB)`);
