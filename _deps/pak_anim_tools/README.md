# 泳池黑夜水中僵尸动画实验工具（A 方案，实验性，未启用）

用途：给没有 `anim_swim` 的僵尸 reanim 追加游泳动画段，并重打包 `main.pak`。

关键结论（踩坑记录）：
- 游戏实际加载的是 pak 里 `compiled\reanim\*.reanim.compiled` 预编译定义，不是 XML；
  所以脚本会删除对应 compiled 条目，让引擎回退加载 XML。
- XML 里动画段由 `anim_walk/anim_idle/anim_eat/anim_death` 等标记轨道上的槽位界定，
  骨骼/贴图轨道按槽位存每帧变换；给没有 anim_swim 的文件复制已有帧段改写即可加上动画。
- 实测结果：动画会卡住（帧段标记语义没有完全对上），因此**最终版本没有启用**，
  这 6 种僵尸（扶梯/橄榄球/读报/雪人/小丑/伴舞）改为"水路非法，直接淹死"。
  本目录代码仅保留备查，勿直接用于发布。

文件：
- `gen_swim_reanim.py`   把 idle/moonwalk 帧段改写成 anim_swim，输出 .trash/main_swim.pak
- `pak_strip_compiled.py` 生成"删除指定 compiled 定义"的测试 pak
- `pak_rebuild_verify.py` 原样重打包校验（应与官方包字节一致）

用法（先备份 `Plants Vs. Zombies\main.pak`）：先跑 gen_swim_reanim.py，再把生成的 pak 拷到 bin 目录测试。
