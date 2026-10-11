import os
import sys
import json
import time
import shutil
import glob
import datetime

def get_app_data_dir():
    base = os.getenv("LOCALAPPDATA") or os.path.expanduser("~")
    # For developer source mode, use AlchMate_Dev to keep developer test data separate from public AlchMate
    app_folder = "AlchMate" if getattr(sys, "frozen", False) else "AlchMate_Dev"
    return os.path.join(base, app_folder, "data")

STATE_DIR = get_app_data_dir()
CONFIG_FILE = os.path.join(STATE_DIR, "config.json")
TIMERS_FILE = os.path.join(STATE_DIR, "timers.json")
SESSION_FILE = os.path.join(STATE_DIR, "session.json")
ACCOUNTS_FILE = os.path.join(STATE_DIR, "accounts.json")

DEFAULT_CONFIG = {
    "members": True,
    "f2p": False,
    "cash_stack": 5000000,
    "min_volume": 100,
    "max_item_cost": 500000,
    "strategy": "patient",  # 'patient' (bid) or 'instant' (ask)
    "auto_refresh_mins": 2,
    "alert_threshold_alch": 200,
    "sound_enabled": True,
    "desktop_alerts": True,
    "free_alchs_mode": False,
    "custom_nature_price": 0, # 0 = use live price
    "alch_speed": 1200,
    "player_levels": {
        "Crafting": 99,
        "Smithing": 99,
        "Fletching": 99,
        "Magic": 99,
        "Herblore": 99,
        "Cooking": 99
    },
    "only_usable_recipes": False,
    "use_cash_stack": True,
    "min_profit": None, # None or 0 = show everything
    "owned_nature_runes": 0,
    "speed_filter": "All",
    "hide_maxed_cooldown": True,
    "price_basis": "5m", # '5m' (Volume-Weighted Avg) or 'latest' (1-Trade Tick)
    "min_alert_5m_vol": 3, # Minimum 5m sell volume required to trigger a price change alert
    "alch_type_rune": True,
    "alch_type_addy": True,
    "alch_type_mith": True,
    "alch_type_dragon": True,
    "alch_type_jewel": True,
    "alch_type_bows": True,
    "alch_type_staves": True,
    "alch_type_barrows": True,
    "alch_type_other": True,
    "monitored_character": "All Accounts",
    "last_seen_version": "1.0.0",
    "update_channel": "test" if not getattr(sys, "frozen", False) else "stable",
    "bridge_port": 18833
}

class AppState:
    def __init__(self):
        os.makedirs(STATE_DIR, exist_ok=True)
        self.config = dict(DEFAULT_CONFIG)
        self.timers = {} # item_id -> {"name": ..., "bought_time": ..., "qty": ..., "account": ...}
        self.session = {
            "total_alchs": 0,
            "total_profit": 0,
            "total_xp": 0,
            "history": []
        }
        self.accounts = {} # account_name -> {"coins": ..., "nature_runes": ..., "world": ..., "is_members": ..., "levels": {...}, "last_seen": ...}
        self.active_account = "All"
        self.cart_items = {} # item_id -> qty
        self.alert_history = [] # list of recent alert strings
        self.notified_timers = set() # track timers already notified
        self.last_alerted_profits = {} # item_id -> profit_ea

        self.load_all()

    def load_all(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    self.config.update(json.load(f))
            except Exception:
                pass

        if os.path.exists(TIMERS_FILE):
            try:
                with open(TIMERS_FILE, "r", encoding="utf-8") as f:
                    self.timers = json.load(f)
            except Exception:
                pass

        if os.path.exists(SESSION_FILE):
            try:
                with open(SESSION_FILE, "r", encoding="utf-8") as f:
                    self.session.update(json.load(f))
            except Exception:
                pass

        if os.path.exists(ACCOUNTS_FILE):
            try:
                with open(ACCOUNTS_FILE, "r", encoding="utf-8") as f:
                    self.accounts = json.load(f)
            except Exception:
                pass

    def save_config(self):
        try:
            tmp = CONFIG_FILE + ".tmp"
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=2)
            os.replace(tmp, CONFIG_FILE)
        except Exception as e:
            print(f"Error saving config: {e}")

    def save_timers(self):
        try:
            tmp = TIMERS_FILE + ".tmp"
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(self.timers, f, indent=2)
            os.replace(tmp, TIMERS_FILE)
        except Exception as e:
            print(f"Error saving timers: {e}")

    def save_session(self):
        try:
            tmp = SESSION_FILE + ".tmp"
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(self.session, f, indent=2)
            os.replace(tmp, SESSION_FILE)
        except Exception as e:
            print(f"Error saving session: {e}")

    def save_accounts(self):
        try:
            tmp = ACCOUNTS_FILE + ".tmp"
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(self.accounts, f, indent=2)
            os.replace(tmp, ACCOUNTS_FILE)
        except Exception as e:
            print(f"Error saving accounts: {e}")

    def update_account(self, name, coins=None, nature_runes=None, world=None, is_members=None, levels=None, xp=None, skilling=None,
                       batch_gross_gp=None, total_wealth=None, batch_item_name=None, batch_item_qty=None,
                       profit_per_hour=None, alchs_per_hour=None, bank_coins=None, bank_nature_runes=None):
        if not name or name == "Unknown":
            return
        if name not in self.accounts:
            self.accounts[name] = {
                "name": name,
                "coins": 0,
                "nature_runes": 0,
                "world": 301,
                "is_members": True,
                "levels": {"Crafting": 99, "Smithing": 99, "Fletching": 99, "Magic": 99, "Herblore": 99, "Cooking": 99},
                "xp": {},
                "skilling": {},
                "last_seen": time.time()
            }
        acc = self.accounts[name]
        acc["last_seen"] = time.time()
        if coins is not None:
            acc["coins"] = max(0, int(coins))
        if nature_runes is not None:
            acc["nature_runes"] = max(0, int(nature_runes))
        if world is not None:
            acc["world"] = int(world)
        if is_members is not None:
            acc["is_members"] = bool(is_members)
        if levels:
            acc.setdefault("levels", {}).update(levels)
        if xp:
            acc.setdefault("xp", {}).update(xp)
        if skilling:
            acc.setdefault("skilling", {}).update(skilling)
        if batch_gross_gp is not None:
            acc["batch_gross_gp"] = max(0, int(batch_gross_gp))
        if total_wealth is not None:
            acc["total_wealth"] = max(0, int(total_wealth))
        if batch_item_name is not None:
            acc["batch_item_name"] = str(batch_item_name)
        if batch_item_qty is not None:
            acc["batch_item_qty"] = max(0, int(batch_item_qty))
        if profit_per_hour is not None:
            acc["profit_per_hour"] = int(profit_per_hour)
        if alchs_per_hour is not None:
            acc["alchs_per_hour"] = int(alchs_per_hour)
        if bank_coins is not None:
            acc["bank_coins"] = max(0, int(bank_coins))
        if bank_nature_runes is not None:
            acc["bank_nature_runes"] = max(0, int(bank_nature_runes))
        self.save_accounts()

    def add_timer(self, item_id, item_name, qty, account="Default"):
        now = time.time()
        iid_str = str(item_id)
        clean_acc = str(account).replace('\u00a0', ' ').strip() if account else "Default"
        acc_tag = clean_acc if clean_acc and clean_acc != "Unknown" else "Default"
        key = f"{acc_tag}_{iid_str}" if acc_tag != "Default" else iid_str

        existing = self.timers.get(key)
        if not existing and key != iid_str and iid_str in self.timers:
            existing = self.timers[iid_str]
            key = iid_str

        if existing and (now - existing.get("bought_time", 0)) < 14400:
            # Active timer already running within 4 hours: keep original anchor time, add qty!
            existing["qty"] = existing.get("qty", 0) + qty
            existing["name"] = item_name
            existing["account"] = acc_tag
            existing["item_id"] = int(item_id) if str(item_id).isdigit() else 0
        else:
            self.timers[key] = {
                "account": acc_tag,
                "item_id": int(item_id) if str(item_id).isdigit() else 0,
                "name": item_name,
                "bought_time": now,
                "qty": qty
            }
        if key in self.notified_timers:
            self.notified_timers.remove(key)
        self.save_timers()

    def get_remaining_limit(self, item_id, base_limit, account=None):
        """Returns (remaining_qty, seconds_left, is_on_cooldown)"""
        if not base_limit or base_limit <= 0:
            return 1000, 0, False

        iid_str = str(item_id)
        now = time.time()

        tinfo = None
        target_account = account or getattr(self, "active_account", "All")

        if target_account and target_account != "All":
            clean_tgt = str(target_account).replace('\u00a0', ' ').strip()
            tinfo = self.timers.get(f"{clean_tgt}_{iid_str}") or self.timers.get(iid_str)
        else:
            candidates = []
            for k, t in self.timers.items():
                if str(t.get("item_id", "")) == iid_str or k.endswith(f"_{iid_str}") or k == iid_str:
                    if (now - t.get("bought_time", 0)) < 14400:
                        candidates.append(t)
            if candidates:
                tinfo = max(candidates, key=lambda x: x.get("qty", 0))

        if not tinfo:
            return base_limit, 0, False

        elapsed = now - tinfo.get("bought_time", 0)
        if elapsed >= 14400: # Expired
            return base_limit, 0, False

        bought_qty = tinfo.get("qty", 0)
        remaining = max(0, base_limit - bought_qty)
        seconds_left = max(0, 14400 - elapsed)
        return remaining, seconds_left, True

    def remove_timer(self, item_id):
        iid_str = str(item_id)
        keys_to_del = [k for k in self.timers if k == iid_str or k.endswith(f"_{iid_str}")]
        for k in keys_to_del:
            del self.timers[k]
            if k in self.notified_timers:
                self.notified_timers.remove(k)
        self.save_timers()

    def check_expired_timers(self):
        now = time.time()
        expired = []
        for key, tinfo in list(self.timers.items()):
            elapsed = now - tinfo.get("bought_time", 0)
            if elapsed >= 14400: # 4 hours elapsed (timer hits 0)
                expired.append({
                    "name": tinfo.get("name", "Item"),
                    "account": tinfo.get("account", "Default"),
                    "key": key
                })
                # Auto-remove timer once 4 hours have elapsed
                if key in self.timers:
                    del self.timers[key]
                if key in self.notified_timers:
                    self.notified_timers.remove(key)

        if expired:
            self.save_timers()
        return expired

    def reset_all_timers(self, account=None):
        """1-click reset to wipe active timers (for a specific account or all)."""
        if not account or account in ("All", "All Accounts"):
            self.timers.clear()
            self.notified_timers.clear()
        else:
            keys_to_del = [k for k, t in list(self.timers.items()) if t.get("account") == account]
            for k in keys_to_del:
                del self.timers[k]
                if k in self.notified_timers:
                    self.notified_timers.remove(k)
        self.save_timers()

    def sync_from_runelite_ge(self, api_mapping=None, default_nat_price=140, raw_sync_data=None):
        """Authoritatively synchronizes active 4-hour buy limits and past trades directly
        from RuneLite profile configurations or live GE_SYNC bridge events.
        Guarantees exact reset timestamps, true bought quantities, and backfills any trades
        missed in the session tracker without double-counting.
        """
        now_utc = datetime.datetime.now(datetime.timezone.utc)
        now_local = time.time()
        mapping = api_mapping or {}

        display_names = {}
        account_buylimits = {} # acc_name -> {iid: iso_str}
        account_trades = {}    # acc_name -> list of trades
        account_slots = {}     # acc_name -> {iid: qty_sold}

        if raw_sync_data and isinstance(raw_sync_data, dict):
            acc = raw_sync_data.get("account", "Default")
            if "buylimits" in raw_sync_data and isinstance(raw_sync_data["buylimits"], dict):
                account_buylimits[acc] = raw_sync_data["buylimits"]
            if "tradeHistory" in raw_sync_data and isinstance(raw_sync_data["tradeHistory"], list):
                account_trades[acc] = raw_sync_data["tradeHistory"]
        else:
            raw_paths = glob.glob(os.path.expanduser(r"~\.runelite\*profiles*\*rsprofile*.properties")) + \
                        glob.glob(os.path.expanduser(r"~\.runelite\profiles*\*rsprofile*.properties"))
            profile_paths = sorted([p for p in raw_paths if os.path.exists(p)], key=os.path.getmtime, reverse=True)

            acc_hash_buylimits = {}
            acc_hash_trades = {}
            acc_hash_slots = {}

            for p in profile_paths:
                try:
                    with open(p, "r", encoding="utf-8") as f:
                        for line in f:
                            line = line.strip()
                            if ".displayName=" in line:
                                parts = line.split("=")
                                if len(parts) == 2:
                                    acc_hash = parts[0].split(".")[2]
                                    if acc_hash not in display_names:
                                        display_names[acc_hash] = parts[1]
                            elif "buylimit." in line:
                                parts = line.split("=")
                                if len(parts) == 2:
                                    key_parts = parts[0].split(".")
                                    if len(key_parts) >= 4:
                                        acc_hash = key_parts[2]
                                        iid = key_parts[-1]
                                        iso_val = parts[1].replace(r"\:", ":")
                                        if iid not in acc_hash_buylimits.setdefault(acc_hash, {}):
                                            acc_hash_buylimits[acc_hash][iid] = iso_val
                            elif "tradeHistory=" in line:
                                parts = line.split("tradeHistory=")
                                if len(parts) == 2:
                                    key_parts = parts[0].rstrip(".").split(".")
                                    acc_hash = key_parts[2] if len(key_parts) >= 3 else "default"
                                    raw_json = parts[1].replace(r"\:", ":")
                                    try:
                                        t_list = json.loads(raw_json)
                                        if acc_hash not in acc_hash_trades:
                                            acc_hash_trades[acc_hash] = t_list
                                    except Exception:
                                        pass
                            elif "geoffer." in line:
                                parts = line.split("=")
                                if len(parts) == 2:
                                    key_parts = parts[0].split(".")
                                    if len(key_parts) >= 3:
                                        acc_hash = key_parts[2]
                                        raw_slot = parts[1].replace(r"\:", ":")
                                        try:
                                            slot_obj = json.loads(raw_slot)
                                            s_iid = str(slot_obj.get("itemId", 0))
                                            s_sold = int(slot_obj.get("quantitySold", 0))
                                            if s_iid != "0" and s_sold > 0:
                                                slots_dict = acc_hash_slots.setdefault(acc_hash, {})
                                                slots_dict[s_iid] = max(slots_dict.get(s_iid, 0), s_sold)
                                        except Exception:
                                            pass
                except Exception:
                    pass

            for acc_hash, bl in acc_hash_buylimits.items():
                acc_name = display_names.get(acc_hash, acc_hash)
                account_buylimits[acc_name] = bl
            for acc_hash, tr in acc_hash_trades.items():
                acc_name = display_names.get(acc_hash, acc_hash)
                account_trades[acc_name] = tr
            for acc_hash, sl in acc_hash_slots.items():
                acc_name = display_names.get(acc_hash, acc_hash)
                account_slots[acc_name] = sl

        if not account_buylimits and not account_trades:
            return {"timers_updated": 0, "session_imported": 0}

        # 1. Update active 4h timers
        timers_updated = 0
        EXCLUDED_NON_ALCH_IDS = {
            554, 555, 556, 557, 558, 559, 560, 561, 562, 563, 564, 565, 566,
            882, 884, 886, 888, 890, 892,
            995
        }

        for acc_name, limits in account_buylimits.items():
            trades = account_trades.get(acc_name, [])
            slots = account_slots.get(acc_name, {})
            for iid, iso_str in limits.items():
                try:
                    exp_dt = datetime.datetime.fromisoformat(iso_str)
                    key = f"{acc_name}_{iid}" if acc_name != "Default" else str(iid)
                    if exp_dt > now_utc:
                        start_dt = exp_dt - datetime.timedelta(hours=4)
                        start_ts = start_dt.timestamp()

                        item_trades = [
                            t for t in trades 
                            if str(t.get("i")) == str(iid) and t.get("b") and (t.get("t")/1000.0) >= (start_ts - 30)
                        ]
                        trades_qty = sum(t.get("q", 0) for t in item_trades)
                        slot_qty = slots.get(str(iid), 0)

                        # Check session.json history within this 4h window
                        session_qty = 0
                        for eh in self.session.get("history", []):
                            if str(eh.get("item_id", "")) == str(iid):
                                eh_ts = eh.get("timestamp", 0)
                                if eh_ts >= (start_ts - 30):
                                    session_qty += eh.get("qty", 0)

                        existing_qty = self.timers.get(key, {}).get("qty", 0)

                        mdata = mapping.get(str(iid), {})
                        name = mdata.get("name", self.timers.get(key, {}).get("name", f"Item {iid}"))
                        base_limit = mdata.get("limit", 0)

                        tot_qty = max(trades_qty, slot_qty, session_qty, existing_qty)
                        if tot_qty == 0 and base_limit > 0 and (now_local - start_ts) < 14400:
                            # If RuneLite has an active buylimit timestamp for an alchable item,
                            # but tradeHistory was cleared, default to base_limit if existing timer was maxed
                            tot_qty = existing_qty if existing_qty > 0 else base_limit

                        if base_limit > 0 and tot_qty > base_limit:
                            tot_qty = base_limit

                        existing_ts = self.timers.get(key, {}).get("bought_time", 0)
                        final_bought_time = start_ts
                        if existing_ts > 0 and abs(existing_ts - start_ts) < 14400:
                            final_bought_time = min(start_ts, existing_ts)

                        self.timers[key] = {
                            "account": acc_name,
                            "item_id": int(iid) if str(iid).isdigit() else 0,
                            "name": name,
                            "bought_time": final_bought_time,
                            "qty": tot_qty
                        }
                        timers_updated += 1
                    else:
                        # Expired in RuneLite on disk: only remove if the timer in memory is ALSO expired (>= 4 hours)
                        # Prevents stale on-disk properties files from wiping freshly created live in-memory timers!
                        for k_del in (key, str(iid)):
                            if k_del in self.timers:
                                existing_ts = self.timers[k_del].get("bought_time", 0)
                                if (now_local - existing_ts) >= 14400:
                                    del self.timers[k_del]
                                    if k_del in self.notified_timers:
                                        self.notified_timers.discard(k_del)
                except Exception:
                    pass

        self.save_timers()

        # 2. Backfill missing trades into Session History (last 12h)
        session_imported = 0
        existing_history = self.session.get("history", [])

        for acc_name, trades in account_trades.items():
            for t in trades:
                if not t.get("b"):
                    continue
                iid = t.get("i")
                if iid in EXCLUDED_NON_ALCH_IDS:
                    continue
                t_ts = t.get("t", 0) / 1000.0
                if (now_local - t_ts) > 43200: # Only last 12 hours
                    continue
                qty = t.get("q", 0)
                price = t.get("p", 0)
                if qty <= 0:
                    continue

                matched = False
                for eh in existing_history:
                    eh_ts = eh.get("timestamp", 0)
                    eh_iid = eh.get("item_id")
                    eh_qty = eh.get("qty")
                    if eh_iid == iid and eh_qty == qty and abs(eh_ts - t_ts) < 60:
                        matched = True
                        break

                if not matched:
                    mdata = mapping.get(str(iid), {})
                    name = mdata.get("name", f"Item {iid}")
                    highalch = mdata.get("highalch", 0)
                    nat_price = default_nat_price
                    profit = (highalch - (price + nat_price)) * qty if highalch > 0 else 0

                    # Skip if not an alchable item
                    if highalch <= 0 or profit < -5000:
                        continue

                    entry_id = f"ge_{int(t.get('t', 0))}_{iid}_{qty}"
                    entry = {
                        "id": entry_id,
                        "account": acc_name,
                        "item_id": iid,
                        "timestamp": t_ts,
                        "time": time.strftime("%H:%M:%S", time.localtime(t_ts)),
                        "item": name,
                        "qty": qty,
                        "buy_price": price,
                        "nat_price": nat_price,
                        "alch_val": highalch,
                        "profit": profit
                    }
                    self.session["history"].append(entry)
                    session_imported += 1

        if session_imported > 0:
            # Sort history newest first by timestamp
            self.session["history"].sort(key=lambda x: x.get("timestamp", 0), reverse=True)
            self.session["history"] = self.session["history"][:200]
            self._recalc_session_totals()
            self.save_session()

        return {"timers_updated": timers_updated, "session_imported": session_imported}

    def _adjust_timer_qty(self, item_id, item_name, diff_qty, entry=None):
        """Adjusts the 4-hour Grand Exchange cooldown timer when a session batch quantity changes."""
        if diff_qty == 0:
            return

        iid_str = str(item_id) if item_id is not None else None
        found_iid = None
        acc_tag = entry.get("account", "Default") if entry else "Default"
        key_acc = f"{acc_tag}_{iid_str}" if acc_tag != "Default" else iid_str

        if key_acc and key_acc in self.timers:
            found_iid = key_acc
        elif iid_str and iid_str in self.timers:
            found_iid = iid_str
        elif item_name:
            name_clean = str(item_name).strip().lower()
            for tid, tinfo in self.timers.items():
                if tinfo.get("name", "").strip().lower() == name_clean:
                    if acc_tag == "Default" or tinfo.get("account") == acc_tag:
                        found_iid = tid
                        break

        now = time.time()

        if found_iid:
            tinfo = self.timers[found_iid]
            # Only adjust active timers within the 4-hour window
            elapsed = now - tinfo.get("bought_time", 0)
            if elapsed < 14400:
                new_qty = tinfo.get("qty", 0) + diff_qty
                if new_qty <= 0:
                    self.remove_timer(found_iid)
                else:
                    tinfo["qty"] = new_qty
                    self.save_timers()
        else:
            # If no timer exists, but this batch was recorded within 4 hours and has positive quantity,
            # recreate the active cooldown timer
            entry_qty = entry.get("qty", 0) if entry else diff_qty
            if entry_qty > 0:
                entry_time = None
                if entry:
                    entry_time = entry.get("timestamp")
                    if not entry_time and "id" in entry:
                        parts = str(entry["id"]).split("_")
                        if parts and parts[0].isdigit():
                            try:
                                ts = float(parts[0])
                                entry_time = ts / 1000.0 if ts > 1e11 else ts
                            except (ValueError, TypeError):
                                pass
                if not entry_time:
                    entry_time = now

                if (now - entry_time) < 14400:
                    target_id = iid_str
                    if not target_id and entry:
                        target_id = str(entry.get("item_id", "")) if entry.get("item_id") else None
                    if not target_id and entry:
                        parts = str(entry.get("id", "")).split("_")
                        if len(parts) >= 2 and parts[1].isdigit():
                            target_id = parts[1]
                    if not target_id:
                        target_id = str(int(now))

                    timer_key = f"{acc_tag}_{target_id}" if acc_tag != "Default" else target_id
                    self.timers[timer_key] = {
                        "account": acc_tag,
                        "item_id": int(target_id) if str(target_id).isdigit() else 0,
                        "name": item_name or "Unknown Item",
                        "bought_time": entry_time,
                        "qty": entry_qty
                    }
                    if timer_key in self.notified_timers:
                        self.notified_timers.remove(timer_key)
                    self.save_timers()

    def log_alch_batch(self, item_id, item_name, qty, buy_price, nat_price, alch_val, account="Default", timestamp=None):
        now = float(timestamp) if timestamp else time.time()
        entry_id = str(int(now * 1000)) + f"_{item_id}"
        profit_ea = alch_val - (buy_price + nat_price)
        total_profit = qty * profit_ea

        entry = {
            "id": entry_id,
            "account": account or "Default",
            "item_id": item_id,
            "timestamp": now,
            "time": time.strftime("%H:%M:%S", time.localtime(now)),
            "item": item_name,
            "qty": qty,
            "buy_price": buy_price,
            "nat_price": nat_price,
            "alch_val": alch_val,
            "profit": total_profit
        }

        self.session["history"].insert(0, entry)
        self.session["history"] = self.session["history"][:200]
        self._recalc_session_totals()

        # Deduct nature runes from stockpile if tracked
        owned = self.config.get("owned_nature_runes", 0)
        if owned > 0:
            self.config["owned_nature_runes"] = max(0, owned - qty)
            self.save_config()
        self.save_session()
        return entry

    def log_trade_flip(self, item_id, item_name, qty, buy_price, sell_price, profit, account="Default", timestamp=None):
        now = float(timestamp) if timestamp else time.time()
        entry_id = str(int(now * 1000)) + f"_flip_{item_id}"
        entry = {
            "id": entry_id,
            "account": account or "Default",
            "item_id": item_id,
            "timestamp": now,
            "time": time.strftime("%H:%M:%S", time.localtime(now)),
            "item": f"[Trade Flip] {item_name}",
            "qty": qty,
            "buy_price": buy_price,
            "nat_price": 0,
            "alch_val": sell_price,
            "profit": profit
        }
        self.session["history"].insert(0, entry)
        self.session["history"] = self.session["history"][:200]
        self._recalc_session_totals()
        self.save_session()
        return entry

    def update_session_entry(self, entry_id, new_qty, new_buy_price, new_nat_price):
        for entry in self.session["history"]:
            if entry["id"] == entry_id:
                old_qty = entry.get("qty", 0)
                diff_qty = new_qty - old_qty
                entry["qty"] = new_qty
                entry["buy_price"] = new_buy_price
                entry["nat_price"] = new_nat_price
                alch_val = entry["alch_val"]
                entry["profit"] = new_qty * (alch_val - (new_buy_price + new_nat_price))

                # Update nature runes stockpile if tracked
                if "owned_nature_runes" in self.config and self.config.get("owned_nature_runes", 0) > 0:
                    self.config["owned_nature_runes"] = max(0, self.config["owned_nature_runes"] - diff_qty)
                    self.save_config()

                # Adjust 4h GE timer for this item
                item_id = entry.get("item_id")
                if not item_id:
                    parts = str(entry.get("id", "")).split("_")
                    if len(parts) >= 2 and parts[1].isdigit():
                        item_id = int(parts[1])
                self._adjust_timer_qty(item_id, entry.get("item"), diff_qty, entry)
                break
        self._recalc_session_totals()
        self.save_session()

    def delete_session_entry(self, entry_id):
        entry_to_delete = None
        for entry in self.session["history"]:
            if entry["id"] == entry_id:
                entry_to_delete = entry
                break

        if entry_to_delete:
            old_qty = entry_to_delete.get("qty", 0)
            item_id = entry_to_delete.get("item_id")
            if not item_id:
                parts = str(entry_to_delete.get("id", "")).split("_")
                if len(parts) >= 2 and parts[1].isdigit():
                    item_id = int(parts[1])
            self._adjust_timer_qty(item_id, entry_to_delete.get("item"), -old_qty, entry_to_delete)

            # Restore nature runes if stockpile tracked
            if "owned_nature_runes" in self.config and self.config.get("owned_nature_runes", 0) > 0:
                self.config["owned_nature_runes"] += old_qty
                self.save_config()

        self.session["history"] = [e for e in self.session["history"] if e["id"] != entry_id]
        self._recalc_session_totals()
        self.save_session()

    def _recalc_session_totals(self):
        total_alchs = 0
        total_profit = 0
        for entry in self.session["history"]:
            total_alchs += entry.get("qty", 0)
            total_profit += entry.get("profit", 0)
        self.session["total_alchs"] = total_alchs
        self.session["total_profit"] = total_profit
        self.session["total_xp"] = total_alchs * 65.0

    def reset_session(self):
        self.session = {
            "total_alchs": 0,
            "total_profit": 0,
            "total_xp": 0,
            "history": []
        }
        self.save_session()
