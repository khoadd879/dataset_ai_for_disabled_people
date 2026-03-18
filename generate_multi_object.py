import json
import random

# 1. Phân loại mức độ nguy hiểm của vật cản (Yếu tố cốt lõi để AI biết ưu tiên)
nguy_hiem_cao = ["ổ gà", "nắp cống hở", "bậc tam cấp đi xuống", "vũng nước sâu"]
nguy_hiem_thap = ["xe máy đỗ", "người đi bộ", "thùng rác", "ghế nhựa", "cột điện"]

huong_list = ["10 giờ", "11 giờ", "12 giờ", "1 giờ", "2 giờ"]
khoang_cach_list = [0.5, 1.0, 1.5, 2.0, 2.5]

SYSTEM_PROMPT = "Bạn là trợ lý dẫn đường khẩn cấp cho người khiếm thị. Trả lời dứt khoát dưới 20 chữ. Ưu tiên tránh hố sâu/ổ gà và dừng lại nếu bị chặn đường."

def xu_ly_da_vat_the(danh_sach_vat_the):
    """Hàm logic mô phỏng tư duy của người dẫn đường để tạo đáp án chuẩn cho AI học"""
    
    # 1. Quét xem các hướng nào đang bị chặn
    co_trai = any(v["huong"] in ["10 giờ", "11 giờ"] for v in danh_sach_vat_the)
    co_phai = any(v["huong"] in ["1 giờ", "2 giờ"] for v in danh_sach_vat_the)
    co_giua = any(v["huong"] == "12 giờ" for v in danh_sach_vat_the)
    
    # 2. Tìm vật nguy hiểm nhất và vật gần nhất trong đống hỗn độn đó
    vat_nguy_hiem_nhat = None
    khoang_cach_min = 99.0
    
    for v in danh_sach_vat_the:
        if v["khoang_cach_m"] < khoang_cach_min:
            khoang_cach_min = v["khoang_cach_m"]
        if v["vat_the"] in nguy_hiem_cao:
            vat_nguy_hiem_nhat = v

    # --- BẮT ĐẦU XÉT LUẬT ƯU TIÊN ---

    # LUẬT SỐ 1: Có vật cản nguy hiểm cao (ổ gà/hố sâu) trong phạm vi gần
    if vat_nguy_hiem_nhat and vat_nguy_hiem_nhat["khoang_cach_m"] <= 1.5:
        return f"Cẩn thận! Có {vat_nguy_hiem_nhat['vat_the']} hướng {vat_nguy_hiem_nhat['huong']}. Đứng yên dùng gậy dò."

    # LUẬT SỐ 2: Quá gần (< 1m) bất kể là vật gì -> Phải phanh gấp
    if khoang_cach_min <= 1.0:
        return "Nhiều vật cản rất gần phía trước. Dừng bước ngay lập tức."

    # LUẬT SỐ 3: Bị chặn kẹp chả 2 bên (Trái + Phải đều có vật) hoặc bị chặn toàn bộ
    if (co_trai and co_phai) or (co_giua and co_trai and co_phai):
        return "Đường hẹp bị chặn hai bên. Hãy dừng lại hoặc tìm đường khác."

    # LUẬT SỐ 4: Bị chặn bên TRÁI và GIỮA -> Phải lách mạnh sang PHẢI
    if co_trai and co_giua and not co_phai:
        return "Trước mặt và bên trái có vật cản. Hãy lách hẳn sang lề phải."

    # LUẬT SỐ 5: Bị chặn bên PHẢI và GIỮA -> Phải lách mạnh sang TRÁI
    if co_phai and co_giua and not co_trai:
        return "Trước mặt và bên phải có vật cản. Hãy lách hẳn sang lề trái."
        
    # Mặc định an toàn
    return "Phía trước có vài vật cản. Hãy đi chậm và chú ý."

# 2. Bắt đầu sinh 500 mẫu dữ liệu phức tạp
dataset = []
for _ in range(500):
    # Mỗi tình huống sẽ có ngẫu nhiên 2 hoặc 3 vật thể xuất hiện
    so_luong_vat = random.randint(2, 3) 
    
    danh_sach_vat_the = []
    huong_da_dung = [] # Đảm bảo 2 vật không nằm đè lên cùng 1 hướng (ví dụ không thể có 2 vật cùng ở hướng 10 giờ)
    
    for _ in range(so_luong_vat):
        # Trộn ngẫu nhiên vật nguy hiểm cao và thấp
        loai_vat = random.choice([nguy_hiem_cao, nguy_hiem_thap])
        vat = random.choice(loai_vat)
        
        # Chọn hướng chưa bị chiếm
        huong_kha_dung = [h for h in huong_list if h not in huong_da_dung]
        huong = random.choice(huong_kha_dung)
        huong_da_dung.append(huong)
        
        khoang_cach = random.choice(khoang_cach_list)
        danh_sach_vat_the.append({"vat_the": vat, "huong": huong, "khoang_cach_m": khoang_cach})
    
    # Ép mảng Python thành chuỗi JSON y hệt như App của đồng đội sẽ gửi lên
    yolo_json = json.dumps(danh_sach_vat_the, ensure_ascii=False)
    
    # Lấy đáp án từ hàm Logic
    assistant_reply = xu_ly_da_vat_the(danh_sach_vat_the)
    
    # Đóng gói chuẩn 3 Role
    mau_du_lieu = {
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": yolo_json},
            {"role": "assistant", "content": assistant_reply}
        ]
    }
    dataset.append(mau_du_lieu)

# 3. Lưu file
with open("llama3_dataset_multi_obj.jsonl", "w", encoding="utf-8") as f:
    for item in dataset:
        f.write(json.dumps(item, ensure_ascii=False) + "\n")

print("Đã tạo thành công 500 kịch bản ĐA VẬT THỂ cực kỳ hóc búa!")