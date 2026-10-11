# 🧙‍♂️ AlchMate - OSRS High Alchemy & Crafting Profit Tracker

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-Windows-0078D6.svg)](https://www.microsoft.com/windows)

A real-time, desktop companion and in-game RuneLite overlay tool for **Old School RuneScape (OSRS)** that monitors live Grand Exchange prices via the official OSRS Wiki Real-time Prices API. It tracks high-margin High Alchemy flips, auto-detects item acquisition origin (GE vs P2P/W308), tracks Bond progression and invested GE capital, evaluates Craft-then-Alch skilling recipes, manages 4-hour Grand Exchange buy limit timers, tracks Nature Rune bank stockpiles, and logs session profit and Magic XP.

## ✨ Key Features

- **🛒 GE Cart Live Sync & Offer Cancellation Bugfix (v1.3.38):**
  - **Fixed GE Buy Offer Cancellation Cascade:** Resolved a critical bug where cancelling a single buy offer on the Grand Exchange caused the entire shopping cart to be wiped out.
  - **Account Name Sanitization & Delimiter Safety:** Fixed parsing for account usernames containing underscores (e.g. `iron_alt_42`) or Unicode non-breaking spaces from RuneLite, ensuring active monitored characters always match incoming bridge events accurately.
  - **Manual Cart Item Preservation:** Fully protects manually added and auto-filled shopping cart items during in-game GE slot cancellations and updates.

- **🔒 Tree Open/Closed State Persistence Bugfix (v1.3.37):**
  - **Fixed Auto-Refresh Tree Expansion Bug:** Resolved an issue where background periodic price updates (or the 2-minute auto-refresh timer) would inadvertently re-expand collapsed tiers in the Skilling Guide Material Family Tree. The application now uses recursive open-node tracking and persistent initialization flags, ensuring user-defined open/collapsed node states remain 100% stable and untouched across refreshes.

- **🌲 Smithing Material Family Tree & Opportunity Profit Analysis (v1.3.36):**
  - **Comprehensive Hierarchical Tree Mode:** Switch between `🌲 Material Chain Tree` and `📈 Level Progression (1-99)` in the Skilling Guide toolbar. The Material Chain Tree visualizes the complete production pipeline from raw ores to finished weapons and armor across all 6 metal tiers (Bronze, Iron, Steel, Mithril, Adamant, and Rune).
  - **🏷️ Instant Baseline Benchmark (`↳ 🏷️ Sell Bar on GE`):** Every metal tier unfolds with a dedicated benchmark row displaying the exact baseline profit of smelting the bar from raw ores and selling it directly on the Grand Exchange.
  - **🎯 Chain Verdict Badges & Opportunity Cost Analysis:**
    - 🟢 **`⭐ Beats Bar (+{diff} gp vs GE)`:** Smithing this equipment yields MORE gold profit than selling the raw bars on GE, while giving full Smithing XP!
    - 🟡 **`⚡ Subsidized XP ({cost} gp/xp)`:** Whole chain from raw ores yields net positive gold in your pocket, trading a portion of bar profit to buy ultra-cheap anvil XP!
    - 🔴 **`⛔ Sell Bar on GE ({diff} gp vs bar)`:** Making this item results in net loss or high opportunity loss from raw ores; sell bars on GE instead!
  - **⚔️ 157 Comprehensive Items & Multi-Level Dropdowns:** Includes all 157 craftable weapons, armor, dart tips, arrowtips, unfinished bolts, knives, nails, and cannonballs. Clicking `▶` on any item expands into its exact ingredients (`↳ 5x Mithril bar`, `↳ 5x Mithril ore`, `↳ 10x Coal`, `↳ 1x Nature rune`) with individual buy ceilings!
  - **🛡️ Adaptive Blast Furnace (P2P) vs Standard Furnace (F2P):** Toggling "P2P Methods" dynamically recalculates coal fuel requirements—halved coal for Blast Furnace vs full coal for Free-to-Play furnaces.
  - **🔄 Recursive Expand All / Collapse All:** `➕ Expand All` and `➖ Collapse All` recursively expand and collapse all tiers and ingredient depths simultaneously.

- **⚔️ Complete Tier Smithing, Crafting & Fletching Recipe Suite (v1.3.35):**
  - **Full Rune, Adamant, Mithril & Steel Smithing Coverage:** Expanded the Skilling Guide database to **76 detailed brackets**, including all craftable weapons, armor, dart tips, arrowtips, unfinished bolts, knives, and cannonballs across Rune (levels 85–99), Adamant (levels 70–88), Mithril (levels 50–68), and Steel (levels 30–48).
  - **Comprehensive Leveling Guides for Crafting & Fletching:** Expanded Crafting to **24 brackets** (including gem cutting, all elemental battlestaves, blue/black d'hide bodies, and high-level Amethyst crafting) and Fletching to **18 brackets** (including full dart progression from Bronze to Dragon, broad ammunition, and bow cutting/stringing).
  - **Multi-Output Quantity Precision:** Fixed revenue and profit calculation in `recalculate_guide_table()` for recipes that yield multiple outputs per bar (e.g., 10x dart tips, 15x arrowtips, 4x cannonballs, 5x knives, 10x bolts, 15x nails), ensuring 100% accurate GP/XP, total batch revenue, and breakeven ceilings.
  - **Massive Recipe Expansion Across Craft & Alch & GE Moneymaking:** Expanded `💰 Craft & Sell GE` to **167 production recipes** and `🔨 Craft & Alch` to **195 recipes**, adding all high-volume ammunition, weapons, and armor components.

- **📂 Expandable Ingredient Dropdown Trees in Skilling Guide (v1.3.34):**
  - **Hierarchical Ingredient Tree (`▶` / `▼`):** The Skilling Guide is now an interactive dropdown tree! Click `▶` on any method (such as bar smelting, bows, potions, or jewellery) to expand and reveal its exact raw materials indented underneath (`↳ 1x Iron ore`, `↳ 2x Coal`).
  - **Individual Buy Ceilings for Each Ore & Material:** Each individual ingredient row calculates and displays its own dedicated **`🎯 Max Mat Buy` ceiling** (`target_buy_p`) and breakeven ceiling, telling you the exact ceiling price to pay for each component to maintain your profit margin.
  - **Live Offer & Ask Market Prices:** Ingredient rows display real-time GE Target Offer (Bid), Instant Buy (Ask), total quantity scaled to your goal level, and total batch gold cost.
  - **1-Click Copy on Child Cells:** Click any ingredient's Max Buy price, Bid Offer, Ask, or quantity to instantly copy the exact integer to your clipboard for rapid in-game trading.
  - **➕ Expand All / ➖ Collapse All:** One-click toolbar controls to expand all training methods at once or collapse back to compact rows.
  - **Full Multi-Material Ceilings in Craft & Sell GE:** Secondary ingredients (like Coal, second ores, secondaries) in `💰 Craft & Sell GE` now calculate and display individual best buy ceilings and breakeven values alongside primary materials.

- **🔨 Comprehensive Bar Smelting & Blast Furnace Training (v1.3.33):**
  - **Complete Bar Smelting in Skilling Guide:** Added mathematically exact training brackets for smelting **Bronze, Iron, Silver, Steel, Gold (with Goldsmith Gauntlets), Mithril, Adamantite, and Runite bars** into the Skilling Guide tab.
  - **Blast Furnace vs. Standard Furnace Methods:** Full support for both premier Members Blast Furnace training (halved coal requirements, 110k+ XP/hr, and 1M+ GP/hr profit) and standard Furnace methods (Edgeville/Falador/Lumbridge) for Free-to-Play players.
  - **Family Crest Quest Integration:** Added *Family Crest* to Smithing quest unlocks, highlighting Goldsmith Gauntlets (boosts Gold bar smelting from 22.5 ➔ 56.2 XP ea, unlocking 350k+ XP/hr at Blast Furnace).
  - **Craft & Sell GE Expansion:** Added furnace smelting recipes for Bronze, Silver, Steel, Gold, Mithril, Adamantite, and Runite bars into `💰 Craft & Sell GE`, providing F2P production recipes alongside Blast Furnace.

- **🏷️ Target Sell Price in Craft & Sell GE (v1.3.32):**
  - **Accurate In-Game GE Listing Price:** The sell column now displays the exact **Target Sell Price** you should list the item for on the Grand Exchange (`gross_sell_ea`), rather than the net post-tax amount.
  - **1-Click Copy Listing Price:** Clicking the cell copies the exact gross listing price to your clipboard so you can paste it directly into the in-game GE offer window without accidentally double-taxing your offer.
  - **Transparent Tax Accounting:** The hover tooltip details the full breakdown: Target GE Listing Price, 1% Jagex tax deduction, and Net Revenue received. Net profit and ROI remain 100% tax-accurate.

- **🛡️ Full-Stack Audit, Column Sorting & Clipboard Hardening (v1.3.31):**
  - **Comprehensive Production Stability Audit:** Performed deep audit across all 9 application modules, eliminating potential edge cases, crashes, and index mismatches.
  - **Column Sorting Corrections:** Fixed Treeview column index lookups across both *Craft & Alch* and *Craft & Sell GE* tabs, ensuring multi-direction sorting works flawlessly on every single column without exception.
  - **1-Click Cell Price Copying in Craft & Alch:** Clicking Material Cost, Alch Value, or Profit cells in *Craft & Alch* now copies the exact numerical values directly to the clipboard.
  - **Clipboard Lock Protection:** Hardened `copy_to_clipboard` with OS-level exception handling and `pyperclip` fallback to prevent rare Windows clipboard locking errors.
  - **Full Skill State Preservation:** Expanded default profile tracking to include *Smithing*, *Herblore*, and *Cooking* levels alongside *Crafting*, *Fletching*, and *Magic*, ensuring multi-skill configurations persist across restarts and account switches.
  - **Enhanced Keyboard Shortcuts:** Bound `Esc` across all search inputs to instantly reset filters.

- **💰 Brand New "Craft & Sell GE" Tab (v1.3.30):**
  - **Pure Grand Exchange Production Moneymaking:** A completely dedicated production moneymaking tab featuring over 120 verified recipes across **Herblore, Crafting, Fletching, Smithing, Cooking, and Magic**. Buy raw ingredients on the Grand Exchange, process them, and sell the finished items directly on the GE for pure gold profit!
  - **📂 Expandable Ingredient Rows (`▶` / `▼` Dropdown):** Click the arrow or double-click any product (e.g. *Rune pickaxe*, *Prayer potion(3)*, *Air battlestaff*) to expand its raw material breakdown directly underneath it.
  - **🎯 Exact GE Bid & Ask Pricing with 1-Click Copy:**
    - Parent finished items display Total Material Cost at Bid vs Ask, Net GE Sell Price (with 1% OSRS tax deducted), Profit ea, ROI %, 4h Limit, Batch Profit, and GP/Hr.
    - Expanded ingredient rows display their exact **Target Offer (Bid)**, **Instant Buy (Ask)**, and **🎯 Best Buy Ceiling** (the maximum price you can pay for that raw material on the GE to guarantee profit!).
    - Clicking any price cell instantly copies the number directly to your clipboard for instant GE order placement.
  - **🛡️ Strict F2P vs Members Isolation:** Unticking Members or checking F2P Only completely hides 100% of Members skills (Herblore, Fletching) and Members-only materials/recipes across the entire dashboard.
  - **1-Click Expand All / Collapse All:** Instantly expand all recipes or collapse back to summary view with a single click.

- **🌐 Universal Search Across ALL Tabs & 57 New Recipes (v1.3.29):**
  - **Universal Instant Search:** The top search bar (`self.ent_search`) now dynamically filters live data across **EVERY single tab**: *Pure High Alch*, *Smart Picks*, *Craft & Alch*, *Level Guide*, *4h GE Timers*, *Session Tracker*, and *Alert Feed*.
  - **Dual Field Sync:** Typing in either the global search bar or the Craft & Alch search bar instantly keeps both fields in sync.
  - **Material & Ingredient Search:** Search recipes not just by finished item name, but also by component materials (e.g. typing `mithril bar`, `yew logs`, `cosmic rune`, or `ruby` instantly shows all relevant crafts).
  - **Non-Intrusive Ctrl+F:** Pressing `Ctrl+F` focuses the search bar on whichever tab you are currently viewing without jarringly switching tabs. Pressing `Esc` clears all filters instantly.
  - **Massive Recipe Expansion (+57 Recipes):** Added full coverage across all 4 skilling categories:
    - *Smithing:* Added Steel, Mithril, Adamant, Iron, and Bronze 2h swords, battleaxes, platelegs, plateskirts, warhammers, and scimitars.
    - *Crafting:* Added Zenyte jewellery (ring, necklace, bracelet, amulet), Silver jewellery (Opal, Jade, Topaz), and Leather / Hardleather bodies.
    - *Fletching:* Added full bow crafting from logs + bow string (Magic, Yew, Maple, Willow, Oak shortbows & longbows), unstrung cutting recipes, and crossbows (Dragon, Adamant, Mithril, Steel).
    - *Magic Enchanting:* Added Zenyte jewellery enchanting (Amulet of torture, Necklace of anguish, Tormented bracelet, Ring of suffering), Onyx jewellery (Fury, Berserker, Regen, Stone), Ring of recoil, and Enchanted bolts (Onyx, Dragonstone, Diamond, Ruby).

- **🎯 Exact Level Requirements Accuracy (v1.3.28 Fix):**
  - **Smithing Levels Corrected:** Fixed **Iron platebody** requirement to **Level 33** (previously listed as 29). Added **Bronze platebody** for Levels 18–33 to cleanly bridge from Level 29 (*The Knight's Sword*) up to Level 33. Iron platebody now properly covers Level 33➔48 (until Steel platebodies unlock at 48).
  - **Fletching Bow Tiers Corrected:** Split Oak bows into **Oak shortbow** (Level 20) and **Oak longbow** (Level 25); updated **Willow longbow** to its true Level 40 requirement.
  - **Crafting Tiers Corrected:** Added **Leather body** for Levels 14–20, and updated **Cut Sapphire** to its correct Level 20 requirement.
- **📦 Total Material Breakdown & Interactive Skilling Cards (v1.3.27+):**
  - **Total Materials / Bars Needed:** New dedicated column dynamically calculates the exact total materials/bars required across each training bracket (or remaining to reach your target goal level).
  - **1-Click Total Quantity Copy:** Click the `Total Mats Needed` column or right-click to copy the exact total material quantity directly to your clipboard for instant buying on the Grand Exchange.
  - **Full Skilling Tooltip Cards:** Rich hover tooltip cards for every skilling step, detailing XP per action, total units and materials needed, breakeven ceilings, current market margin, live GP/XP, net profit/loss, and strategy tips.
- **🎯 Breakeven & Target Material Buy Prices (v1.3.26+):**
  - **Live Breakeven Ceilings:** Automatically calculates the exact maximum Grand Exchange buy price for bars, dragonhides, and logs to train at **zero gold loss** based on live High Alch / GE sell values and real-time Nature Rune prices.
  - **Configurable Safety Margin:** Real-time `Target Margin` input lets you set a desired profit per item (e.g. 50, 100, 200 gp), automatically recalculating required GE buy bids.
  - **1-Click GE Price Copy:** Click the `🎯 Max Mat Buy` column to copy the exact integer buy price directly to your clipboard.
  - **Permanent Filter Lock:** Game bridge snapshots (RuneLite) no longer overwrite or revert your manual F2P / Members filter selection.
- **🛡️ Strict F2P vs Members Isolation (v1.3.25+):**
  - **F2P Only Mode:** Toggling `F2P Only` strictly hides 100% of Members items, recipes, quests, and brackets across all tabs (Smithing hides Cannonballs and P2P quests; Crafting hides Dragonhide bodies, Battlestaves, and Unpowered orbs).
  - **Fletching P2P Warning:** When Free-to-Play is selected, Fletching cleanly indicates that it is a 100% Members-only skill in Old School RuneScape.
  - **Mutual Sync:** Checking `F2P Only` or `Members` seamlessly syncs across the global top bar and the Skilling Guide tab.
- **🎓 Skilling & Level Training Guide (v1.3.24+):**
  - **Progression Database:** Comprehensive, mathematically exact leveling brackets for **Smithing, Fletching, Crafting, and Magic**.
  - **📍 "You Are Here" Tracking:** Automatically highlights your current training bracket based on your live in-game stats.
  - **📜 Early Game Quest Skips:** Instant 1-click browser access to OSRS Wiki quest guides for critical XP skips (*The Knight's Sword* 1➔29, *The Tourist Trap* 1➔26, *Misthalin Mystery*, etc.).
  - **Live Market GP/XP Rates:** Live Grand Exchange price evaluation computing exact GP/XP cost or net gold profit for each training step.
  - **🪄 Alch vs. 🏪 GE Disposal:** Intelligent recommendations on whether to High Alch your crafted products or sell them on the Grand Exchange.
  - **🛒 1-Click Skilling Shopping Cart & Bank Tags:** Instantly add materials to your cart, copy formatted skilling shopping lists, or export RuneLite Bank Tag tabs (`banktags,1,...`).
- **🔒 Dedicated Multi-Instance / Monitored Character Lock:**
  - **Focus Lock:** Dropdown selector in the top bar to lock 100% of dashboard monitoring (Cash, Nats, Levels, GE Cart, Session, Timers) to a specific character (e.g. `'Main'`, `'AlchAlt'`).
  - **Silent Background Processing:** Secondary clients / alts update silently in the background without stealing focus or overwriting active data.
- **⭐ Smart Picks & Top Recommendations:**
  - **🏆 All-Time Workhorses:** Instant access to Hall-of-Fame staples that veteran players rely on (Rune platelegs, plateskirts, 2h swords, kiteshields, battleaxes, Adamant platebody, Battlestaves, D'hide) with custom strategic verdicts.
  - **⚡ Fast Fills (<5m):** High-velocity items with verified 5-minute sales that fill in minutes.
  - **💰 Top 4h Batch Profit:** Highest total profit achievable in a single 4-hour Grand Exchange cycle.
  - **🌙 Overnight Sleepers:** High-margin patient items ideal for queuing low bids before logging off.
  - **⚡ 1-Click Auto-Fill Empty GE Slots:** Intelligently allocates empty GE slots (up to 8) with the most profitable non-cooldown items, automatically sized to your cash stack budget.
- **🕒 OSRS Market Clock & Liquidity Window:**
  - Live Grand Exchange server clock (UTC) synchronized with global player activity curves.
  - Real-time Activity Meter and Status Badges (`🟢 Peak Liquidity Window`, `🟡 Evening Wind-Down`, `🌙 Off-Peak Sleepers Window`, `🌅 Morning Ramp-Up`).
  - Actionable market timing advice on whether to place fast flip bids or queue up patient overnight sleeper buy orders.
- **🔌 RuneLite Live Auto-Bridge (100% Passive & TOS Compliant):**
  - **Zero In-Game Automation / 100% Read-Only:** Only listens to passive game events; performs zero clicks or actions.
  - **Auto GE Limit Timers:** Starts tick-accurate 4-hour cooldown timers the moment your Grand Exchange buy fills or starts buying.
  - **Auto Session Profit Logging:** Automatically records filled GE buy orders to your Session Tracker with exact prices paid and profit calculated.
  - **Live Inventory & Bank Sync:** Automatically keeps your active Cash Stack and Nature Rune stockpiles updated in real time.
  - **Multi-Instance / Multi-Account Tracking:** Run multiple client instances simultaneously; separate timers, cash stacks, and session profits per character with an instant Account dropdown selector.
  - **Live Stat Sync:** Synchronizes your Crafting, Smithing, Fletching, and Magic levels as well as World membership status on login.
- **⚡ Real-Time Price Sync:** Fetches live bid/ask margins and 24-hour traded volumes directly from the OSRS Wiki API.
- **⏱️ Dynamic 4-Hour GE Limit Tracking:**
  - Real-time limit depletion with remaining and cooldown formatting (e.g. `5 / 70 (3h 52m)` or `0 / 70 (1h 44m)`).
  - Active cooldown indicators that automatically reset when the 4-hour window expires.
  - Desktop toast alerts and audio chimes when limits reset.
- **🌿 Nature Rune Stockpile Tracker:**
  - Track owned Nature Runes in your bank.
  - Cart automatically alerts you if you need to purchase more runes before your alch session.
  - Automatically deducts used runes on session log.
  - Optional fixed cost override (leave empty to use live standard GE prices).
- **💰 Smart Cash Stack Baseline (`Max Afford`):**
  - Accurately calculates how many items you can afford based on your remaining budget and active limits without zeroing out table rows.
  - Easily toggle budget constraints on or off for unlimited calculations.
- **🛒 Grand Exchange Cart & Fast 1-Click Pasting:**
  - **Click Column #1:** Copies exact buy quantity.
  - **Click Column #2 (Name):** Copies item name for fast GE search.
  - **Click Column #3 (Bid):** Copies patient buy offer price.
  - **Click Column #4 (Ask):** Copies instant buy price.
  - **Right-Click:** Set custom quantities or remove items.
- **🔨 Craft & Alch Breakdown:**
  - Interactive recipe tree comparing the cost of buying raw materials, crafting, and alching vs. buying finished items.
  - Filter recipes by your in-game Crafting, Fletching, and Magic levels.
- **📋 RuneLite Bank Tag Exporter:**
  - 1-click export of your active cart or master profitable alch list as a RuneLite Bank Tag tab (`banktags,1,...`).
- **🔍 Instant Live Search & Filter:**
  - Filter items in real time as you type (`Ctrl + F`).
  - Min Profit threshold (leave blank to display all items including break-even and XP alchs).

---

## ⌨️ Keyboard Shortcuts

| Shortcut | Action |
| :--- | :--- |
| **`F5`** | Immediately refresh live market prices |
| **`Ctrl + F`** | Jump to search bar |
| **`Esc`** | Clear active search |
| **`Enter`** | Apply cash stack or filter input |

---

## 📥 Download & Installation

Choose the version that best fits your needs:

| Edition | File | Best For | Direct Download Link |
| :--- | :--- | :--- | :--- |
| **🚀 Windows Installer (Recommended)** | `AlchMate_Setup.exe` | Standard installation with Start Menu & Desktop shortcuts, clean uninstall, and repair mode. | [⬇️ Download Installer](https://github.com/jef11222/osrs-alch-tracker/releases/latest/download/AlchMate_Setup.exe) |
| **⚡ Portable Edition (.exe)** | `AlchMate_Portable.exe` / `AlchMate.exe` | Zero installation required. Run directly from your Downloads folder, USB drive, or desktop. | [⬇️ Download Portable (.exe)](https://github.com/jef11222/osrs-alch-tracker/releases/latest/download/AlchMate_Portable.exe) |
| **📦 Portable Edition (.zip)** | `AlchMate-v1.0.0-Portable.zip` | Standalone ZIP containing portable executable, plugin JAR, and readme. | [⬇️ Download Portable (.zip)](https://github.com/jef11222/osrs-alch-tracker/releases/latest/download/AlchMate-v1.0.0-Portable.zip) |

> 🔗 **All Versions & Release Notes:** [View Latest GitHub Release](https://github.com/jef11222/osrs-alch-tracker/releases/latest)

---

## 🔌 RuneLite Plugin (AlchMate)

AlchMate includes an official in-game RuneLite bridge plugin (`AlchBridgePlugin.jar`):
- **Live In-Game HUD Overlay:** Displays live alchs/hr, net profit, batch completion ETA, skilling pace, and 2-line Bond roadmap.
- **Side Panel Top 10 Alchs:** Direct in-game panel displaying live profitable alch items with 1-click clipboard copy.
- **Auto-Detection:** Automatically distinguishes items acquired via Grand Exchange from Player-to-Player trades (e.g. W308 Anvil).
- **Invested GE Wealth Tracking:** Accurately accounts for coins sitting in active buy offers in the Bond tracker.

To install manually:
1. Place `AlchBridgePlugin.jar` into your `.runelite/plugins/` directory (or run `Update-Bridge-Plugin.bat`).
2. Start RuneLite. The "AlchMate" plugin will appear in your plugin list and sidebar.

---

## 🚀 Running from Source

Ensure you have **Python 3.10+** installed:
```bash
# Clone the repository
git clone https://github.com/jef11222/osrs-alch-tracker.git
cd osrs-alch-tracker

# Run the application
python main.py
```

### Building Standalone Executable
```bash
pip install pyinstaller
python -m PyInstaller AlchMate.spec --noconfirm
```

---

## 📁 Project Structure

```
osrs-alch-tracker/
├── api.py               # OSRS Wiki Real-time Prices API client
├── crafting.py          # Crafting & fletching recipe definitions
├── skilling_guide.py    # Skilling & Level training progression and quest skip DB
├── state.py             # State persistence (config, 4h timers, session log)
├── gui.py               # Tkinter GUI (custom dark theme, tooltips, tables)
├── main.py              # Application entry point
├── run.bat              # 1-click launch batch script
├── Launch_Dashboard.vbs # Silent background launcher
└── .gitignore           # Ignores build artifacts and local caches
```

---

## 📜 License

This project is licensed under the [MIT License](LICENSE) - see the [LICENSE](LICENSE) file for details.
