import fs from 'node:fs';
const bits = (x) => { const b = new ArrayBuffer(8); const f = new Float64Array(b); const u = new BigUint64Array(b); f[0]=x; return '0x'+u[0].toString(16).padStart(16,'0'); };
const value = (x) => ({decimal:String(x), bits:bits(x), finite:Number.isFinite(x), nan:Number.isNaN(x), posInf:x===Infinity, negInf:x===-Infinity, negZero:Object.is(x,-0)});
const signed = {
  input_pos_zero:value(0), input_neg_zero:value(-0), sin_neg_zero:value(Math.sin(-0)), cos_neg_zero:value(Math.cos(-0)),
  add_neg_zero_pos_zero:value(-0+0), sub_pos_zero_pos_zero:value(0-0), mul_pos_zero_neg_one:value(0*-1), mul_neg_zero_neg_one:value(-0*-1),
  div_one_neg_inf:value(1/-Infinity), atan2_neg_zero_one:value(Math.atan2(-0,1)), sign_neg_zero:Math.sign(-0)
};
const vals=[0,-0,Number.MIN_VALUE,-Number.MIN_VALUE,Number.MAX_VALUE,-Number.MAX_VALUE,Infinity,-Infinity,NaN,1e308,-1e308];
const angles=[0,-0,45,90,180,360,1e20,Number.MAX_VALUE,Infinity,-Infinity,NaN];
const extremes=[];
for (const n of vals) for (const d of angles) {
  const r=d*Math.PI/180, c=Math.cos(r), s=Math.sin(r);
  const x=n*c-n*s, y=n*s+n*c;
  extremes.push({n:value(n),degrees:value(d),radians:value(r),cos:value(c),sin:value(s),x:value(x),y:value(y)});
}
const summary={
  signed_zero_observations:Object.keys(signed).length,
  extreme_vectors:extremes.length,
  nonfinite_inputs:extremes.filter(v=>!v.n.finite||!v.degrees.finite).length,
  output_nan:extremes.filter(v=>v.x.nan||v.y.nan).length,
  output_infinite:extremes.filter(v=>v.x.posInf||v.x.negInf||v.y.posInf||v.y.negInf).length,
  negative_zero_outputs:extremes.filter(v=>v.x.negZero||v.y.negZero).length
};
fs.writeFileSync(process.argv[2],JSON.stringify({runtime:{node:process.version,v8:process.versions.v8,platform:process.platform,arch:process.arch},summary,signed_zero:signed,extreme_vectors:extremes},null,2)+'\n');
console.log(JSON.stringify(summary));
