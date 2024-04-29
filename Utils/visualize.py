#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2024/4/30 2:33
# @Author  : hylan(https://github.com/Hylan-J)
# @Description : 可视化的相关util
def display_schedule_results_by_flows(network, flows, route_results, schedule_results):
    print('-----------------------------------------------------------------------------------')
    edges = network.links
    for flow in flows:
        print('\n| 流量 {:2d} 的调度结果:'.format(flow.id))
        route = route_results[flow.id]
        for i in range(len(route) - 1):
            for vi, vj in edges:
                if route[i] == vi and route[i + 1] == vj:
                    start_time = schedule_results[vi, vj, flow.id].varValue
                    if start_time != 0:
                        end_time = start_time + network.t_tran(flow.packet_length)
                        print('| 链路 {}-{} : {:5f} μs - {:5f} μs'.format(vi, vj, start_time, end_time))
    print('-----------------------------------------------------------------------------------')


