import { rotatePoint, transformLocalPoint, route45 } from "/home/ubuntu/PCB-Studio-Pro-p2-4-d-1/shared/engineering.ts";

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
const rotated = rotatePoint(p, Number(input.degrees));
const transformed = transformLocalPoint(origin, local, Number(input.degrees));
const radians = Number(input.degrees) * Math.PI / 180;
const routed = route45(p, { x: Number(input.endX), y: Number(input.endY) });
console.log(JSON.stringify({
  input: { point: point(p), origin: point(origin), local: point(local), degreesBits: bits(Number(input.degrees)) },
  radiansBits: bits(radians),
  rotate: point(rotated), transform: point(transformed),
  route: routed.map(point),
}));
