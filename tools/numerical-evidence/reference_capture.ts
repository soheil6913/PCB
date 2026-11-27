import { existsSync } from "node:fs";
import { resolve } from "node:path";
import { pathToFileURL } from "node:url";

async function main() {
  const sourceWorktree = process.env.PCB_SOURCE_WORKTREE;
  if (!sourceWorktree) throw new Error("PCB_SOURCE_WORKTREE is required; no source checkout fallback is allowed");
  const sourcePath = resolve(sourceWorktree, "shared/engineering.ts");
  if (!existsSync(sourcePath)) throw new Error(`reference source file is missing: ${sourcePath}`);
  const referenceCommit = process.env.PCB_REFERENCE_COMMIT;
  if (!referenceCommit) throw new Error("PCB_REFERENCE_COMMIT is required");
  const { rotatePoint, transformLocalPoint, route45 } = await import(pathToFileURL(sourcePath).href);

  const input = JSON.parse(process.argv[2]);
  const buf = new ArrayBuffer(8);
  const view = new DataView(buf);
  const bits = (value: number) => {
    view.setFloat64(0, value, false);
    return `0x${view.getBigUint64(0, false).toString(16).padStart(16, "0")}`;
  };
  const point = (p: { x: number; y: number }) => ({
    xBits: bits(p.x), yBits: bits(p.y),
    xNegZero: Object.is(p.x, -0), yNegZero: Object.is(p.y, -0),
    xFinite: Number.isFinite(p.x), yFinite: Number.isFinite(p.y),
  });
  const p = { x: Number(input.x), y: Number(input.y) };
  const origin = { x: Number(input.originX), y: Number(input.originY) };
  const local = { x: Number(input.localX), y: Number(input.localY) };
  const degrees = Number(input.degrees);
  const rotated = rotatePoint(p, degrees);
  const transformed = transformLocalPoint(origin, local, degrees);
  const radians = degrees * Math.PI / 180;
  const routed = route45(p, { x: Number(input.endX), y: Number(input.endY) });
  console.log(JSON.stringify({
    referenceSource: sourcePath,
    referenceCommit,
    input: { point: point(p), origin: point(origin), local: point(local), degreesBits: bits(degrees) },
    radiansBits: bits(radians),
    rotate: point(rotated), transform: point(transformed),
    route: routed.map(point),
  }));
}

main().catch((error) => { console.error(error); process.exitCode = 1; });
