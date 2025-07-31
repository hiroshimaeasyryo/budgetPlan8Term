"""
データ管理モジュール
事業部の基本データと本部費用の配賦ロジックを管理
"""

import pandas as pd
from typing import Dict, List, Tuple

class DataManager:
    """事業部データと本部費用配賦を管理するクラス"""
    
    def __init__(self):
        # 事業部の基本データ（概要.mdから取得）
        self.departments = {
            "キャリア": {
                "margin_rate": 0.6025,
                "fixed_cost": 25_572_000,
                "variable_cost": 10_430_800
            },
            "インサイド": {
                "margin_rate": 0.6483,
                "fixed_cost": 30_516_360,
                "variable_cost": 7_014_000
            },
            "フィールド": {
                "margin_rate": 0.4512,
                "fixed_cost": 4_830_000,
                "variable_cost": 374_600
            },
            "SP": {
                "margin_rate": 0.5421,
                "fixed_cost": 15_112_000,
                "variable_cost": 2_985_600
            },
            "飲食": {
                "margin_rate": 0.5478,
                "fixed_cost": 9_862_800,
                "variable_cost": 1_619_400
            }
        }
        
        # 本部費用
        self.headquarters_fixed_cost = 53_013_900
        self.headquarters_variable_cost = 11_649_400
        
        # 本部費用の配賦割合（初期値：均等配賦）
        self.allocation_ratios = {
            "キャリア": {"fixed": 0.2, "variable": 0.2},
            "インサイド": {"fixed": 0.2, "variable": 0.2},
            "フィールド": {"fixed": 0.2, "variable": 0.2},
            "SP": {"fixed": 0.2, "variable": 0.2},
            "飲食": {"fixed": 0.2, "variable": 0.2}
        }
        
        # 事業部間の負担調整（初期値：なし）
        self.cost_transfers = {}
    
    def get_department_data(self) -> Dict:
        """事業部の基本データを取得"""
        return self.departments.copy()
    
    def get_headquarters_costs(self) -> Tuple[int, int]:
        """本部費用を取得"""
        return self.headquarters_fixed_cost, self.headquarters_variable_cost
    
    def get_allocation_ratios(self) -> Dict:
        """本部費用の配賦割合を取得"""
        return self.allocation_ratios.copy()
    
    def update_allocation_ratios(self, new_ratios: Dict):
        """本部費用の配賦割合を更新"""
        self.allocation_ratios = new_ratios
    
    def calculate_implied_sales(self, dept_name: str) -> float:
        """限界利益率から仮の売上総利益を逆算"""
        dept_data = self.departments[dept_name]
        margin_rate = dept_data["margin_rate"]
        variable_cost = dept_data["variable_cost"]
        
        # 限界利益率 = (売上総利益 - 変動費) / 売上総利益
        # 売上総利益 = 変動費 / (1 - 限界利益率)
        implied_sales = variable_cost / (1 - margin_rate)
        
        return implied_sales
    
    def calculate_allocated_costs(self) -> Dict:
        """配賦後の各事業部のコストを計算（売上総利益調整版）"""
        allocated_costs = {}
        
        for dept_name, dept_data in self.departments.items():
            # 元の仮の売上総利益を計算
            original_implied_sales = self.calculate_implied_sales(dept_name)
            
            # 本部費用の配賦分を計算
            hq_fixed_allocated = self.headquarters_fixed_cost * self.allocation_ratios[dept_name]["fixed"]
            hq_variable_allocated = self.headquarters_variable_cost * self.allocation_ratios[dept_name]["variable"]
            
            # 事業部固有のコスト
            dept_fixed = dept_data["fixed_cost"]
            dept_variable = dept_data["variable_cost"]
            
            # 事業部間の負担調整を適用
            transfer_fixed = self.cost_transfers.get(f"{dept_name}_fixed", 0)
            transfer_variable = self.cost_transfers.get(f"{dept_name}_variable", 0)
            
            # 配賦後の売上総利益（本部変動費分を加算）
            allocated_sales = original_implied_sales + hq_variable_allocated
            
            # 総コストを計算
            total_fixed = dept_fixed + hq_fixed_allocated + transfer_fixed
            total_variable = dept_variable + hq_variable_allocated + transfer_variable
            
            # 配賦後の限界利益率を再計算
            new_margin_rate = (allocated_sales - total_variable) / allocated_sales
            
            allocated_costs[dept_name] = {
                "original_margin_rate": dept_data["margin_rate"],
                "margin_rate": new_margin_rate,  # 再計算された限界利益率
                "original_implied_sales": original_implied_sales,  # 元の仮の売上総利益
                "implied_sales": allocated_sales,  # 配賦後の売上総利益
                "sales_increase": hq_variable_allocated,  # 売上総利益増加額
                "fixed_cost": total_fixed,
                "variable_cost": total_variable,
                "original_fixed": dept_fixed,
                "original_variable": dept_variable,
                "hq_fixed_allocated": hq_fixed_allocated,
                "hq_variable_allocated": hq_variable_allocated,
                "transfer_fixed": transfer_fixed,
                "transfer_variable": transfer_variable
            }
        
        return allocated_costs
    
    def calculate_break_even_point(self, dept_name: str) -> float:
        """指定した事業部の損益分岐点を計算"""
        allocated_costs = self.calculate_allocated_costs()
        dept_data = allocated_costs[dept_name]
        
        # 損益分岐点 = 固定費 / 限界利益率
        bep = dept_data["fixed_cost"] / dept_data["margin_rate"]
        return bep
    
    def validate_allocation_ratios(self) -> bool:
        """配賦割合の合計が1.0になることを確認"""
        fixed_sum = sum(ratio["fixed"] for ratio in self.allocation_ratios.values())
        variable_sum = sum(ratio["variable"] for ratio in self.allocation_ratios.values())
        
        return abs(fixed_sum - 1.0) < 0.001 and abs(variable_sum - 1.0) < 0.001
    
    def get_allocation_impact_analysis(self) -> Dict:
        """配賦の影響分析を取得（売上総利益調整版）"""
        impact_data = {}
        
        for dept_name, dept_data in self.departments.items():
            # 配賦前のデータ
            original_fixed = dept_data["fixed_cost"]
            original_variable = dept_data["variable_cost"]
            original_margin_rate = dept_data["margin_rate"]
            original_implied_sales = self.calculate_implied_sales(dept_name)
            
            # 配賦後のデータ
            allocated = self.calculate_allocated_costs()[dept_name]
            
            impact_data[dept_name] = {
                "配賦前": {
                    "固定費": original_fixed,
                    "変動費": original_variable,
                    "限界利益率": original_margin_rate,
                    "仮の売上総利益": original_implied_sales
                },
                "配賦後": {
                    "固定費": allocated["fixed_cost"],
                    "変動費": allocated["variable_cost"],
                    "限界利益率": allocated["margin_rate"],
                    "仮の売上総利益": allocated["implied_sales"],
                    "売上総利益増加": allocated["sales_increase"],
                    "本部変動費配賦額": allocated["hq_variable_allocated"]
                },
                "影響": {
                    "固定費増加": allocated["fixed_cost"] - original_fixed,
                    "変動費増加": allocated["variable_cost"] - original_variable,
                    "変動費増加率": (allocated["variable_cost"] - original_variable) / original_variable * 100 if original_variable > 0 else 0,
                    "売上総利益増加": allocated["sales_increase"],
                    "売上総利益増加率": allocated["sales_increase"] / original_implied_sales * 100 if original_implied_sales > 0 else 0,
                    "限界利益率変化": allocated["margin_rate"] - original_margin_rate,
                    "限界利益率変化率": (allocated["margin_rate"] - original_margin_rate) / original_margin_rate * 100
                }
            }
        
        return impact_data
    
    def get_summary_data(self) -> pd.DataFrame:
        """サマリーデータをDataFrameで取得"""
        allocated_costs = self.calculate_allocated_costs()
        
        summary_data = []
        for dept_name, costs in allocated_costs.items():
            bep = self.calculate_break_even_point(dept_name)
            summary_data.append({
                "事業部": dept_name,
                "元の限界利益率": f"{costs['original_margin_rate']:.1%}",
                "配賦後限界利益率": f"{costs['margin_rate']:.1%}",
                "限界利益率変化": f"{costs['margin_rate'] - costs['original_margin_rate']:+.1%}",
                "固定費": f"{costs['fixed_cost']:,.0f}円",
                "変動費": f"{costs['variable_cost']:,.0f}円",
                "損益分岐点": f"{bep:,.0f}円"
            })
        
        return pd.DataFrame(summary_data)
    
    def calculate_operating_profit_contribution(self, target_sales_increase: float = None) -> Dict:
        """
        営業利益貢献度を計算
        
        Args:
            target_sales_increase: 目標売上総利益増加額（Noneの場合は現在の配賦による増加額を使用）
        
        Returns:
            各事業部の営業利益貢献度分析
        """
        allocated_costs = self.calculate_allocated_costs()
        contribution_data = {}
        
        for dept_name, costs in allocated_costs.items():
            # 売上総利益増加額（本部変動費配賦による増加）
            sales_increase = costs["sales_increase"]
            
            # 目標売上総利益増加額が指定されている場合は使用
            if target_sales_increase is not None:
                sales_increase = target_sales_increase
            
            # 営業利益への貢献額 = 売上総利益増加額 × 限界利益率
            profit_contribution = sales_increase * costs["margin_rate"]
            
            # 現在の営業利益（仮の売上総利益から固定費を引いた額）
            current_operating_profit = costs["implied_sales"] - costs["fixed_cost"]
            
            # 営業利益貢献度の計算（営業利益が負の値の場合の処理を改善）
            if current_operating_profit > 0:
                contribution_rate = profit_contribution / current_operating_profit
                profit_increase_rate = profit_contribution / current_operating_profit
            elif current_operating_profit < 0:
                # 営業利益が負の値の場合、損失改善率として計算
                contribution_rate = profit_contribution / abs(current_operating_profit)
                profit_increase_rate = profit_contribution / abs(current_operating_profit)
            else:
                # 営業利益が0の場合
                contribution_rate = 0
                profit_increase_rate = 0
            
            # 損益分岐点との差額を計算
            break_even_point = self.calculate_break_even_point(dept_name)
            
            contribution_data[dept_name] = {
                "売上総利益増加額": sales_increase,
                "限界利益率": costs["margin_rate"],
                "営業利益貢献額": profit_contribution,
                "営業利益貢献度": contribution_rate,
                "営業利益増加率": profit_increase_rate,
                "損益分岐点": break_even_point,
                "営業利益状態": "黒字" if current_operating_profit > 0 else "赤字" if current_operating_profit < 0 else "損益分岐"
            }
        
        return contribution_data
    
    def get_operating_profit_contribution_summary(self, target_sales_increase: float = None) -> pd.DataFrame:
        """
        営業利益貢献度のサマリーをDataFrameで取得
        
        Args:
            target_sales_increase: 目標売上総利益増加額
        
        Returns:
            営業利益貢献度のサマリーDataFrame
        """
        contribution_data = self.calculate_operating_profit_contribution(target_sales_increase)
        
        summary_data = []
        for dept_name, data in contribution_data.items():
            # 営業利益貢献度の表示を改善
            if data["営業利益状態"] == "赤字":
                contribution_display = f"損失改善率: {data['営業利益貢献度']:.1%}"
                profit_increase_display = f"損失改善率: {data['営業利益増加率']:.1%}"
            else:
                contribution_display = f"{data['営業利益貢献度']:.1%}"
                profit_increase_display = f"{data['営業利益増加率']:.1%}"
            
            summary_data.append({
                "事業部": dept_name,
                "売上総利益増加額": f"{data['売上総利益増加額']:,.0f}円",
                "限界利益率": f"{data['限界利益率']:.1%}",
                "営業利益貢献額": f"{data['営業利益貢献額']:,.0f}円",
                "営業利益状態": data["営業利益状態"],
                "営業利益貢献度": contribution_display,
                "営業利益増加率": profit_increase_display,
                "損益分岐点": f"{data['損益分岐点']:,.0f}円"
            })
        
        return pd.DataFrame(summary_data)
    
    def calculate_sales_profit_elasticity(self) -> Dict:
        """
        売上総利益-営業利益弾性を計算
        売上総利益が1%増加した時の営業利益の増加率を算出
        
        Returns:
            各事業部の売上総利益-営業利益弾性
        """
        allocated_costs = self.calculate_allocated_costs()
        elasticity_data = {}
        
        for dept_name, costs in allocated_costs.items():
            current_profit = costs["implied_sales"] - costs["fixed_cost"]
            
            # 売上総利益を1%増加させた場合の営業利益
            increased_sales = costs["implied_sales"] * 1.01
            increased_profit = increased_sales - costs["fixed_cost"]
            
            # 営業利益の増加率（営業利益が負の値の場合の処理を改善）
            if current_profit > 0:
                profit_increase_rate = (increased_profit - current_profit) / current_profit
            elif current_profit < 0:
                # 営業利益が負の値の場合、損失改善率として計算
                if increased_profit > current_profit:
                    profit_increase_rate = (increased_profit - current_profit) / abs(current_profit)
                else:
                    profit_increase_rate = 0
            else:
                # 営業利益が0の場合
                profit_increase_rate = 0
            
            # 売上総利益-営業利益弾性 = 営業利益増加率 / 売上総利益増加率（1%）
            elasticity = profit_increase_rate / 0.01
            
            # 営業利益マージン
            if costs["implied_sales"] > 0:
                profit_margin = current_profit / costs["implied_sales"]
            else:
                profit_margin = 0
            
            elasticity_data[dept_name] = {
                "営業利益増加率": profit_increase_rate,
                "売上総利益-営業利益弾性": elasticity,
                "限界利益率": costs["margin_rate"],
                "営業利益状態": "黒字" if current_profit > 0 else "赤字" if current_profit < 0 else "損益分岐"
            }
        
        return elasticity_data 