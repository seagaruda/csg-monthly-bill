#!/usr/bin/env python3
"""
中国南方电网月度账单查询脚本

基于 CubicPill/china_southern_power_grid_stat 的 csg_client 封装，
通过 95598.csg.cn 网页端接口获取个人家庭电费账单。

首次运行需交互式登录（短信/密码+短信/扫码），登录态保存到 session.json，
后续运行自动复用。

依赖: requests, pycryptodome  (见 requirements.txt)
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from csg_client import (  # noqa: E402
    LOGIN_TYPE_TO_QR_CODE_TYPE,
    CSGClient,
    CSGElectricityAccount,
    LoginType,
)

QR_SCAN_TIMEOUT = 300
DEFAULT_SESSION = Path(__file__).resolve().parent / "session.json"


def _input(prompt: str) -> str:
    return input(prompt).strip()


def do_login(client: CSGClient) -> None:
    print(
        "请选择登录方式：\n"
        "  1. 手机号 + 短信验证码\n"
        "  2. 手机号 + 密码 + 短信验证码\n"
        "  3. 扫码登录"
    )
    sel = _input("选择 [1/2/3]: ")
    login_type: LoginType | None = None
    if sel == "1":
        login_type = LoginType.LOGIN_TYPE_SMS
    elif sel == "2":
        login_type = LoginType.LOGIN_TYPE_PWD_AND_SMS
    elif sel == "3":
        print("扫码渠道：\n  1. 南网 APP\n  2. 微信\n  3. 支付宝")
        q = _input("选择 [1/2/3]: ")
        login_type = {
            "1": LoginType.LOGIN_TYPE_CSG_QR,
            "2": LoginType.LOGIN_TYPE_WX_QR,
            "3": LoginType.LOGIN_TYPE_ALI_QR,
        }.get(q)
    if login_type is None:
        print("无效选择"); sys.exit(1)

    if login_type in (LoginType.LOGIN_TYPE_SMS, LoginType.LOGIN_TYPE_PWD_AND_SMS):
        username = os.getenv("CSG_USERNAME") or _input("手机号: ")
        password = None
        if login_type == LoginType.LOGIN_TYPE_PWD_AND_SMS:
            password = os.getenv("CSG_PASSWORD") or _input("密码: ")
        client.api_send_login_sms(username)
        code = _input("验证码已发送，请输入验证码: ")
        if login_type == LoginType.LOGIN_TYPE_SMS:
            auth_token = client.api_login_with_sms_code(username, code)
        else:
            auth_token = client.api_login_with_password_and_sms_code(
                username, password, code
            )
    else:
        login_id, qr_url = client.api_create_login_qr_code(
            channel=LOGIN_TYPE_TO_QR_CODE_TYPE[login_type]
        )
        print(f"请使用对应 APP 扫码登录（{QR_SCAN_TIMEOUT}s 内有效）：\n  {qr_url}")
        deadline = time.time() + QR_SCAN_TIMEOUT
        auth_token = None
        while time.time() < deadline:
            ok, auth_token = client.api_get_qr_login_status(login_id)
            if ok:
                print("扫码成功！"); break
            time.sleep(1)
        if auth_token is None:
            print("扫码超时"); sys.exit(1)

    client.set_authentication_params(auth_token)
    print("登录成功！")


def get_client(session_path: Path, fresh: bool) -> CSGClient:
    if not fresh and session_path.is_file():
        with session_path.open(encoding="utf-8") as f:
            client = CSGClient.load(json.load(f))
        client.initialize()
        if client.verify_login():
            print(f"已从 {session_path.name} 恢复登录态")
            return client
        print("保存的登录态已失效，需要重新登录")
        fresh = True

    if fresh:
        if session_path.is_file():
            session_path.unlink()
        client = CSGClient()
        do_login(client)
        client.initialize()
    with session_path.open("w", encoding="utf-8") as f:
        json.dump(client.dump(), f)
    print(f"登录态已保存到 {session_path.name}")
    return client


def choose_account(client: CSGClient, index: int | None) -> CSGElectricityAccount:
    accounts = client.get_all_electricity_accounts()
    if not accounts:
        print("未查询到绑定的电费账户"); sys.exit(1)
    print(f"\n共 {len(accounts)} 个绑定账户：")
    for i, a in enumerate(accounts):
        print(f"  {i + 1}. 户号 {a.account_number} | {a.user_name} | {a.address}")
    if index is None:
        idx = int(_input(f"\n选择账户 [1-{len(accounts)}]: ")) - 1
    else:
        idx = index - 1
    if not 0 <= idx < len(accounts):
        print("账户序号越界"); sys.exit(1)
    return accounts[idx]


def print_year_table(year: int, total_charge: float, total_kwh: float,
                     by_month: list[dict]) -> None:
    print(f"\n{'=' * 56}")
    print(f"  {year} 年 按月电费账单汇总")
    print(f"{'=' * 56}")
    print(f"{'月份':<8}{'电费(元)':>14}{'电量(kWh)':>16}")
    print("-" * 56)
    for row in by_month:
        print(f"{row['month']:<8}{row['charge']:>14.2f}{row['kwh']:>16.2f}")
    print("-" * 56)
    print(f"{'合计':<8}{total_charge:>14.2f}{total_kwh:>>16.2f}".replace(">>", ">"))
    print(f"{'=' * 56}\n")


def print_month_detail(account: CSGElectricityAccount, year: int, month: int,
                       total_cost, total_kwh, ladder, by_day) -> None:
    print(f"\n{'=' * 60}")
    print(f"  {year}-{month:02d} 每日用电明细  户号 {account.account_number}")
    print(f"{'=' * 60}")
    print(f"当月电费: {_fmt(total_cost)} 元    当月电量: {_fmt(total_kwh)} kWh")
    if ladder.get("ladder") is not None:
        print(f"当前阶梯: {ladder['ladder']}    阶梯单价: {_fmt(ladder.get('tariff'))} 元/kWh"
              f"    剩余额度: {_fmt(ladder.get('remaining_kwh'))} kWh")
    print("-" * 60)
    print(f"{'日期':<14}{'电费(元)':>14}{'电量(kWh)':>16}")
    print("-" * 60)
    for d in by_day:
        print(f"{d['date']:<14}{d['charge']:>14.2f}{d['kwh']:>16.2f}")
    print(f"{'=' * 60}\n")


def _fmt(v) -> str:
    return f"{v:.2f}" if isinstance(v, (int, float)) else "N/A"


def export_csv(year: int, by_month: list[dict], path: Path) -> None:
    with path.open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["账期(年月)", "电费(元)", "电量(kWh)"])
        for row in by_month:
            w.writerow([row["month"], f"{row['charge']:.2f}", f"{row['kwh']:.2f}"])
    print(f"已导出 CSV: {path}")


def main() -> None:
    ap = argparse.ArgumentParser(
        description="中国南方电网月度账单查询（基于 95598.csg.cn 网页端接口）"
    )
    ap.add_argument("--year", type=int, default=dt.datetime.now().year,
                    help="查询哪一年的按月账单汇总（默认当前年）")
    ap.add_argument("--month", type=int, metavar="MM",
                    help="进一步输出指定月份的每日明细")
    ap.add_argument("--account", type=int, metavar="N",
                    help="使用第 N 个绑定账户（不填则交互选择）")
    ap.add_argument("--csv", type=Path, metavar="PATH",
                    help="将按月汇总导出为 CSV 文件")
    ap.add_argument("--fresh-login", action="store_true",
                    help="丢弃保存的登录态，重新登录")
    ap.add_argument("--session", type=Path, default=DEFAULT_SESSION,
                    help=f"登录态文件路径（默认 {DEFAULT_SESSION.name}）")
    args = ap.parse_args()

    client = get_client(args.session, args.fresh_login)
    account = choose_account(client, args.account)
    print(f"\n已选账户：户号 {account.account_number} | {account.user_name} | {account.address}")

    total_charge, total_kwh, by_month = client.get_year_month_stats(account, args.year)
    print_year_table(args.year, total_charge, total_kwh, by_month)

    if args.csv:
        export_csv(args.year, by_month, args.csv)

    if args.month:
        if not 1 <= args.month <= 12:
            print("月份必须在 1-12 之间"); sys.exit(1)
        cost, kwh, ladder, by_day = client.get_month_daily_cost_detail(
            account, (args.year, args.month)
        )
        print_month_detail(account, args.year, args.month, cost, kwh, ladder, by_day)

    bal, arr = client.get_balance_and_arrears(account)
    print(f"账户余额: {bal:.2f} 元    欠费: {arr:.2f} 元")


if __name__ == "__main__":
    main()