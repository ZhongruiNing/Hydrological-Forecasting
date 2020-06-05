"""
新安江模型核心函数
ini_soil_moisture：计算初始土壤含水量
evapor_single_period：计算每时段蒸发
runoff_generation_single_period：单一时段产流计算
different_sources：分水源计算
uh_forecast:运用时段单位线进行汇流计算
route_linear_resourvior：线性水库坡地汇流
"""
import numpy as np
import pandas as pd

def ini_soil_moisture(xaj_params,w0_initial,day_precip,day_evapor):
    """
    Objective
    ---------
    根据初始土壤含水量，降雨，蒸发，推求各个时段的土壤含水量，蒸发，产流量

    Parameters
    ----------
    xaj_params：新安江模型参数 (Pandas.DataFrame)
    w0_initial：初始土壤含水量 (Pandas.DataFrame)
    day_precip：流域日降水(list)
    day_evapor：流域日蒸发(list)

    Returns
    -------
    w0：模型计算使用的流域前期土壤含水量(Pandas.Series)
    """
    w0 = w0_initial
    eu_s, el_s, ed_s, wu_s, wl_s, wd_s, r_s =[], [], [], [], [], [], []
    for i in range(day_evapor.size):
        eu, el, ed, wu, wl, wd, r = evapor_single_period(xaj_params, w0, day_precip[i], day_evapor[i])
        w0 = pd.DataFrame({'Value':[wu,wl,wd]},index=['wu','wl','wd'])
        eu_s.append(eu)
        el_s.append(el)
        ed_s.append(ed)
        wu_s.append(wu)
        wl_s.append(wl)
        wd_s.append(wd)
        r_s.append(r)
    result=pd.DataFrame([eu_s, el_s, ed_s, wu_s, wl_s, wd_s, r_s],index=['eu', 'el', 'ed', 'wu', 'wl', 'wd', 'r'])
    return result.T


def evapor_single_period(evapor_params, initial_conditions, precip, evapor):
    """
    Objective
    ---------
    计算每时段蒸发

    Method
    ------
    三层蒸发模式，不考虑不透水面积

    Parameters
    ----------
    evapor_params: 三层蒸发模型计算所需参数 (Pandas.DataFrame)
    initial_conditions: 三层蒸发模型计算所需初始土壤含水量条件 (Pandas.DataFrame)
    precip: 流域时段面平均降雨量
    evapor: 流域时段蒸散发

    Evapor-Parameters
    -----------------
    KC ：流域蒸发能力折算系数
    WUM：上层张力水蓄水容量
    WLM：下层张力水蓄水容量
    WM ：流域平均蓄水容量
    C  ：深层蒸散发折算系数

    Returns
    -------
    eu,el,ed:流域时段三层蒸散发(float)
    wu,wl,wd:流域时段三层含水量(float)
    """

    #读取计算参数
    k = evapor_params.loc['KC','Value']
    wum = evapor_params.loc['WUM','Value']
    wlm = evapor_params.loc['WLM','Value']
    c = evapor_params.loc['C','Value']
    wm = evapor_params.loc['WM','Value']

    #evapor为观测蒸发，e计算为实际蒸发
    ep = k * evapor
    p = precip

    #读取初始土壤含水量参数
    wu0 = initial_conditions.loc['wu','Value']
    wl0 = initial_conditions.loc['wl','Value']
    wd0 = initial_conditions.loc['wd','Value']

    #计算深层张力水蓄水容量
    wdm = wm - wum - wlm

    #三层蒸发模式计算
    if wu0 + p >= ep:
        eu = ep
        el = 0
        ed = 0
    else:
        eu=round(wu0+p,1)
        if wl0 >= c * wlm:
            el=round((ep - eu) * wl0 / wlm, 1)
            ed = 0
        if wl0 >= c * (ep - eu) and wl0 < c * wlm:
            eu = round(wu0 + p, 1)
            el = round(c * (ep - eu), 1)
            ed = 0
        if wl0 < c * (ep - eu):
            eu = round(wu0 + p, 1)
            el = wl0
            ed = round(c * (ep - eu) - el, 1)
    if p - ep > 0:
        r = runoff_generation_single_period(evapor_params, initial_conditions, precip, evapor)
        wu = wu0 + p - eu - r
        wl = wl0 - el
        wd = wd0 - ed
        if wu > wum:
            wl = wl + wu - wum
            wu = wum
        if wl > wlm:
            wd = wd + wl - wlm
            wl = wlm
        if wu < 0.001:
            wu = 0
        if wl < 0.001:
            wl = 0 
        if wd < 0.001:
            wd = 0
    else:
        r = 0
        wu = wu0 + p - eu
        wl = wl0 - el
        wd = wd0 - ed
    return eu, el, ed, wu, wl, wd, r


def runoff_generation_single_period(gene_params, initial_conditions, precip, evapor):
    """
    Objective
    ---------
    单一时段流域产流计算

    Method
    ------
    蓄满产流模型

    Parameters
    ----------
    gene_params: 新安江模型产流参数 (Pandas.DataFrame)
    initial_conditions: 时段初计算条件 (Pandas.DataFrame)
    precip: 该时段面平均降雨量 (Pandas.DataFrame)
    evapor: 流域该时段蒸散发 (Pandas.DataFrame)

    Gene-Parameters
    ---------------
    wm：流域平均张力水蓄水容量
    B ：张力水蓄水容量面积分布曲线方次 

    Returns
    -------
    runoff：流域时段产流量
    """
    b = gene_params.loc['B','Value']
    wm = gene_params.loc['WM','Value']

    wu0 = initial_conditions.loc['wu','Value']
    wl0 = initial_conditions.loc['wl','Value']
    wd0 = initial_conditions.loc['wd','Value']
    w0 = wu0 + wl0 + wd0

    pe = precip - evapor
    wmm = wm * (1 + b)
    a = wmm * (1 - (1 - w0 / wm) ** (1 / (1 + b)))

    if a + pe < wmm:
        r = round(pe + w0 - wm + wm * (1 - (a + pe) / wmm) ** (b + 1), 1)
    else:
        r = round(pe + w0 - wm, 1)

    return r


def different_sources(diff_source_params, initial_conditions, precip, evapor, runoff):
    """
    Objective
    ---------
    分水源计算

    Method
    ------
    水箱模型三水源划分

    Parameters
    ----------
    diff_source_params:分水源计算所需参数 (Pandas.DataFrame)
    initial_conditions:计算所需初始条件 (Pandas.DataFrame)
    precips:各时段降雨 (Pandas.DataFrame)
    evapors:各时段蒸发 (Pandas.DataFrame)
    runoffs:各时段产流 (Pandas.DataFrame)

    Diff-Source-Params
    ------------------
    k ：流域蒸发能力折算系数
    sm：表土层自由水蓄量
    ex：自由水蓄水容量面积分许曲线指数
    ki：自由水蓄水库壤中流日出流系数
    kg：自由水蓄水库地下水日出流系数

    Returns
    -------
    Diff_source：分水源计算结果 (Pandas.DataFrame)
    """

    # 取参数值
    k = diff_source_params.loc['KC','Value']
    sm = diff_source_params.loc['SM','Value']
    ex = diff_source_params.loc['EX','Value']
    ki = diff_source_params.loc['KI','Value']
    #KI+KG=0.7，即雨止到壤中流止的时间为3天
    kg = 0.7 - ki

    # 为便于后面计算，这里以数组形式给出s和fr
    s_s = []#自由水蓄水库自由水蓄量
    fr_s = []#产流面积

    # 取初始值
    s0 = initial_conditions.loc['S0','Value']
    fr0 = initial_conditions.loc['FR0','Value']

    # 流域最大点自由水蓄水容量深
    ms = sm * (1 + ex)

    rs_s, ri_s, rg_s = [], [], []
    for i in range(precip.size):
        #上一时段的产流面积FR0，自由水蓄水量S0
        if i == 0:
            fr0 = fr0
            s0 = s0
        else:
            fr0 = fr_s[i-1]
            s0 = s_s[i-1]
        #本时段计算
        p = precip[i]
        e = k * evapor[i]
        if runoff[i] < 0:
            rs = 0
            ri = s0 * fr0 * ki
            ri = round(ri , 3)
            rg = s0 * fr0 * kg
            rg = round(rg , 3)
            fr=fr0
            if fr <= 0:
                fr = 0.001
            if fr > 0:
                fr = 1
            s = s0 * (1 - ki - kg)
            if s < 0:
                s = 0
            if s > sm:
                s = sm
            if ri < 0.01:
                ri = 0
            if rg < 0.01:
                rg = 0
        else:
            pe = p - e
            fr = runoff[i] / pe
            if fr <= 0:
                fr = 0.01
            if fr > 1:
                fr = 1
            au = ms * (1 - ((1 - ((s0 * fr0) / (fr * sm))) ** (1 / (1 + ex))))
            if pe + au < ms:
                rs = fr * (pe + (s0 * fr0) / fr - sm + sm * ((1 - (pe + au) / ms) ** (1+ex)))
            else:
                rs = fr * (pe + s0 * fr0 / fr - sm)
            s = s0 * fr0 / fr + (runoff[i] - rs) / fr
            ri = ki * s * fr
            rg = kg * s * fr
            rs = round(rs , 3)
            ri = round(ri , 3)
            rg = round(rg , 3)
            s0 = s * (1 - ki - kg)
            if rs < 0.01:
                rs = 0
            if ri < 0.01:
                ri = 0
            if rg < 0.01:
                rg = 0
        fr_s.append(fr)
        s_s.append(s)
        rs_s.append(rs)
        ri_s.append(ri)
        rg_s.append(rg)
        diff_source=pd.DataFrame([rs_s, ri_s, rg_s], index=['rs', 'ri', 'rg'])
    return diff_source.T

def uh_forecast(runoffs, uh):
    """运用时段单位线进行汇流计算
    Parameters
    ------------
    runoffs:场次洪水对应的各时段净雨，数组
    uh:单位线各个时段数值

    Return
    ------------
    汇流计算结果——流量过程线 (list)
    """
    q = np.convolve(runoffs, uh)
    return q

def route_linear_resourvior(route_params, basin_property, initial_conditions, rs, ri, rg):
    """
    Objective
    ---------
    坡地汇流计算

    Method
    ------
    线性水库

    Parameters
    ----------
    route_params：汇流参数 (Pandas.DataFrame)
    basin_property：流域属性条件 (Pandas.DataFrame)
    initial_confitions：初始条件 (Pandas.DataFrame)
    rs：地面径流净雨 (Pandas.DataFrame)
    ri：壤中流净雨 (Pandas.DataFrame)
    rg：地下径流净雨 (Pandas.DataFrame)

    Route-Params
    ------------
    cs：地面径流消退系数
    ci：壤中流消退系数
    cg：地下径流消退系数

    Returns
    -------
    QT_Network 单元面积河网总入流(m3/s) (Pandas.DataFrame)
    """
    f = basin_property.loc['basin_area/km^2','Value']
    time_in = 24
    u = f / (3.6 * time_in)

    cs = route_params.loc['CS','Value']
    ci = route_params.loc['CI','Value']
    cg = route_params.loc['CG','Value']

    qs0=initial_conditions.loc['QS0','Value']
    qi0=initial_conditions.loc['QI0','Value']
    qg0=initial_conditions.loc['QG0','Value']

    qs_s, qi_s, qg_s = [], [], []
    
    qs_s.append(qs0)
    qi_s.append(qi0)
    qg_s.append(qg0)

    for i in range(len(rs)):
        if i == 0:
            qs0 = qs0
            qi0 = qi0
            qg0 = qg0
        else:
            qs0 = qs_s[i-1]
            qi0 = qi_s[i-1]
            qg0 = qg_s[i-1]

        qs = cs * qs0 + (1 - cs) * rs[i] * u
        qi = ci * qi0 + (1 - ci) * ri[i] * u
        qg = cg * qg0 + (1 - cg) * rg[i] * u

        if i == 0:
            qs_s[i] = qs
            qi_s[i] = qi
            qg_s[i] = qg
        else:
            qs_s.append(qs)
            qi_s.append(qi)
            qg_s.append(qg)

    qs_s=np.array(qs_s)
    qi_s=np.array(qi_s)
    qg_s=np.array(qg_s)
    qt_s = qs_s + qi_s + qg_s
    
    QT_Network=pd.DataFrame([qs_s,qi_s,qg_s,qt_s], index=['qs','qi','qg','qt'])
    return QT_Network.T
