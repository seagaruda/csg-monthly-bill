# CSG Monthly Bill Query | 中国南方电网月度账单查询

[English](#english) | [中文](#中文)

---

## 中文

查询**中国南方电网（CSG）**个人家庭电费的月度账单，按月汇总输出，支持每日明细与 CSV 导出。

> ⚠️ **免责声明**：本项目通过 `95598.csg.cn` 网页端接口获取数据，**非官方公开 API**。接口来自对网页前端 JS 的逆向，随时可能变动。本项目仅供个人查询本人绑定账户的电费账单，请勿用于商业用途或大规模抓取。使用本项目的风险由使用者自行承担。

### 功能

- 按月汇总全年电费账单（一次请求返回 12 个月电费/电量）
- 指定月份的每日用电明细（电费、电量、阶梯信息）
- 账户余额与欠费查询
- 多账户支持（交互选择或命令行指定）
- CSV 导出
- 登录态本地持久化，避免频繁登录
- 三种登录方式：手机号+短信、手机号+密码+短信、扫码（南网 APP / 微信 / 支付宝）

### 依赖

- Python ≥ 3.10
- `requests`、`pycryptodome`、`brotli`

```bash
pip install -r requirements.txt
```

> ⚠️ `brotli` 为**必要依赖**：`95598.csg.cn` 认证后的接口返回 Brotli 压缩响应，缺该库会报 `json.decoder.JSONDecodeError: Expecting value`。

### 快速开始

```bash
git clone https://github.com/seagaruda/csg-monthly-bill.git
cd csg-monthly-bill
pip install -r requirements.txt

# 在你自己的终端运行（手机号/验证码仅在本机输入，不经过任何第三方或 AI）
python3 query_monthly_bill.py
```

首次运行会交互式登录（见下），登录态保存到本地 `session.json`，**之后查询无需再次登录**。

### 用法

```bash
cd csg_bill_query

# 首次运行：交互式登录，登录态保存到 session.json
python3 query_monthly_bill.py                       # 查当年按月账单
python3 query_monthly_bill.py --year 2025           # 查 2025 全年各月
python3 query_monthly_bill.py --year 2026 --month 7 # 再输出 7 月每日明细
python3 query_monthly_bill.py --csv bill_2026.csv   # 导出 CSV
python3 query_monthly_bill.py --account 1           # 跳过账户选择，用第 1 个
python3 query_monthly_bill.py --fresh-login         # 丢弃登录态，重新登录
```

也可通过环境变量提供手机号/密码（避免交互输入）：

```bash
export CSG_USERNAME=13800000000
export CSG_PASSWORD=your_password
python3 query_monthly_bill.py --fresh-login
```

### 登录方式与隐私

首次运行需登录「南网在线」，三种方式任选其一：

| 方式 | 需输入 | 说明 |
|------|--------|------|
| 1 手机号+短信 | 手机号、短信验证码 | 最常用 |
| 2 手机号+密码+短信 | 手机号、密码、短信验证码 | 密码+验证码双重 |
| 3 扫码 | 无需输入任何信息 | 用南网 APP / 微信 / 支付宝扫码，**最省事且不暴露手机号** |

**隐私边界（重要）**：

- 请**在你自己的终端**运行本脚本。手机号、密码、验证码仅在本地终端由你本人输入，**不经过任何第三方服务或 AI 大模型**。
- 若通过 AI agent 使用：让 AI 提供/克隆代码即可，但**登录这一步请自己在终端完成**，不要把手机号/验证码发给 AI。登录成功后把 `session.json` 留在本地，后续查询可交给 AI（只需只读的 token，且 token 可随时用 `--fresh-login` 失效重建）。
- `session.json` 含登录 token，**仅存本地**，已被 `.gitignore` 排除，切勿提交或分享。
- 推荐用**扫码登录**：全程无需输入手机号/验证码，隐私性最佳。

### 参数

| 参数 | 说明 |
|------|------|
| `--year YYYY` | 查询哪一年的按月账单汇总（默认当前年） |
| `--month MM` | 进一步输出指定月份的每日明细 |
| `--account N` | 使用第 N 个绑定账户（不填则交互选择） |
| `--csv PATH` | 将按月汇总导出为 CSV |
| `--fresh-login` | 丢弃保存的登录态，重新登录 |
| `--session PATH` | 登录态文件路径（默认 `session.json`） |

### 工作原理

`csg_client/` 取自开源项目 [CubicPill/china_southern_power_grid_stat](https://github.com/CubicPill/china_southern_power_grid_stat)（GPLv3，Home Assistant 集成），封装了 `95598.csg.cn` 网页端的全部接口逻辑：

- 登录流程（短信验证码 / 密码+短信 / 扫码）
- 请求参数 AES 加密、密码 RSA 加密、签名
- 账户列表、月度账单、每日明细、余额欠费等高层接口

`const.py` 中的 `PARAM_KEY` / `PARAM_IV` / `CREDENTIAL_PUBKEY` 均来自 `95598.csg.cn` 前端公开 JS 文件，任何人访问网页即可获取，非私密凭证。

### 安全提示

- `session.json` 含登录态，**已由 `.gitignore` 排除**，切勿提交到版本库或分享
- 登录态会过期，过期后用 `--fresh-login` 重新登录
- 建议在虚拟环境中运行：`python3 -m venv .venv && source .venv/bin/activate`

### 致谢

- [CubicPill/china_southern_power_grid_stat](https://github.com/CubicPill/china_southern_power_grid_stat) — 核心接口封装
- [Accurio/CSG-Bill-Reader](https://github.com/Accurio/CSG-Bill-Reader) — PDF 账单解析参考

### 许可证

GPL-3.0（因 `csg_client` 派生自 GPLv3 项目）

---

## English

Query **China Southern Power Grid (CSG)** residential electricity bills aggregated by month, with optional daily breakdown and CSV export.

> ⚠️ **Disclaimer**: This project fetches data via the `95598.csg.cn` web endpoint, which is **NOT an official public API**. The endpoints were reverse-engineered from the website's frontend JS and may change at any time. Use only to query your own bound account's bills. Do not use for commercial purposes or large-scale scraping. Use at your own risk.

### Features

- Full-year monthly bill summary in a single request (12 months of charge / kWh)
- Daily breakdown for a specified month (charge, kWh, tiered-pricing info)
- Account balance and arrears
- Multiple accounts (interactive pick or CLI flag)
- CSV export
- Local session persistence to avoid repeated logins
- Three login methods: phone+SMS, phone+password+SMS, QR scan (CSG app / WeChat / Alipay)

### Requirements

- Python ≥ 3.10
- `requests`, `pycryptodome`, `brotli`

```bash
pip install -r requirements.txt
```

> ⚠️ `brotli` is **required**: authenticated endpoints from `95598.csg.cn` return Brotli-compressed responses; without it you'll get `json.decoder.JSONDecodeError: Expecting value`.

### Quick Start

```bash
git clone https://github.com/seagaruda/csg-monthly-bill.git
cd csg-monthly-bill
pip install -r requirements.txt

# Run in YOUR OWN terminal (phone/SMS code stay local, never sent to any third party or AI)
python3 query_monthly_bill.py
```

The first run does an interactive login (see below); the session is saved to a local `session.json` and **no further login is needed** for subsequent queries.

### Usage

```bash
cd csg_bill_query

# First run: interactive login, session saved to session.json
python3 query_monthly_bill.py                       # current year, monthly summary
python3 query_monthly_bill.py --year 2025           # full-year 2025
python3 query_monthly_bill.py --year 2026 --month 7 # also print July daily detail
python3 query_monthly_bill.py --csv bill_2026.csv   # export CSV
python3 query_monthly_bill.py --account 1           # use 1st bound account
python3 query_monthly_bill.py --fresh-login         # discard session, re-login
```

Credentials can be supplied via environment variables to skip interactive input:

```bash
export CSG_USERNAME=13800000000
export CSG_PASSWORD=your_password
python3 query_monthly_bill.py --fresh-login
```

### Login & Privacy

The first run requires logging in to 「南网在线」. Pick one of three methods:

| Method | Input needed | Notes |
|--------|--------------|-------|
| 1 Phone + SMS | phone number, SMS code | Most common |
| 2 Phone + Password + SMS | phone, password, SMS code | Two-factor |
| 3 QR scan | none | Scan with CSG app / WeChat / Alipay — **easiest, no phone number exposed** |

**Privacy boundary (important)**:

- Run the script **in your own terminal**. Phone number, password, and SMS code are typed only by you locally and **never pass through any third party or AI model**.
- If using an AI agent: let the AI clone/provide the code, but **do the login step yourself in a terminal** — don't send your phone number / SMS code to the AI. After login, `session.json` stays local; subsequent queries can be handed to the AI (it only needs a read-only token, revocable anytime via `--fresh-login`).
- `session.json` contains the login token, **stays local only**, excluded by `.gitignore` — never commit or share it.
- **QR login** is recommended for best privacy: no phone number or SMS code typed at all.

### Options

| Flag | Description |
|------|-------------|
| `--year YYYY` | Year of the monthly summary (default: current year) |
| `--month MM` | Also print daily breakdown for this month |
| `--account N` | Use the N-th bound account (interactive if omitted) |
| `--csv PATH` | Export monthly summary to CSV |
| `--fresh-login` | Discard saved session and log in again |
| `--session PATH` | Session file path (default: `session.json`) |

### How it works

`csg_client/` is taken from [CubicPill/china_southern_power_grid_stat](https://github.com/CubicPill/china_southern_power_grid_stat) (GPLv3, a Home Assistant integration) and encapsulates all `95598.csg.cn` web endpoint logic:

- Login flows (SMS code / password+SMS / QR scan)
- Request parameter AES encryption, password RSA encryption, signing
- High-level APIs: account list, monthly bills, daily detail, balance/arrears

`PARAM_KEY` / `PARAM_IV` / `CREDENTIAL_PUBKEY` in `const.py` come from `95598.csg.cn`'s public frontend JS bundles — anyone visiting the site can read them; they are not secrets.

### Security notes

- `session.json` contains the login session and is **excluded by `.gitignore`** — never commit or share it
- Sessions expire; use `--fresh-login` when that happens
- Recommended to run in a venv: `python3 -m venv .venv && source .venv/bin/activate`

### Credits

- [CubicPill/china_southern_power_grid_stat](https://github.com/CubicPill/china_southern_power_grid_stat) — core API client
- [Accurio/CSG-Bill-Reader](https://github.com/Accurio/CSG-Bill-Reader) — PDF bill parser reference

### License

GPL-3.0 (`csg_client` is derived from a GPLv3 project)