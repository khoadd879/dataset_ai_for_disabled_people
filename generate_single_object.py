import json
import random

# 1. Khai báo các biến ngẫu nhiên (Theo hệ thống Mặt đồng hồ)
vat_can_list = ["xe máy", "ổ gà", "cột điện", "người đi bộ", "bậc tam cấp", "thùng rác"]
khoang_cach_list = [0.5, 1.0, 1.5, 2.0, 3.0]

# Hướng quy ước: 12h (Chính diện), 10h-11h (Bên trái), 1h-2h (Bên phải)
huong_list = ["10 giờ", "11 giờ", "12 giờ", "1 giờ", "2 giờ"]

# Câu lệnh hệ thống (Đạo diễn) ghim cố định
SYSTEM_PROMPT = "Bạn là trợ lý dẫn đường khẩn cấp cho người khiếm thị. Trả lời dứt khoát dưới 15 chữ. Dùng hướng đồng hồ để định vị."

def tao_cau_tra_loi_mau(vat_can, huong, khoang_cach):
    """Hàm logic để tạo ra 'Đáp án' thông minh cho Llama 3 học"""
    
    # TRƯỜNG HỢP 1: Cực kỳ nguy hiểm (Ngay sát trước mặt)
    if khoang_cach <= 1.0 and huong in ["11 giờ", "12 giờ", "1 giờ"]:
        return f"Nguy hiểm! {vat_can} ngay trước mặt. Dừng lại ngay."
    
    # TRƯỜNG HỢP 2: Vật cản nằm bên TRÁI (10h, 11h) -> Khuyên lách sang PHẢI
    if huong in ["10 giờ", "11 giờ"]:
        return f"Có {vat_can} hướng {huong}. Hãy đi hơi lách sang phải."
    
    # TRƯỜNG HỢP 3: Vật cản nằm bên PHẢI (1h, 2h) -> Khuyên lách sang TRÁI
    elif huong in ["1 giờ", "2 giờ"]:
        return f"Có {vat_can} hướng {huong}. Hãy đi hơi lách sang trái."
    
    # TRƯỜNG HỢP 4: Ở xa nhưng nằm ngay chính giữa (12h)
    else:
        return f"Chú ý {vat_can} hướng 12 giờ, cách {khoang_cach} mét. Chuẩn bị né."

# 2. Bắt đầu sinh 500 mẫu dữ liệu
dataset = []
for _ in range(500):
    vat_can = random.choice(vat_can_list)
    huong = random.choice(huong_list)
    khoang_cach = random.choice(khoang_cach_list)
    
    # Giả lập cục JSON xịn xò do YOLOv8 gửi lên (có hướng đồng hồ)
    yolo_json = f'[{{"vat_the": "{vat_can}", "huong": "{huong}", "khoang_cach_m": {khoang_cach}}}]'
    
    # Lấy câu trả lời mẫu
    assistant_reply = tao_cau_tra_loi_mau(vat_can, huong, khoang_cach)
    
    # Đóng gói thành chuẩn 3 Role
    mau_du_lieu = {
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": yolo_json},
            {"role": "assistant", "content": assistant_reply}
        ]
    }
    dataset.append(mau_du_lieu)

# 3. Lưu thành file .jsonl
with open("llama3_dataset_clockface.jsonl", "w", encoding="utf-8") as f:
    for item in dataset:
        f.write(json.dumps(item, ensure_ascii=False) + "\n")

print("Đã tạo thành công file 'llama3_dataset_clockface.jsonl' với 500 tình huống!")