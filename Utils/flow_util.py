#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2024/4/30 2:31
# @Author  : hylan(https://github.com/Hylan-J)
# @Description :
import random

from ..Objects import *


def generate_flows(num_flow: int, ES_nodes: list):
    """
    生成流量
    :param num_flow: 流的数量
    :param ES_nodes: 终端节点
    :return:
    """
    flows = []
    for i in range(num_flow):
        # 获取流的id
        id = i
        # 获取流的源节点和目的节点
        # random.sample: 无放回抽取
        src, dst = random.sample(ES_nodes, 2)
        # 设置流的周期{1000μs, 2000μs, 4000μs}
        trans_period = random.choice([1000, 2000, 4000])
        # 设置流的包大小[64*8 bit, 1512*8 bit]
        packet_length = 8 * random.randrange(64, 1512, 1)
        flows.append(
            Flow(id=id, v_s=src, v_d=dst, pr=trans_period, si=packet_length, dl=300))
    return flows
