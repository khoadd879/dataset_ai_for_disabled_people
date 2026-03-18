import json
import random

nguy_hiem_cao = ["ổ gà", "nắp cống hở", "bậc tam cấp đi xuống", "vũng nước sâu", "xe tải đang lùi"]
nguy_hiem_thap = ["xe máy đỗ", "người đi bộ", "thùng rác", "ghế nhựa", "cột điện"]
huong_list = ["10 giờ", "11 giờ", "12 giờ", "1 giờ", "2 giờ"]
khoang_cach_list = [0.5, 1.0, 1.5, 2.0, 2.5]

danh_sach_tinh_huong = []

# Tạo 500 tình huống ngẫu nhiên
for _ in range(500):
    so_luong_vat = random.randint(1, 3) 
    tinh_huong = []
    huong_da_dung = [] 
    
    for _ in range(so_luong_vat):
        vat = random.choice(random.choice([nguy_hiem_cao, nguy_hiem_thap]))
        huong = random.choice([h for h in huong_list if h not in huong_da_dung])
        huong_da_dung.append(huong)
        khoang_cach = random.choice(khoang_cach_list)
        
        tinh_huong.append({"vat_the": vat, "huong": huong, "khoang_cach_m": khoang_cach})
    
    danh_sach_tinh_huong.append(tinh_huong)

# Lưu lại thành file JSON thô
with open("tinh_huong_tho.json", "w", encoding="utf-8") as f:
    json.dump(danh_sach_tinh_huong, f, ensure_ascii=False, indent=2)

print("Đã tạo xong 500 tình huống thô!")