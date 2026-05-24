#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A股专业选股工具 v2
使用东方财富免费API获取数据
"""

import requests
import json
import time
import sys

import sys

# 设置输出编码
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def get_all_stocks():
    """获取全部A股股票"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    all_stocks = []
    for page in range(1, 100):  # 最多100页
        params = {
            'pn': page,
            'pz': 1000,
            'po': 1,
            'np': 1,
            'ut': 'bd1d9ddb04089700cf9c27f6f7426281',
            'fltt': 2,
            'invt': 2,
            'fid': 'f3',
            'fs': 'm:0+t:6,m:0+t:80,m:1+t:2,m:1+t:23',
            'fields': 'f2,f3,f4,f5,f6,f7,f12,f13,f14,f100,f104,f105,f106'
        }
        
        try:
            resp = requests.get("http://28.push2.eastmoney.com/api/qt/clist/get", 
                             params=params, headers=headers, timeout=10)
            data = resp.json()
            if data.get('data') and data['data'].get('diff'):
                all_stocks.extend(data['data']['diff'])
            else:
                break
            if len(all_stocks) >= 5000:
                break
        except Exception as e:
            print(f"Error: {e}")
            break
    
    return all_stocks

def get_kline_data(code, days=60):
    """获取K线数据"""
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    # 确定市场
    if code.startswith('6'):
        secid = f"1.{code}"
    else:
        secid = f"0.{code}"
    
    url = "http://push2his.eastmoney.com/api/qt/stock/kline/get"
    params = {
        'secid': secid,
        'fields1': 'f1,f2,f3,f4,f5,f6',
        'fields2': 'f51,f52,f53,f54,f55,f56,f57,f58,f59,f60',
        'klt': '101',
        'fqt': '1',
        'beg': '20250101',
        'end': '20260311'
    }
    
    try:
        resp = requests.get(url, params=params, headers=headers, timeout=10)
        data = resp.json()
        if data.get('data') and data['data'].get('klines'):
            return data['data']['klines']
    except:
        pass
    return []

def get_stock_info(code):
    """获取个股详细信息"""
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    if code.startswith('6'):
        secid = f"1.{code}"
    else:
        secid = f"0.{code}"
    
    url = "http://push2.eastmoney.com/api/qt/stock/get"
    params = {
        'secid': secid,
        'fields': 'f57,f58,f43,f44,f45,f46,f100,f127,f128,f162,f164,f167,f168,f169,f170,f171,f173,f174,f175,f176,f177,f178,f179,f180,f181,f182,f183,f184,f185,f186,f187,f188,f189,f190,f191,f192,f193,f194,f195,f196,f197,f198,f199,f200,f201,f202,f203,f204,f205,f206,f207,f208,f209,f210'
    }
    
    try:
        resp = requests.get(url, params=params, headers=headers, timeout=10)
        data = resp.json()
        if data.get('data'):
            return data['data']
    except:
        pass
    return {}

def main():
    print("=" * 60)
    print("A股专业选股筛选")
    print("筛选条件：")
    print("  1. 近30天成交量温和放大 (10%-100%)")
    print("  2. 市盈率合理 (0-40倍)")
    print("  3. 排除ST股票和退市风险标的")
    print("=" * 60)
    
    print("\n[1/3] 获取A股股票列表...")
    stocks = get_all_stocks()
    print(f"  获取到 {len(stocks)} 只股票")
    
    # 过滤ST和退市
    valid_stocks = []
    for s in stocks:
        name = s.get('f14', '')
        code = s.get('f12', '')
        
        if 'ST' in name or '*ST' in name or 'S*ST' in name or '退' in name:
            continue
        if code.startswith('90') or code.startswith('20'):  # 排除B股
            continue
            
        valid_stocks.append(s)
    
    print(f"  排除ST/退市后剩余 {len(valid_stocks)} 只")
    
    print("\n[2/3] 筛选符合条件股票...")
    results = []
    
    for idx, stock in enumerate(valid_stocks[:300]):  # 处理前300只
        code = stock.get('f12', '')
        name = stock.get('f14', '')
        
        if (idx + 1) % 30 == 0:
            print(f"  已处理 {idx + 1}/300...")
        
        # 获取详细信息
        info = get_stock_info(code)
        if not info:
            continue
        
        # 获取市盈率
        pe = info.get('f162')  # 市盈率TTM
        if not pe or pe == '-' or float(pe) <= 0 or float(pe) > 50:
            continue
        
        pe = float(pe)
        
        # 获取行业
        industry = info.get('f100', '')
        
        # 获取成交量数据
        klines = get_kline_data(code)
        if len(klines) < 30:
            continue
        
        # 分析成交量趋势
        volumes = [int(k.split(',')[6]) for k in klines[-30:]]
        early_avg = sum(volumes[:15]) / 15
        recent_avg = sum(volumes[-15:]) / 15
        
        if early_avg > 0:
            change_pct = (recent_avg - early_avg) / early_avg * 100
            
            # 温和放大：10%-100%
            if 10 <= change_pct <= 100:
                # 获取当前价格和涨跌幅
                price = info.get('f43', 0)
                change = info.get('f44', 0)
                
                results.append({
                    'code': code,
                    'name': name,
                    'price': price,
                    'change': change,
                    'pe': pe,
                    'industry': industry,
                    'volume_change': change_pct
                })
        
        time.sleep(0.15)  # 避免请求过快
    
    print(f"  初步筛选: {len(results)} 只符合条件")
    
    print("\n[3/3] 按行业分组分析...")
    # 按行业PE排序，取低于行业平均的
    
    # 简化的行业平均PE (实际应该从API获取)
    industry_avg_pe = {
        '银行': 6, '房地产': 8, '钢铁': 10, '煤炭': 8,
        '有色金属': 15, '化工': 18, '医药生物': 25, '电子': 30,
        '计算机': 35, '通信': 20, '汽车': 15, '机械设备': 20,
        '电气设备': 20, '国防军工': 40, '传媒': 20, '轻工制造': 18,
        '农林牧渔': 20, '食品饮料': 25, '纺织服装': 15, '家用电器': 15,
        '建筑装饰': 8, '交通运输': 12, '公用事业': 15, '商业贸易': 15,
        '休闲服务': 25, '综合': 15, '建筑材料': 12
    }
    
    final_results = []
    for r in results:
        ind = r.get('industry', '')
        avg_pe = industry_avg_pe.get(ind, 25)
        
        # 市盈率低于行业平均15%
        if r['pe'] < avg_pe * 0.85:
            r['industry_avg_pe'] = avg_pe
            final_results.append(r)
    
    # 排序输出
    final_results.sort(key=lambda x: x['volume_change'], reverse=True)
    
    print("\n" + "=" * 60)
    print(f"筛选结果: 共 {len(final_results)} 只股票符合所有条件")
    print("=" * 60)
    
    if final_results:
        print(f"\n{'代码':<10} {'名称':<10} {'价格':<8} {'涨跌':<8} {'市盈率':<8} {'行业':<12} {'成交量变化':<10}")
        print("-" * 70)
        
        for i, r in enumerate(final_results[:30]):  # 显示前30只
            change_str = f"{r['change']:.2f}%" if r['change'] else "N/A"
            print(f"{r['code']:<10} {r['name']:<10} {r['price']:<8} {change_str:<8} {r['pe']:<8.2f} {r['industry']:<12} {r['volume_change']:.1f}%")
        
        if len(final_results) > 30:
            print(f"\n... 还有 {len(final_results) - 30} 只股票")
    else:
        print("\n当前筛选结果为0只股票")
        print("\n提示：可尝试放宽筛选条件")
    
    return final_results

if __name__ == "__main__":
    main()
