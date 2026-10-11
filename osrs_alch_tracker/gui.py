import os
import sys
import time
import math
import glob
import shutil
import threading
import tkinter as tk
from tkinter import ttk, messagebox

# Sound support on Windows
try:
    import winsound
    HAS_WINSOUND = True
except ImportError:
    HAS_WINSOUND = False

from api import OSRSPricesAPI, NATURE_RUNE_ID
from crafting import CRAFTING_RECIPES
from ge_crafting import GE_PROFIT_RECIPES
from skilling_guide import SKILLING_GUIDES, SMITHING_MATERIAL_CHAINS, get_xp_for_level, get_level_for_xp, calculate_skilling_cycle, get_progression_eta, format_skilling_duration
from state import AppState
from updater import APP_VERSION, check_for_updates, UpdateDialog, WhatsNewDialog
from bridge_server import BridgeServer
import datetime
import webbrowser
import re

# Hall-of-Fame All-Time Workhorses (The gold standards of OSRS High Alchemy)
WORKHORSE_ITEMS = [
    {
        "id": 1079,
        "name": "Rune platelegs",
        "limit": 70,
        "members": False,
        "verdict": "👑 All-Time King: Highest alch floor (38.4k), zero price risk, instant liquidity."
    },
    {
        "id": 1093,
        "name": "Rune plateskirt",
        "limit": 70,
        "members": False,
        "verdict": "👑 Platelegs Twin: Identical 38.4k alch value, massive supply from smithers."
    },
    {
        "id": 1319,
        "name": "Rune 2h sword",
        "limit": 70,
        "members": False,
        "verdict": "⚔️ Top Volume Weapon: Constant supply from smithing & clue scrolls, fills fast."
    },
    {
        "id": 1201,
        "name": "Rune kiteshield",
        "limit": 70,
        "members": False,
        "verdict": "🛡️ High Alch Staple: Very steady 32.6k value, rock-solid profit margins."
    },
    {
        "id": 1113,
        "name": "Rune chainbody",
        "limit": 70,
        "members": False,
        "verdict": "🛡️ Solid 30k Floor: Reliable slayer drop supply, high profit spreads."
    },
    {
        "id": 1373,
        "name": "Rune battleaxe",
        "limit": 70,
        "members": False,
        "verdict": "🪓 Slayer Classic: Consistently traded at 24.9k floor with rapid turnover."
    },
    {
        "id": 1347,
        "name": "Rune warhammer",
        "limit": 70,
        "members": False,
        "verdict": "🔨 High Turnover: Frequent undercut sellers create wide profit spreads."
    },
    {
        "id": 1185,
        "name": "Rune sq shield",
        "limit": 70,
        "members": False,
        "verdict": "🛡️ Steady Earner: Reliable 23k floor with steady patient fills."
    },
    {
        "id": 1123,
        "name": "Adamant platebody",
        "limit": 125,
        "members": False,
        "verdict": "📦 High 125 Limit: Low capital (~1M batch), great F2P/P2P staple."
    },
    {
        "id": 1163,
        "name": "Rune full helm",
        "limit": 70,
        "members": False,
        "verdict": "🪖 Steady Volume: Reliable 21.1k alch value, quick fill cycles."
    },
    {
        "id": 1333,
        "name": "Rune scimitar",
        "limit": 70,
        "members": False,
        "verdict": "🗡️ High Liquidity: F2P/P2P staple, fast trading velocity."
    },
    {
        "id": 1213,
        "name": "Rune dagger",
        "limit": 70,
        "members": False,
        "verdict": "🗡️ Low Capital: Low buy price (~4.3k), high volume from monster drops."
    },
    {
        "id": 1397,
        "name": "Air battlestaff",
        "limit": 18000,
        "members": True,
        "verdict": "⚡ Massive 18k Limit: Premier crafting & bulk alch item with huge daily turnover."
    },
    {
        "id": 1135,
        "name": "Green d'hide body",
        "limit": 125,
        "members": False,
        "verdict": "🏹 Bulk Crafting Staple: Low buy price, high 125 limit, safe margins."
    },
    {
        "id": 1215,
        "name": "Dragon dagger",
        "limit": 70,
        "members": True,
        "verdict": "🗡️ Slayer Favorite: 18k alch value with deep undercut sell volume."
    }
]

def get_market_timing_info():
    """
    Analyzes global OSRS market liquidity based on UTC time and concurrent player activity curves.
    Peak player activity occurs between 14:00 and 22:00 UTC (~120k-165k players).
    Off-peak / sleepers window occurs between 02:00 and 10:00 UTC (~45k-75k players).
    """
    now_utc = datetime.datetime.now(datetime.timezone.utc)
    hour = now_utc.hour + now_utc.minute / 60.0
    time_str = now_utc.strftime("%H:%M UTC")

    if 14.0 <= hour < 22.0:
        pct = int(75 + 25 * (1.0 - abs(hour - 18.0) / 4.0))
        pct = max(75, min(100, pct))
        est_players = f"~{int(115000 + (pct - 75) * 1800):,} online"
        bar_n = int(round(pct / 10))
        bar = "█" * bar_n + "░" * (10 - bar_n)
        return {
            "time_str": time_str,
            "badge": "🟢 Peak Liquidity Window (Fast Fills & High Volume)",
            "badge_color": "#2ecc71",
            "activity": f"Activity: [{bar}] {pct}% ({est_players})",
            "advice": "💡 Market Tip: Prime EU/US trading hours! Buy orders fill in 2-5m. Best time for Fast Fills & Workhorses.",
            "rec_cat": "fast"
        }
    elif 22.0 <= hour or hour < 2.0:
        pct = 65
        est_players = "~95,000 online"
        bar = "██████░░░░"
        return {
            "time_str": time_str,
            "badge": "🟡 Evening Wind-Down (Good for Setting Overnight Orders)",
            "badge_color": "#f1c40f",
            "activity": f"Activity: [{bar}] 65% ({est_players})",
            "advice": "💡 Market Tip: US late evening. Volume tapering off. Queue up high-profit overnight bids.",
            "rec_cat": "overnight"
        }
    elif 2.0 <= hour < 10.0:
        pct = 40
        est_players = "~55,000 online"
        bar = "████░░░░░░"
        return {
            "time_str": time_str,
            "badge": "🌙 Off-Peak / Sleepers Window (Wide Overnight Margins)",
            "badge_color": "#9b59b6",
            "activity": f"Activity: [{bar}] 40% ({est_players})",
            "advice": "💡 Market Tip: Lowest global player count. Patient low bids fill with zero competition from undercut sellers.",
            "rec_cat": "overnight"
        }
    else: # 10.0 <= hour < 14.0
        pct = 60
        est_players = "~85,000 online"
        bar = "██████░░░░"
        return {
            "time_str": time_str,
            "badge": "🌅 Morning Ramp-Up (Volume Building)",
            "badge_color": "#3498db",
            "activity": f"Activity: [{bar}] 60% ({est_players})",
            "advice": "💡 Market Tip: European morning. Market liquidity is steadily accelerating towards afternoon peak.",
            "rec_cat": "workhorse"
        }

def format_gp(val):
    if val is None:
        return "0 gp"
    try:
        val = int(val)
        if abs(val) >= 1_000_000:
            return f"{val / 1_000_000:.2f}M gp"
        elif abs(val) >= 1_000:
            return f"{val:,} gp"
        else:
            return f"{val} gp"
    except Exception:
        return f"{val} gp"

def parse_cash_input(text):
    text = str(text).strip().upper().replace(",", "").replace(" ", "").replace("GP", "")
    if not text:
        return 0
    multiplier = 1
    if text.endswith("K"):
        multiplier = 1_000
        text = text[:-1]
    elif text.endswith("M"):
        multiplier = 1_000_000
        text = text[:-1]
    elif text.endswith("B"):
        multiplier = 1_000_000_000
        text = text[:-1]
    try:
        return int(float(text) * multiplier)
    except ValueError:
        return 0

def is_activity_match(detected_act: str, target_name: str) -> bool:
    if not detected_act or not target_name:
        return False
    d = detected_act.lower().strip()
    t = target_name.lower().strip()
    if d in t or t in d:
        return True
    d_tokens = set(re.findall(r"\w+", d))
    t_tokens = set(re.findall(r"\w+", t))
    metals = {"bronze", "iron", "steel", "silver", "gold", "mithril", "adamant", "adamantite", "rune", "runite"}
    d_metals = {m.replace("adamantite", "adamant").replace("runite", "rune") for m in d_tokens.intersection(metals)}
    t_metals = {m.replace("adamantite", "adamant").replace("runite", "rune") for m in t_tokens.intersection(metals)}
    if d_metals and t_metals and d_metals != t_metals:
        return False
    is_d_smelt = any(w in d for w in ("smelt", "furnace")) or ("bar" in d and "smith" not in d)
    is_t_smelt = any(w in t for w in ("smelt", "furnace", "baseline")) or ("bar" in t and not any(k in t for k in ("plate", "legs", "helm", "sword", "dagger", "axe", "dart", "knife", "2h", "chain", "skirt", "scimitar", "warhammer", "battleaxe", "mace", "claws", "shield")))
    if is_d_smelt and is_t_smelt and d_metals and d_metals == t_metals:
        return True
    is_d_anvil = any(w in d for w in ("smith", "anvil", "hammer", "plate", "legs", "helm", "sword", "dagger", "axe", "dart", "knife"))
    is_t_anvil = any(w in t for w in ("smith", "anvil", "hammer", "plate", "legs", "helm", "sword", "dagger", "axe", "dart", "knife", "scimitar", "2h"))
    if is_d_anvil and is_t_anvil and d_metals and d_metals == t_metals:
        overlap = d_tokens.intersection(t_tokens) - {"smithing", "smith", "bars", "bar"}
        if overlap or not is_d_smelt:
            return True
    return False

class FloatingToast(tk.Toplevel):
    def __init__(self, parent, title, message, duration=5000):
        super().__init__(parent)
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.configure(bg="#2d2d30", highlightthickness=1, highlightbackground="#f39c12")

        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        w = 340
        h = 85
        x = screen_w - w - 25
        y = screen_h - h - 60
        self.geometry(f"{w}x{h}+{x}+{y}")

        title_lbl = tk.Label(self, text=title, font=("Segoe UI", 10, "bold"), fg="#f39c12", bg="#2d2d30")
        title_lbl.pack(anchor="w", padx=12, pady=(8, 2))

        msg_lbl = tk.Label(self, text=message, font=("Segoe UI", 9), fg="#ffffff", bg="#2d2d30", wraplength=310, justify="left")
        msg_lbl.pack(anchor="w", padx=12, pady=(0, 8))

        self.after(duration, self.destroy)
        self.bind("<Button-1>", lambda e: self.destroy())

class EditSessionDialog(tk.Toplevel):
    def __init__(self, parent, entry, on_save_callback):
        super().__init__(parent)
        self.title("Edit Session Entry")
        self.geometry("380x300")
        self.resizable(False, False)
        self.configure(bg="#252528")
        self.transient(parent)
        self.grab_set()

        self.entry = entry
        self.on_save_callback = on_save_callback

        # Center dialog
        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - 190
        y = parent.winfo_y() + (parent.winfo_height() // 2) - 150
        self.geometry(f"+{x}+{y}")

        lbl_title = tk.Label(self, text=f"Edit: {entry['item']}", font=("Segoe UI", 11, "bold"), fg="#f39c12", bg="#252528")
        lbl_title.pack(pady=(12, 10))

        form = tk.Frame(self, bg="#252528")
        form.pack(padx=20, fill="x")

        # Qty
        tk.Label(form, text="Quantity Bought:", fg="#cccccc", bg="#252528").grid(row=0, column=0, sticky="w", pady=5)
        self.ent_qty = tk.Entry(form, bg="#1e1e1e", fg="#ffffff", insertbackground="#ffffff")
        self.ent_qty.insert(0, str(entry.get("qty", 1)))
        self.ent_qty.grid(row=0, column=1, pady=5, padx=5)

        # Buy Price
        tk.Label(form, text="Bought At (ea):", fg="#cccccc", bg="#252528").grid(row=1, column=0, sticky="w", pady=5)
        self.ent_buy = tk.Entry(form, bg="#1e1e1e", fg="#ffffff", insertbackground="#ffffff")
        self.ent_buy.insert(0, str(entry.get("buy_price", 0)))
        self.ent_buy.grid(row=1, column=1, pady=5, padx=5)

        # Nat Cost
        tk.Label(form, text="Nature Cost (ea):", fg="#cccccc", bg="#252528").grid(row=2, column=0, sticky="w", pady=5)
        self.ent_nat = tk.Entry(form, bg="#1e1e1e", fg="#ffffff", insertbackground="#ffffff")
        self.ent_nat.insert(0, str(entry.get("nat_price", 0)))
        self.ent_nat.grid(row=2, column=1, pady=5, padx=5)

        # Alch Val (Readonly)
        tk.Label(form, text="High Alch Val:", fg="#888888", bg="#252528").grid(row=3, column=0, sticky="w", pady=5)
        lbl_alch = tk.Label(form, text=f"{entry.get('alch_val', 0):,} gp (Fixed)", fg="#888888", bg="#252528")
        lbl_alch.grid(row=3, column=1, sticky="w", pady=5, padx=5)

        # 4h Cooldown auto-sync note
        tk.Label(form, text="💡 4h GE buy limit cooldown will auto-sync with this quantity.",
                 fg="#888888", bg="#252528", font=("Segoe UI", 8, "italic")).grid(row=4, column=0, columnspan=2, pady=(4, 0))

        # Dynamic Profit preview
        self.lbl_profit_preview = tk.Label(self, text="Realized Profit: ...", font=("Segoe UI", 10, "bold"), fg="#2ecc71", bg="#252528")
        self.lbl_profit_preview.pack(pady=8)

        self.ent_qty.bind("<KeyRelease>", self.update_preview)
        self.ent_buy.bind("<KeyRelease>", self.update_preview)
        self.ent_nat.bind("<KeyRelease>", self.update_preview)
        self.update_preview()

        # Buttons
        btn_box = tk.Frame(self, bg="#252528")
        btn_box.pack(pady=10)

        tk.Button(btn_box, text="Save Changes", command=self.save, bg="#27ae60", fg="#ffffff", relief="flat", padx=10, cursor="hand2").pack(side="left", padx=6)
        tk.Button(btn_box, text="Cancel", command=self.destroy, bg="#7f8c8d", fg="#ffffff", relief="flat", padx=10, cursor="hand2").pack(side="left", padx=6)

    def update_preview(self, event=None):
        try:
            q = int(self.ent_qty.get().strip().replace(",", ""))
            b = int(self.ent_buy.get().strip().replace(",", ""))
            n = int(self.ent_nat.get().strip().replace(",", ""))
            alch_v = self.entry.get("alch_val", 0)
            profit_ea = alch_v - (b + n)
            total = q * profit_ea
            color = "#2ecc71" if total >= 0 else "#e74c3c"
            self.lbl_profit_preview.config(text=f"Realized Profit: {total:+,} gp ({profit_ea:+,} ea)", fg=color)
        except Exception:
            self.lbl_profit_preview.config(text="Realized Profit: [Invalid Input]", fg="#e74c3c")

    def save(self):
        try:
            q = int(self.ent_qty.get().strip().replace(",", ""))
            b = int(self.ent_buy.get().strip().replace(",", ""))
            n = int(self.ent_nat.get().strip().replace(",", ""))
            if q < 0 or b < 0 or n < 0:
                messagebox.showerror("Invalid Input", "Quantity and prices cannot be negative.")
                return
            self.on_save_callback(self.entry["id"], q, b, n)
            self.destroy()
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter valid whole numbers.")


class EditTimerDialog(tk.Toplevel):
    """Dialog to manually adjust quantity bought on an active 4h GE cooldown timer."""
    def __init__(self, parent, item_id, tinfo, on_save_callback):
        super().__init__(parent)
        self.title("Edit 4h GE Limit Timer")
        self.geometry("380x190")
        self.configure(bg="#252528")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self.item_id = item_id
        self.tinfo = tinfo
        self.on_save_callback = on_save_callback

        lbl_title = tk.Label(self, text=f"Edit Timer: {tinfo.get('name', 'Item')}", font=("Segoe UI", 11, "bold"), fg="#f39c12", bg="#252528")
        lbl_title.pack(pady=(15, 8))

        form = tk.Frame(self, bg="#252528")
        form.pack(padx=20, fill="x")

        tk.Label(form, text="Quantity Bought:", fg="#cccccc", bg="#252528").grid(row=0, column=0, sticky="w", pady=5)
        self.ent_qty = tk.Entry(form, bg="#1e1e1e", fg="#ffffff", insertbackground="#ffffff")
        self.ent_qty.insert(0, str(tinfo.get("qty", 0)))
        self.ent_qty.grid(row=0, column=1, pady=5, padx=5)

        tk.Label(form, text="💡 Set to 0 to clear this cooldown timer.", fg="#888888", bg="#252528", font=("Segoe UI", 8, "italic")).grid(row=1, column=0, columnspan=2, pady=(4, 0))

        btn_box = tk.Frame(self, bg="#252528")
        btn_box.pack(pady=15)

        tk.Button(btn_box, text="Save Changes", command=self.save, bg="#27ae60", fg="#ffffff", relief="flat", padx=10, cursor="hand2").pack(side="left", padx=6)
        tk.Button(btn_box, text="Cancel", command=self.destroy, bg="#7f8c8d", fg="#ffffff", relief="flat", padx=10, cursor="hand2").pack(side="left", padx=6)

        self.ent_qty.focus_set()
        self.ent_qty.select_range(0, tk.END)
        self.bind("<Return>", lambda e: self.save())
        self.bind("<Escape>", lambda e: self.destroy())

    def save(self):
        try:
            q = int(self.ent_qty.get().strip().replace(",", ""))
            if q < 0:
                messagebox.showerror("Invalid Input", "Quantity cannot be negative.")
                return
            self.on_save_callback(self.item_id, q)
            self.destroy()
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid whole number.")

class ToolTip:
    """Lightweight hover tooltip for widgets."""
    def __init__(self, widget, text, delay=350):
        self.widget = widget
        self.text = text
        self.delay = delay
        self.tip_window = None
        self.id = None
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.leave)
        self.widget.bind("<ButtonPress>", self.leave)

    def enter(self, event=None):
        self.schedule()

    def leave(self, event=None):
        self.unschedule()
        self.hide_tip()

    def schedule(self):
        self.unschedule()
        self.id = self.widget.after(self.delay, self.show_tip)

    def unschedule(self):
        if self.id:
            self.widget.after_cancel(self.id)
            self.id = None

    def show_tip(self):
        if self.tip_window or not self.text:
            return
        x = self.widget.winfo_rootx() + 15
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 5
        self.tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.attributes("-topmost", True)
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(tw, text=self.text, justify="left",
                         background="#181818", foreground="#f1f1f1",
                         relief="solid", borderwidth=1,
                         font=("Segoe UI", 8), padx=7, pady=4)
        label.pack()
        tw.lift()

    def hide_tip(self):
        if self.tip_window:
            self.tip_window.destroy()
            self.tip_window = None

class HeadingToolTip:
    """Dynamic hover tooltip for Treeview column headings."""
    def __init__(self, tree, col_tooltips_map, delay=300):
        self.tree = tree
        self.tooltips = col_tooltips_map
        self.delay = delay
        self.tip_window = None
        self.curr_col = None
        self.id = None
        self.tree.bind("<Motion>", self.on_motion, add="+")
        self.tree.bind("<Leave>", self.on_leave, add="+")

    def on_motion(self, event):
        region = self.tree.identify_region(event.x, event.y)
        if region == "heading":
            col = self.tree.identify_column(event.x)
            if col != self.curr_col:
                self.curr_col = col
                self.hide_tip()
                tip_text = self.tooltips.get(col)
                if tip_text:
                    x = self.tree.winfo_rootx() + event.x + 10
                    y = self.tree.winfo_rooty() + 25
                    if self.id:
                        self.tree.after_cancel(self.id)
                    self.id = self.tree.after(self.delay, lambda: self.show_tip(x, y, tip_text))
        else:
            self.on_leave()

    def on_leave(self, event=None):
        if self.id:
            self.tree.after_cancel(self.id)
            self.id = None
        self.curr_col = None
        self.hide_tip()

    def show_tip(self, x, y, text):
        if self.tip_window or not text:
            return
        self.tip_window = tw = tk.Toplevel(self.tree)
        tw.wm_overrideredirect(True)
        tw.attributes("-topmost", True)
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(tw, text=text, justify="left",
                         background="#181818", foreground="#f1f1f1",
                         relief="solid", borderwidth=1,
                         font=("Segoe UI", 8), padx=7, pady=4)
        label.pack()
        tw.lift()

    def hide_tip(self):
        if self.tip_window:
            self.tip_window.destroy()
            self.tip_window = None

class RowToolTip:
    """Dynamic hover tooltip card for Treeview data rows."""
    def __init__(self, tree, get_tooltip_callback, delay=400):
        self.tree = tree
        self.get_tooltip_callback = get_tooltip_callback
        self.delay = delay
        self.tip_window = None
        self.curr_iid = None
        self.id = None
        self.tree.bind("<Motion>", self.on_motion, add="+")
        self.tree.bind("<Leave>", self.on_leave, add="+")
        self.tree.bind("<ButtonPress>", self.on_leave, add="+")
        self.tree.bind("<MouseWheel>", self.on_leave, add="+")

    def on_motion(self, event):
        region = self.tree.identify_region(event.x, event.y)
        if region in ("cell", "tree"):
            iid = self.tree.identify_row(event.y)
            if iid and iid != self.curr_iid:
                self.curr_iid = iid
                self.hide_tip()
                if self.id:
                    self.tree.after_cancel(self.id)
                gx = event.x_root
                gy = event.y_root
                self.id = self.tree.after(self.delay, lambda: self.show_tip(gx, gy, iid))
            elif not iid:
                self.on_leave()
        else:
            self.on_leave()

    def on_leave(self, event=None):
        if self.id:
            self.tree.after_cancel(self.id)
            self.id = None
        self.curr_iid = None
        self.hide_tip()

    def show_tip(self, mouse_x, mouse_y, iid):
        if self.tip_window or not iid:
            return
        tip_info = self.get_tooltip_callback(iid)
        if not tip_info:
            return

        try:
            self.tip_window = tw = tk.Toplevel(self.tree)
            tw.wm_overrideredirect(True)
            tw.attributes("-topmost", True)

            border_col = "#e67e22" if tip_info.get("has_warning") else "#4a4a52"
            card = tk.Frame(tw, bg="#1a1a1d", highlightthickness=1,
                            highlightbackground=border_col, padx=12, pady=9)
            card.pack()

            # Title
            title_box = tk.Frame(card, bg="#1a1a1d")
            title_box.pack(fill="x", pady=(0, 4))
            tk.Label(title_box, text=tip_info.get("title", ""), font=("Segoe UI", 9, "bold"),
                     fg=tip_info.get("title_color", "#f1c40f"), bg="#1a1a1d").pack(side="left")
            if tip_info.get("subtitle"):
                tk.Label(title_box, text=f" ({tip_info['subtitle']})", font=("Segoe UI", 8),
                         fg="#888888", bg="#1a1a1d").pack(side="left")

            tk.Frame(card, bg="#2f2f35", height=1).pack(fill="x", pady=(2, 6))

            # Metric Rows
            for label_text, val_text, val_color in tip_info.get("rows", []):
                rf = tk.Frame(card, bg="#1a1a1d")
                rf.pack(fill="x", pady=1)
                tk.Label(rf, text=label_text, font=("Segoe UI", 8), fg="#9e9ea7",
                         bg="#1a1a1d", width=23, anchor="w").pack(side="left")
                is_num = any(char.isdigit() for char in val_text)
                tk.Label(rf, text=val_text, font=("Segoe UI", 8, "bold" if is_num else "normal"),
                         fg=val_color, bg="#1a1a1d", anchor="e").pack(side="right")

            # Warnings
            warnings = tip_info.get("warnings", [])
            if warnings:
                tk.Frame(card, bg="#2f2f35", height=1).pack(fill="x", pady=(5, 5))
                for w in warnings:
                    tk.Label(card, text=f"⚠️ {w}", font=("Segoe UI", 8, "bold"),
                             fg="#e67e22", bg="#1a1a1d", wraplength=340, justify="left", anchor="w").pack(fill="x", pady=1)

            # Footer
            if tip_info.get("hint"):
                tk.Frame(card, bg="#2f2f35", height=1).pack(fill="x", pady=(5, 3))
                tk.Label(card, text=tip_info["hint"], font=("Segoe UI", 7, "italic"),
                         fg="#6e6e77", bg="#1a1a1d", anchor="w").pack(fill="x")

            tw.update_idletasks()
            w = tw.winfo_reqwidth()
            h = tw.winfo_reqheight()

            # Bound STRICTLY inside the application window boundaries across multi-monitors
            app = self.tree.winfo_toplevel()
            app_x = app.winfo_rootx()
            app_y = app.winfo_rooty()
            app_w = app.winfo_width()
            app_h = app.winfo_height()

            # Default offset: slightly to the right and below the cursor
            x = mouse_x + 18
            y = mouse_y + 12

            # Keep inside horizontal bounds of app
            if x + w > app_x + app_w - 15:
                x = mouse_x - w - 15
            if x < app_x + 10:
                x = app_x + 10

            # Keep inside vertical bounds of app
            if y + h > app_y + app_h - 15:
                y = mouse_y - h - 10
            if y < app_y + 35:
                y = app_y + 35

            tw.wm_geometry(f"+{x}+{y}")
            tw.lift()
        except Exception:
            self.hide_tip()

    def hide_tip(self):
        if self.tip_window:
            try:
                self.tip_window.destroy()
            except Exception:
                pass
            self.tip_window = None

class SetQuantityDialog(tk.Toplevel):
    def __init__(self, parent, item_name, current_qty, max_allowed, on_save):
        super().__init__(parent)
        self.title(f"Set Quantity - {item_name}")
        self.geometry("320x165")
        self.configure(bg="#252528")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self.on_save = on_save
        self.max_allowed = max_allowed

        # Center dialog
        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - 160
        y = parent.winfo_y() + (parent.winfo_height() // 2) - 85
        self.geometry(f"+{x}+{y}")

        tk.Label(self, text="Set Cart Quantity for:", fg="#aaaaaa", bg="#252528", font=("Segoe UI", 9)).pack(pady=(10, 2))
        tk.Label(self, text=item_name, fg="#f39c12", bg="#252528", font=("Segoe UI", 10, "bold")).pack()
        tk.Label(self, text=f"(Max allowed: {max_allowed:,})", fg="#888888", bg="#252528", font=("Segoe UI", 8)).pack(pady=(0, 6))

        f = tk.Frame(self, bg="#252528")
        f.pack(pady=4)
        self.ent = tk.Entry(f, width=10, bg="#1e1e1e", fg="#2ecc71", font=("Segoe UI", 10, "bold"), insertbackground="#ffffff", justify="center")
        self.ent.insert(0, str(current_qty))
        self.ent.pack()
        self.ent.focus_set()
        self.ent.select_range(0, tk.END)

        btn_box = tk.Frame(self, bg="#252528")
        btn_box.pack(pady=10)
        tk.Button(btn_box, text="Set Quantity", command=self.save, bg="#27ae60", fg="#ffffff", relief="flat", padx=8, cursor="hand2").pack(side="left", padx=4)
        tk.Button(btn_box, text="Remove", command=self.remove, bg="#c0392b", fg="#ffffff", relief="flat", padx=6, cursor="hand2").pack(side="left", padx=4)
        tk.Button(btn_box, text="Cancel", command=self.destroy, bg="#7f8c8d", fg="#ffffff", relief="flat", padx=6, cursor="hand2").pack(side="left", padx=4)

        self.bind("<Return>", lambda e: self.save())
        self.bind("<Escape>", lambda e: self.destroy())

    def save(self):
        try:
            val = int(self.ent.get().strip().replace(",", ""))
            if val <= 0:
                self.on_save(0)
            else:
                val = min(val, self.max_allowed)
                self.on_save(val)
            self.destroy()
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid whole number.")

    def remove(self):
        self.on_save(0)
        self.destroy()

W308_STAPLES = [
    {"id": 1319, "name": "Rune 2h sword", "alch": 38400, "w308_buy": 37600, "w308_sell_p2p": 37875, "short": "R2H", "members": False,
     "skill": "Smithing", "level": 99, "xp": 225.0, "mat_id": 2363, "mat_name": "Runite bar", "mat_qty": 3, "mat_default": 12175},
    {"id": 1079, "name": "Rune platelegs", "alch": 38400, "w308_buy": 37600, "w308_sell_p2p": 37875, "short": "R Legs", "members": False,
     "skill": "Smithing", "level": 99, "xp": 225.0, "mat_id": 2363, "mat_name": "Runite bar", "mat_qty": 3, "mat_default": 12175},
    {"id": 1093, "name": "Rune plateskirt", "alch": 38400, "w308_buy": 37600, "w308_sell_p2p": 37875, "short": "R Skirts", "members": False,
     "skill": "Smithing", "level": 99, "xp": 225.0, "mat_id": 2363, "mat_name": "Runite bar", "mat_qty": 3, "mat_default": 12175},
    {"id": 1113, "name": "Rune chainbody", "alch": 30000, "w308_buy": 29350, "w308_sell_p2p": 29500, "short": "R Chain", "members": False,
     "skill": "Smithing", "level": 96, "xp": 225.0, "mat_id": 2363, "mat_name": "Runite bar", "mat_qty": 3, "mat_default": 12175},
    {"id": 1373, "name": "Rune battleaxe", "alch": 24960, "w308_buy": 24400, "w308_sell_p2p": 24550, "short": "R Baxe", "members": False,
     "skill": "Smithing", "level": 95, "xp": 225.0, "mat_id": 2363, "mat_name": "Runite bar", "mat_qty": 3, "mat_default": 12175},
    {"id": 1185, "name": "Rune sq shield", "alch": 23040, "w308_buy": 22500, "w308_sell_p2p": 22650, "short": "R Sq", "members": False,
     "skill": "Smithing", "level": 93, "xp": 150.0, "mat_id": 2363, "mat_name": "Runite bar", "mat_qty": 2, "mat_default": 12175},
    {"id": 1275, "name": "Rune pickaxe", "alch": 19200, "w308_buy": 18750, "w308_sell_p2p": 18850, "short": "R Pick", "members": False,
     "skill": None, "level": 0, "xp": 0.0, "mat_id": None, "mat_name": None, "mat_qty": 0, "mat_default": 0},
    {"id": 1333, "name": "Rune scimitar", "alch": 15360, "w308_buy": 15000, "w308_sell_p2p": 15100, "short": "R Scim", "members": False,
     "skill": "Smithing", "level": 90, "xp": 150.0, "mat_id": 2363, "mat_name": "Runite bar", "mat_qty": 2, "mat_default": 12175},
    {"id": 1289, "name": "Rune sword", "alch": 12480, "w308_buy": 12200, "w308_sell_p2p": 12250, "short": "R Sword", "members": False,
     "skill": "Smithing", "level": 89, "xp": 75.0, "mat_id": 2363, "mat_name": "Runite bar", "mat_qty": 1, "mat_default": 12175},
    {"id": 1147, "name": "Rune med helm", "alch": 11520, "w308_buy": 11250, "w308_sell_p2p": 11300, "short": "R Med", "members": False,
     "skill": "Smithing", "level": 88, "xp": 75.0, "mat_id": 2363, "mat_name": "Runite bar", "mat_qty": 1, "mat_default": 12175},
    {"id": 1213, "name": "Rune dagger", "alch": 4800, "w308_buy": 4600, "w308_sell_p2p": 4650, "short": "R Dagger", "members": False,
     "skill": "Smithing", "level": 85, "xp": 75.0, "mat_id": 2363, "mat_name": "Runite bar", "mat_qty": 1, "mat_default": 12175},
    {"id": 1123, "name": "Adamant platebody", "alch": 9984, "w308_buy": 9650, "w308_sell_p2p": 9750, "short": "Addy Body", "members": False,
     "skill": "Smithing", "level": 88, "xp": 312.5, "mat_id": 2361, "mat_name": "Adamantite bar", "mat_qty": 5, "mat_default": 1883},
    {"id": 1121, "name": "Mithril platebody", "alch": 3120, "w308_buy": 2900, "w308_sell_p2p": 2950, "short": "Mith Body", "members": False,
     "skill": "Smithing", "level": 68, "xp": 250.0, "mat_id": 2359, "mat_name": "Mithril bar", "mat_qty": 5, "mat_default": 956},
    {"id": 1397, "name": "Air battlestaff", "alch": 9300, "w308_buy": 8950, "w308_sell_p2p": 9050, "short": "Air Bstaff", "members": True,
     "skill": "Crafting", "level": 66, "xp": 137.5, "mat_id": 1391, "mat_name": "Battlestaff", "mat_qty": 1, "mat_default": 7817,
     "mat2_id": 573, "mat2_name": "Air orb", "mat2_qty": 1, "mat2_default": 1120},
    {"id": 1393, "name": "Fire battlestaff", "alch": 9300, "w308_buy": 8950, "w308_sell_p2p": 9050, "short": "Fire Bstaff", "members": True,
     "skill": "Crafting", "level": 62, "xp": 125.0, "mat_id": 1391, "mat_name": "Battlestaff", "mat_qty": 1, "mat_default": 7817,
     "mat2_id": 569, "mat2_name": "Fire orb", "mat2_qty": 1, "mat2_default": 1175},
    {"id": 1395, "name": "Water battlestaff", "alch": 9300, "w308_buy": 8900, "w308_sell_p2p": 9000, "short": "Water Bstaff", "members": True,
     "skill": "Crafting", "level": 54, "xp": 100.0, "mat_id": 1391, "mat_name": "Battlestaff", "mat_qty": 1, "mat_default": 7817,
     "mat2_id": 571, "mat2_name": "Water orb", "mat2_qty": 1, "mat2_default": 800},
    {"id": 1399, "name": "Earth battlestaff", "alch": 9300, "w308_buy": 8850, "w308_sell_p2p": 8950, "short": "Earth Bstaff", "members": True,
     "skill": "Crafting", "level": 58, "xp": 112.5, "mat_id": 1391, "mat_name": "Battlestaff", "mat_qty": 1, "mat_default": 7817,
     "mat2_id": 575, "mat2_name": "Earth orb", "mat2_qty": 1, "mat2_default": 800},
    {"id": 2503, "name": "Black d'hide body", "alch": 8085, "w308_buy": 7750, "w308_sell_p2p": 7850, "short": "Black Dhide", "members": True,
     "skill": "Crafting", "level": 84, "xp": 258.0, "mat_id": 2509, "mat_name": "Black dragon leather", "mat_qty": 3, "mat_default": 2500},
    {"id": 2501, "name": "Red d'hide body", "alch": 6738, "w308_buy": 6450, "w308_sell_p2p": 6550, "short": "Red Dhide", "members": True,
     "skill": "Crafting", "level": 77, "xp": 234.0, "mat_id": 2507, "mat_name": "Red dragon leather", "mat_qty": 3, "mat_default": 2100},
    {"id": 2499, "name": "Blue d'hide body", "alch": 5616, "w308_buy": 5350, "w308_sell_p2p": 5450, "short": "Blue Dhide", "members": True,
     "skill": "Crafting", "level": 71, "xp": 210.0, "mat_id": 2505, "mat_name": "Blue dragon leather", "mat_qty": 3, "mat_default": 1700},
    {"id": 1135, "name": "Green d'hide body", "alch": 4680, "w308_buy": 4450, "w308_sell_p2p": 4550, "short": "Green Dhide", "members": True,
     "skill": "Crafting", "level": 63, "xp": 186.0, "mat_id": 1745, "mat_name": "Green dragon leather", "mat_qty": 3, "mat_default": 1400},
    {"id": 859, "name": "Magic longbow", "alch": 1536, "w308_buy": 1200, "w308_sell_p2p": 1300, "short": "Mage Long", "members": True,
     "skill": "Fletching", "level": 85, "xp": 91.5, "mat_id": 70, "mat_name": "Magic longbow (u)", "mat_qty": 1, "mat_default": 704,
     "mat2_id": 1777, "mat2_name": "Bow string", "mat2_qty": 1, "mat2_default": 242},
    {"id": 855, "name": "Yew longbow", "alch": 768, "w308_buy": 600, "w308_sell_p2p": 650, "short": "Yew Long", "members": True,
     "skill": "Fletching", "level": 70, "xp": 75.0, "mat_id": 66, "mat_name": "Yew longbow (u)", "mat_qty": 1, "mat_default": 170,
     "mat2_id": 1777, "mat2_name": "Bow string", "mat2_qty": 1, "mat2_default": 242},
    {"id": 11115, "name": "Dragonstone bracelet", "alch": 11475, "w308_buy": 11350, "w308_sell_p2p": 11400, "short": "Dstone Brac", "members": True,
     "skill": "Crafting", "level": 74, "xp": 110.0, "mat_id": 1615, "mat_name": "Dragonstone", "mat_qty": 1, "mat_default": 10789,
     "mat2_id": 2357, "mat2_name": "Gold bar", "mat2_qty": 1, "mat2_default": 69},
    {"id": 11092, "name": "Diamond bracelet", "alch": 2295, "w308_buy": 1950, "w308_sell_p2p": 2050, "short": "Dia Brac", "members": True,
     "skill": "Crafting", "level": 58, "xp": 95.0, "mat_id": 1601, "mat_name": "Diamond", "mat_qty": 1, "mat_default": 1575,
     "mat2_id": 2357, "mat2_name": "Gold bar", "mat2_qty": 1, "mat2_default": 69},
    {"id": 11085, "name": "Ruby bracelet", "alch": 1395, "w308_buy": 1100, "w308_sell_p2p": 1150, "short": "Ruby Brac", "members": True,
     "skill": "Crafting", "level": 42, "xp": 80.0, "mat_id": 1603, "mat_name": "Ruby", "mat_qty": 1, "mat_default": 713,
     "mat2_id": 2357, "mat2_name": "Gold bar", "mat2_qty": 1, "mat2_default": 69},
    {"id": 1215, "name": "Dragon dagger", "alch": 18000, "w308_buy": 17300, "w308_sell_p2p": 17500, "short": "DDS", "members": True,
     "skill": None, "level": 0, "xp": 0.0, "mat_id": None, "mat_name": None, "mat_qty": 0, "mat_default": 0},
    {"id": 9245, "name": "Onyx bolts (e)", "alch": 9000, "w308_buy": 8550, "w308_sell_p2p": 8650, "short": "Onyx Bolts", "members": True,
     "skill": None, "level": 0, "xp": 0.0, "mat_id": None, "mat_name": None, "mat_qty": 0, "mat_default": 0},
]

class OSRSAlchDashboard(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("AlchMate - OSRS High Alchemy & Crafting Profit Dashboard")
        self.geometry("1280x780")
        self.minsize(1020, 620)

        # App state & API
        self.state = AppState()
        self.api = OSRSPricesAPI()

        # Runtime data
        self.alch_rows = []
        self.craft_rows = []
        self.rec_rows = []
        self.bond_data = {}
        self.is_fetching = False
        self.seconds_until_refresh = self.state.config.get("auto_refresh_mins", 2) * 60

        # Sorting states: {col_name: descending_bool}
        self.alch_sort_col = "profit_ea"
        self.alch_sort_desc = True

        self.craft_sort_col = "profit_ea"
        self.craft_sort_desc = True

        self.rec_sort_col = "profit_ea"
        self.rec_sort_desc = True

        self.session_sort_col = "time"
        self.session_sort_desc = True
        self.session_view_mode = self.state.config.get("session_view_mode", "consolidated")
        self.w308_rows = []
        self.w308_sort_col = "profit_ea"
        self.w308_sort_desc = True

        # Clipboard copy feedback
        self.clipboard_clear_timer = None

        self.bridge_port = int(self.state.config.get("bridge_port", 18833))

        self.setup_styles()
        self.build_ui()

        # Keyboard shortcuts
        self.bind("<F5>", lambda e: self.trigger_refresh())
        self.bind("<Control-f>", lambda e: self.focus_search())
        self.bind("<Control-F>", lambda e: self.focus_search())

        # Start timer tick
        self.after(1000, self.timer_tick)

        # Window close protocol (prompts if update available)
        self.protocol("WM_DELETE_WINDOW", self.on_app_close)

        # Update checker
        self.latest_update_info = None
        self.after(2000, lambda: threading.Thread(target=self._check_update_startup, daemon=True).start())

        # Check if app was just updated to show "What's New" popup
        self.after(800, self._check_first_run_after_update)

        # Ensure plugin is deployed to .runelite plugin directories if present
        self._ensure_plugin_deployed()

        # Bridge Server for RuneLite live sync
        self._logged_ge_offers = set()
        self._ge_cart_slots = {}
        self._ge_tracked_items = set()
        self._ge_slot_progress = {}

        # Immediate sync from local container exports and active account data
        self._sync_from_container_export()
        self._apply_active_account_data()

        self.bridge_port = int(self.state.config.get("bridge_port", 18833))
        self.bridge_server = BridgeServer(port=self.bridge_port, event_callback=self._on_bridge_event_async)
        self.bridge_server.start()

    def _ensure_plugin_deployed(self):
        """Ensures AlchBridgePlugin.jar is deployed into .runelite plugin directories if present."""
        try:
            user_home = os.path.expanduser("~")
            runelite_dir = os.path.join(user_home, ".runelite")
            if not os.path.exists(runelite_dir):
                return

            app_dir = os.path.dirname(os.path.abspath(__file__))
            exe_dir = os.path.dirname(os.path.abspath(sys.executable)) if getattr(sys, "frozen", False) else app_dir

            sources = [
                os.path.join(app_dir, "bridge_plugin", "AlchBridgePlugin.jar"),
                os.path.join(exe_dir, "plugins", "AlchBridgePlugin.jar"),
                os.path.join(exe_dir, "bridge_plugin", "AlchBridgePlugin.jar")
            ]

            valid_src = None
            for src in sources:
                if os.path.exists(src):
                    valid_src = src
                    break

            if not valid_src:
                return

            dest_dirs = []
            std_plugins = os.path.join(runelite_dir, "plugins")
            if os.path.exists(std_plugins):
                dest_dirs.append(std_plugins)

            for entry in glob.glob(os.path.join(runelite_dir, "*plugins*")):
                if os.path.isdir(entry) and entry not in dest_dirs:
                    dest_dirs.append(entry)

            for d in dest_dirs:
                try:
                    dest_jar = os.path.join(d, "AlchBridgePlugin.jar")
                    if not os.path.exists(dest_jar) or (os.path.getmtime(valid_src) > os.path.getmtime(dest_jar)):
                        shutil.copy2(valid_src, dest_jar)
                except Exception:
                    pass
        except Exception:
            pass

        # Initial load in background thread
        self.trigger_refresh()

    def _sync_from_container_export(self, force=False):
        """Reads RuneLite container_inventory.json and container_bank.json if available. Returns True if data changed."""
        try:
            inv_path = os.path.expanduser(r"~/.runelite/Data Exports/container_inventory.json")
            if not os.path.exists(inv_path):
                return False

            inv_mtime = os.path.getmtime(inv_path)
            last_mtime = getattr(self, "_last_inv_mtime", 0)
            if not force and inv_mtime == last_mtime:
                return False
            self._last_inv_mtime = inv_mtime

            coins = None
            nats = None
            detected_staples = {}
            with open(inv_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        item = json.loads(line)
                        iid = item.get("id")
                        qty = item.get("quantity", 0)
                        name = item.get("name", "")
                        if iid == 995 or name == "Coins":
                            coins = qty
                        elif iid == 561 or name == "Nature rune":
                            nats = qty
                        elif qty > 0 and (name in ("Rune 2h sword", "Rune platelegs", "Rune plateskirt", "Adamant platebody", "Rune battleaxe", "Green d'hide body", "Air battlestaff") or iid in (1320, 1080, 1094, 1124, 1374)):
                            detected_staples[name] = {"id": iid, "qty": qty, "name": name}
                    except Exception:
                        continue

            bank_path = os.path.expanduser(r"~/.runelite/Data Exports/container_bank.json")
            bank_coins = None
            bank_nats = None
            if os.path.exists(bank_path):
                try:
                    with open(bank_path, "r", encoding="utf-8") as f:
                        for line in f:
                            line = line.strip()
                            if not line:
                                continue
                            try:
                                item = json.loads(line)
                                iid = item.get("id")
                                qty = item.get("quantity", 0)
                                name = item.get("name", "")
                                if iid == 995 or name == "Coins":
                                    bank_coins = qty
                                elif iid == 561 or name == "Nature rune":
                                    bank_nats = qty
                            except Exception:
                                continue
                except Exception:
                    pass

            sel = self.var_account.get() if hasattr(self, "var_account") else "All Accounts"
            acc_name = sel if (sel and sel != "All Accounts") else (self.state.config.get("monitored_character") or "Default")
            if acc_name == "All Accounts":
                acc_name = "Default" if not self.state.accounts else sorted(list(self.state.accounts.keys()))[0]

            acc_data = self.state.accounts.setdefault(acc_name, {"name": acc_name})
            # If account is actively receiving authoritative live bridge events, do not overwrite unless forced
            if not force and (time.time() - acc_data.get("last_seen", 0)) < 60:
                return False

            changed = False

            if coins is not None and acc_data.get("coins") != coins:
                acc_data["coins"] = coins
                changed = True
            if nats is not None and acc_data.get("nature_runes") != nats:
                acc_data["nature_runes"] = nats
                changed = True
            if bank_coins is not None and acc_data.get("bank_coins") != bank_coins:
                acc_data["bank_coins"] = bank_coins
                changed = True
            if bank_nats is not None and acc_data.get("bank_nats") != bank_nats:
                acc_data["bank_nats"] = bank_nats
                changed = True

            if detected_staples:
                best_st = max(detected_staples.values(), key=lambda s: s["qty"])
                clean_name = best_st["name"].replace(" (noted)", "")
                acc_data["batch_item_name"] = clean_name
                acc_data["batch_item_qty"] = best_st["qty"]
                changed = True

            if changed or force:
                self.state.save_accounts()
            return changed or force
        except Exception:
            return False

    def setup_styles(self):
        self.configure(bg="#1e1e1e")
        style = ttk.Style(self)
        style.theme_use("clam")

        # Global Dark Theme Options
        style.configure(".", background="#1e1e1e", foreground="#ffffff", font=("Segoe UI", 9))
        style.configure("TFrame", background="#1e1e1e")
        style.configure("Card.TFrame", background="#252528", relief="solid", borderwidth=1)
        style.configure("TopBar.TFrame", background="#252528")

        # High Contrast Combobox Theme (Fixes unreadable white text)
        style.configure("TCombobox",
            background="#2d2d30",
            foreground="#ffffff",
            fieldbackground="#1e1e1e",
            darkcolor="#1e1e1e",
            lightcolor="#3e3e42",
            bordercolor="#3e3e42",
            arrowcolor="#f39c12",
            padding=[4, 2]
        )
        style.map("TCombobox",
            fieldbackground=[("readonly", "#1e1e1e"), ("active", "#252528")],
            foreground=[("readonly", "#ffffff"), ("active", "#ffffff")],
            selectbackground=[("readonly", "#38383e")],
            selectforeground=[("readonly", "#f39c12")]
        )

        # Force dark listbox for dropdown menus
        self.option_add("*TCombobox*Listbox.background", "#252528")
        self.option_add("*TCombobox*Listbox.foreground", "#ffffff")
        self.option_add("*TCombobox*Listbox.selectBackground", "#f39c12")
        self.option_add("*TCombobox*Listbox.selectForeground", "#000000")
        self.option_add("*TCombobox*Listbox.font", ("Segoe UI", 9))

        # Tabs
        style.configure("TNotebook", background="#1e1e1e", borderwidth=0)
        style.configure("TNotebook.Tab", background="#2d2d30", foreground="#cccccc", padding=[16, 6], font=("Segoe UI", 10, "bold"))
        style.map("TNotebook.Tab",
            background=[("selected", "#3e3e42"), ("active", "#353538")],
            foreground=[("selected", "#f39c12"), ("active", "#ffffff")]
        )

        # Treeview (Tables)
        style.configure("Treeview",
            background="#252528",
            foreground="#f1f1f1",
            fieldbackground="#252528",
            rowheight=26,
            bordercolor="#3e3e42",
            font=("Segoe UI", 9)
        )
        style.configure("Treeview.Heading",
            background="#2d2d30",
            foreground="#f39c12",
            relief="flat",
            font=("Segoe UI", 9, "bold"),
            padding=[4, 6]
        )
        style.map("Treeview",
            background=[("selected", "#38383e")],
            foreground=[("selected", "#f39c12")]
        )
        style.map("Treeview.Heading",
            background=[("active", "#3a3a3e")]
        )

        style.configure("Vertical.TScrollbar", background="#2d2d30", troughcolor="#1e1e1e", borderwidth=0, arrowcolor="#cccccc")
        style.configure("Horizontal.TScrollbar", background="#2d2d30", troughcolor="#1e1e1e", borderwidth=0, arrowcolor="#cccccc")
        style.configure("TScrollbar", background="#2d2d30", troughcolor="#1e1e1e", borderwidth=0, arrowcolor="#cccccc")

    def build_ui(self):
        # 1. Top Control Strip
        self.top_frame = ttk.Frame(self, style="TopBar.TFrame")
        self.top_frame.pack(fill="x", padx=10, pady=(10, 5))
        self.build_top_controls()

        # 2. Prominent Nature Rune & Shopping Cart Bar
        self.sub_bar = ttk.Frame(self, style="Card.TFrame")
        self.sub_bar.pack(fill="x", padx=10, pady=5)
        self.build_sub_bar()

        # 3. Main Notebook (5 Consolidated Super-Hubs)
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=5)
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)

        # Hub 1: 🔮 High Alchemy & Trading Hub
        self.tab_hub_alch = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_hub_alch, text="🔮 High Alch & Trading")
        self.build_alch_hub()

        # Hub 2: 🔨 Crafting & Production Workshop
        self.tab_hub_craft = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_hub_craft, text="🔨 Crafting Workshop")
        self.build_craft_hub()

        # Hub 3: 🎟️ Bond Roadmap & Freedom Engine
        self.tab_bond = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_bond, text="🎟️ Bond Roadmap")
        self.build_bond_tab()

        # Hub 4: ⏱️ 4h GE Limit Timers
        self.tab_timers = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_timers, text="⏱️ 4h GE Timers")
        self.build_timers_tab()

        # Hub 5: 📊 Session & Activity Center
        self.tab_hub_activity = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_hub_activity, text="📊 Session & Activity")
        self.build_activity_hub()

        # 4. Bottom Status Bar
        self.status_bar = tk.Frame(self, bg="#181818", height=28)
        self.status_bar.pack(fill="x", side="bottom")
        self.build_status_bar()

    def build_top_controls(self):
        # Row 1: Essential Controls (Always Visible)
        p1 = tk.Frame(self.top_frame, bg="#252528")
        p1.pack(fill="x", padx=8, pady=(4, 2))

        # Search Bar
        tk.Label(p1, text="🔍", fg="#f39c12", bg="#252528").pack(side="left", padx=(2, 1))
        self.ent_search = tk.Entry(p1, width=14, bg="#1e1e1e", fg="#ffffff", insertbackground="#ffffff", relief="flat")
        self.ent_search.pack(side="left", padx=(1, 8))
        self.ent_search.bind("<KeyRelease>", self.on_global_search_changed)
        self.ent_search.bind("<Escape>", lambda e: self.clear_search())
        ToolTip(self.ent_search, "Universal search across ALL tabs (Alch, Smart Picks, Craft, Guide, Timers, History). Press Esc to clear, Ctrl+F to focus.")

        # Cash Stack
        self.var_use_cash = tk.BooleanVar(value=self.state.config.get("use_cash_stack", True))
        self.cb_cash = tk.Checkbutton(p1, text="Cash:", variable=self.var_use_cash, command=self.on_cash_toggle_changed,
                                      bg="#252528", fg="#cccccc", selectcolor="#2d2d30", activebackground="#252528", activeforeground="#2ecc71")
        self.cb_cash.pack(side="left", padx=(2, 0))
        ToolTip(self.cb_cash, "Toggle budget constraint. Uncheck for unlimited cash.")

        self.ent_cash = tk.Entry(p1, width=8, bg="#1e1e1e", fg="#2ecc71", insertbackground="#ffffff", relief="flat")
        self.ent_cash.insert(0, format_gp(self.state.config.get("cash_stack", 5000000)))
        if not self.var_use_cash.get():
            self.ent_cash.config(state="disabled")
        self.ent_cash.pack(side="left", padx=(1, 8))
        self.ent_cash.bind("<FocusOut>", self.on_cash_changed)
        self.ent_cash.bind("<Return>", self.on_cash_changed)
        ToolTip(self.ent_cash, "Your current in-game cash stack. Supports 900k, 1.5m, etc.")

        # Mode: Members / F2P
        self.var_members = tk.BooleanVar(value=self.state.config.get("members", True))
        self.var_f2p = tk.BooleanVar(value=self.state.config.get("f2p", False))

        cb_mem = tk.Checkbutton(p1, text="Members", variable=self.var_members, command=self.on_members_clicked,
                                bg="#252528", fg="#f1f1f1", selectcolor="#2d2d30", activebackground="#252528", activeforeground="#f39c12")
        cb_mem.pack(side="left", padx=2)
        ToolTip(cb_mem, "Members Mode (P2P):\nShows all tradeable items and skilling methods (both P2P items and F2P staples).")

        cb_f2p = tk.Checkbutton(p1, text="F2P Only", variable=self.var_f2p, command=self.on_f2p_clicked,
                                bg="#252528", fg="#f1f1f1", selectcolor="#2d2d30", activebackground="#252528", activeforeground="#2ecc71")
        cb_f2p.pack(side="left", padx=2)
        ToolTip(cb_f2p, "Free-to-Play Mode (F2P Only):\nStrictly filters to F2P items, recipes, quests, and brackets only.")

        tk.Label(p1, text="|", fg="#444444", bg="#252528").pack(side="left", padx=6)

        # Strategy Combobox
        lbl_strat = tk.Label(p1, text="Strategy:", fg="#cccccc", bg="#252528")
        lbl_strat.pack(side="left")
        ToolTip(lbl_strat, "Select your buy pricing strategy on the Grand Exchange.")

        curr_strat = self.state.config.get("strategy", "patient")
        strat_display = "smart (Bid+1)" if curr_strat == "smart" else ("instant (Ask)" if curr_strat == "instant" else "patient (Bid)")
        self.var_strat = tk.StringVar(value=strat_display)
        cb_strat = ttk.Combobox(p1, textvariable=self.var_strat, values=["patient (Bid)", "smart (Bid+1)", "instant (Ask)"], width=13, state="readonly")
        cb_strat.pack(side="left", padx=(2, 6))
        cb_strat.bind("<<ComboboxSelected>>", self.on_strategy_changed)
        ToolTip(cb_strat, "patient (Bid) = Lowest price, maximum profit.\nsmart (Bid+1) = Bid + 1 gp for top queue priority.\ninstant (Ask) = Instant fill.")

        # Pinned Actions on Right of Row 1
        self.btn_update = tk.Button(p1, text=f"⚡ v{APP_VERSION}", command=self.on_update_button_click,
                                    bg="#2d2d30", fg="#3498db", font=("Segoe UI", 8, "bold"), relief="flat", padx=8, pady=1, cursor="hand2")
        self.btn_update.pack(side="right", padx=(4, 0))
        ToolTip(self.btn_update, f"OSRS Tracker v{APP_VERSION}.\nClick to check GitHub for updates.")

        self.btn_refresh = tk.Button(p1, text="🔄 Refresh Now", command=self.trigger_refresh,
                                     bg="#f39c12", fg="#000000", font=("Segoe UI", 8, "bold"), relief="flat", padx=10, pady=1, cursor="hand2")
        self.btn_refresh.pack(side="right", padx=(4, 2))
        ToolTip(self.btn_refresh, "Fetch latest live prices from OSRS Wiki API. Shortcut: F5")

        self.lbl_countdown = tk.Label(p1, text="(Next: 02:00)", fg="#888888", bg="#252528", font=("Segoe UI", 8))
        self.lbl_countdown.pack(side="right", padx=(0, 4))
        ToolTip(self.lbl_countdown, "Time until next automatic price sync with OSRS Wiki.")

        self.lbl_bridge_status = tk.Label(p1, text="🟢 Bridge", fg="#2ecc71", bg="#252528", font=("Segoe UI", 8, "bold"), cursor="hand2")
        self.lbl_bridge_status.pack(side="right", padx=(2, 8))
        self.lbl_bridge_status.bind("<Button-1>", lambda e: self.open_bridge_settings_dialog())
        ToolTip(self.lbl_bridge_status, f"RuneLite Bridge:\nListening on 127.0.0.1:{self.bridge_port} for live GE trades, 4h cooldown timers, coins, and nature runes.\nClick to change port, test connection, or resync.")

        # Expandable Filters Drawer Button
        self.show_filters_drawer = self.state.config.get("show_advanced_filters", False)
        filter_btn_text = "⚙️ Filters ▴" if self.show_filters_drawer else "⚙️ Filters ▾"
        filter_btn_bg = "#3e3e42" if self.show_filters_drawer else "#252528"
        self.btn_toggle_filters = tk.Button(p1, text=filter_btn_text, command=self.toggle_filters_drawer,
                                            bg=filter_btn_bg, fg="#f39c12", font=("Segoe UI", 8, "bold"), relief="flat", padx=8, pady=1, cursor="hand2")
        self.btn_toggle_filters.pack(side="right", padx=(2, 6))
        ToolTip(self.btn_toggle_filters, "Toggle Advanced Filters Drawer (Min Vol, Max Spend, Min Profit, Speed, Audio/Popups, Monitor).")

        # Row 2: Collapsible Filters Drawer
        self.p2 = tk.Frame(self.top_frame, bg="#202023", relief="solid", borderwidth=1, padx=6, pady=4)

        # Max Item Spend
        tk.Label(self.p2, text="Max Spend:", fg="#cccccc", bg="#202023").pack(side="left")
        self.ent_max_spend = tk.Entry(self.p2, width=7, bg="#1e1e1e", fg="#f1f1f1", insertbackground="#ffffff", relief="flat")
        self.ent_max_spend.insert(0, format_gp(self.state.config.get("max_item_cost", 500000)))
        self.ent_max_spend.pack(side="left", padx=(2, 6))
        self.ent_max_spend.bind("<FocusOut>", self.on_filter_changed)
        self.ent_max_spend.bind("<Return>", self.on_filter_changed)
        ToolTip(self.ent_max_spend, "Maximum buy price of a single item to display.")

        # Min 24h Volume
        tk.Label(self.p2, text="Min Vol:", fg="#cccccc", bg="#202023").pack(side="left")
        self.ent_min_vol = tk.Entry(self.p2, width=6, bg="#1e1e1e", fg="#f1f1f1", insertbackground="#ffffff", relief="flat")
        self.ent_min_vol.insert(0, str(self.state.config.get("min_volume", 5000)))
        self.ent_min_vol.pack(side="left", padx=(2, 6))
        self.ent_min_vol.bind("<FocusOut>", self.on_filter_changed)
        self.ent_min_vol.bind("<Return>", self.on_filter_changed)
        ToolTip(self.ent_min_vol, "Minimum 24-hour traded volume on Grand Exchange.")

        # Min Profit per alch
        tk.Label(self.p2, text="Min Profit:", fg="#cccccc", bg="#202023").pack(side="left")
        self.ent_min_profit = tk.Entry(self.p2, width=5, bg="#1e1e1e", fg="#2ecc71", insertbackground="#ffffff", relief="flat")
        m_prof = self.state.config.get("min_profit")
        if m_prof is not None and m_prof > 0:
            self.ent_min_profit.insert(0, str(m_prof))
        self.ent_min_profit.pack(side="left", padx=(2, 6))
        self.ent_min_profit.bind("<KeyRelease>", lambda e: self.recalculate_alch_table())
        ToolTip(self.ent_min_profit, "Minimum GP profit per alch. Leave blank to show all items (even 0 or negative for XP).")

        # Speed Filter Combobox
        lbl_spd = tk.Label(self.p2, text="Speed:", fg="#cccccc", bg="#202023")
        lbl_spd.pack(side="left")
        ToolTip(lbl_spd, "Filter items by estimated transaction fill wait time.")

        self.var_speed = tk.StringVar(value=self.state.config.get("speed_filter", "All"))
        cb_spd = ttk.Combobox(self.p2, textvariable=self.var_speed, values=["All", "⚡ Fast (<15m)", "⏱️ Steady (<1h)"], width=12, state="readonly")
        cb_spd.pack(side="left", padx=(2, 6))
        cb_spd.bind("<<ComboboxSelected>>", self.on_speed_filter_changed)
        ToolTip(cb_spd, "Filter by buy fill speed:\n⚡ Fast (<15m) = Active sales happening right now\n⏱️ Steady (<1h) = Consistent volume\nAll = Show all items")

        tk.Label(self.p2, text="|", fg="#444444", bg="#202023").pack(side="left", padx=4)

        # Explorer's Ring
        self.var_free_alch = tk.BooleanVar(value=self.state.config.get("free_alchs_mode", False))
        cb_free = tk.Checkbutton(self.p2, text="🌿 Ring (0 Nat)", variable=self.var_free_alch, command=self.on_filter_changed,
                                 bg="#202023", fg="#3498db", selectcolor="#2d2d30", activebackground="#202023")
        cb_free.pack(side="left", padx=(0, 4))
        ToolTip(cb_free, "Explorer's Ring Mode: Calculates profit assuming 0 Nature Rune cost.")

        # Sound & Desktop
        self.var_sound = tk.BooleanVar(value=self.state.config.get("sound_enabled", True))
        self.var_desktop = tk.BooleanVar(value=self.state.config.get("desktop_alerts", True))
        self.var_hide_maxed = tk.BooleanVar(value=self.state.config.get("hide_maxed_cooldown", True))

        cb_snd = tk.Checkbutton(self.p2, text="🔊 Sound", variable=self.var_sound, command=self.save_preferences,
                                bg="#202023", fg="#cccccc", selectcolor="#2d2d30", activebackground="#202023")
        cb_snd.pack(side="left", padx=4)

        cb_dsk = tk.Checkbutton(self.p2, text="🔔 Popups", variable=self.var_desktop, command=self.save_preferences,
                                bg="#202023", fg="#cccccc", selectcolor="#2d2d30", activebackground="#202023")
        cb_dsk.pack(side="left", padx=4)

        cb_max = tk.Checkbutton(self.p2, text="⏳ Hide Maxed", variable=self.var_hide_maxed, command=self.on_hide_maxed_changed,
                                bg="#202023", fg="#cccccc", selectcolor="#2d2d30", activebackground="#202023")
        cb_max.pack(side="left", padx=4)

        tk.Label(self.p2, text="|", fg="#444444", bg="#202023").pack(side="left", padx=4)

        # Basis
        tk.Label(self.p2, text="Basis:", fg="#cccccc", bg="#202023").pack(side="left", padx=(2, 2))
        curr_basis = self.state.config.get("price_basis", "5m")
        basis_display = "5m Volume Avg" if curr_basis == "5m" else "1-Trade Tick"
        self.var_price_basis = tk.StringVar(value=basis_display)
        cb_basis = ttk.Combobox(self.p2, textvariable=self.var_price_basis, values=["5m Volume Avg", "1-Trade Tick"], width=13, state="readonly")
        cb_basis.pack(side="left", padx=(0, 6))
        cb_basis.bind("<<ComboboxSelected>>", self.on_price_basis_changed)

        # Auto-Sync
        tk.Label(self.p2, text="⏱️ Sync:", fg="#888888", bg="#202023", font=("Segoe UI", 8)).pack(side="left")
        self.var_refresh = tk.StringVar(value=f"{self.state.config.get('auto_refresh_mins', 2)} min")
        cb_ref = ttk.Combobox(self.p2, textvariable=self.var_refresh, values=["1 min", "2 min", "5 min", "10 min", "Off"], width=6, state="readonly")
        cb_ref.pack(side="left", padx=(2, 6))
        cb_ref.bind("<<ComboboxSelected>>", self.on_refresh_rate_changed)

        # Account Lock
        tk.Label(self.p2, text="|", fg="#444444", bg="#202023").pack(side="left", padx=4)
        tk.Label(self.p2, text="Monitor:", fg="#3498db", bg="#202023", font=("Segoe UI", 8, "bold")).pack(side="left", padx=(2, 2))
        saved_char = self.state.config.get("monitored_character", "All Accounts")
        self.var_account = tk.StringVar(value=saved_char)
        init_accs = ["All Accounts"] + sorted(list(self.state.accounts.keys()))
        if saved_char not in init_accs:
            init_accs.append(saved_char)
        self.cb_account = ttk.Combobox(self.p2, textvariable=self.var_account, values=init_accs, width=13, state="readonly")
        self.cb_account.pack(side="left", padx=(0, 4))
        self.cb_account.bind("<<ComboboxSelected>>", self.on_account_selected)

        # Bridge Port in drawer
        tk.Label(self.p2, text="|", fg="#444444", bg="#202023").pack(side="left", padx=4)
        tk.Label(self.p2, text="Port:", fg="#cccccc", bg="#202023", font=("Segoe UI", 8)).pack(side="left", padx=(2, 2))
        self.ent_bridge_port = tk.Entry(self.p2, width=6, bg="#1e1e1e", fg="#2ecc71", insertbackground="#ffffff", relief="flat", justify="center")
        self.ent_bridge_port.insert(0, str(self.bridge_port))
        self.ent_bridge_port.pack(side="left", padx=(0, 2))
        self.ent_bridge_port.bind("<FocusOut>", self.on_bridge_port_changed)
        self.ent_bridge_port.bind("<Return>", self.on_bridge_port_changed)
        ToolTip(self.ent_bridge_port, f"Bridge Server Port (Default: 18833).\nLocal port for RuneLite plugin to connect on 127.0.0.1.\nEdit and press Enter to rebind.")

        btn_bridge_gear = tk.Button(self.p2, text="🔌", command=self.open_bridge_settings_dialog,
                                    bg="#252528", fg="#f1c40f", font=("Segoe UI", 8), relief="flat", padx=3, pady=0, cursor="hand2")
        btn_bridge_gear.pack(side="left", padx=(0, 4))
        ToolTip(btn_bridge_gear, "Open Bridge Connection & Port Settings dialog.")

        # Pack drawer if enabled
        if self.show_filters_drawer:
            self.p2.pack(fill="x", padx=8, pady=(2, 4))

    def toggle_filters_drawer(self):
        self.show_filters_drawer = not getattr(self, "show_filters_drawer", False)
        self.state.config["show_advanced_filters"] = self.show_filters_drawer
        self.state.save_config()
        if self.show_filters_drawer:
            self.p2.pack(fill="x", padx=8, pady=(2, 4))
            self.btn_toggle_filters.config(text="⚙️ Filters ▴", bg="#3e3e42")
        else:
            self.p2.pack_forget()
            self.btn_toggle_filters.config(text="⚙️ Filters ▾", bg="#252528")
        ToolTip(self.lbl_countdown, "Time until next automatic price sync with OSRS Wiki.")

    def build_sub_bar(self):
        p = tk.Frame(self.sub_bar, bg="#252528")
        p.pack(fill="x", padx=8, pady=3)

        # Dedicated Nature Rune Card
        nat_card = tk.Frame(p, bg="#1e1e1e", relief="solid", borderwidth=1, padx=6, pady=2)
        nat_card.pack(side="left")

        tk.Label(nat_card, text="🌿 NATURE RUNE", font=("Segoe UI", 9, "bold"), fg="#2ecc71", bg="#1e1e1e").pack(side="left", padx=(0, 4))

        self.lbl_nat_target = tk.Label(nat_card, text="🎯 Offer: 168 gp", font=("Segoe UI", 9, "bold"), bg="#27ae60", fg="#ffffff", padx=5, pady=1, cursor="hand2")
        self.lbl_nat_target.pack(side="left", padx=2)
        ToolTip(self.lbl_nat_target, "Live GE patient buy offer for Nature Runes. Click to copy price!")
        self.lbl_nat_target.bind("<Button-1>", lambda e: self.copy_to_clipboard(str(self.api.nature_rune_bid), f"Copied Nature Rune Bid: {self.api.nature_rune_bid} gp"))

        self.lbl_nat_details = tk.Label(nat_card, text="Ask: 172 gp | Limit: 18k", font=("Segoe UI", 8), fg="#aaaaaa", bg="#1e1e1e")
        self.lbl_nat_details.pack(side="left", padx=3)
        ToolTip(self.lbl_nat_details, "Nature Rune instant buy (Ask) price and 4h GE buy limit (18,000).")

        tk.Label(nat_card, text="Lock:", font=("Segoe UI", 8), fg="#888888", bg="#1e1e1e").pack(side="left", padx=(2, 1))
        self.ent_custom_nat = tk.Entry(nat_card, width=4, bg="#252528", fg="#f39c12", relief="flat")
        self.ent_custom_nat.pack(side="left", padx=(1, 2))
        c_price = self.state.config.get("custom_nature_price", 0)
        if c_price > 0:
            self.ent_custom_nat.insert(0, str(c_price))
        self.ent_custom_nat.bind("<FocusOut>", self.on_custom_nat_changed)
        self.ent_custom_nat.bind("<Return>", self.on_custom_nat_changed)
        ToolTip(self.ent_custom_nat, "Optional fixed Nature Rune price. Leave blank to use live GE market price.")

        tk.Label(nat_card, text="Owned:", font=("Segoe UI", 8), fg="#888888", bg="#1e1e1e").pack(side="left", padx=(2, 1))
        self.ent_owned_nat = tk.Entry(nat_card, width=5, bg="#252528", fg="#2ecc71", relief="flat")
        self.ent_owned_nat.pack(side="left", padx=(1, 2))
        owned = self.state.config.get("owned_nature_runes", 0)
        if owned > 0:
            self.ent_owned_nat.insert(0, str(owned))
        self.ent_owned_nat.bind("<FocusOut>", self.on_owned_nat_changed)
        self.ent_owned_nat.bind("<Return>", self.on_owned_nat_changed)
        ToolTip(self.ent_owned_nat, "Your Nature Rune bank stockpile. Cart tells you if you need to buy more.")

        # Action Buttons pinned to Right
        btn_frame = tk.Frame(p, bg="#252528")
        btn_frame.pack(side="right")

        btn_master_tag = tk.Button(btn_frame, text="📋 Master Tag", command=self.export_master_bank_tag,
                                   bg="#8e44ad", fg="#ffffff", font=("Segoe UI", 8, "bold"), relief="flat", padx=6, cursor="hand2")
        btn_master_tag.pack(side="right", padx=2)
        ToolTip(btn_master_tag, "Export all profitable items as a RuneLite bank tag tab.")

        btn_cart_tag = tk.Button(btn_frame, text="🛒 Cart Tag", command=self.export_cart_bank_tag,
                                 bg="#2980b9", fg="#ffffff", font=("Segoe UI", 8, "bold"), relief="flat", padx=6, cursor="hand2")
        btn_cart_tag.pack(side="right", padx=2)
        ToolTip(btn_cart_tag, "Export only items currently in your cart as a RuneLite bank tag tab.")

        btn_log_cart = tk.Button(btn_frame, text="✓ Log Cart", command=self.log_cart_session,
                                 bg="#27ae60", fg="#ffffff", font=("Segoe UI", 8, "bold"), relief="flat", padx=6, cursor="hand2")
        btn_log_cart.pack(side="right", padx=2)
        ToolTip(btn_log_cart, "Record cart into Session Tracker and start 4h GE cooldown timers.")

        btn_clear_cart = tk.Button(btn_frame, text="✕ Clear", command=self.clear_cart,
                                   bg="#c0392b", fg="#ffffff", font=("Segoe UI", 8), relief="flat", padx=5, cursor="hand2")
        btn_clear_cart.pack(side="right", padx=2)
        ToolTip(btn_clear_cart, "Clear all items from your shopping cart.")

        # Separator
        tk.Label(p, text="|", fg="#444444", bg="#252528").pack(side="left", padx=6)

        # Shopping Cart Summary in center
        self.lbl_cart_status = tk.Label(p, text="🛒 Slots: 0/8 | Allocated: 0 gp | Left: 5.00M gp | Profit: +0 gp",
                                        font=("Segoe UI", 8, "bold"), fg="#2ecc71", bg="#252528")
        self.lbl_cart_status.pack(side="left", padx=2)
        ToolTip(self.lbl_cart_status, "Shopping cart status: slots used, gold budget allocated, projected profit, and casting time.")

    def build_alch_hub(self):
        nav_bar = tk.Frame(self.tab_hub_alch, bg="#1e1e1e", padx=6, pady=4)
        nav_bar.pack(fill="x")

        pill_box = tk.Frame(nav_bar, bg="#252528", relief="solid", borderwidth=1, padx=2, pady=2)
        pill_box.pack(side="left")

        self.btn_sub_alch_all = tk.Button(pill_box, text="📋 All Alch Items", command=lambda: self.switch_alch_subview("all"),
                                          bg="#f39c12", fg="#000000", font=("Segoe UI", 9, "bold"), relief="flat", padx=10, pady=2, cursor="hand2")
        self.btn_sub_alch_all.pack(side="left", padx=2)

        self.btn_sub_alch_rec = tk.Button(pill_box, text="⭐ Smart Picks", command=lambda: self.switch_alch_subview("rec"),
                                          bg="#252528", fg="#cccccc", font=("Segoe UI", 9, "bold"), relief="flat", padx=10, pady=2, cursor="hand2")
        self.btn_sub_alch_rec.pack(side="left", padx=2)

        self.btn_sub_alch_night = tk.Button(pill_box, text="🌙 Overnight Planner", command=lambda: self.switch_alch_subview("overnight"),
                                            bg="#252528", fg="#cccccc", font=("Segoe UI", 9, "bold"), relief="flat", padx=10, pady=2, cursor="hand2")
        self.btn_sub_alch_night.pack(side="left", padx=2)

        self.btn_sub_alch_w308 = tk.Button(pill_box, text="🤝 W308 Bulk Trading", command=lambda: self.switch_alch_subview("w308"),
                                           bg="#252528", fg="#cccccc", font=("Segoe UI", 9, "bold"), relief="flat", padx=10, pady=2, cursor="hand2")
        self.btn_sub_alch_w308.pack(side="left", padx=2)

        self.alch_hub_content = tk.Frame(self.tab_hub_alch, bg="#1e1e1e")
        self.alch_hub_content.pack(fill="both", expand=True)

        self.tab_alch = ttk.Frame(self.alch_hub_content)
        self.build_alch_tab()

        self.tab_rec = ttk.Frame(self.alch_hub_content)
        self.build_rec_tab()

        self.tab_overnight = ttk.Frame(self.alch_hub_content)
        self.build_overnight_tab()

        self.tab_w308 = ttk.Frame(self.alch_hub_content)
        self.build_w308_tab()

        self.current_alch_subview = "all"
        self.tab_alch.pack(fill="both", expand=True)

    def switch_alch_subview(self, key):
        self.current_alch_subview = key
        for tab in (self.tab_alch, self.tab_rec, self.tab_overnight, self.tab_w308):
            tab.pack_forget()

        for btn in (self.btn_sub_alch_all, self.btn_sub_alch_rec, self.btn_sub_alch_night, self.btn_sub_alch_w308):
            btn.config(bg="#252528", fg="#cccccc")

        if key == "all":
            self.tab_alch.pack(fill="both", expand=True)
            self.btn_sub_alch_all.config(bg="#f39c12", fg="#000000")
            self.recalculate_alch_table()
        elif key == "rec":
            self.tab_rec.pack(fill="both", expand=True)
            self.btn_sub_alch_rec.config(bg="#f39c12", fg="#000000")
            self.recalculate_rec_table()
        elif key == "overnight":
            self.tab_overnight.pack(fill="both", expand=True)
            self.btn_sub_alch_night.config(bg="#f39c12", fg="#000000")
            self.recalculate_overnight_table()
        elif key == "w308":
            self.tab_w308.pack(fill="both", expand=True)
            self.btn_sub_alch_w308.config(bg="#f39c12", fg="#000000")
            self.recalculate_w308_table()

    def build_craft_hub(self):
        nav_bar = tk.Frame(self.tab_hub_craft, bg="#1e1e1e", padx=6, pady=4)
        nav_bar.pack(fill="x")

        pill_box = tk.Frame(nav_bar, bg="#252528", relief="solid", borderwidth=1, padx=2, pady=2)
        pill_box.pack(side="left")

        self.btn_sub_craft_alch = tk.Button(pill_box, text="🔨 Craft & Alch", command=lambda: self.switch_craft_subview("craft_alch"),
                                            bg="#f39c12", fg="#000000", font=("Segoe UI", 9, "bold"), relief="flat", padx=10, pady=2, cursor="hand2")
        self.btn_sub_craft_alch.pack(side="left", padx=2)

        self.btn_sub_craft_ge = tk.Button(pill_box, text="💰 Craft & Sell GE", command=lambda: self.switch_craft_subview("craft_ge"),
                                          bg="#252528", fg="#cccccc", font=("Segoe UI", 9, "bold"), relief="flat", padx=10, pady=2, cursor="hand2")
        self.btn_sub_craft_ge.pack(side="left", padx=2)

        self.btn_sub_craft_guide = tk.Button(pill_box, text="🎓 Level Training Guide", command=lambda: self.switch_craft_subview("guide"),
                                             bg="#252528", fg="#cccccc", font=("Segoe UI", 9, "bold"), relief="flat", padx=10, pady=2, cursor="hand2")
        self.btn_sub_craft_guide.pack(side="left", padx=2)

        self.craft_hub_content = tk.Frame(self.tab_hub_craft, bg="#1e1e1e")
        self.craft_hub_content.pack(fill="both", expand=True)

        self.tab_craft = ttk.Frame(self.craft_hub_content)
        self.build_craft_tab()

        self.tab_ge_craft = ttk.Frame(self.craft_hub_content)
        self.build_ge_craft_tab()

        self.tab_guide = ttk.Frame(self.craft_hub_content)
        self.build_guide_tab()

        self.current_craft_subview = "craft_alch"
        self.tab_craft.pack(fill="both", expand=True)

    def switch_craft_subview(self, key):
        self.current_craft_subview = key
        for tab in (self.tab_craft, self.tab_ge_craft, self.tab_guide):
            tab.pack_forget()

        for btn in (self.btn_sub_craft_alch, self.btn_sub_craft_ge, self.btn_sub_craft_guide):
            btn.config(bg="#252528", fg="#cccccc")

        if key == "craft_alch":
            self.tab_craft.pack(fill="both", expand=True)
            self.btn_sub_craft_alch.config(bg="#f39c12", fg="#000000")
            self.recalculate_craft_table()
        elif key == "craft_ge":
            self.tab_ge_craft.pack(fill="both", expand=True)
            self.btn_sub_craft_ge.config(bg="#f39c12", fg="#000000")
            self.recalculate_ge_craft_table()
        elif key == "guide":
            self.tab_guide.pack(fill="both", expand=True)
            self.btn_sub_craft_guide.config(bg="#f39c12", fg="#000000")
            self.recalculate_guide_table()

    def build_activity_hub(self):
        nav_bar = tk.Frame(self.tab_hub_activity, bg="#1e1e1e", padx=6, pady=4)
        nav_bar.pack(fill="x")

        pill_box = tk.Frame(nav_bar, bg="#252528", relief="solid", borderwidth=1, padx=2, pady=2)
        pill_box.pack(side="left")

        self.btn_sub_act_session = tk.Button(pill_box, text="📊 Session Profit Ledger", command=lambda: self.switch_activity_subview("session"),
                                             bg="#f39c12", fg="#000000", font=("Segoe UI", 9, "bold"), relief="flat", padx=10, pady=2, cursor="hand2")
        self.btn_sub_act_session.pack(side="left", padx=2)

        self.btn_sub_act_alerts = tk.Button(pill_box, text="🔔 Live Alerts Feed", command=lambda: self.switch_activity_subview("alerts"),
                                            bg="#252528", fg="#cccccc", font=("Segoe UI", 9, "bold"), relief="flat", padx=10, pady=2, cursor="hand2")
        self.btn_sub_act_alerts.pack(side="left", padx=2)

        self.activity_hub_content = tk.Frame(self.tab_hub_activity, bg="#1e1e1e")
        self.activity_hub_content.pack(fill="both", expand=True)

        self.tab_session = ttk.Frame(self.activity_hub_content)
        self.build_session_tab()

        self.tab_alerts = ttk.Frame(self.activity_hub_content)
        self.build_alerts_tab()

        self.current_activity_subview = "session"
        self.tab_session.pack(fill="both", expand=True)

    def switch_activity_subview(self, key):
        self.current_activity_subview = key
        for tab in (self.tab_session, self.tab_alerts):
            tab.pack_forget()

        for btn in (self.btn_sub_act_session, self.btn_sub_act_alerts):
            btn.config(bg="#252528", fg="#cccccc")

        if key == "session":
            self.tab_session.pack(fill="both", expand=True)
            self.btn_sub_act_session.config(bg="#f39c12", fg="#000000")
            self.update_session_display()
        elif key == "alerts":
            self.tab_alerts.pack(fill="both", expand=True)
            self.btn_sub_act_alerts.config(bg="#f39c12", fg="#000000")

    def build_alch_tab(self):
        container = ttk.Frame(self.tab_alch)
        container.pack(fill="both", expand=True)

        cols = ("cart", "name", "offer_bid", "instant_ask", "alch_val", "profit_ea", "profit_hr", "speed", "limit", "batch_profit", "max_afford", "volume")
        self.tree_alch = ttk.Treeview(container, columns=cols, show="headings", selectmode="browse")

        self.tree_alch.heading("cart", text="Cart", command=lambda: self.toggle_sort_alch("cart"))
        self.tree_alch.heading("name", text="Item Name", command=lambda: self.toggle_sort_alch("name"))
        self.tree_alch.heading("offer_bid", text="Target Offer (Bid)", command=lambda: self.toggle_sort_alch("offer_bid"))
        self.tree_alch.heading("instant_ask", text="Instant Buy (Ask)", command=lambda: self.toggle_sort_alch("instant_ask"))
        self.tree_alch.heading("alch_val", text="Alch Value", command=lambda: self.toggle_sort_alch("alch_val"))
        self.tree_alch.heading("profit_ea", text="Profit / Alch ▼", command=lambda: self.toggle_sort_alch("profit_ea"))
        self.tree_alch.heading("profit_hr", text="Profit / Hr (1.2k)", command=lambda: self.toggle_sort_alch("profit_hr"))
        self.tree_alch.heading("speed", text="Fill Speed", command=lambda: self.toggle_sort_alch("speed"))
        self.tree_alch.heading("limit", text="4h Limit", command=lambda: self.toggle_sort_alch("limit"))
        self.tree_alch.heading("batch_profit", text="4h Batch Profit", command=lambda: self.toggle_sort_alch("batch_profit"))
        self.tree_alch.heading("max_afford", text="Max Afford", command=lambda: self.toggle_sort_alch("max_afford"))
        self.tree_alch.heading("volume", text="24h Volume", command=lambda: self.toggle_sort_alch("volume"))

        self.tree_alch.column("cart", width=46, anchor="center")
        self.tree_alch.column("name", width=170, anchor="w")
        self.tree_alch.column("offer_bid", width=105, anchor="e")
        self.tree_alch.column("instant_ask", width=105, anchor="e")
        self.tree_alch.column("alch_val", width=85, anchor="e")
        self.tree_alch.column("profit_ea", width=100, anchor="e")
        self.tree_alch.column("profit_hr", width=110, anchor="e")
        self.tree_alch.column("speed", width=128, anchor="center")
        self.tree_alch.column("limit", width=95, anchor="center")
        self.tree_alch.column("batch_profit", width=110, anchor="e")
        self.tree_alch.column("max_afford", width=85, anchor="center")
        self.tree_alch.column("volume", width=115, anchor="e")

        scrollbar = ttk.Scrollbar(container, orient="vertical", command=self.tree_alch.yview)
        h_scrollbar = ttk.Scrollbar(container, orient="horizontal", command=self.tree_alch.xview)
        self.tree_alch.configure(yscrollcommand=scrollbar.set, xscrollcommand=h_scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        h_scrollbar.pack(side="bottom", fill="x")
        self.tree_alch.pack(side="left", fill="both", expand=True)

        self.tree_alch.bind("<Button-1>", self.on_alch_click)
        self.tree_alch.bind("<Double-1>", self.on_alch_double_click)
        self.tree_alch.bind("<Button-3>", self.on_alch_right_click)

        # Hover descriptions for every table column header
        alch_col_tooltips = {
            "#1": "Shopping Cart:\nShows items in cart. Click row cell to copy quantity number to clipboard.\nRight-click row to set custom cart quantity.",
            "#2": "Item Name:\nGrand Exchange item name. Click row cell to copy name to clipboard for GE search.",
            "#3": "Target Offer (Bid):\nBest patient buy price from active sellers. Click cell to copy price.\nIf using Smart strategy, bids Bid + 1 gp for queue priority.",
            "#4": "Instant Buy (Ask):\nInstant purchase price from active sellers. Fills immediately. Click cell to copy.",
            "#5": "High Alch Value:\nFixed gold returned by casting the High Level Alchemy spell.",
            "#6": "Profit / Alch:\nNet GP profit per cast = High Alch Value - Item Buy Price - Nature Rune Cost.\nClick column header to sort.",
            "#7": "Profit / Hr:\nEstimated profit per hour at standard 1,200 casts/hour rate.\nClick column header to sort.",
            "#8": "Fill Speed & 5m Sold:\nEstimated wait time or live 5-minute sales velocity.\nIn 1-Trade Tick mode, shows exact quantity sold into bids in the past 5 minutes (e.g. '3 sold') to verify real market activity.\nClick column header to sort.",
            "#9": "4h GE Buy Limit:\nOfficial Grand Exchange purchase limit every 4 hours.\n⚠️ Volume Capped: If 24h market volume is lower than GE limit, shows 'Volume / Limit ⚠️' to avoid illiquid paper profit traps.",
            "#10": "4h Batch Profit:\nRealistic profit achievable for a full 4-hour batch (Profit ea * Effective volume-capped limit).\nClick column header to sort.",
            "#11": "Max Afford:\nMaximum quantity your current cash stack can afford out of remaining available limit.\nClick column header to sort.",
            "#12": "24h Volume & 5m Sold:\nTotal units traded on Grand Exchange over the last 24 hours.\nIn 1-Trade Tick mode, displays '24h Vol (5m Sold)' to verify active trades.\nClick column header to sort."
        }
        HeadingToolTip(self.tree_alch, alch_col_tooltips)
        RowToolTip(self.tree_alch, self.get_alch_row_tooltip)

    def build_rec_tab(self):
        container = ttk.Frame(self.tab_rec)
        container.pack(fill="both", expand=True, padx=6, pady=4)

        # 1. Market Clock & Timing Banner Card
        self.market_clock_card = tk.Frame(container, bg="#202023", relief="solid", borderwidth=1, padx=10, pady=6)
        self.market_clock_card.pack(fill="x", pady=(2, 6))

        clock_top = tk.Frame(self.market_clock_card, bg="#202023")
        clock_top.pack(fill="x")

        self.lbl_market_time = tk.Label(clock_top, text="🕒 --:-- UTC", font=("Segoe UI", 11, "bold"), fg="#f1c40f", bg="#202023")
        self.lbl_market_time.pack(side="left", padx=(0, 10))
        ToolTip(self.lbl_market_time, "Current Grand Exchange server time (UTC).\nOSRS market activity cycles strictly follow UTC time zones.")

        self.lbl_market_badge = tk.Label(clock_top, text="🟢 Peak Trading Hours", font=("Segoe UI", 10, "bold"), fg="#2ecc71", bg="#202023")
        self.lbl_market_badge.pack(side="left", padx=(0, 12))

        self.lbl_market_activity = tk.Label(clock_top, text="Activity: [████████░░] 80%", font=("Segoe UI", 9), fg="#3498db", bg="#202023")
        self.lbl_market_activity.pack(side="left")

        self.lbl_market_advice = tk.Label(self.market_clock_card, text="💡 Tip: Market is active. Place smart bids on high-volume staples.",
                                          font=("Segoe UI", 9, "italic"), fg="#e0e0e0", bg="#202023")
        self.lbl_market_advice.pack(anchor="w", pady=(4, 0))

        # 2. Controls & Categories Row
        rec_ctrl = tk.Frame(container, bg="#252528", relief="solid", borderwidth=1, padx=8, pady=5)
        rec_ctrl.pack(fill="x", pady=(0, 6))

        tk.Label(rec_ctrl, text="Category:", font=("Segoe UI", 9, "bold"), fg="#f39c12", bg="#252528").pack(side="left", padx=(2, 8))

        self.var_rec_cat = tk.StringVar(value="workhorse")
        cat_options = [
            ("🏆 All-Time Workhorses", "workhorse", "Proven high-volume alch staples that rarely fail (Rune armor, weapons, battlestaves)."),
            ("⚡ Fast Fills (<5m)", "fast", "Items with rapid transaction velocity and live 5m sales activity that fill in under 5 minutes."),
            ("💰 Top 4h Batch Profit", "batch", "Items ranked by total profit achievable in a single 4-hour GE limit cycle."),
            ("🌙 Overnight Sleepers", "overnight", "High-margin items ideal for leaving patient bids overnight during off-peak hours.")
        ]
        for label, val, tip in cat_options:
            rb = tk.Radiobutton(rec_ctrl, text=label, variable=self.var_rec_cat, value=val,
                                command=self.recalculate_rec_table,
                                bg="#252528", fg="#f1f1f1", selectcolor="#2d2d30",
                                activebackground="#252528", activeforeground="#f39c12",
                                font=("Segoe UI", 9))
            rb.pack(side="left", padx=4)
            ToolTip(rb, f"{label}:\n{tip}")

        # Action Buttons on right
        btn_auto_fill = tk.Button(rec_ctrl, text="⚡ Auto-Fill Empty GE Slots", command=self.auto_fill_ge_slots,
                                  bg="#27ae60", fg="#ffffff", font=("Segoe UI", 9, "bold"), relief="flat", padx=10, pady=2, cursor="hand2")
        btn_auto_fill.pack(side="right", padx=3)
        ToolTip(btn_auto_fill, "⚡ Auto-Fill Empty GE Slots:\nInspects your remaining empty GE slots (up to 8) and automatically allocates\nthe top recommended items into your shopping cart, fitted to your cash stack budget!")

        btn_copy_all = tk.Button(rec_ctrl, text="📋 Copy All", command=self.copy_all_recs,
                                 bg="#2980b9", fg="#ffffff", font=("Segoe UI", 8, "bold"), relief="flat", padx=8, pady=2, cursor="hand2")
        btn_copy_all.pack(side="right", padx=3)
        ToolTip(btn_copy_all, "Copy All:\nCopy formatted text list of all displayed recommendations to clipboard.")

        btn_refresh = tk.Button(rec_ctrl, text="🔄 Refresh", command=self.recalculate_rec_table,
                                bg="#3e3e42", fg="#f1f1f1", font=("Segoe UI", 8), relief="flat", padx=6, pady=2, cursor="hand2")
        btn_refresh.pack(side="right", padx=3)
        ToolTip(btn_refresh, "Refresh recommendations using latest live GE prices.")

        # 3. Recommendations Table Container
        tree_frame = ttk.Frame(container)
        tree_frame.pack(fill="both", expand=True)

        cols = ("badge", "name", "category", "offer_bid", "alch_val", "profit_ea", "limit", "batch_profit", "speed", "batch_cost", "verdict")
        self.tree_rec = ttk.Treeview(tree_frame, columns=cols, show="headings", selectmode="browse")

        self.tree_rec.heading("badge", text="Rank", command=lambda: self.toggle_sort_rec("badge"))
        self.tree_rec.heading("name", text="Item Name", command=lambda: self.toggle_sort_rec("name"))
        self.tree_rec.heading("category", text="Category", command=lambda: self.toggle_sort_rec("category"))
        self.tree_rec.heading("offer_bid", text="Target Bid", command=lambda: self.toggle_sort_rec("offer_bid"))
        self.tree_rec.heading("alch_val", text="Alch Value", command=lambda: self.toggle_sort_rec("alch_val"))
        self.tree_rec.heading("profit_ea", text="Profit / Alch ▼", command=lambda: self.toggle_sort_rec("profit_ea"))
        self.tree_rec.heading("limit", text="4h Limit", command=lambda: self.toggle_sort_rec("limit"))
        self.tree_rec.heading("batch_profit", text="4h Batch Profit", command=lambda: self.toggle_sort_rec("batch_profit"))
        self.tree_rec.heading("speed", text="Fill Speed", command=lambda: self.toggle_sort_rec("speed"))
        self.tree_rec.heading("batch_cost", text="Batch Spend", command=lambda: self.toggle_sort_rec("batch_cost"))
        self.tree_rec.heading("verdict", text="Why Buy? / Verdict", command=lambda: self.toggle_sort_rec("verdict"))

        self.tree_rec.column("badge", width=55, anchor="center")
        self.tree_rec.column("name", width=165, anchor="w")
        self.tree_rec.column("category", width=130, anchor="center")
        self.tree_rec.column("offer_bid", width=95, anchor="e")
        self.tree_rec.column("alch_val", width=85, anchor="e")
        self.tree_rec.column("profit_ea", width=95, anchor="e")
        self.tree_rec.column("limit", width=95, anchor="center")
        self.tree_rec.column("batch_profit", width=105, anchor="e")
        self.tree_rec.column("speed", width=120, anchor="center")
        self.tree_rec.column("batch_cost", width=100, anchor="e")
        self.tree_rec.column("verdict", width=290, anchor="w")

        v_scroll = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree_rec.yview)
        h_scroll = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree_rec.xview)
        self.tree_rec.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)

        v_scroll.pack(side="right", fill="y")
        h_scroll.pack(side="bottom", fill="x")
        self.tree_rec.pack(side="left", fill="both", expand=True)

        self.tree_rec.bind("<Button-1>", self.on_rec_click)
        self.tree_rec.bind("<Double-1>", self.on_rec_double_click)
        self.tree_rec.bind("<Button-3>", self.on_rec_right_click)

        rec_col_tooltips = {
            "#1": "Rank & Badge:\nRank position within this recommendation list.",
            "#2": "Item Name:\nGrand Exchange item name. Click to copy name to clipboard.",
            "#3": "Category:\nStrategy category: All-Time Workhorse, Fast Fill, Batch Profit, or Overnight Sleeper.",
            "#4": "Target Bid:\nBest buy offer price. Click to copy.",
            "#5": "Alch Value:\nHigh Alchemy gold value.",
            "#6": "Profit / Alch:\nNet gold profit per High Alch cast (Alch Value - Buy Price - Nature Rune Cost).",
            "#7": "4h GE Buy Limit:\nMaximum Grand Exchange units purchasable every 4 hours.",
            "#8": "4h Batch Profit:\nTotal profit earned for a full 4h limit batch (Profit ea * Available limit).",
            "#9": "Fill Speed:\nLive transaction velocity badge (⚡ Fast, ⏱️ Steady, 🐢 Slow).",
            "#10": "Batch Spend:\nTotal gold required to purchase a full batch of this item.",
            "#11": "Why Buy? / Verdict:\nStrategic summary explaining why this item is recommended."
        }
        HeadingToolTip(self.tree_rec, rec_col_tooltips)
        RowToolTip(self.tree_rec, self.get_alch_row_tooltip)

    def build_overnight_tab(self):
        container = ttk.Frame(self.tab_overnight)
        container.pack(fill="both", expand=True, padx=6, pady=4)

        # 1. Market Timing & Sleep Strategy Banner Card
        self.overnight_banner_card = tk.Frame(container, bg="#202023", relief="solid", borderwidth=1, padx=10, pady=6)
        self.overnight_banner_card.pack(fill="x", pady=(2, 6))

        b_top = tk.Frame(self.overnight_banner_card, bg="#202023")
        b_top.pack(fill="x")

        lbl_on_title = tk.Label(b_top, text="🌙 GE Overnight Optimizer", font=("Segoe UI", 11, "bold"), fg="#f1c40f", bg="#202023")
        lbl_on_title.pack(side="left", padx=(0, 10))
        ToolTip(lbl_on_title, "Optimizes Grand Exchange buy offers for overnight sleep windows.\nAnalyzes 48h & 7-day percentile dips to catch off-peak sell dumps with high fill rates.")

        lbl_on_badge = tk.Label(b_top, text="💤 48h & 7d Multi-Day Dip Analysis", font=("Segoe UI", 10, "bold"), fg="#2ecc71", bg="#202023")
        lbl_on_badge.pack(side="left", padx=(0, 12))

        self.lbl_overnight_cycles = tk.Label(b_top, text="⏰ Limit Multiplier: 3.0x (12h Window = 3 GE Limit Resets)", font=("Segoe UI", 9, "bold"), fg="#3498db", bg="#202023")
        self.lbl_overnight_cycles.pack(side="left")

        self.lbl_overnight_tip = tk.Label(
            self.overnight_banner_card,
            text="💡 Sleep Strategy: Between 03:00 and 08:00 UTC, player activity drops ~50%. Placing patient percentile bids lets you catch massive undercut dumps while 4h buy limits reset multiple times!",
            font=("Segoe UI", 9, "italic"), fg="#e0e0e0", bg="#202023"
        )
        self.lbl_overnight_tip.pack(anchor="w", pady=(4, 0))

        # 2. Control Strip (Duration, Strategy, Slots, Focus, Owned Nats)
        ctrl_strip = tk.Frame(container, bg="#252528", relief="solid", borderwidth=1, padx=8, pady=5)
        ctrl_strip.pack(fill="x", pady=(0, 6))

        # Duration
        tk.Label(ctrl_strip, text="💤 Duration:", font=("Segoe UI", 9, "bold"), fg="#f39c12", bg="#252528").pack(side="left", padx=(2, 3))
        self.var_overnight_dur = tk.StringVar(value="12 Hours (3x limit)")
        self.cb_overnight_dur = ttk.Combobox(ctrl_strip, textvariable=self.var_overnight_dur,
                                             values=["6 Hours (2x limit)", "8 Hours (2x limit)", "10 Hours (3x limit)", "12 Hours (3x limit)"],
                                             width=17, state="readonly")
        self.cb_overnight_dur.pack(side="left", padx=(0, 6))
        self.cb_overnight_dur.bind("<<ComboboxSelected>>", lambda e: self.recalculate_overnight_table())
        ToolTip(self.cb_overnight_dur, "Select your sleep duration.\nGrand Exchange 4-hour buy limits reset every 4h, so you can buy 2x or 3x the normal limit while asleep!")

        # Strategy
        tk.Label(ctrl_strip, text="🎯 Strategy:", font=("Segoe UI", 9, "bold"), fg="#f39c12", bg="#252528").pack(side="left", padx=(2, 3))
        self.var_overnight_strat = tk.StringVar(value="Safe Morning Fill (25% Low)")
        self.cb_overnight_strat = ttk.Combobox(ctrl_strip, textvariable=self.var_overnight_strat,
                                               values=["Safe Morning Fill (25% Low)", "Deep-Dip Sniper (10% Low)"],
                                               width=23, state="readonly")
        self.cb_overnight_strat.pack(side="left", padx=(0, 6))
        self.cb_overnight_strat.bind("<<ComboboxSelected>>", lambda e: self.recalculate_overnight_table())
        ToolTip(self.cb_overnight_strat, "• Safe Morning Fill (25% Low): Bids at 25th percentile of 48h lows + 5 gp. High fill probability (>95%) by morning.\n• Deep-Dip Sniper (10% Low): Bids at 10th percentile of 48h lows + 5 gp with 7d floor clamp. Highest margin for 3-6 AM dumps.")

        # Slots
        tk.Label(ctrl_strip, text="📦 Slots:", font=("Segoe UI", 9, "bold"), fg="#f39c12", bg="#252528").pack(side="left", padx=(2, 3))
        init_slot = "3 Slots (F2P)" if (hasattr(self, "var_f2p") and self.var_f2p.get()) else "8 Slots (P2P)"
        self.var_overnight_slots = tk.StringVar(value=init_slot)
        self.cb_overnight_slots = ttk.Combobox(ctrl_strip, textvariable=self.var_overnight_slots,
                                               values=["1 Slot", "2 Slots", "3 Slots (F2P)", "4 Slots", "5 Slots", "6 Slots", "7 Slots", "8 Slots (P2P)"],
                                               width=13, state="readonly")
        self.cb_overnight_slots.pack(side="left", padx=(0, 6))
        self.cb_overnight_slots.bind("<<ComboboxSelected>>", lambda e: self.recalculate_overnight_table())
        ToolTip(self.cb_overnight_slots, "Number of Grand Exchange offer slots to allocate.\nF2P players have 3 slots. Members have up to 8 slots.")

        # Focus / Category
        tk.Label(ctrl_strip, text="🔍 Focus:", font=("Segoe UI", 9, "bold"), fg="#f39c12", bg="#252528").pack(side="left", padx=(2, 3))
        self.var_overnight_focus = tk.StringVar(value="🌟 All Staples (Highest Profit)")
        self.cb_overnight_focus = ttk.Combobox(ctrl_strip, textvariable=self.var_overnight_focus,
                                               values=["🌟 All Staples (Highest Profit)", "🛡️ Rune Heavy Gear Only", "📦 Adamant & Budget High-ROI", "🪄 Battlestaves & Crafting (P2P)", "🏹 Stackables & Bolts (P2P)"],
                                               width=24, state="readonly")
        self.cb_overnight_focus.pack(side="left", padx=(0, 6))
        self.cb_overnight_focus.bind("<<ComboboxSelected>>", lambda e: self.recalculate_overnight_table())
        ToolTip(self.cb_overnight_focus, "Filter candidate pool:\n• All Staples: Evaluates all items to maximize total profit.\n• Rune Heavy Gear: High alch value armor & weapons (Helms, Platebodies, Legs, Warhammers).\n• Adamant & Budget: High-ROI lower cost gear.\n• Battlestaves / Stackables: Bulk P2P items.")

        # Max Alch Time (Realistic Morning Window)
        tk.Label(ctrl_strip, text="⏱️ Alch Time:", font=("Segoe UI", 9, "bold"), fg="#f39c12", bg="#252528").pack(side="left", padx=(2, 3))
        self.var_overnight_time = tk.StringVar(value="1 Hour (~1.2k items)")
        self.cb_overnight_time = ttk.Combobox(ctrl_strip, textvariable=self.var_overnight_time,
                                              values=["30 Mins (~600 items)", "45 Mins (~900 items)", "1 Hour (~1.2k items)", "2 Hours (~2.4k items)", "3 Hours (~3.6k items)", "♾️ Unlimited (No Cap)"],
                                              width=19, state="readonly")
        self.cb_overnight_time.pack(side="left", padx=(0, 6))
        self.cb_overnight_time.bind("<<ComboboxSelected>>", lambda e: self.recalculate_overnight_table())
        ToolTip(self.cb_overnight_time, "Realistic Alching Time Constraint:\nCaps total items to what you can realistically alch in the morning (1,200 casts/hour).\nPrevents absurd 30,000 bolt or 50,000 battlestaff piles and prioritizes high-margin items!")

        # Max Items Per Slot Cap
        tk.Label(ctrl_strip, text="📦 Max / Slot:", font=("Segoe UI", 9, "bold"), fg="#f39c12", bg="#252528").pack(side="left", padx=(2, 3))
        self.var_overnight_max_slot = tk.StringVar(value="500 (Balanced)")
        self.cb_overnight_max_slot = ttk.Combobox(ctrl_strip, textvariable=self.var_overnight_max_slot,
                                                  values=["250 (Fast 12m)", "375 (12h Armor Cap)", "500 (Balanced)", "1,000 (Extended)", "♾️ Unlimited"],
                                                  width=16, state="readonly")
        self.cb_overnight_max_slot.pack(side="left", padx=(0, 6))
        self.cb_overnight_max_slot.bind("<<ComboboxSelected>>", lambda e: self.recalculate_overnight_table())
        ToolTip(self.cb_overnight_max_slot, "Max Items Per GE Slot Offer:\nCaps individual buy offers (e.g. max 500) so no single item dominates your bag or turns into a 30k mountain.\nEnsures variety across your GE slots!")

        # 0 GP Nature Runes (Use Owned)
        self.var_overnight_owned_nat = tk.BooleanVar(value=True)
        self.cb_overnight_nats = tk.Checkbutton(ctrl_strip, text="🌿 0 GP Nats", variable=self.var_overnight_owned_nat,
                                                command=self.recalculate_overnight_table,
                                                bg="#252528", fg="#2ecc71", selectcolor="#2d2d30", activebackground="#252528", activeforeground="#2ecc71",
                                                font=("Segoe UI", 9, "bold"))
        self.cb_overnight_nats.pack(side="left", padx=(2, 6))
        ToolTip(self.cb_overnight_nats, "🌿 Use Owned Nature Runes (0 GP Nat Cost):\nAssumes you already own Nature Runes in your bank, dedicating 100% of your cash stack to buying alch items!")

        # Right Action Buttons
        btn_opt = tk.Button(ctrl_strip, text="⚡ Auto-Optimize Bag", command=self.on_auto_optimize_clicked,
                            bg="#27ae60", fg="#ffffff", font=("Segoe UI", 9, "bold"), relief="flat", padx=8, pady=2, cursor="hand2")
        btn_opt.pack(side="right", padx=3)
        ToolTip(btn_opt, "⚡ Auto-Optimize Overnight Bag:\nSolves the optimal cash stack allocation across the selected GE slots to maximize overnight profit with minimal idle coins!")

        btn_cart = tk.Button(ctrl_strip, text="🛒 Send to Cart", command=self.send_overnight_bag_to_cart,
                             bg="#2980b9", fg="#ffffff", font=("Segoe UI", 8, "bold"), relief="flat", padx=6, pady=2, cursor="hand2")
        btn_cart.pack(side="right", padx=3)
        ToolTip(btn_cart, "Load the optimized overnight items and quantities directly into your Grand Exchange Shopping Cart!")

        btn_copy = tk.Button(ctrl_strip, text="📋 Copy Plan", command=self.copy_overnight_offers,
                             bg="#8e44ad", fg="#ffffff", font=("Segoe UI", 8, "bold"), relief="flat", padx=6, pady=2, cursor="hand2")
        btn_copy.pack(side="right", padx=3)
        ToolTip(btn_copy, "Copy formatted GE buy orders (Item, Bid, Quantity, Total Cost) to clipboard for fast in-game entry!")

        btn_ref = tk.Button(ctrl_strip, text="🔄 Refresh", command=self.refresh_overnight_dips,
                            bg="#3e3e42", fg="#f1f1f1", font=("Segoe UI", 8), relief="flat", padx=5, pady=2, cursor="hand2")
        btn_ref.pack(side="right", padx=3)
        ToolTip(btn_ref, "Re-fetch latest 48h and 7d timeseries dip prices from OSRS Wiki API.")

        # 3. Overnight Summary Metrics Bar
        self.overnight_summary_card = tk.Frame(container, bg="#1e1e1e", relief="solid", borderwidth=1, padx=10, pady=5)
        self.overnight_summary_card.pack(fill="x", pady=(0, 6))

        tk.Label(self.overnight_summary_card, text="💰 Budget:", font=("Segoe UI", 8), fg="#888888", bg="#1e1e1e").pack(side="left")
        self.lbl_on_budget = tk.Label(self.overnight_summary_card, text="-- gp", font=("Segoe UI", 9, "bold"), fg="#ffffff", bg="#1e1e1e")
        self.lbl_on_budget.pack(side="left", padx=(2, 10))

        tk.Label(self.overnight_summary_card, text="🛒 Spend Allocated:", font=("Segoe UI", 8), fg="#888888", bg="#1e1e1e").pack(side="left")
        self.lbl_on_spend = tk.Label(self.overnight_summary_card, text="-- gp", font=("Segoe UI", 9, "bold"), fg="#3498db", bg="#1e1e1e")
        self.lbl_on_spend.pack(side="left", padx=(2, 10))

        tk.Label(self.overnight_summary_card, text="🪙 Leftover GP:", font=("Segoe UI", 8), fg="#888888", bg="#1e1e1e").pack(side="left")
        self.lbl_on_leftover = tk.Label(self.overnight_summary_card, text="-- gp", font=("Segoe UI", 9, "bold"), fg="#e67e22", bg="#1e1e1e")
        self.lbl_on_leftover.pack(side="left", padx=(2, 10))

        tk.Label(self.overnight_summary_card, text="✨ Expected Profit:", font=("Segoe UI", 8), fg="#888888", bg="#1e1e1e").pack(side="left")
        self.lbl_on_profit = tk.Label(self.overnight_summary_card, text="+-- gp", font=("Segoe UI", 10, "bold"), fg="#2ecc71", bg="#1e1e1e")
        self.lbl_on_profit.pack(side="left", padx=(2, 10))

        tk.Label(self.overnight_summary_card, text="🔥 Total Items:", font=("Segoe UI", 8), fg="#888888", bg="#1e1e1e").pack(side="left")
        self.lbl_on_items = tk.Label(self.overnight_summary_card, text="-- items", font=("Segoe UI", 9, "bold"), fg="#9b59b6", bg="#1e1e1e")
        self.lbl_on_items.pack(side="left", padx=(2, 10))

        tk.Label(self.overnight_summary_card, text="⏱️ Est. Alch Time:", font=("Segoe UI", 8), fg="#888888", bg="#1e1e1e").pack(side="left")
        self.lbl_on_time = tk.Label(self.overnight_summary_card, text="-- mins", font=("Segoe UI", 9, "bold"), fg="#f1c40f", bg="#1e1e1e")
        self.lbl_on_time.pack(side="left", padx=(2, 10))

        tk.Label(self.overnight_summary_card, text="🚀 Hourly Rate:", font=("Segoe UI", 8), fg="#888888", bg="#1e1e1e").pack(side="left")
        self.lbl_on_rate = tk.Label(self.overnight_summary_card, text="--/hr", font=("Segoe UI", 10, "bold"), fg="#00d2d3", bg="#1e1e1e")
        self.lbl_on_rate.pack(side="left", padx=(2, 0))

        # 4. Overnight Table
        tree_frame = ttk.Frame(container)
        tree_frame.pack(fill="both", expand=True)

        cols = ("badge", "name", "bid", "alch", "profit_ea", "limit_period", "alloc_qty", "total_cost", "slot_profit", "confidence", "verdict")
        self.tree_overnight = ttk.Treeview(tree_frame, columns=cols, show="headings", selectmode="browse")

        self.tree_overnight.heading("badge", text="Pick", command=lambda: self.toggle_sort_overnight("badge"))
        self.tree_overnight.heading("name", text="Item Name", command=lambda: self.toggle_sort_overnight("name"))
        self.tree_overnight.heading("bid", text="Optimal Bid", command=lambda: self.toggle_sort_overnight("bid"))
        self.tree_overnight.heading("alch", text="High Alch", command=lambda: self.toggle_sort_overnight("alch"))
        self.tree_overnight.heading("profit_ea", text="Profit / Ea", command=lambda: self.toggle_sort_overnight("profit_ea"))
        self.tree_overnight.heading("limit_period", text="Period Limit", command=lambda: self.toggle_sort_overnight("limit_period"))
        self.tree_overnight.heading("alloc_qty", text="Allocated Qty", command=lambda: self.toggle_sort_overnight("alloc_qty"))
        self.tree_overnight.heading("total_cost", text="Total Spend", command=lambda: self.toggle_sort_overnight("total_cost"))
        self.tree_overnight.heading("slot_profit", text="Expected Profit ▼", command=lambda: self.toggle_sort_overnight("slot_profit"))
        self.tree_overnight.heading("confidence", text="Fill Confidence", command=lambda: self.toggle_sort_overnight("confidence"))
        self.tree_overnight.heading("verdict", text="Night Market Analysis / Historical Dips", command=lambda: self.toggle_sort_overnight("verdict"))

        self.tree_overnight.column("badge", width=70, anchor="center")
        self.tree_overnight.column("name", width=165, anchor="w")
        self.tree_overnight.column("bid", width=95, anchor="e")
        self.tree_overnight.column("alch", width=85, anchor="e")
        self.tree_overnight.column("profit_ea", width=95, anchor="e")
        self.tree_overnight.column("limit_period", width=95, anchor="center")
        self.tree_overnight.column("alloc_qty", width=90, anchor="center")
        self.tree_overnight.column("total_cost", width=105, anchor="e")
        self.tree_overnight.column("slot_profit", width=115, anchor="e")
        self.tree_overnight.column("confidence", width=130, anchor="center")
        self.tree_overnight.column("verdict", width=310, anchor="w")

        v_scroll = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree_overnight.yview)
        h_scroll = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree_overnight.xview)
        self.tree_overnight.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)

        v_scroll.pack(side="right", fill="y")
        h_scroll.pack(side="bottom", fill="x")
        self.tree_overnight.pack(side="left", fill="both", expand=True)

        self.tree_overnight.bind("<Button-1>", self.on_overnight_click)
        self.tree_overnight.bind("<Double-1>", self.on_overnight_double_click)
        self.tree_overnight.bind("<Button-3>", self.on_overnight_right_click)

        overnight_col_tooltips = {
            "#1": "Pick Badge:\nIdentifies whether this item is an active allocated pick in your overnight bag or an alternative candidate.",
            "#2": "Item Name:\nGrand Exchange item name. Click to copy name to clipboard.",
            "#3": "Optimal Bid:\nCalculated percentile buy price based on 48h/7d dips. Click to copy price!",
            "#4": "High Alch:\nHigh Alchemy value in gold.",
            "#5": "Profit / Ea:\nNet profit per item alched (High Alch - Optimal Bid - Nat Cost).",
            "#6": "Period Limit:\nTotal Grand Exchange buy limit over your selected sleep duration.",
            "#7": "Allocated Qty:\nOptimal quantity to buy with your cash stack. Click to copy quantity!",
            "#8": "Total Spend:\nTotal gold required to purchase the allocated quantity.",
            "#9": "Expected Profit:\nTotal gold profit earned once all units are bought and alched.",
            "#10": "Fill Confidence:\nLikelihood of the buy offer filling before morning based on historical 24h & 48h volume.",
            "#11": "Night Market Analysis:\nDetailed rationale based on 48h/7d timeseries market behavior."
        }
        HeadingToolTip(self.tree_overnight, overnight_col_tooltips)

    def get_current_cash_stack(self):
        if hasattr(self, "ent_cash"):
            try:
                val = parse_cash_input(self.ent_cash.get())
                if val >= 0:
                    return val
            except Exception:
                pass
        return self.state.config.get("cash_stack", 5000000)

    def get_w308_item_material_cost(self, it):
        """Calculates total GE raw material cost to forge/craft 1 unit of this item."""
        if not it or not it.get("skill"):
            return 0, "Not craftable / monster drop"
        mat_id = it.get("mat_id")
        if not mat_id:
            return 0, "No raw materials required"
        qty1 = it.get("mat_qty", 1)
        ge1 = self.api.latest_prices.get(str(mat_id)) or self.api.latest_prices.get(mat_id) or {}
        p1 = ge1.get("high") or ge1.get("low") or it.get("mat_default", 0)
        total_cost = qty1 * p1
        desc = f"{qty1}x {it.get('mat_name')} ({p1:,} ea)"

        mat2_id = it.get("mat2_id")
        if mat2_id:
            qty2 = it.get("mat2_qty", 1)
            ge2 = self.api.latest_prices.get(str(mat2_id)) or self.api.latest_prices.get(mat2_id) or {}
            p2 = ge2.get("high") or ge2.get("low") or it.get("mat2_default", 0)
            total_cost += qty2 * p2
            desc += f" + {qty2}x {it.get('mat2_name')} ({p2:,} ea)"

        return total_cost, desc

    def build_w308_tab(self):
        container = ttk.Frame(self.tab_w308)
        container.pack(fill="both", expand=True, padx=6, pady=4)

        cash_stack = self.get_current_cash_stack()

        # 1. Header & Quick Advertising Strip
        banner = tk.Frame(container, bg="#202023", relief="solid", borderwidth=1, padx=10, pady=6)
        banner.pack(fill="x", pady=(2, 6))

        top_row = tk.Frame(banner, bg="#202023")
        top_row.pack(fill="x")

        tk.Label(top_row, text="🤝 World 308 'Varrock West' Bulk Trading Hub", font=("Segoe UI", 11, "bold"), fg="#f39c12", bg="#202023").pack(side="left")
        tk.Label(top_row, text="📍 W308 Varrock West Bank | Clan Guest: 'Varrock Mob'", font=("Segoe UI", 8), fg="#888888", bg="#202023").pack(side="right")

        # Operating Role Switcher: Alcher / Buyer vs Smither / Crafter (Seller)
        role_frame = tk.Frame(banner, bg="#18181a", relief="solid", borderwidth=1, padx=8, pady=3)
        role_frame.pack(fill="x", pady=(4, 3))

        tk.Label(role_frame, text="🎭 Operating Role:", font=("Segoe UI", 9, "bold"), fg="#f1c40f", bg="#18181a").pack(side="left", padx=(2, 8))

        self.var_w308_role = tk.StringVar(value="buyer")
        r_buyer = tk.Radiobutton(role_frame, text="🛒 Alcher / Buyer Mode (Buy bulk alchables at W308 benchmark prices)",
                                 variable=self.var_w308_role, value="buyer", command=self.on_w308_role_changed,
                                 bg="#18181a", fg="#2ecc71", selectcolor="#2d2d30", activebackground="#18181a", font=("Segoe UI", 8, "bold"))
        r_buyer.pack(side="left", padx=4)

        r_seller = tk.Radiobutton(role_frame, text="🔨 Smither / Crafter Mode (Forge items from GE materials & sell P2P bulk)",
                                  variable=self.var_w308_role, value="seller", command=self.on_w308_role_changed,
                                  bg="#18181a", fg="#e67e22", selectcolor="#2d2d30", activebackground="#18181a", font=("Segoe UI", 8, "bold"))
        r_seller.pack(side="left", padx=4)

        self.lbl_w308_desc = tk.Label(banner, text="Bypass the 4-hour 70-unit GE buy limit and save 2% GE tax by trading bulk noted items directly with smiths and crafters!",
                                      font=("Segoe UI", 8), fg="#cccccc", bg="#202023")
        self.lbl_w308_desc.pack(anchor="w", pady=(2, 4))

        # Live Money Stack & Top Allocation Strip
        self.w308_budget_bar = tk.Frame(banner, bg="#18181a", relief="solid", borderwidth=1, padx=8, pady=4)
        self.w308_budget_bar.pack(fill="x", pady=(2, 5))

        self.lbl_w308_budget = tk.Label(self.w308_budget_bar, text=f"💰 Active Money Stack: {format_gp(cash_stack)}", font=("Segoe UI", 9, "bold"), fg="#2ecc71", bg="#18181a")
        self.lbl_w308_budget.pack(side="left", padx=(2, 10))

        self.lbl_w308_top_pick = tk.Label(self.w308_budget_bar, text="🏆 Top Stack Pick: Calculating...", font=("Segoe UI", 9), fg="#f39c12", bg="#18181a")
        self.lbl_w308_top_pick.pack(side="left", padx=(2, 10))

        self.btn_load_w308_top = tk.Button(self.w308_budget_bar, text="🎯 Allocate Full Stack to Top Pick", command=self.load_w308_top_pick_to_validator,
                                           bg="#f39c12", fg="#000000", font=("Segoe UI", 8, "bold"), relief="flat", padx=8, pady=1, cursor="hand2")
        self.btn_load_w308_top.pack(side="right", padx=2)
        ToolTip(self.btn_load_w308_top, "Instantly loads the highest-profit bulk item into the Validator and allocates your active working capital!")

        self.btn_w308_inv_item = tk.Button(self.w308_budget_bar, text="📦 Load Inventory Items", command=self.load_w308_inventory_staple,
                                           bg="#2d2d30", fg="#3498db", font=("Segoe UI", 8, "bold"), relief="flat", padx=8, pady=1, cursor="hand2")
        self.btn_w308_inv_item.pack(side="right", padx=4)
        ToolTip(self.btn_w308_inv_item, "Instantly loads bulk items detected in your inventory (e.g. 340 noted Rune 2h swords) into the Trade Validator!")

        # Ad Buttons Row
        ad_row = tk.Frame(banner, bg="#202023")
        ad_row.pack(fill="x", pady=(2, 0))

        self.lbl_ad_title = tk.Label(ad_row, text="📢 Trade Ad Fast-Copy:", font=("Segoe UI", 8, "bold"), fg="#3498db", bg="#202023")
        self.lbl_ad_title.pack(side="left", padx=(0, 6))

        r2h_qty = cash_stack // 37600
        r2h_lbl = f"Copy: Buying {r2h_qty:,} R2H 37.6k ea" if r2h_qty > 0 else "Copy: Buying R2H 37.6k ea"
        self.btn_ad_r2h = tk.Button(ad_row, text=r2h_lbl, command=self.copy_w308_r2h_ad,
                                    bg="#2d2d30", fg="#f1c40f", font=("Segoe UI", 8, "bold"), relief="flat", padx=6, pady=2, cursor="hand2")
        self.btn_ad_r2h.pack(side="left", padx=3)
        ToolTip(self.btn_ad_r2h, "Click to copy bulk R2H trade offer calculated directly from your money stack.")

        legs_qty = cash_stack // 37600
        legs_lbl = f"Copy: Buying {legs_qty:,} Legs/Skirts 37.6k" if legs_qty > 0 else "Copy: Buying Legs/Skirts 37.6k"
        self.btn_ad_legs = tk.Button(ad_row, text=legs_lbl, command=self.copy_w308_legs_ad,
                                     bg="#2d2d30", fg="#f1c40f", font=("Segoe UI", 8, "bold"), relief="flat", padx=6, pady=2, cursor="hand2")
        self.btn_ad_legs.pack(side="left", padx=3)
        ToolTip(self.btn_ad_legs, "Click to copy bulk Rune legs/skirts trade offer calculated directly from your money stack.")

        self.btn_ad_multi = tk.Button(ad_row, text="Copy: Multi-Item Bulk Ad",
                                      command=self.copy_w308_multi_ad,
                                      bg="#2d2d30", fg="#2ecc71", font=("Segoe UI", 8, "bold"), relief="flat", padx=6, pady=2, cursor="hand2")
        self.btn_ad_multi.pack(side="left", padx=3)
        ToolTip(self.btn_ad_multi, "Click to copy multi-item trade advertisement to clipboard!")

        # W308 Filter: All | F2P Only | P2P Only
        tk.Label(ad_row, text="|", fg="#444444", bg="#202023").pack(side="left", padx=4)
        tk.Label(ad_row, text="Trades Filter:", font=("Segoe UI", 8, "bold"), fg="#888888", bg="#202023").pack(side="left", padx=(2, 2))
        self.var_w308_mem_filter = tk.StringVar(value="all")
        for m_lbl, m_val in (("All", "all"), ("F2P Only", "f2p"), ("P2P (Members)", "p2p")):
            r = tk.Radiobutton(ad_row, text=m_lbl, variable=self.var_w308_mem_filter, value=m_val,
                               command=self.on_w308_mem_filter_changed,
                               bg="#202023", fg="#f1f1f1", selectcolor="#2d2d30", activebackground="#202023", font=("Segoe UI", 8))
            r.pack(side="left", padx=2)

        # 2. Anti-Scam Bulk Trade Validator Card
        val_card = tk.Frame(container, bg="#1a1a1d", relief="solid", borderwidth=1, padx=10, pady=6)
        val_card.pack(fill="x", pady=(0, 6))

        v_head = tk.Frame(val_card, bg="#1a1a1d")
        v_head.pack(fill="x", pady=(0, 4))
        self.lbl_v_title = tk.Label(v_head, text="🛡️ Anti-Scam Bulk Trade Calculator & 2nd Screen Verifier", font=("Segoe UI", 9, "bold"), fg="#e67e22", bg="#1a1a1d")
        self.lbl_v_title.pack(side="left")
        self.lbl_v_sub = tk.Label(v_head, text="Auto-scaled to your money stack so you never have to guess quantities or totals", font=("Segoe UI", 8, "italic"), fg="#888888", bg="#1a1a1d")
        self.lbl_v_sub.pack(side="left", padx=(10, 0))

        v_body = tk.Frame(val_card, bg="#1a1a1d")
        v_body.pack(fill="x")

        # Inputs on left
        v_in = tk.Frame(v_body, bg="#1a1a1d")
        v_in.pack(side="left", fill="y", padx=(0, 15))

        # Item row
        r1 = tk.Frame(v_in, bg="#1a1a1d")
        r1.pack(fill="x", pady=2)
        tk.Label(r1, text="Item:", width=7, anchor="w", fg="#cccccc", bg="#1a1a1d", font=("Segoe UI", 8)).pack(side="left")
        item_names = [it["name"] for it in W308_STAPLES]
        self.var_w308_item = tk.StringVar(value=item_names[0] if item_names else "")
        self.cb_w308_item = ttk.Combobox(r1, textvariable=self.var_w308_item, values=item_names, width=17, state="readonly")
        self.cb_w308_item.pack(side="left")
        self.cb_w308_item.bind("<<ComboboxSelected>>", self.on_w308_validator_item_selected)

        # Price row
        r3 = tk.Frame(v_in, bg="#1a1a1d")
        r3.pack(fill="x", pady=2)
        self.lbl_v_price_prompt = tk.Label(r3, text="Agreed Ea:", width=7, anchor="w", fg="#cccccc", bg="#1a1a1d", font=("Segoe UI", 8))
        self.lbl_v_price_prompt.pack(side="left")
        first_price = W308_STAPLES[0]["w308_buy"] if W308_STAPLES else 37600
        self.ent_w308_price = tk.Entry(r3, width=8, bg="#252528", fg="#f1c40f", insertbackground="#ffffff", relief="flat")
        self.ent_w308_price.insert(0, str(first_price))
        self.ent_w308_price.pack(side="left")
        self.ent_w308_price.bind("<KeyRelease>", self.on_w308_price_changed)

        # Qty row with Quick Money Stack Allocation Buttons
        r2 = tk.Frame(v_in, bg="#1a1a1d")
        r2.pack(fill="x", pady=2)
        tk.Label(r2, text="Qty:", width=7, anchor="w", fg="#cccccc", bg="#1a1a1d", font=("Segoe UI", 8)).pack(side="left")
        self.ent_w308_qty = tk.Entry(r2, width=7, bg="#252528", fg="#2ecc71", insertbackground="#ffffff", relief="flat")
        init_qty = cash_stack // first_price if first_price > 0 else 100
        self.ent_w308_qty.insert(0, str(init_qty if init_qty > 0 else 100))
        self.ent_w308_qty.pack(side="left", padx=(0, 2))
        self.ent_w308_qty.bind("<KeyRelease>", self.calculate_w308_trade_validator)

        self.btn_max_val = tk.Button(r2, text="Max Cash", command=lambda: self.set_w308_validator_fraction(1.0),
                                     bg="#2d2d30", fg="#2ecc71", font=("Segoe UI", 7, "bold"), relief="flat", padx=3, pady=1, cursor="hand2")
        self.btn_max_val.pack(side="left", padx=1)
        ToolTip(self.btn_max_val, "Set quantity to 100% of your active capital/budget.")

        btn_half = tk.Button(r2, text="50%", command=lambda: self.set_w308_validator_fraction(0.5),
                             bg="#2d2d30", fg="#f39c12", font=("Segoe UI", 7, "bold"), relief="flat", padx=3, pady=1, cursor="hand2")
        btn_half.pack(side="left", padx=1)
        ToolTip(btn_half, "Set quantity to 50% of your active capital/budget.")

        btn_qtr = tk.Button(r2, text="25%", command=lambda: self.set_w308_validator_fraction(0.25),
                            bg="#2d2d30", fg="#3498db", font=("Segoe UI", 7, "bold"), relief="flat", padx=3, pady=1, cursor="hand2")
        btn_qtr.pack(side="left", padx=1)
        ToolTip(btn_qtr, "Set quantity to 25% of your active capital/budget.")

        # Results on center-right
        v_res = tk.Frame(v_body, bg="#1a1a1d")
        v_res.pack(side="left", fill="both", expand=True)

        res_grid = tk.Frame(v_res, bg="#1a1a1d")
        res_grid.pack(fill="x")

        self.lbl_v_coins = tk.Label(res_grid, text="Coins To Give: -- gp", font=("Segoe UI", 9, "bold"), fg="#f39c12", bg="#1a1a1d")
        self.lbl_v_coins.grid(row=0, column=0, sticky="w", padx=6, pady=1)

        self.lbl_v_alch = tk.Label(res_grid, text="High Alch: -- gp", font=("Segoe UI", 9), fg="#9b59b6", bg="#1a1a1d")
        self.lbl_v_alch.grid(row=0, column=1, sticky="w", padx=6, pady=1)

        self.lbl_v_nat = tk.Label(res_grid, text="Nature Cost: -- gp", font=("Segoe UI", 9), fg="#3498db", bg="#1a1a1d")
        self.lbl_v_nat.grid(row=1, column=0, sticky="w", padx=6, pady=1)

        self.lbl_v_profit = tk.Label(res_grid, text="Net Profit: -- gp", font=("Segoe UI", 9, "bold"), fg="#2ecc71", bg="#1a1a1d")
        self.lbl_v_profit.grid(row=1, column=1, sticky="w", padx=6, pady=1)

        self.lbl_v_budget_status = tk.Label(v_res, text="🪙 Money Stack: -- gp | Remaining Change: -- gp", font=("Segoe UI", 8, "bold"), fg="#2ecc71", bg="#1a1a1d")
        self.lbl_v_budget_status.pack(anchor="w", padx=6, pady=(2, 0))

        self.lbl_v_warning = tk.Label(v_res, text="⚠️ Verification: Ensure 2nd trade screen shows EXACT noted items and coins!",
                                      font=("Segoe UI", 8, "bold"), fg="#e67e22", bg="#1a1a1d")
        self.lbl_v_warning.pack(anchor="w", padx=6, pady=(2, 0))

        # Actions on right
        v_act = tk.Frame(v_body, bg="#1a1a1d")
        v_act.pack(side="right", fill="y", padx=(10, 0))

        self.btn_copy_coins = tk.Button(v_act, text="⌨️ Type: --",
                                        command=lambda: None,
                                        bg="#f39c12", fg="#000000", font=("Segoe UI", 8, "bold"), relief="flat", padx=8, pady=2, cursor="hand2")
        self.btn_copy_coins.pack(fill="x", pady=2)
        ToolTip(self.btn_copy_coins, "Shows exact shorthand to type into OSRS Offer-X prompt (e.g. 7580k). Click for step-by-step guidance!")

        self.btn_copy_validator_ad = tk.Button(v_act, text="📢 Copy Trade Ad", command=self.copy_w308_validator_ad,
                                               bg="#2d2d30", fg="#3498db", font=("Segoe UI", 8, "bold"), relief="flat", padx=8, pady=2, cursor="hand2")
        self.btn_copy_validator_ad.pack(fill="x", pady=2)
        ToolTip(self.btn_copy_validator_ad, "Copy tailored chat trade ad with this exact quantity and price.")

        self.btn_log_w308 = tk.Button(v_act, text="✓ Log To Session",
                                      command=self.log_w308_trade_to_session,
                                      bg="#27ae60", fg="#ffffff", font=("Segoe UI", 8, "bold"), relief="flat", padx=8, pady=2, cursor="hand2")
        self.btn_log_w308.pack(fill="x", pady=2)
        ToolTip(self.btn_log_w308, "Record this bulk purchase directly into your Session Tracker.")

        # 3. W308 Margin Sheet Table
        tree_frame = ttk.Frame(container)
        tree_frame.pack(fill="both", expand=True)

        cols = ("item", "w308_price", "ge_instant", "alch_val", "profit_ea", "margin_pct", "max_stack", "total_spend", "expected_profit", "chat_ad")
        self.tree_w308 = ttk.Treeview(tree_frame, columns=cols, show="headings", selectmode="browse")

        self.tree_w308.heading("item", text="Bulk Item", command=lambda: self.toggle_sort_w308("item"))
        self.tree_w308.heading("w308_price", text="W308 Buy (ea)", command=lambda: self.toggle_sort_w308("w308_price"))
        self.tree_w308.heading("ge_instant", text="GE Instant (ea)", command=lambda: self.toggle_sort_w308("ge_instant"))
        self.tree_w308.heading("alch_val", text="High Alch", command=lambda: self.toggle_sort_w308("alch_val"))
        self.tree_w308.heading("profit_ea", text="Profit / Ea ▼", command=lambda: self.toggle_sort_w308("profit_ea"))
        self.tree_w308.heading("margin_pct", text="Margin %", command=lambda: self.toggle_sort_w308("margin_pct"))
        self.tree_w308.heading("max_stack", text="Max Stack (Budget)", command=lambda: self.toggle_sort_w308("max_stack"))
        self.tree_w308.heading("total_spend", text="Total Spend", command=lambda: self.toggle_sort_w308("total_spend"))
        self.tree_w308.heading("expected_profit", text="Expected Net Profit", command=lambda: self.toggle_sort_w308("expected_profit"))
        self.tree_w308.heading("chat_ad", text="Chat Ad Copy", command=lambda: self.toggle_sort_w308("chat_ad"))

        self.tree_w308.column("item", width=150, anchor="w")
        self.tree_w308.column("w308_price", width=105, anchor="e")
        self.tree_w308.column("ge_instant", width=105, anchor="e")
        self.tree_w308.column("alch_val", width=95, anchor="e")
        self.tree_w308.column("profit_ea", width=95, anchor="e")
        self.tree_w308.column("margin_pct", width=80, anchor="center")
        self.tree_w308.column("max_stack", width=120, anchor="center")
        self.tree_w308.column("total_spend", width=105, anchor="e")
        self.tree_w308.column("expected_profit", width=130, anchor="e")
        self.tree_w308.column("chat_ad", width=240, anchor="w")

        v_scroll = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree_w308.yview)
        h_scroll = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree_w308.xview)
        self.tree_w308.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)

        v_scroll.pack(side="right", fill="y")
        h_scroll.pack(side="bottom", fill="x")
        self.tree_w308.pack(side="left", fill="both", expand=True)

        self.tree_w308.bind("<Button-1>", self.on_w308_click)
        self.tree_w308.bind("<Double-1>", self.on_w308_double_click)
        self.tree_w308.bind("<Button-3>", self.on_w308_right_click)

        w308_col_tooltips = {
            "#1": "Bulk Item:\nName of the bulk tradeable alchable item. Double-click row to load into Anti-Scam Validator!",
            "#2": "W308 Buy (ea):\nStandard community benchmark buy price in World 308 Varrock West Bank.",
            "#3": "GE Instant (ea):\nInstant buy (Ask) price on the Grand Exchange. Demonstrates your savings buying bulk direct!",
            "#4": "High Alch:\nFixed gold payout per item when cast with High Alchemy.",
            "#5": "Profit / Ea:\nNet profit per item alched = High Alch - W308 Buy - Nature Rune Cost.",
            "#6": "Margin %:\nProfit percentage relative to your capital outlay.",
            "#7": "Max Stack (Budget):\nMaximum quantity you can purchase with your current active cash stack without GE limits!",
            "#8": "Total Spend:\nTotal gold required to purchase the max stack.",
            "#9": "Expected Net Profit:\nTotal gold profit earned once all units are purchased and alched.",
            "#10": "Chat Ad Copy:\nReady-to-use chat spam message. Click cell to copy directly to your clipboard!"
        }
        self.w308_heading_tooltip = HeadingToolTip(self.tree_w308, w308_col_tooltips)
        self.calculate_w308_trade_validator()

    def on_w308_role_changed(self):
        is_seller = getattr(self, "var_w308_role", None) and self.var_w308_role.get() == "seller"

        if is_seller:
            if hasattr(self, "lbl_w308_desc"):
                self.lbl_w308_desc.config(
                    text="Train Smithing & Crafting profitably! Buy raw materials on GE, forge bulk batches, and sell un-noted/noted to high alchers in W308 at premium rates!"
                )
            if hasattr(self, "btn_load_w308_top"):
                self.btn_load_w308_top.config(text="🎯 Max Forge Budget on Top Pick")
            if hasattr(self, "lbl_v_title"):
                self.lbl_v_title.config(text="🛡️ Anti-Scam Seller Trade Calculator & Material Cost Verifier", fg="#2ecc71")
            if hasattr(self, "lbl_v_sub"):
                self.lbl_v_sub.config(text="Verifies buyer offers exact coins & calculates your net smithing/crafting training profit and XP")
            if hasattr(self, "lbl_v_price_prompt"):
                self.lbl_v_price_prompt.config(text="Agreed Sell:")
            if hasattr(self, "btn_max_val"):
                self.btn_max_val.config(text="Max Forge")
            if hasattr(self, "btn_ad_multi"):
                self.btn_ad_multi.config(text="Copy: Multi-Item Seller Ad")

            seller_tooltips = {
                "#1": "Crafted Item:\nName of the smithed or crafted bulk item. Double-click row to load into Seller Validator!",
                "#2": "W308 Sell (ea):\nCommunity benchmark bulk sell rate in W308 (e.g. 37,875 - 37,900 for R2H).",
                "#3": "Material Cost (ea):\nLive GE cost of raw materials required to forge/craft 1 unit (e.g. 3x Runite bars @ ~12,175 ea).",
                "#4": "Skill & Lvl:\nSkill requirement and level required to forge or craft the item.",
                "#5": "Profit / Ea:\nNet profit per item smithed = W308 Sell Price - GE Material Cost.",
                "#6": "XP / Item:\nSmithing, Crafting, or Fletching experience earned per completed item.",
                "#7": "Max Forge (Budget):\nMaximum quantity of items you can forge with your current cash/bar budget.",
                "#8": "Total Bar Cost:\nTotal gold required to purchase raw materials on GE for the entire batch.",
                "#9": "Net Smither Profit:\nTotal gold profit earned once the entire forged batch is sold.",
                "#10": "Seller Ad Copy:\nReady-to-use chat advertisement for Varrock West Bank. Click cell to copy!"
            }
            if hasattr(self, "w308_heading_tooltip"):
                self.w308_heading_tooltip.tooltips = seller_tooltips
        else:
            if hasattr(self, "lbl_w308_desc"):
                self.lbl_w308_desc.config(
                    text="Bypass the 4-hour 70-unit GE buy limit and save 2% GE tax by trading bulk noted items directly with smiths and crafters!"
                )
            if hasattr(self, "btn_load_w308_top"):
                self.btn_load_w308_top.config(text="🎯 Allocate Full Stack to Top Pick")
            if hasattr(self, "lbl_v_title"):
                self.lbl_v_title.config(text="🛡️ Anti-Scam Bulk Trade Calculator & 2nd Screen Verifier", fg="#e67e22")
            if hasattr(self, "lbl_v_sub"):
                self.lbl_v_sub.config(text="Auto-scaled to your money stack so you never have to guess quantities or totals")
            if hasattr(self, "lbl_v_price_prompt"):
                self.lbl_v_price_prompt.config(text="Agreed Ea:")
            if hasattr(self, "btn_max_val"):
                self.btn_max_val.config(text="Max Cash")
            if hasattr(self, "btn_ad_multi"):
                self.btn_ad_multi.config(text="Copy: Multi-Item Bulk Ad")

            buyer_tooltips = {
                "#1": "Bulk Item:\nName of the bulk tradeable alchable item. Double-click row to load into Anti-Scam Validator!",
                "#2": "W308 Buy (ea):\nStandard community benchmark buy price in World 308 Varrock West Bank.",
                "#3": "GE Instant (ea):\nInstant buy (Ask) price on the Grand Exchange. Demonstrates your savings buying bulk direct!",
                "#4": "High Alch:\nFixed gold payout per item when cast with High Alchemy.",
                "#5": "Profit / Ea:\nNet profit per item alched = High Alch - W308 Buy - Nature Rune Cost.",
                "#6": "Margin %:\nProfit percentage relative to your capital outlay.",
                "#7": "Max Stack (Budget):\nMaximum quantity you can purchase with your current active cash stack without GE limits!",
                "#8": "Total Spend:\nTotal gold required to purchase the max stack.",
                "#9": "Expected Net Profit:\nTotal gold profit earned once all units are purchased and alched.",
                "#10": "Chat Ad Copy:\nReady-to-use chat spam message. Click cell to copy directly to your clipboard!"
            }
            if hasattr(self, "w308_heading_tooltip"):
                self.w308_heading_tooltip.tooltips = buyer_tooltips

        self.update_w308_combobox_items()
        self.on_w308_validator_item_selected()
        self.recalculate_w308_table()

    def update_w308_combobox_items(self):
        f_val = self.var_w308_mem_filter.get() if hasattr(self, "var_w308_mem_filter") else "all"
        is_seller = getattr(self, "var_w308_role", None) and self.var_w308_role.get() == "seller"

        filtered = []
        for it in W308_STAPLES:
            if is_seller and not it.get("skill"):
                continue
            is_mem = it.get("members", False)
            if f_val == "f2p" and is_mem:
                continue
            if f_val == "p2p" and not is_mem:
                continue
            filtered.append(it)

        names = [it["name"] for it in filtered]
        if hasattr(self, "cb_w308_item"):
            self.cb_w308_item.config(values=names)
            curr = self.var_w308_item.get()
            if not curr or curr not in names:
                if names:
                    self.var_w308_item.set(names[0])

    def set_w308_validator_fraction(self, frac):
        is_seller = getattr(self, "var_w308_role", None) and self.var_w308_role.get() == "seller"
        sel_name = self.var_w308_item.get()
        item = next((it for it in W308_STAPLES if it["name"] == sel_name), None)
        cash = self.get_current_cash_stack()

        if is_seller:
            mat_cost, _ = self.get_w308_item_material_cost(item) if item else (0, "")
            if mat_cost <= 0:
                try:
                    price = int(self.ent_w308_price.get().strip().replace(",", ""))
                except Exception:
                    price = 0
                target_qty = int((cash * frac) // price) if price > 0 else 1
            else:
                target_qty = int((cash * frac) // mat_cost)
        else:
            try:
                price = int(self.ent_w308_price.get().strip().replace(",", ""))
            except Exception:
                price = 0
            if price <= 0:
                return
            target_qty = int((cash * frac) // price)

        self.ent_w308_qty.delete(0, tk.END)
        self.ent_w308_qty.insert(0, str(target_qty if target_qty > 0 else 1))
        self.calculate_w308_trade_validator()

    def on_w308_price_changed(self, event=None):
        self.calculate_w308_trade_validator()

    def copy_w308_validator_ad(self):
        is_seller = getattr(self, "var_w308_role", None) and self.var_w308_role.get() == "seller"
        sel_name = self.var_w308_item.get()
        item = next((it for it in W308_STAPLES if it["name"] == sel_name), None)
        short_name = item["short"] if item else sel_name
        try:
            qty = int(self.ent_w308_qty.get().strip().replace(",", ""))
        except Exception:
            qty = 0
        try:
            price = int(self.ent_w308_price.get().strip().replace(",", ""))
        except Exception:
            price = 0
        p_str = f"{price / 1000:.1f}k" if price % 1000 != 0 else f"{price // 1000}k"
        if is_seller:
            ad_str = f"Selling {qty:,} {short_name} {p_str} ea Bulk - Trade Me" if qty > 0 else f"Selling {short_name} {p_str} ea Bulk - Trade Me"
        else:
            ad_str = f"Buying {qty:,} {short_name} {p_str} ea Bulk - Trade Me" if qty > 0 else f"Buying {short_name} {p_str} ea Bulk - Trade Me"
        self.copy_to_clipboard(ad_str, f"Copied custom trade ad: '{ad_str}'")

    def load_w308_top_pick_to_validator(self):
        if not self.w308_rows:
            return
        best = max(self.w308_rows, key=lambda r: r.get("expected_profit", 0))
        if best and best.get("max_stack", 0) > 0:
            self.var_w308_item.set(best["item"])
            self.ent_w308_price.delete(0, tk.END)
            self.ent_w308_price.insert(0, str(best["w308_price"]))
            self.ent_w308_qty.delete(0, tk.END)
            self.ent_w308_qty.insert(0, str(best["max_stack"]))
            self.calculate_w308_trade_validator()
            is_seller = getattr(self, "var_w308_role", None) and self.var_w308_role.get() == "seller"
            if is_seller:
                FloatingToast(self, "Top Smither Pick Loaded", f"Allocated bar budget to {best['item']} ({best['max_stack']:,} forged, +{format_gp(best['expected_profit'])} profit, +{best.get('total_xp', 0):,} XP)!", 3000)
            else:
                FloatingToast(self, "Top Stack Pick Loaded", f"Allocated 100% of money stack to {best['item']} ({best['max_stack']:,} units, +{format_gp(best['expected_profit'])} profit)!", 3000)

    def load_w308_inventory_staple(self):
        sel_acc = self.var_account.get() if hasattr(self, "var_account") else "Default"
        acc = self.state.accounts.get(sel_acc) or (max(self.state.accounts.values(), key=lambda a: a.get("last_seen", 0)) if self.state.accounts else {})
        b_name = acc.get("batch_item_name", "")
        b_qty = acc.get("batch_item_qty", 0)

        # Also fallback to container inventory file directly if batch item not yet registered
        if not b_name or b_qty <= 0:
            try:
                inv_path = os.path.expanduser(r"~/.runelite/Data Exports/container_inventory.json")
                if os.path.exists(inv_path):
                    with open(inv_path, "r", encoding="utf-8") as f:
                        for line in f:
                            if not line.strip():
                                continue
                            itm = json.loads(line.strip())
                            if itm.get("quantity", 0) > 0 and itm.get("name") in ("Rune 2h sword", "Rune platelegs", "Rune plateskirt", "Adamant platebody"):
                                b_name = itm["name"]
                                b_qty = itm["quantity"]
                                break
            except Exception:
                pass

        if b_name and b_qty > 0:
            if hasattr(self, "var_w308_role"):
                self.var_w308_role.set("seller")
                self.on_w308_role_changed()

            matched = next((it for it in W308_STAPLES if it["name"].lower() == b_name.lower()), None)
            if matched:
                self.var_w308_item.set(matched["name"])
                sell_p = matched.get("w308_sell_p2p", 37875)
                self.ent_w308_price.delete(0, tk.END)
                self.ent_w308_price.insert(0, str(sell_p))
                self.ent_w308_qty.delete(0, tk.END)
                self.ent_w308_qty.insert(0, str(b_qty))
                self.calculate_w308_trade_validator()
                FloatingToast(self, "Inventory Bulk Item Loaded", f"Loaded {b_qty:,}x {matched['name']} from backpack into Validator (Gross: {format_gp(b_qty * sell_p)})!", 3500)
            else:
                self.show_status_message(f"Item {b_name} loaded into Validator.")
        else:
            FloatingToast(self, "Inventory Check", "No bulk trade staple items currently detected in backpack.", 3000)

    def copy_w308_r2h_ad(self):
        cash = self.get_current_cash_stack()
        is_seller = getattr(self, "var_w308_role", None) and self.var_w308_role.get() == "seller"
        item = next((it for it in W308_STAPLES if it["id"] == 1319), None)
        if is_seller:
            sel_acc = self.var_account.get() if hasattr(self, "var_account") else "Default"
            acc = self.state.accounts.get(sel_acc) or (max(self.state.accounts.values(), key=lambda a: a.get("last_seen", 0)) if self.state.accounts else {})
            inv_qty = acc.get("batch_item_qty", 0) if acc.get("batch_item_name") == "Rune 2h sword" else 0
            if inv_qty > 0:
                qty = inv_qty
            else:
                mat_cost, _ = self.get_w308_item_material_cost(item) if item else (36525, "")
                qty = cash // mat_cost if mat_cost > 0 else 0
            sell_p = item.get("w308_sell_p2p", 37875) if item else 37875
            p_str = f"{sell_p / 1000:.1f}k" if sell_p % 1000 != 0 else f"{sell_p // 1000}k"
            ad_str = f"Selling {qty:,} R2H {p_str} ea Bulk - Trade Me" if qty > 0 else f"Selling R2H {p_str} ea Bulk - Trade Me"
            self.copy_to_clipboard(ad_str, f"Copied R2H seller ad: '{ad_str}'")
        else:
            price = 37600
            qty = cash // price
            ad_str = f"Buying {qty:,} R2H 37.6k ea Bulk - Trade Me" if qty > 0 else "Buying R2H 37.6k ea Bulk - Trade Me"
            self.copy_to_clipboard(ad_str, f"Copied R2H buy ad: '{ad_str}'")

    def copy_w308_legs_ad(self):
        cash = self.get_current_cash_stack()
        is_seller = getattr(self, "var_w308_role", None) and self.var_w308_role.get() == "seller"
        item = next((it for it in W308_STAPLES if it["id"] == 1079), None)
        if is_seller:
            sel_acc = self.var_account.get() if hasattr(self, "var_account") else "Default"
            acc = self.state.accounts.get(sel_acc) or (max(self.state.accounts.values(), key=lambda a: a.get("last_seen", 0)) if self.state.accounts else {})
            inv_qty = acc.get("batch_item_qty", 0) if acc.get("batch_item_name") in ("Rune platelegs", "Rune plateskirt") else 0
            if inv_qty > 0:
                qty = inv_qty
            else:
                mat_cost, _ = self.get_w308_item_material_cost(item) if item else (36525, "")
                qty = cash // mat_cost if mat_cost > 0 else 0
            sell_p = item.get("w308_sell_p2p", 37875) if item else 37875
            p_str = f"{sell_p / 1000:.1f}k" if sell_p % 1000 != 0 else f"{sell_p // 1000}k"
            ad_str = f"Selling {qty:,} Rune Legs {p_str} ea Bulk - Trade Me" if qty > 0 else f"Selling Rune Legs {p_str} ea Bulk - Trade Me"
            self.copy_to_clipboard(ad_str, f"Copied Rune legs seller ad: '{ad_str}'")
        else:
            price = 37600
            qty = cash // price
            ad_str = f"Buying {qty:,} Rune Legs/Skirts 37.6k ea Bulk - Trade Me" if qty > 0 else "Buying Rune Legs/Skirts 37.6k ea Bulk - Trade Me"
            self.copy_to_clipboard(ad_str, f"Copied Rune legs/skirts ad: '{ad_str}'")

    def copy_w308_multi_ad(self):
        is_seller = getattr(self, "var_w308_role", None) and self.var_w308_role.get() == "seller"
        if is_seller:
            ad_str = "Selling R2H / Legs / Skirts 37.9k | Addy Body 9.75k Bulk - Trade Me"
            self.copy_to_clipboard(ad_str, "Copied Multi-Item Seller Ad to clipboard!")
        else:
            ad_str = "Buying R2H / Legs / Skirts 37.6k | Addy Body 9.65k Bulk - Trade Me"
            self.copy_to_clipboard(ad_str, "Copied Multi-Alch Ad to clipboard!")

    def on_w308_validator_item_selected(self, event=None):
        sel_name = self.var_w308_item.get()
        item = next((it for it in W308_STAPLES if it["name"] == sel_name), None)
        is_seller = getattr(self, "var_w308_role", None) and self.var_w308_role.get() == "seller"
        cash = self.get_current_cash_stack()

        if item:
            if is_seller:
                price = item.get("w308_sell_p2p", 37875)
                mat_cost, _ = self.get_w308_item_material_cost(item)
                max_qty = cash // mat_cost if mat_cost > 0 else 100
            else:
                price = item["w308_buy"]
                max_qty = cash // price if price > 0 else 100

            self.ent_w308_price.delete(0, tk.END)
            self.ent_w308_price.insert(0, str(price))
            self.ent_w308_qty.delete(0, tk.END)
            self.ent_w308_qty.insert(0, str(max_qty if max_qty > 0 else 100))

        self.calculate_w308_trade_validator()

    def calculate_w308_trade_validator(self, event=None):
        if not hasattr(self, "lbl_v_coins"):
            return
        is_seller = getattr(self, "var_w308_role", None) and self.var_w308_role.get() == "seller"
        sel_name = self.var_w308_item.get()
        item = next((it for it in W308_STAPLES if it["name"] == sel_name), None)
        alch_val = item["alch"] if item else 38400
        short_name = item["short"] if item else sel_name

        try:
            qty = int(self.ent_w308_qty.get().strip().replace(",", ""))
        except Exception:
            qty = 0

        try:
            price = int(self.ent_w308_price.get().strip().replace(",", ""))
        except Exception:
            price = 0

        cash_stack = self.get_current_cash_stack()
        total_coins = qty * price

        # Exact in-game shorthand for OSRS trade "Enter amount:" prompt (e.g. 7580k, 15m)
        if total_coins > 0:
            if total_coins % 1_000_000 == 0:
                trade_shorthand = f"{total_coins // 1_000_000}m"
            elif total_coins % 1_000 == 0:
                trade_shorthand = f"{total_coins // 1_000}k"
            else:
                trade_shorthand = str(total_coins)
        else:
            trade_shorthand = "0"

        c_str = f"{total_coins / 1_000_000:.2f}M" if total_coins >= 1_000_000 else f"{total_coins:,}"
        p_ad = f"{price / 1000:.1f}k" if price % 1000 != 0 else f"{price // 1000}k"

        if is_seller:
            mat_cost_ea, mat_desc = self.get_w308_item_material_cost(item) if item else (0, "")
            total_mat_cost = qty * mat_cost_ea
            net_profit = total_coins - total_mat_cost
            profit_ea = (net_profit // qty) if qty > 0 else 0
            margin_pct = (profit_ea / mat_cost_ea * 100.0) if mat_cost_ea > 0 else 0.0
            xp_ea = item.get("xp", 0.0) if item else 0.0
            total_xp = int(qty * xp_ea)
            skill = item.get("skill", "Smithing") if item else "Smithing"

            self.lbl_v_coins.config(text=f"Coins To Receive: {total_coins:,} gp ({c_str})")
            self.lbl_v_alch.config(text=f"GE Material Cost: {total_mat_cost:,} gp ({mat_cost_ea:,}/ea)")
            self.lbl_v_nat.config(text=f"Training XP: +{total_xp:,} {skill} XP (+{xp_ea:.1f}/ea)")

            prof_color = "#2ecc71" if net_profit >= 0 else "#e74c3c"
            self.lbl_v_profit.config(text=f"Net Smither Profit: {net_profit:+,} gp ({profit_ea:+,}/ea, {margin_pct:.1f}%)", fg=prof_color)

            # Working capital / material budget check
            rem_budget = cash_stack - total_mat_cost
            if hasattr(self, "lbl_v_budget_status"):
                if rem_budget >= 0:
                    self.lbl_v_budget_status.config(
                        text=f"🪙 Bar Budget: {format_gp(cash_stack)} | Material Outlay: {total_mat_cost:,} gp | Surplus: {rem_budget:,} gp",
                        fg="#2ecc71"
                    )
                else:
                    deficit = abs(rem_budget)
                    self.lbl_v_budget_status.config(
                        text=f"⚠️ Over Budget by {deficit:,} gp! (Need {total_mat_cost:,} gp for materials, have {format_gp(cash_stack)})",
                        fg="#e74c3c"
                    )

            self.lbl_v_warning.config(
                text=f"🛡️ 2nd Trade Screen: Offer {qty:,} noted {sel_name} | VERIFY BUYER OFFERS EXACTLY {total_coins:,} gp (Type: {trade_shorthand})!"
            )
            self.btn_copy_coins.config(
                text=f"🛡️ Verify: {trade_shorthand}",
                command=lambda: self.on_click_verify_seller_coins(trade_shorthand, total_coins, qty, sel_name)
            )
            if hasattr(self, "btn_copy_validator_ad"):
                ad_text = f"Selling {qty:,} {short_name} {p_ad} ea Bulk - Trade Me" if qty > 0 else f"Selling {short_name} {p_ad} ea Bulk - Trade Me"
                self.btn_copy_validator_ad.config(
                    text="📢 Copy Seller Ad",
                    command=lambda: self.copy_to_clipboard(ad_text, f"Copied seller trade ad: '{ad_text}'")
                )
        else:
            nat_cost = self.get_effective_nature_price()
            total_alch = qty * alch_val
            total_nats = qty * nat_cost
            net_profit = total_alch - total_coins - total_nats
            profit_ea = (net_profit // qty) if qty > 0 else 0

            a_str = f"{total_alch / 1_000_000:.2f}M" if total_alch >= 1_000_000 else f"{total_alch:,}"

            self.lbl_v_coins.config(text=f"Coins To Give: {total_coins:,} gp (Type: {trade_shorthand})")
            self.lbl_v_alch.config(text=f"High Alch: {total_alch:,} gp ({a_str})")
            self.lbl_v_nat.config(text=f"Nature Cost: {total_nats:,} gp ({qty:,} @ {nat_cost} ea)")

            prof_color = "#2ecc71" if net_profit >= 0 else "#e74c3c"
            self.lbl_v_profit.config(text=f"Net Profit: {net_profit:+,} gp ({profit_ea:+,}/ea)", fg=prof_color)

            # Budget Check & Remaining Cash Display
            remaining_cash = cash_stack - total_coins
            if hasattr(self, "lbl_v_budget_status"):
                if remaining_cash >= 0:
                    rem_str = f"{remaining_cash / 1_000_000:.2f}M" if remaining_cash >= 1_000_000 else f"{remaining_cash:,}"
                    self.lbl_v_budget_status.config(
                        text=f"🪙 Money Stack: {format_gp(cash_stack)} | Remaining Change: {remaining_cash:,} gp ({rem_str})",
                        fg="#2ecc71"
                    )
                else:
                    over = abs(remaining_cash)
                    self.lbl_v_budget_status.config(
                        text=f"⚠️ Over Budget by {over:,} gp! (Your stack: {format_gp(cash_stack)})",
                        fg="#e74c3c"
                    )

            self.lbl_v_warning.config(
                text=f"⌨️ Trade Screen: Offer-X Coins ➔ Type '{trade_shorthand}' (Enter) | Verify: {qty:,} noted {sel_name}"
            )
            self.btn_copy_coins.config(
                text=f"⌨️ Type: {trade_shorthand}",
                command=lambda: self.on_click_copy_trade_coins(trade_shorthand, total_coins)
            )
            if hasattr(self, "btn_copy_validator_ad"):
                ad_text = f"Buying {qty:,} {short_name} {p_ad} ea Bulk - Trade Me" if qty > 0 else f"Buying {short_name} {p_ad} ea Bulk - Trade Me"
                self.btn_copy_validator_ad.config(
                    text="📢 Copy Custom Ad",
                    command=lambda: self.copy_to_clipboard(ad_text, f"Copied trade ad: '{ad_text}'")
                )

    def on_click_copy_trade_coins(self, shorthand, total_coins):
        self.copy_to_clipboard(shorthand, f"Offer-X: Type '{shorthand}' in Trade Screen ({total_coins:,} gp)")
        FloatingToast(
            self,
            "OSRS Trade Amount",
            f"⌨️ In OSRS Trade Screen:\n1. Right-click Coins ➔ Offer-X\n2. Type '{shorthand}' and hit Enter!\n(OSRS automatically enters {total_coins:,} gp)",
            3500
        )

    def on_click_verify_seller_coins(self, shorthand, total_coins, qty, item_name):
        self.copy_to_clipboard(str(total_coins), f"Copied exact coin total: {total_coins:,} gp")
        FloatingToast(
            self,
            "Anti-Scam 2nd Screen Verification",
            f"🛡️ Before Accepting Trade:\n1. Verify other player placed: {total_coins:,} gp ({shorthand})\n2. Verify you are offering: {qty:,} noted {item_name}\n3. Watch for flashing exclamation marks indicating trade alterations!",
            4000
        )

    def log_w308_trade_to_session(self):
        sel_name = self.var_w308_item.get()
        item = next((it for it in W308_STAPLES if it["name"] == sel_name), None)
        if not item:
            return

        try:
            qty = int(self.ent_w308_qty.get().strip().replace(",", ""))
            price = int(self.ent_w308_price.get().strip().replace(",", ""))
        except Exception:
            messagebox.showerror("Invalid Input", "Please enter valid whole numbers for quantity and price.")
            return

        if qty <= 0 or price <= 0:
            messagebox.showerror("Invalid Input", "Quantity and price must be greater than zero.")
            return

        active_acc = getattr(self.state, "active_account", "Default")
        if not active_acc or active_acc in ("All", "All Accounts"):
            active_acc = self.var_account.get() if getattr(self, "var_account", None) and self.var_account.get() != "All Accounts" else "Default"

        is_seller = getattr(self, "var_w308_role", None) and self.var_w308_role.get() == "seller"
        if is_seller:
            mat_cost_ea, _ = self.get_w308_item_material_cost(item)
            net_profit = (price - mat_cost_ea) * qty
            self.state.log_trade_flip(
                item_id=item["id"],
                item_name=f"{item['name']} (Forged/Crafted)",
                qty=qty,
                buy_price=mat_cost_ea,
                sell_price=price,
                profit=net_profit,
                account=active_acc
            )
            self.update_session_display()
            FloatingToast(self, "W308 Smither Trade Logged", f"Logged {qty:,}x {item['name']} ({net_profit:+,} gp realized profit) to Session Tracker!", 4000)
        else:
            nat_cost = self.get_effective_nature_price()
            self.state.log_alch_batch(
                item_id=item["id"],
                item_name=item["name"],
                qty=qty,
                buy_price=price,
                nat_price=nat_cost,
                alch_val=item["alch"],
                account=active_acc
            )
            self.update_session_display()
            total_profit = (item["alch"] - (price + nat_cost)) * qty
            FloatingToast(self, "W308 Trade Logged", f"Logged {qty:,}x {item['name']} ({total_profit:+,} gp realized profit) to Session Tracker!", 4000)

    def toggle_sort_w308(self, col):
        if getattr(self, "w308_sort_col", None) == col:
            self.w308_sort_desc = not self.w308_sort_desc
        else:
            self.w308_sort_col = col
            self.w308_sort_desc = True if col in ("profit_ea", "margin_pct", "max_stack", "total_spend", "expected_profit", "alch_val") else False
        self.recalculate_w308_table()

    def on_w308_mem_filter_changed(self):
        self.update_w308_combobox_items()
        self.on_w308_validator_item_selected()
        self.recalculate_w308_table()

    def recalculate_w308_table(self):
        if not hasattr(self, "tree_w308"):
            return

        is_seller = getattr(self, "var_w308_role", None) and self.var_w308_role.get() == "seller"
        nat_cost = self.get_effective_nature_price()
        cash_stack = self.get_current_cash_stack()
        search_query = self.ent_search.get().strip().lower() if hasattr(self, "ent_search") else ""
        mem_filter = getattr(self, "var_w308_mem_filter", None)
        f_mode = mem_filter.get() if mem_filter else "all"

        rows = []
        if is_seller:
            for it in W308_STAPLES:
                if not it.get("skill"):
                    continue
                is_mem = it.get("members", False)
                if f_mode == "f2p" and is_mem:
                    continue
                if f_mode == "p2p" and not is_mem:
                    continue
                item_name = it["name"]
                if search_query and search_query not in item_name.lower():
                    continue

                item_id = it["id"]
                w308_sell = it.get("w308_sell_p2p", 37875)
                mat_cost_ea, _ = self.get_w308_item_material_cost(it)

                profit_ea = w308_sell - mat_cost_ea
                margin_pct = (profit_ea / mat_cost_ea * 100.0) if mat_cost_ea > 0 else 0.0
                max_forge = (cash_stack // mat_cost_ea) if mat_cost_ea > 0 else 0
                total_spend = max_forge * mat_cost_ea
                expected_profit = max_forge * profit_ea
                xp_ea = it.get("xp", 0.0)
                skill_lvl = f"{it.get('skill', '')} {it.get('level', '')}"
                p_str = f"{w308_sell / 1000:.1f}k" if w308_sell % 1000 != 0 else f"{w308_sell // 1000}k"
                chat_ad = f"Selling {it['short']} {p_str} ea Bulk - Trade Me"

                rows.append({
                    "id": item_id,
                    "item": item_name,
                    "w308_price": w308_sell,
                    "ge_instant": mat_cost_ea,
                    "alch_val": skill_lvl,
                    "profit_ea": profit_ea,
                    "margin_pct": margin_pct,
                    "max_stack": max_forge,
                    "total_spend": total_spend,
                    "expected_profit": expected_profit,
                    "chat_ad": chat_ad,
                    "short": it["short"],
                    "xp_ea": xp_ea,
                    "total_xp": int(max_forge * xp_ea)
                })
        else:
            for it in W308_STAPLES:
                is_mem = it.get("members", False)
                if f_mode == "f2p" and is_mem:
                    continue
                if f_mode == "p2p" and not is_mem:
                    continue
                item_name = it["name"]
                if search_query and search_query not in item_name.lower():
                    continue

                item_id = it["id"]
                alch_val = it["alch"]
                w308_buy = it["w308_buy"]

                # GE Instant price from API if present
                ge_data = self.api.latest_prices.get(str(item_id)) or self.api.latest_prices.get(item_id) or {}
                ge_instant = ge_data.get("high") or ge_data.get("low") or w308_buy

                profit_ea = alch_val - (w308_buy + nat_cost)
                margin_pct = (profit_ea / w308_buy * 100.0) if w308_buy > 0 else 0.0
                max_stack = (cash_stack // w308_buy) if w308_buy > 0 else 0
                total_spend = max_stack * w308_buy
                expected_profit = max_stack * profit_ea
                p_str = f"{w308_buy / 1000:.1f}k" if w308_buy % 1000 != 0 else f"{w308_buy // 1000}k"
                chat_ad = f"Buying {it['short']} {p_str} ea Bulk - Trade Me"

                rows.append({
                    "id": item_id,
                    "item": item_name,
                    "w308_price": w308_buy,
                    "ge_instant": ge_instant,
                    "alch_val": alch_val,
                    "profit_ea": profit_ea,
                    "margin_pct": margin_pct,
                    "max_stack": max_stack,
                    "total_spend": total_spend,
                    "expected_profit": expected_profit,
                    "chat_ad": chat_ad,
                    "short": it["short"]
                })

        self.w308_rows = rows

        # Sort
        col = getattr(self, "w308_sort_col", "profit_ea")
        desc = getattr(self, "w308_sort_desc", True)
        if col in ("item", "chat_ad", "alch_val"):
            self.w308_rows.sort(key=lambda r: str(r.get(col, "")).lower(), reverse=desc)
        else:
            self.w308_rows.sort(key=lambda r: r.get(col, 0), reverse=desc)

        # Update headings
        if is_seller:
            col_names = {
                "item": "Crafted Item",
                "w308_price": "W308 Sell (ea)",
                "ge_instant": "Material Cost (ea)",
                "alch_val": "Skill & Lvl",
                "profit_ea": "Profit / Ea",
                "margin_pct": "XP / Item",
                "max_stack": "Max Forge (Budget)",
                "total_spend": "Total Bar Cost",
                "expected_profit": "Net Smither Profit",
                "chat_ad": "Seller Ad Copy"
            }
        else:
            col_names = {
                "item": "Bulk Item",
                "w308_price": "W308 Buy (ea)",
                "ge_instant": "GE Instant (ea)",
                "alch_val": "High Alch",
                "profit_ea": "Profit / Ea",
                "margin_pct": "Margin %",
                "max_stack": "Max Stack (Budget)",
                "total_spend": "Total Spend",
                "expected_profit": "Expected Net Profit",
                "chat_ad": "Chat Ad Copy"
            }

        for col_id, base_text in col_names.items():
            if col == col_id:
                indicator = " ▼" if desc else " ▲"
                self.tree_w308.heading(col_id, text=f"{base_text}{indicator}")
            else:
                self.tree_w308.heading(col_id, text=base_text)

        # Insert items
        self.tree_w308.delete(*self.tree_w308.get_children())
        for r in self.w308_rows:
            p_ea_str = f"+{r['profit_ea']:,} gp" if r['profit_ea'] >= 0 else f"{r['profit_ea']:,} gp"
            tot_p_str = f"+{format_gp(r['expected_profit'])}" if r['expected_profit'] >= 0 else f"-{format_gp(abs(r['expected_profit']))}"
            
            if is_seller:
                alch_or_skill = str(r["alch_val"])
                margin_or_xp = f"{r.get('xp_ea', 0):.1f} XP"
            else:
                alch_or_skill = f"{r['alch_val']:,} gp"
                margin_or_xp = f"{r['margin_pct']:.1f}%"

            self.tree_w308.insert("", "end", iid=str(r["id"]), values=(
                r["item"],
                f"{r['w308_price']:,} gp",
                f"{r['ge_instant']:,} gp",
                alch_or_skill,
                p_ea_str,
                margin_or_xp,
                f"{r['max_stack']:,}",
                format_gp(r["total_spend"]),
                tot_p_str,
                r["chat_ad"]
            ))

        # Update Money Stack Allocation banner
        if hasattr(self, "lbl_w308_budget"):
            if is_seller:
                self.lbl_w308_budget.config(text=f"💰 Working Capital (Bar Budget): {format_gp(cash_stack)}")
            else:
                self.lbl_w308_budget.config(text=f"💰 Active Money Stack: {format_gp(cash_stack)}")

        if hasattr(self, "lbl_w308_top_pick") and self.w308_rows:
            best = max(self.w308_rows, key=lambda r: r.get("expected_profit", 0))
            if best and best.get("max_stack", 0) > 0:
                if is_seller:
                    self.lbl_w308_top_pick.config(
                        text=f"🏆 Top Smither Pick: {best['max_stack']:,}x {best['item']} (+{format_gp(best['expected_profit'])} profit, +{best.get('total_xp', 0):,} XP)"
                    )
                else:
                    self.lbl_w308_top_pick.config(
                        text=f"🏆 Top Stack Pick: {best['max_stack']:,}x {best['item']} (+{format_gp(best['expected_profit'])} profit)"
                    )

        sel_acc = self.var_account.get() if hasattr(self, "var_account") else "Default"
        acc = self.state.accounts.get(sel_acc) or (max(self.state.accounts.values(), key=lambda a: a.get("last_seen", 0)) if self.state.accounts else {})
        b_name = acc.get("batch_item_name", "")
        b_qty = acc.get("batch_item_qty", 0)

        if hasattr(self, "btn_w308_inv_item"):
            if b_name and b_qty > 0:
                self.btn_w308_inv_item.config(text=f"📦 In Backpack: {b_qty:,}x {b_name}", state="normal", bg="#27ae60", fg="#ffffff")
            else:
                self.btn_w308_inv_item.config(text="📦 Load Inventory Items", state="normal", bg="#2d2d30", fg="#3498db")

        # Update ad buttons with exact quantity from cash stack or inventory
        if hasattr(self, "btn_ad_r2h"):
            r2h_item = next((it for it in W308_STAPLES if it["id"] == 1319), None)
            if is_seller:
                inv_r2h = b_qty if b_name == "Rune 2h sword" else 0
                mat_cost, _ = self.get_w308_item_material_cost(r2h_item) if r2h_item else (36525, "")
                r2h_cnt = inv_r2h if inv_r2h > 0 else (cash_stack // mat_cost if mat_cost > 0 else 0)
                sell_p = r2h_item.get("w308_sell_p2p", 37875) if r2h_item else 37875
                p_str = f"{sell_p / 1000:.1f}k" if sell_p % 1000 != 0 else f"{sell_p // 1000}k"
                self.btn_ad_r2h.config(text=f"Copy: Selling {r2h_cnt:,} R2H {p_str} ea" if r2h_cnt > 0 else f"Copy: Selling R2H {p_str} ea")
            else:
                r2h_cnt = cash_stack // 37600
                self.btn_ad_r2h.config(text=f"Copy: Buying {r2h_cnt:,} R2H 37.6k ea" if r2h_cnt > 0 else "Copy: Buying R2H 37.6k ea")

        if hasattr(self, "btn_ad_legs"):
            legs_item = next((it for it in W308_STAPLES if it["id"] == 1079), None)
            if is_seller:
                inv_legs = b_qty if b_name in ("Rune platelegs", "Rune plateskirt") else 0
                mat_cost, _ = self.get_w308_item_material_cost(legs_item) if legs_item else (36525, "")
                legs_cnt = inv_legs if inv_legs > 0 else (cash_stack // mat_cost if mat_cost > 0 else 0)
                sell_p = legs_item.get("w308_sell_p2p", 37875) if legs_item else 37875
                p_str = f"{sell_p / 1000:.1f}k" if sell_p % 1000 != 0 else f"{sell_p // 1000}k"
                self.btn_ad_legs.config(text=f"Copy: Selling {legs_cnt:,} Legs {p_str} ea" if legs_cnt > 0 else f"Copy: Selling Legs {p_str} ea")
            else:
                legs_cnt = cash_stack // 37600
                self.btn_ad_legs.config(text=f"Copy: Buying {legs_cnt:,} Legs/Skirts 37.6k" if legs_cnt > 0 else "Copy: Buying Legs/Skirts 37.6k")

        if hasattr(self, "calculate_w308_trade_validator"):
            self.calculate_w308_trade_validator()

    def on_w308_click(self, event):
        region = self.tree_w308.identify_region(event.x, event.y)
        if region != "cell":
            return
        col = self.tree_w308.identify_column(event.x)
        row_id = self.tree_w308.identify_row(event.y)
        if not row_id:
            return
        row = next((r for r in self.w308_rows if str(r["id"]) == str(row_id)), None)
        if not row:
            return

        is_seller = getattr(self, "var_w308_role", None) and self.var_w308_role.get() == "seller"
        if col == "#1":  # item
            self.copy_to_clipboard(row["item"], f"Copied '{row['item']}'")
        elif col == "#2":  # w308_price
            lbl = "W308 Sell Price" if is_seller else "W308 Buy Price"
            self.copy_to_clipboard(str(row["w308_price"]), f"Copied {lbl}: {row['w308_price']:,} gp")
        elif col == "#7":  # max_stack
            lbl = "Max Forge" if is_seller else "Max Stack"
            self.copy_to_clipboard(str(row["max_stack"]), f"Copied {lbl}: {row['max_stack']:,}")
        elif col == "#10":  # chat_ad
            lbl = "Seller Ad" if is_seller else "Chat Ad"
            self.copy_to_clipboard(row["chat_ad"], f"Copied {lbl}: '{row['chat_ad']}'")

    def on_w308_double_click(self, event):
        row_id = self.tree_w308.identify_row(event.y)
        if not row_id:
            return
        row = next((r for r in self.w308_rows if str(r["id"]) == str(row_id)), None)
        if not row:
            return
        self.var_w308_item.set(row["item"])
        self.ent_w308_price.delete(0, tk.END)
        self.ent_w308_price.insert(0, str(row["w308_price"]))
        self.ent_w308_qty.delete(0, tk.END)
        self.ent_w308_qty.insert(0, str(row["max_stack"] if row["max_stack"] > 0 else 1))
        self.calculate_w308_trade_validator()
        is_seller = getattr(self, "var_w308_role", None) and self.var_w308_role.get() == "seller"
        mode_str = "Smither Mode" if is_seller else "Buyer Mode"
        FloatingToast(self, "Trade Validator Loaded", f"Loaded {row['item']} into Trade Validator ({mode_str})!", 2500)

    def on_w308_right_click(self, event):
        row_id = self.tree_w308.identify_row(event.y)
        if not row_id:
            return
        self.tree_w308.selection_set(row_id)
        row = next((r for r in self.w308_rows if str(r["id"]) == str(row_id)), None)
        if not row:
            return

        is_seller = getattr(self, "var_w308_role", None) and self.var_w308_role.get() == "seller"
        menu = tk.Menu(self, tearoff=0, bg="#252528", fg="#f1f1f1", activebackground="#f39c12", activeforeground="#000000")
        menu.add_command(label=f"🛡️ Load {row['item']} into Trade Validator", command=lambda: self.on_w308_double_click(event))
        ad_lbl = "Seller Ad" if is_seller else "Chat Ad"
        menu.add_command(label=f"📢 Copy {ad_lbl} ('{row['chat_ad']}')", command=lambda: self.copy_to_clipboard(row["chat_ad"], f"Copied {ad_lbl}"))
        price_lbl = f"Sell Price ({row['w308_price']:,} gp)" if is_seller else f"Buy Price ({row['w308_price']:,} gp)"
        menu.add_command(label=f"💰 Copy {price_lbl}", command=lambda: self.copy_to_clipboard(str(row["w308_price"]), f"Copied price"))
        stack_lbl = f"Max Forge ({row['max_stack']:,})" if is_seller else f"Max Stack ({row['max_stack']:,})"
        menu.add_command(label=f"📦 Copy {stack_lbl}", command=lambda: self.copy_to_clipboard(str(row["max_stack"]), f"Copied stack"))
        menu.tk_popup(event.x_root, event.y_root)

    def build_bond_tab(self):
        container = ttk.Frame(self.tab_bond)
        container.pack(fill="both", expand=True, padx=6, pady=4)

        # 1. Header & Market Strategy Banner
        self.bond_banner_card = tk.Frame(container, bg="#202023", relief="solid", borderwidth=1, padx=10, pady=6)
        self.bond_banner_card.pack(fill="x", pady=(2, 6))

        b_top = tk.Frame(self.bond_banner_card, bg="#202023")
        b_top.pack(fill="x")

        lbl_b_title = tk.Label(b_top, text="🎟️ Old School Bond Roadmap & 14-Day Freedom Engine", font=("Segoe UI", 11, "bold"), fg="#f1c40f", bg="#202023")
        lbl_b_title.pack(side="left", padx=(0, 10))
        ToolTip(lbl_b_title, "Track live Old School Bond market prices (Item ID 13190), plan your transition to Members,\nand simulate perpetual membership sustainment using High Alchemy profits.")

        lbl_b_badge = tk.Label(b_top, text="⚡ Live OSRS Wiki Ticker", font=("Segoe UI", 9, "bold"), fg="#2ecc71", bg="#202023")
        lbl_b_badge.pack(side="left", padx=(0, 12))

        btn_refresh_bond = tk.Button(b_top, text="🔄 Refresh Bond Market", command=self.refresh_bond_data,
                                     bg="#3498db", fg="#ffffff", font=("Segoe UI", 8, "bold"), relief="flat", padx=8, pady=1, cursor="hand2")
        btn_refresh_bond.pack(side="right")
        ToolTip(btn_refresh_bond, "Refresh live bond prices and timeseries analysis directly from the OSRS Wiki API.")

        self.lbl_bond_tip = tk.Label(
            self.bond_banner_card,
            text="💡 Overnight Dip Sniping: Never insta-buy a bond during daytime peak hours. Bidding at the overnight valley (01:00–06:00 UTC) saves ~300k–550k gp compared to insta-buying!",
            font=("Segoe UI", 9, "italic"), fg="#e0e0e0", bg="#202023"
        )
        self.lbl_bond_tip.pack(anchor="w", pady=(4, 0))

        # Main scrollable canvas so everything fits on any resolution
        canvas = tk.Canvas(container, bg="#1e1e1e", highlightthickness=0)
        v_scroll = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scroll_content = tk.Frame(canvas, bg="#1e1e1e")

        scroll_content.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas_win = canvas.create_window((0, 0), window=scroll_content, anchor="nw")
        def _on_bond_canvas_resize(e):
            canvas.itemconfig(canvas_win, width=e.width)
        canvas.bind("<Configure>", _on_bond_canvas_resize)
        canvas.configure(yscrollcommand=v_scroll.set)

        canvas.pack(side="left", fill="both", expand=True)
        v_scroll.pack(side="right", fill="y")

        # -------------------------------------------------------------
        # Section 1: Live Bond Ticker & Overnight Dip Sniper Cards
        # -------------------------------------------------------------
        sec1_frame = tk.Frame(scroll_content, bg="#1e1e1e")
        sec1_frame.pack(fill="x", pady=(0, 6))

        # 4 Stat Cards
        cards_row = tk.Frame(sec1_frame, bg="#1e1e1e")
        cards_row.pack(fill="x")

        # Card 1: Insta-Buy (Ask)
        c1 = tk.Frame(cards_row, bg="#252528", relief="solid", borderwidth=1, padx=12, pady=8)
        c1.pack(side="left", expand=True, fill="both", padx=4)
        tk.Label(c1, text="🛒 Insta-Buy (Ask)", font=("Segoe UI", 9), fg="#aaaaaa", bg="#252528").pack(anchor="w")
        self.card_bond_ask = tk.Label(c1, text="-- gp", font=("Segoe UI", 13, "bold"), fg="#e74c3c", bg="#252528")
        self.card_bond_ask.pack(anchor="w", pady=(2, 0))
        ToolTip(c1, "Current Grand Exchange Insta-Buy price (Lowest active sell offer).\nAvoid buying at this price unless you need immediate membership!")

        # Card 2: Patient Dip Bid (Recommended)
        c2 = tk.Frame(cards_row, bg="#252528", relief="solid", borderwidth=1, padx=12, pady=8)
        c2.pack(side="left", expand=True, fill="both", padx=4)
        c2_top = tk.Frame(c2, bg="#252528")
        c2_top.pack(fill="x")
        tk.Label(c2_top, text="🎯 Patient Dip Bid", font=("Segoe UI", 9, "bold"), fg="#2ecc71", bg="#252528").pack(side="left")
        btn_copy_bid = tk.Button(c2_top, text="📋 Copy Bid", command=self.copy_bond_bid,
                                 bg="#2ecc71", fg="#000000", font=("Segoe UI", 8, "bold"), relief="flat", padx=6, pady=0, cursor="hand2")
        btn_copy_bid.pack(side="right")
        ToolTip(btn_copy_bid, "Copy the recommended patient bond bid price to clipboard for easy pasting into the GE offer window.")
        self.card_bond_bid = tk.Label(c2, text="-- gp", font=("Segoe UI", 13, "bold"), fg="#2ecc71", bg="#252528")
        self.card_bond_bid.pack(anchor="w", pady=(2, 0))
        ToolTip(c2, "Recommended patient GE buy bid based on 48h percentile dip analysis.\nLeave this offer active overnight to catch undercut dumps!")

        # Card 3: Patient Savings
        c3 = tk.Frame(cards_row, bg="#252528", relief="solid", borderwidth=1, padx=12, pady=8)
        c3.pack(side="left", expand=True, fill="both", padx=4)
        tk.Label(c3, text="💰 Patient Bid Savings", font=("Segoe UI", 9), fg="#aaaaaa", bg="#252528").pack(anchor="w")
        self.card_bond_savings = tk.Label(c3, text="-- gp", font=("Segoe UI", 13, "bold"), fg="#00d2d3", bg="#252528")
        self.card_bond_savings.pack(anchor="w", pady=(2, 0))
        ToolTip(c3, "Total gold saved by placing a patient bid instead of insta-buying from impatient sellers.")

        # Card 4: 7-Day Range & Daily Volume
        c4 = tk.Frame(cards_row, bg="#252528", relief="solid", borderwidth=1, padx=12, pady=8)
        c4.pack(side="left", expand=True, fill="both", padx=4)
        tk.Label(c4, text="📊 7-Day Range & Vol", font=("Segoe UI", 9), fg="#aaaaaa", bg="#252528").pack(anchor="w")
        self.card_bond_range = tk.Label(c4, text="-- gp", font=("Segoe UI", 11, "bold"), fg="#f39c12", bg="#252528")
        self.card_bond_range.pack(anchor="w", pady=(2, 0))
        ToolTip(c4, "7-day low to high price band and average daily trading volume (~12k bonds traded per day).")

        # -------------------------------------------------------------
        # Section 2: Two-Stage Freedom Progress Bar
        # -------------------------------------------------------------
        sec2_card = tk.Frame(scroll_content, bg="#202023", relief="solid", borderwidth=1, padx=12, pady=8)
        sec2_card.pack(fill="x", pady=(4, 6))

        s2_header = tk.Frame(sec2_card, bg="#202023")
        s2_header.pack(fill="x")
        tk.Label(s2_header, text="🚀 Two-Stage Freedom Progress Bar", font=("Segoe UI", 10, "bold"), fg="#f1c40f", bg="#202023").pack(side="left")
        tk.Label(s2_header, text="[Stage 1: Bond Ticket  ➔  Stage 2: P2P Operating Cushion]", font=("Segoe UI", 9), fg="#aaaaaa", bg="#202023").pack(side="left", padx=8)

        # Control Row: Wealth Entry & Cushion Selector
        ctrl_wealth_row = tk.Frame(sec2_card, bg="#202023")
        ctrl_wealth_row.pack(fill="x", pady=(6, 6))

        tk.Label(ctrl_wealth_row, text="💰 Account Wealth:", font=("Segoe UI", 9, "bold"), fg="#e0e0e0", bg="#202023").pack(side="left", padx=(0, 4))
        self.ent_bond_wealth = tk.Entry(ctrl_wealth_row, width=12, bg="#1e1e1e", fg="#2ecc71", insertbackground="#ffffff", relief="flat", font=("Segoe UI", 9, "bold"))
        self.ent_bond_wealth.pack(side="left", padx=(0, 6))
        self.ent_bond_wealth.bind("<FocusOut>", lambda e: self.recalculate_bond_roadmap())
        self.ent_bond_wealth.bind("<Return>", lambda e: self.recalculate_bond_roadmap())
        ToolTip(self.ent_bond_wealth, "Your total account wealth (Cash in inventory/bank + active alch supplies).\nSupports 9.5m, 12m, etc. Edit directly or click Auto-Sync!")

        btn_sync_wealth = tk.Button(ctrl_wealth_row, text="🔄 Auto-Sync From Game", command=self.sync_bond_wealth,
                                    bg="#252528", fg="#2ecc71", font=("Segoe UI", 8, "bold"), relief="flat", padx=6, pady=1, cursor="hand2")
        btn_sync_wealth.pack(side="left", padx=(0, 16))
        ToolTip(btn_sync_wealth, "Automatically pull current coins and account cash balance from RuneLite live tracking.")

        tk.Label(ctrl_wealth_row, text="🛡️ Operating Cushion:", font=("Segoe UI", 9, "bold"), fg="#e0e0e0", bg="#202023").pack(side="left", padx=(0, 4))
        self.var_bond_cushion = tk.StringVar(value="8,000,000 gp (Recommended Balanced)")
        self.cb_bond_cushion = ttk.Combobox(ctrl_wealth_row, textvariable=self.var_bond_cushion,
                                            values=[
                                                "3,000,000 gp (Bare Minimum)",
                                                "5,000,000 gp (Lean / Aggressive)",
                                                "8,000,000 gp (Recommended Balanced)",
                                                "12,000,000 gp (Safe Operating Cushion)",
                                                "15,000,000 gp (High-Roller Capital)"
                                            ],
                                            width=32, state="readonly")
        self.cb_bond_cushion.pack(side="left", padx=(0, 6))
        self.cb_bond_cushion.bind("<<ComboboxSelected>>", lambda e: self.recalculate_bond_roadmap())
        ToolTip(self.cb_bond_cushion, "Operating capital to keep AFTER buying the Bond.\nWhy keep a cushion? If you spend all coins on a bond, you enter Members with 0 gp and cannot buy high-margin P2P items.\nWith 8M cushion, you can immediately utilize all 8 GE slots for 1.2M+ gp/hr profit!")

        # Dual Progress Canvas
        self.canvas_bond_prog = tk.Canvas(sec2_card, bg="#1e1e1e", height=32, highlightthickness=1, highlightbackground="#3e3e42")
        self.canvas_bond_prog.pack(fill="x", pady=(4, 6))
        self.canvas_bond_prog.bind("<Configure>", lambda e: self.draw_bond_progress())

        # Status Pill / Banner
        self.lbl_bond_stage_status = tk.Label(
            sec2_card,
            text="Calculating Freedom Progress...",
            font=("Segoe UI", 9, "bold"), fg="#ffffff", bg="#252528", padx=10, pady=5, relief="flat"
        )
        self.lbl_bond_stage_status.pack(fill="x", pady=(2, 0))

        # -------------------------------------------------------------
        # Section 3: Time-to-Goal Engine & Pace Calculator
        # -------------------------------------------------------------
        sec3_card = tk.Frame(scroll_content, bg="#202023", relief="solid", borderwidth=1, padx=12, pady=8)
        sec3_card.pack(fill="x", pady=(4, 6))

        s3_header = tk.Frame(sec3_card, bg="#202023")
        s3_header.pack(fill="x")
        tk.Label(s3_header, text="⏱️ Time-to-Goal Engine & Daily Pace Calculator", font=("Segoe UI", 10, "bold"), fg="#f1c40f", bg="#202023").pack(side="left")

        # Pace Controls
        ctrl_pace_row = tk.Frame(sec3_card, bg="#202023")
        ctrl_pace_row.pack(fill="x", pady=(6, 6))

        tk.Label(ctrl_pace_row, text="🎮 Daily Playtime:", font=("Segoe UI", 9, "bold"), fg="#e0e0e0", bg="#202023").pack(side="left", padx=(0, 4))
        self.var_bond_playtime = tk.StringVar(value="12 Hours / Day (Hardcore Speedrun)")
        self.cb_bond_playtime = ttk.Combobox(ctrl_pace_row, textvariable=self.var_bond_playtime,
                                             values=[
                                                 "2 Hours / Day (Casual)",
                                                 "4 Hours / Day (Steady)",
                                                 "6 Hours / Day (Dedicated)",
                                                 "8 Hours / Day (Grinder)",
                                                 "12 Hours / Day (Hardcore Speedrun)"
                                             ],
                                             width=30, state="readonly")
        self.cb_bond_playtime.pack(side="left", padx=(0, 16))
        self.cb_bond_playtime.bind("<<ComboboxSelected>>", lambda e: self.recalculate_bond_roadmap())
        ToolTip(self.cb_bond_playtime, "Select how many hours per day you plan to actively play/alch.")

        tk.Label(ctrl_pace_row, text="⚡ Earning Method:", font=("Segoe UI", 9, "bold"), fg="#e0e0e0", bg="#202023").pack(side="left", padx=(0, 4))
        self.var_bond_mode = tk.StringVar(value="⚡ Live Active Session Rate")
        self.cb_bond_mode = ttk.Combobox(ctrl_pace_row, textvariable=self.var_bond_mode,
                                         values=[
                                             "⚡ Live Active Session Rate",
                                             "F2P Pure High Alch (~780k gp/hr)",
                                             "F2P Mixed Flipping & Alch (~600k gp/hr)",
                                             "P2P Members High Alch (~1,200k gp/hr)",
                                             "P2P Members Alch + Herb Runs (~1,600k gp/hr)"
                                         ],
                                         width=36, state="readonly")
        self.cb_bond_mode.pack(side="left", padx=(0, 6))
        self.cb_bond_mode.bind("<<ComboboxSelected>>", lambda e: self.recalculate_bond_roadmap())
        ToolTip(self.cb_bond_mode, "Hourly gold earning benchmark based on live session tracking or method presets.")

        # Pace Result Stat Cards
        pace_cards = tk.Frame(sec3_card, bg="#202023")
        pace_cards.pack(fill="x", pady=(4, 6))

        # Stat 1: Remaining GP
        p1 = tk.Frame(pace_cards, bg="#252528", relief="solid", borderwidth=1, padx=10, pady=6)
        p1.pack(side="left", expand=True, fill="both", padx=3)
        tk.Label(p1, text="Remaining GP Needed", font=("Segoe UI", 8), fg="#aaaaaa", bg="#252528").pack(anchor="w")
        self.card_bond_gp_needed = tk.Label(p1, text="-- gp", font=("Segoe UI", 12, "bold"), fg="#f39c12", bg="#252528")
        self.card_bond_gp_needed.pack(anchor="w", pady=(2, 0))

        # Stat 2: Total Hours
        p2 = tk.Frame(pace_cards, bg="#252528", relief="solid", borderwidth=1, padx=10, pady=6)
        p2.pack(side="left", expand=True, fill="both", padx=3)
        tk.Label(p2, text="Total Grind Hours", font=("Segoe UI", 8), fg="#aaaaaa", bg="#252528").pack(anchor="w")
        self.card_bond_hrs_needed = tk.Label(p2, text="-- hrs", font=("Segoe UI", 12, "bold"), fg="#3498db", bg="#252528")
        self.card_bond_hrs_needed.pack(anchor="w", pady=(2, 0))

        # Stat 3: Calendar Days
        p3 = tk.Frame(pace_cards, bg="#252528", relief="solid", borderwidth=1, padx=10, pady=6)
        p3.pack(side="left", expand=True, fill="both", padx=3)
        tk.Label(p3, text="Days to Freedom Goal", font=("Segoe UI", 8, "bold"), fg="#2ecc71", bg="#252528").pack(anchor="w")
        self.card_bond_days_needed = tk.Label(p3, text="-- Days", font=("Segoe UI", 13, "bold"), fg="#2ecc71", bg="#252528")
        self.card_bond_days_needed.pack(anchor="w", pady=(2, 0))

        # Stat 4: Casts & Magic XP
        p4 = tk.Frame(pace_cards, bg="#252528", relief="solid", borderwidth=1, padx=10, pady=6)
        p4.pack(side="left", expand=True, fill="both", padx=3)
        tk.Label(p4, text="High Alchs / XP Gained", font=("Segoe UI", 8), fg="#aaaaaa", bg="#252528").pack(anchor="w")
        self.card_bond_casts_needed = tk.Label(p4, text="-- casts", font=("Segoe UI", 11, "bold"), fg="#9b59b6", bg="#252528")
        self.card_bond_casts_needed.pack(anchor="w", pady=(2, 0))

        # Pro-Tip Callout: World 308 Anvil GE Limit Bypass Secret
        w308_box = tk.Frame(sec3_card, bg="#1a252f", relief="solid", borderwidth=1, padx=10, pady=6)
        w308_box.pack(fill="x", pady=(4, 0))
        tk.Label(w308_box, text="⚡ F2P Speed Secret — How to Alch 12h/Day Without Hitting GE Limits:", font=("Segoe UI", 9, "bold"), fg="#3498db", bg="#1a252f").pack(anchor="w")
        tk.Label(
            w308_box,
            text="In F2P, the GE limits you to 70 rune items every 4 hours. To alch continuously without waiting for GE limits, visit World 308 at Varrock West Bank (Join as Clan Guest: 'Varrock Mob' or trade in Public Chat). High-level smithers sell thousands of noted Rune 2h swords and battleaxes directly in unlimited bulk for GE mid/low! Zero buy limits!",
            font=("Segoe UI", 8, "italic"), fg="#ecf0f1", bg="#1a252f", wraplength=950, justify="left"
        ).pack(anchor="w", pady=(2, 0))

        # -------------------------------------------------------------
        # Section 4: 14-Day Perpetual Membership Sustainer Simulator
        # -------------------------------------------------------------
        sec4_card = tk.Frame(scroll_content, bg="#202023", relief="solid", borderwidth=1, padx=12, pady=8)
        sec4_card.pack(fill="x", pady=(4, 10))

        s4_header = tk.Frame(sec4_card, bg="#202023")
        s4_header.pack(fill="x")
        tk.Label(s4_header, text="♾️ 14-Day Perpetual Membership Sustainer Simulator", font=("Segoe UI", 10, "bold"), fg="#f1c40f", bg="#202023").pack(side="left")
        tk.Label(s4_header, text="[Shows why your FIRST bond is the only hard one — subsequent bonds are 100% self-funding!]", font=("Segoe UI", 9), fg="#aaaaaa", bg="#202023").pack(side="left", padx=8)

        # Sustainer Treeview Table
        cols_sust = ("daily", "total_hrs", "gross_gp", "bond_cov", "surplus_gp", "milestone")
        self.tree_bond_sustainer = ttk.Treeview(sec4_card, columns=cols_sust, show="headings", height=6)
        self.tree_bond_sustainer.heading("daily", text="Daily Alch Time")
        self.tree_bond_sustainer.heading("total_hrs", text="14-Day Hours")
        self.tree_bond_sustainer.heading("gross_gp", text="Gross P2P Revenue")
        self.tree_bond_sustainer.heading("bond_cov", text="Next Bond Paid?")
        self.tree_bond_sustainer.heading("surplus_gp", text="14-Day Bank Surplus")
        self.tree_bond_sustainer.heading("milestone", text="Player Gear & Wealth Milestone")

        self.tree_bond_sustainer.column("daily", width=140, anchor="w")
        self.tree_bond_sustainer.column("total_hrs", width=95, anchor="center")
        self.tree_bond_sustainer.column("gross_gp", width=130, anchor="e")
        self.tree_bond_sustainer.column("bond_cov", width=115, anchor="center")
        self.tree_bond_sustainer.column("surplus_gp", width=140, anchor="e")
        self.tree_bond_sustainer.column("milestone", width=340, anchor="w")

        self.tree_bond_sustainer.tag_configure("break_even", foreground="#3498db")
        self.tree_bond_sustainer.tag_configure("steady", foreground="#2ecc71")
        self.tree_bond_sustainer.tag_configure("rapid", foreground="#2ecc71", font=("Segoe UI", 9, "bold"))
        self.tree_bond_sustainer.tag_configure("boss", foreground="#f1c40f", font=("Segoe UI", 9, "bold"))
        self.tree_bond_sustainer.tag_configure("master", foreground="#00d2d3", font=("Segoe UI", 9, "bold"))

        self.tree_bond_sustainer.pack(fill="x", pady=(6, 6))

        sust_col_tooltips = {
            "#1": "Daily Active Alch Time:\nHow much time you spend High Alching per day in Members.",
            "#2": "14-Day Total Hours:\nCumulative alching hours across the full 14-day membership period.",
            "#3": "Gross P2P Revenue:\nTotal gold earned at conservative P2P alching rate of ~1.2M gp/hr.",
            "#4": "Next Bond Paid:\nWhether the 14-day earnings completely pay off the next 11.0M Bond.",
            "#5": "14-Day Bank Surplus:\nNet profit left in your bank AFTER purchasing the next 14-day bond!",
            "#6": "Milestones:\nIconic OSRS items you can easily afford with your 14-day surplus gold."
        }
        HeadingToolTip(self.tree_bond_sustainer, sust_col_tooltips)

        # Bottom Freedom Takeaway Box
        freedom_box = tk.Frame(sec4_card, bg="#1b4332", relief="solid", borderwidth=1, padx=10, pady=6)
        freedom_box.pack(fill="x", pady=(2, 0))
        tk.Label(freedom_box, text="🏆 The Infinite Membership Guarantee:", font=("Segoe UI", 9, "bold"), fg="#2ecc71", bg="#1b4332").pack(anchor="w")
        tk.Label(
            freedom_box,
            text="Once you cross into Members with your 8M cushion, you only need ~35 to 45 minutes of alching per day to fund perpetual membership forever. At 12 hours a day, you pay off the next bond in under 1 single day, leaving 13 days of pure compounding profit to build an endgame 100M+ bank!",
            font=("Segoe UI", 8), fg="#d8f3dc", bg="#1b4332", wraplength=950, justify="left"
        ).pack(anchor="w", pady=(2, 0))

        # Initial populate
        self.sync_bond_wealth(silent=True)
        self.refresh_bond_data(silent=True)

    def copy_bond_bid(self):
        data = getattr(self, "bond_data", {})
        bid = data.get("safe_bid") or 10600000
        self.copy_to_clipboard(str(bid), f"Copied patient Bond bid: {bid:,} gp to clipboard!")

    def sync_bond_wealth(self, silent=False):
        wealth = 0
        if hasattr(self, "state") and self.state:
            active_acc = self.var_account.get() if hasattr(self, "var_account") else ""
            if active_acc and active_acc in self.state.accounts:
                acc_data = self.state.accounts[active_acc]
                tot_wealth = acc_data.get("total_wealth", 0)
                if tot_wealth > 0:
                    wealth = tot_wealth
                else:
                    wealth = acc_data.get("coins", 0) + acc_data.get("bank_coins", 0) + acc_data.get("batch_gross_gp", 0)
            elif self.state.accounts:
                wealth = sum(
                    acc.get("total_wealth", 0) or (acc.get("coins", 0) + acc.get("bank_coins", 0) + acc.get("batch_gross_gp", 0))
                    for acc in self.state.accounts.values()
                )
            if wealth == 0:
                wealth = self.state.config.get("cash_stack", 5000000)
        if wealth == 0 and hasattr(self, "ent_cash"):
            wealth = parse_cash_input(self.ent_cash.get())

        if hasattr(self, "ent_bond_wealth"):
            self.ent_bond_wealth.delete(0, tk.END)
            self.ent_bond_wealth.insert(0, format_gp(wealth))
            self.recalculate_bond_roadmap()
            if not silent:
                self.show_status_message(f"Synced account net wealth: {format_gp(wealth)}")

    def refresh_bond_data(self, silent=False):
        try:
            self.bond_data = self.api.get_bond_data(force_refresh=True)
            self.update_bond_display()
            self.recalculate_bond_roadmap()
            if not silent:
                self.show_status_message("Bond market prices updated successfully!")
        except Exception as e:
            print(f"[Bond] Refresh error: {e}")

    def update_bond_display(self):
        data = getattr(self, "bond_data", {})
        if not data:
            return
        if hasattr(self, "card_bond_ask"):
            self.card_bond_ask.config(text=format_gp(data.get("insta_buy", 0)))
        if hasattr(self, "card_bond_bid"):
            self.card_bond_bid.config(text=format_gp(data.get("safe_bid", 0)))
        if hasattr(self, "card_bond_savings"):
            self.card_bond_savings.config(text=f"+{format_gp(data.get('patient_savings', 0))} (Save)")
        if hasattr(self, "card_bond_range"):
            f7 = data.get("floor_7d", 0)
            p7 = data.get("peak_7d", 0)
            vol = data.get("daily_vol", 0)
            self.card_bond_range.config(text=f"{format_gp(f7)} - {format_gp(p7)} ({vol:,}/d)")

    def draw_bond_progress(self):
        if not hasattr(self, "canvas_bond_prog"):
            return
        c = self.canvas_bond_prog
        c.delete("all")
        w = c.winfo_width()
        h = c.winfo_height()
        if w < 50:
            w = 700
        if h < 20:
            h = 32

        data = getattr(self, "bond_data", {})
        bond_cost = data.get("safe_bid") or 11000000

        cushion_raw = self.var_bond_cushion.get() if hasattr(self, "var_bond_cushion") else "8,000,000"
        cushion_val = parse_cash_input(cushion_raw.split()[0])
        if cushion_val <= 0:
            cushion_val = 8000000

        total_goal = bond_cost + cushion_val
        wealth_str = self.ent_bond_wealth.get() if hasattr(self, "ent_bond_wealth") else "0"
        wealth = parse_cash_input(wealth_str)

        split_ratio = bond_cost / total_goal if total_goal > 0 else 0.6
        x_split = int(w * split_ratio)

        # Background
        c.create_rectangle(0, 0, w, h, fill="#252528", outline="")

        if wealth >= bond_cost:
            # Stage 1 complete
            c.create_rectangle(0, 0, x_split, h, fill="#2ecc71", outline="")
            # Stage 2 cushion
            cushion_acc = wealth - bond_cost
            cushion_ratio = min(1.0, cushion_acc / cushion_val) if cushion_val > 0 else 1.0
            x_cushion = x_split + int((w - x_split) * cushion_ratio)
            cushion_color = "#f1c40f" if cushion_ratio < 1.0 else "#00d2d3"
            if x_cushion > x_split:
                c.create_rectangle(x_split, 0, x_cushion, h, fill=cushion_color, outline="")
        else:
            # Stage 1 accumulating
            bond_ratio = max(0.0, wealth / bond_cost) if bond_cost > 0 else 0.0
            x_bond = int(x_split * bond_ratio)
            if x_bond > 0:
                c.create_rectangle(0, 0, x_bond, h, fill="#3498db", outline="")

        # Split line
        c.create_line(x_split, 0, x_split, h, fill="#555555", width=2)

        bond_pct = min(100.0, (wealth / bond_cost) * 100.0) if bond_cost > 0 else 0.0
        cush_acc = max(0, wealth - bond_cost)
        cush_pct = min(100.0, (cush_acc / cushion_val) * 100.0) if cushion_val > 0 else 0.0

        txt_stage1 = f"🎟️ Stage 1: Bond {format_gp(bond_cost)} ({bond_pct:.1f}%)"
        txt_stage2 = f"🛡️ Stage 2: Cushion {format_gp(cushion_val)} ({cush_pct:.1f}%)"

        c.create_text(max(60, x_split // 2), h // 2, text=txt_stage1, font=("Segoe UI", 9, "bold"), fill="#ffffff")
        c.create_text(min(w - 60, x_split + (w - x_split) // 2), h // 2, text=txt_stage2, font=("Segoe UI", 9, "bold"), fill="#ffffff")

    def recalculate_bond_roadmap(self):
        if not hasattr(self, "ent_bond_wealth"):
            return

        data = getattr(self, "bond_data", {})
        bond_cost = data.get("safe_bid") or 11000000

        cushion_raw = self.var_bond_cushion.get() if hasattr(self, "var_bond_cushion") else "8,000,000"
        cushion_val = parse_cash_input(cushion_raw.split()[0])
        if cushion_val <= 0:
            cushion_val = 8000000

        if hasattr(self, "bridge_server") and self.bridge_server:
            self.bridge_server.set_bond_cushion(cushion_val)

        total_goal = bond_cost + cushion_val
        wealth = parse_cash_input(self.ent_bond_wealth.get())

        self.draw_bond_progress()

        # Update Freedom Status Pill
        if wealth < bond_cost:
            rem_bond = bond_cost - wealth
            self.lbl_bond_stage_status.config(
                text=f"🔒 Stage 1: Accumulating First Bond — Need {format_gp(rem_bond)} more to reach Bond purchase threshold ({wealth / bond_cost * 100:.1f}% reached).",
                bg="#1a252f", fg="#3498db"
            )
        elif wealth < total_goal:
            rem_cush = total_goal - wealth
            self.lbl_bond_stage_status.config(
                text=f"⚠️ Stage 2: Bond Cost Secured! Building Operating Cushion — Need {format_gp(rem_cush)} more before redeeming so you don't enter Members broke!",
                bg="#3d2b00", fg="#f39c12"
            )
        else:
            self.lbl_bond_stage_status.config(
                text=f"🎉 FREEDOM ACHIEVED! You have {format_gp(wealth)} (Bond {format_gp(bond_cost)} + Full {format_gp(cushion_val)} Cushion). Ready for Members!",
                bg="#1b4332", fg="#2ecc71"
            )

        # Pace calculations
        play_raw = self.var_bond_playtime.get() if hasattr(self, "var_bond_playtime") else "12"
        try:
            daily_hrs = float(play_raw.split()[0])
        except Exception:
            daily_hrs = 12.0

        mode_raw = self.var_bond_mode.get() if hasattr(self, "var_bond_mode") else ""
        active_acc = self.var_account.get() if hasattr(self, "var_account") else ""
        alchs_per_hr = 1200
        if active_acc and hasattr(self, "state") and active_acc in self.state.accounts:
            a_hr = self.state.accounts[active_acc].get("alchs_per_hour", 0)
            if a_hr > 0:
                alchs_per_hr = a_hr

        if "Live" in mode_raw:
            live_rate = 0
            if active_acc and hasattr(self, "state") and active_acc in self.state.accounts:
                live_rate = self.state.accounts[active_acc].get("profit_per_hour", 0)
            if live_rate <= 0 and hasattr(self, "state") and self.state.accounts:
                live_rate = max((acc.get("profit_per_hour", 0) for acc in self.state.accounts.values()), default=0)
            if live_rate <= 0:
                live_rate = getattr(self, "live_session_profit_hr", 0)
            rate = max(100000, int(live_rate)) if live_rate > 0 else 780000
        elif "780k" in mode_raw:
            rate = 780000
        elif "600k" in mode_raw:
            rate = 600000
        elif "1,600k" in mode_raw:
            rate = 1600000
        elif "1,200k" in mode_raw:
            rate = 1200000
        else:
            rate = 780000

        needed_gp = max(0, total_goal - wealth)
        hrs_needed = (needed_gp / rate) if rate > 0 else 0.0
        days_needed = (hrs_needed / daily_hrs) if daily_hrs > 0 else 0.0
        casts_needed = int(hrs_needed * alchs_per_hr)
        magic_xp = casts_needed * 65

        if hasattr(self, "card_bond_gp_needed"):
            self.card_bond_gp_needed.config(text=format_gp(needed_gp))
        if hasattr(self, "card_bond_hrs_needed"):
            self.card_bond_hrs_needed.config(text=f"{hrs_needed:.1f} Hours")
        if hasattr(self, "card_bond_days_needed"):
            self.card_bond_days_needed.config(text=f"{days_needed:.1f} Days ({days_needed * 24:.0f}h calendar)")
        if hasattr(self, "card_bond_casts_needed"):
            self.card_bond_casts_needed.config(text=f"{casts_needed:,} alchs (+{magic_xp:,} XP)")

        # Sustainer treeview
        if hasattr(self, "tree_bond_sustainer"):
            for item in self.tree_bond_sustainer.get_children():
                self.tree_bond_sustainer.delete(item)

            sust_specs = [
                ("35 - 45 mins / day", 9.2, 1.2, "✅ 100% Fully Paid", "🪙 Infinite Membership (Zero real cash ever again)", "break_even"),
                ("2 Hours / day", 28.0, 1.2, "✅ 100% Fully Paid", "⚔️ Mid-Tier Gear (Abyssal whip, Fury, Dragon boots)", "steady"),
                ("4 Hours / day", 56.0, 1.2, "✅ 100% Fully Paid", "🛡️ High-Tier Gear (Bandos tassets, Ahrim's, Blowpipe)", "rapid"),
                ("6 Hours / day", 84.0, 1.2, "✅ 100% Fully Paid", "💎 100M+ Bank (Full Zenyte jewelry, Fang)", "rapid"),
                ("8 Hours / day", 112.0, 1.2, "✅ 100% Fully Paid", "🏹 Bossing Ready (Bow of Faerdhinen, Crystal armour)", "boss"),
                ("12 Hours / day", 168.0, 1.2, "✅ 100% Fully Paid", "👑 Economy Master (+190M liquid surplus every 14 days!)", "master"),
            ]

            for daily_label, hrs_14d, rate_m, status_txt, milestone_txt, tag in sust_specs:
                gross_gp = int(hrs_14d * rate_m * 1_000_000)
                surplus_gp = max(0, gross_gp - bond_cost)
                surplus_str = f"+{format_gp(surplus_gp)}" if surplus_gp > 0 else "+0 gp"
                self.tree_bond_sustainer.insert("", "end", values=(
                    daily_label,
                    f"{hrs_14d:.1f} hrs",
                    format_gp(gross_gp),
                    status_txt,
                    surplus_str,
                    milestone_txt
                ), tags=(tag,))

    def build_craft_tab(self):
        sub_top = tk.Frame(self.tab_craft, bg="#252528")
        sub_top.pack(fill="x", padx=6, pady=(6, 2))

        tk.Label(sub_top, text="Your Stats:", font=("Segoe UI", 9, "bold"), fg="#f39c12", bg="#252528").pack(side="left", padx=4)

        levels = self.state.config.get("player_levels", {})
        tk.Label(sub_top, text="Crafting:", fg="#cccccc", bg="#252528").pack(side="left")
        self.ent_craft_lvl = tk.Entry(sub_top, width=4, bg="#1e1e1e", fg="#ffffff", relief="flat")
        self.ent_craft_lvl.insert(0, str(levels.get("Crafting", 99)))
        self.ent_craft_lvl.pack(side="left", padx=(2, 6))
        self.ent_craft_lvl.bind("<FocusOut>", self.on_levels_changed)
        ToolTip(self.ent_craft_lvl, "Your in-game Crafting level. Recipes above this level are flagged or hidden.")

        tk.Label(sub_top, text="Smithing:", fg="#cccccc", bg="#252528").pack(side="left")
        self.ent_smith_lvl = tk.Entry(sub_top, width=4, bg="#1e1e1e", fg="#ffffff", relief="flat")
        self.ent_smith_lvl.insert(0, str(levels.get("Smithing", 99)))
        self.ent_smith_lvl.pack(side="left", padx=(2, 6))
        self.ent_smith_lvl.bind("<FocusOut>", self.on_levels_changed)
        ToolTip(self.ent_smith_lvl, "Your in-game Smithing level. Recipes above this level are flagged or hidden.")

        tk.Label(sub_top, text="Fletching:", fg="#cccccc", bg="#252528").pack(side="left")
        self.ent_fletch_lvl = tk.Entry(sub_top, width=4, bg="#1e1e1e", fg="#ffffff", relief="flat")
        self.ent_fletch_lvl.insert(0, str(levels.get("Fletching", 99)))
        self.ent_fletch_lvl.pack(side="left", padx=(2, 6))
        self.ent_fletch_lvl.bind("<FocusOut>", self.on_levels_changed)
        ToolTip(self.ent_fletch_lvl, "Your in-game Fletching level.")

        tk.Label(sub_top, text="Magic:", fg="#cccccc", bg="#252528").pack(side="left")
        self.ent_mage_lvl = tk.Entry(sub_top, width=4, bg="#1e1e1e", fg="#ffffff", relief="flat")
        self.ent_mage_lvl.insert(0, str(levels.get("Magic", 99)))
        self.ent_mage_lvl.pack(side="left", padx=(2, 10))
        self.ent_mage_lvl.bind("<FocusOut>", self.on_levels_changed)
        ToolTip(self.ent_mage_lvl, "Your in-game Magic level.")

        self.var_only_usable = tk.BooleanVar(value=self.state.config.get("only_usable_recipes", False))
        cb_usable = tk.Checkbutton(sub_top, text="Only Show Usable Recipes", variable=self.var_only_usable, command=self.on_levels_changed,
                                   bg="#252528", fg="#2ecc71", selectcolor="#2d2d30", activebackground="#252528")
        cb_usable.pack(side="left", padx=6)
        ToolTip(cb_usable, "Filter out recipes that exceed your current Crafting, Smithing, Fletching, or Magic levels.")

        # Recipe Search Box
        tk.Label(sub_top, text="🔍", fg="#f39c12", bg="#252528").pack(side="left", padx=(12, 2))
        self.ent_craft_search = tk.Entry(sub_top, width=14, bg="#1e1e1e", fg="#ffffff", insertbackground="#ffffff", relief="flat")
        self.ent_craft_search.pack(side="left", padx=(0, 6))
        self.ent_craft_search.bind("<KeyRelease>", self.on_craft_search_changed)
        self.ent_craft_search.bind("<Escape>", lambda e: self.clear_search())
        ToolTip(self.ent_craft_search, "Filter recipes by name or ingredients (e.g. 'rune', 'diamond', 'ring', 'body', 'bow', 'cosmic').")

        # Category Skill Toggle Buttons Row
        sub_filters = tk.Frame(self.tab_craft, bg="#202023")
        sub_filters.pack(fill="x", padx=6, pady=(0, 6))

        tk.Label(sub_filters, text="Categories:", font=("Segoe UI", 9, "bold"), fg="#3498db", bg="#202023").pack(side="left", padx=(4, 6))

        self.var_filter_craft = tk.BooleanVar(value=self.state.config.get("filter_craft", True))
        self.var_filter_smith = tk.BooleanVar(value=self.state.config.get("filter_smith", True))
        self.var_filter_fletch = tk.BooleanVar(value=self.state.config.get("filter_fletch", True))
        self.var_filter_magic = tk.BooleanVar(value=self.state.config.get("filter_magic", True))

        cb_craft = tk.Checkbutton(sub_filters, text="🔨 Crafting", variable=self.var_filter_craft, command=self.on_skill_filter_changed,
                                  bg="#202023", fg="#e67e22", selectcolor="#2d2d30", activebackground="#202023", activeforeground="#e67e22", font=("Segoe UI", 9, "bold"))
        cb_craft.pack(side="left", padx=4)
        ToolTip(cb_craft, "Toggle Crafting recipes (Gold/Silver Jewellery, D'hide Armour, Battlestaves).")

        cb_smith = tk.Checkbutton(sub_filters, text="⚒️ Smithing", variable=self.var_filter_smith, command=self.on_skill_filter_changed,
                                  bg="#202023", fg="#95a5a6", selectcolor="#2d2d30", activebackground="#202023", activeforeground="#bdc3c7", font=("Segoe UI", 9, "bold"))
        cb_smith.pack(side="left", padx=4)
        ToolTip(cb_smith, "Toggle Smithing recipes (Rune, Adamant, Mithril weapons & armour from bars at an anvil).")

        cb_fletch = tk.Checkbutton(sub_filters, text="🏹 Fletching", variable=self.var_filter_fletch, command=self.on_skill_filter_changed,
                                   bg="#202023", fg="#2ecc71", selectcolor="#2d2d30", activebackground="#202023", activeforeground="#2ecc71", font=("Segoe UI", 9, "bold"))
        cb_fletch.pack(side="left", padx=4)
        ToolTip(cb_fletch, "Toggle Fletching recipes (Bows, Crossbows, and Shields from logs).")

        cb_magic = tk.Checkbutton(sub_filters, text="✨ Magic", variable=self.var_filter_magic, command=self.on_skill_filter_changed,
                                  bg="#202023", fg="#9b59b6", selectcolor="#2d2d30", activebackground="#202023", activeforeground="#9b59b6", font=("Segoe UI", 9, "bold"))
        cb_magic.pack(side="left", padx=4)
        ToolTip(cb_magic, "Toggle Magic Enchanting recipes (Enchanting jewellery with Cosmic runes).")

        btn_all = tk.Button(sub_filters, text="All", command=self.select_all_skill_filters, bg="#2d2d30", fg="#f1f1f1", relief="flat", padx=6, font=("Segoe UI", 8))
        btn_all.pack(side="left", padx=(10, 2))
        btn_none = tk.Button(sub_filters, text="None", command=self.clear_all_skill_filters, bg="#2d2d30", fg="#888888", relief="flat", padx=6, font=("Segoe UI", 8))
        btn_none.pack(side="left", padx=2)

        container = ttk.Frame(self.tab_craft)
        container.pack(fill="both", expand=True)

        # Uses tree and headings for +/- hierarchical recipe expansion!
        cols = ("skill_req", "mat_cost", "alch_val", "profit_ea", "extra_vs_buy", "xp_ea", "profit_hr")
        self.tree_craft = ttk.Treeview(container, columns=cols, show="tree headings", selectmode="browse")

        self.tree_craft.heading("#0", text="Recipe / Ingredient Breakdown", command=lambda: self.toggle_sort_craft("recipe"))
        self.tree_craft.heading("skill_req", text="Skill & Req", command=lambda: self.toggle_sort_craft("skill_req"))
        self.tree_craft.heading("mat_cost", text="Materials Cost", command=lambda: self.toggle_sort_craft("mat_cost"))
        self.tree_craft.heading("alch_val", text="Alch Value", command=lambda: self.toggle_sort_craft("alch_val"))
        self.tree_craft.heading("profit_ea", text="Profit (Craft + Alch) ▼", command=lambda: self.toggle_sort_craft("profit_ea"))
        self.tree_craft.heading("extra_vs_buy", text="Bonus vs Buying Finished", command=lambda: self.toggle_sort_craft("bonus"))
        self.tree_craft.heading("xp_ea", text="XP / Item", command=lambda: self.toggle_sort_craft("xp"))
        self.tree_craft.heading("profit_hr", text="Est Craft+Alch GP/Hr", command=lambda: self.toggle_sort_craft("hr_profit"))

        self.tree_craft.column("#0", width=250, anchor="w")
        self.tree_craft.column("skill_req", width=120, anchor="center")
        self.tree_craft.column("mat_cost", width=110, anchor="e")
        self.tree_craft.column("alch_val", width=100, anchor="e")
        self.tree_craft.column("profit_ea", width=140, anchor="e")
        self.tree_craft.column("extra_vs_buy", width=160, anchor="e")
        self.tree_craft.column("xp_ea", width=90, anchor="center")
        self.tree_craft.column("profit_hr", width=140, anchor="e")

        scrollbar = ttk.Scrollbar(container, orient="vertical", command=self.tree_craft.yview)
        h_scrollbar = ttk.Scrollbar(container, orient="horizontal", command=self.tree_craft.xview)
        self.tree_craft.configure(yscrollcommand=scrollbar.set, xscrollcommand=h_scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        h_scrollbar.pack(side="bottom", fill="x")
        self.tree_craft.pack(side="left", fill="both", expand=True)

        self.tree_craft.bind("<Button-1>", self.on_craft_click)

        craft_col_tooltips = {
            "#0": "Recipe / Ingredient Breakdown:\nItem to create. Click row expander [+] to see required raw materials breakdown.\nClick item name to copy to clipboard.",
            "#1": "Skill & Req:\nSkill and minimum level required to craft this item.",
            "#2": "Materials Cost:\nTotal purchase cost of raw materials needed to craft one item.",
            "#3": "Alch Value:\nHigh Alchemy gold value returned upon casting.",
            "#4": "Profit (Craft + Alch):\nTotal profit earned by buying raw materials, crafting, and alching the finished item.\nClick column header to sort.",
            "#5": "Bonus vs Buying Finished:\nExtra profit gained compared to buying the finished item directly on the GE.\nClick column header to sort.",
            "#6": "XP / Item:\nCrafting or Fletching experience granted per created item.\nClick column header to sort.",
            "#7": "Est Craft+Alch GP/Hr:\nProjected hourly profit accounting for crafting + alching speed.\nClick column header to sort."
        }
        HeadingToolTip(self.tree_craft, craft_col_tooltips)
        RowToolTip(self.tree_craft, self.get_craft_row_tooltip)

    def build_ge_craft_tab(self):
        # 1. Top Controls Bar
        sub_top = tk.Frame(self.tab_ge_craft, bg="#252528")
        sub_top.pack(fill="x", padx=6, pady=(6, 2))

        # Skill Filter Combobox
        tk.Label(sub_top, text="Skill:", font=("Segoe UI", 9, "bold"), fg="#f39c12", bg="#252528").pack(side="left", padx=(4, 2))
        self.var_ge_skill = tk.StringVar(value="All")
        cb_ge_skill = ttk.Combobox(sub_top, textvariable=self.var_ge_skill, values=[
            "All", "🌿 Herblore", "🔨 Crafting", "🏹 Fletching", "⚒️ Smithing", "🍳 Cooking", "✨ Magic"
        ], width=13, state="readonly")
        cb_ge_skill.pack(side="left", padx=(2, 8))
        cb_ge_skill.bind("<<ComboboxSelected>>", lambda e: self.recalculate_ge_craft_table())
        ToolTip(cb_ge_skill, "Filter production recipes by skill.")

        # Sell Strategy Combobox
        tk.Label(sub_top, text="Sell Strategy:", fg="#cccccc", bg="#252528").pack(side="left")
        self.var_ge_sell_strat = tk.StringVar(value="patient (Ask)")
        cb_ge_sell = ttk.Combobox(sub_top, textvariable=self.var_ge_sell_strat, values=["patient (Ask)", "instant (Bid)"], width=13, state="readonly")
        cb_ge_sell.pack(side="left", padx=(2, 8))
        cb_ge_sell.bind("<<ComboboxSelected>>", lambda e: self.recalculate_ge_craft_table())
        ToolTip(cb_ge_sell, "patient (Ask) = List finished products on GE for maximum sale profit.\ninstant (Bid) = Dump immediately into active buy orders on GE.")

        # Target Safety Margin Input
        tk.Label(sub_top, text="Target Margin:", fg="#cccccc", bg="#252528").pack(side="left")
        self.ent_ge_margin = tk.Entry(sub_top, width=6, bg="#1e1e1e", fg="#2ecc71", insertbackground="#ffffff", relief="flat")
        self.ent_ge_margin.insert(0, "0")
        self.ent_ge_margin.pack(side="left", padx=(2, 8))
        self.ent_ge_margin.bind("<KeyRelease>", lambda e: self.recalculate_ge_craft_table())
        ToolTip(self.ent_ge_margin, "Desired profit margin per item in GP.\nAutomatically recalculates the 🎯 Best Buy ceiling prices for raw materials.")

        # Checkbutton: Only Show Usable Recipes
        self.var_ge_only_usable = tk.BooleanVar(value=False)
        cb_ge_usable = tk.Checkbutton(sub_top, text="Only Usable", variable=self.var_ge_only_usable, command=self.recalculate_ge_craft_table,
                                      bg="#252528", fg="#2ecc71", selectcolor="#2d2d30", activebackground="#252528")
        cb_ge_usable.pack(side="left", padx=(2, 8))
        ToolTip(cb_ge_usable, "Only show recipes you have the required level to make.")

        # Min Profit Entry
        tk.Label(sub_top, text="Min Profit:", fg="#cccccc", bg="#252528").pack(side="left")
        self.ent_ge_min_profit = tk.Entry(sub_top, width=5, bg="#1e1e1e", fg="#ffffff", insertbackground="#ffffff", relief="flat")
        self.ent_ge_min_profit.pack(side="left", padx=(2, 8))
        self.ent_ge_min_profit.bind("<KeyRelease>", lambda e: self.recalculate_ge_craft_table())
        ToolTip(self.ent_ge_min_profit, "Minimum profit per craft. Leave blank to show all items (even negative for XP).")

        # Local Search Box
        tk.Label(sub_top, text="🔍", fg="#f39c12", bg="#252528").pack(side="left", padx=(4, 1))
        self.ent_ge_search = tk.Entry(sub_top, width=12, bg="#1e1e1e", fg="#ffffff", insertbackground="#ffffff", relief="flat")
        self.ent_ge_search.pack(side="left", padx=(1, 8))
        self.ent_ge_search.bind("<KeyRelease>", self.on_ge_search_changed)
        self.ent_ge_search.bind("<Escape>", lambda e: self.clear_search())
        ToolTip(self.ent_ge_search, "Filter recipes or ingredients (e.g. 'pickaxe', 'ranarr', 'dart', 'molten glass').")

        # Expand / Collapse All Buttons
        btn_exp = tk.Button(sub_top, text="[+] Expand", command=self.expand_all_ge, bg="#2d2d30", fg="#f1f1f1", relief="flat", padx=6, font=("Segoe UI", 8))
        btn_exp.pack(side="left", padx=2)
        ToolTip(btn_exp, "Expand all recipes to reveal ingredient breakdowns.")

        btn_col = tk.Button(sub_top, text="[-] Collapse", command=self.collapse_all_ge, bg="#2d2d30", fg="#888888", relief="flat", padx=6, font=("Segoe UI", 8))
        btn_col.pack(side="left", padx=2)
        ToolTip(btn_col, "Collapse all recipes back to summary view.")

        # 2. Main Treeview Container
        container = ttk.Frame(self.tab_ge_craft)
        container.pack(fill="both", expand=True)

        cols = ("skill_lvl", "offer_bid", "instant_ask", "sell_price", "profit_ea", "roi", "limit", "batch_profit", "profit_hr", "xp_info", "speed", "volume")
        self.tree_ge = ttk.Treeview(container, columns=cols, show="tree headings", selectmode="browse")

        self.tree_ge.heading("#0", text="Item / Ingredients (▶ Expand)", command=lambda: self.toggle_sort_ge("name"))
        self.tree_ge.heading("skill_lvl", text="Skill & Req", command=lambda: self.toggle_sort_ge("skill"))
        self.tree_ge.heading("offer_bid", text="Target Offer (Bid)", command=lambda: self.toggle_sort_ge("offer_bid"))
        self.tree_ge.heading("instant_ask", text="Instant Buy (Ask)", command=lambda: self.toggle_sort_ge("instant_ask"))
        self.tree_ge.heading("sell_price", text="Target Sell Price", command=lambda: self.toggle_sort_ge("sell_price"))
        self.tree_ge.heading("profit_ea", text="Profit ea ▼", command=lambda: self.toggle_sort_ge("profit_ea"))
        self.tree_ge.heading("roi", text="ROI %", command=lambda: self.toggle_sort_ge("roi"))
        self.tree_ge.heading("limit", text="4h Limit", command=lambda: self.toggle_sort_ge("limit"))
        self.tree_ge.heading("batch_profit", text="4h Batch Profit", command=lambda: self.toggle_sort_ge("batch_profit"))
        self.tree_ge.heading("profit_hr", text="Profit / Hr", command=lambda: self.toggle_sort_ge("profit_hr"))
        self.tree_ge.heading("xp_info", text="XP (ea & /hr)", command=lambda: self.toggle_sort_ge("xp"))
        self.tree_ge.heading("speed", text="Fill Speed", command=lambda: self.toggle_sort_ge("speed"))
        self.tree_ge.heading("volume", text="24h Volume", command=lambda: self.toggle_sort_ge("volume"))

        self.tree_ge.column("#0", width=225, anchor="w")
        self.tree_ge.column("skill_lvl", width=95, anchor="center")
        self.tree_ge.column("offer_bid", width=105, anchor="e")
        self.tree_ge.column("instant_ask", width=105, anchor="e")
        self.tree_ge.column("sell_price", width=120, anchor="e")
        self.tree_ge.column("profit_ea", width=100, anchor="e")
        self.tree_ge.column("roi", width=75, anchor="e")
        self.tree_ge.column("limit", width=75, anchor="center")
        self.tree_ge.column("batch_profit", width=110, anchor="e")
        self.tree_ge.column("profit_hr", width=110, anchor="e")
        self.tree_ge.column("xp_info", width=105, anchor="center")
        self.tree_ge.column("speed", width=110, anchor="center")
        self.tree_ge.column("volume", width=85, anchor="e")

        scrollbar = ttk.Scrollbar(container, orient="vertical", command=self.tree_ge.yview)
        h_scrollbar = ttk.Scrollbar(container, orient="horizontal", command=self.tree_ge.xview)
        self.tree_ge.configure(yscrollcommand=scrollbar.set, xscrollcommand=h_scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        h_scrollbar.pack(side="bottom", fill="x")
        self.tree_ge.pack(side="left", fill="both", expand=True)

        self.tree_ge.tag_configure("profit", foreground="#2ecc71")
        self.tree_ge.tag_configure("loss", foreground="#e74c3c")
        self.tree_ge.tag_configure("child_row", foreground="#cccccc")
        self.tree_ge.tag_configure("locked", foreground="#7f8c8d")

        self.tree_ge.bind("<Button-1>", self.on_ge_tree_click)
        self.tree_ge.bind("<Double-Button-1>", self.on_ge_tree_double_click)
        self.tree_ge.bind("<Button-3>", self.on_ge_context_menu)

        ge_col_tooltips = {
            "#0": "Finished Item / Ingredient Breakdown:\nClick [▶] or double-click row to expand materials and see individual bar/ingredient costs & Best Buy ceilings.",
            "#1": "Skill & Requirement:\nSkill category and minimum level required to craft or process this item.",
            "#2": "Target Offer (Bid):\nFor finished item: Total material cost if buying raw materials patiently on Bid.\nFor child ingredient: Exact buy bid to place on the Grand Exchange. Click cell to copy price!",
            "#3": "Instant Buy (Ask):\nFor finished item: Total material cost if buying materials instantly.\nFor child ingredient: Instant purchase price from active sellers. Click cell to copy!",
            "#4": "Target Sell Price / 🎯 Best Buy:\nFor finished item: The exact price you should list this item for on the Grand Exchange (Net profit already deducts the 1% GE tax).\nFor child ingredient: 🎯 Best Buy ceiling price (maximum to pay for this material on the GE to guarantee profit!). Click to copy!",
            "#5": "Profit ea:\nNet gold profit per craft (Net GE Sale Revenue - Total Material Cost).\nClick header to sort.",
            "#6": "Return on Investment (ROI %):\nProfit margin percentage relative to total material cost.\nClick header to sort.",
            "#7": "4h GE Buy Limit:\nGrand Exchange buy limit of the limiting raw material.",
            "#8": "4h Batch Profit:\nTotal gold profit earned for crafting a full 4-hour limit batch.",
            "#9": "Profit / Hr:\nEstimated hourly gold profit based on standard game action velocity.",
            "#10": "XP (ea & /hr):\nExperience granted per craft, and estimated XP/hr rate.",
            "#11": "Fill Speed:\nMarket transaction speed badge (⚡ Fast, ⏱️ Steady, 🐢 Slow).",
            "#12": "24h Traded Volume:\nTotal 24-hour Grand Exchange transaction volume."
        }
        HeadingToolTip(self.tree_ge, ge_col_tooltips)
        RowToolTip(self.tree_ge, self.get_ge_craft_row_tooltip)

    def build_guide_tab(self):
        container = ttk.Frame(self.tab_guide)
        container.pack(fill="both", expand=True, padx=6, pady=4)

        # 1. Top Controls Bar: Skill Selector Buttons + Level Inputs + Dynamic Target Banner
        guide_ctrl = tk.Frame(container, bg="#252528", relief="solid", borderwidth=1, padx=8, pady=5)
        guide_ctrl.pack(fill="x", pady=(2, 4))

        tk.Label(guide_ctrl, text="Skill:", font=("Segoe UI", 9, "bold"), fg="#f39c12", bg="#252528").pack(side="left", padx=(2, 6))

        self.var_guide_skill = tk.StringVar(value="Smithing")
        self.btn_guide_skills = {}
        skills_info = [
            ("Smithing", "⚒️ Smithing"),
            ("Fletching", "🏹 Fletching"),
            ("Crafting", "🔨 Crafting"),
            ("Magic", "✨ Magic")
        ]
        for sk_key, sk_label in skills_info:
            b = tk.Button(guide_ctrl, text=sk_label, command=lambda k=sk_key: self.set_guide_skill(k),
                          bg="#f39c12" if sk_key == "Smithing" else "#2d2d30",
                          fg="#000000" if sk_key == "Smithing" else "#cccccc",
                          font=("Segoe UI", 9, "bold" if sk_key == "Smithing" else "normal"),
                          relief="flat", padx=8, pady=1, cursor="hand2")
            b.pack(side="left", padx=2)
            self.btn_guide_skills[sk_key] = b
            ToolTip(b, f"Switch Skilling & Level Training Guide to {sk_key}.")

        tk.Label(guide_ctrl, text="|", fg="#444444", bg="#252528").pack(side="left", padx=6)

        # Current Level & Target Level Inputs
        tk.Label(guide_ctrl, text="Current Lvl:", fg="#cccccc", bg="#252528", font=("Segoe UI", 8)).pack(side="left", padx=(2, 2))
        self.ent_guide_cur_lvl = tk.Entry(guide_ctrl, width=4, bg="#1e1e1e", fg="#ffffff", relief="flat", justify="center")
        init_smith = self.state.config.get("player_levels", {}).get("Smithing", 99)
        self.ent_guide_cur_lvl.insert(0, str(init_smith))
        self.ent_guide_cur_lvl.pack(side="left", padx=(0, 6))
        self.ent_guide_cur_lvl.bind("<FocusOut>", lambda e: self.on_guide_levels_changed())
        self.ent_guide_cur_lvl.bind("<Return>", lambda e: self.on_guide_levels_changed())
        ToolTip(self.ent_guide_cur_lvl, "Your current skill level.\nAutomatically updates when logged into RuneLite bridge, or edit manually.")

        tk.Label(guide_ctrl, text="Goal Lvl:", fg="#cccccc", bg="#252528", font=("Segoe UI", 8)).pack(side="left", padx=(2, 2))
        self.ent_guide_target_lvl = tk.Entry(guide_ctrl, width=4, bg="#1e1e1e", fg="#2ecc71", relief="flat", justify="center")
        self.ent_guide_target_lvl.insert(0, str(self.state.config.get("guide_target_level", 99)))
        self.ent_guide_target_lvl.pack(side="left", padx=(0, 6))
        self.ent_guide_target_lvl.bind("<FocusOut>", lambda e: self.on_guide_levels_changed())
        self.ent_guide_target_lvl.bind("<Return>", lambda e: self.on_guide_levels_changed())
        ToolTip(self.ent_guide_target_lvl, "Target level goal (e.g. 50, 70, 85, 99).\nCalculates total remaining XP, actions, and cost required.")

        tk.Label(guide_ctrl, text="|", fg="#444444", bg="#252528").pack(side="left", padx=6)

        # Style & Strategy Radio / Filter
        self.var_guide_style = tk.StringVar(value="all")
        style_radios = [
            ("All", "all", "Show all training methods."),
            ("💰 Profitable", "profit", "Filter to methods that yield net gold profit or minimal loss."),
            ("⚡ Fast XP", "fast", "Filter to high XP/hr progression methods."),
            ("☕ AFK", "afk", "Filter to low-click, relaxed methods.")
        ]
        for slab, sval, stip in style_radios:
            r = tk.Radiobutton(guide_ctrl, text=slab, variable=self.var_guide_style, value=sval,
                               command=self.recalculate_guide_table,
                               bg="#252528", fg="#f1f1f1", selectcolor="#2d2d30",
                               activebackground="#252528", activeforeground="#f39c12",
                               font=("Segoe UI", 8))
            r.pack(side="left", padx=3)
            ToolTip(r, stip)

        init_guide_p2p = (not self.var_f2p.get()) if hasattr(self, "var_f2p") else self.state.config.get("guide_members", True)
        self.var_guide_members = tk.BooleanVar(value=init_guide_p2p)
        self.cb_guide_mem = tk.Checkbutton(guide_ctrl, text="P2P Methods", variable=self.var_guide_members, command=self.on_guide_p2p_toggled,
                                           bg="#252528", fg="#3498db", selectcolor="#2d2d30", activebackground="#252528", font=("Segoe UI", 8))
        self.cb_guide_mem.pack(side="left", padx=3)
        ToolTip(self.cb_guide_mem, "Include Members-only (P2P) skilling brackets and quests.\nUncheck if training on Free-to-play (F2P).")

        # Guide View Selector (Material Chain Tree vs Linear Progression)
        tk.Label(guide_ctrl, text="|", fg="#444444", bg="#252528").pack(side="left", padx=4)
        tk.Label(guide_ctrl, text="View:", fg="#cccccc", bg="#252528", font=("Segoe UI", 8, "bold")).pack(side="left", padx=(2, 2))
        self.var_guide_view = tk.StringVar(value=self.state.config.get("guide_view_mode", "🌲 Material Chain Tree"))
        self.combo_guide_view = ttk.Combobox(
            guide_ctrl,
            textvariable=self.var_guide_view,
            values=["🌲 Material Chain Tree", "📈 Level Progression (1-99)"],
            state="readonly",
            width=21,
            font=("Segoe UI", 8)
        )
        self.combo_guide_view.pack(side="left", padx=(0, 4))
        self.combo_guide_view.bind("<<ComboboxSelected>>", lambda e: self.on_guide_view_changed())
        ToolTip(self.combo_guide_view, "Switch between:\n• 🌲 Material Chain Tree: Hierarchical comparison of smelting raw ores into bars vs smithing each weapon/armor, showing exact profit differences & chain verdicts.\n• 📈 Level Progression (1-99): Standard skilling brackets sorted by level requirement.")

        # Target Profit Margin per item (Breakeven if 0)
        tk.Label(guide_ctrl, text="|", fg="#444444", bg="#252528").pack(side="left", padx=4)
        tk.Label(guide_ctrl, text="Target Margin:", fg="#cccccc", bg="#252528", font=("Segoe UI", 8)).pack(side="left", padx=(2, 2))
        self.var_guide_margin = tk.StringVar(value=str(self.state.config.get("guide_margin", 0)))
        self.ent_guide_margin = tk.Entry(guide_ctrl, textvariable=self.var_guide_margin, width=5, bg="#1e1e1e", fg="#2ecc71",
                                         insertbackground="#ffffff", relief="flat", font=("Segoe UI", 8))
        self.ent_guide_margin.pack(side="left", padx=(0, 4))
        self.ent_guide_margin.bind("<KeyRelease>", lambda e: self.on_guide_margin_changed())
        ToolTip(self.ent_guide_margin, "Target Safety Profit Margin per item (GP):\n• 0 gp = Exact Breakeven buy price (0 gp loss).\n• 50 / 100 / 200 gp = Max buy price needed to guarantee that profit margin.")

        # Sale Price Inspector Toggle Button
        tk.Label(guide_ctrl, text="|", fg="#444444", bg="#252528").pack(side="left", padx=4)
        self.btn_toggle_guide_inspector = tk.Button(guide_ctrl, text="💰 Sale Price Inspector ▴", command=self.toggle_guide_inspector,
                                                    bg="#2d2d30", fg="#f39c12", font=("Segoe UI", 8, "bold"), relief="flat", padx=6, pady=1, cursor="hand2")
        self.btn_toggle_guide_inspector.pack(side="left", padx=2)
        ToolTip(self.btn_toggle_guide_inspector, "Toggle the Manual Sale Price & Profit Inspector to test agreed/custom sale prices against live market material costs.")

        # Right Action Buttons
        btn_guide_batch = tk.Button(guide_ctrl, text="🛒 Add Batch to Cart", command=self.add_guide_batch_to_cart,
                                    bg="#27ae60", fg="#ffffff", font=("Segoe UI", 8, "bold"), relief="flat", padx=8, pady=2, cursor="hand2")
        btn_guide_batch.pack(side="right", padx=3)
        ToolTip(btn_guide_batch, "🛒 Add Training Batch to Cart:\nAdds materials or alchables for the active or selected step into your shopping cart.")

        btn_shop_list = tk.Button(guide_ctrl, text="📋 Shopping List", command=self.copy_guide_shopping_list,
                                  bg="#2980b9", fg="#ffffff", font=("Segoe UI", 8, "bold"), relief="flat", padx=6, pady=2, cursor="hand2")
        btn_shop_list.pack(side="right", padx=3)
        ToolTip(btn_shop_list, "📋 Copy Shopping List:\nCopies formatted materials and cost list for this bracket to clipboard.")

        btn_bank_tag = tk.Button(guide_ctrl, text="🏷️ Bank Tag", command=self.copy_guide_bank_tag,
                                 bg="#8e44ad", fg="#ffffff", font=("Segoe UI", 8, "bold"), relief="flat", padx=6, pady=2, cursor="hand2")
        btn_bank_tag.pack(side="right", padx=3)
        ToolTip(btn_bank_tag, "🏷️ Copy RuneLite Bank Tag:\nCopies a RuneLite Bank Tag Tab string to organize all training materials in your bank.")

        btn_guide_collapse = tk.Button(guide_ctrl, text="➖ Collapse All", command=self.collapse_all_guide,
                                       bg="#34495e", fg="#ffffff", font=("Segoe UI", 8, "bold"), relief="flat", padx=6, pady=2, cursor="hand2")
        btn_guide_collapse.pack(side="right", padx=3)
        ToolTip(btn_guide_collapse, "➖ Collapse All Rows:\nCollapses all skilling brackets back to compact summary rows.")

        btn_guide_expand = tk.Button(guide_ctrl, text="➕ Expand All", command=self.expand_all_guide,
                                     bg="#34495e", fg="#ffffff", font=("Segoe UI", 8, "bold"), relief="flat", padx=6, pady=2, cursor="hand2")
        btn_guide_expand.pack(side="right", padx=3)
        ToolTip(btn_guide_expand, "➕ Expand All Rows:\nExpands all skilling brackets to reveal individual raw ingredients and buy ceilings underneath.")

        # 2. Dynamic Progress & XP Summary Banner
        self.banner_guide_xp = tk.Frame(container, bg="#202023", relief="solid", borderwidth=1, padx=8, pady=5)
        self.banner_guide_xp.pack(fill="x", pady=(0, 4))

        top_prog_row = tk.Frame(self.banner_guide_xp, bg="#202023")
        top_prog_row.pack(fill="x")
        self.lbl_guide_xp_summary = tk.Label(top_prog_row, text="🎯 Calculating progression...", font=("Segoe UI", 9, "bold"), fg="#e0e0e0", bg="#202023")
        self.lbl_guide_xp_summary.pack(side="left")

        self.lbl_guide_eta_badge = tk.Label(top_prog_row, text="⏱️ Est. Next Lvl: --", font=("Segoe UI", 9, "bold"), fg="#00e5ff", bg="#202023")
        self.lbl_guide_eta_badge.pack(side="right")

        # Visual progress bar canvas
        self.canvas_guide_prog = tk.Canvas(self.banner_guide_xp, height=14, bg="#151518", highlightthickness=1, highlightbackground="#35353a")
        self.canvas_guide_prog.pack(fill="x", pady=(3, 3))
        self.canvas_guide_prog.bind("<Configure>", lambda e: self._draw_guide_progress_bar())

        bot_prog_row = tk.Frame(self.banner_guide_xp, bg="#202023")
        bot_prog_row.pack(fill="x")
        self.lbl_guide_pace_summary = tk.Label(bot_prog_row, text="⚡ Pace: Calculating...", font=("Segoe UI", 8), fg="#aaaaaa", bg="#202023")
        self.lbl_guide_pace_summary.pack(side="left")

        self.lbl_guide_trips_summary = tk.Label(bot_prog_row, text="🎒 Trips: --", font=("Segoe UI", 8), fg="#cccccc", bg="#202023")
        self.lbl_guide_trips_summary.pack(side="right")

        # 2b. Manual Sale Price & Profit Inspector Card
        self.frame_guide_inspector = tk.Frame(container, bg="#1a1a1d", relief="solid", borderwidth=1, padx=8, pady=5)
        self.frame_guide_inspector.pack(fill="x", pady=(0, 4))
        self.guide_inspector_visible = True

        insp_head = tk.Frame(self.frame_guide_inspector, bg="#1a1a1d")
        insp_head.pack(fill="x", pady=(0, 3))
        tk.Label(insp_head, text="💰 Manual Sale Price & Profit Inspector", font=("Segoe UI", 9, "bold"), fg="#f39c12", bg="#1a1a1d").pack(side="left")
        tk.Label(insp_head, text="Type your agreed sale price per item to test profitability with live market material costs!",
                 font=("Segoe UI", 8, "italic"), fg="#888888", bg="#1a1a1d").pack(side="left", padx=(8, 0))
        btn_close_insp = tk.Button(insp_head, text="✕ Hide", command=self.toggle_guide_inspector,
                                   bg="#1a1a1d", fg="#888888", activeforeground="#ffffff", relief="flat", padx=4, font=("Segoe UI", 7), cursor="hand2")
        btn_close_insp.pack(side="right")
        ToolTip(btn_close_insp, "Hide this Inspector card (click '💰 Sale Price Inspector ▾' in top bar to reopen).")

        insp_body = tk.Frame(self.frame_guide_inspector, bg="#1a1a1d")
        insp_body.pack(fill="x")

        # Left Column: Inputs
        insp_left = tk.Frame(insp_body, bg="#1a1a1d")
        insp_left.pack(side="left", fill="y", padx=(0, 10))

        # Item Selector row
        r_item = tk.Frame(insp_left, bg="#1a1a1d")
        r_item.pack(fill="x", pady=1)
        tk.Label(r_item, text="Item:", width=7, anchor="w", fg="#cccccc", bg="#1a1a1d", font=("Segoe UI", 8)).pack(side="left")
        self.var_insp_item = tk.StringVar(value="Air battlestaff")
        insp_item_list = self.get_all_inspector_item_names()
        self.cb_insp_item = ttk.Combobox(r_item, textvariable=self.var_insp_item, values=insp_item_list, width=17, state="readonly")
        self.cb_insp_item.pack(side="left")
        self.cb_insp_item.bind("<<ComboboxSelected>>", self.on_insp_item_selected)

        # Selling Price row
        r_price = tk.Frame(insp_left, bg="#1a1a1d")
        r_price.pack(fill="x", pady=1)
        tk.Label(r_price, text="Sell Ea:", width=7, anchor="w", fg="#cccccc", bg="#1a1a1d", font=("Segoe UI", 8)).pack(side="left")
        self.ent_insp_price = tk.Entry(r_price, width=8, bg="#252528", fg="#f1c40f", insertbackground="#ffffff", relief="flat")
        self.ent_insp_price.insert(0, "9050")
        self.ent_insp_price.pack(side="left")
        self.ent_insp_price.bind("<KeyRelease>", self.calculate_guide_inspector)
        tk.Label(r_price, text="gp", fg="#888888", bg="#1a1a1d", font=("Segoe UI", 8)).pack(side="left", padx=2)

        # Qty row
        r_qty = tk.Frame(insp_left, bg="#1a1a1d")
        r_qty.pack(fill="x", pady=1)
        tk.Label(r_qty, text="Qty:", width=7, anchor="w", fg="#cccccc", bg="#1a1a1d", font=("Segoe UI", 8)).pack(side="left")
        self.ent_insp_qty = tk.Entry(r_qty, width=7, bg="#252528", fg="#2ecc71", insertbackground="#ffffff", relief="flat")
        self.ent_insp_qty.insert(0, "1000")
        self.ent_insp_qty.pack(side="left", padx=(0, 2))
        self.ent_insp_qty.bind("<KeyRelease>", self.calculate_guide_inspector)

        for q_txt, q_val in (("100", 100), ("500", 500), ("1k", 1000), ("Max Cash", -1)):
            btn_q = tk.Button(r_qty, text=q_txt, command=lambda v=q_val: self.set_insp_qty(v),
                              bg="#2d2d30", fg="#3498db" if q_txt == "Max Cash" else "#cccccc", font=("Segoe UI", 7, "bold"), relief="flat", padx=3, pady=1, cursor="hand2")
            btn_q.pack(side="left", padx=1)

        # Center Column: Comparisons
        insp_center = tk.Frame(insp_body, bg="#1a1a1d")
        insp_center.pack(side="left", fill="both", expand=True, padx=(0, 10))

        self.lbl_insp_materials = tk.Label(insp_center, text="Recipe: 1x Battlestaff + 1x Air orb", font=("Segoe UI", 8), fg="#cccccc", bg="#1a1a1d", anchor="w")
        self.lbl_insp_materials.pack(fill="x", pady=1)

        c_grid = tk.Frame(insp_center, bg="#1a1a1d")
        c_grid.pack(fill="x")

        self.lbl_insp_mat_cost = tk.Label(c_grid, text="Live Mat Cost: -- gp", font=("Segoe UI", 8, "bold"), fg="#e74c3c", bg="#1a1a1d", anchor="w")
        self.lbl_insp_mat_cost.grid(row=0, column=0, sticky="w", padx=(0, 10), pady=1)

        self.lbl_insp_ge_sell = tk.Label(c_grid, text="GE Instant Net: -- gp", font=("Segoe UI", 8), fg="#3498db", bg="#1a1a1d", anchor="w")
        self.lbl_insp_ge_sell.grid(row=0, column=1, sticky="w", padx=(0, 10), pady=1)

        self.lbl_insp_alch_net = tk.Label(c_grid, text="High Alch Net: -- gp", font=("Segoe UI", 8), fg="#9b59b6", bg="#1a1a1d", anchor="w")
        self.lbl_insp_alch_net.grid(row=1, column=0, sticky="w", padx=(0, 10), pady=1)

        self.lbl_insp_w308 = tk.Label(c_grid, text="Bulk Benchmark: -- gp", font=("Segoe UI", 8), fg="#f39c12", bg="#1a1a1d", anchor="w")
        self.lbl_insp_w308.grid(row=1, column=1, sticky="w", padx=(0, 10), pady=1)

        self.lbl_insp_comparison = tk.Label(insp_center, text="Comparing your sell price with current market...", font=("Segoe UI", 8, "italic"), fg="#aaaaaa", bg="#1a1a1d", anchor="w")
        self.lbl_insp_comparison.pack(fill="x", pady=(2, 0))

        # Right Column: Results & Actions
        insp_right = tk.Frame(insp_body, bg="#1a1a1d")
        insp_right.pack(side="right", fill="y")

        r_grid = tk.Frame(insp_right, bg="#1a1a1d")
        r_grid.pack(fill="x")

        self.lbl_insp_profit_ea = tk.Label(r_grid, text="Profit / Ea: -- gp", font=("Segoe UI", 9, "bold"), fg="#2ecc71", bg="#1a1a1d")
        self.lbl_insp_profit_ea.grid(row=0, column=0, sticky="w", padx=(0, 8), pady=1)

        self.lbl_insp_batch_profit = tk.Label(r_grid, text="Batch Profit: -- gp", font=("Segoe UI", 9, "bold"), fg="#2ecc71", bg="#1a1a1d")
        self.lbl_insp_batch_profit.grid(row=0, column=1, sticky="w", padx=(0, 8), pady=1)

        self.lbl_insp_gpxp = tk.Label(r_grid, text="GP / XP: --", font=("Segoe UI", 8, "bold"), fg="#3498db", bg="#1a1a1d")
        self.lbl_insp_gpxp.grid(row=1, column=0, sticky="w", padx=(0, 8), pady=1)

        self.lbl_insp_breakeven = tk.Label(r_grid, text="Breakeven Mat: ≤ -- gp", font=("Segoe UI", 8), fg="#cccccc", bg="#1a1a1d")
        self.lbl_insp_breakeven.grid(row=1, column=1, sticky="w", padx=(0, 8), pady=1)

        insp_actions = tk.Frame(insp_right, bg="#1a1a1d")
        insp_actions.pack(fill="x", pady=(3, 0))

        btn_insp_cart = tk.Button(insp_actions, text="🛒 Add Mats to Cart", command=self.add_insp_materials_to_cart,
                                  bg="#27ae60", fg="#ffffff", font=("Segoe UI", 7, "bold"), relief="flat", padx=5, pady=1, cursor="hand2")
        btn_insp_cart.pack(side="left", padx=1)
        ToolTip(btn_insp_cart, "Add all raw materials required to produce this batch into your Shopping Cart.")

        btn_insp_w308 = tk.Button(insp_actions, text="🤝 Load in W308 Hub", command=self.load_insp_into_w308,
                                  bg="#f39c12", fg="#000000", font=("Segoe UI", 7, "bold"), relief="flat", padx=5, pady=1, cursor="hand2")
        btn_insp_w308.pack(side="left", padx=1)
        ToolTip(btn_insp_w308, "Switch to the World 308 Bulk Trading Hub and load this item and price into the Trade Screen Validator.")

        btn_insp_ad = tk.Button(insp_actions, text="📢 Copy Sell Ad", command=self.copy_insp_trade_ad,
                                bg="#2d2d30", fg="#3498db", font=("Segoe UI", 7, "bold"), relief="flat", padx=5, pady=1, cursor="hand2")
        btn_insp_ad.pack(side="left", padx=1)
        ToolTip(btn_insp_ad, "Copy ready-to-paste chat ad for selling this batch (e.g. 'Selling 1,000 Air battlestaff 9.1k ea Bulk - Trade Me').")

        # 3. Early Quest Skips & Shortcuts Card
        self.frame_guide_quests = tk.Frame(container, bg="#202023", relief="solid", borderwidth=1, padx=8, pady=4)
        self.frame_guide_quests.pack(fill="x", pady=(0, 4))

        q_top = tk.Frame(self.frame_guide_quests, bg="#202023")
        q_top.pack(fill="x")
        tk.Label(q_top, text="📜 Essential Early Quest Skips & Shortcuts (Click 🌐 to view Wiki Guide):",
                 font=("Segoe UI", 8, "bold"), fg="#f1c40f", bg="#202023").pack(side="left")

        self.frame_quest_inner = tk.Frame(self.frame_guide_quests, bg="#202023")
        self.frame_quest_inner.pack(fill="x", pady=(3, 0))

        # 4. Skilling Progression Treeview Table
        tree_frame = ttk.Frame(container)
        tree_frame.pack(fill="both", expand=True)

        cols = ("status", "level_range", "materials", "tot_mats", "needed", "max_buy", "xp_ea", "gp_xp", "bracket_cost", "action_rec", "xp_rate", "time_est", "verdict")
        self.tree_guide = ttk.Treeview(tree_frame, columns=cols, show="tree headings", selectmode="browse")

        self.tree_guide.heading("#0", text="Training Method (▶ Expand)", command=lambda: self.toggle_sort_guide("name"))
        self.tree_guide.heading("status", text="Status", command=lambda: self.toggle_sort_guide("status"))
        self.tree_guide.heading("level_range", text="Level Range", command=lambda: self.toggle_sort_guide("level_range"))
        self.tree_guide.heading("materials", text="Materials (ea)", command=lambda: self.toggle_sort_guide("materials"))
        self.tree_guide.heading("tot_mats", text="Total Mats Needed", command=lambda: self.toggle_sort_guide("tot_mats"))
        self.tree_guide.heading("needed", text="Units Needed", command=lambda: self.toggle_sort_guide("needed"))
        self.tree_guide.heading("max_buy", text="🎯 Max Mat Buy", command=lambda: self.toggle_sort_guide("max_buy"))
        self.tree_guide.heading("xp_ea", text="XP / Act", command=lambda: self.toggle_sort_guide("xp_ea"))
        self.tree_guide.heading("gp_xp", text="Live GP/XP", command=lambda: self.toggle_sort_guide("gp_xp"))
        self.tree_guide.heading("bracket_cost", text="Net Profit / Loss", command=lambda: self.toggle_sort_guide("bracket_cost"))
        self.tree_guide.heading("action_rec", text="Best Disposal", command=lambda: self.toggle_sort_guide("action_rec"))
        self.tree_guide.heading("xp_rate", text="XP / Hour", command=lambda: self.toggle_sort_guide("xp_rate"))
        self.tree_guide.heading("time_est", text="Est. Time", command=lambda: self.toggle_sort_guide("time_est"))
        self.tree_guide.heading("verdict", text="Strategy Tips / Verdict", command=lambda: self.toggle_sort_guide("verdict"))

        self.tree_guide.column("#0", width=220, anchor="w")
        self.tree_guide.column("status", width=110, anchor="center")
        self.tree_guide.column("level_range", width=75, anchor="center")
        self.tree_guide.column("materials", width=130, anchor="w")
        self.tree_guide.column("tot_mats", width=145, anchor="w")
        self.tree_guide.column("needed", width=85, anchor="e")
        self.tree_guide.column("max_buy", width=110, anchor="e")
        self.tree_guide.column("xp_ea", width=65, anchor="e")
        self.tree_guide.column("gp_xp", width=85, anchor="e")
        self.tree_guide.column("bracket_cost", width=100, anchor="e")
        self.tree_guide.column("action_rec", width=100, anchor="center")
        self.tree_guide.column("xp_rate", width=80, anchor="e")
        self.tree_guide.column("time_est", width=70, anchor="center")
        self.tree_guide.column("verdict", width=260, anchor="w")

        v_scroll = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree_guide.yview)
        h_scroll = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree_guide.xview)
        self.tree_guide.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)

        v_scroll.pack(side="right", fill="y")
        h_scroll.pack(side="bottom", fill="x")
        self.tree_guide.pack(side="left", fill="both", expand=True)

        self.tree_guide.tag_configure("current", foreground="#f1c40f", font=("Segoe UI", 9, "bold"))
        self.tree_guide.tag_configure("completed", foreground="#7f8c8d")
        self.tree_guide.tag_configure("locked", foreground="#666666")
        self.tree_guide.tag_configure("profit", foreground="#2ecc71")
        self.tree_guide.tag_configure("mild_loss", foreground="#f39c12")
        self.tree_guide.tag_configure("loss", foreground="#e74c3c")
        self.tree_guide.tag_configure("quest", foreground="#3498db", font=("Segoe UI", 9, "bold"))
        self.tree_guide.tag_configure("child_row", foreground="#a0a0a5")
        self.tree_guide.tag_configure("tier_root", foreground="#f39c12", font=("Segoe UI", 9, "bold"))
        self.tree_guide.tag_configure("baseline", foreground="#3498db")

        self.tree_guide.bind("<Button-1>", self.on_guide_click)
        self.tree_guide.bind("<Double-1>", self.on_guide_double_click)
        self.tree_guide.bind("<Button-3>", self.on_guide_right_click)

        guide_col_tooltips = {
            "#0": "Training Method / Breakdown:\nClick ▶ to expand into individual raw ingredients with individual buy ceilings.",
            "#1": "Status:\n📍 YOU ARE HERE (Current training step for your level)\n✅ Completed (Already passed this level)\n🔒 Locked (Requires higher level).",
            "#2": "Level Range:\nRecommended level bracket for this skilling method.",
            "#3": "Materials Needed (ea):\nRaw ingredients required per single action.",
            "#4": "Total Mats Needed:\nTotal raw materials / bars needed to complete this bracket (or remaining for your level goal).",
            "#5": "Units Needed:\nNumber of actions required to complete this bracket (or reach your target goal).",
            "#6": "🎯 Max Mat Buy:\nMaximum GE buy price to pay for raw materials to break even (or meet target margin).",
            "#7": "XP / Act:\nExperience granted per single crafted/smithed item or cast (or GE Bid Offer on ingredient rows).",
            "#8": "Live GP/XP:\nNet gold profit/cost per experience point (or Instant Buy Ask on ingredient rows).",
            "#9": "Net Profit / Loss:\nTotal projected gold profit (+) or loss (-) to complete all needed units in this bracket.",
            "#10": "Best Disposal:\nOptimal way to dispose of finished products: 🪄 High Alch vs 🏪 Sell on GE vs 📜 Quest Turn-in.",
            "#11": "XP / Hour:\nRealistic hourly experience rate attainable with this method.",
            "#12": "Est. Time:\nProjected grind time to finish this bracket at standard XP/hr rates.",
            "#13": "Strategy Tips / Verdict:\nPro tips, quest skips, and strategy breakdown."
        }
        HeadingToolTip(self.tree_guide, guide_col_tooltips)
        RowToolTip(self.tree_guide, self.get_guide_row_tooltip)

        self.guide_rows = []
        self.guide_sort_col = "level_range"
        self.guide_sort_asc = True
        self.update_guide_quests_card("Smithing")

    def on_guide_view_changed(self):
        self.state.config["guide_view_mode"] = self.var_guide_view.get()
        self.save_preferences()
        self.recalculate_guide_table()

    def expand_all_guide(self):
        def _exp_rec(parent=""):
            for iid in self.tree_guide.get_children(parent):
                self.tree_guide.item(iid, open=True)
                _exp_rec(iid)
        _exp_rec("")

    def collapse_all_guide(self):
        def _col_rec(parent=""):
            for iid in self.tree_guide.get_children(parent):
                self.tree_guide.item(iid, open=False)
                _col_rec(iid)
        _col_rec("")


    def set_guide_skill(self, skill_name):
        self.var_guide_skill.set(skill_name)
        for sk_key, b in self.btn_guide_skills.items():
            if sk_key == skill_name:
                b.config(bg="#f39c12", fg="#000000", font=("Segoe UI", 9, "bold"))
            else:
                b.config(bg="#2d2d30", fg="#cccccc", font=("Segoe UI", 9))

        curr_char = self.var_account.get() if hasattr(self, "var_account") else "All Accounts"
        player_levels = self.state.config.get("player_levels", {})
        if curr_char != "All Accounts" and curr_char in self.state.accounts:
            char_lvls = self.state.accounts[curr_char].get("levels", {})
            lvl = char_lvls.get(skill_name, player_levels.get(skill_name, 1))
        elif self.state.accounts:
            latest_acc = max(self.state.accounts.values(), key=lambda a: a.get("last_seen", 0))
            char_lvls = latest_acc.get("levels", {})
            lvl = char_lvls.get(skill_name, player_levels.get(skill_name, 1))
        else:
            lvl = player_levels.get(skill_name, 1)

        self.ent_guide_cur_lvl.delete(0, tk.END)
        self.ent_guide_cur_lvl.insert(0, str(lvl))

        self.update_guide_quests_card(skill_name)
        self.recalculate_guide_table()

    def is_guide_p2p_allowed(self):
        # Strict F2P mode: if top bar F2P is checked and Members is not checked, or guide P2P is unchecked
        if hasattr(self, "var_f2p") and self.var_f2p.get() and hasattr(self, "var_members") and not self.var_members.get():
            return False
        if hasattr(self, "var_guide_members"):
            return self.var_guide_members.get()
        return True

    def on_guide_p2p_toggled(self):
        p2p_on = self.var_guide_members.get()
        if hasattr(self, "var_members") and hasattr(self, "var_f2p"):
            self.var_members.set(p2p_on)
            self.var_f2p.set(not p2p_on)
            self.state.config["members"] = p2p_on
            self.state.config["f2p"] = not p2p_on
        self.state.config["guide_members"] = p2p_on
        self.save_preferences()
        self.update_guide_quests_card(self.var_guide_skill.get())
        self.recalculate_all()

    def update_guide_quests_card(self, skill_name):
        for w in self.frame_quest_inner.winfo_children():
            w.destroy()

        sdata = SKILLING_GUIDES.get(skill_name, {})
        quests = sdata.get("quests", [])
        p2p_allowed = self.is_guide_p2p_allowed()

        filtered_quests = [q for q in quests if p2p_allowed or not q.get("members", True)]

        if not filtered_quests:
            msg = "ℹ️ No F2P quest skips for this skill (All quest skips require Members)." if not p2p_allowed else "No early quest skips registered for this skill."
            tk.Label(self.frame_quest_inner, text=msg, fg="#888888", bg="#202023", font=("Segoe UI", 8)).pack(side="left")
            return

        for q in filtered_quests:
            q_btn = tk.Button(self.frame_quest_inner, text=f"📜 {q['name']} ({q['skip'].split('!')[0]}) 🌐",
                              command=lambda slug=q['wiki_slug']: webbrowser.open(f"https://oldschool.runescape.wiki/w/{slug}"),
                              bg="#2d2d30", fg="#3498db", activebackground="#3498db", activeforeground="#ffffff",
                              relief="flat", padx=6, pady=1, font=("Segoe UI", 8, "bold"), cursor="hand2")
            q_btn.pack(side="left", padx=3)
            mem_tag = " (Members)" if q.get("members", True) else " (F2P)"
            q_tip = (
                f"Quest: {q['name']}{mem_tag}\n"
                f"XP Reward: {q['xp']:,} XP\n"
                f"Benefit: {q['skip']}\n"
                f"Requirements: {q['reqs']}\n\n"
                f"Tip: {q['tip']}\n"
                "Click to open the full OSRS Wiki Guide in your browser."
            )
            ToolTip(q_btn, q_tip)

    def on_guide_levels_changed(self):
        try:
            cur_lvl = int(self.ent_guide_cur_lvl.get().strip())
            cur_lvl = max(1, min(99, cur_lvl))
        except ValueError:
            cur_lvl = 1
            self.ent_guide_cur_lvl.delete(0, tk.END)
            self.ent_guide_cur_lvl.insert(0, "1")

        try:
            target_lvl = int(self.ent_guide_target_lvl.get().strip())
            target_lvl = max(cur_lvl, min(99, target_lvl))
        except ValueError:
            target_lvl = 99
            self.ent_guide_target_lvl.delete(0, tk.END)
            self.ent_guide_target_lvl.insert(0, "99")

        active_skill = self.var_guide_skill.get()
        self.state.config.setdefault("player_levels", {})[active_skill] = cur_lvl
        self.state.config["guide_target_level"] = target_lvl
        self.state.save_config()

        self.recalculate_guide_table()

    def on_guide_margin_changed(self):
        try:
            val = parse_cash_input(self.var_guide_margin.get())
            self.state.config["guide_margin"] = max(0, val)
            self.save_preferences()
        except Exception:
            pass
        self.recalculate_guide_table()

    def _render_smithing_material_tree(self, cur_lvl, target_lvl, cur_xp, target_xp, rem_xp, mem_ok, style_filter, search_query, strat, nat_price, prev_open, live_rate=0, detected_activity=""):
        coal_id = 453
        coal_price = self.api.get_price(coal_id, strat) or 140
        basis = "5m" if hasattr(self, "var_price_basis") and "5m" in self.var_price_basis.get() else self.state.config.get("price_basis", "5m")
        best_active_item = None

        target_margin = 0
        if hasattr(self, "ent_guide_margin"):
            try:
                target_margin = max(0, parse_cash_input(self.ent_guide_margin.get()))
            except Exception:
                target_margin = 0

        # Update XP summary banner with tree explanation
        if hasattr(self, "lbl_guide_xp_summary"):
            bf_tag = "Blast Furnace (Halved Coal)" if mem_ok else "Standard Furnace (Full Coal)"
            self.lbl_guide_xp_summary.config(text=f"🌲 Smithing Material Family Tree ({bf_tag})  |  Compare Smelting vs Anvil Products  |  🟢 ⭐ Beats Bar  |  🟡 ⚡ Subsidized XP  |  🔴 ⛔ Sell Bar on GE")

        # Determine active sort column and direction
        sort_col = getattr(self, "guide_sort_col", "level_range")
        sort_asc = getattr(self, "guide_sort_asc", True)

        is_first_init = not getattr(self, "_guide_tree_initialized", False)
        self._guide_tree_initialized = True

        for tier in SMITHING_MATERIAL_CHAINS:
            tier_name = tier["tier"]
            bar_name = tier["bar_name"]
            bar_id = tier["bar_id"]
            ore_name = tier["ore_name"]
            ore_id = tier["ore_id"]
            second_name = tier.get("second_name", "")
            second_id = tier.get("second_id", 0)
            smelt_lvl = tier["smelt_lvl"]
            smelt_xp = tier["smelt_xp"]
            coal_qty = tier.get("coal_qty_bf", 0) if mem_ok else tier.get("coal_qty_reg", 0)

            # Check if tier itself is members-only
            if tier.get("members", False) and not mem_ok:
                continue

            # Pricing for ores & bar
            ore_p = self.api.get_price(ore_id, strat)
            second_p = self.api.get_price(second_id, strat) if (second_id > 0 and tier_name == "Bronze") else 0
            if tier_name == "Bronze":
                ore_cost_per_bar = ore_p + second_p
                ore_summary_str = f"1x {ore_name} + 1x {second_name}"
            elif coal_qty > 0:
                ore_cost_per_bar = ore_p + (coal_qty * coal_price)
                ore_summary_str = f"1x {ore_name} + {coal_qty}x Coal"
            else:
                ore_cost_per_bar = ore_p
                ore_summary_str = f"1x {ore_name}"

            bar_buy = self.api.get_price(bar_id, strat)
            bar_sell = self.api.get_price(bar_id, "instasell")
            bar_net = math.floor(bar_sell * 0.99)
            bar_profit = bar_net - ore_cost_per_bar
            smelt_gp_xp = (bar_profit / smelt_xp) if smelt_xp > 0 else 0.0

            # Raw ore breakeven buy price
            other_fuel = (coal_qty * coal_price) if tier_name != "Bronze" else second_p
            max_ore_buy = max(0, bar_net - other_fuel - target_margin)

            # Evaluate child craftable items first
            tier_items = []
            for item in tier.get("items", []):
                # Filter members
                if item.get("members", False) and not mem_ok:
                    continue

                bars_needed = item["bars"]
                item_ore_cost = bars_needed * ore_cost_per_bar
                out_qty = item.get("qty", 1)
                alch_val = self.api.mapping.get(str(item["id"]), {}).get("highalch", 0)
                ge_sell = self.api.get_price(item["id"], "instasell")

                eff_alch = ((alch_val * out_qty) - nat_price) if alch_val > 0 else -99999999
                eff_ge = (math.floor(ge_sell * 0.99) * out_qty) if ge_sell > 0 else -99999999
                w308_staple = next((it_s for it_s in W308_STAPLES if it_s["id"] == item["id"] or it_s["name"].lower() == item["name"].lower()), None)
                eff_w308 = (w308_staple["w308_buy"] * out_qty) if w308_staple else -99999999
                best_rev = max(eff_alch, eff_ge, eff_w308)
                if best_rev < 0:
                    best_rev = 0

                chain_profit = best_rev - item_ore_cost
                total_bar_net = bars_needed * bar_net
                diff_vs_bar = best_rev - total_bar_net

                smith_xp = item["xp"]
                chain_gp_xp = (chain_profit / smith_xp) if smith_xp > 0 else 0.0

                # Classification & Verdict
                if diff_vs_bar >= 0:
                    tag = "profit"
                    badge = f"⭐ Beats Bar (+{diff_vs_bar:,} gp vs GE)"
                    verdict_msg = f"Crafting beats selling bars! Yields +{diff_vs_bar:,} gp MORE than selling bars on GE, plus {smith_xp:.1f} Smithing XP!"
                elif chain_profit > 0:
                    cost_per_anvil_xp = abs(diff_vs_bar) / smith_xp if smith_xp > 0 else 0.0
                    tag = "mild_loss"
                    badge = f"⚡ Subsidized XP ({cost_per_anvil_xp:.1f} gp/xp)"
                    verdict_msg = f"Net cash profit: +{chain_profit:,} gp from ores. Trades {abs(diff_vs_bar):,} gp bar profit to buy {smith_xp:.1f} anvil XP at only {cost_per_anvil_xp:.1f} gp/xp!"
                else:
                    tag = "loss"
                    badge = f"⛔ Sell Bar on GE ({diff_vs_bar:,} gp vs bar)"
                    verdict_msg = f"Net cash loss: -{abs(chain_profit):,} gp from raw ores. Better to sell raw bars on GE (+{abs(diff_vs_bar):,} gp better)!"

                # Filter by style
                if style_filter == "profit" and chain_profit <= 0 and diff_vs_bar < 0:
                    continue
                if style_filter == "fast" and item["name"] not in ("Dart tip", "Knife", "Platebody", "Arrowtips") and "platebody" not in item["name"].lower() and "dart" not in item["name"].lower():
                    continue
                if style_filter == "afk" and "cannonball" not in item["name"].lower() and "dart" not in item["name"].lower() and "arrow" not in item["name"].lower():
                    continue

                # Filter by search
                if search_query:
                    match_name = search_query in item["name"].lower()
                    match_tier = search_query in tier_name.lower()
                    if not (match_name or match_tier):
                        continue

                # Anvil XP Rate
                item_lower = item["name"].lower()
                if "cannonball" in item_lower:
                    xp_rate = 25600
                elif "dart" in item_lower:
                    xp_rate = 120000
                elif "knife" in item_lower:
                    xp_rate = 105000
                elif "arrow" in item_lower:
                    xp_rate = 110000
                elif "bolts" in item_lower:
                    xp_rate = 95000
                elif "platebody" in item_lower:
                    xp_rate = 220000
                elif any(k in item_lower for k in ("platelegs", "plateskirt", "chainbody", "2h")):
                    xp_rate = 150000
                elif any(k in item_lower for k in ("scimitar", "sq shield", "claws", "warhammer", "battleaxe")):
                    xp_rate = 110000
                else:
                    xp_rate = 75000

                # Max buy ceiling for the bar
                be_bar = math.floor(best_rev / bars_needed) if bars_needed > 0 else 0
                tb_bar = math.floor((best_rev - target_margin) / bars_needed) if bars_needed > 0 else 0

                item_obj = {
                    "tier_name": tier_name,
                    "bar_name": bar_name,
                    "bar_id": bar_id,
                    "ore_name": ore_name,
                    "ore_id": ore_id,
                    "second_name": second_name,
                    "second_id": second_id,
                    "coal_qty": coal_qty,
                    "coal_price": coal_price,
                    "ore_cost_per_bar": ore_cost_per_bar,
                    "item": item,
                    "bars_needed": bars_needed,
                    "item_ore_cost": item_ore_cost,
                    "out_qty": out_qty,
                    "alch_val": alch_val,
                    "ge_sell": ge_sell,
                    "eff_alch": eff_alch,
                    "eff_ge": eff_ge,
                    "best_rev": best_rev,
                    "action_rec": "🤝 Bulk Trade" if (eff_w308 >= eff_ge and eff_w308 >= eff_alch and eff_w308 > 0) else ("🪄 High Alch" if (eff_alch >= eff_ge and eff_alch > 0) else "🏪 Sell on GE"),
                    "chain_profit": chain_profit,
                    "diff_vs_bar": diff_vs_bar,
                    "smith_xp": smith_xp,
                    "chain_gp_xp": chain_gp_xp,
                    "tag": tag,
                    "badge": badge,
                    "verdict_msg": verdict_msg,
                    "xp_rate": xp_rate,
                    "be_bar": be_bar,
                    "tb_bar": tb_bar,
                    "bar_buy": bar_buy,
                    "req_lvl": item["level"]
                }
                tier_items.append(item_obj)

            # If searching or filtering and no items match, skip tier unless search matches tier name directly
            if search_query and not tier_items and search_query not in tier_name.lower():
                continue
            if style_filter != "all" and not tier_items:
                continue

            # Sort tier items according to user sort choice
            if sort_col == "level_range":
                tier_items.sort(key=lambda x: x["req_lvl"], reverse=not sort_asc)
            elif sort_col == "bracket_cost":
                tier_items.sort(key=lambda x: x["chain_profit"], reverse=not sort_asc)
            elif sort_col == "gp_xp":
                tier_items.sort(key=lambda x: x["chain_gp_xp"], reverse=not sort_asc)
            elif sort_col == "xp_ea":
                tier_items.sort(key=lambda x: x["smith_xp"], reverse=not sort_asc)
            elif sort_col == "max_buy":
                tier_items.sort(key=lambda x: x["tb_bar"], reverse=not sort_asc)
            elif sort_col == "xp_rate":
                tier_items.sort(key=lambda x: x["xp_rate"], reverse=not sort_asc)
            elif sort_col == "needed":
                tier_items.sort(key=lambda x: x["bars_needed"], reverse=not sort_asc)
            elif sort_col == "name":
                tier_items.sort(key=lambda x: x["item"]["name"], reverse=not sort_asc)
            else:
                tier_items.sort(key=lambda x: x["req_lvl"], reverse=not sort_asc)

            # Insert Tier Root
            tier_iid = f"tier_root_{tier_name}"
            tier_status = f"✅ Smelt Lvl {smelt_lvl}" if cur_lvl >= smelt_lvl else f"🔒 Smelt Lvl {smelt_lvl}"
            tier_tag = "tier_root"

            furnace_rec = "🔥 Blast Furnace" if (mem_ok and coal_qty > 0) else "🔥 Edgeville Furnace"
            furnace_xp_rate = "90k/hr (BF)" if (mem_ok and coal_qty > 0) else "25k/hr (Smelt)"

            # Materials for smelting cycle
            tier_mats_raw = [{"id": ore_id, "name": ore_name, "qty": 1}]
            if tier_name == "Bronze" and second_id > 0:
                tier_mats_raw.append({"id": second_id, "name": second_name, "qty": 1})
            elif coal_qty > 0:
                tier_mats_raw.append({"id": coal_id, "name": "Coal", "qty": coal_qty})

            base_cycle = calculate_skilling_cycle("Smithing", f"{bar_name} (Furnace Smelt)", smelt_xp, tier_mats_raw)
            base_cycle_rate = base_cycle.get("xp_per_hour", 25000)
            is_matching_smelt = bool(detected_activity and (is_activity_match(detected_activity, f"{bar_name} (Smelt Ore)") or is_activity_match(detected_activity, bar_name)))
            base_eff_rate = live_rate if (live_rate > 5000 and is_matching_smelt) else base_cycle_rate
            base_prog = get_progression_eta(cur_lvl, cur_xp, cur_lvl + 1, smelt_xp, base_cycle, live_rate=base_eff_rate if (live_rate > 5000 and is_matching_smelt) else 0)

            if cur_lvl >= smelt_lvl:
                base_time_est = f"{base_prog['time_str_next']} (Next)"
                if is_matching_smelt:
                    best_active_item = {
                        "name": f"{bar_name} Smelting",
                        "req_lvl": smelt_lvl,
                        "cycle": base_cycle,
                        "prog": base_prog,
                        "rate": base_eff_rate,
                        "is_matched": True
                    }
                elif best_active_item is None:
                    best_active_item = {
                        "name": f"{bar_name} Smelting",
                        "req_lvl": smelt_lvl,
                        "cycle": base_cycle,
                        "prog": base_prog,
                        "rate": base_eff_rate,
                        "is_matched": False
                    }
            else:
                base_time_est = f"~{base_prog['time_str_next']}"

            self.tree_guide.insert("", "end", iid=tier_iid, text=f"⚒️ {bar_name} Smelting & Smithing Family Tree", values=(
                tier_status,
                f"Lvl {smelt_lvl}+",
                ore_summary_str,
                "1 Bar = 1 Bar",
                "--",
                f"≤ {max_ore_buy:,} gp" if max_ore_buy > 0 else "--",
                f"{smelt_xp:.1f}",
                f"{'+' if smelt_gp_xp >= 0 else ''}{smelt_gp_xp:.2f} GP/XP",
                f"{'+' if bar_profit >= 0 else ''}{bar_profit:,} gp / bar",
                furnace_rec,
                furnace_xp_rate,
                base_time_est,
                f"Smelt {bar_name} from raw ores ({ore_summary_str}). Sells on GE for {bar_net:,} gp net ({'+' if bar_profit >= 0 else ''}{bar_profit:,} gp profit/bar)."
            ), tags=(tier_tag,))

            self.guide_rows.append({
                "id": tier_iid,
                "name": f"{bar_name} (Smelt Ore)",
                "status": tier_status,
                "level_range": f"{smelt_lvl} - 99",
                "min_lvl": smelt_lvl,
                "max_lvl": 99,
                "materials": ore_summary_str,
                "materials_raw": tier_mats_raw,
                "tot_mats": "1 Bar = 1 Bar",
                "tot_mat_qty": 1,
                "needed": 100,
                "max_buy": f"≤ {max_ore_buy:,} gp",
                "breakeven_ea": max_ore_buy,
                "target_buy_p": max_ore_buy,
                "curr_mat_price": ore_p,
                "margin_ea": max_ore_buy - ore_p,
                "primary_mat_name": ore_name,
                "xp_ea": smelt_xp,
                "gp_xp": f"{'+' if smelt_gp_xp >= 0 else ''}{smelt_gp_xp:.2f} GP/XP",
                "gp_xp_val": smelt_gp_xp,
                "bracket_cost": f"{'+' if bar_profit >= 0 else ''}{bar_profit:,} gp / bar",
                "bracket_cost_val": bar_profit,
                "action_rec": furnace_rec,
                "xp_rate": furnace_xp_rate,
                "xp_rate_val": 90000 if (mem_ok and coal_qty > 0) else 25000,
                "time_est": base_time_est,
                "cycle": base_cycle,
                "prog": base_prog,
                "verdict": f"Smelt {bar_name} from raw ores ({ore_summary_str}). Sells on GE for {bar_net:,} gp net ({'+' if bar_profit >= 0 else ''}{bar_profit:,} gp profit/bar).",
                "output_id": bar_id,
                "tag": tier_tag
            })

            # 1. Baseline Benchmark Child Row: Sell Bar on GE
            base_iid = f"{tier_iid}_baseline"
            self.tree_guide.insert(tier_iid, "end", iid=base_iid, text=f"  ↳ 🏷️ Sell {bar_name} on GE (Baseline Benchmark)", values=(
                "🏷️ Baseline",
                f"Lvl {smelt_lvl}",
                f"1x {bar_name}",
                ore_summary_str,
                "1 bar",
                f"≤ {bar_net:,} gp",
                "0.0",
                "--",
                f"{'+' if bar_profit >= 0 else ''}{bar_profit:,} gp",
                "🏪 Sell on GE",
                furnace_xp_rate,
                base_time_est,
                f"BASELINE BENCHMARK: Smelt bar and sell directly on GE for {bar_net:,} gp ({'+' if bar_profit >= 0 else ''}{bar_profit:,} gp profit/bar). Compare all anvil items against this baseline!"
            ), tags=("baseline",))

            self.guide_rows.append({
                "id": base_iid,
                "name": f"Sell {bar_name} on GE (Baseline)",
                "status": "🏷️ Baseline",
                "level_range": f"{smelt_lvl}",
                "min_lvl": smelt_lvl,
                "max_lvl": smelt_lvl,
                "materials": f"1x {bar_name}",
                "materials_raw": [{"id": bar_id, "name": bar_name, "qty": 1}],
                "tot_mats": ore_summary_str,
                "tot_mat_qty": 1,
                "needed": 1,
                "max_buy": f"≤ {bar_net:,} gp",
                "breakeven_ea": bar_net,
                "target_buy_p": bar_net,
                "curr_mat_price": bar_buy,
                "margin_ea": bar_net - bar_buy,
                "primary_mat_name": bar_name,
                "xp_ea": 0.0,
                "gp_xp": "--",
                "gp_xp_val": 0.0,
                "bracket_cost": f"{'+' if bar_profit >= 0 else ''}{bar_profit:,} gp",
                "bracket_cost_val": bar_profit,
                "action_rec": "🏪 Sell on GE",
                "xp_rate": furnace_xp_rate,
                "xp_rate_val": 90000 if (mem_ok and coal_qty > 0) else 25000,
                "time_est": base_time_est,
                "cycle": base_cycle,
                "prog": base_prog,
                "verdict": f"BASELINE BENCHMARK: Smelt bar and sell directly on GE for {bar_net:,} gp ({'+' if bar_profit >= 0 else ''}{bar_profit:,} gp profit/bar).",
                "output_id": bar_id,
                "tag": "baseline"
            })

            # 2. Insert Craftable Child Items
            for itm in tier_items:
                raw_item = itm["item"]
                req_lvl = itm["req_lvl"]
                itm_id = raw_item["id"]
                itm_name = raw_item["name"]
                bars_cnt = itm["bars_needed"]
                smith_xp = itm["smith_xp"]
                chain_prof = itm["chain_profit"]
                diff_bar = itm["diff_vs_bar"]
                chain_gpxp = itm["chain_gp_xp"]
                act_rec = itm["action_rec"]
                xp_rt = itm["xp_rate"]
                tb_b = itm["tb_bar"]
                be_b = itm["be_bar"]
                tag = itm["tag"]
                badge = itm["badge"]
                verdict_text = f"{badge} | {itm['verdict_msg']}"

                itm_iid = f"tree_{tier_name}_{itm_id}_{req_lvl}"
                status_str = f"✅ Lvl {req_lvl}" if cur_lvl >= req_lvl else f"🔒 Lvl {req_lvl}"

                # Total raw ores string
                if tier_name == "Bronze":
                    raw_ores_str = f"{bars_cnt}x Copper + {bars_cnt}x Tin"
                elif coal_qty > 0:
                    raw_ores_str = f"{bars_cnt}x {ore_name} + {bars_cnt * coal_qty}x Coal"
                else:
                    raw_ores_str = f"{bars_cnt}x {ore_name}"

                max_bar_str = f"≤ {tb_b:,} gp" if target_margin > 0 else f"≤ {be_b:,} gp"

                mats_cycle = [{"id": bar_id, "name": bar_name, "qty": bars_cnt}]
                cycle = calculate_skilling_cycle("Smithing", itm_name, smith_xp, mats_cycle)
                cycle_rate = cycle.get("xp_per_hour", itm.get("xp_rate", 50000))
                is_matching_active = bool(detected_activity and is_activity_match(detected_activity, itm_name))
                eff_rate = live_rate if (live_rate > 5000 and is_matching_active) else cycle_rate

                prog = get_progression_eta(cur_lvl, cur_xp, cur_lvl + 1, smith_xp, cycle, live_rate=eff_rate if (live_rate > 5000 and is_matching_active) else 0)

                if cur_lvl >= req_lvl:
                    time_est_str = f"{prog['time_str_next']} (Next)"
                    if is_matching_active:
                        best_active_item = {
                            "name": itm_name,
                            "req_lvl": req_lvl,
                            "cycle": cycle,
                            "prog": prog,
                            "rate": eff_rate,
                            "is_matched": True
                        }
                    elif best_active_item is None or (not best_active_item.get("is_matched") and req_lvl >= best_active_item.get("req_lvl", 0)):
                        best_active_item = {
                            "name": itm_name,
                            "req_lvl": req_lvl,
                            "cycle": cycle,
                            "prog": prog,
                            "rate": eff_rate,
                            "is_matched": False
                        }
                else:
                    time_est_str = f"~{prog['time_str_next']}"

                self.tree_guide.insert(tier_iid, "end", iid=itm_iid, text=f"    ↳ {itm_name}", values=(
                    status_str,
                    f"Lvl {req_lvl}",
                    f"{bars_cnt}x {bar_name}",
                    raw_ores_str,
                    f"{bars_cnt} bars",
                    max_bar_str,
                    f"{smith_xp:.1f}",
                    f"{'+' if chain_gpxp >= 0 else ''}{chain_gpxp:.2f} GP/XP",
                    f"{'+' if chain_prof >= 0 else '-'}{format_gp(abs(chain_prof))}",
                    act_rec,
                    f"{xp_rt // 1000}k/hr",
                    time_est_str,
                    verdict_text
                ), tags=(tag,))

                # Register in self.guide_rows
                self.guide_rows.append({
                    "id": itm_iid,
                    "name": itm_name,
                    "status": status_str,
                    "level_range": f"{req_lvl}",
                    "min_lvl": req_lvl,
                    "max_lvl": req_lvl,
                    "materials": f"{bars_cnt}x {bar_name}",
                    "materials_raw": [{"id": bar_id, "name": bar_name, "qty": bars_cnt}],
                    "tot_mats": raw_ores_str,
                    "tot_mat_qty": bars_cnt,
                    "needed": bars_cnt,
                    "max_buy": max_bar_str,
                    "breakeven_ea": be_b,
                    "target_buy_p": tb_b,
                    "curr_mat_price": bar_buy,
                    "margin_ea": tb_b - bar_buy,
                    "primary_mat_name": bar_name,
                    "xp_ea": smith_xp,
                    "gp_xp": f"{'+' if chain_gpxp >= 0 else ''}{chain_gpxp:.2f} GP/XP",
                    "gp_xp_val": chain_gpxp,
                    "bracket_cost": f"{'+' if chain_prof >= 0 else '-'}{format_gp(abs(chain_prof))}",
                    "bracket_cost_val": chain_prof,
                    "action_rec": act_rec,
                    "xp_rate": f"{xp_rt // 1000}k/hr",
                    "xp_rate_val": xp_rt,
                    "time_est": time_est_str,
                    "cycle": cycle,
                    "prog": prog,
                    "verdict": verdict_text,
                    "output_id": itm_id,
                    "nature_cost": 1 if act_rec == "🪄 High Alch" else 0,
                    "tag": tag,
                    "best_rev": itm["best_rev"],
                    "target_margin": target_margin,
                    "diff_vs_bar": diff_bar,
                    "chain_profit": chain_prof
                })

                # Grandchildren: Expand to see individual ingredients & buy ceilings
                # 1. Bar buy ceiling
                bar_bid, bar_ask = self.api.get_bid_ask(str(bar_id), basis=basis)
                self.tree_guide.insert(itm_iid, "end", iid=f"{itm_iid}_mat_bar", text=f"        ↳ {bars_cnt}x {bar_name} (Anvil Bar)", values=(
                    "--",
                    "--",
                    f"{bars_cnt}x {bar_name}",
                    f"{bars_cnt}x {bar_name}",
                    f"{bars_cnt}x",
                    max_bar_str,
                    f"Offer: {bar_bid:,}" if bar_bid > 0 else "--",
                    f"Ask: {bar_ask:,}" if bar_ask > 0 else "--",
                    f"Cost: {format_gp(bars_cnt * bar_buy)}",
                    "🏪 GE Buy Bar",
                    "--",
                    "--",
                    f"🎯 Buy {bar_name} ≤ {tb_b if target_margin > 0 else be_b:,} gp to profit directly from anvil"
                ), tags=("child_row",))

                # 2. Raw Primary Ore buy ceiling
                other_sub = (bars_cnt * coal_qty * coal_price) if tier_name != "Bronze" else (bars_cnt * second_p)
                nat_sub = nat_price if act_rec == "🪄 High Alch" else 0
                net_alloc_ore = itm["best_rev"] - other_sub - nat_sub
                be_ore = math.floor(net_alloc_ore / bars_cnt) if bars_cnt > 0 else 0
                tb_ore = math.floor((net_alloc_ore - target_margin) / bars_cnt) if bars_cnt > 0 else 0
                ore_bid, ore_ask = self.api.get_bid_ask(str(ore_id), basis=basis)

                self.tree_guide.insert(itm_iid, "end", iid=f"{itm_iid}_mat_ore", text=f"        ↳ {bars_cnt}x {ore_name} (Raw Ore Smelt)", values=(
                    "--",
                    "--",
                    f"{bars_cnt}x {ore_name}",
                    f"{bars_cnt}x {ore_name}",
                    f"{bars_cnt}x",
                    f"≤ {tb_ore if target_margin > 0 else be_ore:,} gp",
                    f"Offer: {ore_bid:,}" if ore_bid > 0 else "--",
                    f"Ask: {ore_ask:,}" if ore_ask > 0 else "--",
                    f"Cost: {format_gp(bars_cnt * ore_p)}",
                    "⛏️ Raw Ore",
                    "--",
                    "--",
                    f"🎯 Buy {ore_name} ≤ {tb_ore if target_margin > 0 else be_ore:,} gp to profit from full smelting + smithing chain"
                ), tags=("child_row",))

                # 3. Coal or Secondary Fuel (if applicable)
                if coal_qty > 0 and tier_name != "Bronze":
                    tot_coal = bars_cnt * coal_qty
                    net_alloc_coal = itm["best_rev"] - (bars_cnt * ore_p) - nat_sub
                    be_coal = math.floor(net_alloc_coal / tot_coal) if tot_coal > 0 else 0
                    tb_coal = math.floor((net_alloc_coal - target_margin) / tot_coal) if tot_coal > 0 else 0
                    coal_bid, coal_ask = self.api.get_bid_ask(str(coal_id), basis=basis)

                    self.tree_guide.insert(itm_iid, "end", iid=f"{itm_iid}_mat_coal", text=f"        ↳ {tot_coal}x Coal (Smelting Fuel)", values=(
                        "--",
                        "--",
                        f"{tot_coal}x Coal",
                        f"{tot_coal}x Coal",
                        f"{tot_coal}x",
                        f"≤ {tb_coal if target_margin > 0 else be_coal:,} gp",
                        f"Offer: {coal_bid:,}" if coal_bid > 0 else "--",
                        f"Ask: {coal_ask:,}" if coal_ask > 0 else "--",
                        f"Cost: {format_gp(tot_coal * coal_price)}",
                        "🔥 Smelt Fuel",
                        "--",
                        "--",
                        f"🎯 Buy Coal ≤ {tb_coal if target_margin > 0 else be_coal:,} gp to preserve chain profit"
                    ), tags=("child_row",))

                # 4. Nature rune if alching
                if act_rec == "🪄 High Alch" and itm["alch_val"] > 0:
                    nat_bid, nat_ask = self.api.get_bid_ask(str(NATURE_RUNE_ID), basis=basis)
                    self.tree_guide.insert(itm_iid, "end", iid=f"{itm_iid}_mat_nat", text=f"        ↳ 1x Nature rune (High Alchemy)", values=(
                        "--",
                        "--",
                        "1x Nature rune",
                        "1x Nature rune",
                        "1x",
                        f"≤ {itm['alch_val'] - itm['item_ore_cost']:,} gp",
                        f"Offer: {nat_bid:,}" if nat_bid > 0 else "--",
                        f"Ask: {nat_ask:,}" if nat_ask > 0 else "--",
                        f"Cost: {format_gp(nat_price)}",
                        "🪄 Alch Rune",
                        "--",
                        "--",
                        f"High Alch gives {itm['alch_val']:,} gp gross revenue"
                    ), tags=("child_row",))

                if itm_iid in prev_open:
                    self.tree_guide.item(itm_iid, open=True)

            # Open root tiers by default only on initial app load if not previously set
            if (is_first_init and not prev_open) or tier_iid in prev_open:
                self.tree_guide.item(tier_iid, open=True)

        # Update top progress banner for Smithing tree
        if best_active_item and hasattr(self, "lbl_guide_eta_badge"):
            b_cycle = best_active_item["cycle"]
            b_prog = best_active_item["prog"]
            b_rate = best_active_item["rate"]

            self.lbl_guide_eta_badge.config(text=f"⏱️ Est. Next Lvl: {b_prog.get('time_str_next', '--')}")

            st_name = b_cycle.get("station_name", "Varrock West Anvil")
            c_sec = b_cycle.get("cycle_secs", 0)
            a_inv = b_cycle.get("actions_per_inv", 5)
            pace_txt = f"⚡ Physical Pace: ~{c_sec:.1f}s cycle ({a_inv} items/inv @ {st_name})"
            if live_rate > 5000:
                pace_txt += f"  •  🟢 LIVE: {int(live_rate):,} XP/hr"
            else:
                pace_txt += f"  •  Est: {int(b_cycle.get('xp_per_hour', 0)):,} XP/hr"
            if hasattr(self, "lbl_guide_pace_summary"):
                self.lbl_guide_pace_summary.config(text=pace_txt)

            trips_txt = f"🎒 Trips to Next Lvl: ~{b_prog.get('trips_next', 0)} inv ({b_prog.get('actions_next', 0):,} actions)"
            if target_lvl > cur_lvl + 1:
                trips_txt += f"  |  Goal Lvl {target_lvl}: ~{b_prog.get('trips_goal', 0)} inv ({b_prog.get('time_str_goal', '--')})"
            if hasattr(self, "lbl_guide_trips_summary"):
                self.lbl_guide_trips_summary.config(text=trips_txt)

            self._guide_prog_data = {
                "cur_lvl": cur_lvl,
                "next_lvl": min(99, cur_lvl + 1),
                "target_lvl": target_lvl,
                "cur_xp": cur_xp,
                "rem_xp_next": b_prog.get("rem_xp_next", 0),
                "pct_next": b_prog.get("pct_to_next", 0.0),
                "time_str_next": b_prog.get("time_str_next", "--")
            }
            self._draw_guide_progress_bar()

    def _draw_guide_progress_bar(self):
        if not hasattr(self, "canvas_guide_prog"):
            return
        c = self.canvas_guide_prog
        w = c.winfo_width()
        h = c.winfo_height()
        if w < 10 or h < 5:
            return
        c.delete("all")

        data = getattr(self, "_guide_prog_data", None)
        if not data:
            c.create_rectangle(0, 0, w, h, fill="#151518", outline="")
            c.create_text(w // 2, h // 2, text="🎯 Set level or connect bridge to track pacing", font=("Segoe UI", 8), fill="#777777")
            return

        cur_lvl = data.get("cur_lvl", 1)
        next_lvl = data.get("next_lvl", min(99, cur_lvl + 1))
        target_lvl = data.get("target_lvl", 99)
        pct_next = max(0.0, min(100.0, data.get("pct_next", 0.0)))
        rem_xp_next = data.get("rem_xp_next", 0)
        time_str_next = data.get("time_str_next", "--")

        fill_w = int(w * (pct_next / 100.0))
        # Background track
        c.create_rectangle(0, 0, w, h, fill="#1c1c20", outline="")
        # Progress fill
        if fill_w > 0:
            c.create_rectangle(0, 0, fill_w, h, fill="#00b4d8", outline="")

        if cur_lvl >= target_lvl:
            prog_txt = f"🏆 Goal Level {target_lvl} Complete! (100%)"
        elif cur_lvl >= 99:
            prog_txt = "👑 Level 99 Reached!"
        else:
            prog_txt = f"Level {cur_lvl} → {next_lvl}: {pct_next:.1f}% ({rem_xp_next:,} XP left)  •  ETA: {time_str_next}"

        c.create_text(w // 2, h // 2, text=prog_txt, font=("Segoe UI", 8, "bold"), fill="#ffffff")

    def recalculate_guide_table(self):
        if not hasattr(self, "tree_guide"):
            return

        active_skill = self.var_guide_skill.get()
        try:
            cur_lvl = int(self.ent_guide_cur_lvl.get().strip())
        except ValueError:
            cur_lvl = 1

        try:
            target_lvl = int(self.ent_guide_target_lvl.get().strip())
        except ValueError:
            target_lvl = 99

        # Check if connected account has exact XP and live skilling activity data
        active_acc_name = self.var_account.get() if hasattr(self, "var_account") else "All Accounts"
        acc_info = {}
        if active_acc_name != "All Accounts" and active_acc_name in self.state.accounts:
            acc_info = self.state.accounts[active_acc_name]
        elif self.state.accounts:
            # Fall back to the most recently seen account
            acc_info = max(self.state.accounts.values(), key=lambda a: a.get("last_seen", 0))

        acc_levels = acc_info.get("levels", {})
        if active_skill in acc_levels:
            live_lvl = acc_levels[active_skill]
            if live_lvl > 0 and (cur_lvl <= 1 or cur_lvl != live_lvl):
                cur_lvl = live_lvl
                if hasattr(self, "ent_guide_cur_lvl"):
                    self.ent_guide_cur_lvl.delete(0, tk.END)
                    self.ent_guide_cur_lvl.insert(0, str(live_lvl))

        acc_xps = acc_info.get("xp", {})
        exact_xp = acc_xps.get(active_skill)
        if exact_xp is not None and exact_xp > 0:
            cur_xp = int(exact_xp)
        else:
            cur_xp = get_xp_for_level(cur_lvl)

        skilling_data = acc_info.get("skilling", {})
        live_rate = 0
        detected_activity = ""
        if skilling_data and skilling_data.get("active_skill") == active_skill:
            if time.time() - skilling_data.get("timestamp", 0) < 180:
                live_rate = skilling_data.get("skilling_xp_hr", 0)
                detected_activity = skilling_data.get("detected_activity", "")

        target_xp = get_xp_for_level(target_lvl)
        rem_xp = max(0, target_xp - cur_xp)
        pct_done = (1.0 - (rem_xp / max(1, target_xp))) * 100.0 if target_xp > 0 else 100.0

        summary_txt = f"🎯 Goal: Level {target_lvl} ({target_xp:,} XP)  |  Current: Level {cur_lvl} ({cur_xp:,} XP)  |  XP Remaining: {rem_xp:,} XP ({pct_done:.1f}% Complete)"
        if hasattr(self, "lbl_guide_xp_summary"):
            self.lbl_guide_xp_summary.config(text=summary_txt)

        def _get_open_iids(tree, parent=""):
            open_set = set()
            for iid in tree.get_children(parent):
                if tree.item(iid, "open"):
                    open_set.add(iid)
                open_set.update(_get_open_iids(tree, iid))
            return open_set

        prev_open = _get_open_iids(self.tree_guide)
        self.tree_guide.delete(*self.tree_guide.get_children())
        self.guide_rows = []
        search_query = self.ent_search.get().strip().lower() if hasattr(self, "ent_search") else ""

        sdata = SKILLING_GUIDES.get(active_skill, {})
        brackets = sdata.get("brackets", [])
        style_filter = self.var_guide_style.get()
        mem_ok = self.is_guide_p2p_allowed()

        # Update local checkbutton visual state if needed
        if hasattr(self, "cb_guide_mem") and hasattr(self, "var_guide_members"):
            if self.var_guide_members.get() != mem_ok:
                self.var_guide_members.set(mem_ok)

        # If skill is strictly members-only (like Fletching) and mem_ok is False:
        if active_skill == "Fletching" and not mem_ok:
            if hasattr(self, "lbl_guide_xp_summary"):
                self.lbl_guide_xp_summary.config(text="⚠️ Fletching is a Members-only skill in Old School RuneScape. Enable P2P Methods to view recipes.")
            self.tree_guide.insert("", "end", iid="fletch_p2p_warn", text="🔒 Fletching is Members-only", values=(
                "🔒 P2P Only",
                "1 - 99",
                "None (P2P)",
                "--",
                "0",
                "--",
                "--",
                "0",
                "--",
                "--",
                "Enable P2P",
                "--",
                "--",
                "⚠️ Fletching cannot be trained on Free-to-play worlds."
            ), tags=("locked",))
            return

        strat = self.var_strat.get().split()[0] if hasattr(self, "var_strat") else "smart"
        nat_price = self.get_effective_nature_price()

        guide_view = self.var_guide_view.get() if hasattr(self, "var_guide_view") else "🌲 Material Chain Tree"
        if active_skill == "Smithing" and guide_view == "🌲 Material Chain Tree":
            self._render_smithing_material_tree(cur_lvl, target_lvl, cur_xp, target_xp, rem_xp, mem_ok, style_filter, search_query, strat, nat_price, prev_open, live_rate=live_rate, detected_activity=detected_activity)
            return

        active_bracket_obj = None
        current_step_found = False

        for b in brackets:
            b_mem = b.get("members", True)
            if not mem_ok and b_mem:
                continue

            b_style = b.get("style", "standard")
            if style_filter == "profit" and b_style not in ("profit", "quest"):
                continue
            if style_filter == "fast" and b_style not in ("fast", "quest"):
                continue
            if style_filter == "afk" and b_style not in ("afk", "quest"):
                continue

            min_l = b["min_lvl"]
            max_l = b["max_lvl"]

            # Status determination
            if cur_lvl >= max_l:
                status = "✅ Completed"
                status_tag = "completed"
            elif min_l <= cur_lvl < max_l:
                status = "📍 YOU ARE HERE"
                status_tag = "current"
                current_step_found = True
            elif not current_step_found and cur_lvl < min_l:
                status = "🔒 Locked"
                status_tag = "locked"
            else:
                status = "🔒 Locked"
                status_tag = "locked"

            if b_style == "quest":
                status_tag = "quest"

            # Actions needed
            xp_ea = b.get("xp_per_action", 1.0)
            if cur_lvl >= max_l:
                xp_needed_bracket = 0
                actions_needed = 0
            else:
                step_start_xp = max(get_xp_for_level(cur_lvl), get_xp_for_level(min_l))
                step_end_xp = min(get_xp_for_level(max_l), target_xp)
                xp_needed_bracket = max(0, step_end_xp - step_start_xp)
                actions_needed = math.ceil(xp_needed_bracket / xp_ea) if (xp_ea > 0 and xp_needed_bracket > 0) else 0

            # Material cost & total materials needed calculation
            mat_cost_ea = 0
            mat_str_list = []
            mats = b.get("materials", [])
            for m in mats:
                p = self.api.get_price(m["id"], strat)
                mat_cost_ea += p * m["qty"]
                mat_str_list.append(f"{m['qty']}x {m['name']}")
            materials_str = ", ".join(mat_str_list) if mat_str_list else "None / Quest"

            # Total materials needed across the bracket
            tot_mats_str = "--"
            tot_mat_qty = 0
            primary_mat_name = mats[0]["name"] if mats else ""

            display_actions = actions_needed
            if display_actions == 0 and cur_lvl < min_l:
                # Locked / upcoming bracket: calculate full bracket requirement
                bracket_xp = min(get_xp_for_level(max_l), target_xp) - get_xp_for_level(min_l)
                display_actions = math.ceil(bracket_xp / xp_ea) if (xp_ea > 0 and bracket_xp > 0) else 0

            if mats:
                if display_actions > 0:
                    tot_mat_qty = mats[0]["qty"] * display_actions
                    tot_mats_list = [f"{m['qty'] * display_actions:,}x {m['name']}" for m in mats]
                    tot_mats_str = ", ".join(tot_mats_list)
                elif cur_lvl >= max_l:
                    tot_mats_str = "0 (Completed)"
                else:
                    tot_mats_str = "0"
            elif b_style == "quest":
                tot_mats_str = "None (Quest)"

            # Output valuation & disposal recommendation
            out_id = b.get("output_id", 0)
            out_qty = b.get("output_qty", 1)
            alch_val = self.api.mapping.get(str(out_id), {}).get("highalch", 0) if b.get("can_alch") else 0
            nat_cost = nat_price if b.get("nature_cost", 0) > 0 else 0
            total_act_cost = mat_cost_ea + nat_cost

            profit_alch = ((alch_val * out_qty) - total_act_cost) if b.get("can_alch") else -99999999
            ge_sell = self.api.get_price(out_id, "instasell") if b.get("can_sell_ge") and out_id > 0 else 0
            profit_ge = ((int(ge_sell * 0.99) * out_qty) - mat_cost_ea) if b.get("can_sell_ge") and out_id > 0 else -99999999

            w308_staple = next((it_s for it_s in W308_STAPLES if it_s["id"] == out_id or it_s["name"].lower() == b.get("item_name", "").lower()), None)
            profit_w308 = ((w308_staple["w308_buy"] * out_qty) - mat_cost_ea) if w308_staple else -99999999

            if b_style == "quest":
                action_rec = "📜 Quest Turn-in"
                best_profit_ea = 0
                gp_per_xp = 0.0
                gp_xp_str = "FREE (0 GP)"
                bracket_cost_str = "0 gp"
                total_cost = 0
            elif profit_w308 >= profit_ge and profit_w308 >= profit_alch and profit_w308 > -90000000:
                action_rec = "🤝 Bulk Trade"
                best_profit_ea = profit_w308
                gp_per_xp = best_profit_ea / xp_ea if xp_ea > 0 else 0.0
                gp_xp_str = f"+{gp_per_xp:.2f} GP/XP" if gp_per_xp >= 0 else f"{gp_per_xp:.2f} GP/XP"
                total_cost = best_profit_ea * (actions_needed if actions_needed > 0 else 100)
                bracket_cost_str = f"+{format_gp(total_cost)}" if total_cost >= 0 else f"-{format_gp(abs(total_cost))}"
            elif profit_alch >= profit_ge and b.get("can_alch"):
                action_rec = "🪄 High Alch"
                best_profit_ea = profit_alch
                gp_per_xp = best_profit_ea / xp_ea if xp_ea > 0 else 0.0
                gp_xp_str = f"+{gp_per_xp:.2f} GP/XP" if gp_per_xp >= 0 else f"{gp_per_xp:.2f} GP/XP"
                total_cost = best_profit_ea * (actions_needed if actions_needed > 0 else 100)
                bracket_cost_str = f"+{format_gp(total_cost)}" if total_cost >= 0 else f"-{format_gp(abs(total_cost))}"
            elif b.get("can_sell_ge"):
                action_rec = "🏪 Sell on GE"
                best_profit_ea = profit_ge
                gp_per_xp = best_profit_ea / xp_ea if xp_ea > 0 else 0.0
                gp_xp_str = f"+{gp_per_xp:.2f} GP/XP" if gp_per_xp >= 0 else f"{gp_per_xp:.2f} GP/XP"
                total_cost = best_profit_ea * (actions_needed if actions_needed > 0 else 100)
                bracket_cost_str = f"+{format_gp(total_cost)}" if total_cost >= 0 else f"-{format_gp(abs(total_cost))}"
            else:
                action_rec = "⚔️ Train / Consume"
                best_profit_ea = -mat_cost_ea
                gp_per_xp = best_profit_ea / xp_ea if xp_ea > 0 else 0.0
                gp_xp_str = f"{gp_per_xp:.2f} GP/XP"
                total_cost = best_profit_ea * (actions_needed if actions_needed > 0 else 100)
                bracket_cost_str = f"-{format_gp(abs(total_cost))}"

            # Breakeven & Target Material Buy Calculation
            target_margin = 0
            if hasattr(self, "ent_guide_margin"):
                try:
                    target_margin = max(0, parse_cash_input(self.ent_guide_margin.get()))
                except Exception:
                    target_margin = 0

            eff_alch_rev = ((alch_val * out_qty) - nat_cost) if (b.get("can_alch") and alch_val > 0) else -99999999
            eff_ge_rev = (int(ge_sell * 0.99) * out_qty) if (b.get("can_sell_ge") and out_id > 0) else -99999999
            best_rev = max(eff_alch_rev, eff_ge_rev)

            curr_mat_p = 0
            breakeven_p = 0
            target_buy_p = 0
            margin_at_curr = 0
            max_buy_str = "--"

            if mats and best_rev > -99999999:
                primary_mat = mats[0]
                primary_qty = primary_mat.get("qty", 1)
                curr_mat_p = self.api.get_price(primary_mat["id"], strat)

                # Secondary materials cost (e.g. gems or bow strings)
                secondary_cost = sum(self.api.get_price(m["id"], strat) * m["qty"] for m in mats[1:])
                net_alloc_rev = best_rev - secondary_cost

                breakeven_p = math.floor(net_alloc_rev / primary_qty) if primary_qty > 0 else 0
                target_buy_p = math.floor((net_alloc_rev - target_margin) / primary_qty) if primary_qty > 0 else 0
                margin_at_curr = target_buy_p - curr_mat_p

                if target_margin > 0:
                    max_buy_str = f"≤ {target_buy_p:,} gp"
                else:
                    max_buy_str = f"≤ {breakeven_p:,} gp"
            elif b_style == "quest":
                max_buy_str = "FREE (Quest)"

            verdict_text = b.get("verdict", "")
            if breakeven_p > 0:
                if target_margin > 0:
                    verdict_text = f"{verdict_text} [🎯 Buy @ ≤ {target_buy_p:,} gp ea (+{target_margin:,} margin | Breakeven: ≤ {breakeven_p:,} gp)]"
                else:
                    verdict_text = f"{verdict_text} [🎯 Breakeven Buy: ≤ {breakeven_p:,} gp ea (Market: {curr_mat_p:,} gp)]"

            # Cycle & Progression ETA calculation
            cycle = calculate_skilling_cycle(active_skill, b["name"], xp_ea, mats)
            cycle_rate = cycle.get("xp_per_hour", b.get("xp_rate", 50000))
            is_matching_active = bool(detected_activity and is_activity_match(detected_activity, b["name"]))
            eff_rate = live_rate if (live_rate > 5000 and is_matching_active) else cycle_rate

            prog = get_progression_eta(cur_lvl, cur_xp, cur_lvl + 1, xp_ea, cycle, live_rate=eff_rate if (live_rate > 5000 and is_matching_active) else 0)

            # Time estimate
            if status_tag == "current":
                time_est_str = f"{prog['time_str_next']} (Next)"
                if is_matching_active:
                    active_bracket_obj = {
                        "name": b["name"],
                        "cycle": cycle,
                        "prog": prog,
                        "rate": eff_rate,
                        "is_matched": True
                    }
                elif active_bracket_obj is None or not active_bracket_obj.get("is_matched"):
                    active_bracket_obj = {
                        "name": b["name"],
                        "cycle": cycle,
                        "prog": prog,
                        "rate": eff_rate,
                        "is_matched": False
                    }
            elif cur_lvl >= max_l:
                time_est_str = "0s"
            elif xp_needed_bracket > 0 and cycle_rate > 0:
                hrs = xp_needed_bracket / cycle_rate
                secs = int(hrs * 3600.0)
                time_est_str = format_skilling_duration(secs)
            else:
                time_est_str = "--"

            # Row tag priority
            if status_tag == "current":
                final_tag = "current"
            elif status_tag == "quest":
                final_tag = "quest"
            elif status_tag == "completed":
                final_tag = "completed"
            elif gp_per_xp >= 0:
                final_tag = "profit"
            elif gp_per_xp >= -2.0:
                final_tag = "mild_loss"
            else:
                final_tag = "loss"

            row_obj = {
                "id": f"{min_l}_{max_l}_{b['name']}",
                "status": status,
                "level_range": f"{min_l} - {max_l}",
                "name": b["name"],
                "materials": materials_str,
                "materials_raw": b.get("materials", []),
                "tot_mats": tot_mats_str,
                "tot_mat_qty": tot_mat_qty,
                "max_buy": max_buy_str,
                "max_buy_val": target_buy_p if target_buy_p > 0 else breakeven_p,
                "breakeven_ea": breakeven_p,
                "target_buy_p": target_buy_p,
                "curr_mat_price": curr_mat_p,
                "margin_ea": margin_at_curr,
                "primary_mat_name": primary_mat_name,
                "xp_ea": xp_ea,
                "needed": actions_needed,
                "gp_xp": gp_xp_str,
                "gp_xp_val": gp_per_xp,
                "bracket_cost": bracket_cost_str,
                "bracket_cost_val": total_cost,
                "action_rec": action_rec,
                "xp_rate": f"{int(cycle_rate) // 1000}k/hr" if cycle_rate >= 1000 else f"{int(cycle_rate)}/hr",
                "xp_rate_val": cycle_rate,
                "time_est": time_est_str,
                "cycle": cycle,
                "prog": prog,
                "verdict": verdict_text,
                "output_id": out_id,
                "nature_cost": b.get("nature_cost", 0),
                "tag": final_tag,
                "min_lvl": min_l,
                "max_lvl": max_l,
                "wiki_slug": b.get("wiki_slug", ""),
                "display_actions": display_actions,
                "best_rev": best_rev,
                "target_margin": target_margin
            }

            if search_query:
                name_match = search_query in b["name"].lower()
                mat_match = search_query in materials_str.lower()
                verdict_match = search_query in verdict_text.lower()
                action_match = search_query in action_rec.lower()
                if not (name_match or mat_match or verdict_match or action_match):
                    continue

            self.guide_rows.append(row_obj)

        # Sort guide rows according to active column
        if getattr(self, "guide_sort_col", None):
            col = self.guide_sort_col
            asc = getattr(self, "guide_sort_asc", True)
            if col == "level_range":
                self.guide_rows.sort(key=lambda r: r["min_lvl"], reverse=not asc)
            elif col == "tot_mats":
                self.guide_rows.sort(key=lambda r: r.get("tot_mat_qty", 0), reverse=not asc)
            elif col == "max_buy":
                self.guide_rows.sort(key=lambda r: r.get("max_buy_val", 0), reverse=not asc)
            elif col == "xp_ea":
                self.guide_rows.sort(key=lambda r: r["xp_ea"], reverse=not asc)
            elif col == "needed":
                self.guide_rows.sort(key=lambda r: r["needed"], reverse=not asc)
            elif col == "gp_xp":
                self.guide_rows.sort(key=lambda r: r["gp_xp_val"], reverse=not asc)
            elif col == "bracket_cost":
                self.guide_rows.sort(key=lambda r: r["bracket_cost_val"], reverse=not asc)
            elif col == "xp_rate":
                self.guide_rows.sort(key=lambda r: r["xp_rate_val"], reverse=not asc)
            elif col == "name":
                self.guide_rows.sort(key=lambda r: r["name"], reverse=not asc)
            else:
                self.guide_rows.sort(key=lambda r: str(r.get(col, "")), reverse=not asc)

        basis = "5m" if hasattr(self, "var_price_basis") and "5m" in self.var_price_basis.get() else self.state.config.get("price_basis", "5m")

        for r in self.guide_rows:
            p_id = r["id"]
            self.tree_guide.insert("", "end", iid=p_id, text=f"  {r['name']}", values=(
                r["status"],
                r["level_range"],
                r["materials"],
                r["tot_mats"],
                f"{r['needed']:,}",
                r["max_buy"],
                f"{r['xp_ea']:,.1f}" if r["xp_ea"] % 1 else f"{int(r['xp_ea']):,}",
                r["gp_xp"],
                r["bracket_cost"],
                r["action_rec"],
                r["xp_rate"],
                r["time_est"],
                r["verdict"]
            ), tags=(r["tag"],))

            # Insert child ingredient rows underneath if materials exist
            mats = r.get("materials_raw", [])
            if mats:
                actions_cnt = r["needed"] if r["needed"] > 0 else r.get("display_actions", 0)
                best_rev_val = r.get("best_rev", 0)
                t_margin = r.get("target_margin", 0)

                for idx, m in enumerate(mats):
                    child_iid = f"{p_id}_mat_{m['id']}_{idx}"
                    m_qty = m["qty"]

                    # Calculate individual ceiling for this material assuming other materials at market price
                    other_cost = sum(self.api.get_price(other["id"], strat) * other["qty"] for other_idx, other in enumerate(mats) if other_idx != idx)
                    net_alloc_m = best_rev_val - other_cost
                    be_m = math.floor(net_alloc_m / m_qty) if m_qty > 0 else 0
                    tb_m = math.floor((net_alloc_m - t_margin) / m_qty) if m_qty > 0 else 0

                    m_ceiling = f"🎯 ≤ {tb_m:,} gp" if tb_m > 0 else (f"≤ {be_m:,} gp" if be_m > 0 else "--")

                    tot_m_qty = m_qty * actions_cnt
                    tot_m_str = f"{tot_m_qty:,}x {m['name']}" if tot_m_qty > 0 else f"{m_qty}x {m['name']}"

                    m_bid, m_ask = self.api.get_bid_ask(str(m["id"]), basis=basis)
                    p_curr = self.api.get_price(m["id"], strat)
                    sub_cost = p_curr * tot_m_qty

                    self.tree_guide.insert(p_id, "end", iid=child_iid, text=f"    ↳ {m['qty']}x {m['name']}", values=(
                        "--",
                        "--",
                        f"{m['qty']}x {m['name']}",
                        tot_m_str,
                        f"{tot_m_qty:,}" if tot_m_qty > 0 else f"{m_qty}x",
                        m_ceiling,
                        f"Offer: {m_bid:,}" if m_bid > 0 else "--",
                        f"Ask: {m_ask:,}" if m_ask > 0 else "--",
                        f"Cost: {format_gp(sub_cost)}" if sub_cost > 0 else "--",
                        "🏪 GE Offer",
                        "--",
                        "--",
                        f"🎯 Buy {m['name']} ≤ {tb_m if tb_m > 0 else be_m:,} gp to maintain margin"
                    ), tags=("child_row",))

            if p_id in prev_open:
                self.tree_guide.item(p_id, open=True)


        # Append current step target buy info to XP summary banner if available
        curr_step = next((r for r in self.guide_rows if "YOU ARE HERE" in r.get("status", "")), None)
        if curr_step and curr_step.get("breakeven_ea", 0) > 0 and hasattr(self, "lbl_guide_xp_summary"):
            cur_summary = self.lbl_guide_xp_summary.cget("text")
            if "Target Buy:" not in cur_summary:
                self.lbl_guide_xp_summary.config(text=f"{cur_summary}  |  🎯 Current Step Buy: {curr_step['max_buy']} ({curr_step.get('primary_mat_name', 'bars')})")

        # Update top banner progression metrics for standard views
        if active_bracket_obj and hasattr(self, "lbl_guide_eta_badge"):
            b_cycle = active_bracket_obj["cycle"]
            b_prog = active_bracket_obj["prog"]
            b_rate = active_bracket_obj["rate"]

            self.lbl_guide_eta_badge.config(text=f"⏱️ Est. Next Lvl: {b_prog.get('time_str_next', '--')}")

            st_name = b_cycle.get("station_name", "Bank Booth")
            c_sec = b_cycle.get("cycle_secs", 0)
            a_inv = b_cycle.get("actions_per_inv", 27)
            pace_txt = f"⚡ Physical Pace: ~{c_sec:.1f}s cycle ({a_inv} items/inv @ {st_name})"
            if live_rate > 5000:
                pace_txt += f"  •  🟢 LIVE: {int(live_rate):,} XP/hr"
            else:
                pace_txt += f"  •  Est: {int(b_cycle.get('xp_per_hour', 0)):,} XP/hr"
            if hasattr(self, "lbl_guide_pace_summary"):
                self.lbl_guide_pace_summary.config(text=pace_txt)

            trips_txt = f"🎒 Trips to Next Lvl: ~{b_prog.get('trips_next', 0)} inv ({b_prog.get('actions_next', 0):,} actions)"
            if target_lvl > cur_lvl + 1:
                trips_txt += f"  |  Goal Lvl {target_lvl}: ~{b_prog.get('trips_goal', 0)} inv ({b_prog.get('time_str_goal', '--')})"
            if hasattr(self, "lbl_guide_trips_summary"):
                self.lbl_guide_trips_summary.config(text=trips_txt)

            self._guide_prog_data = {
                "cur_lvl": cur_lvl,
                "next_lvl": min(99, cur_lvl + 1),
                "target_lvl": target_lvl,
                "cur_xp": cur_xp,
                "rem_xp_next": b_prog.get("rem_xp_next", 0),
                "pct_next": b_prog.get("pct_to_next", 0.0),
                "time_str_next": b_prog.get("time_str_next", "--")
            }
            self._draw_guide_progress_bar()
        elif cur_lvl >= target_lvl:
            if hasattr(self, "lbl_guide_eta_badge"):
                self.lbl_guide_eta_badge.config(text="⏱️ Goal Complete!")
            if hasattr(self, "lbl_guide_pace_summary"):
                self.lbl_guide_pace_summary.config(text="⚡ Target Level Reached! Congratulations!")
            if hasattr(self, "lbl_guide_trips_summary"):
                self.lbl_guide_trips_summary.config(text="🎒 Trips: 0 remaining")
            self._guide_prog_data = {
                "cur_lvl": cur_lvl,
                "next_lvl": min(99, cur_lvl + 1),
                "target_lvl": target_lvl,
                "cur_xp": cur_xp,
                "rem_xp_next": 0,
                "pct_next": 100.0,
                "time_str_next": "0s"
            }
            self._draw_guide_progress_bar()

    def get_selected_guide_row(self):
        sel = self.tree_guide.selection()
        if not sel:
            return None
        row_id = sel[0]
        if "_mat_" in str(row_id):
            parent_id = self.tree_guide.parent(row_id)
            return next((r for r in self.guide_rows if r["id"] == parent_id), None)
        return next((r for r in self.guide_rows if r["id"] == row_id), None)

    def on_guide_click(self, event):
        row_id = self.tree_guide.identify_row(event.y)
        if not row_id:
            return
        col_id = self.tree_guide.identify_column(event.x)

        if col_id == "#0":
            if self.tree_guide.get_children(row_id):
                cur = self.tree_guide.item(row_id, "open")
                self.tree_guide.item(row_id, open=not cur)
            raw_text = self.tree_guide.item(row_id, "text")
            clean_name = raw_text.replace("▶", "").replace("▼", "").replace("↳", "").strip()
            if "x " in clean_name and clean_name[:3].replace("x", "").strip().isdigit():
                clean_name = clean_name.split("x ", 1)[-1].strip()
            self.copy_to_clipboard(clean_name, f"Copied '{clean_name}' to clipboard!")
            return

        if col_id == "#6":
            raw_buy = self.tree_guide.set(row_id, "max_buy")
            clean_p = "".join(c for c in raw_buy if c.isdigit())
            if clean_p:
                raw_text = self.tree_guide.item(row_id, "text").replace("↳", "").strip()
                self.copy_to_clipboard(clean_p, f"📋 Copied Max Buy Price: {int(clean_p):,} gp ({raw_text}) to clipboard!")
            return

        if col_id in ("#4", "#5"):
            raw_val = self.tree_guide.set(row_id, "needed") if col_id == "#5" else self.tree_guide.set(row_id, "tot_mats")
            clean_qty = "".join(c for c in raw_val if c.isdigit())
            if clean_qty:
                self.copy_to_clipboard(clean_qty, f"📋 Copied Quantity: {int(clean_qty):,} to clipboard!")
            return

        if col_id == "#7":
            raw_val = self.tree_guide.set(row_id, "xp_ea")
            clean_num = "".join(c for c in raw_val if c.isdigit())
            if clean_num and "Offer:" in raw_val:
                self.copy_to_clipboard(clean_num, f"📋 Copied Target Offer (Bid): {int(clean_num):,} gp to clipboard!")
            return

        if col_id == "#8":
            raw_val = self.tree_guide.set(row_id, "gp_xp")
            clean_num = "".join(c for c in raw_val if c.isdigit())
            if clean_num and "Ask:" in raw_val:
                self.copy_to_clipboard(clean_num, f"📋 Copied Instant Buy (Ask): {int(clean_num):,} gp to clipboard!")
            return

        row = next((r for r in self.guide_rows if r["id"] == row_id), None)
        item_n = row["name"] if row else self.tree_guide.item(row_id, "text")
        if item_n:
            self.load_item_into_inspector(item_n)
        if not row:
            return

        if col_id == "#3":
            self.copy_to_clipboard(row["materials"], f"Copied materials for '{row['name']}' to clipboard!")

    def on_guide_double_click(self, event):
        row_id = self.tree_guide.identify_row(event.y)
        if not row_id:
            return
        if self.tree_guide.get_children(row_id):
            cur = self.tree_guide.item(row_id, "open")
            self.tree_guide.item(row_id, open=not cur)
        else:
            self.tree_guide.selection_set(row_id)
            self.add_guide_batch_to_cart()

    def on_guide_right_click(self, event):
        row_id = self.tree_guide.identify_row(event.y)
        if not row_id:
            return
        self.tree_guide.selection_set(row_id)

        menu = tk.Menu(self, tearoff=0, bg="#2d2d30", fg="#ffffff", activebackground="#f39c12", activeforeground="#000000")

        if "_mat_" in str(row_id):
            raw_text = self.tree_guide.item(row_id, "text").replace("↳", "").strip()
            clean_name = raw_text.split("x ", 1)[-1].strip() if "x " in raw_text else raw_text
            menu.add_command(label=f"📦 Copy Material Name: {clean_name}",
                             command=lambda: self.copy_to_clipboard(clean_name, f"Copied '{clean_name}'"))

            raw_buy = self.tree_guide.set(row_id, "max_buy")
            clean_p = "".join(c for c in raw_buy if c.isdigit())
            if clean_p:
                menu.add_command(label=f"🎯 Copy Max Buy Price: {int(clean_p):,} gp",
                                 command=lambda: self.copy_to_clipboard(clean_p, f"Copied {int(clean_p):,} gp for {clean_name}"))

            raw_bid = self.tree_guide.set(row_id, "xp_ea")
            clean_bid = "".join(c for c in raw_bid if c.isdigit())
            if clean_bid and "Offer:" in raw_bid:
                menu.add_command(label=f"💰 Copy Target Offer (Bid): {int(clean_bid):,} gp",
                                 command=lambda: self.copy_to_clipboard(clean_bid, f"Copied {int(clean_bid):,} gp for {clean_name}"))

            raw_ask = self.tree_guide.set(row_id, "gp_xp")
            clean_ask = "".join(c for c in raw_ask if c.isdigit())
            if clean_ask and "Ask:" in raw_ask:
                menu.add_command(label=f"⚡ Copy Instant Buy (Ask): {int(clean_ask):,} gp",
                                 command=lambda: self.copy_to_clipboard(clean_ask, f"Copied {int(clean_ask):,} gp for {clean_name}"))

            raw_qty = self.tree_guide.set(row_id, "needed")
            clean_qty = "".join(c for c in raw_qty if c.isdigit())
            if clean_qty:
                menu.add_command(label=f"📋 Copy Total Quantity: {int(clean_qty):,}x",
                                 command=lambda: self.copy_to_clipboard(clean_qty, f"Copied {int(clean_qty):,} for {clean_name}"))

            menu.post(event.x_root, event.y_root)
            return

        row = next((r for r in self.guide_rows if r["id"] == row_id), None)
        if not row:
            return

        menu.add_command(label=f"💰 Inspect Custom Sale Price ({row['name']})", command=lambda n=row['name']: self.load_item_into_inspector(n))
        menu.add_command(label=f"🛒 Add Training Batch to Cart ({row['needed']:,} units)", command=self.add_guide_batch_to_cart)
        p_buy = row.get("target_buy_p", 0) or row.get("breakeven_ea", 0)
        if p_buy > 0:
            mat_n = row.get("primary_mat_name", "materials")
            menu.add_command(label=f"🎯 Copy Max Buy Price ({p_buy:,} gp for {mat_n})",
                             command=lambda pb=p_buy, mn=mat_n: self.copy_to_clipboard(str(pb), f"Copied {pb:,} gp for {mn}!"))
        tot_qty = row.get("tot_mat_qty", 0)
        if tot_qty > 0:
            mat_n = row.get("primary_mat_name", "materials")
            menu.add_command(label=f"📦 Copy Total Material Qty ({tot_qty:,}x {mat_n})",
                             command=lambda tq=tot_qty, mn=mat_n: self.copy_to_clipboard(str(tq), f"Copied {tq:,} for {mn}!"))
        menu.add_separator()
        menu.add_command(label="📋 Copy Shopping List for this Step", command=self.copy_guide_shopping_list)
        menu.add_command(label="🏷️ Copy RuneLite Bank Tag Tab", command=self.copy_guide_bank_tag)
        menu.add_command(label=f"📋 Copy Method Name ('{row['name']}')", command=lambda: self.copy_to_clipboard(row["name"], f"Copied '{row['name']}'!"))
        if row.get("output_id", 0) > 0:
            menu.add_separator()
            menu.add_command(label="🌐 Open in OSRS Wiki Prices", command=lambda: self.open_wiki_url(row["output_id"]))
        elif row.get("wiki_slug"):
            menu.add_separator()
            menu.add_command(label="🌐 Open Quest Guide on OSRS Wiki", command=lambda: webbrowser.open(f"https://oldschool.runescape.wiki/w/{row['wiki_slug']}"))
        menu.post(event.x_root, event.y_root)

    def add_guide_batch_to_cart(self):
        row = self.get_selected_guide_row()
        if not row:
            row = next((r for r in self.guide_rows if "YOU ARE HERE" in r.get("status", "")), None)
        if not row or (row.get("output_id", 0) == 0 and not row.get("materials_raw")):
            row = next((r for r in self.guide_rows if r.get("materials_raw") or r.get("output_id", 0) > 0), None)
        if not row:
            return

        needed_actions = max(1, row.get("needed", 100))
        mats = row.get("materials_raw", [])
        if mats:
            primary_mat = mats[0]
            mat_id = str(primary_mat["id"])
            total_needed = primary_mat["qty"] * needed_actions
            mdata = self.api.mapping.get(mat_id, {})
            base_limit = mdata.get("limit", 10000)
            batch_qty = min(total_needed, base_limit)

            self.state.cart_items[mat_id] = batch_qty
            self.recalculate_alch_table()
            self.update_cart_display()
            self.lbl_status_right.config(text=f"🛒 Added {batch_qty:,}x {primary_mat['name']} to cart for {row['name']}", fg="#2ecc71")
        elif row.get("output_id", 0) > 0:
            item_id = str(row["output_id"])
            mdata = self.api.mapping.get(item_id, {})
            base_limit = mdata.get("limit", 70)
            batch_qty = min(needed_actions, base_limit)
            self.state.cart_items[item_id] = batch_qty
            self.recalculate_alch_table()
            self.update_cart_display()
            self.lbl_status_right.config(text=f"🛒 Added {batch_qty:,}x {row['name']} to cart", fg="#2ecc71")

    def copy_guide_shopping_list(self):
        row = self.get_selected_guide_row()
        if not row:
            row = next((r for r in self.guide_rows if "YOU ARE HERE" in r.get("status", "")), None)
        if not row or (row.get("output_id", 0) == 0 and not row.get("materials_raw")):
            row = next((r for r in self.guide_rows if r.get("materials_raw") or r.get("output_id", 0) > 0), None)
        if not row:
            return

        needed_units = max(1, row["needed"]) if row["needed"] > 0 else 100
        lines = [
            f"========================================",
            f"🎓 OSRS SKILLING SHOPPING LIST: {self.var_guide_skill.get()}",
            f"Method: {row['name']}",
            f"Level Bracket: {row['level_range']}",
            f"Actions Required: {needed_units:,} units",
            f"----------------------------------------",
            f"Required Materials:"
        ]
        total_mat_cost = 0
        strat = self.var_strat.get().split()[0] if hasattr(self, "var_strat") else "smart"
        for m in row.get("materials_raw", []):
            p = self.api.get_price(m["id"], strat)
            tot_qty = m["qty"] * needed_units
            sub = p * tot_qty
            total_mat_cost += sub
            lines.append(f"  • {tot_qty:,}x {m['name']} (~{format_gp(sub)})")

        if row.get("nature_cost", 0) > 0 and row.get("action_rec") == "🪄 High Alch":
            nat_price = self.get_effective_nature_price()
            tot_nats = row["nature_cost"] * needed_units
            sub_nat = nat_price * tot_nats
            total_mat_cost += sub_nat
            lines.append(f"  • {tot_nats:,}x Nature rune (~{format_gp(sub_nat)})")

        if row.get("breakeven_ea", 0) > 0:
            lines.append(f"----------------------------------------")
            lines.append(f"🎯 Target GE Buy: {row['max_buy']} ea (for {row.get('primary_mat_name', 'materials')})")
            lines.append(f"   (Breakeven ceiling: ≤ {row['breakeven_ea']:,} gp ea)")

        lines.append(f"Total Est. Cost: {format_gp(total_mat_cost)}")
        lines.append(f"Disposal Strategy: {row['action_rec']}")
        lines.append(f"Net Est. Outcome: {row['bracket_cost']} ({row['gp_xp']})")
        lines.append(f"Est. Training Time: {row['time_est']} ({row['xp_rate']})")
        lines.append(f"========================================")

        text = "\n".join(lines)
        self.copy_to_clipboard(text, f"📋 Copied Skilling Shopping List for {row['name']}!")

    def copy_guide_bank_tag(self):
        row = self.get_selected_guide_row()
        if not row:
            row = next((r for r in self.guide_rows if "YOU ARE HERE" in r.get("status", "")), None)
        if not row or (row.get("output_id", 0) == 0 and not row.get("materials_raw")):
            row = next((r for r in self.guide_rows if r.get("materials_raw") or r.get("output_id", 0) > 0), None)
        if not row:
            return

        skill_tag = self.var_guide_skill.get().lower()[:5]
        bracket_tag = row['level_range'].replace(' ', '').replace('-', '_')
        tag_name = f"{skill_tag}_{bracket_tag}"

        item_ids = []
        for m in row.get("materials_raw", []):
            item_ids.append(str(m["id"]))
        if row.get("output_id", 0) > 0:
            item_ids.append(str(row["output_id"]))
        if row.get("nature_cost", 0) > 0:
            item_ids.append("561")

        if not item_ids:
            self.lbl_status_right.config(text=f"No item IDs associated with this step.", fg="#f1c40f")
            return

        icon_id = item_ids[0]
        tag_str = f"banktags,1,{tag_name},{icon_id}," + ",".join(item_ids)
        self.copy_to_clipboard(tag_str, f"📋 Copied RuneLite Bank Tag tab '{tag_name}' to clipboard!")
        messagebox.showinfo("Bank Tag Copied",
            f"Successfully copied Bank Tag tab '{tag_name}' to clipboard!\n\n"
            f"Items included: {len(item_ids)}\n"
            "In RuneLite, right-click the '+' tab icon in your bank and click 'Import tag tab'.")

    def get_guide_row_tooltip(self, row_id):
        if row_id == "fletch_p2p_warn":
            return {
                "title": "🔒 Members-Only Skill",
                "subtitle": "Fletching",
                "title_color": "#e74c3c",
                "rows": [
                    ("Restriction:", "Members Only", "#e74c3c"),
                    ("How to Train:", "Enable P2P Methods checkbox", "#3498db")
                ],
                "warnings": ["Fletching cannot be trained on Free-to-play worlds."],
                "has_warning": True,
                "hint": "Check 'P2P Methods' at the top to unlock Fletching guides."
            }

        if "_mat_" in str(row_id):
            raw_text = self.tree_guide.item(row_id, "text").replace("↳", "").strip()
            clean_name = raw_text.split("x ", 1)[-1].strip() if "x " in raw_text else raw_text
            max_buy_val = self.tree_guide.set(row_id, "max_buy")
            tot_val = self.tree_guide.set(row_id, "tot_mats")
            cost_val = self.tree_guide.set(row_id, "bracket_cost")
            offer_val = self.tree_guide.set(row_id, "xp_ea").replace("Offer: ", "")
            ask_val = self.tree_guide.set(row_id, "gp_xp").replace("Ask: ", "")
            return {
                "title": f"📦 Ingredient: {clean_name}",
                "subtitle": "Raw Material Requirement",
                "title_color": "#f39c12",
                "rows": [
                    ("Total Quantity Needed:", tot_val, "#f1c40f"),
                    ("🎯 Target Buy Ceiling:", max_buy_val, "#2ecc71"),
                    ("Current GE Offer (Bid):", f"{offer_val} gp" if offer_val != "--" else "--", "#3498db"),
                    ("Current Instant Buy (Ask):", f"{ask_val} gp" if ask_val != "--" else "--", "#e67e22"),
                    ("Total Batch Cost:", cost_val.replace("Cost: ", ""), "#f1f1f1"),
                ],
                "warnings": [f"Buy at or below {max_buy_val} to preserve target training margin."],
                "has_warning": False,
                "hint": "💡 Click cell to copy price or quantity directly to clipboard!"
            }

        row = next((r for r in self.guide_rows if str(r.get("id")) == str(row_id)), None)
        if not row:
            return None

        is_here = "HERE" in row.get("status", "")
        title_col = "#f1c40f" if is_here else ("#2ecc71" if "profit" in row.get("tag", "") else "#3498db")

        rows = [
            ("Current Status:", row.get("status", "--"), "#f1c40f" if is_here else "#cccccc"),
            ("Level Range:", f"Levels {row.get('level_range', '--')}", "#f1f1f1"),
            ("XP per Action:", f"{row.get('xp_ea', 0):,.1f} XP" if row.get("xp_ea", 0) % 1 else f"{int(row.get('xp_ea', 0)):,} XP", "#3498db"),
            ("Units Needed:", f"{row.get('needed', 0):,} units", "#f1f1f1"),
            ("Total Materials:", row.get("tot_mats", "--"), "#e67e22" if row.get("tot_mat_qty", 0) > 0 else "#888888"),
        ]

        if row.get("breakeven_ea", 0) > 0:
            rows.append(("Target GE Buy Price:", row.get("max_buy", "--"), "#2ecc71"))
            rows.append(("Breakeven Ceiling:", f"≤ {row['breakeven_ea']:,} gp ea", "#f1c40f"))
            if row.get("curr_mat_price", 0) > 0:
                rows.append(("Current Market Price:", f"{row['curr_mat_price']:,} gp ea", "#cccccc"))
                m_ea = row.get("margin_ea", 0)
                m_col = "#2ecc71" if m_ea >= 0 else "#e74c3c"
                rows.append(("Margin at Market:", f"{m_ea:+,} gp ea", m_col))

        if row.get("diff_vs_bar") is not None:
            c_prof = row.get("chain_profit", 0)
            d_bar = row.get("diff_vs_bar", 0)
            rows.append(("Chain Net Profit (from Ores):", f"{c_prof:+,} gp", "#2ecc71" if c_prof >= 0 else "#e74c3c"))
            rows.append(("Comparison vs Selling Bars on GE:", f"{d_bar:+,} gp", "#2ecc71" if d_bar >= 0 else ("#f1c40f" if c_prof > 0 else "#e74c3c")))

        rows.extend([
            ("Live GP / XP:", row.get("gp_xp", "--"), "#2ecc71" if "+" in row.get("gp_xp", "") else ("#f1c40f" if "-0." in row.get("gp_xp", "") else "#e74c3c")),
            ("Net Profit / Loss:", row.get("bracket_cost", "--"), "#2ecc71" if "+" in row.get("bracket_cost", "") else "#e74c3c"),
            ("Disposal Strategy:", row.get("action_rec", "--"), "#3498db"),
            ("XP Rate / Hour:", row.get("xp_rate", "--"), "#f1f1f1"),
            ("Est. Grind Time:", row.get("time_est", "--"), "#f1c40f"),
        ])

        cycle = row.get("cycle")
        if cycle:
            c_sec = cycle.get("cycle_secs", 0)
            w_sec = cycle.get("walk_secs", 0)
            b_sec = cycle.get("bank_secs", 0)
            a_sec = cycle.get("action_secs", 0)
            st_name = cycle.get("station_name", "Station")
            w_desc = cycle.get("walk_desc", "")
            rows.append(("Physical Loop:", f"~{c_sec:.1f}s/trip ({a_sec:.1f}s anim + {w_sec:.1f}s walk + {b_sec:.1f}s bank)", "#00e5ff"))
            rows.append(("Location & Route:", f"{st_name} ({w_desc})", "#aaaaaa"))

        prog = row.get("prog")
        if prog:
            rows.append(("Trips to Next Level:", f"~{prog.get('trips_next', 0)} inv ({prog.get('actions_next', 0):,} actions)", "#2ecc71"))
            rows.append(("Est. Time Till Next:", f"{prog.get('time_str_next', '--')}", "#f1c40f"))

        warnings = []
        if row.get("verdict"):
            warnings.append(row["verdict"])

        return {
            "title": f"🎓 {row['name']}",
            "subtitle": f"Lvl {row.get('level_range', '')} ({self.var_guide_skill.get()})",
            "title_color": title_col,
            "rows": rows,
            "warnings": warnings,
            "has_warning": bool("loss" in row.get("tag", "") or "Loss" in row.get("bracket_cost", "")),
            "hint": "💡 Click 'Total Mats' for quantity | Click 'Max Buy' for price | Right-click for Shopping List & Bank Tag"
        }

    def toggle_sort_guide(self, col):
        if getattr(self, "guide_sort_col", "") == col:
            self.guide_sort_asc = not self.guide_sort_asc
        else:
            self.guide_sort_col = col
            self.guide_sort_asc = True

        arrow = " ▼" if not self.guide_sort_asc else " ▲"
        headers = {
            "name": ("#0", "Training Method (▶ Expand)"),
            "status": ("status", "Status"),
            "level_range": ("level_range", "Level Range"),
            "materials": ("materials", "Materials (ea)"),
            "tot_mats": ("tot_mats", "Total Mats Needed"),
            "needed": ("needed", "Units Needed"),
            "max_buy": ("max_buy", "🎯 Max Mat Buy"),
            "xp_ea": ("xp_ea", "XP / Act"),
            "gp_xp": ("gp_xp", "Live GP/XP"),
            "bracket_cost": ("bracket_cost", "Net Profit / Loss"),
            "action_rec": ("action_rec", "Best Disposal"),
            "xp_rate": ("xp_rate", "XP / Hour"),
            "time_est": ("time_est", "Est. Time"),
            "verdict": ("verdict", "Strategy Tips / Verdict")
        }
        for sort_k, (col_id, title) in headers.items():
            self.tree_guide.heading(col_id, text=title + (arrow if getattr(self, "guide_sort_col", "") == sort_k else ""))

        self.recalculate_guide_table()

    def get_all_inspector_item_names(self):
        items = set()
        for st in W308_STAPLES:
            items.add(st["name"])
        for r in CRAFTING_RECIPES:
            items.add(r["name"])
        for c in SMITHING_MATERIAL_CHAINS:
            for it in c["items"]:
                items.add(it["name"])
        for sk, sdata in SKILLING_GUIDES.items():
            for b in sdata.get("brackets", []):
                inm = b.get("item_name", "")
                if inm and "Quest" not in inm:
                    items.add(inm)
        staples_order = [s["name"] for s in W308_STAPLES]
        remaining = sorted(list(items - set(staples_order)))
        return staples_order + remaining

    def get_recipe_for_skilling_item(self, name):
        if not name:
            return None
        clean_n = name.replace("▶", "").replace("▼", "").replace("↳", "").strip()
        if "x " in clean_n and clean_n[:3].replace("x", "").strip().isdigit():
            clean_n = clean_n.split("x ", 1)[-1].strip()
        base_n = clean_n.split("(")[0].strip()

        for r in CRAFTING_RECIPES:
            if r["name"].lower() in (clean_n.lower(), base_n.lower()):
                return {
                    "name": r["name"],
                    "output_id": r["output_id"],
                    "skill": "Crafting",
                    "xp": r.get("xp", 100.0),
                    "materials": r["materials"],
                    "members": r.get("members", False)
                }

        for c in SMITHING_MATERIAL_CHAINS:
            bar_id = c["bar_id"]
            bar_name = c["bar_name"]
            for it in c["items"]:
                if it["name"].lower() in (clean_n.lower(), base_n.lower()):
                    return {
                        "name": it["name"],
                        "output_id": it["id"],
                        "skill": "Smithing",
                        "xp": it["xp"],
                        "materials": [{"id": bar_id, "name": bar_name, "qty": it["bars"]}],
                        "members": it.get("members", False)
                    }

        for sk, sdata in SKILLING_GUIDES.items():
            for b in sdata.get("brackets", []):
                b_name = b.get("item_name", "") or b.get("name", "")
                if b_name.lower() in (clean_n.lower(), base_n.lower()):
                    return {
                        "name": b_name,
                        "output_id": b.get("output_id", 0),
                        "skill": sk,
                        "xp": b.get("xp_per_action", 50.0),
                        "materials": b.get("materials", []),
                        "members": b.get("members", False)
                    }

        st = next((s for s in W308_STAPLES if s["name"].lower() in (clean_n.lower(), base_n.lower())), None)
        if st:
            return {
                "name": st["name"],
                "output_id": st["id"],
                "skill": "Skilling",
                "xp": 100.0,
                "materials": [],
                "members": st.get("members", False)
            }
        return None

    def toggle_guide_inspector(self):
        self.guide_inspector_visible = not getattr(self, "guide_inspector_visible", True)
        if self.guide_inspector_visible:
            self.frame_guide_inspector.pack(fill="x", pady=(0, 4), before=self.frame_guide_quests)
            self.btn_toggle_guide_inspector.config(text="💰 Sale Price Inspector ▴")
            self.calculate_guide_inspector()
        else:
            self.frame_guide_inspector.pack_forget()
            self.btn_toggle_guide_inspector.config(text="💰 Sale Price Inspector ▾")

    def on_insp_item_selected(self, event=None):
        item_name = self.var_insp_item.get()
        recipe = self.get_recipe_for_skilling_item(item_name)
        if not recipe:
            return

        out_id = recipe["output_id"]
        st = next((s for s in W308_STAPLES if s["id"] == out_id or s["name"].lower() == item_name.lower()), None)
        ge_sell = self.api.get_price(out_id, "instasell") or 0
        ge_net = math.floor(ge_sell * 0.99) if ge_sell > 0 else 0
        alch_val = self.api.mapping.get(str(out_id), {}).get("highalch", 0)
        alch_net = max(0, alch_val - self.get_effective_nature_price())

        suggested_price = st["w308_buy"] if st else (ge_net if ge_net > 0 else alch_net)
        if suggested_price > 0:
            self.ent_insp_price.delete(0, tk.END)
            self.ent_insp_price.insert(0, str(suggested_price))

        self.calculate_guide_inspector()

    def calculate_guide_inspector(self, event=None):
        if not hasattr(self, "lbl_insp_mat_cost"):
            return
        item_name = self.var_insp_item.get()
        recipe = self.get_recipe_for_skilling_item(item_name)
        if not recipe:
            self.lbl_insp_materials.config(text=f"No recipe found for '{item_name}'")
            return

        try:
            sell_price = int(self.ent_insp_price.get().strip().replace(",", ""))
        except Exception:
            sell_price = 0

        try:
            qty = int(self.ent_insp_qty.get().strip().replace(",", ""))
        except Exception:
            qty = 1000
        if qty <= 0:
            qty = 1

        out_id = recipe["output_id"]
        strat = self.var_strat.get().split()[0] if hasattr(self, "var_strat") else "smart"

        mat_cost_ea = 0
        mat_parts = []
        for m in recipe["materials"]:
            p = self.api.get_price(m["id"], strat) or 100
            mat_cost_ea += p * m["qty"]
            mat_parts.append(f"{m['qty']}x {m['name']} (@ {p:,})")

        rec_str = " + ".join(mat_parts) if mat_parts else "Raw materials / Base item"
        self.lbl_insp_materials.config(text=f"Recipe: {rec_str}")
        self.lbl_insp_mat_cost.config(text=f"Live Mat Cost: {mat_cost_ea:,} gp")

        ge_sell = self.api.get_price(out_id, "instasell") or 0
        ge_net = math.floor(ge_sell * 0.99) if ge_sell > 0 else 0
        self.lbl_insp_ge_sell.config(text=f"GE Instant Net: {ge_net:,} gp" if ge_net > 0 else "GE Instant Net: --")

        alch_val = self.api.mapping.get(str(out_id), {}).get("highalch", 0)
        alch_net = max(0, alch_val - self.get_effective_nature_price()) if alch_val > 0 else 0
        self.lbl_insp_alch_net.config(text=f"High Alch Net: {alch_net:,} gp" if alch_net > 0 else "High Alch Net: --")

        st = next((s for s in W308_STAPLES if s["id"] == out_id or s["name"].lower() == item_name.lower()), None)
        w308_p = st["w308_buy"] if st else 0
        self.lbl_insp_w308.config(text=f"Bulk Benchmark: {w308_p:,} gp" if w308_p > 0 else "Bulk Benchmark: None")

        profit_ea = sell_price - mat_cost_ea
        batch_profit = profit_ea * qty
        xp_ea = recipe["xp"]
        gp_xp = (profit_ea / xp_ea) if xp_ea > 0 else 0.0

        if profit_ea > 0:
            p_col = "#2ecc71"
            self.lbl_insp_profit_ea.config(text=f"Profit / Ea: +{profit_ea:,} gp", fg=p_col)
            self.lbl_insp_batch_profit.config(text=f"Batch Profit: +{format_gp(batch_profit)}", fg=p_col)
            self.lbl_insp_gpxp.config(text=f"GP / XP: +{gp_xp:.2f} (Profitable!)", fg=p_col)
            comp_text = f"⭐ Profitable Training! Selling at {sell_price:,} gp nets +{profit_ea:,} gp profit/ea over material costs (+{format_gp(batch_profit)} total)!"
        elif profit_ea == 0:
            p_col = "#f1c40f"
            self.lbl_insp_profit_ea.config(text="Breakeven (0 gp)", fg=p_col)
            self.lbl_insp_batch_profit.config(text="Batch Profit: 0 gp", fg=p_col)
            self.lbl_insp_gpxp.config(text="GP / XP: FREE (0.00)", fg=p_col)
            comp_text = f"⚖️ 100% Free Training! Training {recipe['skill']} completely free of cost (Breakeven sell price)!"
        else:
            loss_ea = abs(profit_ea)
            loss_batch = abs(batch_profit)
            p_col = "#f39c12" if abs(gp_xp) <= 3.0 else "#e74c3c"
            self.lbl_insp_profit_ea.config(text=f"Profit / Ea: -{loss_ea:,} gp", fg=p_col)
            self.lbl_insp_batch_profit.config(text=f"Batch Profit: -{format_gp(loss_batch)}", fg=p_col)
            tier_str = "Subsidized XP" if abs(gp_xp) <= 3.0 else "Costly XP"
            self.lbl_insp_gpxp.config(text=f"GP / XP: {gp_xp:.2f} ({tier_str})", fg=p_col)
            comp_text = f"⚡ Training Cost: Selling at {sell_price:,} gp costs {loss_ea:,} gp/ea to gain {xp_ea:.1f} XP ({abs(gp_xp):.2f} GP/XP)."

        diff_vs_ge = sell_price - ge_net if ge_net > 0 else 0
        if ge_net > 0 and diff_vs_ge > 0:
            comp_text += f" (Beats GE instant sell by +{diff_vs_ge:,} gp/ea — saves 1% tax & 4h limit!)"
        elif ge_net > 0 and diff_vs_ge < 0:
            comp_text += f" (GE instant net is {abs(diff_vs_ge):,} gp higher: {ge_net:,} gp)"

        self.lbl_insp_breakeven.config(text=f"Breakeven Mat: ≤ {sell_price:,} gp")
        self.lbl_insp_comparison.config(text=comp_text)

    def set_insp_qty(self, val):
        if val == -1:
            cash = self.get_current_cash_stack()
            item_name = self.var_insp_item.get()
            recipe = self.get_recipe_for_skilling_item(item_name)
            strat = self.var_strat.get().split()[0] if hasattr(self, "var_strat") else "smart"
            mat_cost_ea = 0
            if recipe and recipe.get("materials"):
                for m in recipe["materials"]:
                    p = self.api.get_price(m["id"], strat) or 100
                    mat_cost_ea += p * m["qty"]
            target_qty = (cash // mat_cost_ea) if mat_cost_ea > 0 else 100
            val = max(1, target_qty)
        self.ent_insp_qty.delete(0, tk.END)
        self.ent_insp_qty.insert(0, str(val))
        self.calculate_guide_inspector()

    def load_item_into_inspector(self, name):
        recipe = self.get_recipe_for_skilling_item(name)
        if not recipe:
            return
        if not getattr(self, "guide_inspector_visible", True):
            self.toggle_guide_inspector()
        self.var_insp_item.set(recipe["name"])
        self.on_insp_item_selected()

    def add_insp_materials_to_cart(self):
        item_name = self.var_insp_item.get()
        recipe = self.get_recipe_for_skilling_item(item_name)
        if not recipe or not recipe.get("materials"):
            FloatingToast(self, "No Recipe", f"No raw ingredients registered for '{item_name}'.", 3000)
            return
        try:
            qty = int(self.ent_insp_qty.get().strip().replace(",", ""))
        except Exception:
            qty = 1000
        added_parts = []
        for m in recipe["materials"]:
            mid_str = str(m["id"])
            mdata = self.api.mapping.get(mid_str, {})
            tot_req = m["qty"] * qty
            limit = mdata.get("limit", 10000) or 10000
            batch_amt = min(tot_req, limit)
            self.state.cart_items[mid_str] = batch_amt
            added_parts.append(f"{batch_amt:,}x {m['name']}")
        self.recalculate_alch_table()
        self.update_cart_display()
        FloatingToast(self, "🛒 Materials Added", f"Added materials for {qty:,}x {recipe['name']}:\n" + ", ".join(added_parts), 4000)

    def load_insp_into_w308(self):
        item_name = self.var_insp_item.get()
        recipe = self.get_recipe_for_skilling_item(item_name)
        st = next((s for s in W308_STAPLES if s["name"].lower() == item_name.lower()), None)
        if not st and recipe:
            st = next((s for s in W308_STAPLES if s["id"] == recipe.get("output_id", 0)), None)

        try:
            price = int(self.ent_insp_price.get().strip().replace(",", ""))
        except Exception:
            price = 0
        try:
            qty = int(self.ent_insp_qty.get().strip().replace(",", ""))
        except Exception:
            qty = 1000

        self.notebook.select(self.tab_hub_alch)
        self.switch_alch_subview("w308")

        if st:
            self.var_w308_item.set(st["name"])
            self.ent_w308_price.delete(0, tk.END)
            self.ent_w308_price.insert(0, str(price if price > 0 else st["w308_buy"]))
            self.ent_w308_qty.delete(0, tk.END)
            self.ent_w308_qty.insert(0, str(qty if qty > 0 else 100))
            self.calculate_w308_trade_validator()
            FloatingToast(self, "W308 Hub Loaded", f"Transferred {st['name']} ({qty:,} units @ {price:,} gp) into W308 Bulk Validator!", 3000)
        else:
            FloatingToast(self, "W308 Hub", f"Switched to W308 Hub! (Note: '{item_name}' is not in standard W308 trade staples).", 3000)

    def copy_insp_trade_ad(self):
        item_name = self.var_insp_item.get()
        recipe = self.get_recipe_for_skilling_item(item_name)
        st = next((s for s in W308_STAPLES if s["name"].lower() == item_name.lower()), None)
        short_name = st["short"] if st else item_name
        try:
            qty = int(self.ent_insp_qty.get().strip().replace(",", ""))
        except Exception:
            qty = 1000
        try:
            price = int(self.ent_insp_price.get().strip().replace(",", ""))
        except Exception:
            price = 0
        p_str = f"{price / 1000:.1f}k" if price % 1000 != 0 else f"{price // 1000}k" if price >= 1000 else f"{price} gp"
        ad_str = f"Selling {qty:,} {short_name} {p_str} ea Bulk - Trade Me" if qty > 0 else f"Selling {short_name} {p_str} ea Bulk - Trade Me"
        self.copy_to_clipboard(ad_str, f"Copied custom selling ad: '{ad_str}'")

    def build_timers_tab(self):
        container = ttk.Frame(self.tab_timers)
        container.pack(fill="both", expand=True, padx=10, pady=10)

        top_info = tk.Label(container, text="Active 4-Hour GE Buy Limit Watchlist. Alerts you when 4h expires!",
                            fg="#cccccc", bg="#1e1e1e", font=("Segoe UI", 9, "italic"))
        top_info.pack(anchor="w", pady=(0, 6))

        cols = ("account", "item", "qty", "time_left", "status")
        self.tree_timers = ttk.Treeview(container, columns=cols, show="headings", height=12)

        self.tree_timers.heading("account", text="Account")
        self.tree_timers.heading("item", text="Item Name")
        self.tree_timers.heading("qty", text="Quantity Bought")
        self.tree_timers.heading("time_left", text="Time Remaining")
        self.tree_timers.heading("status", text="Status")

        self.tree_timers.column("account", width=120, anchor="center")
        self.tree_timers.column("item", width=220, anchor="w")
        self.tree_timers.column("qty", width=120, anchor="center")
        self.tree_timers.column("time_left", width=140, anchor="center")
        self.tree_timers.column("status", width=160, anchor="center")

        self.tree_timers.pack(fill="both", expand=True)

        timers_col_tooltips = {
            "#1": "Account:\nIn-game character name for this 4-hour cooldown timer.",
            "#2": "Item Name:\nItem currently on 4-hour Grand Exchange buy limit cooldown.",
            "#3": "Quantity Bought:\nNumber of units purchased in this 4-hour limit window.",
            "#4": "Time Remaining:\nCount down until the 4-hour Grand Exchange limit completely resets.",
            "#5": "Status:\nShows whether cooldown is actively ticking or ready to purchase again."
        }
        HeadingToolTip(self.tree_timers, timers_col_tooltips)

        btn_bar = tk.Frame(container, bg="#1e1e1e")
        btn_bar.pack(fill="x", pady=6)

        btn_edit_timer = tk.Button(btn_bar, text="✏️ Edit Quantity Bought", command=self.edit_selected_timer,
                                   bg="#f39c12", fg="#000000", font=("Segoe UI", 8, "bold"), relief="flat", padx=8, pady=4, cursor="hand2")
        btn_edit_timer.pack(side="left")
        ToolTip(btn_edit_timer, "Edit Quantity Bought:\nAdjust the purchased amount for this 4h cooldown timer.")

        btn_reset_all = tk.Button(btn_bar, text="⚡ Reset All Timers", command=self.reset_all_timers,
                                  bg="#d35400", fg="#ffffff", font=("Segoe UI", 8, "bold"), relief="flat", padx=8, pady=4, cursor="hand2")
        btn_reset_all.pack(side="left", padx=6)
        ToolTip(btn_reset_all, "Reset All Timers:\n1-click reset to clear active 4h GE cooldown timers.")

        btn_ge_sync_timers = tk.Button(btn_bar, text="🔄 Sync with GE", command=self.manual_ge_sync,
                                       bg="#2980b9", fg="#ffffff", font=("Segoe UI", 8, "bold"), relief="flat", padx=8, pady=4, cursor="hand2")
        btn_ge_sync_timers.pack(side="left", padx=6)
        ToolTip(btn_ge_sync_timers, "Sync with GE:\nAuthoritatively fetch live 4-hour buy limits and trades directly from RuneLite.")

        btn_del = tk.Button(btn_bar, text="🗑️ Remove Selected Timer", command=self.remove_selected_timer,
                            bg="#c0392b", fg="#ffffff", relief="flat", padx=8, pady=4, cursor="hand2")
        btn_del.pack(side="right")
        ToolTip(btn_del, "Remove selected item cooldown timer from active watchlist.")

        self.tree_timers.bind("<Double-1>", lambda e: self.edit_selected_timer())

    def build_session_tab(self):
        container = ttk.Frame(self.tab_session)
        container.pack(fill="both", expand=True, padx=15, pady=15)

        cards_frame = tk.Frame(container, bg="#1e1e1e")
        cards_frame.pack(fill="x", pady=(0, 15))

        self.card_alchs = self.create_stat_card(cards_frame, "Total Casts Done", "0", "#3498db", "Total High Alchemy casts completed during this session.")
        self.card_profit = self.create_stat_card(cards_frame, "Realized Profit", "0 gp", "#2ecc71", "Total net profit realized across all logged alch batches.")
        self.card_xp = self.create_stat_card(cards_frame, "Magic XP Gained", "0 XP", "#9b59b6", "Total Magic experience gained (65 XP per High Alchemy cast).")
        self.card_nats = self.create_stat_card(cards_frame, "Natures Used", "0", "#f39c12", "Total Nature Runes consumed during this session.")

        # Top of History table with Action Buttons & View Mode Switcher
        hist_bar = tk.Frame(container, bg="#1e1e1e")
        hist_bar.pack(fill="x", pady=(5, 4))

        lbl_hist = tk.Label(hist_bar, text="Session Ledger:", font=("Segoe UI", 10, "bold"), fg="#f39c12", bg="#1e1e1e")
        lbl_hist.pack(side="left")

        # View Mode Switcher Pills
        self.btn_view_consolidated = tk.Button(hist_bar, text="📦 Consolidated Daily View",
                                               command=lambda: self.set_session_view_mode("consolidated"),
                                               relief="flat", padx=10, pady=2, font=("Segoe UI", 8, "bold"), cursor="hand2")
        self.btn_view_consolidated.pack(side="left", padx=(12, 4))
        ToolTip(self.btn_view_consolidated, "Consolidate all purchases by day and item stack (e.g. 500 Rune platelegs total with weighted average buy price and daily P&L). Expand rows to audit individual fills.")

        self.btn_view_detailed = tk.Button(hist_bar, text="📜 Detailed Transactions",
                                           command=lambda: self.set_session_view_mode("detailed"),
                                           relief="flat", padx=10, pady=2, font=("Segoe UI", 8, "bold"), cursor="hand2")
        self.btn_view_detailed.pack(side="left", padx=4)
        ToolTip(self.btn_view_detailed, "View flat unbundled list of every individual transaction fill with full timestamps.")

        btn_edit = tk.Button(hist_bar, text="✏️ Edit Selected", command=self.open_edit_session_dialog,
                             bg="#f39c12", fg="#000000", font=("Segoe UI", 8, "bold"), relief="flat", padx=8, cursor="hand2")
        btn_edit.pack(side="right", padx=4)
        ToolTip(btn_edit, "Edit Selected Entry:\nManually adjust buy price, nature cost, or quantity if actual GE purchase differed.")

        btn_del = tk.Button(hist_bar, text="🗑️ Delete Entry", command=self.delete_session_entry,
                            bg="#c0392b", fg="#ffffff", font=("Segoe UI", 8), relief="flat", padx=8, cursor="hand2")
        btn_del.pack(side="right", padx=4)
        ToolTip(btn_del, "Delete Entry:\nRemove the selected transaction from your session history log.")

        cols = ("time", "account", "item", "qty", "buy_price", "nat_price", "alch_val", "profit")
        self.tree_session = ttk.Treeview(container, columns=cols, show="tree headings", height=10)

        self.tree_session.heading("#0", text="📅 Breakdown / Stack")
        self.tree_session.column("#0", width=230, anchor="w")

        self.tree_session.heading("time", text="Time", command=lambda: self.toggle_sort_session("time"))
        self.tree_session.heading("account", text="Account", command=lambda: self.toggle_sort_session("account"))
        self.tree_session.heading("item", text="Item Name", command=lambda: self.toggle_sort_session("item"))
        self.tree_session.heading("qty", text="Quantity", command=lambda: self.toggle_sort_session("qty"))
        self.tree_session.heading("buy_price", text="Bought At (ea)", command=lambda: self.toggle_sort_session("buy_price"))
        self.tree_session.heading("nat_price", text="Nat Cost (ea)", command=lambda: self.toggle_sort_session("nat_price"))
        self.tree_session.heading("alch_val", text="Alch Value (Fixed)", command=lambda: self.toggle_sort_session("alch_val"))
        self.tree_session.heading("profit", text="Realized Profit", command=lambda: self.toggle_sort_session("profit"))

        self.tree_session.column("time", width=85, anchor="center")
        self.tree_session.column("account", width=95, anchor="center")
        self.tree_session.column("item", width=180, anchor="w")
        self.tree_session.column("qty", width=85, anchor="center")
        self.tree_session.column("buy_price", width=105, anchor="e")
        self.tree_session.column("nat_price", width=95, anchor="e")
        self.tree_session.column("alch_val", width=105, anchor="e")
        self.tree_session.column("profit", width=130, anchor="e")

        self.tree_session.pack(fill="both", expand=True)
        self.tree_session.bind("<Double-1>", lambda e: self.open_edit_session_dialog())

        session_col_tooltips = {
            "#0": "Breakdown / Stack:\nHierarchical view showing Day -> Consolidated Stack -> Individual Fill transaction rows.",
            "#1": "Time / Count:\nTimestamp when batch was recorded or count of transaction fills in consolidated mode.",
            "#2": "Account:\nIn-game character name that bought/alched this batch.",
            "#3": "Item Name:\nName of the alched item.",
            "#4": "Quantity:\nTotal number of items alched in this batch or consolidated stack.",
            "#5": "Bought At (ea):\nGold price paid per item (or weighted average buy price in consolidated mode).",
            "#6": "Nat Cost (ea):\nPrice paid per Nature Rune (or weighted average cost).",
            "#7": "Alch Value (Fixed):\nFixed High Alchemy gold payout per item.",
            "#8": "Realized Profit:\nNet profit earned = (Alch Value - Buy Price - Nat Cost) * Quantity."
        }
        HeadingToolTip(self.tree_session, session_col_tooltips)
        self.update_session_view_buttons()

        session_btn_bar = tk.Frame(container, bg="#1e1e1e")
        session_btn_bar.pack(fill="x", pady=8)

        btn_ge_sync_sess = tk.Button(session_btn_bar, text="🔄 Sync with GE", command=self.manual_ge_sync,
                                     bg="#2980b9", fg="#ffffff", font=("Segoe UI", 8, "bold"), relief="flat", padx=10, pady=4, cursor="hand2")
        btn_ge_sync_sess.pack(side="left")
        ToolTip(btn_ge_sync_sess, "Sync with GE:\nImport any completed GE trades from RuneLite history into this session.")

        btn_reset = tk.Button(session_btn_bar, text="Reset Session", command=self.reset_session,
                              bg="#7f8c8d", fg="#ffffff", relief="flat", padx=10, pady=4, cursor="hand2")
        btn_reset.pack(side="right")
        ToolTip(btn_reset, "Reset Session:\nClears all session stats and history log back to zero.")

    def set_session_view_mode(self, mode):
        self.session_view_mode = mode
        self.state.config["session_view_mode"] = mode
        self.state.save_config()
        self.update_session_view_buttons()
        self.update_session_display()

    def update_session_view_buttons(self):
        if not hasattr(self, "btn_view_consolidated"):
            return
        if getattr(self, "session_view_mode", "consolidated") == "consolidated":
            self.btn_view_consolidated.config(bg="#f39c12", fg="#000000")
            self.btn_view_detailed.config(bg="#252528", fg="#cccccc")
        else:
            self.btn_view_consolidated.config(bg="#252528", fg="#cccccc")
            self.btn_view_detailed.config(bg="#f39c12", fg="#000000")

    def toggle_sort_session(self, col):
        if getattr(self, "session_sort_col", None) == col:
            self.session_sort_desc = not self.session_sort_desc
        else:
            self.session_sort_col = col
            self.session_sort_desc = True if col in ("qty", "buy_price", "nat_price", "alch_val", "profit", "time") else False
        self.update_session_headings()
        self.update_session_display()

    def update_session_headings(self):
        col_names = {
            "time": "Time",
            "account": "Account",
            "item": "Item Name",
            "qty": "Quantity",
            "buy_price": "Bought At (ea)",
            "nat_price": "Nat Cost (ea)",
            "alch_val": "Alch Value (Fixed)",
            "profit": "Realized Profit"
        }
        for col_id, base_text in col_names.items():
            if getattr(self, "session_sort_col", "time") == col_id:
                indicator = " ▼" if getattr(self, "session_sort_desc", True) else " ▲"
                self.tree_session.heading(col_id, text=f"{base_text}{indicator}")
            else:
                self.tree_session.heading(col_id, text=base_text)

    def create_stat_card(self, parent, title, initial_val, val_color, tooltip=""):
        card = tk.Frame(parent, bg="#252528", relief="solid", borderwidth=1, padx=14, pady=10)
        card.pack(side="left", expand=True, fill="both", padx=6)

        lbl_t = tk.Label(card, text=title, font=("Segoe UI", 9), fg="#aaaaaa", bg="#252528")
        lbl_t.pack(anchor="w")

        lbl_v = tk.Label(card, text=initial_val, font=("Segoe UI", 14, "bold"), fg=val_color, bg="#252528")
        lbl_v.pack(anchor="w", pady=(4, 0))
        if tooltip:
            ToolTip(card, tooltip)
            ToolTip(lbl_t, tooltip)
            ToolTip(lbl_v, tooltip)
        return lbl_v

    def build_alerts_tab(self):
        container = ttk.Frame(self.tab_alerts)
        container.pack(fill="both", expand=True, padx=10, pady=10)

        tk.Label(container, text="Recent High Margin Alerts (Only Fires on >=2 gp Shift):", font=("Segoe UI", 10, "bold"), fg="#f39c12", bg="#1e1e1e").pack(anchor="w", pady=(0, 6))

        self.lst_alerts = tk.Listbox(container, bg="#252528", fg="#f1f1f1", font=("Segoe UI", 10), selectbackground="#3e3e42", relief="flat", highlightthickness=0)
        self.lst_alerts.pack(fill="both", expand=True)
        ToolTip(self.lst_alerts, "Feed of real-time high margin price alerts detected while running.")

    def build_status_bar(self):
        self.lbl_status_left = tk.Label(self.status_bar, text="Initializing...", font=("Segoe UI", 8), fg="#888888", bg="#181818")
        self.lbl_status_left.pack(side="left", padx=10)

        self.lbl_status_right = tk.Label(self.status_bar, text="Ready", font=("Segoe UI", 8), fg="#888888", bg="#181818")
        self.lbl_status_right.pack(side="right", padx=10)

    # ------------------ LOGIC & HANDLERS ------------------

    def get_effective_nature_price(self):
        if self.var_free_alch.get():
            return 0
        custom = self.state.config.get("custom_nature_price", 0)
        if custom > 0:
            return custom
        return self.api.nature_rune_price

    def trigger_refresh(self):
        if self.is_fetching:
            return
        self.is_fetching = True
        self.btn_refresh.config(state="disabled", text="⏳ Syncing...")
        self.lbl_status_left.config(text="Syncing in-game state & fetching Wiki prices...")

        # 1. Immediately force sync from container export
        self._sync_from_container_export(force=True)
        self._apply_active_account_data(force=True)

        # 2. Request live account snapshot from RuneLite bridge
        if hasattr(self, "bridge_server") and self.bridge_server:
            self.bridge_server.request_resync()

        threading.Thread(target=self._worker_fetch, daemon=True).start()

    def _worker_fetch(self):
        try:
            if not self.api.mapping:
                self.api.load_mapping()
            self.api.fetch_latest_and_volumes()
        except Exception as e:
            print(f"Worker fetch error: {e}")

        try:
            self.after(0, self._on_fetch_complete)
        except Exception:
            pass

    def _on_fetch_complete(self):
        self.is_fetching = False
        self.btn_refresh.config(state="normal", text="🔄 Refresh Now")
        self.seconds_until_refresh = self.state.config.get("auto_refresh_mins", 2) * 60

        # Update Nature Rune labels
        bid = self.api.nature_rune_bid
        ask = self.api.nature_rune_ask
        self.lbl_nat_target.config(text=f"🎯 Offer: {bid} gp")
        self.lbl_nat_details.config(text=f"Ask: {ask} gp | Limit: 18,000")

        # Sync from container export and active account before recalculating
        self._sync_from_container_export(force=True)
        self._apply_active_account_data(force=True)

        # Authoritatively reconcile 4h timers and past trades from RuneLite profiles FIRST
        try:
            ge_res = self.state.sync_from_runelite_ge(self.api.mapping, self.get_effective_nature_price())
            if ge_res.get("timers_updated", 0) > 0 or ge_res.get("session_imported", 0) > 0:
                self.update_timers_display()
                self.update_session_display()
        except Exception:
            pass

        # Clean up any expired timers
        try:
            self.state.cleanup_expired_timers()
        except Exception:
            pass

        # Recalculate tables with latest limits, timers, and cash stack
        self.recalculate_all()

        # Check for alerts ONLY on fresh fetch!
        self._check_alerts_on_sync()

        sync_str = time.strftime("%H:%M:%S")
        self.lbl_status_left.config(text=f"Live Nature Rune: {self.get_effective_nature_price()} gp | Items Monitored: {len(self.api.latest_prices):,} | Last Sync: {sync_str}")

    def _check_alerts_on_sync(self):
        """Runs strictly when new API data arrives to avoid alert spam on UI interactions."""
        threshold = self.state.config.get("alert_threshold_alch", 200)
        min_vol = self.state.config.get("min_volume", 5000)

        alerts_fired = 0
        for row in self.alch_rows:
            iid = str(row["id"])
            profit = row["profit_ea"]
            vol = row["volume"]

            # Mute popup and sound alerts if item has reached its 4h GE buy limit!
            base_limit = row.get("base_limit", row.get("limit", 0))
            rem_limit, _, is_cd = self.state.get_remaining_limit(row["id"], base_limit)
            if is_cd and rem_limit <= 0:
                continue

            # Proper Sell Boundary:
            # Require at least min_alert_vol (3+) items sold in the 5m window to confirm a real selling market.
            # Avoids spamming alerts on 1-off freak single-sell dumps!
            min_alert_vol = self.state.config.get("min_alert_5m_vol", 3)
            v5 = self.api.volumes_5m.get(iid, {})
            vol_5m_low = v5.get("low", 0) or 0
            vol_5m_total = v5.get("total", 0) or 0
            if vol_5m_low < min_alert_vol and vol_5m_total < (min_alert_vol * 2):
                continue

            if profit >= threshold and vol >= min_vol:
                last_profit = self.state.last_alerted_profits.get(iid)
                # Only alert if brand new OR margin shifted by >= 2 gp
                if last_profit is None or abs(profit - last_profit) >= 2:
                    self.state.last_alerted_profits[iid] = profit
                    alert_msg = f"{row['name']} margin: +{profit:,} gp/ea ({row['profit_hr']/1000:.0f}k/hr) | 5m: {vol_5m_low} sold"
                    self.state.alert_history.insert(0, f"[{time.strftime('%H:%M:%S')}] 🚨 {alert_msg}")
                    self.state.alert_history = self.state.alert_history[:60]
                    self.update_alerts_display()
                    if alerts_fired < 2:
                        self.trigger_alert_notification(row['name'], f"+{profit:,} gp/ea (+{row['profit_hr']/1000:.0f}k/hr) | 5m: {vol_5m_low} sold", item_id=row["id"])
                        alerts_fired += 1

    # ------------------ GITHUB AUTO-UPDATER ------------------

    def _check_update_startup(self):
        try:
            has_up, remote_v, dl_url, notes = check_for_updates(APP_VERSION)
            if has_up:
                self.latest_update_info = (remote_v, dl_url, notes)
                try:
                    self.after(0, self._render_update_available)
                except Exception:
                    pass
        except Exception as e:
            print(f"Startup update check: {e}")
        finally:
            # Automatically re-checks GitHub every 30 minutes while running
            try:
                self.after(30 * 60 * 1000, lambda: threading.Thread(target=self._check_update_startup, daemon=True).start())
            except Exception:
                pass

    def _render_update_available(self):
        if self.latest_update_info:
            remote_v, _, _ = self.latest_update_info
            self.btn_update.config(
                text=f"✨ Update {remote_v}",
                bg="#27ae60",
                fg="#ffffff",
                font=("Segoe UI", 8, "bold")
            )
            self.lbl_status_right.config(text=f"Update {remote_v} available!", fg="#2ecc71")

    def on_update_button_click(self):
        if self.latest_update_info:
            remote_v, dl_url, notes = self.latest_update_info
            UpdateDialog(self, remote_v, dl_url, notes)
        else:
            self.btn_update.config(text="Checking...", state="disabled")
            def worker():
                try:
                    has_up, remote_v, dl_url, notes = check_for_updates(APP_VERSION)
                    self.after(0, lambda: self._on_manual_check_done(has_up, remote_v, dl_url, notes))
                except Exception as e:
                    self.after(0, lambda: self._on_manual_check_done(False, APP_VERSION, None, str(e)))
            threading.Thread(target=worker, daemon=True).start()

    def _on_manual_check_done(self, has_up, remote_v, dl_url, notes):
        self.btn_update.config(state="normal")
        if has_up:
            self.latest_update_info = (remote_v, dl_url, notes)
            self._render_update_available()
            UpdateDialog(self, remote_v, dl_url, notes)
        else:
            self.btn_update.config(text=f"v{APP_VERSION}", bg="#2d2d30", fg="#888888")
            messagebox.showinfo("Up to Date", f"You are running the latest version (v{APP_VERSION})!")

    def _check_first_run_after_update(self):
        last_v = self.state.config.get("last_seen_version")
        if last_v is None:
            # Initial setup: mark current version
            self.state.config["last_seen_version"] = APP_VERSION
            self.state.save_config()
        elif last_v != APP_VERSION:
            # App was just updated! Show "What's New" modal
            self.state.config["last_seen_version"] = APP_VERSION
            self.state.save_config()
            WhatsNewDialog(self, APP_VERSION)

    def on_app_close(self):
        if self.latest_update_info:
            remote_v, dl_url, notes = self.latest_update_info
            ans = messagebox.askyesnocancel(
                "Update Available",
                f"A new version ({remote_v}) is ready to install!\n\n"
                f"Would you like to install the update now before exiting?\n\n"
                f"• Click YES to update & restart into {remote_v}\n"
                f"• Click NO to exit without updating\n"
                f"• Click CANCEL to stay in the app"
            )
            if ans is True:
                UpdateDialog(self, remote_v, dl_url, notes)
                return
            elif ans is False:
                if hasattr(self, "bridge_server") and self.bridge_server:
                    self.bridge_server.stop()
                self.destroy()
                return
            else:
                return # Cancelled, stay in app
        if hasattr(self, "bridge_server") and self.bridge_server:
            self.bridge_server.stop()
        self.destroy()

    def update_owned_nat_display(self):
        if hasattr(self, "ent_owned_nat"):
            self.ent_owned_nat.delete(0, tk.END)
            owned = self.state.config.get("owned_nature_runes", 0)
            if owned > 0:
                self.ent_owned_nat.insert(0, str(owned))

    def recalculate_all(self):
        self.recalculate_alch_table()
        self.recalculate_rec_table()
        if hasattr(self, "recalculate_overnight_table"):
            self.recalculate_overnight_table()
        if hasattr(self, "recalculate_w308_table"):
            self.recalculate_w308_table()
        if hasattr(self, "recalculate_bond_roadmap"):
            self.recalculate_bond_roadmap()
        self.recalculate_craft_table()
        if hasattr(self, "recalculate_ge_craft_table"):
            self.recalculate_ge_craft_table()
        if hasattr(self, "recalculate_guide_table"):
            if hasattr(self, "var_guide_skill"):
                self.update_guide_quests_card(self.var_guide_skill.get())
            self.recalculate_guide_table()
        self.update_cart_display()
        self.update_session_display()
        self.update_timers_display()
        self.update_owned_nat_display()

    def focus_search(self):
        self.ent_search.focus_set()
        self.ent_search.select_range(0, tk.END)
        return "break"

    def clear_search(self):
        self.ent_search.delete(0, tk.END)
        if hasattr(self, "ent_craft_search"):
            self.ent_craft_search.delete(0, tk.END)
        if hasattr(self, "ent_ge_search"):
            self.ent_ge_search.delete(0, tk.END)
        self.on_global_search_changed()

    def on_global_search_changed(self, event=None):
        if hasattr(self, "ent_craft_search") and hasattr(self, "ent_search"):
            val = self.ent_search.get()
            if self.ent_craft_search.get() != val:
                self.ent_craft_search.delete(0, tk.END)
                self.ent_craft_search.insert(0, val)
        if hasattr(self, "ent_ge_search") and hasattr(self, "ent_search"):
            val = self.ent_search.get()
            if self.ent_ge_search.get() != val:
                self.ent_ge_search.delete(0, tk.END)
                self.ent_ge_search.insert(0, val)
        self.recalculate_alch_table()
        if hasattr(self, "recalculate_rec_table"):
            self.recalculate_rec_table()
        if hasattr(self, "recalculate_overnight_table"):
            self.recalculate_overnight_table()
        if hasattr(self, "recalculate_w308_table"):
            self.recalculate_w308_table()
        if hasattr(self, "recalculate_craft_table"):
            self.recalculate_craft_table()
        if hasattr(self, "recalculate_ge_craft_table"):
            self.recalculate_ge_craft_table()
        if hasattr(self, "recalculate_guide_table"):
            self.recalculate_guide_table()
        if hasattr(self, "update_timers_display"):
            self.update_timers_display()
        if hasattr(self, "update_session_display"):
            self.update_session_display()
        if hasattr(self, "update_alerts_display"):
            self.update_alerts_display()

    def on_craft_search_changed(self, event=None):
        if hasattr(self, "ent_craft_search") and hasattr(self, "ent_search"):
            val = self.ent_craft_search.get()
            if self.ent_search.get() != val:
                self.ent_search.delete(0, tk.END)
                self.ent_search.insert(0, val)
        self.on_global_search_changed()

    def on_tab_changed(self, event=None):
        search_query = self.ent_search.get().strip() if hasattr(self, "ent_search") else ""
        if search_query:
            self.on_global_search_changed()
        try:
            curr_tab = self.notebook.tab(self.notebook.select(), "text")
            if "Bond Roadmap" in curr_tab and hasattr(self, "recalculate_bond_roadmap"):
                self.recalculate_bond_roadmap()
        except Exception:
            pass

    def recalculate_alch_table(self):
        nat_cost = self.get_effective_nature_price()
        strat = self.var_strat.get().split()[0]
        cash_stack = self.get_current_cash_stack()
        max_spend = self.state.config.get("max_item_cost", 500000)
        min_vol = self.state.config.get("min_volume", 5000)
        mem_ok = self.var_members.get()
        f2p_ok = self.var_f2p.get()
        speed_filter = self.var_speed.get() if hasattr(self, "var_speed") else "All"

        # Parse user min profit filter (leave blank to show ALL items)
        min_p_val = None
        min_p_raw = self.ent_min_profit.get().strip().replace(",", "")
        if min_p_raw:
            try:
                min_p_val = int(min_p_raw)
            except ValueError:
                pass

        search_query = self.ent_search.get().strip().lower()

        new_rows = []

        if hasattr(self, "var_price_basis"):
            basis = "5m" if "5m" in self.var_price_basis.get() else "latest"
        else:
            basis = self.state.config.get("price_basis", "5m")

        for item_id_str, mdata in self.api.mapping.items():
            high_alch = mdata.get("highalch", 0)
            if not high_alch or high_alch <= 10:
                continue

            if search_query and search_query not in mdata["name"].lower():
                continue

            is_mem = mdata.get("members", False)
            if f2p_ok and not mem_ok and is_mem:
                continue
            if not f2p_ok and not mem_ok:
                continue

            bid, ask = self.api.get_bid_ask(item_id_str, basis=basis)
            buy_price = self.api.get_price(item_id_str, strat, basis=basis)
            if not buy_price or buy_price <= 0:
                continue
            if buy_price > max_spend:
                continue

            vol = self.api.volumes_24h.get(item_id_str, 0)
            if vol < min_vol:
                continue

            cost = buy_price + nat_cost
            profit = high_alch - cost

            # User filter cutoff: if blank, shows all items!
            if min_p_val is not None and profit < min_p_val:
                continue

            base_limit = mdata.get("limit", 0) or 0
            rem_limit, secs_left, is_cd = self.state.get_remaining_limit(mdata["id"], base_limit)

            # Hide Maxed (4h GE limit reached): temporarily remove from table while cooldown is active
            if getattr(self, "var_hide_maxed", None) and self.var_hide_maxed.get() and is_cd and rem_limit <= 0:
                continue

            speed_cat, speed_badge, est_mins, speed_score = self.api.get_fill_speed_info(mdata["id"], base_limit if base_limit > 0 else 70)

            # Detect 1-item freak spike vs 5m volume average & format 1-tick sold count
            is_spike, spike_pct, lat_low, avg_low_p, vol_5m_l = self.api.get_spike_info(mdata["id"])
            if basis == "latest":
                if is_spike:
                    speed_badge = f"⚠️ Spike ({vol_5m_l} sold)"
                elif vol_5m_l > 0:
                    badge_prefix = "⚡ Fast" if speed_cat == "fast" else "⏱️ Steady"
                    speed_badge = f"{badge_prefix} ({vol_5m_l} sold)"
                elif str(speed_badge).startswith("⚠️ Stale"):
                    speed_badge = "⚠️ Stale (0 sold)"
                else:
                    speed_badge = f"🐢 Slow ({vol_5m_l} sold)"

            # Apply Speed Filter
            if "Fast" in speed_filter and speed_cat != "fast":
                continue
            if "Steady" in speed_filter and speed_cat not in ("fast", "steady"):
                continue

            # Realistic Volume Capping (inspired by QuantScapers analysis engine)
            is_vol_capped = False
            if is_cd and rem_limit <= 0:
                effective_limit = 0
            elif base_limit > 0:
                avail_limit = rem_limit if is_cd else base_limit
                if vol > 0 and vol < avail_limit:
                    effective_limit = vol
                    is_vol_capped = True
                else:
                    effective_limit = avail_limit
            else:
                effective_limit = min(vol, 125) if vol > 0 else 125
                if vol > 0 and vol < 125:
                    is_vol_capped = True

            if is_cd:
                hours = int(secs_left // 3600)
                mins = int((secs_left % 3600) // 60)
                time_tag = f" ({hours}h {mins:02d}m)"
                if rem_limit > 0:
                    limit_str = f"{effective_limit}/{base_limit} ⚠️" if is_vol_capped else f"{rem_limit}/{base_limit}{time_tag}"
                else:
                    limit_str = f"0/{base_limit}{time_tag}"
            else:
                if base_limit > 0:
                    limit_str = f"{effective_limit}/{base_limit} ⚠️" if is_vol_capped else f"{base_limit}"
                else:
                    limit_str = f"{effective_limit} (Cap)" if is_vol_capped else "-"

            profit_hr = profit * 1200
            batch_profit = profit * effective_limit

            if self.var_use_cash.get():
                afford_qty = min(effective_limit, cash_stack // buy_price) if buy_price > 0 else 0
            else:
                afford_qty = effective_limit

            cart_qty = self.state.cart_items.get(str(mdata["id"]), 0)

            row_dict = {
                "id": mdata["id"],
                "cart": cart_qty,
                "name": mdata["name"],
                "bid": bid,
                "ask": ask,
                "buy_at": buy_price,
                "alch_val": high_alch,
                "profit_ea": profit,
                "profit_hr": profit_hr,
                "speed_cat": speed_cat,
                "speed_badge": speed_badge,
                "est_mins": est_mins,
                "speed_score": speed_score,
                "limit": effective_limit,
                "base_limit": base_limit,
                "effective_limit": effective_limit,
                "is_vol_capped": is_vol_capped,
                "is_spike": is_spike,
                "spike_pct": spike_pct,
                "latest_low": lat_low,
                "avg_low": avg_low_p,
                "vol_5m_low": vol_5m_l,
                "limit_str": limit_str,
                "is_cd": is_cd,
                "batch_profit": batch_profit,
                "max_afford": afford_qty,
                "volume": vol
            }
            new_rows.append(row_dict)

        # Sort based on active sorting column and direction
        sort_key_map = {
            "cart": "cart",
            "offer_bid": "bid",
            "instant_ask": "ask",
            "speed": "speed_score",
            "limit": "limit",
            "batch_profit": "batch_profit",
            "max_afford": "max_afford",
            "volume": "volume"
        }
        k = sort_key_map.get(self.alch_sort_col, self.alch_sort_col)
        if k == "name":
            new_rows.sort(key=lambda x: str(x.get("name", "")).lower(), reverse=self.alch_sort_desc)
        else:
            new_rows.sort(key=lambda x: x.get(k, 0), reverse=self.alch_sort_desc)
        self.alch_rows = new_rows

        # Dynamically sync column headings with active pricing basis
        arrow = " ▼" if self.alch_sort_desc else " ▲"
        speed_header = "Fill Speed (5m Sold)" if basis == "latest" else "Fill Speed"
        vol_header = "24h Vol (5m Sold)" if basis == "latest" else "24h Volume"
        self.tree_alch.heading("speed", text=speed_header + (arrow if self.alch_sort_col == "speed" else ""))
        self.tree_alch.heading("volume", text=vol_header + (arrow if self.alch_sort_col == "volume" else ""))

        self.tree_alch.delete(*self.tree_alch.get_children())
        for row in self.alch_rows[:300]:
            cart_str = f"{row['cart']}x" if row['cart'] > 0 else ""
            vol_base = f"{row['volume']/1000:.0f}k" if row['volume'] >= 100000 else f"{row['volume']:,}"
            if basis == "latest":
                vol_str = f"{vol_base} ({row['vol_5m_low']} sold)"
            else:
                vol_str = vol_base
            limit_str = row["limit_str"]

            p_ea_str = f"+{row['profit_ea']:,} gp" if row['profit_ea'] >= 0 else f"{row['profit_ea']:,} gp"
            p_hr_str = f"+{row['profit_hr']/1000:.1f}k/hr" if row['profit_hr'] >= 0 else f"{row['profit_hr']/1000:.1f}k/hr"
            b_p_str = f"+{row['batch_profit']:,} gp" if row['batch_profit'] >= 0 else f"{row['batch_profit']:,} gp"

            item_tag = "profit" if row['profit_ea'] >= 200 else ("mild" if row['profit_ea'] >= 0 else "loss")
            tags = (item_tag, "incart") if row['cart'] > 0 else (item_tag,)

            self.tree_alch.insert("", "end", iid=str(row["id"]), values=(
                cart_str,
                row["name"],
                f"{row['bid']:,} gp",
                f"{row['ask']:,} gp",
                f"{row['alch_val']:,} gp",
                p_ea_str,
                p_hr_str,
                row["speed_badge"],
                limit_str,
                b_p_str,
                f"{row['max_afford']:,}",
                vol_str
            ), tags=tags)

        self.tree_alch.tag_configure("profit", foreground="#2ecc71")
        self.tree_alch.tag_configure("mild", foreground="#f1c40f")
        self.tree_alch.tag_configure("loss", foreground="#e74c3c")
        self.tree_alch.tag_configure("incart", font=("Segoe UI", 9, "bold"))

        # Update BridgeServer with Top 10 recommendations for in-game plugin
        if hasattr(self, "bridge_server") and self.bridge_server:
            top_list = []
            for r in self.alch_rows:
                if r["profit_ea"] > 0 and r["limit"] > 0:
                    metrics = self.api.get_quote_metrics(r["id"])
                    top_list.append({
                        "id": r["id"],
                        "name": r["name"],
                        "buy_price": r["buy_at"],
                        "alch_value": r["alch_val"],
                        "profit_ea": r["profit_ea"],
                        "profit_hr": r["profit_hr"],
                        "limit": r["limit"],
                        "speed": r["speed_badge"],
                        "vol_5m": metrics.get("vol_5m_low", 0),
                        "vol_5m_price": metrics.get("avg_low", 0),
                        "vol_24h": r["volume"]
                    })
                if len(top_list) >= 10:
                    break
            self.bridge_server.set_top_items(top_list)

    def toggle_sort_alch(self, col):
        if self.alch_sort_col == col:
            if col == "name":
                if self.alch_sort_desc:
                    # 3rd click on name (was Z-A) -> reset to default
                    self.alch_sort_col = "profit_ea"
                    self.alch_sort_desc = True
                else:
                    # 2nd click on name -> Z-A
                    self.alch_sort_desc = True
            else:
                if not self.alch_sort_desc:
                    # 3rd click (was ascending / lowest first) -> reset to default
                    self.alch_sort_col = "profit_ea"
                    self.alch_sort_desc = True
                else:
                    # 2nd click -> ascending / lowest first
                    self.alch_sort_desc = False
        else:
            # 1st click on new column
            self.alch_sort_col = col
            self.alch_sort_desc = False if col == "name" else True

        arrow = " ▼" if self.alch_sort_desc else " ▲"
        if hasattr(self, "var_price_basis"):
            basis = "5m" if "5m" in self.var_price_basis.get() else "latest"
        else:
            basis = self.state.config.get("price_basis", "5m")
        speed_header = "Fill Speed (5m Sold)" if basis == "latest" else "Fill Speed"
        vol_header = "24h Vol (5m Sold)" if basis == "latest" else "24h Volume"
        headers = {
            "cart": "Cart",
            "name": "Item Name",
            "offer_bid": "Target Offer (Bid)",
            "instant_ask": "Instant Buy (Ask)",
            "alch_val": "Alch Value",
            "profit_ea": "Profit / Alch",
            "profit_hr": "Profit / Hr (1.2k)",
            "speed": speed_header,
            "limit": "4h Limit",
            "batch_profit": "4h Batch Profit",
            "max_afford": "Max Afford",
            "volume": vol_header
        }
        for c, title in headers.items():
            self.tree_alch.heading(c, text=title + (arrow if c == self.alch_sort_col else ""))

        self.recalculate_alch_table()

    def recalculate_rec_table(self):
        if not hasattr(self, "tree_rec"):
            return

        timing = get_market_timing_info()
        self.lbl_market_time.config(text=f"🕒 {timing['time_str']}")
        self.lbl_market_badge.config(text=timing['badge'], fg=timing['badge_color'])
        self.lbl_market_activity.config(text=timing['activity'])
        self.lbl_market_advice.config(text=timing['advice'])

        cat = self.var_rec_cat.get() if hasattr(self, "var_rec_cat") else "workhorse"
        nat_cost = self.get_effective_nature_price()
        strat = self.var_strat.get().split()[0] if hasattr(self, "var_strat") else "smart"
        cash_stack = self.state.config.get("cash_stack", 5000000)
        max_spend = self.state.config.get("max_item_cost", 500000)
        mem_ok = self.var_members.get() if hasattr(self, "var_members") else True
        f2p_ok = self.var_f2p.get() if hasattr(self, "var_f2p") else False

        basis = "5m" if hasattr(self, "var_price_basis") and "5m" in self.var_price_basis.get() else self.state.config.get("price_basis", "5m")
        search_query = self.ent_search.get().strip().lower() if hasattr(self, "ent_search") else ""

        rows = []

        if cat == "workhorse":
            for spec in WORKHORSE_ITEMS:
                iid_str = str(spec["id"])
                mdata = self.api.mapping.get(iid_str, {})
                item_name = mdata.get("name", spec["name"])
                if search_query:
                    if (search_query not in item_name.lower() and
                        search_query not in spec.get("verdict", "").lower() and
                        search_query not in "workhorse"):
                        continue

                high_alch = mdata.get("highalch", 0)
                if not high_alch or high_alch <= 10:
                    continue

                is_mem = mdata.get("members", spec.get("members", False))
                if f2p_ok and not mem_ok and is_mem:
                    continue
                if not f2p_ok and not mem_ok:
                    continue

                bid, ask = self.api.get_bid_ask(iid_str, basis=basis)
                buy_price = self.api.get_price(iid_str, strat, basis=basis)
                if not buy_price or buy_price <= 0:
                    continue
                if buy_price > max_spend:
                    continue

                profit = high_alch - buy_price - nat_cost
                base_limit = spec.get("limit", mdata.get("limit", 70))
                rem_limit, secs_left, is_cd = self.state.get_remaining_limit(spec["id"], base_limit)

                vol = self.api.volumes_24h.get(iid_str, 0)
                speed_cat, speed_badge, est_mins, speed_score = self.api.get_fill_speed_info(spec["id"], base_limit)

                avail_limit = rem_limit if is_cd else base_limit
                eff_limit = avail_limit if (vol <= 0 or vol >= avail_limit) else vol
                batch_profit = profit * eff_limit if eff_limit > 0 else 0
                batch_cost = buy_price * eff_limit

                if is_cd:
                    hours = int(secs_left // 3600)
                    mins = int((secs_left % 3600) // 60)
                    time_tag = f" ({hours}h {mins:02d}m)"
                    limit_str = f"{rem_limit}/{base_limit}{time_tag}" if rem_limit > 0 else f"0/{base_limit}{time_tag}"
                else:
                    limit_str = f"{base_limit}"

                rows.append({
                    "id": spec["id"],
                    "name": mdata.get("name", spec["name"]),
                    "category": "🏆 Workhorse",
                    "bid": bid or buy_price,
                    "ask": ask or buy_price,
                    "buy_at": buy_price,
                    "alch_val": high_alch,
                    "profit_ea": profit,
                    "profit_hr": profit * 1200,
                    "limit": base_limit,
                    "rem_limit": rem_limit,
                    "eff_limit": eff_limit,
                    "limit_str": limit_str,
                    "batch_profit": batch_profit,
                    "batch_cost": batch_cost,
                    "speed_cat": speed_cat,
                    "speed_badge": speed_badge,
                    "verdict": spec["verdict"]
                })

        else:
            for iid_str, mdata in self.api.mapping.items():
                high_alch = mdata.get("highalch", 0)
                if not high_alch or high_alch <= 10:
                    continue

                is_mem = mdata.get("members", False)
                if f2p_ok and not mem_ok and is_mem:
                    continue
                if not f2p_ok and not mem_ok:
                    continue

                bid, ask = self.api.get_bid_ask(iid_str, basis=basis)
                buy_price = self.api.get_price(iid_str, strat, basis=basis)
                if not buy_price or buy_price <= 0 or buy_price > max_spend:
                    continue

                profit = high_alch - buy_price - nat_cost
                if profit <= 0:
                    continue

                base_limit = mdata.get("limit", 0) or 0
                if base_limit <= 0:
                    continue

                vol = self.api.volumes_24h.get(iid_str, 0)
                rem_limit, secs_left, is_cd = self.state.get_remaining_limit(mdata["id"], base_limit)
                avail_limit = rem_limit if is_cd else base_limit
                eff_limit = avail_limit if (vol <= 0 or vol >= avail_limit) else vol
                if eff_limit <= 0:
                    continue

                batch_profit = profit * eff_limit
                batch_cost = buy_price * eff_limit
                speed_cat, speed_badge, est_mins, speed_score = self.api.get_fill_speed_info(mdata["id"], base_limit)

                if is_cd:
                    hours = int(secs_left // 3600)
                    mins = int((secs_left % 3600) // 60)
                    time_tag = f" ({hours}h {mins:02d}m)"
                    limit_str = f"{rem_limit}/{base_limit}{time_tag}" if rem_limit > 0 else f"0/{base_limit}{time_tag}"
                else:
                    limit_str = f"{base_limit}"

                v5 = self.api.volumes_5m.get(iid_str, {})
                sold_5m = v5.get("low", 0) or 0

                if cat == "fast":
                    if speed_cat != "fast" and sold_5m < 8:
                        continue
                    cat_label = "⚡ Fast Fill"
                    verdict = f"⚡ Instant velocity: {sold_5m} sold in 5m into bids. Fills in ~{est_mins}m."
                elif cat == "batch":
                    if eff_limit < 10 or batch_profit < 10000:
                        continue
                    cat_label = "💰 Batch Profit"
                    verdict = f"💰 Top Batch Yield: Earns +{batch_profit:,} gp for full {base_limit} batch."
                elif cat == "overnight":
                    if profit < 250 or eff_limit < 15:
                        continue
                    cat_label = "🌙 Overnight"
                    verdict = f"🌙 Patient sleeper: +{profit:,} gp/ea. Queue low bid overnight during off-peak hours."
                else:
                    cat_label = "Smart Pick"
                    verdict = "Solid alch margin."

                if search_query:
                    if (search_query not in mdata["name"].lower() and
                        search_query not in cat_label.lower() and
                        search_query not in verdict.lower()):
                        continue

                rows.append({
                    "id": mdata["id"],
                    "name": mdata["name"],
                    "category": cat_label,
                    "bid": bid or buy_price,
                    "ask": ask or buy_price,
                    "buy_at": buy_price,
                    "alch_val": high_alch,
                    "profit_ea": profit,
                    "profit_hr": profit * 1200,
                    "limit": base_limit,
                    "rem_limit": rem_limit,
                    "eff_limit": eff_limit,
                    "limit_str": limit_str,
                    "batch_profit": batch_profit,
                    "batch_cost": batch_cost,
                    "speed_cat": speed_cat,
                    "speed_badge": speed_badge,
                    "verdict": verdict
                })

        sort_col = getattr(self, "rec_sort_col", "profit_ea")
        sort_desc = getattr(self, "rec_sort_desc", True)
        if cat == "batch" and sort_col == "profit_ea" and sort_desc:
            sort_col = "batch_profit"
        elif cat == "fast" and sort_col == "profit_ea" and sort_desc:
            sort_col = "profit_hr"

        if sort_col == "name":
            rows.sort(key=lambda x: str(x.get("name", "")).lower(), reverse=sort_desc)
        elif sort_col == "badge":
            pass
        else:
            rows.sort(key=lambda x: x.get(sort_col, 0), reverse=sort_desc)

        self.rec_rows = rows[:25]

        self.tree_rec.delete(*self.tree_rec.get_children())
        medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]

        for idx, r in enumerate(self.rec_rows):
            badge = medals[idx] if idx < len(medals) else f"#{idx+1}"
            r["badge"] = badge

            p_ea_str = f"+{r['profit_ea']:,} gp" if r['profit_ea'] >= 0 else f"{r['profit_ea']:,} gp"
            b_p_str = f"+{r['batch_profit']:,} gp" if r['batch_profit'] >= 0 else f"{r['batch_profit']:,} gp"
            b_cost_str = format_gp(r['batch_cost'])

            in_cart = str(r["id"]) in self.state.cart_items
            tags = ("incart",) if in_cart else ("profit",)

            self.tree_rec.insert("", "end", iid=str(r["id"]), values=(
                badge,
                r["name"],
                r["category"],
                f"{r['bid']:,} gp",
                f"{r['alch_val']:,} gp",
                p_ea_str,
                r["limit_str"],
                b_p_str,
                r["speed_badge"],
                b_cost_str,
                r["verdict"]
            ), tags=tags)

        self.tree_rec.tag_configure("profit", foreground="#2ecc71")
        self.tree_rec.tag_configure("incart", font=("Segoe UI", 9, "bold"), foreground="#f39c12")

    def toggle_sort_rec(self, col):
        if getattr(self, "rec_sort_col", "") == col:
            self.rec_sort_desc = not self.rec_sort_desc
        else:
            self.rec_sort_col = col
            self.rec_sort_desc = False if col in ("name", "category", "badge") else True
        self.recalculate_rec_table()

    # ------------------ OVERNIGHT PLANNER LOGIC ------------------

    def recalculate_overnight_table(self):
        if not hasattr(self, "tree_overnight"):
            return

        # 1. Parse Duration & Limit Multiplier
        dur_str = self.var_overnight_dur.get() if hasattr(self, "var_overnight_dur") else "12 Hours (3x limit)"
        if "6 Hours" in dur_str:
            hours, cycles = 6, 2
        elif "8 Hours" in dur_str:
            hours, cycles = 8, 2
        elif "10 Hours" in dur_str:
            hours, cycles = 10, 3
        else:
            hours, cycles = 12, 3

        if hasattr(self, "lbl_overnight_cycles"):
            self.lbl_overnight_cycles.config(text=f"⏰ Limit Multiplier: {cycles}.0x ({hours}h Window = {cycles} GE Limit Resets)")

        # 2. Parse Strategy & Slots
        strat_str = self.var_overnight_strat.get() if hasattr(self, "var_overnight_strat") else "Safe"
        strat_type = "deep" if "Deep" in strat_str else "safe"

        slots_str = self.var_overnight_slots.get() if hasattr(self, "var_overnight_slots") else "3"
        try:
            num_slots = int(slots_str.split()[0])
        except Exception:
            num_slots = 3 if (hasattr(self, "var_f2p") and self.var_f2p.get()) else 8

        # 3. Nature Rune Cost
        use_owned_nats = self.var_overnight_owned_nat.get() if hasattr(self, "var_overnight_owned_nat") else True
        nat_cost = 0 if use_owned_nats else self.get_effective_nature_price()

        # 4. Cash Budget
        use_cash = self.var_use_cash.get() if hasattr(self, "var_use_cash") else True
        cash_stack = self.state.config.get("cash_stack", 5000000) if use_cash else 999_999_999

        # 5. Max Alch Time (Morning Session Duration)
        time_str = self.var_overnight_time.get() if hasattr(self, "var_overnight_time") else "1 Hour"
        if "30 Mins" in time_str:
            max_casts = 600
        elif "45 Mins" in time_str:
            max_casts = 900
        elif "1 Hour" in time_str:
            max_casts = 1200
        elif "2 Hours" in time_str:
            max_casts = 2400
        elif "3 Hours" in time_str:
            max_casts = 3600
        else:
            max_casts = None

        # 5b. Max Items Per Offer Slot Cap
        slot_cap_str = self.var_overnight_max_slot.get() if hasattr(self, "var_overnight_max_slot") else "500"
        if "250" in slot_cap_str:
            max_per_item = 250
        elif "375" in slot_cap_str:
            max_per_item = 375
        elif "500" in slot_cap_str:
            max_per_item = 500
        elif "1,000" in slot_cap_str:
            max_per_item = 1000
        else:
            max_per_item = None

        # 6. Membership & Focus Filters
        mem_ok = self.var_members.get() if hasattr(self, "var_members") else True
        f2p_ok = self.var_f2p.get() if hasattr(self, "var_f2p") else False
        focus = self.var_overnight_focus.get() if hasattr(self, "var_overnight_focus") else "All"
        search_query = self.ent_search.get().strip().lower() if hasattr(self, "ent_search") else ""

        # Fetch candidate data
        raw_candidates = self.api.get_overnight_data()
        pool = []

        is_bulk_focus = any(k in focus for k in ("Battlestaves", "Stackables"))

        for it in raw_candidates:
            is_mem = it.get("members", False)
            if f2p_ok and not mem_ok and is_mem:
                continue
            if not f2p_ok and not mem_ok:
                continue

            grp = it.get("group", "")
            name_lower = it["name"].lower()
            base_ge_limit = it.get("limit", 0) or 0

            # Auto-exclude bulk skilling & ammo (GE limit > 250) unless user explicitly selects Battlestaves or Stackables
            if not is_bulk_focus and not search_query and base_ge_limit > 250:
                continue

            if "Rune Heavy" in focus:
                if grp != "rune" and "rune" not in name_lower:
                    continue
            elif "Adamant" in focus:
                if grp != "adamant" and "adamant" not in name_lower:
                    continue
            elif "Battlestaves" in focus:
                if grp != "staff" and "staff" not in name_lower:
                    continue
            elif "Stackables" in focus:
                if grp not in ("bolt", "ammo") and "bolt" not in name_lower:
                    continue

            if search_query:
                if (search_query not in name_lower and
                    search_query not in it.get("verdict", "").lower()):
                    continue

            bid = it["deep_bid"] if strat_type == "deep" else it["safe_bid"]
            if not bid or bid <= 0:
                continue
            prof_ea = it["alch"] - bid - nat_cost
            if prof_ea <= 0:
                continue

            # Exclude low-margin ammo (< 200 gp profit) unless explicitly searching or focusing on stackables
            if grp in ("bolt", "ammo") and prof_ea < 200 and "Stackables" not in focus and not search_query:
                continue

            pool.append(it)

        # 7. Optimize Bag
        alloc, total_spend, total_profit = self.optimize_overnight_bag(
            pool, num_slots, cash_stack, cycles, nat_cost, strat_type=strat_type, max_casts=max_casts, max_per_item=max_per_item
        )
        self.overnight_alloc = alloc

        # 8. Update Summary Card
        total_items = sum(a["qty"] for a in alloc)
        leftover_gp = max(0, cash_stack - total_spend) if use_cash else 0

        if hasattr(self, "lbl_on_budget"):
            self.lbl_on_budget.config(text=format_gp(cash_stack) if use_cash else "Unlimited")
            self.lbl_on_spend.config(text=format_gp(total_spend))
            self.lbl_on_leftover.config(text=format_gp(leftover_gp) if use_cash else "N/A")
            self.lbl_on_profit.config(text=f"+{format_gp(total_profit)}")
            self.lbl_on_items.config(text=f"{total_items:,} items")
            alch_mins = int(math.ceil(total_items / 20.0)) if total_items > 0 else 0
            self.lbl_on_time.config(text=f"~{alch_mins} mins (1.2k/hr)" if alch_mins > 0 else "-- mins")
            hourly_rate = int(total_profit / (total_items / 1200.0)) if total_items > 0 else 0
            if hasattr(self, "lbl_on_rate"):
                self.lbl_on_rate.config(text=f"+{format_gp(hourly_rate)}/hr" if hourly_rate > 0 else "--/hr")

        # 9. Build Table Rows
        alloc_map = {a["id"]: a for a in alloc}
        medals = ["🥇 Pick #1", "🥈 Pick #2", "🥉 Pick #3", "⭐ Pick #4", "⭐ Pick #5", "⭐ Pick #6", "⭐ Pick #7", "⭐ Pick #8"]
        pick_order = {a["id"]: idx for idx, a in enumerate(alloc)}

        rows = []
        for it in pool:
            bid = it["deep_bid"] if strat_type == "deep" else it["safe_bid"]
            prof_ea = it["alch"] - bid - nat_cost
            base_lim = it["limit"] * cycles
            period_limit = base_lim
            if max_per_item:
                period_limit = min(period_limit, max_per_item)
            if max_casts:
                period_limit = min(period_limit, max_casts)
            conf = it.get("conf_deep" if strat_type == "deep" else "conf_safe", "🟢 High")
            is_alloc = it["id"] in alloc_map

            if is_alloc:
                a_info = alloc_map[it["id"]]
                rank_idx = pick_order.get(it["id"], 0)
                badge = medals[rank_idx] if rank_idx < len(medals) else f"⭐ Pick #{rank_idx+1}"
                alloc_qty = a_info["qty"]
                cost = a_info["cost"]
                slot_prof = a_info["profit"]
                sort_rank = rank_idx
            else:
                badge = "Alternative"
                alloc_qty = 0
                cost = 0
                slot_prof = prof_ea * period_limit
                sort_rank = 999

            rows.append({
                "id": it["id"],
                "badge": badge,
                "name": it["name"],
                "bid": bid,
                "alch": it["alch"],
                "profit_ea": prof_ea,
                "limit_period": period_limit,
                "alloc_qty": alloc_qty,
                "total_cost": cost,
                "slot_profit": slot_prof,
                "confidence": conf,
                "verdict": it.get("verdict", ""),
                "is_alloc": is_alloc,
                "sort_rank": sort_rank
            })

        # Sorting
        sort_col = getattr(self, "overnight_sort_col", None)
        sort_desc = getattr(self, "overnight_sort_desc", True)

        if sort_col:
            rows.sort(key=lambda r: r.get(sort_col, 0), reverse=sort_desc)
        else:
            # Default sort: Allocated picks first by rank, then alternatives by expected profit descending
            rows.sort(key=lambda r: (r["sort_rank"], -r["slot_profit"]))

        self.overnight_rows = rows

        # Render Treeview
        self.tree_overnight.delete(*self.tree_overnight.get_children())
        for r in rows:
            iid_str = str(r["id"])
            in_cart = iid_str in self.state.cart_items

            tags = []
            if in_cart:
                tags.append("incart")
            elif r["is_alloc"]:
                tags.append("allocated")
            else:
                tags.append("alt")

            self.tree_overnight.insert("", "end", iid=iid_str, values=(
                r["badge"],
                r["name"],
                f"{r['bid']:,} gp",
                f"{r['alch']:,} gp",
                f"+{r['profit_ea']:,} gp",
                f"{r['limit_period']:,}",
                f"{r['alloc_qty']:,}x" if r["alloc_qty"] > 0 else "--",
                f"{r['total_cost']:,} gp" if r["total_cost"] > 0 else "--",
                f"+{r['slot_profit']:,} gp",
                r["confidence"],
                r["verdict"]
            ), tags=tags)

        self.tree_overnight.tag_configure("allocated", font=("Segoe UI", 9, "bold"), foreground="#2ecc71")
        self.tree_overnight.tag_configure("incart", font=("Segoe UI", 9, "bold"), foreground="#f39c12")
        self.tree_overnight.tag_configure("alt", foreground="#cccccc")

    def optimize_overnight_bag(self, items, num_slots, total_budget, cycles, nat_cost, strat_type="safe", max_casts=None, max_per_item=None):
        if not items or num_slots <= 0:
            return [], 0, 0

        valid_items = []
        for it in items:
            bid = it["deep_bid"] if strat_type == "deep" else it["safe_bid"]
            if not bid or bid <= 0:
                continue
            prof_ea = it["alch"] - bid - nat_cost
            if prof_ea <= 0:
                continue
            base_limit = it["limit"] * cycles
            period_limit = base_limit
            if max_per_item:
                period_limit = min(period_limit, max_per_item)
            if max_casts:
                period_limit = min(period_limit, max_casts)
            valid_items.append({
                "item": it,
                "id": it["id"],
                "name": it["name"],
                "bid": bid,
                "alch": it["alch"],
                "profit_ea": prof_ea,
                "period_limit": period_limit,
                "roi": prof_ea / max(1, bid),
                "period_profit": prof_ea * period_limit,
                "period_cost": bid * period_limit,
                "verdict": it.get("verdict", ""),
                "conf": it.get("conf_deep" if strat_type == "deep" else "conf_safe", "")
            })

        if not valid_items:
            return [], 0, 0

        # Multi-pass greedy knapsack evaluating:
        # Pass 1: Highest Profit Per Cast (profit_ea) - maximizes hourly rate / morning alch profit
        # Pass 2: Highest ROI (profit_ea / bid) - maximizes coin efficiency when capital constrained
        # Pass 3: Highest Total Batch Profit (period_profit) - for bulk hoarding runs
        passes = [
            sorted(valid_items, key=lambda x: x["profit_ea"], reverse=True),
            sorted(valid_items, key=lambda x: x["roi"], reverse=True),
            sorted(valid_items, key=lambda x: (x["period_profit"], x["profit_ea"]), reverse=True)
        ]

        best_alloc = []
        best_profit = -1
        best_spend = 0

        for candidate_list in passes:
            rem_budget = total_budget
            rem_casts = max_casts if max_casts else 999_999_999
            cur_alloc = []
            tot_prof = 0
            tot_spend = 0
            for it in candidate_list:
                if len(cur_alloc) >= num_slots or rem_casts <= 0:
                    break
                can_buy = min(it["period_limit"], rem_casts, rem_budget // it["bid"])
                if can_buy > 0:
                    cost = can_buy * it["bid"]
                    prof = can_buy * it["profit_ea"]
                    rem_budget -= cost
                    rem_casts -= can_buy
                    tot_spend += cost
                    tot_prof += prof
                    cur_alloc.append({
                        "id": it["id"],
                        "name": it["name"],
                        "bid": it["bid"],
                        "alch": it["alch"],
                        "profit_ea": it["profit_ea"],
                        "period_limit": it["period_limit"],
                        "qty": can_buy,
                        "cost": cost,
                        "profit": prof,
                        "conf": it["conf"],
                        "verdict": it["verdict"]
                    })
            if tot_prof > best_profit:
                best_profit = tot_prof
                best_alloc = cur_alloc
                best_spend = tot_spend

        return best_alloc, best_spend, best_profit

    def on_auto_optimize_clicked(self):
        self.recalculate_overnight_table()
        if getattr(self, "overnight_alloc", None):
            self.lbl_status_right.config(
                text=f"⚡ Auto-optimized {len(self.overnight_alloc)} overnight slots to maximize profit!",
                fg="#2ecc71"
            )

    def send_overnight_bag_to_cart(self):
        alloc = getattr(self, "overnight_alloc", [])
        if not alloc:
            messagebox.showinfo("No Overnight Bag", "Please configure or auto-optimize your overnight bag first.")
            return

        added_count = 0
        for item in alloc:
            iid_str = str(item["id"])
            qty = item["qty"]
            if qty > 0:
                self.state.cart_items[iid_str] = qty
                added_count += 1

        self.recalculate_alch_table()
        self.update_cart_display()
        self.recalculate_overnight_table()
        self.lbl_status_right.config(
            text=f"🛒 Sent {added_count} overnight items to your Grand Exchange Shopping Cart!",
            fg="#2ecc71"
        )

    def copy_overnight_offers(self):
        alloc = getattr(self, "overnight_alloc", [])
        if not alloc:
            self.lbl_status_right.config(text="No overnight bag to copy", fg="#888888")
            return

        dur = self.var_overnight_dur.get() if hasattr(self, "var_overnight_dur") else "12 Hours"
        strat = self.var_overnight_strat.get() if hasattr(self, "var_overnight_strat") else "Safe"

        lines = [
            f"🌙 Grand Exchange Overnight Buy Plan ({dur} - {strat})",
            "────────────────────────────────────────────────────────────"
        ]
        tot_spend = 0
        tot_prof = 0
        for idx, it in enumerate(alloc, 1):
            name = it["name"]
            qty = it["qty"]
            bid = it["bid"]
            cost = it["cost"]
            prof = it["profit"]
            tot_spend += cost
            tot_prof += prof
            lines.append(f"{idx}. {name}: {qty:,}x @ {bid:,} gp (Cost: {format_gp(cost)} | Profit: +{format_gp(prof)})")

        lines.append("────────────────────────────────────────────────────────────")
        lines.append(f"Total Spend: {format_gp(tot_spend)} | Expected Profit: +{format_gp(tot_prof)}")
        text = "\n".join(lines)

        self.clipboard_clear()
        self.clipboard_append(text)
        self.lbl_status_right.config(text=f"📋 Copied overnight buy plan ({len(alloc)} items) to clipboard!", fg="#3498db")

    def refresh_overnight_dips(self):
        self.lbl_status_right.config(text="Refreshing overnight dip data from Wiki API...", fg="#f39c12")
        def _worker():
            try:
                self.api.get_overnight_data(force_refresh=True)
            except Exception as e:
                print(f"Overnight refresh error: {e}")
            try:
                self.after(0, self.recalculate_overnight_table)
            except Exception:
                pass
        threading.Thread(target=_worker, daemon=True).start()

    def toggle_sort_overnight(self, col):
        if getattr(self, "overnight_sort_col", "") == col:
            self.overnight_sort_desc = not self.overnight_sort_desc
        else:
            self.overnight_sort_col = col
            self.overnight_sort_desc = False if col in ("name", "badge", "confidence") else True
        self.recalculate_overnight_table()

    def on_overnight_click(self, event):
        item_id = self.tree_overnight.identify_row(event.y)
        if not item_id:
            return
        row = next((r for r in getattr(self, "overnight_rows", []) if str(r["id"]) == item_id), None)
        if not row:
            return
        col_id = self.tree_overnight.identify_column(event.x)
        if col_id == "#3": # Bid
            self.copy_to_clipboard(str(row["bid"]), f"Copied Bid: {row['bid']:,} gp ({row['name']})")
        elif col_id == "#7": # Alloc Qty
            qty = row["alloc_qty"] if row["alloc_qty"] > 0 else row["limit_period"]
            self.copy_to_clipboard(str(qty), f"Copied Qty: {qty:,}x ({row['name']})")
        else:
            self.copy_to_clipboard(row["name"], f"Copied '{row['name']}' to clipboard!")

    def on_overnight_double_click(self, event):
        item_id = self.tree_overnight.identify_row(event.y)
        if not item_id:
            return
        if item_id in self.state.cart_items:
            del self.state.cart_items[item_id]
            self.lbl_status_right.config(text="Removed item from cart", fg="#888888")
        else:
            row = next((r for r in getattr(self, "overnight_rows", []) if str(r["id"]) == item_id), None)
            if row:
                qty = row["alloc_qty"] if row["alloc_qty"] > 0 else row["limit_period"]
                self.state.cart_items[item_id] = qty
                self.lbl_status_right.config(text=f"Added {qty:,}x {row['name']} to cart", fg="#2ecc71")
        self.recalculate_alch_table()
        self.update_cart_display()
        self.recalculate_overnight_table()

    def on_overnight_right_click(self, event):
        item_id = self.tree_overnight.identify_row(event.y)
        if not item_id:
            return
        row = next((r for r in getattr(self, "overnight_rows", []) if str(r["id"]) == item_id), None)
        if not row:
            return

        qty = row["alloc_qty"] if row["alloc_qty"] > 0 else row["limit_period"]
        menu = tk.Menu(self, tearoff=0, bg="#2d2d30", fg="#ffffff", activebackground="#f39c12", activeforeground="#000000")
        menu.add_command(label=f"🛒 Add to Cart ({qty:,}x)", command=lambda: self._overnight_add_to_cart(row, qty))
        menu.add_command(label="✏️ Set Custom Quantity in Cart...", command=lambda: self._overnight_set_custom_qty(row))
        menu.add_separator()
        menu.add_command(label=f"📋 Copy Name ('{row['name']}')", command=lambda: self.copy_to_clipboard(row["name"], f"Copied '{row['name']}'!"))
        menu.add_command(label=f"💰 Copy Bid Price ({row['bid']:,} gp)", command=lambda: self.copy_to_clipboard(str(row["bid"]), f"Copied {row['bid']:,} gp!"))
        menu.add_command(label=f"🔢 Copy Quantity ({qty:,}x)", command=lambda: self.copy_to_clipboard(str(qty), f"Copied {qty:,}x!"))
        menu.add_command(label=f"📝 Copy GE Order ('Buy {qty:,}x @ {row['bid']:,} gp')", command=lambda: self.copy_to_clipboard(f"Buy {qty:,}x {row['name']} @ {row['bid']:,} gp", f"Copied GE Order!"))
        menu.add_separator()
        menu.add_command(label="🌐 Open in OSRS Wiki Prices", command=lambda: self.open_wiki_url(row["id"]))
        menu.post(event.x_root, event.y_root)

    def _overnight_add_to_cart(self, row, qty):
        item_id = str(row["id"])
        self.state.cart_items[item_id] = qty
        self.recalculate_alch_table()
        self.update_cart_display()
        self.recalculate_overnight_table()
        self.lbl_status_right.config(text=f"Added {qty:,}x {row['name']} to cart", fg="#2ecc71")

    def _overnight_set_custom_qty(self, row):
        item_id = str(row["id"])
        curr_qty = self.state.cart_items.get(item_id, 0)
        max_allowed = row.get("limit_period", 1000)

        def save_qty(new_qty):
            if new_qty <= 0:
                if item_id in self.state.cart_items:
                    del self.state.cart_items[item_id]
                self.lbl_status_right.config(text=f"Removed {row['name']} from cart", fg="#888888")
            else:
                self.state.cart_items[item_id] = new_qty
                self.lbl_status_right.config(text=f"Set {new_qty:,}x {row['name']} in cart", fg="#2ecc71")
            self.recalculate_alch_table()
            self.update_cart_display()
            self.recalculate_overnight_table()

        SetQuantityDialog(self, row["name"], curr_qty, max_allowed, save_qty)

    def recalculate_craft_table(self):
        nat_cost = self.get_effective_nature_price()
        strat = self.var_strat.get().split()[0]
        levels = self.state.config.get("player_levels", {})
        only_usable = self.var_only_usable.get()
        craft_query = self.ent_craft_search.get().strip().lower() if hasattr(self, "ent_craft_search") else ""
        if not craft_query and hasattr(self, "ent_search"):
            craft_query = self.ent_search.get().strip().lower()
        mem_ok = self.var_members.get() if hasattr(self, "var_members") else True
        f2p_ok = self.var_f2p.get() if hasattr(self, "var_f2p") else False

        self.tree_craft.delete(*self.tree_craft.get_children())
        rows = []

        for r in CRAFTING_RECIPES:
            if craft_query:
                name_match = craft_query in r["name"].lower()
                mat_match = any(craft_query in m["name"].lower() for m in r.get("materials", []))
                skill_match = craft_query in r.get("skill", "").lower()
                if not name_match and not mat_match and not skill_match:
                    continue

            is_mem = r.get("members", True)
            if f2p_ok and not mem_ok and is_mem:
                continue
            if not f2p_ok and not mem_ok:
                continue

            req_skill = r["skill"]
            if req_skill == "Crafting" and hasattr(self, "var_filter_craft") and not self.var_filter_craft.get():
                continue
            if req_skill == "Smithing" and hasattr(self, "var_filter_smith") and not self.var_filter_smith.get():
                continue
            if req_skill == "Fletching" and hasattr(self, "var_filter_fletch") and not self.var_filter_fletch.get():
                continue
            if req_skill == "Magic" and hasattr(self, "var_filter_magic") and not self.var_filter_magic.get():
                continue

            req_lvl = r["level"]
            player_lvl = levels.get(req_skill, 99)
            can_make = player_lvl >= req_lvl

            if only_usable and not can_make:
                continue

            mat_cost = 0
            valid_mats = True
            mat_breakdown = []
            for m in r["materials"]:
                p = self.api.get_price(m["id"], strat)
                if not p:
                    valid_mats = False
                    break
                sub_total = p * m["qty"]
                mat_cost += sub_total
                mat_breakdown.append({
                    "name": m["name"],
                    "qty": m["qty"],
                    "price_ea": p,
                    "total": sub_total
                })

            if not valid_mats:
                continue

            out_meta = self.api.mapping.get(str(r["output_id"]), {})
            alch_val = out_meta.get("highalch", 0)
            if not alch_val:
                continue

            total_recipe_cost = mat_cost + nat_cost
            craft_alch_profit = alch_val - total_recipe_cost

            finished_buy_price = self.api.get_price(r["output_id"], strat)
            direct_alch_profit = (alch_val - (finished_buy_price + nat_cost)) if finished_buy_price else 0
            bonus_vs_buy = craft_alch_profit - direct_alch_profit

            hr_profit = craft_alch_profit * 1200

            rows.append({
                "recipe": r["name"],
                "skill_req": f"{req_skill} {req_lvl}" + ("" if can_make else " ⚠️"),
                "mat_cost": mat_cost,
                "alch_val": alch_val,
                "profit_ea": craft_alch_profit,
                "bonus": bonus_vs_buy,
                "xp": r["xp"],
                "hr_profit": hr_profit,
                "can_make": can_make,
                "materials": mat_breakdown,
                "nat_cost": nat_cost
            })

        rows.sort(key=lambda x: x.get(self.craft_sort_col, 0), reverse=self.craft_sort_desc)
        self.craft_rows = rows

        for cr in rows:
            p_ea_str = f"+{cr['profit_ea']:,} gp" if cr['profit_ea'] >= 0 else f"{cr['profit_ea']:,} gp"
            bonus_str = f"+{cr['bonus']:,} gp" if cr['bonus'] >= 0 else f"{cr['bonus']:,} gp"
            hr_str = f"+{cr['hr_profit']/1000:.1f}k/hr" if cr['hr_profit'] >= 0 else f"{cr['hr_profit']/1000:.1f}k/hr"

            tag = "profit" if cr['profit_ea'] >= 250 else ("mild" if cr['profit_ea'] >= 0 else "loss")
            if not cr["can_make"]:
                tag = "unusable"

            # Insert Parent Recipe Row
            parent_id = self.tree_craft.insert("", "end", text=f" {cr['recipe']}", values=(
                cr["skill_req"],
                f"{cr['mat_cost']:,} gp",
                f"{cr['alch_val']:,} gp",
                p_ea_str,
                bonus_str,
                f"{cr['xp']} xp",
                hr_str
            ), tags=(tag,), open=False)

            # Insert Breakdown Sub-rows (+ / -)
            for m in cr["materials"]:
                self.tree_craft.insert(parent_id, "end", text=f"  ↳ {m['name']} (x{m['qty']})", values=(
                    "-",
                    f"{m['total']:,} gp ({m['price_ea']:,} ea)",
                    "-",
                    "-",
                    "-",
                    "-",
                    "-"
                ), tags=("subrow",))

            self.tree_craft.insert(parent_id, "end", text=f"  ↳ Nature rune (x1)", values=(
                "-",
                f"{cr['nat_cost']:,} gp",
                "-",
                "-",
                "-",
                "-",
                "-"
            ), tags=("subrow",))

        self.tree_craft.tag_configure("profit", foreground="#2ecc71")
        self.tree_craft.tag_configure("mild", foreground="#f1c40f")
        self.tree_craft.tag_configure("loss", foreground="#e74c3c")
        self.tree_craft.tag_configure("unusable", foreground="#777777")
        self.tree_craft.tag_configure("subrow", foreground="#95a5a6")

    def toggle_sort_craft(self, col):
        if self.craft_sort_col == col:
            if col == "recipe":
                if self.craft_sort_desc:
                    # 3rd click on recipe (was Z-A) -> reset to default
                    self.craft_sort_col = "profit_ea"
                    self.craft_sort_desc = True
                else:
                    # 2nd click on recipe -> Z-A
                    self.craft_sort_desc = True
            else:
                if not self.craft_sort_desc:
                    # 3rd click (was ascending / lowest first) -> reset to default
                    self.craft_sort_col = "profit_ea"
                    self.craft_sort_desc = True
                else:
                    # 2nd click -> ascending / lowest first
                    self.craft_sort_desc = False
        else:
            # 1st click on new column
            self.craft_sort_col = col
            self.craft_sort_desc = False if col == "recipe" else True

        arrow = " ▼" if self.craft_sort_desc else " ▲"
        headers = {
            "recipe": ("#0", "Recipe / Ingredient Breakdown"),
            "skill_req": ("skill_req", "Skill & Req"),
            "mat_cost": ("mat_cost", "Materials Cost"),
            "alch_val": ("alch_val", "Alch Value"),
            "profit_ea": ("profit_ea", "Profit (Craft + Alch)"),
            "bonus": ("extra_vs_buy", "Bonus vs Buying Finished"),
            "xp": ("xp_ea", "XP / Item"),
            "hr_profit": ("profit_hr", "Est Craft+Alch GP/Hr")
        }
        for sort_k, (col_id, title) in headers.items():
            self.tree_craft.heading(col_id, text=title + (arrow if self.craft_sort_col == sort_k else ""))

        self.recalculate_craft_table()

    # ------------------ GE PRODUCTION & CRAFTING PROFIT TAB ------------------

    def recalculate_ge_craft_table(self):
        if not hasattr(self, "tree_ge"):
            return

        strat = self.var_strat.get().split()[0] if hasattr(self, "var_strat") else "patient"
        sell_strat = self.var_ge_sell_strat.get() if hasattr(self, "var_ge_sell_strat") else "patient (Ask)"
        levels = self.state.config.get("player_levels", {})
        only_usable = self.var_ge_only_usable.get() if hasattr(self, "var_ge_only_usable") else False
        skill_filter = self.var_ge_skill.get() if hasattr(self, "var_ge_skill") else "All"
        if " " in skill_filter:
            skill_filter = skill_filter.split()[-1] # strip emoji

        search_query = self.ent_search.get().strip().lower() if hasattr(self, "ent_search") else ""
        if not search_query and hasattr(self, "ent_ge_search"):
            search_query = self.ent_ge_search.get().strip().lower()

        target_margin = 0
        if hasattr(self, "ent_ge_margin"):
            try:
                target_margin = max(0, parse_cash_input(self.ent_ge_margin.get()))
            except Exception:
                target_margin = 0

        min_p_val = None
        if hasattr(self, "ent_ge_min_profit"):
            raw_p = self.ent_ge_min_profit.get().strip().replace(",", "")
            if raw_p:
                try:
                    min_p_val = int(raw_p)
                except ValueError:
                    pass

        mem_ok = self.var_members.get() if hasattr(self, "var_members") else True
        f2p_ok = self.var_f2p.get() if hasattr(self, "var_f2p") else False

        prev_open = {iid for iid in self.tree_ge.get_children() if self.tree_ge.item(iid, "open")}
        self.tree_ge.delete(*self.tree_ge.get_children())
        self.ge_rows = []

        basis = "5m" if hasattr(self, "var_price_basis") and "5m" in self.var_price_basis.get() else self.state.config.get("price_basis", "5m")

        for r in GE_PROFIT_RECIPES:
            req_skill = r["skill"]

            # 1. Strict F2P vs Members Isolation: Herblore & Fletching are 100% P2P in OSRS
            if (f2p_ok and not mem_ok) and req_skill in ("Herblore", "Fletching"):
                continue

            is_mem = (
                r.get("members", True) or
                any(self.api.mapping.get(str(m["id"]), {}).get("members", False) for m in r["materials"]) or
                self.api.mapping.get(str(r["output_id"]), {}).get("members", False)
            )
            if f2p_ok and not mem_ok and is_mem:
                continue
            if not f2p_ok and not mem_ok:
                continue

            # 2. Skill Category Filter
            req_skill = r["skill"]
            if skill_filter != "All" and req_skill.lower() != skill_filter.lower():
                continue

            # 3. Player Level Requirement Check
            req_lvl = r["level"]
            player_lvl = levels.get(req_skill, 99)
            can_make = player_lvl >= req_lvl
            if only_usable and not can_make:
                continue

            # 4. Search Filter
            if search_query:
                name_match = search_query in r["name"].lower()
                mat_match = any(search_query in m["name"].lower() for m in r.get("materials", []))
                skill_match = search_query in req_skill.lower()
                if not name_match and not mat_match and not skill_match:
                    continue

            # 5. Evaluate Material Costs
            bid_total = 0
            ask_total = 0
            strat_total = 0
            valid_mats = True
            mat_info_list = []
            min_limit = 9999999

            for m in r["materials"]:
                mid_str = str(m["id"])
                m_meta = self.api.mapping.get(mid_str, {})
                m_bid, m_ask = self.api.get_bid_ask(mid_str, basis=basis)
                m_strat_p = self.api.get_price(mid_str, strat, basis=basis)
                if not m_strat_p or m_strat_p <= 0:
                    valid_mats = False
                    break

                q = m["qty"]
                bid_total += (m_bid or m_strat_p) * q
                ask_total += (m_ask or m_strat_p) * q
                strat_total += m_strat_p * q

                m_lim = m_meta.get("limit", 10000) or 10000
                if m_lim > 0:
                    min_limit = min(min_limit, m_lim // max(1, q))

                m_vol = self.api.volumes_24h.get(mid_str, 0)
                _, m_spd_badge, _, _ = self.api.get_fill_speed_info(m["id"], q * 100)

                mat_info_list.append({
                    "id": m["id"],
                    "name": m["name"],
                    "qty": q,
                    "bid": m_bid or m_strat_p,
                    "ask": m_ask or m_strat_p,
                    "price_ea": m_strat_p,
                    "limit": m_lim,
                    "vol": m_vol,
                    "speed_badge": m_spd_badge
                })

            if not valid_mats:
                continue

            # 6. Evaluate Output Finished Product
            out_id_str = str(r["output_id"])
            out_meta = self.api.mapping.get(out_id_str, {})
            out_qty = r.get("output_qty", 1)

            out_bid, out_ask = self.api.get_bid_ask(out_id_str, basis=basis)
            gross_sell_ea = out_ask if "patient" in sell_strat.lower() else out_bid
            if not gross_sell_ea or gross_sell_ea <= 0:
                continue

            # OSRS GE Tax (1% on items >= 100 gp, max 5,000,000 gp cap)
            ge_tax_ea = min(5000000, math.floor(gross_sell_ea * 0.01)) if gross_sell_ea >= 100 else 0
            net_sell_ea = gross_sell_ea - ge_tax_ea
            net_revenue = net_sell_ea * out_qty

            # 7. Net Profit & ROI
            profit_ea = net_revenue - strat_total
            if min_p_val is not None and profit_ea < min_p_val:
                continue

            roi_pct = (profit_ea / strat_total * 100.0) if strat_total > 0 else 0.0

            # 8. Hourly Output & Velocity
            actions_per_hr = r.get("hourly_actions", 1500)
            profit_hr = profit_ea * actions_per_hr
            xp_ea = r.get("xp", 0.0)
            xp_hr = int(xp_ea * actions_per_hr)

            # 9. 4h Batch Limits
            batch_limit = min_limit if min_limit < 9999999 else (out_meta.get("limit", 70) or 70)
            batch_profit = profit_ea * batch_limit

            out_vol = self.api.volumes_24h.get(out_id_str, 0)
            _, out_spd_badge, _, out_spd_score = self.api.get_fill_speed_info(r["output_id"], out_qty * 50)

            # 10. Compute Best Buy / Breakeven ceiling for primary material
            sec_cost = sum(m["price_ea"] * m["qty"] for m in mat_info_list[1:])
            primary_m = mat_info_list[0]
            prim_qty = primary_m["qty"]
            net_alloc = net_revenue - sec_cost

            breakeven_p = math.floor(net_alloc / prim_qty) if prim_qty > 0 else 0
            target_buy_p = math.floor((net_alloc - target_margin) / prim_qty) if prim_qty > 0 else 0

            parent_id = f"ge_rec_{r['output_id']}_{r['name']}"
            parent_row = {
                "id": parent_id,
                "name": r["name"],
                "skill": req_skill,
                "level": req_lvl,
                "skill_req": f"{req_skill[:5]} {req_lvl}",
                "can_make": can_make,
                "output_id": r["output_id"],
                "output_qty": out_qty,
                "bid_mat_cost": bid_total,
                "ask_mat_cost": ask_total,
                "strat_mat_cost": strat_total,
                "gross_sell": gross_sell_ea,
                "ge_tax": ge_tax_ea,
                "net_sell": net_sell_ea,
                "net_revenue": net_revenue,
                "profit_ea": profit_ea,
                "roi": roi_pct,
                "limit": batch_limit,
                "batch_profit": batch_profit,
                "profit_hr": profit_hr,
                "xp_ea": xp_ea,
                "xp_hr": xp_hr,
                "speed_badge": out_spd_badge,
                "speed_score": out_spd_score,
                "volume": out_vol,
                "materials": mat_info_list,
                "breakeven_p": breakeven_p,
                "target_buy_p": target_buy_p
            }
            self.ge_rows.append(parent_row)

        # Sort rows
        sort_col = getattr(self, "ge_sort_col", "profit_ea")
        sort_desc = getattr(self, "ge_sort_desc", True)
        if sort_col == "name":
            self.ge_rows.sort(key=lambda x: x["name"].lower(), reverse=sort_desc)
        elif sort_col == "skill":
            self.ge_rows.sort(key=lambda x: (x["skill"], x["level"]), reverse=sort_desc)
        elif sort_col == "speed":
            self.ge_rows.sort(key=lambda x: x["speed_score"], reverse=sort_desc)
        else:
            self.ge_rows.sort(key=lambda x: x.get(sort_col, 0), reverse=sort_desc)

        for p in self.ge_rows:
            prof_str = f"{p['profit_ea']:+,} gp"
            roi_str = f"{p['roi']:+.1f}%"
            b_sign = "+" if p["batch_profit"] >= 0 else "-"
            b_prof_str = f"{b_sign}{format_gp(abs(p['batch_profit']))}"
            hr_prof_str = f"{format_gp(p['profit_hr'])}/hr"
            xp_str = f"{p['xp_ea']:.0f} XP ({format_gp(p['xp_hr'])}/hr)" if p["xp_ea"] > 0 else "--"
            vol_str = f"{p['volume']:,}"

            p_tag = "profit" if p["profit_ea"] >= 0 else "loss"
            if not p["can_make"]:
                p_tag = "locked"

            # Insert parent row
            self.tree_ge.insert("", "end", iid=p["id"], text=f"▶  {p['name']}", values=(
                p["skill_req"],
                f"{p['bid_mat_cost']:,} gp",
                f"{p['ask_mat_cost']:,} gp",
                f"{p['gross_sell']:,} gp",
                prof_str,
                roi_str,
                f"{p['limit']:,}",
                b_prof_str,
                hr_prof_str,
                xp_str,
                p["speed_badge"],
                vol_str
            ), tags=(p_tag,))

            # Insert child ingredients underneath parent
            for idx, m in enumerate(p["materials"]):
                child_id = f"{p['id']}_mat_{m['id']}_{idx}"
                other_mats_cost = sum(other["price_ea"] * other["qty"] for other_idx, other in enumerate(p["materials"]) if other_idx != idx)
                net_alloc_m = p["net_revenue"] - other_mats_cost
                m_qty = m["qty"]
                be_m = math.floor(net_alloc_m / m_qty) if m_qty > 0 else 0
                tb_m = math.floor((net_alloc_m - target_margin) / m_qty) if m_qty > 0 else 0

                ceiling_str = f"🎯 ≤ {tb_m:,} gp" if tb_m > 0 else (f"≤ {be_m:,} gp" if be_m > 0 else "--")
                m_prof_str = f"≤ {be_m:,} be" if be_m > 0 else "--"

                self.tree_ge.insert(p["id"], "end", iid=child_id, text=f"    ↳ {m['qty']}x {m['name']}", values=(
                    "--",
                    f"{m['bid']:,} gp",
                    f"{m['ask']:,} gp",
                    ceiling_str,
                    m_prof_str,
                    "--",
                    f"{m['limit']:,}",
                    f"Cost: {format_gp(m['price_ea'] * m['limit'])}",
                    "--",
                    "--",
                    m["speed_badge"],
                    f"{m['vol']:,}"
                ), tags=("child_row",))

            if p["id"] in prev_open:
                self.tree_ge.item(p["id"], open=True)

    def toggle_sort_ge(self, col):
        if getattr(self, "ge_sort_col", "") == col:
            self.ge_sort_desc = not self.ge_sort_desc
        else:
            self.ge_sort_col = col
            self.ge_sort_desc = False if col in ("name", "skill") else True

        arrow = " ▼" if self.ge_sort_desc else " ▲"
        headers = {
            "name": ("#0", "Item / Ingredients (▶ Expand)"),
            "skill": ("skill_lvl", "Skill & Req"),
            "offer_bid": ("offer_bid", "Target Offer (Bid)"),
            "instant_ask": ("instant_ask", "Instant Buy (Ask)"),
            "sell_price": ("sell_price", "Target Sell Price"),
            "profit_ea": ("profit_ea", "Profit ea"),
            "roi": ("roi", "ROI %"),
            "limit": ("limit", "4h Limit"),
            "batch_profit": ("batch_profit", "4h Batch Profit"),
            "profit_hr": ("profit_hr", "Profit / Hr"),
            "xp": ("xp_info", "XP (ea & /hr)"),
            "speed": ("speed", "Fill Speed"),
            "volume": ("volume", "24h Volume")
        }
        for sort_k, (col_id, title) in headers.items():
            self.tree_ge.heading(col_id, text=title + (arrow if self.ge_sort_col == sort_k else ""))

        self.recalculate_ge_craft_table()

    def expand_all_ge(self):
        for iid in self.tree_ge.get_children():
            self.tree_ge.item(iid, open=True)

    def collapse_all_ge(self):
        for iid in self.tree_ge.get_children():
            self.tree_ge.item(iid, open=False)

    def on_ge_search_changed(self, event=None):
        if hasattr(self, "ent_ge_search") and hasattr(self, "ent_search"):
            val = self.ent_ge_search.get()
            if self.ent_search.get() != val:
                self.ent_search.delete(0, tk.END)
                self.ent_search.insert(0, val)
        self.on_global_search_changed()

    def on_ge_tree_click(self, event):
        item_id = self.tree_ge.identify_row(event.y)
        col = self.tree_ge.identify_column(event.x)
        if not item_id:
            return

        if col == "#0":
            if self.tree_ge.get_children(item_id):
                cur = self.tree_ge.item(item_id, "open")
                self.tree_ge.item(item_id, open=not cur)
            raw_text = self.tree_ge.item(item_id, "text")
            clean_name = raw_text.replace("▶", "").replace("↳", "").strip()
            if "x " in clean_name and clean_name[:3].replace("x", "").strip().isdigit():
                clean_name = clean_name.split("x ", 1)[-1].strip()
            self.copy_to_clipboard(clean_name, f"Copied '{clean_name}' to clipboard!")
            return

        if col == "#2":
            val_str = self.tree_ge.set(item_id, "offer_bid").replace("gp", "").replace(",", "").strip()
            if val_str.isdigit():
                self.copy_to_clipboard(val_str, f"Copied Target Offer (Bid): {int(val_str):,} gp to clipboard!")
            return

        if col == "#3":
            val_str = self.tree_ge.set(item_id, "instant_ask").replace("gp", "").replace(",", "").strip()
            if val_str.isdigit():
                self.copy_to_clipboard(val_str, f"Copied Instant Buy (Ask): {int(val_str):,} gp to clipboard!")
            return

        if col == "#4":
            raw_val = self.tree_ge.set(item_id, "sell_price")
            clean_p = "".join(c for c in raw_val if c.isdigit())
            if clean_p:
                label = "Best Buy Ceiling" if "≤" in raw_val else "Target Sell Price"
                self.copy_to_clipboard(clean_p, f"Copied {label}: {int(clean_p):,} gp to clipboard!")
            return

    def on_ge_tree_double_click(self, event):
        item_id = self.tree_ge.identify_row(event.y)
        if item_id and self.tree_ge.get_children(item_id):
            cur = self.tree_ge.item(item_id, "open")
            self.tree_ge.item(item_id, open=not cur)

    def on_ge_context_menu(self, event):
        item_id = self.tree_ge.identify_row(event.y)
        if not item_id:
            return
        self.tree_ge.selection_set(item_id)
        menu = tk.Menu(self, tearoff=0, bg="#252528", fg="#ffffff", activebackground="#f39c12", activeforeground="#000000")

        raw_text = self.tree_ge.item(item_id, "text")
        clean_name = raw_text.replace("▶", "").replace("↳", "").strip()
        if "x " in clean_name and clean_name[:3].replace("x", "").strip().isdigit():
            clean_name = clean_name.split("x ", 1)[-1].strip()

        menu.add_command(label=f"📋 Copy Name: {clean_name}", command=lambda: self.copy_to_clipboard(clean_name, f"Copied '{clean_name}'"))

        bid_str = self.tree_ge.set(item_id, "offer_bid").replace("gp", "").replace(",", "").strip()
        if bid_str.isdigit():
            menu.add_command(label=f"🎯 Copy Target Offer (Bid): {int(bid_str):,} gp", command=lambda: self.copy_to_clipboard(bid_str, f"Copied Target Offer (Bid): {int(bid_str):,} gp"))

        ask_str = self.tree_ge.set(item_id, "instant_ask").replace("gp", "").replace(",", "").strip()
        if ask_str.isdigit():
            menu.add_command(label=f"⚡ Copy Instant Buy (Ask): {int(ask_str):,} gp", command=lambda: self.copy_to_clipboard(ask_str, f"Copied Instant Buy (Ask): {int(ask_str):,} gp"))

        sell_str = self.tree_ge.set(item_id, "sell_price")
        clean_num = "".join(c for c in sell_str if c.isdigit())
        if clean_num:
            lbl = f"🎯 Copy Best Buy Ceiling: {int(clean_num):,} gp" if "≤" in sell_str else f"🏪 Copy Target Sell Price: {int(clean_num):,} gp"
            menu.add_command(label=lbl, command=lambda: self.copy_to_clipboard(clean_num, f"Copied Target Sell Price: {int(clean_num):,} gp"))

        menu.add_separator()
        slug = clean_name.replace(" ", "_")
        menu.add_command(label="🌐 Open OSRS Wiki", command=lambda: webbrowser.open(f"https://oldschool.runescape.wiki/w/{slug}"))

        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    def get_ge_craft_row_tooltip(self, iid):
        try:
            if "_mat_" in str(iid):
                raw_text = self.tree_ge.item(iid, "text")
                clean_name = raw_text.replace("↳", "").strip()
                bid_val = self.tree_ge.set(iid, "offer_bid")
                ask_val = self.tree_ge.set(iid, "instant_ask")
                target_val = self.tree_ge.set(iid, "sell_price")
                return {
                    "title": f"Ingredient: {clean_name}",
                    "subtitle": "Raw Material Requirement",
                    "title_color": "#f39c12",
                    "rows": [
                        ("Target Offer (Bid):", bid_val, "#2ecc71"),
                        ("Instant Buy (Ask):", ask_val, "#f1f1f1"),
                        ("🎯 Best Buy Ceiling:", target_val, "#3498db"),
                        ("4h GE Limit:", self.tree_ge.set(iid, "limit"), "#f1f1f1"),
                        ("24h Volume:", self.tree_ge.set(iid, "volume"), "#f1f1f1")
                    ],
                    "warnings": [],
                    "has_warning": False,
                    "hint": "💡 Click Target Offer (Bid) or Best Buy to copy price to clipboard"
                }

            row = next((r for r in getattr(self, "ge_rows", []) if r["id"] == str(iid)), None)
            if not row:
                return None

            p_ea = row["profit_ea"]
            rows = [
                ("Skill & Lvl:", f"{row['skill']} (Level {row['level']})", "#f1f1f1" if row["can_make"] else "#e74c3c"),
                ("Total Mat Cost (Bid):", f"{row['bid_mat_cost']:,} gp", "#f1f1f1"),
                ("Total Mat Cost (Ask):", f"{row['ask_mat_cost']:,} gp", "#f1f1f1"),
                ("Target Sell Price (List on GE):", f"{row['gross_sell']:,} gp", "#f1c40f"),
                ("GE Tax Deduction (1%):", f"-{row['ge_tax']:,} gp", "#e74c3c"),
                ("Net GE Revenue:", f"{row['net_revenue']:,} gp", "#2ecc71"),
                ("Net Profit ea:", f"{p_ea:+,} gp ({row['roi']:+.1f}%)", "#2ecc71" if p_ea >= 0 else "#e74c3c"),
                ("Hourly Profit:", f"{format_gp(row['profit_hr'])}/hr", "#2ecc71" if row["profit_hr"] >= 0 else "#e74c3c"),
                ("4h Batch Profit:", f"{format_gp(row['batch_profit'])} (full {row['limit']:,} batch)", "#f39c12")
            ]

            warnings = []
            if not row["can_make"]:
                warnings.append(f"Level Requirement Unmet: Requires Level {row['level']} {row['skill']}.")

            return {
                "title": f"Production: {row['name']}",
                "subtitle": f"{row['skill']} • Level {row['level']}",
                "title_color": "#2ecc71" if p_ea >= 250 else ("#f1c40f" if p_ea >= 0 else "#e74c3c"),
                "rows": rows,
                "warnings": warnings,
                "has_warning": bool(warnings),
                "hint": "💡 Click [▶] to expand ingredients | Click Target Offer cell to copy price"
            }
        except Exception:
            return None

    def on_owned_nat_changed(self, event=None):
        raw = self.ent_owned_nat.get().strip().replace(",", "")
        try:
            val = int(raw) if raw else 0
            self.state.config["owned_nature_runes"] = max(0, val)
            self.save_preferences()
            self.update_cart_display()
        except ValueError:
            pass

    def update_cart_display(self):
        use_cash = self.var_use_cash.get()
        cash_stack = self.state.config.get("cash_stack", 5000000)
        strat = self.var_strat.get().split()[0]
        total_cost = 0
        total_exp_profit = 0
        slots_used = len(self.state.cart_items)
        total_alchs = sum(self.state.cart_items.values())

        for iid_str, qty in self.state.cart_items.items():
            row = next((r for r in self.alch_rows if str(r["id"]) == iid_str), None)
            if row:
                total_cost += row["buy_at"] * qty
                total_exp_profit += row["profit_ea"] * qty
            else:
                p = self.api.get_price(iid_str, strat)
                total_cost += p * qty

        # F2P vs Members GE slot cap
        max_slots = 3 if (self.var_f2p.get() and not self.var_members.get()) else 8

        if use_cash:
            remaining = cash_stack - total_cost
            slot_color = "#e74c3c" if (slots_used > max_slots or remaining < 0) else "#2ecc71"
            budget_str = f"Left: {format_gp(remaining)}"
        else:
            slot_color = "#e74c3c" if slots_used > max_slots else "#2ecc71"
            budget_str = "Budget: Unlimited"

        # Estimated Alch Time at 1,200 alchs/hr (20 alchs/min)
        time_part = ""
        if total_alchs > 0:
            alch_mins = math.ceil(total_alchs / 20)
            if alch_mins >= 60:
                h = alch_mins // 60
                m = alch_mins % 60
                time_part = f"  |  ⏱️ ~{h}h {m}m ({total_alchs:,} alchs)"
            else:
                time_part = f"  |  ⏱️ ~{alch_mins}m ({total_alchs:,} alchs)"

        # Nature Rune Stockpile check
        nat_part = ""
        if total_alchs > 0:
            owned_nats = self.state.config.get("owned_nature_runes", 0)
            if owned_nats >= total_alchs:
                nat_part = f"  |  🌿 Nats: {total_alchs:,}/{owned_nats:,} OK"
            else:
                shortage = total_alchs - owned_nats
                nat_part = f"  |  ⚠️ Buy {shortage:,} Nats"

        if slots_used == 0:
            cart_text = f"🛒 0/{max_slots} Slots  |  Budget: {format_gp(cash_stack) if use_cash else 'Unlimited'}"
        else:
            p_sign = "+" if total_exp_profit >= 0 else "-"
            cart_text = f"🛒 {slots_used}/{max_slots}  |  Cost: {format_gp(total_cost)}  |  {budget_str}  |  {p_sign}{format_gp(abs(total_exp_profit))}{time_part}{nat_part}"

        self.lbl_cart_status.config(
            text=cart_text,
            fg=slot_color
        )

    def update_session_display(self):
        history = self.state.session.get("history", [])
        curr_sel = self.var_account.get() if getattr(self, "var_account", None) else "All Accounts"
        search_query = self.ent_search.get().strip().lower() if hasattr(self, "ent_search") else ""

        if curr_sel != "All Accounts":
            filtered = [h for h in history if h.get("account", "Default") == curr_sel]
            total_alchs = sum(h.get("qty", 0) for h in filtered)
            total_profit = sum(h.get("profit", 0) for h in filtered)
            total_xp = total_alchs * 65.0
        else:
            filtered = history
            total_alchs = self.state.session.get("total_alchs", 0)
            total_profit = self.state.session.get("total_profit", 0)
            total_xp = self.state.session.get("total_xp", 0)

        self.card_alchs.config(text=f"{total_alchs:,}")
        self.card_profit.config(text=format_gp(total_profit))
        self.card_xp.config(text=f"{total_xp:,.0f} XP")
        self.card_nats.config(text=f"{total_alchs:,}")

        self.tree_session.delete(*self.tree_session.get_children())
        table_rows = [h for h in filtered if not search_query or (search_query in h.get("item", "").lower() or search_query in h.get("account", "").lower())]

        view_mode = getattr(self, "session_view_mode", "consolidated")
        if view_mode == "consolidated":
            self.tree_session.configure(show="tree headings")
            self.tree_session.heading("#0", text="📅 Breakdown / Stack")

            # Group by Date
            today_str = time.strftime("%Y-%m-%d")
            yesterday_str = time.strftime("%Y-%m-%d", time.localtime(time.time() - 86400))

            days_map = {}
            for h in table_rows:
                ts = h.get("timestamp")
                if ts:
                    d_str = time.strftime("%Y-%m-%d", time.localtime(ts))
                else:
                    d_str = today_str
                days_map.setdefault(d_str, []).append(h)

            sorted_days = sorted(days_map.keys(), reverse=True)
            for d_str in sorted_days:
                day_entries = days_map[d_str]
                day_qty = sum(e.get("qty", 0) for e in day_entries)
                day_profit = sum(e.get("profit", 0) for e in day_entries)
                day_label = f"📅 Today ({d_str})" if d_str == today_str else (f"📅 Yesterday ({d_str})" if d_str == yesterday_str else f"📅 {d_str}")

                day_prof_str = f"+{format_gp(day_profit)}" if day_profit >= 0 else f"-{format_gp(abs(day_profit))}"
                day_iid = f"day_{d_str}"

                # Group by Item within day
                items_map = {}
                for e in day_entries:
                    items_map.setdefault(e.get("item", "Unknown"), []).append(e)

                self.tree_session.insert("", "end", iid=day_iid, text=day_label, values=(
                    f"{len(day_entries)} fills",
                    curr_sel if curr_sel != "All Accounts" else "All",
                    f"{len(items_map)} item types",
                    f"{day_qty:,}",
                    "—",
                    "—",
                    "—",
                    day_prof_str
                ), open=True)

                # Sort items by total profit descending
                sorted_items = sorted(items_map.items(), key=lambda kv: sum(x.get("profit", 0) for x in kv[1]), reverse=True)
                for item_name, item_entries in sorted_items:
                    it_qty = sum(x.get("qty", 0) for x in item_entries)
                    it_profit = sum(x.get("profit", 0) for x in item_entries)
                    total_spend = sum(x.get("qty", 0) * x.get("buy_price", 0) for x in item_entries)
                    total_nat = sum(x.get("qty", 0) * x.get("nat_price", 0) for x in item_entries)
                    avg_buy = int(round(total_spend / it_qty)) if it_qty > 0 else 0
                    avg_nat = int(round(total_nat / it_qty)) if it_qty > 0 else 0
                    alch_val = item_entries[0].get("alch_val", 0)
                    acc_str = item_entries[0].get("account", "Default") if len(set(x.get("account") for x in item_entries)) == 1 else "Multi"

                    it_prof_str = f"+{format_gp(it_profit)}" if it_profit >= 0 else f"-{format_gp(abs(it_profit))}"
                    item_iid = f"item_{d_str}_{item_name.replace(' ', '_')}"

                    self.tree_session.insert(day_iid, "end", iid=item_iid, text=f"  📦 {item_name}", values=(
                        f"{len(item_entries)} fills",
                        acc_str,
                        item_name,
                        f"{it_qty:,}",
                        f"{avg_buy:,} gp",
                        f"{avg_nat:,} gp",
                        f"{alch_val:,} gp",
                        it_prof_str
                    ), open=True)

                    # Individual fills
                    for idx, h in enumerate(item_entries):
                        p = h.get("profit", 0)
                        p_str = f"+{format_gp(p)}" if p >= 0 else f"-{format_gp(abs(p))}"
                        fill_iid = h.get("id")
                        self.tree_session.insert(item_iid, "end", iid=fill_iid, text=f"    ↳ Fill #{idx + 1} ({h.get('time')})", values=(
                            h.get("time"),
                            h.get("account", "Default"),
                            h.get("item"),
                            f"{h.get('qty', 0):,}",
                            f"{h.get('buy_price', 0):,} gp",
                            f"{h.get('nat_price', 0):,} gp",
                            f"{h.get('alch_val', 0):,} gp",
                            p_str
                        ))
        else:
            # Detailed Flat Mode with Interactive Column Sorting
            self.tree_session.configure(show="headings")
            col = getattr(self, "session_sort_col", "time")
            desc = getattr(self, "session_sort_desc", True)

            def get_sort_key(h):
                if col == "time":
                    return h.get("timestamp", 0)
                elif col == "account":
                    return h.get("account", "").lower()
                elif col == "item":
                    return h.get("item", "").lower()
                elif col == "qty":
                    return h.get("qty", 0)
                elif col == "buy_price":
                    return h.get("buy_price", 0)
                elif col == "nat_price":
                    return h.get("nat_price", 0)
                elif col == "alch_val":
                    return h.get("alch_val", 0)
                elif col == "profit":
                    return h.get("profit", 0)
                return 0

            table_rows.sort(key=get_sort_key, reverse=desc)

            for h in table_rows:
                prof = h.get('profit', 0)
                prof_str = f"+{format_gp(prof)}" if prof >= 0 else f"-{format_gp(abs(prof))}"
                self.tree_session.insert("", "end", iid=h.get("id"), values=(
                    h.get("time"),
                    h.get("account", "Default"),
                    h.get("item"),
                    f"{h.get('qty', 0):,}",
                    f"{h.get('buy_price', 0):,} gp",
                    f"{h.get('nat_price', 0):,} gp",
                    f"{h.get('alch_val', 0):,} gp",
                    prof_str
                ))

    def update_timers_display(self):
        self.tree_timers.delete(*self.tree_timers.get_children())
        now = time.time()
        curr_sel = self.var_account.get() if getattr(self, "var_account", None) else "All Accounts"
        search_query = self.ent_search.get().strip().lower() if hasattr(self, "ent_search") else ""

        expired_keys = []
        for iid, tinfo in list(self.state.timers.items()):
            elapsed = now - tinfo.get("bought_time", 0)
            if elapsed >= 14400: # Has hit 0 / expired
                expired_keys.append(iid)
                continue

            acc = tinfo.get("account", "Default")
            if curr_sel != "All Accounts" and acc != curr_sel:
                continue

            item_name = tinfo.get("name", "Item")
            if search_query and search_query not in item_name.lower() and search_query not in acc.lower():
                continue

            left = max(0, 14400 - elapsed)
            hours = int(left // 3600)
            mins = int((left % 3600) // 60)
            secs = int(left % 60)
            time_left_str = f"{hours:02d}h {mins:02d}m {secs:02d}s"

            self.tree_timers.insert("", "end", iid=iid, values=(
                acc,
                item_name,
                f"{tinfo.get('qty', 0):,}",
                time_left_str,
                "Cooldown Active"
            ))

        if expired_keys:
            for k in expired_keys:
                if k in self.state.timers:
                    del self.state.timers[k]
                self.state.notified_timers.discard(k)
            self.state.save_timers()

    def update_alerts_display(self):
        self.lst_alerts.delete(0, tk.END)
        search_query = self.ent_search.get().strip().lower() if hasattr(self, "ent_search") else ""
        for a in self.state.alert_history:
            if search_query and search_query not in a.lower():
                continue
            self.lst_alerts.insert(tk.END, a)

    # ------------------ HOVER ROW TOOLTIPS (QuantScapers Inspired) ------------------

    def get_alch_row_tooltip(self, iid):
        try:
            row = next((r for r in self.alch_rows if str(r["id"]) == str(iid)), None)
            if not row:
                return None

            m_id = row["id"]
            metrics = self.api.get_quote_metrics(m_id)
            nat_cost = self.get_effective_nature_price()
            buy_at = row["buy_at"]
            total_cost = buy_at + nat_cost
            profit_ea = row["profit_ea"]
            roi_pct = (profit_ea / max(1, total_cost) * 100.0) if total_cost > 0 else 0.0

            title_col = "#2ecc71" if profit_ea >= 200 else ("#f1c40f" if profit_ea >= 0 else "#e74c3c")
            speed_badge = row["speed_badge"]
            if "Fast" in speed_badge:
                speed_col = "#2ecc71"
            elif "Steady" in speed_badge:
                speed_col = "#3498db"
            elif "Stale" in speed_badge:
                speed_col = "#e67e22"
            else:
                speed_col = "#95a5a6"

            limit_info = f"{row['effective_limit']:,}"
            if row.get("is_vol_capped"):
                limit_info = f"{row['effective_limit']:,} (Capped from {row['base_limit']:,})"

            p_hr_k = row["profit_hr"] / 1000.0

            rows = [
                ("Target Offer (Bid):", f"{row['bid']:,} gp", "#f1f1f1"),
                ("Instant Buy (Ask):", f"{row['ask']:,} gp ({metrics['spread_pct']:.1f}% sprd)", "#f1f1f1"),
                ("Nature Rune Cost:", f"{nat_cost:,} gp", "#95a5a6"),
                ("High Alch Value:", f"{row['alch_val']:,} gp", "#f1c40f"),
                ("Net Profit / Alch:", f"{profit_ea:+,} gp ({roi_pct:+.1f}%)", "#2ecc71" if profit_ea >= 0 else "#e74c3c"),
                ("Profit / Hr (1.2k):", f"{p_hr_k:+.1f}k GP/hr", "#2ecc71" if p_hr_k >= 0 else "#e74c3c"),
                ("Fill Velocity:", speed_badge, speed_col),
                ("24h Traded Volume:", f"{row['volume']:,} items", "#f1f1f1"),
                ("5m Sells into Bids:", f"{metrics['vol_5m_low']:,} items @ ~{metrics['avg_low']:,} gp" if metrics['vol_5m_low'] > 0 else "0 items", "#2ecc71" if metrics['vol_5m_low'] >= 3 else ("#f1c40f" if metrics['vol_5m_low'] > 0 else "#e74c3c")),
                ("5m Buys from Asks:", f"{metrics['vol_5m_high']:,} items @ ~{metrics['avg_high']:,} gp" if metrics['vol_5m_high'] > 0 else "0 items", "#3498db" if metrics['vol_5m_high'] > 0 else "#95a5a6"),
                ("5m Total Traded:", f"{metrics['vol_5m_total']:,} items (~{metrics['vol_5m_total'] * 12:,}/hr)", "#2ecc71" if metrics['vol_5m_total'] >= 10 else "#f1f1f1"),
                ("4h Buy Limit:", limit_info, "#e67e22" if row.get("is_vol_capped") else "#f1f1f1"),
                ("4h Batch Profit:", f"{row['batch_profit']:+,} gp", "#2ecc71" if row["batch_profit"] >= 0 else "#e74c3c"),
                ("Quote Freshness:", metrics["age_str"], "#e67e22" if metrics["is_stale"] else "#95a5a6"),
            ]

            if hasattr(self, "var_price_basis"):
                basis = "5m" if "5m" in self.var_price_basis.get() else "latest"
            else:
                basis = self.state.config.get("price_basis", "5m")
            if basis == "latest":
                if metrics['vol_5m_low'] >= 3:
                    verdict_txt = f"✓ Real Activity ({metrics['vol_5m_low']} sold in 5m) - Worth bidding!"
                    verdict_col = "#2ecc71"
                elif metrics['vol_5m_low'] in (1, 2):
                    verdict_txt = f"⚠️ Low Activity ({metrics['vol_5m_low']} sold in 5m) - Small batch recommended"
                    verdict_col = "#f1c40f"
                else:
                    verdict_txt = "⚠️ No 5m Sales Recorded (0 sold) - Potential outlier tick"
                    verdict_col = "#e74c3c"
                rows.insert(7, ("1-Tick Activity:", verdict_txt, verdict_col))

            warnings = []
            if metrics.get("is_spike"):
                warnings.append(
                    f"1-Item Spike Detected: Latest 1-trade price ({metrics['latest_low']:,} gp) is {metrics['spike_pct']:.1f}% below 5m volume average ({metrics['avg_low']:,} gp with only {metrics['vol_5m_low']} sold). Unlikely to fill full batch."
                )
            if metrics["is_stale"]:
                warnings.append(f"Stale Quote: Last GE trade was {metrics['age_str']}. Check in-game GE price.")
            if row.get("is_vol_capped"):
                warnings.append(f"Volume Capped: 24h volume ({row['volume']:,}) < 4h limit ({row['base_limit']:,}). Batch profit adjusted.")
            if metrics["is_wide_spread"]:
                warnings.append(f"Wide Spread ({metrics['spread_pct']:.1f}%): Low liquidity. Offer may take long to fill.")

            return {
                "title": row["name"],
                "subtitle": f"ID: {m_id}",
                "title_color": title_col,
                "rows": rows,
                "warnings": warnings,
                "has_warning": bool(warnings),
                "hint": "💡 Click Bid/Ask to copy price | Double-click row to add to cart"
            }
        except Exception:
            return None

    def get_craft_row_tooltip(self, iid):
        try:
            item_text = self.tree_craft.item(iid, "text").strip()
        except Exception:
            return None
        if not item_text:
            return None

        # If it's a sub-ingredient row
        if item_text.startswith("↳"):
            clean_name = item_text.lstrip("↳").strip()
            parent_id = self.tree_craft.parent(iid)
            parent_text = self.tree_craft.item(parent_id, "text").strip() if parent_id else "Recipe"
            return {
                "title": f"Ingredient: {clean_name}",
                "subtitle": f"For {parent_text}",
                "title_color": "#95a5a6",
                "rows": [("Material:", clean_name, "#f1f1f1")],
                "warnings": [],
                "has_warning": False,
                "hint": "💡 Click cell to copy ingredient name to clipboard"
            }

        # Parent Recipe row
        cr = next((r for r in self.craft_rows if r["recipe"] == item_text), None)
        if not cr:
            return None

        p_ea = cr["profit_ea"]
        bonus = cr["bonus"]
        hr_p = cr["hr_profit"] / 1000.0

        rows = [
            ("Skill Required:", cr["skill_req"], "#f1c40f" if not cr["can_make"] else "#f1f1f1"),
            ("Materials Total:", f"{cr['mat_cost']:,} gp", "#f1f1f1"),
            ("Nature Rune Cost:", f"{cr['nat_cost']:,} gp", "#95a5a6"),
            ("High Alch Value:", f"{cr['alch_val']:,} gp", "#f1c40f"),
            ("Craft + Alch Profit:", f"{p_ea:+,} gp ea", "#2ecc71" if p_ea >= 0 else "#e74c3c"),
            ("Bonus vs Buy Finished:", f"{bonus:+,} gp", "#2ecc71" if bonus >= 0 else "#e74c3c"),
            ("Est GP / Hr:", f"{hr_p:+.1f}k GP/hr", "#2ecc71" if hr_p >= 0 else "#e74c3c"),
            ("XP Earned / Item:", f"{cr['xp']} Craft/Fletch + 65 Magic", "#3498db")
        ]

        warnings = []
        if not cr["can_make"]:
            warnings.append(f"Level Requirement Unmet: You need {cr['skill_req']} to craft this item.")

        return {
            "title": f"Recipe: {cr['recipe']}",
            "subtitle": cr["skill_req"],
            "title_color": "#2ecc71" if p_ea >= 250 else ("#f1c40f" if p_ea >= 0 else "#e74c3c"),
            "rows": rows,
            "warnings": warnings,
            "has_warning": bool(warnings),
            "hint": "💡 Click row to copy name | Click [+] to expand ingredient breakdown"
        }

    # ------------------ CLICKS, EXPORTS & ACTIONS ------------------

    def on_alch_click(self, event):
        item_id = self.tree_alch.identify_row(event.y)
        if not item_id:
            return
        col_id = self.tree_alch.identify_column(event.x)
        row = next((r for r in self.alch_rows if str(r["id"]) == item_id), None)
        if not row:
            return

        # col_id corresponds to display column: #1 (Cart), #2 (Name), #3 (Bid), #4 (Ask)
        if col_id == "#1":
            qty_in_cart = self.state.cart_items.get(item_id, 0)
            if qty_in_cart > 0:
                self.copy_to_clipboard(str(qty_in_cart), f"Copied Quantity: {qty_in_cart:,} ({row['name']})")
            else:
                max_aff = row.get("max_afford", 1)
                self.copy_to_clipboard(str(max_aff), f"Copied Quantity: {max_aff:,} ({row['name']})")
        elif col_id == "#3":
            self.copy_to_clipboard(str(row["bid"]), f"Copied Bid Price: {row['bid']:,} gp ({row['name']})")
        elif col_id == "#4":
            self.copy_to_clipboard(str(row["ask"]), f"Copied Ask Price: {row['ask']:,} gp ({row['name']})")
        else:
            self.copy_to_clipboard(row["name"], f"Copied '{row['name']}' to clipboard!")

    def on_alch_double_click(self, event):
        item_id = self.tree_alch.identify_row(event.y)
        if not item_id:
            return
        if item_id in self.state.cart_items:
            del self.state.cart_items[item_id]
            self.lbl_status_right.config(text="Removed item from cart", fg="#888888")
        else:
            row = next((r for r in self.alch_rows if str(r["id"]) == item_id), None)
            if row:
                base_limit = row.get("base_limit", row["limit"]) if row.get("base_limit", 0) > 0 else (row["limit"] if row["limit"] > 0 else 70)
                rem_limit, secs_left, is_cd = self.state.get_remaining_limit(row["id"], base_limit)

                if is_cd and rem_limit <= 0:
                    hours = int(secs_left // 3600)
                    mins = int((secs_left % 3600) // 60)
                    self.lbl_status_right.config(
                        text=f"Cannot add {row['name']}: 4h GE cooldown active for {hours}h {mins:02d}m!",
                        fg="#e74c3c"
                    )
                    return

                limit_cap = row.get("effective_limit", rem_limit if is_cd else (base_limit if base_limit > 0 else 70))
                use_cash = self.var_use_cash.get()

                if use_cash:
                    cash_stack = self.state.config.get("cash_stack", 5000000)
                    strat = self.var_strat.get().split()[0]
                    allocated_so_far = sum(
                        self.api.get_price(iid, strat) * q
                        for iid, q in self.state.cart_items.items()
                    )
                    remaining_budget = max(0, cash_stack - allocated_so_far)
                    buy_price = max(1, row["buy_at"])

                    afford_with_remaining = remaining_budget // buy_price
                    qty = min(limit_cap, afford_with_remaining)

                    if qty <= 0:
                        if remaining_budget < buy_price:
                            self.lbl_status_right.config(
                                text=f"Cannot add {row['name']}: remaining budget ({format_gp(remaining_budget)}) < item price ({format_gp(buy_price)})! (Uncheck Cash Stack for unlimited)",
                                fg="#e74c3c"
                            )
                            return
                        qty = 1
                else:
                    qty = limit_cap

                self.state.cart_items[item_id] = qty
                self.lbl_status_right.config(
                    text=f"Added {qty:,}x {row['name']} to cart ({format_gp(qty * row['buy_at'])})",
                    fg="#2ecc71"
                )

        self.recalculate_alch_table()
        self.update_cart_display()

    def on_alch_right_click(self, event):
        item_id = self.tree_alch.identify_row(event.y)
        if not item_id:
            return
        row = next((r for r in self.alch_rows if str(r["id"]) == item_id), None)
        if not row:
            return

        current_qty = self.state.cart_items.get(item_id, 0)
        base_limit = row.get("base_limit", row["limit"]) if row.get("base_limit", 0) > 0 else (row["limit"] if row["limit"] > 0 else 1000)
        rem_limit, _, is_cd = self.state.get_remaining_limit(row["id"], base_limit)
        max_allowed = rem_limit if is_cd else base_limit
        if max_allowed <= 0:
            max_allowed = 1000

        def save_qty(new_qty):
            if new_qty <= 0:
                if item_id in self.state.cart_items:
                    del self.state.cart_items[item_id]
                self.lbl_status_right.config(text=f"Removed {row['name']} from cart", fg="#888888")
            else:
                self.state.cart_items[item_id] = new_qty
                self.lbl_status_right.config(text=f"Set {new_qty:,}x {row['name']} in cart", fg="#2ecc71")
            self.recalculate_alch_table()
            self.update_cart_display()

        SetQuantityDialog(self, row["name"], current_qty, max_allowed, save_qty)

    def auto_fill_ge_slots(self):
        curr_cart_count = len(self.state.cart_items)
        empty_slots = 8 - curr_cart_count
        if empty_slots <= 0:
            messagebox.showinfo(
                "GE Slots Full",
                f"All 8 Grand Exchange slots are already filled in your Shopping Cart ({curr_cart_count}/8)!\n\n"
                "Clear or remove items from your cart before auto-filling."
            )
            return

        strat = self.var_strat.get().split()[0] if hasattr(self, "var_strat") else "smart"
        cash_stack = self.state.config.get("cash_stack", 5000000)
        use_cash = self.var_use_cash.get() if hasattr(self, "var_use_cash") else True

        allocated_so_far = sum(
            self.api.get_price(iid, strat) * q
            for iid, q in self.state.cart_items.items()
        )
        remaining_budget = max(0, cash_stack - allocated_so_far) if use_cash else 999_999_999

        if use_cash and remaining_budget < 5000:
            messagebox.showwarning(
                "Budget Fully Allocated",
                f"Your Cash Stack budget ({format_gp(cash_stack)}) is already fully allocated across existing cart items ({format_gp(allocated_so_far)}).\n\n"
                "Increase your Cash Stack or remove cart items to allocate more slots."
            )
            return

        if not self.rec_rows:
            self.recalculate_rec_table()

        candidates = []
        for r in self.rec_rows:
            iid_str = str(r["id"])
            if iid_str in self.state.cart_items:
                continue
            if r["profit_ea"] <= 0:
                continue

            base_limit = r.get("limit", 70)
            rem_limit, _, is_cd = self.state.get_remaining_limit(r["id"], base_limit)
            if rem_limit <= 0:
                continue

            buy_price = max(1, r["buy_at"])
            if use_cash and buy_price > remaining_budget:
                continue

            candidates.append(r)

        if not candidates:
            messagebox.showinfo(
                "No Available Recommendations",
                "No eligible items found to auto-fill.\n\n"
                "Items may already be in your cart, on 4-hour cooldown, or exceed your remaining budget."
            )
            return

        added_count = 0
        total_spent = 0
        total_profit = 0
        budget_left = remaining_budget

        for r in candidates:
            if added_count >= empty_slots:
                break

            iid_str = str(r["id"])
            buy_price = max(1, r["buy_at"])
            rem_limit = r["rem_limit"]

            if use_cash:
                max_units = budget_left // buy_price
                qty = min(rem_limit, max_units)
            else:
                qty = rem_limit

            if qty <= 0:
                continue

            self.state.cart_items[iid_str] = qty
            cost = qty * buy_price
            budget_left -= cost
            total_spent += cost
            total_profit += qty * r["profit_ea"]
            added_count += 1

        self.recalculate_alch_table()
        self.update_cart_display()
        self.recalculate_rec_table()

        msg = f"Auto-filled {added_count} empty GE slots! Allocated {format_gp(total_spent)} (Est. Profit: +{format_gp(total_profit)})"
        self.lbl_status_right.config(text=f"⚡ {msg}", fg="#2ecc71")
        if self.state.config.get("desktop_alerts"):
            FloatingToast(self, "⚡ GE Slots Auto-Filled", msg)
        else:
            messagebox.showinfo("Auto-Fill Completed", f"Successfully added {added_count} items to your shopping cart!\n\n• Gold Allocated: {format_gp(total_spent)}\n• Projected Profit: +{format_gp(total_profit)}\n• Slots Used: {len(self.state.cart_items)}/8")

    def copy_all_recs(self):
        if not self.rec_rows:
            return
        cat = self.var_rec_cat.get() if hasattr(self, "var_rec_cat") else "workhorse"
        timing = get_market_timing_info()
        lines = [
            f"=== OSRS Smart Picks ({cat.title()}) [{timing['time_str']}] ===",
            f"Status: {timing['badge']}",
            ""
        ]
        for r in self.rec_rows[:15]:
            lines.append(f"{r['badge']} {r['name']} | Bid: {r['bid']:,} gp | Alch: {r['alch_val']:,} gp | Profit: +{r['profit_ea']:,} gp | Limit: {r['limit']} (Batch: +{r['batch_profit']:,} gp) | {r['speed_badge']}")
        text = "\n".join(lines)
        self.clipboard_clear()
        self.clipboard_append(text)
        self.lbl_status_right.config(text=f"📋 Copied {len(self.rec_rows[:15])} recommendations to clipboard!", fg="#3498db")

    def on_rec_click(self, event):
        item_id = self.tree_rec.identify_row(event.y)
        if not item_id:
            return
        row = next((r for r in self.rec_rows if str(r["id"]) == item_id), None)
        if not row:
            return
        col_id = self.tree_rec.identify_column(event.x)
        if col_id == "#4":
            self.copy_to_clipboard(str(row["bid"]), f"Copied Bid Price: {row['bid']:,} gp ({row['name']})")
        else:
            self.copy_to_clipboard(row["name"], f"Copied '{row['name']}' to clipboard!")

    def on_rec_double_click(self, event):
        item_id = self.tree_rec.identify_row(event.y)
        if not item_id:
            return
        if item_id in self.state.cart_items:
            del self.state.cart_items[item_id]
            self.lbl_status_right.config(text="Removed item from cart", fg="#888888")
        else:
            row = next((r for r in self.rec_rows if str(r["id"]) == item_id), None)
            if row:
                base_limit = row.get("limit", 70)
                rem_limit, secs_left, is_cd = self.state.get_remaining_limit(row["id"], base_limit)
                if is_cd and rem_limit <= 0:
                    hours = int(secs_left // 3600)
                    mins = int((secs_left % 3600) // 60)
                    self.lbl_status_right.config(
                        text=f"Cannot add {row['name']}: 4h GE cooldown active for {hours}h {mins:02d}m!",
                        fg="#e74c3c"
                    )
                    return
                limit_cap = rem_limit if is_cd else base_limit
                use_cash = self.var_use_cash.get() if hasattr(self, "var_use_cash") else True
                if use_cash:
                    cash_stack = self.state.config.get("cash_stack", 5000000)
                    strat = self.var_strat.get().split()[0] if hasattr(self, "var_strat") else "smart"
                    allocated_so_far = sum(
                        self.api.get_price(iid, strat) * q
                        for iid, q in self.state.cart_items.items()
                    )
                    remaining_budget = max(0, cash_stack - allocated_so_far)
                    buy_price = max(1, row["buy_at"])
                    afford = remaining_budget // buy_price
                    qty = min(limit_cap, afford)
                    if qty <= 0:
                        qty = 1 if remaining_budget >= buy_price else 0
                        if qty == 0:
                            self.lbl_status_right.config(
                                text=f"Cannot add {row['name']}: remaining budget ({format_gp(remaining_budget)}) < item price ({format_gp(buy_price)})!",
                                fg="#e74c3c"
                            )
                            return
                else:
                    qty = limit_cap
                self.state.cart_items[item_id] = qty
                self.lbl_status_right.config(
                    text=f"Added {qty:,}x {row['name']} to cart ({format_gp(qty * row['buy_at'])})",
                    fg="#2ecc71"
                )

        self.recalculate_alch_table()
        self.update_cart_display()
        self.recalculate_rec_table()

    def on_rec_right_click(self, event):
        item_id = self.tree_rec.identify_row(event.y)
        if not item_id:
            return
        row = next((r for r in self.rec_rows if str(r["id"]) == item_id), None)
        if not row:
            return

        menu = tk.Menu(self, tearoff=0, bg="#2d2d30", fg="#ffffff", activebackground="#f39c12", activeforeground="#000000")
        menu.add_command(label=f"🛒 Add Full Limit ({row['limit']}x) to Cart", command=lambda: self._rec_add_full(row))
        menu.add_command(label="✏️ Set Custom Quantity in Cart...", command=lambda: self._rec_set_custom_qty(row))
        menu.add_separator()
        menu.add_command(label=f"📋 Copy Item Name ('{row['name']}')", command=lambda: self.copy_to_clipboard(row["name"], f"Copied '{row['name']}'!"))
        menu.add_command(label=f"💰 Copy Target Bid ({row['bid']:,} gp)", command=lambda: self.copy_to_clipboard(str(row["bid"]), f"Copied {row['bid']:,} gp!"))
        menu.add_separator()
        menu.add_command(label="🌐 Open in OSRS Wiki Prices", command=lambda: self.open_wiki_url(row["id"]))
        menu.post(event.x_root, event.y_root)

    def _rec_add_full(self, row):
        item_id = str(row["id"])
        base_limit = row.get("limit", 70)
        rem_limit, _, is_cd = self.state.get_remaining_limit(row["id"], base_limit)
        qty = rem_limit if (is_cd and rem_limit > 0) else base_limit
        self.state.cart_items[item_id] = qty
        self.recalculate_alch_table()
        self.update_cart_display()
        self.recalculate_rec_table()
        self.lbl_status_right.config(text=f"Added {qty}x {row['name']} to cart", fg="#2ecc71")

    def _rec_set_custom_qty(self, row):
        item_id = str(row["id"])
        curr_qty = self.state.cart_items.get(item_id, 0)
        base_limit = row.get("limit", 70)
        rem_limit, _, is_cd = self.state.get_remaining_limit(row["id"], base_limit)
        max_allowed = rem_limit if is_cd else base_limit
        if max_allowed <= 0:
            max_allowed = 1000

        def save_qty(new_qty):
            if new_qty <= 0:
                if item_id in self.state.cart_items:
                    del self.state.cart_items[item_id]
                self.lbl_status_right.config(text=f"Removed {row['name']} from cart", fg="#888888")
            else:
                self.state.cart_items[item_id] = new_qty
                self.lbl_status_right.config(text=f"Set {new_qty:,}x {row['name']} in cart", fg="#2ecc71")
            self.recalculate_alch_table()
            self.update_cart_display()
            self.recalculate_rec_table()

        SetQuantityDialog(self, row["name"], curr_qty if curr_qty > 0 else (rem_limit if rem_limit > 0 else base_limit), max_allowed, save_qty)

    def open_wiki_url(self, item_id):
        url = f"https://prices.runescape.wiki/osrs/item/{item_id}"
        webbrowser.open(url)

    def on_craft_click(self, event):
        item = self.tree_craft.identify_row(event.y)
        if not item:
            return
        try:
            col = self.tree_craft.identify_column(event.x)
            # Toggle tree expansion if clicking tree column
            if col == "#0" and self.tree_craft.get_children(item):
                is_open = self.tree_craft.item(item, "open")
                self.tree_craft.item(item, open=not is_open)

            if col == "#2":
                raw_cost = self.tree_craft.set(item, "mat_cost")
                clean_num = "".join(c for c in raw_cost if c.isdigit())
                if clean_num:
                    self.copy_to_clipboard(clean_num, f"Copied Materials Cost: {int(clean_num):,} gp to clipboard!")
                    return
            elif col == "#3":
                raw_alch = self.tree_craft.set(item, "alch_val")
                clean_num = "".join(c for c in raw_alch if c.isdigit())
                if clean_num:
                    self.copy_to_clipboard(clean_num, f"Copied Alch Value: {int(clean_num):,} gp to clipboard!")
                    return
            elif col == "#4":
                raw_p = self.tree_craft.set(item, "profit_ea")
                clean_num = "".join(c for c in raw_p if c.isdigit())
                if clean_num:
                    self.copy_to_clipboard(clean_num, f"Copied Profit: {int(clean_num):,} gp to clipboard!")
                    return

            text_val = self.tree_craft.item(item, "text").strip().lstrip("+").lstrip("↳").strip()
            if text_val:
                clean_name = text_val.split("(")[0].strip()
                self.copy_to_clipboard(clean_name, f"Copied '{clean_name}' to clipboard!")
        except Exception:
            pass

    def show_status_message(self, message, fg="#f39c12", duration_ms=3000):
        if not hasattr(self, "lbl_status_right"):
            return
        self.lbl_status_right.config(text=message, fg=fg)
        if self.clipboard_clear_timer:
            self.after_cancel(self.clipboard_clear_timer)
        self.clipboard_clear_timer = self.after(duration_ms, lambda: self.lbl_status_right.config(text="Ready", fg="#888888"))

    def copy_to_clipboard(self, text, message=""):
        try:
            self.clipboard_clear()
            self.clipboard_append(str(text))
            self.update_idletasks()
        except Exception:
            try:
                import pyperclip
                pyperclip.copy(str(text))
            except Exception:
                pass
        if message:
            self.show_status_message(message)

    def export_master_bank_tag(self):
        """Exports all currently profitable items matching active filters as a RuneLite bank tag."""
        profitable_ids = [str(r["id"]) for r in self.alch_rows if r["profit_ea"] > 0]
        if not profitable_ids:
            messagebox.showinfo("No Items", "No profitable items found matching your current filters.")
            return

        # Prepend Nature Rune (561) as icon and item
        tag_str = f"banktags,1,alch,561,561," + ",".join(profitable_ids)
        self.copy_to_clipboard(tag_str, f"Copied Master Alch Tag ({len(profitable_ids)} items) to clipboard!")
        messagebox.showinfo("Master Tag Exported",
            f"Successfully copied Master Tag with {len(profitable_ids)} profitable items to clipboard!\n\n"
            "In RuneLite, right-click the '+' tab icon in your bank and click 'Import tag tab'.")

    def export_cart_bank_tag(self):
        """Exports items currently in your shopping cart as a RuneLite bank tag."""
        if not self.state.cart_items:
            messagebox.showinfo("Cart Empty", "Your shopping cart is currently empty. Double-click items to add them first.")
            return

        cart_ids = list(self.state.cart_items.keys())
        tag_str = f"banktags,1,cart,561,561," + ",".join(cart_ids)
        self.copy_to_clipboard(tag_str, f"Copied Cart Tag ({len(cart_ids)} items) to clipboard!")
        messagebox.showinfo("Cart Tag Exported",
            f"Successfully copied Cart Tag ({len(cart_ids)} items) to clipboard!\n\n"
            "In RuneLite, right-click the '+' tab icon in your bank and click 'Import tag tab'.")

    def log_cart_session(self):
        if not self.state.cart_items:
            messagebox.showinfo("Cart Empty", "Double-click items in the High Alch tab to add them to your cart first!")
            return

        count = len(self.state.cart_items)
        nat_cost = self.get_effective_nature_price()

        active_acc = getattr(self.state, "active_account", "Default")
        if not active_acc or active_acc in ("All", "All Accounts"):
            active_acc = self.var_account.get() if getattr(self, "var_account", None) and self.var_account.get() != "All Accounts" else "Default"

        for iid_str, qty in list(self.state.cart_items.items()):
            row = next((r for r in self.alch_rows if str(r["id"]) == iid_str), None)
            if row:
                self.state.log_alch_batch(
                    item_id=row["id"],
                    item_name=row["name"],
                    qty=qty,
                    buy_price=row["buy_at"],
                    nat_price=nat_cost,
                    alch_val=row["alch_val"],
                    account=active_acc
                )
                self.state.add_timer(row["id"], row["name"], qty, account=active_acc)

        self.state.cart_items.clear()
        if hasattr(self, "_ge_tracked_items"):
            self._ge_tracked_items.clear()
        self.recalculate_all()

        messagebox.showinfo("Logged Successfully", f"Logged {count} items into your session tracker and started their 4-hour GE limit timers!\n\nYou can click 'Edit Selected Entry' in the Session Tracker anytime if your actual buy price was different.")

    def open_edit_session_dialog(self):
        selected_id = self.tree_session.selection()
        if not selected_id:
            messagebox.showinfo("Select Entry", "Please select a session history entry to edit.")
            return

        entry_id = selected_id[0]
        entry = next((e for e in self.state.session.get("history", []) if e["id"] == entry_id), None)
        if entry:
            EditSessionDialog(self, entry, self._on_entry_edited)
        else:
            messagebox.showinfo("Select Fill", "Please expand the group and select an individual transaction fill to edit.")

    def _on_entry_edited(self, entry_id, new_qty, new_buy_price, new_nat_price):
        self.state.update_session_entry(entry_id, new_qty, new_buy_price, new_nat_price)
        self.recalculate_all()
        self.show_status_message(f"Session entry updated ({new_qty:,} bought) & 4h GE timer synced!")

    def delete_session_entry(self):
        selected_id = self.tree_session.selection()
        if not selected_id:
            return
        entry_id = selected_id[0]
        entry = next((e for e in self.state.session.get("history", []) if e["id"] == entry_id), None)
        if not entry:
            messagebox.showinfo("Select Fill", "Please expand the group and select an individual transaction fill to delete.")
            return
        if messagebox.askyesno("Delete Entry", f"Delete this transaction fill for {entry['item']} from your session?"):
            self.state.delete_session_entry(entry_id)
            self.recalculate_all()
            self.show_status_message("Session entry deleted & 4h GE timer updated.")

    def clear_cart(self):
        self._ge_cart_slots.clear()
        if hasattr(self, "_ge_tracked_items"):
            self._ge_tracked_items.clear()
        self.state.cart_items.clear()
        self.recalculate_alch_table()
        self.update_cart_display()

    def edit_selected_timer(self):
        selected = self.tree_timers.selection()
        if not selected:
            messagebox.showinfo("Select Timer", "Please select a timer from the list to edit.")
            return

        item_id = selected[0]
        tinfo = self.state.timers.get(item_id)
        if not tinfo:
            return

        EditTimerDialog(self, item_id, tinfo, self._on_timer_edited)

    def _on_timer_edited(self, item_id, new_qty):
        tinfo = self.state.timers.get(item_id)
        item_name = tinfo.get("name", "Item") if tinfo else "Item"
        if new_qty <= 0:
            self.state.remove_timer(item_id)
            self.show_status_message(f"Cleared timer for {item_name} (cooldown reset).")
        else:
            if item_id in self.state.timers:
                self.state.timers[item_id]["qty"] = new_qty
                self.state.save_timers()
                self.show_status_message(f"Updated timer for {item_name} to {new_qty:,} bought.")
        self.recalculate_all()

    def remove_selected_timer(self):
        selected = self.tree_timers.selection()
        if selected:
            for item_id in selected:
                self.state.remove_timer(item_id)
            self.recalculate_all()
            self.show_status_message("Selected cooldown timer(s) removed.")

    def reset_all_timers(self):
        curr_sel = self.var_account.get() if getattr(self, "var_account", None) else "All Accounts"
        prompt_txt = f"Reset all active 4-hour GE cooldown timers for {curr_sel}?" if curr_sel != "All Accounts" else "Reset all active 4-hour GE cooldown timers across all accounts?"
        if messagebox.askyesno("Reset Timers", prompt_txt):
            self.state.reset_all_timers(account=curr_sel)
            self.recalculate_all()
            self.show_status_message(f"All 4h GE timers reset for {curr_sel}.")

    def reset_session(self):
        if messagebox.askyesno("Reset Session", "Are you sure you want to reset all session statistics?"):
            self.state.reset_session()
            self.update_session_display()

    def manual_ge_sync(self):
        """Authoritatively syncs 4-hour buy limits and past trades directly from RuneLite."""
        try:
            res = self.state.sync_from_runelite_ge(self.api.mapping, self.get_effective_nature_price())
            self.update_timers_display()
            self.update_session_display()
            self.recalculate_all()
            t_up = res.get("timers_updated", 0)
            s_up = res.get("session_imported", 0)
            msg = f"GE Sync Complete: {t_up} active timer(s) synced, {s_up} missing trade(s) imported."
            self.show_status_message(msg)
            FloatingToast(self, "🔄 GE Synced", msg)
        except Exception as e:
            self.show_status_message(f"GE Sync Error: {e}")

    def trigger_alert_notification(self, item_name, details, item_id=None):
        if item_id:
            rem_limit, _, is_cd = self.state.get_remaining_limit(item_id, 1000)
            if is_cd and rem_limit <= 0:
                return

        if self.state.config.get("sound_enabled") and HAS_WINSOUND:
            try:
                winsound.MessageBeep(winsound.MB_ICONASTERISK)
            except Exception:
                pass

        if self.state.config.get("desktop_alerts"):
            try:
                FloatingToast(self, "🚨 OSRS High Alch Opportunity!", f"{item_name} spiked to {details}")
            except Exception:
                pass

    # ------------------ TIMERS & SETTINGS ------------------

    def timer_tick(self):
        # Periodic container fallback sync (every 3 seconds)
        if not hasattr(self, "_last_container_check"):
            self._last_container_check = 0
        now = time.time()
        if now - self._last_container_check >= 3.0:
            self._last_container_check = now
            if self._sync_from_container_export():
                self._apply_active_account_data()
                self.recalculate_all()

        # Bridge connection health monitor
        last_bridge = getattr(self, "_last_bridge_event_time", 0)
        curr_acc = self.var_account.get() if hasattr(self, "var_account") else "Default"
        if hasattr(self, "lbl_bridge_status"):
            if last_bridge > 0:
                elapsed = now - last_bridge
                if elapsed <= 8.0:
                    self.lbl_bridge_status.config(text=f"🟢 {curr_acc}", fg="#2ecc71")
                elif elapsed <= 25.0:
                    self.lbl_bridge_status.config(text=f"🟡 {curr_acc} (Delayed)", fg="#f1c40f")
                else:
                    self.lbl_bridge_status.config(text=f"🔴 {curr_acc} (Stale)", fg="#e74c3c")
            else:
                self.lbl_bridge_status.config(text="⚪ Bridge Waiting", fg="#888888")

        if self.state.config.get("auto_refresh_mins", 2) > 0 and not self.is_fetching:
            self.seconds_until_refresh -= 1
            if self.seconds_until_refresh <= 0:
                self.trigger_refresh()
            else:
                m = self.seconds_until_refresh // 60
                s = self.seconds_until_refresh % 60
                self.lbl_countdown.config(text=f"(Next: {m:02d}:{s:02d})")

        expired = self.state.check_expired_timers()
        if expired:
            for exp in expired:
                item_name = exp.get("name") if isinstance(exp, dict) else exp
                acc = exp.get("account", "Default") if isinstance(exp, dict) else "Default"
                acc_tag = f"[{acc}] " if acc != "Default" else ""
                if self.state.config.get("sound_enabled") and HAS_WINSOUND:
                    winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
                if self.state.config.get("desktop_alerts"):
                    FloatingToast(self, f"⏰ {acc_tag}GE 4-Hour Limit Reset!", f"You can now buy {item_name} on the GE again!")
            # Unhide expired items and refresh active watchlists
            self.recalculate_all()
        else:
            self.update_timers_display()

        self.after(1000, self.timer_tick)

    def on_cash_toggle_changed(self):
        use = self.var_use_cash.get()
        self.state.config["use_cash_stack"] = use
        self.save_preferences()
        if use:
            self.ent_cash.config(state="normal")
        else:
            self.ent_cash.config(state="disabled")
        self.recalculate_all()

    def on_cash_changed(self, event=None):
        raw = self.ent_cash.get()
        val = parse_cash_input(raw)
        if val >= 0:
            self.state.config["cash_stack"] = val
            self.ent_cash.delete(0, tk.END)
            self.ent_cash.insert(0, format_gp(val))
            self.save_preferences()
            self.recalculate_all()

    def on_custom_nat_changed(self, event=None):
        raw = self.ent_custom_nat.get().strip()
        try:
            val = int(raw) if raw else 0
            self.state.config["custom_nature_price"] = val
            self.save_preferences()
            self.recalculate_all()
        except ValueError:
            pass

    def on_members_clicked(self):
        if self.var_members.get():
            self.var_f2p.set(False)
            if hasattr(self, "var_guide_members"):
                self.var_guide_members.set(True)
            if hasattr(self, "var_overnight_slots"):
                self.var_overnight_slots.set("8 Slots (P2P)")
        else:
            self.var_f2p.set(True)
            if hasattr(self, "var_guide_members"):
                self.var_guide_members.set(False)
            if hasattr(self, "var_overnight_slots"):
                self.var_overnight_slots.set("3 Slots (F2P)")
        self.on_filter_changed()

    def on_f2p_clicked(self):
        if self.var_f2p.get():
            self.var_members.set(False)
            if hasattr(self, "var_guide_members"):
                self.var_guide_members.set(False)
            if hasattr(self, "var_overnight_slots"):
                self.var_overnight_slots.set("3 Slots (F2P)")
        else:
            self.var_members.set(True)
            if hasattr(self, "var_guide_members"):
                self.var_guide_members.set(True)
            if hasattr(self, "var_overnight_slots"):
                self.var_overnight_slots.set("8 Slots (P2P)")
        self.on_filter_changed()

    def on_filter_changed(self, event=None):
        self.state.config["members"] = self.var_members.get()
        self.state.config["f2p"] = self.var_f2p.get()
        if hasattr(self, "var_guide_members"):
            self.state.config["guide_members"] = self.var_guide_members.get()
        self.state.config["free_alchs_mode"] = self.var_free_alch.get()

        max_s = parse_cash_input(self.ent_max_spend.get())
        if max_s > 0:
            self.state.config["max_item_cost"] = max_s

        min_v = parse_cash_input(self.ent_min_vol.get())
        if min_v >= 0:
            self.state.config["min_volume"] = min_v

        self.save_preferences()
        self.recalculate_all()

    def on_strategy_changed(self, event=None):
        strat = self.var_strat.get().split()[0]
        self.state.config["strategy"] = strat
        self.save_preferences()
        self.recalculate_all()

    def on_speed_filter_changed(self, event=None):
        self.state.config["speed_filter"] = self.var_speed.get()
        self.save_preferences()
        self.recalculate_alch_table()

    def on_refresh_rate_changed(self, event=None):
        val = self.var_refresh.get()
        if "1" in val:
            mins = 1
        elif "2" in val:
            mins = 2
        elif "5" in val:
            mins = 5
        elif "10" in val:
            mins = 10
        else:
            mins = 0
        self.state.config["auto_refresh_mins"] = mins
        self.seconds_until_refresh = mins * 60
        self.save_preferences()

    def on_levels_changed(self, event=None):
        try:
            c = int(self.ent_craft_lvl.get())
            s = int(self.ent_smith_lvl.get()) if hasattr(self, "ent_smith_lvl") else 99
            f = int(self.ent_fletch_lvl.get())
            m = int(self.ent_mage_lvl.get())
            p_lvls = self.state.config.setdefault("player_levels", {})
            p_lvls["Crafting"] = c
            p_lvls["Smithing"] = s
            p_lvls["Fletching"] = f
            p_lvls["Magic"] = m
        except ValueError:
            pass
        self.state.config["only_usable_recipes"] = self.var_only_usable.get()
        self.save_preferences()
        self.recalculate_craft_table()
        if hasattr(self, "var_guide_skill") and hasattr(self, "ent_guide_cur_lvl"):
            g_sk = self.var_guide_skill.get()
            cur_p_lvls = self.state.config.get("player_levels", {})
            if g_sk in cur_p_lvls:
                self.ent_guide_cur_lvl.delete(0, tk.END)
                self.ent_guide_cur_lvl.insert(0, str(cur_p_lvls[g_sk]))
                self.recalculate_guide_table()

    def on_skill_filter_changed(self):
        self.state.config["filter_craft"] = self.var_filter_craft.get()
        self.state.config["filter_smith"] = self.var_filter_smith.get()
        self.state.config["filter_fletch"] = self.var_filter_fletch.get()
        self.state.config["filter_magic"] = self.var_filter_magic.get()
        self.save_preferences()
        self.recalculate_craft_table()

    def select_all_skill_filters(self):
        self.var_filter_craft.set(True)
        self.var_filter_smith.set(True)
        self.var_filter_fletch.set(True)
        self.var_filter_magic.set(True)
        self.on_skill_filter_changed()

    def clear_all_skill_filters(self):
        self.var_filter_craft.set(False)
        self.var_filter_smith.set(False)
        self.var_filter_fletch.set(False)
        self.var_filter_magic.set(False)
        self.on_skill_filter_changed()

    def on_hide_maxed_changed(self):
        self.state.config["hide_maxed_cooldown"] = self.var_hide_maxed.get()
        self.save_preferences()
        self.recalculate_alch_table()

    def on_price_basis_changed(self, event=None):
        val = "5m" if "5m" in self.var_price_basis.get() else "latest"
        self.state.config["price_basis"] = val
        self.save_preferences()
        self.recalculate_all()

    def save_preferences(self):
        self.state.config["sound_enabled"] = self.var_sound.get()
        self.state.config["desktop_alerts"] = self.var_desktop.get()
        if hasattr(self, "var_hide_maxed"):
            self.state.config["hide_maxed_cooldown"] = self.var_hide_maxed.get()
        if hasattr(self, "var_price_basis"):
            self.state.config["price_basis"] = "5m" if "5m" in self.var_price_basis.get() else "latest"
        self.state.save_config()

    # ------------------ RUNELITE BRIDGE HANDLERS & PORT CONFIGURATION ------------------

    def on_bridge_port_changed(self, event=None):
        """Called when the user edits the port Entry in the Settings Drawer."""
        if not hasattr(self, "ent_bridge_port"):
            return
        val = self.ent_bridge_port.get().strip()
        try:
            port = int(val)
            if port != self.bridge_port:
                self.change_bridge_port(port)
        except ValueError:
            self.ent_bridge_port.delete(0, "end")
            self.ent_bridge_port.insert(0, str(self.bridge_port))
            messagebox.showwarning("Invalid Port", "Port must be an integer between 1024 and 65535.")

    def change_bridge_port(self, new_port):
        """Gracefully rebinds the bridge HTTP server to a new port and saves configuration."""
        try:
            new_port = int(new_port)
            if new_port < 1024 or new_port > 65535:
                raise ValueError("Port must be between 1024 and 65535.")
        except Exception as e:
            messagebox.showerror("Invalid Port", f"Please enter a valid port number between 1024 and 65535.\nError: {e}")
            return False

        if new_port == getattr(self, "bridge_port", 18833) and self.bridge_server and self.bridge_server.is_running:
            self.show_status_message(f"Bridge already running on port {new_port}.")
            return True

        # Stop existing server
        if hasattr(self, "bridge_server") and self.bridge_server:
            try:
                self.bridge_server.stop()
            except Exception:
                pass

        self.bridge_port = new_port
        self.state.config["bridge_port"] = new_port
        self.state.save_config()

        self.bridge_server = BridgeServer(port=self.bridge_port, event_callback=self._on_bridge_event_async)
        success = self.bridge_server.start()

        if hasattr(self, "ent_bridge_port"):
            self.ent_bridge_port.delete(0, "end")
            self.ent_bridge_port.insert(0, str(self.bridge_port))

        if hasattr(self, "lbl_bridge_status"):
            tooltip_txt = f"RuneLite Bridge:\nListening on 127.0.0.1:{self.bridge_port} for live GE trades, 4h cooldown timers, coins, and nature runes.\nClick to change port, test connection, or resync."
            ToolTip(self.lbl_bridge_status, tooltip_txt)

        if success:
            self.show_status_message(f"Bridge HTTP Server started on 127.0.0.1:{self.bridge_port}")
            FloatingToast(self, "🔌 Bridge Reconnected", f"Listening on port {self.bridge_port}")
            return True
        else:
            self.show_status_message(f"Failed to bind Bridge Server on port {self.bridge_port}.")
            messagebox.showwarning("Port Conflict", f"Could not bind to port {self.bridge_port}.\nPlease ensure another application isn't using it or try another port.")
            return False

    def open_bridge_settings_dialog(self):
        """Opens a friendly modal dialog allowing the user to view/change the bridge port, test local connectivity, and resync."""
        dlg = tk.Toplevel(self)
        dlg.title("🔌 RuneLite Bridge Settings")
        dlg.configure(bg="#1e1e1e")
        dlg.resizable(False, False)
        dlg.transient(self)
        dlg.grab_set()

        try:
            x = self.winfo_rootx() + (self.winfo_width() // 2) - 220
            y = self.winfo_rooty() + (self.winfo_height() // 2) - 170
            dlg.geometry(f"440x340+{max(0, x)}+{max(0, y)}")
        except Exception:
            dlg.geometry("440x340")

        # Header banner
        header = tk.Frame(dlg, bg="#252528", padx=14, pady=10)
        header.pack(fill="x")
        tk.Label(header, text="🔌 RuneLite Bridge Connection", font=("Segoe UI", 11, "bold"), fg="#f39c12", bg="#252528").pack(anchor="w")
        tk.Label(header, text="Private local communication between OSRS RuneLite & Tracker", font=("Segoe UI", 8), fg="#888888", bg="#252528").pack(anchor="w")

        body = tk.Frame(dlg, bg="#1e1e1e", padx=16, pady=12)
        body.pack(fill="both", expand=True)

        is_running = bool(self.bridge_server and self.bridge_server.is_running)
        status_txt = f"● Active (Listening on 127.0.0.1:{self.bridge_port})" if is_running else "● Inactive / Stopped"
        status_color = "#2ecc71" if is_running else "#e74c3c"
        lbl_status = tk.Label(body, text=status_txt, font=("Segoe UI", 9, "bold"), fg=status_color, bg="#1e1e1e")
        lbl_status.pack(anchor="w", pady=(0, 10))

        port_row = tk.Frame(body, bg="#1e1e1e")
        port_row.pack(fill="x", pady=4)
        tk.Label(port_row, text="Communication Port:", font=("Segoe UI", 9), fg="#cccccc", bg="#1e1e1e").pack(side="left")

        ent_dlg_port = tk.Entry(port_row, width=8, bg="#252528", fg="#2ecc71", font=("Segoe UI", 10, "bold"), insertbackground="#ffffff", relief="flat", justify="center")
        ent_dlg_port.insert(0, str(self.bridge_port))
        ent_dlg_port.pack(side="left", padx=10)

        lbl_test_result = tk.Label(body, text="", font=("Segoe UI", 8), fg="#cccccc", bg="#1e1e1e", wraplength=400, justify="left")
        lbl_test_result.pack(anchor="w", pady=4)

        def do_save_reconnect():
            p_val = ent_dlg_port.get().strip()
            ok = self.change_bridge_port(p_val)
            if ok:
                lbl_status.config(text=f"● Active (Listening on 127.0.0.1:{self.bridge_port})", fg="#2ecc71")
                lbl_test_result.config(text=f"✅ Successfully bound and listening on port {self.bridge_port}.", fg="#2ecc71")
            else:
                lbl_status.config(text="● Failed to bind", fg="#e74c3c")
                lbl_test_result.config(text="❌ Failed to bind to requested port. Try another port number.", fg="#e74c3c")

        def do_test_ping():
            p_val = ent_dlg_port.get().strip()
            try:
                import urllib.request
                req = urllib.request.Request(f"http://127.0.0.1:{p_val}/api/ping", headers={"User-Agent": "OSRS-Alch-Tester"})
                with urllib.request.urlopen(req, timeout=1.5) as resp:
                    if resp.status == 200:
                        lbl_test_result.config(text=f"✅ Port {p_val} responded OK! Local bridge server is healthy.", fg="#2ecc71")
                        return
            except Exception as ex:
                lbl_test_result.config(text=f"⚠️ Ping check failed on port {p_val}: {ex}", fg="#f1c40f")

        def do_force_resync():
            if self.bridge_server:
                self.bridge_server.request_resync()
            self.manual_ge_sync()
            lbl_test_result.config(text="🔄 Resync requested! RuneLite will broadcast full snapshot on next tick.", fg="#3498db")

        btn_bar = tk.Frame(body, bg="#1e1e1e")
        btn_bar.pack(fill="x", pady=8)

        btn_apply = tk.Button(btn_bar, text="💾 Save & Rebind", command=do_save_reconnect,
                              bg="#2ecc71", fg="#000000", font=("Segoe UI", 8, "bold"), relief="flat", padx=10, pady=3, cursor="hand2")
        btn_apply.pack(side="left", padx=(0, 6))

        btn_test = tk.Button(btn_bar, text="🧪 Test Port (Ping)", command=do_test_ping,
                             bg="#252528", fg="#cccccc", font=("Segoe UI", 8), relief="flat", padx=8, pady=3, cursor="hand2")
        btn_test.pack(side="left", padx=4)

        btn_sync = tk.Button(btn_bar, text="🔄 Force Resync", command=do_force_resync,
                             bg="#2980b9", fg="#ffffff", font=("Segoe UI", 8), relief="flat", padx=8, pady=3, cursor="hand2")
        btn_sync.pack(side="left", padx=4)

        note_box = tk.Frame(dlg, bg="#252528", padx=12, pady=8)
        note_box.pack(fill="x", side="bottom")
        note_txt = (
            "💡 Matching Port in RuneLite:\n"
            "If you change the port here, open RuneLite Settings (wrench icon) ➔ "
            "search 'Alch Dashboard Bridge' ➔ set 'Dashboard Port' to match."
        )
        tk.Label(note_box, text=note_txt, font=("Segoe UI", 8), fg="#aaaaaa", bg="#252528", justify="left").pack(anchor="w")

    def _on_bridge_event_async(self, data):
        try:
            self.after(0, lambda: self.handle_bridge_event(data))
        except Exception:
            pass

    def _register_account(self, account):
        if not account or account == "Unknown":
            return
        clean_acc = account.replace('\u00a0', ' ').strip()
        if hasattr(self, "cb_account"):
            curr_vals = list(self.cb_account["values"])
            if clean_acc not in curr_vals:
                curr_vals.append(clean_acc)
                self.cb_account["values"] = sorted(curr_vals, key=lambda x: (x != "All Accounts", x))

    def on_account_selected(self, event=None):
        sel = self.var_account.get()
        self.state.active_account = "All" if sel == "All Accounts" else sel
        self.state.config["monitored_character"] = sel
        self.state.save_config()
        self._apply_active_account_data()
        self.recalculate_all()
        if hasattr(self, "recalculate_guide_table"):
            self.recalculate_guide_table()

    def _apply_active_account_data(self, force=False):
        self._sync_from_container_export(force=force)
        sel = self.var_account.get() if hasattr(self, "var_account") else "All Accounts"
        target_acc = None
        if sel != "All Accounts" and sel in self.state.accounts:
            target_acc = self.state.accounts[sel]
        elif self.state.accounts:
            target_acc = max(self.state.accounts.values(), key=lambda a: a.get("last_seen", 0))

        if sel == "All Accounts":
            if self.state.accounts:
                total_coins = sum(acc.get("coins", 0) for acc in self.state.accounts.values())
                total_nats = sum(acc.get("nature_runes", 0) for acc in self.state.accounts.values())
                if self.var_use_cash.get() and hasattr(self, "ent_cash"):
                    self.ent_cash.delete(0, tk.END)
                    self.ent_cash.insert(0, format_gp(total_coins))
                    self.state.config["cash_stack"] = total_coins
                if hasattr(self, "ent_owned_nat"):
                    self.ent_owned_nat.delete(0, tk.END)
                    self.ent_owned_nat.insert(0, str(total_nats))
                    self.state.config["owned_nature_runes"] = total_nats
        else:
            if target_acc:
                coins = target_acc.get("coins", 0)
                nats = target_acc.get("nature_runes", 0)

                if self.var_use_cash.get() and hasattr(self, "ent_cash"):
                    self.ent_cash.delete(0, tk.END)
                    self.ent_cash.insert(0, format_gp(coins))
                    self.state.config["cash_stack"] = coins

                if hasattr(self, "ent_owned_nat"):
                    self.ent_owned_nat.delete(0, tk.END)
                    self.ent_owned_nat.insert(0, str(nats))
                    self.state.config["owned_nature_runes"] = nats

        if target_acc:
            levels = target_acc.get("levels", {})

            if hasattr(self, "ent_craft_lvl") and "Crafting" in levels:
                self.ent_craft_lvl.delete(0, tk.END)
                self.ent_craft_lvl.insert(0, str(levels["Crafting"]))
                self.state.config.setdefault("player_levels", {})["Crafting"] = levels["Crafting"]

            if hasattr(self, "ent_smith_lvl") and "Smithing" in levels:
                self.ent_smith_lvl.delete(0, tk.END)
                self.ent_smith_lvl.insert(0, str(levels["Smithing"]))
                self.state.config.setdefault("player_levels", {})["Smithing"] = levels["Smithing"]

            if hasattr(self, "ent_fletch_lvl") and "Fletching" in levels:
                self.ent_fletch_lvl.delete(0, tk.END)
                self.ent_fletch_lvl.insert(0, str(levels["Fletching"]))
                self.state.config.setdefault("player_levels", {})["Fletching"] = levels["Fletching"]

            if hasattr(self, "ent_mage_lvl") and "Magic" in levels:
                self.ent_mage_lvl.delete(0, tk.END)
                self.ent_mage_lvl.insert(0, str(levels["Magic"]))
                self.state.config.setdefault("player_levels", {})["Magic"] = levels["Magic"]

            if hasattr(self, "ent_guide_cur_lvl") and hasattr(self, "var_guide_skill"):
                g_sk = self.var_guide_skill.get()
                if g_sk in levels:
                    self.ent_guide_cur_lvl.delete(0, tk.END)
                    self.ent_guide_cur_lvl.insert(0, str(levels[g_sk]))

        self._sync_cart_from_ge()
        if hasattr(self, "recalculate_w308_table"):
            self.recalculate_w308_table()

    def _sync_cart_from_ge(self):
        curr_sel = self.var_account.get() if getattr(self, "var_account", None) else "All Accounts"
        if curr_sel:
            curr_sel = curr_sel.replace('\u00a0', ' ').strip()
        active_ge_items = {}
        slots = getattr(self, "_ge_cart_slots", {})
        for k, info in slots.items():
            acc = info.get("account")
            if not acc:
                acc = k.rsplit("_", 1)[0]
            if acc:
                acc = acc.replace('\u00a0', ' ').strip()
            if curr_sel == "All Accounts" or acc == curr_sel:
                iid = str(info["item_id"])
                active_ge_items[iid] = active_ge_items.get(iid, 0) + info["qty"]

        # Cleanly remove previous GE-driven items that are no longer actively buying
        if not hasattr(self, "_ge_tracked_items"):
            self._ge_tracked_items = set()

        for iid in list(self._ge_tracked_items):
            if iid not in active_ge_items:
                if iid in self.state.cart_items:
                    del self.state.cart_items[iid]
                self._ge_tracked_items.discard(iid)

        # Add or update currently active GE items
        for iid, qty in active_ge_items.items():
            self.state.cart_items[iid] = qty
            self._ge_tracked_items.add(iid)

        self.recalculate_alch_table()
        self.update_cart_display()

    def handle_bridge_event(self, data):
        self._last_bridge_event_time = time.time()
        event_type = data.get("event")
        raw_account = data.get("account", "Default")
        if not raw_account or raw_account == "Unknown":
            account = "Default"
        else:
            account = raw_account.replace('\u00a0', ' ').strip()

        self._register_account(account)
        active_monitored = self.var_account.get() if hasattr(self, "var_account") else "All Accounts"
        is_active = (active_monitored == "All Accounts" or account == active_monitored)

        if event_type in ("ACCOUNT_LOGIN", "ACCOUNT_SNAPSHOT"):
            world = data.get("world")
            is_mem = data.get("isMembers", True)
            levels = {
                "Crafting": data.get("crafting", 99),
                "Smithing": data.get("smithing", 99),
                "Fletching": data.get("fletching", 99),
                "Magic": data.get("magic", 99)
            }
            xp = {
                "Crafting": data.get("crafting_xp"),
                "Smithing": data.get("smithing_xp"),
                "Fletching": data.get("fletching_xp"),
                "Magic": data.get("magic_xp")
            }
            skilling = {}
            if data.get("active_skill"):
                skilling = {
                    "active_skill": data.get("active_skill"),
                    "detected_activity": data.get("detected_activity"),
                    "skilling_xp_hr": data.get("skilling_xp_hr", 0),
                    "rem_xp_next": data.get("rem_xp_next", 0),
                    "est_secs_next": data.get("est_secs_next", 0),
                    "timestamp": time.time()
                }
            coins = data.get("coins")
            nats = data.get("natureRunes")
            bank_coins = data.get("bankCoins")
            batch_gross = data.get("batchGrossGp")
            tot_wealth = data.get("totalWealth")
            b_item = data.get("batchItemName")
            b_qty = data.get("batchItemQty")
            prof_hr = data.get("profitPerHour")
            alchs_hr = data.get("alchsPerHour")
            self.state.update_account(
                account, coins=coins, nature_runes=nats, bank_coins=bank_coins, world=world, is_members=is_mem,
                levels=levels, xp={k: v for k, v in xp.items() if v is not None}, skilling=skilling,
                batch_gross_gp=batch_gross, total_wealth=tot_wealth,
                batch_item_name=b_item, batch_item_qty=b_qty,
                profit_per_hour=prof_hr, alchs_per_hour=alchs_hr
            )
            if is_active:
                self._apply_active_account_data()
                if hasattr(self, "lbl_bridge_status"):
                    self.lbl_bridge_status.config(text=f"🟢 {account}", fg="#2ecc71")
                self.recalculate_all()
                if hasattr(self, "recalculate_guide_table"):
                    self.recalculate_guide_table()
                if hasattr(self, "recalculate_bond_roadmap"):
                    self.recalculate_bond_roadmap()

        elif event_type == "INVENTORY_SYNC":
            coins = data.get("coins")
            nats = data.get("natureRunes")
            batch_gross = data.get("batchGrossGp")
            tot_wealth = data.get("totalWealth")
            b_item = data.get("batchItemName")
            b_qty = data.get("batchItemQty")
            prof_hr = data.get("profitPerHour")
            alchs_hr = data.get("alchsPerHour")
            self.state.update_account(
                account, coins=coins, nature_runes=nats,
                batch_gross_gp=batch_gross, total_wealth=tot_wealth,
                batch_item_name=b_item, batch_item_qty=b_qty,
                profit_per_hour=prof_hr, alchs_per_hour=alchs_hr
            )
            if is_active:
                self._apply_active_account_data()
                self.recalculate_alch_table()
                if hasattr(self, "recalculate_w308_table"):
                    self.recalculate_w308_table()
                if hasattr(self, "recalculate_bond_roadmap"):
                    self.recalculate_bond_roadmap()

        elif event_type == "BANK_SYNC":
            bank_coins = data.get("bankCoins")
            bank_nats = data.get("bankNatureRunes")
            tot_wealth = data.get("totalWealth")
            acc = self.state.accounts.get(account, {})
            if bank_coins is not None:
                acc["bank_coins"] = bank_coins
            if bank_nats is not None:
                acc["bank_nats"] = bank_nats
            if tot_wealth is not None:
                acc["total_wealth"] = tot_wealth
            self.state.save_accounts()
            if is_active:
                self._apply_active_account_data()
                if hasattr(self, "recalculate_w308_table"):
                    self.recalculate_w308_table()
                if hasattr(self, "recalculate_bond_roadmap"):
                    self.recalculate_bond_roadmap()

        elif event_type == "SKILLS_SYNC":
            levels = {
                "Crafting": data.get("crafting"),
                "Smithing": data.get("smithing"),
                "Fletching": data.get("fletching"),
                "Magic": data.get("magic")
            }
            xp = {
                "Crafting": data.get("crafting_xp"),
                "Smithing": data.get("smithing_xp"),
                "Fletching": data.get("fletching_xp"),
                "Magic": data.get("magic_xp")
            }
            skilling = {}
            if data.get("active_skill"):
                skilling = {
                    "active_skill": data.get("active_skill"),
                    "detected_activity": data.get("detected_activity"),
                    "skilling_xp_hr": data.get("skilling_xp_hr", 0),
                    "rem_xp_next": data.get("rem_xp_next", 0),
                    "est_secs_next": data.get("est_secs_next", 0),
                    "timestamp": time.time()
                }
            self.state.update_account(account, levels={k: v for k, v in levels.items() if v is not None}, xp={k: v for k, v in xp.items() if v is not None}, skilling=skilling)
            if is_active:
                self._apply_active_account_data()
                self.recalculate_craft_table()
                if hasattr(self, "recalculate_guide_table"):
                    self.recalculate_guide_table()

        elif event_type == "GE_OFFER":
            item_id = data.get("itemId", 0)
            item_name = data.get("itemName", "")
            qty_sold = data.get("quantitySold", 0)
            total_qty = data.get("totalQuantity", 0)
            spent = data.get("spent", 0)
            price = data.get("price", 0)
            state = data.get("state", "")
            slot = data.get("slot", 0)

            slot_key = f"{account}_{slot}"

            # 1. Live GE Sync into Shopping Cart
            if state == "BUYING" and item_id > 0 and total_qty > 0:
                self._ge_cart_slots[slot_key] = {
                    "account": account,
                    "slot": slot,
                    "item_id": str(item_id),
                    "qty": total_qty
                }
                self._sync_cart_from_ge()
            elif state in ("BOUGHT", "CANCELLED_BUY", "EMPTY"):
                if slot_key in self._ge_cart_slots:
                    del self._ge_cart_slots[slot_key]
                    self._sync_cart_from_ge()

            if item_id > 0:
                # 2. Real-time incremental 4-hour limit tracking (starts immediately on first buy!)
                if not hasattr(self, "_ge_slot_progress"):
                    self._ge_slot_progress = {}

                prev_slot_info = self._ge_slot_progress.get(slot_key, {})
                prev_item = prev_slot_info.get("item_id", 0)
                prev_sold = prev_slot_info.get("qty_sold", 0) if prev_item == item_id else 0

                delta_sold = max(0, qty_sold - prev_sold)
                if delta_sold > 0:
                    self.state.add_timer(item_id, item_name, delta_sold, account=account)
                    self.update_timers_display()
                    self.recalculate_alch_table()

                if state == "BUYING":
                    self._ge_slot_progress[slot_key] = {"item_id": item_id, "qty_sold": qty_sold}
                elif state in ("BOUGHT", "CANCELLED_BUY"):
                    if slot_key in self._ge_slot_progress:
                        del self._ge_slot_progress[slot_key]

                    # Log finalized trade to Session Tracker
                    if qty_sold > 0:
                        finalize_key = f"{account}_{slot}_{item_id}_{qty_sold}_{state}"
                        if finalize_key not in self._logged_ge_offers:
                            self._logged_ge_offers.add(finalize_key)
                            unit_buy_price = int(spent // qty_sold) if spent > 0 else int(price)
                            nat_price = self.get_effective_nature_price()
                            mdata = self.api.mapping.get(str(item_id), {})
                            high_alch = mdata.get("highalch", 0)
                            if high_alch > 0:
                                entry = self.state.log_alch_batch(item_id, item_name, qty_sold, unit_buy_price, nat_price, high_alch, account=account, timestamp=data.get("timestamp"))
                                self.update_session_display()
                                tag = "Completed" if state == "BOUGHT" else "Cancelled (Partial)"
                                if is_active:
                                    self.lbl_status_right.config(text=f"🛒 Logged GE Buy ({tag}): {qty_sold}x {item_name} [{account}]", fg="#2ecc71")
                                    if self.state.config.get("desktop_alerts"):
                                        FloatingToast(self, f"🛒 GE Buy {tag} [{account}]", f"Bought {qty_sold}x {item_name} at {unit_buy_price:,} gp (Profit: +{format_gp(entry['profit'])})")
                                else:
                                    if self.state.config.get("desktop_alerts"):
                                        FloatingToast(self, f"🛒 Alt GE Buy [{account}]", f"Bought {qty_sold}x {item_name} at {unit_buy_price:,} gp")

                    # Reconcile authoritative 4h buy limits and trades from RuneLite without deleting live timers
                    try:
                        self.state.sync_from_runelite_ge(self.api.mapping, self.get_effective_nature_price())
                        self.update_timers_display()
                        self.recalculate_alch_table()
                    except Exception:
                        pass
                elif state == "EMPTY":
                    if slot_key in self._ge_slot_progress:
                        del self._ge_slot_progress[slot_key]

        elif event_type == "GE_SYNC":
            try:
                res = self.state.sync_from_runelite_ge(self.api.mapping, self.get_effective_nature_price(), raw_sync_data=data)
                self.update_timers_display()
                self.update_session_display()
                self.recalculate_alch_table()
                if is_active:
                    self.lbl_status_right.config(
                        text=f"🔄 GE Synced [{account}]: {res.get('timers_updated', 0)} timers, {res.get('session_imported', 0)} trades",
                        fg="#3498db"
                    )
            except Exception as e:
                print(f"Error handling GE_SYNC: {e}")

        elif event_type == "TRADE_ACCEPTED":
            item_id = data.get("itemId", 0)
            item_name = data.get("itemName", "")
            qty = data.get("quantity", 0)
            unit_price = data.get("unitPrice", 0)
            if item_id > 0 and qty > 0 and unit_price > 0:
                nat_price = self.get_effective_nature_price()
                mdata = self.api.mapping.get(str(item_id), {})
                high_alch = mdata.get("highalch", 0)
                if high_alch > 0:
                    entry = self.state.log_alch_batch(item_id, item_name, qty, unit_price, nat_price, high_alch, account=account, timestamp=data.get("timestamp"))
                    self.update_session_display()
                    if is_active:
                        self.lbl_status_right.config(text=f"🤝 Logged W308 Trade: {qty:,}x {item_name} @ {unit_price:,} gp [{account}]", fg="#f39c12")
                        if self.state.config.get("desktop_alerts"):
                            FloatingToast(self, f"🤝 W308 Trade [{account}]", f"Bought {qty:,}x {item_name} @ {unit_price:,} gp ea (Profit: +{format_gp(entry['profit'])})")

        elif event_type == "TRADE_SOLD":
            item_id = data.get("itemId", 0)
            item_name = data.get("itemName", "")
            qty = data.get("quantity", 0)
            unit_price = data.get("unitPrice", 0)
            buy_price = data.get("buyPrice", 0)
            profit = data.get("profit", 0)
            if item_id > 0 and qty > 0:
                entry = self.state.log_trade_flip(item_id, item_name, qty, buy_price, unit_price, profit, account=account, timestamp=data.get("timestamp"))
                self.update_session_display()
                if is_active:
                    self.lbl_status_right.config(text=f"🤝 P2P/W308 Sale: Sold {qty:,}x {item_name} @ {unit_price:,} gp (+{format_gp(profit)}) [{account}]", fg="#2ecc71")
                    if self.state.config.get("desktop_alerts"):
                        FloatingToast(self, f"🤝 Trade Sale [{account}]", f"Sold {qty:,}x {item_name} @ {unit_price:,} gp ea (Profit: +{format_gp(profit)})")

        elif event_type == "ALCH_CAST":
            batch_gross = data.get("batchGrossGp")
            tot_wealth = data.get("totalWealth")
            prof_hr = data.get("profitPerHour")
            alchs_hr = data.get("alchsPerHour")
            self.state.update_account(
                account, batch_gross_gp=batch_gross, total_wealth=tot_wealth,
                profit_per_hour=prof_hr, alchs_per_hour=alchs_hr
            )
            if is_active:
                self.lbl_status_right.config(text=f"🪄 [{account}] High Alch Cast (+65 XP)", fg="#f39c12")
                if hasattr(self, "recalculate_bond_roadmap"):
                    self.recalculate_bond_roadmap()

if __name__ == "__main__":
    app = OSRSAlchDashboard()
    app.mainloop()
