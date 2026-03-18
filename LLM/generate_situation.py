import json
import random
import time
import google.generativeai as genai
import os
from dotenv import load_dotenv

# ==========================================
# 1. CẤU HÌNH API GEMINI
# ==========================================
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash') 

# ==========================================
# 2. TẠO TÌNH HUỐNG (Hệ tọa độ OXZ mới)
# ==========================================
# =====================================================================
# 1. NGUY HIỂM CAO (Cần phanh gấp, né gấp - Đe dọa tính mạng/chấn thương)
# =====================================================================
nguy_hiem_cao = [
    # Nhóm địa hình sụt lún, vấp ngã
    "ổ gà", "ổ voi", "nắp cống hở", "hố ga mất nắp", "bậc tam cấp đi xuống", "rãnh nước sâu", "vũng nước sâu",
    
    # Nhóm công trình, vật liệu sắc nhọn
    "rào chắn công trình", "cốt thép nhô lên", "đống xà bần", "gạch đá ngổn ngang", "kính vỡ", "hàng rào rào thép gai",
    
    # Nhóm chướng ngại vật trên không (nguy hiểm vùng đầu)
    "dây điện sà xuống thấp", "cành cây gãy", "bảng hiệu sắt sắc bén",
    
    # Nhóm nhiệt độ, động vật rủi ro
    "bếp than tổ ong đang cháy", "chó thả rông", 
    
    # Nhóm phương tiện động
    "xe tải đang lùi", "xe máy đi ngược chiều trên vỉa hè", "ô tô đang rẽ"
]

# =====================================================================
# 2. NGUY HIỂM THẤP / TRUNG BÌNH (Chỉ cần lách tránh, không đe dọa ngay)
# =====================================================================
nguy_hiem_thap = [
    # Nhóm lấn chiếm vỉa hè (Đặc sản Việt Nam)
    "xe máy đỗ vỉa hè", "xe đạp đỗ", "bàn ghế quán nước", "ghế nhựa", "bàn nhựa", 
    "xe đẩy bán hàng rong", "tủ kính bán bánh mì", "bảng hiệu quảng cáo đứng", "mái hiên bạt che thấp",
    
    # Nhóm hạ tầng đô thị
    "cột điện", "cột đèn chiếu sáng", "tủ điện vỉa hè", "biển báo giao thông", "cột nước cứu hỏa",
    "thùng rác công cộng", "xe đẩy thu gom rác", "chậu cây cảnh", "bồn cây xây gạch",
    
    # Nhóm con người & động vật hiền lành
    "người đi bộ", "đám đông đứng chờ", "trẻ em đang chơi", "chó mèo nằm ngủ",
    
    # Nhóm địa hình nhẹ
    "vũng nước nông", "bậc tam cấp đi lên", "gờ giảm tốc", "nắp cống lồi"
]

SYSTEM_PROMPT = "Bạn là trợ lý dẫn đường khẩn cấp cho người khiếm thị. Trả lời dứt khoát dưới 20 chữ."
output_file = "llama3_dataset_gemini_toado.jsonl"
so_luong_tinh_huong = 1000

print(f"Bắt đầu nhờ Gemini xử lý tọa độ mới...")

with open(output_file, "w", encoding="utf-8") as f:
    for i in range(so_luong_tinh_huong):
        so_luong_vat = random.randint(1, 3)
        danh_sach_vat_the = []
        
        for _ in range(so_luong_vat):
            vat = random.choice(random.choice([nguy_hiem_cao, nguy_hiem_thap]))
            
            # Sinh khoảng cách trực diện (Z) từ 0.5m đến 3.0m
            truc_dien = round(random.uniform(0.5, 3.0), 1)
            
            # Sinh độ lệch ngang (X) từ -1.5m (Trái) đến +1.5m (Phải)
            lech_ngang_so = round(random.uniform(-1.5, 1.5), 1)
            
            # Định dạng thành chuỗi có dấu + hoặc - y hệt YOLO
            lech_ngang_str = f"+{lech_ngang_so}" if lech_ngang_so > 0 else f"{lech_ngang_so}"
            if lech_ngang_so == 0.0: lech_ngang_str = "0.0"
            
            danh_sach_vat_the.append({
                "vat_the": vat, 
                "truc_dien_m": truc_dien, 
                "lech_ngang_m": lech_ngang_str
            })
        
        yolo_json = json.dumps(danh_sach_vat_the, ensure_ascii=False)
        
        # ==========================================
        # 3. PROMPT ĐỊNH TUYẾN TỌA ĐỘ (CỰC KỲ QUAN TRỌNG)
        # ==========================================
        prompt_cho_gemini = f"""
        Hệ thống camera gửi về mảng JSON các vật cản:
        {yolo_json}
        
        GIẢI THÍCH HỆ TỌA ĐỘ:
        - "truc_dien_m": Khoảng cách tính bằng mét tiến thẳng về phía trước.
        - "lech_ngang_m": Độ lệch sang hai bên. Dấu "+" là bên PHẢI, dấu "-" là bên TRÁI. 
        - HÀNH LANG CHÍNH DIỆN: Nếu lech_ngang_m nằm trong khoảng [-0.3 đến +0.3], vật đó đang CHẮN NGAY TRƯỚC MẶT.
        
        Nhiệm vụ: Đưa ra MỘT câu chỉ dẫn khẩn cấp bằng tiếng Việt (dưới 20 chữ) cho người khiếm thị.
        
        LUẬT BẮT BUỘC:
        1. NẾU BỊ CHẶN CHÍNH DIỆN (có vật nguy hiểm dưới 2m và lech_ngang_m từ -0.3 đến +0.3): BẮT BUỘC phải khuyên "Lách sang [hướng an toàn]" hoặc "Dừng lại".
        2. NẾU CHÍNH DIỆN TRỐNG (các vật cản đều có lech_ngang_m < -0.4 hoặc > +0.4): Khuyên người dùng "Cứ đi thẳng" và chỉ cảnh báo nhẹ vật ở hai bên.
        3. Tuyệt đối không đọc các con số tọa độ (+0.5, -1.2) cho người dùng nghe. Chỉ dùng chữ "Bên trái", "Bên phải", "Phía trước".
        """
        
        try:
            response = model.generate_content(prompt_cho_gemini)
            assistant_reply = response.text.strip().replace('\n', ' ')
            
            mau_du_lieu = {
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": yolo_json},
                    {"role": "assistant", "content": assistant_reply}
                ]
            }
            
            f.write(json.dumps(mau_du_lieu, ensure_ascii=False) + "\n")
            
            print(f"[{i+1}] Dữ liệu YOLO: {yolo_json}")
            print(f"    => AI Dẫn đường: {assistant_reply}\n")
            
            time.sleep(2)
            
        except Exception as e:
            print(f"Lỗi: {e}")

print("Đã tạo xong dữ liệu hệ tọa độ mới!")