import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from datetime import datetime
import psycopg2
from psycopg2 import sql

class KiemTraNangLuong:
    def __init__(self, root):
        self.root = root
        self.root.iconbitmap('python_94570.ico')
        self.root.title("Quản lý tiêu thụ điện năng của gia đình")
        self.root.resizable(False, False)

        # Danh sách các cảnh báo
        self.canhbao_list = []
        # Ngưỡng cảnh báo
        self.nguongcanhbao = {"Điện": 100, "Nước": 50, "Khí Gas": 30}
        # Giá
        self.gia_tien = {"Điện": 3000, "Nước": 5000, "Khí Gas": 20000}
        # Nơi chứa giá trị vừa nhập
        self.recent_dien = 0
        self.recent_nuoc = 0
        self.recent_gas = 0
        self.recent_date = ""  # Biến lưu ngày tháng nhập vào

        # Biến lưu trữ thông tin CSDL
        self.db_name = tk.StringVar()
        self.user = tk.StringVar(value='postgres')
        self.password = tk.StringVar()
        self.host = tk.StringVar(value='localhost')
        self.port = tk.StringVar(value='5432')
        self.table_name = tk.StringVar()

        # Giao diện
        self.giao_dien()
        self.thanh_menu()

# Tạo phần nhập thông tin tiêu thụ
        # Tạo thêm các nút sửa, xóa và tìm kiếm trong phần giao diện
   
    def giao_dien(self):
        # Xóa tất cả widget hiện tại
        for widget in self.root.grid_slaves():
            widget.grid_forget()

        # Frame cho phần nhập thời gian
        frame_thoigian = ttk.LabelFrame(self.root, text="Thời gian", padding=(10, 5))
        frame_thoigian.grid(row=0, column=0, padx=10, pady=10, columnspan=2)

        # Tạo Label và Entry cho ngày tháng
        label_date = ttk.Label(frame_thoigian, text="Ngày tiêu thụ (dd/mm/yyyy):")
        label_date.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.entry_date = ttk.Entry(frame_thoigian)
        self.entry_date.grid(row=0, column=1, padx=10, pady=5)
        self.entry_date.focus()

        # Frame cho phần nhập liệu tiêu thụ
        frame_nhap = ttk.LabelFrame(self.root, text="Nhập liệu tiêu thụ", padding=(10, 5))
        frame_nhap.grid(row=1, column=0, padx=10, pady=10, columnspan=2)

        # Tạo Label trong frame nhập
        label_id = ttk.Label(frame_nhap, text="ID (nếu có):")
        label_id.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.entry_id = ttk.Entry(frame_nhap)
        self.entry_id.grid(row=0, column=1, padx=10, pady=5)

        label_dien = ttk.Label(frame_nhap, text="Điện tiêu thụ (kWh):")
        label_dien.grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.entry_dien = ttk.Entry(frame_nhap)
        self.entry_dien.grid(row=1, column=1, padx=10, pady=5)

        label_nuoc = ttk.Label(frame_nhap, text="Nước tiêu thụ (m³):")
        label_nuoc.grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.entry_nuoc = ttk.Entry(frame_nhap)
        self.entry_nuoc.grid(row=2, column=1, padx=10, pady=5)

        label_gas = ttk.Label(frame_nhap, text="Khí Gas tiêu thụ (m³):")
        label_gas.grid(row=3, column=0, padx=10, pady=5, sticky="w")
        self.entry_gas = ttk.Entry(frame_nhap)
        self.entry_gas.grid(row=3, column=1, padx=10, pady=5)

        # Khung chứa các nút chức năng
        frame_ketqua = ttk.LabelFrame(self.root, text="Thao tác với thông tin", padding=(10, 5))
        frame_ketqua.grid(row=2, column=0, padx=10, pady=10, columnspan=2, sticky='ew' )

        # Nút "Lưu thông tin" nằm ở giữa, trải dài cả chiều ngang
        submit_button = ttk.Button(frame_ketqua, text="Lưu thông tin", command=self.nhap_data)
        submit_button.grid(row=1, column=0, columnspan=3, pady=10, sticky='ew')

        # Ba nút khác nằm ở hàng thứ 2, bố trí đều
        update_button = ttk.Button(frame_ketqua, text="Sửa thông tin", command=self.sua_data)
        update_button.grid(row=2, column=0, pady=5, padx=5)

        search_button = ttk.Button(frame_ketqua, text="Tìm kiếm", command=self.tim_kiem)
        search_button.grid(row=2, column=1, pady=5, padx=5)

        delete_button = ttk.Button(frame_ketqua, text="Xóa thông tin", command=self.xoa_data)
        delete_button.grid(row=2, column=2, pady=5, padx=5)
    
    
    def sua_data(self):
        try:
            id_ = self.entry_id.get().strip()
            dien = self.entry_dien.get().strip()
            nuoc = self.entry_nuoc.get().strip()
            gas = self.entry_gas.get().strip()

            # Kiểm tra nếu ID và các trường thông tin không rỗng
            if not id_ or not dien or not nuoc or not gas:
                messagebox.showerror("Lỗi", "Vui lòng nhập đầy đủ ID và các trường cần sửa!")
                return

            # Tạo câu lệnh UPDATE
            update_query = sql.SQL("""
                UPDATE {} 
                SET dien = %s, nuoc = %s, gas = %s 
                WHERE id = %s
            """).format(sql.Identifier(self.table_name.get()))

            # Thực hiện cập nhật
            self.cur.execute(update_query, (float(dien), float(nuoc), float(gas), int(id_)))

            # Kiểm tra số dòng bị ảnh hưởng
            if self.cur.rowcount == 0:
                messagebox.showwarning("Thông báo", "Không tìm thấy ID trong cơ sở dữ liệu!")
            else:
                self.conn.commit()
                messagebox.showinfo("Thông báo", "Sửa thông tin thành công!")
                self.entry_date.delete(0, 'end')
                self.entry_id.delete(0, 'end')
                self.entry_dien.delete(0, 'end')
                self.entry_nuoc.delete(0, 'end')
                self.entry_gas.delete(0, 'end')
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể sửa thông tin: {e}")


    # Hàm xóa thông tin dựa trên id hoặc ngày tiêu thụ
    def xoa_data(self):
        try:
            id_ = self.entry_id.get().strip()
            ngay_thang = self.entry_date.get().strip()

            # Kiểm tra nếu không nhập cả ID lẫn ngày
            if not id_ and not ngay_thang:
                messagebox.showerror("Lỗi", "Vui lòng nhập ID hoặc ngày tiêu thụ để xóa!")
                return

            # Tạo câu lệnh DELETE dựa trên id hoặc ngày tiêu thụ
            if id_ and ngay_thang:
                delete_query = sql.SQL("DELETE FROM {} WHERE id = %s AND ngay = %s").format(sql.Identifier(self.table_name.get()))
                self.cur.execute(delete_query, (int(id_), ngay_thang))
                self.conn.commit()
                messagebox.showinfo("Thông báo", "Xóa thông tin thành công!")
            else:
                messagebox.showerror("Lỗi", "Vui lòng nhập cả ID và ngày tiêu thụ để xóa!")
            
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể xóa thông tin: {e}")

    # Hàm tìm kiếm dựa trên id hoặc ngày tiêu thụ
    def tim_kiem(self):
        try:
            id_ = self.entry_id.get().strip()
            ngay_thang = self.entry_date.get().strip()

            # Kiểm tra nếu không nhập cả ID lẫn ngày
            if not id_ and not ngay_thang:
                messagebox.showerror("Lỗi", "Vui lòng nhập ID hoặc ngày tiêu thụ để tìm kiếm!")
                return

            # Tạo câu lệnh SELECT dựa trên id hoặc ngày tiêu thụ
            if id_:
                search_query = sql.SQL("SELECT * FROM {} WHERE id = %s").format(sql.Identifier(self.table_name.get()))
                self.cur.execute(search_query, (int(id_),))
            else:
                search_query = sql.SQL("SELECT * FROM {} WHERE ngay = %s").format(sql.Identifier(self.table_name.get()))
                self.cur.execute(search_query, (ngay_thang,))

            # Lấy tất cả các bản ghi phù hợp
            rows = self.cur.fetchall()

            # Kiểm tra nếu có kết quả
            if rows:
                result = ""
                for row in rows:
                    result += (f"ID: {row[0]}\n"
                            f"Ngày: {row[1]}\n"
                            f"Điện: {row[2]} kWh\n"
                            f"Nước: {row[3]} m³\n"
                            f"Khí Gas: {row[4]} m³\n"
                            "------------------------\n")
                
                # Hiển thị tất cả kết quả trong messagebox
                messagebox.showinfo("Thông tin tìm thấy", result)
            else:
                messagebox.showinfo("Kết quả", "Không tìm thấy dữ liệu phù hợp!")

        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể tìm kiếm thông tin: {e}")




    # Xử lý khi nhập dữ liệu tiêu thụ
    def nhap_data(self):
        try:
            ngay_thang = self.entry_date.get().strip()
            dien = self.entry_dien.get().strip()
            nuoc = self.entry_nuoc.get().strip()
            gas = self.entry_gas.get().strip()
            if not ngay_thang or not dien or not nuoc or not gas :
                messagebox.showerror("Lỗi","Vui lòng nhập đầy đủ các trường thông tin!")
                return
            
            ngay_thang = self.entry_date.get()
            datetime.strptime(ngay_thang,'%d/%m/%Y')  # Kiểm tra định dạng ngày
            dien = float(self.entry_dien.get())
            nuoc = float(self.entry_nuoc.get())
            gas = float(self.entry_gas.get())

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
                 
            self.recent_date = ngay_thang
            self.recent_dien = dien
            self.recent_nuoc = nuoc
            self.recent_gas = gas

            self.entry_dien.delete(0, tk.END)
            self.entry_nuoc.delete(0, tk.END)
            self.entry_gas.delete(0, tk.END)
            self.entry_date.delete(0, tk.END)


        except ValueError:
            messagebox.showerror("Lỗi", "Vui lòng nhập giá trị số hợp lệ và đúng định dạng ngày!")
            return
        #lưu trữ vào cơ sỡ dữ liệu 
        try:
            insert_query = sql.SQL("INSERT INTO {} (ngay,dien,nuoc,gas) VALUES (%s, %s, %s, %s)").format(sql.Identifier(self.table_name.get()))
            data_to_insert = (self.recent_date, self.recent_dien, self.recent_nuoc, self.recent_gas)  # Sử dụng các biến đã lưu trữ
            self.cur.execute(insert_query, data_to_insert)
            self.conn.commit()
            messagebox.showinfo("Thông báo", "Dữ liệu được lưu thành công!")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Dữ liệu không được lưu thành công!: {e}")
            

    # Hiển thị giá tiền
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

    # Hiển thị thông số tiêu thụ
    def show_thongso(self):
        try:
            # Truy vấn tất cả dữ liệu từ bảng
            query = sql.SQL("""
            SELECT * FROM {} 
            ORDER BY ngay DESC 
            LIMIT 5
            """).format(sql.Identifier(self.table_name.get()))
            self.cur.execute(query)
            
            # Lấy tất cả các dòng từ kết quả truy vấn
            rows = self.cur.fetchall()

            # Nếu bảng không có dữ liệu
            if not rows:
                messagebox.showinfo("Thông báo", "Không có dữ liệu trong bảng!")
                return

            # Xây dựng chuỗi để hiển thị tất cả dữ liệu
            result = ""
            for row in rows:
                result += (f"Mã ID: {row[0]}\n"
                        f"Ngày: {row[1]}\n"
                        f"Điện: {row[2]} kWh\n"
                        f"Nước: {row[3]} m³\n"
                        f"Khí Gas: {row[4]} m³\n"
                        "------------------------\n")
            
            # Hiển thị tất cả các thông số trong messagebox
            messagebox.showinfo("Thông số tiêu thụ", result)

        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể tải dữ liệu: {e}")
        

# Tạo khung nhập thông tin CSDL
    def create_widgets(self):
        # Xóa các widget hiện tại (nếu có)
        for widget in self.root.grid_slaves():
            widget.grid_forget()

        # Tạo frame cho phần nhập thông tin CSDL
        connection_frame = ttk.LabelFrame(self.root, text="Nhập thông tin CSDL", padding=(10, 5))
        connection_frame.grid(row=0, column=0, padx=10, pady=10, columnspan=2)

        # Nhập thông tin CSDL
        tk.Label(connection_frame, text="DB Name:").grid(row=0, column=0, padx=5, pady=5)
        tk.Entry(connection_frame, textvariable=self.db_name).grid(row=0, column=1, padx=5, pady=5)

        tk.Label(connection_frame, text="User:").grid(row=1, column=0, padx=5, pady=5)
        tk.Entry(connection_frame, textvariable=self.user).grid(row=1, column=1, padx=5, pady=5)

        tk.Label(connection_frame, text="Password:").grid(row=2, column=0, padx=5, pady=5)
        tk.Entry(connection_frame, textvariable=self.password, show="*").grid(row=2, column=1, padx=5, pady=5)

        tk.Label(connection_frame, text="Host:").grid(row=3, column=0, padx=5, pady=5)
        tk.Entry(connection_frame, textvariable=self.host).grid(row=3, column=1, padx=5, pady=5)

        tk.Label(connection_frame, text="Port:").grid(row=4, column=0, padx=5, pady=5)
        tk.Entry(connection_frame, textvariable=self.port).grid(row=4, column=1, padx=5, pady=5)

        tk.Button(connection_frame, text="Connect", command=self.connect_db).grid(row=5, columnspan=2, pady=10)

        # Tạo frame chứa khung nhập Table Name và nút Load Data
        query_frame = ttk.LabelFrame(self.root, text="Nhập tên bảng", padding=(10, 5))
        query_frame.grid(row=1, column=0, padx=10, pady=10, columnspan=2)

        tk.Label(query_frame, text="Table Name:").grid(row=0, column=0, padx=5, pady=5)
        tk.Entry(query_frame, textvariable=self.table_name).grid(row=0, column=1, padx=5, pady=5)

        tk.Button(query_frame, text="Load Data", command=self.load_data).grid(row=1, columnspan=2, pady=10)

        self.data_display = tk.Text(self.root, height=10, width=50)
        self.data_display.grid(row=2, column=0, padx=10, pady=10, columnspan=2)

# Kết nối đến cơ sở dữ liệu PostgreSQL
    def connect_db(self):
        try:
            db_name = self.db_name.get().strip()
            user = self.user.get().strip()
            password = self.password.get().strip()
            host = self.host.get().strip()
            port = self.port.get().strip()
            

            # Kiểm tra nếu bất kỳ trường nào bị bỏ trống
            if not db_name or not user or not password or not host or not port :
                messagebox.showerror("Lỗi", "Vui lòng nhập đầy đủ các trường thông tin khi kết nối CSDL!")
                return
            
            self.conn= psycopg2.connect(
                dbname=self.db_name.get(),
                user=self.user.get(),
                password=self.password.get(),
                host=self.host.get(),
                port=self.port.get()
            )
            self.conn.autocommit = True
            self.cur = self.conn.cursor()
            messagebox.showinfo("Kết nối", "Kết nối đến cơ sở dữ liệu thành công!")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Kết nối đến cơ sở dữ liệu thất bại: {e}")
            
    def load_data(self):
        try:
            table_name = self.table_name.get().strip()
            if not table_name :
                messagebox.showerror("Lỗi", "Vui lòng nhập tên bảng dữ liệu!")
                return
            
            query = sql.SQL("SELECT * FROM {}").format(sql.Identifier(self.table_name.get()))
            
            self.cur.execute(query)
            rows = self.cur.fetchall()
            self.data_display.delete(1.0, tk.END)
            for row in rows:
                self.data_display.insert(tk.END, f"{row}\n")
        except Exception as e:
            messagebox.showerror("Thất bại", f"Quá trình tải dữ liệu lên thất bại !: {e}")

# Tạo menu chính cho ứng dụng
    def thanh_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # Menu Cài đặt
        cài_đặt_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Cài đặt", menu=cài_đặt_menu)
        cài_đặt_menu.add_command(label="Kết nối CSDL", command=self.create_widgets)

        # Menu Thống kê
        thongke_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Trang chủ", menu=thongke_menu)
        thongke_menu.add_command(label="Nhập thông số", command=self.giao_dien)  
        thongke_menu.add_command(label="Xem giá tiền vừa nhập", command=self.show_sotien)
        thongke_menu.add_command(label="Xem thông số tiêu thụ ", command=self.show_thongso)

        # Menu thoát
        menubar.add_command(label="Thoát", command=self.root.quit)
        

if __name__ == "__main__":
    root = tk.Tk()
    app = KiemTraNangLuong(root)
    root.mainloop()
