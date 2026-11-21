# گزارش ممیزی دروازه P1 برای نگاشت اجرایی Phase 6.1.2

**نتیجه: P1 کامل نیست؛ P2 شروع نشده است.** شرط توقف برقرار است، چون در baseline محصول هیچ انتخاب‌گر صریح و نسخه‌داری برای dispatch مدل/evaluator وجود ندارد. تست‌های طلایی v2 و رفتار تاریخی clearance در کد حضور دارند و suite متمرکز موفق است، اما این موارد جای معیار مستقل «Selector is explicit; never sniff span presence» را نمی‌گیرند. در نتیجه، این گزارش P2 را پیاده‌سازی‌شده یا تأییدشده معرفی نمی‌کند.

## منبع مرجع و نگاشت فاز

منبع کنترل‌کننده، همان فایل پیوست‌شده از سوی کاربر با نام `PHASE_6_0_10_DELEGATED_OWNER_DECISIONS_AND_PRODUCT_ARCHITECTURE.md` است؛ سند دیگری از Phase 6.0 جایگزین آن نشده است. بخش 11، بند 2، صریحاً ایجاد golden fixtureهای v2 و پیاده‌سازی model selector صریح را پیش‌نیاز می‌داند. جدول بخش 13 نیز P1 را «V2 evaluator freeze/dispatch» تعریف می‌کند: goldenهای v2 باید رفتار projected-2D و fallback را ثابت کنند، selector باید صریح باشد و نباید با دیدن ViaSpan حدس زده شود؛ شناسه/کلید تاریخی باید از baseline درست بازیابی شود یا بدون اختراع مقدار جدید دست‌نخورده بماند. rollback نیز باید reader/evaluator v2 را نگه دارد و در صورت شکست هم‌ارزی، migration/new model را غیرفعال کند. [1]

سند canonical در جدول بخش 13، P2 را «Schema-v3 and migration contract» می‌نامد و آن را وابسته به P0–P1 قرار می‌دهد. بنابراین «Phase 6.1.2» در دستور اجرایی این کار فقط برچسب نگاشت پروژه به P2 است، نه نام لفظی یک مرحله در سند canonical. چون P1 کامل نیست، معیارهای P2 در این اجرا پیاده‌سازی یا تأیید نشده‌اند. [1] [2]

## مبنای ممیزی و حفظ ایزولاسیون

مخزن محصول `soheil6913/-PCB-Studio-Pro` در baseline دقیق `a98384bbfc3296947b90f5254a03a77b11fdc8a9` بررسی شد. این SHA همان merge commit مربوط به PR شماره 2 است؛ PR در 2026-11-21 ادغام شده و check-run به نام `verify` روی همین SHA با نتیجه `success` خاتمه یافته است. [3] [8] [9]

از baseline فوق یک clone تازه و ایزوله استفاده شد. پس از نصب وابستگی‌ها با `pnpm install --frozen-lockfile`، suite متمرکز اجرا شد و tracked worktree پاک ماند؛ HEAD همچنان روی همان SHA بود. هیچ شاخه‌ای ساخته نشد، هیچ فایل محصولی تغییر نکرد، commit یا pushی به مخزن محصول انجام نشد و PR تازه‌ای باز نشد. چون P1 در دروازه متوقف شد، P2 آغاز نشد.

## نتیجه معیارهای P1

**رفتار طلایی v2 و projected-2D all-pairs — برقرار است.** تست‌های merged شامل 14 سناریوی Via-clearance و مقایسه با فرمول مستقل برای همهٔ جفت‌های معتبر خارج از نوار عدم‌قطعیت مستند هستند. موارد diameter صریح، fallback مبتنی بر `drill * 2`، برابری دقیق آستانه، نقض قطعی، نبود rule، ترتیب آرایه و چند جفت مستقل نیز بررسی می‌شوند. پیاده‌سازی baseline حلقهٔ all-pairs را روی تمام Viaها اجرا می‌کند؛ فاصلهٔ دوبعدی مراکز را می‌سنجد و شرطی بر هم‌پوشانی لایه‌ها ندارد. قطر مؤثر همان `(diameter ?? drill * 2)` است. بنابراین رفتار تاریخی `minimumViaClearance` و fallback حاضرند و suite آن‌ها را تثبیت می‌کند. [4] [5] [6]

**شناسه‌های finding و RuleId — در goldenها حفظ شده‌اند.** تست snapshot، `id`، `ruleId`، `severity` و `objectIds` را با مقادیر مورد انتظار fixture مقایسه می‌کند. ارزیابی انجام‌شده شناسهٔ تازه‌ای اختراع یا شناسهٔ تاریخی را جایگزین نکرده است. [5] [6]

**حدس‌زدن policy بر مبنای حضور ViaSpan — در کد اجرایی پیدا نشد.** جست‌وجوی read-only سراسری روی فایل‌های tracked در SHA دقیق baseline، `ViaSpan` اجرایی یا شرطی که با حضور span مدل/evaluator را عوض کند پیدا نکرد. دو hit مشابه در تست‌ها صرفاً نام fixture/متغیر (`futureViaSpan` و `noViaSpan`) هستند؛ هیچ‌کدام selector اجرایی نیستند. نبود چنین شرطی به‌تنهایی معیار P1 را کامل نمی‌کند، چون انتخاب‌گر صریح نیز لازم است. [3] [4] [5] [7]

**اعمال gate شواهد مدل جدید به v2 — در baseline مشاهده نشد.** مدل حاضر `EngineeringVia` را با مختصات، drill، diameter اختیاری و tuple لایه‌های v2 تعریف می‌کند؛ مدل ViaSpan/فرایند/ledger برای انتخاب evaluator در این مسیر وجود ندارد. Via-to-via clearance با لایه‌ها فیلتر نمی‌شود. کد legacy برای نبودن `layers` در برخی بررسی‌های track-to-via و via-to-pad finding اطلاع‌رسانی جداگانه دارد؛ این رفتار موجود v2 است و با Via-pair clearance یا selector یکی نیست. [3] [4] [7]

**Selector صریح و dispatch نسخه‌دار — برقرار نیست؛ این blocker است.** `EngineeringProject.schemaVersion` اختیاری است و مقدار جاری پروژه 2 است. اعتبارسنجی، نسخه‌های عددی 1 و 2 را می‌پذیرد، اما `runDesignRules` پس از اعتبارسنجی همواره همان `validateSchematic(project)` و `validatePcb(project)` را فراخوانی می‌کند. `validatePcb` ورودی نسخه‌دار/selector دریافت نمی‌کند و `schemaVersion` را برای انتخاب evaluator نمی‌خواند. `migrateProjectJson` هم مقدار فاقد `schemaVersion` را به‌عنوان ورودی legacy v1 تلقی و به نسخهٔ جاری 2 تبدیل می‌کند. پس این metadata و migration موجود، dispatch صریح v2 در برابر مدل جدید نیست. تست‌های golden مقدار `schemaVersion: 2` دارند، اما clearance را مستقیماً با `validatePcb(fixture.project)` می‌سنجند؛ هیچ تستی انتخاب evaluator بر اساس نسخه یا رفتار unsupported model را assert نمی‌کند. تست `hypothetically disjoint future spans` فقط metadata فرضی fixture را بررسی می‌کند و یک مدل runtime یا dispatch نیست. [3] [4] [5] [6]

این gap با دو الزام منبع قابل ردیابی است: بند 2 بخش 11 می‌گوید explicit model selector باید پیاده‌سازی شود؛ معیار P1 در بخش 13 می‌گوید selector صریح باشد و حضور ViaSpan مبنای حدس نباشد. task specification نیز صریحاً project/model selection صریح و نسخه‌دار را در چک‌لیست P1 قرار می‌دهد. [1] [2]

## شکاف دقیق و حداقل دامنهٔ اصلاح

**شکاف:** نسخهٔ پروژه یک metadata اختیاری است و در مسیر DRC به انتخاب model/evaluator تبدیل نشده است. در نتیجه، baseline برای انتخاب legacy v2 در برابر مدل آینده، قرارداد dispatch صریحی ندارد و تست‌های Phase 6.1.1 آن مرز را پوشش نمی‌دهند. این نتیجه به معنی وجود ViaSpan-sniffing نیست؛ جست‌وجو چنین منطق اجرایی‌ای نیافت. نقص، نبود انتخاب‌گر صریح است.

**حداقل دامنهٔ اصلاحی برای P1، که در این اجرا انجام نشد و نیازمند مجوز اجرای اصلاح است:** یک قرارداد انتخاب‌گر صریح و نسخه‌دار مطابق معماری مصوب تعریف و مسیر اجرای v2 را به evaluator تاریخی موجود dispatch کند؛ انتخاب هیچ‌گاه از حضور/عدم حضور ViaSpan استنباط نشود؛ خروجی goldenهای v2، شامل RuleId و finding ID، بدون تغییر بماند. تست‌های متمرکز باید dispatch صریح legacy-v2، نسخه/model ناشناخته یا پشتیبانی‌نشده، و ثابت‌ماندن خروجی v2 در برابر تغییرات فرضی presence span را پوشش دهند. این اصلاح نباید به پیاده‌سازی schema-v3 یا migration گسترش یابد. پس از پذیرش مستقل این اصلاح، P1 باید دوباره ممیزی شود؛ فقط در صورت کامل‌شدن P1 می‌توان P2 را آغاز کرد. این گزارش دربارهٔ نام فیلد، مقدارهای enum، یا سیاست جزئی نسخهٔ آینده تصمیم جدیدی نمی‌گیرد.

## تست‌ها، CI و وضعیت P2

روی SHA `a98384bbfc3296947b90f5254a03a77b11fdc8a9` این دستور اجرا شد:

```text
pnpm exec vitest run shared/engineering.v2-compatibility.test.ts
```

نتیجه: 1 فایل تست و 20 از 20 تست موفق شدند. این نتیجه فقط موفقیت suite متمرکز موجود را اثبات می‌کند؛ نبود selector را جبران نمی‌کند. check-run ادغام PR شماره 2 با نام `verify` نیز روی همان SHA موفق است. [5] [9]

به دلیل عدم تغییر کد و توقف در دروازهٔ P1، `pnpm test`، `pnpm check` و `pnpm build` برای این اجرا اجرا نشدند؛ بنابراین نتیجه‌ای برای آن‌ها ادعا نمی‌شود. این کار هیچ تستی برای P2، هیچ پیاده‌سازی schema-v3/migration، هیچ شاخه‌ای و هیچ PR جدیدی ندارد. PR شماره 2 همان PR پیشین Phase 6.1.1 است و گزارش آن را PR مربوط به Phase 6.1.2 معرفی نمی‌کند. [2]

## وضعیت تحویل و ریسک‌های باز

این فایل تنها artifact تحویلیِ این ممیزی است و در مخزن موقت گزارش‌ها `soheil6913/PCB`، شاخه `main` ثبت می‌شود. مخزن محصول و PR آن حاوی این گزارش نیستند. baseline محصول همچنان `a98384bbfc3296947b90f5254a03a77b11fdc8a9` باقی مانده است؛ هیچ فایل محصولی تغییر نکرده است.

معیار برآورده‌نشده P1، نبود model/evaluator selector صریح و تست dispatch است. تا رفع و پذیرش مستقل این gap، P2 مجاز به شروع نیست. همچنین suite کامل پروژه، check و build در این اجرای بدون تغییر کد اجرا نشده‌اند. اجرای P2، تغییرات محصول، شاخه یا PR جدید عمداً متوقف ماندند.

## منابع

[1]: پیوست مرجع ارائه‌شده توسط کاربر، `PHASE_6_0_10_DELEGATED_OWNER_DECISIONS_AND_PRODUCT_ARCHITECTURE.md`، بخش 11 بند 2 و بخش 13 ردیف‌های P1–P2. این attachment عمومی/منتشرشده نیست و در مخزن گزارش کپی نشده است.
[2]: پیوست دستور اجرای ارائه‌شده توسط کاربر، `pasted_content.txt`، چک‌لیست دروازه P1، معیارهای توقف، جداسازی مخازن و الزامات گزارش. این attachment عمومی/منتشرشده نیست و در مخزن گزارش کپی نشده است.
[3]: https://github.com/soheil6913/-PCB-Studio-Pro/blob/a98384bbfc3296947b90f5254a03a77b11fdc8a9/shared/engineering.ts#L1-L23 "مدل Via، schemaVersion و نسخهٔ جاری در baseline"
[4]: https://github.com/soheil6913/-PCB-Studio-Pro/blob/a98384bbfc3296947b90f5254a03a77b11fdc8a9/shared/engineering.ts#L320-L350 "Via clearance، اجرای DRC، اعتبارسنجی و migration در baseline"
[5]: https://github.com/soheil6913/-PCB-Studio-Pro/blob/a98384bbfc3296947b90f5254a03a77b11fdc8a9/shared/engineering.v2-compatibility.test.ts "تست‌های compatibility و migration نسخهٔ v2"
[6]: https://github.com/soheil6913/-PCB-Studio-Pro/blob/a98384bbfc3296947b90f5254a03a77b11fdc8a9/shared/engineering.v2-compatibility.fixtures.ts "fixtureهای طلایی compatibility نسخهٔ v2"
[7]: https://github.com/soheil6913/-PCB-Studio-Pro/blob/a98384bbfc3296947b90f5254a03a77b11fdc8a9/shared/phase5_4.drc-boundary-semantics.test.ts#L1339-L1370 "تست قدیمی missing Via layers برای clearanceهای track و pad"
[8]: https://github.com/soheil6913/-PCB-Studio-Pro/pull/2 "PR شماره 2 مربوط به Phase 6.1.1"
[9]: https://github.com/soheil6913/-PCB-Studio-Pro/actions/runs/44909006925/job/136860607891 "check-run موفق verify روی merge commit baseline"
