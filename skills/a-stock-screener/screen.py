#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A股专业选股工具
使用东方财富免费API获取数据，进行专业筛选
筛选条件：
1. 近30天成交量温和放大
2. 市盈率低于行业平均15%
3. 排除ST和退市风险标的
"""

import requests
import json
import time
from datetime import datetime, timedelta

# 东方财富API
STOCK_LIST_URL = "http://28.push2.eastmoney.com/api/qt/clist/get"
INDUSTRY_PE_URL = "http://push2.eastmoney.com/api/qt/ulist.np/get"
STOCK_DETAIL_URL = "http://push2.eastmoney.com/api/qt/stock/get"

def get_stock_list(pn=1,pz=1000):
    """获取A股股票列表"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    params = {
        'pn': pn,
        'pz': pz,
        'po': 1,
        'np': 1,
        'ut': 'bd1d9ddb04089700cf9c27f6f7426281',
        'fltt': 2,
        'invt': 2,
        'fid': 'f3',
        'fs': 'm:0+t:6,m:0+t:80,m:1+t:2,m:1+t:23',
        'fields': 'f1,f2,f3,f4,f5,f6,f7,f12,f13,f14,f100,f104,f105,f106,f107,f108,f109,f110,f111,f112,f113,f114,f115,f116,f117,f118,f119,f120,f121,f122,f123,f124,f125,f126,f127,f128,f129,f130,f131,f132,f133,f134,f135,f136,f137,f138,f139,f140,f141,f142,f143,f144,f145,f146,f147,f148,f149,f150,f151,f152,f153,f154,f155,f156,f157,f158,f159,f160,f161,f162,f163,f164,f165,f166,f167,f168,f169,f170,f171,f172,f173,f174,f175,f176,f177,f178,f179,f180,f181,f182,f183,f184,f185,f186,f187,f188,f189,f190,f191,f192,f193,f194,f195,f196,f197,f198,f199,f200,f201,f202,f203,f204,f205,f206,f207,f208,f209,f210'
    }
    
    try:
        response = requests.get(STOCK_LIST_URL, params=params, headers=headers, timeout=30)
        data = response.json()
        if data.get('data') and data['data'].get('diff'):
            return data['data']['diff']
    except Exception as e:
        print(f"获取股票列表失败: {e}")
    return []

def get_industry_pe():
    """获取行业市盈率"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    params = {
        'pn': 1,
        'pz': 100,
        'po': 1,
        'np': 1,
        'ut': 'bd1d9ddb04089700cf9c27f6f7426281',
        'fltt': 2,
        'invt': 2,
        'fid': 'f2',
        'fs': 'm:90+t:2',
        'fields': 'f2,f3,f4,f12,f13,f14'
    }
    
    try:
        response = requests.get(INDUSTRY_PE_URL, params=params, headers=headers, timeout=30)
        data = response.json()
        if data.get('data') and data['data'].get('diff'):
            industry_pe = {}
            for item in data['data']['diff']:
                if item.get('f2') and item['f2'] != '-':
                    industry_pe[item.get('f14', '')] = float(item['f2'])
            return industry_pe
    except Exception as e:
        print(f"获取行业市盈率失败: {e}")
    return {}

def get_stock_volume_trend(stock_code):
    """获取股票近30天成交量趋势"""
    # 简化版本：使用近期成交量数据判断趋势
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    # 使用历史K线数据
    kline_url = f"http://push2his.eastmoney.com/api/qt/stock/kline/get"
    params = {
        'secid': f"0.{stock_code}" if stock_code.startswith('6') else f"1.{stock_code}",
        'fields1': 'f1,f2,f3,f4,f5,f6',
        'fields2': 'f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61',
        'klt': '101',  # 日K
        'fqt': '1',
        'beg': '20250201',  # 从2月开始
        'end': '20260311'
    }
    
    try:
        response = requests.get(kline_url, params=params, headers=headers, timeout=30)
        data = response.json()
        if data.get('data') and data['data'].get('klines'):
            klines = data['data']['klines']
            if len(klines) >= 20:
                # 取近20个交易日
                volumes = []
                for kline in klines[-20:]:
                    vol = int(kline.split(',')[6])
                    volumes.append(vol)
                
                # 计算近期(后10天) vs 早期(前10天) 平均成交量
                early_avg = sum(volumes[:10]) / 10
                recent_avg = sum(volumes[-10:]) / 10
                
                # 温和放大：增长10%-100%
                if early_avg > 0:
                    change_pct = (recent_avg - early_avg) / early_avg * 100
                    if 10 <= change_pct <= 100:
                        return True, change_pct
        return False, 0
    except Exception as e:
        return False, 0

def check_stock_pe_industry(stock_code, industry_pe_dict):
    """检查股票市盈率是否低于行业平均15%"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    # 确定市场代码
    if stock_code.startswith('6'):
        secid = f"1.{stock_code}"
    elif stock_code.startswith('0') or stock_code.startswith('3'):
        secid = f"0.{stock_code}"
    else:
        return None, None, False
    
    params = {
        'secid': secid,
        'fields': 'f57,f58,f43,f44,f45,f46,f47,f48,f116,f117,f118,f119,f120,f127,f128,f129,f130,f131,f132,f133,f134,f135,f136,f137,f138,f139,f140,f141,f142,f143,f144,f145,f146,f147,f148,f149,f150,f151,f152,f153,f154,f155,f156,f157,f158,f159,f160,f161,f162,f163,f164,f165,f166,f167,f168,f169,f170,f171,f172,f173,f174,f175,f176,f177,f178,f179,f180,f181,f182,f183,f184,f185,f186,f187,f188,f189,f190,f191,f192,f193,f194,f195,f196,f197,f198,f199,f200,f201,f202,f203,f204,f205,f206,f207,f208,f209,f210'
    }
    
    try:
        response = requests.get(STOCK_DETAIL_URL, params=params, headers=headers, timeout=30)
        data = response.json()
        
        if data.get('data'):
            stock_data = data['data']
            
            # 获取市盈率
            pe = stock_data.get('f162')  # 市盈率TTM
            if pe and pe != '-' and float(pe) > 0:
                pe = float(pe)
            else:
                return None, None, False
            
            # 获取行业名称
            industry = stock_data.get('f100', '')
            
            # 获取行业平均PE
            industry_avg_pe = industry_pe_dict.get(industry, 0)
            
            if industry_avg_pe and industry_avg_pe > 0:
                # 检查是否低于行业平均15%
                if pe < industry_avg_pe * 0.85:
                    return pe, industry, True
            
            return pe, industry, False
            
    except Exception as e:
        pass
    
    return None, None, False

def screen_stocks():
    """执行选股筛选"""
    print("=" * 60)
    print("A股专业选股筛选")
    print("筛选条件：")
    print("  1. 近30天成交量温和放大 (10%-100%)")
    print("  2. 市盈率低于行业平均15%")
    print("  3. 排除ST股票和退市风险标的")
    print("=" * 60)
    
    print("\n[1/4] 获取行业市盈率数据...")
    industry_pe = get_industry_pe()
    print(f"  获取到 {len(industry_pe)} 个行业市盈率数据")
    
    print("\n[2/4] 获取A股股票列表...")
    stocks = get_stock_list(pn=1, pz=2000)
    print(f"  获取到 {len(stocks)} 只股票")
    
    # 过滤ST股票和退市风险
    valid_stocks = []
    for stock in stocks:
        name = stock.get('f14', '')
        code = stock.get('f12', '')
        
        # 排除ST股票
        if 'ST' in name or '*ST' in name or 'S*ST' in name:
            continue
        # 排除退市
        if '退' in name:
            continue
        # 排除B股
        if code.startswith('90') or code.startswith('20'):
            continue
            
        valid_stocks.append(stock)
    
    print(f"  排除ST/退市后剩余 {len(valid_stocks)} 只")
    
    print("\n[3/4] 筛选市盈率低于行业平均15%的股票...")
    pe_screened = []
    
    for i, stock in enumerate(valid_stocks[:200]):  # 限制前200只演示
        code = stock.get('f12', '')
        name = stock.get('f14', '')
        
        if (i+1) % 50 == 0:
            print(f"  已处理 {i+1}/{min(200, len(valid_stocks))}...")
        
        pe, industry, is_low = check_stock_pe_industry(code, industry_pe)
        
        if is_low:
            pe_screened.append({
                'code': code,
                'name': name,
                'pe': pe,
                'industry': industry,
                'industry_pe': industry_pe.get(industry, 0)
            })
        
        time.sleep(0.1)  # 避免请求过快
    
    print(f"  市盈率筛选: {len(pe_screened)} 只符合条件")
    
    print("\n[4/4] 检查成交量趋势...")
    final_results = []
    
    for stock_info in pe_screened[:50]:  # 限制处理数量
        code = stock_info['code']
        name = stock_info['name']
        
        has_volume, change_pct = get_stock_volume_trend(code)
        
        if has_volume:
            stock_info['volume_change'] = change_pct
            final_results.append(stock_info)
            print(f"  ✓ {code} {name} - 成交量放大 {change_pct:.1f}%")
    
    # 输出结果
    print("\n" + "=" * 60)
    print(f"筛选结果: 共 {len(final_results)} 只股票符合所有条件")
    print("=" * 60)
    
    if final_results:
        print(f"\n{'代码':<10} {'名称':<12} {'市盈率':<10} {'行业':<15} {'成交量变化':<10}")
        print("-" * 60)
        for stock in final_results:
            print(f"{stock['code']:<10} {stock['name']:<12} {stock['pe']:<10.2f} {stock['industry']:<15} {stock.get('volume_change', 0):.1f}%")
    else:
        print("\n当前筛选结果为0只股票，可能原因：")
        print("  1. 市场整体PE较高")
        print("  2. 成交量温和放大的股票较少")
        print("\n建议：可尝试放宽筛选条件")
    
    return final_results

if __name__ == "__main__":
    screen_stocks()
