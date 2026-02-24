#!/usr/bin/env python3
"""抓取中国福利彩票双色球历史开奖数据，并给出一个基于频率的“预测”号码。

说明：彩票结果是随机事件，任何预测都无法保证准确。本脚本仅用于学习数据抓取与分析。
"""

from __future__ import annotations

import argparse
import csv
import random
import time
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List
from urllib.error import URLError

import json
from urllib.parse import urlencode
from urllib.request import Request, urlopen

API_URL = "https://www.cwl.gov.cn/cwl_admin/kjxx/findDrawNotice"


@dataclass
class DrawRecord:
    issue: str
    date: str
    reds: List[int]
    blue: int
    sales: str
    poolmoney: str



def parse_code(code: str) -> tuple[List[int], int]:
    parts = [int(x) for x in code.strip().split(",") if x.strip()]
    if len(parts) != 7:
        raise ValueError(f"开奖码格式异常: {code}")
    return sorted(parts[:6]), parts[6]



def fetch_page(page_no: int, page_size: int = 50, timeout: int = 10) -> Dict:
    params = {
        "name": "ssq",
        "issueCount": "",
        "issueStart": "",
        "issueEnd": "",
        "dayStart": "",
        "dayEnd": "",
        "pageNo": page_no,
        "pageSize": page_size,
        "systemType": "PC",
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; ssq-history-fetcher/1.0)",
        "Referer": "https://www.cwl.gov.cn/",
    }
    url = f"{API_URL}?{urlencode(params)}"
    req = Request(url, headers=headers)
    with urlopen(req, timeout=timeout) as resp:
        if resp.status != 200:
            raise RuntimeError(f"请求失败: HTTP {resp.status}")
        return json.loads(resp.read().decode("utf-8"))



def fetch_all_records(page_size: int = 100, sleep_s: float = 0.1) -> List[DrawRecord]:
    first = fetch_page(1, page_size)
    data = first.get("result", [])
    total_page = int(first.get("totalPage", 1))

    all_rows = list(data)
    for page in range(2, total_page + 1):
        payload = fetch_page(page, page_size)
        all_rows.extend(payload.get("result", []))
        time.sleep(sleep_s)

    records: List[DrawRecord] = []
    for row in all_rows:
        code = row.get("red")
        if not code:
            continue
        reds, blue = parse_code(code)
        records.append(
            DrawRecord(
                issue=row.get("code", ""),
                date=row.get("date", ""),
                reds=reds,
                blue=blue,
                sales=row.get("sales", ""),
                poolmoney=row.get("poolmoney", ""),
            )
        )

    # 按期号升序
    records.sort(key=lambda x: x.issue)
    return records



def save_csv(records: List[DrawRecord], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(["issue", "date", "red1", "red2", "red3", "red4", "red5", "red6", "blue", "sales", "poolmoney"])
        for r in records:
            writer.writerow([r.issue, r.date, *r.reds, r.blue, r.sales, r.poolmoney])



def predict_next(records: List[DrawRecord], seed: int | None = None) -> tuple[List[int], int]:
    """基于历史频率做一个示例预测。

    方法：
    1) 最近记录权重更大（线性权重）。
    2) 红球按权重抽取 6 个不重复号码；蓝球抽取 1 个。
    """
    if not records:
        raise ValueError("没有历史记录，无法预测")

    rng = random.Random(seed)

    red_scores = Counter({n: 0.0 for n in range(1, 34)})
    blue_scores = Counter({n: 0.0 for n in range(1, 17)})

    total = len(records)
    for i, rec in enumerate(records, start=1):
        w = i / total
        for n in rec.reds:
            red_scores[n] += w
        blue_scores[rec.blue] += w

    # 将分数转为概率分布，红球做无放回加权抽样
    available = list(range(1, 34))
    picked_reds: List[int] = []
    for _ in range(6):
        weights = [max(red_scores[n], 1e-9) for n in available]
        choice = rng.choices(available, weights=weights, k=1)[0]
        picked_reds.append(choice)
        available.remove(choice)

    picked_reds.sort()

    blue_candidates = list(range(1, 17))
    blue_weights = [max(blue_scores[n], 1e-9) for n in blue_candidates]
    picked_blue = rng.choices(blue_candidates, weights=blue_weights, k=1)[0]

    return picked_reds, picked_blue



def main() -> None:
    parser = argparse.ArgumentParser(description="抓取双色球历史开奖并给出示例预测")
    parser.add_argument("--output", default="data/ssq_history.csv", help="历史数据输出 CSV 路径")
    parser.add_argument("--seed", type=int, default=None, help="随机种子，便于复现预测结果")
    args = parser.parse_args()

    print("正在抓取双色球历史开奖数据...")
    try:
        records = fetch_all_records()
    except URLError as e:
        print(f"抓取失败：{e}")
        print("提示：当前环境可能限制了外网访问，请在可访问 cwl.gov.cn 的网络环境重试。")
        return
    print(f"抓取完成，共 {len(records)} 期")

    output = Path(args.output)
    save_csv(records, output)
    print(f"历史数据已保存到: {output}")

    reds, blue = predict_next(records, seed=args.seed)
    print("\n=== 示例预测（仅供学习，不具备实际投注价值）===")
    print("红球:", " ".join(f"{n:02d}" for n in reds))
    print("蓝球:", f"{blue:02d}")


if __name__ == "__main__":
    main()
