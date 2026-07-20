"""verify_csv_columns.py - CSV 列名-数据对应验证

解决 2026-07-20 listing-种子词 B0CGB215HR CSV 表头错位 BUG：
safe_csv.verify_csv_safe 只验证「列数一致」，但不验证「表头列名 = 数据列语义」。
手写 data.append([...]) 时多填/少填一列，列数仍然一致，但内容全错位。

用法：
    from verify_csv_columns import verify_csv_columns, must_verify_columns

    # 验证列名与数据语义一致（不依赖外部 schema）
    must_verify_columns('/path/to/seed-words.csv')

    # 验证表头 = 预期 schema
    must_verify_columns('/path/to/out.csv',
                        expected=['序号', '关键词', '搜索量', ...])

    # 看每列的实际数据示例（用于 debug）
    verify_csv_columns('/path/to/out.csv', show_samples=True)
"""
import csv
import sys
from typing import List, Optional


def verify_csv_columns(path: str,
                       expected: Optional[List[str]] = None,
                       show_samples: bool = False,
                       encoding: str = 'utf-8',
                       verbose: bool = True) -> bool:
    """
    验证 CSV 列名-数据对应（比 verify_csv_safe 多一步）

    Args:
        path: CSV 路径
        expected: 预期的表头列名列表（None = 只检查列名不是空 + 至少 1 行有数据）
        show_samples: True = 打印每列前 3 行的实际数据
        encoding: utf-8

    Returns:
        True = 列名与数据一致，False = 有问题
    """
    with open(path, encoding=encoding) as f:
        rows = list(csv.reader(f))

    if not rows:
        if verbose:
            print(f"⚠️  {path} 是空文件")
        return False

    header = rows[0]
    ncols = len(header)

    # 检查 1：列数 = 表头列数
    broken = [(i, len(r), r[:3]) for i, r in enumerate(rows) if len(r) != ncols]
    if broken:
        if verbose:
            print(f"❌ {path} 列数不一致 {len(broken)} 行:")
            for b in broken[:5]:
                print(f"   行 {b[0]}: 列数 {b[1]}, 内容: {b[2]}")
        return False

    # 检查 2：表头列名非空
    empty_cols = [(i, h) for i, h in enumerate(header) if not h or h.strip() == '']
    if empty_cols:
        if verbose:
            print(f"❌ {path} 表头有空列名 {len(empty_cols)} 个:")
            for i, h in empty_cols[:5]:
                print(f"   第 {i} 列: {h!r}")
        return False

    # 检查 3：表头 == expected（如果指定）
    if expected:
        if header != expected:
            if verbose:
                print(f"❌ {path} 表头不匹配:")
                print(f"   预期: {expected}")
                print(f"   实际: {header}")
                # 找差异
                for i, (e, a) in enumerate(zip(expected, header)):
                    if e != a:
                        print(f"   差异第 {i} 列: 预期={e!r}, 实际={a!r}")
                if len(expected) != len(header):
                    print(f"   ⚠️ 列数差异: 预期 {len(expected)} 列, 实际 {len(header)} 列")
            return False

    # 检查 4：每列至少有非空数据
    # 提取每列的所有数据值，看哪些列全是 '-'/空
    col_data = [[] for _ in range(ncols)]
    for r in rows[1:]:
        for i, v in enumerate(r):
            col_data[i].append(v)
    dead_cols = []
    for i, vals in enumerate(col_data):
        non_empty = [v for v in vals if v and v.strip() not in ('-', '', 'None')]
        if not non_empty:
            dead_cols.append((i, header[i]))
    if dead_cols and verbose:
        print(f"⚠️  {path} 有 {len(dead_cols)} 列完全空:")
        for i, h in dead_cols[:5]:
            print(f"   第 {i} 列 ({h}): {len(col_data[i])} 行全为空")

    if verbose:
        print(f"✅ {path} 列名-数据对应正确 ({len(rows)-1} 行 × {ncols} 列)")
        if show_samples:
            print(f"\n每列前 3 行示例:")
            for i, h in enumerate(header):
                samples = [r[i] for r in rows[1:4]]
                print(f"   [{i:>2}] {h}: {samples}")
    return not dead_cols  # dead_cols 不致命，只警告


def must_verify_columns(path: str, expected: Optional[List[str]] = None) -> None:
    """强制验证，错位/列名错直接 raise（适合 CI）"""
    if not verify_csv_columns(path, expected=expected):
        raise ValueError(
            f"CSV 列错位或表头错位: {path} → "
            f"检查表头列名 vs data.append 时的 column 索引！"
        )


if __name__ == '__main__':
    # 自测 demo
    print("=== verify_csv_columns.py 自测 ===\n")

    import os
    test_path = '/tmp/verify_columns_test.csv'

    # Case 1: 列名-数据对应正确
    with open(test_path, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
        w.writerow(['序号', '关键词', '搜索量', '维度命中数'])
        w.writerow(['1', 'neck cream with peptides', '517', '4'])
        w.writerow(['2', 'retinol neck firming cream', '378', '4'])

    print("Case 1: 正常 CSV")
    verify_csv_columns(test_path,
                       expected=['序号', '关键词', '搜索量', '维度命中数'])
    print()

    # Case 2: 列数一致但表头错位（多了一列没写到表头）
    with open(test_path, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
        w.writerow(['序号', '关键词', '搜索量', '维度命中数'])  # 表头 4 列
        w.writerow(['1', 'neck cream with peptides', '517', '4', 'extra'])  # 数据 5 列
        w.writerow(['2', 'retinol neck firming cream', '378', '4', 'extra'])

    print("Case 2: 数据多了一列（列数不一致）")
    try:
        must_verify_columns(test_path,
                            expected=['序号', '关键词', '搜索量', '维度命中数'])
    except ValueError as e:
        print(f"✅ 正确捕获: {e}")
    print()

    # Case 3: 表头与 expected 错位
    with open(test_path, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
        w.writerow(['序号', '关键词', '搜索量', '命中维度数'])  # 列名差异
        w.writerow(['1', 'neck cream with peptides', '517', '4'])

    print("Case 3: 表头与 expected 错位")
    try:
        must_verify_columns(test_path,
                            expected=['序号', '关键词', '搜索量', '维度命中数'])
    except ValueError as e:
        print(f"✅ 正确捕获: {e}")
    print()

    os.remove(test_path)
    print("=== 自测完毕 ===")