import tkinter as tk
from tkinter import ttk 
from tkinter import messagebox

class kiemtranangluong:
    def __init__(self, root):
        self.root = root
        self.root.title("Quản lý tiêu thụ điện năng của gia đình")
        self.root.geometry("350x250")
        self.root.resizable(False, False)  # Lệnh dùng để khóa phóng lớn 
        
        #danh sach cac canh bao
        self.canhbao_list = []
        # Ngưỡng cảnh báo 
        self.nguongcanhbao = {"Điện": 100, "Nước": 50, "Khí Gas": 30}
        # Giá 
        self.gia_tien = {"Điện": 3000, "Nước": 5000, "Khí Gas": 20000} 
        # Nơi chứa giá trị vừa nhập
        self.recent_dien = 0
        self.recent_nuoc = 0
        self.recent_gas = 0

        # Giao diện
        self.giao_dien()
        self.thanh_menu()

    def nhap_data(self):
        try:
            dien = float(self.entry_dien.get())
            nuoc = float(self.entry_nuoc.get())
            gas = float(self.entry_gas.get())

            # Lưu các giá trị vừa nhập gần nhất 
            self.recent_dien = dien
            self.recent_nuoc = nuoc
            self.recent_gas = gas

            # Kiểm tra các lượng tiêu thụ vượt mức
            if dien > self.nguongcanhbao["Điện"]:
                canhbao_message = "Lượng điện tiêu thụ quá mức!"
                self.canhbao_list.append(canhbao_message)
                messagebox.showwarning("Cảnh báo", canhbao_message)
            if nuoc > self.nguongcanhbao["Nước"]:
                canhbao_message = "Lượng nước tiêu thụ quá mức!"
                self.canhbao_list.append(canhbao_message)
                messagebox.showwarning("Cảnh báo", canhbao_message)
            if gas > self.nguongcanhbao["Khí Gas"]:
                canhbao_message = "Lượng khí gas tiêu thụ quá mức!"
                self.canhbao_list.append(canhbao_message)
                messagebox.showwarning("Cảnh báo", canhbao_message)

            # Xóa các ô sau khi nhấn nút kiểm tra 
            self.entry_dien.delete(0, tk.END)
            self.entry_nuoc.delete(0, tk.END)
            self.entry_gas.delete(0, tk.END)

            messagebox.showinfo("Thông báo", "Dữ liệu được lưu thành công!")

        except ValueError:
            messagebox.showerror("Lỗi", "Vui lòng nhập giá trị số hợp lệ và không để trống!")

    def show_sotien(self):
        tien_dien = self.recent_dien * self.gia_tien["Điện"]
        tien_nuoc = self.recent_nuoc * self.gia_tien["Nước"]
        tien_gas = self.recent_gas * self.gia_tien["Khí Gas"]
        tong_cong = tien_dien + tien_nuoc + tien_gas
        hienthi1 = (f"Tiền điện: {tien_dien} VND\n"
                    f"Tiền nước: {tien_nuoc} VND\n"
                    f"Tiền khí gas: {tien_gas} VND\n"
                    f"Tổng tiền: {tong_cong} VND")
        messagebox.showinfo("Giá tiền:", hienthi1)

    def show_thongso(self):
        hienthi2 = (f"Điện: {self.recent_dien} kWh\n"
                    f"Nước: {self.recent_nuoc} m³\n"
                    f"Khí Gas: {self.recent_gas} m³")
        messagebox.showinfo("Thông số tiêu thụ", hienthi2)

    def giao_dien(self):
        frame_nhap = ttk.LabelFrame(self.root, text="Nhập liệu tiêu thụ", padding=(10, 5))
        frame_nhap.grid(row=0, column=0, padx=10, pady=10, columnspan=2)

        # Tạo Label trong frame nhập
        label_dien = ttk.Label(frame_nhap, text="Điện tiêu thụ (kWh):")
        label_dien.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.entry_dien = ttk.Entry(frame_nhap)
        self.entry_dien.grid(row=0, column=1, padx=10, pady=5)
        self.entry_dien.focus()

        label_nuoc = ttk.Label(frame_nhap, text="Nước tiêu thụ (m³):")
        label_nuoc.grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.entry_nuoc = ttk.Entry(frame_nhap)
        self.entry_nuoc.grid(row=1, column=1, padx=10, pady=5)

        label_gas = ttk.Label(frame_nhap, text="Khí Gas tiêu thụ (m³):")
        label_gas.grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.entry_gas = ttk.Entry(frame_nhap)
        self.entry_gas.grid(row=2, column=1, padx=10, pady=5)

        # Button kết quả
        frame_ketqua = ttk.LabelFrame(self.root, text="Kiểm tra thông tin", padding=(10, 5))
        frame_ketqua.grid(row=1, column=0, padx=10, pady=10, columnspan=2, sticky='w')
      

        submit_button = ttk.Button(frame_ketqua, text="Kiểm tra", command=self.nhap_data)
        submit_button.grid(row=1, column=0, columnspan=2, pady=10)
    #tạo menubar
    def thanh_menu(self):
        menu_bar = tk.Menu(self.root)
        self.root.config(menu=menu_bar)

        # Thêm menubar
        tongtien_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Tổng tiền", menu=tongtien_menu)
        tongtien_menu.add_command(label="Hiển thị tổng tiền", command=self.show_sotien)

        thongso_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Thông số", menu=thongso_menu)
        thongso_menu.add_command(label="Hiển thị thông số", command=self.show_thongso)


if __name__ == "__main__":
    root = tk.Tk()  
    app = kiemtranangluong(root)  
    root.mainloop()  
