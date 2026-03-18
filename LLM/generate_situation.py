import json
import random
import time
import google.generativeai as genai

# ==========================================
# 1. CẤU HÌNH API GEMINI
# Lấy key miễn phí tại: https://aistudio.google.com/app/apikey
# ==========================================
GOOGLE_API_KEY = "ĐIỀN_API_KEY_CỦA_BẠN_VÀO_ĐÂY"
genai.configure(api_key=GOOGLE_API_KEY)

# Dùng bản Flash cho nhanh và miễn phí
model = genai.GenerativeModel('gemini-1.5-flash') 

# ==========================================
# 2. TẠO TÌNH HUỐNG (Từ code cũ của bạn)
# ==========================================
nguy_hiem_cao = ["ổ gà", "nắp cống hở", "bậc tam cấp đi xuống", "vũng nước sâu", "xe tải đang lùi"]
nguy_hiem_thap = ["xe máy đỗ", "người đi bộ", "thùng rác", "ghế nhựa", "cột điện"]
huong_list = ["10 giờ", "11 giờ", "12 giờ", "1 giờ", "2 giờ"]
khoang_cach_list = [0.5, 0.8, 1.2, 1.5, 2.0, 2.5]

SYSTEM_PROMPT = "Bạn là trợ lý dẫn đường khẩn cấp cho người khiếm thị. Trả lời dứt khoát dưới 20 chữ."

# Chuẩn bị file xuất ra
output_file = "llama3_dataset_gemini.jsonl"
so_luong_tinh_huong = 100 # Chạy thử 100 tình huống trước

print(f"Bắt đầu nhờ Gemini xử lý {so_luong_tinh_huong} tình huống...")

with open(output_file, "w", encoding="utf-8") as f:
    for i in range(so_luong_tinh_huong):
        # --- Sinh JSON tình huống ngẫu nhiên ---
        so_luong_vat = random.randint(1, 3)
        danh_sach_vat_the = []
        huong_da_dung = []
        
        for _ in range(so_luong_vat):
            vat = random.choice(random.choice([nguy_hiem_cao, nguy_hiem_thap]))
            huong = random.choice([h for h in huong_list if h not in huong_da_dung])
            huong_da_dung.append(huong)
            khoang_cach = random.choice(khoang_cach_list)
            
            danh_sach_vat_the.append({"vat_the": vat, "huong": huong, "khoang_cach_m": khoang_cach})
        
        yolo_json = json.dumps(danh_sach_vat_the, ensure_ascii=False)
        
        # --- Ép Gemini đóng vai chuyên gia ---
        prompt_cho_gemini = f"""
        Bạn là một chuyên gia huấn luyện chó dẫn đường và hướng dẫn viên cho người khiếm thị.
        Hệ thống camera vừa gửi về mảng JSON chứa các vật cản phía trước mặt người dùng:
        {yolo_json}
        
        Nhiệm vụ: Đưa ra MỘT câu chỉ dẫn bằng tiếng Việt thật ngắn gọn (dưới 20 chữ), dễ nghe để phát qua tai nghe.
        Quy tắc:
        1. Nếu có vật nguy hiểm (ổ gà, nắp cống...) cách dưới 1.5m ở hướng 12 giờ: Yêu cầu dừng lại hoặc lách sang hướng trống.
        2. Nếu hướng 12 giờ trống, nhưng có vật cản ở hai bên (10h, 2h): Báo cáo nhanh và nhắc cứ đi thẳng.
        3. Tuyệt đối KHÔNG giải thích, KHÔNG chào hỏi. Chỉ nhả ra câu lệnh hành động.
        """
        
        try:
            # Gọi API
            response = model.generate_content(prompt_cho_gemini)
            assistant_reply = response.text.strip().replace('\n', ' ')
            
            # Đóng gói chuẩn ChatML cho Llama 3
            mau_du_lieu = {
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": yolo_json},
                    {"role": "assistant", "content": assistant_reply}
                ]
            }
            
            # Ghi vào file
            f.write(json.dumps(mau_du_lieu, ensure_ascii=False) + "\n")
            
            print(f"[{i+1}/{so_luong_tinh_huong}] Input: {yolo_json}")
            print(f"       => Gemini: {assistant_reply}\n")
            
            # Nghỉ 2 giây để không bị API chặn (Rate Limit của gói Free)
            time.sleep(2)
            
        except Exception as e:
            print(f"Lỗi ở tình huống {i+1}: {e}")

print(f"HOÀN TẤT! Dữ liệu siêu xịn đã được lưu tại: {output_file}")