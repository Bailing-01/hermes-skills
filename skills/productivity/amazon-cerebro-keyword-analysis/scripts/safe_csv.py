"""
safe_csv.py - 亚马逊/H10 CSV 安全写入工具（跨 skill 共享）

解决 2026-07-19 v41-zh.csv 错位 BUG:
关键词/标题/变体名/ASIN/评论摘录 等字段几乎都含逗号、&、/、' 等特殊字符。
手写 f.write(','.join(row)) 必然导致 Excel 列错位。
本模块强制用 csv.writer(quoting=QUOTE_MINIMAL) + 自验证。

被以下 skill 引用（不要重复创建副本）:
- amazon-cerebro-keyword-analysis (v3, SKILL.md Pitfall #13)
- amazon-keyword-cosmo-attribute-analysis (v4.1, SKILL.md Pitfall #9)

用法:
    import sys
    sys.path.insert(0, '/Users/bailing/.hermes/skills/productivity/amazon-cerebro-keyword-analysis/scripts')
    from safe_csv import write_csv_safe, verify_csv_safe, must_verify

    data = [['anua collagen cream, neck cream for lifting', '648', 'C']]
    write_csv_safe('/tmp/test.csv', ['关键词', '搜索量', '流量等级'], data)
    must_verify('/tmp/test.csv')   # 必跑
"""
import csv
from typing import List


def write_csv_safe(path: str, header: List[str], data: List[List],
                   quoting: int = csv.QUOTE_MINIMAL,
                   encoding: str = 'utf-8') -> int:
    """
    安全写入 CSV（自动给含特殊字符的字段加引号包裹）

    Args:
        path: 输出路径
        header: 表头
        data: 行数据 (list of list)
        quoting: csv.QUOTE_MINIMAL (默认,自动转义) / QUOTE_ALL (强制全字段加引号)
        encoding: utf-8 (默认)

    Returns:
        写入行数
    """
    with open(path, 'w', newline='', encoding=encoding) as f:
        writer = csv.writer(f, quoting=quoting)
        writer.writerow(header)
        n = 0
        for row in data:
            writer.writerow(row)
            n += 1
    return n


def verify_csv_safe(path: str, encoding: str = 'utf-8', verbose: bool = True) -> bool:
    """
    验证 CSV 列数一致性（防止 2026-07-19 v41-zh.csv 错位 BUG 重演）

    Args:
        path: CSV 路径
        encoding: utf-8
        verbose: True=打印验证结果

    Returns:
        True=列数一致, False=有错位行
    """
    with open(path, encoding=encoding) as f:
        rows = list(csv.reader(f))

    if not rows:
        if verbose:
            print(f"⚠️  {path} 是空文件")
        return False

    header_ncols = len(rows[0])
    broken = []
    for i, r in enumerate(rows):
        if len(r) != header_ncols:
            broken.append((i, len(r), r[:3]))

    if verbose:
        if not broken:
            print(f"✅ {path} 列数一致 ({len(rows)-1} 行 × {header_ncols} 列)")
        else:
            print(f"❌ {path} 列数不一致 {len(broken)} 行")
            for b in broken[:5]:
                print(f"   行 {b[0]}: 列数 {b[1]}, 内容: {b[2]}")
    return not broken


def find_broken_rows(path: str, encoding: str = 'utf-8') -> List[dict]:
    """
    找出所有列数不一致的行（排错用）
    """
    with open(path, encoding=encoding) as f:
        rows = list(csv.reader(f))
    if not rows:
        return []
    header_ncols = len(rows[0])
    return [
        {'row': i, 'ncols': len(r), 'preview': r[:3]}
        for i, r in enumerate(rows) if len(r) != header_ncols
    ]


def must_verify(path: str) -> None:
    """
    强制验证 CSV，列数不一致直接 raise（适合 CI/生产环境）

    凡是写完 CSV 必跑这个函数。错位 = 漏数据进 Excel = 用户在培训 / 投放环节抓出来。
    """
    if not verify_csv_safe(path, verbose=True):
        raise ValueError(
            f"CSV 列错位: {path} → 用 write_csv_safe 重写！"
        )


if __name__ == '__main__':
    # 自测 demo
    print("=== safe_csv.py 自测 ===\n")

    test_path = '/tmp/safe_csv_test.csv'
    data = [
        ['anua collagen, neck cream', 648, 'C'],
        ['roca retinol & vitamin c', 1234, 'B'],
        ['normal_kw', 100, 'D'],
    ]
    n = write_csv_safe(test_path, ['关键词', '搜索量', '流量'], data)
    print(f"写入 {n} 行 → {test_path}\n")

    verify_csv_safe(test_path)
    print()

    broken = find_broken_rows(test_path)
    print(f"broken 行: {broken}")
    print(f"\n=== 自测完毕 ===")

    import os
    os.remove(test_path)
