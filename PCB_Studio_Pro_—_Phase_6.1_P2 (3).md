# PCB Studio Pro — Phase 6.1 P2.3
## ممیزی مستقل قراردادهای API هندسی و مرزهای اعتبارسنجی

**وضعیت:** تکمیل ممیزی منبع‌محور؛ اجرای تست‌ها به‌علت نبود executableهای وابستگی در checkout مسدود شد. هیچ اصلاحی پیاده‌سازی نشده است.

## 1. خلاصه اجرایی

مبنای ممیزی، checkout پاک شاخهٔ `fix/phase6-1-p2-2-circle-oval-contract-20261123` در SHA `192cac1e3b0293a9ce41d9c06f01a91ae70333fe` است؛ این SHA با مرجع P2.2 الزام‌شده تطبیق دارد. checkout اصلی `/home/ubuntu/work/repo` جدا و دست‌نخورده روی `implementation/phase6-net-aware-drc-20261120` در `6fad0dcdc7e5878e671b8b419b2f61084e5a8138` باقی است.

مسئولیت‌های مرزی عمدتاً از هم تفکیک شده‌اند: `validateProjectJsonDetailed` اعتبارسنجی کامل ساختار پروژه را انجام می‌دهد؛ `validatePcb` مرز سازگاری PCB-only است؛ `validateSchematic` ورودی زیرمجموعهٔ شماتیک را از مسیر اعتبارسنجی ساختاری بررسی می‌کند؛ `runDesignRules` ابتدا پروژهٔ کامل را اعتبارسنجی و سپس همان evaluator نسخهٔ ثابت V2 را اجرا می‌کند. قراردادهای Circle/Oval نیز در validator حفظ شده‌اند: ابعاد Circle باید برابر و مثبت/متناهی باشند و Oval می‌تواند ابعاد مستقل داشته باشد (خطوط 415 و 258 در `shared/engineering.ts`).

سه نقص/ریسک منبع‌اثبات‌شده برجسته شد: (1) آرایه‌های sparse از حلقه‌های `forEach`/`map` اعتبارسنجی به‌طور کامل عبور می‌کنند و می‌توانند محتوای ناقص را به evaluator بدهند؛ (2) مسیر محاسبهٔ `route45` برای نسبت‌های عمومی غیر از نمونهٔ 2:1 نقطهٔ میانی‌ای می‌سازد که هر دو قطعه 45 درجه نیستند؛ (3) ورودی `options: null` با وجود نوع پیش‌فرض، در مسیر عمومی `validatePcb` قابل عبور است و هنگامی که محاسبهٔ جفت پد به GJK می‌رسد، به دسترسی به `options.gjkMaxIterations` و throw منجر می‌شود. علاوه‌براین، توابع هندسی مستقیم exported عموماً قرارداد runtime خوداعتبارسنجی ندارند؛ نتیجه می‌تواند عدد ظاهراً معتبر باشد، `NaN`/Infinity یا `INDETERMINATE` باشد، یا برای گزینهٔ null استثنا رخ دهد.

هیچ تستی با موفقیت اجرا نشد: تلاش برای اجرای چهار فایل تست مرتبط با `pnpm exec vitest run ...` با exit code 254 متوقف شد، چون `vitest` در checkout نصب/قابل‌دسترسی نبود. بنابراین گزارش، ادعای تأیید اجراییِ repro ندارد؛ یافته‌ها از کد و تست‌های موجود استنتاج شده‌اند.

## 2. مخزن، شاخه و مبنای ممیزی

| مورد | مقدار تأییدشده |
|---|---|
| مخزن | `soheil6913/-PCB-Studio-Pro` |
| شاخهٔ ممیزی | `fix/phase6-1-p2-2-circle-oval-contract-20261123` |
| HEAD | `192cac1e3b0293a9ce41d9c06f01a91ae70333fe` |
| SHA مرجع P2.2 | `192cac1e3b0293a9ce41d9c06f01a91ae70333fe` (مطابقت دارد) |
| وضعیت checkout ممیزی | پاک هنگام بررسی؛ tracking با ref ریموت متناظر |
| checkout اصلی | `implementation/phase6-net-aware-drc-20261120`, SHA `6fad0dcdc7e5878e671b8b419b2f61084e5a8138`, پاک |
| refs گزارش‌شده در بررسی مستقل قبلی | `main`=`a98384bbfc3296947b90f5254a03a77b11fdc8a9`; P1=`f2db0afbdcdea6909e7ee91a8f340862741c6db0`; P2.1=`e6b2a9153beec74c6d2013c6eda5362e850806b0` |
| PR #3 | در بررسی قبلی باز، Draft و ادغام‌نشده گزارش شد؛ این ممیزی PR را تغییر نداد |

بررسی‌های Git و ref در checkout جداگانه انجام شدند تا مبنای خواندن از checkout اصلی با HEAD متفاوت جدا بماند. تغییر refها یا PR در این کار انجام نشد.

## 3. موجودی APIها و مسئولیت

`shared/engineering.ts` در مجموع 18 تابع exported مرتبط با مدل/هندسه/اعتبارسنجی/DRC دارد. توابع و APIهای geometry این ماژول از خطوط 28 تا 263، validator/evaluator از 269 تا 436 هستند. `shared/phase5_3.independent-oracle.ts` ابزار test-only است (توضیح فایل در خطوط 1–5)، و 20 تابع exported مستقل برای oracle دارد؛ نباید به‌عنوان ورودی برنامه یا API تولیدی تلقی شود.

| API | محل | مسئولیت و قرارداد مشاهده‌شده |
|---|---|---|
| `distance` | engineering.ts:28 | محاسبهٔ فاصله با `Math.hypot`؛ ورودی را runtime validate نمی‌کند. |
| `measure` | :29 | wrapper اندازه‌گیری؛ grid فقط با شرط `grid > 0` تقسیم می‌شود، بدون finite/type check. |
| `snapToGrid` | :30 | snap ساده؛ ورودی نقطه/grid را validate نمی‌کند. |
| `rotatePoint`, `transformLocalPoint` | :31–32 | تبدیل مستقیم مختصات/زاویه، بدون رد ورودی نامعتبر. |
| `route45` | :33 | مسیر سادهٔ دو/سه‌نقطه‌ای؛ ورودی runtime validate نمی‌شود؛ نقص نسبت شیب در F-01. |
| `segmentsIntersect` | :66 | predicate عمومی تقاطع؛ orientation مقاوم‌سازی شده، ولی `distance`/ساختارها precondition مستند runtime ندارند. |
| `segmentDistance` | :79 | فاصلهٔ قطعه‌ها؛ ممکن است `NaN` از `pointToSegment` منتشر شود (خطوط 67–78). |
| `gjkWithinDistance` | :119–224 | بودجهٔ iteration را validate می‌کند و حالت `INDETERMINATE` دارد؛ Pads/clearance را به‌طور کامل validate نمی‌کند. |
| `padToPadDistanceDetailed` | :258 | در مسیرها عدد converged یا indeterminate برمی‌گرداند؛ shape ناشناخته ممکن است به fallback GJK برسد؛ گزینهٔ null می‌تواند throw کند. |
| `padToPadDistance` | :259 | wrapper عددی؛ برای indeterminate، `GeometryCalculationError` می‌اندازد. ورودی پد را validate نمی‌کند. |
| `viaToPadDistance` | :263 | فرمول مستقیم؛ قرارداد مستند ورودی ندارد و ورودی بد می‌تواند خروجی ظاهراً عادی/NaN بدهد. |
| `validateSchematic` | :269–301 | ورودی سطح بالا را با validator ساختاری می‌سنجد و یافته برمی‌گرداند؛ بعد محاسبات topology اجرا می‌کند. |
| `validatePcb` | :367–377 | مرز PCB-only عمومی؛ اعتبارسنجی ساختاری سپس evaluator؛ options در runtime validate نمی‌شود. |
| `runDesignRules` | :388–410 | full-project validation، سپس ارزیابی V2 و یافته‌های شماتیک؛ قرارداد تأییدشده محفوظ است. |
| `validateProjectJsonDetailed` | :417–433 | ورودی `unknown` و خطاهای مسیرمند؛ sparse-array gap دارد. |
| `migrateProjectJson` | :435 | migration نسخه‌دار با defaults برای فیلد غایب؛ خروجی را از validator عبور می‌دهد؛ null در ورودی رد می‌شود. |
| `validateProjectJson` | :436 | type guard که همان validator را صدا می‌زند. |

در فایل oracle، exports (همه test-only) شامل exact BigInt predicates/distances، distance intervals بیضی، تبدیل مستقل مختصات و گوشه‌های مستطیل چرخیده و interval فاصله نقطه/قطعه تا چندضلعی هستند. خطوط مرجع: `shared/phase5_3.independent-oracle.ts:18–601`. هیچ‌یک تابع تولیدی هندسه را وارد نمی‌کند (خطوط 1–5). این exports با توابع تولیدی شمارش نشده‌اند.

## 4. ماتریس مرز اعتماد

| مرز/لایه | ورودی قابل‌اعتماد | اعتبارسنجی واقعی | ارزیابی |
|---|---|---|---|
| Full project: `validateProjectJsonDetailed` | `unknown` | root، فیلدهای ناشناخته، مدل‌های nested، اعداد و شکل‌ها را بررسی می‌کند (:417–433) | مناسب‌ترین مرز ساختاری؛ sparse arrays نیازمند اصلاح. |
| Full project: `runDesignRules` | `EngineeringProject` در TS، ورودی runtime ممکن است خراب باشد | ابتدا validator کامل (:388–390)، سپس نسخهٔ schema و evaluator V2 (:392–409) | مرز DRC کامل؛ حفظ شود. |
| PCB-only: `validatePcb` | Pick تایپی از پروژه، ولی runtime نامطمئن | root محدود و version، سپس evaluator که payload PCB را validate می‌کند (:344–377، :303–323) | مرز سازگاری PCB-only است؛ نباید با اعتبارسنجی کامل عوض شود. |
| Schematic: `validateSchematic` | Pick تایپی، runtime نامطمئن | ساختار components/wires/junctions با validator عمومی (:269–286) | عمدتاً fail-closed؛ نقص sparse arrays و حساسیت topology به اعداد بزرگ باقی است. |
| Geometry API مستقیم | `Pad`, `EngineeringVia`, `Point` تایپی | اغلب هیچ بررسی کامل runtime ندارد | باید قرارداد precondition/خروجی invalid مستند شود؛ وضعیت فعلی ناهمگون است. |
| Import/storage/UI | متکی به caller | `migrateProjectJson` ابزار مهاجرت است، اما مسیر callerهای برنامه در این snapshot به‌طور کامل ردیابی قطعی نشد | ادعایی دربارهٔ همهٔ ورودی‌های شبکه/ذخیره‌سازی نمی‌شود؛ این محدودیت را در نظر بگیرید. |
| Test-only oracle | fixtureهای تست | بعضی ورودی‌ها را صریح validate و بعضی را با throw/interval مدل می‌کند | از production path مجزا است. |

### مسیرهای فراخوانی مهم

- `runDesignRules → validateProjectJsonDetailed → (schemaVersion gate) → evaluatePcbV2 → validateProjectJsonDetailed` و سپس `validateSchematic`; شواهد `engineering.ts:388–410`, `303–323`, `269–286`.
- `validatePcb → validatePcbRootBoundary → evaluatePcbV2 → validateProjectJsonDetailed`; شواهد `:367–377`, `:344–360`, `:303–323`.
- evaluator: `localPads → padAxisAlignedHalfExtents/segmentToPadDistance/padToPadDistanceDetailed/viaToPadDistance/segmentDistance/distance`; شواهد `:100–110`, `:327–338`.
- `padToPadDistanceDetailed → analytic shape paths یا gjkWithinDistance → binary search`; `:258`, `:119–224`.
- `migrateProjectJson → validateProjectJsonDetailed`; `:435`.
- `validateSchematic → validateProjectJsonDetailed → graph/topology`؛ `:269–300`.

آزمون‌های موجود مستقیماً APIهای هندسه و مرزهای DRC را مصرف می‌کنند: `shared/engineering.test.ts:35–160`, `shared/engineering.p2.test.ts:1–69`, `shared/phase5_1.geometry-validation.test.ts:1–546`, `shared/phase6-1-p2-2.circle-oval-contract.test.ts` و `shared/engineering.v2-compatibility.test.ts`. این پوشش شامل malformed object، Circle/Oval و برخی extreme inputs است، اما مورد sparse-array و options-null در پوشش مشاهده‌شده یافت نشد.

## 5. یافته‌های طبقه‌بندی‌شده

### F-01 — P2: `route45` برای شیب‌های عمومی مسیر 45 درجه نمی‌سازد

**شاهد:** `shared/engineering.ts:33`: اگر اختلاف‌ها نه برابر و نه محوری باشند، `diagonal=min(|dx|,|dy|)` و نقطهٔ میانی `(start.x + sign(dx)*diagonal, start.y)` است. برای start `(0,0)` و end `(80,20)` خروجی نقاط `(0,0)`, `(20,0)`, `(80,20)` خواهد بود؛ قطعهٔ دوم نسبت 60 به 20 دارد و زاویه‌اش 45 درجه نیست. تنها fixture مشاهده‌شده‌ی `engineering.test.ts:35` برای `(80,40)` است که اتفاقاً قطعهٔ دوم 40×40 می‌شود.

**انتظار/واقعیت:** با توجه به نام و استفادهٔ routing، مسیر باید فقط قطعات مجاز 45°/محوری تولید کند یا قرارداد محدودیت نسبت را صریح رد کند؛ فعلی بعضی شیب‌ها را بی‌هشدار تحویل می‌دهد. **تأثیر مسیر عادی:** احتمالاً callerهای routing، نه validator/DRC مستقیم؛ هیچ نتیجه‌ای دربارهٔ کاربرد runtime خاص بدون call-site قطعی ادعا نمی‌شود. **اصلاح حداقلی:** تعیین قرارداد هندسی؛ الگوریتم مسیریابی مانِهَتَن/45° صریح یا rejection، بدون تغییر DRC موجود. **تست:** نسبت‌های 4:1، 1:4 و شیب‌های علامت‌دار؛ بررسی هر segment. ریسک: تغییر شکل routeهای موجود.

### F-02 — P1/P2 (تأیید boundary، شدت عملیاتی وابسته به مسیر): sparse arrays از validation عبور می‌کنند

**شاهد:** validator روی `components`, `wires`, `tracks`, `vias` ابتدا `Array.isArray` می‌سنجد، سپس `uniqueIds` و nested validation را با `forEach` می‌گرداند (`engineering.ts:422–428`). `forEach` عناصر حذف‌شدهٔ sparse array را رد نمی‌کند. نمونهٔ ساختاری `[ , validTrack ]` بنابراین hole را بدون error می‌گذراند. evaluator همان آرایه‌ها را با `forEach` می‌گرداند یا `flatMap` می‌کند (`:325–338`)، پس بعضی شیءها عملاً بی‌ارزیابی می‌شوند. در `validateSchematic`, `normalized.wires.map(...)` hole را حفظ می‌کند، و سپس حلقه‌های indexدار topology در صورت ترکیب hole با طول/شبکهٔ مناسب ممکن است به عضو undefined برسند (`:293`, `:297`).

**انتظار/واقعیت:** آرایه‌های JSON خالص hole ندارند، اما API صریحاً `unknown` و runtime را می‌پذیرد و TS callerها می‌توانند آرایهٔ sparse بسازند؛ لازم است hole به‌عنوان ورودی malformed رد شود یا normalizer صریح داشته باشد. **قابلیت دسترسی:** direct API و `validatePcb`/`runDesignRules` قابل دسترسی‌اند؛ ورودی JSON شبکه‌ای معمولی hole ندارد، ولی stateهای JS داخلی/تست/API ممکن است. **اصلاح حداقلی:** پیمایش index-based و الزام `hasOwn` هر index در مرز validation؛ بدون پرکردن خودکار hole. **تست:** sparse در هر آرایه و sparse در wires/components؛ تضمین validator خطای pathمند و APIها بدون throw/بدون omission خاموش.

### F-03 — P2: `validatePcb(..., null)` می‌تواند از مرز ساختاری عبور کرده و throw کند

**شاهد:** امضای `validatePcb(..., options: GeometryOptions = {})` (:367–370) فقط default را برای `undefined` می‌دهد؛ `null` در runtime جایگزین نمی‌شود. `evaluatePcbV2` options را تا `padToPadDistanceDetailed` می‌رساند (:336). آن تابع، پس از مسیرهای analytic، `options.gjkMaxIterations` را می‌خواند (:258). برای جفت Oval چرخیدهٔ غیرهم‌محور که وارد GJK شود، null باعث TypeError می‌شود. خود GJK iteration budget را بررسی می‌کند (:125–126)، اما این کنترل بعد از dereference است.

**انتظار/واقعیت:** API DRC که malformed project را به `PCB_INVALID_INPUT` تبدیل می‌کند نباید با malformed options ناگهانی throw کند؛ یا options خارج از قرارداد باشد و precondition مستند شود، یا رد ساختاری شود. **دسترسی:** caller مستقیم `validatePcb`، به‌ویژه تست/مصرف‌کنندهٔ کتابخانه‌ای؛ شواهدی که UI options=null می‌فرستد یافت نشد. **اصلاح حداقلی:** validate options در مرز و خروجی diagnostic پایدار، یا normalize فقط `undefined` و رد `null`. **تست:** options null و مقادیر `gjkMaxIterations` NaN، fractional، صفر، منفی؛ مسیرهایی که GJK را قطعاً فعال می‌کنند.

### F-04 — P2: APIهای هندسی مستقیم خوداعتبارسنجی ندارند و خروجی نامعتبر ناهمگون است

**شاهد:** `distance`/`measure`/`rotatePoint` مستقیم محاسبه می‌کنند (:28–32)؛ `viaToPadDistance` فرمول را بدون guard اجرا می‌کند (:263); `padToPadDistanceDetailed` با shapeها و dimensions نامعتبر وارد analytic helpers می‌شود (:258); `gjkWithinDistance` بعضی intermediateهای غیرمتناهی را indeterminate می‌کند، ولی قبل از آن مستقیم به `a.position` و ابعاد دسترسی می‌یابد (:128–146). تفاوت `padToPadDistance` با `viaToPadDistance` روشن است: اولی indeterminate را throw می‌کند (:259)، دومی number برمی‌گرداند (:263). Circle نامعتبر با ابعاد unequal اگر مستقیماً به circle-circle برسد، تنها `width` را به شعاع می‌گیرد و می‌تواند فاصلهٔ عددی قابل‌قبول‌نما بدهد؛ ورودی پروژه از validator رد می‌شود (:415)، پس این یافته به‌تنهایی نقص DRC پروژهٔ معتبر را اثبات نمی‌کند.

**انتظار/واقعیت:** APIهای هندسی می‌توانند precondition داشته باشند، ولی قرارداد فعلی برای مصرف‌کننده مستند نیست و پاسخ نامعتبر یکدست نیست. **شدت:** P2 برای ناسازگاری قرارداد/اعتماد caller، نه اثبات خطای DRC معتبر. **اصلاح حداقلی:** مستندسازی precondition «قبلاً validated» یا wrapperهای عمومی با نتیجهٔ discriminated invalid-input؛ helpers داخلی از exports جدا شوند. **تست:** malformed structure، shape unknown، missing point، Circle unequal، oval invalid، nonfinite coordinates، clearance و options.

### F-05 — P2: مختصات finite بسیار بزرگ از validator می‌گذرند و بعضی فاصله‌های ساده می‌توانند indeterminate/NaN شوند

**شاهد:** `finite` تنها `Number.isFinite` است (:82); `validateCoordinates` همین شرط را دارد (:413); مقدارهای finite نزدیک `Number.MAX_VALUE` را نمی‌بندد. در `pointToSegment` تفاضل‌ها ممکن است overflow کنند و طول غیرمتناهی، صریحاً `NaN` بازگرداند (:67–78). DRC برای track-track فاصله را می‌گیرد و `compareClearance` مقدار nonfinite را indeterminate می‌شناسد (:84–89, :326); بنابراین در این مسیر fail-safe error finding دارد. اما topology schematic از `pointToSegment` برای وصل‌کردن استفاده می‌کند (:294–297) و نتیجه NaN مقایسهٔ tolerance را false می‌کند؛ همچنین `distance` در dedup nodes ممکن است به Infinity برسد (:292). **انتظار/واقعیت:** ورودی finite مجاز است، اما الگوریتم‌ها در دامنهٔ finite کامل تضمین عددی ندارند؛ بعضی مسیرهای DRC fail-safe و برخی connectivity ممکن است به‌جای indeterminate، اتصال را نپذیرند.

**دسترسی:** direct geometry و validation سطح پروژه؛ impact بیشتر به دادهٔ pathological/صادرات غیرعادی محدود است. **اصلاح حداقلی:** تعیین دامنهٔ مجاز مختصات در schema یا محاسبهٔ topology مقیاس‌پذیر و نتیجهٔ uncertainty؛ رد حد arbitrary نیازمند تصمیم دامنه/واحد است. **تست:** مختصات finite نزدیک حد overflow، offsetهای بزرگ با delta کوچک، و کنترل اینکه topology نامعلوم را «قطعاً جدا» معرفی نکند.

### F-06 — DESIGN: قرارداد runtime مستقیم geometry و نقش APIهای exported

نوع‌های TypeScript در compile-time مفیدند ولی برای `unknown`، JS caller، دادهٔ deserializeشده یا `as` تضمین نیستند. معماری فعلی هم APIهای محاسباتی exported دارد، هم internal helperهای private، اما مستندات precondition عمومی geometry در همین ماژول دیده نمی‌شود. تصمیم لازم: آیا direct geometry API عمومی باید structured invalid result بدهد، خطای قطعی بیندازد، یا پیش‌شرط «validated inputs only» داشته باشد؟ این انتخاب را نباید از یافته‌های DRC به‌تنهایی نتیجه گرفت.

### NO ISSUE — قرارداد Circle/Oval و مرزهای اصلی DRC

`validatePad` shapeهای مجاز را محدود و width/height را positive finite می‌کند؛ Circle unequal را رد می‌کند، و Oval مستقل است (:415). `runDesignRules` ابتدا کل پروژه را validate می‌کند (:388–390) و `validatePcb` همچنان boundary PCB-only مستقل با root fields و schema support دارد (:342–377). مهاجرت، فیلدهای غایب را default می‌کند ولی فیلد صریح null/wrong type را با own-property و validation نهایی حفظ/رد می‌کند (:435؛ نیز `shared/engineering.p2.test.ts:11–38`). شواهدی از نرمال‌سازی خاموش Circle در migration دیده نشد.

## 6. پاسخ به ده پرسش اجباری

1. **آیا validatePcb می‌تواند Pad nested خراب را عبور دهد؟** برای ساختارهای dense معمولی، نه؛ evaluator آن را از مسیر `validateProjectJsonDetailed` اعتبارسنجی می‌کند (`:303–323`, `:415`, `:425`). اما sparse hole در آرایه‌های pads/components ممکن است دیده نشود (F-02). گزینهٔ null ورودی geometry نیست ولی boundary options را bypass می‌کند (F-03).
2. **آیا evaluator تمام دادهٔ مصرفی را validate می‌کند؟** در ساختار dense، validator تمام مدل‌های عمده را بررسی می‌کند و evaluator چند کنترل تکمیلی دارد؛ اما options را validate نمی‌کند، finite دامنهٔ اندازه‌پذیر محدود ندارد، و sparse hole را پوشش نمی‌دهد. پس پاسخ مطلق «بله» نیست.
3. **آیا padToPadDistanceDetailed با Circle نامعتبر عدد plausible می‌دهد؟** بله، در مسیر analytic می‌تواند (مثلاً Circle width و height نابرابر: تنها width مبنای شعاع است). این ثابت نمی‌کند `validatePcb` یا `runDesignRules` چنین Padای را ارزیابی می‌کنند؛ validator پروژه آن را رد می‌کند.
4. **آیا GJK مستقیم با Pad خراب گمراه‌کننده است؟** ممکن است پیش از guard، به‌علت property dereference روی structure ناقص throw کند؛ ابعاد/clearance نامعتبر نیز الزاماً به invalid-input نتیجه تبدیل نمی‌شوند. برای intermediate غیرمتناهی، indeterminate می‌دهد. پس contract مستقیم fail-safe و یکنواخت نیست.
5. **آیا viaToPadDistance قرارداد مستند دارد؟** خیر؛ امضا type دارد، ولی comment/precondition یا runtime validation ندارد (:263). در evaluator فقط پس از project validation فراخوانی می‌شود، با استثنای hole sparse.
6. **آیا APIها در malformed input بین عدد، indeterminate و throw تفاوت دارند؟** بله: direct analytic functions number، detailed GJK indeterminate، numeric wrapper throw روی indeterminate، و nested dereference می‌تواند TypeError دهد (F-04).
7. **آیا error conventions یکدست‌اند؟** خیر؛ project validators structured diagnostics، detailed geometry union، wrapper exception و توابع ساده number دارند. این لزوماً اشتباه نیست، اما نیازمند قرارداد مستند است.
8. **آیا معماری trusted helper/public entrypoint را روشن می‌کند؟** درون فایل private helpers وجود دارد و DRC boundary جداست؛ اما geometry helperهای exported فاقد docs دربارهٔ trusted inputs هستند. تفکیک جزئی است، نه کامل.
9. **کدام defects تأییدشده/ابهام/سخت‌سازی‌اند؟** F-01، F-02، F-03 و F-05 نقص/ریسک منبع‌اثبات‌شده‌اند؛ F-04 ناسازگاری contract با تأثیر وابسته به caller؛ F-06 تصمیم طراحی؛ دامنهٔ coordinate limits و اینکه geometry API export بماند hardening/تصمیم محصول است. هیچ P0 شناسایی نشد.
10. **کوچک‌ترین remediation امن چیست؟** نخست sparse-array rejection در validator و options guard در `validatePcb`; سپس اصلاح/تعریف دقیق route45 به‌همراه regression tests؛ مستندسازی یا wrapper اعتبارسنجی برای geometry مستقیم. الگوریتم‌های DRC معتبر و تفکیک `validatePcb`/`runDesignRules` تغییر نکنند. برای extreme coordinates، پیش از سقف‌گذاری، دامنه و واحدها تعیین شود.

## 7. برآورد شدت و اصلاح

| شناسه | شدت | مسیر عادی | اقدام کمینه |
|---|---|---|---|
| F-01 route45 | P2 | احتمالاً caller routing؛ نه اثبات مسیر DRC | define contract، الگوریتم قطعه‌ای معتبر یا رد ورودی‌های خارج قرارداد، تست نسبت‌های متعدد |
| F-02 sparse arrays | P1 اگر ورودی JS داخلی/API؛ P2 در ورودی‌های متعارف JSON | مرزهای validatePcb/runDesignRules/validateSchematic | rejection صریح hole با path؛ regression در همهٔ آرایه‌های nested |
| F-03 options null | P2 | direct validatePcb در مسیر GJK | validate options پیش از evaluator؛ diagnostic پایدار |
| F-04 direct geometry | P2 / contract | caller مستقیم | قرارداد validated-input یا structured invalid؛ حفظ مسیر معتبر DRC |
| F-05 extreme finite coordinate | P2 hardening | دادهٔ pathological، برخی topology | مشخص‌کردن دامنه یا arithmetic مقاوم/indeterminate |
| F-06 public API role | DESIGN | مصرف‌کنندهٔ مستقیم | تصمیم API؛ export visibility و error semantics |
| Circle/Oval boundaries | NO ISSUE | full-project DRC/migration | عدم تغییر؛ حفظ تست‌ها |

هیچ موردی به P0 ارتقا داده نشده است. توصیه‌ها طرح آتی‌اند؛ هیچ موردی در P2.3 تغییر داده نشد.

## 8. برنامهٔ تست پیشنهادی

1. sparse arrays در root و `footprintGeometry.pads`, `components.pins`, `wires`, `tracks`, `vias`, `junctions`؛ assert خطای validation یا نتیجهٔ diagnostic و عدم throw.
2. `validatePcb` با options `null`, `undefined`, `{gjkMaxIterations: 0}`, fractional، NaN، Infinity؛ fixture Oval rotated که قطعاً GJK را اجرا کند.
3. direct calls برای `gjkWithinDistance`, `padToPadDistanceDetailed`, `padToPadDistance`, `viaToPadDistance` با null/missing fields، dimensions صفر/منفی/NaN/Infinity، shape ناشناخته و unequal Circle؛ آزمون جدا از اعتبارسنجی پروژه.
4. `route45`: انواع dx/dy با نسبت‌های 4:1، 1:4، 2:1 و 1:1 در چهار ربع؛ بررسی هر قطعه بر اساس قرارداد نهایی محصول.
5. extreme finite values: نزدیک `Number.MAX_VALUE`, فاصلهٔ دو مختصات که subtraction آن overflow می‌کند، و offset بسیار بزرگ با delta کوچک؛ تضمین DRC `INDETERMINATE` و عدم ادعای topology قطعی.
6. قراردادهای حفظ‌شده: valid/invalid Circle و Oval مستقل در validate، migration، `validatePcb` و `runDesignRules`؛ asserts فعلی نباید تضعیف شوند.

## 9. تست و دستورات اجراشده

| فرمان دقیق | نتیجه |
|---|---|
| `pnpm exec vitest run shared/engineering.test.ts shared/engineering.p2.test.ts shared/phase5_1.geometry-validation.test.ts shared/phase6-1-p2-2.circle-oval-contract.test.ts` | exit code **254**؛ `ERR_PNPM_RECURSIVE_EXEC_FIRST_FAIL: Command "vitest" not found`؛ صفر تست اجرا شد. |
| `git status --short --branch && git rev-parse HEAD && git branch --show-current && git status --porcelain=v1` در checkout ممیزی | HEAD/شاخه تأیید شد؛ خروجی porcelain خالی، درخت پاک. |
| بررسی `shared/engineering.ts`, تست‌های هندسه و oracle، `rg` برای exportها/call sites | خواندن فقط؛ بدون تغییر. |

`package.json` اسکریپت `test` را `vitest run` معرفی می‌کند؛ `check` و `build` نیز scripts موجودند، ولی این‌ها اجرا نشدند. `pnpm test` نیز اجرا نشد چون executable vitest در دسترس نبود. هیچ شمارش تست موفقی وجود ندارد. احتمال cache یا اثر جانبی اجرای ابزار محدود بررسی شد و Git status نهایی در تحویل دوباره کنترل می‌شود.

## 10. محدودیت‌ها

- اجرای تست‌ها به‌علت نبود `vitest` ممکن نشد؛ هیچ repro دینامیکی از یافته‌ها ادعا نمی‌شود.
- مسیرهای سرور/UI/ذخیره‌سازی از نظر فراخوانی validator در همهٔ entrypointها exhaustively با trace کامل runtime اثبات نشدند؛ یافته‌های reachability محدود به call graph کد مشترک و تست‌های موجودند.
- `route45` فقط از نام، الگوریتم، TODO مستند route usage و تست 2:1 استنباط شده؛ سیاست محصول برای نسبت‌های دلخواه روشن نیست، ازاین‌رو F-01 توصیهٔ اصلاح همراه با تعیین قرارداد است.
- تحلیل extreme inputs مبتنی بر رفتار IEEE-754 و کد است و به آزمون اجرایی تبدیل نشده است.
- oracle مستقل test-only شمارش/بررسی شد، نه به‌عنوان API محصول؛ 20 تابع exported آن برای تحقیق تست مستقل به‌کار می‌روند.

## 11. فایل‌های تغییرکرده و تأیید محدوده

تنها فایل ایجادشده توسط این کار:

- `/home/ubuntu/work/PHASE_6_1_P2_3_GEOMETRY_API_BOUNDARY_AUDIT.md`

هیچ application source، test، configuration، workflow، schema یا UI ویرایش نشد. هیچ commit، push، merge، rebase، cherry-pick، PR، release، tag یا deploy انجام نشد. شاخه‌های `main`, P1, P2.1, P2.2 و PR #3 تغییر داده نشدند. checkout اصلی دست‌نخورده باقی ماند. وضعیت نهایی Git در checkout گزارش هنگام شروع نوشتن پاک و روی مبنای درست بود؛ پس از ایجاد گزارش، وضعیت checkout منبع کنترل نهایی جداگانه انجام می‌شود.
