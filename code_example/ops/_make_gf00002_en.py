# -*- coding: utf-8 -*-
"""Translate GF-00-002 Document Issue (Update) List to English Excel."""
from __future__ import annotations

from copy import copy
from pathlib import Path

import openpyxl
from openpyxl.utils import get_column_letter

SRC = Path(
    r"e:\腾讯电脑管家软件搬家\xwechat_files\wxid_j9jgj60bl99o21_4a84\msg\file\2026-10"
    r"\GF-00-002文件发行（更新）清单.202609.xlsx"
)
DST = SRC.parent / "GF-00-002文件发行（更新）清单 Document Issue (Update) List.202609.xlsx"
DST_COPY = Path(r"E:\solarautotestnewui\docs") / DST.name
# Also keep a pure-English sibling if previously generated.
DST_EN_ONLY = SRC.parent / "GF-00-002 Document Issue (Update) List.202609.xlsx"

# Exact Chinese -> natural English (document titles / UI strings)
TRANSLATE = {
    # Titles / headers
    "2026年9月文件发行（更新）清单": "Document Issue (Update) List - September 2026",
    "2026年9月各部门文件发行（更新）清单如下": (
        "Document Issue (Update) List by Department - September 2026"
    ),
    " 2026年9月各部门文件发行（更新）清单如下": (
        "Document Issue (Update) List by Department - September 2026"
    ),
    "2026年9月各实部门文件发行（更新）清单如下": (
        "Document Issue (Update) List by Department - September 2026"
    ),
    "  2026年9月各实部门文件发行（更新）清单如下": (
        "Document Issue (Update) List by Department - September 2026"
    ),
    "序号": "No.",
    "变更号": "Change No.",
    "文件名称": "Document Title",
    "文件编号": "Document No.",
    "版次": "Revision",
    "生效日期": "Effective Date",
    "备注": "Remarks",
    # Sheet names
    "质量手册": "Quality Manual",
    "程序文件": "Procedures",
    "三阶文件": "Work Instructions",
    "四阶表单": "Forms",
    # Quality Manual
    # Procedures
    "公正性控制程序": "Impartiality Control Procedure",
    "保密性控制程序": "Confidentiality Control Procedure",
    "人员权责及资格要求管理程序": (
        "Personnel Responsibilities and Qualification Requirements Procedure"
    ),
    "人员教育培训管理程序": "Personnel Education and Training Procedure",
    "质量监督控制程序": "Quality Supervision Control Procedure",
    "实验室设施和环境控制程序": "Laboratory Facilities and Environment Control Procedure",
    "仪器设备管制程序": "Equipment Control Procedure",
    "仪器设备管理程序": "Equipment Management Procedure",
    "设备校准和计量溯源控制程序": (
        "Equipment Calibration and Metrological Traceability Control Procedure"
    ),
    "服务和供应品采购控制程序": "Purchasing of Services and Supplies Control Procedure",
    "分包控制程序": "Subcontracting Control Procedure",
    "合同评审管理程序": "Contract Review Procedure",
    "客户服务程序": "Customer Service Procedure",
    "方法使用与管理程序": "Method Use and Management Procedure",
    "样品管理程序": "Sample Management Procedure",
    "测量不确定度控制程序": "Measurement Uncertainty Control Procedure",
    "质量控制程序": "Quality Control Procedure",
    "能力验证控制程序": "Proficiency Testing Control Procedure",
    "报告管理程序": "Report Management Procedure",
    "客户投诉处理程序": "Customer Complaint Handling Procedure",
    "不符合工作控制程序": "Control of Nonconforming Work Procedure",
    "计算机软硬件及电子数据控制程序": (
        "Computer Hardware/Software and Electronic Data Control Procedure"
    ),
    "文件管制程序": "Document Control Procedure",
    "记录控制程序": "Records Control Procedure",
    "风险与机遇控制程序": "Risks and Opportunities Control Procedure",
    "纠正、预防措施和改进控制程序": (
        "Corrective Action, Preventive Action, and Improvement Control Procedure"
    ),
    "内部审核程序": "Internal Audit Procedure",
    "管理评审程序": "Management Review Procedure",
    "CBTL控制程序": "CBTL Control Procedure",
    "认可标识使用及认可状态声明": (
        "Use of Accreditation Marks and Statements of Accreditation Status"
    ),
    # Work instructions – general
    "新增项目作业规范": "Work Instruction for New Test Items",
    "样品收件及管控作业规范": "Work Instruction for Sample Receipt and Control",
    "机电安全作业管理规定": "Electromechanical Safety Work Management Rules",
    "质量目标管理程序": "Quality Objectives Management Procedure",
    "检测报告变更管理规范": "Specification for Test Report Change Management",
    "文件编码原则": "Document Coding Principles",
    "CNAS 认可标识与证书使用规范": (
        "Specification for Use of CNAS Accreditation Marks and Certificates"
    ),
    "劳动防护用品管理规定": "Personal Protective Equipment Management Rules",
    "保密样品动态管理办法": "Confidential Sample Dynamic Management Rules",
    "防范和惩治弄虚作假行为管理规定": (
        "Rules for Preventing and Punishing Fraudulent Practices"
    ),
    "保密措施管制办法": "Confidentiality Measures Control Rules",
    "分包作业规范": "Work Instruction for Subcontracting",
    "Chroma61830/61800使用规范": "Chroma 61830/61800 Operating Specification",
    "Chroma62150H-1000S操作规范": "Chroma 62150H-1000S Operating Specification",
    "YOKOGAWA功率分析仪WT1800操作规范": (
        "YOKOGAWA Power Analyzer WT1800 Operating Specification"
    ),
    "YOKOGAWA示波器DL850操作规范": "YOKOGAWA Oscilloscope DL850 Operating Specification",
    "KIKUSUI安规测试仪TOS9303LC操作规范": (
        "KIKUSUI Safety Tester TOS9303LC Operating Specification"
    ),
    "DEWETRON功率分析仪E3A4操作规范": (
        "DEWETRON Power Analyzer E3A4 Operating Specification"
    ),
    "恒定湿热试验作业规范": "Work Instruction for Constant Damp Heat Test",
    "低温试验作业规范": "Work Instruction for Low-Temperature Test",
    "高温试验作业规范": "Work Instruction for High-Temperature Test",
    "温度变化试验作业规范": "Work Instruction for Temperature Change Test",
    "交变湿热（12h+12h循环)作业规范": (
        "Work Instruction for Cyclic Damp Heat Test (12 h + 12 h Cycle)"
    ),
    "温湿度箱操作规范": "Temperature and Humidity Chamber Operating Specification",
    "仪器设备校准周期的确定和调整作业规范": (
        "Work Instruction for Determining and Adjusting Equipment Calibration Intervals"
    ),
    "期间核查指导书": "Intermediate Check Instruction",
    "低温不确定度评定": "Uncertainty Evaluation for Low Temperature",
    "检测仪器设备之类别代码精度及校准周期规范": (
        "Specification for Category Codes, Accuracy Classes, and Calibration Intervals of Test Equipment"
    ),
    "逆变器有功控制作业规范": "Work Instruction for Inverter Active Power Control",
    "电流不确定度评定": "Uncertainty Evaluation for Current",
    "电压不确定度评定": "Uncertainty Evaluation for Voltage",
    "有功功率不确定度评定": "Uncertainty Evaluation for Active Power",
    "功率因数不确定度评定": "Uncertainty Evaluation for Power Factor",
    "转换效率不确定度评定": "Uncertainty Evaluation for Conversion Efficiency",
    "时间不确定度评定": "Uncertainty Evaluation for Time",
    "电气参数作业规范": "Work Instruction for Electrical Parameters",
    "电容放电作业规范": "Work Instruction for Capacitor Discharge",
    "耐压测试作业规范": "Work Instruction for Dielectric Withstand Test",
    "温升测试作业规范": "Work Instruction for Temperature Rise Test",
    "逆变器10min过压保护作业规范": (
        "Work Instruction for Inverter 10-Minute Overvoltage Protection"
    ),
    "逆变器Q(U)曲线作业规范": "Work Instruction for Inverter Q(U) Characteristic",
    "逆变器电压穿越测试作业规范": "Work Instruction for Inverter Voltage Ride-Through Test",
    "逆变器电压监控保护作业规范": (
        "Work Instruction for Inverter Voltage Monitoring and Protection"
    ),
    "逆变器孤岛测试作业规范": "Work Instruction for Inverter Anti-Islanding Test",
    "逆变器固定功率因素作业规范": (
        "Work Instruction for Inverter Fixed Power Factor"
    ),
    "逆变器固定无功作业规范": "Work Instruction for Inverter Fixed Reactive Power",
    "逆变器过频降载作业规范": (
        "Work Instruction for Inverter Overfrequency Power Reduction"
    ),
    "逆变器开机、故障重连作业规范": (
        "Work Instruction for Inverter Start-Up and Fault Reconnection"
    ),
    "逆变器频率监控保护作业规范": (
        "Work Instruction for Inverter Frequency Monitoring and Protection"
    ),
    "逆变器欠频升载作业规范": (
        "Work Instruction for Inverter Underfrequency Power Increase"
    ),
    "逆变器闪变作业规范": "Work Instruction for Inverter Flicker",
    "逆变器谐波作业规范": "Work Instruction for Inverter Harmonics",
    "逆变器直流分量作业规范": "Work Instruction for Inverter DC Component",
    "逆变器转换效率作业规范": "Work Instruction for Inverter Conversion Efficiency",
    "逆变器动静态MPPT效率作业规范": (
        "Work Instruction for Inverter Dynamic and Static MPPT Efficiency"
    ),
    "逆变器cos φ（P）曲线作业规范": (
        "Work Instruction for Inverter cos φ(P) Characteristic"
    ),
    "逆变器P(U)曲线作业规范": "Work Instruction for Inverter P(U) Characteristic",
    "逆变器相位角偏移作业规范": "Work Instruction for Inverter Phase Angle Displacement",
    "拉弧试验作业规范": "Work Instruction for Arc Fault Test",
    "爱科赛博交流源操作规范": "ActionPower AC Source Operating Specification",
    "蓝点直流源操作规范": "Bluesight DC Source Operating Specification",
    "电弧发生器操作规范": "Arc Generator Operating Specification",
    "温湿度箱期间核查作业规范": (
        "Work Instruction for Intermediate Check of Temperature and Humidity Chamber"
    ),
    "万用表期间核查作业规范": "Work Instruction for Intermediate Check of Multimeter",
    "温度不确定度评定": "Uncertainty Evaluation for Temperature",
    "放电电流不确定的评定": "Uncertainty Evaluation for Discharge Current",
    "电池交流电阻不确定度评定": (
        "Uncertainty Evaluation for Battery AC Internal Resistance"
    ),
    "蓝点直流源操设备操作规范": "Bluesight DC Source Equipment Operating Specification",
    "蓝点交流源设备操作规范": "Bluesight AC Source Equipment Operating Specification",
    "1650V&650V充放电机设备操作规范": (
        "1650 V & 650 V Charge/Discharge Equipment Operating Specification"
    ),
    "脉冲测试仪设备操作规范": "Pulse Tester Equipment Operating Specification",
    "负载箱子操作规范操作规范": "Load Box Operating Specification",
    "温度记录仪设备操作规范": "Temperature Recorder Equipment Operating Specification",
    "温湿度环境箱设备操作规范": (
        "Temperature and Humidity Environmental Chamber Operating Specification"
    ),
    "振动台设备操作规范": "Vibration Table Equipment Operating Specification",
    "便携式温湿度记录仪设备操作规范": (
        "Portable Temperature and Humidity Recorder Operating Specification"
    ),
    "千分尺设备操作规范": "Micrometer Operating Specification",
    "跌落机设备操作规范": "Drop Tester Equipment Operating Specification",
    "热电偶线点焊机设备操作规范": (
        "Thermocouple Wire Spot Welder Operating Specification"
    ),
    "耐异常高温作业规范": "Work Instruction for Abnormal High-Temperature Withstand",
    "运输和安装过程中的电气绝缘检查作业规范": (
        "Work Instruction for Electrical Insulation Check During Transport and Installation"
    ),
    "运输和安装过程中的短路保护作业规范": (
        "Work Instruction for Short-Circuit Protection During Transport and Installation"
    ),
    "反向连接保护作业规范": "Work Instruction for Reverse Connection Protection",
    "过放电控制作业规范": "Work Instruction for Over-Discharge Control",
    "跌落测试作业规范": "Work Instruction for Drop Test",
    "电气间隙和爬电距离测试作业规范": (
        "Work Instruction for Clearance and Creepage Distance Test"
    ),
    "不可接触测试作业规范": "Work Instruction for Inaccessibility Test",
    "电缆护套测试作业规范": "Work Instruction for Cable Sheath Test",
    "稳定力30N测试作业规范": "Work Instruction for Steady Force Test (30 N)",
    "稳定力250N测试作业规范": "Work Instruction for Steady Force Test (250 N)",
    "小球冲击测试作业规范": "Work Instruction for Small Ball Impact Test",
    "应力释放测试作业规范": "Work Instruction for Stress Relief Test",
    "稳定性测试作业规范": "Work Instruction for Stability Test",
    "壁挂测试作业规范": "Work Instruction for Wall-Mount Test",
    "机架安装设备测试作业规范": "Work Instruction for Rack-Mounted Equipment Test",
    "手柄和手动控制机构固定拉力测试作业规范": (
        "Work Instruction for Handle and Manual Control Secureness (Pull) Test"
    ),
    "脉冲电压冲击测试作业规范": "Work Instruction for Impulse Voltage Test",
    "冲击耐压测试的替代方法作业规范": (
        "Work Instruction for Alternative Method to Impulse Withstand Voltage Test"
    ),
    "交流-直流耐压试验作业规范": "Work Instruction for AC-DC Dielectric Withstand Test",
    "保护阻抗测试作业规范": "Work Instruction for Protective Impedance Test",
    "接触电流测试作业规范": "Work Instruction for Touch Current Test",
    "有限电源测试作业规范": "Work Instruction for Limited Power Source Test",
    "反馈保护测试作业规范": "Work Instruction for Feedback Protection Test",
    "输入电流测试作业规范": "Work Instruction for Input Current Test",
    "短时耐受电流测试作业规范": "Work Instruction for Short-Time Withstand Current Test",
    "变压器保护测试作业规范": "Work Instruction for Transformer Protection Test",
    "接地连续性测试作业规范": "Work Instruction for Protective Earthing Continuity Test",
    "单一故障测试作业规范": "Work Instruction for Single Fault Test",
    "干热测试作业规范": "Work Instruction for Dry Heat Test",
    "湿热测试作业规范": "Work Instruction for Damp Heat Test",
    "振动测试作业规范作业规范": "Work Instruction for Vibration Test",
    "外部短路测试作业规范": "Work Instruction for External Short-Circuit Test",
    "撞击测试作业规范": "Work Instruction for Impact Test",
    "热滥用测试作业规范": "Work Instruction for Thermal Abuse Test",
    "过充电测试作业规范": "Work Instruction for Overcharge Test",
    "强制放电测试作业规范": "Work Instruction for Forced Discharge Test",
    "热失控测试作业规范": "Work Instruction for Thermal Runaway Test",
    "过压控制测试作业规范": "Work Instruction for Overvoltage Control Test",
    "过流控制测试作业规范": "Work Instruction for Overcurrent Control Test",
    "过热控制测试作业规范": "Work Instruction for Overtemperature Control Test",
    "充电程序测试作业规范": "Work Instruction for Charging Procedure Test",
    "+25度放电容量测试作业规范": (
        "Work Instruction for Discharge Capacity Test at +25 °C"
    ),
    "低温放电性能作业规范": "Work Instruction for Low-Temperature Discharge Performance",
    "高倍率运行放电作业规范": "Work Instruction for High-Rate Discharge Operation",
    "电荷（容量）保留和恢复作业规范": (
        "Work Instruction for Charge (Capacity) Retention and Recovery"
    ),
    "交流内阻测量作业规范": "Work Instruction for AC Internal Resistance Measurement",
    "直流内阻测量作业规范": "Work Instruction for DC Internal Resistance Measurement",
    "循环寿命实验作业规范": "Work Instruction for Cycle Life Test",
    "恒定电压下的存储耐久性（永久充电寿命）作业规范": (
        "Work Instruction for Storage Endurance at Constant Voltage (Permanent Charge Life)"
    ),
    "热电偶制作作业规范": "Work Instruction for Thermocouple Fabrication",
    "电池充放电机期间核查作业规范": (
        "Work Instruction for Intermediate Check of Battery Charge/Discharge Equipment"
    ),
    "直流源期间核查": "Intermediate Check of DC Source",
    "交流模拟电源期间核查": "Intermediate Check of AC Simulated Power Source",
    "防尘设备设备操作规范": "Dustproof Equipment Operating Specification",
    "防水设备设备操作规范": "Waterproof Equipment Operating Specification",
    "球压试验操作规范": "Ball Pressure Test Operating Specification",
    "防尘防水测试作业规范": "Work Instruction for Dust and Water Ingress Protection Test",
    "针焰试验操作规范": "Needle-Flame Test Operating Specification",
    "试验火焰 50W 水平与垂直火焰测试操作规范": (
        "50 W Test Flame – Horizontal and Vertical Flame Test Operating Specification"
    ),
    # Forms
    "文件新（更）版发行通知单": "New/Revised Document Issue Notice",
    "文件发行（更新）清单": "Document Issue (Update) List",
    "文件分发签收表": "Document Distribution and Acknowledgement Form",
    "文件(数据)调（借）阅申请单": "Document/Data Access (Loan) Application Form",
    "文件（数据）转移单": "Document/Data Transfer Form",
    "文件编号申请登记表": "Document Number Application Register",
    "文件适用性确认记录表": "Document Applicability Confirmation Record",
    "文件数据记录销毁申请单": "Document/Data/Record Destruction Application Form",
    "实验室人员一览表": "Laboratory Personnel List",
    "实验室环境记录表": "Laboratory Environment Record",
    "实验室测量记录表": "Laboratory Measurement Record",
    "实验室样品领用记录表": "Laboratory Sample Issue Record",
    "劳保用品发放报废登记总表": (
        "PPE Issuance and Scrap Registration Summary"
    ),
    "计量溯源图": "Metrological Traceability Chart",
    "报废样品清单": "Scrapped Sample List",
    "消耗品验收记录表": "Consumables Acceptance Record",
    "样品标签": "Sample Label",
    "不符合项整改报告": "Nonconformity Corrective Action Report",
    "管理体系内审方案（年度计划）": (
        "Management System Internal Audit Program (Annual Plan)"
    ),
    "管理体系内部审核报告": "Management System Internal Audit Report",
    "管理体系内部审核核查表（CNAS）": (
        "Management System Internal Audit Checklist (CNAS)"
    ),
    "内审不符合改善一览表": "Internal Audit Nonconformity Improvement List",
    "管理评审计划": "Management Review Plan",
    "管理评审报告": "Management Review Report",
    "检测报告变更/补发申请表": "Test Report Change/Reissue Application Form",
    "检测报告退回签发部门登记表": (
        "Register of Test Reports Returned to the Issuing Department"
    ),
    "检测报告变更记录表": "Test Report Change Record",
    "进出样登记表": "Sample In/Out Register",
    "仓库样品库存点检记录表": "Warehouse Sample Inventory Check Record",
    "会议记录": "Meeting Minutes",
    "举一反三检查记录表": "Horizontal Deployment Inspection Record",
    "记录交接表": "Record Handover Form",
    "员工信息登记表": "Employee Information Register",
    "签到表": "Attendance Sheet",
    "员工教育培训记录卡": "Employee Education and Training Record Card",
    "教育培训课程计划表": "Education and Training Course Plan",
    "教育培训有效性评价表": "Education and Training Effectiveness Evaluation Form",
    "员工上岗登记一览表": "Employee Job Authorization Register",
    "人员岗位分布表": "Personnel Position Assignment Chart",
    "培训合格上岗证": "Training Qualification / Job Authorization Certificate",
    "实验室上岗人员及设备对照表": (
        "Laboratory Authorized Personnel and Equipment Matrix"
    ),
    "实验室检测项目及设备授权书": (
        "Authorization for Laboratory Test Items and Equipment"
    ),
    "关键岗位人员变更申请表": "Key Position Personnel Change Application Form",
    "关键岗位人员能力确认及授权书": (
        "Key Position Competence Confirmation and Authorization"
    ),
    "人员上岗实操考核记录表": (
        "Personnel Job Authorization Practical Assessment Record"
    ),
    "人员上岗培训计划表": "Personnel Job Authorization Training Plan",
    "上岗能力复核计划表": "Job Authorization Competence Review Plan",
    "人员持续上岗能力复核表": (
        "Personnel Ongoing Job Authorization Competence Review Form"
    ),
    "内审员实习考核表": "Internal Auditor Trainee Assessment Form",
    "检测报告授权签字人、审核人变更申请单": (
        "Application for Change of Authorized Signatory / Reviewer for Test Reports"
    ),
    "员工工作交接表": "Employee Work Handover Form",
    "合格分包实验室考核表": "Approved Subcontract Laboratory Evaluation Form",
    "合格分包实验室一览表": "Approved Subcontract Laboratory List",
    "合格供应商一览表": "Approved Supplier List",
    "供应商评估表": "Supplier Evaluation Form",
    "检测室访客登记表": "Test Laboratory Visitor Register",
    "人员培训有效性评价报告": "Personnel Training Effectiveness Evaluation Report",
    "供应商评估计划表": "Supplier Evaluation Plan",
    "内外部受控文件清单": "List of Internally and Externally Controlled Documents",
    "文件审查计划表": "Document Review Plan",
    "实验室典型性报告记录表": "Laboratory Typical Report Record",
    "报告发放与标识使用记录表": "Report Issuance and Mark Use Record",
    "授权签字人一览表": "Authorized Signatory List",
    "采购申请单": "Purchase Requisition",
    "实验室设备年度校准计划": "Laboratory Equipment Annual Calibration Plan",
    "分包协议": "Subcontract Agreement",
    "实验室设备清单": "Laboratory Equipment List",
    "仪器设备使用记录表": "Equipment Use Record",
    "仪器设备点检表": "Equipment Daily/Routine Check Form",
    "仪器设备故障及维修记录表": "Equipment Fault and Maintenance Record",
    "仪器设备保养检查记录表": "Equipment Maintenance Inspection Record",
    "仪器设备维护保养计划表": "Equipment Maintenance Plan",
    "电源特性检查报告": "Power Source Characteristic Inspection Report",
    "仪器设备借/携出登记表": "Equipment Loan/Take-Out Register",
    "仪器设备校准方案": "Equipment Calibration Scheme",
    "仪器设备校准结果确认表": "Equipment Calibration Result Confirmation Form",
    "仪器设备期间检查记录表": "Equipment Intermediate Check Record",
    "仪器设备期间核查计划表": "Equipment Intermediate Check Plan",
    "标准查新记录表": "Standards Literature Search Record",
    "标准更新研读记录表": "Standards Update Study Record",
    "标准变更确认记录表": "Standards Change Confirmation Record",
    "检测校准方法验证报告": "Test/Calibration Method Validation Report",
    "检测校准方法适用性评审表": (
        "Test/Calibration Method Suitability Review Form"
    ),
    "质量控制计划表": "Quality Control Plan",
    "人员监督计划表": "Personnel Supervision Plan",
    "能力验证/测量审核/实验室间比对的计划": (
        "Plan for Proficiency Testing / Measurement Audit / Interlaboratory Comparison"
    ),
    "人员能力监控计划表": "Personnel Competence Monitoring Plan",
    "人员能力监控记录表": "Personnel Competence Monitoring Record",
    "人员监督记录表": "Personnel Supervision Record",
    "风险与机遇识别、评估分析记录表": (
        "Risks and Opportunities Identification and Assessment Record"
    ),
    "公正性和保密性工作监督检查记录表": (
        "Impartiality and Confidentiality Supervision Inspection Record"
    ),
    "检测报告（中文）": "Test Report (Chinese)",
    "检测报告（英文）": "Test Report (English)",
    "原始数据记录表": "Raw Data Record",
    "能力验证测量审核实验室间比对测试记录表": (
        "Proficiency Testing / Measurement Audit / Interlaboratory Comparison Test Record"
    ),
    "能力验证测量审核实验室间比对测试报告": (
        "Proficiency Testing / Measurement Audit / Interlaboratory Comparison Test Report"
    ),
    "设备验收表": "Equipment Acceptance Form",
    "设备履历表": "Equipment History Card",
    "质量控制记录报告": "Quality Control Record Report",
    "检测能力范围表": "Scope of Testing Capability",
    "测试数据记录表-IEC/EN 62619": "Test Data Record - IEC/EN 62619",
    "测试数据记录表-IEC/EN 63056": "Test Data Record - IEC/EN 63056",
    "测试数据记录表-IEC/EN 62040-1": "Test Data Record - IEC/EN 62040-1",
    "测试数据记录表-IEC/EN 62477-1": "Test Data Record - IEC/EN 62477-1",
    "测试数据记录表-IEC/EN 62620": "Test Data Record - IEC/EN 62620",
    "测试数据记录表-SA TS 5398:2025": "Test Data Record - SA TS 5398:2025",
    "监督监控问题整改跟踪表": "Supervision/Monitoring Issue Corrective Action Tracking Form",
    "实验室危害因素 & PPE更换频率一览表": (
        "Laboratory Hazard Factors & PPE Replacement Frequency List"
    ),
    "球压测试记录表": "Ball Pressure Test Record",
    "灼热丝测试记录表": "Glow-Wire Test Record",
    "水平垂直燃烧记录表": "Horizontal and Vertical Burning Test Record",
    "IPX1~IPX8 测试记录表": "IPX1-IPX8 Test Record",
    " IP1x~IP6X 测试记录表": "IP1X-IP6X Test Record",
    "IP1x~IP6X 测试记录表": "IP1X-IP6X Test Record",
    "干热，湿热，温湿度变化测试数据表 ": (
        "Dry Heat, Damp Heat, and Temperature/Humidity Change Test Data Sheet"
    ),
    "干热，湿热，温湿度变化测试数据表": (
        "Dry Heat, Damp Heat, and Temperature/Humidity Change Test Data Sheet"
    ),
    "振动测试记录表": "Vibration Test Record",
    "滑石粉更换记录表": "Talc Powder Replacement Record",
    "测试委托单": "Test Request Form",
    " 客户投诉受理及处理报告单": "Customer Complaint Acceptance and Handling Report",
    "客户投诉受理及处理报告单": "Customer Complaint Acceptance and Handling Report",
    "客户满意度调查": "Customer Satisfaction Survey",
    "满意度调查整改情况跟踪验证记录": (
        "Customer Satisfaction Survey Corrective Action Tracking and Verification Record"
    ),
}

# Normalize fancy dashes in generated strings for Excel compatibility.
TRANSLATE = {k: (v.replace("\u2013", "-").replace("\u2014", "-") if isinstance(v, str) else v) for k, v in TRANSLATE.items()}


def tr(text):
    if text is None:
        return None
    if not isinstance(text, str):
        return text
    key = text
    if key in TRANSLATE and TRANSLATE[key] is not None:
        return TRANSLATE[key]
    stripped = text.strip()
    if stripped in TRANSLATE and TRANSLATE[stripped] is not None:
        # preserve leading/trailing spaces only if meaningful; prefer clean English
        return TRANSLATE[stripped]
    # Already English / codes / empty
    if not any("\u4e00" <= ch <= "\u9fff" for ch in text):
        return text.strip() if text != text.strip() and stripped else text
    raise KeyError(f"Missing translation for: {text!r}")


HEADER_BI = {
    "序号": "序号\nNo.",
    "变更号": "变更号\nChange No.",
    "文件名称": "文件名称\nDocument Title",
    "文件编号": "文件编号\nDocument No.",
    "版次": "版次\nRev.",
    "生效日期": "生效日期\nEffective Date",
    "备注": "备注\nRemarks",
}


def _cn_en(zh: str, *, multiline: bool = False) -> str:
    """Keep Chinese, append English; preserve original leading spaces if any."""
    leading = zh[: len(zh) - len(zh.lstrip(" "))] if zh.startswith(" ") else ""
    zh_clean = zh.strip()
    en = tr(zh_clean)
    if en is None or en == zh_clean:
        return zh
    sep = "\n" if multiline else " / "
    return f"{leading}{zh_clean}{sep}{en}"


def main():
    """In-place bilingual text; keep original columns, merges, and styles."""
    from copy import copy
    from openpyxl.styles import Alignment

    wb = openpyxl.load_workbook(SRC)
    missing = []

    for ws in wb.worksheets:
        # Slightly widen title column for bilingual text; keep other widths
        c_width = ws.column_dimensions["C"].width or 35
        ws.column_dimensions["C"].width = max(c_width, 48)

        for row in ws.iter_rows(min_row=1, max_row=ws.max_row or 1, max_col=7):
            for cell in row:
                val = cell.value
                if not isinstance(val, str) or not val.strip():
                    continue
                try:
                    if cell.row <= 2:
                        # Title / subtitle: Chinese + English, wrap in merged cells
                        cell.value = _cn_en(val, multiline=True)
                        cell.alignment = Alignment(
                            horizontal="center",
                            vertical="center",
                            wrap_text=True,
                        )
                    elif cell.row == 3:
                        if val in HEADER_BI:
                            cell.value = HEADER_BI[val]
                            cell.alignment = Alignment(
                                horizontal="center",
                                vertical="center",
                                wrap_text=True,
                            )
                    elif cell.column == 3:
                        # Document title column only
                        cell.value = _cn_en(val, multiline=True)
                        cell.alignment = Alignment(
                            horizontal="center",
                            vertical="center",
                            wrap_text=True,
                        )
                except KeyError as exc:
                    missing.append(str(exc))

        # Bump header / title row height a bit for two-line text
        if ws.row_dimensions[1].height:
            ws.row_dimensions[1].height = max(ws.row_dimensions[1].height or 0, 72)
        if ws.row_dimensions[2].height:
            ws.row_dimensions[2].height = max(ws.row_dimensions[2].height or 0, 40)
        if ws.row_dimensions[3].height:
            ws.row_dimensions[3].height = max(ws.row_dimensions[3].height or 0, 36)
        for r in range(4, (ws.max_row or 4) + 1):
            if ws.cell(r, 3).value and "\n" in str(ws.cell(r, 3).value):
                h = ws.row_dimensions[r].height or 25
                ws.row_dimensions[r].height = max(h, 36)

    if missing:
        uniq = sorted(set(missing))
        raise SystemExit("Missing translations:\n" + "\n".join(uniq))

    wb.save(DST)
    DST_COPY.parent.mkdir(parents=True, exist_ok=True)
    wb.save(DST_COPY)
    print("Saved (same layout, CN+EN in cells):", DST)
    print("Copy:", DST_COPY)


if __name__ == "__main__":
    main()
