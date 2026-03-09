import tkinter as tk
from tkinter import messagebox
from grocery_app import (init_db, db_get_members, db_add_member, db_remove_member,
    db_get_lists, db_add_list, db_remove_list, db_get_items, db_add_item,
    db_delete_item, db_toggle_bought)

init_db()
BG, BTN, RED = "#f5f5f5", "#e0e0e0", "#ffdddd"

def clear(f):
    for w in f.winfo_children(): w.destroy()

def sep(p):
    tk.Frame(p, height=1, bg="#ccc").pack(fill="x", pady=6)

def lbl(p, t, bold=False, gray=False):
    tk.Label(p, text=t, bg=BG, font=("Arial", 10, "bold" if bold else "normal"),
             fg="gray" if gray else "black", anchor="center").pack(fill="x")

def mkbtn(p, text, cmd, color=BTN, w=10):
    return tk.Button(p, text=text, command=cmd, width=w, font=("Arial", 9),
                     bg=color, relief="groove", cursor="hand2")

def big_btn(p, text, cmd):
    tk.Button(p, text=text, command=cmd, width=22, font=("Arial", 10),
              bg=BTN, relief="groove", cursor="hand2").pack(pady=2)

def entry_row(p, var, cmd, btn_text="Add"):
    r = tk.Frame(p, bg=BG); r.pack(pady=5)
    e = tk.Entry(r, textvariable=var, width=18, font=("Arial", 10))
    e.pack(side="left", padx=3); e.bind("<Return>", lambda _: cmd()); e.focus()
    tk.Button(r, text=btn_text, command=cmd, width=7, font=("Arial", 10),
              bg=BTN, relief="groove", cursor="hand2").pack(side="left")

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Household Grocery List")
        self.geometry("520x560"); self.resizable(False, False); self.configure(bg=BG)
        self.main = tk.Frame(self, bg=BG, padx=50, pady=16)
        self.main.pack(fill="both", expand=True)
        self.show_home()

    def show_home(self):
        clear(self.main)
        lbl(self.main, "🛒 Household Grocery List", bold=True); sep(self.main)
        lbl(self.main, "Who are you?")
        members = db_get_members()
        if members:
            for mid, name in members:
                r = tk.Frame(self.main, bg=BG); r.pack(pady=2)
                mkbtn(r, name, lambda i=mid, n=name: self.show_lists(i, n), w=16).pack(side="left", padx=3)
                mkbtn(r, "Remove", lambda i=mid, n=name: self.remove_member(i, n), RED).pack(side="left")
        else:
            lbl(self.main, "No members yet.", gray=True)
        sep(self.main); lbl(self.main, "Add new member:")
        self.mvar = tk.StringVar()
        entry_row(self.main, self.mvar, self.add_member)
        sep(self.main)
        r = tk.Frame(self.main, bg=BG); r.pack()
        mkbtn(r, "Manage Lists", self.show_manage_lists, w=14).pack(side="left", padx=4)
        mkbtn(r, "View List (read only)", self.show_view_pick, w=18).pack(side="left")

    def add_member(self):
        n = self.mvar.get().strip()
        if not n: return
        if not db_add_member(n): messagebox.showerror("Error", f"'{n}' already exists.")
        else: self.show_home()

    def remove_member(self, mid, name):
        if messagebox.askyesno("Remove", f"Remove '{name}' and all their items?"):
            db_remove_member(mid); self.show_home()

    def show_lists(self, mid, mname):
        clear(self.main)
        lbl(self.main, f"👤 {mname}", bold=True); sep(self.main)
        lbl(self.main, "Choose a list:")
        lists = db_get_lists()
        [big_btn(self.main, n, lambda i=l, n=n: self.show_list(i, n, mid, mname)) for l, n in lists] \
            if lists else lbl(self.main, "No lists yet.", gray=True)
        sep(self.main); lbl(self.main, "Or create a new list:")
        self.nlvar = tk.StringVar()
        entry_row(self.main, self.nlvar, lambda: self.add_list_here(mid, mname), "Create")
        sep(self.main)
        mkbtn(self.main, "← Back", self.show_home).pack()

    def add_list_here(self, mid, mname):
        n = self.nlvar.get().strip()
        if not n: return
        if not db_add_list(n): messagebox.showerror("Error", f"'{n}' already exists.")
        else: self.show_lists(mid, mname)

    def show_manage_lists(self):
        clear(self.main); lbl(self.main, "📋 Manage Lists", bold=True); sep(self.main)
        lists = db_get_lists()
        if lists:
            for lid, n in lists:
                r = tk.Frame(self.main, bg=BG); r.pack(pady=2)
                tk.Label(r, text=n, width=18, font=("Arial", 10), bg=BG, anchor="w").pack(side="left", padx=4)
                mkbtn(r, "Delete", lambda i=lid, n=n: self.delete_list(i, n), RED).pack(side="left")
        else:
            lbl(self.main, "No lists yet.", gray=True)
        sep(self.main); lbl(self.main, "Create new list:")
        self.lvar = tk.StringVar()
        entry_row(self.main, self.lvar, self.add_list, "Create")
        sep(self.main)
        mkbtn(self.main, "← Back", self.show_home).pack()

    def add_list(self):
        n = self.lvar.get().strip()
        if not n: return
        if not db_add_list(n): messagebox.showerror("Error", f"'{n}' already exists.")
        else: self.show_manage_lists()

    def delete_list(self, lid, name):
        if messagebox.askyesno("Delete", f"Delete '{name}' and all its items?"):
            db_remove_list(lid); self.show_manage_lists()

    def show_view_pick(self):
        clear(self.main); lbl(self.main, "📋 View a List", bold=True); sep(self.main)
        lbl(self.main, "Choose a list (read only):")
        lists = db_get_lists()
        [big_btn(self.main, n, lambda i=l, n=n: self.show_list(i, n, None, None, True)) for l, n in lists] \
            if lists else lbl(self.main, "No lists yet.", gray=True)
        sep(self.main)
        mkbtn(self.main, "← Back", self.show_home).pack()

    def show_list(self, lid, lname, mid, mname, readonly=False):
        clear(self.main)
        lbl(self.main, f"🗒 {lname}" + (" [Read Only]" if readonly else f" — {mname}"), bold=True)
        items = db_get_items(lid)
        bought = sum(1 for i in items if i[4])
        lbl(self.main, f"{len(items)} items  |  {len(items)-bought} to buy  |  {bought} bought", gray=True)
        sep(self.main)
        frame = tk.Frame(self.main, bg=BG, height=220)
        frame.pack(fill="x"); frame.pack_propagate(False)
        canvas = tk.Canvas(frame, bg=BG, highlightthickness=0)
        sb = tk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        sf = tk.Frame(canvas, bg=BG)
        sf.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=sf, anchor="nw")
        canvas.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y"); canvas.pack(side="left", fill="both", expand=True)

        if not items:
            tk.Label(sf, text="List is empty.", bg=BG, fg="gray", font=("Arial", 10)).pack(pady=10)
        for iid, mem, iname, date, ib in items:
            r = tk.Frame(sf, bg="#e8f5e9" if ib else "white", relief="groove", bd=1)
            r.pack(fill="x", pady=2, padx=2)
            tk.Label(r, text=f"  {'✓' if ib else '○'}  {iname}", width=14, anchor="w",
                     font=("Arial", 10, "overstrike" if ib else "normal"), bg=r["bg"]).pack(side="left")
            tk.Label(r, text=f"{mem} · {date}", font=("Arial", 8), fg="gray", bg=r["bg"]).pack(side="left")
            if not readonly:
                mkbtn(r, "Unbought" if ib else "Bought",
                      lambda i=iid, b=ib: self._toggle(i, b, lid, lname, mid, mname), w=8
                      ).pack(side="right", padx=2, pady=2)
                mkbtn(r, "Delete",
                      lambda i=iid, n=iname: self._delete(i, n, lid, lname, mid, mname),
                      RED, w=6).pack(side="right", pady=2)
        sep(self.main)
        if not readonly:
            lbl(self.main, "Add item:")
            self.ivar = tk.StringVar()
            entry_row(self.main, self.ivar, lambda: self._add(lid, lname, mid, mname), "Add")
            sep(self.main)

        back = (lambda: self.show_view_pick()) if readonly else (lambda: self.show_lists(mid, mname))
        mkbtn(self.main, "← Back", back).pack()

    def _add(self, lid, lname, mid, mname):
        n = self.ivar.get().strip()
        if n: db_add_item(lid, mid, n); self.show_list(lid, lname, mid, mname)

    def _delete(self, iid, name, lid, lname, mid, mname):
        if messagebox.askyesno("Delete", f"Delete '{name}'?"):
            db_delete_item(iid); self.show_list(lid, lname, mid, mname)

    def _toggle(self, iid, cur, lid, lname, mid, mname):
        db_toggle_bought(iid, cur); self.show_list(lid, lname, mid, mname)

if __name__ == "__main__":
    App().mainloop()