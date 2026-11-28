import { createHash } from "node:crypto";
import { execFileSync } from "node:child_process";
import { readFileSync, writeFileSync, realpathSync } from "node:fs";
import { realpath } from "node:fs/promises";
import { pathToFileURL } from "node:url";
import path from "node:path";

const EXPECTED = "941262899a46e54cbf1a94a4da6dd528b8d36780";
const sourceRoot = process.env.PCB_SOURCE_WORKTREE;
if (!sourceRoot) throw new Error("SOURCE_ATTESTATION_FAILED: PCB_SOURCE_WORKTREE is required");
if (process.env.PCB_EXPECTED_SOURCE_SHA && process.env.PCB_EXPECTED_SOURCE_SHA !== EXPECTED)
  throw new Error("SOURCE_ATTESTATION_FAILED: PCB_EXPECTED_SOURCE_SHA mismatch");
const root = await realpath(sourceRoot).catch(() => { throw new Error("SOURCE_ATTESTATION_FAILED: source path is not accessible"); });
const git = (args: string[]) => {
  try { return execFileSync("git", ["-C", root, ...args], { encoding: "utf8" }); }
  catch (error: any) { throw new Error(`SOURCE_ATTESTATION_FAILED: git ${args.join(" ")} failed: ${error.stderr ?? error.message}`); }
};
const observed = git(["rev-parse", "HEAD"]).trim();
if (observed !== EXPECTED) throw new Error(`SOURCE_ATTESTATION_FAILED: expected ${EXPECTED}, observed ${observed}`);
const dirty = git(["status", "--porcelain=v1", "--untracked-files=all"]);
if (dirty !== "") throw new Error(`SOURCE_ATTESTATION_FAILED: dirty source checkout:\n${dirty}`);
const sourceFiles = ["shared/engineering.ts"];
const fileRecords = sourceFiles.map(file => {
  const absolute = path.resolve(root, file);
  if (!absolute.startsWith(root + path.sep)) throw new Error("SOURCE_ATTESTATION_FAILED: source path escapes checkout");
  const canonical = realpathSync(absolute);
  if (canonical !== absolute) throw new Error("SOURCE_ATTESTATION_FAILED: source file is a symlink or changed path");
  git(["ls-files", "--error-unmatch", "--", file]);
  const content = readFileSync(absolute);
  const hash = createHash("sha256").update(content).digest("hex");
  return { file, absolute, sha256: hash, bytes: content.length };
});
const sourceText = readFileSync(fileRecords[0].absolute, "utf8");
const sourceModule: any = await import(pathToFileURL(path.join(root, "shared/engineering.ts")).href);
const lineOf = (needle: string) => {
  const index = sourceText.indexOf(needle);
  return index < 0 ? null : sourceText.slice(0, index).split("\n").length;
};
const expressions = {
  source_sha: observed,
  route45: { line: lineOf("export function route45"), expression: "dx = end.x - start.x; dy = end.y - start.y; Math.abs(dx); Math.abs(dy); Math.min(abs(dx), abs(dy)); start.x + Math.sign(dx) * diagonal" },
  rotatePoint: { line: lineOf("export function rotatePoint"), expression: "radians = degrees * Math.PI / 180; cos = Math.cos(radians); sin = Math.sin(radians); x = point.x * cos - point.y * sin; y = point.x * sin + point.y * cos" },
  transformLocalPoint: { line: lineOf("export function transformLocalPoint"), expression: "rotated = rotatePoint(local, rotation); x = origin.x + rotated.x; y = origin.y + rotated.y" },
  degree_radian_order: "degrees * Math.PI / 180 (left associative: multiplication then division)",
};

function bits(value: number): string {
  const buffer = new ArrayBuffer(8); new DataView(buffer).setFloat64(0, value, false);
  return `0x${new DataView(buffer).getBigUint64(0, false).toString(16).padStart(16, "0")}`;
}
function rec(operation: string, value: number) { return { operation, decimal: String(value), bits: bits(value), finite: Number.isFinite(value), isNaN: Number.isNaN(value) }; }
function add(steps: any[], operation: string, value: number) { steps.push(rec(operation, value)); return value; }
function sourceRotate(point: any, degrees: number) {
  const steps: any[] = [];
  const product = add(steps, "degrees * Math.PI", degrees * Math.PI);
  const radians = add(steps, "(degrees * Math.PI) / 180", product / 180);
  const cos = add(steps, "Math.cos(radians)", Math.cos(radians));
  const sin = add(steps, "Math.sin(radians)", Math.sin(radians));
  const xProduct = add(steps, "point.x * cos", point.x * cos);
  const yProduct = add(steps, "point.y * sin", point.y * sin);
  const x = add(steps, "xProduct - yProduct", xProduct - yProduct);
  const xSin = add(steps, "point.x * sin", point.x * sin);
  const yCos = add(steps, "point.y * cos", point.y * cos);
  const y = add(steps, "xSin + yCos", xSin + yCos);
  return { result: { x, y }, steps };
}
function sourceTransform(origin: any, local: any, rotation: number) {
  const rotated = sourceRotate(local, rotation);
  const steps = [...rotated.steps];
  const x = add(steps, "origin.x + rotated.x", origin.x + rotated.result.x);
  const y = add(steps, "origin.y + rotated.y", origin.y + rotated.result.y);
  return { result: { x, y }, steps };
}
function sourceRoute(start: any, end: any) {
  const steps: any[] = [];
  const dx = add(steps, "end.x - start.x", end.x - start.x);
  const dy = add(steps, "end.y - start.y", end.y - start.y);
  const adx = add(steps, "Math.abs(dx)", Math.abs(dx));
  const ady = add(steps, "Math.abs(dy)", Math.abs(dy));
  const difference = add(steps, "Math.abs(Math.abs(dx) - Math.abs(dy))", Math.abs(adx - ady));
  const diagonal = add(steps, "Math.min(Math.abs(dx), Math.abs(dy))", Math.min(adx, ady));
  const sign = add(steps, "Math.sign(dx)", Math.sign(dx));
  const waypointX = add(steps, "start.x + Math.sign(dx) * diagonal", start.x + sign * diagonal);
  return { steps, route: (adx < 1e-7 || ady < 1e-7 || difference < 1e-7) ? [start, end] : [start, { x: waypointX, y: start.y }, end] };
}

const vectors = [
  ["ordinary-0", {x: 1.25, y: -2.5}, {x: 10, y: -20}, 0],
  ["ordinary-45", {x: 3, y: -4}, {x: 100, y: -200}, 45],
  ["ordinary-90", {x: 3, y: -4}, {x: 100, y: -200}, 90],
  ["ordinary-180", {x: 3, y: -4}, {x: 100, y: -200}, 180],
  ["ordinary-270", {x: 3, y: -4}, {x: 100, y: -200}, 270],
  ["ordinary-360", {x: 3, y: -4}, {x: 100, y: -200}, 360],
  ["negative-angle", {x: 1e3, y: -2e3}, {x: -4e3, y: 5e3}, -45],
  ["adjacent-45", {x: 1, y: 1}, {x: 0, y: 0}, 45 + Number.EPSILON],
  ["adjacent-90", {x: 1, y: -1}, {x: 0, y: 0}, 90 - Number.EPSILON],
  ["adjacent-180", {x: 1, y: 1}, {x: 0, y: 0}, 180 + Number.EPSILON],
  ["adjacent-270", {x: 1, y: 1}, {x: 0, y: 0}, 270 - Number.EPSILON],
  ["adjacent-360", {x: 1, y: 1}, {x: 0, y: 0}, 360 + Number.EPSILON],
  ["large-cancellation", {x: Number.MAX_VALUE, y: Number.MAX_VALUE}, {x: 0, y: 0}, 45],
  ["large-opposite", {x: Number.MAX_VALUE, y: -Number.MAX_VALUE}, {x: -Number.MAX_VALUE, y: Number.MAX_VALUE}, 45],
  ["subnormal", {x: Number.MIN_VALUE, y: -Number.MIN_VALUE}, {x: 0, y: 0}, Number.MIN_VALUE],
  ["signed-zero", {x: -0, y: +0}, {x: -0, y: +0}, -0],
  ["huge-angle", {x: 1, y: 2}, {x: 3, y: 4}, 1e16],
  ["max-angle", {x: 1, y: 2}, {x: 3, y: 4}, Number.MAX_VALUE],
  ["overflow-translation", {x: Number.MAX_VALUE, y: -Number.MAX_VALUE}, {x: Number.MAX_VALUE, y: Number.MAX_VALUE}, 0],
];
const rows = vectors.map(([id, local, origin, degrees]: any) => {
  const rotation = sourceRotate(local, degrees);
  const transformed = sourceTransform(origin, local, degrees);
  const radians = degrees * Math.PI / 180;
  const route = sourceRoute(local, origin);
  const actualRotate = sourceModule.rotatePoint(local, degrees);
  const actualTransform = sourceModule.transformLocalPoint(origin, local, degrees);
  const actualRoute = sourceModule.route45(local, origin);
  if (bits(actualRotate.x) !== bits(rotation.result.x) || bits(actualRotate.y) !== bits(rotation.result.y))
    throw new Error(`SOURCE_SEQUENCE_MISMATCH: rotatePoint ${id}`);
  if (bits(actualTransform.x) !== bits(transformed.result.x) || bits(actualTransform.y) !== bits(transformed.result.y))
    throw new Error(`SOURCE_SEQUENCE_MISMATCH: transformLocalPoint ${id}`);
  if (JSON.stringify(actualRoute) !== JSON.stringify(route.route))
    throw new Error(`SOURCE_SEQUENCE_MISMATCH: route45 ${id}`);
  return {
    id, input: { local: {x: rec("input.local.x", local.x), y: rec("input.local.y", local.y)}, origin: {x: rec("input.origin.x", origin.x), y: rec("input.origin.y", origin.y)}, degrees: rec("input.degrees", degrees), radians: rec("radians", radians) },
    rotate: { source_result: { x: rec("final.rotate.x", rotation.result.x), y: rec("final.rotate.y", rotation.result.y) }, steps: rotation.steps },
    transform: { source_result: { x: rec("final.transform.x", transformed.result.x), y: rec("final.transform.y", transformed.result.y) }, steps: transformed.steps },
    route: { result: route.route, actual_source_result: actualRoute, steps: route.steps },
    source_runtime: { rotate: actualRotate, transform: actualTransform },
    rad_bits: bits(radians), x_bits: bits(local.x), y_bits: bits(local.y), ox_bits: bits(origin.x), oy_bits: bits(origin.y),
  };
});
const after = sourceFiles.map(file => ({ file, sha256: createHash("sha256").update(readFileSync(path.resolve(root, file))).digest("hex") }));
if (JSON.stringify(fileRecords.map(x => x.sha256)) !== JSON.stringify(after.map(x => x.sha256))) throw new Error("SOURCE_ATTESTATION_FAILED: source file changed during capture");
const out = process.env.CAPTURE_OUTPUT ?? "javascript-capture.json";
writeFileSync(out, JSON.stringify({ attestation: { sourceRoot: root, expectedSha: EXPECTED, observedSha: observed, dirtyStatus: dirty, files: fileRecords, filesAfter: after }, expressions, runtime: { node: process.version, v8: process.versions.v8, platform: process.platform, arch: process.arch }, vectors: rows }, null, 2) + "\n");
console.log(JSON.stringify({ vectors: rows.length, source: observed, fileSha256: fileRecords[0].sha256, output: out }, null, 2));
