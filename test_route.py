#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2024/4/30 2:18
# @Author  : hylan(https://github.com/Hylan-J)
# @Description :
from Objects import *
from Configs import *

# 表 3.2 示例中流集合 S 的参数
flow1 = Flow(id=1, v_s='ES0', v_d='ES5', pr=50, si=80, dl=300, rl=2)
flow2 = Flow(id=2, v_s='ES1', v_d='ES3', pr=100, si=160, dl=250, rl=2)
flow3 = Flow(id=3, v_s='ES2', v_d='ES1', pr=50, si=160, dl=300, rl=2)
flow4 = Flow(id=4, v_s='ES1', v_d='ES4', pr=200, si=320, dl=250, rl=2)

network = Network(ES_nodes=ES_nodes,
                  SW_nodes=SW_nodes,
                  links=links,
                  unreliable_links=unreliable_links,
                  link_speed=1,
                  t_switch=4,
                  p_r=0.05,
                  p_ur=0.2)