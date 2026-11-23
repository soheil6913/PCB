# PCB Studio Pro — Phase 6.1 P2.2
## Circle Pad Contract Investigation — Source-Grounded, Design-Only Audit

**تاریخ ممیزی:** 2026-11-23  
**نوع کار:** Design-only investigation  
**وضعیت:** بدون تغییر کد، تست، تنظیمات، workflow، branch، commit، PR، merge، release یا tag

## 1. Executive conclusion

نتیجه‌ی مستقل این ممیزی **C با مؤلفه‌ی مشخصی از D** است:

> قرارداد Circle Pad در repository به‌طور صریح تعریف نشده و میان schema و geometry یک ناسازگاری واقعی وجود دارد. بنابراین در وضعیت فعلی نمی‌توان با شواهد کافی نتیجه گرفت که `width === height` الزام محصول است یا unequal dimensions عمداً معتبرند.

شواهد قطعی فعلی:

- مدل ذخیره‌سازی Pad دو فیلد مستقل `width` و `height` دارد و `shape` می‌تواند `circle` باشد.
- validator برای Circle فقط مثبت و finite بودن هر دو مقدار را بررسی می‌کند و equality را enforce نمی‌کند.
- geometry در چند مسیر، Circle را با شعاع `width / 2` مدل می‌کند و `height` را برای Circle نادیده می‌گیرد.
- همه‌ی fixtureهای Circle که پیدا شدند از ابعاد برابر استفاده می‌کنند؛ اما هیچ تستی این برابری را به‌عنوان invariant صریح assert نمی‌کند.
- UI فعلی Pad geometry، shape selector یا width/height editor ندارد؛ بنابراین از UI نمی‌توان قصد محصول درباره‌ی unequal Circle را استخراج کرد.
- مسیر 3D فعلی placeholder است و مسیر manufacturing/KiCad/Gerber پیاده‌سازی نشده است.

در نتیجه، **برابری ابعاد نباید بدون تصمیم صریح محصول/قرارداد schema enforce شود**. همچنین حفظ unequal dimensions بدون تصمیم نیز نباید به‌عنوان پشتیبانی عمدی از ellipse-like Circle ادعا شود. توصیه‌ی این ممیزی: ابتدا قرارداد را تعیین کنید، سپس یک اصلاح کوچک و هماهنگ در schema، geometry، fixtures و مستندات انجام دهید.

## 2. Verified repository and baseline SHAs

Baseline قبل از شروع بررسی مستقل با local و remote تطبیق داده شد:

| Reference | Verified SHA |
|---|---|
| Repository | `soheil6913/-PCB-Studio-Pro` |
| `main` | `a98384bbfc3296947b90f5254a03a77b11fdc8a9` |
| P1 branch `fix/phase6-1-p1-explicit-v2-dispatch-20261122` | `f2db0afbdcdea6909e7ee91a8f340862741c6db0` |
| Audit branch `audit/phase6-1-p2-independent-20261123` | `e6b2a9153beec74c6d2013c6eda5362e850806b0` |
| P2.1 commit | `e6b2a9153beec74c6d2013c6eda5362e850806b0` |
| Existing temporary CI branch `verification/phase6-1-p2-1-ci-20261123` | `e6b2a9153beec74c6d2013c6eda5362e850806b0` |

Local branch هنگام بررسی `audit/phase6-1-p2-independent-20261123` بود، روی همان P2.1 SHA قرار داشت و worktree clean بود. این audit هیچ branch جدیدی ایجاد نکرد.

## 3. Circle Pad data-model definition

### 3.1 Type definition

در `shared/engineering.ts:5` نوع Pad به این شکل تعریف شده است:

```ts
export type Pad = {
  id: string;
  number: string;
  position: Point;
  width: number;
  height: number;
  shape?: "circle" | "rect" | "oval";
  layer: Layer;
  layers?: Layer[];
  drill?: number;
  plated?: boolean;
  rotation?: number;
};
```

این مدل:

- یک diameter واحد برای Circle ندارد؛
- دو مقدار مستقل `width` و `height` ذخیره می‌کند؛
- `shape` فقط یک discriminant متنی است؛
- invariant وابسته به shape در type system بیان نشده است؛
- برای `circle` در type-level مشخص نمی‌کند که `width` و `height` باید برابر باشند.

از خود type نمی‌توان نتیجه گرفت که unequal values عمدی یا غیرمجاز هستند.

### 3.2 Runtime/schema validation

در `shared/engineering.ts:415`، `validatePad` موارد زیر را بررسی می‌کند:

- `width` مثبت و finite؛
- `height` مثبت و finite؛
- shape یکی از `circle`, `rect`, `oval`؛
- position، layer، layers، rotation، drill و plated با نوع و دامنه‌ی مجاز.

اما در همین symbol هیچ شرطی مانند زیر وجود ندارد:

```ts
if (pad.shape === "circle" && pad.width !== pad.height) ...
```

بنابراین، از نظر validator فعلی، نمونه‌ای مانند `shape: "circle", width: 10, height: 4` از منظر shape dimensions رد نمی‌شود؛ تا زمانی که هر دو مقدار مثبت و finite باشند.

### 3.3 Serialization, deserialization, and migration

مسیرهای واقعی در `client/src/pages/Home.tsx` عبارت‌اند از:

- `Home.tsx:89`: بارگذاری `localStorage` با `JSON.parse` و پذیرش فقط در صورت `validateProjectJson(saved)`؛
- `Home.tsx:91`: autosave با `JSON.stringify(project)`؛
- `Home.tsx:94`: export JSON با `JSON.stringify({...project, schemaVersion: 2})`؛
- `Home.tsx:96`: import با `JSON.parse` سپس `migrateProjectJson(parsed)`؛
- `Home.tsx:97`: save با `JSON.stringify(next)`.

`shared/engineering.ts:435` در `migrateProjectJson` فیلدهای موجود را با own-property check حفظ می‌کند و فقط فیلدهای غایب legacy را default می‌کند. Migration برای Circle ابعاد را normalize نمی‌کند و equality جدیدی نیز اعمال نمی‌کند.

نکته‌ی مهم: مدل `Project` در `Home.tsx:21` برای `components` فقط component-level fields را تعریف می‌کند و `footprintGeometry`/Pad را در مدل TypeScript UI شامل نمی‌کند؛ درحالی‌که schema مشترک در `engineering.ts` آن nested data را می‌شناسد. بنابراین import/export فعلی از نظر runtime می‌تواند داده‌ی اضافی را در object نگه دارد، اما UI editor برای آن contract مستقلی ندارد.

هیچ version-specific handling جداگانه‌ای برای Circle Pad پیدا نشد. schemaVersion در migration و DRC dispatch وجود دارد، اما shape-specific Circle rule ندارد.

## 4. End-to-end lifecycle trace

### 4.1 Creation and editing

Library و creation UI در `Home.tsx:25-30` فقط component kindهایی مانند resistor، capacitor، LED، MCU، sensor، connector، diode و MOSFET را ارائه می‌کند. Pad یا footprint editor در این فهرست وجود ندارد.

- `Home.tsx:64`: Place در schematic یک `Component` می‌سازد، نه Pad.
- `Home.tsx:75`: Place در PCB نیز یک Component با footprint string می‌سازد، نه `footprintGeometry.pads`.
- `Home.tsx:98`: افزودن از library فقط component-level data تولید می‌کند.
- `Home.tsx:99`: property editor فقط `ref`, `value`, `footprint`, `x`, `y`, `rotation` و `layer` را تغییر می‌دهد.

هیچ width/height control، shape selector، pad resize operation یا synchronization خودکار `width = height` در UI پیدا نشد. بنابراین کاربر از مسیر UI فعلی نمی‌تواند عمداً unequal Circle Pad وارد کند؛ اما این نیز ثابت نمی‌کند که فایل‌های import‌شده یا داده‌های external نباید چنین مقادیری داشته باشند.

### 4.2 Persistence/import/export

`Home.tsx:89-97` persistence عمومی پروژه را انجام می‌دهد، نه persistence مخصوص Pad. JSON export object فعلی را serialize می‌کند و import آن را به migration و validation می‌سپارد. چون migration ابعاد Circle را تغییر نمی‌دهد، اگر nested pad در payload موجود باشد، policy فعلی حفظ مقدار و سپس validation عمومی است.

هیچ round-trip test اختصاصی برای Circle با ابعاد unequal پیدا نشد. بنابراین preservation فعلی برای چنین payloadی از مسیر تست‌شده اثبات نشده است، هرچند کد migration از normalization shape-specific استفاده نمی‌کند.

### 4.3 Rendering and selection

- Schematic rendering در `Home.tsx:66-70` component symbols را render می‌کند و Pad geometry را رسم نمی‌کند.
- PCB rendering در `Home.tsx:76` board، track، via و component shell را render می‌کند؛ `footprintGeometry.pads` و shape/width/height Pad در JSX استفاده نمی‌شود.
- selection و dragging در `Home.tsx:64-69`/`73-76` component-level است، نه Pad-level.
- 3D در `Home.tsx:79` یک placeholder board و `model-chip` برای componentهاست و Pad geometry را مصرف نمی‌کند.

پس هیچ rendering path مستقلی وجود ندارد که unequal Circle dimensions را به‌صورت بصری به Circle یا ellipse تبدیل کند.

## 5. Geometry findings

### 5.1 Component/pad transform

در `shared/engineering.ts:101` تابع `localPads` موقعیت Pad را با rotation قطعه به world تبدیل می‌کند و rotation مؤثر را از مجموع rotation قطعه و Pad می‌سازد. این مسیر برای shapeهای مختلف مشترک است.

### 5.2 Circle support geometry

در `shared/engineering.ts:117`، `supportPad` برای shape غیر-rect از ellipse-like support استفاده می‌کند. برای Circle:

```ts
const rx = pad.width / 2;
const ry = shape === "circle" ? pad.width / 2 : pad.height / 2;
```

در `shared/engineering.ts:262`، `pointToEllipseBoundaryDistance` نیز برای Circle مقدار `ry` را از `pad.width` می‌سازد، نه `pad.height`:

```ts
const rx = pad.width / 2;
const ry = (pad.shape === "circle" ? pad.width : pad.height) / 2;
```

در `shared/engineering.ts:263`، `viaToPadDistance` برای Circle از همین ellipse boundary path استفاده می‌کند.

در `shared/engineering.ts:266`، `segmentToPadDistance` برای Circle مستقیماً فاصله‌ی center-to-segment منهای `pad.width / 2` را حساب می‌کند.

در `shared/engineering.ts:258`:

- Circle–Circle از center distance منهای `a.width/2` و `b.width/2` استفاده می‌کند؛
- Circle–Rect و Circle–Oval Circle را با `width` به‌عنوان diameter به مسیر via-to-pad می‌فرستند؛
- مسیرهای دیگر ممکن است `width` و `height` را در GJK upper bound استفاده کنند، اما support shape برای Circle همچنان width-based است.

### 5.3 Interpretation

این رفتار با یک Circle واقعی که یک diameter دارد سازگار است، اما با یک قرارداد «دو مقدار مستقل برای Circle» سازگار نیست. اگر `width = 10` و `height = 4` باشد، geometry عملاً شکل دایره‌ای با diameter 10 را محاسبه می‌کند و height=4 را نادیده می‌گیرد.

این observation به‌تنهایی ثابت نمی‌کند که unequal Circle باید رد شود؛ اما ثابت می‌کند schema فعلی اجازه‌ی داده‌ای را می‌دهد که همه‌ی geometry consumers آن را یکسان تفسیر نمی‌کنند.

## 6. DRC and manufacturing/export findings

### 6.1 DRC

`runDesignRules` در `shared/engineering.ts:388-409` ابتدا project validation را انجام می‌دهد، سپس evaluator نسخه‌ی V2 را اجرا می‌کند و findings schematic و PCB را ترکیب می‌کند. Circle dimensions در DRC از geometry paths ذکرشده در بخش 5 استفاده می‌شوند.

Finding IDs و ordering در این ممیزی تغییر نکرده‌اند و هیچ پیشنهاد اجرایی برای تغییر آن‌ها اعمال نشده است.

### 6.2 Manufacturing/export

در `Home.tsx:107` کنترل KiCad/Gerber با وضعیت `Not enabled yet` نمایش داده می‌شود. در کل repository مسیر اجرایی Gerber، KiCad یا manufacturing export برای Pad geometry پیدا نشد.

- BOM export در `Home.tsx:95` فقط اطلاعات component-level را تولید می‌کند.
- 3D view در `Home.tsx:79` placeholder است.
- هیچ ادعای manufacturing، IPC compliance یا external footprint-library correctness از این بررسی قابل استخراج نیست.

## 7. Existing tests, fixtures, and missing coverage

### 7.1 Existing equal-dimension evidence

تمام Circle fixtureهای پیدا‌شده از dimensions برابر استفاده می‌کنند، از جمله:

- `shared/engineering.test.ts:162,173,178,211,233`؛
- `shared/phase4.gjk.test.ts:26-30,39-41`؛
- `shared/phase5_4.drc-boundary-semantics.test.ts:1217,1298,1303,1443,1566,1740-1771`؛
- `shared/phase5_3.independent-oracles.test.ts:589,615`؛
- `shared/phase5_5.drc-policy-certification.test.ts` helperهای Circle.

این‌ها نشان می‌دهند convention تست‌شده برای Circle، `width === height` است؛ اما هیچ fixture یا assertion صریحی وجود ندارد که بگوید unequal dimensions باید invalid باشند.

### 7.2 Missing coverage

موارد زیر پیدا نشدند:

- تست مستقیم `validateProjectJsonDetailed` برای Circle با `width !== height`؛
- تست مستقیم `migrateProjectJson` برای unequal Circle؛
- تست serialization round-trip با unequal Circle؛
- تست اینکه geometry باید از `height` Circle استفاده کند یا آن را رد کند؛
- تست UI برای Pad editor یا shape selector؛
- تست import/export واقعی برای nested footprint pads؛
- تستی که Circle را به‌عنوان یک diameter field واحد در schema تثبیت کند.

موارد malformed مانند null، zero، negative، NaN و Infinity برای Pad dimensions در validator عمومی از مسیر positive/finite checks پوشش داده می‌شوند، اما shape-specific unequal semantics پوشش داده نشده است.

## 8. Repository documentation and external standards

جستجوی documentation و source برای IPC، KiCad footprint specification، Gerber یا clause استاندارد مرتبط با Circle Pad contract، سندی پیدا نکرد که این repository آن را به‌عنوان invariant اجرایی خود adopt کرده باشد.

اسناد موجود بیشتر limitations و geometry/DRC verification را گزارش می‌کنند. آن‌ها Circle fixtureهای equal یا geometry behavior را نشان می‌دهند، اما clause قراردادی برای equality ارائه نمی‌کنند.

بنابراین generic industry convention یا معنای رایج واژه‌ی Circle به‌تنهایی به‌عنوان contract این application استفاده نشده است.

## 9. A/B/C/D decision matrix

| گزینه | شواهد پشتیبان | شواهد مخالف/کمبود | پیامد | اعتماد |
|---|---|---|---|---|
| **A. Circle الزاماً `width === height` است** | نام shape `circle`؛ همه‌ی fixtureهای موجود equal هستند؛ geometry برای Circle فقط width را به diameter تبدیل می‌کند؛ `supportPad` و distance paths رفتار دایره‌ای دارند | schema equality را enforce نمی‌کند؛ UI contract یا document صریح وجود ندارد؛ unequal input هیچ test policy مشخصی ندارد | enforce کردن equality می‌تواند فایل‌های موجود یا external را بدون migration policy رد کند؛ اما semantic ambiguity و ignored data را رفع می‌کند | متوسط، اما برای تغییر breaking کافی نیست |
| **B. Circle از width و height مستقل پشتیبانی می‌کند** | type دو فیلد دارد؛ validator هر دو را مستقل positive/finite می‌سنجد؛ migration normalization نمی‌کند | geometry برای Circle height را نادیده می‌گیرد؛ UI editor ندارد؛ هیچ unequal fixture یا assertion عمدی وجود ندارد | حفظ unequal values بدون اصلاح geometry به داده‌ای منجر می‌شود که ظاهراً معتبر است اما با width-based circle تفسیر می‌شود | پایین |
| **C. مدل فعلی مبهم/ناکامل است** | type دو بعدی است؛ validator equality ندارد؛ geometry width-only است؛ UI و docs contract را تعریف نمی‌کنند؛ tests فقط convention را نشان می‌دهند | بخش‌هایی از geometry عملاً دایره‌ی واقعی را فرض کرده‌اند | قبل از تغییر باید تصمیم محصول/schema گرفته شود؛ کمترین ریسک و بیشترین انطباق با شواهد فعلی | **بالا** |
| **D. subsystemها semantics متعارض دارند** | validator unequal Circle را قبول می‌کند، درحالی‌که geometry آن را به Circle با width-based diameter تفسیر می‌کند؛ بنابراین accepted data و evaluated geometry یکسان نیستند | این تعارض ممکن است ناشی از invariant ضمنیِ enforce‌نشده باشد، نه الزاماً پشتیبانی عمدی از ellipse | می‌تواند DRC و persisted data را از نظر معنایی divergent کند؛ نیازمند قرارداد و regression test است | **بالا برای وجود ناسازگاری فنی؛ متوسط برای severity محصول** |

### Final decision

تصمیم عملی این ممیزی: **C primary / D secondary**. یعنی قرارداد محصول هنوز روشن نشده و implementation فعلی در boundary validator-versus-geometry ناسازگاری دارد.

## 10. Risks of enforcing equal dimensions

اگر بدون تصمیم رسمی equality enforce شود:

1. فایل‌های import‌شده یا legacy که unequal values دارند fail closed می‌شوند، بدون اینکه ثابت شده باشد چنین داده‌ای همیشه corrupted است.
2. compatibility با external footprint sources ممکن است شکسته شود.
3. users ممکن است داده‌ای را که پیش‌تر validator می‌پذیرفت از دست‌رفته یا غیرقابل‌واردکردن ببینند.
4. migration باید policy روشن داشته باشد: reject یا normalize؛ normalization می‌تواند داده‌ی اصلی را بی‌صدا تغییر دهد.
5. تست‌ها و گزارش‌های موجود باید از «convention equal» به «invariant equality» ارتقا پیدا کنند.

## 11. Risks of preserving independent dimensions

اگر unequal values پذیرفته بمانند اما geometry فعلی تغییر نکند:

1. مقدار `height` در Circle semantics عملاً ignored می‌شود.
2. یک payload معتبر از دید schema می‌تواند با انتظار نویسنده‌ی فایل متفاوت محاسبه شود.
3. DRC clearance برای Circle ممکن است بر اساس diameter width محاسبه شود، نه bounding dimensions ذخیره‌شده.
4. round-trip ظاهری داده ممکن است حفظ شود اما meaning آن حفظ نشود.
5. external footprint import در آینده ممکن است ellipse را به‌عنوان Circle وارد کند و geometry آن را به‌صورت دایره تفسیر کند.
6. تیم نمی‌تواند ادعا کند Circle از independent width/height پشتیبانی می‌کند، چون هیچ editor، renderer یا manufacturing path چنین semanticsی را اجرا نمی‌کند.

## 12. Recommended contract and rationale

### Immediate recommendation

تا زمان تصمیم رسمی، contract را **ambiguous/unsupported for unequal Circle dimensions** اعلام کنید:

- unequal Circle را intentional supported feature معرفی نکنید؛
- equality validation را در این phase اضافه نکنید؛
- ابعاد Circle را silently normalize نکنید؛
- این مورد را به‌عنوان schema/product decision مستقل نگه دارید.

### Preferred future contract

با توجه به geometry موجود، گزینه‌ی کم‌ریسک‌تر برای تصمیم آینده این است:

> `shape: "circle"` یک geometry دایره‌ای با یک diameter مفهومی دارد و در representation فعلی باید `width === height` باشد.

اما این توصیه فقط زمانی قابل پیاده‌سازی است که product owner آن را تأیید کند و migration compatibility policy مشخص شود. اگر محصول واقعاً independent X/Y dimensions می‌خواهد، آن shape از نظر semantics باید به‌صورت ellipse یا shape مستقل تعریف و تمام geometry/rendering/schema/tests آن هماهنگ شوند؛ تغییر نام یا reinterpretation نباید بی‌صدا انجام شود.

## 13. Exact follow-up implementation scope, if approved later

این ممیزی هیچ‌یک از موارد زیر را اجرا نکرده است. در صورت approval جداگانه، scope پیشنهادی باید یکی از دو مسیر منسجم باشد:

### مسیر A — Circle واقعی با equality invariant

1. افزودن validation صریح در `validatePad` برای `shape === "circle"` و equality با policy عددی مشخص.
2. تعیین رفتار migration برای unequal persisted values: reject با diagnostic شفاف یا migration صریح و قابل‌ردیابی؛ نه normalization خاموش.
3. افزودن تست direct validation، migration، import/export round-trip و DRC geometry.
4. حفظ finding IDs و ordering موجود و افزودن diagnostic schema-level بدون تغییر DRC IDs.
5. update مستندات و fixtureها برای ثبت invariant.

### مسیر B — پشتیبانی واقعی از independent dimensions

1. تعریف shape/contract روشن برای ellipse یا نام‌گذاری مستقل، بدون استفاده‌ی مبهم از `circle`.
2. هماهنگ‌سازی `supportPad`، point/segment distance، pad-to-pad distance، DRC، rendering، hit testing و هر future export path.
3. افزودن fixtureهای unequal و assertions عددی مستقل.
4. تعیین backward compatibility برای Circleهای فعلی و migration/version policy.
5. مستندسازی اینکه manufacturing/export هنوز وجود ندارد و نباید ادعای آن اضافه شود.

هیچ‌کدام از این follow-upها در P2.2 اجرا نشدند.

## 14. Explicit preservation statement

در این investigation:

- هیچ source file تغییر نکرد؛
- هیچ test file تغییر نکرد؛
- هیچ package configuration یا dependency تغییر نکرد؛
- هیچ workflow تغییر نکرد؛
- هیچ branch جدیدی ایجاد نشد؛
- هیچ commit جدیدی ایجاد نشد؛
- هیچ push انجام نشد؛
- هیچ PR جدیدی ایجاد یا PR #3 اصلاح نشد؛
- هیچ merge، rebase، release یا tag انجام نشد؛
- `main`، P1، P2/P2.1 و PR #3 تغییر نکردند؛
- هیچ Circle dimension normalize، migrate یا rewrite نشد؛
- geometry algorithms، finding IDs/order، project compatibility، UI و manufacturing behavior تغییر نکردند.

این فایل تنها deliverable این مرحله است و گزارش آن **design-only** است؛ نتیجه‌ی آن مجوز اجرای اصلاح production محسوب نمی‌شود.
