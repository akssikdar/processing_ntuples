#!/usr/bin/julia

sqrtsum(x) = sqrt(sum(x.^2))

# the last number is top pT
acc_el_err = sqrtsum([0.0006                0.0002                0.0022                0.0006                0.0020                0.0012                0.0047  0.0017 ])
acc_mu_err = sqrtsum([0.0008                0.0002                0.0025                0.0005                0.0026                0.0006                0.0049  0.0019 ])
acc_bt_err = sqrtsum([0.0007                0.0002                0.0023                0.0005                0.0023                0.0008                0.0048  0.0019 ])

acc_el = 0.1687
acc_mu = 0.1756
acc_bt = 0.1722

println(acc_el, " ", acc_el_err)
println(acc_mu, " ", acc_mu_err)
println(acc_bt, " ", acc_bt_err)

accept = [acc_el acc_mu acc_bt]

el_sig  = 1.020
el_sys  = 0.096
el_stat = 0.015

mu_sig  = 0.909
mu_sys  = 0.077
mu_stat = 0.011

bt_sig  = 0.941
bt_sys  = 0.075
bt_stat = 0.009


# v13 test13 FULLFIT1 update1 update2

el_sig  = 0.941
el_sys  = 0.08
el_stat = 0.014

mu_sig  = 0.936
mu_sys  = 0.072
mu_stat = 0.011

bt_sig  = 0.949
bt_sys  = 0.071
bt_stat = 0.009

# v13 test15 paper6

el_sig  = 0.946
el_sys  = 0.082
el_stat = 0.014

mu_sig  = 0.945
mu_sys  = 0.072
mu_stat = 0.011

bt_sig  = 0.961
bt_sys  = 0.071
bt_stat = 0.009

# v37 test172 BIN1 paper (11) 12

el_sig  = 0.949
el_sys  = 0.082
el_stat = 0.014

mu_sig  = 0.926
mu_sys  = 0.073
mu_stat = 0.011

bt_sig  = 0.939
bt_sys  = 0.071
bt_stat = 0.009




# and the actual calculation

# fiducial (visible) phase space

xsec_el_vis = [el_sig el_stat el_sys 0.025 ]
xsec_mu_vis = [mu_sig mu_stat mu_sys 0.025 ]
xsec_bt_vis = [bt_sig bt_stat bt_sys 0.025 ]

# expected vis xsecs
xsec_vis = 831.76 * accept

# scale everything to expected (!!!) visible xsec
xsec_visible_el = xsec_el_vis * xsec_vis[1]
xsec_visible_mu = xsec_mu_vis * xsec_vis[2]
xsec_visible_bt = xsec_bt_vis * xsec_vis[3]

println(xsec_visible_el)
println(xsec_visible_mu)
println(xsec_visible_bt)


# scale uncertainties to the measured (!!!) visible xsec
xsec_el_meas = el_sig * 831.76 * acc_el
xsec_mu_meas = mu_sig * 831.76 * acc_mu
xsec_bt_meas = bt_sig * 831.76 * acc_bt

println(xsec_el_meas, " ", xsec_el_meas .* [el_stat el_sys 0.025])
println(xsec_mu_meas, " ", xsec_mu_meas .* [mu_stat mu_sys 0.025])
println(xsec_bt_meas, " ", xsec_bt_meas .* [bt_stat bt_sys 0.025])



# full phase space

el_sys_extr = sum([el_sys acc_el_err / acc_el].^2) ^ 0.5
mu_sys_extr = sum([mu_sys acc_mu_err / acc_mu].^2) ^ 0.5
bt_sys_extr = sum([bt_sys acc_bt_err / acc_bt].^2) ^ 0.5

println(el_sys, "\t", acc_el_err / acc_el)
println(mu_sys, "\t", acc_mu_err / acc_mu)
println(bt_sys, "\t", acc_bt_err / acc_bt)

println(el_sys_extr)
println(mu_sys_extr)
println(bt_sys_extr)

xsec_el_extr = [el_sig el_stat el_sys_extr  0.025]
xsec_mu_extr = [mu_sig mu_stat mu_sys_extr  0.025]
xsec_bt_extr = [bt_sig bt_stat bt_sys_extr  0.025]

xsec_el_extr = el_sig * 831.76
xsec_mu_extr = mu_sig * 831.76
xsec_bt_extr = bt_sig * 831.76

println(xsec_el_extr, " ", xsec_el_extr .* [el_stat el_sys_extr  0.025 ])
println(xsec_mu_extr, " ", xsec_mu_extr .* [mu_stat mu_sys_extr  0.025 ])
println(xsec_bt_extr, " ", xsec_bt_extr .* [bt_stat bt_sys_extr  0.025 ])

