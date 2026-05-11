# งานจากการตรวจสอบฐานโค้ด

วันที่ตรวจสอบ: 2026-05-06

## 1) งานแก้ไขข้อความ/ความชัดเจนของตัวอย่าง config
- **ปัญหา:** `example_config.yaml` ใช้คีย์ `pinecone.environment` ซึ่งไม่มีใน `PineconeConfig` และทำให้ผู้ใช้เข้าใจผิดได้.
- **งานที่ทำ:** ปรับตัวอย่าง config ให้ใช้ `transport`, `cloud`, `region`, `skills.paths`, และ `safety.required_toolsets` ให้ตรงกับโค้ดปัจจุบัน.
- **ผลลัพธ์:** ตัวอย่าง config สอดคล้องกับ field ที่ `load_config()` โหลดจริง.

## 2) งานแก้ไขบั๊ก
- **ปัญหา:** `SkillIndexer.sync()` ใช้ path คงที่ `~/.hermes/skills` แทน `config.skills.paths`.
- **งานที่ทำ:** เพิ่ม `configured_skill_paths()` เพื่อ expand/dedupe/skip path ที่ไม่มีอยู่จริง แล้วให้ `sync()` วน index ทุก path จาก config.
- **ผลลัพธ์:** ผู้ใช้กำหนดหลาย skill directories ได้ตาม config.

## 3) งานแก้ไขคอมเมนต์/เอกสารที่คลาดเคลื่อนกับ behavior
- **ปัญหา:** `require_toolset_match` ถูก define ใน config แต่ policy engine ไม่เคยใช้จริง.
- **งานที่ทำ:** เพิ่ม `required_toolsets` ใน `SafetyConfig` และเพิ่ม logic ให้ `is_allowed()` block skill ที่ไม่มี toolsets ครบตามที่กำหนด.
- **ผลลัพธ์:** safety flag มีผลกับ routing decision จริง แทนที่จะเป็น config ที่ไม่มีผล.

## 4) งานปรับปรุงการทดสอบ
- **ปัญหา:** ไม่มี unit tests ครอบคลุมเส้นทางหลักที่ถูก review.
- **งานที่ทำ:** เพิ่ม unittest สำหรับ configured index paths, toolset policy matching, cache prefix deletion, และ markdown section parsing.
- **ผลลัพธ์:** ลด regression ของ logic indexing, policy filtering, cache invalidation, และ skill parsing.
