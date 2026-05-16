import tkinter as tk
from tkinter import ttk, messagebox
import calendar
from datetime import datetime
import threading
import time

calendar.setfirstweekday(calendar.SUNDAY)

# =========================
# Reminder Storage
# =========================
# Format:
# reminders["2026-05-13"] = [
#     ("10:00", "11:00", "Math Class", "Class")
# ]
reminders = {}

COLOR_MAP = {
    "Class": "#4FC3F7",
    "Exam": "#EF5350",
    "Assignment": "#66BB6A",
    "Other": "#FFD54F"
}


# =========================
# Brighten Hover Color
# =========================
def brighten(color, factor=1.2):

    color = color.lstrip("#")

    r, g, b = tuple(
        int(color[i:i+2], 16)
        for i in (0, 2, 4)
    )

    r = min(int(r * factor), 255)
    g = min(int(g * factor), 255)
    b = min(int(b * factor), 255)

    return f"#{r:02x}{g:02x}{b:02x}"


# =========================
# Main Calendar App
# =========================
class CalendarApp:

    def __init__(self, root):

        self.root = root

        self.root.title("Smart Calendar")

        self.root.geometry("760x650")

        self.root.configure(bg="#1e1e1e")

        self.year = datetime.now().year
        self.month = datetime.now().month

        self.selected_day = None

        # =========================
        # Header
        # =========================
        self.header = tk.Label(
            root,
            font=("Segoe UI", 18, "bold"),
            bg="#1e1e1e",
            fg="white"
        )

        self.header.pack(pady=10)

        # =========================
        # Month Navigation
        # =========================
        nav = tk.Frame(root, bg="#1e1e1e")
        nav.pack(pady=5)

        # Previous Month
        prev_frame = tk.Frame(nav, bg="#1e1e1e")
        prev_frame.pack(side=tk.LEFT, padx=20)

        tk.Label(
            prev_frame,
            text="Previous Month",
            bg="#1e1e1e",
            fg="#aaaaaa",
            font=("Segoe UI", 9)
        ).pack()

        prev_btn = tk.Button(
            prev_frame,
            text="❮",
            font=("Segoe UI", 14, "bold"),
            bg="#2f2f2f",
            fg="white",
            relief="flat",
            width=4,
            cursor="hand2",
            command=self.prev_month
        )

        prev_btn.pack(pady=2)

        # Next Month
        next_frame = tk.Frame(nav, bg="#1e1e1e")
        next_frame.pack(side=tk.LEFT, padx=20)

        tk.Label(
            next_frame,
            text="Next Month",
            bg="#1e1e1e",
            fg="#aaaaaa",
            font=("Segoe UI", 9)
        ).pack()

        next_btn = tk.Button(
            next_frame,
            text="❯",
            font=("Segoe UI", 14, "bold"),
            bg="#2f2f2f",
            fg="white",
            relief="flat",
            width=4,
            cursor="hand2",
            command=self.next_month
        )

        next_btn.pack(pady=2)

        # Hover Effects
        def nav_enter(e):
            e.widget.config(bg="#444")

        def nav_leave(e):
            e.widget.config(bg="#2f2f2f")

        prev_btn.bind("<Enter>", nav_enter)
        prev_btn.bind("<Leave>", nav_leave)

        next_btn.bind("<Enter>", nav_enter)
        next_btn.bind("<Leave>", nav_leave)

        # =========================
        # Calendar Frame
        # =========================
        self.cal_frame = tk.Frame(
            root,
            bg="#1e1e1e"
        )

        self.cal_frame.pack(
            pady=10,
            fill="both",
            expand=True
        )

        # =========================
        # Reminder Section
        # =========================
        self.reminder_frame = tk.Frame(
            root,
            bg="#2b2b2b"
        )

        self.reminder_frame.pack(
            pady=10,
            fill="x",
            padx=20
        )

        tk.Label(
            self.reminder_frame,
            text="Reminders",
            font=("Segoe UI", 14, "bold"),
            bg="#2b2b2b",
            fg="white"
        ).pack(pady=5)

        # Reminder List
        self.reminder_list = tk.Listbox(
            self.reminder_frame,
            bg="#1e1e1e",
            fg="white",
            height=6
        )

        self.reminder_list.pack(
            fill="x",
            padx=10,
            pady=5
        )

        # =========================
        # Edit/Delete Buttons
        # =========================
        action_frame = tk.Frame(
            self.reminder_frame,
            bg="#2b2b2b"
        )

        action_frame.pack()

        tk.Button(
            action_frame,
            text="Edit",
            bg="#2196F3",
            fg="white",
            command=self.edit_reminder
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            action_frame,
            text="Delete",
            bg="#f44336",
            fg="white",
            command=self.delete_reminder
        ).pack(side=tk.LEFT, padx=5)

        # =========================
        # Input Section
        # =========================
        input_frame = tk.Frame(
            self.reminder_frame,
            bg="#2b2b2b"
        )

        input_frame.pack(pady=5)

        # Start Time
        self.start_time_entry = tk.Entry(
            input_frame,
            width=8
        )

        self.start_time_entry.insert(0, "10:00")

        self.start_time_entry.pack(
            side=tk.LEFT,
            padx=3
        )

        tk.Label(
            input_frame,
            text="to",
            bg="#2b2b2b",
            fg="white"
        ).pack(side=tk.LEFT)

        # End Time
        self.end_time_entry = tk.Entry(
            input_frame,
            width=8
        )

        self.end_time_entry.insert(0, "11:00")

        self.end_time_entry.pack(
            side=tk.LEFT,
            padx=3
        )

        # Reminder Text
        self.text_entry = tk.Entry(
            input_frame,
            width=22
        )

        self.text_entry.pack(
            side=tk.LEFT,
            padx=5
        )

        # Reminder Type
        self.type_var = tk.StringVar(value="Class")

        ttk.OptionMenu(
            input_frame,
            self.type_var,
            "Class",
            "Class",
            "Exam",
            "Assignment",
            "Other"
        ).pack(side=tk.LEFT)

        # Add Button
        tk.Button(
            self.reminder_frame,
            text="Add Reminder",
            bg="#4CAF50",
            fg="white",
            command=self.add_reminder
        ).pack(pady=5)

        # =========================
        # Initial Draw
        # =========================
        self.draw_calendar()

        # Notification Thread
        threading.Thread(
            target=self.check_notifications,
            daemon=True
        ).start()

    # =========================
    # Reminder Dots
    # =========================
    def get_day_dots(self, date_key):

        if date_key not in reminders:
            return []

        types = [
            typ
            for _, _, _, typ
            in reminders[date_key]
        ]

        return [
            COLOR_MAP.get(t, "#ffffff")
            for t in types
        ]

    # =========================
    # Draw Calendar
    # =========================
    def draw_calendar(self):

        for widget in self.cal_frame.winfo_children():
            widget.destroy()

        self.header.config(
            text=f"{calendar.month_name[self.month]} {self.year}"
        )

        # Configure Columns
        for i in range(7):

            self.cal_frame.grid_columnconfigure(
                i,
                weight=1,
                uniform="col"
            )

        # Weekday Names
        days = [
            "Sun", "Mon", "Tue",
            "Wed", "Thu", "Fri", "Sat"
        ]

        for col, d in enumerate(days):

            tk.Label(
                self.cal_frame,
                text=d,
                bg="#1e1e1e",
                fg="white",
                font=("Segoe UI", 10, "bold")
            ).grid(
                row=0,
                column=col,
                sticky="nsew"
            )

        cal = calendar.monthcalendar(
            self.year,
            self.month
        )

        # Create Calendar Days
        for r, week in enumerate(cal, start=1):

            for c, day in enumerate(week):

                if day == 0:

                    tk.Label(
                        self.cal_frame,
                        bg="#1e1e1e"
                    ).grid(
                        row=r,
                        column=c,
                        sticky="nsew"
                    )

                else:

                    date_key = (
                        f"{self.year}-"
                        f"{self.month:02d}-"
                        f"{day:02d}"
                    )

                    # Selected Day = Red
                    if date_key == self.selected_day:
                        base_color = "#E53935"
                    else:
                        base_color = "#2f2f2f"

                    hover_color = brighten(base_color, 1.3)

                    frame = tk.Frame(
                        self.cal_frame,
                        bg=base_color
                    )

                    frame.grid(
                        row=r,
                        column=c,
                        padx=3,
                        pady=3,
                        sticky="nsew"
                    )

                    # Day Button
                    btn = tk.Button(
                        frame,
                        text=str(day),
                        bg=base_color,
                        fg="white",
                        relief="flat",
                        font=("Segoe UI", 11, "bold"),
                        bd=0,
                        highlightthickness=0,
                        activebackground=hover_color,
                        activeforeground="white",
                        command=lambda d=day:
                        self.select_day(d)
                    )

                    btn.pack(
                        fill="both",
                        expand=True
                    )

                    # Hover Effects
                    def enter(
                        e,
                        b=btn,
                        f=frame,
                        hc=hover_color
                    ):
                        b.config(bg=hc)
                        f.config(bg=hc)

                    def leave(
                        e,
                        b=btn,
                        f=frame,
                        bc=base_color
                    ):
                        b.config(bg=bc)
                        f.config(bg=bc)

                    btn.bind("<Enter>", enter)
                    btn.bind("<Leave>", leave)

                    # Reminder Dots
                    dot_frame = tk.Frame(
                        frame,
                        bg=base_color
                    )

                    dot_frame.pack(pady=2)

                    dots = self.get_day_dots(date_key)

                    for color in dots[:6]:

                        tk.Label(
                            dot_frame,
                            text="●",
                            fg=color,
                            bg=base_color,
                            font=("Arial", 7)
                        ).pack(side=tk.LEFT)

                    if len(dots) > 6:

                        tk.Label(
                            dot_frame,
                            text=f"+{len(dots)-6}",
                            fg="white",
                            bg=base_color,
                            font=("Arial", 7, "bold")
                        ).pack(side=tk.LEFT)

    # =========================
    # Select Day
    # =========================
    def select_day(self, day):

        self.selected_day = (
            f"{self.year}-"
            f"{self.month:02d}-"
            f"{day:02d}"
        )

        self.draw_calendar()
        self.update_reminders()

    # =========================
    # Update Reminder List
    # =========================
    def update_reminders(self):

        self.reminder_list.delete(0, tk.END)

        if self.selected_day in reminders:

            self.sorted_reminders = sorted(
                reminders[self.selected_day],
                key=lambda x:
                datetime.strptime(
                    x[0],
                    "%H:%M"
                )
            )

            for i, (
                start,
                end,
                text,
                typ
            ) in enumerate(self.sorted_reminders):

                self.reminder_list.insert(
                    tk.END,
                    f"{start} - {end} | {text} ({typ})"
                )

                self.reminder_list.itemconfig(
                    i,
                    bg=COLOR_MAP.get(typ),
                    fg="black"
                )

    # =========================
    # Add Reminder
    # =========================
    def add_reminder(self):

        if not self.selected_day:

            messagebox.showwarning(
                "Warning",
                "Select a date first!"
            )

            return

        try:

            start_time = self.start_time_entry.get()
            end_time = self.end_time_entry.get()

            start_obj = datetime.strptime(
                start_time,
                "%H:%M"
            )

            end_obj = datetime.strptime(
                end_time,
                "%H:%M"
            )

            if end_obj <= start_obj:

                messagebox.showerror(
                    "Error",
                    "End time must be after start time"
                )

                return

        except ValueError:

            messagebox.showerror(
                "Error",
                "Use HH:MM format"
            )

            return

        reminder_text = self.text_entry.get()
        reminder_type = self.type_var.get()

        # Prevent Overlap
        if self.selected_day in reminders:

            for (
                existing_start,
                existing_end,
                _,
                _
            ) in reminders[self.selected_day]:

                existing_start_obj = datetime.strptime(
                    existing_start,
                    "%H:%M"
                )

                existing_end_obj = datetime.strptime(
                    existing_end,
                    "%H:%M"
                )

                overlap = (
                    start_obj < existing_end_obj
                    and end_obj > existing_start_obj
                )

                if overlap:

                    messagebox.showerror(
                        "Schedule Conflict",
                        f"Overlaps with:\n"
                        f"{existing_start} - {existing_end}"
                    )

                    return

        # Add Reminder
        reminders.setdefault(
            self.selected_day,
            []
        ).append(
            (
                start_time,
                end_time,
                reminder_text,
                reminder_type
            )
        )

        # Clear Text
        self.text_entry.delete(0, tk.END)

        # Refresh
        self.update_reminders()
        self.draw_calendar()

    # =========================
    # Delete Reminder
    # =========================
    def delete_reminder(self):

        selection = self.reminder_list.curselection()

        if not selection:
            return

        index = selection[0]

        item = self.sorted_reminders[index]

        reminders[self.selected_day].remove(item)

        self.update_reminders()
        self.draw_calendar()

    # =========================
    # Edit Reminder
    # =========================
    def edit_reminder(self):

        selection = self.reminder_list.curselection()

        if not selection:
            return

        index = selection[0]

        old = self.sorted_reminders[index]

        self.start_time_entry.delete(0, tk.END)
        self.start_time_entry.insert(0, old[0])

        self.end_time_entry.delete(0, tk.END)
        self.end_time_entry.insert(0, old[1])

        self.text_entry.delete(0, tk.END)
        self.text_entry.insert(0, old[2])

        self.type_var.set(old[3])

        reminders[self.selected_day].remove(old)

        self.update_reminders()
        self.draw_calendar()

    # =========================
    # Previous Month
    # =========================
    def prev_month(self):

        self.month -= 1

        if self.month < 1:

            self.month = 12
            self.year -= 1

        self.draw_calendar()

    # =========================
    # Next Month
    # =========================
    def next_month(self):

        self.month += 1

        if self.month > 12:

            self.month = 1
            self.year += 1

        self.draw_calendar()

    # =========================
    # Notifications
    # =========================
    def check_notifications(self):

        while True:

            now = datetime.now()

            today = now.strftime("%Y-%m-%d")

            current_time = now.strftime("%H:%M")

            if today in reminders:

                for (
                    start,
                    end,
                    text,
                    typ
                ) in reminders[today]:

                    if start == current_time:

                        messagebox.showinfo(
                            "Reminder",
                            f"{start} - {end}\n"
                            f"{text} ({typ})"
                        )

            time.sleep(60)


# =========================
# Run App
# =========================
root = tk.Tk()

app = CalendarApp(root)

root.mainloop()