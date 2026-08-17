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
- `requests`
- `pycryptodome`

```bash
pip install -r requirements.txt
```

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
- `requests`
- `pycryptodome`

```bash
pip install -r requirements.txt
```

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