# 💻 Advanced System Monitor with Notifications, Charts, and Logging

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import psutil
import threading
import time
import csv
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class SystemMonitor:
    def __init__(self, root):
        self.root = root
        self.root.title("💻 Advanced System Monitor")
        self.root.geometry("800x600")

        # Setup data containers
        self.cpu_data = []
        self.mem_data = []
        self.disk_data = []
        self.time_stamps = []

        # Initialize UI
        self.create_widgets()

        # Start monitoring in background
        self.running = True
        threading.Thread(target=self.update_stats, daemon=True).start()

    def create_widgets(self):
        # CPU Usage
        self.cpu_label = ttk.Label(self.root, text="CPU Usage:")
        self.cpu_label.pack(pady=5)
        self.cpu_progress = ttk.Progressbar(self.root, length=500, maximum=100)
        self.cpu_progress.pack()

        # Memory Usage
        self.mem_label = ttk.Label(self.root, text="Memory Usage:")
        self.mem_label.pack(pady=5)
        self.mem_progress = ttk.Progressbar(self.root, length=500, maximum=100)
        self.mem_progress.pack()

        # Disk Usage
        self.disk_label = ttk.Label(self.root, text="Disk Usage:")
        self.disk_label.pack(pady=5)
        self.disk_progress = ttk.Progressbar(self.root, length=500, maximum=100)
        self.disk_progress.pack()

        # Chart area
        self.fig, self.ax = plt.subplots(figsize=(7, 3))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.get_tk_widget().pack(pady=20)

        # Button area
        btn_frame = ttk.Frame(self.root)
        btn_frame.pack(pady=10)

        self.export_btn = ttk.Button(btn_frame, text="Export Report", command=self.export_report)
        self.export_btn.grid(row=0, column=0, padx=10)

        self.quit_btn = ttk.Button(btn_frame, text="Exit", command=self.stop)
        self.quit_btn.grid(row=0, column=1, padx=10)

    def update_stats(self):
        # Log file setup
        with open("system_log.csv", "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Timestamp", "CPU (%)", "Memory (%)", "Disk (%)"])

            while self.running:
                # Gather data
                cpu = psutil.cpu_percent()
                mem = psutil.virtual_memory().percent
                disk = psutil.disk_usage('/').percent
                now = datetime.now().strftime("%H:%M:%S")

                # Update UI
                self.cpu_progress["value"] = cpu
                self.cpu_label.config(text=f"CPU Usage: {cpu}%")
                self.mem_progress["value"] = mem
                self.mem_label.config(text=f"Memory Usage: {mem}%")
                self.disk_progress["value"] = disk
                self.disk_label.config(text=f"Disk Usage: {disk}%")

                # Write to CSV
                writer.writerow([now, cpu, mem, disk])
                f.flush()

                # Warnings
                if cpu > 80:
                    self.notify(f"⚠️ High CPU Usage Detected: {cpu}%")
                if mem > 80:
                    self.notify(f"⚠️ High Memory Usage Detected: {mem}%")
                if disk > 90:
                    self.notify(f"⚠️ High Disk Usage Detected: {disk}%")

                # Save for chart
                self.time_stamps.append(now)
                self.cpu_data.append(cpu)
                self.mem_data.append(mem)
                self.disk_data.append(disk)

                # Limit to last 60 points
                self.time_stamps = self.time_stamps[-60:]
                self.cpu_data = self.cpu_data[-60:]
                self.mem_data = self.mem_data[-60:]
                self.disk_data = self.disk_data[-60:]

                self.update_chart()
                time.sleep(2)

    def update_chart(self):
        self.ax.clear()
        self.ax.plot(self.time_stamps, self.cpu_data, label="CPU")
        self.ax.plot(self.time_stamps, self.mem_data, label="Memory")
        self.ax.plot(self.time_stamps, self.disk_data, label="Disk")
        self.ax.set_title("System Usage Over Time")
        self.ax.set_xlabel("Time")
        self.ax.set_ylabel("Usage (%)")
        self.ax.legend()
        self.ax.set_ylim(0, 100)
        self.ax.tick_params(axis='x', labelrotation=45)
        self.fig.tight_layout()
        self.canvas.draw()

    def notify(self, message):
        print(message)
        self.root.after(0, lambda: messagebox.showwarning("System Alert", message))

    def export_report(self):
        export_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if export_path:
            try:
                with open("system_log.csv", "r") as src, open(export_path, "w", newline="") as dst:
                    dst.writelines(src.readlines())
                messagebox.showinfo("Export Complete", f"Report exported to:\n{export_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export report:\n{e}")

    def stop(self):
        self.running = False
        self.root.quit()

if __name__ == "__main__":
    root = tk.Tk()
    app = SystemMonitor(root)
    root.mainloop()
