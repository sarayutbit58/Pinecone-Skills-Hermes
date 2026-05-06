# งานแก้ไขจากการตรวจสอบฐานโค้ด

วันที่อัปเดต: 2026-05-06

## 1) งานแก้ไขข้อความพิมพ์ผิด/คุณภาพข้อความ (Typo/Text Quality)
- **สถานะ:** เปิดไว้เป็นงานถัดไป.
- **ปัญหา:** ประโยคใน README วลี `Hermes core untouched first` อ่านไม่เป็นธรรมชาติและสื่อความกำกวม.
- **ตำแหน่ง:** `README.md` ในหัวข้อ **Main Capabilities**.
- **งานที่เสนอ:** ปรับเป็น `Keep Hermes core untouched at first` หรือ `Keep Hermes core untouched initially` เพื่อให้สื่อความชัดเจนขึ้น.
- **ผลลัพธ์ที่คาดหวัง:** ผู้อ่านใหม่เข้าใจขอบเขตโปรเจกต์ได้ตรงขึ้น ลดความกำกวมเชิงภาษา.

## 2) งานแก้ไขบั๊ก (Bug Fix)
- **สถานะ:** แก้แล้ว.
- **ปัญหา:** ตัว indexer ใช้ path คงที่ `~/.hermes/skills` และไม่ใช้ `config.skills.paths` ทำให้ค่า config ของผู้ใช้ไม่มีผล.
- **ตำแหน่ง:** `src/indexer.py` เมธอด `sync()`.
- **สิ่งที่แก้:** เปลี่ยนให้วน index ตามทุก path ใน `config.skills.paths` พร้อม expand `~` และ dedupe path ที่ซ้ำ.
- **ผลลัพธ์ที่คาดหวัง:** ระบบ index skill ได้ถูกต้องตามค่าคอนฟิกทุก environment.

## 3) งานแก้ไขคอมเมนต์/เอกสารที่คลาดเคลื่อน (Doc/Code Drift)
- **สถานะ:** แก้แล้ว.
- **ปัญหา:** `example_config.yaml` ใช้คีย์ `pinecone.environment` แต่โค้ด `load_config()` รองรับ `cloud` และ `region` ทำให้ตัวอย่าง config ไม่ตรง implementation.
- **ตำแหน่ง:** `example_config.yaml`, `src/config.py`.
- **สิ่งที่แก้:** อัปเดตตัวอย่าง config ให้ใช้ `cloud` + `region` และเพิ่มตัวอย่าง `skills.paths`/`safety` ให้ตรงกับ field ที่โค้ดอ่านจริง.
- **ผลลัพธ์ที่คาดหวัง:** ลดการตั้งค่าผิดพลาดตอนเริ่มใช้งาน และลด issue ซ้ำจากผู้ใช้ใหม่.

## 4) งานปรับปรุงการทดสอบ (Test Improvement)
- **สถานะ:** แก้แล้วบางส่วน.
- **ปัญหา:** ก่อนหน้านี้ยังไม่มีชุดทดสอบอัตโนมัติสำหรับเส้นทางหลัก.
- **ตำแหน่ง:** โฟลเดอร์ `tests/`.
- **สิ่งที่แก้:** เพิ่ม unit tests สำหรับ `SkillIndexer.sync()` ที่ต้องเคารพ `config.skills.paths`, policy toolset matching, cache prefix deletion, autonomous prompt enrichment และ Pinecone SDK error wrapping.
- **ผลลัพธ์ที่คาดหวัง:** ลด regression เมื่อ refactor logic routing/indexing.
